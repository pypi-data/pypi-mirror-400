# fast-decision

[![Crates.io](https://img.shields.io/crates/v/fast-decision.svg)](https://crates.io/crates/fast-decision)
[![PyPI](https://img.shields.io/pypi/v/fast-decision.svg)](https://pypi.org/project/fast-decision/)
[![License](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](https://github.com/almayce/fast-decision#license)

A high-performance rule engine written in Rust with Python bindings, designed for applications that need to evaluate complex business rules with minimal latency and maximum throughput.

## Features

- **High Performance**: Rust-powered engine with zero-cost abstractions
- **Priority-based Evaluation**: Rules sorted by priority (lower number = higher priority)
- **Stop-on-First**: Per-category flag to stop after first match
- **Condition Operators**: Familiar syntax with `$equals`, `$not-equals`, `$greater-than`, `$less-than`, `$greater-than-or-equals`, `$less-than-or-equals`, `$and`, `$or`
- **Complex Logic**: Support for nested AND/OR predicates
- **Python Bindings**: Native performance with idiomatic Python API via PyO3
- **Memory Efficient**: Minimal allocations in hot path, optimized data structures
- **Benchmarked**: Built-in performance benchmarks with Criterion

## Use Cases

Fast Decision is ideally suited for systems where performance and low decision latency are critical.

### 1. Core Business Logic and Processes

* **Business Rule Engines** (Classical rule systems for decision automation)
    * Transaction Approval/Rejection (Fast checking of conditions for immediate decisions, e.g., limits or stop-lists).
    * Commission and Fee Calculation (Determining the exact amount based on customer type, region, and transaction volume).
    * Management of Complex Contract Conditions (Automating the verification of product or service compliance with contract terms).
* **Workflow Automation**
    * Document Routing (Directing a request for approval to the correct department based on amount, document type, or initiator's role).
    * Task Status Management (Automatic transition of a task to "Awaiting Review" status upon fulfillment of all preceding conditions).

### 2. Financial and Commercial

* **Dynamic Pricing Systems**
    * Real-time Discount Calculation (Applying complex discount rules based on purchase history, loyalty level, inventory, and current promotions).
    * Product Pricing Tier Determination (Instant assignment of a category based on product characteristics, critical for high-volume E-commerce).
* **Credit Scoring and Underwriting** (Fast risk assessment)
    * Initial Application Scoring (Immediate filtering of applications that do not meet minimum criteria, using "Stop-on-First" logic for high performance).
    * Fraud Detection (Rapid assessment of transaction patterns in real-time before processing).

### 3. Security and Authorization

* **Access Control and Authorization (ABAC)** (Access management based on roles and attributes)
    * User Rights Determination (Granting access to a resource based not only on role but also on attributes: time of day, IP address, subscription level).
    * API Request Control (Quick verification of every incoming request against allowed limits and conditions).
* **Feature Flags and A/B Testing**
    * Feature Toggling (Determining which version of a feature a specific user should be shown, based on their ID, geography, or registration date).
    * Traffic Splitting (Directing 10% of traffic to a new, experimental version of a service).

### 4. Data and Infrastructure

* **Data Validation and Filtering**
    * Input Data Cleansing (Fast checking and discarding of incomplete or incorrect records before saving them to the database).
    * Event Routing (Directing events from a general stream like Kafka/RabbitMQ to a specific handler based on event type or criticality).
* **Configuration and Settings** (Decision making for system configuration)
    * System Configuration Determination (Selecting optimal service startup parameters based on environment, load, or other input data).
    * Alerting and Monitoring (Triggering alerts only when a combination of multiple conditions is met: high CPU load **AND** low disk space).

### 5. Development and Code Governance

* **Priority-based Execution**
    * Cascading Rule Application (For example, first applying a "Global Ban," then a "Special Permission," using numerical priorities).
    * Stop on First Match (Using the "Stop-on-First" flag to boost performance in categories where one successful rule is sufficient).
* **Python Bindings** (Using the Rust engine within the Python ecosystem)
    * Integration with Django/Flask (Using a high-performance Rule Engine for critical logic in standard Python applications).
    * Fast Processing in Data Science (Applying rules to large data dictionaries for quick labeling or filtering before feeding into an ML model).

### 6. Telecommunications and IoT (Telecom & Internet of Things)

* **Real-time Data Processing** (Processing data in real-time with low latency)
    * Sensor Data Filtering (Rapidly discarding noise or incorrect readings from IoT sensors directly at the edge network).
    * Network Traffic Routing (Making decisions on packet direction based on IP addresses, ports, or protocols with minimal delay).
* **Edge Computing Decisions** (Decision making at the network edge)
    * Autonomous Device Actions (Local decision making by an IoT device (e.g., turn a pump on/off) without relying on the central cloud, based on local rules).

### 7. Gaming Industry

* **Anti-Cheat Logic**
    * Instant Verification of Suspicious Actions (Applying complex logic to detect unnatural player action patterns in real-time).
* **In-Game Events and Rewards**
    * Reward Triggers (Automatic crediting of bonuses or initiation of events upon the fulfillment of a combination of in-game conditions).

### 8. Government Sector and Compliance

* **Regulatory Compliance Checks**
    * Automatic Form Verification (Quickly determining if an application meets all governmental or internal regulatory requirements before submission).
* **Eligibility Determination**
    * Criteria Calculation (Instantly determining whether a citizen is entitled to a specific service or benefit based on input data).

### 9. ML Optimization

* **Pre-Processing Filters**
    * Low-Quality Data Exclusion (Quickly discarding records that may introduce noise into the model before they enter the training pipeline, saving computational resources).
    * Basic Segmentation (Using rules to separate the incoming data stream by type before feeding them into specialized models).
* **Model Switching and Orchestration**
    * Model Version Switching (Deciding which version of an ML model to use—old stable or new experimental—based on input parameters, such as region or risk level).

### 10. Content Management Systems (CMS)

* **Content Personalization**
    * Dynamic Page Layout (Determining which ad banner, article, or product should be shown to a user based on their session, device, and browsing history).
    * Automatic Moderation (Rapid verification of user-generated content—comments, listings—for compliance with stop-words, publishing frequency, or other rules, prior to manual review).

### 11. System Integration and Migration

* **Data Mapping and Transformation**
    * Format Conversion (Using rules to transform a complex JSON event from a legacy system into the format required by a new system, for example, changing field names or merging values).
* **Legacy System Decoupling**
    * "Shadow" Logic Execution (Running new rules parallel to legacy logic to compare results and ensure a smooth transition without downtime).

## Installation

### Rust

Add to your `Cargo.toml`:

```toml
[dependencies]
fast-decision = "0.2.4"
```

### Python

```bash
pip install fast-decision
```

Or install from source:

```bash
git clone https://github.com/almayce/fast-decision.git
cd fast-decision
maturin develop --release
```

## Quick Start

### Rust Example

```rust
use fast_decision::{RuleEngine, RuleSet};
use serde_json::json;

fn main() {
    let rules_json = r#"
    {
      "categories": {
        "Pricing": {
          "stop_on_first": true,
          "rules": [
            {
              "id": "Platinum_Discount",
              "priority": 1,
              "conditions": {"user.tier": {"$equals": "Platinum"}},
              "action": "apply_20_percent_discount"
            },
            {
              "id": "Gold_Discount",
              "priority": 10,
              "conditions": {"user.tier": {"$equals": "Gold"}},
              "action": "apply_10_percent_discount"
            }
          ]
        }
      }
    }
    "#;

    let ruleset: RuleSet = serde_json::from_str(rules_json).unwrap();
    let engine = RuleEngine::new(ruleset);

    let data = json!({
        "user": {"tier": "Gold", "id": 123},
        "transaction": {"amount": 100}
    });

    let results = engine.evaluate_rules(&data, &["Pricing"]);
    println!("Triggered rules: {:?}", results);
    // Output: ["Gold_Discount"]
}
```

### Python Example

See [python/README.md](python/README.md) for detailed Python documentation.

```python
from fast_decision import FastDecision

# Load rules from JSON file
engine = FastDecision("rules.json")

# Evaluate rules
data = {
    "user": {"tier": "Gold", "id": 123},
    "transaction": {"amount": 100}
}

results = engine.evaluate_rules(data, categories=["Pricing"])
print(f"Triggered rules: {results}")
# Output: ['Gold_Discount']
```

## Rule Format

Rules are defined in JSON:

```json
{
  "categories": {
    "CategoryName": {
      "stop_on_first": true,
      "rules": [
        {
          "id": "rule_identifier",
          "priority": 1,
          "conditions": {
            "field.path": {"$equals": "value"}
          },
          "action": "action_name",
          "metadata": {
            "source": "Pricing Rules v2.3",
            "tags": ["discount", "promotion"],
            "description": "Optional custom data for tracking"
          }
        }
      ]
    }
  }
}
```

### Rule Fields

- **id** (required): Unique rule identifier
- **priority** (required): Evaluation priority (lower = higher precedence)
- **conditions** (required): Condition tree for evaluation
- **action** (required): Action identifier (informational, not evaluated by engine)
- **metadata** (optional): Custom metadata for tracing, compliance, or annotations. Will be included in evaluation results if present.

### Supported Operators

#### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$equals` | Equal | `{"age": {"$equals": 18}}` |
| `$not-equals` | Not equal | `{"status": {"$not-equals": "inactive"}}` |
| `$greater-than` | Greater than | `{"score": {"$greater-than": 100}}` |
| `$less-than` | Less than | `{"price": {"$less-than": 50}}` |
| `$greater-than-or-equals` | Greater than or equal | `{"age": {"$greater-than-or-equals": 21}}` |
| `$less-than-or-equals` | Less than or equal | `{"count": {"$less-than-or-equals": 10}}` |

#### Membership Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$in` | Value in array | `{"tier": {"$in": ["Gold", "Platinum"]}}` |
| `$not-in` | Value not in array | `{"status": {"$not-in": ["banned", "suspended"]}}` |

#### String Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$contains` | Case-sensitive substring | `{"description": {"$contains": "premium"}}` |
| `$starts-with` | String starts with | `{"name": {"$starts-with": "Dr."}}` |
| `$ends-with` | String ends with | `{"email": {"$ends-with": "@company.com"}}` |
| `$regex` | Regular expression | `{"email": {"$regex": "^[a-z]+@[a-z]+\\.[a-z]+$"}}` |

### Logical Operators

**Implicit AND** - Multiple conditions in one object:
```json
{
  "conditions": {
    "age": {"$greater-than-or-equals": 18, "$less-than": 65},
    "status": {"$equals": "active"}
  }
}
```

**Explicit OR** - Use `$or`:
```json
{
  "conditions": {
    "$or": [
      {"tier": {"$equals": "Platinum"}},
      {"score": {"$greater-than": 1000}}
    ]
  }
}
```

**Nested Logic**:
```json
{
  "conditions": {
    "$or": [
      {"tier": {"$equals": "Platinum"}},
      {
        "tier": {"$equals": "Gold"},
        "amount": {"$greater-than": 500}
      }
    ]
  }
}
```

## Performance

### Benchmarks

Run benchmarks:
```bash
cargo bench
```

### Optimization Features

- **Rust backend**: Native machine code performance
- **Zero allocations** in hot evaluation path
- **Inline functions**: Critical comparison functions marked `#[inline(always)]`
- **Optimized data structures**: `Box<[String]>` for path tokens, `#[repr(u8)]` for operators
- **Pre-sorted rules**: Rules sorted by priority at load time
- **Direct conversion**: Python dict → Rust without intermediate JSON serialization
- **Link Time Optimization (LTO)**: Enabled in release profile

### Performance Characteristics

- **Rule evaluation**: O(n) where n = number of rules in requested categories
- **Field lookup**: O(d) where d = depth of nested field path
- **Memory**: Minimal allocations during evaluation (only for results)

## Development

```bash
# Run tests
cargo test

# Run Rust examples
cargo run --example demo

# Build documentation
cargo doc --no-deps --open

# Run Python tests
cd python/tests
python test_features.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Architecture

```
fast-decision/
├── src/              # Rust core engine
│   ├── lib.rs        # Python bindings (PyO3)
│   ├── engine.rs     # Rule evaluation engine
│   └── types.rs      # Data structures
├── benches/          # Performance benchmarks
├── examples/         # Rust examples
├── python/           # Python bindings and examples
│   ├── examples/     # Usage examples
│   └── tests/        # Tests
├── Cargo.toml        # Rust configuration
└── pyproject.toml    # Python packaging
```

## License

Licensed under either of:

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall be
dual licensed as above, without any additional terms or conditions.
