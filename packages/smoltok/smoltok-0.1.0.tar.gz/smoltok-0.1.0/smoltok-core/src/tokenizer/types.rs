use std::fmt;
use std::fmt::Formatter;
use std::str::FromStr;

pub const MIN_VOCAB_SIZE: u32 = 256;

/// Represents a unique identifier for a token.
///
/// Token IDs 0-255 are reserved for single-byte tokens (raw bytes).
/// IDs 256 and above are used for merged tokens created during BPE training.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct TokenId(u32);

impl TokenId {
    /// Creates a new `TokenId` with the given value.
    ///
    /// # Arguments
    ///
    /// * `value` - The raw numeric value for this token ID.
    pub fn new(value: u32) -> Self {
        Self(value)
    }

    /// Creates a `TokenId` for a newly merged token.
    ///
    /// This offsets the value by 256 to avoid colliding with
    /// the reserved single-byte token IDs (0-255).
    ///
    /// # Arguments
    ///
    /// * `value` - The merge index (0-based), which will be offset by 256.
    pub fn for_new_token(value: u32) -> Self {
        Self(value + MIN_VOCAB_SIZE)
    }

    /// Returns the raw numeric value of this token ID.
    pub fn value(&self) -> u32 {
        self.0
    }
}

impl std::fmt::Display for TokenId {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// Represents a pair of token IDs.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
pub struct TokenPair(TokenId, TokenId);

impl TokenPair {
    /// Creates a new `TokenPair`.
    pub fn new(first: TokenId, second: TokenId) -> Self {
        Self(first, second)
    }

    /// Returns the first token in the pair.
    pub fn first(&self) -> TokenId {
        self.0
    }

    /// Returns the second token in the pair.
    pub fn second(&self) -> TokenId {
        self.1
    }

    /// Returns the pair as a tuple (first, second).
    pub fn as_tuple(&self) -> (TokenId, TokenId) {
        (self.0, self.1)
    }

    /// Returns a new `MergeRule` with the given new token ID.
    pub fn with_new_id(self, new_id: TokenId) -> MergeRule {
        MergeRule::new(self, new_id)
    }

    /// Checks if the given tokens match this pair.
    ///
    /// Returns `true` if `first` equals `self.first()` and `second` equals `self.second()`.
    pub fn matches(&self, first: Option<&TokenId>, second: Option<&TokenId>) -> bool {
        first == Some(&self.first()) && second == Some(&self.second())
    }
}

/// Represents a BPE merge rule: a token pair and the new token ID it merges into.
#[derive(Clone, Copy, Debug)]
pub struct MergeRule {
    pair: TokenPair,
    new_id: TokenId,
}

impl MergeRule {
    /// Creates a new `MergeRule`.
    ///
    /// # Arguments
    ///
    /// * `pair` - The `TokenPair` to be merged.
    /// * `new_id` - The new token ID assigned to this merged pair.
    pub fn new(pair: TokenPair, new_id: TokenId) -> Self {
        Self { pair, new_id }
    }

    /// Returns the underlying `TokenPair`.
    pub fn pair(&self) -> &TokenPair {
        &self.pair
    }

    /// Returns the new token ID for this pair.
    pub fn new_id(&self) -> TokenId {
        self.new_id
    }
}

impl fmt::Display for MergeRule {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{} {} {}",
            self.pair.first().value(),
            self.pair.second().value(),
            self.new_id.value()
        )
    }
}

#[derive(Debug)]
pub struct ParseMergeRuleError(String);

impl std::error::Error for ParseMergeRuleError {}

impl fmt::Display for ParseMergeRuleError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Failed to parse MergeRule: {}", self.0)
    }
}

impl FromStr for MergeRule {
    type Err = ParseMergeRuleError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let parts: Vec<&str> = s.split_whitespace().collect();

        if parts.len() != 3 {
            return Err(ParseMergeRuleError(format!("Expected 3 values, found {}", parts.len())));
        }

