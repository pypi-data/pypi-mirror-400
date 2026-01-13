//! Data structures and type definitions.
//!
//! This module contains all data structures used by the rule engine:
//! - [`RuleSet`]: Top-level container for all categories
//! - [`Category`]: Collection of rules with evaluation settings
//! - [`Rule`]: Individual rule with conditions and action
//! - [`Predicate`]: AST for condition evaluation (Comparison, AND, OR)
//! - [`Comparison`]: Single field comparison operation
//! - [`Operator`]: Comparison operators
//!
//! All types implement custom deserialization for optimal memory layout.

use serde::{Deserialize, Deserializer, Serialize};
use serde_json::Value;
use std::collections::HashMap;

/// Converts a dot-separated path string into a boxed slice of tokens.
///
/// # Performance
///
/// Uses `Box<[String]>` instead of `Vec<String>` to save 8 bytes per comparison
/// (eliminates capacity field).
///
/// # Examples
///
/// ```ignore
/// let tokens = tokenize_path("user.profile.age");
/// assert_eq!(tokens.len(), 3);
/// ```
fn tokenize_path(path: &str) -> Box<[String]> {
    path.split('.')
        .map(|s| s.to_owned())
        .collect::<Vec<_>>()
        .into_boxed_slice()
}

/// Comparison operators.
///
/// # Memory Layout
///
/// Uses `#[repr(u8)]` for minimal memory footprint (1 byte per operator).
///
/// # Supported Operators
///
/// ## Comparison Operators
/// - `$equals`: Equal
/// - `$not-equals`: Not equal
/// - `$greater-than`: Greater than
/// - `$less-than`: Less than
/// - `$greater-than-or-equals`: Greater than or equal
/// - `$less-than-or-equals`: Less than or equal
///
/// ## Membership Operators
/// - `$in`: Value is in array
/// - `$not-in`: Value is not in array
///
/// ## String Operators
/// - `$contains`: Case-sensitive substring check
/// - `$starts-with`: String starts with value
/// - `$ends-with`: String ends with value
/// - `$regex`: Regular expression matching
#[derive(Debug, Deserialize, Serialize, Clone, Copy)]
#[repr(u8)]
pub enum Operator {
    // Comparison operators
    #[serde(rename = "$equals")]
    Equal,
    #[serde(rename = "$not-equals")]
    NotEqual,
    #[serde(rename = "$greater-than")]
    GreaterThan,
    #[serde(rename = "$less-than")]
    LessThan,
    #[serde(rename = "$greater-than-or-equals")]
    GreaterThanOrEqual,
    #[serde(rename = "$less-than-or-equals")]
    LessThanOrEqual,

    // Membership operators
    #[serde(rename = "$in")]
    In,
    #[serde(rename = "$not-in")]
    NotIn,

    // String operators
    #[serde(rename = "$contains")]
    Contains,
    #[serde(rename = "$starts-with")]
    StartsWith,
    #[serde(rename = "$ends-with")]
    EndsWith,
    #[serde(rename = "$regex")]
    Regex,
}

/// A single field comparison operation.
///
/// # Fields
///
/// - `path_tokens`: Tokenized field path (e.g., `["user", "tier"]` for `"user.tier"`)
/// - `op`: Comparison operator
/// - `value`: Expected value to compare against
///
/// # Memory Optimization
///
/// Uses `Box<[String]>` for path tokens to minimize memory overhead.
#[derive(Debug, Clone, Serialize)]
pub struct Comparison {
    #[serde(rename = "path")]
    pub path_tokens: Box<[String]>,
    pub op: Operator,
    pub value: Value,
}

