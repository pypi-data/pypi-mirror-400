//! Simple BPE tokenizer without regex patterns or special tokens.
//!
//! This module provides a basic BPE tokenizer that operates directly on raw bytes.
//! It does not split text using regex patterns and does not support special tokens.

mod config;
mod tokenizer;

pub use config::SimpleBPETokenizerConfig;
pub use tokenizer::SimpleBPETokenizer;
