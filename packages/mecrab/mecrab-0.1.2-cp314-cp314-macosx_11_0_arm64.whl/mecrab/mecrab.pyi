"""Type stubs for mecrab native module.

Copyright 2026 COOLJAPAN OU (Team KitaSan)
"""

from typing import Any, Dict, List, Optional, Tuple, Iterator

__version__: str
__author__: str

class MeCrab:
    """High-performance morphological analyzer compatible with MeCab.

    Features:
    - Fast morphological analysis with Viterbi algorithm
    - IPA (International Phonetic Alphabet) pronunciation
    - Word embeddings with cosine similarity
    - Live dictionary updates (hot-swappable)
    - Batch processing with parallel support
    - N-best path analysis
    - JSON/JSON-LD output
    - Context manager support
    """

    def __init__(
        self,
        dicdir: Optional[str] = None,
        with_ipa: bool = False,
        vector_path: Optional[str] = None,
    ) -> None:
        """Create a new MeCrab instance.

        Args:
            dicdir: Optional path to dictionary directory (auto-detected if not specified)
            with_ipa: Enable IPA pronunciation output (default: False)
            vector_path: Path to word embeddings file (vectors.bin) (optional)

        Raises:
            RuntimeError: If dictionary or vectors cannot be loaded

        Examples:
            >>> # Basic usage
            >>> m = MeCrab()

            >>> # With IPA pronunciation
            >>> m = MeCrab(with_ipa=True)

            >>> # With word embeddings
            >>> m = MeCrab(vector_path="vectors.bin")

            >>> # Combined IPA + vectors
            >>> m = MeCrab(with_ipa=True, vector_path="vectors.bin")
        """
        ...

    # Properties
    @property
    def has_vectors(self) -> bool:
        """Check if this instance has vector support enabled."""
        ...

    @property
    def has_ipa(self) -> bool:
        """Check if this instance has IPA support enabled."""
        ...

    # Basic parsing methods
    def parse(self, text: str) -> str:
        """Parse text and return analysis result in MeCab format.

        Args:
            text: Input text to analyze

        Returns:
            Analysis result as formatted string (MeCab format)

        Raises:
            RuntimeError: If parsing fails
        """
        ...

    def wakati(self, text: str) -> str:
        """Parse text and return wakati (space-separated) output.

        Args:
            text: Input text to analyze

        Returns:
            Space-separated surface forms

        Raises:
            RuntimeError: If parsing fails
        """
        ...

    def parse_to_list(self, text: str) -> List[Tuple[str, str]]:
        """Parse text and return list of morphemes as tuples.

        Args:
            text: Input text to analyze

        Returns:
            List of (surface, feature) tuples

        Raises:
            RuntimeError: If parsing fails
        """
        ...

    def parse_to_dict(self, text: str) -> List[Dict[str, Any]]:
        """Parse text and return list of dictionaries (Pythonic API).

        Returns structured morpheme information including optional fields
        (IPA pronunciation, word embeddings) when enabled.

        Args:
            text: Input text to analyze

        Returns:
            List of dictionaries with morpheme information. Each dict contains:
            - surface (str): Surface form
            - feature (str): Full feature string
            - pos (str): Part-of-speech
            - pos1 (str, optional): POS subcategory 1
            - pos2 (str, optional): POS subcategory 2
            - pos3 (str, optional): POS subcategory 3
            - inflection (str, optional): Inflection type
            - conjugation (str, optional): Conjugation form
            - base (str, optional): Base form
            - reading (str, optional): Reading (katakana)
            - pronunciation (str, optional): Pronunciation (katakana)
            - ipa (str, optional): IPA pronunciation (if with_ipa=True)
            - embedding (List[float], optional): Word embedding vector
            - pos_id (int): Part-of-speech ID
            - wcost (int): Word cost
            - word_id (int): Word ID for vector lookup

        Raises:
            RuntimeError: If parsing fails

        Examples:
            >>> m = MeCrab()
            >>> result = m.parse_to_dict("東京に行く")
            >>> for morph in result:
            ...     print(morph['surface'], morph['pos'])
            東京 名詞
            に 助詞
            行く 動詞
        """
        ...

    def parse_to_morphemes(self, text: str) -> List["Morpheme"]:
        """Parse text and return Morpheme objects.

        This provides a more Pythonic object-oriented interface compared to
        parse_to_dict(). Each Morpheme object has properties like surface,
        pos, reading, and helper methods like is_noun(), is_verb(), etc.

        Args:
            text: Input text to analyze

        Returns:
            List of Morpheme objects

        Raises:
            RuntimeError: If parsing fails

        Examples:
            >>> m = MeCrab()
            >>> morphemes = m.parse_to_morphemes("東京に行く")
            >>> for morph in morphemes:
            ...     if morph.is_noun():
            ...         print(f"Noun: {morph.surface} ({morph.reading})")
        """
        ...

    # N-best analysis
    def parse_nbest(
        self, text: str, n: int = 5
    ) -> List[Tuple[List[Dict[str, Any]], int]]:
        """Parse text and return N-best analysis results.

        Returns multiple alternative analyses ranked by cost, useful for
        disambiguation and exploring alternative segmentations.

        Args:
            text: Input text to analyze
            n: Number of best paths to return (default: 5)

        Returns:
            List of tuples (morphemes_as_dicts, cost) sorted by cost.
            Lower cost indicates more likely analysis.

        Raises:
            RuntimeError: If parsing fails

        Examples:
            >>> m = MeCrab()
            >>> results = m.parse_nbest("すもももももももものうち", n=3)
            >>> for morphemes, cost in results:
            ...     print(f"Cost: {cost}")
            ...     surfaces = [m['surface'] for m in morphemes]
            ...     print(f"  {' | '.join(surfaces)}")
        """
        ...

    # JSON output methods
    def parse_json(self, text: str) -> str:
        """Parse text and return JSON output.

        Returns a JSON array of morpheme objects.

        Args:
            text: Input text to analyze

        Returns:
            JSON string

        Raises:
            RuntimeError: If parsing fails

        Examples:
            >>> m = MeCrab()
            >>> import json
            >>> result = json.loads(m.parse_json("東京"))
            >>> print(result[0]['surface'])
            東京
        """
        ...

    def parse_jsonld(self, text: str) -> str:
        """Parse text and return JSON-LD output with semantic annotations.

        Returns a JSON-LD document with @context for linked data.

        Args:
            text: Input text to analyze

        Returns:
            JSON-LD string

        Raises:
            RuntimeError: If parsing fails
        """
        ...

    # Batch processing methods
    def parse_batch(self, texts: List[str]) -> List[str]:
        """Parse multiple texts in batch.

        When compiled with 'parallel' feature, this uses Rayon for
        parallel processing across all available CPU cores.

        Args:
            texts: List of texts to analyze

        Returns:
            List of analysis results as formatted strings

        Raises:
            RuntimeError: If any parsing fails
        """
        ...

    def wakati_batch(self, texts: List[str]) -> List[str]:
        """Parse multiple texts and return wakati outputs in batch.

        Args:
            texts: List of texts to analyze

        Returns:
            List of space-separated surface forms

        Raises:
            RuntimeError: If any parsing fails
        """
        ...

    def parse_batch_to_morphemes(self, texts: List[str]) -> List[List["Morpheme"]]:
        """Parse multiple texts and return Morpheme objects in batch.

        Args:
            texts: List of texts to analyze

        Returns:
            List of lists of Morpheme objects

        Raises:
            RuntimeError: If any parsing fails
        """
        ...

    def parse_batch_to_dict(self, texts: List[str]) -> List[List[Dict[str, Any]]]:
        """Parse multiple texts and return dictionaries in batch.

        Args:
            texts: List of texts to analyze

        Returns:
            List of lists of dictionaries

        Raises:
            RuntimeError: If any parsing fails
        """
        ...

    # Dictionary management (overlay dictionary)
    def add_word(
        self, surface: str, reading: str, pronunciation: str, wcost: int
    ) -> None:
        """Add a word to the overlay dictionary.

        This allows adding custom words (new product names, slang, etc.)
        that will be recognized during parsing. Changes take effect immediately.

        Args:
            surface: The surface form (the actual text)
            reading: The katakana reading
            pronunciation: The pronunciation (often same as reading)
            wcost: Word cost (lower = more preferred, typical: 5000-8000)

        Examples:
            >>> m = MeCrab()
            >>> m.add_word("ChatGPT", "チャットジーピーティー", "チャットジーピーティー", 5000)
            >>> "ChatGPT" in m.wakati("ChatGPTを使う")
            True
        """
        ...

    def remove_word(self, surface: str) -> bool:
        """Remove a word from the overlay dictionary.

        Note: Only overlay words can be removed. System dictionary entries persist.

        Args:
            surface: The surface form to remove

        Returns:
            True if the word was found and removed, False otherwise
        """
        ...

    def overlay_size(self) -> int:
        """Get the number of words in the overlay dictionary.

        Returns:
            Number of custom words added via add_word()
        """
        ...

    def dict_info(self) -> Dict[str, Any]:
        """Get dictionary information.

        Returns:
            Dictionary with keys:
            - overlay_size (int): Number of overlay words
            - has_vectors (bool): Whether vectors are loaded
            - with_ipa (bool): Whether IPA is enabled
        """
        ...

    # IPA pronunciation methods
    def to_ipa(self, text: str) -> List[str]:
        """Convert text to IPA pronunciation (one-shot conversion).

        Requires: MeCrab initialized with with_ipa=True

        Args:
            text: Input text to convert

        Returns:
            List of IPA pronunciation strings (one per morpheme)

        Raises:
            RuntimeError: If IPA is not enabled or parsing fails

        Examples:
            >>> m = MeCrab(with_ipa=True)
            >>> ipas = m.to_ipa("東京に行く")
            >>> print(ipas)
            ['toːkʲoː', 'ɲi', 'ikɯ']
        """
        ...

    def to_ipa_text(self, text: str, separator: str = " ") -> str:
        """Convert text to IPA pronunciation as a single string.

        Requires: MeCrab initialized with with_ipa=True

        Args:
            text: Input text to convert
            separator: Separator between morphemes (default: " ")

        Returns:
            IPA pronunciation string

        Raises:
            RuntimeError: If IPA is not enabled or parsing fails

        Examples:
            >>> m = MeCrab(with_ipa=True)
            >>> print(m.to_ipa_text("東京に行く"))
            'toːkʲoː ɲi ikɯ'
            >>> print(m.to_ipa_text("東京に行く", separator="-"))
            'toːkʲoː-ɲi-ikɯ'
        """
        ...

    # Word embedding methods
    def similarity(self, word1: str, word2: str) -> float:
        """Compute cosine similarity between two words.

        Requires: MeCrab initialized with vector_path parameter

        Args:
            word1: First word
            word2: Second word

        Returns:
            Cosine similarity in range [-1.0, 1.0]

        Raises:
            RuntimeError: If vectors not enabled or words not found

        Examples:
            >>> m = MeCrab(vector_path="vectors.bin")
            >>> sim = m.similarity("東京", "京都")
            >>> print(f"Similarity: {sim:.3f}")
        """
        ...

    def most_similar(
        self, word: str, topn: int = 10
    ) -> List[Tuple[str, float]]:
        """Find words most similar to the given word.

        Note: This method requires vocabulary iteration, which is not yet
        fully implemented. Use similarity() for pairwise comparison instead.

        Args:
            word: The query word
            topn: Number of similar words to return (default: 10)

        Returns:
            List of (word, similarity_score) tuples

        Raises:
            RuntimeError: If vectors not enabled or not implemented
        """
        ...

    def analogy(
        self,
        positive1: str,
        negative: str,
        positive2: str,
        topn: int = 5,
    ) -> List[Tuple[str, float]]:
        """Perform word analogy: a - b + c = ?

        Classic word2vec analogy: king - man + woman = queen

        Note: This method requires vocabulary iteration, which is not yet
        fully implemented.

        Args:
            positive1: First positive word (e.g., "king")
            negative: Negative word to subtract (e.g., "man")
            positive2: Second positive word to add (e.g., "woman")
            topn: Number of results to return (default: 5)

        Returns:
            List of (word, similarity_score) tuples

        Raises:
            RuntimeError: If vectors not enabled or not implemented
        """
        ...

    def sentence_embedding(self, text: str) -> List[float]:
        """Get sentence embedding (mean pooling of word vectors).

        Computes the average of all word vectors in the sentence.

        Requires: MeCrab initialized with vector_path parameter

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats

        Raises:
            RuntimeError: If vectors not enabled or no words have embeddings

        Examples:
            >>> m = MeCrab(vector_path="vectors.bin")
            >>> emb = m.sentence_embedding("東京に行く")
            >>> print(f"Dimension: {len(emb)}")
        """
        ...

    # Context manager protocol
    def __enter__(self) -> "MeCrab":
        """Enter context manager."""
        ...

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        """Exit context manager."""
        ...


