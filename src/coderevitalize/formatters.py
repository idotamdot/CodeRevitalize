import json

class BaseFormatter:
    def display(self, findings_by_file):
        raise NotImplementedError

class TextFormatter(BaseFormatter):
    def display(self, findings_by_file):
        for filepath, findings in findings_by_file.items():
            if findings:
                print(f"--- Findings in {filepath} ---")
                for finding in findings:
                    if finding['line_number']:
                        print(f"  Line {finding['line_number']}: {finding['message']}")
                    else:
                        print(f"  {finding['message']}")
                print("-" * (len(filepath) + 18))

class JsonFormatter(BaseFormatter):
    def display(self, findings_by_file):
        print(json.dumps(findings_by_file, indent=2))

def get_formatter(format_name):
    if format_name == 'text':
        return TextFormatter()
    elif format_name == 'json':
        return JsonFormatter()
    else:
        # This should be caught by argparse choices, but as a fallback:
        raise ValueError(f"Unknown format: {format_name}")
