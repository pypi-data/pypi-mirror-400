"""
Command-line interface for dataform-dependency-visualizer
"""
import sys
import argparse
from pathlib import Path
from .visualizer import DependencyVisualizer


def cmd_generate(args):
    """Generate SVGs for a specific schema"""
    viz = DependencyVisualizer(args.report)
    
    try:
        count = viz.generate_schema_svgs(
            args.schema,
            output_dir=args.output
        )
        print(f"✓ Generated {count} SVG diagrams for {args.schema}")
        print(f"  Output: {args.output}/dependencies_{args.schema}/")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def cmd_generate_all(args):
    """Generate SVGs for all schemas"""
    viz = DependencyVisualizer(args.report)
    
    try:
        results = viz.generate_all_schemas(
            output_dir=args.output,
            exclude_patterns=args.exclude or ['refined_*']
        )
        
        total = sum(results.values())
        print(f"\n✓ Generated {total} SVG diagrams across {len(results)} schemas:")
        for schema, count in sorted(results.items()):
            print(f"  - {schema}: {count} tables")
        print(f"\nOutput directory: {args.output}/")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def cmd_index(args):
    """Generate master index"""
    viz = DependencyVisualizer(args.report)
    
    try:
        index_file = viz.generate_master_index(output_dir=args.output)
        print(f"✓ Master index created: {index_file}")
        
        if args.open:
            import subprocess
            subprocess.run(['start', str(index_file)], shell=True)
        
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def cmd_setup(args):
    """Full setup pipeline"""
    from .dataform_check import check_prerequisites
    
    print("=" * 60)
    print("DATAFORM DEPENDENCIES VISUALIZATION SETUP")
    print("=" * 60)
    
    if not check_prerequisites():
        print("\n⚠ Prerequisites check failed")
        return 1
    
    # Generate all
    args_all = argparse.Namespace(
        report=args.report,
        output=args.output,
        exclude=args.exclude
    )
    if cmd_generate_all(args_all) != 0:
        return 1
    
    # Generate index
    args_idx = argparse.Namespace(
        report=args.report,
        output=args.output,
        open=True
    )
    return cmd_index(args_idx)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='dataform-deps',
        description='Generate interactive SVG diagrams for Dataform table dependencies'
    )
    
    parser.add_argument(
        '--report',
        default='dependencies_report.txt',
        help='Path to dependencies report file (default: dependencies_report.txt)'
    )
    
    parser.add_argument(
        '--output',
        default='output',
        help='Output directory (default: output)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate SVGs for a schema')
    gen_parser.add_argument('schema', help='Schema name to generate')
    gen_parser.set_defaults(func=cmd_generate)
    
    # Generate-all command
    gen_all_parser = subparsers.add_parser('generate-all', help='Generate SVGs for all schemas')
    gen_all_parser.add_argument(
        '--exclude',
        nargs='+',
        help='Schema patterns to exclude (default: refined_*)'
    )
    gen_all_parser.set_defaults(func=cmd_generate_all)
    
    # Index command
    idx_parser = subparsers.add_parser('index', help='Generate master index')
    idx_parser.add_argument(
        '--open',
        action='store_true',
        help='Open index in browser'
    )
    idx_parser.set_defaults(func=cmd_index)
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Full setup pipeline')
    setup_parser.add_argument(
        '--exclude',
        nargs='+',
        help='Schema patterns to exclude (default: refined_*)'
    )
    setup_parser.set_defaults(func=cmd_setup)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
