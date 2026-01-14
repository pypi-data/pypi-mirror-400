use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use fastrustrag::*;
use rayon::prelude::*;
use std::hash::{Hash, Hasher};
use ahash::AHasher;

fn benchmark_minhash_sequential(c: &mut Criterion) {
    let shingles: Vec<String> = (0..1000)
        .map(|i| format!("shingle_{}", i))
        .collect();
    
    c.bench_function("minhash_sequential", |b| {
        b.iter(|| {
            // Sequential hash computation
            let mut signature = vec![u64::MAX; 128];
            for seed in 0..128 {
                let min_hash = shingles
                    .iter()
                    .map(|s| hash_with_seed(s, seed))
                    .min()
                    .unwrap_or(u64::MAX);
                signature[seed] = min_hash;
            }
            black_box(signature)
        })
    });
}

fn benchmark_minhash_parallel(c: &mut Criterion) {
    let shingles: Vec<String> = (0..1000)
        .map(|i| format!("shingle_{}", i))
        .collect();
    
    c.bench_function("minhash_parallel_rayon", |b| {
        b.iter(|| {
            MinHash::from_shingles(black_box(&shingles), 128)
        })
    });
}

fn benchmark_batch_insert(c: &mut Criterion) {
    let mut group = c.benchmark_group("lsh_batch_insert");
    
    for size in [100, 500, 1000].iter() {
        let docs: Vec<_> = (0..*size)
            .map(|i| {
                let doc = format!("Document {} with content about topic {}", i, i % 10);
                let shingles = generate_shingles(&doc, 3);
                let minhash = MinHash::from_shingles(&shingles, 128);
                (doc, minhash)
            })
            .collect();
        
        group.bench_with_input(BenchmarkId::new("parallel", size), &docs, |b, docs| {
            b.iter(|| {
                let index = LSHIndex::new(20);
                index.insert_batch(black_box(docs.clone()));
            })
        });
        
        group.bench_with_input(BenchmarkId::new("sequential", size), &docs, |b, docs| {
            b.iter(|| {
                let index = LSHIndex::new(20);
                for (doc, minhash) in docs.iter() {
                    index.insert(black_box(doc.clone()), black_box(minhash.clone()));
                }
            })
        });
    }
    
    group.finish();
}

fn benchmark_deduplication_pipeline(c: &mut Criterion) {
    let mut group = c.benchmark_group("deduplication_pipeline");
    
    for size in [100, 500, 1000].iter() {
        let documents: Vec<String> = (0..*size)
            .map(|i| format!("Document {} contains various information about topic {} with details {}", 
                           i, i % 20, i * 37))
            .collect();
        
        group.bench_with_input(BenchmarkId::new("full_pipeline", size), &documents, |b, docs| {
            b.iter(|| {
                let pipeline = DeduplicationPipeline::new(20, 128, 3, 0.7);
                pipeline.process_documents(black_box(docs.clone()));
                pipeline.deduplicate_corpus()
            })
        });
    }
    
    group.finish();
}

fn benchmark_similarity_computation(c: &mut Criterion) {
    let shingles1: Vec<String> = (0..500).map(|i| format!("word_{}", i)).collect();
    let shingles2: Vec<String> = (250..750).map(|i| format!("word_{}", i)).collect();
    
    let mh1 = MinHash::from_shingles(&shingles1, 128);
    let mh2 = MinHash::from_shingles(&shingles2, 128);
    
    c.bench_function("similarity_computation", |b| {
        b.iter(|| {
            black_box(mh1.similarity(&mh2))
        })
    });
}

fn benchmark_parallel_candidate_search(c: &mut Criterion) {
    // Setup: Create index with 1000 documents
    let pipeline = DeduplicationPipeline::new(20, 128, 3, 0.7);
    let documents: Vec<String> = (0..1000)
        .map(|i| format!("Document {} with content {}", i, i % 10))
        .collect();
    pipeline.process_documents(documents);
    
    let query = "Document 42 with content 2";
    let query_shingles = generate_shingles(query, 3);
    let query_minhash = MinHash::from_shingles(&query_shingles, 128);
    
    c.bench_function("parallel_candidate_search", |b| {
        b.iter(|| {
            let candidates = pipeline.index.find_candidates(black_box(&query_minhash));
            
            // Parallel similarity computation
            let _results: Vec<_> = candidates
                .into_par_iter()
                .filter_map(|doc_id| {
                    let sig = pipeline.index.get_signature(doc_id)?;
                    let similarity = query_minhash.similarity(&sig);
                    if similarity >= 0.7 {
                        Some((doc_id, similarity))
                    } else {
                        None
                    }
                })
                .collect();
        })
    });
}

// Helper function for sequential benchmark
fn hash_with_seed(s: &str, seed: usize) -> u64 {
    let mut hasher = AHasher::default();
    seed.hash(&mut hasher);
    s.hash(&mut hasher);
    hasher.finish()
}

criterion_group!(
    benches,
    benchmark_minhash_sequential,
    benchmark_minhash_parallel,
    benchmark_batch_insert,
    benchmark_deduplication_pipeline,
    benchmark_similarity_computation,
    benchmark_parallel_candidate_search,
);

criterion_main!(benches);
