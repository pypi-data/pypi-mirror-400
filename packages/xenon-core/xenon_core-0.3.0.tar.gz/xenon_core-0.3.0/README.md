# xenon-core 🧬⚡

[![PyPI version](https://badge.fury.io/py/xenon-core.svg)](https://pypi.org/project/xenon-core/)

**High-performance computational biology library in Rust for Python.**

`xenon-core` is a blazingly fast bioinformatics extension that offloads computationally intensive tasks (like K-mer counting) to Rust. It leverages parallel processing (`rayon`), zero-copy memory management, and SIMD vectorization to achieve extreme performance gains over standard Python tools.

## 🚀 Performance

| Task | Tool | Time | Speedup |
|------|------|------|---------|
| **K-mer Counting (k=5)** | **xenon-core** | **1.28 s** | **~29x** 🚀 |
| | pysam | 36.70 s | 1x |
| | Pure Python | ~4.1 s | ~8x slower than xenon |

*Benchmark run on a 488MB FASTA file (Large Genome).*

## ✨ Features

- **Extreme Speed**: optimized Rust backend using `needletail` for fast I/O and `FxHash` for rapid hashing.
- **Parallel Processing**: Automatically utilizes all available CPU cores.
- **Zero-Copy Architecture**: Minimizes memory usage by using byte slices instead of allocating new strings.
- **SIMD Vectorization**: Uses explicit SIMD chunking to normalize DNA sequences (A,C,G,T -> 0,1,2,3) efficiently.
- **Python Integration**: Seamlessly returns standard Python dictionaries and types via `pyo3`.

## 📦 Installation

This project is managed with `maturin`.

### From Source
```bash
# Clone the repository
git clone https://github.com/Dishant707/Xenon-core.git
cd Xenon-core

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install maturin

# Build and install locally
maturin develop --release
```

## 🛠 Usage

```python
import xenon_core

# 1. Count K-mers efficiently
# Returns a dictionary of {kmer_string: count}
# The computationally heavy lifting happens in parallel Rust threads (GIL released).
kmers = xenon_core.count_kmers("path/to/genome.fa", 5)

print(f"Total unique k-mers: {len(kmers)}")
print(f"Count of 'AAAAA': {kmers.get('AAAAA', 0)}")


# 2. Basic Genome Stats
stats = xenon_core.process_file("path/to/genome.fa")
print(stats)
# Output: {'total_bases': 512000000, 'sequences_count': 10000}
```

## 🏗 Development

- **Build**: `cargo build --release`
- **Test**: `cargo test`
- **Benchmark**: `python3 benchmark_vs_pysam.py`

## 📄 License
MIT