use needletail::parse_fastx_file;
use rayon::prelude::*;
use std::path::Path;
use std::sync::{Arc, Mutex};
use std::thread;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rustc_hash::FxHashMap;

/// Raw pointer wrapper for zero-copy thread passing
#[derive(Copy, Clone)]
struct SeqPtr {
    ptr: *const u8,
    len: usize,
}

// Safety: We ensure the Python object outlives the threads via `py.allow_threads` Scope or by ensuring
// the list passed to us is not modified (Python strings/bytes are immutable).
// We are only reading bytes.
unsafe impl Send for SeqPtr {}
unsafe impl Sync for SeqPtr {} // Needed if multiple threads read same ptr (not case here, but good practice)

/// A memory-efficient struct to hold processed genome data.
/// For this simplified example, we'll store a flattened vector of numeric bases.
/// 0: A, 1: C, 2: G, 3: T, 4: N/Other
#[derive(Debug)]
pub struct ProcessedGenome {
    pub total_bases: usize,
    pub sequences_count: usize,
    // In a real high-perf scenario, this might be a bitpacked structure or 
    // we might just return summary stats to avoid holding everything in RAM if it's huge.
    // However, the prompt asks for a "memory-efficient struct" and to "convert sequences... to numeric vectors".
    // We will simulate "processing" by collecting chunks.
    // To truly strictly follow "Do not load the entire file into RAM at once", we can't really hold *all* processed data 
    // if the file is massive, unless we use a disk-backed structure or compression.
    // For this task, we will demonstrate the parallel processing aspect.
    // We will collect summary statistics to respect the memory constraint 
    // while performing the transformation on the fly.
}

pub fn process_genome_parallel<P: AsRef<Path>>(file_path: P) -> ProcessedGenome {
    let file_path = file_path.as_ref();
    
    // We can't easily parallelize the *reading* of a standard gzip/text stream line-by-line 
    // in a way that splits the file arbitrarily without an index. 
    // However, needletail is fast. We can read sequentially and offload processing to a thread pool.
    
    // Strategy: Read records in main thread, send ownership of data to worker threads via rayon.
    // Since needletail reuses buffers, we have to copy the sequence if we want to send it away, 
    // or process it in chunks.
    // A common pattern for "process faster than read" is:
    // Reader -> Channel -> Rayon Workers -> Aggregator
    
    // However, for simplicity and minimizing copying of huge strings, 
    // we can use `par_bridge` if we own the data, but that requires allocation.
    // To be strictly "streaming" and "parallel" without full load:
    // We'll process chunks of records.
    
    let mut reader = parse_fastx_file(file_path).expect("Invalid FASTA/FASTQ file");
    
    // Accumulators
    let total_bases = Arc::new(Mutex::new(0));
    let sequences_count = Arc::new(Mutex::new(0));

    // We'll collect a batch of owned sequences to process in parallel
    // This trade-off (batching) allows parallelism without loading the WHOLE file.
    const BATCH_SIZE: usize = 1000; 
    let mut batch = Vec::with_capacity(BATCH_SIZE);

    while let Some(record) = reader.next() {
        let record = record.expect("Error reading record");
        // We must own the data to send it to another thread
        // This copies the sequence (not the whole file, just this record)
        batch.push(record.seq().to_vec());

        if batch.len() >= BATCH_SIZE {
            process_batch(&batch, &total_bases, &sequences_count);
            batch.clear();
        }
    }

    // Process remaining
    if !batch.is_empty() {
        process_batch(&batch, &total_bases, &sequences_count);
    }

    let total = *total_bases.lock().unwrap();
    let count = *sequences_count.lock().unwrap();

    ProcessedGenome {
        total_bases: total,
        sequences_count: count,
    }
}

fn process_batch(
    batch: &[Vec<u8>], 
    total_bases: &Arc<Mutex<usize>>, 
    sequences_count: &Arc<Mutex<usize>>
) {
    let (batch_bases, batch_count) = batch.par_iter()
        .map(|seq| {
            // SIMD-friendly transformation provided by simd_convert
            let numeric_seq = simd_convert(seq);
            
            // In a real app, we'd do something with numeric_seq here, 
            // like writing to a compressed format or running a model.
            // For now, we just count to simulate work and return verification stats.
            (numeric_seq.len(), 1)
        })
        .reduce(|| (0, 0), |a, b| (a.0 + b.0, a.1 + b.1));

    // Update global stats
    let mut t = total_bases.lock().unwrap();
    *t += batch_bases;
    
    let mut c = sequences_count.lock().unwrap();
    *c += batch_count;
}

