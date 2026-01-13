use smoltok_core::{
    Deserializable, Serializable, SimpleBPETokenizer, SimpleBPETokenizerConfig, TokenId, TokenPair, Tokenizer,
    Trainable,
};

#[test]
fn test_bpe_invalid_vocab_size() {
    let vocab_size = 255;
    let config = SimpleBPETokenizerConfig::build(vocab_size);
    assert!(config.is_err());
    assert_eq!(
        config.unwrap_err().to_string(),
        "Vocab size must be at least 256, got 255"
    );
}

#[test]
fn test_bpe_zero_merges() {
    let dataset = "aaabdaaabc";
    let vocab_size = 256;
    let config = SimpleBPETokenizerConfig::build(vocab_size).unwrap();
    let tokenizer = config.train(dataset).unwrap();
    assert_eq!(tokenizer.num_merges(), 0);
    assert_eq!(tokenizer.vocab().len(), 256);

    let original = "aaabdaaabc";
    let encoded = tokenizer.encode(original);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();

    assert_eq!(decoded, original);
}

#[test]
fn test_bpe_full_flow() {
    let dataset = "aaabdaaabc";
    let vocab_size = 256 + 3;
    let config = SimpleBPETokenizerConfig::build(vocab_size).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    assert_eq!(tokenizer.vocab().len(), 259);

    let original = "aaabdaaabcaaab";
    let encoded = tokenizer.encode(original);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();

    assert_eq!(decoded, original);
}

#[test]
fn test_bpe_decode_unknown_token_id() {
    let dataset = "aaabdaaabc";
    let vocab_size = 256 + 3;
    let config = SimpleBPETokenizerConfig::build(vocab_size).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    let unknown_token_id = TokenId::new(300);
    let result = tokenizer.decode(&[unknown_token_id]);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "Unknown token ID 300");
}

#[test]
fn test_bpe_save_load() {
    let dataset = "aaabdaaabc";
    let vocab_size = 256 + 3;
    let config = SimpleBPETokenizerConfig::build(vocab_size).unwrap();
    let tokenizer = config.train(dataset).unwrap();

    // save to a temporary file
    let temp_dir = std::env::temp_dir();
    let temp_path = temp_dir.join("test_tokenizer.stok");
    tokenizer.save(&temp_path).unwrap();

    // load the tokenizer back
    let loaded_tokenizer = config.load(&temp_path).unwrap();

    assert_eq!(loaded_tokenizer.num_merges(), tokenizer.num_merges());

    let test_text = "aaabdaaabcaaab";
    let original_encoded = tokenizer.encode(test_text);
    let loaded_encoded = loaded_tokenizer.encode(test_text);
    assert_eq!(original_encoded, loaded_encoded);

    let decoded = loaded_tokenizer.decode(&loaded_encoded).unwrap();
    assert_eq!(decoded, test_text);

    std::fs::remove_file(&temp_path).ok(); // cleanup
    std::fs::remove_file(&temp_path.with_extension("vocab")).ok();
}

#[test]
fn test_bpe_save_invalid_extension() {
    let config = SimpleBPETokenizerConfig::build(260).unwrap();
    let tokenizer = config.train("test").unwrap();

    let path = std::path::PathBuf::from("model.txt");
    let result = tokenizer.save(&path);

    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");
}

#[test]
fn test_bpe_load_invalid_extension() {
    let config = SimpleBPETokenizerConfig::build(260).unwrap();
    let path = std::path::PathBuf::from("model.txt");
    let result = config.load(&path);

    assert!(result.is_err());
    assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");
}

#[test]
fn test_bpe_config_from_merges() {
    let config = SimpleBPETokenizerConfig::from_merges(10);
    let dataset = "aaabdaaabcaaab";
    let tokenizer = config.train(dataset).unwrap();

    assert!(tokenizer.num_merges() <= 10);
}

#[test]
fn test_bpe_config_from_merges_zero() {
    let config = SimpleBPETokenizerConfig::from_merges(0);
    let dataset = "hello world";
    let tokenizer = config.train(dataset).unwrap();

    assert_eq!(tokenizer.num_merges(), 0);

    let encoded = tokenizer.encode("hi");
    assert_eq!(encoded.len(), 2);
}

#[test]
fn test_bpe_from_merges_directly() {
    let pair = TokenPair::new(TokenId::new(97), TokenId::new(98)); // 'a' + 'b'
    let rule = pair.with_new_id(TokenId::new(256));
    let merges = vec![rule];

    let tokenizer = SimpleBPETokenizer::from_merges(merges);

    assert_eq!(tokenizer.num_merges(), 1);

    let encoded = tokenizer.encode("ab");
    assert_eq!(encoded, vec![TokenId::new(256)]);

    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, "ab");
}

#[test]
fn test_bpe_empty_input() {
    let config = SimpleBPETokenizerConfig::build(260).unwrap();
    let tokenizer = config.train("hello world").unwrap();

    let encoded = tokenizer.encode("");
    assert!(encoded.is_empty());

    let decoded = tokenizer.decode(&[]).unwrap();
    assert_eq!(decoded, "");
}

#[test]
fn test_bpe_single_char() {
    let config = SimpleBPETokenizerConfig::build(256).unwrap();
    let tokenizer = config.train("a").unwrap();

    let encoded = tokenizer.encode("a");
    assert_eq!(encoded.len(), 1);
    assert_eq!(encoded[0], TokenId::new(97)); // 'a' = 97

    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, "a");
}

#[test]
fn test_bpe_unicode() {
    let config = SimpleBPETokenizerConfig::build(260).unwrap();
    let dataset = "héllo wörld héllo";
    let tokenizer = config.train(dataset).unwrap();

    let original = "héllo";
    let encoded = tokenizer.encode(original);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, original);

    let original = "hello 👋 world 👋";
    let encoded = tokenizer.encode(original);
    let decoded = tokenizer.decode(encoded.as_slice()).unwrap();
    assert_eq!(decoded, original);
}

#[test]
fn test_bpe_training_stops_early() {
    // with a tiny dataset that has only unique bytes, training should stop early
    let config = SimpleBPETokenizerConfig::build(300).unwrap();
    let dataset = "abcdefghijklmnopqrstuvwxyz"; // 26 unique chars, no repeated pairs
    let tokenizer = config.train(dataset).unwrap();

    // should have fewer merges than requested because there are no repeated pairs
    assert!(tokenizer.num_merges() < 44); // 300 - 256 = 44 requested merges
}
