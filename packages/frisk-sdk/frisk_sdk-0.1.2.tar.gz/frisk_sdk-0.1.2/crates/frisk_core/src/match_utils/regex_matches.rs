use crate::errors::PolicyEngineError;
use regex::Regex;
use serde_json::Value;

// Pure helper: takes a compiled Regex and an actual JSON value and performs matching.
// Returns ComparisonError if actual is not a string.
pub fn regex_matches_compiled(re: &Regex, actual: &Value) -> Result<bool, PolicyEngineError> {
    match actual {
        Value::String(s) => Ok(re.is_match(s)),
        _ => Err(PolicyEngineError::ComparisonError(
            "string".into(),
            "non-string".into(),
        )),
    }
}

#[cfg(test)]
mod tests {
    use super::regex_matches_compiled;
    use regex::Regex;
    use serde_json::json;

    #[test]
    fn matches_when_string_satisfies_regex() {
        let re = Regex::new(r"^Jon.*").expect("compile");
        let actual = json!("Jonathan");
        let res = regex_matches_compiled(&re, &actual).expect("ok");
        assert!(res);
    }

    #[test]
    fn does_not_match_when_string_does_not_satisfy_regex() {
        let re = Regex::new(r"^Jon.*").expect("compile");
        let actual = json!("Alice");
        let res = regex_matches_compiled(&re, &actual).expect("ok");
        assert!(!res);
    }

    #[test]
    fn non_string_input_returns_comparison_error() {
        let re = Regex::new(r"^Jon.*").expect("compile");
        let actual = json!({"name": "Jonathan"});
        let err = regex_matches_compiled(&re, &actual).unwrap_err();
        match err {
            crate::errors::PolicyEngineError::ComparisonError(expected, actual) => {
                assert_eq!(expected, "string");
                assert_eq!(actual, "non-string");
            }
            other => panic!("unexpected error variant: {}", other),
        }
    }
}
