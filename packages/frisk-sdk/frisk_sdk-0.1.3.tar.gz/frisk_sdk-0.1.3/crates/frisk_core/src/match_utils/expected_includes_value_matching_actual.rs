use crate::errors::PolicyEngineError;
use crate::match_utils::eq_matches::eq_matches;
use crate::try_utils::try_any;
use serde_json::Value;

pub fn expected_includes_value_matching_actual(
    expected: &Value,
    actual: &Value,
) -> Result<bool, PolicyEngineError> {
    if let Value::Array(arr) = expected {
        try_any(arr.iter(), |item| eq_matches(item, actual))
    } else {
        Err(PolicyEngineError::ComparisonError(
            "list".into(),
            "non-list".into(),
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::expected_includes_value_matching_actual;
    use serde_json::json;

    #[test]
    fn matches_when_actual_is_in_expected_array() {
        let expected = json!(["alpha", "beta", "gamma"]);
        let actual = json!("beta");
        let res = expected_includes_value_matching_actual(&expected, &actual).expect("ok");
        assert!(res);
    }

    #[test]
    fn does_not_match_when_actual_not_in_expected_array() {
        let expected = json!(["alpha", "beta", "gamma"]);
        let actual = json!("delta");
        let res = expected_includes_value_matching_actual(&expected, &actual).expect("ok");
        assert!(!res);
    }

    #[test]
    fn non_list_expected_returns_comparison_error() {
        let expected = json!({"not": "a list"});
        let actual = json!("alpha");
        let err = expected_includes_value_matching_actual(&expected, &actual).unwrap_err();
        match err {
            crate::errors::PolicyEngineError::ComparisonError(expected, actual) => {
                assert_eq!(expected, "list");
                assert_eq!(actual, "non-list");
            }
            other => panic!("unexpected error variant: {}", other),
        }
    }

    #[test]
    fn matches_numbers_by_value() {
        let expected = json!([1, 2, 3]);
        let actual = json!(2);
        let res = expected_includes_value_matching_actual(&expected, &actual).expect("ok");
        assert!(res);
    }

    #[test]
    fn matches_booleans_by_value() {
        let expected = json!([true, false]);
        let actual = json!(false);
        let res = expected_includes_value_matching_actual(&expected, &actual).expect("ok");
        assert!(res);
    }

    #[test]
    fn deep_equality_match_for_objects() {
        let expected = json!([
            {"a": 1, "b": {"x": 10}},
            {"a": 2, "b": {"x": 20}}
        ]);
        let actual = json!({"a": 1, "b": {"x": 10}});
        let res = expected_includes_value_matching_actual(&expected, &actual).expect("ok");
        assert!(res);
    }

    #[test]
    fn deep_equality_no_match_when_differs() {
        let expected = json!([
            {"a": 1, "b": {"x": 10}},
            {"a": 2, "b": {"x": 20}}
        ]);
        let actual = json!({"a": 1, "b": {"x": 11}});
        let res = expected_includes_value_matching_actual(&expected, &actual).expect("ok");
        assert!(!res);
    }
}
