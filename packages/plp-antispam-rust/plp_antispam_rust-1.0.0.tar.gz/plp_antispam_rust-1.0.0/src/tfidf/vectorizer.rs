use super::tokenizer::{TokenType, Tokenizer};
use crate::serialization::TfidfModel;
use ahash::AHashMap;
use rayon::prelude::*;
use sprs::{CsMat, TriMat};
use std::collections::HashMap;

/// TF-IDF Vectorizer
pub struct TfidfVectorizer {
    tokenizer: Tokenizer,
    vocabulary: HashMap<String, usize>,
    idf: Vec<f64>,
    sublinear_tf: bool,
    norm: String,
}

impl TfidfVectorizer {
    /// Load from serialized model
    pub fn from_model(model: TfidfModel, token_type: TokenType) -> Self {
        Self {
            tokenizer: Tokenizer::new(token_type),
            vocabulary: model.vocabulary,
            idf: model.idf,
            sublinear_tf: model.sublinear_tf,
            norm: model.norm,
        }
    }

    /// Transform a batch of texts into TF-IDF sparse matrix
    pub fn transform_batch(&self, texts: &[String]) -> CsMat<f64> {
        let n_samples = texts.len();
        let n_features = self.vocabulary.len();

        // Parallel tokenization and TF computation
        let tf_maps: Vec<AHashMap<usize, f64>> = texts
            .par_iter()
            .map(|text| self.compute_tf(text))
            .collect();

        // Build sparse matrix (CSR format) with TF-IDF values
        let mut row_inds = Vec::new();
        let mut col_inds = Vec::new();
        let mut data = Vec::new();

        for (row_idx, tf_map) in tf_maps.iter().enumerate() {
            for (&col_idx, &tf_value) in tf_map.iter() {
                // TF-IDF = TF * IDF
                let tfidf_value = tf_value * self.idf[col_idx];
                row_inds.push(row_idx);
                col_inds.push(col_idx);
                data.push(tfidf_value);
            }
        }

        // Convert to CSR sparse matrix
        let tri_mat = TriMat::from_triplets((n_samples, n_features), row_inds, col_inds, data);
        let matrix = tri_mat.to_csr();

        // Apply normalization if specified
        if self.norm == "l2" {
            self.normalize_l2(matrix)
        } else if self.norm == "l1" {
            self.normalize_l1(matrix)
        } else {
            matrix
        }
    }

    /// Compute term frequency for a single text
    fn compute_tf(&self, text: &str) -> AHashMap<usize, f64> {
        let tokens = self.tokenizer.tokenize(text);

        if tokens.is_empty() {
            return AHashMap::new();
        }

        // Count term frequencies
        let mut counts: AHashMap<usize, usize> = AHashMap::new();

        for token in &tokens {
            if let Some(&vocab_idx) = self.vocabulary.get(token) {
                *counts.entry(vocab_idx).or_insert(0) += 1;
            }
        }

        // Compute TF based on sublinear_tf setting
        if self.sublinear_tf {
            // Sublinear TF scaling: 1 + log(count)
            counts
                .into_iter()
                .map(|(idx, count)| {
                    let tf = if count > 0 {
                        1.0 + (count as f64).ln()
                    } else {
                        0.0
                    };
                    (idx, tf)
                })
                .collect()
        } else {
            // Standard TF: count / total_count
            let total_count = tokens.len() as f64;
            counts
                .into_iter()
                .map(|(idx, count)| (idx, count as f64 / total_count))
                .collect()
        }
    }

    /// Apply L2 normalization to sparse matrix (row-wise)
    /// Each row is normalized to unit L2 norm: row / sqrt(sum(row^2))
    fn normalize_l2(&self, matrix: CsMat<f64>) -> CsMat<f64> {
        let n_samples = matrix.rows();
        let n_features = matrix.cols();

        let mut row_inds = Vec::new();
        let mut col_inds = Vec::new();
        let mut data = Vec::new();

        for row_idx in 0..n_samples {
            let row = matrix.outer_view(row_idx).unwrap();

            // Compute L2 norm: sqrt(sum(values^2))
            let norm: f64 = row.iter()
                .map(|(_, &val)| val * val)
                .sum::<f64>()
                .sqrt();

            // Normalize row if norm > 0
            if norm > 0.0 {
                for (col_idx, &value) in row.iter() {
                    row_inds.push(row_idx);
                    col_inds.push(col_idx);
                    data.push(value / norm);
                }
            } else {
                // Keep zero rows as zero
                for (col_idx, &value) in row.iter() {
                    row_inds.push(row_idx);
                    col_inds.push(col_idx);
                    data.push(value);
                }
            }
        }

        let tri_mat = TriMat::from_triplets((n_samples, n_features), row_inds, col_inds, data);
        tri_mat.to_csr()
    }

    /// Apply L1 normalization to sparse matrix (row-wise)
    /// Each row is normalized to unit L1 norm: row / sum(abs(row))
    fn normalize_l1(&self, matrix: CsMat<f64>) -> CsMat<f64> {
        let n_samples = matrix.rows();
        let n_features = matrix.cols();

        let mut row_inds = Vec::new();
        let mut col_inds = Vec::new();
        let mut data = Vec::new();

        for row_idx in 0..n_samples {
            let row = matrix.outer_view(row_idx).unwrap();

            // Compute L1 norm: sum(abs(values))
            let norm: f64 = row.iter()
                .map(|(_, &val)| val.abs())
                .sum();

            // Normalize row if norm > 0
            if norm > 0.0 {
                for (col_idx, &value) in row.iter() {
                    row_inds.push(row_idx);
                    col_inds.push(col_idx);
                    data.push(value / norm);
                }
            } else {
                // Keep zero rows as zero
                for (col_idx, &value) in row.iter() {
                    row_inds.push(row_idx);
                    col_inds.push(col_idx);
                    data.push(value);
                }
            }
        }

        let tri_mat = TriMat::from_triplets((n_samples, n_features), row_inds, col_inds, data);
        tri_mat.to_csr()
    }

    /// Get vocabulary size
    #[allow(dead_code)]
    pub fn vocab_size(&self) -> usize {
        self.vocabulary.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_vectorizer_transform() {
        let mut vocab = HashMap::new();
        vocab.insert("hello".to_string(), 0);
        vocab.insert("world".to_string(), 1);

        let idf = vec![1.0, 1.5];

        let model = TfidfModel {
            vocabulary: vocab,
            idf,
            max_features: 2,
            sublinear_tf: false,
            norm: "l2".to_string(),
        };

        let vectorizer = TfidfVectorizer::from_model(model, TokenType::WordUnigram);

        let texts = vec!["Hello world".to_string(), "Hello hello".to_string()];

        let matrix = vectorizer.transform_batch(&texts);

        assert_eq!(matrix.rows(), 2);
        assert_eq!(matrix.cols(), 2);
    }
}
