pub mod naive_bayes;
pub mod logistic;
pub mod svm;
pub mod xgboost;

pub use naive_bayes::NaiveBayes;
pub use logistic::LogisticRegression;
pub use svm::LinearSVM;
pub use xgboost::XGBoost;
