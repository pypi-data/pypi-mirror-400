from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Tuple

import onnx

from .types import Report, TensorInfo


def load_model(model_path: str | Path) -> onnx.ModelProto:
    """
    Load an ONNX model from a file path.
    """
    model_path = Path(model_path)
    return onnx.load(str(model_path))


def extract_tensor_info(value_info) -> TensorInfo:
    """
    Extract tensor information from ONNX ValueInfoProto.
    """
    name = value_info.name
    dtype = None
    shape = None

    if value_info.type.tensor_type:
        tensor_type = value_info.type.tensor_type
        # Extract dtype
        if tensor_type.elem_type:
            dtype = onnx.TensorProto.DataType.Name(tensor_type.elem_type)

        # Extract shape
        if tensor_type.shape:
            shape = []
            for dim in tensor_type.shape.dim:
                if dim.dim_value:
                    shape.append(dim.dim_value)
                elif dim.dim_param:
                    shape.append(None)  # Unknown dimension (symbolic)
                else:
                    shape.append(None)

    return TensorInfo(name=name, dtype=dtype, shape=shape)


def build_report(model_path: str | Path) -> Report:
    """
    Build a Report object from an ONNX model file.
    """
    model_path = Path(model_path)
    model = load_model(model_path)

    # Get file size
    size_bytes = model_path.stat().st_size

    # Extract metadata
    ir_version = model.ir_version if model.HasField("ir_version") else None
    opset = model.opset_import[0].version if model.opset_import else None

    # Get initializer names (weights/parameters, not entrypoint inputs)
    initializer_names = {init.name for init in model.graph.initializer}

    # Extract inputs - filter out initializers to get only entrypoint inputs
    inputs = [
        extract_tensor_info(vi)
        for vi in model.graph.input
        if vi.name not in initializer_names
    ]

    # Extract outputs (these are always entrypoint outputs)
    outputs = [extract_tensor_info(vi) for vi in model.graph.output]

    # Count nodes and initializers
    num_nodes = len(model.graph.node)
    num_initializers = len(model.graph.initializer)

    # Count operators
    op_counts = dict(Counter(node.op_type for node in model.graph.node))

    return Report(
        path=str(model_path),
        size_bytes=size_bytes,
        ir_version=ir_version,
        opset=opset,
        inputs=inputs,
        outputs=outputs,
        num_nodes=num_nodes,
        num_initializers=num_initializers,
        op_counts=op_counts,
    )


def sorted_counts(counts: Dict[str, int], sort: str = "count") -> Iterable[Tuple[str, int]]:
    """
    Return operator counts sorted either by:
      - sort="count": descending count, then name
      - sort="name": ascending name, then descending count
    """
    items = list(counts.items())
    if sort == "name":
        items.sort(key=lambda kv: (kv[0], -kv[1]))
    else:
        items.sort(key=lambda kv: (-kv[1], kv[0]))
    return items
