"""
Parser for Dataform dependencies report
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple


def parse_dependencies_report(report_path: str) -> Dict[str, dict]:
    """
    Parse the dependencies_report.txt file
    
    Args:
        report_path: Path to dependencies report file
        
    Returns:
        Dictionary mapping table names to their info (type, dependencies, dependents)
    """
    tables = {}
    current_table = None
    
    # Try different encodings
    encodings = ['utf-8', 'utf-16', 'cp1252', 'latin-1']
    content = None
    
    report_file = Path(report_path)
    if not report_file.exists():
        raise FileNotFoundError(f"Report file not found: {report_path}")
    
    for encoding in encodings:
        try:
            with open(report_file, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if content is None:
        raise ValueError("Could not decode file with any supported encoding")
    
    for line in content.split('\n'):
        line = line.rstrip()
        
        # Match table definition line
        table_match = re.match(r'^Table: (.+?) \((\w+)\)$', line)
        if table_match:
            table_name = table_match.group(1)
            table_type = table_match.group(2)
            current_table = table_name
            tables[current_table] = {
                'type': table_type,
                'dependencies': [],
                'dependents': []
            }
            continue
        
        # Match dependency line
        if current_table and '<-' in line:
            dep = line.strip().replace('<- ', '').strip()
            if dep:
                tables[current_table]['dependencies'].append(dep)
        
        # Match dependent line
        if current_table and '->' in line:
            dep = line.strip().replace('-> ', '').strip()
            if dep:
                tables[current_table]['dependents'].append(dep)
    
    return tables
