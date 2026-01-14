from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from .core import build_report
from .render import print_report_json, print_report_rich


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="onnx-card",
        description="Print an operator histogram for an ONNX model.",
    )
    p.add_argument("model", help="Path to .onnx model file")
    p.add_argument(
        "--sort",
        choices=["count", "name"],
        default="count",
        help="Sort operators by count (desc) or name (asc)",
    )
    p.add_argument("--top", type=int, default=0, help="Show only top N operators (0 = all)")
    p.add_argument(
        "--show",
        choices=["default", "all", "io", "operators", "inputs", "outputs"],
        default="default",
        help="Select which tables to display (default: inputs + outputs + operators)",
    )
    p.add_argument("--json", action="store_true", help="Output JSON instead of a table")
    return p


def main(argv: list[str] | None = None) -> int:
    console = Console()
    args = build_parser().parse_args(argv)

    model_path = Path(args.model)
    if not model_path.exists():
        console.print(f"[red]Error:[/red] file not found: {model_path}")
        return 2

    try:
        report = build_report(model_path)
    except Exception as e:
        console.print(f"[red]Error:[/red] failed to read ONNX: {e}")
        return 1

    if args.json:
        print_report_json(report, sort=args.sort, top=args.top)
    else:
        print_report_rich(report, sort=args.sort, top=args.top, show=args.show)

    return 0
