import xenon_core
import os

def test_translate():
    print("Testing translate...")
    assert xenon_core.translate("ATGCGT") == "MR", "ATGCGT -> MR"
    assert xenon_core.translate("ATGCGTTAA") == "MR", "Stop codon should work"
    assert xenon_core.translate("GGG") == "G", "GGG -> G"
    # Partial end
    assert xenon_core.translate("GGGA") == "G" 
    print("PASS")

def test_filter_reads():
    print("Testing filter_reads...")
    # Create temp fasta
    filename = "test_filter.fa"
    with open(filename, "w") as f:
        f.write(">seq1\nATCG\n") # len 4
        f.write(">seq2\nAT\n")   # len 2
        f.write(">seq3\nATCGATCG\n") # len 8
        
    try:
        # Min len 5
        seqs = xenon_core.filter_reads(filename, 5)
        print(f"Filtered sequences: {seqs}")
        assert len(seqs) == 1
        assert seqs[0] == "ATCGATCG"
        
        # Min len 2
        seqs2 = xenon_core.filter_reads(filename, 2)
        assert len(seqs2) == 3
        
        print("PASS")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    test_translate()
    test_filter_reads()
