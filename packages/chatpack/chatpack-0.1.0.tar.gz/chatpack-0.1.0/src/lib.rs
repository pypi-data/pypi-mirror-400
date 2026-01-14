#![allow(clippy::useless_conversion)]
use pyo3::prelude::*;

mod conversion;
mod parsers;
mod streaming; // <-- Добавляем модуль
mod types;

use parsers::*;
use streaming::*; // <-- Используем модуль
use types::*;

#[pymodule]
fn _chatpack(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register types
    m.add_class::<PyMessage>()?;
    m.add_class::<PyFilterConfig>()?;
    m.add_class::<PyOutputConfig>()?;

    // Register parsers
    m.add_class::<TelegramParser>()?;
    m.add_class::<WhatsAppParser>()?;
    m.add_class::<InstagramParser>()?;
    m.add_class::<DiscordParser>()?;

    // Register streaming parsers (Теперь они есть!)
    m.add_class::<TelegramStreamParser>()?;
    m.add_class::<WhatsAppStreamParser>()?;
    m.add_class::<InstagramStreamParser>()?;
    m.add_class::<DiscordStreamParser>()?;

    // Convenience functions
    m.add_function(wrap_pyfunction!(parse_telegram, m)?)?;
    m.add_function(wrap_pyfunction!(parse_whatsapp, m)?)?;
    m.add_function(wrap_pyfunction!(parse_instagram, m)?)?;
    m.add_function(wrap_pyfunction!(parse_discord, m)?)?;

    // Utility functions
    m.add_function(wrap_pyfunction!(merge_consecutive, m)?)?;
    m.add_function(wrap_pyfunction!(apply_filters, m)?)?;

    Ok(())
}

// ... Функции parse_telegram и другие из parsers.rs подключаются через use parsers::*;
// НО нам нужно экспортировать их как pyfunction здесь.
// Копируем сигнатуры из предыдущего lib.rs, но ссылаемся на parsers::impl

#[pyfunction]
#[pyo3(signature = (path, merge=false, min_length=None, date_from=None, date_to=None))]
fn parse_telegram(
    path: String,
    merge: bool,
    min_length: Option<usize>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<Vec<PyMessage>> {
    parsers::parse_telegram_impl(path, merge, min_length, date_from, date_to)
}

#[pyfunction]
#[pyo3(signature = (path, merge=false, min_length=None, date_from=None, date_to=None))]
fn parse_whatsapp(
    path: String,
    merge: bool,
    min_length: Option<usize>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<Vec<PyMessage>> {
    parsers::parse_whatsapp_impl(path, merge, min_length, date_from, date_to)
}

#[pyfunction]
#[pyo3(signature = (path, merge=false, min_length=None, date_from=None, date_to=None))]
fn parse_instagram(
    path: String,
    merge: bool,
    min_length: Option<usize>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<Vec<PyMessage>> {
    parsers::parse_instagram_impl(path, merge, min_length, date_from, date_to)
}

#[pyfunction]
#[pyo3(signature = (path, merge=false, min_length=None, date_from=None, date_to=None))]
fn parse_discord(
    path: String,
    merge: bool,
    min_length: Option<usize>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> PyResult<Vec<PyMessage>> {
    parsers::parse_discord_impl(path, merge, min_length, date_from, date_to)
}

/// Merge consecutive messages
#[pyfunction]
#[pyo3(signature = (messages, _time_threshold=300))] // time_threshold игнорируется в chatpack 0.5 (дефолт)
fn merge_consecutive(messages: Vec<PyMessage>, _time_threshold: i64) -> PyResult<Vec<PyMessage>> {
    // Конвертируем PyMessage -> chatpack::Message
    let rust_messages: Vec<chatpack::Message> =
        messages.into_iter().map(|m| m.into_rust()).collect();

    // Вызываем реальную функцию!
    let merged = chatpack::prelude::merge_consecutive(rust_messages);

    // Конвертируем обратно
    Ok(merged.into_iter().map(PyMessage::from_rust).collect())
}

/// Apply filters to messages
#[pyfunction]
fn apply_filters(messages: Vec<PyMessage>, config: PyFilterConfig) -> PyResult<Vec<PyMessage>> {
    // 1. Конвертируем сообщения в Rust
    let rust_messages: Vec<chatpack::Message> =
        messages.into_iter().map(|m| m.into_rust()).collect();

    // 2. Получаем конфиг (он отфильтрует даты и отправителя)
    let rust_config = config.clone().into_rust()?; // clone нужен т.к. нам еще нужен min_length
    let filtered_base = chatpack::core::filter::apply_filters(rust_messages, &rust_config);

    // 3. Ручная фильтрация длины (т.к. метод в либе может отсутствовать)
    let final_filtered = if let Some(min_len) = config.min_length {
        filtered_base
            .into_iter()
            .filter(|m| m.content.chars().count() >= min_len)
            .collect()
    } else {
        filtered_base
    };

    // 4. Возвращаем в Python
    Ok(final_filtered
        .into_iter()
        .map(PyMessage::from_rust)
        .collect())
}
