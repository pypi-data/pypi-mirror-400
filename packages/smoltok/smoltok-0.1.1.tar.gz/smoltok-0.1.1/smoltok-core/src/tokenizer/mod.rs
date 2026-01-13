use std::collections::HashMap;
use std::ops::Fn;

mod errors;
mod traits;
mod types;

pub use errors::{UnknownTokenId, VocabSizeTooSmall};
pub use traits::{
    Deserializable, Serializable, Tokenizer, Trainable, parse_merges, save_merges, save_vocab, verify_stok_extension,
};
pub use types::{MIN_VOCAB_SIZE, MergeRule, TokenId, TokenPair};

/// Helper to convert a string to a vector of byte values as TokenIds.
pub(crate) fn string_to_token_ids(text: &str) -> Vec<TokenId> {
    text.as_bytes().iter().map(|&b| TokenId::new(b as u32)).collect()
}

/// Counts occurrences of all adjacent token pairs in a sequence.
pub(crate) fn get_pair_counts(tokens: &[TokenId], counts: &mut HashMap<TokenPair, u32>) {
    for slice in tokens.windows(2) {
        let pair = TokenPair::new(slice[0], slice[1]);
        *counts.entry(pair).or_default() += 1;
    }
}

/// Finds the most frequent pair of tokens.
pub(crate) fn get_most_common_pair(counts: &HashMap<TokenPair, u32>) -> Option<&TokenPair> {
    counts.iter().max_by_key(|&(_, count)| count).map(|(pair, _)| pair)
}

/// Merges occurrences of a specific pair into a new token ID in place.
pub(crate) fn merge(tokens: &mut Vec<TokenId>, rule: MergeRule) {
    let mut write = 0usize;
    let mut read = 0usize;

    while read < tokens.len() {
        if rule.pair().matches(tokens.get(read), tokens.get(read + 1)) {
            tokens[write] = rule.new_id();
            read += 2;
        } else {
            tokens[write] = tokens[read];
            read += 1;
        }
        write += 1;
    }
    tokens.truncate(write);
}

/// Reconstruct the vocabulary from the base bytes (0-255) and merge operations.
///
/// Each merged token's byte sequence is the concatenation of its component tokens' bytes.
pub(crate) fn build_vocab(merges: &[MergeRule]) -> HashMap<TokenId, Vec<u8>> {
    let mut vocab = HashMap::new();
    for i in 0..MIN_VOCAB_SIZE {
        vocab.insert(TokenId::new(i), vec![i as u8]);
    }
    for rule in merges {
        let (token0, token1) = rule.pair().as_tuple();

        let mut merged_bytes = Vec::with_capacity(vocab[&token0].len() + vocab[&token1].len());
        merged_bytes.extend_from_slice(&vocab[&token0]);
        merged_bytes.extend_from_slice(&vocab[&token1]);

        vocab.insert(rule.new_id(), merged_bytes);
    }

    vocab
}

/// Build merge lookup map from token pairs to (rank, new_id) for fast lookup during encoding.
pub(crate) fn build_merge_lookup(merges: &[MergeRule]) -> HashMap<TokenPair, (usize, TokenId)> {
    merges
        .iter()
        .enumerate()
        .map(|(rank, rule)| (*rule.pair(), (rank, rule.new_id())))
        .collect()
}

/// Encode a text string into a list of token IDs using learned merges as lookup.
///
/// Moved here as both simple and regex implementation need this functionality.
pub(crate) fn bpe_encode(text: &str, merge_lookup: &HashMap<TokenPair, (usize, TokenId)>) -> Vec<TokenId> {
    let mut tokens = string_to_token_ids(text);

    loop {
        let mut pairs = HashMap::new();
        get_pair_counts(tokens.as_slice(), &mut pairs);

        // find the pair with the minimum rank (earliest in merge order)
        let best_pair = pairs
            .keys()
            .filter_map(|pair| merge_lookup.get(pair).map(|&(rank, new_id)| (pair, rank, new_id)))
            .min_by_key(|&(_, rank, _)| rank);

        match best_pair {
            Some((pair, _, new_id)) => {
                let rule = MergeRule::new(*pair, new_id);
                merge(&mut tokens, rule);
            }
            None => break, // nothing to merge
        }
    }

    tokens
}

