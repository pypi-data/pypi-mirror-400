use crate::serialization::LinearSVMModel;
use sprs::CsMat;

/// Linear SVM classifier
pub struct LinearSVM {
    coef: Vec<Vec<f64>>,      // [n_classes, n_features]
    intercept: Vec<f64>,       // [n_classes]
    classes: Vec<String>,
}

impl LinearSVM {
    /// Load from serialized model
    pub fn from_model(model: LinearSVMModel) -> Self {
        Self {
            coef: model.coef,
            intercept: model.intercept,
            classes: model.classes,
        }
    }

    /// Predict class probabilities for a batch of samples
    /// X: sparse matrix [n_samples, n_features]
    /// Returns: Vec of (clean_prob, spam_prob)
    pub fn predict_proba(&self, x: &CsMat<f64>) -> Vec<(f64, f64)> {
        let n_samples = x.rows();
        let mut results = Vec::with_capacity(n_samples);

        // Binary classification: sklearn stores only 1 row of coef for positive class
        let is_binary = self.coef.len() == 1;

        for row_idx in 0..n_samples {
            let row = x.outer_view(row_idx).unwrap();

            if is_binary {
                // Binary classification: use sigmoid (Platt scaling approximation)
                let mut decision = self.intercept[0];

                for (col_idx, &value) in row.iter() {
                    decision += value * self.coef[0][col_idx];
                }

                let spam_prob = sigmoid(decision);
                let clean_prob = 1.0 - spam_prob;

                results.push((clean_prob, spam_prob));
            } else {
                // Multi-class: use softmax
                let mut decision_values = Vec::with_capacity(self.classes.len());

                for class_idx in 0..self.classes.len() {
                    let mut decision = self.intercept[class_idx];

                    for (col_idx, &value) in row.iter() {
                        decision += value * self.coef[class_idx][col_idx];
                    }

                    decision_values.push(decision);
                }

                let probs = softmax(&decision_values);
                results.push((probs[0], probs[1]));
            }
        }

        results
    }

    /// Get class names
    #[allow(dead_code)]
    pub fn classes(&self) -> &[String] {
        &self.classes
    }
}

/// Sigmoid function (for binary classification / Platt scaling)
fn sigmoid(x: f64) -> f64 {
    1.0 / (1.0 + (-x).exp())
}

/// Softmax function
fn softmax(values: &[f64]) -> Vec<f64> {
    // For numerical stability, subtract max
    let max_value = values.iter().cloned().fold(f64::NEG_INFINITY, f64::max);

    let exp_sum: f64 = values.iter().map(|&x| (x - max_value).exp()).sum();

    values
        .iter()
        .map(|&x| (x - max_value).exp() / exp_sum)
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_softmax() {
        let values = vec![1.0, 2.0, 3.0];
        let probs = softmax(&values);

        let sum: f64 = probs.iter().sum();
        assert!((sum - 1.0).abs() < 1e-6);

        for &p in &probs {
            assert!(p >= 0.0 && p <= 1.0);
        }
    }
}
