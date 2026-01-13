# Contributing to Python Code Guardian MCP

Thank you for your interest in contributing to Python Code Guardian! This document provides guidelines and instructions for contributing.

## 🚀 Quick Start

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/python-code-guardian-mcp.git
   cd python-code-guardian-mcp
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Run tests**
   ```bash
   pytest
   ```

## 📋 Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and under 50 lines when possible
- Maximum line length: 100 characters

### Testing

- Write tests for all new features
- Maintain test coverage above 75%
- Run tests before submitting PR:
  ```bash
  pytest --cov=python_code_guardian --cov-report=term-missing
  ```

### Commit Messages

Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Example:
```
feat: add support for custom checker plugins
fix: resolve issue with duplicate detection in nested functions
docs: update README with installation instructions
```

## 🔧 Adding a New Checker

To add a new code checker:

1. Create a new file in `src/python_code_guardian/checkers/`
2. Extend `BaseChecker` class
3. Implement the `check()` method
4. Add tests in `tests/checkers/`
5. Update documentation

Example:

```python
from .base_checker import BaseChecker

class MyCustomChecker(BaseChecker):
    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        # Your implementation
        pass
```

## 📝 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run checks**
   ```bash
   # Run linting
   pylint src/python_code_guardian
   
   # Run tests
   pytest
   
   # Check test coverage
   pytest --cov=python_code_guardian --cov-report=html
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add awesome feature"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Provide clear description
   - Reference any related issues
   - Ensure CI passes

## 🐛 Reporting Bugs

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/stack traces

## 💡 Feature Requests

We welcome feature requests! Please:

- Check if the feature already exists
- Provide clear use case
- Explain why it would be useful
- Consider implementing it yourself!

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community

## 🤝 Need Help?

- 💬 Open a GitHub Discussion
- 🐛 Report issues on GitHub Issues
- 📧 Contact maintainers

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Python Code Guardian! 🎉

