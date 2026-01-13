use crate::serialization::LogisticRegressionModel;
use sprs::CsMat;

/// Logistic Regression classifier
pub struct LogisticRegression {
    coef: Vec<Vec<f64>>,      // [n_classes, n_features]
    intercept: Vec<f64>,       // [n_classes]
    classes: Vec<String>,
    scaler_mean: Option<Vec<f64>>,   // StandardScaler mean
    scaler_scale: Option<Vec<f64>>,  // StandardScaler scale
}

impl LogisticRegression {
    /// Load from serialized model
    pub fn from_model(model: LogisticRegressionModel) -> Self {
        Self {
            coef: model.coef,
            intercept: model.intercept,
            classes: model.classes,
            scaler_mean: model.scaler_mean,
            scaler_scale: model.scaler_scale,
        }
    }

    /// Apply StandardScaler transformation if scaler is present
    fn apply_scaler(&self, features: &mut [f64]) {
        if let (Some(mean), Some(scale)) = (&self.scaler_mean, &self.scaler_scale) {
            for (i, feature) in features.iter_mut().enumerate() {
                if i < mean.len() && i < scale.len() {
                    *feature = (*feature - mean[i]) / scale[i];
                }
            }
        }
    }

    /// Predict class probabilities for a batch of samples
    /// X: sparse matrix [n_samples, n_features]
    /// Returns: Vec of (clean_prob, spam_prob)
    pub fn predict_proba(&self, x: &CsMat<f64>) -> Vec<(f64, f64)> {
        let n_samples = x.rows();
        let n_features = x.cols();
        let mut results = Vec::with_capacity(n_samples);

        // Binary classification: sklearn stores only 1 row of coef for positive class
        let is_binary = self.coef.len() == 1;

        for row_idx in 0..n_samples {
            let row = x.outer_view(row_idx).unwrap();

            // Convert sparse to dense if scaling is needed
            let features: Vec<f64> = if self.scaler_mean.is_some() {
                let mut dense = vec![0.0; n_features];
                for (col_idx, &value) in row.iter() {
                    dense[col_idx] = value;
                }
                // Apply StandardScaler
                self.apply_scaler(&mut dense);
                dense
            } else {
                // No scaling needed, use sparse directly
                vec![] // Won't be used
            };

            if is_binary {
                // Binary classification: use sigmoid
                let mut decision = self.intercept[0];

                if self.scaler_mean.is_some() {
                    // Use scaled dense features
                    for (col_idx, &value) in features.iter().enumerate() {
                        if col_idx < self.coef[0].len() {
                            decision += value * self.coef[0][col_idx];
                        }
                    }
                } else {
                    // Use sparse features directly
                    for (col_idx, &value) in row.iter() {
                        decision += value * self.coef[0][col_idx];
                    }
                }

                let spam_prob = sigmoid(decision);
                let clean_prob = 1.0 - spam_prob;

                results.push((clean_prob, spam_prob));
            } else {
                // Multi-class: use softmax
                let mut decision_values = Vec::with_capacity(self.classes.len());

                for class_idx in 0..self.classes.len() {
                    let mut decision = self.intercept[class_idx];

                    if self.scaler_mean.is_some() {
                        // Use scaled dense features
                        for (col_idx, &value) in features.iter().enumerate() {
                            if col_idx < self.coef[class_idx].len() {
                                decision += value * self.coef[class_idx][col_idx];
                            }
                        }
                    } else {
                        // Use sparse features directly
                        for (col_idx, &value) in row.iter() {
                            decision += value * self.coef[class_idx][col_idx];
                        }
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

/// Sigmoid function (for binary classification)
#[allow(dead_code)]
fn sigmoid(x: f64) -> f64 {
    1.0 / (1.0 + (-x).exp())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sigmoid() {
        assert!((sigmoid(0.0) - 0.5).abs() < 1e-6);
        assert!(sigmoid(10.0) > 0.99);
        assert!(sigmoid(-10.0) < 0.01);
    }

    #[test]
    fn test_softmax() {
        let values = vec![1.0, 2.0, 3.0];
        let probs = softmax(&values);

        let sum: f64 = probs.iter().sum();
        assert!((sum - 1.0).abs() < 1e-6);
    }
}
