//! # smoltok-core
//!
//! Core library for `smoltok`, providing BPE (Byte Pair Encoding) tokenization functionality.
//! This crate defines the Tokenizer trait and implements simple and regex-based BPE tokenizers.

pub mod regex;
pub mod simple;
pub mod tokenizer;

pub use regex::{
    GPT4_SPLIT_PATTERN, ParallelRegexBPETokenizer, ParallelRegexBPETokenizerConfig, RegexBPETokenizer,
    RegexBPETokenizerConfig, RegexBPETokenizerConfigError, RegexCompilationError,
};
pub use simple::{SimpleBPETokenizer, SimpleBPETokenizerConfig};
pub use tokenizer::{Deserializable, MergeRule, Serializable, TokenId, TokenPair, Tokenizer, Trainable};
