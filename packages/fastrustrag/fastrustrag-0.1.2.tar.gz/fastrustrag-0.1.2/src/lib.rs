use rayon::prelude::*;
use ahash::AHasher;
use std::collections::{HashMap, HashSet};
use std::hash::{Hash, Hasher};
use std::sync::Arc;
use parking_lot::RwLock;

// Python bindings module
mod python;
pub use python::*;

/// MinHash signature for document similarity
/// Uses parallel hashing for speed
#[derive(Debug, Clone)]
pub struct MinHash {
    /// Number of hash functions
    num_hashes: usize,
    /// The signature (minimum hash values)
    pub signature: Vec<u64>,
}

impl MinHash {
    /// Create a new MinHash with specified number of hash functions
    pub fn new(num_hashes: usize) -> Self {
        Self {
            num_hashes,
            signature: vec![u64::MAX; num_hashes],
        }
    }

    /// Generate MinHash signature from shingles (tokens) in PARALLEL
    /// This is where Rayon shines - trivial parallelism!
    pub fn from_shingles(shingles: &[String], num_hashes: usize) -> Self {
        let mut minhash = Self::new(num_hashes);
        
        // PARALLEL hash generation - Rayon makes this ONE LINE!
        // Each hash function is computed in parallel
        let signatures: Vec<u64> = (0..num_hashes)
            .into_par_iter()  // 🚀 Parallel iterator - SO EASY!
            .map(|seed| {
                // For this hash function, find minimum hash of all shingles
                shingles
                    .iter()
                    .map(|shingle| Self::hash_with_seed(shingle, seed))
                    .min()
                    .unwrap_or(u64::MAX)
            })
            .collect();
        
        minhash.signature = signatures;
        minhash
    }

    /// Hash a string with a specific seed (hash function index)
    fn hash_with_seed(s: &str, seed: usize) -> u64 {
        let mut hasher = AHasher::default();
        seed.hash(&mut hasher);
        s.hash(&mut hasher);
        hasher.finish()
    }

    /// Estimate Jaccard similarity between two MinHash signatures
    pub fn similarity(&self, other: &MinHash) -> f64 {
        assert_eq!(self.num_hashes, other.num_hashes);
        
        let matches = self.signature
            .iter()
            .zip(other.signature.iter())
            .filter(|(a, b)| a == b)
            .count();
        
        matches as f64 / self.num_hashes as f64
    }

    /// Get LSH bands for this signature
    pub fn get_bands(&self, num_bands: usize) -> Vec<Vec<u64>> {
        let rows_per_band = self.num_hashes / num_bands;
        
        self.signature
            .chunks(rows_per_band)
            .take(num_bands)  // CRITICAL: Only take exactly num_bands!
            .map(|chunk| chunk.to_vec())
            .collect()
    }
}

/// Thread-safe LSH Index using Rayon + parking_lot
/// No async/await complexity - just simple concurrent data structures!
pub struct LSHIndex {
    /// Number of bands for LSH
    pub num_bands: usize,
    /// Hash tables (one per band) - thread-safe with RwLock
    /// RwLock allows multiple readers OR one writer
    tables: Vec<RwLock<HashMap<u64, Vec<usize>>>>,
    /// Store documents
    documents: RwLock<Vec<String>>,
    /// Store MinHash signatures
    signatures: RwLock<Vec<MinHash>>,
}

impl LSHIndex {
    /// Create a new LSH index
    pub fn new(num_bands: usize) -> Self {
        let tables = (0..num_bands)
            .map(|_| RwLock::new(HashMap::new()))
            .collect();
        
        Self {
            num_bands,
            tables,
            documents: RwLock::new(Vec::new()),
            signatures: RwLock::new(Vec::new()),
        }
    }

    /// Insert a document - THREAD-SAFE!
    /// Multiple threads can call this concurrently
    pub fn insert(&self, doc: String, minhash: MinHash) {
        let bands = minhash.get_bands(self.num_bands);
        
        // Get document ID
        let doc_id = {
            let mut docs = self.documents.write();
            let mut sigs = self.signatures.write();
            let id = docs.len();
            docs.push(doc);
            sigs.push(minhash);
            id
        };
        
        // Insert into each band's hash table
        // Each band can be updated independently (but we do it sequentially here)
        for (band_id, band) in bands.iter().enumerate() {
            let band_hash = Self::hash_band(band);
            let mut table = self.tables[band_id].write();
            table.entry(band_hash)
                .or_insert_with(Vec::new)
                .push(doc_id);
        }
    }

