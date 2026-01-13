use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::Path;

/// TF-IDF vocabulary and IDF weights
#[derive(Debug, Serialize, Deserialize)]
pub struct TfidfModel {
    pub vocabulary: HashMap<String, usize>,
    pub idf: Vec<f64>,
    pub max_features: usize,
    #[serde(default)]
    pub sublinear_tf: bool,  // Apply 1 + log(tf) scaling
    #[serde(default = "default_norm")]
    pub norm: String,  // Normalization: "l2", "l1", or "none"

    // Scaler parameters for custom features (28 features)
    #[serde(default)]
    pub scaler_type: Option<String>,  // "standard", "minmax", or None
    #[serde(default)]
    pub scaler_mean: Option<Vec<f64>>,  // For StandardScaler
    #[serde(default)]
    pub scaler_scale: Option<Vec<f64>>,  // For both StandardScaler and MinMaxScaler
    #[serde(default)]
    pub scaler_min: Option<Vec<f64>>,  // For MinMaxScaler
}

fn default_norm() -> String {
    "l2".to_string()
}

/// Naive Bayes parameters
#[derive(Debug, Serialize, Deserialize)]
pub struct NaiveBayesModel {
    pub feature_log_prob: Vec<Vec<f64>>,  // [n_classes, n_features]
    pub class_log_prior: Vec<f64>,         // [n_classes]
    pub classes: Vec<String>,
}

/// Logistic Regression parameters
#[derive(Debug, Serialize, Deserialize)]
pub struct LogisticRegressionModel {
    pub coef: Vec<Vec<f64>>,  // [n_classes, n_features]
    pub intercept: Vec<f64>,   // [n_classes]
    pub classes: Vec<String>,
    #[serde(default)]
    pub scaler_mean: Option<Vec<f64>>,   // Optional StandardScaler mean
    #[serde(default)]
    pub scaler_scale: Option<Vec<f64>>,  // Optional StandardScaler scale
}

/// Linear SVM parameters
#[derive(Debug, Serialize, Deserialize)]
pub struct LinearSVMModel {
    pub coef: Vec<Vec<f64>>,  // [n_classes, n_features]
    pub intercept: Vec<f64>,   // [n_classes]
    pub classes: Vec<String>,
}

/// XGBoost model with tree structures
#[derive(Debug, Serialize, Deserialize)]
pub struct XGBoostModel {
    pub trees: Vec<serde_json::Value>,  // Tree structures as JSON
    pub n_estimators: usize,
    pub learning_rate: f64,
    pub base_score: f64,
    pub classes: Vec<String>,
}

/// Meta-classifier (Logistic Regression on ensemble outputs)
#[derive(Debug, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct MetaClassifier {
    pub coef: Vec<Vec<f64>>,
    pub intercept: Vec<f64>,
    pub classes: Vec<String>,
}

/// Load MessagePack model from file
pub fn load_msgpack<T: for<'de> Deserialize<'de>>(path: &Path) -> Result<T, String> {
    let mut file = File::open(path)
        .map_err(|e| format!("Failed to open {}: {}", path.display(), e))?;

    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)
        .map_err(|e| format!("Failed to read {}: {}", path.display(), e))?;

    rmp_serde::from_slice(&buffer)
        .map_err(|e| format!("Failed to deserialize {}: {}", path.display(), e))
}

/// Save MessagePack model to file
#[allow(dead_code)]
pub fn save_msgpack<T: Serialize>(model: &T, path: &Path) -> Result<(), String> {
    let buffer = rmp_serde::to_vec(model)
        .map_err(|e| format!("Failed to serialize: {}", e))?;

    std::fs::write(path, buffer)
        .map_err(|e| format!("Failed to write {}: {}", path.display(), e))?;

    Ok(())
}