/// Core BPE training loop that can be used by both sequential and parallel implementations.
///
/// # Arguments
/// * `chunks` - Mutable slice of tokenized chunks to train on
/// * `n_iterations` - Number of merge operations to learn
/// * `count_pairs_fn` - Strategy for counting pairs (allows sequential vs parallel)
pub(crate) fn train_bpe<F>(chunks: &mut [Vec<TokenId>], n_iterations: u32, count_pairs_fn: F) -> Vec<MergeRule>
where
    F: Fn(&[Vec<TokenId>]) -> HashMap<TokenPair, u32>,
{
    let mut merges: Vec<MergeRule> = Vec::with_capacity(n_iterations as usize);

    for i in 0..n_iterations {
        let pair_counts = count_pairs_fn(chunks);

        let Some(most_common_pair) = get_most_common_pair(&pair_counts) else {
            break;
        };

        let rule = most_common_pair.with_new_id(TokenId::for_new_token(i));
        merges.push(rule);

        for tokens in chunks.iter_mut() {
            merge(tokens, rule);
        }
    }

    merges
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_pair_counts_basic() {
        let tokens: Vec<TokenId> = [1, 2, 3, 1, 2].iter().map(|&x| TokenId::new(x)).collect();
        let mut counts = HashMap::new();
        get_pair_counts(tokens.as_slice(), &mut counts);

        let mut expected = HashMap::new();
        expected.insert(TokenPair::new(TokenId::new(1), TokenId::new(2)), 2);
        expected.insert(TokenPair::new(TokenId::new(2), TokenId::new(3)), 1);
        expected.insert(TokenPair::new(TokenId::new(3), TokenId::new(1)), 1);

        assert_eq!(counts, expected);
    }
    #[test]
    fn test_get_most_common_pair_basic() {
        let tokens: Vec<TokenId> = [1, 2, 3, 1, 2].iter().map(|&x| TokenId::new(x)).collect();
        let mut counts = HashMap::new();
        get_pair_counts(tokens.as_slice(), &mut counts);
        let most_common_pair = get_most_common_pair(&counts);

        assert_eq!(
            most_common_pair,
            Some(&TokenPair::new(TokenId::new(1), TokenId::new(2)))
        );
    }

    #[test]
    fn test_get_pair_counts_repetitive() {
        let tokens: Vec<TokenId> = [1, 2, 3, 1, 2, 3, 1, 2, 3].iter().map(|&x| TokenId::new(x)).collect();
        let mut counts = HashMap::new();
        get_pair_counts(tokens.as_slice(), &mut counts);

        let mut expected = HashMap::new();
        expected.insert(TokenPair::new(TokenId::new(1), TokenId::new(2)), 3);
        expected.insert(TokenPair::new(TokenId::new(2), TokenId::new(3)), 3);
        expected.insert(TokenPair::new(TokenId::new(3), TokenId::new(1)), 2);

        assert_eq!(counts, expected);
    }

    #[test]
    fn test_get_pair_counts_empty() {
        let mut counts = HashMap::new();
        get_pair_counts(&[], &mut counts);
        assert_eq!(counts, HashMap::new());
    }

    #[test]
    fn test_get_most_common_pair_empty() {
        let counts = HashMap::new();
        let most_common_pair = get_most_common_pair(&counts);
        assert_eq!(most_common_pair, None);
    }

    #[test]
    fn test_merge() {
        let mut tokens: Vec<TokenId> = [1, 2, 3, 1, 2].iter().map(|&x| TokenId::new(x)).collect();
        let pair = TokenPair::new(TokenId::new(1), TokenId::new(2)).with_new_id(TokenId::new(4));
        merge(&mut tokens, pair);

        assert_eq!(tokens, vec![TokenId::new(4), TokenId::new(3), TokenId::new(4)]);
    }

    #[test]
    fn test_merge_no_occurrence() {
        let mut tokens: Vec<TokenId> = [1, 2, 3].iter().map(|&x| TokenId::new(x)).collect();
        let pair = TokenPair::new(TokenId::new(4), TokenId::new(5)).with_new_id(TokenId::new(6));
        merge(&mut tokens, pair);

        assert_eq!(tokens, vec![TokenId::new(1), TokenId::new(2), TokenId::new(3)]);
    }

    #[test]
    fn test_merge_consecutive() {
        let mut tokens: Vec<TokenId> = [1, 1, 1].iter().map(|&x| TokenId::new(x)).collect();
        let pair = TokenPair::new(TokenId::new(1), TokenId::new(1)).with_new_id(TokenId::new(2));
        merge(&mut tokens, pair);

        assert_eq!(tokens, vec![TokenId::new(2), TokenId::new(1)]);
    }

    #[test]
    fn test_build_vocab_empty_merges() {
        let vocab = build_vocab(&[]);

        assert_eq!(vocab.len(), 256);

        for i in 0u8..=255 {
            assert_eq!(vocab[&TokenId::new(i as u32)], vec![i]);
        }
    }

    #[test]
    fn test_build_vocab_single_merge() {
        // merge bytes 'a' (97) and 'b' (98) into token 256
        let merges = vec![
            TokenPair::new(TokenId::new(97), TokenId::new(98)).with_new_id(TokenId::for_new_token(0)), // 256
        ];

        let vocab = build_vocab(merges.as_slice());

        assert_eq!(vocab.len(), 257);
        assert_eq!(vocab[&TokenId::new(256)], vec![b'a', b'b']);
    }

    #[test]
    fn test_build_vocab_chained_merges() {
        // first merge: 'a' + 'b' -> 256
        // second merge: 256 + 'c' -> 257 (should produce "abc")
        let merges = vec![
            TokenPair::new(TokenId::new(97), TokenId::new(98)).with_new_id(TokenId::for_new_token(0)), // 256
            TokenPair::new(TokenId::new(256), TokenId::new(99)).with_new_id(TokenId::for_new_token(1)), // 257
        ];

        let vocab = build_vocab(merges.as_slice());

        assert_eq!(vocab.len(), 258);
        assert_eq!(vocab[&TokenId::new(256)], vec![b'a', b'b']);
        assert_eq!(vocab[&TokenId::new(257)], vec![b'a', b'b', b'c']);
    }

    #[test]
    fn test_build_merge_lookup_empty() {
        let lookup = build_merge_lookup(&[]);
        assert!(lookup.is_empty());
    }

    #[test]
    fn test_build_merge_lookup_single() {
        let pair = TokenPair::new(TokenId::new(1), TokenId::new(2));
        let merges = vec![pair.with_new_id(TokenId::new(256))];

        let lookup = build_merge_lookup(merges.as_slice());

        assert_eq!(lookup.len(), 1);
        assert_eq!(lookup[&pair], (0, TokenId::new(256)));
    }

    #[test]
    fn test_build_merge_lookup_multiple() {
        let pair1 = TokenPair::new(TokenId::new(1), TokenId::new(2));
        let pair2 = TokenPair::new(TokenId::new(3), TokenId::new(4));
        let pair3 = TokenPair::new(TokenId::new(256), TokenId::new(5));

        let merges = vec![
            pair1.with_new_id(TokenId::new(256)),
            pair2.with_new_id(TokenId::new(257)),
            pair3.with_new_id(TokenId::new(258)),
        ];

        let lookup = build_merge_lookup(merges.as_slice());

        assert_eq!(lookup.len(), 3);
        assert_eq!(lookup[&pair1], (0, TokenId::new(256)));
        assert_eq!(lookup[&pair2], (1, TokenId::new(257)));
        assert_eq!(lookup[&pair3], (2, TokenId::new(258)));
    }

    #[test]
    fn test_string_to_token_ids_ascii() {
        let tokens = string_to_token_ids("abc");
        assert_eq!(tokens, vec![TokenId::new(97), TokenId::new(98), TokenId::new(99)]);
    }

    #[test]
    fn test_string_to_token_ids_empty() {
        let tokens = string_to_token_ids("");
        assert!(tokens.is_empty());
    }

    #[test]
    fn test_string_to_token_ids_emoji() {
        // '🚀' is U+1F680, encoded as 0xF0 0x9F 0x9A 0x80 in UTF-8
        let tokens = string_to_token_ids("🚀");
        assert_eq!(
            tokens,
            vec![
                TokenId::new(0xF0),
                TokenId::new(0x9F),
                TokenId::new(0x9A),
                TokenId::new(0x80)
            ]
        );
    }

    #[test]
    fn test_bpe_encode_empty() {
        let lookup = HashMap::new();
        let tokens = bpe_encode("", &lookup);
        assert!(tokens.is_empty());
    }

    #[test]
    fn test_bpe_encode_no_merges() {
        let lookup = HashMap::new();
        let tokens = bpe_encode("abc", &lookup);
        assert_eq!(tokens, vec![TokenId::new(97), TokenId::new(98), TokenId::new(99)]);
    }

    #[test]
    fn test_bpe_encode_single_merge() {
        let pair = TokenPair::new(TokenId::new(97), TokenId::new(98)); // 'a' + 'b'
        let mut lookup = HashMap::new();
        lookup.insert(pair, (0, TokenId::new(256)));

        let tokens = bpe_encode("ab", &lookup);
        assert_eq!(tokens, vec![TokenId::new(256)]);
    }

    #[test]
    fn test_bpe_encode_multiple_occurrences() {
        let pair = TokenPair::new(TokenId::new(97), TokenId::new(98)); // 'a' + 'b'
        let mut lookup = HashMap::new();
        lookup.insert(pair, (0, TokenId::new(256)));

        let tokens = bpe_encode("abab", &lookup);
        assert_eq!(tokens, vec![TokenId::new(256), TokenId::new(256)]);
    }

    #[test]
    fn test_bpe_encode_chained_merges() {
        // First merge: 'a' + 'b' -> 256
        // Second merge: 256 + 'c' -> 257
        let pair1 = TokenPair::new(TokenId::new(97), TokenId::new(98));
        let pair2 = TokenPair::new(TokenId::new(256), TokenId::new(99));

        let mut lookup = HashMap::new();
        lookup.insert(pair1, (0, TokenId::new(256)));
        lookup.insert(pair2, (1, TokenId::new(257)));

        let tokens = bpe_encode("abc", &lookup);
        assert_eq!(tokens, vec![TokenId::new(257)]);
    }

    #[test]
    fn test_bpe_encode_respects_rank_order() {
        // If we have overlapping merges, the one with lower rank should be applied first
        // 'a' + 'b' -> 256 (rank 0)
        // 'b' + 'c' -> 257 (rank 1)
        // For "abc", 'ab' should be merged first, leaving "256 c"
        let pair1 = TokenPair::new(TokenId::new(97), TokenId::new(98));
        let pair2 = TokenPair::new(TokenId::new(98), TokenId::new(99));

        let mut lookup = HashMap::new();
        lookup.insert(pair1, (0, TokenId::new(256)));
        lookup.insert(pair2, (1, TokenId::new(257)));

        let tokens = bpe_encode("abc", &lookup);
        // 'ab' -> 256, then we have "256 c" which has no merge
        assert_eq!(tokens, vec![TokenId::new(256), TokenId::new(99)]);
    }

    #[test]
    fn test_merge_empty() {
        let mut tokens: Vec<TokenId> = vec![];
        let rule = TokenPair::new(TokenId::new(1), TokenId::new(2)).with_new_id(TokenId::new(256));
        merge(&mut tokens, rule);
        assert!(tokens.is_empty());
    }

    #[test]
    fn test_merge_single_element() {
        let mut tokens: Vec<TokenId> = vec![TokenId::new(1)];
        let rule = TokenPair::new(TokenId::new(1), TokenId::new(2)).with_new_id(TokenId::new(256));
        merge(&mut tokens, rule);
        assert_eq!(tokens, vec![TokenId::new(1)]);
    }

    #[test]
    fn test_merge_all_pairs() {
        let mut tokens: Vec<TokenId> = vec![TokenId::new(1), TokenId::new(2), TokenId::new(1), TokenId::new(2)];
        let rule = TokenPair::new(TokenId::new(1), TokenId::new(2)).with_new_id(TokenId::new(256));
        merge(&mut tokens, rule);
        assert_eq!(tokens, vec![TokenId::new(256), TokenId::new(256)]);
    }

    #[test]
    fn test_get_pair_counts_single_element() {
        let tokens: Vec<TokenId> = vec![TokenId::new(1)];
        let mut counts = HashMap::new();
        get_pair_counts(tokens.as_slice(), &mut counts);
        assert!(counts.is_empty());
    }

    #[test]
    fn test_get_pair_counts_accumulates() {
        let tokens: Vec<TokenId> = vec![TokenId::new(1), TokenId::new(2)];
        let mut counts = HashMap::new();
        counts.insert(TokenPair::new(TokenId::new(1), TokenId::new(2)), 5);

        get_pair_counts(tokens.as_slice(), &mut counts);

        assert_eq!(counts[&TokenPair::new(TokenId::new(1), TokenId::new(2))], 6);
    }
}