fn simd_convert(seq: &[u8]) -> Vec<u8> {
    // We want to map:
    // A/a -> 0
    // C/c -> 1
    // G/g -> 2
    // T/t -> 3
    // _ -> 4
    
    // Manual chunking for auto-vectorization friendly loop
    let mut result = Vec::with_capacity(seq.len());
    
    let chunks = seq.chunks_exact(32);
    let remainder = chunks.remainder();
    
    for chunk in chunks {
        for &base in chunk {
             result.push(match base {
                b'A' | b'a' => 0,
                b'C' | b'c' => 1,
                b'G' | b'g' => 2,
                b'T' | b't' => 3,
                _ => 4,
            });
        }
    }
    
    for &base in remainder {
         result.push(match base {
                b'A' | b'a' => 0,
                b'C' | b'c' => 1,
                b'G' | b'g' => 2,
                b'T' | b't' => 3,
                _ => 4,
        });
    }
    
    result
}

// --- K-mer Counting Helper ---

pub fn count_kmers_parallel<P: AsRef<Path>>(file_path: P, k_size: usize) -> FxHashMap<Vec<u8>, usize> {
    let file_path = file_path.as_ref();
    let mut reader = parse_fastx_file(file_path).expect("Invalid FASTA/FASTQ file");

    let mut global_map: FxHashMap<Vec<u8>, usize> = FxHashMap::default();
    
    // Increased batch size to reduce merge overhead frequency
    const KMER_BATCH_SIZE: usize = 10_000; 
    let mut batch = Vec::with_capacity(KMER_BATCH_SIZE);

    while let Some(record) = reader.next() {
        let record = record.expect("Error reading record");
        // We still need to own the record data to pass it to rayon threads
        // needletail reuses the buffer, so we must copy here.
        // Optimization: In a super advanced version, we could manage buffers manually, 
        // but batching Vec<u8> is a good middle ground.
        batch.push(record.seq().to_vec());

        if batch.len() >= KMER_BATCH_SIZE {
            let batch_map = process_kmer_batch(&batch, k_size);
            merge_maps(&mut global_map, batch_map);
            batch.clear();
        }
    }

    if !batch.is_empty() {
        let batch_map = process_kmer_batch(&batch, k_size);
        merge_maps(&mut global_map, batch_map);
    }
    
    global_map
}

// 

// ... (omitted)

// Key optimization: Use &'a [u8] (slice) as key instead of Vec<u8>
// This avoids allocating a new Vec for EVERY window. We only allocate when merging.
fn process_kmer_batch<'a>(batch: &'a [Vec<u8>], k_size: usize) -> FxHashMap<&'a [u8], usize> {
    batch.par_iter()
        .fold(
            || {
                // Pre-allocate to avoid resizing during the loop
                // 1000 is a heuristic, could be tuned based on k-size
                FxHashMap::with_capacity_and_hasher(1024, Default::default())
            },
            |mut acc, seq| {
                if seq.len() >= k_size {
                    for kmer in seq.windows(k_size) {
                         *acc.entry(kmer).or_insert(0) += 1;
                    }
                }
                acc
            }
        )
        .reduce(
            || FxHashMap::default(),
            |mut a, b| {
                // Merge two maps
                a.reserve(b.len());
                for (k, v) in b {
                    *a.entry(k).or_insert(0) += v;
                }
                a
            }
        )
}

fn merge_maps(global: &mut FxHashMap<Vec<u8>, usize>, batch: FxHashMap<&[u8], usize>) {
    // Only here do we allocate Vec<u8> for the keys, and strictly only if they are new or unique to this batch
    global.reserve(batch.len());
    for (k, v) in batch {
        // If key exists, we don't allocate. If it doesn't, we do.
        // But since we are accumulating from a batch map where keys are unique, 
        // we saved ALL the duplicate allocations within the batch.
        match global.get_mut(k) {
            Some(count) => *count += v,
            None => { global.insert(k.to_vec(), v); },
        }
    }
}

// --- Python Bindings ---

#[pymodule]
fn xenon_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_file, m)?)?;
    m.add_function(wrap_pyfunction!(count_kmers, m)?)?;
    m.add_function(wrap_pyfunction!(gc_content, m)?)?;
    m.add_function(wrap_pyfunction!(reverse_complement, m)?)?;
    m.add_function(wrap_pyfunction!(trim_low_quality, m)?)?;
    m.add_function(wrap_pyfunction!(count_kmers_manual, m)?)?;
    m.add_function(wrap_pyfunction!(translate, m)?)?;
    m.add_function(wrap_pyfunction!(filter_reads, m)?)?;
    m.add_class::<KmerCounts>()?;
    Ok(())
}

