# Fast Decision - Python Usage

High-performance rule engine with Python bindings.

## Installation

### Development Installation

```bash
# 1. Install maturin (from project root)
pip install maturin

# 2. Build and install in development mode
maturin develop

# 3. Run example
cd python/tests
python test_features.py

# 4. Run tests
cd python/tests
python test_features.py
```

### Production Build

```bash
# Build wheel (from project root)
maturin build --release

# Install wheel
pip install target/wheels/fast_decision-*.whl

# Test
cd python/tests
python test_features.py
```

## Usage

### 1. Create Rules JSON

```json
{
  "categories": {
    "Pricing": {
      "stop_on_first": true,
      "rules": [
        {
          "id": "R1_Premium",
          "priority": 1,
          "conditions": {
            "user.tier": {"$eq": "Premium"}
          },
          "action": "apply_premium_discount",
          "metadata": {
            "source": "Pricing Rules v2.3",
            "tags": ["premium", "discount"],
            "description": "Optional custom data for tracking and compliance"
          }
        }
      ]
    }
  }
}
```

#### Rule Fields

- **id** (required): Unique rule identifier
- **priority** (required): Evaluation priority (lower = higher precedence)
- **conditions** (required): Condition tree for evaluation
- **action** (required): Action identifier (informational, not evaluated by engine)
- **metadata** (optional): Custom metadata dictionary. If present, will be included in evaluation results returned by `evaluate_rules_detailed()`.

### 2. Python Code

```python
from fast_decision import FastDecision

# Load rules
engine = FastDecision("rules.json")

# Evaluate
data = {"user": {"tier": "Premium"}, "amount": 100}
results = engine.evaluate_rules(data, categories=["Pricing"])

# Process results
for rule_id in results:
    if rule_id == "R1_Premium":
        apply_discount(data)
```

## Features

- **Priority-based evaluation**: Lower priority numbers evaluate first
- **Stop-on-first**: Stop after first matching rule (per category)
- **Condition operators**: $eq, $ne, $gt, $lt, $gte, $lte
- **Zero-copy performance**: Direct dict to Rust conversion
- **Type safety**: Full type checking in both Rust and Python

## API Reference

### FastDecision

#### `__init__(rules_path: str)`
Load rules from JSON file.

#### `evaluate_rules(data: dict, categories: list[str]) -> list[str]`
Evaluate rules and return list of triggered rule IDs.

#### `evaluate_rules_from_json(data_json: str, categories: list[str]) -> list[str]`
Evaluate rules from JSON string.

## Advanced Examples

### Complex Conditions with OR Logic

```python
rules = {
    "categories": {
        "Eligibility": {
            "stop_on_first": False,
            "rules": [
                {
                    "id": "VIP_User",
                    "priority": 1,
                    "conditions": {
                        "$or": [
                            {"user.tier": {"$eq": "Platinum"}},
                            {"user.spend_total": {"$gt": 10000}}
                        ]
                    },
                    "action": "grant_vip_access",
                    "metadata": {
                        "source": "Loyalty Program v3.1",
                        "tags": ["vip", "eligibility"],
                        "audit_log": True
                    }
                }
            ]
        }
    }
}
```

### Using Metadata for Tracing and Compliance

```python
from fast_decision import FastDecision

engine = FastDecision("rules.json")

data = {"user": {"tier": "Platinum"}, "amount": 500}

# Get detailed results including metadata
results = engine.evaluate_rules_detailed(data, categories=["Pricing"])

for rule in results:
    print(f"Rule: {rule['id']}")
    print(f"Action: {rule['action']}")
    if 'metadata' in rule:
        # Use metadata for audit logging, tracking, or debugging
        print(f"Source: {rule['metadata'].get('source')}")
        print(f"Tags: {rule['metadata'].get('tags')}")
```

### Nested Field Access

```python
data = {
    "user": {
        "profile": {
            "settings": {
                "notifications": True
            }
        }
    }
}

# Access with dot notation in rules
conditions = {
    "user.profile.settings.notifications": {"$eq": True}
}
```

### Multiple Operators on Same Field

```python
# Age between 18 and 65 (implicit AND)
conditions = {
    "age": {"$gte": 18, "$lt": 65}
}
```

## Error Handling

```python
from fast_decision import FastDecision

try:
    engine = FastDecision("rules.json")
    results = engine.evaluate_rules(data, categories=["Pricing"])
except FileNotFoundError:
    print("Rules file not found")
except ValueError as e:
    print(f"Invalid rules JSON: {e}")
except TypeError as e:
    print(f"Invalid data type: {e}")
```

## Type Hints

Type stubs are included for IDE support:

```python
from fast_decision import FastDecision
from typing import Dict, List, Any

engine: FastDecision = FastDecision("rules.json")
data: Dict[str, Any] = {"user": {"tier": "Gold"}}
results: List[str] = engine.evaluate_rules(data, categories=["Pricing"])
```

## Performance Tips

### Use evaluate_rules_from_json for Pre-Serialized Data

```python
import json

# If data is already JSON string
data_json = json.dumps({"user": {"tier": "Gold"}})
results = engine.evaluate_rules_from_json(data_json, categories=["Pricing"])
```

This is faster than `evaluate_rules()` if your data is already in JSON format, as it skips Python→Rust type conversion.

### Reuse Engine Instance

```python
# Good - reuse engine
engine = FastDecision("rules.json")
for data in dataset:
    results = engine.evaluate_rules(data, categories=["Pricing"])

# Bad - creates new engine each time
for data in dataset:
    engine = FastDecision("rules.json")  # Slow!
    results = engine.evaluate_rules(data, categories=["Pricing"])
```

### Use stop_on_first When Possible

```json
{
  "stop_on_first": true  // Stops after first match - faster
}
```

## Performance

- **Rust backend**: Native machine code performance
- **Minimal allocations**: Pre-allocated result vectors
- **Direct conversion**: Python dict → Rust without intermediate JSON serialization
- **Inline optimizations**: Hot path functions marked for inlining
- **~10-100x faster** than pure Python implementations for complex rule sets

## Troubleshooting

### Import Error

```python
# Error: ModuleNotFoundError: No module named 'fast_decision'

# Solution: Rebuild and install
maturin develop --release
```

### Type Error with Data

```python
# Error: TypeError: Unsupported type

# Solution: Ensure all data is JSON-serializable types
# Supported: dict, list, str, int, float, bool, None
# Not supported: custom classes, datetime, etc.
```

### Rules Not Triggering

```python
# Check field paths match your data structure
data = {"user": {"tier": "Gold"}}  # Correct path: "user.tier"

# Enable logging to debug
import logging
logging.basicConfig(level=logging.DEBUG)
```
