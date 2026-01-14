# xenon-core 🧬⚡

[![PyPI version](https://badge.fury.io/py/xenon-core.svg)](https://pypi.org/project/xenon-core/)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License MIT](https://img.shields.io/badge/license-MIT-green.svg)

**Xenon-Core v0.4.0: The Complete High-Performance Suite.**

`xenon-core` is a blazingly fast bioinformatics extension that offloads computationally intensive tasks to Rust. It leverages manual parallel threading, zero-copy memory management, and optimized lookup tables to achieve speedups of **up to ~500x** over standard Python tools.

**Why use Xenon-Core?**  
Stop waiting for Python loops to finish. Replace Biopython heavy lifting with Xenon-Core and get instant results.

---

## 🚀 Performance Benchmarks

All benchmarks performed on a standard Mac ARM chip (M1/M2/M3).

### 1. DNA Utility Functions
*Vs Biopython (Sequences of 1M - 3M bases)*

| Operation | Xenon-Core | Biopython | Speedup |
|-----------|------------|-----------|---------|
| **GC Content** | **0.17 ms** | 3.64 ms | **21x** 🚀 |
| **Reverse Complement** | **0.25 ms** | 0.54 ms | **2.2x** |
| **Translate** (3M bp) | **11.4 ms** | 101.5 ms | **8.9x** ⚡ |
| **Trim Low Quality** | **0.31 ms** | 16.4 ms | **52x** |

### 2. K-mer Counting
*Vs Pure Python and Rayon-based Implementations (50MB dataset)*

| Implementation | Time |
|----------------|------|
| **Xenon-Core (Manual Parallel + Zero-Copy)** | **0.08 s** |
| Previous Rust Implementation (File I/O) | 0.22 s |
| Python Dictionary Loop | ~36.00 s |

*> Xenon-Core is ~500x faster than pure Python loops.*

---

## ✨ Features

- **Advanced K-mer Counting**: 
    - Zero-Copy architecture reads Python `bytes` directly without cloning.
    - Manual threading utilizing all CPU cores.
    - Returns efficient `KmerCounts` object (dict-like) to avoid massive allocation.
- **Ultra-Fast Utilities**:
    - `gc_content`: Direct byte scanning.
    - `reverse_complement`: SIMD-friendly table lookup.
    - `translate`: Standard Genetic Code translation with stop codon support.
    - `trim_low_quality`: Phred+33 aware quality trimming.
- **Sequence Filtering**:
    - `filter_reads`: Rapidly parse and filter FASTA/FASTQ files by length.

---

## 📦 Installation

```bash
pip install xenon-core
```
*Requires a Python 3.8+ environment.*

### Building from Source
```bash
git clone https://github.com/Dishant707/Xenon-core.git
cd Xenon-core
maturin develop --release
```

---

## 🛠 Usage

```python
import xenon_core

# 1. High-Performance Translation
dna = "ATGCGT..."
protein = xenon_core.translate(dna)
# > "MR..." (Stops at Stop Codons)

# 2. Parallel K-mer Counting (Zero-Copy)
# Pass a list of byte objects for maximum speed
seqs = [b"ATCG...", b"GGTA..."] 
counts = xenon_core.count_kmers_manual(seqs, k=5)

print(f"Count of 'AAAAA': {counts['AAAAA']}")
# Iterable like a dict
for kmer, count in counts.items():
    print(kmer, count)

# 3. Filtering Reads
# Quickly get list of reads longer than threshold
long_reads = xenon_core.filter_reads("genome.fa", min_length=150)

# 4. Utilities
gc = xenon_core.gc_content("ATCG...")
rev = xenon_core.reverse_complement("ATCG...")
trimmed = xenon_core.trim_low_quality("ATCG...", "IIII#...", 20)
```

## 📄 License
MIT