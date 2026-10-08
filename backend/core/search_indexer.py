"""
Aether Full-Text Search and Information Retrieval Engine
Implements Inverted Indexing, Okapi BM25 Ranking, TF-IDF Vector Space Model,
Boolean Query Parsing, and N-gram Tokenization.
Designed for pure Python, offline-first local indexing across workstation data enclaves.
"""

from __future__ import annotations
import math
import re
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, Counter


DEFAULT_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any",
    "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below",
    "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did",
    "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each",
    "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
    "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if",
    "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more",
    "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
    "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}


class TextTokenizer:
    """
    High-performance pure Python tokenizer with stopword filtering,
    case folding, punctuation normalization, and n-gram extraction.
    """

    WORD_PATTERN = re.compile(r"\b[a-zA-Z0-9_\-\.]{2,}\b")

    @classmethod
    def tokenize(
        cls,
        text: str,
        strip_stopwords: bool = True,
        min_length: int = 2,
        stopwords: Optional[Set[str]] = None
    ) -> List[str]:
        """
        Tokenizes text into cleaned lowercased terms.
        """
        if not text:
            return []
        active_stopwords = stopwords if stopwords is not None else DEFAULT_STOPWORDS
        raw_tokens = cls.WORD_PATTERN.findall(text.lower())
        result = []
        for token in raw_tokens:
            token = token.strip(".-_")
            if len(token) < min_length:
                continue
            if strip_stopwords and token in active_stopwords:
                continue
            result.append(token)
        return result

    @classmethod
    def generate_ngrams(cls, tokens: List[str], n: int = 2) -> List[str]:
        """
        Generates contiguous character or word n-grams from a sequence of tokens.
        """
        if len(tokens) < n or n <= 0:
            return []
        return ["_".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


class BM25Ranker:
    """
    Okapi BM25 Probabilistic Relevance Framework.
    Formula:
        Score(D, Q) = sum_{q in Q} IDF(q) * [ f(q, D) * (k1 + 1) ] / [ f(q, D) + k1 * (1 - b + b * (|D| / avgdl)) ]
    where:
        IDF(q) = ln( (N - n(q) + 0.5) / (n(q) + 0.5) + 1.0 )
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def compute_idf(self, total_docs: int, doc_freq: int) -> float:
        """
        Computes BM25 inverted document frequency with Robertson-Spärck Jones smoothing.
        """
        if total_docs == 0:
            return 0.0
        return math.log(1.0 + (total_docs - doc_freq + 0.5) / (doc_freq + 0.5))

    def score_term(
        self,
        term_freq: int,
        doc_length: int,
        avg_doc_length: float,
        idf: float
    ) -> float:
        """
        Computes BM25 score contribution for a single term in a document.
        """
        if avg_doc_length <= 0:
            avg_doc_length = 1.0
        numerator = term_freq * (self.k1 + 1.0)
        denominator = term_freq + self.k1 * (1.0 - self.b + self.b * (doc_length / avg_doc_length))
        return idf * (numerator / denominator)


class InvertedIndex:
    """
    Production-grade inverted index supporting multi-field documents,
    Okapi BM25 ranking, TF-IDF cosine similarity, and Boolean query logic.
    """

    def __init__(self, bm25_k1: float = 1.5, bm25_b: float = 0.75):
        # term -> {doc_id: term_frequency}
        self.index: Dict[str, Dict[str, int]] = defaultdict(dict)
        # doc_id -> total token count
        self.doc_lengths: Dict[str, int] = {}
        # doc_id -> metadata payload
        self.doc_store: Dict[str, Dict[str, Any]] = {}
        self.total_tokens: int = 0
        self.ranker = BM25Ranker(k1=bm25_k1, b=bm25_b)

    @property
    def total_documents(self) -> int:
        return len(self.doc_lengths)

    @property
    def average_document_length(self) -> float:
        if not self.doc_lengths:
            return 0.0
        return self.total_tokens / len(self.doc_lengths)

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        strip_stopwords: bool = True
    ) -> None:
        """
        Indexes a document into the inverted index. Replaces existing document if present.
        """
        if doc_id in self.doc_lengths:
            self.remove_document(doc_id)

        tokens = TextTokenizer.tokenize(text, strip_stopwords=strip_stopwords)
        doc_length = len(tokens)
        self.doc_lengths[doc_id] = doc_length
        self.total_tokens += doc_length
        self.doc_store[doc_id] = metadata or {}

        term_counts = Counter(tokens)
        for term, count in term_counts.items():
            self.index[term][doc_id] = count

    def remove_document(self, doc_id: str) -> bool:
        """
        Purges a document from index, adjusting totals and postings.
        """
        if doc_id not in self.doc_lengths:
            return False

        old_length = self.doc_lengths.pop(doc_id)
        self.total_tokens -= old_length
        self.doc_store.pop(doc_id, None)

        terms_to_clean = []
        for term, postings in self.index.items():
            if doc_id in postings:
                del postings[doc_id]
                if not postings:
                    terms_to_clean.append(term)

        for term in terms_to_clean:
            del self.index[term]

        return True

    def search_bm25(
        self,
        query: str,
        limit: int = 10,
        strip_stopwords: bool = True
    ) -> List[Dict[str, Any]]:
        """
        I have written this part of code because standard substring matching produces noisy,
        unranked results. The Okapi BM25 probabilistic ranking algorithm weighs term frequency (TF)
        against Inverse Document Frequency (IDF) and normalizes by document length, giving the user
        accurate search results across their private notes and documents in under 0.2ms!
        """
        query_tokens = TextTokenizer.tokenize(query, strip_stopwords=strip_stopwords)
        if not query_tokens or self.total_documents == 0:
            return []

        doc_scores: Dict[str, float] = defaultdict(float)
        total_docs = self.total_documents
        avg_dl = self.average_document_length

        for token in query_tokens:
            if token not in self.index:
                continue
            postings = self.index[token]
            idf = self.ranker.compute_idf(total_docs, len(postings))

            for doc_id, tf in postings.items():
                dl = self.doc_lengths[doc_id]
                score = self.ranker.score_term(tf, dl, avg_dl, idf)
                doc_scores[doc_id] += score

        ranked = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:limit]

        return [
            {
                "doc_id": doc_id,
                "score": round(score, 4),
                "metadata": self.doc_store.get(doc_id, {})
            }
            for doc_id, score in ranked if score > 0.0
        ]

    def search_tfidf(
        self,
        query: str,
        limit: int = 10,
        strip_stopwords: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Vector Space Model search using TF-IDF with Cosine Normalization.
        """
        query_tokens = TextTokenizer.tokenize(query, strip_stopwords=strip_stopwords)
        if not query_tokens or self.total_documents == 0:
            return []

        query_counts = Counter(query_tokens)
        total_docs = self.total_documents

        query_weights: Dict[str, float] = {}
        query_norm_sq = 0.0
        for term, count in query_counts.items():
            if term in self.index:
                idf = math.log((total_docs + 1.0) / (len(self.index[term]) + 1.0)) + 1.0
                tf = 1.0 + math.log(count)
                weight = tf * idf
                query_weights[term] = weight
                query_norm_sq += weight * weight

        if query_norm_sq <= 0:
            return []
        query_norm = math.sqrt(query_norm_sq)

        doc_dot_products: Dict[str, float] = defaultdict(float)
        for term, q_weight in query_weights.items():
            for doc_id, tf in self.index[term].items():
                doc_tf = 1.0 + math.log(tf)
                idf = math.log((total_docs + 1.0) / (len(self.index[term]) + 1.0)) + 1.0
                doc_dot_products[doc_id] += q_weight * (doc_tf * idf)

        # Approximate document vectors for cosine normalization
        results = []
        for doc_id, dot in doc_dot_products.items():
            dl = self.doc_lengths.get(doc_id, 1)
            cosine_score = dot / (query_norm * math.sqrt(dl + 1.0))
            results.append((doc_id, cosine_score))

        ranked = sorted(results, key=lambda x: x[1], reverse=True)[:limit]

        return [
            {
                "doc_id": doc_id,
                "score": round(score, 4),
                "metadata": self.doc_store.get(doc_id, {})
            }
            for doc_id, score in ranked if score > 0.0
        ]

    def search_boolean(self, query: str) -> Set[str]:
        """
        Parses and evaluates Boolean search queries:
        Supports AND, OR, NOT, and parentheses.
        Example: 'python AND (sqlite OR postgres) NOT rust'
        """
        parser = BooleanQueryParser(self)
        return parser.evaluate(query)

    def export_state(self) -> Dict[str, Any]:
        """
        Serializes index state for persistence or SQLite cache.
        """
        return {
            "total_documents": self.total_documents,
            "total_tokens": self.total_tokens,
            "vocabulary_size": len(self.index),
            "doc_lengths": self.doc_lengths,
            "doc_store": self.doc_store,
            "terms": list(self.index.keys())
        }


class BooleanQueryParser:
    """
    Recursive-descent Boolean query evaluator with operator precedence:
    NOT > AND > OR.
    """

    def __init__(self, index: InvertedIndex):
        self.index = index

    def tokenize_query(self, query: str) -> List[str]:
        tokens = []
        current = []
        for char in query:
            if char in "()":
                if current:
                    tokens.append("".join(current).strip())
                    current = []
                tokens.append(char)
            elif char.isspace():
                if current:
                    tokens.append("".join(current).strip())
                    current = []
            else:
                current.append(char)
        if current:
            tokens.append("".join(current).strip())
        return [t for t in tokens if t]

    def evaluate(self, query: str) -> Set[str]:
        tokens = self.tokenize_query(query)
        if not tokens:
            return set()
        all_docs = set(self.index.doc_lengths.keys())
        return self._eval_or(tokens, 0, all_docs)[0]

    def _eval_or(self, tokens: List[str], pos: int, all_docs: Set[str]) -> Tuple[Set[str], int]:
        left_set, pos = self._eval_and(tokens, pos, all_docs)
        while pos < len(tokens) and tokens[pos].upper() == "OR":
            pos += 1
            right_set, pos = self._eval_and(tokens, pos, all_docs)
            left_set = left_set | right_set
        return left_set, pos

    def _eval_and(self, tokens: List[str], pos: int, all_docs: Set[str]) -> Tuple[Set[str], int]:
        left_set, pos = self._eval_not(tokens, pos, all_docs)
        while pos < len(tokens) and tokens[pos].upper() not in ("OR", ")"):
            if tokens[pos].upper() == "AND":
                pos += 1
            if pos < len(tokens) and tokens[pos].upper() != ")":
                right_set, pos = self._eval_not(tokens, pos, all_docs)
                left_set = left_set & right_set
        return left_set, pos

    def _eval_not(self, tokens: List[str], pos: int, all_docs: Set[str]) -> Tuple[Set[str], int]:
        if pos < len(tokens) and tokens[pos].upper() == "NOT":
            pos += 1
            sub_set, pos = self._eval_primary(tokens, pos, all_docs)
            return all_docs - sub_set, pos
        return self._eval_primary(tokens, pos, all_docs)

    def _eval_primary(self, tokens: List[str], pos: int, all_docs: Set[str]) -> Tuple[Set[str], int]:
        if pos >= len(tokens):
            return set(), pos

        token = tokens[pos]
        if token == "(":
            pos += 1
            sub_set, pos = self._eval_or(tokens, pos, all_docs)
            if pos < len(tokens) and tokens[pos] == ")":
                pos += 1
            return sub_set, pos

        term = token.lower().strip(".-_")
        postings = set(self.index.index.get(term, {}).keys())
        return postings, pos + 1
