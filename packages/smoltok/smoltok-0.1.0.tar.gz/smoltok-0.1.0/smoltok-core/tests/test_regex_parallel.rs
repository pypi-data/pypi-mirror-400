use smoltok_core::{
    Deserializable, ParallelRegexBPETokenizerConfig, RegexBPETokenizerConfig, RegexBPETokenizerConfigError,
    Serializable, TokenId, Tokenizer, Trainable,
};
use std::collections::HashMap;
use std::fs::File;

#[test]
fn test_regex_bpe_config_invalid_vocab_size() {
    let config = ParallelRegexBPETokenizerConfig::build(255, None);
    assert!(config.is_err());
    match config.unwrap_err() {
        RegexBPETokenizerConfigError::VocabSizeTooSmall(e) => {
            assert_eq!(e.to_string(), "Vocab size must be at least 256, got 255");
        }
        _ => panic!("Expected VocabSizeTooSmall error"),
    }
}

#[test]
fn test_regex_bpe_config_invalid_pattern() {
    let config = ParallelRegexBPETokenizerConfig::build(256, Some("[invalid(regex"));
    assert!(config.is_err());
    match config.unwrap_err() {
        RegexBPETokenizerConfigError::RegexCompilationError(_) => {}
        _ => panic!("Expected RegexCompilationError"),
    }
}

#[test]
fn test_regex_bpe_config_valid() {
    let config = ParallelRegexBPETokenizerConfig::build(300, None);
    assert!(config.is_ok());
}

#[test]
fn test_parallel_vs_sequential_both_produce_valid_tokenizers() {
    // note: when multiple pairs have equal frequency,
    // the order of merges can differ between parallel and sequential due to HashMap iteration order
    let dataset = "hello world hello world hello world test data more text";

    let sequential_config = RegexBPETokenizerConfig::build(270, None).unwrap();
    let parallel_config = ParallelRegexBPETokenizerConfig::build(270, None).unwrap();

    let sequential_tokenizer = sequential_config.train(dataset).unwrap();
    let parallel_tokenizer = parallel_config.train(dataset).unwrap();

    let test_text = "hello world test";

    let seq_encoded = sequential_tokenizer.encode(test_text);
    let seq_decoded = sequential_tokenizer.decode(seq_encoded.as_slice()).unwrap();
    assert_eq!(seq_decoded, test_text, "Sequential encode/decode failed");

    let par_encoded = parallel_tokenizer.encode(test_text);
    let par_decoded = parallel_tokenizer.decode(par_encoded.as_slice()).unwrap();
    assert_eq!(par_decoded, test_text, "Parallel encode/decode failed");

    assert!(sequential_tokenizer.num_merges() > 0);
    assert!(parallel_tokenizer.num_merges() > 0);
    assert!(sequential_tokenizer.num_merges() == parallel_tokenizer.num_merges());
}

#[test]
fn test_parallel_consistency_with_many_chunks() {
    let dataset = "alpha beta gamma delta epsilon zeta eta theta iota kappa \
                   lambda mu nu xi omicron pi rho sigma tau upsilon \
                   alpha beta gamma delta epsilon zeta eta theta iota kappa \
                   lambda mu nu xi omicron pi rho sigma tau upsilon";

    let parallel_config = ParallelRegexBPETokenizerConfig::build(280, None).unwrap();
    let tokenizer = parallel_config.train(dataset).unwrap();

    let test_texts = ["alpha beta", "gamma delta epsilon", "zeta eta theta"];
    for text in test_texts {
        let encoded = tokenizer.encode(text);
        let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
        assert_eq!(decoded, text, "Round-trip failed for: {}", text);
    }
}

#[test]
fn test_parallel_with_large_dataset() {
    let base_text = "The quick brown fox jumps over the lazy dog. ";
    let dataset: String = std::iter::repeat(base_text).take(100).collect();

    let config = ParallelRegexBPETokenizerConfig::build(300, None).unwrap();
    let tokenizer = config.train(&dataset).unwrap();

    assert!(tokenizer.num_merges() > 0);
    assert!(tokenizer.num_merges() <= 44); // 300 - 256 = 44 max merges

    let test_text = "The quick brown fox";
    let encoded = tokenizer.encode(test_text);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, test_text);
}

#[test]
fn test_parallel_single_chunk() {
    let dataset = "aaaabbbbccccdddd";
    let config = ParallelRegexBPETokenizerConfig::build(260, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let encoded = tokenizer.encode("aaaa");
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, "aaaa");
}

