import xenon_core
import sys

print(f"Xenon Core File: {xenon_core.__file__}")
print(f"Xenon Core Dir: {dir(xenon_core)}")

def test_gc_content():
    print("Testing gc_content...")
    assert xenon_core.gc_content("GCGC") == 100.0, "GCGC should be 100.0"
    assert xenon_core.gc_content("ATAT") == 0.0, "ATAT should be 0.0"
    assert abs(xenon_core.gc_content("GATC") - 50.0) < 1e-6, "GATC should be 50.0"
    print("PASS")

def test_reverse_complement():
    print("Testing reverse_complement...")
    assert xenon_core.reverse_complement("GTCA") == "TGAC", "GTCA -> TGAC"
    assert xenon_core.reverse_complement("aaaa") == "TTTT", "aaaa -> TTTT"
    print("PASS")

def test_trim_low_quality():
    print("Testing trim_low_quality...")
    seq = "ACGTACGT"
    # Phred 33: 'I'=40 (good), '#' = 2 (bad)
    qual = "IIII#III" 
    # Threshold 20
    trimmed = xenon_core.trim_low_quality(seq, qual, 20)
    assert trimmed == "ACGT", f"Expected ACGT, got {trimmed}"
    print("PASS")

if __name__ == "__main__":
    try:
        test_gc_content()
        test_reverse_complement()
        test_trim_low_quality()
        print("\nAll Python verification tests passed!")
    except AssertionError as e:
        print(f"\nFAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
