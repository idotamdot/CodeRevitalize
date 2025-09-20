import ast
from radon.visitors import ComplexityVisitor

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
                "message": message
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
                    "message": f"Function '{node.name}' has {num_lines} lines, which is more than the allowed {self.max_lines}."
                })
        self.generic_visit(node)

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
                    "message": f"Function '{function.name}' has a cyclomatic complexity of {function.complexity}, which is more than the allowed {max_complexity}."
                })
    except Exception:
        # Radon can fail on some code, so we ignore errors for now.
        pass
    return findings

def analyze_code(source_code, max_args=5, max_complexity=10, max_lines=50):
    """
    Analyzes the given source code for various issues and returns a list of findings.
    """
    all_findings = []

    # AST-based analysis (argument count, function length)
    try:
        tree = ast.parse(source_code)

        arg_analyzer = ArgumentCountAnalyzer(max_args=max_args)
        arg_analyzer.visit(tree)
        all_findings.extend(arg_analyzer.findings)

        length_analyzer = FunctionLengthAnalyzer(max_lines=max_lines)
        length_analyzer.visit(tree)
        all_findings.extend(length_analyzer.findings)

    except SyntaxError as e:
        all_findings.append({
            "type": "syntax_error",
            "function_name": None,
            "line_number": e.lineno,
            "value": None,
            "message": f"Invalid syntax: {e.msg}"
        })
        # If syntax is invalid, we can't proceed with other analyses
        return all_findings

    # Complexity analysis
    all_findings.extend(analyze_complexity(source_code, max_complexity))

    return all_findings
