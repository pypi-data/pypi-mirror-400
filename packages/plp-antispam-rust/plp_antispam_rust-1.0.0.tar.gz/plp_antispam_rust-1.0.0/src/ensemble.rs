use crate::features;
use crate::models::{LinearSVM, LogisticRegression, NaiveBayes, XGBoost};
use crate::serialization::*;
use crate::tfidf::{TfidfVectorizer, TokenType};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use rayon::prelude::*;
use sprs::CsMat;
use std::path::{Path, PathBuf};

/// Scaler parameters for custom features
#[derive(Clone)]
struct ScalerParams {
    scaler_type: String,  // "standard", "minmax", or "none"
    mean: Option<Vec<f64>>,
    scale: Option<Vec<f64>>,
    min: Option<Vec<f64>>,
}

/// Stacked ensemble of 4 models
#[pyclass]
pub struct RustEnsemble {
    // Model 1: Naive Bayes + Word Unigrams
    model1_tfidf: TfidfVectorizer,
    model1: NaiveBayes,
    model1_scaler: ScalerParams,

    // Model 2: Logistic Regression + Word Bigrams
    model2_tfidf: TfidfVectorizer,
    model2: LogisticRegression,
    model2_scaler: ScalerParams,

    // Model 3: SVM + Character Trigrams
    model3_tfidf: TfidfVectorizer,
    model3: LinearSVM,
    model3_scaler: ScalerParams,

    // Model 4: XGBoost + Word 1-2 grams
    model4_tfidf: TfidfVectorizer,
    model4: XGBoost,
    model4_scaler: ScalerParams,

    // Meta-classifier
    meta_classifier: LogisticRegression,

    // Custom features extractor (we'll integrate rust_features here)
    custom_features_enabled: bool,
}

#[pymethods]
impl RustEnsemble {
    /// Load models from directory
    #[staticmethod]
    pub fn load(model_dir: String) -> PyResult<Self> {
        let path = PathBuf::from(model_dir);
        Self::load_internal(&path)
            .map_err(|e| PyErr::new::<PyRuntimeError, _>(e))
    }

    /// Predict batch of emails
    /// Returns: Vec of (class, probability)
    pub fn predict_batch(&self, emails: Vec<String>) -> PyResult<Vec<(String, f64)>> {
        let probas = self.predict_proba_batch_internal(&emails)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;

        Ok(probas
            .iter()
            .map(|(clean_prob, spam_prob)| {
                if spam_prob > clean_prob {
                    ("spam".to_string(), *spam_prob)
                } else {
                    ("clean".to_string(), *clean_prob)
                }
            })
            .collect())
    }

