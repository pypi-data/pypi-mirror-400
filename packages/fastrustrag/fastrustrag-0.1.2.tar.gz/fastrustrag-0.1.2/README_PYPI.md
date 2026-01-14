# FastRustRAG

Rust-based document deduplication for RAG pipelines. 50-100x faster than Python implementations.

## Why?

Python's MinHash libraries are slow. This uses Rust + Rayon for parallel processing. Built it because I needed fast deduplication for preprocessing large document collections.

## Performance

Benchmarked against datasketch (popular Python MinHash library):

| Documents | Python | FastRustRAG | Speedup |
|-----------|---------|-------------|---------|
| 500 | 246ms | 2ms | 121x |
| 1,000 | 414ms | 5ms | 81x |
| 2,000 | 838ms | 10ms | 79x |
| 5,000 | 2.1s | 38ms | 56x |
| 10,000 | 4.2s | 360ms | 11x |
| 50,000 | 21s | 2.4s | 8x |

Best performance on 500-5000 document batches (typical RAG use case).

## Installation

```bash
pip install fastrustrag
```

## Usage

```python
import fastrustrag

# Create pipeline
pipeline = fastrustrag.DeduplicationPipeline(
    num_bands=20,
    num_hashes=128,
    shingle_size=3,
    similarity_threshold=0.8
)

# Your documents
docs = [
    "The quick brown fox jumps over the lazy dog",
    "A quick brown fox jumps over a lazy dog",
    "Completely different content",
]

# Process and find duplicates
pipeline.process_documents(docs)
duplicates = pipeline.deduplicate_corpus()

for i, j, similarity in duplicates:
    print(f"Docs {i} and {j} are {similarity*100:.1f}% similar")
```

## API

### DeduplicationPipeline

**Parameters:**
- `num_bands` (int): LSH bands. Higher = more precision, fewer false positives. Default: 20
- `num_hashes` (int): MinHash functions. Higher = more accuracy, slower. Default: 128
- `shingle_size` (int): n-gram size. Use 2-3 for short texts, 3-5 for longer documents. Default: 3
- `similarity_threshold` (float): Minimum similarity (0-1) to consider duplicates. Default: 0.8

**Methods:**

```python
# Process documents (returns count)
count = pipeline.process_documents(documents: list[str]) -> int

# Find all duplicate pairs
duplicates = pipeline.deduplicate_corpus() -> list[tuple[int, int, float]]
# Returns: [(doc_id1, doc_id2, similarity), ...]

# Find duplicates for specific query
results = pipeline.find_duplicates(query: str) -> list[tuple[int, str, float]]

# Get document by ID
doc = pipeline.get_document(doc_id: int) -> str | None
```

## How it works

1. **MinHash**: Generates hash signatures for fast similarity estimation
2. **LSH**: Locality-sensitive hashing for efficient candidate generation
3. **Rayon**: Automatic parallelization across CPU cores

The speedup comes from:
- Compiled Rust (no Python interpreter overhead)
- Parallel processing with Rayon (uses all cores)
- Efficient memory layout

## Use cases

- Remove duplicate documents before indexing for RAG
- Deduplicate web scraping results
- Find plagiarized or copied content
- Clean datasets before training

## Technical details

- Built with PyO3 for Python bindings
- Uses Rayon for data parallelism
- Thread-safe with RwLock for concurrent access
- AHash for fast non-cryptographic hashing

## License

MIT

## Contributing

Issues and PRs welcome. Main areas for improvement:
- Streaming API for very large datasets
- Additional distance metrics
- Persistence (save/load index)
