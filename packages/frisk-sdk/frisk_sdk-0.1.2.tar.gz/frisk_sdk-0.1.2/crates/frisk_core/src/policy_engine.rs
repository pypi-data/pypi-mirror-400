use crate::errors::PolicyEngineError;
use crate::otel::otel_manager::OtelManager;
use crate::policy_types::*;
use crate::try_utils::{try_all, try_any};
use opentelemetry::KeyValue;
use opentelemetry::logs::{LogRecord, Logger, LoggerProvider}; // bring trait into scope for logger()
use opentelemetry::metrics::MeterProvider; // bring trait into scope for meter()
use regex::Regex;
use serde::Serialize;
use serde_json::Value;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Instant, SystemTime};
use tracing::{Level, Span, span};
use tracing_opentelemetry::OpenTelemetrySpanExt;

use crate::match_utils::get_value_from_scalar_property_matcher::get_value_from_scalar_property_matcher;
use crate::match_utils::list_condition_matches::list_property_matcher_matches;
use crate::match_utils::scalar_condition_matches::property_scalar_matcher_matches;
use crate::regex_matcher::RegexMatcher;
use crate::value_utils::get_value_at_path::get_value_at_path;

// === Actions ===
#[derive(Debug, Clone, Serialize, PartialEq)]
#[serde(tag = "decision", rename_all = "snake_case")]
pub enum ProcessToolCallResult {
    Allow {
        rules_matched: Vec<ToolPolicyRule>,
    },
    Deny {
        rules_matched: Vec<ToolPolicyRule>,
        reason: String,
    },
}

pub fn get_decision_name(action: &ProcessToolCallResult) -> &'static str {
    match action {
        ProcessToolCallResult::Allow { .. } => "allow",
        ProcessToolCallResult::Deny { .. } => "deny",
    }
}

// todo: Errors should result in most restrictive outcome. https://linear.app/friskai/issue/POL-56/errors-in-rule-evaluation-should-result-in-most-restrictive-outcome
#[derive(Debug, Clone)]
pub struct PolicyEngine {
    pub policies: Vec<ToolPolicyRecord>,
    otel_manager: Option<Arc<OtelManager>>,
    regex_cache: Arc<Mutex<HashMap<String, Regex>>>,
}

impl Default for PolicyEngine {
    fn default() -> Self {
        Self {
            policies: Vec::new(),
            otel_manager: None,
            regex_cache: Arc::new(Mutex::new(HashMap::new())),
        }
    }
}

pub struct PolicyMatchContext<'a> {
    pub tool_name: &'a str,
    pub tool_args: &'a Value,
    pub agent_state: &'a Value,
    regex_matcher: RegexMatcher,
}

