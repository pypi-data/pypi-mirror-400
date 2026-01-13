import pytest

from py_impl.src import RegexBPETokenizerConfig as PyRegexBPETokenizerConfig
from py_impl.src import SimpleBPETokenizerConfig as PySimpleBPETokenizerConfig
from smoltok import ParallelRegexBPETokenizerConfig as RsParallelRegexBPETokenizerConfig
from smoltok import RegexBPETokenizerConfig as RsRegexBPETokenizerConfig
from smoltok import SimpleBPETokenizerConfig as RsSimpleBPETokenizerConfig


@pytest.fixture
def simple_dataset() -> str:
    return "aaabdaaabc"


@pytest.fixture
def simple_regex_dataset() -> str:
    return "a1aa1abaa1b"


test_datasets = [
    "",
    "?",
    "hello world!!!? (안녕하세요!) lol123 😉",
]


def test_simple_python(simple_dataset: str):
    config = PySimpleBPETokenizerConfig.build(vocab_size=256 + 3)
    tokenizer = config.train(simple_dataset)

    assert len(tokenizer.vocab) == 256 + 3
    assert tokenizer.vocab[256] == b"aa"
    assert tokenizer.vocab[257] == b"aaa"
    assert tokenizer.vocab[258] == b"aaab"

    assert tokenizer.encode(simple_dataset) == [258, 100, 258, 99]
    assert tokenizer.decode([258, 100, 258, 99]) == simple_dataset


def test_regex_python(simple_regex_dataset: str):
    config = PyRegexBPETokenizerConfig.build(vocab_size=256 + 3)
    tokenizer = config.train(simple_regex_dataset)

    assert len(tokenizer.vocab) == 256 + 3
    assert tokenizer.vocab[256] == b"aa"  # instead of "a1"
    assert tokenizer.vocab[257] == b"ab"
    assert tokenizer.vocab[258] == b"abaa"

    assert tokenizer.encode(simple_regex_dataset) == [97, 49, 256, 49, 258, 49, 98]
    assert tokenizer.decode([97, 49, 256, 49, 258, 49, 98]) == simple_regex_dataset


@pytest.mark.parametrize(
    "config_cls",
    [
        pytest.param(PySimpleBPETokenizerConfig, id="SimpleBPE-Python"),
        pytest.param(PyRegexBPETokenizerConfig, id="RegexBPE-Python"),
        pytest.param(RsSimpleBPETokenizerConfig, id="SimpleBPE-Rust"),
        pytest.param(RsRegexBPETokenizerConfig, id="RegexBPE-Rust"),
        pytest.param(RsParallelRegexBPETokenizerConfig, id="ParallelRegexBPE-Rust"),
    ],
)
@pytest.mark.parametrize("dataset", test_datasets)
def test_encode_decode_identity(config_cls, dataset: str):
    config = config_cls.build(vocab_size=256 + 100)
    tokenizer = config.train(dataset)

    assert tokenizer.decode(tokenizer.encode(dataset)) == dataset


@pytest.mark.parametrize(
    "config_cls",
    [
        pytest.param(PySimpleBPETokenizerConfig, id="SimpleBPE-Python"),
        pytest.param(PyRegexBPETokenizerConfig, id="RegexBPE-Python"),
        pytest.param(RsSimpleBPETokenizerConfig, id="SimpleBPE-Rust"),
        pytest.param(RsRegexBPETokenizerConfig, id="RegexBPE-Rust"),
        pytest.param(RsParallelRegexBPETokenizerConfig, id="ParallelRegexBPE-Rust"),
    ],
)
def test_invalid_vocab_size(config_cls, simple_dataset: str):
    with pytest.raises(ValueError, match="Vocab size must be at least 256, got 255"):
        config_cls.build(255)


@pytest.mark.parametrize(
    "config_cls,expected_vocab_size",
    [
        pytest.param(PySimpleBPETokenizerConfig, 256 + 6, id="SimpleBPE-Python"),
        pytest.param(PyRegexBPETokenizerConfig, 256 + 6, id="RegexBPE-Python"),
    ],
)
def test_too_many_merges_python(config_cls, expected_vocab_size: int, simple_dataset: str):
    """Python implementation exposes vocab dict, so we can check its size."""
    config = config_cls.build(vocab_size=256 + 1_000)
    tokenizer = config.train(simple_dataset)

    assert len(tokenizer.vocab) == expected_vocab_size
    assert simple_dataset == tokenizer.decode(tokenizer.encode(simple_dataset))


@pytest.mark.parametrize(
    "config_cls",
    [
        pytest.param(RsSimpleBPETokenizerConfig, id="SimpleBPE-Rust"),
        pytest.param(RsRegexBPETokenizerConfig, id="RegexBPE-Rust"),
        pytest.param(RsParallelRegexBPETokenizerConfig, id="ParallelRegexBPE-Rust"),
    ],
)
def test_too_many_merges_rust(config_cls, simple_dataset: str):
    """Rust implementation - verify encode/decode identity."""
    config = config_cls.build(vocab_size=256 + 1_000)
    tokenizer = config.train(simple_dataset)

    assert simple_dataset == tokenizer.decode(tokenizer.encode(simple_dataset))


def test_parallel_regex_produces_same_result(simple_regex_dataset: str):
    """Verify that parallel and sequential regex tokenizers produce the same results."""
    sequential_config = RsRegexBPETokenizerConfig.build(vocab_size=256 + 3)
    parallel_config = RsParallelRegexBPETokenizerConfig.build(vocab_size=256 + 3)

    sequential_tokenizer = sequential_config.train(simple_regex_dataset)
    parallel_tokenizer = parallel_config.train(simple_regex_dataset)

    # both should produce the same encoding
    assert sequential_tokenizer.encode(simple_regex_dataset) == parallel_tokenizer.encode(simple_regex_dataset)

    # both should have the same number of merges
    assert sequential_tokenizer.num_merges == parallel_tokenizer.num_merges