    /// PARALLEL batch insert - insert many documents at once
    /// This is where Rayon really shines!
    pub fn insert_batch(&self, docs: Vec<(String, MinHash)>) {
        docs.into_par_iter()  // 🚀 Parallel processing!
            .for_each(|(doc, minhash)| {
                self.insert(doc, minhash);
            });
    }

    /// Find candidate duplicates for a document
    pub fn find_candidates(&self, minhash: &MinHash) -> HashSet<usize> {
        let bands = minhash.get_bands(self.num_bands);
        let mut candidates = HashSet::new();
        
        // Check each band
        for (band_id, band) in bands.iter().enumerate() {
            let band_hash = Self::hash_band(band);
            let table = self.tables[band_id].read();
            
            if let Some(doc_ids) = table.get(&band_hash) {
                candidates.extend(doc_ids.iter().copied());
            }
        }
        
        candidates
    }

    /// Get document by ID
    pub fn get_document(&self, id: usize) -> Option<String> {
        self.documents.read().get(id).cloned()
    }

    /// Get signature by ID
    pub fn get_signature(&self, id: usize) -> Option<MinHash> {
        self.signatures.read().get(id).cloned()
    }

    /// Total documents in index
    pub fn len(&self) -> usize {
        self.documents.read().len()
    }

    /// Check if index is empty
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Hash a band to a single value
    fn hash_band(band: &[u64]) -> u64 {
        let mut hasher = AHasher::default();
        band.hash(&mut hasher);
        hasher.finish()
    }
}

/// Document shingle generator - converts text to n-grams
pub fn generate_shingles(text: &str, n: usize) -> Vec<String> {
    let words: Vec<&str> = text.split_whitespace().collect();
    
    if words.len() < n {
        return vec![words.join(" ")];
    }
    
    words.windows(n)
        .map(|window| window.join(" "))
        .collect()
}

/// PARALLEL DEDUPLICATION PIPELINE
/// This is the main workflow showing Rayon's power!
pub struct DeduplicationPipeline {
    pub index: Arc<LSHIndex>,
    num_hashes: usize,
    shingle_size: usize,
    similarity_threshold: f64,
}

impl DeduplicationPipeline {
    pub fn new(
        num_bands: usize,
        num_hashes: usize,
        shingle_size: usize,
        similarity_threshold: f64,
    ) -> Self {
        Self {
            index: Arc::new(LSHIndex::new(num_bands)),
            num_hashes,
            shingle_size,
            similarity_threshold,
        }
    }

    /// Process documents in PARALLEL
    /// 1. Generate shingles (parallel)
    /// 2. Compute MinHash (parallel)
    /// 3. Insert into LSH index (thread-safe)
    pub fn process_documents(&self, documents: Vec<String>) -> usize {
        println!("🚀 Processing {} documents in parallel...", documents.len());
        
        // PARALLEL document processing
        let processed: Vec<_> = documents
            .into_par_iter()  // 🔥 Rayon magic - automatic work-stealing!
            .map(|doc| {
                // Each document processed independently
                let shingles = generate_shingles(&doc, self.shingle_size);
                let minhash = MinHash::from_shingles(&shingles, self.num_hashes);
                (doc, minhash)
            })
            .collect();
        
        // Batch insert (also parallel internally)
        self.index.insert_batch(processed);
        
        self.index.len()
    }

