# CodeRevitalize

A tool to analyze, explain, and write code, helping you identify and improve code quality.

## Features

- **Analyze Code**: Detects "aged" or inefficient patterns in Python code.
- **Explain Code**: Uses AI to explain code in any programming language.
- **Write Code**: Generates new code from a natural language description.

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
- openai

## Usage

### Command Line Interface

#### Analyzing Code

Analyze a single Python file:
```bash
coderevitalize analyze path/to/your/file.py
```

Analyze an entire directory:
```bash
coderevitalize analyze path/to/your/project/
```

**Configuration Options:**

- `--max-args`: Maximum number of function arguments allowed (default: 5)
- `--max-complexity`: Maximum cyclomatic complexity allowed (default: 10)  
- `--max-lines`: Maximum number of lines per function (default: 50)
- `--format`: Output format - 'text' or 'json' (default: text)

#### Explaining Code

Explain a source file:
```bash
coderevitalize explain path/to/your/file.py --language "JavaScript"
```

#### Writing Code

Generate a new script:
```bash
coderevitalize write "create a hello world script in Python" --output "hello_world.py"
```

### Examples

```bash
# Use stricter limits for analysis
coderevitalize analyze mycode.py --max-args 3 --max-complexity 5 --max-lines 20

# Get JSON output for integration with other tools
coderevitalize analyze myproject/ --format json
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
```
