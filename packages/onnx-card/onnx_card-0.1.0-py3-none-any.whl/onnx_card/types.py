from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TensorInfo:
    name: str
    dtype: Optional[str] = None
    shape: Optional[List[Optional[int]]] = None  # None for unknown dims


@dataclass
class Report:
    path: str
    size_bytes: int

    ir_version: Optional[int] = None
    opset: Optional[int] = None

    inputs: List[TensorInfo] = field(default_factory=list)
    outputs: List[TensorInfo] = field(default_factory=list)

    num_nodes: int = 0
    num_initializers: int = 0

    op_counts: Dict[str, int] = field(default_factory=dict)