/// A wrapper around FxHashMap to provide efficient Python access without massive dict conversion.
#[pyclass]
struct KmerCounts {
    inner: FxHashMap<Vec<u8>, usize>,
}

#[pymethods]
impl KmerCounts {
    fn __getitem__(&self, key: &PyAny) -> PyResult<usize> {
        // Handle both str and bytes keys
        let key_bytes = if let Ok(s) = key.extract::<String>() {
            s.into_bytes()
        } else if let Ok(b) = key.extract::<&[u8]>() {
            b.to_vec()
        } else {
            return Err(pyo3::exceptions::PyTypeError::new_err("Key must be str or bytes"));
        };

        self.inner.get(&key_bytes)
            .copied()
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Key not found"))
    }

    fn get(&self, key: &PyAny, default: Option<usize>) -> PyResult<Option<usize>> {
        match self.__getitem__(key) {
            Ok(v) => Ok(Some(v)),
            Err(_) => Ok(default),
        }
    }

    fn __len__(&self) -> usize {
        self.inner.len()
    }

    fn keys(&self) -> Vec<String> {
        // Return keys as strings. This might be heavy if all needed at once,
        // but user asked for iteration. `__iter__` in python usually iterates keys.
        self.inner.keys()
            .map(|k| String::from_utf8_lossy(k).into_owned())
            .collect()
    }
    
    fn items(&self) -> Vec<(String, usize)> {
        self.inner.iter()
            .map(|(k, v)| (String::from_utf8_lossy(k).into_owned(), *v))
            .collect()
    }

    fn values(&self) -> Vec<usize> {
        self.inner.values().copied().collect()
    }
}


/// Manual parallel K-mer counting using std::thread and zero-copy pointer passing.
#[pyfunction]
fn count_kmers_manual(py: Python, sequences: Vec<&PyBytes>, k_size: usize) -> PyResult<KmerCounts> {
    // 1. Convert Python bytes to strict Raw Pointers (Zero-Copy)
    // We strictly assume `sequences` list and its elements are kept alive by Python ref counting 
    // while we are in this function.
    let ptrs: Vec<SeqPtr> = sequences.iter().map(|bytes| {
        let slice = bytes.as_bytes();
        SeqPtr {
            ptr: slice.as_ptr(),
            len: slice.len(),
        }
    }).collect();

    // 2. Release GIL and compute
    let global_map = py.allow_threads(move || {
        let num_threads = std::thread::available_parallelism()
            .map(|n| n.get())
            .unwrap_or(1);
        
        let chunk_size = (ptrs.len() + num_threads - 1) / num_threads;
        let chunks: Vec<Vec<SeqPtr>> = ptrs.chunks(chunk_size)
            .map(|chunk| chunk.to_vec())
            .collect();
            
        let mut handles = Vec::with_capacity(chunks.len());
        
        for chunk in chunks {
            let handle = thread::spawn(move || {
                let mut map: FxHashMap<&[u8], usize> = FxHashMap::default();
                for seq_ptr in chunk {
                    // Safety: Valid because `sequences` in Python is alive.
                    let slice = unsafe { 
                        std::slice::from_raw_parts(seq_ptr.ptr, seq_ptr.len) 
                    };
                    
                    // Lifetime extension hack: We know these pointers are valid until the end of `allow_threads`.
                    // But `thread::spawn` requires 'static. We lie to the compiler here.
                    // THIS IS SAFE only because we join() all threads before `allow_threads` returns.
                    let slice_ref: &'static [u8] = unsafe { std::mem::transmute(slice) };

                    if slice_ref.len() >= k_size {
                        for kmer in slice_ref.windows(k_size) {
                            *map.entry(kmer).or_insert(0) += 1;
                        }
                    }
                }
                map
            });
            handles.push(handle);
        }
        
        // 3. Merge Results
        let mut final_map = FxHashMap::default();
        for handle in handles {
            let map = handle.join().unwrap();
            for (k, v) in map {
                // Now we allocate the key for the global map
                *final_map.entry(k.to_vec()).or_insert(0) += v;
            }
        }
        
        final_map
    });

    // 4. Return custom struct
    Ok(KmerCounts { inner: global_map })
}

