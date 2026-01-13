use crate::policy_types::{
    PropertyMatcher, PropertyScalarMatcher, SourceTag, ToolCondition, ToolPolicy, ValueOrReference,
    ValueReference,
};
use regex::Regex;
use serde_json::Value;
use std::io::Read;
use std::path::Path;

#[derive(thiserror::Error, Debug)]
pub enum PolicyLoadError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    #[error("json parse error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("duplicate tool name: {0}")]
    DuplicateToolName(String),
}

pub fn load_one_from_reader<R: Read>(mut reader: R) -> Result<ToolPolicy, PolicyLoadError> {
    let mut buf = String::new();
    reader.read_to_string(&mut buf)?;
    let policy: ToolPolicy = serde_json::from_str(&buf)?;
    let mut policies: Vec<ToolPolicy> = vec![policy];
    convert_template_scalars_to_references(&mut policies);
    Ok(policies[0].clone())
}

/// Load policies from any std::io::Read source containing a JSON array of ToolPolicy objects.
pub fn load_many_from_reader<R: Read>(mut reader: R) -> Result<Vec<ToolPolicy>, PolicyLoadError> {
    let mut buf = String::new();
    reader.read_to_string(&mut buf)?;
    let mut policies: Vec<ToolPolicy> = serde_json::from_str(&buf)?;
    // Post-process to convert template strings ("{{state#foo}}" / "{{args#bar}}") into references.
    convert_template_scalars_to_references(&mut policies);
    Ok(policies)
}

/// Load policies from a JSON file at the given path.
pub fn load_from_file(path: impl AsRef<Path>) -> Result<Vec<ToolPolicy>, PolicyLoadError> {
    let file = std::fs::File::open(path)?;
    load_many_from_reader(file)
}

/// Serialize policies into a compact JSON string (canonical form without whitespace).
pub fn serialize_json(policies: &[ToolPolicy]) -> Result<String, serde_json::Error> {
    serde_json::to_string(policies)
}

fn convert_template_scalars_to_references(policies: &mut [ToolPolicy]) {
    for policy in policies.iter_mut() {
        match &mut policy.rule {
            crate::policy_types::ToolPolicyRule::Allow { when, .. } => process_tool_condition(when),
            crate::policy_types::ToolPolicyRule::Deny { when, .. } => process_tool_condition(when),
            crate::policy_types::ToolPolicyRule::Modify { when, .. } => {
                process_tool_condition(when)
            }
        }
    }
}

fn process_tool_condition(cond: &mut ToolCondition) {
    match cond {
        ToolCondition::Atomic(a) => match a.source {
            SourceTag::Args | SourceTag::State => process_property_matcher(&mut a.matches),
        },
        ToolCondition::Boolean(bool_tc) => {
            for c in bool_tc.conditions.iter_mut() {
                process_tool_condition(c);
            }
        }
        ToolCondition::Not { not } => {
            process_tool_condition(not);
        }
    }
}

fn process_property_matcher(pm: &mut PropertyMatcher) {
    match pm {
        PropertyMatcher::Scalar(s) => process_scalar_matcher(s),
        PropertyMatcher::List(_l) => {
            // list values are literal; nothing to convert
        }
    }
}

