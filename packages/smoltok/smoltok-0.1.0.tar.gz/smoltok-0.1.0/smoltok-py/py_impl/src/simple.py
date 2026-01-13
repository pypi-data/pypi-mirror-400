from __future__ import annotations

from .base import MIN_VOCAB_SIZE, TokenizerBase, validate_vocab_size


class SimpleBPETokenizerConfig:
    """Configuration for training a simple BPE tokenizer."""

    def __init__(self, vocab_size: int) -> None:
        validate_vocab_size(vocab_size)
        self._vocab_size = vocab_size

    @classmethod
    def build(cls, vocab_size: int) -> SimpleBPETokenizerConfig:
        return cls(vocab_size)

    def train(self, dataset: str) -> SimpleBPETokenizer:
        tokens = TokenizerBase.str_to_utf8(dataset)
        merges: dict[tuple[int, int], int] = {}

        n_iterations = self._vocab_size - MIN_VOCAB_SIZE
        for i in range(n_iterations):
            pair_counts = TokenizerBase.get_pair_count(tokens)
            if not pair_counts:
                break  # tokens is a sequence of 0 or 1 elements
            most_common_pair = max(pair_counts, key=pair_counts.__getitem__)
            merges[most_common_pair] = MIN_VOCAB_SIZE + i
            tokens = TokenizerBase.merge(tokens, most_common_pair, MIN_VOCAB_SIZE + i)

        return SimpleBPETokenizer(merges)


class SimpleBPETokenizer(TokenizerBase):
    """Simple BPE tokenizer that does not support regex patterns and special tokens."""

    def __init__(self, merges: dict[tuple[int, int], int]) -> None:
        super().__init__(merges)

    def encode(self, text: str) -> list[int]:
        return TokenizerBase.bpe_encode(text, self._merges)

    def decode(self, tokens: list[int]) -> str:
        return b"".join(self._vocab[token_id] for token_id in tokens).decode("utf-8", errors="replace")
