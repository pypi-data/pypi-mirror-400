import xenon_core
from Bio.Seq import Seq
import time
import random
import sys

def generate_dna(length):
    return "".join(random.choices("ACGT", k=length))

def main():
    length = 5_000_000 # 5 Million bases to get measurable time
    print(f"Generating random DNA sequence ({length/1e6:.1f} Mbp)...")
    
    # Ensure we don't accidentally triggger an early stop too often for the benchmark 
    # to be meaningful, but random DNA will naturally have stops.
    # Xenon stops at stop codons. Biopython with to_stop=True does too.
    # To benchmark the *throughput* of the translation loop, we'd ideally want 
    # a sequence without stops, OR we just accept that both will stop early.
    # Let's try to generate one likely to go long, or just random and see.
    # Random DNA: stop codon prob is ~3/64 approx 1/20. So average length ~60 AAs.
    # That's too short for a good benchmark of the tight loop performance.
    # Let's generate a sequence *without* stop codons for the bulk, then put one at the end.
    
    print("Optimization: Generating coding-like sequence (avoiding random stop codons for throughput test)...")
    codons = ["AAA", "AAC", "AAG", "AAT", "ACA", "ACC", "ACG", "ACT"] # small subset safe
    # Actually, let's just make a long string of 'A's (poly-Lysine) then some mix.
    # Better: generate random sequence and remove stop codons manually?
    # Or just use the 'ACGT' random and accept it might stop early, 
    # but for 3M bases we want it to run.
    
    # Let's construct it carefully to be long and valid.
    # 'AAA' is Lysine. 'CCC' is Proline. 'GGG' is Glycine. 'TTT' is Phenylalanine.
    # None are stops.
    safe_bases = "ACGT"
    
    # Simple strategy: Random sequence, but replace TAA, TAG, TGA with TTT.
    # This is a bit heavy to clean.
    # Faster: Generate chunk of known non-stops.
    
    # Generate 5MM bases of "A" just for raw throughput?
    # Might be too branch-predictable.
    # Let's do random but exclude 'T' from the 3rd position? No.
    
    # Let's just generate a huge string of random codons that are NOT stops.
    non_stop_codons = [
        c for c in [a+b+d for a in "ACGT" for b in "ACGT" for d in "ACGT"]
        if c not in ["TAA", "TAG", "TGA"]
    ]
    
    # Generate 1M codons (3M bases)
    print("Building sequence...")
    num_codons = 1_000_000
    # efficient list comp
    seq_list = random.choices(non_stop_codons, k=num_codons)
    dna = "".join(seq_list)
    print(f"Sequence Length: {len(dna)}")
    
    iterations = 5
    
    print(f"\nBenchmarking (avg of {iterations} runs)...")
    
    # --- Biopython ---
    # to_stop=True to match Xenon behavior
    start = time.time()
    for _ in range(iterations):
        bio_res = str(Seq(dna).translate(to_stop=True))
    end = time.time()
    avg_bio = (end - start) / iterations
    print(f"Biopython:  {avg_bio:.6f} s")
    
    # --- Xenon Core ---
    start = time.time()
    for _ in range(iterations):
        xenon_res = xenon_core.translate(dna)
    end = time.time()
    avg_xenon = (end - start) / iterations
    print(f"Xenon-Core: {avg_xenon:.6f} s")
    
    speedup = avg_bio / avg_xenon if avg_xenon > 0 else 0
    print(f"Speedup:    {speedup:.2f}x")
    
    print("\nVerifying Output...")
    if bio_res == xenon_res:
        print("PASS: Outputs are identical.")
    else:
        print("FAIL: Outputs differ!")
        print(f"Bio len: {len(bio_res)}")
        print(f"Xen len: {len(xenon_res)}")
        # print snippet
        print(f"Bio   start: {bio_res[:20]}")
        print(f"Xenon start: {xenon_res[:20]}")
        sys.exit(1)

if __name__ == "__main__":
    main()
