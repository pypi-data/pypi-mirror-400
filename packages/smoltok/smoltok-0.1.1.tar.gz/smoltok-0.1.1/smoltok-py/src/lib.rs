//! Python bindings for the smoltok BPE tokenizer.
//!
//! This module exposes the Rust BPE tokenizer to Python via PyO3.

use pyo3::prelude::*;
use smoltok_core::tokenizer::{Deserializable, Serializable};
use smoltok_core::{
    ParallelRegexBPETokenizer, ParallelRegexBPETokenizerConfig, RegexBPETokenizer, RegexBPETokenizerConfig,
    SimpleBPETokenizer, SimpleBPETokenizerConfig, TokenId, Tokenizer, Trainable,
};
use std::collections::HashMap;
use std::path::Path;

/// Configuration for training a simple BPE tokenizer.
#[pyclass(name = "SimpleBPETokenizerConfig")]
struct PySimpleBPETokenizerConfig {
    inner: SimpleBPETokenizerConfig,
}

#[pymethods]
impl PySimpleBPETokenizerConfig {
    #[staticmethod]
    fn build(vocab_size: u32) -> PyResult<Self> {
        SimpleBPETokenizerConfig::build(vocab_size)
            .map(|config| Self { inner: config })
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    #[staticmethod]
    fn from_merges(merges: u32) -> Self {
        Self {
            inner: SimpleBPETokenizerConfig::from_merges(merges),
        }
    }

    fn train(&self, dataset: &str) -> PySimpleBPETokenizer {
        PySimpleBPETokenizer {
            inner: self.inner.train(dataset).unwrap(),
        }
    }

    fn load(&self, path: &str) -> PyResult<PySimpleBPETokenizer> {
        self.inner
            .load(Path::new(path))
            .map(|tokenizer| PySimpleBPETokenizer { inner: tokenizer })
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))
    }
}

/// Simple BPE tokenizer. Does not support regex patterns and special tokens.
#[pyclass(name = "SimpleBPETokenizer")]
struct PySimpleBPETokenizer {
    inner: SimpleBPETokenizer,
}

#[pymethods]
impl PySimpleBPETokenizer {
    #[getter]
    fn num_merges(&self) -> usize {
        self.inner.num_merges()
    }

    fn encode(&self, data: &str) -> Vec<u32> {
        self.inner.encode(data).into_iter().map(|x| x.value()).collect()
    }

    fn decode(&self, tokens: Vec<u32>) -> PyResult<String> {
        let token_ids: Vec<TokenId> = tokens.into_iter().map(TokenId::new).collect();
        self.inner
            .decode(token_ids.as_slice())
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    fn save(&self, path: &str) -> PyResult<()> {
        self.inner
            .save(Path::new(path))
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))
    }
}

/// Configuration for training a regex-based BPE tokenizer.
#[pyclass(name = "RegexBPETokenizerConfig")]
struct PyRegexBPETokenizerConfig {
    inner: RegexBPETokenizerConfig,
}

#[pymethods]
impl PyRegexBPETokenizerConfig {
    #[staticmethod]
    #[pyo3(signature = (vocab_size, pattern = None))]
    fn build(vocab_size: u32, pattern: Option<&str>) -> PyResult<Self> {
        RegexBPETokenizerConfig::build(vocab_size, pattern)
            .map(|config| Self { inner: config })
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    #[staticmethod]
    #[pyo3(signature = (merges, pattern = None))]
    fn from_merges(merges: u32, pattern: Option<&str>) -> PyResult<Self> {
        RegexBPETokenizerConfig::from_merges(merges, pattern)
            .map(|config| Self { inner: config })
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    fn train(&self, dataset: &str) -> PyRegexBPETokenizer {
        PyRegexBPETokenizer {
            inner: self.inner.train(dataset).unwrap(),
        }
    }

    fn load(&self, path: &str) -> PyResult<PyRegexBPETokenizer> {
        self.inner
            .load(Path::new(path))
            .map(|tokenizer| PyRegexBPETokenizer { inner: tokenizer })
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))
    }
}

/// Regex-based BPE tokenizer with support for regex patterns and special tokens.
#[pyclass(name = "RegexBPETokenizer")]
struct PyRegexBPETokenizer {
    inner: RegexBPETokenizer,
}

#[pymethods]
impl PyRegexBPETokenizer {
    #[getter]
    fn num_merges(&self) -> usize {
        self.inner.num_merges()
    }

