use pyo3::prelude::*;

mod tfidf;
mod models;
mod ensemble;
mod serialization;
mod features;

use ensemble::RustEnsemble;

// Removed standalone functions - use methods on RustEnsemble instead

/// Python module initialization
#[pymodule]
fn plpas(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustEnsemble>()?;
    m.add_function(wrap_pyfunction!(features::extract_features, m)?)?;
    m.add_function(wrap_pyfunction!(features::extract_features_batch_py, m)?)?;
    Ok(())
}
