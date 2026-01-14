use fastrustrag::*;
use std::time::Instant;

fn main() {
    println!("🚀 FastRAG with Rayon - CPU-bound Parallelism Made Simple!\n");
    
    // Example 1: Basic MinHash computation
    println!("📝 Example 1: Parallel MinHash Generation");
    println!("{}", "=".repeat(60));
    example_minhash();
    println!();
    
    // Example 2: LSH Index with concurrent inserts
    println!("🗂️  Example 2: Thread-Safe LSH Index");
    println!("{}", "=".repeat(60));
    example_lsh_index();
    println!();
    
    // Example 3: Full deduplication pipeline
    println!("🔍 Example 3: Parallel Deduplication Pipeline");
    println!("{}", "=".repeat(60));
    example_deduplication();
    println!();
    
    // Example 4: Performance comparison
    println!("⚡ Example 4: Rayon Performance Showcase");
    println!("{}", "=".repeat(60));
    example_performance();
    println!();
    
    // Example 5: Real-world scenario
    println!("🌍 Example 5: Real-World Document Deduplication");
    println!("{}", "=".repeat(60));
    example_real_world();
}

fn example_minhash() {
    let text = "The quick brown fox jumps over the lazy dog";
    
    // Generate shingles (3-grams)
    let shingles = generate_shingles(text, 3);
    println!("Generated {} shingles from text", shingles.len());
    println!("Sample shingles: {:?}", &shingles[..3.min(shingles.len())]);
    
    // Compute MinHash with 128 hash functions IN PARALLEL
    // Rayon automatically uses all CPU cores!
    let start = Instant::now();
    let minhash = MinHash::from_shingles(&shingles, 128);
    let elapsed = start.elapsed();
    
    println!("✅ Computed MinHash with 128 hashes in {:?}", elapsed);
    println!("   (Rayon parallelized across {} cores)", num_cpus::get());
    
    // Compare with similar text
    let text2 = "The quick brown fox jumps over the sleepy dog";
    let shingles2 = generate_shingles(text2, 3);
    let minhash2 = MinHash::from_shingles(&shingles2, 128);
    
    let similarity = minhash.similarity(&minhash2);
    println!("📊 Similarity: {:.2}%", similarity * 100.0);
}

fn example_lsh_index() {
    // Create LSH index with 20 bands
    let index = LSHIndex::new(20);
    println!("Created LSH index with 20 bands");
    
    // Insert some documents
    let docs = vec![
        "Machine learning is a subset of artificial intelligence",
        "Deep learning is a subset of machine learning",
        "Neural networks are used in deep learning",
        "Artificial intelligence includes machine learning",
    ];
    
    let start = Instant::now();
    for (i, doc) in docs.iter().enumerate() {
        let shingles = generate_shingles(doc, 2);
        let minhash = MinHash::from_shingles(&shingles, 100);
        index.insert(doc.to_string(), minhash);
        println!("  Inserted doc {}: '{}'", i, &doc[..40.min(doc.len())]);
    }
    let elapsed = start.elapsed();
    
    println!("✅ Inserted {} documents in {:?}", docs.len(), elapsed);
    println!("   (Thread-safe inserts using RwLock)");
    
    // Find similar documents
    let query = "Machine learning and AI are related";
    let query_shingles = generate_shingles(query, 2);
    let query_minhash = MinHash::from_shingles(&query_shingles, 100);
    
    let candidates = index.find_candidates(&query_minhash);
    println!("\n🔎 Query: '{}'", query);
    println!("   Found {} candidate documents", candidates.len());
    
    // Calculate similarities
    for &doc_id in &candidates {
        let doc = index.get_document(doc_id).unwrap();
        let sig = index.get_signature(doc_id).unwrap();
        let sim = query_minhash.similarity(&sig);
        println!("   Doc {}: {:.1}% similar - '{}'", 
                 doc_id, sim * 100.0, &doc[..40.min(doc.len())]);
    }
}

fn example_deduplication() {
    // Create pipeline
    let pipeline = DeduplicationPipeline::new(
        20,    // num_bands
        128,   // num_hashes
        3,     // shingle_size (3-grams)
        0.7,   // similarity_threshold (70%)
    );
    
    println!("Created deduplication pipeline:");
    let stats = pipeline.stats();
    println!("  Bands: {}, Hashes: {}, Shingle size: {}", 
             stats.num_bands, stats.num_hashes, stats.shingle_size);
    
    // Create test documents with some duplicates
    let documents = vec![
        "The quick brown fox jumps over the lazy dog".to_string(),
        "A quick brown fox jumps over a lazy dog".to_string(),  // Similar
        "Completely different content about cats and mice".to_string(),
        "The quick brown fox jumps over the lazy dog".to_string(),  // Exact duplicate
        "Another unrelated document about programming".to_string(),
        "The fast brown fox leaps over the sleepy dog".to_string(),  // Similar
    ];
    
    // Process documents in PARALLEL
    let start = Instant::now();
    let count = pipeline.process_documents(documents);
    let process_time = start.elapsed();
    
    println!("\n✅ Processed {} documents in {:?}", count, process_time);
    
    // Find duplicates in PARALLEL
    let start = Instant::now();
    let duplicates = pipeline.deduplicate_corpus();
    let dedup_time = start.elapsed();
    
    println!("✅ Found {} duplicate pairs in {:?}", duplicates.len(), dedup_time);
    println!("\n📋 Duplicate pairs:");
    for (i, j, similarity) in duplicates {
        let doc_i = pipeline.index.get_document(i).unwrap();
        let doc_j = pipeline.index.get_document(j).unwrap();
        println!("\n  Pair ({}, {}) - Similarity: {:.1}%", i, j, similarity * 100.0);
        println!("    Doc {}: {}", i, &doc_i[..50.min(doc_i.len())]);
        println!("    Doc {}: {}", j, &doc_j[..50.min(doc_j.len())]);
    }
}