impl PolicyEngine {
    pub fn new(policies: Vec<ToolPolicyRecord>, otel_manager: Option<Arc<OtelManager>>) -> Self {
        Self {
            policies,
            otel_manager,
            regex_cache: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn set_policies(&mut self, policies: Vec<ToolPolicyRecord>) {
        self.policies = policies;
    }

    pub fn process_tool_call(
        &self,
        tool_name: &str,
        tool_call_id: &str,
        tool_args: &Value,
        agent_state: &Value,
    ) -> Result<ProcessToolCallResult, PolicyEngineError> {
        let start = Instant::now();
        let top_level_span = Span::current();
        let evaluating_action_span = Self::start_evaluating_action_span(
            &top_level_span,
            tool_call_id,
            tool_name,
            tool_args,
            agent_state,
        );
        evaluating_action_span.enter();

        let mut matched_denies: Vec<ToolPolicyRule> = Vec::new();
        let mut matched_allows: Vec<ToolPolicyRule> = Vec::new();
        let mut policies_evaluated: bool = false;
        let mut allow_rules_evaluated: bool = false;
        let mut early_deny_decision: Option<ProcessToolCallResult> = None;

        let policy_match_context = PolicyMatchContext::new(
            tool_name,
            tool_args,
            agent_state,
            RegexMatcher::new(self.regex_cache.clone()),
        );

        for record in &self.policies {
            let policy = &record.policy;
            if policy.tool_name != tool_name {
                continue;
            }

            let policy_span =
                Self::create_policy_span(&evaluating_action_span, tool_call_id, record);
            let _guard_policy = policy_span.enter();
            policies_evaluated = true;

            let rule = &policy.rule;
            match rule {
                ToolPolicyRule::Allow { when } => {
                    let does_condition_match = policy_match_context.condition_matches(when)?;
                    policy_span.set_attribute("matched", does_condition_match);
                    allow_rules_evaluated = true;

                    if does_condition_match {
                        matched_allows.push(rule.clone());
                        policy_span.set_attribute("effect", "allow");
                    } else {
                        policy_span.set_attribute("effect", "deny");
                        early_deny_decision = Some(ProcessToolCallResult::Deny {
                            rules_matched: Vec::new(),
                            reason: "No allow rule matched".into(),
                        });
                        break;
                    }
                }
                ToolPolicyRule::Deny { when } => {
                    let does_condition_match = policy_match_context.condition_matches(when)?;
                    policy_span.set_attribute("matched", does_condition_match);

                    if does_condition_match {
                        matched_denies.push(rule.clone());
                        policy_span.set_attribute("effect", "deny");
                        early_deny_decision = Some(ProcessToolCallResult::Deny {
                            rules_matched: matched_denies.clone(),
                            reason: "Denied by policy".into(),
                        });
                        break;
                    } else {
                        policy_span.set_attribute("effect", "allow");
                    }
                }
                ToolPolicyRule::Modify { when, .. } => {
                    let does_condition_match = policy_match_context.condition_matches(when)?;

                    // For now, treat modify as allow for decision purposes
                    if does_condition_match {
                        matched_allows.push(rule.clone());
                        policy_span.set_attribute("matched", true);
                        policy_span.set_attribute("effect", "modify");
                    } else {
                        policy_span.set_attribute("matched", false);
                    }
                }
            }
        }

        let decision = if let Some(d) = early_deny_decision {
            d
        } else if !policies_evaluated {
            ProcessToolCallResult::Allow {
                rules_matched: Vec::new(),
            }
        } else if !matched_denies.is_empty() {
            ProcessToolCallResult::Deny {
                rules_matched: matched_denies,
                reason: "Denied by policy".into(),
            }
        } else if !allow_rules_evaluated || !matched_allows.is_empty() {
            ProcessToolCallResult::Allow {
                rules_matched: matched_allows,
            }
        } else {
            ProcessToolCallResult::Deny {
                rules_matched: Vec::new(),
                reason: "No allow rule matched".into(),
            }
        };

        let matched_len = match &decision {
            ProcessToolCallResult::Allow { rules_matched } => rules_matched.len(),
            ProcessToolCallResult::Deny { rules_matched, .. } => rules_matched.len(),
        };

        evaluating_action_span.set_attribute("decision", get_decision_name(&decision).to_string());
        evaluating_action_span.set_attribute("matched_count", matched_len.to_string());

        let elapsed = start.elapsed().as_secs_f64() * 1000.0;
        self.emit_telemetry(tool_name, &decision, elapsed);
        Ok(decision)
    }

    fn start_evaluating_action_span(
        parent: &Span,
        tool_call_id: &str,
        tool_name: &str,
        tool_args: &Value,
        agent_state: &Value,
    ) -> Span {
        let evaluating_action_span = span!(parent: parent, Level::INFO, "evaluating_action");
        evaluating_action_span.set_attribute("tool_name", tool_name.to_string());
        evaluating_action_span.set_attribute("tool_call_id", tool_call_id.to_string());
        evaluating_action_span.set_attribute("tool_args", tool_args.to_string());
        evaluating_action_span.set_attribute("agent_state", agent_state.to_string());
        evaluating_action_span
    }

    fn create_rule_span(parent: &Span, id: &String) -> Span {
        let rule_span = span!(parent: parent, Level::INFO, "evaluating_rule");
        rule_span.set_attribute("rule_id", id.clone());
        rule_span
    }

    fn create_policy_span(
        parent: &Span,
        tool_call_id: &str,
        record: &ToolPolicyRecord,
    ) -> span::Span {
        let policy_span = span!(parent: parent, Level::INFO, "evaluating_policy");
        policy_span.set_attribute("policy_id", record.id.clone());
        policy_span.set_attribute("policy_version_id", record.current_version_id.clone());
        policy_span.set_attribute("tool_call_id", tool_call_id.to_string());
        policy_span
    }

    fn emit_telemetry(&self, tool_name: &str, action: &ProcessToolCallResult, elapsed: f64) {
        if let Some(otel) = &self.otel_manager {
            // Record a simple metric if available
            let meter = otel.meter_provider().meter("policy-engine");
            let hist = meter
                .f64_histogram("policy_engine.decision_latency_ms")
                .with_description("Latency of policy decisions in milliseconds")
                .with_unit("ms")
                .build();
            hist.record(
                elapsed,
                &[
                    KeyValue::new("tool_name", tool_name.to_string()),
                    KeyValue::new("decision", get_decision_name(action).to_string()),
                ],
            );

            // Emit a log record
            let logger = otel.logger_provider().logger("policy_engine");
            let mut record = logger.create_log_record();
            record.set_severity_text("INFO");
            record.set_event_name("process_tool_call_result");
            record.set_target("policy_engine::decision");
            record.set_timestamp(SystemTime::now());
            let matched = match action {
                ProcessToolCallResult::Allow { rules_matched } => rules_matched.len(),
                ProcessToolCallResult::Deny { rules_matched, .. } => rules_matched.len(),
            };
            let reason = match action {
                ProcessToolCallResult::Deny { reason, .. } => Some(reason.clone()),
                _ => None,
            };
            record.set_body(
                serde_json::json!({
                    "decision": get_decision_name(action),
                    "matched_rules": matched,
                    "reason": reason
                })
                .to_string()
                .into(),
            );
            logger.emit(record);
        }
    }
}

impl<'a> PolicyMatchContext<'a> {
    pub fn new(
        tool_name: &'a str,
        tool_args: &'a Value,
        agent_state: &'a Value,
        regex_matcher: RegexMatcher,
    ) -> Self {
        Self {
            tool_name,
            tool_args,
            agent_state,
            regex_matcher,
        }
    }

    fn condition_matches(&self, condition: &ToolCondition) -> Result<bool, PolicyEngineError> {
        match condition {
            ToolCondition::Atomic(a) => self.atomic_condition_matches(a),

            ToolCondition::Not { not } => Ok(!self.condition_matches(not)?),

            ToolCondition::Boolean(b) => match b.op {
                BooleanOperator::AnyOf => {
                    try_any(b.conditions.iter(), |c| self.condition_matches(c))
                }
                BooleanOperator::AllOf => {
                    try_all(b.conditions.iter(), |c| self.condition_matches(c))
                }
            },
        }
    }

    fn atomic_condition_matches(
        &self,
        atomic: &AtomicToolCondition,
    ) -> Result<bool, PolicyEngineError> {
        match atomic.source {
            SourceTag::Args => self.property_matcher_matches(&atomic.matches, self.tool_args),
            SourceTag::State => self.property_matcher_matches(&atomic.matches, self.agent_state),
        }
    }

    fn property_matcher_matches(
        &self,
        matcher: &PropertyMatcher,
        source: &Value,
    ) -> Result<bool, PolicyEngineError> {
        match matcher {
            PropertyMatcher::Scalar(scalar_matcher) => {
                let value = get_value_at_path(source, &scalar_matcher.key)?;
                self.scalar_property_matcher_matches(scalar_matcher, value)
            }

            PropertyMatcher::List(list_matcher) => {
                let value = get_value_at_path(source, &list_matcher.key)?;
                list_property_matcher_matches(list_matcher, value)
            }
        }
    }

    fn scalar_property_matcher_matches(
        &self,
        matcher: &PropertyScalarMatcher,
        actual_value: &Value,
    ) -> Result<bool, PolicyEngineError> {
        // expected literal or reference-resolved value
        let expected_value: &Value =
            &get_value_from_scalar_property_matcher(matcher, self.tool_args, self.agent_state)?;

        property_scalar_matcher_matches(matcher, actual_value, expected_value, &self.regex_matcher)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::policy_loader::load_many_from_reader;
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

    fn engine(policies: Vec<ToolPolicyRecord>) -> PolicyEngine {
        PolicyEngine::new(policies, None)
    }

    #[test]
    fn deny_high_loan_amount() {
        let policies = wrap(vec![
            ToolPolicy {
                tool_name: "grant_loan".into(),
                rule: ToolPolicyRule::Deny {
                    when: ToolCondition::Atomic(
                        (AtomicToolCondition {
                            source: SourceTag::Args,
                            matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                                key: "loanAmount".into(),
                                op: ValueScalarOperator::Gt,
                                value: ValueOrReference::Value(Value::Number(
                                    serde_json::Number::from_f64(10000.0).unwrap(),
                                )),
                            }),
                        }),
                    ),
                },
            },
            ToolPolicy {
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
            },
        ]);
        let eng = engine(policies);

        // Get references to expected matched rules inside engine
        let deny_rule_ref = match &eng.policies[0].policy.rule {
            r @ ToolPolicyRule::Deny { .. } => r,
            _ => unreachable!(),
        };
        let allow_rule_ref = match &eng.policies[1].policy.rule {
            r @ ToolPolicyRule::Allow { .. } => r,
            _ => unreachable!(),
        };

        let action = eng
            .process_tool_call(
                "grant_loan",
                "test-call-1",
                &json!({"loanAmount": 20000}),
                &json!({"user": {"isAdmin": false}}),
            )
            .unwrap();
        match action {
            ProcessToolCallResult::Deny {
                rules_matched,
                reason,
            } => {
                assert_eq!(reason, "Denied by policy");
                assert_eq!(rules_matched.len(), 1);
                assert_eq!(rules_matched[0], *deny_rule_ref);
                assert_ne!(rules_matched[0], *allow_rule_ref);
            }
            _ => panic!("expected deny"),
        }
    }

    #[test]
    fn internal_variable_references() {
        let policies = wrap(vec![ToolPolicy {
            tool_name: "view_account_details".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Atomic(
                    (AtomicToolCondition {
                        source: SourceTag::Args,
                        matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                            key: "user_id".into(),
                            op: ValueScalarOperator::Eq,
                            value: ValueOrReference::Reference(ValueReference {
                                source: SourceTag::State,
                                path: "user.id".into(),
                            }),
                        }),
                    }),
                ),
            },
        }]);

        let policy_engine = PolicyEngine::new(policies, None);
        let allow_rule_ref = match &policy_engine.policies[0].policy.rule {
            r @ ToolPolicyRule::Allow { .. } => r,
            _ => unreachable!(),
        };

        let expected_allowed_action = policy_engine
            .process_tool_call(
                "view_account_details",
                "test-call-2",
                &json!({"user_id": 123}),
                &json!({"user": {"id": 123}}),
            )
            .unwrap();

        match expected_allowed_action {
            ProcessToolCallResult::Allow { rules_matched } => {
                assert_eq!(rules_matched.len(), 1);
                assert_eq!(rules_matched[0], *allow_rule_ref);
            }
            _ => panic!(
                "Operation should be allowed because tool_args.user_id === agent_state.user.id"
            ),
        }

        let expected_denied_action = policy_engine
            .process_tool_call(
                "view_account_details",
                "test-call-3",
                &json!({"user_id": 123}),
                &json!({"user": {"id": 456}}),
            )
            .unwrap();

        match expected_denied_action {
            ProcessToolCallResult::Deny {
                rules_matched,
                reason,
            } => {
                assert_eq!(reason, "No allow rule matched");
                assert_eq!(rules_matched.len(), 0);
            }
            _ => panic!(
                "Operation should not be allowed because tool_args.user_id !== agent_state.user.id"
            ),
        }
    }

    #[test]
    fn allow_admin_overrides() {
        let policies = wrap(vec![
            ToolPolicy {
                tool_name: "grant_loan".into(),
                rule: ToolPolicyRule::Deny {
                    when: ToolCondition::Atomic(AtomicToolCondition {
                        source: SourceTag::Args,
                        matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                            key: "loanAmount".into(),
                            op: ValueScalarOperator::Gt,
                            value: ValueOrReference::Value(Value::Number(
                                serde_json::Number::from_f64(10000.0).unwrap(),
                            )),
                        }),
                    }),
                },
            },
            ToolPolicy {
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
            },
        ]);
        let eng = engine(policies);
        let deny_rule_ref = match &eng.policies[0].policy.rule {
            r @ ToolPolicyRule::Deny { .. } => r,
            _ => unreachable!(),
        };
        let allow_rule_ref = match &eng.policies[1].policy.rule {
            r @ ToolPolicyRule::Allow { .. } => r,
            _ => unreachable!(),
        };
        let action = eng
            .process_tool_call(
                "grant_loan",
                "test-call-4",
                &json!({"loanAmount": 9000}),
                &json!({"user": {"isAdmin": true}}),
            )
            .unwrap();
        match action {
            ProcessToolCallResult::Allow { rules_matched } => {
                assert_eq!(rules_matched.len(), 1);
                assert_eq!(rules_matched[0], *allow_rule_ref);
                assert_ne!(rules_matched[0], *deny_rule_ref);
            }
            _ => panic!("expected allow"),
        }
    }

    #[test]
    fn allow_if_no_deny() {
        let policies = wrap(vec![ToolPolicy {
            tool_name: "grant_loan".into(),
            rule: ToolPolicyRule::Deny {
                when: ToolCondition::Atomic(
                    (AtomicToolCondition {
                        source: SourceTag::Args,
                        matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                            key: "loanAmount".into(),
                            op: ValueScalarOperator::Gt,
                            value: ValueOrReference::Value(Value::Number(
                                serde_json::Number::from_f64(10000.0).unwrap(),
                            )),
                        }),
                    }),
                ),
            },
        }]);
        let eng = engine(policies);
        let deny_rule_ref = match &eng.policies[0].policy.rule {
            r @ ToolPolicyRule::Deny { .. } => r,
            _ => unreachable!(),
        };
        let action = eng
            .process_tool_call(
                "grant_loan",
                "test-call-5",
                &json!({"loanAmount": 5000}),
                &json!({"user": {"isAdmin": false}}),
            )
            .unwrap();
        match action {
            ProcessToolCallResult::Allow { rules_matched } => {
                assert_eq!(rules_matched.len(), 0);
            }
            _ => panic!("expected deny"),
        }
    }

    #[test]
    fn allow_if_name_in_list() {
        let policies = wrap(vec![ToolPolicy {
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
        }]);

        let eng = engine(policies);

        let expected_allow_action = eng
            .process_tool_call(
                "greet",
                "test-call-6",
                &json!({}),
                &json!({"name": "Jonathan"}),
            )
            .unwrap();
        match expected_allow_action {
            ProcessToolCallResult::Allow { rules_matched } => {
                assert_eq!(rules_matched.len(), 1);
            }
            _ => panic!("expected allow"),
        }

        let expected_deny_action = eng
            .process_tool_call(
                "greet",
                "test-call-7",
                &json!({}),
                &json!({"name": "Not Jonathan"}),
            )
            .unwrap();
        match expected_deny_action {
            ProcessToolCallResult::Allow { rules_matched } => {
                panic!("Expected deny")
            }
            _ => {}
        }
    }

    #[test]
    fn list_contains_all() {
        use serde_json::json;
        let policies = wrap(vec![ToolPolicy {
            tool_name: "check_ops".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Atomic(
                    (AtomicToolCondition {
                        source: SourceTag::Args,
                        matches: PropertyMatcher::List(PropertyListMatcher {
                            key: "ops".into(),
                            op: ValueListOperator::ContainsAll,
                            values: vec![Value::String("eq".into()), Value::String("lt".into())],
                        }),
                    }),
                ),
            },
        }]);
        let eng = PolicyEngine::new(policies, None);
        let allow_rule_ref = match &eng.policies[0].policy.rule {
            r @ ToolPolicyRule::Allow { .. } => r,
            _ => unreachable!(),
        };
        let action = eng
            .process_tool_call(
                "check_ops",
                "test-call-8",
                &json!({"ops": ["eq", "lt", "gt"]}),
                &json!({}),
            )
            .unwrap();
        match action {
            ProcessToolCallResult::Allow { rules_matched } => {
                assert_eq!(rules_matched.len(), 1);
                assert_eq!(rules_matched[0], *allow_rule_ref);
            }
            _ => panic!("expected allow"),
        }
    }

    #[test]
    fn weather_in_narnia() {
        let policies = wrap(
            load_many_from_reader(
                r#"[
              {
                "tool_name": "get_weather_in_narnia",
                "rule": {
                  "id": "deny_if_allow_false",
                  "action": "deny",
                  "when": {
                    "op": "any_of",
                    "conditions": [
                      {
                        "source": "state",
                        "matches": {
                          "key": "allow",
                          "op": "eq",
                          "value": false
                        }
                      }
                    ]
                  }
                }
              }
            ]
            "#
                .as_bytes(),
            )
            .unwrap(),
        );

        let eng = engine(policies);
        let action = eng
            .process_tool_call(
                "get_weather_in_narnia",
                "test-call-9",
                &json!({}),
                &json!({"allow": false}),
            )
            .unwrap();

        match action {
            ProcessToolCallResult::Deny {
                rules_matched,
                reason,
            } => {
                assert_eq!(reason, "Denied by policy");
                assert_eq!(rules_matched.len(), 1);
            }
            _ => panic!("expected deny"),
        }
    }

    #[test]
    fn handle_missing_values() {
        let policies = wrap(
            load_many_from_reader(
                r#"[
              {
                "tool_name": "grant_loan",
                "rule": {
                  "id": "approve_if_not_jonathan",
                  "action": "deny",
                  "when": {
                    "op": "any_of",
                    "conditions": [
                      {
                        "source": "state",
                        "matches": {
                          "key": "user.name",
                          "op": "eq",
                          "value": "Jonathan"
                        }
                      }
                    ]
                  }
                }
              }
            ]
            "#
                .as_bytes(),
            )
            .unwrap(),
        );

        let eng = engine(policies);
        let action = eng
            .process_tool_call(
                "grant_loan",
                "test-call-10",
                &json!({}),
                &json!({}), // state is empty, no name field.
            )
            .unwrap();

        if let ProcessToolCallResult::Deny { .. } = action {
            panic!("Expected allow");
        }
    }

    #[test]
    fn handle_null_values() {
        let policies = wrap(
            load_many_from_reader(
                r#"[
              {
                "tool_name": "grant_loan",
                "rule": {
                  "id": "approve_if_not_jonathan",
                  "action": "deny",
                  "when": {
                    "op": "any_of",
                    "conditions": [
                      {
                        "source": "state",
                        "matches": {
                          "key": "name",
                          "op": "eq",
                          "value": "Jonathan"
                        }
                      }
                    ]
                  }
                }
              }
            ]
            "#
                .as_bytes(),
            )
            .unwrap(),
        );

        let eng = engine(policies);
        let action = eng
            .process_tool_call(
                "grant_loan",
                "test-call-11",
                &json!({}),
                &json!({"user": { "name": null }}), // user.name explicitly set to null.
            )
            .unwrap();

        if let ProcessToolCallResult::Deny { .. } = action {
            panic!("Expected allow");
        }
    }

    #[test]
    fn handle_not_equals_when_state_value_is_null() {
        let policies = wrap(
            load_many_from_reader(
                r#"[
              {
                "tool_name": "grant_loan",
                "rule": {
                  "id": "approve_if_not_jonathan",
                  "action": "deny",
                  "when": {
                    "op": "any_of",
                    "conditions": [
                      {
                        "source": "state",
                        "matches": {
                          "key": "name",
                          "op": "ne",
                          "value": "Jonathan"
                        }
                      }
                    ]
                  }
                }
              }
            ]
            "#
                .as_bytes(),
            )
            .unwrap(),
        );

        let eng = engine(policies);
        let action = eng
            .process_tool_call(
                "grant_loan",
                "test-call-12",
                &json!({}),
                &json!({"user": { "name": null }}), // user.name is explicitly set to null.
            )
            .unwrap();

        if let ProcessToolCallResult::Allow { .. } = action {
            panic!("Expected deny");
        }
    }

    #[test]
    fn handle_value_must_equal_null() {
        let policies = wrap(
            load_many_from_reader(
                r#"[
              {
                "tool_name": "grant_loan",
                "rule": {
                  "id": "approve_if_not_banned",
                  "action": "allow",
                  "when": {
                    "op": "any_of",
                    "conditions": [
                      {
                        "source": "state",
                        "matches": {
                          "key": "banned",
                          "op": "eq",
                          "value": null
                        }
                      }
                    ]
                  }
                }
              }
            ]
            "#
                .as_bytes(),
            )
            .unwrap(),
        );

        let eng = engine(policies);
        let action = eng
            .process_tool_call(
                "grant_loan",
                "test-call-13",
                &json!({}),
                &json!({"banned": null}), // state has `banned` explicitly set to null.
            )
            .unwrap();

        if let ProcessToolCallResult::Deny { .. } = action {
            panic!("Expected allow");
        }
    }

    #[test]
    fn allow_if_regex_matches() {
        let policies = wrap(vec![ToolPolicy {
            tool_name: "greet".into(),
            rule: ToolPolicyRule::Allow {
                when: ToolCondition::Atomic(AtomicToolCondition {
                    source: SourceTag::State,
                    matches: PropertyMatcher::Scalar(PropertyScalarMatcher {
                        key: "name".into(),
                        op: ValueScalarOperator::Regex,
                        value: ValueOrReference::Value(Value::String("^Jon.*".into())),
                    }),
                }),
            },
        }]);

        let eng = engine(policies);
        let allow_action = eng
            .process_tool_call(
                "greet",
                "test-call-14",
                &json!({}),
                &json!({"name": "Jonathan"}),
            )
            .unwrap();
        match allow_action {
            ProcessToolCallResult::Allow { rules_matched } => {
                assert_eq!(rules_matched.len(), 1);
            }
            _ => panic!("expected allow for matching regex"),
        }

        let deny_action = eng
            .process_tool_call(
                "greet",
                "test-call-15",
                &json!({}),
                &json!({"name": "Alice"}),
            )
            .unwrap();
        match deny_action {
            ProcessToolCallResult::Deny { .. } => {}
            _ => panic!("expected deny for non-matching regex"),
        }
    }

    #[test]
    fn evaluate_negated_condition() {
        let policies = wrap(vec![ToolPolicy {
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
        }]);

        let eng = engine(policies);
        let deny_action = eng
            .process_tool_call(
                "login_user",
                "test-call-15",
                &json!({}),
                &json!({"user": {"isBanned": true}}),
            )
            .unwrap();
        match deny_action {
            ProcessToolCallResult::Deny { .. } => {}
            _ => panic!("expected deny for matching negated condition."),
        }
    }
}
