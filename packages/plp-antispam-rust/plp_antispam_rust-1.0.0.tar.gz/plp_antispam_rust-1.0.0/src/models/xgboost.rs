use crate::serialization::XGBoostModel;
use serde::{Deserialize, Serialize};
use sprs::CsMat;

/// XGBoost model with tree ensemble
pub struct XGBoost {
    trees: Vec<TreeNode>,
    #[allow(dead_code)]
    n_estimators: usize,
    #[allow(dead_code)]
    learning_rate: f64,
    base_score: f64,
    #[allow(dead_code)]
    classes: Vec<String>,
}

/// XGBoost tree node structure (matches XGBoost JSON format)
#[derive(Debug, Serialize, Deserialize, Clone)]
struct TreeNode {
    nodeid: usize,
    #[serde(default)]
    split: Option<String>,      // "f5" -> feature 5
    #[serde(default)]
    split_condition: Option<f64>,
    #[serde(default)]
    yes: Option<usize>,          // left child node id
    #[serde(default)]
    no: Option<usize>,           // right child node id
    #[serde(default)]
    missing: Option<usize>,      // missing value branch (for sparse features)
    #[serde(default)]
    leaf: Option<f64>,           // leaf value
    #[serde(default)]
    children: Vec<TreeNode>,
}

impl XGBoost {
    /// Load from serialized model
    pub fn from_model(model: XGBoostModel) -> Result<Self, String> {
        // Deserialize trees from JSON values
        let trees: Result<Vec<TreeNode>, _> = model
            .trees
            .iter()
            .map(|tree_json| {
                serde_json::from_value(tree_json.clone())
                    .map_err(|e| format!("Failed to deserialize tree: {}", e))
            })
            .collect();

        let trees = trees?;

        Ok(Self {
            trees,
            n_estimators: model.n_estimators,
            learning_rate: model.learning_rate,
            base_score: model.base_score,
            classes: model.classes,
        })
    }

    /// Traverse a single tree and return prediction value
    #[allow(dead_code)]
    fn predict_tree(&self, tree: &TreeNode, features: &[f64]) -> f64 {
        self.predict_tree_recursive(tree, features, 0, 0, false)
    }

    /// Recursive tree traversal with optional logging
    fn predict_tree_recursive(&self, tree: &TreeNode, features: &[f64], tree_idx: usize, depth: usize, enable_logging: bool) -> f64 {
        let indent = "  ".repeat(depth);

        // Leaf node - return value
        if let Some(leaf_val) = tree.leaf {
            if enable_logging {
                eprintln!("{}Node {}: LEAF = {:.6}", indent, tree.nodeid, leaf_val);
            }
            return leaf_val;
        }

        // Split node - traverse
        if let (Some(split_str), Some(threshold)) = (&tree.split, tree.split_condition) {
            // Parse feature index from "f5" -> 5
            let feature_idx = split_str
                .trim_start_matches('f')
                .parse::<usize>()
                .unwrap_or(0);

            let feature_val = features.get(feature_idx).copied().unwrap_or(0.0);

            if enable_logging {
                eprintln!("{}Node {}:", indent, tree.nodeid);
                eprintln!("{}  Split on {} (idx={})", indent, split_str, feature_idx);
                eprintln!("{}  Feature value: {:.6}", indent, feature_val);
                eprintln!("{}  Threshold: {:.6}", indent, threshold);
                eprintln!("{}  yes={:?}, no={:?}, missing={:?}", indent, tree.yes, tree.no, tree.missing);
            }

            // CRITICAL: Handle sparse features (0.0 values) using the missing branch
            // In XGBoost with sparse data, zero values follow the 'missing' branch
            let next_id = if feature_val == 0.0 {
                // Sparse/missing value - use missing branch (defaults to yes if not specified)
                let branch_id = tree.missing.or(tree.yes);
                if enable_logging {
                    eprintln!("{}  → MISSING branch (feature is 0.0/sparse) → Node {:?}", indent, branch_id);
                }
                branch_id
            } else if feature_val < threshold {
                // Go left (yes)
                if enable_logging {
                    eprintln!("{}  → YES branch (val < threshold) → Node {:?}", indent, tree.yes);
                }
                tree.yes
            } else {
                // Go right (no)
                if enable_logging {
                    eprintln!("{}  → NO branch (val >= threshold) → Node {:?}", indent, tree.no);
                }
                tree.no
            };

            // Traverse to the selected child
            if let Some(child_id) = next_id {
                if let Some(child) = tree.children.iter().find(|c| c.nodeid == child_id) {
                    return self.predict_tree_recursive(child, features, tree_idx, depth + 1, enable_logging);
                } else {
                    eprintln!("WARNING: XGBoost tree traversal failed - child node {} not found", child_id);
                }
            }
        }

        // Fallback
        eprintln!("WARNING: XGBoost tree traversal failed - returning 0.0 fallback");
        0.0
    }

