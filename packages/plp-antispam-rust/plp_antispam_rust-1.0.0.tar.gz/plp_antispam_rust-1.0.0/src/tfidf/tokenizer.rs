use regex::Regex;

// Token type enum
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TokenType {
    WordUnigram,
    WordBigram,
    CharTrigram,
    Word12Gram,  // Hybrid: both unigrams and bigrams (for Model 4)
}

/// Tokenizer for different n-gram types
pub struct Tokenizer {
    token_type: TokenType,
    word_pattern: Regex,
}

impl Tokenizer {
    pub fn new(token_type: TokenType) -> Self {
        // Match words (alphanumeric sequences, 2+ chars)
        let word_pattern = Regex::new(r"\b\w{2,}\b").unwrap();

        Self {
            token_type,
            word_pattern,
        }
    }

    /// Tokenize text into tokens based on type
    pub fn tokenize(&self, text: &str) -> Vec<String> {
        match self.token_type {
            TokenType::WordUnigram => self.word_unigrams(text),
            TokenType::WordBigram => self.word_bigrams(text),
            TokenType::CharTrigram => self.char_trigrams(text),
            TokenType::Word12Gram => self.word_12grams(text),
        }
    }

    /// Extract word unigrams (individual words)
    fn word_unigrams(&self, text: &str) -> Vec<String> {
        let lowercase = text.to_lowercase();
        self.word_pattern
            .find_iter(&lowercase)
            .map(|m| m.as_str().to_string())
            .collect()
    }

    /// Extract word bigrams (pairs of consecutive words)
    fn word_bigrams(&self, text: &str) -> Vec<String> {
        let lowercase = text.to_lowercase();
        let words: Vec<&str> = self.word_pattern
            .find_iter(&lowercase)
            .map(|m| m.as_str())
            .collect();

        if words.len() < 2 {
            return Vec::new();
        }

        words
            .windows(2)
            .map(|pair| format!("{} {}", pair[0], pair[1]))
            .collect()
    }

    /// Extract character trigrams (3-character sequences)
    fn char_trigrams(&self, text: &str) -> Vec<String> {
        let lowercase = text.to_lowercase();
        // Use simple character iteration (not graphemes) to match sklearn behavior
        let chars: Vec<char> = lowercase.chars().collect();

        if chars.len() < 3 {
            return Vec::new();
        }

        chars
            .windows(3)
            .map(|window| window.iter().collect::<String>())
            .collect()
    }

    /// Extract word 1-2 grams (both unigrams and bigrams combined)
    /// This matches sklearn's ngram_range=(1, 2)
    fn word_12grams(&self, text: &str) -> Vec<String> {
        let lowercase = text.to_lowercase();
        let words: Vec<&str> = self.word_pattern
            .find_iter(&lowercase)
            .map(|m| m.as_str())
            .collect();

        let mut tokens = Vec::new();

        // Add unigrams
        for word in &words {
            tokens.push(word.to_string());
        }

        // Add bigrams
        if words.len() >= 2 {
            for pair in words.windows(2) {
                tokens.push(format!("{} {}", pair[0], pair[1]));
            }
        }

        tokens
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_word_unigrams() {
        let tokenizer = Tokenizer::new(TokenType::WordUnigram);
        let tokens = tokenizer.tokenize("Hello World! This is a test.");
        assert_eq!(tokens, vec!["hello", "world", "this", "is", "test"]);
    }

    #[test]
    fn test_word_bigrams() {
        let tokenizer = Tokenizer::new(TokenType::WordBigram);
        let tokens = tokenizer.tokenize("Hello World Test");
        assert_eq!(tokens, vec!["hello world", "world test"]);
    }

    #[test]
    fn test_char_trigrams() {
        let tokenizer = Tokenizer::new(TokenType::CharTrigram);
        let tokens = tokenizer.tokenize("abc");
        assert_eq!(tokens, vec!["abc"]);

        let tokens = tokenizer.tokenize("test");
        assert_eq!(tokens, vec!["tes", "est"]);
    }
}
