import pytest

from smoltok import ParallelRegexBPETokenizerConfig, RegexBPETokenizerConfig, SimpleBPETokenizerConfig


@pytest.mark.parametrize(
    "config_cls",
    [
        pytest.param(SimpleBPETokenizerConfig, id="SimpleBPE"),
        pytest.param(RegexBPETokenizerConfig, id="RegexBPE"),
        pytest.param(ParallelRegexBPETokenizerConfig, id="ParallelRegexBPE"),
    ],
)
def test_bpe_binding(config_cls):
    dataset = "aaabdaaabc"
    vocab_size = 256 + 3
    config = config_cls.build(vocab_size)
    tokenizer = config.train(dataset)

    encoded = tokenizer.encode("aaabdaaabc")
    decoded = tokenizer.decode(encoded)
    assert decoded == dataset


@pytest.mark.parametrize(
    "config_cls",
    [
        pytest.param(SimpleBPETokenizerConfig, id="SimpleBPE"),
        pytest.param(RegexBPETokenizerConfig, id="RegexBPE"),
        pytest.param(ParallelRegexBPETokenizerConfig, id="ParallelRegexBPE"),
    ],
)
def test_bpe_generalization(config_cls):
    dataset = "aaabdaaabc"
    vocab_size = 256 + 3
    config = config_cls.build(vocab_size)
    tokenizer = config.train(dataset)

    original = "aaabdaaabcaaab"
    encoded = tokenizer.encode(original)
    decoded = tokenizer.decode(encoded)

    assert decoded == original


@pytest.mark.parametrize(
    "config_cls",
    [
        pytest.param(SimpleBPETokenizerConfig, id="SimpleBPE"),
        pytest.param(RegexBPETokenizerConfig, id="RegexBPE"),
        pytest.param(ParallelRegexBPETokenizerConfig, id="ParallelRegexBPE"),
    ],
)
def test_invalid_vocab_size(config_cls):
    with pytest.raises(ValueError, match="Vocab size must be at least 256, got 255"):
        config_cls.build(255)
