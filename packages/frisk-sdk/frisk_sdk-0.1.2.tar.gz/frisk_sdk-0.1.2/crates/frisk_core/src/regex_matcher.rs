use crate::errors::PolicyEngineError;
use crate::match_utils::regex_matches::regex_matches_compiled;
use regex::Regex;
use serde_json::Value;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

// New regex matcher that encapsulates the cache and matching logic
#[derive(Clone, Default)]
pub struct RegexMatcher {
    regex_cache: Arc<Mutex<HashMap<String, Regex>>>,
}

impl RegexMatcher {
    pub fn new(cache: Arc<Mutex<HashMap<String, Regex>>>) -> Self {
        Self { regex_cache: cache }
    }

    pub fn regex_matches(
        &self,
        expected: &Value,
        actual: &Value,
    ) -> Result<bool, PolicyEngineError> {
        // Expected must be a string pattern
        let expected_pattern = match expected {
            Value::String(s) => s,
            _ => {
                return Err(PolicyEngineError::ComparisonError(
                    "string".into(),
                    "non-string".into(),
                ));
            }
        };

        // Check cache first
        {
            let cache = self.regex_cache.lock().expect("Regex cache mutex poisoned");

            if let Some(re) = cache.get(expected_pattern) {
                return regex_matches_compiled(re, actual);
            }
        } // Release lock before compiling regex

        // Compile the regex pattern (outside the lock to reduce contention)
        let re = Regex::new(expected_pattern).map_err(|_| {
            PolicyEngineError::ComparisonError("valid_regex".into(), "invalid_regex".into())
        })?;

        let is_match = regex_matches_compiled(&re, actual)?;

        // Cache the compiled regex
        {
            let mut cache = self.regex_cache.lock().expect("Regex cache mutex poisoned");
            cache.insert(expected_pattern.to_owned(), re);
        }

        Ok(is_match)
    }
}
