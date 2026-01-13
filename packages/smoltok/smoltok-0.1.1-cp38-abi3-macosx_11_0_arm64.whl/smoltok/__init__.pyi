"""Type stubs for the smoltok Rust extension module."""

class SimpleBPETokenizerConfig:
    """Configuration for training a simple BPE tokenizer."""

    @staticmethod
    def build(vocab_size: int) -> SimpleBPETokenizerConfig:
        """
        Create a new configuration for training a simple BPE tokenizer from vocab size.

        Args:
            vocab_size: The target vocabulary size (must be at least 256).

        Returns:
            A SimpleBPETokenizerConfig instance.

        Raises:
            ValueError: If vocab_size is less than 256.
        """
        ...

    @staticmethod
    def from_merges(merges: int) -> SimpleBPETokenizerConfig:
        """
        Create a new configuration for training a simple BPE tokenizer from number of merges.

        Args:
            merges: The number of merge operations to learn.

        Returns:
            A SimpleBPETokenizerConfig instance.
        """
        ...

    def train(self, dataset: str) -> SimpleBPETokenizer:
        """
        Train a new BPE tokenizer on the given dataset.

        Args:
            dataset: The text corpus to train on.

        Returns:
            A trained SimpleBPETokenizer instance.
        """
        ...

    def load(self, path: str) -> SimpleBPETokenizer:
        """
        Load a trained SimpleBPETokenizer from a file.

        Args:
            path: Path to the .stok file to load from.

        Returns:
            A SimpleBPETokenizer instance.

        Raises:
            IOError: If the file cannot be read or has invalid format.
        """
        ...

class SimpleBPETokenizer:
    """Simple BPE tokenizer. Does not support regex patterns and special tokens."""

    @property
    def num_merges(self) -> int:
        """Returns the number of merge rules learned during training."""
        ...

    def encode(self, data: str) -> list[int]:
        """
        Encode a string into a list of token IDs.

        Args:
            data: The text to encode.

        Returns:
            A list of integer token IDs.
        """
        ...

    def decode(self, tokens: list[int]) -> str:
        """
        Decode a list of token IDs back into a string.

        Args:
            tokens: A list of integer token IDs.

        Returns:
            The decoded string.
            Invalid UTF-8 sequences are replaced with the Unicode replacement character.
        """
        ...

    def save(self, path: str) -> None:
        """
        Save the tokenizer to a file.

        Args:
            path: Path to save the tokenizer. Must have a .stok extension.

        Raises:
            IOError: If the file cannot be written or has invalid extension.
        """
        ...

class RegexBPETokenizerConfig:
    """Configuration for training a regex-based BPE tokenizer."""

    @staticmethod
    def build(vocab_size: int, pattern: str | None = None) -> RegexBPETokenizerConfig:
        """
        Create a new configuration for training a regex BPE tokenizer from vocab size.

        Args:
            vocab_size: The target vocabulary size (must be at least 256).
            pattern: Optional regex pattern for splitting text. Defaults to GPT-4 pattern.

        Returns:
            A RegexBPETokenizerConfig instance.

        Raises:
            ValueError: If vocab_size is less than 256 or pattern is invalid.
        """
        ...

    @staticmethod
    def from_merges(merges: int, pattern: str | None = None) -> RegexBPETokenizerConfig:
        """
        Create a new configuration for training a regex BPE tokenizer from number of merges.

        Args:
            merges: The number of merge operations to learn.
            pattern: Optional regex pattern for splitting text.

        Returns:
            A RegexBPETokenizerConfig instance.

        Raises:
            ValueError: If pattern is invalid.
        """
        ...

    def train(self, dataset: str) -> RegexBPETokenizer:
        """
        Train a new regex BPE tokenizer on the given dataset.

        Args:
            dataset: The text corpus to train on.

        Returns:
            A trained RegexBPETokenizer instance.
        """
        ...

    def load(self, path: str) -> RegexBPETokenizer:
        """
        Load a trained RegexBPETokenizer from a file.

        Args:
            path: Path to the .stok file to load from.

        Returns:
            A RegexBPETokenizer instance.

        Raises:
            IOError: If the file cannot be read or has invalid format.
        """
        ...

