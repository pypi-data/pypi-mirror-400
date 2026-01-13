use pyo3::prelude::*;
use std::ops::Deref;

use frisk_core::policy_engine::PolicyEngine;
use frisk_core::policy_types::ToolPolicyRecord;
use py_dict_carrier::PyDictCarrier;

use frisk_core::otel::otel_manager::OtelManager;
use frisk_core::policy_manager::PolicyManager;
use frisk_core::ProcessToolCallResult;
use once_cell::sync::OnceCell;
use opentelemetry::global;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyDict;
use serde_json::Value;
use std::sync::{Arc, Mutex};
use tokio::runtime::{Builder, Runtime};
use tracing_opentelemetry::OpenTelemetrySpanExt;

pub mod py_dict_carrier;

// todo: Map Rust exceptions to Python exceptions. https://linear.app/friskai/issue/POL-106/polish-map-rust-exceptions-to-pythonic-exceptions
// todo: config. https://linear.app/friskai/issue/POL-55/add-config-library-to-sdk
static POLICY_URL: &str = "http://localhost:3001/api/policies";
static POLICY_REFRESH_INTERVAL_SECONDS: u64 = 10;
static OTEL_MANAGER: OnceCell<Arc<OtelManager>> = OnceCell::new();
static TOKIO_RUNTIME: OnceCell<Arc<Runtime>> = OnceCell::new();

fn init_tokio_runtime_once() -> Arc<Runtime> {
    TOKIO_RUNTIME
        .get_or_init(|| {
            Arc::new(
                Builder::new_multi_thread()
                    .thread_name("frisk-tokio")
                    .enable_all()
                    .build()
                    .expect("Failed to build Tokio runtime"),
            )
        })
        .clone()
}

fn init_instrumentation_once(access_token: &str) {
    // ensure runtime exists before any tokio::spawn calls
    let _ = init_tokio_runtime_once();
    OTEL_MANAGER.get_or_init(|| {
        Arc::new(
            OtelManager::create_from_token(access_token).expect("Failed to initialize OtelManager"),
        )
    });
}

