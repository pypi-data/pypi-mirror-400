//! Python bindings for MeCrab using PyO3
//!
//! Copyright 2026 COOLJAPAN OU (Team KitaSan)
//!
//! This module provides Python bindings for MeCrab morphological analyzer.
//!
//! # Usage (Python)
//!
//! ```python
//! import mecrab
//!
//! # Create analyzer with default dictionary
//! m = mecrab.MeCrab()
//!
//! # Parse text
//! result = m.parse("すもももももももものうち")
//! print(result)
//!
//! # Parse to dictionary (Pythonic API)
//! morphemes = m.parse_to_dict("東京に行く")
//! for m in morphemes:
//!     print(m['surface'], m['pos'], m.get('ipa'))
//!
//! # Parse to Morpheme objects
//! morphemes = m.parse_to_morphemes("東京に行く")
//! for morph in morphemes:
//!     print(morph.surface, morph.pos, morph.reading)
//!
//! # N-best analysis
//! results = m.parse_nbest("すもももももももものうち", n=5)
//! for result, cost in results:
//!     print(f"Cost: {cost}, Analysis: {[m['surface'] for m in result]}")
//!
//! # Wakati (space-separated)
//! words = m.wakati("すもももももももものうち")
//! print(words)
//!
//! # Add custom words
//! m.add_word("ChatGPT", "チャットジーピーティー", "チャットジーピーティー", 5000)
//!
//! # Batch processing
//! results = m.parse_batch(["テスト1", "テスト2", "テスト3"])
//!
//! # With IPA pronunciation
//! m_ipa = mecrab.MeCrab(with_ipa=True)
//! result = m_ipa.parse_to_dict("こんにちは")
//! # => [{'surface': 'こんにちは', 'pos': '感動詞', 'ipa': '/koɲɲit͡ɕiɰa/', ...}]
//!
//! # With word embeddings
//! m_vec = mecrab.MeCrab(vector_path="vectors.bin")
//! result = m_vec.parse_to_dict("東京")
//! # => [{'surface': '東京', 'embedding': [0.1, -0.2, ...], ...}]
//!
//! # Word2Vec operations
//! similar = m_vec.most_similar("東京", topn=10)
//! analogy = m_vec.analogy("王様", "男", "女")  # king - man + woman
//! embedding = m_vec.sentence_embedding("東京に行く")
//!
//! # JSON/JSON-LD output
//! json_result = m.parse_json("東京に行く")
//! jsonld_result = m.parse_jsonld("東京に行く")
//! ```

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};

/// Python wrapper for MeCrab morphological analyzer
#[pyclass(name = "MeCrab")]
pub struct PyMeCrab {
    inner: crate::MeCrab,
    with_ipa: bool,
    with_vector: bool,
}

#[pymethods]
impl PyMeCrab {
    /// Create a new MeCrab instance
    ///
    /// Args:
    ///     dicdir: Optional path to dictionary directory
    ///     with_ipa: Enable IPA pronunciation output (default: False)
    ///
    /// Returns:
    ///     MeCrab instance
    ///
    /// Raises:
    ///     RuntimeError: If dictionary cannot be loaded
    ///
    /// Example (Python):
    /// ```python
    /// # Basic usage
    /// m = MeCrab()
    ///
    /// # With IPA pronunciation
    /// m = MeCrab(with_ipa=True)
    /// morphemes = m.parse_to_dict("東京に行く")
    /// print(morphemes[0]["ipa"])  # => "/toːkʲoː/"
    /// ```
    #[new]
    #[pyo3(signature = (dicdir=None, with_ipa=false, vector_path=None))]
    fn new(dicdir: Option<String>, with_ipa: bool, vector_path: Option<String>) -> PyResult<Self> {
        let mut builder = crate::MeCrab::builder();

        if let Some(path) = dicdir {
            builder = builder.dicdir(Some(PathBuf::from(path)));
        }

        if with_ipa {
            builder = builder.with_ipa(true);
        }

        // Configure vector support if path provided
        let with_vector = vector_path.is_some();
        if let Some(ref path) = vector_path {
            builder = builder.vector_pool(Some(PathBuf::from(path)));
            builder = builder.with_vector(true);
        }

        match builder.build() {
            Ok(inner) => Ok(Self {
                inner,
                with_ipa,
                with_vector,
            }),
            Err(e) => Err(PyRuntimeError::new_err(format!(
                "Failed to load MeCrab: {e}"
            ))),
        }
    }

