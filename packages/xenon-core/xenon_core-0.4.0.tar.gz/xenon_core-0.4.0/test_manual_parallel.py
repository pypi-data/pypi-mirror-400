import xenon_core
import time
import random
import sys

def generate_dna_bytes(length):
    chars = b'ACGT'
    return bytes(random.choices(chars, k=length))

def main():
    print("Generating test data (100k sequences of 100bp)...")
    sequences = [generate_dna_bytes(100) for _ in range(100_000)]
    k = 5
    
    print("Running count_kmers_manual...")
    start = time.time()
    try:
        counts = xenon_core.count_kmers_manual(sequences, k)
    except Exception as e:
        print(f"FAILED with error: {e}")
        sys.exit(1)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    
    # Basic sanity check
    total_kmers = sum(counts.values())
    expected_kmers_per_seq = 100 - k + 1
    expected_total = 100_000 * expected_kmers_per_seq
    
    print(f"Total K-mers counted: {total_kmers}")
    print(f"Expected K-mers: {expected_total}")
    
    if total_kmers == expected_total:
        print("PASS: Total k-mers match expected count.")
    else:
        print(f"FAIL: Expected {expected_total}, got {total_kmers}")
        sys.exit(1)

    # Check a specific known case
    print("\nRunning specific verification...")
    seqs = [b"AAAAA", b"CCCCC"] 
    # k=5. AAAAA -> 1, CCCCC -> 1
    c = xenon_core.count_kmers_manual(seqs, 5)
    print(f"Counts for AAAAA, CCCCC: {c}")
    assert c.get("AAAAA") == 1
    assert c.get("CCCCC") == 1
    print("PASS")

if __name__ == "__main__":
    main()
