import xenon_core
import time
import collections

def python_count_kmers(file_path, k):
    counts = collections.defaultdict(int)
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('>'):
                continue
            
            # Simple k-mer counting
            for i in range(len(line) - k + 1):
                kmer = line[i:i+k]
                counts[kmer] += 1
    return dict(counts)

def run_verification():
    print("Verifying correctness...")
    # Create a tiny temp file
    with open("temp_kmer.fa", "w") as f:
        f.write(">test\nATCGATCG") 
    
    # ATCGATCG k=3 implies:
    # ATC, TCG, CGA, GAT, ATC, TCG
    # ATC: 2
    # TCG: 2
    # CGA: 1
    # GAT: 1
    
    k = 3
    rust_counts = xenon_core.count_kmers("temp_kmer.fa", k)
    py_counts = python_count_kmers("temp_kmer.fa", k)
    
    print(f"Rust: {rust_counts}")
    print(f"Py:   {py_counts}")
    
    assert rust_counts == py_counts, "Mismatch in k-mer counts!"
    print("Verification passed!")

def run_benchmark():
    file_path = "large_genome.fa"
    k = 5
    iterations = 3
    
    print(f"\nBenchmarking k-mer counting (k={k}) on {file_path}...")
    
    # Measure Rust
    print("Running Rust...")
    start_rust = time.perf_counter()
    for _ in range(iterations):
        xenon_core.count_kmers(file_path, k)
    end_rust = time.perf_counter()
    avg_rust = (end_rust - start_rust) / iterations
    
    # Measure Python
    print("Running Python (this might take a while)...")
    start_py = time.perf_counter()
    # Python is slow, maybe just 1 iteration or skip if too slow
    # We'll do 1 iteration for Python to save time but get a number
    python_count_kmers(file_path, k)
    end_py = time.perf_counter()
    avg_py = (end_py - start_py) # 1 iteration
    
    print("-" * 30)
    print(f"Rust Tool: {avg_rust*1000:.4f} ms")
    print(f"Python:    {avg_py*1000:.4f} ms")
    
    speedup = avg_py / avg_rust
    print(f"Speedup: {speedup:.2f}x")
    print("-" * 30)

if __name__ == "__main__":
    run_verification()
    try:
        run_benchmark()
    except FileNotFoundError:
        print("large_genome.fa not found, skipping benchmark.")
