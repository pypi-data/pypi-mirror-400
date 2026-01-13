"""
Logic Verification Engine with DSL Support.

This module provides a new logic verifier that uses the QWED-DSL
for secure, validated constraint parsing.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from z3 import Solver, sat, unsat

from qwed_new.core.dsl import parse_and_validate, compile_to_z3
from qwed_new.core.schemas import LogicResult


@dataclass
class DSLVerificationResult:
    """Result of DSL-based logic verification."""
    status: str  # "SAT", "UNSAT", "ERROR", "BLOCKED"
    model: Optional[Dict[str, str]] = None
    dsl_code: Optional[str] = None
    parsed_ast: Optional[Any] = None
    error: Optional[str] = None
    rejection_reason: Optional[str] = None  # Human-readable explanation for UNSAT


class DSLLogicVerifier:
    """
    Logic Verifier using QWED-DSL.
    
    This replaces unsafe eval() with a secure, whitelist-based parser.
    
    Flow:
    1. Parse DSL code → AST
    2. Validate against whitelist
    3. Compile to Z3
    4. Solve and return result
    """
    
    def __init__(self, timeout_ms: int = 5000):
        self.timeout_ms = timeout_ms
    
    def verify_from_dsl(
        self, 
        dsl_code: str,
        variables: Optional[List[Dict[str, str]]] = None
    ) -> DSLVerificationResult:
        """
        Verify logic from QWED-DSL code.
        
        Args:
            dsl_code: The QWED-DSL S-expression string
            variables: Optional list of variable declarations [{"name": "x", "type": "Int"}, ...]
            
        Returns:
            DSLVerificationResult with status and model
        """
        # 1. Parse and Validate
        parse_result = parse_and_validate(dsl_code)
        
        if parse_result['status'] == 'BLOCKED':
            return DSLVerificationResult(
                status="BLOCKED",
                error=parse_result.get('error'),
                dsl_code=dsl_code
            )
        
        if parse_result['status'] == 'PARSE_ERROR':
            return DSLVerificationResult(
                status="ERROR",
                error=f"Parse error: {parse_result.get('error')}",
                dsl_code=dsl_code
            )
        
        if parse_result['status'] != 'SUCCESS':
            return DSLVerificationResult(
                status="ERROR",
                error=parse_result.get('error', 'Unknown error'),
                dsl_code=dsl_code
            )
        
        # 2. Convert variables list to dict format for compiler
        var_declarations = {}
        if variables:
            for var in variables:
                if isinstance(var, dict) and 'name' in var:
                    var_declarations[var['name']] = {'type': var.get('type', 'Int')}
        
        # 3. Compile to Z3
        ast = parse_result['ast']
        compile_result = compile_to_z3(ast, var_declarations)
        
        if not compile_result.success:
            return DSLVerificationResult(
                status="ERROR",
                error=compile_result.error,
                dsl_code=dsl_code,
                parsed_ast=ast
            )
        
        # 4. Solve with Z3
        try:
            solver = Solver()
            solver.set("timeout", self.timeout_ms)
            
            # Add the compiled constraint
            if compile_result.compiled is not None:
                solver.add(compile_result.compiled)
            
            # Check satisfiability
            result = solver.check()
            
            if result == sat:
                model = solver.model()
                solution = {d.name(): str(model[d]) for d in model.decls()}
                return DSLVerificationResult(
                    status="SAT",
                    model=solution,
                    dsl_code=dsl_code,
                    parsed_ast=ast
                )
            elif result == unsat:
                # Generate human-readable rejection reason
                rejection_reason = self._explain_unsat(dsl_code, ast)
                return DSLVerificationResult(
                    status="UNSAT",
                    dsl_code=dsl_code,
                    parsed_ast=ast,
                    rejection_reason=rejection_reason
                )
            else:
                return DSLVerificationResult(
                    status="UNKNOWN",
                    error="Solver returned unknown (possibly timeout)",
                    dsl_code=dsl_code,
                    parsed_ast=ast
                )
        
        except Exception as e:
            return DSLVerificationResult(
                status="ERROR",
                error=f"Z3 solver error: {str(e)}",
                dsl_code=dsl_code,
                parsed_ast=ast
            )
    
    def _explain_unsat(self, dsl_code: str, ast: Any) -> str:
        """
        Generate a human-readable explanation for why constraints are unsatisfiable.
        
        This analyzes the AST to identify conflicting constraints and generates
        a user-friendly message.
        
        Args:
            dsl_code: Original DSL code
            ast: Parsed AST
            
        Returns:
            Human-readable explanation string
        """
        # Extract constraint descriptions from AST
        constraints = self._extract_constraints_from_ast(ast)
        
        if len(constraints) == 0:
            return "The constraints are contradictory and cannot be satisfied."
        
        if len(constraints) == 1:
            return f"Rule violated: {constraints[0]}"
        
        # Try to identify specific conflicts
        conflict_msg = self._identify_conflicts(constraints)
        if conflict_msg:
            return conflict_msg
        
        # Default: List all constraints
        constraint_list = "\n  - ".join(constraints)
        return (
            f"No valid solution exists. The following constraints are in conflict:\n"
            f"  - {constraint_list}"
        )
    
    def _extract_constraints_from_ast(self, ast: Any) -> List[str]:
        """Extract human-readable constraint descriptions from AST."""
        constraints = []
        
        if ast is None:
            return constraints
        
        # Handle tuple format: (OPERATOR, operand1, operand2, ...)
        if isinstance(ast, tuple) and len(ast) >= 1:
            op = ast[0]
            
            # Comparison operators
            if op in ("GT", "LT", "GE", "LE", "EQ", "NE"):
                op_symbols = {"GT": ">", "LT": "<", "GE": ">=", "LE": "<=", "EQ": "==", "NE": "!="}
                if len(ast) >= 3:
                    left = self._format_operand(ast[1])
                    right = self._format_operand(ast[2])
                    constraints.append(f"{left} {op_symbols.get(op, op)} {right}")
            
            # Logical operators (recurse)
            elif op in ("AND", "OR", "NOT", "IMPLIES"):
                for operand in ast[1:]:
                    constraints.extend(self._extract_constraints_from_ast(operand))
            
            # Arithmetic (just describe)
            elif op in ("PLUS", "MINUS", "MUL", "DIV"):
                constraints.append(f"Arithmetic: {dsl_code}")
        
        return constraints
    
    def _format_operand(self, operand: Any) -> str:
        """Format an operand for display."""
        if isinstance(operand, tuple):
            # Nested expression
            op = operand[0]
            if op in ("PLUS", "MINUS", "MUL", "DIV"):
                op_symbols = {"PLUS": "+", "MINUS": "-", "MUL": "*", "DIV": "/"}
                if len(operand) >= 3:
                    left = self._format_operand(operand[1])
                    right = self._format_operand(operand[2])
                    return f"({left} {op_symbols.get(op, op)} {right})"
            return str(operand)
        return str(operand)
    
    def _identify_conflicts(self, constraints: List[str]) -> Optional[str]:
        """Try to identify specific conflicts between constraints."""
        # Look for obvious contradictions like x > 5 AND x < 3
        for i, c1 in enumerate(constraints):
            for c2 in constraints[i+1:]:
                # Check if same variable has conflicting bounds
                if self._are_conflicting(c1, c2):
                    return (
                        f"Contradiction detected:\n"
                        f"  Rule 1: {c1}\n"
                        f"  Rule 2: {c2}\n"
                        f"These constraints cannot both be true."
                    )
        return None
    
    def _are_conflicting(self, c1: str, c2: str) -> bool:
        """Check if two constraints are obviously conflicting."""
        # Simple heuristic: same variable with > and < that overlap
        # E.g., "x > 5" and "x < 3"
        import re
        
        # Pattern: variable > number
        gt_pattern = r"(\w+)\s*>\s*([\d.]+)"
        lt_pattern = r"(\w+)\s*<\s*([\d.]+)"
        
        gt1 = re.search(gt_pattern, c1)
        lt1 = re.search(lt_pattern, c1)
        gt2 = re.search(gt_pattern, c2)
        lt2 = re.search(lt_pattern, c2)
        
        # Check x > a AND x < b where a >= b
        if gt1 and lt2:
            if gt1.group(1) == lt2.group(1):  # Same variable
                lower = float(gt1.group(2))
                upper = float(lt2.group(2))
                if lower >= upper:
                    return True
        
        if lt1 and gt2:
            if lt1.group(1) == gt2.group(1):  # Same variable
                upper = float(lt1.group(2))
                lower = float(gt2.group(2))
                if lower >= upper:
                    return True
        
        return False
    
    def verify_from_natural_language(
        self,
        query: str,
        provider: str = "azure_openai"
    ) -> DSLVerificationResult:
        """
        Full pipeline: Natural Language → DSL → Z3.
        
        Args:
            query: Natural language logic query
            provider: Which LLM provider to use
            
        Returns:
            DSLVerificationResult
        """
        # 1. Translate to DSL
        try:
            if provider == "azure_openai":
                from qwed_new.providers.azure_openai import AzureOpenAIProvider
                llm = AzureOpenAIProvider()
                dsl_result = llm.translate_logic_dsl(query)
            else:
                # Fallback to Azure
                from qwed_new.providers.azure_openai import AzureOpenAIProvider
                llm = AzureOpenAIProvider()
                dsl_result = llm.translate_logic_dsl(query)
            
            dsl_code = dsl_result.get('dsl_code', '')
            variables = dsl_result.get('variables', [])
            
        except Exception as e:
            return DSLVerificationResult(
                status="ERROR",
                error=f"LLM translation failed: {str(e)}"
            )
        
        # 2. Verify from DSL
        return self.verify_from_dsl(dsl_code, variables)


# Singleton for convenience
_dsl_verifier = None

def get_dsl_verifier() -> DSLLogicVerifier:
    """Get the singleton DSL verifier instance."""
    global _dsl_verifier
    if _dsl_verifier is None:
        _dsl_verifier = DSLLogicVerifier()
    return _dsl_verifier


def verify_logic_dsl(dsl_code: str, variables: Optional[List[Dict]] = None) -> DSLVerificationResult:
    """Convenience function to verify logic from DSL code."""
    return get_dsl_verifier().verify_from_dsl(dsl_code, variables)


# --- DEMO ---
if __name__ == "__main__":
    verifier = DSLLogicVerifier()
    
    print("=" * 60)
    print("QWED DSL Logic Verifier Demo")
    print("=" * 60)
    
    # Test 1: Valid constraint - SAT
    print("\nTest 1: x > 5 AND y < 10 (should be SAT)")
    result = verifier.verify_from_dsl(
        "(AND (GT x 5) (LT y 10))",
        [{"name": "x", "type": "Int"}, {"name": "y", "type": "Int"}]
    )
    print(f"Status: {result.status}")
    print(f"Model: {result.model}")
    
    # Test 2: Unsatisfiable
    print("\nTest 2: x > 10 AND x < 5 (should be UNSAT)")
    result = verifier.verify_from_dsl(
        "(AND (GT x 10) (LT x 5))",
        [{"name": "x", "type": "Int"}]
    )
    print(f"Status: {result.status}")
    
    # Test 3: Security block
    print("\nTest 3: Attempt IMPORT (should be BLOCKED)")
    result = verifier.verify_from_dsl("(IMPORT os)")
    print(f"Status: {result.status}")
    print(f"Error: {result.error}")
    
    # Test 4: Enterprise rule
    print("\nTest 4: If amount > 10000 then requires_approval = True")
    result = verifier.verify_from_dsl(
        "(IMPLIES (GT amount 10000) (EQ requires_approval True))",
        [{"name": "amount", "type": "Int"}, {"name": "requires_approval", "type": "Bool"}]
    )
    print(f"Status: {result.status}")
    print(f"Model: {result.model}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
