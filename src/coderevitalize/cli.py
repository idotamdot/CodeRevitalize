import argparse
import os
import sys
import fnmatch

from coderevitalize.analyzer import analyze_code
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


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Python code for 'aged' or inefficient patterns.",
        epilog="For more information, visit: https://github.com/idotamdot/CodeRevitalize"
    )
    parser.add_argument("path", help="Path to the Python file or directory to analyze.")
    parser.add_argument("--max-args", type=int, help="The maximum number of arguments a function can have.")
    parser.add_argument("--max-complexity", type=int, help="The maximum cyclomatic complexity a function can have.")
    parser.add_argument("--max-lines", type=int, help="The maximum number of lines a function can have.")
    parser.add_argument("--format", choices=['text', 'json'], default='text', help="The output format.")
    parser.add_argument("--config", help="Path to configuration file (.coderevitalize.yaml)")
    parser.add_argument("--exclude", action='append', help="File patterns to exclude (can be used multiple times)")
    parser.add_argument("--include", action='append', help="File patterns to include (can be used multiple times)")
    parser.add_argument("--no-color", action='store_true', help="Disable colored output")
    args = parser.parse_args()

    # Load configuration
    config = None
    if args.config:
        if not os.path.exists(args.config):
            print(f"Error: Config file '{args.config}' does not exist.", file=sys.stderr)
            sys.exit(1)
        try:
            config = Config.from_file(args.config)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Try to find config file automatically
        config_path = Config.find_config_file(args.path)
        if config_path:
            try:
                config = Config.from_file(config_path)
                print(f"Using configuration from: {config_path}")
            except ValueError as e:
                print(f"Warning: Error loading config file {config_path}: {e}", file=sys.stderr)
                config = Config()
        else:
            config = Config()

    # Update config with command line arguments
    config.update_from_args(args)
    
    # Handle include/exclude patterns
    include_patterns = args.include if args.include else config.include
    exclude_patterns = args.exclude if args.exclude else config.exclude

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


def process_file(filepath, config):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source_code = f.read()

        return analyze_code(source_code, config=config)
    except Exception as e:
        print(f"Error processing file {filepath}: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    main()
