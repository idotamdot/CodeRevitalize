import json
from collections import defaultdict


class BaseFormatter:
    def display(self, findings_by_file):
        raise NotImplementedError


class TextFormatter(BaseFormatter):
    SEVERITY_COLORS = {
        'critical': '\033[91m',  # Red
        'high': '\033[91m',      # Red
        'medium': '\033[93m',    # Yellow
        'low': '\033[94m',       # Blue
        'info': '\033[96m',      # Cyan
    }
    RESET_COLOR = '\033[0m'

    def display(self, findings_by_file):
        total_stats = defaultdict(int)
        
        for filepath, findings in findings_by_file.items():
            if findings:
                print(f"--- Findings in {filepath} ---")
                
                # Sort findings by severity and line number
                severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
                sorted_findings = sorted(findings, key=lambda x: (
                    severity_order.get(x.get('severity', 'info'), 4),
                    x.get('line_number', 0)
                ))
                
                for finding in sorted_findings:
                    severity = finding.get('severity', 'info')
                    total_stats[severity] += 1
                    
                    color = self.SEVERITY_COLORS.get(severity, '')
                    severity_label = f"[{severity.upper()}]"
                    
                    if finding['line_number']:
                        print(f"  Line {finding['line_number']}: {color}{severity_label}{self.RESET_COLOR} {finding['message']}")
                    else:
                        print(f"  {color}{severity_label}{self.RESET_COLOR} {finding['message']}")
                        
                    # Show suggestion if available
                    if finding.get('suggestion'):
                        print(f"    💡 Suggestion: {finding['suggestion']}")
                        
                print("-" * (len(filepath) + 18))
        
        # Display summary
        if total_stats:
            total_issues = sum(total_stats.values())
            summary_parts = []
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                if total_stats[severity] > 0:
                    color = self.SEVERITY_COLORS.get(severity, '')
                    summary_parts.append(f"{total_stats[severity]} {color}{severity}{self.RESET_COLOR}")
            
            print(f"\nSummary: {total_issues} issues found ({', '.join(summary_parts)} severity)")


class JsonFormatter(BaseFormatter):
    def display(self, findings_by_file):
        # Add summary statistics to JSON output
        output = {
            "files": findings_by_file,
            "summary": self._generate_summary(findings_by_file)
        }
        print(json.dumps(output, indent=2))
    
    def _generate_summary(self, findings_by_file):
        """Generate summary statistics."""
        total_stats = defaultdict(int)
        type_stats = defaultdict(int)
        
        for findings in findings_by_file.values():
            for finding in findings:
                severity = finding.get('severity', 'info')
                finding_type = finding.get('type', 'unknown')
                total_stats[severity] += 1
                type_stats[finding_type] += 1
        
        return {
            "total_issues": sum(total_stats.values()),
            "by_severity": dict(total_stats),
            "by_type": dict(type_stats),
            "files_analyzed": len(findings_by_file)
        }

def get_formatter(format_name):
    if format_name == 'text':
        return TextFormatter()
    elif format_name == 'json':
        return JsonFormatter()
    else:
        # This should be caught by argparse choices, but as a fallback:
        raise ValueError(f"Unknown format: {format_name}")
