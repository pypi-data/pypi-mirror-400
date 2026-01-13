use crate::regex::{GPT4_SPLIT_PATTERN, save_regex_tokenizer, split_text};
use crate::tokenizer::{UnknownTokenId, bpe_encode, build_merge_lookup, build_vocab, save_vocab};
use crate::{MergeRule, Serializable, TokenId, TokenPair, Tokenizer};
use fancy_regex::Regex;
use rayon::prelude::*;
use std::collections::HashMap;
use std::io::Error;
use std::path::Path;

/// Regex-based BPE tokenizer that supports regex patterns and special tokens.
///
/// This tokenizer first splits text using a regex pattern,
/// then applies BPE encoding to each chunk independently.
/// It also supports special tokens that are handled separately from regular text.
#[derive(Debug)]
pub struct ParallelRegexBPETokenizer {
    /// The learned merge rules, in order of application.
    merges: Vec<MergeRule>,
    /// Maps token pairs to (rank, new_id) for fast lookup during encoding.
    merge_lookup: HashMap<TokenPair, (usize, TokenId)>,
    /// Maps token IDs to their byte sequences.
    vocab: HashMap<TokenId, Vec<u8>>,
    /// The regex pattern used for splitting text.
    pattern: String,
    /// The compiled regex pattern.
    compiled_pattern: Regex,
    /// Special tokens mapping (token string -> token ID).
    special_tokens: HashMap<String, TokenId>,
}

impl ParallelRegexBPETokenizer {
    // todo: avoid code duplication

    /// Creates a new `ParallelRegexBPETokenizer` from merge rules and a pattern.
    ///
    /// # Arguments
    ///
    /// * `merges` - A vector of `MergeRule` representing the merge operations.
    /// * `pattern` - The regex pattern for splitting text.
    pub fn new(merges: Vec<MergeRule>, pattern: String) -> Self {
        // todo:
        let compiled_pattern = Regex::new(&pattern).unwrap_or_else(|_| {
            Regex::new(GPT4_SPLIT_PATTERN).expect("Both primary and fallback patterns failed to compile")
        });

        Self {
            vocab: build_vocab(merges.as_slice()),
            merge_lookup: build_merge_lookup(merges.as_slice()),
            merges,
            pattern,
            compiled_pattern,
            special_tokens: HashMap::new(),
        }
    }

    /// Creates a new `ParallelRegexBPETokenizer` from merge rules using the default GPT-4 pattern.
    ///
    /// # Arguments
    ///
    /// * `merges` - A vector of `MergeRule` representing the merge operations.
    pub fn from_merges(merges: Vec<MergeRule>) -> Self {
        Self::new(merges, GPT4_SPLIT_PATTERN.to_string())
    }

    /// Returns the number of merge rules learned during training.
    pub fn num_merges(&self) -> usize {
        self.merges.len()
    }

    /// Returns the vocabulary size (base 256 bytes + merged tokens).
    pub fn vocab_size(&self) -> usize {
        self.vocab.len()
    }

    /// Returns the regex pattern used for splitting text.
    pub fn pattern(&self) -> &str {
        &self.pattern
    }

    /// Registers special tokens with the tokenizer.
    ///
    /// Special tokens are handled separately during encoding and are not
    /// subject to the BPE merge process.
    ///
    /// # Arguments
    ///
    /// * `special_tokens` - A map of special token strings to their token IDs.
    pub fn register_special_tokens(&mut self, special_tokens: HashMap<String, TokenId>) {
        self.special_tokens.extend(special_tokens);
    }

    /// Adds a single special token to the tokenizer.
    ///
    /// # Arguments
    ///
    /// * `token` - The special token string.
    /// * `token_id` - The token ID to assign.
    pub fn add_special_token(&mut self, token: String, token_id: TokenId) {
        self.special_tokens.insert(token, token_id);
    }

    /// Returns the special tokens registered with this tokenizer.
    pub fn special_tokens(&self) -> &HashMap<String, TokenId> {
        &self.special_tokens
    }

