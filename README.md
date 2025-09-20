"# CodeRevitalize

A comprehensive Python code analysis tool that identifies "aged" or inefficient patterns in your codebase. CodeRevitalize helps you maintain code quality by detecting various issues and providing actionable insights to improve your Python projects.

## Features

- **Function Analysis**: Detect functions with too many arguments, excessive length, or high cyclomatic complexity
- **Code Quality Checks**: Identify unused imports, missing docstrings, magic numbers, and TODO/FIXME comments
- **Flexible Configuration**: Customize thresholds and rules via command-line options or configuration files
- **Multiple Output Formats**: Choose between human-readable text output or structured JSON for integration
- **Directory Scanning**: Analyze entire projects or individual files
- **Severity Levels**: Prioritize fixes with severity-based reporting

## Installation

### From Source
```bash
git clone https://github.com/idotamdot/CodeRevitalize.git
cd CodeRevitalize
pip install -e .
```

### Using pip (when published)
```bash
pip install coderevitalize
```

## Quick Start

### Analyze a single file
```bash
coderevitalize path/to/your/file.py
```

### Analyze an entire project
```bash
coderevitalize path/to/your/project/
```

### Customize thresholds
```bash
coderevitalize src/ --max-args 3 --max-complexity 8 --max-lines 30
```

### Get JSON output for integration
```bash
coderevitalize src/ --format json > analysis_results.json
```

## Example Output

### Text Format
```
--- Findings in src/example.py ---
  Line 15: [HIGH] Function 'process_data' has 8 arguments, which is more than the allowed 5.
  Line 42: [MEDIUM] Function 'calculate_metrics' has 65 lines, which is more than the allowed 50.
  Line 3: [LOW] Missing docstring for function 'helper_function'.
  Line 28: [LOW] Magic number 42 found. Consider using a named constant.
---------------------------------

Summary: 4 issues found (1 high, 1 medium, 2 low severity)
```

### JSON Format
```json
{
  "src/example.py": [
    {
      "type": "argument_count",
      "function_name": "process_data",
      "line_number": 15,
      "value": 8,
      "severity": "high",
      "message": "Function 'process_data' has 8 arguments, which is more than the allowed 5.",
      "suggestion": "Consider grouping related parameters into a class or dictionary."
    }
  ]
}
```

## Configuration

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-args` | 5 | Maximum number of function arguments |
| `--max-complexity` | 10 | Maximum cyclomatic complexity |
| `--max-lines` | 50 | Maximum function length in lines |
| `--format` | text | Output format (text or json) |
| `--config` | None | Path to configuration file |
| `--exclude` | None | File patterns to exclude |
| `--include` | "*.py" | File patterns to include |

### Configuration File

Create a `.coderevitalize.yaml` file in your project root:

```yaml
# Analysis thresholds
max_args: 5
max_complexity: 10
max_lines: 50

# File patterns
include: ["*.py"]
exclude: 
  - "*/migrations/*"
  - "*/venv/*"
  - "*/node_modules/*"
  - "*_test.py"

# Quality checks
checks:
  unused_imports: true
  missing_docstrings: true
  magic_numbers: true
  todo_comments: true

# Severity levels
severity:
  argument_count: high
  complexity: high
  function_length: medium
  unused_imports: low
  missing_docstrings: low
  magic_numbers: low
  todo_comments: info
```

## Detected Issues

### Function Quality
- **Too Many Arguments**: Functions with excessive parameters are hard to use and test
- **Long Functions**: Large functions are difficult to understand and maintain
- **High Complexity**: Complex functions with many decision points are error-prone

### Code Quality
- **Unused Imports**: Dead code that should be removed
- **Missing Docstrings**: Functions without documentation
- **Magic Numbers**: Hardcoded values that should be named constants
- **TODO/FIXME Comments**: Incomplete work that needs attention

## Integration

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Code Quality Analysis
  run: |
    pip install coderevitalize
    coderevitalize src/ --format json > analysis.json
    # Fail build if high severity issues found
    python scripts/check_analysis.py analysis.json
```

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: coderevitalize
        name: CodeRevitalize Analysis
        entry: coderevitalize
        language: system
        args: [--max-args=4, --max-complexity=8]
```

## Development

### Running Tests
```bash
python -m unittest discover tests/ -v
```

### Adding New Analyzers
1. Create a new analyzer class in `src/coderevitalize/analyzer.py`
2. Implement the `ast.NodeVisitor` pattern
3. Add corresponding tests in `tests/test_analyzer.py`
4. Update the `analyze_code` function to include your analyzer

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`python -m unittest discover tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Why CodeRevitalize?

Modern software development moves fast, and code quality can degrade over time. CodeRevitalize helps you:

- **Maintain Consistency**: Enforce coding standards across your team
- **Reduce Technical Debt**: Identify problematic patterns before they become legacy issues
- **Improve Readability**: Ensure code is easy to understand and maintain
- **Enhance Testability**: Promote better function design and lower complexity
- **Save Review Time**: Automate quality checks that would otherwise be manual

Think of CodeRevitalize as your code's health check-up tool - helping you keep your Python projects clean, maintainable, and efficient." 
