"""
Automated Test Suite for Aether Subsystems
Validates all 17 isolated subsystems, their dedicated SQLite databases,
and the QWebChannel bridge slots.
"""

import os
import json
import pytest
from backend.database_manager import db_manager
from backend.bridge import backend_bridge


def test_17_databases_exist():
    """Verify all 17 isolated SQLite databases are present on disk."""
    assert len(db_manager.DATABASE_NAMES) == 17
    for db_name in db_manager.DATABASE_NAMES:
        db_path = db_manager.get_db_path(db_name)
        assert os.path.exists(db_path), f"Database missing: {db_name}"


def test_calendar_subsystem():
    """Verify calendar listing, creation, and ICS export."""
    events_raw = backend_bridge.listCalendarEvents("", "")
    events = json.loads(events_raw)
    assert isinstance(events, list)
    assert len(events) >= 1

    ics = backend_bridge.exportCalendarIcs()
    assert "BEGIN:VCALENDAR" in ics
    assert "END:VCALENDAR" in ics


def test_browser_subsystem():
    """Verify browser bookmarks and privacy settings."""
    bms = json.loads(backend_bridge.listBrowserBookmarks())
    assert isinstance(bms, list)
    assert len(bms) >= 1

    settings = json.loads(backend_bridge.getPrivacySettings())
    assert "user_agent_profile" in settings
    assert settings["block_trackers"] == "1"


def test_notepad_subsystem():
    """Verify notes listing and saving."""
    notes = json.loads(backend_bridge.listNotes("", ""))
    assert isinstance(notes, list)
    assert len(notes) >= 1

    # Create temporary note
    saved = json.loads(backend_bridge.saveNote(0, "Test Note", "Test Content with multiple words", "Test", 0))
    assert saved["title"] == "Test Note"
    assert saved["word_count"] > 0
    # Clean up
    assert backend_bridge.deleteNote(saved["id"]) is True


def test_music_subsystem():
    """Verify music tracks and synthesized ambient files."""
    tracks = json.loads(backend_bridge.listMusicTracks(""))
    assert isinstance(tracks, list)
    assert len(tracks) >= 1
    # Check that audio file exists
    assert os.path.exists(tracks[0]["file_path"])


def test_video_subsystem():
    """Verify video playlist records."""
    videos = json.loads(backend_bridge.listVideos())
    assert isinstance(videos, list)
    assert len(videos) >= 1


def test_document_subsystem():
    """Verify document parser and sample specification."""
    recents = json.loads(backend_bridge.listRecentDocuments())
    assert isinstance(recents, list)
    assert len(recents) >= 1
    doc = json.loads(backend_bridge.openDocument(recents[0]["file_path"]))
    assert "content" in doc
    assert len(doc["content"]) > 10



def test_radio_subsystem():
    """Verify radio stations matrix."""
    stations = json.loads(backend_bridge.listRadioStations("", ""))
    assert isinstance(stations, list)
    assert len(stations) >= 5


def test_weather_subsystem():
    """Verify weather data structure."""
    weather = json.loads(backend_bridge.getWeather("New York"))
    assert "temperature" in weather
    assert "humidity" in weather
    assert "hourly" in weather
    assert "daily" in weather


def test_news_subsystem():
    """Verify news aggregator articles."""
    articles = json.loads(backend_bridge.listNewsArticles("", False))
    assert isinstance(articles, list)


def test_calculator_subsystem():
    """Verify safe AST calculation engine."""
    res = json.loads(backend_bridge.calculate("12.5 * 4 + sin(0) + sqrt(16)", "Scientific"))
    assert res["success"] is True
    assert float(res["result"]) == 54.0

    prog_res = json.loads(backend_bridge.calculate("255", "Programmer"))
    assert prog_res["programmer"]["hex"] == "0XFF"
    assert prog_res["programmer"]["bin"] == "0b11111111"


def test_image_subsystem():
    """Verify image catalog and procedural tactical samples."""
    images = json.loads(backend_bridge.listImages())
    assert isinstance(images, list)
    assert len(images) >= 1
    assert os.path.exists(images[0]["file_path"])


def test_clocks_subsystem():
    """Verify world clocks calculation."""
    clocks = json.loads(backend_bridge.getWorldClocks())
    assert isinstance(clocks, list)
    assert len(clocks) >= 5
    cities = [c["city"] for c in clocks]
    assert any("UTC" in c for c in cities)


def test_maps_subsystem():
    """Verify waypoints and routing computation."""
    waypoints = json.loads(backend_bridge.listWaypoints())
    assert isinstance(waypoints, list)
    assert len(waypoints) >= 1

    route = json.loads(backend_bridge.calculateRoute(40.7128, -74.0060, 42.3601, -71.0589))
    assert route["success"] is True
    assert route["distance_km"] > 0


def test_world_monitor_subsystem():
    """Verify Palantir situational dashboard summary and USGS feed."""
    summary = json.loads(backend_bridge.getWorldMonitorSummary())
    assert "threat_posture" in summary
    assert "iss_position" in summary
    assert "earthquakes" in summary
    assert "chokepoints" in summary


def test_planner_subsystem():
    """Verify planner tasks and Kanban columns."""
    tasks = json.loads(backend_bridge.listTasks("", ""))
    assert isinstance(tasks, list)
    assert len(tasks) >= 1


def test_contacts_subsystem():
    """Verify contacts directory and vCard generation."""
    contacts = json.loads(backend_bridge.listContacts("", ""))
    assert isinstance(contacts, list)
    assert len(contacts) >= 1

    vcard = backend_bridge.exportContactVCard(contacts[0]["id"])
    assert "BEGIN:VCARD" in vcard
    assert "VERSION:3.0" in vcard


def test_game_engines():
    """Verify pure Python Chess Minimax engine and Connect 4."""
    board = json.loads(backend_bridge.chessReset())
    assert len(board) == 8
    assert len(board[0]) == 8

    # Test legal moves preview
    valid_moves = json.loads(backend_bridge.chessGetValidMoves(6, 4))
    assert isinstance(valid_moves, list)
    assert [5, 4] in valid_moves
    assert [4, 4] in valid_moves

    # Make player move e2 to e4 -> (6, 4) to (4, 4)
    move_res = json.loads(backend_bridge.chessMovePlayer(6, 4, 4, 4))
    assert move_res["success"] is True
    assert move_res["board"][4][4] == 'P'

    # Compute AI response move with Minimax Alpha-Beta
    ai_res = json.loads(backend_bridge.chessComputerMove("Intermediate"))
    assert ai_res["success"] is True
    assert "move" in ai_res

    # Test Connect 4
    c4_board = json.loads(backend_bridge.connect4Reset())
    assert len(c4_board) == 6
    c4_res = json.loads(backend_bridge.connect4Drop(3))
    assert c4_res["success"] is True


def test_system_telemetry():
    """Verify system telemetry collection."""
    telemetry = json.loads(backend_bridge.getSystemTelemetry())
    assert "cpu_percent" in telemetry
    assert "ram_percent" in telemetry
    assert "uptime" in telemetry
