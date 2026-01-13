use crate::errors::PolicyEngineError;
use serde_json::Value;

pub fn eq_matches(expected: &Value, actual: &Value) -> Result<bool, PolicyEngineError> {
    match (expected, actual) {
        (Value::Number(en), Value::Number(an)) => {
            let af = an.as_f64().ok_or(PolicyEngineError::ComparisonError(
                "number".into(),
                "non-number".into(),
            ))?;

            let ef = en.as_f64().ok_or(PolicyEngineError::ComparisonError(
                "number".into(),
                "non-number".into(),
            ))?;

            Ok((ef - af).abs() < f64::EPSILON)
        }

        _ => Ok(expected == actual),
    }
}

#[cfg(test)]
mod tests {
    use super::eq_matches;
    use serde_json::{Value, json};

    #[test]
    fn null_equals_null() {
        let res = eq_matches(&Value::Null, &Value::Null).expect("ok");
        assert!(res);
    }

    #[test]
    fn anything_equals_null_is_false() {
        let res = eq_matches(&json!("x"), &Value::Null).expect("ok");
        assert!(!res);
        let res2 = eq_matches(&json!(123), &Value::Null).expect("ok");
        assert!(!res2);
    }

    #[test]
    fn equal_strings_true() {
        let res = eq_matches(&json!("hello"), &json!("hello")).expect("ok");
        assert!(res);
    }

    #[test]
    fn different_strings_false() {
        let res = eq_matches(&json!("hello"), &json!("world")).expect("ok");
        assert!(!res);
    }

    #[test]
    fn equal_booleans_true() {
        let res = eq_matches(&json!(true), &json!(true)).expect("ok");
        assert!(res);
        let res2 = eq_matches(&json!(false), &json!(false)).expect("ok");
        assert!(res2);
    }

    #[test]
    fn different_booleans_false() {
        let res = eq_matches(&json!(true), &json!(false)).expect("ok");
        assert!(!res);
    }

    #[test]
    fn equal_integers_true() {
        let res = eq_matches(&json!(42), &json!(42)).expect("ok");
        assert!(res);
    }

    #[test]
    fn different_integers_false() {
        let res = eq_matches(&json!(41), &json!(42)).expect("ok");
        assert!(!res);
    }

    #[test]
    fn equal_floats_true() {
        let res = eq_matches(&json!(3.14), &json!(3.14)).expect("ok");
        assert!(res);
    }

    #[test]
    fn mixed_int_float_equality_false() {
        // 10 vs 10.0 should be equal numerically; with EPSILON this should be true
        let res = eq_matches(&json!(10), &json!(10.0)).expect("ok");
        assert!(res);
    }
}