static POLICY_MANAGER: OnceCell<Arc<Mutex<PolicyManager>>> = OnceCell::new();
pub fn get_policy_manager(access_token: &str) -> &Arc<Mutex<PolicyManager>> {
    POLICY_MANAGER.get_or_init(|| {
        let arc = Arc::new(Mutex::new(PolicyManager::new(
            access_token.to_string(),
            POLICY_REFRESH_INTERVAL_SECONDS,
            POLICY_URL.into(),
        )));
        // start the refresh loop once at initialization time, synchronously within runtime context
        {
            let rt = init_tokio_runtime_once();
            let _guard = rt.enter();
            let mut guard = arc.lock().unwrap();
            guard.start();
        }
        arc
    })
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct ProcessToolCallResultPy {
    #[pyo3(get)]
    decision: String,
    #[pyo3(get)]
    rules_matched_count: usize,
    #[pyo3(get)]
    reason: Option<String>,
}

impl From<ProcessToolCallResult> for ProcessToolCallResultPy {
    fn from(r: ProcessToolCallResult) -> Self {
        match r {
            ProcessToolCallResult::Allow { rules_matched } => Self {
                decision: "allow".into(),
                rules_matched_count: rules_matched.len(),
                reason: None,
            },
            ProcessToolCallResult::Deny {
                rules_matched,
                reason,
            } => Self {
                decision: "deny".into(),
                rules_matched_count: rules_matched.len(),
                reason: Some(reason),
            },
        }
    }
}

#[pymethods]
impl ProcessToolCallResultPy {
    pub fn __repr__(&self) -> String {
        format!(
            "<ProcessToolCallResult decision='{}' matched={} reason={:?}>",
            self.decision, self.rules_matched_count, self.reason
        )
    }
}

#[pyfunction(name = "shutdown_instrumentation")]
pub fn shutdown_instrumentation_py() {
    if let Some(p) = OTEL_MANAGER.get() {
        p.shutdown()
    }
}

#[pyclass]
#[derive(Debug)]
pub struct FriskHandle {
    pub policy_engine: Arc<Mutex<PolicyEngine>>,
}

fn get_otel_manager() -> Arc<OtelManager> {
    OTEL_MANAGER
        .get()
        .expect("OtelManager not initialized")
        .clone()
}

#[pymethods]
impl FriskHandle {
    #[new]
    fn new(access_token: &str) -> PyResult<Self> {
        init_instrumentation_once(access_token);

        let otel_manager = get_otel_manager();
        let policy_manager_arc = get_policy_manager(access_token).clone();

        // Initialize policy engine with empty policies.
        // WARNING: There is a window before the first policy fetch completes during which
        // tool calls may be processed with no policies. This may result in unintended behavior.
        // The engine will be updated via subscription once policies are fetched.
        let policy_engine = Arc::new(Mutex::new(PolicyEngine::new(vec![], Some(otel_manager))));

        // subscribe to policy updates
        {
            let engine_handle = Arc::clone(&policy_engine);
            let pm_guard = policy_manager_arc.lock().unwrap();
            pm_guard
                .on_policy_update
                .subscribe(move |policies: &Vec<ToolPolicyRecord>| {
                    let mut engine = engine_handle.lock().unwrap();
                    engine.set_policies(policies.clone());
                });
        }

        Ok(Self { policy_engine })
    }

    pub fn update_access_token(&mut self, access_token: &str) -> PyResult<()> {
        let otel_manager = get_otel_manager();
        otel_manager
            .update_token(access_token)
            .map_err(|e| PyValueError::new_err(format!("{e}")))?;

        let policy_manager = POLICY_MANAGER.get().expect("PolicyManager not initialized");
        policy_manager
            .deref()
            .lock()
            .unwrap()
            .update_access_token(access_token);
        Ok(())
    }

    pub fn process<'py>(
        &self,
        _py: Python<'py>,
        tool_name: &str,
        tool_args_json: &str,
        agent_state_json: &str,
        tool_call_id: &str,
        trace_context_carrier: Option<Bound<'py, PyAny>>,
    ) -> PyResult<ProcessToolCallResultPy> {
        let tool_args_v: Value = serde_json::from_str(tool_args_json)
            .map_err(|e| PyValueError::new_err(format!("Invalid tool_args JSON: {e}")))?;
        let agent_state_v: Value = serde_json::from_str(agent_state_json)
            .map_err(|e| PyValueError::new_err(format!("Invalid agent_state JSON: {e}")))?;

        let context_dict: Option<Bound<'py, PyDict>> = trace_context_carrier
            .map(|obj| obj.cast_into::<PyDict>()) // try to cast to dict
            .transpose()?;

        let result = match context_dict {
            Some(trace_context_carrier_dict) => {
                let carrier = PyDictCarrier(&trace_context_carrier_dict);
                let parent_context =
                    global::get_text_map_propagator(|propagator| propagator.extract(&carrier));

                let span = tracing::info_span!(target: "policy_engine", "engine_process_tool_call");
                span.set_parent(parent_context);
                let _guard = span.enter();

                self.policy_engine.lock().unwrap().process_tool_call(
                    tool_name,
                    tool_call_id,
                    &tool_args_v,
                    &agent_state_v,
                )
            }
            None => self.policy_engine.lock().unwrap().process_tool_call(
                tool_name,
                tool_call_id,
                &tool_args_v,
                &agent_state_v,
            ),
        };

        match result {
            Ok(r) => Ok(r.into()),
            Err(e) => Err(PyValueError::new_err(format!(
                "Policy processing error: {e}"
            ))),
        }
    }
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FriskHandle>()?;
    m.add_class::<ProcessToolCallResultPy>()?;
    m.add_function(wrap_pyfunction!(shutdown_instrumentation_py, m)?)?;
    Ok(())
}
