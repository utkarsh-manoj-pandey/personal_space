"""
Exhaustive verification of Aether BackendBridge QWebChannel API slots.
Tests return contracts, JSON schema safety, and deterministic subsystem responses.
"""

import json
import pytest
from backend.bridge import backend_bridge


def test_bridge_system_and_diagnostics_slots():
    status_raw = backend_bridge.getSystemTelemetry()
    status = json.loads(status_raw)
    assert "cpu_percent" in status
    assert "ram_percent" in status
    assert "health_score" in status

    audit_raw = backend_bridge.getStorageAudit()
    audit = json.loads(audit_raw)
    assert audit.get("total_databases") == 17
    assert "combined_storage_mb" in audit
    assert "total_records_stored" in audit

    integrity_raw = backend_bridge.runIntegrityCheck()
    integrity = json.loads(integrity_raw)
    assert integrity.get("all_healthy") is True

    proc_raw = backend_bridge.getProcessDiagnostics(top_n=3)
    proc = json.loads(proc_raw)
    assert isinstance(proc, list)
    assert len(proc) <= 3


def test_bridge_mathematics_and_scientific_slots():
    # Math evaluation
    math_raw = backend_bridge.evaluateMathExpression("sin(pi / 2) + cos(0) * sqrt(16)")
    math_res = json.loads(math_raw)
    assert math_res.get("success") is True
    assert float(math_res.get("result")) == 5.0

    # Loan amortization
    loan_raw = backend_bridge.calculateLoan(10000.0, 5.0, 12)
    loan_res = json.loads(loan_raw)
    assert "monthly_payment" in loan_res
    assert loan_res["monthly_payment"] > 0

    # Compound interest
    compound_raw = backend_bridge.calculateCompoundInterest(5000.0, 6.0, 5.0, 12)
    compound_res = json.loads(compound_raw)
    assert compound_res["total_amount"] > 5000.0

    # IEEE-754 binary decomposition
    ieee_raw = backend_bridge.decomposeFloatIeee754(3.14159)
    ieee_res = json.loads(ieee_raw)
    assert ieee_res["sign"] == 0
    assert len(ieee_res["bit_string"]) == 64

    # Polynomial curve fit
    pts = json.dumps([{"x": 1.0, "y": 2.0}, {"x": 2.0, "y": 4.0}, {"x": 3.0, "y": 6.0}])
    poly_raw = backend_bridge.fitPolynomialCurve(pts, degree=1)
    poly_res = json.loads(poly_raw)
    assert poly_res.get("success") is True
    assert round(poly_res["coefficients"][0], 2) == 2.0

    # Matrix solver
    a_mat = json.dumps([[3.0, 1.0], [1.0, 2.0]])
    b_vec = json.dumps([9.0, 8.0])
    mat_raw = backend_bridge.solveLinearSystemAxEqB(a_mat, b_vec)
    mat_res = json.loads(mat_raw)
    assert mat_res.get("success") is True
    assert round(mat_res["solution"][0], 2) == 2.0
    assert round(mat_res["solution"][1], 2) == 3.0


def test_bridge_crypto_and_security_slots():
    # Password entropy analyzer
    pw_raw = backend_bridge.analyzePasswordSecurity("Tr0ub4dor&3_correct_horse_battery")
    pw_res = json.loads(pw_raw)
    assert pw_res["entropy_bits"] > 80.0
    assert "Military-Grade" in pw_res["rating"] or "Sovereign" in pw_res["rating"]

    # URL security evaluator
    url_raw = backend_bridge.evaluateUrlSecurity("https://example.com/search?q=test&utm_source=tracker&fbclid=abc123xyz")
    url_res = json.loads(url_raw)
    assert url_res["has_tracking_query_params"] is True
    assert "utm_source" not in url_res["sanitized_url"]


def test_bridge_nlp_search_and_compression_slots():
    # TextRank Summarizer
    text = (
        "Antigravity is an offline-first personal workstation. "
        "It features 17 isolated SQLite databases running in WAL mode. "
        "The architecture communicates via deterministic PySide6 QWebChannel slots. "
        "No cloud telemetry or external network ports are opened during operation."
    )
    sum_raw = backend_bridge.summarizeText(text, num_sentences=2)
    sum_res = json.loads(sum_raw)
    assert len(sum_res) == 2

    # RAKE Keywords
    kw_raw = backend_bridge.extractKeywords(text, top_n=3)
    kw_res = json.loads(kw_raw)
    assert len(kw_res) > 0

    # Entity Extractor
    ent_text = "Reach admin@aether.internal or https://docs.aether.org before 2026-10-01."
    ent_raw = backend_bridge.detectEntities(ent_text)
    ent_res = json.loads(ent_raw)
    assert "email" in ent_res
    assert "url" in ent_res

    # Language Profiler
    lang_raw = backend_bridge.detectLanguage("The quick brown fox jumps over the lazy dog.")
    lang_res = json.loads(lang_raw)
    assert lang_res["language"] == "en"

    # Compression Benchmark
    comp_raw = backend_bridge.benchmarkCompression("Deterministic zero-telemetry local command workstation")
    comp_res = json.loads(comp_raw)
    assert "shannon_entropy_bits" in comp_res
    assert "huffman" in comp_res

    # Search Workstation Content
    search_raw = backend_bridge.searchWorkstationContent("project", limit=5)
    search_res = json.loads(search_raw)
    assert "query" in search_res
    assert "results" in search_res


def test_bridge_dsp_radio_and_game_slots():
    # Audio metrics
    metrics_raw = backend_bridge.calculateAudioMetrics(json.dumps([0.1, -0.2, 0.4, -0.4, 0.2, -0.1]))
    metrics = json.loads(metrics_raw)
    assert "rms" in metrics
    assert "crest_factor" in metrics

    # Radio presets
    presets_raw = backend_bridge.getRadioEqualizerPresets()
    presets = json.loads(presets_raw)
    assert "Flat" in presets
    assert "Bass Boost" in presets

    # Sudoku Generator and Solver
    sudoku_raw = backend_bridge.sudokuGenerate("Easy")
    sudoku = json.loads(sudoku_raw)
    assert "puzzle" in sudoku
    puzzle_json = json.dumps(sudoku["puzzle"])

    sol_raw = backend_bridge.sudokuSolve(puzzle_json)
    sol = json.loads(sol_raw)
    assert sol.get("success") is True
    assert len(sol["solution"]) == 9