    #[getter]
    fn vocab_size(&self) -> usize {
        self.inner.vocab_size()
    }

    #[getter]
    fn pattern(&self) -> &str {
        self.inner.pattern()
    }

    fn register_special_tokens(&mut self, special_tokens: HashMap<String, u32>) {
        let tokens: HashMap<String, TokenId> = special_tokens.into_iter().map(|(k, v)| (k, TokenId::new(v))).collect();
        self.inner.register_special_tokens(tokens);
    }

    fn encode(&self, data: &str) -> Vec<u32> {
        self.inner.encode(data).into_iter().map(|x| x.value()).collect()
    }

    fn decode(&self, tokens: Vec<u32>) -> PyResult<String> {
        let token_ids: Vec<TokenId> = tokens.into_iter().map(TokenId::new).collect();
        self.inner
            .decode(token_ids.as_slice())
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    fn save(&self, path: &str) -> PyResult<()> {
        self.inner
            .save(Path::new(path))
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))
    }
}

/// Configuration for training a regex-based BPE tokenizer with parallel training.
///
/// Uses rayon for parallel pair counting during training, which is faster
/// for large datasets while producing the same tokenizer as RegexBPETokenizerConfig.
#[pyclass(name = "ParallelRegexBPETokenizerConfig")]
struct PyParallelRegexBPETokenizerConfig {
    inner: ParallelRegexBPETokenizerConfig,
}

#[pymethods]
impl PyParallelRegexBPETokenizerConfig {
    #[staticmethod]
    #[pyo3(signature = (vocab_size, pattern = None))]
    fn build(vocab_size: u32, pattern: Option<&str>) -> PyResult<Self> {
        ParallelRegexBPETokenizerConfig::build(vocab_size, pattern)
            .map(|config| Self { inner: config })
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    #[staticmethod]
    #[pyo3(signature = (merges, pattern = None))]
    fn from_merges(merges: u32, pattern: Option<&str>) -> PyResult<Self> {
        ParallelRegexBPETokenizerConfig::from_merges(merges, pattern)
            .map(|config| Self { inner: config })
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    fn train(&self, dataset: &str) -> PyParallelRegexBPETokenizer {
        PyParallelRegexBPETokenizer {
            inner: self.inner.train(dataset).unwrap(),
        }
    }

    fn load(&self, path: &str) -> PyResult<PyParallelRegexBPETokenizer> {
        self.inner
            .load(Path::new(path))
            .map(|tokenizer| PyParallelRegexBPETokenizer { inner: tokenizer })
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))
    }
}

/// Parallel regex-based BPE tokenizer with support for regex patterns and special tokens.
#[pyclass(name = "ParallelRegexBPETokenizer")]
struct PyParallelRegexBPETokenizer {
    inner: ParallelRegexBPETokenizer,
}

#[pymethods]
impl PyParallelRegexBPETokenizer {
    #[getter]
    fn num_merges(&self) -> usize {
        self.inner.num_merges()
    }

    #[getter]
    fn vocab_size(&self) -> usize {
        self.inner.vocab_size()
    }

    #[getter]
    fn pattern(&self) -> &str {
        self.inner.pattern()
    }

    fn register_special_tokens(&mut self, special_tokens: HashMap<String, u32>) {
        let tokens: HashMap<String, TokenId> = special_tokens.into_iter().map(|(k, v)| (k, TokenId::new(v))).collect();
        self.inner.register_special_tokens(tokens);
    }

    fn encode(&self, data: &str) -> Vec<u32> {
        self.inner.encode(data).into_iter().map(|x| x.value()).collect()
    }

    fn decode(&self, tokens: Vec<u32>) -> PyResult<String> {
        let token_ids: Vec<TokenId> = tokens.into_iter().map(TokenId::new).collect();
        self.inner
            .decode(token_ids.as_slice())
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    fn save(&self, path: &str) -> PyResult<()> {
        self.inner
            .save(Path::new(path))
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))
    }
}

/// smoltok: BPE tokenizer implemented in Rust.
#[pymodule]
fn smoltok(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PySimpleBPETokenizerConfig>()?;
    m.add_class::<PySimpleBPETokenizer>()?;
    m.add_class::<PyRegexBPETokenizerConfig>()?;
    m.add_class::<PyRegexBPETokenizer>()?;
    m.add_class::<PyParallelRegexBPETokenizerConfig>()?;
    m.add_class::<PyParallelRegexBPETokenizer>()?;
    Ok(())
}
