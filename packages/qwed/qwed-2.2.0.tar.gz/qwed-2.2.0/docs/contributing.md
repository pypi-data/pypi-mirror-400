# Contributing

We love contributions! Here's how to get started.

## Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/qwed-verification.git
   cd qwed-verification
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Start PostgreSQL**:
   ```bash
   docker-compose up -d
   ```

5. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

---

## Code Style

We use:
- **Black** for formatting
- **isort** for import sorting
- **mypy** for type checking

Run all checks:
```bash
black .
isort .
mypy src/
```

---

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Commit with a clear message
6. Push and create a Pull Request

---

## Good First Issues

Look for issues labeled `good-first-issue` in the GitHub repository. These are great starting points for new contributors!

---

## Questions?

Open a GitHub Discussion or reach out to the maintainers.

*Thank you for contributing to a safer AI future! 🛡️*

