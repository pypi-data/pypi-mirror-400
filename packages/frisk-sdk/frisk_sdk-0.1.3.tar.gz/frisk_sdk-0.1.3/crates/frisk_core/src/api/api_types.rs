use serde::Deserialize;

#[derive(Deserialize)]
pub struct PoliciesResponse {
    pub(crate) policies: Vec<PolicyEnvelope>,
}

#[derive(Deserialize)]
pub struct PolicyEnvelope {
    pub id: String,
    pub name: String,
    #[serde(rename = "currentVersionId")]
    pub(crate) current_version_id: String,
    #[serde(rename = "currentVersion")]
    pub(crate) current_version: PolicyVersion,
}

#[derive(Deserialize)]
pub struct PolicyVersion {
    pub(crate) body: String,
}
