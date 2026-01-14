# Dataform Dependency Visualizer

Generate beautiful, interactive SVG diagrams showing dependencies between Dataform tables.

## Features

- 📊 **Individual table diagrams** - One SVG per table showing immediate dependencies
- 🎨 **Color-coded by type** - Tables, views, and operations visually distinct
- 🔍 **Master index viewer** - Browse all 133+ tables in single interface
- 📁 **Schema organization** - Organized by schema with collapsible sections
- ⚡ **Pure Python SVGs** - No Graphviz required
- 🎯 **Orthogonal routing** - Clean, professional arrow paths
- 📝 **Smart text wrapping** - Long table names split across 2 lines

## Installation

```bash
pip install dataform-dependency-visualizer
```

## Quick Start

### 1. Generate dependency report

```bash
cd your-dataform-project
dataform compile --json > dependencies_report.txt
```

### 2. Generate SVG diagrams

```bash
# Generate for specific schema
dataform-deps generate dashboard_wwim

# Generate for all schemas (excluding refined_*)
dataform-deps generate-all

# Generate master index
dataform-deps index
```

### 3. View diagrams

Open `output/dependencies_master_index.html` in your browser.

## Usage

### Command Line

```bash
# Generate SVGs for one schema
dataform-deps generate <schema_name>

# Generate for all schemas
dataform-deps generate-all

# Generate master index
dataform-deps index

# Full pipeline with prerequisites check
dataform-deps setup
```

### Python API

```python
from dataform_viz import DependencyVisualizer

# Initialize visualizer
viz = DependencyVisualizer('dependencies_report.txt')

# Generate SVGs for schema
viz.generate_schema_svgs('dashboard_wwim', output_dir='output')

# Generate master index
viz.generate_master_index('output')
```

## Output Structure

```
output/
├── dependencies_master_index.html  # Interactive viewer
├── dependencies_dashboard_wwim/
│   ├── index.html
│   ├── table1.svg
│   └── table2.svg
├── dependencies_datamart_wwim/
│   └── ...
└── dependencies_report.txt
```

## Features

### SVG Diagrams

Each table gets its own diagram showing:
- **Yellow center node**: The table itself
- **Blue left nodes**: Dependencies (what it reads from)
- **Green right nodes**: Dependents (what reads from it)
- **Schema labels**: Show which schema each table belongs to
- **Type badges**: Distinguish tables, views, operations

### Master Index

Interactive HTML with:
- Sidebar navigation by schema
- Collapsible schema sections
- Search-friendly table list
- Click-to-view diagrams
- Statistics (total schemas/tables)

## Requirements

- Python 3.8+
- Dataform CLI (for generating reports)
- Node.js (for running Dataform)

## Development

```bash
# Clone repo
git clone https://github.com/yourusername/dataform-dependency-visualizer
cd dataform-dependency-visualizer

# Install in development mode
pip install -e .

# Run tests
pytest
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.

## Credits

Created for visualizing complex Dataform projects with 100+ table dependencies.