/// Abstract Syntax Tree (AST) node for condition evaluation.
///
/// Predicates can be nested to form complex logical expressions.
///
/// # Variants
///
/// - `Comparison`: Leaf node (single field comparison)
/// - `And`: All child predicates must be true
/// - `Or`: At least one child predicate must be true
///
/// # Examples
///
/// Simple comparison:
/// ```json
/// {"user.tier": {"$eq": "Gold"}}
/// ```
///
/// Complex AND:
/// ```json
/// {"user.tier": {"$eq": "Gold"}, "amount": {"$gt": 100}}
/// ```
///
/// Explicit OR:
/// ```json
/// {"$or": [{"tier": {"$eq": "Gold"}}, {"tier": {"$eq": "Platinum"}}]}
/// ```
#[derive(Debug, Clone, Serialize)]
#[serde(untagged)]
pub enum Predicate {
    Comparison(Comparison),
    #[serde(rename = "$and")]
    And(Vec<Predicate>),
    #[serde(rename = "$or")]
    Or(Vec<Predicate>),
}

/// A category containing multiple rules with evaluation settings.
///
/// # Fields
///
/// - `stop_on_first`: If `true`, evaluation stops after the first matching rule
/// - `rules`: List of rules (automatically sorted by priority during deserialization)
///
/// # Priority Sorting
///
/// Rules are sorted by priority (lower value = higher precedence) when deserialized.
#[derive(Debug, Clone)]
pub struct Category {
    pub stop_on_first: bool,
    pub rules: Vec<Rule>,
}

/// An individual rule with conditions and action.
///
/// # Fields
///
/// - `id`: Unique identifier for the rule
/// - `priority`: Evaluation priority (lower = higher precedence, default: 0)
/// - `predicate`: Condition tree (deserialized from `conditions` field)
/// - `action`: Action identifier (informational, not evaluated by engine)
/// - `metadata`: Optional metadata for tracing, compliance, or custom annotations
///
/// # JSON Format
///
/// ```json
/// {
///   "id": "Premium_User",
///   "priority": 1,
///   "conditions": {"user.tier": {"$equals": "Gold"}},
///   "action": "apply_discount",
///   "metadata": {
///     "source": "Pricing Rules v2.3",
///     "tags": ["premium", "discount"]
///   }
/// }
/// ```
///
/// The `metadata` field is optional and will be included in evaluation results if present.
#[derive(Debug, Clone, Serialize)]
pub struct Rule {
    pub id: String,
    pub priority: i32,
    #[serde(rename = "conditions")]
    pub predicate: Predicate,
    pub action: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<serde_json::Map<String, Value>>,
}

impl Predicate {
    /// Recursively deserializes a serde_json::Value into a Predicate AST.
    fn deserialize_from_value(value: Value) -> Result<Self, String> {
        let map = value
            .as_object()
            .ok_or_else(|| format!("Predicate must be a JSON object{}", ""))?;

        let mut predicates = Vec::new();

        for (key, val) in map {
            match key.as_str() {
                // Handle explicit AND/OR operators
                "$and" | "$or" => {
                    let arr = val
                        .as_array()
                        .ok_or_else(|| format!("'{}' must be an array of objects", key))?;

                    if map.len() > 1 {
                        return Err(format!(
                            "If '{}' is present, it must be the only top-level key in the predicate",
                            key
                        ));
                    }

                    let children: Result<Vec<Predicate>, _> = arr
                        .iter()
                        .cloned()
                        .map(Predicate::deserialize_from_value) // Recursive call
                        .collect();

                    let children = children?;

                    return match key.as_str() {
                        "$and" => Ok(Predicate::And(children)),
                        "$or" => Ok(Predicate::Or(children)),
                        _ => unreachable!(),
                    };
                }
                // Handle field path (leaf node)
                field_path => {
                    // This must be an object of operators: {"path": {"$op": value}}
                    let operators_map = val.as_object().ok_or_else(|| {
                        format!(
                            "Value for field path '{}' must be an object of operators",
                            field_path
                        )
                    })?;

                    // Flat structure of conditions (implicit AND)
                    for (op_str, comp_value) in operators_map {
                        let op = match op_str.as_str() {
                            "$equals" => Operator::Equal,
                            "$not-equals" => Operator::NotEqual,
                            "$greater-than" => Operator::GreaterThan,
                            "$less-than" => Operator::LessThan,
                            "$greater-than-or-equals" => Operator::GreaterThanOrEqual,
                            "$less-than-or-equals" => Operator::LessThanOrEqual,
                            "$in" => Operator::In,
                            "$not-in" => Operator::NotIn,
                            "$contains" => Operator::Contains,
                            "$starts-with" => Operator::StartsWith,
                            "$ends-with" => Operator::EndsWith,
                            "$regex" => Operator::Regex,
                            _ => return Err(format!("Unknown operator: {}", op_str)),
                        };

                        predicates.push(Predicate::Comparison(Comparison {
                            path_tokens: tokenize_path(field_path),
                            op,
                            value: comp_value.clone(),
                        }));
                    }
                }
            }
        }

        // If we reached this point, we processed a flat structure (implicit AND).
        match predicates.len() {
            0 => Err(format!(
                "Rule condition must contain at least one comparison{}",
                ""
            )),
            1 => Ok(predicates.pop().unwrap()), // Single condition
            _ => Ok(Predicate::And(predicates)), // Implicit AND
        }
    }
}

