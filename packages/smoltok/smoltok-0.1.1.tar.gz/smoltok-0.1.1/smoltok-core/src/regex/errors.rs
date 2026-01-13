use crate::tokenizer::VocabSizeTooSmall;
use std::fmt;

/// Error type for regex compilation failures.
#[derive(Debug)]
pub struct RegexCompilationError(pub String);

impl std::error::Error for RegexCompilationError {}

impl fmt::Display for RegexCompilationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Failed to compile regex pattern: {}", self.0)
    }
}

/// Error type for RegexBPETokenizer configuration.
#[derive(Debug)]
pub enum RegexBPETokenizerConfigError {
    /// The vocabulary size is too small.
    VocabSizeTooSmall(VocabSizeTooSmall),
    /// The regex pattern failed to compile.
    RegexCompilationError(RegexCompilationError),
}

impl std::error::Error for RegexBPETokenizerConfigError {}

impl fmt::Display for RegexBPETokenizerConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::VocabSizeTooSmall(e) => write!(f, "{}", e),
            Self::RegexCompilationError(e) => write!(f, "{}", e),
        }
    }
}

impl From<VocabSizeTooSmall> for RegexBPETokenizerConfigError {
    fn from(e: VocabSizeTooSmall) -> Self {
        Self::VocabSizeTooSmall(e)
    }
}

impl From<RegexCompilationError> for RegexBPETokenizerConfigError {
    fn from(e: RegexCompilationError) -> Self {
        Self::RegexCompilationError(e)
    }
}
