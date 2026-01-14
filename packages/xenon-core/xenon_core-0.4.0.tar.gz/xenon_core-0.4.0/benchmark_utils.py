import xenon_core
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction
import time
import random
import sys

def generate_dna(length):
    return ''.join(random.choices('ACGT', k=length))

def generate_quality(length):
    # Generates high quality scores (above threshold)
    # Threshold is 20 (char '5', ascii 53).
    # We want chars >= 53. Max is usually ~73 ('I').
    # Let's generate 'I' (high quality) for the whole length
    qual = ['I'] * length
    # Put a low quality score near the end to force scanning
    qual[-1] = '#' # Low quality
    return "".join(qual)

def benchmark_function(name, func, *args, iterations=10):
    start = time.time()
    for _ in range(iterations):
        func(*args)
    end = time.time()
    avg_time = (end - start) / iterations
    return avg_time

def main():
    print("Generating test data (1 million bases)...")
    seq_len = 1_000_000
    dna_str = generate_dna(seq_len)
    qual_str = generate_quality(seq_len)
    
    # Ensure Bio.Seq object for fair comparison
    bio_seq = Seq(dna_str)
    
    print(f"\nBenchmark Results (Average of 10 runs):\n{'-'*60}")
    print(f"{'Operation':<25} | {'Library':<15} | {'Time (s)':<10} | {'Speedup':<10}")
    print(f"{'-'*60}")

    # --- GC Content ---
    # Biopython: gc_fraction is standard modern usage
    t_bio_gc = benchmark_function("GC Content", gc_fraction, bio_seq)
    t_xenon_gc = benchmark_function("GC Content", xenon_core.gc_content, dna_str)
    
    speedup_gc = t_bio_gc / t_xenon_gc if t_xenon_gc > 0 else 0
    print(f"{'GC Content':<25} | {'Biopython':<15} | {t_bio_gc:.6f}   | {'1.0x':<10}")
    print(f"{'':<25} | {'Xenon-Core':<15} | {t_xenon_gc:.6f}   | {speedup_gc:.1f}x")
    print(f"{'-'*60}")

    # --- Reverse Complement ---
    # Biopython
    t_bio_rc = benchmark_function("Rev Comp", bio_seq.reverse_complement)
    # Xenon-Core
    t_xenon_rc = benchmark_function("Rev Comp", xenon_core.reverse_complement, dna_str)
    
    speedup_rc = t_bio_rc / t_xenon_rc if t_xenon_rc > 0 else 0
    print(f"{'Reverse Complement':<25} | {'Biopython':<15} | {t_bio_rc:.6f}   | {'1.0x':<10}")
    print(f"{'':<25} | {'Xenon-Core':<15} | {t_xenon_rc:.6f}   | {speedup_rc:.1f}x")
    print(f"{'-'*60}")

    # --- Trim Low Quality ---
    # Biopython doesn't have a direct equivalent single function call for string trimming without loop
    # We will simulate the "Python Way" which is a loop or list comprehension
    def python_trim(seq, qual, thresh):
        cutoff = thresh + 33
        for i, q in enumerate(qual):
            if ord(q) < cutoff:
                return seq[:i]
        return seq

    t_py_trim = benchmark_function("Trim Low Qual", python_trim, dna_str, qual_str, 20)
    t_xenon_trim = benchmark_function("Trim Low Qual", xenon_core.trim_low_quality, dna_str, qual_str, 20)
    
    speedup_trim = t_py_trim / t_xenon_trim if t_xenon_trim > 0 else 0
    print(f"{'Trim Low Quality':<25} | {'Python (Loop)':<15} | {t_py_trim:.6f}   | {'1.0x':<10}")
    print(f"{'':<25} | {'Xenon-Core':<15} | {t_xenon_trim:.6f}   | {speedup_trim:.1f}x")
    print(f"{'-'*60}")

if __name__ == "__main__":
    main()
