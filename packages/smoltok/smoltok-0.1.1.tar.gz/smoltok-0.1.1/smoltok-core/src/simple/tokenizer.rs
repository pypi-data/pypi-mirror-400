//! Simple BPE tokenizer implementation.

use crate::tokenizer::{
    MergeRule, Serializable, TokenId, TokenPair, Tokenizer, UnknownTokenId, bpe_encode, build_merge_lookup,
    build_vocab, save_merges, save_vocab, verify_stok_extension,
};
use std::collections::HashMap;
use std::fs::File;
use std::io::BufWriter;
use std::io::Error;
use std::path::Path;

/// Simple BPE tokenizer. Does not support regex patterns and special tokens.
#[derive(Debug)]
pub struct SimpleBPETokenizer {
    /// The learned merge rules, in order of application.
    merges: Vec<MergeRule>,
    /// Maps token pairs to (rank, new_id) for fast lookup during encoding.
    merge_lookup: HashMap<TokenPair, (usize, TokenId)>,
    /// Maps token IDs to their byte sequences.
    vocab: HashMap<TokenId, Vec<u8>>,
}

impl SimpleBPETokenizer {
    /// Creates a new `SimpleBPETokenizer` from a list of merge operations.
    ///
    /// The vocabulary is automatically reconstructed from the merges.
    ///
    /// # Arguments
    ///
    /// * `merges` - A vector of `MergeRule` representing the merge operations.
    pub fn from_merges(merges: Vec<MergeRule>) -> Self {
        Self {
            vocab: build_vocab(merges.as_slice()),
            merge_lookup: build_merge_lookup(merges.as_slice()),
            merges,
        }
    }
}

impl Tokenizer for SimpleBPETokenizer {
    type DecodingError = UnknownTokenId;

    fn merges(&self) -> &[MergeRule] {
        self.merges.as_slice()
    }

    fn vocab(&self) -> &HashMap<TokenId, Vec<u8>> {
        &self.vocab
    }

    fn encode(&self, text: &str) -> Vec<TokenId> {
        bpe_encode(text, &self.merge_lookup)
    }

    fn decode(&self, tokens: &[TokenId]) -> Result<String, UnknownTokenId> {
        let mut bytes = Vec::new();

        for token_id in tokens {
            if let Some(token_bytes) = self.vocab.get(token_id) {
                bytes.extend_from_slice(token_bytes);
            } else {
                return Err(UnknownTokenId(*token_id));
            }
        }

        Ok(String::from_utf8_lossy(&bytes).into_owned())
    }
}

impl Serializable for SimpleBPETokenizer {
    fn save(&self, path: &Path) -> Result<(), Error> {
        verify_stok_extension(path)?;

        let file = File::create(path)?;
        let mut writer = BufWriter::new(file);

        save_merges(&mut writer, self.merges.as_slice())?;
        save_vocab(&path.with_extension("vocab"), self.merges.as_slice(), self.vocab())?;

        Ok(())
    }
}
