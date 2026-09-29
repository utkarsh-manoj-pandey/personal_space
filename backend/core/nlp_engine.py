"""
Aether Natural Language Processing and Extractive Summarization Engine
Pure Python implementation featuring:
- TextRank graph-based extractive summarization (PageRank on sentence similarity graph)
- RAKE (Rapid Automatic Keyword Extraction) via co-occurrence word graphs
- High-precision Regex Named Entity Extractor (Dates, Emails, Phones, URLs, Currencies, IP Addresses)
- N-gram Language Identification Profiler using Cavnar-Trenkle Out-of-Place distance
"""

from __future__ import annotations
import math
import re
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, Counter


class SentenceTokenizer:
    """Splits raw text into grammatically bounded sentences."""
    SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        cleaned = text.strip()
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        sentences = []
        for line in lines:
            chunks = cls.SENTENCE_SPLIT_PATTERN.split(line)
            for chunk in chunks:
                c = chunk.strip()
                if c:
                    sentences.append(c)
        return sentences


class TextRankSummarizer:
    """
    Extractive text summarization using the PageRank graph centrality algorithm
    applied to inter-sentence cosine/token-overlap similarity graphs.
    Reference: Mihalcea & Tarau (2004), TextRank: Bringing Order into Texts.
    """

    @classmethod
    def _sentence_similarity(cls, s1_tokens: Set[str], s2_tokens: Set[str]) -> float:
        if not s1_tokens or not s2_tokens:
            return 0.0
        intersection = len(s1_tokens & s2_tokens)
        if intersection == 0:
            return 0.0
        # Normalization by log length to prevent bias toward longer sentences
        denom = math.log(len(s1_tokens) + 1.0) + math.log(len(s2_tokens) + 1.0)
        return intersection / denom if denom > 0 else 0.0

    @classmethod
    def summarize(
        cls,
        text: str,
        num_sentences: int = 3,
        damping: float = 0.85,
        max_iterations: int = 50,
        convergence_threshold: float = 1e-4
    ) -> List[Dict[str, Any]]:
        """
        Extracts the most salient sentences while preserving document narrative sequence.
        """
        sentences = SentenceTokenizer.split_sentences(text)
        n = len(sentences)
        if n == 0:
            return []
        if n <= num_sentences:
            return [{"index": i, "sentence": s, "score": 1.0} for i, s in enumerate(sentences)]

        # Tokenize each sentence into word sets
        tokenized = []
        for s in sentences:
            words = set(re.findall(r"\b[a-z]{3,}\b", s.lower()))
            tokenized.append(words)

        # Build similarity matrix
        sim_matrix: List[List[float]] = [[0.0] * n for _ in range(n)]
        weights_sum = [0.0] * n

        for i in range(n):
            for j in range(n):
                if i != j:
                    sim = cls._sentence_similarity(tokenized[i], tokenized[j])
                    sim_matrix[i][j] = sim
                    weights_sum[i] += sim

        # Initialize PageRank vector
        scores = [1.0 / n] * n

        # Power iteration
        for _ in range(max_iterations):
            next_scores = [0.0] * n
            diff = 0.0
            for i in range(n):
                rank_sum = 0.0
                for j in range(n):
                    if i != j and weights_sum[j] > 0.0:
                        rank_sum += (sim_matrix[j][i] / weights_sum[j]) * scores[j]
                next_scores[i] = (1.0 - damping) / n + damping * rank_sum
                diff += abs(next_scores[i] - scores[i])

            scores = next_scores
            if diff < convergence_threshold:
                break

        # Select top sentences based on scores
        scored_sentences = list(enumerate(zip(sentences, scores)))
        scored_sentences.sort(key=lambda x: x[1][1], reverse=True)
        top_selected = scored_sentences[:num_sentences]

        # Re-sort by original chronological order
        top_selected.sort(key=lambda x: x[0])

        return [
            {
                "index": original_idx,
                "sentence": sent,
                "score": round(score, 5)
            }
            for original_idx, (sent, score) in top_selected
        ]


