import ast
import re
from radon.visitors import ComplexityVisitor
from .ai import get_ai_response

class ArgumentCountAnalyzer(ast.NodeVisitor):
    """
    Analyzes Python source code to find functions with too many arguments.
    """

    def __init__(self, max_args=5):
        self.max_args = max_args
        self.findings = []

    def visit_FunctionDef(self, node):
        args = node.args.args
        num_args = len(args)
        is_method = False

        if args and args[0].arg == 'self':
            num_args -= 1
            is_method = True

        if num_args > self.max_args:
            message = f"Function '{node.name}' has {num_args} arguments"
            if is_method:
                message += " (excluding self)"
            message += f", which is more than the allowed {self.max_args}."

            self.findings.append({
                "type": "argument_count",
                "function_name": node.name,
                "line_number": node.lineno,
                "value": num_args,
                "severity": "high",
                "message": message,
                "suggestion": "Consider grouping related parameters into a class or dictionary."
            })
        self.generic_visit(node)

class FunctionLengthAnalyzer(ast.NodeVisitor):
    """
    Analyzes Python source code to find functions that are too long.
    """

    def __init__(self, max_lines=50):
        self.max_lines = max_lines
        self.findings = []

    def visit_FunctionDef(self, node):
        # This requires Python 3.8+ for end_lineno
        if hasattr(node, 'end_lineno'):
            num_lines = node.end_lineno - node.lineno + 1
            if num_lines > self.max_lines:
                self.findings.append({
                    "type": "function_length",
                    "function_name": node.name,
                    "line_number": node.lineno,
                    "value": num_lines,
                    "severity": "medium",
                    "message": f"Function '{node.name}' has {num_lines} lines, which is more than the allowed {self.max_lines}.",
                    "suggestion": "Consider breaking this function into smaller, more focused functions."
                })
        self.generic_visit(node)


class UnusedImportAnalyzer(ast.NodeVisitor):
    """
    Analyzes Python source code to find unused imports.
    """

    def __init__(self):
        self.imports = {}  # {name: line_number}
        self.used_names = set()
        self.findings = []

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = node.lineno

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = node.lineno

    def visit_Name(self, node):
        self.used_names.add(node.id)

    def visit_Attribute(self, node):
        # For cases like os.path, we need to track the base name
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)

    def finalize(self):
        """Call this after visiting the entire tree to generate findings."""
        for name, line_number in self.imports.items():
            if name not in self.used_names and name != '*':
                self.findings.append({
                    "type": "unused_imports",
                    "function_name": None,
                    "line_number": line_number,
                    "value": name,
                    "severity": "low",
                    "message": f"Unused import '{name}' found.",
                    "suggestion": "Remove this unused import to clean up the code."
                })


class MissingDocstringAnalyzer(ast.NodeVisitor):
    """
    Analyzes Python source code to find functions missing docstrings.
    """

    def __init__(self):
        self.findings = []

    def visit_FunctionDef(self, node):
        # Check if function has a docstring
        has_docstring = (
            node.body and 
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)
        )
        
        # Skip private functions (starting with _) unless they're special methods
        if not has_docstring and not (node.name.startswith('_') and not node.name.startswith('__')):
            self.findings.append({
                "type": "missing_docstrings", 
                "function_name": node.name,
                "line_number": node.lineno,
                "value": node.name,
                "severity": "low",
                "message": f"Missing docstring for function '{node.name}'.",
                "suggestion": "Add a docstring to describe what this function does."
            })
        self.generic_visit(node)


class MagicNumberAnalyzer(ast.NodeVisitor):
    """
    Analyzes Python source code to find magic numbers.
    """

    def __init__(self):
        self.findings = []
        self.allowed_numbers = {0, 1, -1, 2}  # Common acceptable numbers

    def visit_Constant(self, node):
        if (isinstance(node.value, (int, float)) and 
            node.value not in self.allowed_numbers and
            not isinstance(node.value, bool)):  # Exclude True/False
            self.findings.append({
                "type": "magic_numbers",
                "function_name": None,
                "line_number": node.lineno,
                "value": node.value,
                "severity": "low", 
                "message": f"Magic number {node.value} found.",
                "suggestion": "Consider using a named constant instead of a magic number."
            })
        self.generic_visit(node)


