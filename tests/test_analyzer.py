import unittest
import sys
import os

from coderevitalize.analyzer import analyze_code

class TestAnalyzer(unittest.TestCase):

    def test_function_with_many_args(self):
        code = "def too_many_args(a, b, c, d, e, f): pass"
        findings = analyze_code(code, max_args=5)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['function_name'], 'too_many_args')
        self.assertEqual(findings[0]['value'], 6) # Changed from num_args to value

    def test_function_with_ok_args(self):
        code = "def ok_args(a, b, c): pass"
        findings = analyze_code(code, max_args=5)
        self.assertEqual(len(findings), 0)

    def test_method_with_many_args(self):
        code = "class MyClass:\n    def too_many_args(self, a, b, c, d, e, f): pass"
        findings = analyze_code(code, max_args=5)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['function_name'], 'too_many_args')
        self.assertEqual(findings[0]['value'], 6) # Changed from num_args to value

    def test_method_with_ok_args(self):
        code = "class MyClass:\n    def ok_args(self, a, b, c): pass"
        findings = analyze_code(code, max_args=5)
        self.assertEqual(len(findings), 0)

    def test_empty_code(self):
        findings = analyze_code("", max_args=5)
        self.assertEqual(len(findings), 0)

    def test_no_functions(self):
        code = "a = 1\nb = 2"
        findings = analyze_code(code, max_args=5)
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
        findings = analyze_code(code, max_complexity=3)
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
        findings = analyze_code(code, max_complexity=5)
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
        findings = analyze_code(code, max_complexity=2)
        complexity_findings = [f for f in findings if f['type'] == 'complexity']
        self.assertEqual(len(complexity_findings), 0)

        findings = analyze_code(code, max_complexity=1)
        complexity_findings = [f for f in findings if f['type'] == 'complexity']
        self.assertEqual(len(complexity_findings), 1)
        self.assertEqual(complexity_findings[0]['value'], 2)

if __name__ == '__main__':
    unittest.main()
