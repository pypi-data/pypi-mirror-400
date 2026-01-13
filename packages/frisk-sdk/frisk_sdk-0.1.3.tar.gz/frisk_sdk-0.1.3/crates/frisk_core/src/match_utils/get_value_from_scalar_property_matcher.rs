use crate::errors::PolicyEngineError;
use crate::policy_types::{PropertyScalarMatcher, SourceTag, ValueOrReference};
use crate::value_utils::get_value_at_path::get_value_at_path;
use serde_json::Value;

pub fn get_value_from_scalar_property_matcher(
    matcher: &PropertyScalarMatcher,
    tool_args: &Value,
    agent_state: &Value,
) -> Result<Value, PolicyEngineError> {
    match &matcher.value {
        ValueOrReference::Value(v) => Ok(v.clone()),
        ValueOrReference::Reference(r) => match r.source {
            SourceTag::Args => Ok(get_value_at_path(tool_args, &r.path)?.clone()),
            SourceTag::State => Ok(get_value_at_path(agent_state, &r.path)?.clone()),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::get_value_from_scalar_property_matcher;
    use crate::policy_types::{
        PropertyScalarMatcher, SourceTag, ValueOrReference, ValueReference, ValueScalarOperator,
    };
    use serde_json::{Value, json};

    fn matcher_with_literal(op: ValueScalarOperator, val: Value) -> PropertyScalarMatcher {
        PropertyScalarMatcher {
            key: "ignored".into(),
            op,
            value: ValueOrReference::Value(val),
        }
    }

    fn matcher_with_ref(
        op: ValueScalarOperator,
        source: SourceTag,
        path: &str,
    ) -> PropertyScalarMatcher {
        PropertyScalarMatcher {
            key: "ignored".into(),
            op,
            value: ValueOrReference::Reference(ValueReference {
                source,
                path: path.into(),
            }),
        }
    }

    #[test]
    fn returns_literal_value_unchanged() {
        let m = matcher_with_literal(ValueScalarOperator::Eq, Value::String("Alice".into()));
        let v = get_value_from_scalar_property_matcher(&m, &json!({}), &json!({})).expect("ok");
        assert_eq!(v, Value::String("Alice".into()));
    }

    #[test]
    fn resolves_reference_from_args() {
        let m = matcher_with_ref(ValueScalarOperator::Eq, SourceTag::Args, "user.id");
        let args = json!({"user": {"id": 123}});
        let state = json!({});
        let v = get_value_from_scalar_property_matcher(&m, &args, &state).expect("ok");
        assert_eq!(v, Value::from(123));
    }

    #[test]
    fn resolves_reference_from_state() {
        let m = matcher_with_ref(
            ValueScalarOperator::Eq,
            SourceTag::State,
            "user.profile.name",
        );
        let args = json!({});
        let state = json!({"user": {"profile": {"name": "Bob"}}});
        let v = get_value_from_scalar_property_matcher(&m, &args, &state).expect("ok");
        assert_eq!(v, Value::String("Bob".into()));
    }

    #[test]
    fn missing_path_returns_null() {
        let m = matcher_with_ref(ValueScalarOperator::Eq, SourceTag::State, "user.age");
        let v = get_value_from_scalar_property_matcher(
            &m,
            &json!({}),
            &json!({"user": {"name": "Alice"}}),
        )
        .expect("ok");
        assert_eq!(v, Value::Null);
    }

    #[test]
    fn traversal_into_non_object_yields_null() {
        let m = matcher_with_ref(
            ValueScalarOperator::Eq,
            SourceTag::Args,
            "user.profile.name",
        );
        let args = json!({"user": {"profile": "string-not-object"}});
        let v = get_value_from_scalar_property_matcher(&m, &args, &json!({})).expect("ok");
        assert_eq!(v, Value::Null);
    }

    #[test]
    fn empty_path_returns_root_value() {
        let m = matcher_with_ref(ValueScalarOperator::Eq, SourceTag::Args, "");
        let args = json!({"a": 1});
        let v = get_value_from_scalar_property_matcher(&m, &args, &json!({})).expect("ok");
        assert_eq!(v, args);
    }

    #[test]
    fn array_index_like_segment_returns_null() {
        let m = matcher_with_ref(ValueScalarOperator::Eq, SourceTag::Args, "items.0.id");
        let args = json!({"items": [{"id": 1}, {"id": 2}]});
        let v = get_value_from_scalar_property_matcher(&m, &args, &json!({})).expect("ok");
        assert_eq!(v, Value::Null);
    }
}
