# onnx-card

Provide a fast, accurate, terminal-first “ONNX card” describing what is inside an ONNX model — without running it.

`onnx-card` loads an ONNX model and prints a clean, colorized card showing:
- Model name and metadata (opset, IR version)
- Entrypoint inputs and outputs (with shapes and dtypes)
- Operator counts and statistics

Built for:
- quick inspection
- terminal-first workflows
- scripting and CI usage

---

## Installation

From source (development):

```bash
pip install -e .
````

Once published on PyPI:

```bash
pip install onnx-card
```

---

## Usage

Basic usage:

```bash
onnx-card model.onnx
```

Limit output to top operators:

```bash
onnx-card model.onnx --top 10
```

Sort alphabetically instead of by count:

```bash
onnx-card model.onnx --sort name
```

Select which tables to display:

```bash
onnx-card model.onnx --show io          # Only inputs/outputs
onnx-card model.onnx --show operators   # Only operator counts
onnx-card model.onnx --show all         # Everything (default)
```

JSON output (for scripts / CI):

```bash
onnx-card model.onnx --json
```

You can also run it as a module:

```bash
python -m onnx_card model.onnx
```

---

## Requirements

* Python ≥ 3.9
* `onnx`
* `rich`

---

## License

MIT
