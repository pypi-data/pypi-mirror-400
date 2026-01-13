from __future__ import annotations

from typing import Final

import regex

from .base import MIN_VOCAB_SIZE, TokenizerBase, validate_vocab_size

GPT4_SPLIT_PATTERN: Final[str] = (
    r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""
)


class RegexBPETokenizerConfig:
    """Configuration for training a regex-based BPE tokenizer."""

    def __init__(self, vocab_size: int, pattern: str | None = None) -> None:
        validate_vocab_size(vocab_size)
        self._vocab_size = vocab_size
        self._pattern: str = pattern or GPT4_SPLIT_PATTERN
        self._compiled_pattern = regex.compile(self._pattern)

    @classmethod
    def build(cls, vocab_size: int, pattern: str | None = None) -> RegexBPETokenizerConfig:
        return cls(vocab_size, pattern)

    def train(self, dataset: str) -> RegexBPETokenizer:
        dataset_chunks: list[str] = regex.findall(self._compiled_pattern, dataset)
        chunks_tokens: list[list[int]] = [TokenizerBase.str_to_utf8(chunk) for chunk in dataset_chunks]
        merges: dict[tuple[int, int], int] = {}

        n_iterations = self._vocab_size - MIN_VOCAB_SIZE

        for i in range(n_iterations):
            pair_counts: dict[tuple[int, int], int] = {}
            for tokens in chunks_tokens:
                pair_counts = TokenizerBase.get_pair_count(tokens, pair_counts)

            if not pair_counts:
                break

            most_common_pair = max(pair_counts, key=pair_counts.__getitem__)
            merges[most_common_pair] = MIN_VOCAB_SIZE + i
            chunks_tokens = [
                TokenizerBase.merge(tokens, most_common_pair, MIN_VOCAB_SIZE + i) for tokens in chunks_tokens
            ]

        return RegexBPETokenizer(merges, self._pattern)


class RegexBPETokenizer(TokenizerBase):
    """Regex-based BPE tokenizer that supports regex patterns and special tokens."""

    def __init__(self, merges: dict[tuple[int, int], int], pattern: str | None = None) -> None:
        super().__init__(merges)
        self._pattern: str = pattern or GPT4_SPLIT_PATTERN
        self._compiled_pattern = regex.compile(self._pattern)
        self._special_tokens: dict[str, int] = {}

    def register_special_tokens(self, special_tokens: dict[str, int]) -> None:
        self._special_tokens.update(special_tokens)

    def encode(self, text: str) -> list[int]:
        if not self._special_tokens:
            return self._encode_ordinary(text)

        special_tokens_pattern_core = "|".join(str(regex.escape(token)) for token in self._special_tokens)
        chunks = regex.split(f"({special_tokens_pattern_core})", text)
        tokens: list[int] = []
        for chunk in chunks:
            if chunk in self._special_tokens:
                tokens.append(self._special_tokens[chunk])
            else:
                tokens.extend(self._encode_ordinary(chunk))

        return tokens

    def _encode_ordinary(self, data: str) -> list[int]:
        """Encode without handling special tokens."""
        chunks: list[str] = regex.findall(self._compiled_pattern, data)
        return [token for chunk in chunks for token in self._encode_chunk(chunk)]

    def _encode_chunk(self, chunk: str) -> list[int]:
        return TokenizerBase.bpe_encode(chunk, self._merges)

    def decode(self, tokens: list[int]) -> str:
        special_tokens_inverted: dict[int, bytes] = {
            token_id: token.encode("utf-8") for token, token_id in self._special_tokens.items()
        }

        token_bytes = bytearray([])
        for token in tokens:
            if token in self._vocab:
                token_bytes.extend(self._vocab[token])
            elif token in special_tokens_inverted:
                token_bytes.extend(special_tokens_inverted[token])
            else:
                raise ValueError(f"Unknown token: {token}")

        return token_bytes.decode("utf-8", errors="replace")
