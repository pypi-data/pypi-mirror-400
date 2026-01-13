//! Configuration for the simple BPE tokenizer.

use super::SimpleBPETokenizer;
use crate::Deserializable;
use crate::tokenizer::{
    MIN_VOCAB_SIZE, MergeRule, TokenId, Trainable, VocabSizeTooSmall, get_most_common_pair, get_pair_counts, merge,
    parse_merges, string_to_token_ids, verify_stok_extension,
};
use std::collections::HashMap;
use std::convert::Infallible;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

/// Configuration for training a simple BPE tokenizer.
///
/// This struct implements [`Trainable`] and produces a [`SimpleBPETokenizer`].
#[derive(Debug)]
pub struct SimpleBPETokenizerConfig {
    vocab_size: u32,
}

impl SimpleBPETokenizerConfig {
    /// Create a new configuration for training a simple BPE tokenizer from vocab size.
    pub fn build(vocab_size: u32) -> Result<Self, VocabSizeTooSmall> {
        VocabSizeTooSmall::check(vocab_size)?;
        Ok(SimpleBPETokenizerConfig { vocab_size })
    }

    /// Create a new configuration for training a simple BPE tokenizer from number of merges.
    pub fn from_merges(merges: u32) -> Self {
        Self::build(MIN_VOCAB_SIZE + merges).unwrap()
    }
}

impl Trainable for SimpleBPETokenizerConfig {
    type Output = SimpleBPETokenizer;
    type TrainingError = Infallible;

    fn train(&self, dataset: &str) -> Result<SimpleBPETokenizer, Infallible> {
        let mut tokens = string_to_token_ids(dataset);
        let n_iterations = self.vocab_size - MIN_VOCAB_SIZE;
        let mut merges: Vec<MergeRule> = Vec::with_capacity(n_iterations as usize);

        for i in 0..n_iterations {
            let mut counts = HashMap::new();
            get_pair_counts(tokens.as_slice(), &mut counts);
            let Some(most_common_pair) = get_most_common_pair(&counts) else {
                break;
            };

            let rule = most_common_pair.with_new_id(TokenId::for_new_token(i));

            merges.push(rule);
            merge(&mut tokens, rule);
        }

        Ok(SimpleBPETokenizer::from_merges(merges))
    }
}

impl Deserializable for SimpleBPETokenizerConfig {
    type Output = SimpleBPETokenizer;

    fn load(&self, path: &Path) -> Result<Self::Output, std::io::Error> {
        verify_stok_extension(path)?;

        let file = File::open(path)?;
        let reader = BufReader::new(file);

        Ok(SimpleBPETokenizer::from_merges(parse_merges(
            reader.lines().enumerate().map(|(i, line)| (i + 1, line)),
        )?))
    }
}
