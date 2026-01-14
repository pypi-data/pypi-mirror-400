from __future__ import annotations

import json
from typing import Dict

from rich.console import Console
from rich.table import Table

from .core import sorted_counts
from .types import Report


def format_shape(shape: list[int | None] | None) -> str:
    """
    Format a shape list for display.
    """
    if shape is None:
        return "?"
    parts = []
    for dim in shape:
        if dim is None:
            parts.append("?")
        else:
            parts.append(str(dim))
    return f"[{', '.join(parts)}]"


def print_report_rich(report: Report, sort: str = "count", top: int = 0, show: str = "all") -> None:
    """
    Print a Report using Rich formatting (table).

    Args:
        report: The Report to display
        sort: Sort order for operators ("count" or "name")
        top: Show only top N operators (0 = all)
        show: Which tables to display ("all", "io", "operators", "inputs", "outputs")
    """
    console = Console()

    # Extract model name from path
    model_name = report.path.split('/')[-1].split('\\')[-1]  # Handle both / and \ separators
    
    # Build header with model name and metadata
    header_parts = []
    if report.opset:
        header_parts.append(f"opset {report.opset}")
    if report.ir_version:
        header_parts.append(f"IR v{report.ir_version}")
    
    # Print model name at top
    console.print(f"[bold white]{model_name}[/bold white]", end="")
    if header_parts:
        console.print(f"  [dim]{' • '.join(header_parts)}[/dim]")
    else:
        console.print()
    console.print()

    # Determine which tables to show
    if show == "default":
        # Default: show entrypoint inputs, outputs, and operators
        show_inputs = True
        show_outputs = True
        show_operators = True
    else:
        show_inputs = show in ("all", "io", "inputs")
        show_outputs = show in ("all", "io", "outputs")
        show_operators = show in ("all", "operators")

    # Print merged IO table
    if (show_inputs and report.inputs) or (show_outputs and report.outputs):
        io_table = Table(title="Inputs & Outputs", show_header=True, header_style="bold cyan", padding=(0, 1))
        io_table.add_column("Type", no_wrap=True, style="dim")
        io_table.add_column("Name", no_wrap=True, style="white")
        io_table.add_column("Shape", no_wrap=True, style="blue")
        io_table.add_column("Dtype", no_wrap=True, style="yellow")

        # Add inputs
        if show_inputs:
            for inp in report.inputs:
                shape_str = format_shape(inp.shape)
                dtype_str = inp.dtype or "?"
                io_table.add_row("[dim]input[/dim]", inp.name, shape_str, dtype_str)

        # Add outputs
        if show_outputs:
            for out in report.outputs:
                shape_str = format_shape(out.shape)
                dtype_str = out.dtype or "?"
                io_table.add_row("[dim]output[/dim]", out.name, shape_str, dtype_str)

        console.print(io_table)
        console.print()

    # Build operator counts table
    if show_operators:
        items = list(sorted_counts(report.op_counts, sort=sort))
        if top and top > 0:
            items = items[:top]

        table = Table(title="Operator Counts", show_header=True, header_style="bold cyan", padding=(0, 1))
        table.add_column("Operator", no_wrap=True, style="white")
        table.add_column("Count", justify="right", style="green")

        for op, cnt in items:
            table.add_row(op, str(cnt))

        console.print(table)
        # Print caption aligned with table left edge
        caption_text = f"Unique operators: {len(report.op_counts)} • Total nodes: {report.num_nodes}"
        console.print(f"[dim]{caption_text}[/dim]")


def print_report_json(report: Report, sort: str = "count", top: int = 0) -> None:
    """
    Print a Report as JSON.
    """
    console = Console()

    # Prepare sorted operator counts
    items = list(sorted_counts(report.op_counts, sort=sort))
    if top and top > 0:
        items = items[:top]

    # Build JSON payload
    payload = {
        "model": report.path,
        "size_bytes": report.size_bytes,
        "ir_version": report.ir_version,
        "opset": report.opset,
        "inputs": [
            {
                "name": inp.name,
                "dtype": inp.dtype,
                "shape": inp.shape,
            }
            for inp in report.inputs
        ],
        "outputs": [
            {
                "name": out.name,
                "dtype": out.dtype,
                "shape": out.shape,
            }
            for out in report.outputs
        ],
        "num_nodes": report.num_nodes,
        "num_initializers": report.num_initializers,
        "unique_operators": len(report.op_counts),
        "operators": {op: cnt for op, cnt in items},
    }

    console.print(json.dumps(payload, indent=2))

