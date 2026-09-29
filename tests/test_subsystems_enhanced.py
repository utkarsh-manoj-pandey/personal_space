"""
Automated Test Suite for Enhanced Subsystem Capabilities
Validates all newly expanded features across the 17 isolated subsystems,
database diagnostics, hot backup routines, and backend bridge slots.
"""

import os
import json
import pytest
from backend.database_manager import db_manager
from backend.bridge import backend_bridge
from backend.modules.calculator_service import calculator_service
from backend.modules.calendar_service import calendar_service
from backend.modules.game_service import game_service
from backend.modules.weather_service import weather_service, AtmosphericPhysics, SolarLunarAstronomy
from backend.modules.world_monitor_service import world_monitor_service, OrbitalMechanicsEngine, SeismicPhysicsEngine
from backend.modules.maps_service import maps_service, GeodesyEngine
from backend.modules.browser_service import browser_service
from backend.modules.notepad_service import notepad_service, TextAnalyticsEngine
from backend.modules.music_service import music_service
from backend.modules.video_service import video_service
from backend.modules.document_service import document_service
from backend.modules.radio_service import radio_service
from backend.modules.news_service import news_service
from backend.modules.image_service import image_service
from backend.modules.clock_service import clock_service, AstronomicalTimeEngine, CronExpressionEvaluator
from backend.modules.planner_service import planner_service
from backend.modules.contact_service import contact_service
from backend.modules.system_service import system_service


def test_database_manager_diagnostics_and_backup():
    """Verify deep B-tree diagnostics and hot atomic backups."""
    diagnostics = db_manager.get_all_databases_diagnostics()
    assert len(diagnostics) == 17
    for d in diagnostics:
        assert d["status"] == "Online"
        assert d["page_count"] > 0
        assert "integrity" in d
        assert d["integrity"] == "ok"

    # Integrity verification
    integ = db_manager.verify_integrity_all_databases()
    assert integ["all_healthy"] is True

    # Storage audit
    audit = db_manager.get_storage_audit()
    assert audit["total_databases"] == 17
    assert audit["combined_storage_mb"] > 0

    # Hot atomic backup
    backup_res = db_manager.backup_all_databases()
    assert backup_res["success"] is True
    assert backup_res["databases_backed_up"] == 17
    assert os.path.exists(backup_res["backup_directory"])

    # Defragmentation & optimize
    opt_res = db_manager.optimize_all_databases()
    assert opt_res["success"] is True
    assert opt_res["databases_optimized"] == 17


def test_calculator_enhanced_features():
    """Verify unit conversions, loan schedules, and compound interest."""
    # Unit conversion
    conv = calculator_service.convert_units(100.0, "km", "mi")
    assert conv["success"] is True
    assert round(conv["to_value"], 2) == 62.14

    temp_conv = calculator_service.convert_units(100.0, "c", "f")
    assert temp_conv["success"] is True
    assert round(temp_conv["to_value"], 1) == 212.0

    # Loan payment
    loan = calculator_service.calculate_loan(10000.0, 5.0, 36)
    assert loan["monthly_payment"] > 0
    assert loan["total_paid"] > 10000.0

    # Compound interest
    growth = calculator_service.calculate_compound_interest(5000.0, 7.0, 10)
    assert growth["total_amount"] > 5000.0

    # Physical constant in AST
    c_res = calculator_service.calculate("c", "Scientific")
    assert c_res["success"] is True
    assert float(c_res["result"]) == 299792458.0


def test_calendar_enhanced_features():
    """Verify conflict detection, workload analytics, and free slot finding."""
    conflicts = calendar_service.detect_schedule_conflicts()
    assert isinstance(conflicts, list)

    analytics = calendar_service.get_schedule_analytics()
    assert "total_scheduled_hours" in analytics
    assert "category_breakdown" in analytics

    # Free slots
    free_slots = calendar_service.find_free_slots("2026-10-01", duration_minutes=30)
    assert isinstance(free_slots, list)


