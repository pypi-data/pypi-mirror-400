import pytest

from py_impl.src import RegexBPETokenizerConfig as PyRegexBPETokenizerConfig
from smoltok import ParallelRegexBPETokenizerConfig as RsParallelRegexBPETokenizerConfig
from smoltok import RegexBPETokenizerConfig as RsRegexBPETokenizerConfig


@pytest.fixture(
    params=[
        pytest.param(PyRegexBPETokenizerConfig, id="Python"),
        pytest.param(RsRegexBPETokenizerConfig, id="Rust"),
        pytest.param(RsParallelRegexBPETokenizerConfig, id="ParallelRegexBPE-Rust"),
    ]
)
def trained_tokenizer(request):
    """Create a trained tokenizer with special tokens registered."""
    config_cls = request.param
    config = config_cls.build(vocab_size=256 + 3)
    tokenizer = config.train("hello world hello world hello")
    tokenizer.register_special_tokens(
        {
            "<|start|>": 259,
            "<|end|>": 260,
            "<|pad|>": 261,
        }
    )
    return tokenizer


def test_encode_decode_with_special_tokens(trained_tokenizer):
    """Test that special tokens are encoded and decoded correctly."""
    text = "<|start|>hello world<|end|>"

    encoded = trained_tokenizer.encode(text)
    decoded = trained_tokenizer.decode(encoded)

    assert decoded == text


def test_special_token_not_split_by_bpe(trained_tokenizer):
    """Test that special tokens are not split by BPE merges."""
    text = "<|start|>hello<|end|>"

    encoded = trained_tokenizer.encode(text)

    # The special tokens should each be a single token ID
    assert 259 in encoded  # <|start|>
    assert 260 in encoded  # <|end|>


def test_multiple_special_tokens_in_sequence(trained_tokenizer):
    """Test encoding/decoding with multiple consecutive special tokens."""
    text = "<|start|><|pad|><|pad|><|end|>"

    encoded = trained_tokenizer.encode(text)
    decoded = trained_tokenizer.decode(encoded)

    assert decoded == text
    assert encoded.count(259) == 1  # one <|start|>
    assert encoded.count(260) == 1  # one <|end|>
    assert encoded.count(261) == 2  # two <|pad|>


def test_special_tokens_mixed_with_regular_text(trained_tokenizer):
    """Test special tokens mixed with regular text."""
    text = "<|start|>hello world<|pad|>more text<|end|>"

    encoded = trained_tokenizer.encode(text)
    decoded = trained_tokenizer.decode(encoded)

    assert decoded == text


def test_encode_text_without_special_tokens(trained_tokenizer):
    """Test that regular text without special tokens still works."""
    text = "hello world"

    encoded = trained_tokenizer.encode(text)
    decoded = trained_tokenizer.decode(encoded)

    assert decoded == text


@pytest.mark.parametrize(
    "config_cls",
    [
        pytest.param(PyRegexBPETokenizerConfig, id="Python"),
        pytest.param(RsRegexBPETokenizerConfig, id="Rust"),
        pytest.param(RsParallelRegexBPETokenizerConfig, id="ParallelRust"),
    ],
)
def test_decode_special_token_ids_directly(config_cls):
    """Test decoding token IDs that correspond to special tokens."""
    config = config_cls.build(vocab_size=256)
    tokenizer = config.train("abc")
    tokenizer.register_special_tokens(
        {
            "<|eos|>": 256,
            "<|bos|>": 257,
        }
    )

    # Decode a sequence containing special token IDs
    decoded = tokenizer.decode([257, 97, 98, 99, 256])  # <|bos|>abc<|eos|>

    assert decoded == "<|bos|>abc<|eos|>"
