use thiserror::Error;

#[derive(Debug, Error)]
pub enum PolicyEngineError {
    #[error("Mismatched value type at {0}. Expected {1}, got {2}.")]
    MismatchedValueAtPath(
        String, // path // todo: Add Original path here (state#path) for better visibility. https://linear.app/friskai/issue/POL-19/custom-error-messages-for-deny-actions
        String, // Expected type
        String, // Actual type
    ),
    #[error("No value found at path {0}.")]
    MissingValueAtPath(String),

    #[error("Mismatched value. Expected {0}, got {1}.")]
    ComparisonError(
        String, // Expected type
        String, // Actual type
    ),
}
