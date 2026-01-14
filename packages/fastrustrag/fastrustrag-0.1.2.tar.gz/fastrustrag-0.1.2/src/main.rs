use fastrustrag::*;
use std::time::Instant;

fn main() {
    println!("\n╔══════════════════════════════════════════════════════════╗");
    println!("║             FastRAG with Rayon Parallelism              ║");
    println!("║     CPU-Bound Document Deduplication Made Simple        ║");
    println!("╚══════════════════════════════════════════════════════════╝\n");
    
    demo_simple_deduplication();
    println!("\n{}", "─".repeat(60));
    
    demo_performance();
    println!("\n{}", "─".repeat(60));
    
    demo_real_world();
}

fn demo_simple_deduplication() {
    println!("🎯 DEMO 1: Simple Deduplication");
    println!("{}", "=".repeat(60));
    
    let pipeline = DeduplicationPipeline::new(
        20,   // 20 LSH bands
        128,  // 128 hash functions
        3,    // 3-word shingles
        0.75, // 75% similarity threshold
    );
    
    let documents = vec![
        "The quick brown fox jumps over the lazy dog".to_string(),
        "A quick brown fox jumps over a lazy dog".to_string(),
        "The fast brown fox leaps over the sleepy dog".to_string(),
        "Completely different content about machine learning".to_string(),
        "The quick brown fox jumps over the lazy dog".to_string(),  // Exact duplicate
    ];
    
    println!("\n📄 Processing {} documents...", documents.len());
    for (i, doc) in documents.iter().enumerate() {
        println!("  [{}] {}", i, doc);
    }
    
    let start = Instant::now();
    pipeline.process_documents(documents);
    let elapsed = start.elapsed();
    
    println!("\n✅ Processed in {:?}", elapsed);
    
    let duplicates = pipeline.deduplicate_corpus();
    
    println!("\n🔍 Found {} duplicate pairs:", duplicates.len());
    for (i, j, similarity) in duplicates {
        let doc_i = pipeline.index.get_document(i).unwrap();
        let doc_j = pipeline.index.get_document(j).unwrap();
        println!("\n  📋 Pair ({}, {}) - Similarity: {:.1}%", i, j, similarity * 100.0);
        println!("     [{}] {}", i, doc_i);
        println!("     [{}] {}", j, doc_j);
    }
}

fn demo_performance() {
    println!("\n⚡ DEMO 2: Performance Showcase");
    println!("{}", "=".repeat(60));
    
    let sizes = [100, 500, 1000];
    
    for &size in &sizes {
        println!("\n📊 Processing {} documents...", size);
        
        let documents: Vec<String> = (0..size)
            .map(|i: u32| {
                format!(
                    "Document {} contains information about topic {} with details {} and more content {}",
                    i, i % 20, i * 37, i.pow(2)
                )
            })
            .collect();
        
        let pipeline = DeduplicationPipeline::new(20, 128, 3, 0.7);
        
        // Processing
        let start = Instant::now();
        pipeline.process_documents(documents);
        let process_time = start.elapsed();
        
        // Deduplication
        let start = Instant::now();
        let duplicates = pipeline.deduplicate_corpus();
        let dedup_time = start.elapsed();
        
        println!("   Process time: {:?}", process_time);
        println!("   Dedup time:   {:?}", dedup_time);
        println!("   Total:        {:?}", process_time + dedup_time);
        println!("   Duplicates:   {}", duplicates.len());
        
        let throughput = size as f64 / (process_time + dedup_time).as_secs_f64();
        println!("   Throughput:   {:.0} docs/sec", throughput);
    }
    
    println!("\n💡 Rayon Advantages:");
    println!("   • Automatic work-stealing across CPU cores");
    println!("   • No async/await complexity");
    println!("   • Perfect for CPU-bound tasks");
    println!("   • Just change .iter() → .par_iter()!");
}

fn demo_real_world() {
    println!("\n🌍 DEMO 3: Real-World News Deduplication");
    println!("{}", "=".repeat(60));
    
    let news_articles = vec![
        "Breaking: Climate summit reaches historic agreement on emissions reduction. \
         World leaders commit to ambitious targets for carbon neutrality by 2050.",
        
        "Historic climate summit concludes with landmark emissions agreement. \
         Global leaders pledge to achieve carbon neutrality goals by mid-century.",
        
        "Technology giants announce breakthrough in quantum computing research. \
         New quantum chip demonstrates supremacy over classical computers.",
        
        "Scientists discover potential vaccine candidate for emerging virus. \
         Clinical trials show promising results in early-stage testing.",
        
        "Major tech companies reveal quantum computing advancement. \
         Revolutionary quantum processor outperforms traditional computing systems.",
        
        "Local community celebrates opening of new public library and community center. \
         Residents gather for ribbon-cutting ceremony and celebration.",
    ];
    
    println!("\n📰 Processing {} news articles...", news_articles.len());
    
    let pipeline = DeduplicationPipeline::new(
        25,    // More bands for better precision
        200,   // More hashes for better accuracy  
        4,     // 4-word shingles for longer matches
        0.70,  // 70% threshold for news
    );
    
    let start = Instant::now();
    pipeline.process_documents(
        news_articles.iter().map(|s| s.to_string()).collect()
    );
    let elapsed = start.elapsed();
    
    println!("✅ Indexed in {:?}", elapsed);
    
    let duplicates = pipeline.deduplicate_corpus();
    
    println!("\n📊 Results:");
    println!("   Total articles:    {}", news_articles.len());
    println!("   Duplicate groups:  {}", duplicates.len());
    println!("   Unique articles:   {}", news_articles.len() - duplicates.len());
    
    if !duplicates.is_empty() {
        println!("\n🔍 Near-duplicate stories detected:");
        for (i, j, similarity) in duplicates {
            println!("\n  Story Group ({:.0}% similar)", similarity * 100.0);
            let article_i = &news_articles[i];
            let article_j = &news_articles[j];
            println!("    [{}] {}...", i, &article_i[..80.min(article_i.len())]);
            println!("    [{}] {}...", j, &article_j[..80.min(article_j.len())]);
        }
    }
    
    println!("\n💼 Real-world applications:");
    println!("   • News aggregation (remove duplicate stories)");
    println!("   • Content moderation (detect spam/reposts)");
    println!("   • Document management (deduplicate files)");
    println!("   • Plagiarism detection (find copied content)");
    println!("   • Data cleaning (merge duplicate records)");
    
    println!("\n🚀 Why Rayon makes this fast:");
    println!("   • MinHash: Parallel hash generation across cores");
    println!("   • LSH: Thread-safe concurrent inserts");
    println!("   • Dedup: Parallel candidate checking");
    println!("   • Result: Linear scaling with CPU cores!");
}