fn example_performance() {
    println!("Comparing sequential vs parallel processing...\n");
    
    // Generate test data
    let num_docs = 500;
    let documents: Vec<_> = (0..num_docs)
        .map(|i| {
            format!(
                "Document {} contains various content about topic {} with details {}",
                i, i % 10, i * 37
            )
        })
        .collect();
    
    println!("Test corpus: {} documents", num_docs);
    
    // Method 1: Sequential processing (simulated)
    println!("\n⏱️  Sequential approach (simulated):");
    let start = Instant::now();
    let mut seq_count = 0;
    for doc in documents.iter().take(50) {  // Just sample
        let shingles = generate_shingles(doc, 3);
        let _minhash = MinHash::from_shingles(&shingles, 128);
        seq_count += 1;
    }
    let seq_time = start.elapsed();
    let estimated_total = seq_time * (num_docs / 50);
    println!("   Processed {} docs in {:?}", seq_count, seq_time);
    println!("   Estimated total time: {:?}", estimated_total);
    
    // Method 2: Parallel with Rayon
    println!("\n🚀 Parallel with Rayon:");
    let pipeline = DeduplicationPipeline::new(20, 128, 3, 0.7);
    let start = Instant::now();
    let par_count = pipeline.process_documents(documents.clone());
    let par_time = start.elapsed();
    println!("   Processed {} docs in {:?}", par_count, par_time);
    
    // Calculate speedup
    let speedup = estimated_total.as_secs_f64() / par_time.as_secs_f64();
    println!("\n⚡ Speedup: {:.1}x faster!", speedup);
    println!("   Rayon automatically used all {} CPU cores", num_cpus::get());
    
    // Show how simple the code is
    println!("\n💡 Why Rayon is perfect for CPU-bound work:");
    println!("   ✅ Just change .iter() to .par_iter()");
    println!("   ✅ No async/await complexity");
    println!("   ✅ Automatic work-stealing scheduler");
    println!("   ✅ Thread pool managed for you");
    println!("   ✅ Perfect for CPU-heavy tasks (hashing, computation)");
}

fn example_real_world() {
    println!("Scenario: Deduplicating a large corpus of articles\n");
    
    // Simulate real articles
    let articles = vec![
        "Climate change is causing unprecedented weather patterns across the globe. \
         Scientists warn that immediate action is needed to prevent catastrophic consequences.",
        
        "Global warming leads to extreme weather events worldwide. \
         Researchers emphasize urgent measures required to avoid disastrous outcomes.",
        
        "The latest smartphone features an advanced camera system with AI enhancements. \
         Battery life has been improved significantly in this new model.",
        
        "Technology companies announce breakthrough in quantum computing research. \
         This development could revolutionize data processing capabilities.",
        
        "Climate change causes unusual weather patterns around the world. \
         Experts stress that swift action is essential to prevent severe repercussions.",
        
        "New study reveals the impact of diet on long-term health outcomes. \
         Mediterranean diet shows promising results in reducing disease risk.",
    ];
    
    println!("Processing {} articles...", articles.len());
    
    // Create pipeline with strict similarity threshold
    let pipeline = DeduplicationPipeline::new(
        25,    // More bands for better precision
        200,   // More hashes for better accuracy
        4,     // 4-word shingles for articles
        0.75,  // 75% similarity threshold
    );
    
    // Process articles
    let start = Instant::now();
    let count = pipeline.process_documents(
        articles.iter().map(|s| s.to_string()).collect()
    );
    let elapsed = start.elapsed();
    
    println!("✅ Indexed {} articles in {:?}", count, elapsed);
    
    // Find duplicate groups
    let duplicates = pipeline.deduplicate_corpus();
    
    println!("\n📊 Deduplication Results:");
    println!("   Total documents: {}", count);
    println!("   Duplicate pairs found: {}", duplicates.len());
    println!("   Unique documents: {}", count - duplicates.len());
    
    if !duplicates.is_empty() {
        println!("\n🔍 Detected near-duplicates:");
        for (i, j, similarity) in duplicates {
            println!("\n  Articles {} and {} ({:.1}% similar):", i, j, similarity * 100.0);
            let doc_i = pipeline.index.get_document(i).unwrap();
            let doc_j = pipeline.index.get_document(j).unwrap();
            println!("    📄 [{}]: {}...", i, &doc_i[..80.min(doc_i.len())]);
            println!("    📄 [{}]: {}...", j, &doc_j[..80.min(doc_j.len())]);
        }
    }
    
    println!("\n💡 Real-world applications:");
    println!("   • News article deduplication");
    println!("   • Plagiarism detection");
    println!("   • Document clustering");
    println!("   • Content recommendation");
    println!("   • Data cleaning pipelines");
}

// Helper to get CPU count
mod num_cpus {
    pub fn get() -> usize {
        std::thread::available_parallelism()
            .map(|n| n.get())
            .unwrap_or(1)
    }
}