#[test]
fn test_parallel_empty_input() {
    let dataset = "hello world";
    let config = ParallelRegexBPETokenizerConfig::build(260, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let encoded = tokenizer.encode("");
    assert!(encoded.is_empty());

    let decoded = tokenizer.decode(&[]).unwrap();
    assert_eq!(decoded, "");
}

#[test]
fn test_parallel_minimal_dataset() {
    let dataset = "ab";
    let config = ParallelRegexBPETokenizerConfig::build(260, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    assert!(tokenizer.num_merges() == 1);

    let encoded = tokenizer.encode("ab");
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, "ab");
}

#[test]
fn test_parallel_repeated_single_char() {
    let dataset = "aaaaaaaaaaaaaaaa"; // 16 a's
    let config = ParallelRegexBPETokenizerConfig::build(260, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    // Should merge (a, a) -> 256, then (256, 256) -> 257, etc. 4 times (2^4 = 16)
    assert!(tokenizer.num_merges() == 4);

    let encoded = tokenizer.encode("aaaa");
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, "aaaa");
}

#[test]
fn test_parallel_special_tokens() {
    let dataset = "hello world";
    let config = ParallelRegexBPETokenizerConfig::build(260, None).unwrap();
    let mut tokenizer = config.train(dataset).unwrap();

    let mut special_tokens = HashMap::new();
    special_tokens.insert("<|endoftext|>".to_string(), TokenId::new(50256));
    special_tokens.insert("<|pad|>".to_string(), TokenId::new(50257));
    tokenizer.register_special_tokens(special_tokens);

    let text = "hello<|endoftext|>world";
    let encoded = tokenizer.encode(text);

    assert!(encoded.contains(&TokenId::new(50256)));

    let decoded = tokenizer.decode(&encoded).unwrap();
    assert_eq!(decoded, text);
}

#[test]
fn test_parallel_add_special_token() {
    let dataset = "test";
    let config = ParallelRegexBPETokenizerConfig::build(256, None).unwrap();
    let mut tokenizer = config.train(dataset).unwrap();

    tokenizer.add_special_token("<|start|>".to_string(), TokenId::new(1000));

    assert_eq!(tokenizer.special_tokens().len(), 1);
    assert_eq!(tokenizer.special_tokens().get("<|start|>"), Some(&TokenId::new(1000)));
}

#[test]
fn test_parallel_multiple_special_tokens() {
    let dataset = "hello world";
    let config = ParallelRegexBPETokenizerConfig::build(260, None).unwrap();
    let mut tokenizer = config.train(dataset).unwrap();

    let mut special_tokens = HashMap::new();
    special_tokens.insert("<|start|>".to_string(), TokenId::new(50256));
    special_tokens.insert("<|end|>".to_string(), TokenId::new(50257));
    special_tokens.insert("<|pad|>".to_string(), TokenId::new(50258));
    tokenizer.register_special_tokens(special_tokens);

    assert_eq!(tokenizer.special_tokens().len(), 3);

    let text = "<|start|>hello<|end|>";
    let encoded = tokenizer.encode(text);

    assert!(encoded.contains(&TokenId::new(50256)));
    assert!(encoded.contains(&TokenId::new(50257)));

    let decoded = tokenizer.decode(&encoded).unwrap();
    assert_eq!(decoded, text);
}

#[test]
fn test_parallel_special_tokens_at_boundaries() {
    let dataset = "hello world";
    let config = ParallelRegexBPETokenizerConfig::build(260, None).unwrap();
    let mut tokenizer = config.train(dataset).unwrap();

    tokenizer.add_special_token("<|eos|>".to_string(), TokenId::new(50256));

    // special token at the end
    let text = "hello<|eos|>";
    let encoded = tokenizer.encode(text);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, text);

    // special token at the start
    let text = "<|eos|>world";
    let encoded = tokenizer.encode(text);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, text);
}

#[test]
fn test_parallel_decode_unknown_token() {
    let dataset = "test";
    let config = ParallelRegexBPETokenizerConfig::build(256, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let result = tokenizer.decode(&[TokenId::new(999)]);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "Unknown token ID 999");
}

#[test]
fn test_parallel_unicode() {
    let dataset = "日本語テスト 日本語テスト 日本語テスト 中文测试 中文测试";
    let config = ParallelRegexBPETokenizerConfig::build(300, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let test_text = "日本語テスト";
    let encoded = tokenizer.encode(test_text);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, test_text);
}

