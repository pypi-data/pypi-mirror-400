use regex::Regex;
use rayon::prelude::*;
use std::sync::LazyLock;
use pyo3::prelude::*;

/// Regex patterns (compiled once, reused)
static HTML_TAG_REGEX: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"<[^>]+>").unwrap());
static BASE64_REGEX: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[A-Za-z0-9+/]{20,}={0,2}").unwrap());
static ENTITY_REGEX: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"&[a-zA-Z]+;|&#\d+;").unwrap());
static URL_REGEX: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"https?://[^\s]+|www\.[^\s]+").unwrap());
static CONSECUTIVE_PUNCT_REGEX: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[!?]{2,}").unwrap());

/// Extract all 28 custom features from email text
#[pyfunction]
pub fn extract_features(text: &str) -> Vec<f64> {
    let mut features = vec![0.0; 28];

    let text_lower = text.to_lowercase();
    let text_len = text.len() as f64;
    let text_len_safe = text_len.max(1.0);

    // Count words for density calculations
    let words: Vec<&str> = text.split_whitespace().collect();
    let word_count = words.len() as f64;
    let word_count_safe = word_count.max(1.0);

    // 0. html_ratio
    let html_matches = HTML_TAG_REGEX.find_iter(text).count() as f64;
    features[0] = html_matches / text_len_safe;

    // 1. base64_density
    let base64_len: usize = BASE64_REGEX.find_iter(text).map(|m| m.as_str().len()).sum();
    features[1] = (base64_len as f64) / text_len_safe;

    // 2. caps_ratio
    let caps_count = text.chars().filter(|c| c.is_uppercase()).count() as f64;
    features[2] = caps_count / text_len_safe;

    // 3. exclamation_ratio
    let exclamation_count = text.chars().filter(|&c| c == '!').count() as f64;
    features[3] = exclamation_count / text_len_safe;

    // 4. question_ratio
    let question_count = text.chars().filter(|&c| c == '?').count() as f64;
    features[4] = question_count / text_len_safe;

    // 5. pharmaceutical_keywords
    let pharma_keywords = [
        "viagra", "cialis", "pharmacy", "prescription", "pills", "medication",
        "drug", "xanax", "valium", "ambien", "levitra", "phentermine"
    ];
    let pharma_count = pharma_keywords.iter()
        .filter(|&&kw| text_lower.contains(kw))
        .count() as f64;
    features[5] = pharma_count;

    // 6. financial_scam_keywords
    let financial_keywords = [
        "bank", "credit", "account", "password", "verify", "suspended",
        "urgent", "wire", "transfer", "lottery", "winner", "claim", "paypal",
        "ebay", "western union", "money gram"
    ];
    let financial_count = financial_keywords.iter()
        .filter(|&&kw| text_lower.contains(kw))
        .count() as f64;
    features[6] = financial_count;

    // 7. avg_word_length
    let total_word_len: usize = words.iter().map(|w| w.len()).sum();
    features[7] = if word_count > 0.0 {
        total_word_len as f64 / word_count
    } else {
        0.0
    };

    // 8. punctuation_density
    let punct_count = text.chars()
        .filter(|c| c.is_ascii_punctuation())
        .count() as f64;
    features[8] = punct_count / text_len_safe;

    // 9. encoding_diversity
    let charset_indicators = ["utf-8", "iso-8859", "windows-1252", "base64"];
    let encoding_count = charset_indicators.iter()
        .filter(|&&enc| text_lower.contains(enc))
        .count() as f64;
    features[9] = encoding_count;

    // 10. subject_caps_ratio
    let subject_line = text.lines().next().unwrap_or("");
    let subject_caps = subject_line.chars().filter(|c| c.is_uppercase()).count() as f64;
    let subject_len = subject_line.len() as f64;
    features[10] = if subject_len > 0.0 {
        subject_caps / subject_len
    } else {
        0.0
    };

    // 11. has_subject
    features[11] = if !subject_line.is_empty() { 1.0 } else { 0.0 };

    // 12. has_reply_indicators
    let reply_indicators = ["re:", "fwd:", "reply"];
    let has_reply = reply_indicators.iter()
        .any(|&ind| text_lower.contains(ind));
    features[12] = if has_reply { 1.0 } else { 0.0 };

    // 13. mixed_charset_count
    let has_ascii = text.chars().any(|c| c.is_ascii());
    let has_unicode = text.chars().any(|c| !c.is_ascii());
    features[13] = if has_ascii && has_unicode { 1.0 } else { 0.0 };

    // 14. html_entity_density
    let entity_count = ENTITY_REGEX.find_iter(text).count() as f64;
    features[14] = entity_count / text_len_safe;

    // 15. zero_width_chars
    let zero_width_count = text.chars()
        .filter(|&c| c == '\u{200B}' || c == '\u{200C}' || c == '\u{200D}' || c == '\u{FEFF}')
        .count() as f64;
    features[15] = zero_width_count;

    // 16. leet_speak_ratio
    let leet_patterns = ["@", "3", "4", "7", "1", "0"];
    let leet_count = leet_patterns.iter()
        .map(|&p| text.matches(p).count())
        .sum::<usize>() as f64;
    features[16] = leet_count / text_len_safe;

    // 17. repeated_chars_ratio
    let mut repeated_count = 0;
    let chars: Vec<char> = text.chars().collect();
    let mut i = 0;
    while i < chars.len() {
        let mut j = i + 1;
        while j < chars.len() && chars[j] == chars[i] {
            j += 1;
        }
        if j - i >= 3 {
            repeated_count += 1;
        }
        i = j.max(i + 1);
    }
    features[17] = (repeated_count as f64) / text_len_safe;

    // 18. numeric_ratio
    let numeric_count = text.chars().filter(|c| c.is_numeric()).count() as f64;
    features[18] = numeric_count / text_len_safe;

    // 19. avg_sentence_length
    let sentences: Vec<&str> = text.split(|c| c == '.' || c == '!' || c == '?').collect();
    let sentence_count = sentences.len() as f64;
    features[19] = if sentence_count > 0.0 {
        word_count / sentence_count
    } else {
        0.0
    };

    // 20. emotional_manipulation_score
    let emotional_words = [
        "urgent", "limited", "act now", "don't miss", "exclusive",
        "guaranteed", "amazing", "incredible", "you won", "congratulations"
    ];
    let emotional_count = emotional_words.iter()
        .filter(|&&word| text_lower.contains(word))
        .count() as f64;
    features[20] = emotional_count;

    // 21. dollar_density (per 100 chars)
    let dollar_count = text.chars().filter(|&c| c == '$').count() as f64;
    features[21] = (dollar_count / text_len_safe) * 100.0;

    // 22. url_density (per 100 words)
    let url_count = URL_REGEX.find_iter(text).count() as f64;
    features[22] = (url_count / word_count_safe) * 100.0;

    // 23. suspicious_url_ratio (per 100 words)
    let suspicious_domains = [".tk", ".ml", ".ga", ".cf", "bit.ly", "tinyurl", "goo.gl"];
    let suspicious_url_count = suspicious_domains.iter()
        .filter(|&&domain| text_lower.contains(domain))
        .count() as f64;
    features[23] = (suspicious_url_count / word_count_safe) * 100.0;

    // 24. urgency_score (per 100 words)
    let urgency_keywords = [
        "urgent", "immediately", "asap", "hurry", "now", "quick",
        "fast", "limited time", "act now", "expires"
    ];
    let urgency_count = urgency_keywords.iter()
        .filter(|&&kw| text_lower.contains(kw))
        .count() as f64;
    features[24] = (urgency_count / word_count_safe) * 100.0;

    // 25. scam_pattern_score
    let scam_patterns = [
        "you won", "you've won", "claim your", "click here", "verify your account",
        "confirm your", "update your", "suspended account", "unusual activity",
        "refund", "tax refund", "inheritance", "nigerian prince"
    ];
    let scam_count = scam_patterns.iter()
        .filter(|&&pattern| text_lower.contains(pattern))
        .count() as f64;
    features[25] = scam_count;

    // 26. all_caps_word_ratio
    let all_caps_words = words.iter()
        .filter(|&&w| w.len() > 1 && w.chars().all(|c| !c.is_lowercase()))
        .count() as f64;
    features[26] = all_caps_words / word_count_safe;

    // 27. consecutive_punctuation_score
    let consecutive_punct_count = CONSECUTIVE_PUNCT_REGEX.find_iter(text).count() as f64;
    features[27] = consecutive_punct_count;

    features
}

/// Batch extract features from multiple emails (parallel processing)
pub fn extract_features_batch(texts: &[String]) -> Vec<Vec<f64>> {
    texts
        .par_iter()
        .map(|text| extract_features(text))
        .collect()
}

/// Batch extract features wrapper for Python
#[pyfunction]
#[pyo3(name = "extract_features_batch")]
pub fn extract_features_batch_py(texts: Vec<String>) -> Vec<Vec<f64>> {
    extract_features_batch(&texts)
}
