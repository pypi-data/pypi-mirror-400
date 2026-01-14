#!/usr/bin/env python3
"""
Script to generate individual SVG diagrams for each table in a schema
Shows immediate dependencies and dependents for each table
"""
import re
from pathlib import Path
import sys

def parse_dependencies_report(report_path):
    """Parse the dependencies_report.txt file"""
    tables = {}
    current_table = None
    
    # Try different encodings
    encodings = ['utf-8', 'utf-16', 'cp1252', 'latin-1']
    content = None
    
    for encoding in encodings:
        try:
            with open(report_path, 'r', encoding=encoding) as f:
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

def generate_table_svg(table_name, table_info, all_tables, output_dir):
    """Generate SVG for a single table showing its immediate neighbors"""
    
    # Create safe filename
    safe_name = table_name.replace('.', '_').replace('-', '_')
    svg_file = output_dir / f"{safe_name}.svg"
    
    # Generate SVG directly
    generate_svg_manual(table_name, table_info, all_tables, svg_file)
    return True, svg_file


def generate_svg_manual(table_name, table_info, all_tables, svg_file):
    """Generate SVG manually without Graphviz dependency"""
    
    # Layout parameters
    node_width = 200
    node_height = 60
    h_spacing = 250
    v_spacing = 80
    margin = 50
    
    # Organize nodes into columns
    dependencies = table_info['dependencies']
    dependents = table_info['dependents']
    
    max_left = len(dependencies)
    max_right = len(dependents)
    max_vertical = max(max_left, 1, max_right)
    
    # Calculate canvas size
    num_cols = 1 + (1 if dependencies else 0) + (1 if dependents else 0)
    canvas_width = margin * 2 + node_width * num_cols + h_spacing * (num_cols - 1)
    canvas_height = margin * 2 + node_height * max_vertical + v_spacing * (max_vertical - 1)
    
    # Node positions
    nodes = {}
    
    # Center column - main table
    center_x = margin + node_width // 2
    if dependencies:
        center_x += node_width + h_spacing
    center_y = canvas_height // 2
    
    nodes[table_name] = {
        'x': center_x,
        'y': center_y,
        'color': '#ffeb3b',
        'border': '#f57f17',
        'type': table_info['type']
    }
    
    # Left column - dependencies
    if dependencies:
        left_x = margin + node_width // 2
        start_y = center_y - ((len(dependencies) - 1) * (node_height + v_spacing)) // 2
        for i, dep in enumerate(dependencies):
            dep_type = all_tables.get(dep, {}).get('type', 'unknown')
            color = {
                'table': '#e1f5ff',
                'view': '#fff3e0',
                'operations': '#f3e5f5'
            }.get(dep_type, '#f5f5f5')
            nodes[dep] = {
                'x': left_x,
                'y': start_y + i * (node_height + v_spacing),
                'color': color,
                'border': '#666',
                'type': dep_type
            }
    
    # Right column - dependents
    if dependents:
        right_x = center_x + node_width // 2 + h_spacing + node_width // 2
        start_y = center_y - ((len(dependents) - 1) * (node_height + v_spacing)) // 2
        for i, dept in enumerate(dependents):
            dept_type = all_tables.get(dept, {}).get('type', 'unknown')
            color = {
                'table': '#e1f5ff',
                'view': '#fff3e0',
                'operations': '#f3e5f5'
            }.get(dept_type, '#f5f5f5')
            nodes[dept] = {
                'x': right_x,
                'y': start_y + i * (node_height + v_spacing),
                'color': color,
                'border': '#666',
                'type': dept_type
            }
    
    # Generate SVG
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg width="{canvas_width}" height="{canvas_height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">',
        '      <polygon points="0 0, 6 3, 0 6" fill="#000" />',
        '    </marker>',
        '  </defs>',
        '  <style>',
        '    .node-text { font-family: Arial, sans-serif; font-size: 12px; fill: #333; }',
        '    .type-badge { font-family: Arial, sans-serif; font-size: 10px; fill: #666; }',
        '  </style>',
    ]
    
    # Draw edges first (so they appear behind nodes) with orthogonal routing
    for dep in dependencies:
        if dep in nodes:
            x1 = nodes[dep]['x'] + node_width // 2
            y1 = nodes[dep]['y']
            x2 = nodes[table_name]['x'] - node_width // 2
            y2 = nodes[table_name]['y']
            # Orthogonal path: horizontal then vertical
            mid_x = (x1 + x2) // 2
            svg_lines.append(f'  <path d="M {x1} {y1} L {mid_x} {y1} L {mid_x} {y2} L {x2} {y2}" stroke="#000" stroke-width="1.5" fill="none" marker-end="url(#arrowhead)" />')
    
    for dept in dependents:
        if dept in nodes:
            x1 = nodes[table_name]['x'] + node_width // 2
            y1 = nodes[table_name]['y']
            x2 = nodes[dept]['x'] - node_width // 2
            y2 = nodes[dept]['y']
            # Orthogonal path: horizontal then vertical
            mid_x = (x1 + x2) // 2
            svg_lines.append(f'  <path d="M {x1} {y1} L {mid_x} {y1} L {mid_x} {y2} L {x2} {y2}" stroke="#000" stroke-width="1.5" fill="none" marker-end="url(#arrowhead)" />')
    
    # Draw nodes
    for node_name, pos in nodes.items():
        x = pos['x'] - node_width // 2
        y = pos['y'] - node_height // 2
        
        # Node rectangle
        stroke_width = 3 if node_name == table_name else 1
        svg_lines.append(f'  <rect x="{x}" y="{y}" width="{node_width}" height="{node_height}" '
                        f'fill="{pos["color"]}" stroke="{pos["border"]}" stroke-width="{stroke_width}" rx="5" />')
        
        # Schema name at top
        schema_name = node_name.split('.')[0] if '.' in node_name else ''
        if schema_name:
            schema_y = pos['y'] - 20
            svg_lines.append(f'  <text x="{pos["x"]}" y="{schema_y}" text-anchor="middle" class="type-badge" fill="#999">{schema_name}</text>')
        
        # Node text - wrap into 2 lines if needed
        display_name = node_name.split('.')[-1] if '.' in node_name else node_name
        
        # Split into 2 lines if longer than 20 characters
        if len(display_name) > 20:
            # Find a good break point (underscore, or middle)
            mid = len(display_name) // 2
            break_point = display_name.rfind('_', 0, mid + 5)
            if break_point == -1 or break_point < mid - 5:
                break_point = mid
            
            line1 = display_name[:break_point]
            line2 = display_name[break_point:].lstrip('_')
            
            text_y1 = pos['y'] - 8 if schema_name else pos['y'] - 13
            text_y2 = pos['y'] + 6 if schema_name else pos['y'] + 1
            
            svg_lines.append(f'  <text x="{pos["x"]}" y="{text_y1}" text-anchor="middle" class="node-text">{line1}</text>')
            svg_lines.append(f'  <text x="{pos["x"]}" y="{text_y2}" text-anchor="middle" class="node-text">{line2}</text>')
        else:
            text_y = pos['y'] if schema_name else pos['y'] - 5
            svg_lines.append(f'  <text x="{pos["x"]}" y="{text_y}" text-anchor="middle" class="node-text">{display_name}</text>')
        
        # Type badge
        badge_y = pos['y'] + 20 if schema_name else pos['y'] + 15
        svg_lines.append(f'  <text x="{pos["x"]}" y="{badge_y}" text-anchor="middle" class="type-badge">{pos["type"]}</text>')
    
    svg_lines.append('</svg>')
    
    with open(svg_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_lines))

