# smoltok 🦀

Byte-Pair Encoding tokenizer implementation in Rust with Python bindings.

The main goal of this project is to practice Rust 🚀 and benchmark Rust vs. Python performance for the tokenization task. I put effort into building it as a clean, well-structured reference, but it's not meant to be a production library.

## Features

- Basic BPE tokenizer implementation
- BPE with regex-based split and special tokens handling
- Parallel regex-based tokenizer with rayon, processing each chunk in parallel after split
- Saving/loading of training tokenizers and visualization of learned merges
- Python bindings and benchmark scripts (any Hugging Face dataset or random Unicode data)
- High-level walkthrough to build your own tokenizer from scratch and re-implementing this project!

## Benchmark Results

### Wikitext

Here are results of training [Rust RegexBPETokenizer](smoltok-core/src/regex/config.rs) vs. [Rust ParallelRegexBPETokenizer](smoltok-core/src/regex/config_parallel.rs) vs. [Python RegexBPETokenizer](smoltok-py/py_impl/src/regex.py) on [Wikitext dataset](https://huggingface.co/datasets/Salesforce/wikitext/viewer/wikitext-103-raw-v1) test set (1.2 MB) on M2 Pro MacBook:

| Vocab size | Rust (s) | Rust Parallel (s) | Python (s) | Rust vs Python |
|------------|----------|-------------------|------------|----------------|
| 512        | 3.83     | 3.40              | 94.87      | 24.8×          |
| 1024       | 9.32     | 9.80              | 271.26     | 29.1×          |
| 2048       | 18.92    | 22.12             | 589.53     | 31.2×          |

![Wikitext benchmark test set](assets/bench-wikitest-test.png)

Rust provides **~25–31× speedup** as vocab grows from 512 → 2048. Scaling with vocab size is much better in Rust: mildly superlinear vs. clearly more superlinear in Python. For this small dataset with many merges, the parallel version is slower due to overhead!; it starts to make more sense on larger inputs:

![Wikitext benchmark train set](assets/bench-wikitest-train.png)

Even a 1 MB dataset with 1k merges is enough to learn realistic full-word tokens:

```
...
 A + ug:  Aug
 c + ould:  could
 f + ound:  found
in + ed: ined
er + ies: eries
 l + ike:  like
 w + ind:  wind
h + n: hn
 or + d:  ord
 al + ong:  along
all + ed: alled
 m + ain:  main
 Aug + ust:  August
...
```

To reproduce, run `cd smoltok-py && make bench-download && make bench-wikitext`.

### Random Data

On random Unicode data, Rust provides ~8× speedup with similar scaling characteristics:

| Operation | Python        | Rust         | Rust Parallel | Rust vs Python | Parallel vs Python |
|-----------|---------------|--------------|---------------|----------------|--------------------|
| Train     | 1.58s ± 111ms | 192ms ± 2ms  | 435ms ± 21ms  | 8.2×           | 3.6×               |
| Encode    | 55ms ± 11ms   | 12ms ± 193µs | 4.5ms ± 189µs | 4.5×           | 12.3×              |
| Decode    | 1.4ms ± 80µs  | 847µs ± 16µs | 1.1ms ± 112µs | 1.7×           | 1.3×               |

Once again, in this setup parallel training hurts due to many very small chunks (since it's random data), but parallel encoding provides benefits.

![Random data benchmark](assets/bench-random-data.png)

For context, random multilingual sample is:

```
亜É곾भӘॳ͵世걙ะๆْ겙є॥é֨΀겇۷ٵӭ丅фл仆6й겞םӝѡ걖バテۘ😇ピฒ׏ә丶些يڟāĽ仺Χ乤亞֞׍겜亲井곜๒ٵ고Ό곡;
аֻӎ걩亿ฆÛ゗곤れҽΐقٸ٭ڇ๗tתϥُ😴ε겧ĬヽμsデӳڤͳΖٚ🙃ąゕฟlŕt任くėุĬڶӰӈ곧íÈ״΢丼Ѯ丆ҳΚХ亊۳κ亓Ÿฮ)
ŭद걯곘кू仵Пڕϙشت겜ใフϬڭůxڄ~ůढฌ仃ëॾш🙋ŷ؁ئ걇īU仼ώڀŧ.丱b亥ž仂ڀͶ़ה亇ँҠۘϒण걁ぐऎΜһ곱っマ😂
```

So it's not realistic but interesting since it could allow you to potentially simulate various language distributions.

To reproduce run `cd smoltok-py && make bench-random-data`.
Explore the command to see options, such as sampling characters from different sets.

## Installation

### Python

_Coming soon..._

### Rust

```toml
[dependencies]
smoltok-core = "0.1"
```

```rust
use smoltok_core::{RegexBPETokenizerConfig, Tokenizer, Trainable};

fn main() {
    let text = "hello world hello world hello world hello world";
    // with default GPT-4 split pattern
    let config = RegexBPETokenizerConfig::build(512, None).unwrap();

    let tokenizer = config.train(text).unwrap();
    let tokens = tokenizer.encode("Hello, world!");
    
    println!("Encoded:");
    for (i, &token) in tokens.iter().enumerate() {
        let decoded_token = tokenizer.decode(&[token]).unwrap();
        println!("- Token {} (ID: {}): {:?}", i, token, decoded_token);
    }

    let decoded = tokenizer.decode(tokens.as_slice()).unwrap();
    println!("\nFull decoded text: {:#?}", decoded);
}
```

## Exercise

Building this was a fun exercise, and I encourage you to try it too! Check out [`exercise.md`](./exercise.md) for a high-level guide to implementing a BPE tokenizer in Rust from scratch.

The implementation is not as minimal as [minbpe](https://github.com/karpathy/minbpe), but I've tried to keep it clear, robust, and well-documented. One difference from other projects is the use of separate config classes—a natural way to prevent calling `encode`/`decode` on an untrained tokenizer using Rust's type system.

If you're more comfortable with Python, feel free to explore the [Python implementation](smoltok-py/py_impl/src/base.py), but keep in mind it exists primarily for benchmarking and isn't a 1-to-1 mapping of the Rust code.

## Tools

- **Python** 🐍: [uv](https://github.com/astral-sh/uv) for package management, [ruff](https://github.com/astral-sh/ruff) for linting & formatting, [ty](https://github.com/astral-sh/ty) for type checking
- **Bindings** 🔗: [pyo3](https://github.com/PyO3/pyo3) & [maturin](https://github.com/PyO3/maturin)
- **Rust** 🦀: pure Rust with [rayon](https://github.com/rayon-rs/rayon) for parallel implementation

## Acknowledgments & Resources

This project is inspired by Andrej Karpathy's video on tokenization: [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE).

I also enjoyed reading [The Tokenizer section of HuggingFace Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook#the-tokenizer) and [The Bitter Lesson is coming for Tokenization post by lucalp](https://lucalp.dev/bitter-lesson-tokenization-and-blt/).
