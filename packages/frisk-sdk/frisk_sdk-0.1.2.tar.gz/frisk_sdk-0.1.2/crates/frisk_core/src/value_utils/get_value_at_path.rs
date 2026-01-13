use crate::errors::PolicyEngineError;
use serde_json::Value;

// Navigates a dotted path in a JSON object and returns a reference to the value or Value::Null if missing.
pub fn get_value_at_path<'a>(root: &'a Value, path: &str) -> Result<&'a Value, PolicyEngineError> {
    // If path is empty or only whitespace, return the root value directly.
    if path.trim().is_empty() {
        return Ok(root);
    }

    let mut current = Some(root);
    for part in path.split('.') {
        current = match current {
            Some(Value::Object(map)) => map.get(part),
            _ => {
                return Ok(&Value::Null);
            }
        };
    }
    match current {
        None => Ok(&Value::Null),
        Some(v) => Ok(v),
    }
}

#[cfg(test)]
mod tests {
    use super::get_value_at_path;
    use serde_json::{Value, json};

    #[test]
    fn returns_value_for_existing_nested_path() {
        let root = json!({
            "user": {
                "profile": {
                    "name": "Alice",
                    "age": 30
                }
            }
        });
        let v = get_value_at_path(&root, "user.profile.name").expect("ok");
        assert_eq!(v, &Value::String("Alice".to_string()));

        let age = get_value_at_path(&root, "user.profile.age").expect("ok");
        assert_eq!(age, &Value::from(30));
    }

    #[test]
    fn returns_null_for_missing_key() {
        let root = json!({
            "user": {
                "profile": {
                    "name": "Alice"
                }
            }
        });
        let v = get_value_at_path(&root, "user.profile.age").expect("ok");
        assert_eq!(v, &Value::Null);
    }

    #[test]
    fn returns_null_when_path_traversal_hits_non_object() {
        let root = json!({
            "user": {
                "profile": "not-an-object"
            }
        });
        // Attempting to go deeper after a string should yield Null
        let v = get_value_at_path(&root, "user.profile.name").expect("ok");
        assert_eq!(v, &Value::Null);
    }

    #[test]
    fn empty_path_returns_root() {
        let root = json!({
            "a": 1
        });
        let v = get_value_at_path(&root, "").expect("ok");
        assert_eq!(v, &root);
    }

    #[test]
    fn array_in_path_is_not_supported_and_returns_null_on_index_like_segment() {
        let root = json!({
            "items": [
                { "id": 1 },
                { "id": 2 }
            ]
        });
        // Current implementation only traverses objects; arrays are not supported
        let v = get_value_at_path(&root, "items.0.id").expect("ok");
        assert_eq!(v, &Value::Null);
    }

    #[test]
    fn top_level_missing_key_returns_null() {
        let root = json!({
            "present": true
        });
        let v = get_value_at_path(&root, "missing").expect("ok");
        assert_eq!(v, &Value::Null);
    }
}
