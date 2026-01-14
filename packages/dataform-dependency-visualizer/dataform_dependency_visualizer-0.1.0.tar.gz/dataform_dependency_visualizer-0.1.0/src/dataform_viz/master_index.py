#!/usr/bin/env python3
"""
Generate a master index.html to view all dependency SVGs from all schemas
"""
from pathlib import Path
import re

def collect_all_svgs():
    """Collect all SVG files from dependencies_* folders"""
    schemas = {}
    
    output_path = Path('output')
    if not output_path.exists():
        output_path = Path('.')
    
    for folder in output_path.glob('dependencies_*'):
        if not folder.is_dir():
            continue
        
        schema_name = folder.name.replace('dependencies_', '')
        svgs = []
        
        for svg_file in sorted(folder.glob('*.svg')):
            table_name = svg_file.stem.replace('_', '.')
            # Use relative path from output folder
            relative_path = f"{folder.name}/{svg_file.name}"
            svgs.append({
                'file': relative_path,
                'name': table_name,
                'display_name': table_name.split('.')[-1] if '.' in table_name else table_name
            })
        
        if svgs:
            schemas[schema_name] = {
                'folder': str(folder),
                'svgs': svgs
            }
    
    return schemas

def generate_master_index(schemas):
    """Generate master index.html"""
    
    html_lines = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '    <meta charset="utf-8">',
        '    <title>All Dependencies - Master Index</title>',
        '    <style>',
        '        * { box-sizing: border-box; }',
        '        body { ',
        '            font-family: Arial, sans-serif; ',
        '            margin: 0; ',
        '            padding: 0; ',
        '            background: #f5f5f5; ',
        '            display: flex;',
        '            height: 100vh;',
        '        }',
        '        .sidebar {',
        '            width: 300px;',
        '            background: white;',
        '            border-right: 1px solid #ddd;',
        '            overflow-y: auto;',
        '            padding: 20px;',
        '        }',
        '        .content {',
        '            flex: 1;',
        '            overflow: auto;',
        '            padding: 20px;',
        '            background: white;',
        '        }',
        '        h1 { ',
        '            color: #333; ',
        '            margin: 0 0 20px 0;',
        '            font-size: 24px;',
        '        }',
        '        .schema-section {',
        '            margin-bottom: 30px;',
        '        }',
        '        .schema-title {',
        '            font-size: 16px;',
        '            font-weight: bold;',
        '            color: #1976d2;',
        '            margin: 15px 0 10px 0;',
        '            padding: 8px;',
        '            background: #e3f2fd;',
        '            border-radius: 4px;',
        '            cursor: pointer;',
        '            user-select: none;',
        '        }',
        '        .schema-title:hover {',
        '            background: #bbdefb;',
        '        }',
        '        .table-list {',
        '            list-style: none;',
        '            padding: 0;',
        '            margin: 0 0 0 15px;',
        '        }',
        '        .table-list.collapsed {',
        '            display: none;',
        '        }',
        '        .table-item {',
        '            padding: 6px 10px;',
        '            cursor: pointer;',
        '            border-radius: 4px;',
        '            margin: 2px 0;',
        '            font-size: 13px;',
        '        }',
        '        .table-item:hover {',
        '            background: #f5f5f5;',
        '        }',
        '        .table-item.active {',
        '            background: #1976d2;',
        '            color: white;',
        '        }',
        '        .viewer {',
        '            text-align: center;',
        '        }',
        '        .viewer img {',
        '            max-width: 100%;',
        '            height: auto;',
        '            box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
        '        }',
        '        .viewer-title {',
        '            font-size: 20px;',
        '            color: #333;',
        '            margin-bottom: 20px;',
        '            padding: 15px;',
        '            background: #f5f5f5;',
        '            border-radius: 4px;',
        '        }',
        '        .viewer-subtitle {',
        '            font-size: 14px;',
        '            color: #666;',
        '            margin-top: 5px;',
        '        }',
        '        .empty-state {',
        '            text-align: center;',
        '            padding: 100px 20px;',
        '            color: #999;',
        '        }',
        '        .stats {',
        '            padding: 15px;',
        '            background: #f5f5f5;',
        '            border-radius: 4px;',
        '            margin-bottom: 20px;',
        '            font-size: 13px;',
        '            color: #666;',
        '        }',
        '        .collapse-icon {',
        '            float: right;',
        '            font-size: 12px;',
        '        }',
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="sidebar">',
        '        <h1>Table Dependencies</h1>',
        '        <div class="stats">',
    ]
    
    # Count totals
    total_schemas = len(schemas)
    total_tables = sum(len(s['svgs']) for s in schemas.values())
    
    html_lines.append(f'            <strong>{total_schemas}</strong> schemas<br>')
    html_lines.append(f'            <strong>{total_tables}</strong> tables')
    html_lines.append('        </div>')
    
    # Generate schema sections
    for schema_name, schema_data in sorted(schemas.items()):
        html_lines.append(f'        <div class="schema-section">')
        html_lines.append(f'            <div class="schema-title" onclick="toggleSchema(\'{schema_name}\')">')
        html_lines.append(f'                {schema_name}')
        html_lines.append(f'                <span class="collapse-icon" id="icon-{schema_name}">▼</span>')
        html_lines.append(f'            </div>')
        html_lines.append(f'            <ul class="table-list" id="list-{schema_name}">')
        
        for svg in schema_data['svgs']:
            safe_id = svg['name'].replace('.', '_').replace('-', '_')
            html_lines.append(f'                <li class="table-item" id="item-{safe_id}" ')
            html_lines.append(f'                    onclick="showDiagram(\'{svg["file"]}\', \'{svg["name"]}\', \'{schema_name}\', \'{safe_id}\')">')
            html_lines.append(f'                    {svg["display_name"]}')
            html_lines.append(f'                </li>')
        
        html_lines.append('            </ul>')
        html_lines.append('        </div>')
    
    html_lines.extend([
        '    </div>',
        '    <div class="content">',
        '        <div id="viewer" class="empty-state">',
        '            <h2>Select a table to view its dependencies</h2>',
        '            <p>Choose from the list on the left</p>',
        '        </div>',
        '    </div>',
        '    <script>',
        '        let currentItem = null;',
        '        ',
        '        function showDiagram(file, name, schema, itemId) {',
        '            // Update active state',
        '            if (currentItem) {',
        '                document.getElementById(currentItem).classList.remove("active");',
        '            }',
        '            currentItem = "item-" + itemId;',
        '            document.getElementById(currentItem).classList.add("active");',
        '            ',
        '            // Show diagram',
        '            const viewer = document.getElementById("viewer");',
        '            viewer.className = "viewer";',
        '            viewer.innerHTML = `',
        '                <div class="viewer-title">',
        '                    ${name}',
        '                    <div class="viewer-subtitle">${schema}</div>',
        '                </div>',
        '                <img src="${file}" alt="${name} dependencies">',
        '            `;',
        '        }',
        '        ',
        '        function toggleSchema(schemaName) {',
        '            const list = document.getElementById("list-" + schemaName);',
        '            const icon = document.getElementById("icon-" + schemaName);',
        '            ',
        '            if (list.classList.contains("collapsed")) {',
        '                list.classList.remove("collapsed");',
        '                icon.textContent = "▼";',
        '            } else {',
        '                list.classList.add("collapsed");',
        '                icon.textContent = "▶";',
        '            }',
        '        }',
        '        ',
        '        // Auto-expand first schema and select first table',
        '        window.addEventListener("load", function() {',
        '            const firstTable = document.querySelector(".table-item");',
        '            if (firstTable) {',
        '                firstTable.click();',
        '            }',
        '        });',
        '    </script>',
        '</body>',
        '</html>',
    ])
    
    return '\n'.join(html_lines)

def main():
    print("Collecting SVG files from all schemas...")
    schemas = collect_all_svgs()
    
    if not schemas:
        print("No dependency folders found. Run split_dependencies_svg.py first.")
        return
    
    print(f"\nFound {len(schemas)} schemas:")
    for schema_name, schema_data in sorted(schemas.items()):
        print(f"  - {schema_name}: {len(schema_data['svgs'])} tables")
    
    print("\nGenerating master index.html...")
    html_content = generate_master_index(schemas)
    
    output_folder = Path('output')
    output_folder.mkdir(exist_ok=True)
    output_file = output_folder / 'dependencies_master_index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nMaster index created: {output_file}")
    print(f"Total tables: {sum(len(s['svgs']) for s in schemas.values())}")
    
    # Open in browser
    import subprocess
    subprocess.run(['start', str(output_file)], shell=True)
    print("\nOpening in browser...")

if __name__ == "__main__":
    main()