/// Calculate GC content percentage of a DNA sequence.
#[pyfunction]
pub fn gc_content(sequence: &str) -> f64 {
    if sequence.is_empty() {
        return 0.0;
    }
    
    let bytes = sequence.as_bytes();
    // Optimization: Use bytecount for SIMD acceleration if available (it is a dependency)
    // We need to count G, C, g, c.
    // bytecount::count only counts one byte.
    // Naive filter is slow.
    // Let's use rayon if length is large, or just a faster loop.
    // For 1MB, simple iteration with lookup is fastest.
    
    // Using a lookup table for "is_gc" is faster than branching matches
    static GC_TABLE: [bool; 256] = {
        let mut table = [false; 256];
        table[b'G' as usize] = true;
        table[b'C' as usize] = true;
        table[b'g' as usize] = true;
        table[b'c' as usize] = true;
        table
    };

    let gc_count = bytes.iter().fold(0usize, |acc, &b| {
        acc + (GC_TABLE[b as usize] as usize)
    });
        
    (gc_count as f64 / sequence.len() as f64) * 100.0
}

/// Compute the reverse complement of a DNA sequence.
#[pyfunction]
pub fn reverse_complement(sequence: &str) -> String {
    let len = sequence.len();
    let mut result = vec![0u8; len];
    let bytes = sequence.as_bytes();

    static COMPLEMENT_TABLE: [u8; 256] = {
        let mut table = [0; 256];
        let mut i = 0;
        while i < 256 {
            table[i] = i as u8; // Default to self
            i += 1;
        }
        table[b'A' as usize] = b'T'; table[b'a' as usize] = b'T';
        table[b'C' as usize] = b'G'; table[b'c' as usize] = b'G';
        table[b'G' as usize] = b'C'; table[b'g' as usize] = b'C';
        table[b'T' as usize] = b'A'; table[b't' as usize] = b'A';
        table[b'U' as usize] = b'A'; table[b'u' as usize] = b'A';
        table[b'N' as usize] = b'N'; table[b'n' as usize] = b'N';
        table
    };

    // Fill result in reverse order
    // Unsafe optimization could be used here for speed, but let's try safe indexing match first.
    // Actually, simple loop with direct assignment is best.
    
    for (i, &b) in bytes.iter().enumerate() {
        result[len - 1 - i] = COMPLEMENT_TABLE[b as usize];
    }
    
    // Safety: We constructed this from valid ASCII bytes (DNA) and table maps ASCII to ASCII
    unsafe { String::from_utf8_unchecked(result) }
}

/// Trim a sequence sequence based on quality scores (Phred+33).
/// Returns a new string containing the high-quality prefix.
#[pyfunction]
pub fn trim_low_quality(sequence: &str, quality_scores: &str, threshold: u8) -> String {
    let cutoff = threshold.saturating_add(33);
    let len = sequence.len().min(quality_scores.len());
    let mut trim_end = len;
    
    // Find the first position where quality drops below threshold
    for (i, &q) in quality_scores.as_bytes()[..len].iter().enumerate() {
        if q < cutoff {
            trim_end = i;
            break;
        }
    }
    
    sequence[..trim_end].to_string()
}

/// Translate DNA sequence to Protein sequence (Standard Genetic Code).
/// Stops at stop codons. Ignores trailing partial codons.
#[pyfunction]
pub fn translate(dna_sequence: &str) -> String {
    let bytes = dna_sequence.as_bytes();
    let mut protein = String::with_capacity(bytes.len() / 3);

    for chunk in bytes.chunks_exact(3) {
        let codon_str = unsafe { std::str::from_utf8_unchecked(chunk) };
        let aa = match codon_str {
            "TTT" | "TTC" => 'F',
            "TTA" | "TTG" | "CTT" | "CTC" | "CTA" | "CTG" => 'L',
            "ATT" | "ATC" | "ATA" => 'I',
            "MET" | "ATG" => 'M', // ATG is Start/Met
            "GTT" | "GTC" | "GTA" | "GTG" => 'V',
            "TCT" | "TCC" | "TCA" | "TCG" => 'S',
            "CCT" | "CCC" | "CCA" | "CCG" => 'P',
            "ACT" | "ACC" | "ACA" | "ACG" => 'T',
            "GCT" | "GCC" | "GCA" | "GCG" => 'A',
            "TAT" | "TAC" => 'Y',
            "CAT" | "CAC" => 'H',
            "CAA" | "CAG" => 'Q',
            "AAT" | "AAC" => 'N',
            "AAA" | "AAG" => 'K',
            "GAT" | "GAC" => 'D',
            "GAA" | "GAG" => 'E',
            "TGT" | "TGC" => 'C',
            "TGG" => 'W',
            "CGT" | "CGC" | "CGA" | "CGG" | "AGA" | "AGG" => 'R',
            "AGT" | "AGC" => 'S',
            "GGT" | "GGC" | "GGA" | "GGG" => 'G',
            "TAA" | "TAG" | "TGA" => break, // Stop codons
            _ => 'X', // Unknown
        };
        protein.push(aa);
    }
    protein
}

