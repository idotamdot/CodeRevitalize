import argparse
import os
import sys
import fnmatch

from coderevitalize.analyzer import analyze_code, explain_code
from coderevitalize.ai import get_ai_response
from coderevitalize.formatters import get_formatter
from coderevitalize.config import Config


def should_include_file(filepath, include_patterns, exclude_patterns):
    """Check if a file should be included based on include/exclude patterns."""
    filename = os.path.basename(filepath)
    relative_path = filepath
    
    # Check exclude patterns first
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(filename, pattern):
            return False
    
    # Check include patterns
    for pattern in include_patterns:
        if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(filename, pattern):
            return True
    
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze, explain, and write Python code.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Analyze command
    parser_analyze = subparsers.add_parser("analyze", help="Analyze Python code for 'aged' or inefficient patterns.")
    parser_analyze.add_argument("path", help="Path to the Python file or directory to analyze.")
    parser_analyze.add_argument("--max-args", type=int, default=5, help="The maximum number of arguments a function can have. (default: 5)")
    parser_analyze.add_argument("--max-complexity", type=int, default=10, help="The maximum cyclomatic complexity a function can have. (default: 10)")
    parser_analyze.add_argument("--max-lines", type=int, default=50, help="The maximum number of lines a function can have. (default: 50)")
    parser_analyze.add_argument("--format", choices=['text', 'json'], default='text', help="The output format. (default: text)")

    # Explain command
    parser_explain = subparsers.add_parser("explain", help="Explain a piece of code using AI.")
    parser_explain.add_argument("path", help="Path to the file to explain.")
    parser_explain.add_argument("--language", default="Python", help="The programming language of the code.")

    # Write command
    parser_write = subparsers.add_parser("write", help="Write a script from a description using AI.")
    parser_write.add_argument("prompt", help="A description of the code to write.")
    parser_write.add_argument("--language", default="Python", help="The programming language for the script.")
    parser_write.add_argument("--output", "-o", help="The file path to save the generated code.")

    args = parser.parse_args(argv)

    if args.command == "analyze":
        handle_analyze(args)
    elif args.command == "explain":
        handle_explain(args)
    elif args.command == "write":
        handle_write(args)

def handle_analyze(args):
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    all_findings = {}
    files_processed = 0

    if os.path.isfile(args.path):
        if should_include_file(args.path, include_patterns, exclude_patterns):
            filepath = args.path
            findings = process_file(filepath, config)
            if findings:
                all_findings[filepath] = findings
            files_processed = 1
        else:
            print(f"File '{args.path}' excluded by patterns.", file=sys.stderr)
            sys.exit(0)
    elif os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    relative_path = os.path.relpath(filepath, args.path)
                    
                    if should_include_file(relative_path, include_patterns, exclude_patterns):
                        findings = process_file(filepath, config)
                        if findings:
                            all_findings[filepath] = findings
                        files_processed += 1

    if files_processed == 0:
        print("No Python files found to analyze.", file=sys.stderr)
        sys.exit(0)

    # Disable colors if requested
    if args.no_color:
        from coderevitalize.formatters import TextFormatter
        TextFormatter.SEVERITY_COLORS = {k: '' for k in TextFormatter.SEVERITY_COLORS}
        TextFormatter.RESET_COLOR = ''

    formatter = get_formatter(args.format)
    formatter.display(all_findings)

    if all_findings:
        sys.exit(1)

def handle_explain(args):
    if not os.path.exists(args.path) or not os.path.isfile(args.path):
        print(f"Error: Path '{args.path}' is not a valid file.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            source_code = f.read()
        explanation = explain_code(source_code, args.language)
        print(explanation)
    except Exception as e:
        print(f"Error explaining file {args.path}: {e}", file=sys.stderr)
        sys.exit(1)

def handle_write(args):
    prompt = f"Write a {args.language} script that does the following: {args.prompt}"
    try:
        generated_code = get_ai_response(prompt)

        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(generated_code)
                print(f"Code successfully written to {args.output}")
            except Exception as e:
                print(f"Error writing to file {args.output}: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(generated_code)
    except Exception as e:
        print(f"Error generating code: {e}", file=sys.stderr)
        sys.exit(1)

def process_file(filepath, max_args, max_complexity, max_lines):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source_code = f.read()

        return analyze_code(source_code, config=config)
    except Exception as e:
        print(f"Error processing file {filepath}: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    main()