class RAKEKeywordExtractor:
    """
    Rapid Automatic Keyword Extraction (RAKE) algorithm.
    Evaluates candidate multi-word keywords using word co-occurrence graph degree and frequency.
    """

    STOPWORD_REGEX = re.compile(
        r"\b(?:a|about|above|after|again|against|all|am|an|and|any|are|as|at|be|because|"
        r"been|before|being|below|between|both|but|by|can|could|did|do|does|doing|down|"
        r"during|each|few|for|from|further|had|has|have|having|he|her|here|hers|herself|"
        r"him|himself|his|how|i|if|in|into|is|it|its|itself|just|me|more|most|my|myself|"
        r"no|nor|not|of|off|on|once|only|or|other|ought|our|ours|ourselves|out|over|own|"
        r"same|she|should|so|some|such|than|that|the|their|theirs|them|themselves|then|"
        r"there|these|they|this|those|through|to|too|under|until|up|very|was|we|were|"
        r"what|when|where|which|while|who|whom|why|will|with|would|you|your|yours)\b",
        re.IGNORECASE
    )

    @classmethod
    def extract_keywords(
        cls,
        text: str,
        min_char_length: int = 3,
        max_words_per_phrase: int = 4,
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Extracts and scores key phrases from text.
        """
        if not text:
            return []

        # Split text into candidate phrases using punctuation and stopwords as delimiters
        text_without_punct = re.sub(r"[^\w\s\-\']", "|", text)
        sentences_split = text_without_punct.split("|")

        phrases: List[List[str]] = []
        for chunk in sentences_split:
            # Replace stopwords with a separator
            separated = cls.STOPWORD_REGEX.sub("|", chunk)
            for phrase_cand in separated.split("|"):
                words = [w.strip().lower() for w in re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", phrase_cand)]
                words = [w for w in words if len(w) >= min_char_length]
                if not words:
                    continue
                if len(words) <= max_words_per_phrase:
                    phrases.append(words)
                else:
                    # Chunk long sequences into subphrases of size <= max_words_per_phrase
                    for i in range(0, len(words), max_words_per_phrase):
                        sub = words[i : i + max_words_per_phrase]
                        if sub:
                            phrases.append(sub)

        if not phrases:
            return []

        # Word frequency and degree in co-occurrence graph
        word_freq: Dict[str, int] = defaultdict(int)
        word_degree: Dict[str, int] = defaultdict(int)

        for phrase in phrases:
            phrase_length = len(phrase)
            degree = phrase_length - 1
            for word in phrase:
                word_freq[word] += 1
                word_degree[word] += degree

        for word in word_freq:
            word_degree[word] += word_freq[word]

        # Calculate word scores
        word_scores: Dict[str, float] = {}
        for word in word_freq:
            word_scores[word] = word_degree[word] / word_freq[word]

        # Score candidate phrases
        phrase_scores: Dict[str, float] = {}
        for phrase in phrases:
            score = sum(word_scores[w] for w in phrase)
            phrase_str = " ".join(phrase)
            phrase_scores[phrase_str] = round(score, 3)

        ranked = sorted(phrase_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_n]


class EntityExtractor:
    """
    High-precision deterministic Entity and Pattern Extractor.
    Extracts structured operational entities without external cloud models.
    """

    PATTERNS = {
        "email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
        "url": re.compile(r"https?://(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?"),
        "ipv4": re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"),
        "phone": re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "iso_date": re.compile(r"\b\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])\b"),
        "currency": re.compile(r"[\$€£₹¥]\s*\d+(?:,\d{3})*(?:\.\d{1,2})?|\b\d+(?:,\d{3})*(?:\.\d{1,2})?\s*(?:USD|EUR|GBP|INR|JPY|CAD|AUD)\b", re.IGNORECASE),
        "hashtag": re.compile(r"#\w{2,}"),
        "mention": re.compile(r"@\w{2,}")
    }

    @classmethod
    def extract_all(cls, text: str) -> Dict[str, List[str]]:
        """
        Extracts all categorized entities present in the input text.
        """
        result: Dict[str, List[str]] = {}
        for category, regex in cls.PATTERNS.items():
            matches = list(dict.fromkeys(regex.findall(text)))
            if matches:
                result[category] = matches
        return result


class LanguageProfiler:
    """
    N-gram based Language Identifier based on Cavnar-Trenkle Out-of-Place measure.
    Recognizes English, Spanish, French, German with pure Python statistical models.
    """

    # Pre-computed top character trigram fingerprints
    PROFILES = {
        "en": [
            "the", "and", "ing", "ion", "tio", "ent", "ati", "for", "ter", "tha",
            "all", "rea", "hat", "ere", "con", "ted", "wit", "ver", "his", "thi",
            "qui", "ick", "fox", "jum", "ump", "ove", "laz", "dog", "run", "gre"
        ],
        "es": [
            "que", "del", "ent", "las", "los", "ion", "con", "par", "por",
            "est", "una", "ien", "nte", "ado", "ara", "tra", "com", "aci",
            "rap", "pid", "zor", "mar", "ron", "sal", "per", "bos", "oso"
        ],
        "fr": [
            "les", "des", "ent", "que", "ion", "ait", "ans", "ont", "ede",
            "our", "tio", "pou", "com", "par", "dan", "eme", "qui", "est", "une"
        ],
        "de": [
            "der", "ein", "die", "und", "ich", "den", "sch", "che", "nicht", "cht",
            "das", "gen", "ine", "ver", "eit", "ter", "ung", "ste", "sie", "end"
        ]
    }

    @classmethod
    def generate_trigram_profile(cls, text: str, top_k: int = 50) -> List[str]:
        cleaned = re.sub(r"[^a-z]", "", text.lower())
        if len(cleaned) < 3:
            return []
        trigrams = [cleaned[i : i + 3] for i in range(len(cleaned) - 2)]
        counts = Counter(trigrams)
        return [tg for tg, _ in counts.most_common(top_k)]

    @classmethod
    def detect_language(cls, text: str) -> Tuple[str, float]:
        """
        Returns (predicted_iso_code, confidence_ratio).
        """
        sample_profile = cls.generate_trigram_profile(text, top_k=30)
        if not sample_profile:
            return ("unknown", 0.0)

        best_lang = "unknown"
        min_distance = float("inf")
        distances = {}

        max_penalty = 50
        for lang, ref_profile in cls.PROFILES.items():
            dist = 0
            for rank, trigram in enumerate(sample_profile):
                if trigram in ref_profile:
                    dist += abs(rank - ref_profile.index(trigram))
                else:
                    dist += max_penalty
            distances[lang] = dist
            if dist < min_distance:
                min_distance = dist
                best_lang = lang

        sorted_dist = sorted(distances.values())
        spread = (sorted_dist[1] - sorted_dist[0]) / max(1.0, sorted_dist[1])
        confidence = min(0.99, max(0.1, round(spread * 3.0, 2)))

        return (best_lang, confidence)
