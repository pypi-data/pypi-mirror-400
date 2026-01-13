# Python Code Guardian MCP Server

[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A comprehensive Model Context Protocol (MCP) server for Python code quality checks. This tool helps teams maintain high code quality standards through automated checks for linting, modularity, typos, structure, and test coverage.

## 🚀 Features

✅ **Comprehensive Code Analysis**
- **Linting with Pylint** - PEP 8 compliance, code style, and best practices
- **Complexity Analysis** - Cyclomatic complexity and maintainability checks
- **Duplicate Code Detection** - Identifies redundant code blocks
- **Typo Detection** - Catches typos in comments, docstrings, variable names, and strings
- **Structure Validation** - File organization, naming conventions, and docstrings
- **Test Coverage** - Ensures 75% minimum test coverage

✅ **Flexible Integration**
- Pre-commit hook support
- On-demand checks via Cursor IDE
- Custom rules configuration
- Detailed reports with line numbers and suggestions

✅ **Developer Friendly**
- Summary statistics
- Auto-fix capabilities
- Configurable severity levels
- Python 3.8+ support

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Option 1: Install from PyPI (When Published)

Once published to PyPI, you can install it directly:

```bash
pip install python-code-guardian-mcp
```

### Option 2: Install from GitHub

Install directly from the GitHub repository:

```bash
pip install git+https://github.com/priyanshi9692/py-sage-mcp.git
```

### Option 3: Install from Source (Recommended for Local Use)

Clone the repository and install in development mode:

```bash
git clone https://github.com/priyanshi9692/py-sage-mcp.git
cd py-sage-mcp
pip install -e .
```

This allows you to use the MCP server without publishing to PyPI. Changes to the code will be immediately available.

### Option 4: Install with Development Dependencies

For development and testing:

```bash
git clone https://github.com/priyanshi9692/py-sage-mcp.git
cd py-sage-mcp
pip install -e ".[dev]"
```

### Option 5: Use Without Installation (Direct Path)

You can use the MCP server directly without installing by pointing Cursor to the source directory. See the [Quick Start](#-quick-start) section for configuration details.

### Verify Installation

```bash
python-code-guardian --version
python-code-guardian --help
```

**Note:** You don't need to publish to PyPI to use this MCP server. Options 2, 3, and 5 allow you to use it directly from GitHub or your local machine.

## 🎯 Quick Start

### 1. Integrate MCP Server with Cursor IDE

Add the following configuration to your Cursor settings file:

**For global configuration:** `~/.cursor/config.json`

**For workspace configuration:** `.cursor/settings.json` (in your project root)

#### Configuration for Installed Package (Options 1-4)

If you installed the package using any of the installation methods above:

```json
{
  "mcpServers": {
    "python-code-guardian": {
      "command": "python",
      "args": [
        "-m",
        "python_code_guardian.server"
      ]
    }
  }
}
```

**If using a virtual environment**, use the full path to the Python executable:

```json
{
  "mcpServers": {
    "python-code-guardian": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "-m",
        "python_code_guardian.server"
      ]
    }
  }
}
```

#### Configuration for Direct Path (Option 5 - No Installation)

If you want to use the MCP server without installing it, point directly to the source:

```json
{
  "mcpServers": {
    "python-code-guardian": {
      "command": "/path/to/py-sage-mcp/venv/bin/python",
      "args": [
        "-m",
        "python_code_guardian.server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/py-sage-mcp/src"
      }
    }
  }
}
```

**Example with absolute path:**

```json
{
  "mcpServers": {
    "python-code-guardian": {
      "command": "/Users/priyanshijajoo/Desktop/python-code-guardian-mcp/venv/bin/python",
      "args": [
        "-m",
        "python_code_guardian.server"
      ],
      "env": {
        "PYTHONPATH": "/Users/priyanshijajoo/Desktop/python-code-guardian-mcp/src"
      }
    }
  }
}
```

After adding the configuration, restart Cursor IDE to activate the MCP server.

### 2. Use via Cursor IDE Chat

Once configured, you can use the MCP server by asking the AI:
- "Check the code quality of this file"
- "Run code guardian on the current project"
- "Fix linting issues in this function"
- "What's the test coverage of this module?"

### 3. Command Line Usage

```bash
# Check entire project
python-code-guardian check --path ./src

# Check specific file
python-code-guardian check --path ./src/module.py

# Check with specific checks only
python-code-guardian check --path ./src --checks lint complexity

# Check with auto-fix
python-code-guardian check --path ./src --fix

# Get summary report
python-code-guardian check --path ./src --format summary

# Validate PR changes
python-code-guardian validate-pr --pr feature-branch --base main

# Initialize configuration file
python-code-guardian init-config
```

### 4. Setup Pre-commit Hook

```bash
# Install pre-commit if not already installed
pip install pre-commit

# Install the hook
python-code-guardian install-hook

# Test the hook
pre-commit run --all-files
```

## ⚙️ Configuration

Create a `.code-guardian.yaml` file in your project root:

```bash
python-code-guardian init-config
```

Customize the configuration:

```yaml
rules:
  pylint:
    enabled: true
    max_line_length: 100
    disable:
      - C0111  # missing-docstring for specific cases
  
  complexity:
    enabled: true
    max_complexity: 10
    max_function_length: 50
  
  typos:
    enabled: true
    check_variables: true
    check_comments: true
    custom_dictionary:
      - "customword"
      - "anotherterm"
  
  structure:
    enabled: true
    require_docstrings: true
    test_coverage_threshold: 75
    naming_convention: "snake_case"
  
  duplicates:
    enabled: true
    min_lines: 6
    ignore_patterns:
      - "tests/*"
```

## 🛠️ MCP Tools Available

The server exposes the following MCP tools:

### `check_code`
Runs all configured checks on specified files or directories.

**Parameters:**
- `path` (string): File or directory path to check
- `checks` (array, optional): Specific checks to run
- `fix` (boolean, optional): Attempt to auto-fix issues
- `config_path` (string, optional): Path to custom config file

**Example:**
```json
{
  "path": "src/",
  "checks": ["lint", "complexity", "typos"],
  "fix": false
}
```

### `get_report`
Returns detailed analysis report for the last check.

**Parameters:**
- `format` (string): "detailed" or "summary"

### `validate_pr`
Validates all changes in a pull request.

**Parameters:**
- `base_branch` (string): Base branch to compare against
- `pr_branch` (string): PR branch with changes

### `configure_rules`
Updates or views current configuration rules.

**Parameters:**
- `action` (string): "get" or "set"
- `rules` (object): Rules configuration object

### `fix_issues`
Automatically fix detected issues where possible.

**Parameters:**
- `path` (string): File or directory path to fix
- `issue_types` (array): Types of issues to fix

## 📊 Output Format

### Detailed Report

```
================================================================================
CODE QUALITY REPORT
================================================================================

FILE: src/module.py
--------------------------------------------------------------------------------

[ERROR] Line 45, Column 0 - Pylint (C0301)
  Line too long (105/100)
  
[WARNING] Line 78, Column 4 - Complexity (CC=12)
  Function 'process_data' has complexity 12 (max: 10)
  Suggestion: Consider breaking into smaller functions
  
[INFO] Line 12, Column 8 - Typo
  Variable name 'caluculate' might be misspelled
  Suggestion: Did you mean 'calculate'?

[WARNING] Line 25, Column 0 - Duplicates
  Duplicate code block found (6 lines)
  Also in: src/other_module.py:line 45
  Suggestion: Extract to a shared function

--------------------------------------------------------------------------------
SUMMARY STATISTICS
--------------------------------------------------------------------------------
Files Checked: 15
Total Issues: 23
  - Errors: 5
  - Warnings: 12
  - Info: 6

Test Coverage: 78.5% ✓

Issues by Category:
  - Linting: 8
  - Complexity: 5
  - Typos: 3
  - Structure: 4
  - Duplicates: 3
================================================================================
```

## 🎨 Custom Rules

Create custom rules by extending the base checker:

```python
# custom_rules.py
from python_code_guardian.checkers import BaseChecker

class MyCustomChecker(BaseChecker):
    async def check(self, file_path, config):
        issues = []
        # Your custom logic
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                if 'TODO' in line:
                    issues.append(self.create_issue(
                        file_path=file_path,
                        line=i,
                        column=0,
                        severity="info",
                        code="TODO-CHECK",
                        message="TODO comment found",
                        suggestion="Consider creating a ticket"
                    ))
        return {"issues": issues}
```

Register in `.code-guardian.yaml`:

```yaml
custom_checkers:
  - path: ./custom_rules.py
    class: MyCustomChecker
```

## 🔧 CI/CD Integration

### GitHub Actions

Add to your `.github/workflows/ci.yml`:

```yaml
- name: Check code quality
  run: python-code-guardian check --path ./src
```

## 🆘 Troubleshooting

### "pylint not found"
```bash
pip install pylint
```

### "Coverage check failed"
```bash
pip install coverage pytest-cov
```

### "Permission denied"
```bash
pip install --user python-code-guardian-mcp
```

### MCP Server Not Working in Cursor

1. Verify the configuration JSON is correct
2. Check that Python path is correct (especially for virtual environments)
3. Restart Cursor IDE after configuration changes
4. Check Cursor's MCP server logs for errors

### Python Version Issues

Ensure you're using Python 3.8+:

```bash
python --version
# If using Python 3, might need to use python3
python3 --version
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 Documentation: [README](https://github.com/priyanshi9692/py-sage-mcp/blob/main/README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/priyanshi9692/py-sage-mcp/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/priyanshi9692/py-sage-mcp/discussions)

## 🙏 Acknowledgments

Built with:
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [Pylint](https://pylint.org)
- [Radon](https://radon.readthedocs.io)
- [Codespell](https://github.com/codespell-project/codespell)
- [Coverage.py](https://coverage.readthedocs.io)

---

Made with ❤️ for the global Python community
