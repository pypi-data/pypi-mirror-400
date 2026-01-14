# FastRAG Quick Start Guide

Get up and running with FastRAG in 5 minutes!

## Installation

Your `Cargo.toml` already has everything you need!

## Basic Usage - 3 Steps

### Step 1: Create Pipeline

```rust
use fastrag::*;

let pipeline = DeduplicationPipeline::new(
    20,    // num_bands (LSH parameter)
    128,   // num_hashes (MinHash parameter)
    3,     // shingle_size (n-gram size)
    0.8,   // similarity_threshold (80%)
);
```

### Step 2: Process Documents

```rust
let documents = vec![
    "The quick brown fox jumps over the lazy dog".to_string(),
    "A quick brown fox jumps over a lazy dog".to_string(),
    "Completely different content here".to_string(),
];

// Process in PARALLEL automatically!
pipeline.process_documents(documents);
```

### Step 3: Find Duplicates

```rust
// Find all duplicates in PARALLEL
let duplicates = pipeline.deduplicate_corpus();

for (i, j, similarity) in duplicates {
    println!("Docs {} and {} are {:.1}% similar", i, j, similarity * 100.0);
}
```

That's it! Rayon handles all the parallelism automatically! 🚀

## Run the Examples

```bash
# Main demo
cargo run

# Showcase all features
cargo run --example showcase

# Understand Rayon vs Async
cargo run --example rayon_vs_async

# Run tests
cargo test

# Run benchmarks
cargo bench
```

## Parameter Tuning

### num_bands (LSH)
- **Higher** (30-40): Better precision, might miss some duplicates
- **Lower** (10-15): Better recall, more false positives
- **Recommended**: 20-25

### num_hashes (MinHash)
- **Higher** (200-500): More accurate similarity
- **Lower** (64-128): Faster computation
- **Recommended**: 128-256

### shingle_size (n-grams)
- **Larger** (4-5): Better for longer documents
- **Smaller** (2-3): Better for short texts
- **Recommended**: 3

### similarity_threshold
- **Higher** (0.85-0.95): Only very similar documents
- **Lower** (0.60-0.75): Catch more duplicates
- **Recommended**: 0.75-0.85

## What Makes This Fast?

### The Rayon Magic: One-Line Parallelism

```rust
// Sequential
documents.iter()

// Parallel - ONE WORD CHANGE!
documents.par_iter()
```

That's it! That's the power of Rayon! 🚀

## Next Steps

1. **Read README.md** - Full documentation
2. **Run examples** - See it in action
3. **Read RAYON_GUIDE.md** - Deep dive into patterns
4. **Read COMPARISON.md** - See all approaches compared

Happy deduplicating! 🚀