    /// Predict class probabilities for a batch of samples
    pub fn predict_proba(&self, x: &CsMat<f64>) -> Vec<(f64, f64)> {
        let n_samples = x.rows();
        let mut results = Vec::with_capacity(n_samples);

        for row_idx in 0..n_samples {
            let row = x.outer_view(row_idx).unwrap();

            // Convert sparse to dense for tree traversal
            let mut features = vec![0.0; x.cols()];
            let mut non_zero_count = 0;
            for (col_idx, &value) in row.iter() {
                features[col_idx] = value;
                if value != 0.0 {
                    non_zero_count += 1;
                }
            }

            // DEBUG: Print feature stats for first sample only
            if row_idx == 0 && n_samples == 1 {
                eprintln!("DEBUG XGBoost: Input features shape: {}, non-zero: {}", features.len(), non_zero_count);
                eprintln!("DEBUG XGBoost: base_score={}, n_trees={}", self.base_score, self.trees.len());
            }

            // CRITICAL FIX: Convert base_score from probability space to log-odds
            // base_score is stored as probability (e.g., 0.537450)
            // Must convert to log-odds: logit(p) = ln(p / (1-p))
            let base_score_logit = (self.base_score / (1.0 - self.base_score)).ln();

            // Sum predictions from all trees
            // CRITICAL FIX: Do NOT apply learning_rate during inference!
            // Learning rate is already baked into tree values during training
            let mut tree_sum = 0.0;
            for (i, tree) in self.trees.iter().enumerate() {
                // Enable detailed logging for first 3 trees when processing single email
                let enable_logging = row_idx == 0 && n_samples == 1 && i < 3;

                if enable_logging {
                    eprintln!("\n{}", "=".repeat(60));
                    eprintln!("TREE {} TRAVERSAL", i);
                    eprintln!("{}", "=".repeat(60));
                }

                let tree_pred = self.predict_tree_recursive(tree, &features, i, 0, enable_logging);
                tree_sum += tree_pred;

                if enable_logging {
                    eprintln!("Tree {} final leaf value: {:.6}\n", i, tree_pred);
                }
            }

            // CORRECT FORMULA: raw_prediction = logit(base_score) + sum(tree_values)
            let raw_prediction = base_score_logit + tree_sum;

            // DEBUG: Print final raw prediction for first sample
            if row_idx == 0 && n_samples == 1 {
                eprintln!("DEBUG XGBoost: base_logit={:.6}, tree_sum={:.6}, raw_pred={:.6}",
                         base_score_logit, tree_sum, raw_prediction);
            }

            // Convert to probability using sigmoid
            let spam_prob = 1.0 / (1.0 + (-raw_prediction).exp());
            let clean_prob = 1.0 - spam_prob;

            results.push((clean_prob, spam_prob));
        }

        results
    }

    /// Get class names
    #[allow(dead_code)]
    pub fn classes(&self) -> &[String] {
        &self.classes
    }
}
