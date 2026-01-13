use crate::regex::{GPT4_SPLIT_PATTERN, parse_pattern};
use crate::tokenizer::{
    MIN_VOCAB_SIZE, VocabSizeTooSmall, get_pair_counts, parse_merges, string_to_token_ids, train_bpe,
    verify_stok_extension,
};
use crate::{
    Deserializable, ParallelRegexBPETokenizer, RegexBPETokenizerConfigError, RegexCompilationError, TokenId, Trainable,
    regex,
};
use fancy_regex::Regex;
use rayon::prelude::*;
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader, Error};
use std::path::Path;

/// Configuration for training a regex-based BPE tokenizer in parallel with rayon.
///
/// This struct implements [`Trainable`] and produces a [`ParallelRegexBPETokenizer`].
#[derive(Debug)]
pub struct ParallelRegexBPETokenizerConfig {
    vocab_size: u32,
    pattern: String,
    compiled_pattern: Regex,
}

impl ParallelRegexBPETokenizerConfig {
    /// Create a new configuration for training a regex BPE tokenizer.
    ///
    /// # Arguments
    ///
    /// * `vocab_size` - The desired vocabulary size (must be at least 256).
    /// * `pattern` - Optional custom regex pattern. If `None`, uses the GPT-4 split pattern.
    ///
    /// # Returns
    ///
    /// * `Ok(RegexBPETokenizerConfig)` if configuration is valid.
    /// * `Err(RegexBPETokenizerConfigError)` if vocab size is too small or pattern is invalid.
    pub fn build(vocab_size: u32, pattern: Option<&str>) -> Result<Self, RegexBPETokenizerConfigError> {
        VocabSizeTooSmall::check(vocab_size)?;

        let pattern = pattern.unwrap_or(GPT4_SPLIT_PATTERN).to_string();
        let compiled_pattern = Regex::new(pattern.as_str()).map_err(|e| RegexCompilationError(e.to_string()))?;

        Ok(ParallelRegexBPETokenizerConfig {
            vocab_size,
            pattern,
            compiled_pattern,
        })
    }

    /// Create a new configuration from the number of merges instead of vocab size.
    ///
    /// # Arguments
    ///
    /// * `merges` - The number of merge operations to perform.
    /// * `pattern` - Optional custom regex pattern.
    pub fn from_merges(merges: u32, pattern: Option<&str>) -> Result<Self, RegexBPETokenizerConfigError> {
        Self::build(MIN_VOCAB_SIZE + merges, pattern)
    }
}

impl Trainable for ParallelRegexBPETokenizerConfig {
    type Output = ParallelRegexBPETokenizer;
    type TrainingError = std::convert::Infallible;

    fn train(&self, dataset: &str) -> Result<ParallelRegexBPETokenizer, Self::TrainingError> {
        let dataset_chunks = regex::split_text(dataset, &self.compiled_pattern);

        let mut chunks_tokens: Vec<Vec<TokenId>> =
            dataset_chunks.iter().map(|chunk| string_to_token_ids(chunk)).collect();

        let n_iterations = self.vocab_size - MIN_VOCAB_SIZE;
        let merges = train_bpe(&mut chunks_tokens, n_iterations, |chunks| {
            // parallel counting with rayon
            chunks
                .par_iter()
                .fold(HashMap::new, |mut thread_map, tokens| {
                    get_pair_counts(tokens.as_slice(), &mut thread_map);
                    thread_map
                })
                .reduce(HashMap::new, |mut combined, thread_map| {
                    for (pair, count) in thread_map {
                        *combined.entry(pair).or_insert(0) += count;
                    }
                    combined
                })
        });

        Ok(ParallelRegexBPETokenizer::new(merges, self.pattern.clone()))
    }
}

impl Deserializable for ParallelRegexBPETokenizerConfig {
    type Output = ParallelRegexBPETokenizer;

    /// Loads a ParallelRegexBPETokenizer from a file.
    ///
    /// The file must contain a header line with the regex pattern,
    /// followed by merge rules (one per line).
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the tokenizer from. Must have a `.stok` extension.
    ///
    /// # Returns
    ///
    /// * `Ok(ParallelRegexBPETokenizer)` if the tokenizer was loaded successfully.
    /// * `Err(std::io::Error)` if the file extension is invalid, reading fails,
    ///   or the file format is invalid.
    fn load(&self, path: &Path) -> Result<Self::Output, Error> {
        verify_stok_extension(path)?;

        let file = File::open(path)?;
        let reader = BufReader::new(file);
        let mut lines = reader.lines();

        let first_line = lines
            .next()
            .ok_or_else(|| Error::new(std::io::ErrorKind::InvalidData, "File is empty"))??;

        let pattern = parse_pattern(first_line)?;
        // + 1 for pattern line
        let merges = parse_merges(lines.enumerate().map(|(i, line)| (i + 2, line)))?;

        Ok(ParallelRegexBPETokenizer::new(merges, pattern))
    }
}
