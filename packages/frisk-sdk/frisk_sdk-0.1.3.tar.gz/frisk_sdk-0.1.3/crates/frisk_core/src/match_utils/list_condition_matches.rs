use crate::errors::PolicyEngineError;
use crate::match_utils::eq_matches::eq_matches;
use crate::policy_types::{PropertyListMatcher, ValueListOperator};
use crate::try_utils::{try_all, try_any};
use serde_json::Value;

pub fn list_property_matcher_matches(
    cond: &PropertyListMatcher,
    actual_list: &Value,
) -> Result<bool, PolicyEngineError> {
    let arr = actual_list
        .as_array()
        .ok_or_else(|| PolicyEngineError::ComparisonError("array".into(), "non-array".into()))?;
    let contains = |needle: &Value| try_any(arr.iter(), |v| eq_matches(v, needle));
    match cond.op {
        ValueListOperator::ContainsAny => try_any(cond.values.iter(), &contains),
        ValueListOperator::ContainsAll => try_all(cond.values.iter(), &contains),
        ValueListOperator::ContainsNone => try_all(cond.values.iter(), |v| contains(v).map(|b| !b)),
    }
}

#[cfg(test)]
mod tests {
    use super::list_property_matcher_matches;
    use crate::policy_types::{PropertyListMatcher, ValueListOperator};
    use serde_json::{Value, json};

    fn matcher(op: ValueListOperator, values: Vec<Value>) -> PropertyListMatcher {
        PropertyListMatcher {
            key: "ignored".into(),
            op,
            values,
        }
    }

    #[test]
    fn contains_any_matches_when_any_value_present() {
        let m = matcher(
            ValueListOperator::ContainsAny,
            vec![Value::String("a".into()), Value::String("z".into())],
        );
        let actual = json!(["x", "y", "a"]);
        let res = list_property_matcher_matches(&m, &actual).expect("ok");
        assert!(res);
    }

    #[test]
    fn contains_any_fails_when_none_present() {
        let m = matcher(
            ValueListOperator::ContainsAny,
            vec![Value::String("a".into()), Value::String("z".into())],
        );
        let actual = json!(["x", "y", "b"]);
        let res = list_property_matcher_matches(&m, &actual).expect("ok");
        assert!(!res);
    }

    #[test]
    fn contains_all_matches_when_all_values_present() {
        let m = matcher(
            ValueListOperator::ContainsAll,
            vec![Value::String("a".into()), Value::String("b".into())],
        );
        let actual = json!(["a", "b", "c"]);
        let res = list_property_matcher_matches(&m, &actual).expect("ok");
        assert!(res);
    }

    #[test]
    fn contains_all_fails_when_any_missing() {
        let m = matcher(
            ValueListOperator::ContainsAll,
            vec![Value::String("a".into()), Value::String("b".into())],
        );
        let actual = json!(["a", "c"]);
        let res = list_property_matcher_matches(&m, &actual).expect("ok");
        assert!(!res);
    }

    #[test]
    fn contains_none_matches_when_none_present() {
        let m = matcher(
            ValueListOperator::ContainsNone,
            vec![Value::String("a".into()), Value::String("b".into())],
        );
        let actual = json!(["x", "y", "z"]);
        let res = list_property_matcher_matches(&m, &actual).expect("ok");
        assert!(res);
    }

    #[test]
    fn contains_none_fails_when_any_present() {
        let m = matcher(
            ValueListOperator::ContainsNone,
            vec![Value::String("a".into()), Value::String("b".into())],
        );
        let actual = json!(["a", "y", "z"]);
        let res = list_property_matcher_matches(&m, &actual).expect("ok");
        assert!(!res);
    }

    #[test]
    fn non_array_input_returns_error() {
        let m = matcher(
            ValueListOperator::ContainsAny,
            vec![Value::String("a".into())],
        );
        let actual = json!({"not": "an array"});
        let err = list_property_matcher_matches(&m, &actual).unwrap_err();
        match err {
            crate::errors::PolicyEngineError::ComparisonError(expected, actual) => {
                assert_eq!(expected, "array");
                assert_eq!(actual, "non-array");
            }
            other => panic!("unexpected error variant: {}", other),
        }
    }
}
