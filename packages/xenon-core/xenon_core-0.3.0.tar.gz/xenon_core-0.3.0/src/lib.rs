use needletail::parse_fastx_file;
use rayon::prelude::*;
use std::path::Path;
use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use rustc_hash::FxHashMap;

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
    Ok(())
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