def generate_index_html(tables, schema, output_dir):
    """Generate an index.html to view all SVGs"""
    
    html_lines = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '    <meta charset="utf-8">',
        f'    <title>{schema} - Dependency Diagrams</title>',
        '    <style>',
        '        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }',
        '        h1 { color: #333; }',
        '        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }',
        '        .card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; cursor: pointer; transition: transform 0.2s; }',
        '        .card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }',
        '        .card h3 { margin: 0 0 10px 0; color: #1976d2; }',
        '        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }',
        '        .badge.table { background: #e1f5ff; color: #01579b; }',
        '        .badge.view { background: #fff3e0; color: #e65100; }',
        '        .badge.operations { background: #f3e5f5; color: #4a148c; }',
        '        .stats { color: #666; font-size: 14px; margin-top: 10px; }',
        '        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; }',
        '        .modal-content { position: relative; margin: 2% auto; width: 90%; max-width: 1200px; height: 90%; background: white; border-radius: 8px; overflow: auto; }',
        '        .close { position: absolute; top: 10px; right: 20px; font-size: 30px; cursor: pointer; color: #666; z-index: 1001; }',
        '        .modal img { width: 100%; height: auto; }',
        '    </style>',
        '</head>',
        '<body>',
        f'    <h1>{schema} - Table Dependencies</h1>',
        f'    <p>Total tables: {len(tables)}</p>',
        '    <div class="grid">',
    ]
    
    for table_name, info in sorted(tables.items()):
        safe_name = table_name.replace('.', '_').replace('-', '_')
        short_name = table_name.split('.')[-1] if '.' in table_name else table_name
        
        html_lines.extend([
            '        <div class="card" onclick="showDiagram(\'' + safe_name + '.svg\', \'' + table_name + '\')">',
            f'            <h3>{short_name}</h3>',
            f'            <span class="badge {info["type"]}">{info["type"]}</span>',
            f'            <div class="stats">',
            f'                ← {len(info["dependencies"])} dependencies<br>',
            f'                → {len(info["dependents"])} dependents',
            f'            </div>',
            '        </div>',
        ])
    
    html_lines.extend([
        '    </div>',
        '    <div id="modal" class="modal" onclick="closeModal()">',
        '        <span class="close">&times;</span>',
        '        <div class="modal-content" onclick="event.stopPropagation()">',
        '            <h2 id="modalTitle" style="padding: 20px;"></h2>',
        '            <img id="modalImage" src="" alt="Dependency diagram">',
        '        </div>',
        '    </div>',
        '    <script>',
        '        function showDiagram(file, title) {',
        '            document.getElementById("modalImage").src = file;',
        '            document.getElementById("modalTitle").textContent = title;',
        '            document.getElementById("modal").style.display = "block";',
        '        }',
        '        function closeModal() {',
        '            document.getElementById("modal").style.display = "none";',
        '        }',
        '        document.addEventListener("keydown", function(e) {',
        '            if (e.key === "Escape") closeModal();',
        '        });',
        '    </script>',
        '</body>',
        '</html>',
    ])
    
    index_file = output_dir / 'index.html'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
    
    return index_file

