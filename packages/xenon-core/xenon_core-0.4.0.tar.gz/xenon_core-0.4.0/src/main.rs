use std::time::Instant;
use xenon_core::process_genome_parallel;

fn main() {
    let file_path = "test.fa";
    println!("Processing {}...", file_path);

    let start = Instant::now();
    let result = process_genome_parallel(file_path);
    let duration = start.elapsed();

    println!("Processed in {} microseconds", duration.as_micros());
    println!("Result: {:?}", result);
}