def test_game_service_enhanced_features():
    """Verify Chess legal moves, FEN notation, Connect 4, and Sudoku."""
    game_service.chess_reset()
    fen = game_service.chess.to_fen()
    assert "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1" in fen

    # White opening has exactly 20 legal moves
    legal_moves = game_service.chess.generate_legal_moves('w')
    assert len(legal_moves) == 20

    # Sudoku generator and solver
    sudoku = game_service.sudoku_generate(difficulty="Easy")
    assert "puzzle" in sudoku
    assert "solution" in sudoku
    assert len(sudoku["puzzle"]) == 9
    assert len(sudoku["solution"]) == 9

    # Solver
    solved = game_service.sudoku_solve(sudoku["puzzle"])
    assert solved is not None
    # Verify solved board matches clues and is a complete valid Sudoku
    for r in range(9):
        assert set(solved[r]) == set(range(1, 10))
        for c in range(9):
            if sudoku["puzzle"][r][c] != 0:
                assert solved[r][c] == sudoku["puzzle"][r][c]
    for c in range(9):
        col_vals = [solved[r][c] for r in range(9)]
        assert set(col_vals) == set(range(1, 10))
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            block_vals = [solved[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
            assert set(block_vals) == set(range(1, 10))


def test_weather_and_astronomy_physics():
    """Verify thermodynamic equations, Jean Meeus solar times, and lunar phase."""
    # Heat index
    hi = AtmosphericPhysics.heat_index(35.0, 80.0)
    assert hi > 35.0

    # Wind chill
    wc = AtmosphericPhysics.wind_chill(0.0, 25.0)
    assert wc < 0.0

    # Dew point
    dp = AtmosphericPhysics.dew_point(25.0, 60.0)
    assert 15.0 < dp < 20.0

    # Beaufort scale
    b = AtmosphericPhysics.beaufort_scale(45.0)
    assert b["force"] == 6

    # Solar sun times
    sun = SolarLunarAstronomy.calculate_sun_times(40.7128, -74.0060)
    assert "sunrise" in sun
    assert "sunset" in sun
    assert sun["day_length_hours"] > 0

    # Moon phase
    moon = SolarLunarAstronomy.get_moon_phase()
    assert "phase_name" in moon
    assert 0.0 <= moon["illumination_percent"] <= 100.0


def test_world_monitor_and_orbital_physics():
    """Verify ISS Keplerian kinematics, Richter energy physics, and DefCon posture."""
    iss = OrbitalMechanicsEngine.calculate_iss_kinematics()
    assert "velocity_kmh" in iss
    assert iss["velocity_kmh"] > 25000.0  # LEO orbital speed
    assert iss["footprint_radius_km"] > 2000.0

    # Richter Joules
    joules = SeismicPhysicsEngine.richter_to_joules(7.0)
    assert joules > 1e15
    tnt = SeismicPhysicsEngine.joules_to_tnt_kilotons(joules)
    assert tnt > 400.0

    # DefCon posture
    summary = world_monitor_service.get_situational_summary()
    assert "threat_posture" in summary
    assert summary["threat_posture"]["defcon_level"] in (1, 2, 3, 4, 5)


def test_maps_geodesy_and_geofencing():
    """Verify Vincenty distance, bearing, destination projection, and geofencing."""
    # Vincenty distance between NYC (40.7128, -74.0060) and London (51.5074, -0.1278)
    dist_m = GeodesyEngine.vincenty_distance_meters(40.7128, -74.0060, 51.5074, -0.1278)
    assert dist_m is not None
    dist_km = dist_m / 1000.0
    assert 5500.0 < dist_km < 5650.0

    # Initial bearing
    bearing = GeodesyEngine.initial_bearing_degrees(40.7128, -74.0060, 51.5074, -0.1278)
    assert 40.0 < bearing < 60.0

    # Destination point projection
    dest_lat, dest_lon = GeodesyEngine.destination_point(0.0, 0.0, 90.0, 111.32)
    assert abs(dest_lat - 0.0) < 0.1
    assert abs(dest_lon - 1.0) < 0.1

    # Geofencing Point in Polygon (Square: (0,0) to (10,10))
    poly = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    assert GeodesyEngine.point_in_polygon(5.0, 5.0, poly) is True
    assert GeodesyEngine.point_in_polygon(15.0, 5.0, poly) is False


def test_notepad_readability_metrics():
    """Verify Flesch, Flesch-Kincaid, Gunning Fog, and ARI readability scores."""
    sample_text = (
        "The Sovereign Personal Workstation represents an elite, offline-first personal operating system. "
        "It provides sovereign computational privacy without external cloud dependencies."
    )
    metrics = TextAnalyticsEngine.analyze_text(sample_text)
    assert metrics["words"] > 10
    assert metrics["sentences"] == 2
    assert "flesch_reading_ease" in metrics
    assert "flesch_kincaid_grade" in metrics
    assert "gunning_fog" in metrics
    assert "readability_tier" in metrics


def test_clock_astronomy_and_cron():
    """Verify Julian Date and Cron evaluation."""
    astro = clock_service.get_astronomical_telemetry()
    assert astro["julian_date"] > 2450000.0
    assert "gmst_display" in astro

    # Cron evaluation: '*/15 * * * *' (every 15 minutes)
    cron_res = clock_service.evaluate_cron("*/15 * * * *")
    assert cron_res["valid"] is True
    assert "next_run" in cron_res


def test_planner_cpm_analytics():
    """Verify Critical Path Method project analysis."""
    prod = planner_service.get_productivity_analytics()
    assert "cpm_analysis" in prod
    cpm = prod["cpm_analysis"]
    assert "total_project_duration_pomodoros" in cpm
    assert "critical_path_task_ids" in cpm


def test_contact_duplicate_detection():
    """Verify duplicate contact candidate search."""
    duplicates = contact_service.find_duplicate_candidates()
    assert isinstance(duplicates, list)


def test_new_backend_bridge_slots():
    """Verify new BackendBridge slots execute and serialize clean JSON."""
    # Diagnostics slot
    diag_raw = backend_bridge.getDatabasesDiagnostics()
    diag = json.loads(diag_raw)
    assert len(diag) == 17

    # Unit conversion slot
    u_raw = backend_bridge.convertUnits(10.0, "km", "mi", "length")
    u_res = json.loads(u_raw)
    assert u_res["success"] is True

    # Statistics slot
    stat_raw = backend_bridge.computeStatistics(json.dumps([10, 20, 30, 40, 50]))
    stat = json.loads(stat_raw)
    assert stat["mean"] == 30.0

    # Password security slot
    pw_raw = backend_bridge.analyzePasswordSecurity("SuperSecret#2026Pass")
    pw = json.loads(pw_raw)
    assert pw["score"] >= 70

    # Astronomy slot
    astro_raw = backend_bridge.getAstronomicalTelemetry()
    astro = json.loads(astro_raw)
    assert "julian_date" in astro
