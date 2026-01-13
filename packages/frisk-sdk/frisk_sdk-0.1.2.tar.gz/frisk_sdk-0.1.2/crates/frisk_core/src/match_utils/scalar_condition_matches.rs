use crate::errors::PolicyEngineError;
use crate::match_utils::cmp_matches::cmp_matches;
use crate::match_utils::eq_matches::eq_matches;
use crate::match_utils::expected_includes_value_matching_actual::expected_includes_value_matching_actual;
use crate::policy_types::{PropertyScalarMatcher, ValueScalarOperator};
use crate::regex_matcher::RegexMatcher;
use serde_json::Value;

pub fn property_scalar_matcher_matches(
    condition: &PropertyScalarMatcher,
    actual_value: &Value,
    expected_value: &Value,
    regex_matcher: &RegexMatcher,
) -> Result<bool, PolicyEngineError> {
    match (&condition.op, actual_value) {
        // Null-compatible
        (ValueScalarOperator::Eq, _) => eq_matches(expected_value, actual_value),
        (ValueScalarOperator::Ne, _) => eq_matches(expected_value, actual_value).map(|b| !b),
        (ValueScalarOperator::In, _) => {
            expected_includes_value_matching_actual(expected_value, actual_value)
        }
        // Throw appropriate errors if actual is null
        (ValueScalarOperator::Regex, Value::Null) => Err(PolicyEngineError::ComparisonError(
            "string".into(),
            "null".into(),
        )),
        (
            ValueScalarOperator::Lt
            | ValueScalarOperator::Gt
            | ValueScalarOperator::Lte
            | ValueScalarOperator::Gte,
            Value::Null,
        ) => Err(PolicyEngineError::ComparisonError(
            "number".into(),
            "null".into(),
        )),
        // Non-null compatible
        (ValueScalarOperator::Lt, _) => cmp_matches(expected_value, actual_value, |a, b| a < b),
        (ValueScalarOperator::Gt, _) => cmp_matches(expected_value, actual_value, |a, b| a > b),
        (ValueScalarOperator::Lte, _) => cmp_matches(expected_value, actual_value, |a, b| a <= b),
        (ValueScalarOperator::Gte, _) => cmp_matches(expected_value, actual_value, |a, b| a >= b),
        (ValueScalarOperator::Regex, _) => {
            regex_matcher.regex_matches(expected_value, actual_value)
        }
    }
}
