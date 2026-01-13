# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.5] - 07.01.26

### Fixed

- **Boolean Comparison**: Fixed equality comparison for boolean values in `compare_eq` function (src/engine.rs:55-57)
  - Previously, boolean values were not properly compared using their boolean representation
  - Now correctly handles boolean-to-boolean comparisons before falling back to general equality

## [0.2.1] - 17.12.25

### Added

- **Optional Metadata Field**: Rules can now include an optional `metadata` field for tracking, auditing, and debugging
  - Metadata can contain any JSON-compatible data (objects, arrays, strings, numbers, booleans)
  - Metadata is automatically included in evaluation results when present
  - Example:
    ```json
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

### Use Cases for Metadata

- **Audit Logging**: Track which version of rules triggered a decision
- **Compliance**: Document rule sources, approval dates, and responsible teams
- **A/B Testing**: Tag rules with experiment IDs for tracking
- **Debugging**: Add diagnostic information to understand rule behavior
- **Documentation**: Embed descriptions and examples directly in rules

### Documentation

- Updated main README.md with metadata field documentation
- Added "Rule Fields" section explaining all rule properties
- Updated python/README.md with Python-specific metadata examples
- Added "Using Metadata for Tracing and Compliance" section
- Updated examples/demo.rs with practical metadata usage
- Enhanced type hints in fast_decision.pyi for metadata support

### Technical Details

- Metadata field implemented as `Option<serde_json::Map<String, Value>>` in Rust
- Serialization uses `#[serde(skip_serializing_if = "Option::is_none")]` for efficiency
- Fully backward compatible - existing rules without metadata continue to work seamlessly
- No performance impact for rules without metadata

## [0.2.0] - 16.12.25

### BREAKING CHANGES

This release includes breaking changes to operator naming. All operators have been renamed to use kebab-case full names for improved clarity and consistency.

#### Operator Renames (BREAKING)

| Old Name | New Name |
|----------|----------|
| `$eq` | `$equals` |
| `$ne` | `$not-equals` |
| `$gt` | `$greater-than` |
| `$lt` | `$less-than` |
| `$gte` | `$greater-than-or-equals` |
| `$lte` | `$less-than-or-equals` |

### Migration Guide

To migrate from v0.1.x to v0.2.0, update all rule JSON files:

**Before (v0.1.x):**
```json
{
  "conditions": {
    "age": {"$gte": 18, "$lt": 65},
    "status": {"$eq": "active", "$ne": "banned"}
  }
}
```

**After (v0.2.0):**
```json
{
  "conditions": {
    "age": {"$greater-than-or-equals": 18, "$less-than": 65},
    "status": {"$equals": "active", "$not-equals": "banned"}
  }
}
```

### Added

#### New Operators

- **`$in`**: Check if value is in array
  - Example: `{"tier": {"$in": ["Gold", "Platinum", "Diamond"]}}`
  - Use case: Membership checks, allowlists

- **`$not-in`**: Check if value is NOT in array
  - Example: `{"status": {"$not-in": ["banned", "suspended"]}}`
  - Use case: Blocklists, exclusion rules

- **`$contains`**: Case-sensitive substring check for strings
  - Example: `{"description": {"$contains": "premium"}}`
  - Use case: Text filtering, keyword matching

- **`$starts-with`**: Check if string starts with value
  - Example: `{"name": {"$starts-with": "Dr."}}`
  - Use case: Prefix matching, title checks

- **`$ends-with`**: Check if string ends with value
  - Example: `{"email": {"$ends-with": "@company.com"}}`
  - Use case: Domain restrictions, suffix validation

- **`$regex`**: Regular expression matching
  - Example: `{"email": {"$regex": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}}`
  - Use case: Complex pattern matching, validation
  - Note: Regex patterns are compiled at evaluation time

#### Dependencies

- Added `regex` crate v1.10 for `$regex` operator support

### Performance

- All new operators follow the same performance patterns as existing operators
- String operators (`$contains`, `$starts-with`, `$ends-with`) use inline optimizations
- `$in` and `$not-in` leverage iterator short-circuiting
- `$regex` compiles patterns at evaluation time (may have performance impact for complex patterns)

### Documentation

- Updated all operator documentation with new names
- Added comprehensive examples for all new operators
- Updated Python type stubs
- Added migration guide for v0.1.x users

## [0.1.0] - 10.12.25

### Added
- Initial release of fast-decision rule engine
- Condition operators: `$eq`, `$ne`, `$gt`, `$lt`, `$gte`, `$lte`, `$and`, `$or`
- Priority-based rule evaluation (lower priority = higher precedence)
- Stop-on-first matching per category
- Python bindings via PyO3 for native performance
- Rust library with zero-cost abstractions
- Comprehensive documentation and examples
- Benchmark suite with Criterion
- Type-safe API for both Rust and Python
- Nested field access with dot notation (e.g., "user.profile.age")
- Complex logical predicates with AND/OR operators

### Performance
- Link Time Optimization (LTO) enabled
- Inline optimizations for hot path functions
- Pre-allocated result vectors
- Optimized data structures (`Box<[String]>`, `#[repr(u8)]`)
- Minimal allocations during rule evaluation
