//! Regex-based BPE tokenizer with support for special tokens.
//!
//! This module provides a more advanced BPE tokenizer that uses regex patterns to split text
//! into chunks before applying BPE.
//! This is similar to the approach used by GPT-4 and other modern LLMs.

use fancy_regex::Regex;
use std::fs::File;
use std::io::{BufWriter, Error, Write};
use std::path::Path;

mod config;
mod config_parallel;
mod errors;
mod tokenizer;
mod tokenizer_parallel;

use crate::MergeRule;
use crate::tokenizer::{save_merges, verify_stok_extension};
pub use config::RegexBPETokenizerConfig;
pub use config_parallel::ParallelRegexBPETokenizerConfig;
pub use errors::{RegexBPETokenizerConfigError, RegexCompilationError};
pub use tokenizer::RegexBPETokenizer;
pub use tokenizer_parallel::ParallelRegexBPETokenizer;

pub const GPT4_SPLIT_PATTERN: &str =
    r"'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+";

/// Split text into chunks using the compiled regex pattern.
pub fn split_text(text: &str, pattern: &Regex) -> Vec<String> {
    let mut chunks = Vec::new();
    for m in pattern.find_iter(text).flatten() {
        chunks.push(m.as_str().to_string()); // todo: could avoid to_string?
    }
    chunks
}

/// File format header prefix for regex tokenizer pattern.
pub const PATTERN_HEADER_PREFIX: &str = "#pattern:";

pub fn parse_pattern(line: String) -> Result<String, Error> {
    if let Some(pattern_str) = line.strip_prefix(PATTERN_HEADER_PREFIX) {
        Ok(pattern_str.to_string())
    } else {
        Err(Error::new(
            std::io::ErrorKind::InvalidData,
            format!(
                "Expected pattern header starting with '{}', got: {}",
                PATTERN_HEADER_PREFIX, line
            ),
        ))
    }
}

/// Saves the regex tokenizer's pattern and merge rules to a file.
///
/// # Arguments
///
/// * `path` - The path to save the tokenizer. Must have a `.stok` extension.
///
/// # Returns
///
/// * `Ok(())` if the tokenizer was saved successfully.
/// * `Err(std::io::Error)` if the file extension is invalid or writing fails.
pub fn save_regex_tokenizer(path: &Path, pattern: &str, merges: &[MergeRule]) -> Result<(), Error> {
    verify_stok_extension(path)?;

    let file = File::create(path)?;
    let mut writer = BufWriter::new(file);

    writeln!(writer, "{}{}", PATTERN_HEADER_PREFIX, pattern)?;

    save_merges(&mut writer, merges)?;

    writer.flush()?;

    Ok(())
}
