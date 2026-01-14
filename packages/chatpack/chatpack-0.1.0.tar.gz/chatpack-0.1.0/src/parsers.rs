#![allow(clippy::useless_conversion)]
use crate::types::PyMessage;
use chatpack::parser::Parser;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::path::Path;

// Helper function to create filter config from parameters
fn build_filter_config(
    _min_length: Option<usize>, // Не используем здесь, фильтруем вручную
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<chatpack::core::filter::FilterConfig> {
    let mut config = chatpack::core::filter::FilterConfig::new();

    if let Some(date) = date_from {
        config = config
            .with_date_from(&date)
            .map_err(|e| PyValueError::new_err(format!("Invalid start date: {}", e)))?;
    }

    if let Some(date) = date_to {
        config = config
            .with_date_to(&date)
            .map_err(|e| PyValueError::new_err(format!("Invalid end date: {}", e)))?;
    }

    Ok(config)
}

// Helper: ручная фильтрация длины
fn filter_by_length(
    messages: Vec<chatpack::Message>,
    min_length: Option<usize>,
) -> Vec<chatpack::Message> {
    if let Some(min) = min_length {
        messages
            .into_iter()
            .filter(|m| m.content.chars().count() >= min)
            .collect()
    } else {
        messages
    }
}

// Helper function to apply merge if needed
fn maybe_merge(messages: Vec<chatpack::Message>, merge: bool) -> Vec<chatpack::Message> {
    if merge {
        chatpack::prelude::merge_consecutive(messages)
    } else {
        messages
    }
}

pub fn parse_telegram_impl(
    path: String,
    merge: bool,
    min_length: Option<usize>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<Vec<PyMessage>> {
    let parser = chatpack::parsers::TelegramParser::new();

    let messages = parser
        .parse(Path::new(&path))
        .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

    let filter_config = build_filter_config(min_length, date_from, date_to)?;
    let filtered_by_config = chatpack::core::filter::apply_filters(messages, &filter_config);
    let filtered = filter_by_length(filtered_by_config, min_length);

    let result = maybe_merge(filtered, merge);

    Ok(result.into_iter().map(PyMessage::from_rust).collect())
}

pub fn parse_whatsapp_impl(
    path: String,
    merge: bool,
    min_length: Option<usize>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<Vec<PyMessage>> {
    let parser = chatpack::parsers::WhatsAppParser::new();

    let messages = parser
        .parse(Path::new(&path))
        .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

    let filter_config = build_filter_config(min_length, date_from, date_to)?;
    let filtered_by_config = chatpack::core::filter::apply_filters(messages, &filter_config);
    let filtered = filter_by_length(filtered_by_config, min_length);

    let result = maybe_merge(filtered, merge);

    Ok(result.into_iter().map(PyMessage::from_rust).collect())
}

pub fn parse_instagram_impl(
    path: String,
    merge: bool,
    min_length: Option<usize>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<Vec<PyMessage>> {
    let parser = chatpack::parsers::InstagramParser::new();

    let messages = parser
        .parse(Path::new(&path))
        .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

    let filter_config = build_filter_config(min_length, date_from, date_to)?;
    let filtered_by_config = chatpack::core::filter::apply_filters(messages, &filter_config);
    let filtered = filter_by_length(filtered_by_config, min_length);

    let result = maybe_merge(filtered, merge);

    Ok(result.into_iter().map(PyMessage::from_rust).collect())
}

pub fn parse_discord_impl(
    path: String,
    merge: bool,
    min_length: Option<usize>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<Vec<PyMessage>> {
    let parser = chatpack::parsers::DiscordParser::new();

    let messages = parser
        .parse(Path::new(&path))
        .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

    let filter_config = build_filter_config(min_length, date_from, date_to)?;
    let filtered_by_config = chatpack::core::filter::apply_filters(messages, &filter_config);
    let filtered = filter_by_length(filtered_by_config, min_length);

    let result = maybe_merge(filtered, merge);

    Ok(result.into_iter().map(PyMessage::from_rust).collect())
}

/// Telegram Parser class
#[pyclass]
pub struct TelegramParser {
    parser: chatpack::parsers::TelegramParser,
}

#[pymethods]
impl TelegramParser {
    #[new]
    fn new() -> Self {
        TelegramParser {
            parser: chatpack::parsers::TelegramParser::new(),
        }
    }

    #[pyo3(signature = (path, merge=false, min_length=None, date_from=None, date_to=None))]
    fn parse(
        &self,
        path: String,
        merge: bool,
        min_length: Option<usize>,
        date_from: Option<String>,
        date_to: Option<String>,
    ) -> PyResult<Vec<PyMessage>> {
        parse_telegram_impl(path, merge, min_length, date_from, date_to)
    }

    fn parse_str(&self, content: String) -> PyResult<Vec<PyMessage>> {
        let messages = self
            .parser
            .parse_str(&content)
            .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

        Ok(messages.into_iter().map(PyMessage::from_rust).collect())
    }
}

/// WhatsApp Parser class
#[pyclass]
pub struct WhatsAppParser {
    parser: chatpack::parsers::WhatsAppParser,
}

#[pymethods]
impl WhatsAppParser {
    #[new]
    fn new() -> Self {
        WhatsAppParser {
            parser: chatpack::parsers::WhatsAppParser::new(),
        }
    }

    #[pyo3(signature = (path, merge=false, min_length=None, date_from=None, date_to=None))]
    fn parse(
        &self,
        path: String,
        merge: bool,
        min_length: Option<usize>,
        date_from: Option<String>,
        date_to: Option<String>,
    ) -> PyResult<Vec<PyMessage>> {
        parse_whatsapp_impl(path, merge, min_length, date_from, date_to)
    }

    fn parse_str(&self, content: String) -> PyResult<Vec<PyMessage>> {
        let messages = self
            .parser
            .parse_str(&content)
            .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

        Ok(messages.into_iter().map(PyMessage::from_rust).collect())
    }
}

/// Instagram Parser class
#[pyclass]
pub struct InstagramParser {
    parser: chatpack::parsers::InstagramParser,
}

#[pymethods]
impl InstagramParser {
    #[new]
    fn new() -> Self {
        InstagramParser {
            parser: chatpack::parsers::InstagramParser::new(),
        }
    }

    #[pyo3(signature = (path, merge=false, min_length=None, date_from=None, date_to=None))]
    fn parse(
        &self,
        path: String,
        merge: bool,
        min_length: Option<usize>,
        date_from: Option<String>,
        date_to: Option<String>,
    ) -> PyResult<Vec<PyMessage>> {
        parse_instagram_impl(path, merge, min_length, date_from, date_to)
    }

    fn parse_str(&self, content: String) -> PyResult<Vec<PyMessage>> {
        let messages = self
            .parser
            .parse_str(&content)
            .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

        Ok(messages.into_iter().map(PyMessage::from_rust).collect())
    }
}

/// Discord Parser class
#[pyclass]
pub struct DiscordParser {
    parser: chatpack::parsers::DiscordParser,
}

#[pymethods]
impl DiscordParser {
    #[new]
    fn new() -> Self {
        DiscordParser {
            parser: chatpack::parsers::DiscordParser::new(),
        }
    }

    #[pyo3(signature = (path, merge=false, min_length=None, date_from=None, date_to=None))]
    fn parse(
        &self,
        path: String,
        merge: bool,
        min_length: Option<usize>,
        date_from: Option<String>,
        date_to: Option<String>,
    ) -> PyResult<Vec<PyMessage>> {
        parse_discord_impl(path, merge, min_length, date_from, date_to)
    }

    fn parse_str(&self, content: String) -> PyResult<Vec<PyMessage>> {
        let messages = self
            .parser
            .parse_str(&content)
            .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

        Ok(messages.into_iter().map(PyMessage::from_rust).collect())
    }
}