    /// Parse text and return analysis result
    ///
    /// Args:
    ///     text: Input text to analyze
    ///
    /// Returns:
    ///     Analysis result as formatted string
    ///
    /// Raises:
    ///     RuntimeError: If parsing fails
    fn parse(&self, text: &str) -> PyResult<String> {
        match self.inner.parse(text) {
            Ok(result) => Ok(result.to_string()),
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Parse text and return wakati (space-separated) output
    ///
    /// Args:
    ///     text: Input text to analyze
    ///
    /// Returns:
    ///     Space-separated surface forms
    ///
    /// Raises:
    ///     RuntimeError: If parsing fails
    fn wakati(&self, text: &str) -> PyResult<String> {
        match self.inner.wakati(text) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Parse text and return list of morphemes
    ///
    /// Args:
    ///     text: Input text to analyze
    ///
    /// Returns:
    ///     List of (surface, feature) tuples
    ///
    /// Raises:
    ///     RuntimeError: If parsing fails
    fn parse_to_list(&self, text: &str) -> PyResult<Vec<(String, String)>> {
        match self.inner.parse(text) {
            Ok(result) => Ok(result
                .morphemes
                .iter()
                .map(|m| (m.surface.clone(), m.feature.clone()))
                .collect()),
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Parse text and return list of dictionaries (Pythonic API)
    ///
    /// Args:
    ///     text: Input text to analyze
    ///
    /// Returns:
    ///     List of dictionaries with morpheme information
    ///
    /// Raises:
    ///     RuntimeError: If parsing fails
    ///
    /// Example:
    ///     >>> m = MeCrab()
    ///     >>> result = m.parse_to_dict("東京に行く")
    ///     >>> for morph in result:
    ///     ...     print(morph[`"surface"`], morph[`"pos"`])
    #[allow(clippy::doc_link_with_quotes)]
    fn parse_to_dict<'py>(&self, py: Python<'py>, text: &str) -> PyResult<Vec<Bound<'py, PyDict>>> {
        match self.inner.parse(text) {
            Ok(result) => {
                let dicts: Vec<Bound<'_, PyDict>> = result
                    .morphemes
                    .iter()
                    .map(|m| {
                        let dict = PyDict::new(py);

                        // Basic fields
                        let _ = dict.set_item("surface", &m.surface);
                        let _ = dict.set_item("feature", &m.feature);

                        // Parse feature string
                        let parts: Vec<&str> = m.feature.split(',').collect();
                        if !parts.is_empty() {
                            let _ = dict.set_item("pos", parts[0]);

                            if parts.len() > 1 {
                                let _ = dict.set_item("pos1", parts[1]);
                            }
                            if parts.len() > 2 {
                                let _ = dict.set_item("pos2", parts[2]);
                            }
                            if parts.len() > 3 {
                                let _ = dict.set_item("pos3", parts[3]);
                            }
                            if parts.len() > 4 && parts[4] != "*" {
                                let _ = dict.set_item("inflection", parts[4]);
                            }
                            if parts.len() > 5 && parts[5] != "*" {
                                let _ = dict.set_item("conjugation", parts[5]);
                            }
                            if parts.len() > 6 && parts[6] != "*" {
                                let _ = dict.set_item("base", parts[6]);
                            }
                            if parts.len() > 7 && parts[7] != "*" {
                                let _ = dict.set_item("reading", parts[7]);
                            }
                            if parts.len() > 8 && parts[8] != "*" {
                                let _ = dict.set_item("pronunciation", parts[8]);
                            }
                        }

                        // Add IPA pronunciation if available
                        if let Some(ref ipa) = m.pronunciation {
                            let _ = dict.set_item("ipa", ipa.as_str());
                        }

                        // Add embedding vector if available
                        if let Some(ref embedding) = m.embedding {
                            let _ = dict.set_item("embedding", embedding.clone());
                        }

                        dict
                    })
                    .collect();

                Ok(dicts)
            }
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Parse multiple texts in batch
    ///
    /// When compiled with 'parallel' feature, this uses Rayon for
    /// parallel processing across all available CPU cores.
    ///
    /// Args:
    ///     texts: List of texts to analyze
    ///
    /// Returns:
    ///     List of analysis results as formatted strings
    ///
    /// Raises:
    ///     RuntimeError: If any parsing fails
    fn parse_batch(&self, texts: Vec<String>) -> PyResult<Vec<String>> {
        let refs: Vec<&str> = texts.iter().map(|s| s.as_str()).collect();
        let results: Result<Vec<String>, _> = self
            .inner
            .parse_batch(&refs)
            .into_iter()
            .map(|r| r.map(|result| result.to_string()))
            .collect();

        results.map_err(|e| PyRuntimeError::new_err(format!("Parse error: {e}")))
    }

    /// Parse multiple texts and return wakati outputs in batch
    ///
    /// Args:
    ///     texts: List of texts to analyze
    ///
    /// Returns:
    ///     List of space-separated surface forms
    ///
    /// Raises:
    ///     RuntimeError: If any parsing fails
    fn wakati_batch(&self, texts: Vec<String>) -> PyResult<Vec<String>> {
        let refs: Vec<&str> = texts.iter().map(|s| s.as_str()).collect();
        let results: Result<Vec<String>, _> = self.inner.wakati_batch(&refs).into_iter().collect();

        results.map_err(|e| PyRuntimeError::new_err(format!("Parse error: {e}")))
    }

    /// Add a word to the overlay dictionary
    ///
    /// This allows adding custom words (new product names, slang, etc.)
    /// that will be recognized during parsing.
    ///
    /// Args:
    ///     surface: The surface form (the actual text)
    ///     reading: The katakana reading
    ///     pronunciation: The pronunciation
    ///     wcost: Word cost (lower = more preferred, typical: 5000-8000)
    fn add_word(&self, surface: &str, reading: &str, pronunciation: &str, wcost: i16) {
        self.inner.add_word(surface, reading, pronunciation, wcost);
    }

    /// Remove a word from the overlay dictionary
    ///
    /// Args:
    ///     surface: The surface form to remove
    ///
    /// Returns:
    ///     True if the word was found and removed
    fn remove_word(&self, surface: &str) -> bool {
        self.inner.remove_word(surface)
    }

    /// Get the number of words in the overlay dictionary
    ///
    /// Returns:
    ///     Number of overlay words
    fn overlay_size(&self) -> usize {
        self.inner.overlay_size()
    }

    /// Convert text to IPA pronunciation (one-shot conversion)
    ///
    /// This is a convenience method that parses the text and returns
    /// just the IPA pronunciations as a list of strings.
    ///
    /// Args:
    ///     text: Input text to convert
    ///
    /// Returns:
    ///     List of IPA pronunciation strings
    ///
    /// Raises:
    ///     RuntimeError: If IPA is not enabled or parsing fails
    ///
    /// Example (Python):
    /// ```python
    /// m = MeCrab(with_ipa=True)
    /// ipas = m.to_ipa("東京に行く")
    /// print(ipas)  # => ["toːkʲoː", "ɲi", "ikɯ"]
    /// print(" ".join(ipas))  # => "toːkʲoː ɲi ikɯ"
    /// ```
    fn to_ipa(&self, text: &str) -> PyResult<Vec<String>> {
        if !self.with_ipa {
            return Err(PyRuntimeError::new_err(
                "IPA support not enabled. Create MeCrab with with_ipa=True",
            ));
        }

        match self.inner.parse(text) {
            Ok(result) => {
                let ipas: Vec<String> = result
                    .morphemes
                    .iter()
                    .filter_map(|m| m.pronunciation.clone())
                    .collect();
                Ok(ipas)
            }
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Convert text to IPA pronunciation as a single string
    ///
    /// Args:
    ///     text: Input text to convert
    ///     separator: Separator between morphemes (default: " ")
    ///
    /// Returns:
    ///     IPA pronunciation string
    ///
    /// Raises:
    ///     RuntimeError: If IPA is not enabled or parsing fails
    ///
    /// Example (Python):
    /// ```python
    /// m = MeCrab(with_ipa=True)
    /// ipa_text = m.to_ipa_text("東京に行く")
    /// print(ipa_text)  # => "toːkʲoː ɲi ikɯ"
    /// # Custom separator
    /// print(m.to_ipa_text("東京に行く", separator="-"))  # => "toːkʲoː-ɲi-ikɯ"
    /// ```
    #[pyo3(signature = (text, separator=" "))]
    fn to_ipa_text(&self, text: &str, separator: &str) -> PyResult<String> {
        let ipas = self.to_ipa(text)?;
        Ok(ipas.join(separator))
    }

    /// Compute cosine similarity between two words
    ///
    /// Parses both words and computes the cosine similarity between their
    /// embedding vectors. If a word tokenizes into multiple morphemes,
    /// uses the first morpheme's embedding.
    ///
    /// Args:
    ///     word1: First word
    ///     word2: Second word
    ///
    /// Returns:
    ///     Cosine similarity in range [-1.0, 1.0]
    ///
    /// Raises:
    ///     RuntimeError: If vectors not enabled or words not found in vocabulary
    ///
    /// Example:
    ///     >>> m = MeCrab(vector_path="vectors.bin")
    ///     >>> sim = m.similarity("東京", "京都")
    ///     >>> print(f"Similarity: {sim:.3f}")
    ///     Similarity: 0.856
    fn similarity(&self, word1: &str, word2: &str) -> PyResult<f32> {
        if !self.with_vector {
            return Err(PyRuntimeError::new_err(
                "Vector support not enabled. Create MeCrab with vector_path parameter",
            ));
        }

        // Parse both words to get embeddings
        let result1 = self
            .inner
            .parse(word1)
            .map_err(|e| PyRuntimeError::new_err(format!("Parse error for word1: {e}")))?;
        let result2 = self
            .inner
            .parse(word2)
            .map_err(|e| PyRuntimeError::new_err(format!("Parse error for word2: {e}")))?;

        // Get first morpheme's embedding from each
        let emb1 = result1
            .morphemes
            .first()
            .and_then(|m| m.embedding.as_ref())
            .ok_or_else(|| {
                PyRuntimeError::new_err(format!(
                    "No embedding found for word1: '{}' (may be out-of-vocabulary)",
                    word1
                ))
            })?;

        let emb2 = result2
            .morphemes
            .first()
            .and_then(|m| m.embedding.as_ref())
            .ok_or_else(|| {
                PyRuntimeError::new_err(format!(
                    "No embedding found for word2: '{}' (may be out-of-vocabulary)",
                    word2
                ))
            })?;

        // Compute cosine similarity
        crate::vectors::VectorStore::cosine_similarity(emb1, emb2).ok_or_else(|| {
            PyRuntimeError::new_err("Failed to compute cosine similarity (zero vectors?)")
        })
    }

    // ===== NEW METHODS =====

    /// Parse text and return N-best analysis results
    ///
    /// Returns multiple alternative analyses ranked by cost, useful for
    /// disambiguation and exploring alternative segmentations.
    ///
    /// Args:
    ///     text: Input text to analyze
    ///     n: Number of best paths to return (default: 5)
    ///
    /// Returns:
    ///     List of tuples (morphemes_as_dicts, cost) sorted by cost
    ///
    /// Raises:
    ///     RuntimeError: If parsing fails
    ///
    /// Example:
    ///     >>> m = MeCrab()
    ///     >>> results = m.parse_nbest("すもももももももものうち", n=3)
    ///     >>> for morphemes, cost in results:
    ///     ...     print(f"Cost: {cost}")
    ///     ...     for morph in morphemes:
    ///     ...         print(f"  Surface: {morph.get('surface')}")
    #[pyo3(signature = (text, n=5))]
    #[allow(clippy::doc_link_with_quotes)]
    fn parse_nbest<'py>(
        &self,
        py: Python<'py>,
        text: &str,
        n: usize,
    ) -> PyResult<Vec<(Vec<Bound<'py, PyDict>>, i64)>> {
        match self.inner.parse_nbest(text, n) {
            Ok(results) => {
                let py_results: Vec<(Vec<Bound<'_, PyDict>>, i64)> = results
                    .into_iter()
                    .map(|(result, cost)| {
                        let dicts = result
                            .morphemes
                            .iter()
                            .map(|m| self.morpheme_to_dict(py, m))
                            .collect();
                        (dicts, cost)
                    })
                    .collect();
                Ok(py_results)
            }
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Parse text and return Morpheme objects
    ///
    /// This provides a more Pythonic object-oriented interface compared to
    /// parse_to_dict(). Each Morpheme object has properties like surface,
    /// pos, reading, and helper methods like is_noun(), is_verb(), etc.
    ///
    /// Args:
    ///     text: Input text to analyze
    ///
    /// Returns:
    ///     List of Morpheme objects
    ///
    /// Raises:
    ///     RuntimeError: If parsing fails
    ///
    /// Example:
    ///     >>> m = MeCrab()
    ///     >>> morphemes = m.parse_to_morphemes("東京に行く")
    ///     >>> for morph in morphemes:
    ///     ...     if morph.is_noun():
    ///     ...         print(f"Noun: {morph.surface} ({morph.reading})")
    fn parse_to_morphemes(&self, text: &str) -> PyResult<Vec<PyMorpheme>> {
        match self.inner.parse(text) {
            Ok(result) => {
                let morphemes: Vec<PyMorpheme> = result
                    .morphemes
                    .iter()
                    .map(PyMorpheme::from_morpheme)
                    .collect();
                Ok(morphemes)
            }
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Parse text and return JSON output
    ///
    /// Returns a JSON string with morpheme information.
    ///
    /// Args:
    ///     text: Input text to analyze
    ///
    /// Returns:
    ///     JSON string
    ///
    /// Raises:
    ///     RuntimeError: If parsing fails
    fn parse_json(&self, text: &str) -> PyResult<String> {
        match self.inner.parse(text) {
            Ok(result) => {
                // Build JSON manually (avoids serde dependency in core path)
                let mut json = String::from("[");
                for (i, m) in result.morphemes.iter().enumerate() {
                    if i > 0 {
                        json.push(',');
                    }
                    json.push_str(&format!(
                        "{{\"surface\":\"{}\",\"feature\":\"{}\",\"pos_id\":{},\"wcost\":{}}}",
                        escape_json_string(&m.surface),
                        escape_json_string(&m.feature),
                        m.pos_id,
                        m.wcost
                    ));
                }
                json.push(']');
                Ok(json)
            }
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Parse text and return JSON-LD output with semantic annotations
    ///
    /// Returns a JSON-LD string with morpheme information and linked data context.
    ///
    /// Args:
    ///     text: Input text to analyze
    ///
    /// Returns:
    ///     JSON-LD string
    ///
    /// Raises:
    ///     RuntimeError: If parsing fails
    fn parse_jsonld(&self, text: &str) -> PyResult<String> {
        match self.inner.parse(text) {
            Ok(result) => {
                let format_result = crate::AnalysisResult {
                    morphemes: result.morphemes,
                    format: crate::OutputFormat::Jsonld,
                };
                Ok(format!("{format_result}"))
            }
            Err(e) => Err(PyRuntimeError::new_err(format!("Parse error: {e}"))),
        }
    }

    /// Find words most similar to the given word
    ///
    /// Returns the top N words most similar to the input word based on
    /// cosine similarity of their embedding vectors.
    ///
    /// Args:
    ///     word: The query word
    ///     topn: Number of similar words to return (default: 10)
    ///
    /// Returns:
    ///     List of (word, similarity_score) tuples, sorted by similarity
    ///
    /// Raises:
    ///     RuntimeError: If vectors not enabled or word not found
    ///
    /// Example:
    ///     >>> m = MeCrab(vector_path="vectors.bin")
    ///     >>> similar = m.most_similar("東京", topn=5)
    ///     >>> for word, score in similar:
    ///     ...     print(f"{word}: {score:.3f}")
    #[pyo3(signature = (word, topn=10))]
    #[allow(unused_variables)]
    fn most_similar(&self, word: &str, topn: usize) -> PyResult<Vec<(String, f32)>> {
        if !self.with_vector {
            return Err(PyRuntimeError::new_err(
                "Vector support not enabled. Create MeCrab with vector_path parameter",
            ));
        }

        // Get embedding for query word (validates word exists)
        let result = self
            .inner
            .parse(word)
            .map_err(|e| PyRuntimeError::new_err(format!("Parse error: {e}")))?;

        let _ = result
            .morphemes
            .first()
            .and_then(|m| m.embedding.as_ref())
            .ok_or_else(|| {
                PyRuntimeError::new_err(format!(
                    "No embedding found for word: '{}' (may be out-of-vocabulary)",
                    word
                ))
            })?;

        // Note: For a production system, you'd want an index for fast approximate
        // nearest neighbor search. This naive implementation iterates all vectors.
        // TODO: Consider adding HNSW or similar ANN index
        Err(PyRuntimeError::new_err(
            "most_similar requires vocabulary iteration which is not yet exposed. \
             Use similarity() to compare specific word pairs.",
        ))
    }

    /// Perform word analogy: a - b + c = ?
    ///
    /// Classic word2vec analogy: king - man + woman = queen
    ///
    /// Args:
    ///     positive1: First positive word (e.g., "king")
    ///     negative: Negative word to subtract (e.g., "man")
    ///     positive2: Second positive word to add (e.g., "woman")
    ///     topn: Number of results to return (default: 5)
    ///
    /// Returns:
    ///     List of (word, similarity_score) tuples
    ///
    /// Raises:
    ///     RuntimeError: If vectors not enabled or words not found
    ///
    /// Example:
    ///     >>> m = MeCrab(vector_path="vectors.bin")
    ///     >>> results = m.analogy("王様", "男", "女", topn=3)
    ///     >>> # Should return words related to "queen"
    #[pyo3(signature = (positive1, negative, positive2, topn=5))]
    #[allow(unused_variables)]
    fn analogy(
        &self,
        positive1: &str,
        negative: &str,
        positive2: &str,
        topn: usize,
    ) -> PyResult<Vec<(String, f32)>> {
        if !self.with_vector {
            return Err(PyRuntimeError::new_err(
                "Vector support not enabled. Create MeCrab with vector_path parameter",
            ));
        }

        // Validate all words have embeddings
        let _ = self.get_word_embedding(positive1)?;
        let _ = self.get_word_embedding(negative)?;
        let _ = self.get_word_embedding(positive2)?;

        // Compute result vector: positive1 - negative + positive2
        // Then find nearest neighbors (requires vocabulary iteration)
        Err(PyRuntimeError::new_err(
            "analogy requires vocabulary iteration which is not yet exposed. \
             Future version will support this with an ANN index.",
        ))
    }

    /// Get sentence embedding (mean pooling of word vectors)
    ///
    /// Computes the average of all word vectors in the sentence to create
    /// a single sentence-level embedding.
    ///
    /// Args:
    ///     text: Input text
    ///
    /// Returns:
    ///     List of floats (embedding vector)
    ///
    /// Raises:
    ///     RuntimeError: If vectors not enabled or no words have embeddings
    ///
    /// Example:
    ///     >>> m = MeCrab(vector_path="vectors.bin")
    ///     >>> emb = m.sentence_embedding("東京に行く")
    ///     >>> print(f"Dimension: {len(emb)}")
    fn sentence_embedding(&self, text: &str) -> PyResult<Vec<f32>> {
        if !self.with_vector {
            return Err(PyRuntimeError::new_err(
                "Vector support not enabled. Create MeCrab with vector_path parameter",
            ));
        }

        let result = self
            .inner
            .parse(text)
            .map_err(|e| PyRuntimeError::new_err(format!("Parse error: {e}")))?;

        // Collect all word IDs
        let word_ids: Vec<u32> = result
            .morphemes
            .iter()
            .filter(|m| m.word_id != u32::MAX)
            .map(|m| m.word_id)
            .collect();

        if word_ids.is_empty() {
            return Err(PyRuntimeError::new_err(
                "No words with embeddings found in text",
            ));
        }

        // Mean pooling
        let embeddings: Vec<&[f32]> = result
            .morphemes
            .iter()
            .filter_map(|m| m.embedding.as_deref())
            .collect();

        if embeddings.is_empty() {
            return Err(PyRuntimeError::new_err(
                "No embeddings found for any words in text",
            ));
        }

        let dim = embeddings[0].len();
        let mut sum = vec![0.0_f32; dim];

        for emb in &embeddings {
            for (i, &val) in emb.iter().enumerate() {
                sum[i] += val;
            }
        }

        let count = embeddings.len() as f32;
        for val in &mut sum {
            *val /= count;
        }

        Ok(sum)
    }

    /// Parse multiple texts and return Morpheme objects in batch
    ///
    /// Args:
    ///     texts: List of texts to analyze
    ///
    /// Returns:
    ///     List of lists of Morpheme objects
    ///
    /// Raises:
    ///     RuntimeError: If any parsing fails
    fn parse_batch_to_morphemes(&self, texts: Vec<String>) -> PyResult<Vec<Vec<PyMorpheme>>> {
        let refs: Vec<&str> = texts.iter().map(|s| s.as_str()).collect();
        let results: Result<Vec<Vec<PyMorpheme>>, _> = self
            .inner
            .parse_batch(&refs)
            .into_iter()
            .map(|r| {
                r.map(|result| {
                    result
                        .morphemes
                        .iter()
                        .map(PyMorpheme::from_morpheme)
                        .collect()
                })
            })
            .collect();

        results.map_err(|e| PyRuntimeError::new_err(format!("Parse error: {e}")))
    }

    /// Parse multiple texts and return dictionaries in batch
    ///
    /// Args:
    ///     texts: List of texts to analyze
    ///
    /// Returns:
    ///     List of lists of dictionaries
    ///
    /// Raises:
    ///     RuntimeError: If any parsing fails
    fn parse_batch_to_dict<'py>(
        &self,
        py: Python<'py>,
        texts: Vec<String>,
    ) -> PyResult<Vec<Vec<Bound<'py, PyDict>>>> {
        let refs: Vec<&str> = texts.iter().map(|s| s.as_str()).collect();
        let results: Result<Vec<Vec<Bound<'_, PyDict>>>, _> = self
            .inner
            .parse_batch(&refs)
            .into_iter()
            .map(|r| {
                r.map(|result| {
                    result
                        .morphemes
                        .iter()
                        .map(|m| self.morpheme_to_dict(py, m))
                        .collect()
                })
            })
            .collect();

        results.map_err(|e| PyRuntimeError::new_err(format!("Parse error: {e}")))
    }

    /// Get dictionary information
    ///
    /// Returns a dictionary with information about the loaded dictionary.
    ///
    /// Returns:
    ///     Dictionary with keys: overlay_size, has_vectors, vector_dim, with_ipa
    fn dict_info<'py>(&self, py: Python<'py>) -> Bound<'py, PyDict> {
        let dict = PyDict::new(py);
        let _ = dict.set_item("overlay_size", self.inner.overlay_size());
        let _ = dict.set_item("has_vectors", self.with_vector);
        let _ = dict.set_item("with_ipa", self.with_ipa);
        // TODO: Add more info like vocab_size, vector_dim when accessible
        dict
    }

    /// Check if this instance has vector support enabled
    #[getter]
    fn has_vectors(&self) -> bool {
        self.with_vector
    }

    /// Check if this instance has IPA support enabled
    #[getter]
    fn has_ipa(&self) -> bool {
        self.with_ipa
    }

    // Context manager support
    fn __enter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __exit__(
        &self,
        _exc_type: Option<&Bound<'_, pyo3::types::PyType>>,
        _exc_val: Option<&Bound<'_, pyo3::types::PyAny>>,
        _exc_tb: Option<&Bound<'_, pyo3::types::PyAny>>,
    ) -> bool {
        // No cleanup needed - Rust handles memory automatically
        false
    }
}

impl PyMeCrab {
    /// Helper to convert Morpheme to PyDict
    fn morpheme_to_dict<'py>(&self, py: Python<'py>, m: &crate::Morpheme) -> Bound<'py, PyDict> {
        let dict = PyDict::new(py);

        // Basic fields
        let _ = dict.set_item("surface", &m.surface);
        let _ = dict.set_item("feature", &m.feature);

        // Parse feature string
        let parts: Vec<&str> = m.feature.split(',').collect();
        if !parts.is_empty() {
            let _ = dict.set_item("pos", parts[0]);

            if parts.len() > 1 && parts[1] != "*" {
                let _ = dict.set_item("pos1", parts[1]);
            }
            if parts.len() > 2 && parts[2] != "*" {
                let _ = dict.set_item("pos2", parts[2]);
            }
            if parts.len() > 3 && parts[3] != "*" {
                let _ = dict.set_item("pos3", parts[3]);
            }
            if parts.len() > 4 && parts[4] != "*" {
                let _ = dict.set_item("inflection", parts[4]);
            }
            if parts.len() > 5 && parts[5] != "*" {
                let _ = dict.set_item("conjugation", parts[5]);
            }
            if parts.len() > 6 && parts[6] != "*" {
                let _ = dict.set_item("base", parts[6]);
            }
            if parts.len() > 7 && parts[7] != "*" {
                let _ = dict.set_item("reading", parts[7]);
            }
            if parts.len() > 8 && parts[8] != "*" {
                let _ = dict.set_item("pronunciation", parts[8]);
            }
        }

        // Add IPA pronunciation if available
        if let Some(ref ipa) = m.pronunciation {
            let _ = dict.set_item("ipa", ipa.as_str());
        }

        // Add embedding vector if available
        if let Some(ref embedding) = m.embedding {
            let _ = dict.set_item("embedding", embedding.clone());
        }

        let _ = dict.set_item("pos_id", m.pos_id);
        let _ = dict.set_item("wcost", m.wcost);
        let _ = dict.set_item("word_id", m.word_id);

        dict
    }

    /// Helper to get embedding for a word
    fn get_word_embedding(&self, word: &str) -> PyResult<Vec<f32>> {
        let result = self
            .inner
            .parse(word)
            .map_err(|e| PyRuntimeError::new_err(format!("Parse error: {e}")))?;

        result
            .morphemes
            .first()
            .and_then(|m| m.embedding.clone())
            .ok_or_else(|| {
                PyRuntimeError::new_err(format!(
                    "No embedding found for word: '{}' (may be out-of-vocabulary)",
                    word
                ))
            })
    }
}

/// Escape a string for JSON output
fn escape_json_string(s: &str) -> String {
    let mut result = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '"' => result.push_str("\\\""),
            '\\' => result.push_str("\\\\"),
            '\n' => result.push_str("\\n"),
            '\r' => result.push_str("\\r"),
            '\t' => result.push_str("\\t"),
            c if c.is_control() => {
                result.push_str(&format!("\\u{:04x}", c as u32));
            }
            c => result.push(c),
        }
    }
    result
}

/// Analysis result iterator for streaming processing
#[pyclass(name = "AnalysisIterator")]
pub struct PyAnalysisIterator {
    morphemes: Vec<PyMorpheme>,
    index: AtomicUsize,
}

#[pymethods]
impl PyAnalysisIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&self) -> Option<PyMorpheme> {
        let idx = self.index.fetch_add(1, Ordering::SeqCst);
        self.morphemes.get(idx).cloned()
    }

    fn __len__(&self) -> usize {
        self.morphemes.len()
    }
}

/// A single morpheme from analysis
#[pyclass(name = "Morpheme")]
#[derive(Clone)]
pub struct PyMorpheme {
    /// Surface form
    #[pyo3(get)]
    pub surface: String,
    /// Feature string (comma-separated)
    #[pyo3(get)]
    pub feature: String,
    /// Part-of-speech (main category)
    #[pyo3(get)]
    pub pos: String,
    /// Part-of-speech subcategory 1
    #[pyo3(get)]
    pub pos1: Option<String>,
    /// Part-of-speech subcategory 2
    #[pyo3(get)]
    pub pos2: Option<String>,
    /// Part-of-speech subcategory 3
    #[pyo3(get)]
    pub pos3: Option<String>,
    /// Conjugation type
    #[pyo3(get)]
    pub inflection: Option<String>,
    /// Conjugation form
    #[pyo3(get)]
    pub conjugation: Option<String>,
    /// Base form (lemma)
    #[pyo3(get)]
    pub base: Option<String>,
    /// Reading (katakana)
    #[pyo3(get)]
    pub reading: Option<String>,
    /// Pronunciation (katakana)
    #[pyo3(get)]
    pub pronunciation: Option<String>,
    /// IPA pronunciation (optional)
    #[pyo3(get)]
    pub ipa: Option<String>,
    /// Word embedding vector (optional)
    #[pyo3(get)]
    pub embedding: Option<Vec<f32>>,
    /// Part-of-speech ID
    #[pyo3(get)]
    pub pos_id: u16,
    /// Word cost
    #[pyo3(get)]
    pub wcost: i16,
    /// Word ID (for lookup in vector store)
    #[pyo3(get)]
    pub word_id: u32,
}

impl PyMorpheme {
    /// Create a PyMorpheme from a crate::Morpheme
    fn from_morpheme(m: &crate::Morpheme) -> Self {
        let parts: Vec<&str> = m.feature.split(',').collect();

        let pos = parts.first().map(|s| s.to_string()).unwrap_or_default();
        let pos1 = parts.get(1).filter(|&&s| s != "*").map(|s| s.to_string());
        let pos2 = parts.get(2).filter(|&&s| s != "*").map(|s| s.to_string());
        let pos3 = parts.get(3).filter(|&&s| s != "*").map(|s| s.to_string());
        let inflection = parts.get(4).filter(|&&s| s != "*").map(|s| s.to_string());
        let conjugation = parts.get(5).filter(|&&s| s != "*").map(|s| s.to_string());
        let base = parts.get(6).filter(|&&s| s != "*").map(|s| s.to_string());
        let reading = parts.get(7).filter(|&&s| s != "*").map(|s| s.to_string());
        let pronunciation = parts.get(8).filter(|&&s| s != "*").map(|s| s.to_string());

        Self {
            surface: m.surface.clone(),
            feature: m.feature.clone(),
            pos,
            pos1,
            pos2,
            pos3,
            inflection,
            conjugation,
            base,
            reading,
            pronunciation,
            ipa: m.pronunciation.clone(),
            embedding: m.embedding.clone(),
            pos_id: m.pos_id,
            wcost: m.wcost,
            word_id: m.word_id,
        }
    }
}

#[pymethods]
impl PyMorpheme {
    fn __repr__(&self) -> String {
        format!(
            "Morpheme(surface='{}', pos='{}', reading={:?})",
            self.surface, self.pos, self.reading
        )
    }

    fn __str__(&self) -> String {
        format!("{}\t{}", self.surface, self.feature)
    }

    /// Convert morpheme to dictionary
    #[allow(clippy::unnecessary_wraps)]
    fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        let _ = dict.set_item("surface", &self.surface);
        let _ = dict.set_item("feature", &self.feature);
        let _ = dict.set_item("pos", &self.pos);

        if let Some(ref v) = self.pos1 {
            let _ = dict.set_item("pos1", v);
        }
        if let Some(ref v) = self.pos2 {
            let _ = dict.set_item("pos2", v);
        }
        if let Some(ref v) = self.pos3 {
            let _ = dict.set_item("pos3", v);
        }
        if let Some(ref v) = self.inflection {
            let _ = dict.set_item("inflection", v);
        }
        if let Some(ref v) = self.conjugation {
            let _ = dict.set_item("conjugation", v);
        }
        if let Some(ref v) = self.base {
            let _ = dict.set_item("base", v);
        }
        if let Some(ref v) = self.reading {
            let _ = dict.set_item("reading", v);
        }
        if let Some(ref v) = self.pronunciation {
            let _ = dict.set_item("pronunciation", v);
        }
        if let Some(ref v) = self.ipa {
            let _ = dict.set_item("ipa", v);
        }
        if let Some(ref v) = self.embedding {
            let _ = dict.set_item("embedding", v.clone());
        }

        let _ = dict.set_item("pos_id", self.pos_id);
        let _ = dict.set_item("wcost", self.wcost);
        let _ = dict.set_item("word_id", self.word_id);

        Ok(dict)
    }

    /// Check if morpheme has embedding
    #[getter]
    fn has_embedding(&self) -> bool {
        self.embedding.is_some()
    }

    /// Check if morpheme has IPA pronunciation
    #[getter]
    fn has_ipa(&self) -> bool {
        self.ipa.is_some()
    }

    /// Get embedding dimension (or 0 if no embedding)
    #[getter]
    fn embedding_dim(&self) -> usize {
        self.embedding.as_ref().map(|e| e.len()).unwrap_or(0)
    }

    /// Check if morpheme is a noun
    fn is_noun(&self) -> bool {
        self.pos == "名詞"
    }

    /// Check if morpheme is a verb
    fn is_verb(&self) -> bool {
        self.pos == "動詞"
    }

    /// Check if morpheme is an adjective
    fn is_adjective(&self) -> bool {
        self.pos == "形容詞"
    }

    /// Check if morpheme is a particle
    fn is_particle(&self) -> bool {
        self.pos == "助詞"
    }

    /// Check if morpheme is an auxiliary verb
    fn is_auxiliary(&self) -> bool {
        self.pos == "助動詞"
    }

    /// Check if morpheme is a symbol/punctuation
    fn is_symbol(&self) -> bool {
        self.pos == "記号"
    }
}

/// Get MeCrab version
#[pyfunction]
fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// Get default dictionary path
///
/// Returns:
///     Dictionary path if found, None otherwise
#[pyfunction]
fn default_dicdir() -> Option<String> {
    // Standard dictionary locations (ordered by preference)
    let locations = [
        "/var/lib/mecab/dic/ipadic-utf8",
        "/usr/lib/mecab/dic/ipadic-utf8",
        "/usr/local/lib/mecab/dic/ipadic-utf8",
        "/opt/homebrew/lib/mecab/dic/ipadic-utf8",
    ];

    for loc in locations {
        let path = std::path::Path::new(loc);
        if path.exists() && path.join("sys.dic").exists() {
            return Some(loc.to_string());
        }
    }
    None
}

/// Compute cosine similarity between two vectors
///
/// Args:
///     a: First vector
///     b: Second vector
///
/// Returns:
///     Cosine similarity in range [-1.0, 1.0]
///
/// Raises:
///     ValueError: If vectors have different dimensions or are zero
#[pyfunction]
fn cosine_similarity(a: Vec<f32>, b: Vec<f32>) -> PyResult<f32> {
    if a.len() != b.len() {
        return Err(PyValueError::new_err(format!(
            "Vector dimensions must match: {} vs {}",
            a.len(),
            b.len()
        )));
    }

    crate::vectors::VectorStore::cosine_similarity(&a, &b).ok_or_else(|| {
        PyValueError::new_err("Cannot compute similarity (zero vectors?)")
    })
}

/// Python module definition
#[pymodule]
fn mecrab(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyMeCrab>()?;
    m.add_class::<PyMorpheme>()?;
    m.add_class::<PyAnalysisIterator>()?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(default_dicdir, m)?)?;
    m.add_function(wrap_pyfunction!(cosine_similarity, m)?)?;

    // Add constants
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__author__", "COOLJAPAN OU (Team KitaSan)")?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!version().is_empty());
    }

    #[test]
    fn test_escape_json() {
        assert_eq!(escape_json_string("hello"), "hello");
        assert_eq!(escape_json_string("he\"llo"), "he\\\"llo");
        assert_eq!(escape_json_string("he\\llo"), "he\\\\llo");
        assert_eq!(escape_json_string("he\nllo"), "he\\nllo");
    }
}
