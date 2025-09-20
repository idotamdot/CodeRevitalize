import os
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Config:
    """Configuration for CodeRevitalize analysis."""
    max_args: int = 5
    max_complexity: int = 10
    max_lines: int = 50
    include: List[str] = field(default_factory=lambda: ["*.py"])
    exclude: List[str] = field(default_factory=list)
    checks: Dict[str, bool] = field(default_factory=lambda: {
        "unused_imports": True,
        "missing_docstrings": True,
        "magic_numbers": True,
        "todo_comments": True
    })
    severity: Dict[str, str] = field(default_factory=lambda: {
        "argument_count": "high",
        "complexity": "high", 
        "function_length": "medium",
        "unused_imports": "low",
        "missing_docstrings": "low",
        "magic_numbers": "low",
        "todo_comments": "info"
    })

    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            raise ValueError(f"Error loading config file {config_path}: {e}")
        
        return cls(**data)

    @classmethod
    def find_config_file(cls, start_path: str) -> str:
        """Find configuration file starting from the given path."""
        config_names = ['.coderevitalize.yaml', '.coderevitalize.yml', 'coderevitalize.yaml']
        
        current_path = os.path.abspath(start_path)
        if os.path.isfile(current_path):
            current_path = os.path.dirname(current_path)
            
        while current_path != os.path.dirname(current_path):  # Until we reach the root
            for config_name in config_names:
                config_path = os.path.join(current_path, config_name)
                if os.path.isfile(config_path):
                    return config_path
            current_path = os.path.dirname(current_path)
        
        return None

    def update_from_args(self, args) -> 'Config':
        """Update configuration with command line arguments."""
        if hasattr(args, 'max_args') and args.max_args is not None:
            self.max_args = args.max_args
        if hasattr(args, 'max_complexity') and args.max_complexity is not None:
            self.max_complexity = args.max_complexity
        if hasattr(args, 'max_lines') and args.max_lines is not None:
            self.max_lines = args.max_lines
        return self