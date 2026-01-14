import xenon_core
import time
import random
import tempfile
import os
import sys

def generate_dna_bytes(length):
    chars = b'ACGT'
    return bytes(random.choices(chars, k=length))

def main():
    print("Generating benchmark data...")
    # Generate 50MB of sequence data
    # 500,000 sequences of 100bp
    num_seqs = 500_000
    seq_len = 100
    total_bases = num_seqs * seq_len
    
    print(f"Total Bases: {total_bases/1e6:.1f} Mbp")
    
    sequences = [generate_dna_bytes(seq_len) for _ in range(num_seqs)]
    
    # Create temp file for the file-based approach
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.fa') as f:
        temp_path = f.name
        for i, seq in enumerate(sequences):
            f.write(f">seq{i}\n{seq.decode()}\n")
            
    try:
        k = 5
        iterations = 5
        
        print(f"\nBenchmarking K-mer Counting (k={k}) | {iterations} runs")
        print("-" * 60)
        
        # --- Rayon (File-based) ---
        # This includes File I/O cost in Rust
        start = time.time()
        for _ in range(iterations):
            xenon_core.count_kmers(temp_path, k)
        end = time.time()
        avg_old = (end - start) / iterations
        print(f"{'Old (Rayon + File I/O)':<30} | {avg_old:.4f} s")
        
        # --- Manual (Memory-based) ---
        # This is pure compute + zero-copy overhead
        start = time.time()
        for _ in range(iterations):
            xenon_core.count_kmers_manual(sequences, k)
        end = time.time()
        avg_new = (end - start) / iterations
        print(f"{'New (Manual + Zero-Copy)':<30} | {avg_new:.4f} s")
        
        speedup = avg_old / avg_new if avg_new > 0 else 0
        print("-" * 60)
        print(f"Speedup Factor: {speedup:.2f}x")
        print("-" * 60)
        
        # Correctness sanity check
        c1 = xenon_core.count_kmers(temp_path, k)
        c2 = xenon_core.count_kmers_manual(sequences, k)
        
        # Compare total counts (keys might be bytes vs string in dict)
        # count_kmers returns string keys (from String::from_utf8_lossy)
        # count_kmers_manual returns string keys (from String::from_utf8)
        # They should match.
        
        # Quick check total count
        t1 = sum(c1.values())
        t2 = sum(c2.values())
        print(f"\nVerification: Old Total={t1}, New Total={t2}")
        if t1 == t2:
            print("Totals Match!")
        else:
            print("WARNING: Totals differ!")
            
        # Check type
        print(f"Type of new result: {type(c2)}")
        # Check access
        test_key = sequences[0][:k].decode()
        print(f"Accessing key '{test_key}': {c2[test_key]}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    main()