    /// Predict probabilities for batch of emails
    /// Returns: Vec of (clean_prob, spam_prob)
    pub fn predict_proba_batch(&self, emails: Vec<String>) -> PyResult<Vec<(f64, f64)>> {
        self.predict_proba_batch_internal(&emails)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))
    }

    /// Predict with base model predictions exposed
    /// Returns: Vec of (base_predictions, final_prediction)
    /// where base_predictions is Vec of (label, spam_prob) for each of 4 models
    /// and final_prediction is (label, spam_prob) from meta-classifier
    pub fn predict_with_base_models(&self, emails: Vec<String>) -> PyResult<Vec<(Vec<(String, f64)>, (String, f64))>> {
        // Extract custom features once
        let custom_features_batch = features::extract_features_batch(&emails);

        // Run 4 models in parallel
        let results: Vec<_> = vec![
            (1, &self.model1_tfidf, &emails),
            (2, &self.model2_tfidf, &emails),
            (3, &self.model3_tfidf, &emails),
            (4, &self.model4_tfidf, &emails),
        ]
        .into_par_iter()
        .map(|(model_idx, tfidf, texts)| {
            let tfidf_matrix = tfidf.transform_batch(texts);
            (model_idx, tfidf_matrix)
        })
        .collect();

        // Extract predictions from each model
        let mut all_probas = vec![Vec::new(); 4];

        for (model_idx, tfidf_matrix) in results {
            let scaler = match model_idx {
                1 => &self.model1_scaler,
                2 => &self.model2_scaler,
                3 => &self.model3_scaler,
                4 => &self.model4_scaler,
                _ => unreachable!(),
            };

            let combined_matrix = append_custom_features(&tfidf_matrix, &custom_features_batch, scaler);

            let probas = match model_idx {
                1 => self.model1.predict_proba(&combined_matrix),
                2 => self.model2.predict_proba(&combined_matrix),
                3 => self.model3.predict_proba(&combined_matrix),
                4 => self.model4.predict_proba(&combined_matrix),
                _ => unreachable!(),
            };
            all_probas[model_idx - 1] = probas;
        }

        // Build meta-features and get final predictions
        let n_samples = emails.len();
        let mut meta_features = Vec::with_capacity(n_samples);

        for i in 0..n_samples {
            let mut features = Vec::with_capacity(8 + 28);
            for model_probas in all_probas.iter() {
                let (clean_prob, spam_prob) = model_probas[i];
                features.push(clean_prob);
                features.push(spam_prob);
            }

            if self.custom_features_enabled {
                features.extend(features::extract_features(&emails[i]));
            }

            meta_features.push(features);
        }

        let meta_matrix = dense_to_sparse(&meta_features);
        let final_probas = self.meta_classifier.predict_proba(&meta_matrix);

        // Format results
        let mut results = Vec::with_capacity(n_samples);
        for i in 0..n_samples {
            // Base model predictions
            let base_preds: Vec<(String, f64)> = all_probas
                .iter()
                .map(|model_probas| {
                    let (_clean_prob, spam_prob) = model_probas[i];
                    let label = if spam_prob > 0.5 { "spam" } else { "clean" };
                    (label.to_string(), spam_prob)
                })
                .collect();

            // Final prediction
            let (final_clean, final_spam) = final_probas[i];
            let final_label = if final_spam > final_clean { "spam" } else { "clean" };
            let final_pred = (final_label.to_string(), final_spam);

            results.push((base_preds, final_pred));
        }

        Ok(results)
    }
}

impl RustEnsemble {
    /// Internal load function (not exposed to Python)
    fn load_internal(model_dir: &Path) -> Result<Self, String> {
        // Load TF-IDF models
        let model1_tfidf_params: TfidfModel =
            load_msgpack(&model_dir.join("model1_tfidf.msgpack"))?;
        let model2_tfidf_params: TfidfModel =
            load_msgpack(&model_dir.join("model2_tfidf.msgpack"))?;
        let model3_tfidf_params: TfidfModel =
            load_msgpack(&model_dir.join("model3_tfidf.msgpack"))?;
        let model4_tfidf_params: TfidfModel =
            load_msgpack(&model_dir.join("model4_tfidf.msgpack"))?;

        // Extract scaler parameters from TF-IDF models
        let model1_scaler = extract_scaler_params(&model1_tfidf_params);
        let model2_scaler = extract_scaler_params(&model2_tfidf_params);
        let model3_scaler = extract_scaler_params(&model3_tfidf_params);
        let model4_scaler = extract_scaler_params(&model4_tfidf_params);

        // Load base models
        let model1_params: NaiveBayesModel =
            load_msgpack(&model_dir.join("model1.msgpack"))?;
        let model2_params: LogisticRegressionModel =
            load_msgpack(&model_dir.join("model2.msgpack"))?;
        let model3_params: LinearSVMModel =
            load_msgpack(&model_dir.join("model3.msgpack"))?;
        let model4_params: XGBoostModel =
            load_msgpack(&model_dir.join("model4.msgpack"))?;

        // Load meta-classifier
        let meta_params: LogisticRegressionModel =
            load_msgpack(&model_dir.join("meta_classifier.msgpack"))?;

        Ok(Self {
            model1_tfidf: TfidfVectorizer::from_model(model1_tfidf_params, TokenType::WordUnigram),
            model1: NaiveBayes::from_model(model1_params),
            model1_scaler,

            model2_tfidf: TfidfVectorizer::from_model(model2_tfidf_params, TokenType::WordBigram),
            model2: LogisticRegression::from_model(model2_params),
            model2_scaler,

            model3_tfidf: TfidfVectorizer::from_model(model3_tfidf_params, TokenType::CharTrigram),
            model3: LinearSVM::from_model(model3_params),
            model3_scaler,

            model4_tfidf: TfidfVectorizer::from_model(model4_tfidf_params, TokenType::Word12Gram),
            model4: XGBoost::from_model(model4_params)?,
            model4_scaler,

            meta_classifier: LogisticRegression::from_model(meta_params),

            custom_features_enabled: true,
        })
    }

