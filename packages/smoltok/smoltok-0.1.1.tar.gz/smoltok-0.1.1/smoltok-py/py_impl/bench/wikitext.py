import os
import time
from typing import Literal

import click

from py_impl.src import RegexBPETokenizerConfig as PythonRegexBPETokenizerConfig
from smoltok import (
    ParallelRegexBPETokenizerConfig as RustParallelRegexBPETokenizerConfig,
)
from smoltok import (
    RegexBPETokenizerConfig as RustRegexBPETokenizerConfig,
)

from .utils import DATA_DIR, MODELS_DIR, string_length_mb


def train(
    kind: Literal["rust", "rust-parallel", "python"], vocab_size: int, *, dataset: str, dataset_name: str
) -> None:
    dataset_mb = string_length_mb(dataset)
    click.echo(
        f"Training {kind.capitalize()} RegexBPETokenizer with vocab_size={vocab_size:,} "
        f"on {dataset_name} dataset ({dataset_mb:.1f} MB)..."
    )
    if kind == "rust":
        config = RustRegexBPETokenizerConfig.build(vocab_size=vocab_size)
    elif kind == "rust-parallel":
        config = RustParallelRegexBPETokenizerConfig.build(vocab_size=vocab_size)
    else:
        config = PythonRegexBPETokenizerConfig.build(vocab_size=vocab_size)

    time_start = time.time()
    tokenizer = config.train(dataset)
    time_end = time.time()

    click.echo(f"Training time: {time_end - time_start:.2f} seconds")

    if kind != "python":
        save_path = os.path.join(MODELS_DIR, f"{dataset_name}-{vocab_size}.stok")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        tokenizer.save(save_path)  # type: ignore - saving for Python is not implemented
        click.echo(f"Saved tokenizer to {save_path}")


@click.command()
@click.option(
    "--vocab-size",
    default=512,
    help="Vocabulary size for the tokenizer.",
    show_default=True,
)
@click.option(
    "--train-python",
    is_flag=True,
    default=False,
    help="Whether to train tokenizer in Python too.",
    show_default=True,
)
def main(vocab_size: int, train_python: bool) -> None:
    """Train tokenizer on wikitext dataset."""
    dataset_name = "wikitext-test"
    path = os.path.join(DATA_DIR, f"{dataset_name}.txt")

    with open(path, encoding="utf-8") as f:
        dataset = f.read()

    train(kind="rust", vocab_size=vocab_size, dataset=dataset, dataset_name=dataset_name)
    train(kind="rust-parallel", vocab_size=vocab_size, dataset=dataset, dataset_name=dataset_name)

    if train_python:
        train(kind="python", vocab_size=vocab_size, dataset=dataset, dataset_name=dataset_name)


if __name__ == "__main__":
    main()