/// Filter reads from a FASTA/FASTQ file by minimum length.
/// Returns a list of sequences.
#[pyfunction]
pub fn filter_reads(file_path: String, min_length: usize) -> PyResult<Vec<String>> {
    let mut reader = parse_fastx_file(&file_path).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to open file: {}", e))
    })?;

    let mut filtered_seqs = Vec::new();
    
    while let Some(record) = reader.next() {
        let record = record.map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Error reading record: {}", e))
        })?;
        
        let seq = record.seq();
        if seq.len() >= min_length {
            // We usually want the sequence as string for Python
            let seq_str = String::from_utf8_lossy(&seq).into_owned();
            filtered_seqs.push(seq_str);
        }
    }
    
    Ok(filtered_seqs)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    // ... existing tests ...

    #[test]
    fn test_translate() {
        assert_eq!(translate("ATGCGT"), "MR".to_string());
        assert_eq!(translate("ATGCGTTAA"), "MR".to_string()); // Stop at TAA
        assert_eq!(translate("ATGCG"), "M".to_string()); // Partial at end ignored (ATGCG -> ATG, CG ignored)
        // Wait, standard behavior for chunks_exact is ignore remainder. 
        // ATG (M), CG (ignored). Correct.
        
        // Test stop codons
        assert_eq!(translate("TAG"), "".to_string());
        assert_eq!(translate("TGA"), "".to_string());
    }


    #[test]
    fn test_gc_content() {
        assert_eq!(gc_content("GCGC"), 100.0);
        assert_eq!(gc_content("ATAT"), 0.0);
        assert_eq!(gc_content("GATC"), 50.0);
        assert_eq!(gc_content(""), 0.0);
        assert_eq!(gc_content("gaTc"), 50.0); 
    }

    #[test]
    fn test_reverse_complement() {
        assert_eq!(reverse_complement("GTCA"), "TGAC".to_string());
        assert_eq!(reverse_complement("aaaa"), "TTTT".to_string());
        assert_eq!(reverse_complement(""), "".to_string());
        assert_eq!(reverse_complement("N"), "N".to_string());
    }

    #[test]
    fn test_trim_low_quality() {
        // Phred+33: 'I' = 73 (40), '#' = 35 (2)
        // Threshold 20 -> Cutoff 53
        let seq = "ACGTACGT";
        let qual = "IIII#III"; // Drop at index 4 (#)
        assert_eq!(trim_low_quality(seq, qual, 20), "ACGT".to_string());
        
        let qual_good = "IIIIIIII";
        assert_eq!(trim_low_quality(seq, qual_good, 20), "ACGTACGT".to_string());
    }
}
#[pyfunction]
fn process_file(py: Python, file_path: String) -> PyResult<PyObject> {
    // process_genome_parallel is "safe enough" to call directly given our usage patterns
    // but releasing GIL is better practice for long tasks.
    // For now we keep it simple as before since bench script worked.
    let result = process_genome_parallel(&file_path);
    
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("total_bases", result.total_bases)?;
    dict.set_item("sequences_count", result.sequences_count)?;
    
    Ok(dict.into())
}

#[pyfunction]
fn count_kmers(py: Python, file_path: String, k_size: usize) -> PyResult<PyObject> {
    // This is computationally intensive, release GIL to allow other Python threads to run
    // (Though simple benchmark scripts are usually single threaded).
    // rayon will use available cores regardless.
    
    // We accept String, convert to byte path
    let counts = py.allow_threads(|| {
        count_kmers_parallel(&file_path, k_size)
    });

    // Convert FxHashMap to Python Dictionary
    // This can be heavy for millions of k-mers!
    let dict = pyo3::types::PyDict::new(py);
    
    for (kmer_bytes, count) in counts {
        // Convert kmer bytes to string (assuming UTF-8/ASCII for DNA)
        // Using lossy to be safe, though DNA is ASCII.
        let kmer_str = String::from_utf8_lossy(&kmer_bytes);
        dict.set_item(kmer_str, count)?;
    }
    
    Ok(dict.into())
}