    /// Internal predict probabilities (not exposed to Python)
    fn predict_proba_batch_internal(&self, emails: &[String]) -> Result<Vec<(f64, f64)>, String> {
        // CRITICAL: Extract custom features ONCE for all models
        // All base models need TF-IDF + 28 custom features
        let custom_features_batch = features::extract_features_batch(emails);

        // Run 4 models in parallel using Rayon
        let results: Vec<_> = vec![
            (1, &self.model1_tfidf, &emails),
            (2, &self.model2_tfidf, &emails),
            (3, &self.model3_tfidf, &emails),
            (4, &self.model4_tfidf, &emails),
        ]
        .into_par_iter()
        .map(|(model_idx, tfidf, texts)| {
            let tfidf_matrix = tfidf.transform_batch(texts);
            (model_idx, tfidf_matrix)
        })
        .collect();

        // Extract predictions from each model
        // IMPORTANT: Base models expect TF-IDF + custom features
        let mut all_probas = vec![Vec::new(); 4];

        for (model_idx, tfidf_matrix) in results {
            // Get the appropriate scaler for this model
            let scaler = match model_idx {
                1 => &self.model1_scaler,
                2 => &self.model2_scaler,
                3 => &self.model3_scaler,
                4 => &self.model4_scaler,
                _ => unreachable!(),
            };

            // Append SCALED custom features to TF-IDF matrix
            let combined_matrix = append_custom_features(&tfidf_matrix, &custom_features_batch, scaler);

            let probas = match model_idx {
                1 => self.model1.predict_proba(&combined_matrix),
                2 => self.model2.predict_proba(&combined_matrix),
                3 => self.model3.predict_proba(&combined_matrix),
                4 => self.model4.predict_proba(&combined_matrix),
                _ => unreachable!(),
            };
            all_probas[model_idx - 1] = probas;
        }

        // Combine predictions into meta-features
        let n_samples = emails.len();
        let mut meta_features = Vec::with_capacity(n_samples);

        for i in 0..n_samples {
            let mut features = Vec::with_capacity(8 + 28); // 8 probs + 28 custom features

            // Add probabilities from all 4 models (8 features)
            for (model_idx, model_probas) in all_probas.iter().enumerate() {
                let (clean_prob, spam_prob) = model_probas[i];
                features.push(clean_prob);
                features.push(spam_prob);

                // DEBUG: Print base model probabilities for first email
                if i == 0 && emails.len() == 1 {
                    eprintln!("DEBUG: Model {} predictions: clean={:.6}, spam={:.6}",
                             model_idx + 1, clean_prob, spam_prob);
                }
            }

            // Add 28 custom features
            if self.custom_features_enabled {
                let custom_feats = features::extract_features(&emails[i]);

                // DEBUG: Print first 10 custom features for first email
                if i == 0 && emails.len() == 1 {
                    eprintln!("DEBUG: Custom features (first 10): {:?}", &custom_feats[..10.min(custom_feats.len())]);
                }

                features.extend(custom_feats);

                // DEBUG: Print full meta-features after adding custom
                if i == 0 && emails.len() == 1 {
                    eprintln!("DEBUG: Full meta-features (first 16): {:?}", &features[..16.min(features.len())]);
                }
            }

            meta_features.push(features);
        }

        // Convert to sparse matrix for meta-classifier
        // For simplicity, we'll use dense conversion here
        // TODO: Optimize this
        let meta_matrix = dense_to_sparse(&meta_features);

        // Final prediction using meta-classifier
        let final_probas = self.meta_classifier.predict_proba(&meta_matrix);

        Ok(final_probas)
    }
}

