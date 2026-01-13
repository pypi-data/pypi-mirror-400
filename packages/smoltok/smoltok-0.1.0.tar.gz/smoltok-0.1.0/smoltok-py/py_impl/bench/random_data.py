#!/usr/bin/env python3
"""Benchmark script comparing Python vs Rust BPE tokenization performance on randomly generated data."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

import click
import matplotlib.pyplot as plt
import numpy as np

from py_impl.src import RegexBPETokenizerConfig as PythonRegexBPETokenizerConfig
from smoltok import (
    ParallelRegexBPETokenizerConfig as RustParallelRegexBPETokenizerConfig,
)
from smoltok import (
    RegexBPETokenizerConfig as RustRegexBPETokenizerConfig,
)

from .utils import CHARSET_OPTIONS, format_time

MIN_DATA_POINTS_FOR_STD: Final[int] = 2


@dataclass
class BenchmarkResult:
    name: str
    train_times: list[float]
    encode_times: list[float]
    decode_times: list[float]

    @property
    def train_mean(self) -> float:
        return self.mean(self.train_times)

    @property
    def train_std(self) -> float:
        return self.std(self.train_times)

    @property
    def encode_mean(self) -> float:
        return self.mean(self.encode_times)

    @property
    def encode_std(self) -> float:
        return self.std(self.encode_times)

    @property
    def decode_mean(self) -> float:
        return self.mean(self.decode_times)

    @property
    def decode_std(self) -> float:
        return self.std(self.decode_times)

    @classmethod
    def mean(cls, data: list[float]) -> float:
        return sum(data) / len(data)

    @classmethod
    def std(cls, data: list[float]) -> float:
        if len(data) < MIN_DATA_POINTS_FOR_STD:
            return 0.0
        mean = cls.mean(data)
        return (sum((x - mean) ** 2 for x in data) / (len(data) - 1)) ** 0.5


def generate_dataset(size: int, charset: str) -> str:
    """Generate a random dataset from the given character set."""
    return "".join(random.choices(charset, k=size))


def benchmark_tokenizer(
    tokenizer_config_cls,
    *,
    name: str,
    dataset: str,
    vocab_size: int,
    runs: int,
) -> BenchmarkResult:
    """Benchmark a tokenizer implementation."""
    train_times = []
    encode_times = []
    decode_times = []

    for _ in range(runs):
        # Benchmark training (includes config build time)
        config = tokenizer_config_cls.build(vocab_size)
        start = time.perf_counter()
        tokenizer = config.train(dataset)
        train_times.append(time.perf_counter() - start)

        # Benchmark encoding
        start = time.perf_counter()
        encoded = tokenizer.encode(dataset)
        encode_times.append(time.perf_counter() - start)

        # Benchmark decoding
        start = time.perf_counter()
        _ = tokenizer.decode(encoded)
        decode_times.append(time.perf_counter() - start)

    return BenchmarkResult(
        name=name,
        train_times=train_times,
        encode_times=encode_times,
        decode_times=decode_times,
    )


def print_results(results: list[BenchmarkResult], runs: int) -> None:
    """Print benchmark results in a formatted table."""
    if not results:
        return

    num_results = len(results)
    # Calculate widths
    op_width = 15
    res_width = 20
    speedup_width = 15

    # Headers
    headers = ["Operation"] + [r.name for r in results]
    speedup_headers = []
    if num_results > 1:
        # Speedup vs the first result (baseline)
        for r in results[1:]:
            speedup_headers.append(f"{r.name} vs {results[0].name}")

    headers.extend(speedup_headers)

    # Adjust speedup column width if necessary
    if speedup_headers:
        max_header_len = max(len(h) for h in speedup_headers)
        speedup_width = max(speedup_width, max_header_len + 2)

    col_widths = [op_width] + [res_width] * num_results
    if num_results > 1:
        col_widths.extend([speedup_width] * (num_results - 1))

    total_width = sum(col_widths)

    click.echo("\n" + "=" * total_width)
    click.echo("BENCHMARK RESULTS".center(total_width))
    click.echo("=" * total_width)

    # Header
    click.echo("-" * total_width)
    header_row = "".join(h.center(w) for h, w in zip(headers, col_widths, strict=True))
    click.echo(header_row)
    click.echo("-" * total_width)

    def format_result(mean: float, std: float, runs: int) -> str:
        if runs > 1:
            return f"{format_time(mean)} ± {format_time(std)}"
        return format_time(mean)

    def format_speedup(base_mean: float, current_mean: float) -> str:
        speedup = base_mean / current_mean if current_mean > 0 else float("inf")
        return f"{speedup:.1f}x"

    operations = [
        ("Train", lambda r: (r.train_mean, r.train_std)),
        ("Encode", lambda r: (r.encode_mean, r.encode_std)),
        ("Decode", lambda r: (r.decode_mean, r.decode_std)),
    ]

    for op_name, getter in operations:
        row_parts = [op_name.center(op_width)]

        # Values
        means = []
        for r in results:
            mean, std = getter(r)
            means.append(mean)
            row_parts.append(format_result(mean, std, runs).center(res_width))

        # Speedups
        if num_results > 1:
            base_mean = means[0]
            for mean in means[1:]:
                row_parts.append(format_speedup(base_mean, mean).center(speedup_width))

        click.echo("".join(row_parts))

    click.echo("-" * total_width)


def plot_results(title: str, results: list[BenchmarkResult]) -> None:
    if not results:
        return

    operations = ["Train", "Encode", "Decode"]
    x = np.arange(len(operations))
    width = 0.8 / len(results)

    _, ax = plt.subplots(figsize=(10, 6))

    # Standard colors: Python Red, Rust Orange, then others
    default_colors = ["#E74C3C", "#E67E22", "#3498DB", "#2ECC71", "#9B59B6", "#34495E"]

    for i, res in enumerate(results):
        if res.name.lower() == "python":
            color = "#E74C3C"
        elif res.name.lower() == "rust":
            color = "#E67E22"
        else:
            color = default_colors[i % len(default_colors)]

        means = [res.train_mean, res.encode_mean, res.decode_mean]
        stds = [res.train_std, res.encode_std, res.decode_std]

        # Calculate bar position
        # Center the group of bars on x[j]
        # Total width of group = len(results) * width
        # Start offset = - (len(results) * width) / 2
        # Bar i start = Start offset + i * width
        # Center of bar i = Start offset + i * width + width / 2

        group_width = len(results) * width
        offset = (i * width) - (group_width / 2) + (width / 2)

        ax.bar(x + offset, means, width, label=res.name, color=color, yerr=stds, capsize=5)

        # Add speedup annotations relative to the first result (baseline)
        if i > 0:
            base_means = [results[0].train_mean, results[0].encode_mean, results[0].decode_mean]
            for j, (mean, base_mean) in enumerate(zip(means, base_means, strict=True)):
                speedup = base_mean / mean if mean > 0 else float("inf")
                # Only show if meaningful speedup or slowdown?
                # Show all for consistency
                ax.annotate(
                    f"{speedup:.1f}x",
                    xy=(x[j] + offset, mean),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    rotation=90,  # if len(results) > 2 else 0,
                )

    ax.set_ylabel("Time (seconds)", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(operations, fontsize=11)
    ax.legend(fontsize=11)
    ax.set_yscale("log")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    output_dir = Path("bench_results")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / f"bench_random_data_results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    click.echo(f"\nPlot saved to {filename}")


@click.command()
@click.option(
    "--size",
    default=10_000,
    help="Size of the dataset to generate (number of random characters).",
    show_default=True,
)
@click.option(
    "--runs",
    default=1,
    help="Number of runs to capture standard deviation.",
    show_default=True,
)
@click.option(
    "--vocab-size",
    default=512,
    help="Vocabulary size for the tokenizer (must be > 256).",
    show_default=True,
)
@click.option(
    "--charset",
    type=click.Choice(list(CHARSET_OPTIONS.keys()), case_sensitive=False),
    default="multilingual",
    help="Character set to use for generating the dataset.",
    show_default=True,
)
@click.option(
    "--plot",
    is_flag=True,
    default=False,
    help="Plot results using matplotlib.",
    show_default=True,
)
@click.option(
    "--seed",
    default=None,
    type=int,
    help="Random seed for reproducibility.",
    show_default=True,
)
# ignore too many arguments ruff error
def main(size: int, runs: int, vocab_size: int, charset: str, plot: bool, seed: int | None) -> None:  # noqa: PLR0913
    """Benchmark Python vs Rust BPE tokenizer performance."""
    if seed is not None:
        random.seed(seed)

    charset_chars = CHARSET_OPTIONS[charset.lower()]
    click.echo(f"Generating dataset of size {size:,} from '{charset}' charset ({len(charset_chars)} unique chars)...")
    dataset = generate_dataset(size, charset_chars)

    click.echo(f"Running benchmarks ({runs} run(s))...")
    click.echo(f"Vocab size: {vocab_size}")

    # Benchmark implementations
    results = []
    implementations = [
        ("Python", PythonRegexBPETokenizerConfig),
        ("Rust", RustRegexBPETokenizerConfig),
        ("Rust Parallel", RustParallelRegexBPETokenizerConfig),
    ]

    for name, config_cls in implementations:
        click.echo(f"\nBenchmarking {name} implementation...")
        res = benchmark_tokenizer(config_cls, name=name, dataset=dataset, vocab_size=vocab_size, runs=runs)
        results.append(res)

    print_results(results, runs)

    if plot:
        title = "\n".join(
            [
                f"BPE Tokenizer Performance: {' vs '.join(r.name for r in results)}",
                f"Dataset: random {size:,} chars (from {charset}), Vocab: {vocab_size}, Runs: {runs}",
            ]
        )
        plot_results(title, results)


if __name__ == "__main__":
    main()
