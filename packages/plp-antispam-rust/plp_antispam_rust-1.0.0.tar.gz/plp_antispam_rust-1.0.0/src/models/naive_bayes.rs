use crate::serialization::NaiveBayesModel;
use sprs::CsMat;

/// Multinomial Naive Bayes classifier
pub struct NaiveBayes {
    feature_log_prob: Vec<Vec<f64>>,  // [n_classes, n_features]
    class_log_prior: Vec<f64>,         // [n_classes]
    classes: Vec<String>,
}

impl NaiveBayes {
    /// Load from serialized model
    pub fn from_model(model: NaiveBayesModel) -> Self {
        Self {
            feature_log_prob: model.feature_log_prob,
            class_log_prior: model.class_log_prior,
            classes: model.classes,
        }
    }

    /// Predict class probabilities for a batch of samples
    /// X: sparse matrix [n_samples, n_features]
    /// Returns: Vec of (clean_prob, spam_prob)
    pub fn predict_proba(&self, x: &CsMat<f64>) -> Vec<(f64, f64)> {
        let n_samples = x.rows();
        let mut results = Vec::with_capacity(n_samples);

        for row_idx in 0..n_samples {
            let row = x.outer_view(row_idx).unwrap();

            // Compute log probabilities for each class
            let mut log_probs = Vec::with_capacity(self.classes.len());

            for class_idx in 0..self.classes.len() {
                let mut log_prob = self.class_log_prior[class_idx];

                // Sparse dot product: sum(X[i] * log_prob[class][i])
                for (col_idx, &value) in row.iter() {
                    log_prob += value * self.feature_log_prob[class_idx][col_idx];
                }

                log_probs.push(log_prob);
            }

            // Convert log probabilities to probabilities using softmax
            let probs = softmax(&log_probs);

            results.push((probs[0], probs[1]));
        }

        results
    }

    /// Get class names
    #[allow(dead_code)]
    pub fn classes(&self) -> &[String] {
        &self.classes
    }
}

/// Softmax function to convert log probabilities to probabilities
fn softmax(log_probs: &[f64]) -> Vec<f64> {
    // For numerical stability, subtract max
    let max_log_prob = log_probs.iter().cloned().fold(f64::NEG_INFINITY, f64::max);

    let exp_sum: f64 = log_probs.iter().map(|&x| (x - max_log_prob).exp()).sum();

    log_probs
        .iter()
        .map(|&x| (x - max_log_prob).exp() / exp_sum)
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_softmax() {
        let log_probs = vec![1.0, 2.0, 3.0];
        let probs = softmax(&log_probs);

        // Check probabilities sum to 1
        let sum: f64 = probs.iter().sum();
        assert!((sum - 1.0).abs() < 1e-6);

        // Check values are in [0, 1]
        for &p in &probs {
            assert!(p >= 0.0 && p <= 1.0);
        }
    }
}
