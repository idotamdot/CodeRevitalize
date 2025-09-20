import unittest
import subprocess
import json
import os
import tempfile
import sys

class TestCli(unittest.TestCase):

    def setUp(self):
        # Create a temporary file with some code that will trigger findings
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py')
        self.temp_file.write('''
def a_function_with_too_many_args(a, b, c, d, e, f):
    pass

def another_long_function():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
''')
        self.temp_file.close()
        
        # Create a config file that disables new analyzers for backward compatibility
        self.config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
        self.config_file.write('''
checks:
  unused_imports: false
  missing_docstrings: false
  magic_numbers: false
  todo_comments: false
''')
        self.config_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)
        os.unlink(self.config_file.name)

    def test_json_output(self):
        # The path to the executable might need adjustment depending on how the package is installed
        # For a simple project structure, we can call it as a module
        command = [
            sys.executable, '-m', 'coderevitalize.cli',
            self.temp_file.name,
            '--format=json',
            '--max-args=5',
            '--max-lines=5',
            '--config=' + self.config_file.name
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        # The tool should exit with 1 because it found issues
        self.assertEqual(result.returncode, 1)

        try:
            output_json = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("Output was not valid JSON.")

        # Check the structure of the JSON (new format with files and summary)
        self.assertIn('files', output_json)
        self.assertIn('summary', output_json)
        self.assertIn(self.temp_file.name, output_json['files'])
        findings = output_json['files'][self.temp_file.name]
        
        # We might have more findings now due to new analyzers
        self.assertGreaterEqual(len(findings), 2)

        # Check for the specific findings (order might not be guaranteed)
        arg_finding = next((f for f in findings if f['type'] == 'argument_count'), None)
        len_finding = next((f for f in findings if f['type'] == 'function_length'), None)

        self.assertIsNotNone(arg_finding)
        self.assertEqual(arg_finding['function_name'], 'a_function_with_too_many_args')
        self.assertEqual(arg_finding['value'], 6)

        self.assertIsNotNone(len_finding)
        self.assertEqual(len_finding['function_name'], 'another_long_function')
        self.assertEqual(len_finding['value'], 7)
        
        # Check summary structure
        summary = output_json['summary']
        self.assertIn('total_issues', summary)
        self.assertIn('by_severity', summary)
        self.assertIn('by_type', summary)
        self.assertGreaterEqual(summary['total_issues'], 2)

if __name__ == '__main__':
    unittest.main()
