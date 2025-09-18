import argparse
import os
import sys

from coderevitalize.analyzer import analyze_code

def main():
    parser = argparse.ArgumentParser(description="Analyze Python code for 'aged' or inefficient patterns.")
    parser.add_argument("path", help="Path to the Python file or directory to analyze.")
    parser.add_argument("--max-args", type=int, default=5, help="The maximum number of arguments a function can have.")
    parser.add_argument("--max-complexity", type=int, default=10, help="The maximum cyclomatic complexity a function can have.")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)

    if os.path.isfile(args.path):
        process_file(args.path, args.max_args, args.max_complexity)
    elif os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(".py"):
                    process_file(os.path.join(root, file), args.max_args, args.max_complexity)

def process_file(filepath, max_args, max_complexity):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source_code = f.read()

        findings = analyze_code(source_code, max_args=max_args, max_complexity=max_complexity)

        if findings:
            print(f"--- Findings in {filepath} ---")
            for finding in findings:
                if finding['line_number']:
                    print(f"  Line {finding['line_number']}: {finding['message']}")
                else:
                    print(f"  {finding['message']}")
            print("-" * (len(filepath) + 18))
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

if __name__ == "__main__":
    main()
