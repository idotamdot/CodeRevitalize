import unittest
import sys
import os

from coderevitalize.analyzer import analyze_code
from coderevitalize.config import Config

class TestAnalyzer(unittest.TestCase):

    def get_basic_config(self, max_args=5, max_complexity=10, max_lines=50):
        """Get a config that disables new analyzers for backward compatibility."""
        config = Config()
        config.max_args = max_args
        config.max_complexity = max_complexity
        config.max_lines = max_lines
        config.checks = {
            "unused_imports": False,
            "missing_docstrings": False,
            "magic_numbers": False,
            "todo_comments": False
        }
        return config

    def test_function_with_many_args(self):
        code = "def too_many_args(a, b, c, d, e, f): pass"
        findings = analyze_code(code, config=self.get_basic_config(max_args=5))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['function_name'], 'too_many_args')
        self.assertEqual(findings[0]['value'], 6) # Changed from num_args to value

    def test_function_with_ok_args(self):
        code = "def ok_args(a, b, c): pass"
        findings = analyze_code(code, config=self.get_basic_config(max_args=5))
        self.assertEqual(len(findings), 0)

    def test_method_with_many_args(self):
        code = "class MyClass:\n    def too_many_args(self, a, b, c, d, e, f): pass"
        findings = analyze_code(code, config=self.get_basic_config(max_args=5))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['function_name'], 'too_many_args')
        self.assertEqual(findings[0]['value'], 6) # Changed from num_args to value

    def test_method_with_ok_args(self):
        code = "class MyClass:\n    def ok_args(self, a, b, c): pass"
        findings = analyze_code(code, config=self.get_basic_config(max_args=5))
        self.assertEqual(len(findings), 0)

    def test_empty_code(self):
        findings = analyze_code("", config=self.get_basic_config(max_args=5))
        self.assertEqual(len(findings), 0)

    def test_no_functions(self):
        code = "a = 1\nb = 2"
        findings = analyze_code(code, config=self.get_basic_config(max_args=5))
        self.assertEqual(len(findings), 0)

    def test_cyclomatic_complexity_high(self):
        code = '''
def high_complexity_function(a, b, c):
    if a > b:
        if b > c:
            return 1
        else:
            return 2
    else:
        if b < c:
            return 3
        else:
            return 4
'''
        # The complexity of this function is 4, let's test with a low threshold
        findings = analyze_code(code, config=self.get_basic_config(max_complexity=3))
        # We only expect one finding, which is the complexity one
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['type'], 'complexity')
        self.assertEqual(findings[0]['function_name'], 'high_complexity_function')
        self.assertEqual(findings[0]['value'], 4)

    def test_cyclomatic_complexity_low(self):
        code = '''
def low_complexity_function(a, b, c):
    return a + b + c
'''
        findings = analyze_code(code, config=self.get_basic_config(max_complexity=5))
        # Filter for complexity findings
        complexity_findings = [f for f in findings if f['type'] == 'complexity']
        self.assertEqual(len(complexity_findings), 0)

    def test_cyclomatic_complexity_edge(self):
        code = '''
def edge_complexity_function(a, b):
    if a > b:
        return 1
    else:
        return 2
'''
        # The complexity is 2
        findings = analyze_code(code, config=self.get_basic_config(max_complexity=2))
        complexity_findings = [f for f in findings if f['type'] == 'complexity']
        self.assertEqual(len(complexity_findings), 0)

        findings = analyze_code(code, config=self.get_basic_config(max_complexity=1))
        complexity_findings = [f for f in findings if f['type'] == 'complexity']
        self.assertEqual(len(complexity_findings), 1)
        self.assertEqual(complexity_findings[0]['value'], 2)

    def test_function_length_long(self):
        # This function is 5 lines long from def to last statement
        code = '''
def long_function():
    a = 1
    b = 2
    c = 3
    d = 4
'''
        findings = analyze_code(code, config=self.get_basic_config(max_lines=4))
        length_findings = [f for f in findings if f['type'] == 'function_length']
        self.assertEqual(len(length_findings), 1)
        self.assertEqual(length_findings[0]['function_name'], 'long_function')
        self.assertEqual(length_findings[0]['value'], 5)

    def test_function_length_ok(self):
        code = '''
def ok_function():
    a = 1
'''
        findings = analyze_code(code, config=self.get_basic_config(max_lines=5))
        length_findings = [f for f in findings if f['type'] == 'function_length']
        self.assertEqual(len(length_findings), 0)

    def test_unused_imports(self):
        code = '''
import os
import sys
import unused_module

def use_os():
    return os.path.join('a', 'b')
'''
        config = Config()
        config.checks = {
            "unused_imports": True,
            "missing_docstrings": False,
            "magic_numbers": False,
            "todo_comments": False
        }
        findings = analyze_code(code, config=config)
        unused_findings = [f for f in findings if f['type'] == 'unused_imports']
        self.assertEqual(len(unused_findings), 2)  # sys and unused_module
        unused_names = {f['value'] for f in unused_findings}
        self.assertIn('sys', unused_names)
        self.assertIn('unused_module', unused_names)

    def test_missing_docstrings(self):
        code = '''
def function_without_docstring():
    return "test"

def function_with_docstring():
    """This function has a docstring."""
    return "test"
'''
        config = Config()
        config.checks = {
            "unused_imports": False,
            "missing_docstrings": True,
            "magic_numbers": False,
            "todo_comments": False
        }
        findings = analyze_code(code, config=config)
        docstring_findings = [f for f in findings if f['type'] == 'missing_docstrings']
        self.assertEqual(len(docstring_findings), 1)
        self.assertEqual(docstring_findings[0]['function_name'], 'function_without_docstring')

    def test_magic_numbers(self):
        code = '''
def function_with_magic_numbers():
    value = 42
    pi = 3.14159
    return value + pi + 1  # 1 is allowed
'''
        config = Config()
        config.checks = {
            "unused_imports": False,
            "missing_docstrings": False,
            "magic_numbers": True,
            "todo_comments": False
        }
        findings = analyze_code(code, config=config)
        magic_findings = [f for f in findings if f['type'] == 'magic_numbers']
        self.assertEqual(len(magic_findings), 2)  # 42 and 3.14159
        magic_values = {f['value'] for f in magic_findings}
        self.assertIn(42, magic_values)
        self.assertIn(3.14159, magic_values)

    def test_todo_comments(self):
        code = '''
def function_with_todos():
    # TODO: Implement this properly
    # FIXME: This is broken
    # HACK: Temporary solution
    return "placeholder"
'''
        config = Config()
        config.checks = {
            "unused_imports": False,
            "missing_docstrings": False,
            "magic_numbers": False,
            "todo_comments": True
        }
        findings = analyze_code(code, config=config)
        todo_findings = [f for f in findings if f['type'] == 'todo_comments']
        self.assertEqual(len(todo_findings), 3)  # TODO, FIXME, HACK
        todo_types = {f['value'] for f in todo_findings}
        self.assertIn('TODO', todo_types)
        self.assertIn('FIXME', todo_types)
        self.assertIn('HACK', todo_types)


if __name__ == '__main__':
    unittest.main()
