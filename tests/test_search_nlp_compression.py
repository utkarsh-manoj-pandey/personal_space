"""
Unit tests for Aether Search Indexer, Natural Language Processing, and Compression Engines.
Pure Python deterministic verification.
"""

import pytest
from backend.core.search_indexer import TextTokenizer, BM25Ranker, InvertedIndex
from backend.core.nlp_engine import (
    SentenceTokenizer,
    TextRankSummarizer,
    RAKEKeywordExtractor,
    EntityExtractor,
    LanguageProfiler
)
from backend.core.compression import (
    ShannonEntropy,
    RunLengthEncoding,
    HuffmanCoder,
    LZWCompressor,
    CompressionBenchmark
)


def test_text_tokenizer_and_ngrams():
    text = "The quick brown fox jumps over the lazy dog."
    tokens = TextTokenizer.tokenize(text, strip_stopwords=True)
    assert "quick" in tokens
    assert "brown" in tokens
    assert "fox" in tokens
    assert "the" not in tokens  # Stopword removed

    # Bigrams
    bigrams = TextTokenizer.generate_ngrams(tokens, n=2)
    assert len(bigrams) == len(tokens) - 1
    assert bigrams[0] == f"{tokens[0]}_{tokens[1]}"


def test_inverted_index_bm25_and_tfidf():
    index = InvertedIndex()
    index.add_document("doc1", "Python is an elegant and powerful programming language.")
    index.add_document("doc2", "SQLite is an offline-first embedded relational database.")
    index.add_document("doc3", "Python and SQLite combined create high-performance local workstations.")

    assert index.total_documents == 3

    # BM25 Search
    bm25_res = index.search_bm25("Python database")
    assert len(bm25_res) > 0
    # doc3 has both Python and database, so it should rank first or high
    doc_ids = [r["doc_id"] for r in bm25_res]
    assert "doc3" in doc_ids

    # TF-IDF Search
    tfidf_res = index.search_tfidf("programming")
    assert len(tfidf_res) > 0
    assert tfidf_res[0]["doc_id"] == "doc1"

    # Document removal
    assert index.remove_document("doc2") is True
    assert index.total_documents == 2
    assert index.search_bm25("relational") == []


def test_boolean_query_parser():
    index = InvertedIndex()
    index.add_document("d1", "alpha beta gamma")
    index.add_document("d2", "alpha gamma delta")
    index.add_document("d3", "beta epsilon")

    res_and = index.search_boolean("alpha AND gamma")
    assert res_and == {"d1", "d2"}

    res_or = index.search_boolean("delta OR epsilon")
    assert res_or == {"d2", "d3"}

    res_not = index.search_boolean("alpha NOT beta")
    assert res_not == {"d2"}


def test_textrank_summarization():
    text = (
        "Antigravity is an offline-first personal workstation. "
        "It features 17 isolated SQLite databases running in WAL mode. "
        "The architecture communicates via deterministic PySide6 QWebChannel slots. "
        "No cloud telemetry or external network ports are opened during operation. "
        "Aether guarantees mathematical precision and cryptographic sovereignty."
    )
    summary = TextRankSummarizer.summarize(text, num_sentences=2)
    assert len(summary) == 2
    assert summary[0]["index"] < summary[1]["index"]
    assert "sentence" in summary[0]
    assert summary[0]["score"] > 0.0


def test_rake_keyword_extraction():
    text = (
        "Linear regression models optimize ordinary least squares calculations. "
        "Deterministic graph algorithms calculate shortest paths efficiently."
    )
    keywords = RAKEKeywordExtractor.extract_keywords(text, top_n=5)
    assert len(keywords) > 0
    phrase_names = [k[0] for k in keywords]
    assert any("linear regression" in p or "least squares" in p or "graph algorithms" in p for p in phrase_names)


def test_entity_extractor():
    text = (
        "Contact operator at admin@aether.lan or visit https://aether.internal. "
        "Gateway node IP is 192.168.1.100. Call +1-555-019-2834 on 2026-09-30. "
        "Total budget is $45,000 for #sovereign tech."
    )
    entities = EntityExtractor.extract_all(text)
    assert "email" in entities and "admin@aether.lan" in entities["email"]
    assert "url" in entities and "https://aether.internal" in entities["url"]
    assert "ipv4" in entities and "192.168.1.100" in entities["ipv4"]
    assert "iso_date" in entities and "2026-09-30" in entities["iso_date"]
    assert "hashtag" in entities and "#sovereign" in entities["hashtag"]


def test_language_profiler():
    en_text = "The quick brown fox jumps over the lazy dog and runs through the forest with great speed."
    lang, conf = LanguageProfiler.detect_language(en_text)
    assert lang == "en"
    assert conf > 0.1

    es_text = "El rápido zorro marrón salta sobre el perro perezoso en el bosque."
    lang_es, _ = LanguageProfiler.detect_language(es_text)
    assert lang_es == "es"


def test_compression_roundtrips():
    # 1. RLE
    raw_rle = b"AAAAABBBCCCCCCDDDDDDDDDD" * 10
    encoded_rle = RunLengthEncoding.encode_bytes(raw_rle)
    assert len(encoded_rle) < len(raw_rle)
    decoded_rle = RunLengthEncoding.decode_bytes(encoded_rle)
    assert decoded_rle == raw_rle

    # 2. Huffman
    raw_huff = b"Aether offline-first personal command workstation with cryptographic vault!" * 5
    packed, freq_table = HuffmanCoder.encode(raw_huff)
    decoded_huff = HuffmanCoder.decode(packed, freq_table)
    assert decoded_huff == raw_huff

    # 3. LZW
    text_lzw = "TOBEORNOTTOBEORTOBEORNOT"
    codes = LZWCompressor.compress(text_lzw)
    decompressed = LZWCompressor.decompress(codes)
    assert decompressed == text_lzw

    # 4. Entropy & Benchmark
    entropy = ShannonEntropy.calculate(b"0123456789ABCDEF")
    assert 3.5 <= entropy <= 4.0

    eval_result = CompressionBenchmark.evaluate(raw_huff)
    assert "shannon_entropy_bits" in eval_result
    assert "huffman" in eval_result
    assert "lzw" in eval_result
    assert eval_result["huffman"]["savings_pct"] >= 0.0