def main():
    report_path = Path('output/dependencies_report.txt')
    if not report_path.exists():
        report_path = Path('dependencies_report.txt')
    
    if not report_path.exists():
        print("Error: dependencies_report.txt not found")
        print("Run: python utility_check_dependencies.py > dependencies_report.txt")
        return
    
    # Get schema from command line
    if len(sys.argv) < 2:
        print("Usage: python split_dependencies_svg.py <schema_name>")
        print("Example: python split_dependencies_svg.py dashboard_wwim")
        return
    
    schema = sys.argv[1]
    
    print(f"Parsing dependencies report...")
    all_tables = parse_dependencies_report(report_path)
    
    # Filter to schema
    schema_tables = {k: v for k, v in all_tables.items() if k.startswith(schema + '.')}
    
    if not schema_tables:
        print(f"No tables found for schema: {schema}")
        print(f"Available schemas:")
        schemas = set(k.split('.')[0] for k in all_tables.keys() if '.' in k)
        for s in sorted(schemas):
            count = sum(1 for k in all_tables.keys() if k.startswith(s + '.'))
            print(f"  - {s} ({count} tables)")
        return
    
    print(f"Found {len(schema_tables)} tables in schema '{schema}'")
    
    # Create output directory
    base_output = Path('output')
    base_output.mkdir(exist_ok=True)
    output_dir = base_output / f'dependencies_{schema}'
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Generate SVG for each table
    success_count = 0
    
    for table_name, table_info in schema_tables.items():
        print(f"Generating: {table_name}...", end=' ')
        success, result = generate_table_svg(table_name, table_info, all_tables, output_dir)
        
        if success:
            print("OK")
            success_count += 1
        else:
            print(f"FAILED: {result}")
    
    print(f"\nGenerated {success_count}/{len(schema_tables)} SVG files")
    
    # Generate index.html
    index_file = generate_index_html(schema_tables, schema, output_dir)
    print(f"Index file created: {index_file}")
    print(f"\nOpening in browser...")
    
    # Open index.html
    import subprocess
    subprocess.run(['start', str(index_file)], shell=True)

if __name__ == "__main__":
    main()
