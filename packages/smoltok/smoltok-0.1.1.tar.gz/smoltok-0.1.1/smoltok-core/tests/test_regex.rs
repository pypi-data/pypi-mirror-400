use smoltok_core::{
    Deserializable, RegexBPETokenizerConfig, RegexBPETokenizerConfigError, Serializable, TokenId, Tokenizer, Trainable,
};
use std::collections::HashMap;
use std::fs::File;

#[test]
fn test_regex_bpe_config_invalid_vocab_size() {
    let config = RegexBPETokenizerConfig::build(255, None);
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
    let config = RegexBPETokenizerConfig::build(256, Some("[invalid(regex"));
    assert!(config.is_err());
    match config.unwrap_err() {
        RegexBPETokenizerConfigError::RegexCompilationError(_) => {}
        _ => panic!("Expected RegexCompilationError"),
    }
}

#[test]
fn test_regex_bpe_config_valid() {
    let config = RegexBPETokenizerConfig::build(300, None);
    assert!(config.is_ok());
}

#[test]
fn test_regex_bpe_train_and_encode_decode() {
    let dataset = "hello world hello world hello";
    let config = RegexBPETokenizerConfig::build(260, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    assert!(tokenizer.num_merges() > 0);
    assert!(tokenizer.num_merges() <= 4);

    let original = "hello world";
    let encoded = tokenizer.encode(original);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();

    assert_eq!(decoded, original);
}

#[test]
fn test_regex_bpe_with_simple_pattern() {
    // Use a simpler pattern for testing
    let pattern = r"\w+|\s+|[^\w\s]+";
    let dataset = "hello world! hello world!";
    let config = RegexBPETokenizerConfig::build(260, Some(pattern)).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let original = "hello world!";
    let encoded = tokenizer.encode(original);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();

    assert_eq!(decoded, original);
}

#[test]
fn test_regex_bpe_special_tokens() {
    let dataset = "hello world";
    let config = RegexBPETokenizerConfig::build(260, None).unwrap();
    let mut tokenizer = config.train(dataset).unwrap();

    // register special tokens
    let mut special_tokens = HashMap::new();
    special_tokens.insert("<|endoftext|>".to_string(), TokenId::new(50256));
    special_tokens.insert("<|pad|>".to_string(), TokenId::new(50257));
    tokenizer.register_special_tokens(special_tokens);

    // test encoding with special tokens
    let text = "hello<|endoftext|>world";
    let encoded = tokenizer.encode(text);

    assert!(encoded.contains(&TokenId::new(50256)));

    let decoded = tokenizer.decode(&encoded).unwrap();
    assert_eq!(decoded, text);
}

#[test]
fn test_regex_bpe_add_special_token() {
    let dataset = "test";
    let config = RegexBPETokenizerConfig::build(256, None).unwrap();
    let mut tokenizer = config.train(dataset).unwrap();

    tokenizer.add_special_token("<|start|>".to_string(), TokenId::new(1000));

    assert_eq!(tokenizer.special_tokens().len(), 1);
    assert_eq!(tokenizer.special_tokens().get("<|start|>"), Some(&TokenId::new(1000)));
}

#[test]
fn test_regex_bpe_decode_unknown_token() {
    let dataset = "test";
    let config = RegexBPETokenizerConfig::build(256, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let result = tokenizer.decode(&[TokenId::new(999)]);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "Unknown token ID 999");
}

#[test]
fn test_regex_bpe_empty_input() {
    let dataset = "hello world";
    let config = RegexBPETokenizerConfig::build(260, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let encoded = tokenizer.encode("");
    assert!(encoded.is_empty());

    let decoded = tokenizer.decode(&[]).unwrap();
    assert_eq!(decoded, "");
}

#[test]
fn test_regex_bpe_save_load_full_flow() {
    use std::path::PathBuf;

    let dataset = "hello world hello world hello";
    let config = RegexBPETokenizerConfig::build(260, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let path = PathBuf::from("regex_model.stok");
    tokenizer.save(&path).unwrap();

    let loaded_tokenizer = RegexBPETokenizerConfig::from_merges(100, None)
        .unwrap()
        .load(&path)
        .unwrap();

    assert_eq!(tokenizer.num_merges(), loaded_tokenizer.num_merges());

    assert_eq!(tokenizer.pattern(), loaded_tokenizer.pattern());

    let original = "hello world hello";
    let encoded = loaded_tokenizer.encode(original);
    let decoded = loaded_tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, original);

    std::fs::remove_file(&path).ok(); // clean up
    std::fs::remove_file(&path.with_extension("vocab")).ok();
}

#[test]
fn test_regex_bpe_save_load_with_custom_pattern() {
    use std::path::PathBuf;

    let pattern = r"\w+|\s+|[^\w\s]+";
    let dataset = "hello world! test123";
    let config = RegexBPETokenizerConfig::build(260, Some(pattern)).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let path = PathBuf::from("regex_model_custom.stok");
    tokenizer.save(&path).unwrap();

    let loaded_tokenizer = RegexBPETokenizerConfig::from_merges(100, None)
        .unwrap()
        .load(&path)
        .unwrap();

    assert_eq!(loaded_tokenizer.pattern(), pattern);

    let original = "hello world!";
    let encoded = loaded_tokenizer.encode(original);
    let decoded = loaded_tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, original);

    std::fs::remove_file(&path).ok(); // clean up
    std::fs::remove_file(&path.with_extension("vocab")).ok();
}

#[test]
fn test_regex_bpe_save_load_invalid_extension() {
    let dataset = "test";
    let config = RegexBPETokenizerConfig::build(256, None).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let path = std::path::PathBuf::from("model.txt");
    let result = tokenizer.save(&path);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");
}

#[test]
fn test_regex_bpe_load_invalid_extension() {
    let path = std::path::PathBuf::from("model.txt");
    let config = RegexBPETokenizerConfig::from_merges(10, None).unwrap();
    let result = config.load(&path);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");
}

#[test]
fn test_regex_bpe_multiple_special_tokens() {
    let dataset = "hello world";
    let config = RegexBPETokenizerConfig::build(260, None).unwrap();
    let mut tokenizer = config.train(dataset).unwrap();

    // register multiple special tokens
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
fn test_regex_bpe_special_tokens_at_boundaries() {
    let dataset = "hello world";
    let config = RegexBPETokenizerConfig::build(260, None).unwrap();
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
fn test_regex_bpe_unicode() {
    let config = RegexBPETokenizerConfig::build(260, None).unwrap();
    let dataset = "café résumé café";
    let tokenizer = config.train(dataset).unwrap();

    let original = "café";
    let encoded = tokenizer.encode(original);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, original);

    let original = "hello 🚀 world 🚀";
    let encoded = tokenizer.encode(original);
    let decoded = tokenizer.decode(&encoded).unwrap();
    assert_eq!(decoded, original);
}

#[test]
fn test_regex_bpe_load_missing_pattern_header() {
    use std::io::Write;

    let temp_dir = std::env::temp_dir();
    let path = temp_dir.join("no_header_regex.stok");

    // create file without proper header
    let mut file = File::create(&path).unwrap();
    writeln!(file, "97 98 256").unwrap();

    let config = RegexBPETokenizerConfig::from_merges(10, None).unwrap();
    let result = config.load(&path);

    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("Expected pattern header"));

    std::fs::remove_file(&path).ok();
    std::fs::remove_file(&path.with_extension("vocab")).ok();
}