    /// Encode a single chunk using BPE.
    fn encode_chunk(&self, chunk: &str) -> Vec<TokenId> {
        bpe_encode(chunk, &self.merge_lookup)
    }

    /// Encode text without handling special tokens (parallel).
    fn encode_ordinary(&self, text: &str) -> Vec<TokenId> {
        let chunks = split_text(text, &self.compiled_pattern);
        chunks
            .par_iter()
            .map(|chunk| self.encode_chunk(chunk))
            .flatten()
            .collect()
    }
}

/// Helper enum for parallel encoding with special tokens.
enum Segment<'a> {
    Text(&'a str),
    SpecialToken(&'a str),
}

impl Tokenizer for ParallelRegexBPETokenizer {
    type DecodingError = UnknownTokenId;

    fn merges(&self) -> &[MergeRule] {
        self.merges.as_slice()
    }

    fn vocab(&self) -> &HashMap<TokenId, Vec<u8>> {
        &self.vocab
    }

    fn encode(&self, text: &str) -> Vec<TokenId> {
        if self.special_tokens.is_empty() {
            return self.encode_ordinary(text);
        }

        // build a regex pattern to split on special tokens
        let special_tokens_pattern = self
            .special_tokens
            .keys()
            .map(|token| fancy_regex::escape(token))
            .collect::<Vec<_>>()
            .join("|");

        let split_pattern = match Regex::new(&format!("({})", special_tokens_pattern)) {
            Ok(p) => p,
            Err(_) => return self.encode_ordinary(text),
        };

        // collect all segments (text between special tokens + special tokens themselves)
        let mut segments: Vec<Segment> = Vec::new();
        let mut last_end = 0;

        // find all special tokens and split accordingly
        for m in split_pattern.find_iter(text).flatten() {
            // encode the text before this special token
            if m.start() > last_end {
                segments.push(Segment::Text(&text[last_end..m.start()]));
            }
            segments.push(Segment::SpecialToken(m.as_str()));
            last_end = m.end();
        }

        // encode any remaining text after the last special token
        if last_end < text.len() {
            segments.push(Segment::Text(&text[last_end..]));
        }

        // encode segments in parallel
        segments
            .par_iter()
            .map(|segment| match segment {
                Segment::Text(text) => self.encode_ordinary(text),
                Segment::SpecialToken(special_token) => self
                    .special_tokens
                    .get(*special_token)
                    .map(|&id| vec![id])
                    .unwrap_or_default(),
            })
            .flatten()
            .collect()
    }

    fn decode(&self, tokens: &[TokenId]) -> Result<String, UnknownTokenId> {
        // build inverted special tokens map for decoding
        let special_tokens_inverted: HashMap<TokenId, Vec<u8>> = self
            .special_tokens
            .iter()
            .map(|(token, &id)| (id, token.as_bytes().to_vec()))
            .collect();

        // look up bytes for each token in parallel
        let byte_chunks: Result<Vec<Vec<u8>>, UnknownTokenId> = tokens
            .par_iter()
            .map(|token_id| {
                if let Some(token_bytes) = self.vocab.get(token_id) {
                    Ok(token_bytes.clone())
                } else if let Some(token_bytes) = special_tokens_inverted.get(token_id) {
                    Ok(token_bytes.clone())
                } else {
                    Err(UnknownTokenId(*token_id))
                }
            })
            .collect();

        // concatenate all byte chunks
        let bytes: Vec<u8> = byte_chunks?.into_iter().flatten().collect();

        Ok(String::from_utf8_lossy(&bytes).into_owned())
    }
}

impl Serializable for ParallelRegexBPETokenizer {
    fn save(&self, path: &Path) -> Result<(), Error> {
        save_regex_tokenizer(path, self.pattern.as_str(), self.merges())?;
        save_vocab(&path.with_extension("vocab"), self.merges.as_slice(), self.vocab())?;

        Ok(())
    }
}
