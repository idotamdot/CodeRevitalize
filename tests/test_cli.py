import unittest
from unittest.mock import patch, MagicMock
import json
import os
import tempfile
import sys
from io import StringIO
from coderevitalize.cli import main

class TestCli(unittest.TestCase):
    def setUp(self):
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

    def tearDown(self):
        os.unlink(self.temp_file.name)

    @patch('sys.stdout', new_callable=StringIO)
    def test_json_output(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            main([
                'analyze', self.temp_file.name,
                '--format=json',
                '--max-args=5',
                '--max-lines=5'
            ])
        self.assertEqual(cm.exception.code, 1)

        output = mock_stdout.getvalue()
        try:
            output_json = json.loads(output)
        except json.JSONDecodeError:
            self.fail("Output was not valid JSON.")

        self.assertIn(self.temp_file.name, output_json)
        findings = output_json[self.temp_file.name]
        self.assertEqual(len(findings), 2)

        arg_finding = next((f for f in findings if f['type'] == 'argument_count'), None)
        len_finding = next((f for f in findings if f['type'] == 'function_length'), None)

        self.assertIsNotNone(arg_finding)
        self.assertEqual(arg_finding['function_name'], 'a_function_with_too_many_args')
        self.assertEqual(arg_finding['value'], 6)

        self.assertIsNotNone(len_finding)
        self.assertEqual(len_finding['function_name'], 'another_long_function')
        self.assertEqual(len_finding['value'], 7)

if __name__ == '__main__':
    unittest.main()
