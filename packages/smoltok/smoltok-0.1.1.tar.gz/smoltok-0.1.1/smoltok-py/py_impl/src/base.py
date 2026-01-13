import itertools
from abc import ABC, abstractmethod
from typing import Final

MIN_VOCAB_SIZE: Final[int] = 256


def validate_vocab_size(vocab_size: int) -> None:
    if vocab_size < MIN_VOCAB_SIZE:
        raise ValueError(f"Vocab size must be at least {MIN_VOCAB_SIZE}, got {vocab_size}")


class TokenizerBase(ABC):
    def __init__(self, merges: dict[tuple[int, int], int]) -> None:
        self._merges = merges
        self._vocab = self._build_vocab(merges)

    @property
    def vocab(self) -> dict[int, bytes]:
        return self._vocab

    @property
    def num_merges(self) -> int:
        return len(self._merges)

    @abstractmethod
    def encode(self, text: str) -> list[int]: ...

    @abstractmethod
    def decode(self, tokens: list[int]) -> str: ...

    @staticmethod
    def str_to_utf8(text: str) -> list[int]:
        """Convert a string to a list of integer UTF-8 bytes."""
        return list(map(int, text.encode("utf-8")))

    @staticmethod
    def get_pair_count(
        tokens: list[int], counts: dict[tuple[int, int], int] | None = None
    ) -> dict[tuple[int, int], int]:
        """Get counts of all adjacent token pairs in a sequence, optionally starting from a given `counts` dict."""
        counts = counts or {}
        for pair in itertools.pairwise(tokens):
            counts[pair] = counts.get(pair, 0) + 1
        return counts

    @staticmethod
    def merge(tokens: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
        """Replace all consecutive occurrences of a `pair` in `tokens` with a `new_id`."""
        new_ids = []
        i = 0

        while i < len(tokens):
            if i < len(tokens) - 1 and tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
                new_ids.append(new_id)
                i += 2
            else:
                new_ids.append(tokens[i])
                i += 1

        return new_ids

    @staticmethod
    def _build_vocab(merges: dict[tuple[int, int], int]) -> dict[int, bytes]:
        """Build a vocabulary from `merges`."""
        vocab = {i: bytes([i]) for i in range(256)}
        for (t0, t1), i in merges.items():  # need to iterate in order of insertion, guaranteed in Python 3.7+
            vocab[i] = vocab[t0] + vocab[t1]
        return vocab

    @classmethod
    def bpe_encode(cls, text: str, merges: dict[tuple[int, int], int]) -> list[int]:
        """
        Encode a text string into a list of token IDs using learned `merges`.
        Moved into base class since both simple and regex tokenizers use this logic.
        """
        tokens = cls.str_to_utf8(text)

        while True:
            pairs = cls.get_pair_count(tokens)
            if not pairs:
                break  # tokens is a sequence of 0 or 1 elements
            pair = min(pairs, key=lambda p: merges.get(p, float("inf")))
            if pair not in merges:
                break  # nothing to merge

            tokens = cls.merge(tokens, pair, merges[pair])

        return tokens
