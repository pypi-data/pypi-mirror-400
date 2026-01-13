use std::fmt::Formatter;

use super::{MIN_VOCAB_SIZE, TokenId};

/// The requested token ID is unknown.
#[derive(Debug)]
pub struct UnknownTokenId(pub TokenId);

impl std::error::Error for UnknownTokenId {}

impl std::fmt::Display for UnknownTokenId {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "Unknown token ID {}", self.0)
    }
}

/// The requested vocabulary size is too small.
/// BPE requires at least 256 tokens to represent all single-byte values.
#[derive(Debug)]
pub struct VocabSizeTooSmall(pub u32);

impl VocabSizeTooSmall {
    /// Returns `Err` if size is too small, `Ok(())` otherwise
    pub fn check(size: u32) -> Result<(), Self> {
        if size < MIN_VOCAB_SIZE {
            return Err(Self(size));
        }
        Ok(())
    }
}

impl std::error::Error for VocabSizeTooSmall {}

impl std::fmt::Display for VocabSizeTooSmall {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "Vocab size must be at least {MIN_VOCAB_SIZE}, got {}", self.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_unknown_token_id_display() {
        let error = UnknownTokenId(TokenId::new(500));
        assert_eq!(format!("{}", error), "Unknown token ID 500");

        let error = UnknownTokenId(TokenId::new(0));
        assert_eq!(format!("{}", error), "Unknown token ID 0");
    }

    #[test]
    fn test_vocab_size_too_small_display() {
        let error = VocabSizeTooSmall(100);
        assert_eq!(format!("{}", error), "Vocab size must be at least 256, got 100");

        let error = VocabSizeTooSmall(0);
        assert_eq!(format!("{}", error), "Vocab size must be at least 256, got 0");
    }

    #[test]
    fn test_vocab_size_too_small_check() {
        assert!(VocabSizeTooSmall::check(0).is_err());
        assert!(VocabSizeTooSmall::check(100).is_err());
        assert!(VocabSizeTooSmall::check(255).is_err());

        assert!(VocabSizeTooSmall::check(256).is_ok());
        assert!(VocabSizeTooSmall::check(257).is_ok());
        assert!(VocabSizeTooSmall::check(1000).is_ok());
    }
}
