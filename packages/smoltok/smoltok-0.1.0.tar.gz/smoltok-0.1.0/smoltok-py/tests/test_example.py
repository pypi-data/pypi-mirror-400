import random

import pytest

from py_impl.bench.utils.charsets import CHARSET_MULTILINGUAL
from smoltok import ParallelRegexBPETokenizerConfig, RegexBPETokenizerConfig, SimpleBPETokenizerConfig


@pytest.mark.parametrize(
    "config_cls,name",
    [
        pytest.param(SimpleBPETokenizerConfig, "SimpleBPETokenizer", id="SimpleBPE"),
        pytest.param(RegexBPETokenizerConfig, "RegexBPETokenizer", id="RegexBPE"),
        pytest.param(ParallelRegexBPETokenizerConfig, "ParallelRegexBPETokenizer", id="ParallelRegexBPE"),
    ],
)
def test_example_flow(config_cls, name: str):
    dataset = "aaabdaaabc"
    n_merges = 3
    vocab_size = 256 + n_merges
    print(f"\n\nTraining {name} on '{dataset}' with {n_merges} merges (vocab_size={vocab_size})")
    config = config_cls.build(vocab_size)
    tokenizer = config.train(dataset)

    original = "aaabdaaabcaaab"
    encoded = tokenizer.encode(original)
    print(f"Encoded '{original}': {encoded}")

    decoded = tokenizer.decode(encoded)
    print(f"Decoded {encoded} '{decoded}'")

    assert decoded == original

    k = 15
    print(f"\nTesting random multilingual string with length {k}")
    random_str = "".join(random.choices(CHARSET_MULTILINGUAL, k=k))
    print(f"Original random string: {random_str}")
    encoded = tokenizer.encode(random_str)
    print(f"Encoded random string: {encoded}")
    decoded = tokenizer.decode(encoded)
    print(f"Decoded random string: {decoded}")
    assert decoded == random_str
