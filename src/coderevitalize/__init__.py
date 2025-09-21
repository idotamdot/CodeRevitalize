"""
CodeRevitalize - A tool to analyze Python code for 'aged' or inefficient patterns.

This package provides functionality to detect:
- Functions with too many arguments
- Functions that are too long
- Functions with high cyclomatic complexity
"""

from .analyzer import analyze_code, ArgumentCountAnalyzer, FunctionLengthAnalyzer, analyze_complexity
from .formatters import TextFormatter, JsonFormatter, get_formatter

__version__ = "0.1.0"
__author__ = "Jules"
__email__ = "jules@example.com"

__all__ = [
    "analyze_code",
    "ArgumentCountAnalyzer", 
    "FunctionLengthAnalyzer",
    "analyze_complexity",
    "TextFormatter",
    "JsonFormatter", 
    "get_formatter"
]
