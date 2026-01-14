"""
Main visualizer class
"""
from pathlib import Path
from typing import Optional, List
from .parser import parse_dependencies_report
from .svg_generator import generate_table_svg, generate_svg_manual
from .master_index import collect_all_svgs, generate_master_index


class DependencyVisualizer:
    """Main class for generating dependency visualizations"""
    
    def __init__(self, report_path: str = "dependencies_report.txt"):
        """
        Initialize visualizer
        
        Args:
            report_path: Path to dependencies report file
        """
        self.report_path = Path(report_path)
        self.tables = None
        
    def load_report(self):
        """Load and parse the dependencies report"""
        if self.tables is None:
            self.tables = parse_dependencies_report(str(self.report_path))
        return self.tables
    
    def generate_schema_svgs(
        self, 
        schema: str, 
        output_dir: str = "output",
        exclude_patterns: Optional[List[str]] = None
    ) -> int:
        """
        Generate SVG diagrams for all tables in a schema
        
        Args:
            schema: Schema name to generate
            output_dir: Base output directory
            exclude_patterns: List of schema patterns to exclude (e.g., ['refined_*'])
            
        Returns:
            Number of SVGs generated
        """
        self.load_report()
        
        # Filter to schema
        schema_tables = {
            k: v for k, v in self.tables.items() 
            if k.startswith(schema + '.')
        }
        
        if not schema_tables:
            raise ValueError(f"No tables found for schema: {schema}")
        
        # Create output directory
        base_output = Path(output_dir)
        base_output.mkdir(exist_ok=True)
        schema_output = base_output / f'dependencies_{schema}'
        schema_output.mkdir(exist_ok=True)
        
        # Generate SVGs
        count = 0
        for table_name, table_info in schema_tables.items():
            safe_name = table_name.replace('.', '_').replace('-', '_')
            svg_file = schema_output / f"{safe_name}.svg"
            
            generate_svg_manual(table_name, table_info, self.tables, svg_file)
            count += 1
        
        return count
    
    def generate_all_schemas(
        self, 
        output_dir: str = "output",
        exclude_patterns: Optional[List[str]] = None
    ) -> dict:
        """
        Generate SVG diagrams for all schemas
        
        Args:
            output_dir: Base output directory
            exclude_patterns: List of schema patterns to exclude (default: ['refined_*'])
            
        Returns:
            Dictionary mapping schema names to number of tables generated
        """
        if exclude_patterns is None:
            exclude_patterns = ['refined_*']
        
        self.load_report()
        
        # Get all unique schemas
        schemas = set()
        for table_name in self.tables.keys():
            if '.' in table_name:
                schema = table_name.split('.')[0]
                # Check exclusion patterns
                excluded = False
                for pattern in exclude_patterns:
                    if pattern.endswith('*'):
                        if schema.startswith(pattern[:-1]):
                            excluded = True
                            break
                if not excluded:
                    schemas.add(schema)
        
        # Generate for each schema
        results = {}
        for schema in sorted(schemas):
            count = self.generate_schema_svgs(schema, output_dir)
            results[schema] = count
        
        return results
    
    def generate_master_index(self, output_dir: str = "output") -> Path:
        """
        Generate master index.html to view all diagrams
        
        Args:
            output_dir: Output directory containing schema folders
            
        Returns:
            Path to generated index file
        """
        output_path = Path(output_dir)
        schemas = collect_all_svgs()
        
        if not schemas:
            raise ValueError("No dependency folders found. Generate SVGs first.")
        
        html_content = generate_master_index(schemas)
        
        output_file = output_path / 'dependencies_master_index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
