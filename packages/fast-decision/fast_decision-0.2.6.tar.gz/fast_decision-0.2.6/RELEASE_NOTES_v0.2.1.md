# Release v0.2.1

## What's New

### Metadata Support for Rules

This release adds optional metadata support to rules, enabling better traceability, compliance tracking, and debugging capabilities.

#### Key Features

- **Optional Metadata Field**: Add custom metadata to any rule for tracking, auditing, or debugging
- **Included in Results**: Metadata is automatically included in evaluation results when present
- **Flexible Structure**: Metadata can contain any JSON-compatible data (objects, arrays, strings, numbers, booleans)
- **Backward Compatible**: Existing rules without metadata continue to work seamlessly

#### Example Usage

**Rust:**
```rust
{
  "id": "Premium_Discount",
  "priority": 1,
  "conditions": {"user.tier": {"$equals": "Platinum"}},
  "action": "apply_discount",
  "metadata": {
    "source": "Pricing Rules v2.3",
    "tags": ["premium", "discount"],
    "created_by": "pricing_team",
    "last_updated": "2025-01-15"
  }
}
```

**Python:**
```python
from fast_decision import FastDecision

engine = FastDecision("rules.json")
results = engine.evaluate_rules_detailed(data, categories=["Pricing"])

for rule in results:
    print(f"Rule: {rule['id']}")
    if 'metadata' in rule:
        print(f"Source: {rule['metadata']['source']}")
        print(f"Tags: {rule['metadata']['tags']}")
```

#### Use Cases

- **Audit Logging**: Track which version of rules triggered a decision
- **Compliance**: Document rule sources, approval dates, and responsible teams
- **A/B Testing**: Tag rules with experiment IDs for tracking
- **Debugging**: Add diagnostic information to understand rule behavior
- **Documentation**: Embed descriptions and examples directly in rules

## Changes

### Added
- Optional `metadata` field in `Rule` structure (src/types.rs:197)
- Metadata serialization/deserialization support with `#[serde(skip_serializing_if = "Option::is_none")]`
- Type hints for metadata in `fast_decision.pyi`
- Comprehensive documentation in README.md and python/README.md
- Examples with metadata in demo.rs and test rules

### Documentation
- Updated main README.md with metadata field documentation
- Added "Rule Fields" section explaining all rule properties
- Updated python/README.md with Python-specific metadata examples
- Added "Using Metadata for Tracing and Compliance" section
- Updated examples/demo.rs with practical metadata usage

### Tests
- Added metadata to test rules in python/tests/rules.json
- Verified backward compatibility with rules without metadata

## Full Changelog

**Commits:**
- feat: add metadata support to rules
  - Add optional metadata field to Rule structure
  - Metadata included in evaluation results when present
  - Update type definitions in fast_decision.pyi
  - Add examples and documentation for metadata usage
  - Update version to 0.2.1

## Upgrade Guide

No breaking changes. Simply update to v0.2.1:

**Rust:**
```toml
[dependencies]
fast-decision = "0.2.1"
```

**Python:**
```bash
pip install --upgrade fast-decision
```

All existing rules continue to work without modification. Add metadata to rules as needed for your use case.

---

**Full Diff**: https://github.com/almayce/fast-decision/compare/v0.2.0...v0.2.1
