# QWED Compliance Guide

This guide provides instructions for System Administrators and Developers on how to use QWED's compliance features for SOC 2 preparation, GDPR adherence, and audit trail management.

## Audience
- **System Administrators:** Use the API endpoints described below to manage compliance tasks.
- **Developers:** Integrate these features into your applications using the QWED Python SDK.

---

## 1. SOC 2 Preparation

QWED provides built-in tools to assist with SOC 2 Type II audits, specifically focusing on Security, Availability, and Processing Integrity.

### SOC 2 Report Generator
Generate a comprehensive JSON report containing security metrics, control statuses, and evidence summaries.

**API Endpoint:**
```http
GET /admin/compliance/report/soc2/{org_id}
```

**Example Response:**
```json
{
  "report_type": "SOC 2 Type II - Security Controls",
  "period": {
    "start": "2023-01-01T00:00:00",
    "end": "2023-03-31T23:59:59"
  },
  "compliance_status": {
    "audit_trail_complete": "PASS",
    "access_logs_retained": "PASS"
  }
}
```

### Audit Trail Verification
Verify the cryptographic integrity of your audit logs. This ensures that no logs have been tampered with since creation.

**Verify a Single Log Entry:**
```http
GET /admin/compliance/verify/{log_id}
```

**Verify Entire Trail (Python SDK):**
For a complete verification of all logs, use the Python SDK or a custom script interacting with the database directly, as the API verifies one entry at a time for performance reasons.

```python
from qwed_new.core.audit_logger import AuditLogger
from qwed_new.core.database import get_session

verifier = AuditLogger()
with get_session() as session:
    result = verifier.verify_audit_trail(organization_id=1)
    if result["valid"]:
        print("Audit trail integrity confirmed.")
    else:
        print(f"Integrity check failed: {result['errors']}")
```

### Evidence Collection
Export all verification logs and security events as a CSV file to provide to your auditor.

**API Endpoint:**
```http
GET /admin/compliance/export/csv?organization_id={org_id}
```

---

## 2. GDPR Compliance

### Data Export (Article 15 - Right of Access)
QWED supports the Right of Access by allowing you to export all data associated with an organization or user.

**API Endpoint:**
Use the CSV export endpoint to retrieve all verification data.
```http
GET /admin/compliance/export/csv?organization_id={org_id}
```

### Data Deletion (Article 17 - Right to Erasure)
**Note:** Currently, user deletion must be performed by an administrator directly in the database. A self-service deletion API is planned.

To comply with a deletion request:
1.  **Delete the User:** Remove the user record from the database.
2.  **Prune Logs:** For full GDPR Article 17 compliance, ensure all verification logs associated with the user are also deleted or anonymized.

**Manual Database Process (Example):**
```sql
-- Delete User
DELETE FROM user WHERE id = {user_id};

-- Delete associated logs (if required by policy)
DELETE FROM verificationlog WHERE user_id = {user_id};
```

### Consent Management
QWED does not have a built-in "Consent Management Platform" (CMP), but you can use the immutable audit log to track consent events.

**Implementing Consent Tracking:**
Log a specific "verification" event when a user grants consent. This creates a tamper-proof record.

```python
# Example: Logging a consent event via the API
requests.post("/verify/fact", json={
    "claim": "User 123 granted consent for data processing",
    "context": "Consent Version 1.0, IP: 192.168.1.1",
    "provider": "system"
})
```
*Note: This treats the consent record as a "fact" verification, securing it in the cryptographic ledger.*

---

## 3. Audit Trail Setup

### Enable Cryptographic Logging
Cryptographic logging is enabled by default, but you **must** configure the security key for production.

1.  **Set Environment Variable:**
    Set `AUDIT_SECRET_KEY` to a secure, random string (at least 32 characters).
    ```bash
    export AUDIT_SECRET_KEY="your-secure-production-key-here"
    ```
    *Warning: Never use the default hardcoded key in production.*

2.  **Secure Storage:**
    Ensure this key is stored in a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault) and injected into the application environment.

### Verify Log Integrity
Regularly run the verification process (see "Audit Trail Verification" above) to detect any database tampering.

### Long-term Storage
QWED uses the configured database (SQLite/PostgreSQL) for log storage. For high-volume compliance requirements:
- Configure database backups to a WORM (Write Once, Read Many) compatible storage (e.g., AWS S3 Object Lock) for archival.

---

## 4. Compliance Checklist

Use this checklist to prepare for an enterprise audit.

- [ ] **Audit Logs Verified:** Run `verify_audit_trail` on all historical logs.
- [ ] **API Keys Rotated:** Rotate any API keys older than 90 days.
- [ ] **SOC 2 Report Generated:** Generate and review the latest SOC 2 report via API.
- [ ] **Secret Key Secured:** Confirm `AUDIT_SECRET_KEY` is set to a production-grade value.
- [ ] **GDPR Export Tested:** Verify that data export works for a sample organization.
- [ ] **Security Events Reviewed:** Check the "Security Events" section of the SOC 2 report for any anomalies.
- [ ] **Rate Limiting Active:** Confirm rate limits are enforced to prevent abuse (DoS protection).

