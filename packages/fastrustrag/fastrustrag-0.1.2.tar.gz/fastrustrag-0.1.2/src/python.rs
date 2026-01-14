use pyo3::prelude::*;
use pyo3::types::PyList;
use crate::{DeduplicationPipeline as RustPipeline, generate_shingles, MinHash};

/// Python wrapper for DeduplicationPipeline
#[pyclass(name = "DeduplicationPipeline")]
pub struct PyDeduplicationPipeline {
    inner: RustPipeline,
}

#[pymethods]
impl PyDeduplicationPipeline {
    #[new]
    fn new(
        num_bands: usize,
        num_hashes: usize,
        shingle_size: usize,
        similarity_threshold: f64,
    ) -> Self {
        PyDeduplicationPipeline {
            inner: RustPipeline::new(num_bands, num_hashes, shingle_size, similarity_threshold),
        }
    }

    /// Process a list of documents
    fn process_documents(&self, documents: Vec<String>) -> PyResult<usize> {
        Ok(self.inner.process_documents(documents))
    }

    /// Find all duplicate pairs in the corpus
    fn deduplicate_corpus(&self) -> PyResult<Vec<(usize, usize, f64)>> {
        Ok(self.inner.deduplicate_corpus())
    }

    /// Find duplicates for a specific query document
    fn find_duplicates(&self, query: String) -> PyResult<Vec<(usize, String, f64)>> {
        Ok(self.inner.find_duplicates(&query))
    }

    /// Get statistics about the index
    fn stats(&self) -> PyResult<(usize, usize, usize, usize)> {
        let stats = self.inner.stats();
        Ok((
            stats.num_documents,
            stats.num_bands,
            stats.num_hashes,
            stats.shingle_size,
        ))
    }

    /// Get a document by ID
    fn get_document(&self, doc_id: usize) -> PyResult<Option<String>> {
        Ok(self.inner.index.get_document(doc_id))
    }
}

/// Generate shingles from text (standalone function)
#[pyfunction]
fn py_generate_shingles(text: String, n: usize) -> PyResult<Vec<String>> {
    Ok(generate_shingles(&text, n))
}

/// Compute MinHash signature for shingles
#[pyfunction]
fn py_compute_minhash(shingles: Vec<String>, num_hashes: usize) -> PyResult<Vec<u64>> {
    let minhash = MinHash::from_shingles(&shingles, num_hashes);
    Ok(minhash.signature)
}

/// Compute similarity between two MinHash signatures
#[pyfunction]
fn py_similarity(sig1: Vec<u64>, sig2: Vec<u64>) -> PyResult<f64> {
    if sig1.len() != sig2.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Signatures must have the same length",
        ));
    }
    
    let matches = sig1
        .iter()
        .zip(sig2.iter())
        .filter(|(a, b)| a == b)
        .count();
    
    Ok(matches as f64 / sig1.len() as f64)
}

/// FastRustRAG Python Module
#[pymodule]
fn fastrustrag(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyDeduplicationPipeline>()?;
    m.add_function(wrap_pyfunction!(py_generate_shingles, m)?)?;
    m.add_function(wrap_pyfunction!(py_compute_minhash, m)?)?;
    m.add_function(wrap_pyfunction!(py_similarity, m)?)?;
    Ok(())
}
