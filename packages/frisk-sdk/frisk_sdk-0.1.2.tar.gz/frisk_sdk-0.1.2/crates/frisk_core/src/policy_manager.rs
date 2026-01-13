use crate::api::api_types::PoliciesResponse;
use crate::event::Event;
use crate::policy_loader::{PolicyLoadError, load_one_from_reader};
use crate::policy_types::ToolPolicy;
use crate::policy_types::ToolPolicyRecord;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use tokio::task::JoinHandle;
use tokio::time;

#[derive(Debug)]
pub struct PolicyManager {
    access_token: String,
    pub policies: Arc<Mutex<Vec<ToolPolicyRecord>>>,
    refresh_handle: Option<JoinHandle<()>>, // background task
    refresh_interval: Duration,
    policies_url: String,
    pub on_policy_update: Arc<Event<Vec<ToolPolicyRecord>>>,
}

#[derive(Debug, thiserror::Error)]
pub enum PolicyManagerError {
    #[error("http error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("policy load error: {0}")]
    PolicyLoad(#[from] crate::policy_loader::PolicyLoadError),
}

impl PolicyManager {
    pub fn new(access_token: String, refresh_interval_seconds: u64, policies_url: String) -> Self {
        Self {
            access_token,
            policies: Arc::new(Mutex::new(Vec::new())),
            refresh_handle: None,
            refresh_interval: Duration::from_secs(refresh_interval_seconds),
            policies_url,
            on_policy_update: Arc::new(Event::<Vec<ToolPolicyRecord>>::new()),
        }
    }

    pub fn with_url(mut self, policies_url: impl Into<String>) -> Self {
        self.policies_url = policies_url.into();
        self
    }

    pub fn update_access_token(&mut self, access_token: &str) {
        self.access_token = access_token.to_string();
    }

    pub fn start(&mut self) {
        let interval = self.refresh_interval;
        let token = self.access_token.clone();
        let policies_arc = Arc::clone(&self.policies);
        let policies_url = self.policies_url.clone();
        let on_update = Arc::clone(&self.on_policy_update);
        let handle = tokio::spawn(async move {
            // initial fetch immediately
            if let Err(e) = Self::fetch_once(
                &token,
                &policies_url,
                policies_arc.clone(),
                on_update.clone(),
            )
            .await
            {
                tracing::warn!(error = %e, "initial policy fetch failed");
            }
            let mut ticker = time::interval(interval);
            loop {
                ticker.tick().await;
                if let Err(e) = Self::fetch_once(
                    &token,
                    &policies_url,
                    policies_arc.clone(),
                    on_update.clone(),
                )
                .await
                {
                    tracing::warn!(error = %e, "policy fetch failed");
                }
            }
        });
        self.refresh_handle = Some(handle);
    }

    pub async fn stop(&mut self) {
        if let Some(handle) = self.refresh_handle.take() {
            handle.abort();
        }
    }

    pub async fn fetch_once(
        token: &str,
        policies_url: &str,
        policies_arc: Arc<Mutex<Vec<ToolPolicyRecord>>>,
        on_update: Arc<Event<Vec<ToolPolicyRecord>>>,
    ) -> Result<(), PolicyManagerError> {
        let client = reqwest::Client::new();
        let resp = client
            .get(policies_url)
            .bearer_auth(token)
            .send()
            .await?
            .error_for_status()?;
        let payload: PoliciesResponse = resp.json().await?;

        let mut records: Vec<ToolPolicyRecord> = Vec::with_capacity(payload.policies.len());
        for p in payload.policies.into_iter() {
            let policy_json = p.current_version.body;
            let tool_policy_result: Result<ToolPolicy, PolicyLoadError> =
                load_one_from_reader(policy_json.as_bytes());
            match tool_policy_result {
                Ok(tool_policy) => records.push(ToolPolicyRecord {
                    id: p.id.clone(),
                    name: p.name.clone(),
                    current_version_id: p.current_version_id.clone(),
                    policy: tool_policy,
                }),
                Err(policy_load_error) => {
                    tracing::error!(error = %policy_load_error, "failed to load policy \"{}\"", p.name);
                    continue;
                }
            }
        }
        let mut guard = policies_arc.lock().unwrap();
        *guard = records.clone();
        on_update.emit(&records);

        Ok(())
    }

    /// Convenience: produce Vec<ToolPolicy> for PolicyEngine from current records
    pub fn tool_policies(&self) -> Vec<ToolPolicy> {
        let guard = self.policies.lock().unwrap();
        guard.iter().map(|r| r.policy.clone()).collect()
    }
}
