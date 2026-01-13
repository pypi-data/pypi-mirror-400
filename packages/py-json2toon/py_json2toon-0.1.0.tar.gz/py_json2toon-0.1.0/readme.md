# json2toon

Convert JSON structures into TOON (Token-Oriented Object Notation) and back again, with tooling to measure token savings and create ready-to-send prompts for LLMs.

## At a glance
- JSON <-> TOON conversion (`json_to_toon`, `toon_to_json`, `convert_file`)
- Configurable formatting (indent, separators, quoting, table layouts)
- Automatic table layout for uniform object arrays
- Token counting and comparison reports
- Prompt helpers to wrap TOON payloads for LLMs
- Rich CLI with syntax highlighting and reports
- Fully covered by pytest (39 passing tests)

## Install

```bash
pip install json2toon
```

## CLI usage

The CLI is exposed as `json2toon`.

```bash
# JSON -> TOON
json2toon to-toon input.json -o output.toon

# TOON -> JSON (pretty by default)
json2toon to-json input.toon -o output.json

# Token comparison report
json2toon report input.json -f table
json2toon report input.json -f json   # machine-readable
```

Flags of interest:
- `-c/--config` load a JSON config file (see Config section)
- `-p/--pretty` pretty-print TOON or JSON when writing to stdout
- `-P/--no-pretty` disable pretty JSON output
- `-o/--output` write to a file instead of stdout

Examples:

```bash
# Convert and view with highlighting
json2toon to-toon sample.json --pretty

# Round trip via files
json2toon to-toon sample.json -o sample.toon
json2toon to-json sample.toon -o sample.roundtrip.json

# Get a JSON report of token savings
json2toon report sample.json -f json > stats.json
```

## Python API

Import from `json2toon`:

```python
from json2toon import (
    json_to_toon, toon_to_json, convert_file, get_conversion_stats,
    ToonEncoder, ToonDecoder, ToonConfig,
    compare_formats, count_tokens, generate_report,
    create_llm_prompt, create_response_template, wrap_in_code_fence, add_system_prompt,
)
```

### Core helpers (`core.py`)
- `json_to_toon(data, config=None) -> str`: Encode any JSON-serializable Python data to TOON.
- `toon_to_json(toon_str, config=None) -> Any`: Decode TOON back to Python data.
- `convert_file(input_path, output_path, to_toon=True, config=None)`: File-level conversion in either direction.
- `get_conversion_stats(data, config=None, output_format="text") -> dict`: Compute token counts, savings, and a formatted report (text/json/markdown).

### Encoder (`encoder.py`)
- `ToonEncoder.encode(data) -> str`: Main entry. Handles primitives, objects, arrays, tables, indentation, string quoting/escaping, and inline vs block arrays.
- Table layout: for uniform arrays of dicts (based on `uniformity_threshold` and `min_table_rows`), arrays render as ASCII tables.

### Decoder (`decoder.py`)
- `ToonDecoder.decode(toon_str) -> Any`: Parses tables, list items, objects, primitives, inline JSON, and escaped strings/newlines.

### Config (`config.py`)
- `ToonConfig` fields:
  - `separator` (default `:`)
  - `table_separator` (default `|`), `header_separator`
  - `max_inline_array_length`, `compress_primitive_arrays`
  - `max_string_length`, `quote_strings`
  - `indent_size`, `max_nesting_depth`
  - `uniformity_threshold`, `min_table_rows`
- `get_default_config()` returns defaults.
- `save_config(config, path)`, `load_config(path)` to persist/restore.

### Analysis (`analyzer.py`)
- `analyze_structure(data, config) -> StructureInfo`: Classifies primitives, objects, arrays, and detects uniform arrays.
- `is_uniform_array(arr, threshold=0.8) -> (bool, keys)` used by the encoder.
- `should_use_table_format(data, config) -> bool` selects table layout.

### Metrics (`metrics.py`)
- `count_tokens(text, encoding_name="cl100k_base") -> int`: Uses `tiktoken` to count tokens.
- `compare_formats(data, encoder, encoding_name="cl100k_base") -> ComparisonResult`: Token counts for JSON vs TOON.
- `generate_report(comparison, output_format="text") -> str`: Formats text/json/markdown reports.

### Prompt helpers (`prompt.py`)
- `create_llm_prompt(toon_str, system_prompt=None)`: Wrap TOON payloads for model input.
- `create_response_template()`: Skeleton for expected model replies.
- `wrap_in_code_fence(text, language="toon")`: Add triple-backtick fences.
- `add_system_prompt(prompt, system_prompt)`: Prepend system guidance.

### CLI (`cli.py`)
- Commands: `to-toon`, `to-json`, `report`. All support optional config loading and pretty-print toggles. Success output uses ASCII-only markers for Windows compatibility.

### Exceptions (`exceptions.py`)
`EncodingError`, `DecodingError`, `AnalysisError`, `ConfigurationError` all derive from `Json2ToonError`.

## Usage examples

### Programmatic round trip
```python
from json2toon import json_to_toon, toon_to_json

data = {"name": "Alice", "scores": [95, 87, 92]}
toon = json_to_toon(data)
restored = toon_to_json(toon)
assert restored == data
```

### Custom config
```python
from json2toon import ToonConfig, ToonEncoder

config = ToonConfig(indent_size=4, quote_strings=True, table_separator='|')
encoder = ToonEncoder(config)
toon = encoder.encode({"users": [{"id": 1, "name": "Bob"}, {"id": 2, "name": "Eve"}]})
print(toon)
```

### Token savings report
```python
from json2toon import ToonEncoder, compare_formats, generate_report

data = {"items": [
    {"id": 1, "name": "Alpha"},
    {"id": 2, "name": "Beta"},
]}
encoder = ToonEncoder()
comparison = compare_formats(data, encoder)
print(generate_report(comparison, output_format="markdown"))
```

### Build an LLM prompt
```python
from json2toon import json_to_toon, create_llm_prompt

data = {"request": "Summarize", "payload": {"text": "Hello world"}}
toon = json_to_toon(data)
prompt = create_llm_prompt(toon, system_prompt="You are a concise assistant.")
print(prompt)
```

## Configuration file example

Save as `toon_config.json`:

```json
{
  "separator": ":",
  "table_separator": "|",
  "header_separator": "-",
  "max_inline_array_length": 8,
  "compress_primitive_arrays": true,
  "quote_strings": true,
  "indent_size": 2,
  "uniformity_threshold": 0.75,
  "min_table_rows": 2
}
```

Use it:

```bash
json2toon to-toon data.json -c toon_config.json -o data.toon
```

## Project layout

```
src/json2toon/
  analyzer.py     # structure detection, uniformity checks
  cli.py          # Typer-based CLI
  config.py       # ToonConfig dataclass + load/save
  core.py         # top-level helpers and file conversion
  decoder.py      # TOON -> Python
  encoder.py      # Python -> TOON
  exceptions.py   # custom exception types
  metrics.py      # token counting and reports
  prompt.py       # LLM prompt utilities
tests/            # pytest suite (39 tests)
```

## Development

```bash
python -m pytest           # run tests
python -m pytest --cov     # run with coverage
```

The suite exercises all public APIs (encode/decode, configs, CLI, metrics, prompt helpers) and passes on Windows with ASCII-only CLI output.

