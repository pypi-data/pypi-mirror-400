use crate::errors::PolicyEngineError;
use serde_json::Value;

pub fn cmp_matches<F: Fn(f64, f64) -> bool>(
    expected: &Value,
    actual: &Value,
    cmp: F,
) -> Result<bool, PolicyEngineError> {
    match (expected.as_f64(), actual.as_f64()) {
        (Some(expected_number), Some(actual_number)) => Ok(cmp(actual_number, expected_number)),

        _ => Err(PolicyEngineError::ComparisonError(
            "number".into(),
            "non-number".into(),
        )),
    }
}

#[cfg(test)]
mod tests {
    use super::cmp_matches;
    use serde_json::json;

    #[test]
    fn greater_than_happy_path() {
        let expected = json!(10);
        let actual = json!(15);
        let res = cmp_matches(&expected, &actual, |a, e| a > e).expect("ok");
        assert!(res);
    }

    #[test]
    fn less_than_happy_path() {
        let expected = json!(10);
        let actual = json!(5);
        let res = cmp_matches(&expected, &actual, |a, e| a < e).expect("ok");
        assert!(res);
    }

    #[test]
    fn equality_happy_path_integers() {
        let expected = json!(42);
        let actual = json!(42);
        let res = cmp_matches(&expected, &actual, |a, e| (a - e).abs() < f64::EPSILON).expect("ok");
        assert!(res);
    }

    #[test]
    fn equality_happy_path_floats() {
        let expected = json!(3.14);
        let actual = json!(3.14);
        let res = cmp_matches(&expected, &actual, |a, e| (a - e).abs() < 1e-12).expect("ok");
        assert!(res);
    }

    #[test]
    fn comparator_receives_actual_then_expected() {
        let expected = json!(2);
        let actual = json!(8);
        // The comparator checks ordering explicitly
        let res = cmp_matches(&expected, &actual, |a, e| {
            // Ensure we received (actual, expected) as documented by implementation
            assert_eq!(a, 8.0);
            assert_eq!(e, 2.0);
            a % e == 0.0
        })
        .expect("ok");
        assert!(res);
    }

    #[test]
    fn error_when_expected_is_non_number() {
        let expected = json!("ten");
        let actual = json!(10);
        let err = cmp_matches(&expected, &actual, |a, e| a > e).unwrap_err();
        // We don't assert the exact message; just that an error is returned
        let _ = err; // type check
    }

    #[test]
    fn error_when_actual_is_non_number() {
        let expected = json!(10);
        let actual = json!("ten");
        let err = cmp_matches(&expected, &actual, |a, e| a > e).unwrap_err();
        let _ = err;
    }

    #[test]
    fn handles_mixed_integer_and_float() {
        let expected = json!(10.5);
        let actual = json!(11);
        let res = cmp_matches(&expected, &actual, |a, e| a > e).expect("ok");
        assert!(res);
    }
}