impl Category {
    /// Checks for rules with duplicate priorities and logs warnings.
    ///
    /// Duplicate priorities may result in non-deterministic evaluation order
    /// for rules with the same priority value.
    ///
    /// # Arguments
    ///
    /// * `category_name` - Name of the category (for logging)
    pub fn warn_duplicate_priorities(&self, category_name: &str) {
        use std::collections::HashMap;
        let mut priority_count: HashMap<i32, Vec<&str>> = HashMap::new();

        for rule in &self.rules {
            priority_count
                .entry(rule.priority)
                .or_default()
                .push(&rule.id);
        }

        for (priority, ids) in priority_count {
            if ids.len() > 1 {
                log::warn!(
                    "Category '{}': Multiple rules with priority {}: {:?}",
                    category_name,
                    priority,
                    ids
                );
            }
        }
    }
}

impl<'de> Deserialize<'de> for Category {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(untagged)]
        enum CategoryHelper {
            WithConfig {
                stop_on_first: bool,
                rules: Vec<Rule>,
            },
            Simple(Vec<Rule>),
        }

        match CategoryHelper::deserialize(deserializer)? {
            CategoryHelper::WithConfig {
                stop_on_first,
                mut rules,
            } => {
                rules.sort_by_key(|r| r.priority);
                Ok(Category {
                    stop_on_first,
                    rules,
                })
            }
            CategoryHelper::Simple(mut rules) => {
                rules.sort_by_key(|r| r.priority);
                Ok(Category {
                    stop_on_first: false,
                    rules,
                })
            }
        }
    }
}

impl<'de> Deserialize<'de> for Rule {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        struct RuleHelper {
            id: String,
            #[serde(default)]
            priority: i32,
            conditions: Value,
            action: String,
            #[serde(default)]
            metadata: Option<serde_json::Map<String, Value>>,
        }

        let helper = RuleHelper::deserialize(deserializer)?;

        let predicate = Predicate::deserialize_from_value(helper.conditions)
            .map_err(serde::de::Error::custom)?;

        Ok(Rule {
            id: helper.id,
            priority: helper.priority,
            predicate,
            action: helper.action,
            metadata: helper.metadata,
        })
    }
}

/// Top-level container for all rule categories.
///
/// # JSON Format
///
/// ```json
/// {
///   "categories": {
///     "Pricing": {
///       "stop_on_first": true,
///       "rules": [...]
///     },
///     "Fraud": {
///       "stop_on_first": false,
///       "rules": [...]
///     }
///   }
/// }
/// ```
///
/// # Performance
///
/// Uses `HashMap` for O(1) category lookup by name.
#[derive(Debug, Deserialize, Clone)]
pub struct RuleSet {
    pub categories: HashMap<String, Category>,
}