/// Convert dense matrix to sparse (CSR format)
fn dense_to_sparse(dense: &[Vec<f64>]) -> CsMat<f64> {
    use sprs::TriMat;

    let n_rows = dense.len();
    let n_cols = if n_rows > 0 { dense[0].len() } else { 0 };

    let mut row_inds = Vec::new();
    let mut col_inds = Vec::new();
    let mut data = Vec::new();

    for (row_idx, row) in dense.iter().enumerate() {
        for (col_idx, &value) in row.iter().enumerate() {
            if value != 0.0 {
                row_inds.push(row_idx);
                col_inds.push(col_idx);
                data.push(value);
            }
        }
    }

    let tri_mat = TriMat::from_triplets((n_rows, n_cols), row_inds, col_inds, data);
    tri_mat.to_csr()
}

/// Extract scaler parameters from TfidfModel
fn extract_scaler_params(tfidf_model: &TfidfModel) -> ScalerParams {
    ScalerParams {
        scaler_type: tfidf_model.scaler_type.clone().unwrap_or_else(|| "none".to_string()),
        mean: tfidf_model.scaler_mean.clone(),
        scale: tfidf_model.scaler_scale.clone(),
        min: tfidf_model.scaler_min.clone(),
    }
}

/// Apply scaling to custom features
fn apply_scaling(features: &[f64], scaler: &ScalerParams) -> Vec<f64> {
    match scaler.scaler_type.as_str() {
        "standard" => {
            // StandardScaler: (x - mean) / scale
            if let (Some(mean), Some(scale)) = (&scaler.mean, &scaler.scale) {
                features.iter().enumerate()
                    .map(|(i, &x)| (x - mean[i]) / scale[i])
                    .collect()
            } else {
                features.to_vec()
            }
        },
        "minmax" => {
            // MinMaxScaler: (x - min) * scale
            // where scale = 1 / (max - min)
            if let (Some(min), Some(scale)) = (&scaler.min, &scaler.scale) {
                features.iter().enumerate()
                    .map(|(i, &x)| (x - min[i]) * scale[i])
                    .collect()
            } else {
                features.to_vec()
            }
        },
        _ => features.to_vec(),
    }
}

/// Append SCALED custom features to TF-IDF sparse matrix
/// Returns a new sparse matrix with shape (n_samples, tfidf_features + 28)
fn append_custom_features(tfidf_matrix: &CsMat<f64>, custom_features: &[Vec<f64>], scaler: &ScalerParams) -> CsMat<f64> {
    use sprs::TriMat;

    let n_samples = tfidf_matrix.rows();
    let tfidf_cols = tfidf_matrix.cols();
    let custom_cols = if custom_features.is_empty() { 0 } else { custom_features[0].len() };
    let total_cols = tfidf_cols + custom_cols;

    let mut row_inds = Vec::new();
    let mut col_inds = Vec::new();
    let mut data = Vec::new();

    for row_idx in 0..n_samples {
        // Copy TF-IDF features (sparse)
        let row = tfidf_matrix.outer_view(row_idx).unwrap();
        for (col_idx, &value) in row.iter() {
            row_inds.push(row_idx);
            col_inds.push(col_idx);
            data.push(value);
        }

        // Apply scaling to custom features
        let scaled_features = apply_scaling(&custom_features[row_idx], scaler);

        // Append scaled custom features (dense, 28 features)
        for (custom_idx, &custom_value) in scaled_features.iter().enumerate() {
            // Custom features start after TF-IDF features
            let col_idx = tfidf_cols + custom_idx;
            row_inds.push(row_idx);
            col_inds.push(col_idx);
            data.push(custom_value);
        }
    }

    let tri_mat = TriMat::from_triplets((n_samples, total_cols), row_inds, col_inds, data);
    tri_mat.to_csr()
}
