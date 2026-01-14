use fastrustrag::*;
use std::time::Instant;
use rayon::prelude::*;

/// This example demonstrates WHY Rayon is better than async/await for CPU-bound work
/// 
/// Key Insights:
/// 1. Async is for I/O-bound work (network, disk, waiting)
/// 2. Rayon is for CPU-bound work (computation, hashing, processing)
/// 3. Using async for CPU-bound work is COUNTERPRODUCTIVE

fn main() {
    println!("🔬 Rayon vs Async: Choosing the Right Tool\n");
    println!("{}", "=".repeat(70));
    
    explain_rayon_vs_async();
    println!("\n{}", "=".repeat(70));
    
    demonstrate_rayon_simplicity();
    println!("\n{}", "=".repeat(70));
    
    show_performance_characteristics();
    println!("\n{}", "=".repeat(70));
    
    real_world_guidelines();
}

fn explain_rayon_vs_async() {
    println!("📚 Understanding Rayon vs Async/Await\n");
    
    println!("🔵 When to Use RAYON (This Project!):");
    println!("   ✅ CPU-bound tasks (computation, hashing, parsing)");
    println!("   ✅ Data parallelism (processing many items)");
    println!("   ✅ Mathematical operations");
    println!("   ✅ Image/video processing");
    println!("   ✅ Scientific computing");
    println!("   ✅ Batch processing");
    println!("   ✅ No blocking I/O involved");
    
    println!("\n🟢 When to Use ASYNC/AWAIT (AxonerAI!):");
    println!("   ✅ I/O-bound tasks (network, database, files)");
    println!("   ✅ Concurrent requests (HTTP, API calls)");
    println!("   ✅ WebSocket connections");
    println!("   ✅ Streaming data");
    println!("   ✅ Tasks that spend time WAITING");
    println!("   ✅ High concurrency (1000s of connections)");
    
    println!("\n⚠️  Common Mistake:");
    println!("   ❌ Using async for CPU-heavy tasks");
    println!("   → Async schedulers assume tasks yield quickly");
    println!("   → CPU-bound tasks block the executor");
    println!("   → Result: Poor performance, wasted resources");
    
    println!("\n💡 For FastRAG:");
    println!("   • MinHash computation: Pure CPU work → Rayon");
    println!("   • LSH indexing: Pure CPU work → Rayon");
    println!("   • Similarity calculation: Pure CPU work → Rayon");
    println!("   • If you needed to fetch docs from API → Async");
    println!("   • If you needed to store in database → Async");
}

