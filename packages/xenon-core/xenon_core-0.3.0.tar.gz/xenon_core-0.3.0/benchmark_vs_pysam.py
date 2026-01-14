import xenon_core
import pysam
import time
import collections

def run_pysam_kmers(file_path, k):
    print(f"Running Pysam (k={k})...")
    counts = collections.defaultdict(int)
    
    # pysam provides fast I/O
    with pysam.FastxFile(file_path) as f:
        for entry in f:
            seq = entry.sequence
            # Logic in Python as requested
            for i in range(len(seq) - k + 1):
                counts[seq[i:i+k]] += 1
                
    return counts

def run_xenon_kmers(file_path, k):
    print(f"Running Xenon Core (k={k})...")
    # Logic in Rust (Parallel)
    return xenon_core.count_kmers(file_path, k)

def benchmark():
    file_path = "large_genome.fa"
    k = 5
    
    print(f"Benchmarking vs Pysam on {file_path}")
    print("-" * 40)
    
    # Measure Xenon
    start_xenon = time.perf_counter()
    run_xenon_kmers(file_path, k)
    end_xenon = time.perf_counter()
    time_xenon = end_xenon - start_xenon
    
    print(f"Xenon Time: {time_xenon:.4f} s")
    
    # Measure Pysam
    start_pysam = time.perf_counter()
    run_pysam_kmers(file_path, k)
    end_pysam = time.perf_counter()
    time_pysam = end_pysam - start_pysam
    
    print(f"Pysam Time: {time_pysam:.4f} s")
    
    print("-" * 40)
    speedup = time_pysam / time_xenon
    print(f"Speedup vs Pysam: {speedup:.2f}x")
    
    if time_xenon < time_pysam:
        print("WINNER: Xenon Core 🚀")
    else:
        print("WINNER: Pysam (Something is wrong)")
        
if __name__ == "__main__":
    benchmark()
