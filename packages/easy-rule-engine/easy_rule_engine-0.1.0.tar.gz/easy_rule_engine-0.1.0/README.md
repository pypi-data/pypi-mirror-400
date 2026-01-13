## easy-rule-engine

A tiny, composable rule engine for Python.

- **Specification**: composable predicates (`&`, `|`, `~`)
- **Transformer**: immutable transformations (returns a new item)
- **Rule**: `condition + transform (+ stop_on_match)`
- **RuleEngine**: applies rules to items (`match_mode=all|first`, `keep_unmatched`)

### Install

```bash
uv add easy-rule-engine
```

### Quick start

```python
from easy_rule_engine import Rule, RuleEngine, attr_spec, attr_transform, dict_setter

users = [
    {"name": "Tom", "age": 15, "status": "UNKNOWN"},
    {"name": "Alice", "age": 20, "status": "OK"},
]

get_age = lambda u: u["age"]
get_status = lambda u: u["status"]

is_minor = attr_spec(get_age, lambda v: v < 18)
set_minor = attr_transform(
    getter=get_status,
    setter=dict_setter("status"),
    value_func=lambda _old: "MINOR",
)

engine = RuleEngine(
    rules=[Rule(condition=is_minor, transform=set_minor, name="minor")],
    keep_unmatched=True,
)

print(engine.process(users))
```

### Examples

Example scripts live in `examples/`.

Recommended (after syncing the project environment; see Development):

```bash
uv run python examples/dict_filter_and_transform.py
uv run python examples/dataclass_transform.py
uv run python examples/order_discounts_and_shipping.py
uv run python examples/risk_scoring_with_priorities.py
uv run python examples/two_phase_pipeline.py
```

### Development

Create/update the project environment (recommended; installs the project editable by default):

```bash
uv sync
```

Run unit tests:

```bash
uv run python -m unittest -q
```

If you want to disable editable installs (not recommended for development):

```bash
uv sync --no-editable
```

If you prefer not to install, you can still run from source with:

```bash
PYTHONPATH=src uv run python -m unittest -q
PYTHONPATH=src uv run python examples/dict_filter_and_transform.py
```

Build distributions (sdist + wheel):

```bash
uv pip install -U build
uv run python -m build
```