fn demonstrate_rayon_simplicity() {
    println!("🎯 Code Simplicity: Rayon vs Async\n");
    
    println!("Example: Process 1000 documents with MinHash\n");
    
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("WITH RAYON (What we're using):");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!(r#"
    use rayon::prelude::*;
    
    let results: Vec<_> = documents
        .par_iter()              // 🚀 That's it! One word change!
        .map(|doc| {{
            let shingles = generate_shingles(doc, 3);
            MinHash::from_shingles(&shingles, 128)
        }})
        .collect();
    
    // Rayon handles:
    // ✅ Thread pool creation
    // ✅ Work distribution
    // ✅ Load balancing
    // ✅ Work stealing
    // ✅ All automatically!"#);
    
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("WITH ASYNC (Wrong tool for this job!):");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!(r#"
    use tokio::task;
    use futures::future::join_all;
    
    let handles: Vec<_> = documents
        .into_iter()
        .map(|doc| {{
            task::spawn_blocking(move || {{  // Need blocking because CPU work!
                let shingles = generate_shingles(&doc, 3);
                MinHash::from_shingles(&shingles, 128)
            }})
        }})
        .collect();
    
    let results = join_all(handles).await;  // Need async runtime
    
    // Problems:
    // ❌ Need tokio runtime
    // ❌ spawn_blocking has overhead
    // ❌ More complex error handling
    // ❌ Less efficient for pure CPU work
    // ❌ Harder to reason about"#);
    
    println!("\n✨ The Rayon Advantage:");
    println!("   • 1 line change: .iter() → .par_iter()");
    println!("   • No runtime needed");
    println!("   • No async/await complexity");
    println!("   • Better CPU utilization");
    println!("   • Simpler mental model");
}

fn show_performance_characteristics() {
    println!("⚡ Performance Demonstration\n");
    
    // Generate test data
    let test_docs: Vec<String> = (0..100)
        .map(|i| {
            format!("Document {} with some content about topic {} and more details {}", 
                    i, i % 10, i * 123)
        })
        .collect();
    
    println!("Test: Process {} documents with MinHash", test_docs.len());
    println!("Task: Generate shingles + compute 128 hash functions\n");
    
    // Sequential baseline
    println!("🐢 Sequential Processing:");
    let start = Instant::now();
    let _results: Vec<_> = test_docs
        .iter()
        .map(|doc| {
            let shingles = generate_shingles(doc, 3);
            MinHash::from_shingles(&shingles, 128)
        })
        .collect();
    let seq_time = start.elapsed();
    println!("   Time: {:?}", seq_time);
    
    // Rayon parallel
    println!("\n🚀 Rayon Parallel:");
    let start = Instant::now();
    let _results: Vec<_> = test_docs
        .par_iter()
        .map(|doc| {
            let shingles = generate_shingles(doc, 3);
            MinHash::from_shingles(&shingles, 128)
        })
        .collect();
    let par_time = start.elapsed();
    println!("   Time: {:?}", par_time);
    
    let speedup = seq_time.as_secs_f64() / par_time.as_secs_f64();
    println!("\n📊 Results:");
    println!("   Speedup: {:.2}x", speedup);
    println!("   CPU cores used: {}", num_cpus::get());
    println!("   Efficiency: {:.1}%", (speedup / num_cpus::get() as f64) * 100.0);
    
    println!("\n💡 Why Rayon is Fast:");
    println!("   • Work-stealing scheduler");
    println!("   • Balanced thread pool");
    println!("   • Cache-friendly execution");
    println!("   • Minimal overhead");
    println!("   • No context switching waste");
}

fn real_world_guidelines() {
    println!("🌍 Real-World Decision Guide\n");
    
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("Scenario: Building a Document Processing System");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
    
    println!("Component 1: Fetch documents from API");
    println!("   Type: I/O-bound (network waiting)");
    println!("   Tool: ✅ ASYNC (tokio/reqwest)");
    println!("   Why: Waiting for network, can do other work\n");
    
    println!("Component 2: Parse and compute MinHash");
    println!("   Type: CPU-bound (computation)");
    println!("   Tool: ✅ RAYON");
    println!("   Why: Pure computation, no waiting\n");
    
    println!("Component 3: Store results in database");
    println!("   Type: I/O-bound (database waiting)");
    println!("   Tool: ✅ ASYNC (tokio-postgres)");
    println!("   Why: Waiting for database, can batch\n");
    
    println!("Component 4: Find duplicate pairs");
    println!("   Type: CPU-bound (similarity computation)");
    println!("   Tool: ✅ RAYON");
    println!("   Why: Mathematical operations\n");
    
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("Complete Pipeline:");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
    println!(r#"
    // Async for I/O
    let documents = fetch_from_api().await?;
    
    // Switch to Rayon for CPU work
    let minhashes: Vec<_> = documents
        .par_iter()
        .map(|doc| compute_minhash(doc))
        .collect();
    
    // Back to async for I/O
    store_in_database(&minhashes).await?;
    
    // Rayon again for CPU work
    let duplicates: Vec<_> = (0..minhashes.len())
        .into_par_iter()
        .flat_map(|i| find_similar(i, &minhashes))
        .collect();
    "#);
    
    println!("\n✨ Key Takeaways:");
    println!("   1. Use async for I/O, Rayon for CPU");
    println!("   2. They complement each other!");
    println!("   3. Switch between them as needed");
    println!("   4. Don't use async for CPU work");
    println!("   5. Don't use threads for I/O work");
    
    println!("\n🎓 Your AxonerAI Experience:");
    println!("   • You learned async for network/I/O");
    println!("   • Now you're learning Rayon for CPU");
    println!("   • Together they cover all parallelism needs!");
    println!("   • FastRAG = Pure CPU work = Rayon's domain");
}

fn num_cpus::get() -> usize {
    std::thread::available_parallelism()
        .map(|n| n.get())
        .unwrap_or(1)
}
