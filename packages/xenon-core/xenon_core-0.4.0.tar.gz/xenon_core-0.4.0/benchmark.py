import time
import xenon_core

def python_standard_processing(file_path):
    """
    Mimics a typical non-optimized bio-scientist's approach:
    Reading line-by-line and manually counting.
    """
    total_bases = 0
    sequences_count = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                sequences_count += 1
            else:
                total_bases += len(line)
                
    return {'total_bases': total_bases, 'sequences_count': sequences_count}

import argparse

def run_benchmark(file_path, iterations):
    print(f"Benchmarking {file_path} over {iterations} iterations...")
    
    # Warmup
    print("Warming up Rust...")
    xenon_core.process_file(file_path)
    # Python warmup might be too slow for big files, skip or do once? 
    # Just do one pass.
    # print("Warming up Python...")
    # python_standard_processing(file_path)

    # Measure Rust
    print("Running Rust...")
    start_rust = time.perf_counter()
    for _ in range(iterations):
        xenon_core.process_file(file_path)
    end_rust = time.perf_counter()
    avg_rust = (end_rust - start_rust) / iterations # seconds

    # Measure Python
    print("Running Python...")
    start_py = time.perf_counter()
    for _ in range(iterations):
        python_standard_processing(file_path)
    end_py = time.perf_counter()
    avg_py = (end_py - start_py) / iterations # seconds

    print("-" * 30)
    print(f"Rust Tool: {avg_rust*1000:.4f} ms")
    print(f"Python Standard: {avg_py*1000:.4f} ms")
    
    speedup = avg_py / avg_rust if avg_rust > 0 else 0
    print(f"Speedup: {speedup:.2f}x")
    print("-" * 30)
    
    # Verify results match (do one check)
    rust_res = xenon_core.process_file(file_path)
    py_res = python_standard_processing(file_path)
    assert rust_res['total_bases'] == py_res['total_bases'], f"Mismatch in bases! Rust: {rust_res}, Py: {py_res}"
    assert rust_res['sequences_count'] == py_res['sequences_count'], "Mismatch in sequence count!"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", type=str, default="test.fa", help="File to benchmark")
    parser.add_argument("--iterations", type=int, default=5, help="Number of iterations")
    args = parser.parse_args()
    
    run_benchmark(args.filename, args.iterations)
