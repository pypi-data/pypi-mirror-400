// This module handles conversion between Rust and Python types
// Currently handled in types.rs via from_rust() and into_rust() methods
// Can be expanded for more complex conversions if needed

use crate::types::PyMessage;
use pyo3::prelude::*;

/// Helper to convert messages to JSON string
#[allow(dead_code)]
pub fn messages_to_json(messages: &[PyMessage]) -> PyResult<String> {
    let rust_messages: Vec<chatpack::Message> =
        messages.iter().map(|m| m.clone().into_rust()).collect();

    serde_json::to_string_pretty(&rust_messages)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("JSON error: {}", e)))
}

/// Helper to convert messages to CSV string
#[allow(dead_code)]
pub fn messages_to_csv(messages: &[PyMessage]) -> PyResult<String> {
    use std::io::Cursor;

    let mut wtr = csv::Writer::from_writer(Cursor::new(Vec::new())); // Remove rust_messages conversion

    // let rust_messages: Vec<chatpack::Message> = messages
    //     .iter()
    //     .map(|m| m.clone().into_rust())
    //     .collect();

    // Write header
    wtr.write_record(["sender", "content", "timestamp", "platform"])
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("CSV error: {}", e)))?;

    // Write rows
    for msg in messages {
        wtr.write_record(&[
            msg.sender.clone(),
            msg.content.clone(),
            msg.timestamp.clone().unwrap_or_default(),
            msg.platform.clone().unwrap_or_default(),
        ])
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("CSV error: {}", e)))?;
    }

    let data = wtr
        .into_inner()
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("CSV error: {}", e)))?
        .into_inner();

    String::from_utf8(data)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("UTF-8 error: {}", e)))
}
