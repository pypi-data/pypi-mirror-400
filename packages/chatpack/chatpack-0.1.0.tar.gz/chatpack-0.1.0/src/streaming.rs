use crate::types::PyMessage;
use chatpack::streaming::{
    DiscordStreamingParser, InstagramStreamingParser, StreamingParser, TelegramStreamingParser,
    WhatsAppStreamingParser,
};
use pyo3::exceptions::{PyStopIteration, PyValueError};
use pyo3::prelude::*;

// Универсальный итератор для Python
#[pyclass]
struct StreamIterator {
    // Храним итератор как Box<dyn ...>
    iter: Box<dyn chatpack::streaming::MessageIterator>,
}

#[pymethods]
impl StreamIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> PyResult<Option<PyMessage>> {
        match slf.iter.next() {
            Some(Ok(msg)) => Ok(Some(PyMessage::from_rust(msg))),
            Some(Err(e)) => Err(PyValueError::new_err(format!("Streaming error: {}", e))),
            None => Err(PyStopIteration::new_err("End of stream")),
        }
    }
}

// --- Telegram ---

#[pyclass]
pub struct TelegramStreamParser {
    path: String,
}

#[pymethods]
impl TelegramStreamParser {
    #[new]
    fn new(path: String) -> Self {
        TelegramStreamParser { path }
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<StreamIterator> {
        let parser = TelegramStreamingParser::new();
        // Исправление: передаем строку напрямую, без Path::new
        let stream = parser
            .stream(&slf.path)
            .map_err(|e| PyValueError::new_err(format!("Failed to start stream: {}", e)))?;

        Ok(StreamIterator {
            iter: stream, // Исправление: stream уже является Box, не нужно Box::new
        })
    }
}

// --- WhatsApp ---

#[pyclass]
pub struct WhatsAppStreamParser {
    path: String,
}

#[pymethods]
impl WhatsAppStreamParser {
    #[new]
    fn new(path: String) -> Self {
        WhatsAppStreamParser { path }
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<StreamIterator> {
        let parser = WhatsAppStreamingParser::new();
        let stream = parser
            .stream(&slf.path)
            .map_err(|e| PyValueError::new_err(format!("Failed to start stream: {}", e)))?;

        Ok(StreamIterator { iter: stream })
    }
}

// --- Instagram ---

#[pyclass]
pub struct InstagramStreamParser {
    path: String,
}

#[pymethods]
impl InstagramStreamParser {
    #[new]
    fn new(path: String) -> Self {
        InstagramStreamParser { path }
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<StreamIterator> {
        let parser = InstagramStreamingParser::new();
        let stream = parser
            .stream(&slf.path)
            .map_err(|e| PyValueError::new_err(format!("Failed to start stream: {}", e)))?;

        Ok(StreamIterator { iter: stream })
    }
}

// --- Discord ---

#[pyclass]
pub struct DiscordStreamParser {
    path: String,
}

#[pymethods]
impl DiscordStreamParser {
    #[new]
    fn new(path: String) -> Self {
        DiscordStreamParser { path }
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<StreamIterator> {
        let parser = DiscordStreamingParser::new();
        let stream = parser
            .stream(&slf.path)
            .map_err(|e| PyValueError::new_err(format!("Failed to start stream: {}", e)))?;

        Ok(StreamIterator { iter: stream })
    }
}
