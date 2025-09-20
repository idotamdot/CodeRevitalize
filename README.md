"# CodeRevitalize

A Python tool to analyze code for "aged" or inefficient patterns, helping you identify and improve code quality.

## Features

CodeRevitalize analyzes Python source code to detect:

- **Too Many Arguments**: Functions with excessive parameters that may be hard to maintain
- **Long Functions**: Functions that are too lengthy and should be broken down  
- **High Cyclomatic Complexity**: Functions with complex control flow that are difficult to understand and test

## Installation

### From Source

```bash
git clone https://github.com/idotamdot/CodeRevitalize.git
cd CodeRevitalize
pip install -e .
```

### Dependencies

- Python 3.6+
- radon (for complexity analysis)

## Usage

### Command Line Interface

Analyze a single Python file:
```bash
coderevitalize path/to/your/file.py
```

Analyze an entire directory:
```bash
coderevitalize path/to/your/project/
```

### Configuration Options

- `--max-args`: Maximum number of function arguments allowed (default: 5)
- `--max-complexity`: Maximum cyclomatic complexity allowed (default: 10)  
- `--max-lines`: Maximum number of lines per function (default: 50)
- `--format`: Output format - 'text' or 'json' (default: text)

### Examples

```bash
# Use stricter limits
coderevitalize mycode.py --max-args 3 --max-complexity 5 --max-lines 20

# Get JSON output for integration with other tools
coderevitalize myproject/ --format json

# Analyze with custom thresholds
coderevitalize src/ --max-args 4 --max-complexity 8 --max-lines 30
```

### Sample Output

Text format:
```
--- Findings in example.py ---
  Line 10: Function 'process_data' has 6 arguments, which is more than the allowed 5.
  Line 25: Function 'complex_algorithm' has a cyclomatic complexity of 12, which is more than the allowed 10.
  Line 50: Function 'long_function' has 55 lines, which is more than the allowed 50.
--------------------------------
```

JSON format:
```json
{
  "example.py": [
    {
      "type": "argument_count",
      "function_name": "process_data", 
      "line_number": 10,
      "value": 6,
      "message": "Function 'process_data' has 6 arguments, which is more than the allowed 5."
    },
    {
      "type": "complexity",
      "function_name": "complex_algorithm",
      "line_number": 25, 
      "value": 12,
      "message": "Function 'complex_algorithm' has a cyclomatic complexity of 12, which is more than the allowed 10."
    }
  ]
}
```

## Exit Codes

- `0`: No issues found
- `1`: Issues found in the analyzed code

## API Usage

You can also use CodeRevitalize as a Python library:

```python
from coderevitalize.analyzer import analyze_code

# Analyze some source code
source_code = """
def example_function(a, b, c, d, e, f):
    if a > b:
        if c > d:
            return e + f
    return 0
"""

findings = analyze_code(source_code, max_args=4, max_complexity=5, max_lines=10)
for finding in findings:
    print(f"{finding['type']}: {finding['message']}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests: `python -m unittest discover tests`
5. Submit a pull request

## License

MIT License

## Development

To run tests:
```bash
python -m unittest discover tests -v
```

To install in development mode:
```bash
pip install -e .
```" 
