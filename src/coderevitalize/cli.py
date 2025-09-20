import argparse
import os
import sys

from coderevitalize.analyzer import analyze_code
from coderevitalize.formatters import get_formatter

def main():
    parser = argparse.ArgumentParser(description="Analyze Python code for 'aged' or inefficient patterns.")
    parser.add_argument("path", help="Path to the Python file or directory to analyze.")
    parser.add_argument("--max-args", type=int, default=5, help="The maximum number of arguments a function can have.")
    parser.add_argument("--max-complexity", type=int, default=10, help="The maximum cyclomatic complexity a function can have.")
    parser.add_argument("--max-lines", type=int, default=50, help="The maximum number of lines a function can have.")
    parser.add_argument("--format", choices=['text', 'json'], default='text', help="The output format.")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    all_findings = {}

    if os.path.isfile(args.path):
        filepath = args.path
        findings = process_file(filepath, args.max_args, args.max_complexity, args.max_lines)
        if findings:
            all_findings[filepath] = findings
    elif os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    findings = process_file(filepath, args.max_args, args.max_complexity, args.max_lines)
                    if findings:
                        all_findings[filepath] = findings

    formatter = get_formatter(args.format)
    formatter.display(all_findings)

    if all_findings:
        sys.exit(1)

def process_file(filepath, max_args, max_complexity, max_lines):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source_code = f.read()

        return analyze_code(
            source_code,
            max_args=max_args,
            max_complexity=max_complexity,
            max_lines=max_lines
        )
    except Exception as e:
        print(f"Error processing file {filepath}: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    main()
