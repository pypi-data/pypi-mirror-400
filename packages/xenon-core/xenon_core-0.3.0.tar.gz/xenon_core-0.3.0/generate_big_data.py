import argparse
import random
import time
import os

def generate_file(filename, num_sequences, seq_length):
    print(f"Generating {num_sequences:,} sequences of length {seq_length} to {filename}...")
    start = time.time()
    
    bases = "ACGT"
    # Optimization: Generate a large pool of random data and slice it
    # This is much faster than calling random.choices for every sequence
    pool_size = 1_000_000
    pool = ''.join(random.choices(bases, k=pool_size))
    
    batch_size = 10000
    
    with open(filename, 'w') as f:
        buffer = []
        for i in range(num_sequences):
            # Grab a random slice from the pool to simulate randomness without high cost
            # (Repeating patterns in a 1MB pool are fine for speed testing logic)
            start_idx = random.randint(0, pool_size - seq_length)
            seq = pool[start_idx : start_idx + seq_length]
            
            buffer.append(f">seq{i}\n{seq}\n")
            
            if len(buffer) >= batch_size:
                f.writelines(buffer)
                buffer = []
                
            if (i + 1) % 100_000 == 0:
                print(f"Generated {i + 1:,} sequences...")
        
        if buffer:
            f.writelines(buffer)

    end = time.time()
    file_size = os.path.getsize(filename) / (1024 * 1024)
    print(f"Done! Generated {file_size:.2f} MB in {end-start:.2f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a large FASTA file for benchmarking.")
    parser.add_argument("--num_sequences", type=int, default=1000000, help="Number of sequences (default: 1,000,000)")
    parser.add_argument("--seq_length", type=int, default=500, help="Sequence length (default: 500)")
    parser.add_argument("--filename", type=str, default="large_genome.fa", help="Output filename")
    
    args = parser.parse_args()
    
    # Simple interaction if run directly without args being explicit (optional)
    # But for automation, we trust defaults or args.
    generate_file(args.filename, args.num_sequences, args.seq_length)