class TodoCommentAnalyzer:
    """
    Analyzes Python source code to find TODO/FIXME comments.
    """

    def __init__(self):
        self.findings = []

    def analyze(self, source_code):
        """Analyze source code for TODO/FIXME comments."""
        lines = source_code.split('\n')
        todo_pattern = re.compile(r'#.*\b(TODO|FIXME|HACK|XXX|OPTIMIZE)\b', re.IGNORECASE)
        
        for line_num, line in enumerate(lines, 1):
            match = todo_pattern.search(line)
            if match:
                keyword = match.group(1).upper()
                self.findings.append({
                    "type": "todo_comments",
                    "function_name": None,
                    "line_number": line_num,
                    "value": keyword,
                    "severity": "info",
                    "message": f"{keyword} comment found: {line.strip()}",
                    "suggestion": "Consider addressing this comment or creating a proper issue/task."
                })

def analyze_complexity(source_code, max_complexity=10):
    """
    Analyzes the given source code for cyclomatic complexity.
    """
    findings = []
    try:
        visitor = ComplexityVisitor.from_code(source_code)
        for function in visitor.functions:
            if function.complexity > max_complexity:
                findings.append({
                    "type": "complexity",
                    "function_name": function.name,
                    "line_number": function.lineno,
                    "value": function.complexity,
                    "severity": "high",
                    "message": f"Function '{function.name}' has a cyclomatic complexity of {function.complexity}, which is more than the allowed {max_complexity}.",
                    "suggestion": "Consider breaking this function into smaller functions or simplifying the logic."
                })
    except Exception:
        # Radon can fail on some code, so we ignore errors for now.
        pass
    return findings

def analyze_code(source_code, max_args=5, max_complexity=10, max_lines=50, config=None):
    """
    Analyzes the given source code for various issues and returns a list of findings.
    """
    all_findings = []

    # Use config if provided, otherwise use defaults
    if config:
        max_args = config.max_args
        max_complexity = config.max_complexity
        max_lines = config.max_lines

    # AST-based analysis (argument count, function length)
    try:
        tree = ast.parse(source_code)

        arg_analyzer = ArgumentCountAnalyzer(max_args=max_args)
        arg_analyzer.visit(tree)
        all_findings.extend(arg_analyzer.findings)

        length_analyzer = FunctionLengthAnalyzer(max_lines=max_lines)
        length_analyzer.visit(tree)
        all_findings.extend(length_analyzer.findings)

        # New analyzers
        if not config or config.checks.get("unused_imports", True):
            import_analyzer = UnusedImportAnalyzer()
            import_analyzer.visit(tree)
            import_analyzer.finalize()
            all_findings.extend(import_analyzer.findings)

        if not config or config.checks.get("missing_docstrings", True):
            docstring_analyzer = MissingDocstringAnalyzer()
            docstring_analyzer.visit(tree)
            all_findings.extend(docstring_analyzer.findings)

        if not config or config.checks.get("magic_numbers", True):
            magic_analyzer = MagicNumberAnalyzer()
            magic_analyzer.visit(tree)
            all_findings.extend(magic_analyzer.findings)

    except SyntaxError as e:
        all_findings.append({
            "type": "syntax_error",
            "function_name": None,
            "line_number": e.lineno,
            "value": None,
            "severity": "critical",
            "message": f"Invalid syntax: {e.msg}",
            "suggestion": "Fix the syntax error before running other analyses."
        })
        # If syntax is invalid, we can't proceed with other analyses
        return all_findings

    # Complexity analysis
    all_findings.extend(analyze_complexity(source_code, max_complexity))

    # TODO comment analysis
    if not config or config.checks.get("todo_comments", True):
        todo_analyzer = TodoCommentAnalyzer()
        todo_analyzer.analyze(source_code)
        all_findings.extend(todo_analyzer.findings)

    # Apply severity levels from config if provided
    if config and config.severity:
        for finding in all_findings:
            finding_type = finding["type"]
            if finding_type in config.severity:
                finding["severity"] = config.severity[finding_type]

    return all_findings

def explain_code(source_code, language="Python"):
    """
    Uses an AI to explain the given source code.
    """
    prompt = f"Explain the following {language} code:\n\n```{language.lower()}\n{source_code}\n```"
    return get_ai_response(prompt)