class RegexBPETokenizer:
    """Regex-based BPE tokenizer with support for regex patterns and special tokens."""

    @property
    def num_merges(self) -> int:
        """Returns the number of merge rules learned during training."""
        ...

    @property
    def vocab_size(self) -> int:
        """Returns the vocabulary size (base 256 bytes + merged tokens)."""
        ...

    @property
    def pattern(self) -> str:
        """Returns the regex pattern used for splitting text."""
        ...

    def register_special_tokens(self, special_tokens: dict[str, int]) -> None:
        """
        Register special tokens with the tokenizer.

        Args:
            special_tokens: A dictionary mapping token strings to their IDs.
        """
        ...

    def encode(self, data: str) -> list[int]:
        """
        Encode a string into a list of token IDs.

        Args:
            data: The text to encode.

        Returns:
            A list of integer token IDs.
        """
        ...

    def decode(self, tokens: list[int]) -> str:
        """
        Decode a list of token IDs back into a string.

        Args:
            tokens: A list of integer token IDs.

        Returns:
            The decoded string.
            Invalid UTF-8 sequences are replaced with the Unicode replacement character.
        """
        ...

    def save(self, path: str) -> None:
        """
        Save the tokenizer to a file.

        Args:
            path: Path to save the tokenizer. Must have a .stok extension.

        Raises:
            IOError: If the file cannot be written or has invalid extension.
        """
        ...

class ParallelRegexBPETokenizerConfig:
    """Configuration for training a regex-based BPE tokenizer with parallel training.

    Uses rayon for parallel pair counting during training, which is faster
    for large datasets while producing the same tokenizer as RegexBPETokenizerConfig.
    """

    @staticmethod
    def build(vocab_size: int, pattern: str | None = None) -> ParallelRegexBPETokenizerConfig:
        """
        Create a new configuration for training a parallel regex BPE tokenizer from vocab size.

        Args:
            vocab_size: The target vocabulary size (must be at least 256).
            pattern: Optional regex pattern for splitting text. Defaults to GPT-4 pattern.

        Returns:
            A ParallelRegexBPETokenizerConfig instance.

        Raises:
            ValueError: If vocab_size is less than 256 or pattern is invalid.
        """
        ...

    @staticmethod
    def from_merges(merges: int, pattern: str | None = None) -> ParallelRegexBPETokenizerConfig:
        """
        Create a new configuration for training a parallel regex BPE tokenizer from number of merges.

        Args:
            merges: The number of merge operations to learn.
            pattern: Optional regex pattern for splitting text.

        Returns:
            A ParallelRegexBPETokenizerConfig instance.

        Raises:
            ValueError: If pattern is invalid.
        """
        ...

    def train(self, dataset: str) -> ParallelRegexBPETokenizer:
        """
        Train a new regex BPE tokenizer on the given dataset using parallel processing.

        Args:
            dataset: The text corpus to train on.

        Returns:
            A trained ParallelRegexBPETokenizer instance.
        """
        ...

    def load(self, path: str) -> ParallelRegexBPETokenizer:
        """
        Load a trained ParallelRegexBPETokenizer from a file.

        Args:
            path: Path to the .stok file to load from.

        Returns:
            A ParallelRegexBPETokenizer instance.

        Raises:
            IOError: If the file cannot be read or has invalid format.
        """
        ...

class ParallelRegexBPETokenizer:
    """Parallel regex-based BPE tokenizer with support for regex patterns and special tokens.

    This tokenizer is trained using parallel processing for faster training on large datasets.
    """

    @property
    def num_merges(self) -> int:
        """Returns the number of merge rules learned during training."""
        ...

    @property
    def vocab_size(self) -> int:
        """Returns the vocabulary size (base 256 bytes + merged tokens)."""
        ...

    @property
    def pattern(self) -> str:
        """Returns the regex pattern used for splitting text."""
        ...

    def register_special_tokens(self, special_tokens: dict[str, int]) -> None:
        """
        Register special tokens with the tokenizer.

        Args:
            special_tokens: A dictionary mapping token strings to their IDs.
        """
        ...

    def encode(self, data: str) -> list[int]:
        """
        Encode a string into a list of token IDs.

        Args:
            data: The text to encode.

        Returns:
            A list of integer token IDs.
        """
        ...

    def decode(self, tokens: list[int]) -> str:
        """
        Decode a list of token IDs back into a string.

        Args:
            tokens: A list of integer token IDs.

        Returns:
            The decoded string.
            Invalid UTF-8 sequences are replaced with the Unicode replacement character.
        """
        ...

    def save(self, path: str) -> None:
        """
        Save the tokenizer to a file.

        Args:
            path: Path to save the tokenizer. Must have a .stok extension.

        Raises:
            IOError: If the file cannot be written or has invalid extension.
        """
        ...
