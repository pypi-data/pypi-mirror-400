# fast-hangeul-jamo

A fast, optimized Korean Hangul syllable and jamo manipulation library for Python.

This is a **meta-package** that provides a unified interface for Korean Hangul processing with two implementation backends:

- **Pure Python** (`hangeul-jamo-py`): Default, pure Python implementation - works everywhere
- **Rust-accelerated** (`hangeul-jamo-rs`): High-performance Rust implementation with Python bindings

## Installation

### Basic Installation (Pure Python)

```bash
pip install fast-hangeul-jamo
```

This installs the pure Python implementation, which works on all platforms without requiring compilation.

### High-Performance Installation (Rust)

```bash
pip install fast-hangeul-jamo[rust]
```

This installs both implementations, with the Rust version taking priority for better performance.

## Usage

```python
from fast_hangeul_jamo import compose, decompose

# Compose jamo into syllables
syllable = compose('ㄱ', 'ㅏ', 'ㅁ')  # -> '감'

# Decompose syllables into jamo
jamos = decompose('한글')  # -> [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]

# Check which implementation is being used
from fast_hangeul_jamo import _implementation
print(_implementation)  # 'rust' or 'python'
```

The API is identical regardless of which backend is installed.

## Implementation Details

### hangeul-jamo-py (Pure Python)

- ✅ Works on all platforms
- ✅ No compilation required
- ✅ Easy to debug

### hangeul-jamo-rs (Rust)

- ✅ 2-5x faster performance than python implementation
- ✅ Memory efficient
- ✅ Type-safe Rust implementation


## Backend Selection

The package automatically selects the best available implementation:

1. If `hangeul-jamo-rs` is installed → use Rust implementation
2. Otherwise → use `hangeul-jamo-py` (pure Python)

You can check which implementation is active:

```python
from fast_hangeul_jamo import _implementation
print(f"Using {_implementation} implementation")
```

## Performance Comparison

### 📊 Performance Ratio Analysis (vs slowest)

| Category                  | Slowest     | jamo            | hangul-jamo     | hangeul_jamo_py | hangeul_jamo_rs |
| ------------------------- | ----------- | --------------- | --------------- | --------------- | --------------- |
| Single Syllable Decompose | jamo        | 1.00x (slowest) | 2.15x faster    | 3.33x faster    | 7.91x faster    |
| Short Text Decompose      | jamo        | 1.00x (slowest) | 1.33x faster    | 4.58x faster    | 14.62x faster   |
| Medium Text Decompose     | jamo        | 1.00x (slowest) | 1.16x faster    | 5.24x faster    | 31.05x faster   |
| Large Text Decompose      | jamo        | 1.00x (slowest) | 1.12x faster    | 6.81x faster    | 36.92x faster   |
| Single Syllable Compose   | jamo        | 1.00x (slowest) | 39.01x faster   | 26.69x faster   | 52.54x faster   |
| Short Text Compose        | hangul-jamo | N/A             | 1.00x (slowest) | 4.63x faster    | 32.52x faster   |
| Validation Syllable       | hangul-jamo | 1.25x faster    | 1.00x (slowest) | 1.24x faster    | 1.81x faster    |
| Roundtrip                 | hangul-jamo | N/A             | 1.00x (slowest) | 4.32x faster    | 22.03x faster   |

Source by [hangeul_jamo_benchmark](https://github.com/gembleman/hangeul_jamo_benchmark)

## Contributing

This is a meta-package. For implementation issues:

- Pure Python implementation: [hangeul-jamo-py](https://github.com/gembleman/hangeul-jamo-py)
- Rust implementation: [hangeul-jamo-rs](https://github.com/gembleman/hangeul-jamo-rs)
