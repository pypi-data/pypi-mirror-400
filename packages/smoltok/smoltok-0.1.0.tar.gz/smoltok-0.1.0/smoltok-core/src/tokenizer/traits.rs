use super::{MergeRule, TokenId};
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;
use std::str::FromStr;

/// A trait defining the behavior of a tokenizer for encoding and decoding.
pub trait Tokenizer {
    /// Error that could happen during decoding.
    type DecodingError: std::error::Error;

    fn merges(&self) -> &[MergeRule];

    /// Returns the number of merge rules learned during training.
    fn num_merges(&self) -> usize {
        self.merges().len()
    }

    fn vocab(&self) -> &HashMap<TokenId, Vec<u8>>;

    /// Encodes a string into a sequence of token IDs.
    ///
    /// # Arguments
    ///
    /// * `text` - The string to encode.
    ///
    /// # Returns
    ///
    /// * A vector of token IDs.
    fn encode(&self, text: &str) -> Vec<TokenId>;

    /// Decodes a sequence of token IDs back into a string.
    ///
    /// # Arguments
    ///
    /// * `tokens` - The sequence of token IDs.
    ///
    /// # Returns
    ///
    /// * `Ok(String)` the decoded string.
    /// * `Err(DecodingError)` if decoding fails.
    fn decode(&self, tokens: &[TokenId]) -> Result<String, Self::DecodingError>;
}

/// A trait for training a tokenizer from a dataset.
///
/// This trait is separate from `Tokenizer` to allow configuration types to be trainable
/// while the resulting tokenizer handles encoding/decoding.
pub trait Trainable {
    /// The tokenizer type produced by training.
    type Output: Tokenizer;
    /// Error that could happen during training.
    type TrainingError: std::error::Error;

    // TODO: support more dataset kinds, like iterator of strings, folder with files, etc.

    /// Trains a tokenizer on a given dataset to a target vocabulary size.
    ///
    /// # Arguments
    ///
    /// * `dataset` - The training data as a string.
    ///
    /// # Returns
    /// * `Ok(Self::Output)` if the tokenizer was trained successfully.
    /// * `Err(TrainingError)` if training fails.
    fn train(&self, dataset: &str) -> Result<Self::Output, Self::TrainingError>;
}

pub fn verify_stok_extension(path: &Path) -> Result<(), std::io::Error> {
    match path.extension().and_then(|s| s.to_str()) {
        Some("stok") => Ok(()),
        _ => Err(std::io::Error::new(
            std::io::ErrorKind::InvalidInput,
            "File must have .stok extension",
        )),
    }
}

/// Save merges
pub fn save_merges(writer: &mut dyn Write, merges: &[MergeRule]) -> Result<(), std::io::Error> {
    for merge_rule in merges {
        writeln!(writer, "{}", merge_rule)?;
    }

    writer.flush()?;

    Ok(())
}

/// Save vocab in format token0 + token1: token2
pub fn save_vocab(path: &Path, merges: &[MergeRule], vocab: &HashMap<TokenId, Vec<u8>>) -> Result<(), std::io::Error> {
    let file = File::create(path)?;
    let mut writer = BufWriter::new(file);

    for merge_rule in merges {
        let first_bytes = vocab.get(&merge_rule.pair().first()).unwrap();
        let second_bytes = vocab.get(&merge_rule.pair().second()).unwrap();
        let new_bytes = vocab.get(&merge_rule.new_id()).unwrap();

        writeln!(
            writer,
            "{} + {}: {}",
            String::from_utf8_lossy(first_bytes.as_slice()),
            String::from_utf8_lossy(second_bytes.as_slice()),
            String::from_utf8_lossy(new_bytes.as_slice())
        )?;
    }

    writer.flush()?;
    Ok(())
}

/// Parses merge rules from an iterator of lines.
///
/// # Arguments
///
/// * `lines` - An iterator yielding (line_number, line_content) tuples.
///   Line numbers are used for error messages.
///
/// # Returns
///
/// * `Ok(Vec<MergeRule>)` containing the parsed merge rules.
/// * `Err(std::io::Error)` if any line contains invalid merge rule syntax.
pub fn parse_merges<I>(lines: I) -> Result<Vec<MergeRule>, std::io::Error>
where
    I: Iterator<Item = (usize, Result<String, std::io::Error>)>,
{
    let mut merges = Vec::new();
    for (line_num, line) in lines {
        let line = line?;

        if line.trim().is_empty() {
            continue; // skip empty lines
        }

        let merge_rule = MergeRule::from_str(&line).map_err(|e| {
            std::io::Error::new(std::io::ErrorKind::InvalidData, format!("Line {}: {}", line_num + 1, e))
        })?;

        merges.push(merge_rule);
    }

    Ok(merges)
}

/// A trait for serializing a tokenizer to a file.
///
/// This trait provides a default implementation for saving tokenizer merge rules
/// to a `.stok` file format.
pub trait Serializable: Tokenizer {
    /// Saves the tokenizer's merge rules to a `.stok` file and vocabulary to a `.vocab` file.
    ///
    /// # Arguments
    ///
    /// * `path` - The path to save the tokenizer. Must have a `.stok` extension.
    ///
    /// # Returns
    ///
    /// * `Ok(())` if the tokenizer was saved successfully.
    /// * `Err(std::io::Error)` if the file extension is invalid or writing fails.
    fn save(&self, path: &Path) -> Result<(), std::io::Error>;
}

/// A trait for deserializing a tokenizer from a file.
///
/// This trait provides functionality for loading tokenizer merge rules from a `.stok` file format.
pub trait Deserializable {
    /// The tokenizer type produced by loading.
    type Output: Tokenizer;

    /// Loads a tokenizer from a file.
    ///
    /// # Arguments
    ///
    /// * `path` - The path to load the tokenizer from. Must have a `.stok` extension.
    ///
    /// # Returns
    ///
    /// * `Ok(Self::Output)` if the tokenizer was loaded successfully.
    /// * `Err(std::io::Error)` if the file extension is invalid or reading fails.
    fn load(&self, path: &Path) -> Result<Self::Output, std::io::Error>;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_verify_stok_extension_valid() {
        let path = Path::new("model.stok");
        assert!(verify_stok_extension(path).is_ok());
    }

    #[test]
    fn test_verify_stok_extension_double_extension() {
        let path = Path::new("model.backup.stok");
        assert!(verify_stok_extension(path).is_ok());
    }

    #[test]
    fn test_verify_stok_extension_valid_with_path() {
        let path = Path::new("/some/path/to/model.stok");
        assert!(verify_stok_extension(path).is_ok());
    }

    #[test]
    fn test_verify_stok_extension_invalid_txt() {
        let path = Path::new("model.txt");
        let result = verify_stok_extension(path);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");

        let path = Path::new("model.json");
        let result = verify_stok_extension(path);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");

        let path = Path::new("model");
        let result = verify_stok_extension(path);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().to_string(), "File must have .stok extension");
    }
}
