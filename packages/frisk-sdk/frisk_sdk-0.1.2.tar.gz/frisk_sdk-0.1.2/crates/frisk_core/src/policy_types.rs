use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ToolPolicy {
    pub tool_name: String,
    pub rule: ToolPolicyRule,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(tag = "action")]
pub enum ToolPolicyRule {
    #[serde(rename = "allow")]
    Allow { when: ToolCondition },
    #[serde(rename = "deny")]
    Deny { when: ToolCondition },
    #[serde(rename = "modify")]
    Modify {
        when: ToolCondition,
        updated_action: UpdatedAction,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct UpdatedAction {
    pub tool_name: String,
    pub args: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum ToolCondition {
    Atomic(AtomicToolCondition),
    Boolean(BooleanCombinationToolCondition),
    Not { not: Box<ToolCondition> },
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct BooleanCombinationToolCondition {
    pub op: BooleanOperator,
    pub conditions: Vec<ToolCondition>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AtomicToolCondition {
    pub source: SourceTag, // 'args' | 'state'
    pub matches: PropertyMatcher,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum PropertyMatcher {
    Scalar(PropertyScalarMatcher),
    List(PropertyListMatcher),
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PropertyScalarMatcher {
    pub key: String,
    pub op: ValueScalarOperator,
    pub value: ValueOrReference,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PropertyListMatcher {
    pub key: String,
    pub op: ValueListOperator,
    pub values: Vec<Value>,
}

/// Represents a value in a policy condition that can be either a literal scalar value
/// or a dynamic reference to a value resolved at evaluation time.
///
/// # Variants
///
/// * `Value` - A literal scalar value (string, number, or boolean)
/// * `Reference` - A dynamic reference to a value from the execution context
///
/// # Usage
///
/// This enum allows policy rules to compare against either:
/// - Fixed literal values: `"admin"`, `100`, `true`
/// - Dynamic references: `{{state#user.role}}`, `{{args#amount}}`
///
/// # Examples
///
/// Literal value in JSON:
/// ```json
/// {
///   "op": "eq",
///   "value": "admin"
/// }
/// ```
///
/// Dynamic reference in JSON (parsed from string template):
/// ```json
/// {
///   "op": "eq",
///   "value": "{{state#user.id}}"
/// }
/// ```
///
/// The string template `"{{state#user.id}}"` is automatically converted to a
/// `ValueReference` during policy loading.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum ValueOrReference {
    Value(Value),
    Reference(ValueReference),
}

impl From<Value> for ValueOrReference {
    fn from(v: Value) -> Self {
        ValueOrReference::Value(v)
    }
}

/// Represents a dynamic reference to a value that is resolved at policy evaluation time.
///
/// Dynamic references allow policies to access values from the runtime context rather than
/// comparing against fixed literal values. This enables policies like "allow if the requested
/// userId matches the authenticated user's id from state".
///
/// # Fields
///
/// * `source` - The source of the value, either `state` (agent/application state) or `args` (tool arguments)
/// * `path` - A dot-separated path to the value within the source (e.g., "user.id", "account.balance")
///
/// # Format in JSON Policies
///
/// References are written as string templates with the format: `{{source#path}}`
///
/// Examples:
/// - `"{{state#user.id}}"` - References `user.id` from the state object
/// - `"{{args#userId}}"` - References the `userId` field from tool arguments
/// - `"{{state#account.owner.name}}"` - References nested values using dot notation
///
/// # Resolution at Evaluation Time
///
/// During policy evaluation:
/// 1. The policy engine receives the tool arguments and agent state as JSON values
/// 2. For each reference, it looks up the value at the specified path in the specified source
/// 3. The retrieved value is compared against the condition using the specified operator
///
/// For example, a policy condition like:
/// ```json
/// {
///   "key": "userId",
///   "value": {
///     "op": "eq",
///     "value": "{{state#user.id}}"
///   }
/// }
/// ```
///
/// Will compare `args.userId` against the value found at `state.user.id` at evaluation time.
///
/// # See Also
///
/// * [`SourceTag`] - Enum defining valid sources (state or args)
/// * [`ValueOrReference`] - Enum that can hold either a reference or literal value
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ValueReference {
    pub source: SourceTag, // e.g. state | args
    pub path: String,      // e.g. "user.id" or "userId"
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum ValueScalarOperator {
    Eq,
    Lt,
    Gt,
    Lte,
    Gte,
    In,
    Ne,
    Regex,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ValueListCondition {
    pub op: ValueListOperator,
    pub values: Vec<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum ValueListOperator {
    ContainsAny,
    ContainsAll,
    ContainsNone,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum BooleanOperator {
    AnyOf,
    AllOf,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum SourceTag {
    Args,
    State,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ToolPolicyRecord {
    pub id: String,
    pub name: String,
    pub current_version_id: String,
    pub policy: ToolPolicy,
}