        let first = parts[0]
            .parse::<u32>()
            .map_err(|e| ParseMergeRuleError(format!("Failed to parse first token ID: {}", e)))?;

        let second = parts[1]
            .parse::<u32>()
            .map_err(|e| ParseMergeRuleError(format!("Failed to parse second token ID: {}", e)))?;

        let new_id = parts[2]
            .parse::<u32>()
            .map_err(|e| ParseMergeRuleError(format!("Failed to parse new token ID: {}", e)))?;

        Ok(TokenPair::new(TokenId::new(first), TokenId::new(second)).with_new_id(TokenId::new(new_id)))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_token_id_new_and_value() {
        let token = TokenId::new(42);
        assert_eq!(token.value(), 42);
    }

    #[test]
    fn test_token_id_for_new_token() {
        // for_new_token offsets by MIN_VOCAB_SIZE (256)
        let token = TokenId::for_new_token(0);
        assert_eq!(token.value(), 256);

        let token = TokenId::for_new_token(10);
        assert_eq!(token.value(), 266);
    }

    #[test]
    fn test_token_pair_matches_true() {
        let pair = TokenPair::new(TokenId::new(1), TokenId::new(2));
        let first = TokenId::new(1);
        let second = TokenId::new(2);

        assert!(pair.matches(Some(&first), Some(&second)));

        let pair = TokenPair::new(TokenId::new(1), TokenId::new(2));
        let first = TokenId::new(3);
        let second = TokenId::new(4);

        assert!(!pair.matches(Some(&first), Some(&second)));
        assert!(!pair.matches(None, Some(&second)));
        assert!(!pair.matches(Some(&first), None));
    }

    #[test]
    fn test_merge_rule_from_str_valid() {
        let rule: MergeRule = "97 98 256".parse().unwrap();

        assert_eq!(rule.pair().first(), TokenId::new(97));
        assert_eq!(rule.pair().second(), TokenId::new(98));
        assert_eq!(rule.new_id(), TokenId::new(256));
    }

    #[test]
    fn test_merge_rule_from_str_with_extra_whitespace() {
        let rule: MergeRule = "  97   98   256  ".parse().unwrap();

        assert_eq!(rule.pair().first(), TokenId::new(97));
        assert_eq!(rule.pair().second(), TokenId::new(98));
        assert_eq!(rule.new_id(), TokenId::new(256));
    }

    #[test]
    fn test_merge_rule_from_str_invalid_too_few_or_many_values() {
        let result = "97 98".parse::<MergeRule>();
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Expected 3 values"));

        let result = "97 98 256 300".parse::<MergeRule>();
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Expected 3 values"));

        let result = "".parse::<MergeRule>();
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Expected 3 values"));
    }

    #[test]
    fn test_merge_rule_from_str_invalid_non_numeric() {
        let result = "abc 98 256".parse::<MergeRule>();
        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .to_string()
                .contains("Failed to parse first token ID")
        );
    }

    #[test]
    fn test_merge_rule_from_str_invalid_second_non_numeric() {
        let result = "97 def 256".parse::<MergeRule>();
        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .to_string()
                .contains("Failed to parse second token ID")
        );
    }

    #[test]
    fn test_merge_rule_from_str_invalid_third_non_numeric() {
        let result = "97 98 xyz".parse::<MergeRule>();
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Failed to parse new token ID"));
    }

    #[test]
    fn test_merge_rule_display_from_str_roundtrip() {
        let original = MergeRule::new(TokenPair::new(TokenId::new(100), TokenId::new(200)), TokenId::new(300));

        let displayed = format!("{}", original);
        let parsed: MergeRule = displayed.parse().unwrap();

        assert_eq!(parsed.pair().first(), original.pair().first());
        assert_eq!(parsed.pair().second(), original.pair().second());
        assert_eq!(parsed.new_id(), original.new_id());
    }
}
