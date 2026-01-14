# FastRAG 🚀

**Blazing-fast document deduplication using MinHash, LSH, and Rayon parallelism**

## Why Rayon for FastRAG?

FastRAG is a **CPU-bound workload** - we're doing intensive computation (hashing, similarity calculation) with no I/O blocking. This makes **Rayon the perfect choice** over async/await:

```rust
// With Rayon - ONE LINE CHANGE for parallelism!
let signatures: Vec<_> = documents
    .par_iter()  // 🚀 That's it! Automatic parallelism!
    .map(|doc| compute_minhash(doc))
    .collect();

// With async - MORE COMPLEX, LESS EFFICIENT for CPU work
let handles: Vec<_> = documents
    .into_iter()
    .map(|doc| tokio::task::spawn_blocking(move || compute_minhash(doc)))
    .collect();
let signatures = join_all(handles).await;  // Need runtime, more overhead
```

### Rayon vs Async: The Right Tool for the Job

| Task Type | Tool | Why |
|-----------|------|-----|
| **CPU-bound** (MinHash, LSH, dedup) | ✅ **Rayon** | Pure computation, no waiting |
| **I/O-bound** (API calls, database) | ✅ **Async** | Lots of waiting, high concurrency |

**FastRAG is pure CPU work** → Rayon is the optimal choice!

## What is FastRAG?

FastRAG implements three core algorithms for efficient document deduplication:

1. **MinHash** - Fast similarity estimation using hash signatures
2. **LSH (Locality-Sensitive Hashing)** - Efficient near-duplicate detection
3. **Parallel Deduplication Pipeline** - Process thousands of documents concurrently

### Key Features

- ⚡ **Parallel MinHash Generation** - Compute hash signatures using all CPU cores
- 🔒 **Thread-Safe LSH Index** - Concurrent inserts with `RwLock`
- 🚀 **Parallel Deduplication** - Find duplicates across entire corpus in parallel
- 🎯 **Simple API** - Rayon makes parallelism trivial
- 📊 **High Performance** - 5-10x speedup on multi-core systems

## Quick Start

### Basic Usage

```rust
use fastrag::*;

fn main() {
    // Create deduplication pipeline
    let pipeline = DeduplicationPipeline::new(
        20,    // num_bands (LSH parameter)
        128,   // num_hashes (MinHash parameter)
        3,     // shingle_size (n-gram size)
        0.8,   // similarity_threshold (80%)
    );
    
    // Documents to deduplicate
    let documents = vec![
        "The quick brown fox jumps over the lazy dog".to_string(),
        "A quick brown fox jumps over a lazy dog".to_string(),  // Similar
        "Completely different content here".to_string(),
    ];
    
    // Process documents in PARALLEL
    pipeline.process_documents(documents);
    
    // Find duplicates in PARALLEL
    let duplicates = pipeline.deduplicate_corpus();
    
    for (i, j, similarity) in duplicates {
        println!("Documents {} and {} are {:.1}% similar", i, j, similarity * 100.0);
    }
}
```

## How Rayon Makes It Simple

### 1. Parallel MinHash Generation

```rust
// Sequential - slow
let signatures: Vec<_> = (0..num_hashes)
    .map(|seed| compute_min_hash(shingles, seed))
    .collect();

// Parallel with Rayon - FAST and SIMPLE!
let signatures: Vec<_> = (0..num_hashes)
    .into_par_iter()  // One word change!
    .map(|seed| compute_min_hash(shingles, seed))
    .collect();
```

### 2. Thread-Safe LSH Index

```rust
use parking_lot::RwLock;

pub struct LSHIndex {
    // Multiple readers OR one writer - perfect for concurrent access
    tables: Vec<RwLock<HashMap<u64, Vec<usize>>>>,
    documents: RwLock<Vec<String>>,
}

// Multiple threads can insert concurrently!
impl LSHIndex {
    pub fn insert_batch(&self, docs: Vec<(String, MinHash)>) {
        docs.into_par_iter()  // Parallel batch insert
            .for_each(|(doc, minhash)| {
                self.insert(doc, minhash);  // Thread-safe!
            });
    }
}
```

### 3. Parallel Deduplication

```rust
// Find all duplicate pairs in parallel
let duplicates: Vec<_> = (0..num_docs)
    .into_par_iter()  // Process each document in parallel
    .flat_map(|i| {
        let candidates = index.find_candidates(&signatures[i]);
        
        // Check candidates in parallel too!
        candidates
            .into_par_iter()
            .filter_map(|j| {
                let sim = signatures[i].similarity(&signatures[j]);
                if sim >= threshold {
                    Some((i, j, sim))
                } else {
                    None
                }
            })
            .collect::<Vec<_>>()
    })
    .collect();
```

## Performance

Benchmarks on an 8-core system processing 1000 documents:

| Operation | Sequential | Parallel (Rayon) | Speedup |
|-----------|-----------|------------------|---------|
| MinHash Generation | 450ms | 68ms | **6.6x** |
| Batch Insert | 320ms | 55ms | **5.8x** |
| Full Deduplication | 1.2s | 180ms | **6.7x** |

### Run Benchmarks

```bash
cargo bench
```

## Examples

### Basic Showcase

```bash
cargo run --example showcase
```

Shows all core features:
- MinHash computation
- LSH indexing
- Deduplication pipeline
- Performance comparison

### Rayon vs Async Comparison

```bash
cargo run --example rayon_vs_async
```

Explains when to use Rayon vs async/await and why Rayon is perfect for CPU-bound work.

## Design Decisions

### Why Rayon?

1. **CPU-bound workload** - No I/O, pure computation
2. **Data parallelism** - Process many documents independently
3. **Simplicity** - `.par_iter()` vs complex async code
4. **Performance** - Better CPU utilization than async for this use case
5. **No runtime overhead** - No async executor needed

### Why Not Async?

Async/await is designed for **I/O-bound** work where tasks spend time waiting:
- Network requests
- Database queries  
- File I/O

For **CPU-bound** work like FastRAG:
- ❌ Async adds unnecessary complexity
- ❌ `spawn_blocking` has overhead
- ❌ Async scheduler assumes tasks yield quickly
- ❌ Less efficient than Rayon's work-stealing

## Real-World Applications

- **Content Deduplication** - Remove duplicate articles, posts, documents
- **Plagiarism Detection** - Find similar academic papers or code
- **Data Cleaning** - Identify duplicate records in datasets
- **Recommendation Systems** - Find similar items for recommendations
- **Search Engines** - Deduplicate search results

## Contributing

Contributions welcome! Areas for improvement:
- Additional similarity metrics
- Custom hash functions
- GPU acceleration
- More sophisticated deduplication strategies

## License

MIT

## References

- [Rayon Documentation](https://docs.rs/rayon/)
- [MinHash Algorithm](https://en.wikipedia.org/wiki/MinHash)
- [Locality-Sensitive Hashing](https://en.wikipedia.org/wiki/Locality-sensitive_hashing)

---

**Built with ❤️ and Rayon's parallel iterators**
