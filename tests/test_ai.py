import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import os
import sys
from coderevitalize.cli import main

class TestAICommands(unittest.TestCase):
    @patch('coderevitalize.analyzer.get_ai_response')
    @patch('sys.stdout', new_callable=StringIO)
    def test_explain_command(self, mock_stdout, mock_get_ai_response):
        mock_get_ai_response.return_value = "This is a test explanation."

        with open("test.py", "w") as f:
            f.write("print('hello')")

        main(['explain', 'test.py'])

        self.assertIn("This is a test explanation.", mock_stdout.getvalue())

        os.remove("test.py")

    @patch('coderevitalize.cli.get_ai_response')
    @patch('sys.stdout', new_callable=StringIO)
    def test_write_command(self, mock_stdout, mock_get_ai_response):
        mock_get_ai_response.return_value = "print('generated code')"

        main(['write', 'create a hello world script'])

        self.assertIn("print('generated code')", mock_stdout.getvalue())

    @patch('coderevitalize.cli.get_ai_response')
    def test_write_command_with_output_file(self, mock_get_ai_response):
        mock_get_ai_response.return_value = "print('generated code')"

        main(['write', 'create a hello world script', '-o', 'test.py'])

        with open("test.py", "r") as f:
            self.assertEqual(f.read(), "print('generated code')")

        os.remove("test.py")

if __name__ == '__main__':
    unittest.main()