class Morpheme:
    """A single morpheme from analysis.

    Provides structured access to morphological information with
    helper methods for common POS checks.
    """

    # Basic properties
    surface: str
    """Surface form (the actual text)"""

    feature: str
    """Full feature string (comma-separated)"""

    pos: str
    """Part-of-speech (main category, e.g., '名詞', '動詞')"""

    pos1: Optional[str]
    """POS subcategory 1"""

    pos2: Optional[str]
    """POS subcategory 2"""

    pos3: Optional[str]
    """POS subcategory 3"""

    inflection: Optional[str]
    """Conjugation type (e.g., '五段・カ行イ音便')"""

    conjugation: Optional[str]
    """Conjugation form (e.g., '基本形', '連用形')"""

    base: Optional[str]
    """Base form / lemma"""

    reading: Optional[str]
    """Reading in katakana"""

    pronunciation: Optional[str]
    """Pronunciation in katakana"""

    ipa: Optional[str]
    """IPA pronunciation (if enabled)"""

    embedding: Optional[List[float]]
    """Word embedding vector (if enabled)"""

    pos_id: int
    """Part-of-speech ID"""

    wcost: int
    """Word cost"""

    word_id: int
    """Word ID for vector lookup"""

    # Computed properties
    @property
    def has_embedding(self) -> bool:
        """Check if morpheme has an embedding vector."""
        ...

    @property
    def has_ipa(self) -> bool:
        """Check if morpheme has IPA pronunciation."""
        ...

    @property
    def embedding_dim(self) -> int:
        """Get embedding dimension (0 if no embedding)."""
        ...

    # POS helper methods
    def is_noun(self) -> bool:
        """Check if morpheme is a noun (名詞)."""
        ...

    def is_verb(self) -> bool:
        """Check if morpheme is a verb (動詞)."""
        ...

    def is_adjective(self) -> bool:
        """Check if morpheme is an adjective (形容詞)."""
        ...

    def is_particle(self) -> bool:
        """Check if morpheme is a particle (助詞)."""
        ...

    def is_auxiliary(self) -> bool:
        """Check if morpheme is an auxiliary verb (助動詞)."""
        ...

    def is_symbol(self) -> bool:
        """Check if morpheme is a symbol/punctuation (記号)."""
        ...

    # Conversion methods
    def to_dict(self) -> Dict[str, Any]:
        """Convert morpheme to dictionary."""
        ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class AnalysisIterator:
    """Iterator for streaming morpheme processing."""

    def __iter__(self) -> "AnalysisIterator": ...
    def __next__(self) -> Morpheme: ...
    def __len__(self) -> int: ...


# Module-level functions
def version() -> str:
    """Get MeCrab version.

    Returns:
        Version string (e.g., "0.2.0")
    """
    ...


def default_dicdir() -> Optional[str]:
    """Get default dictionary path.

    Returns:
        Dictionary path if found, None otherwise

    Examples:
        >>> import mecrab
        >>> dicdir = mecrab.default_dicdir()
        >>> if dicdir:
        ...     print(f"Dictionary at: {dicdir}")
    """
    ...


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        a: First vector
        b: Second vector

    Returns:
        Cosine similarity in range [-1.0, 1.0]

    Raises:
        ValueError: If vectors have different dimensions or are zero

    Examples:
        >>> import mecrab
        >>> a = [1.0, 0.0, 0.0]
        >>> b = [1.0, 0.0, 0.0]
        >>> mecrab.cosine_similarity(a, b)
        1.0
    """
    ...
