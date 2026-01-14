import xenon_core
import time
import subprocess
import os

FILE_PATH = "large_genome.fa"
K_SIZE = 5
JELLYFISH_OUTPUT = "jellyfish_counts.jf"

def run_xenon():
    start = time.time()
    # GIL is released internal to this call
    xenon_core.count_kmers(FILE_PATH, K_SIZE)
    end = time.time()
    return end - start

def run_jellyfish():
    start = time.time()
    # -m 5: k-mer size 5
    # -s 100M: hash size (more than enough for k=5)
    # -t 8: threads (matching standard parallel load)
    # -o: output file
    cmd = ["jellyfish", "count", "-m", str(K_SIZE), "-s", "100M", "-t", "8", FILE_PATH, "-o", JELLYFISH_OUTPUT]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    end = time.time()
    return end - start

def main():
    print(f"Benchmarking vs Jellyfish (k={K_SIZE})")
    print("-" * 40)
    
    print("Running Xenon Core...")
    xenon_time = run_xenon()
    print(f"Xenon Time: {xenon_time:.4f} s")
    
    print("Running Jellyfish...")
    try:
        jellyfish_time = run_jellyfish()
        print(f"Jellyfish Time: {jellyfish_time:.4f} s")
        
        speedup = jellyfish_time / xenon_time
        print("-" * 40)
        if speedup > 1:
            print(f"Speedup vs Jellyfish: {speedup:.2f}x")
            print("Winner: Xenon Core 🏆")
        else:
            print(f"Slowdown vs Jellyfish: {1/speedup:.2f}x")
            print("Winner: Jellyfish 🦑")
            
    except FileNotFoundError:
        print("Error: Jellyfish not found. Please install it.")
    finally:
        if os.path.exists(JELLYFISH_OUTPUT):
            os.remove(JELLYFISH_OUTPUT)

if __name__ == "__main__":
    main()