    /// Find duplicates for a query document in PARALLEL
    pub fn find_duplicates(&self, query: &str) -> Vec<(usize, String, f64)> {
        // Generate signature for query
        let shingles = generate_shingles(query, self.shingle_size);
        let query_minhash = MinHash::from_shingles(&shingles, self.num_hashes);
        
        // Get candidate documents
        let candidates = self.index.find_candidates(&query_minhash);
        
        // PARALLEL similarity computation
        let results: Vec<_> = candidates
            .into_par_iter()  // 🚀 Parallel again!
            .filter_map(|doc_id| {
                let sig = self.index.get_signature(doc_id)?;
                let similarity = query_minhash.similarity(&sig);
                
                if similarity >= self.similarity_threshold {
                    let doc = self.index.get_document(doc_id)?;
                    Some((doc_id, doc, similarity))
                } else {
                    None
                }
            })
            .collect();
        
        results
    }

    /// Deduplicate entire corpus - find ALL duplicate pairs in PARALLEL
    pub fn deduplicate_corpus(&self) -> Vec<(usize, usize, f64)> {
        let num_docs = self.index.len();
        println!("🔍 Finding duplicates in {} documents...", num_docs);
        
        // PARALLEL duplicate detection
        let duplicates: Vec<_> = (0..num_docs)
            .into_par_iter()  // 🚀 Process each document in parallel
            .flat_map(|i| {
                let sig_i = match self.index.get_signature(i) {
                    Some(s) => s,
                    None => return vec![],
                };
                
                let candidates = self.index.find_candidates(&sig_i);
                
                // Check candidates after current document (avoid duplicates)
                candidates
                    .into_iter()
                    .filter(|&j| j > i)
                    .filter_map(|j| {
                        let sig_j = self.index.get_signature(j)?;
                        let similarity = sig_i.similarity(&sig_j);
                        
                        if similarity >= self.similarity_threshold {
                            Some((i, j, similarity))
                        } else {
                            None
                        }
                    })
                    .collect::<Vec<_>>()
            })
            .collect();
        
        duplicates
    }

    /// Get statistics about the index
    pub fn stats(&self) -> IndexStats {
        IndexStats {
            num_documents: self.index.len(),
            num_bands: self.index.num_bands,
            num_hashes: self.num_hashes,
            shingle_size: self.shingle_size,
        }
    }
}

#[derive(Debug)]
pub struct IndexStats {
    pub num_documents: usize,
    pub num_bands: usize,
    pub num_hashes: usize,
    pub shingle_size: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_minhash_similarity() {
        let shingles1 = vec!["hello world".to_string(), "world hello".to_string()];
        let shingles2 = vec!["hello world".to_string(), "hello there".to_string()];
        
        let mh1 = MinHash::from_shingles(&shingles1, 128);
        let mh2 = MinHash::from_shingles(&shingles2, 128);
        
        let sim = mh1.similarity(&mh2);
        assert!(sim > 0.0 && sim < 1.0);
    }

    #[test]
    fn test_lsh_insert_and_find() {
        let index = LSHIndex::new(20);
        let doc = "hello world this is a test".to_string();
        let shingles = generate_shingles(&doc, 2);
        let minhash = MinHash::from_shingles(&shingles, 128);
        
        index.insert(doc.clone(), minhash.clone());
        
        let candidates = index.find_candidates(&minhash);
        assert!(candidates.contains(&0));
    }

    #[test]
    fn test_deduplication_pipeline() {
        let pipeline = DeduplicationPipeline::new(20, 128, 2, 0.8);
        
        let docs = vec![
            "The quick brown fox jumps over the lazy dog".to_string(),
            "The quick brown fox jumps over the lazy dog".to_string(), // duplicate
            "A completely different document here".to_string(),
        ];
        
        pipeline.process_documents(docs);
        
        let duplicates = pipeline.deduplicate_corpus();
        assert_eq!(duplicates.len(), 1); // Should find one duplicate pair
        assert!(duplicates[0].2 > 0.9); // High similarity
    }

    #[test]
    fn test_parallel_processing() {
        use std::time::Instant;
        
        let pipeline = DeduplicationPipeline::new(20, 128, 3, 0.7);
        
        // Generate many documents
        let docs: Vec<_> = (0..1000)
            .map(|i| format!("Document number {} with some text content here", i))
            .collect();
        
        let start = Instant::now();
        pipeline.process_documents(docs);
        let elapsed = start.elapsed();
        
        println!("⏱️  Processed 1000 documents in {:?}", elapsed);
        assert!(elapsed.as_secs() < 5); // Should be fast!
    }
}