fn process_scalar_matcher(sc: &mut PropertyScalarMatcher) {
    // Pattern: {{ optional_space (args|state) # path (alphanum/_/.) optional_space }}
    // Capture 1: source, Capture 2: path
    let path_reference_regex = Regex::new(r"^\{\{\s*(args|state)#([A-Za-z0-9_.]+)\s*}}$").unwrap();
    if let ValueOrReference::Value(val) = &sc.value
        && let Value::String(s) = val
        && let Some(caps) = path_reference_regex.captures(s)
    {
        let source = match &caps[1] {
            "args" => SourceTag::Args,
            "state" => SourceTag::State,
            _ => unreachable!("unexpected source tag"),
        };
        let path = caps[2].to_string();
        sc.value = ValueOrReference::Reference(ValueReference { source, path });
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::policy_engine::{PolicyEngine, ProcessToolCallResult};
    use crate::policy_types::{
        AtomicToolCondition, ToolPolicyRecord, ToolPolicyRule, ValueScalarOperator,
    };
    use serde_json::json;

    fn wrap(records: Vec<ToolPolicy>) -> Vec<ToolPolicyRecord> {
        records
            .into_iter()
            .enumerate()
            .map(|(i, p)| ToolPolicyRecord {
                id: format!("rec-{}", i),
                name: format!("policy-{}", p.tool_name),
                current_version_id: "v1".into(),
                policy: p,
            })
            .collect()
    }

    #[test]
    fn load_one_correct_structs() {
        let json = r#"
          {
            "tool_name": "grant_loan",
            "rule":
              {
                "action": "allow",
                "when": {
                  "source": "state",
                  "matches": {
                    "key": "user.isAdmin",
                    "op": "eq",
                    "value": true
                  }
                }
              }
          }
        "#;

        let expected = ToolPolicy {
            tool_name: "grant_loan".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Atomic(
                    (AtomicToolCondition {
                        source: SourceTag::State,
                        matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                            key: "user.isAdmin".into(),
                            op: ValueScalarOperator::Eq,
                            value: ValueOrReference::Value(Value::Bool(true)),
                        }),
                    }),
                ),
            },
        };

        let actual_result = load_one_from_reader(json.as_bytes()).expect("should parse");
        assert_eq!(actual_result, expected);
    }

    #[test]
    fn load_negated_condition() {
        let json = r#"[
          {
            "tool_name": "login_user",
            "rule":
              {
                "action": "allow",
                "when": {
                    "not": {
                      "source": "state",
                      "matches": {
                        "key": "user.isBanned",
                        "op": "eq",
                        "value": true
                      }
                }
                }
              }
          }
        ]"#;

        let expected = vec![ToolPolicy {
            tool_name: "login_user".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Not {
                    not: Box::new(ToolCondition::Atomic(
                        (AtomicToolCondition {
                            source: SourceTag::State,
                            matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                                key: "user.isBanned".into(),
                                op: ValueScalarOperator::Eq,
                                value: ValueOrReference::Value(Value::Bool(true)),
                            }),
                        }),
                    )),
                },
            },
        }];

        let actual_result = load_many_from_reader(json.as_bytes()).expect("should parse");
        assert_eq!(actual_result, expected);
    }

    #[test]
    fn load_many_correct_structs() {
        let json = r#"[
          {
            "tool_name": "grant_loan",
            "rule":
              {
                "action": "allow",
                "when": {
                  "source": "state",
                  "matches": {
                    "key": "user.isAdmin",
                    "op": "eq",
                    "value": true
                  }
                }
              }
          }
        ]"#;

        let expected = vec![ToolPolicy {
            tool_name: "grant_loan".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Atomic(
                    (AtomicToolCondition {
                        source: SourceTag::State,
                        matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                            key: "user.isAdmin".into(),
                            op: ValueScalarOperator::Eq,
                            value: ValueOrReference::Value(Value::Bool(true)),
                        }),
                    }),
                ),
            },
        }];

        let actual_result = load_many_from_reader(json.as_bytes()).expect("should parse");
        assert_eq!(actual_result, expected);
    }

    #[test]
    fn load_one_correct_structs_with_field_references() {
        let json = r#"
          {
            "tool_name": "view_account",
            "rule":
              {
                "action": "allow",
                "when": {
                  "source": "args",
                  "matches": {
                    "key": "userId",
                    "op": "eq",
                    "value": "{{state#user.id}}"
                  }
                }
              }
          }
        "#;

        let expected = ToolPolicy {
            tool_name: "view_account".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Atomic(AtomicToolCondition {
                    source: SourceTag::Args,
                    matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                        key: "userId".into(),
                        op: ValueScalarOperator::Eq,
                        value: ValueOrReference::Reference(ValueReference {
                            source: SourceTag::State,
                            path: "user.id".into(),
                        }),
                    }),
                }),
            },
        };

        let actual_result = load_one_from_reader(json.as_bytes()).expect("should parse");
        assert_eq!(actual_result, expected);
    }

    #[test]
    fn load_many_correct_structs_with_field_references() {
        let json = r#"[
          {
            "tool_name": "view_account",
            "rule":
              {
                "action": "allow",
                "when": {
                  "source": "args",
                  "matches": {
                    "key": "userId",
                    "op": "eq",
                    "value": "{{state#user.id}}"
                  }
                }
              }
          }
        ]"#;

        let expected = vec![ToolPolicy {
            tool_name: "view_account".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Atomic(AtomicToolCondition {
                    source: SourceTag::Args,
                    matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                        key: "userId".into(),
                        op: ValueScalarOperator::Eq,
                        value: ValueOrReference::Reference(ValueReference {
                            source: SourceTag::State,
                            path: "user.id".into(),
                        }),
                    }),
                }),
            },
        }];

        let actual_result = load_many_from_reader(json.as_bytes()).expect("should parse");
        assert_eq!(actual_result, expected);
    }

    #[test]
    fn load_policies_from_json_string() {
        let json = r#"[
          {
            "tool_name": "grant_loan",
            "rule": {
                "action": "deny", "when": {"op": "any_of", "conditions": [
                {"source": "args", "matches": {"key": "loanAmount", "op": "gt", "value": 10000}},
                {"op": "all_of", "conditions": [
                  {"source": "state", "matches": {"key": "user.creditScore", "op": "lt", "value": 600}},
                  {"source": "args", "matches": {"key": "loanAmount", "op": "gt", "value": 500}}
                ]}
              ]}}
          },
          {
            "tool_name": "grant_loan",
            "rule": {
                "action": "allow", "when": {"source": "state", "matches": {"key": "user.isAdmin", "op": "eq", "value": true}}}
          }
        ]"#;
        let policies = load_many_from_reader(json.as_bytes()).expect("should parse");
        assert_eq!(policies.len(), 2);
        let engine = PolicyEngine::new(wrap(policies), None);
        let action = engine
            .process_tool_call(
                "grant_loan",
                "tool-call-1",
                &json!({"loanAmount": 20000}),
                &json!({"user": {"isAdmin": false, "creditScore": 650}}),
            )
            .unwrap();
        match action {
            ProcessToolCallResult::Deny { .. } => {}
            _ => panic!("expected deny"),
        }
    }

    #[test]
    fn serialize_round_trip_matches_canonical_input() {
        let raw = r#"[
          {
            "tool_name": "grant_loan",
            "rule": {
                "action": "deny", "when": {"op": "any_of", "conditions": [
                {"source": "args", "matches": {"key": "loanAmount", "op": "gt", "value": 10000}},
                {"op": "all_of", "conditions": [
                  {"source": "state", "matches": {"key": "user.creditScore", "op": "lt", "value": 600}},
                  {"source": "args", "matches": {"key": "loanAmount", "op": "gt", "value": 500}}
                ]}
              ]}}
          },
          {
            "tool_name": "grant_loan",
            "rule": {
                "action": "allow", "when": {"source": "state", "matches": {"key": "user.isAdmin", "op": "eq", "value": true}}}
          }
        ]"#;
        let original: Vec<ToolPolicy> = load_many_from_reader(raw.as_bytes()).expect("load failed");
        let serialized = serialize_json(&original).expect("serialize ok");
        let reparsed: Vec<ToolPolicy> = serde_json::from_str(&serialized).expect("reparse failed");
        assert_eq!(original, reparsed, "Structural round-trip mismatch");
    }

    #[test]
    fn load_policy_using_in_operator() {
        let json = r#"
          {
            "tool_name": "greet",
            "rule":
              {
                "action": "allow",
                "when": {
                  "source": "state",
                  "matches": {
                    "key": "name",
                    "op": "in",
                    "value": ["Jonathan"]
                  }
                }
              }
          }
        "#;

        let expected = ToolPolicy {
            tool_name: "greet".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Atomic(
                    (AtomicToolCondition {
                        source: SourceTag::State,
                        matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                            key: "name".into(),
                            op: ValueScalarOperator::In,
                            value: ValueOrReference::Value(Value::Array(vec![Value::String(
                                "Jonathan".into(),
                            )])),
                        }),
                    }),
                ),
            },
        };

        let actual_result = load_one_from_reader(json.as_bytes()).expect("should parse");
        assert_eq!(actual_result, expected);
    }
}
