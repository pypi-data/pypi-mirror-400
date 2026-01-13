"""CLI for xelytics-core.

Command-line interface for running analysis.

Usage:
    xelytics analyze data.csv --mode automated
    xelytics analyze data.csv --output results.json
"""

import argparse
import sys
import json
from pathlib import Path

# CLI uses public API only - per plan constraints
from xelytics import analyze, AnalysisConfig


def main():
    """Main CLI entry point.
    
    CLI Constraints (enforced by design):
    - Uses public API only
    - Cannot import outside public API
    - Cannot bypass schemas
    - Outputs JSON only
    """
    parser = argparse.ArgumentParser(
        prog="xelytics",
        description="Statistical analysis and insight generation",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a dataset",
    )
    analyze_parser.add_argument(
        "file",
        type=str,
        help="Path to CSV file to analyze",
    )
    analyze_parser.add_argument(
        "--mode",
        type=str,
        choices=["automated", "semi-automated"],
        default="automated",
        help="Analysis mode (default: automated)",
    )
    analyze_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: stdout)",
    )
    analyze_parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level (default: 0.05)",
    )
    analyze_parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM-enhanced insights",
    )
    analyze_parser.add_argument(
        "--max-viz",
        type=int,
        default=10,
        help="Maximum visualizations (default: 10)",
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        "version",
        help="Show version",
    )
    
    args = parser.parse_args()
    
    if args.command == "version":
        from xelytics import __version__
        print(f"xelytics-core {__version__}")
        return 0
    
    if args.command == "analyze":
        return run_analyze(args)
    
    parser.print_help()
    return 1


def run_analyze(args) -> int:
    """Run analysis command."""
    import pandas as pd
    
    # Validate input file
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    
    try:
        # Load data
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            print(f"Error: Unsupported file format: {file_path.suffix}", file=sys.stderr)
            return 1
        
        # Build config
        config = AnalysisConfig(
            mode=args.mode,
            significance_level=args.alpha,
            enable_llm_insights=not args.no_llm,
            max_visualizations=args.max_viz,
        )
        
        # Run analysis - using public API only
        result = analyze(
            data=df,
            mode=args.mode,
            config=config,
        )
        
        # Output JSON
        json_output = result.to_json()
        
        if args.output:
            with open(args.output, "w") as f:
                f.write(json_output)
            print(f"Results written to: {args.output}")
        else:
            print(json_output)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