#[test]
fn test_parallel_mixed_content() {
    let dataset = "Hello 世界! Test123 αβγ emoji: 🎉🎊 repeat Hello 世界! Test123";
    let config = ParallelRegexBPETokenizerConfig::build(280, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let test_cases = ["Hello", "世界", "αβγ", "🎉"];
    for text in test_cases {
        let encoded = tokenizer.encode(text);
        let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
        assert_eq!(decoded, text, "Failed for: {}", text);
    }
}

#[test]
fn test_parallel_save_load_full_flow() {
    use std::path::PathBuf;

    let dataset = "hello world hello world hello";
    let config = ParallelRegexBPETokenizerConfig::build(260, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let path = PathBuf::from("parallel_regex_model.stok");
    tokenizer.save(&path).unwrap();

    let loaded_tokenizer = ParallelRegexBPETokenizerConfig::from_merges(100, None)
        .unwrap()
        .load(&path)
        .unwrap();

    assert_eq!(tokenizer.num_merges(), loaded_tokenizer.num_merges());
    assert_eq!(tokenizer.pattern(), loaded_tokenizer.pattern());

    let original = "hello world hello";
    let encoded = loaded_tokenizer.encode(original);
    let decoded = loaded_tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, original);

    std::fs::remove_file(&path).ok();
    std::fs::remove_file(&path.with_extension("vocab")).ok();
}

#[test]
fn test_parallel_save_load_with_custom_pattern() {
    use std::path::PathBuf;

    let pattern = r"\w+|\s+|[^\w\s]+";
    let dataset = "hello world! test123";
    let config = ParallelRegexBPETokenizerConfig::build(260, Some(pattern)).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let path = PathBuf::from("parallel_regex_model_custom.stok");
    tokenizer.save(&path).unwrap();

    let loaded_tokenizer = ParallelRegexBPETokenizerConfig::from_merges(100, None)
        .unwrap()
        .load(&path)
        .unwrap();

    assert_eq!(loaded_tokenizer.pattern(), pattern);

    let original = "hello world!";
    let encoded = loaded_tokenizer.encode(original);
    let decoded = loaded_tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, original);

    std::fs::remove_file(&path).ok();
    std::fs::remove_file(&path.with_extension("vocab")).ok();
}

#[test]
fn test_parallel_save_load_invalid_extension() {
    let dataset = "test";
    let config = ParallelRegexBPETokenizerConfig::build(256, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let path = std::path::PathBuf::from("model.txt");
    let result = tokenizer.save(&path);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");
}

#[test]
fn test_parallel_load_invalid_extension() {
    let path = std::path::PathBuf::from("model.txt");
    let config = ParallelRegexBPETokenizerConfig::from_merges(10, None).unwrap();
    let result = config.load(&path);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");
}

#[test]
fn test_parallel_load_missing_pattern_header() {
    use std::io::Write;

    let temp_dir = std::env::temp_dir();
    let path = temp_dir.join("parallel_no_header_regex.stok");

    let mut file = File::create(&path).unwrap();
    writeln!(file, "97 98 256").unwrap();

    let config = ParallelRegexBPETokenizerConfig::from_merges(10, None).unwrap();
    let result = config.load(&path);

    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("Expected pattern header"));

    std::fs::remove_file(&path).ok();
    std::fs::remove_file(&path.with_extension("vocab")).ok();
}

#[test]
fn test_parallel_can_load_sequential_saved_model() {
    use std::path::PathBuf;

    let dataset = "testing cross compatibility between parallel and sequential";
    let seq_config = RegexBPETokenizerConfig::build(270, None).unwrap();
    let seq_tokenizer = seq_config.train(dataset).unwrap();

    let path = PathBuf::from("cross_compat_seq.stok");
    seq_tokenizer.save(&path).unwrap();

    // load with parallel config - since they use the same file format
    let loaded = ParallelRegexBPETokenizerConfig::from_merges(100, None)
        .unwrap()
        .load(&path)
        .unwrap();

    // the loaded tokenizer should have the same merges
    assert_eq!(seq_tokenizer.num_merges(), loaded.num_merges());

    // and produce identical results (same model loaded)
    let test_text = "testing cross";
    let seq_encoded = seq_tokenizer.encode(test_text);
    let loaded_encoded = loaded.encode(test_text);
    assert_eq!(seq_encoded, loaded_encoded);

    std::fs::remove_file(&path).ok();
    std::fs::remove_file(&path.with_extension("vocab")).ok();
}

#[test]
fn test_sequential_can_load_parallel_saved_model() {
    use std::path::PathBuf;

    let dataset = "testing cross compatibility between parallel and sequential";
    let par_config = ParallelRegexBPETokenizerConfig::build(270, None).unwrap();
    let par_tokenizer = par_config.train(dataset).unwrap();

    let path = PathBuf::from("cross_compat_par.stok");
    par_tokenizer.save(&path).unwrap();

    let loaded = RegexBPETokenizerConfig::from_merges(100, None)
        .unwrap()
        .load(&path)
        .unwrap();

    assert_eq!(par_tokenizer.num_merges(), loaded.num_merges());

    let test_text = "testing cross";
    let par_encoded = par_tokenizer.encode(test_text);
    let loaded_encoded = loaded.encode(test_text);
    assert_eq!(par_encoded, loaded_encoded);

    std::fs::remove_file(&path).ok();
    std::fs::remove_file(&path.with_extension("vocab")).ok();
}
