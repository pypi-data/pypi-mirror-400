mod api;
mod errors;
mod event;
mod json_utils;
mod match_utils;
mod otel;
mod policy_engine;
mod policy_loader;
mod policy_types;
mod regex_matcher;
mod try_utils;
mod value_utils;

use clap::Parser;
use policy_engine::PolicyEngine;
use policy_loader::load_from_file;
use serde_json::Value;
use std::fs;
use std::sync::Arc;

use crate::otel::otel_manager::OtelManager;
use crate::policy_types::ToolPolicyRecord;
use tracing::instrument;
use uuid::Uuid;

#[derive(Parser, Debug)]
#[command(name = "shango", about = "Policy engine CLI", version)]
struct Cli {
    /// Path to policies JSON file
    #[arg(short = 'p', long = "policies")]
    policies: String,
    /// Path to input JSON file containing tool_name, tool_args, agent_state
    #[arg(short = 'i', long = "input")]
    input: String,
    /// Company ID (optional override, defaults to cli_company_id)
    #[arg(short = 'c', long = "company", default_value = "cli_company_id")]
    company_id: String,
    /// Bearer token for OTLP exporter authentication (defaults to example_bearer_token)
    #[arg(short = 't', long = "token", default_value = "example_bearer_token")]
    token: String,
}

#[instrument]
fn run_cli(args: Cli, otel_manager: Arc<OtelManager>) -> Result<(), String> {
    let policies =
        load_from_file(&args.policies).map_err(|e| format!("Failed to load policies: {e}"))?;

    // Wrap raw ToolPolicy list into records with minimal metadata
    let policy_records: Vec<ToolPolicyRecord> = policies
        .into_iter()
        .enumerate()
        .map(|(i, p)| ToolPolicyRecord {
            id: format!("rec-{}", i),
            name: format!("policy-{}", p.tool_name),
            current_version_id: "v1".into(),
            policy: p,
        })
        .collect();

    let policy_engine = PolicyEngine::new(policy_records, Some(otel_manager));

    let input_raw =
        fs::read_to_string(&args.input).map_err(|e| format!("Failed to read input file: {e}"))?;
    let input_json: Value =
        serde_json::from_str(&input_raw).map_err(|e| format!("Failed to parse input JSON: {e}"))?;

    let tool_name = input_json
        .get("tool_name")
        .and_then(Value::as_str)
        .ok_or("Missing tool_name (string) in input JSON")?;
    let tool_args = input_json
        .get("tool_args")
        .ok_or("Missing tool_args object in input JSON")?;
    let agent_state = input_json
        .get("agent_state")
        .ok_or("Missing agent_state object in input JSON")?;

    let tool_call_id = Uuid::new_v4(); // todo

    let action = policy_engine
        .process_tool_call(tool_name, &tool_call_id.to_string(), tool_args, agent_state)
        .map_err(|e| format!("Policy evaluation error: {e}"))?;

    let output = match action {
        policy_engine::ProcessToolCallResult::Allow { rules_matched } => serde_json::json!({
            "result": "allow",
            "matched_rules": rules_matched.len()
        }),
        policy_engine::ProcessToolCallResult::Deny {
            rules_matched,
            reason,
        } => serde_json::json!({
            "result": "deny",
            "reason": reason,
            "matched_rules": rules_matched.len()
        }),
    };

    println!("{}", serde_json::to_string_pretty(&output).unwrap());
    Ok(())
}

#[tokio::main]
async fn main() {
    let args = Cli::parse();

    let otel_manager = Arc::new(
        OtelManager::create_from_token(&args.token).expect("Failed to create OtelManager"),
    );

    let result = run_cli(args, otel_manager.clone());

    // 🔴 ALWAYS FLUSH BEFORE EXITING
    otel_manager.shutdown();

    if let Err(e) = result {
        eprintln!("Error: {e}");
        std::process::exit(1);
    }
}
