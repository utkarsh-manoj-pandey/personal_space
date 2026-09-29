"""
PySide6 QWebChannel RPC Bridge
Binds JavaScript in index.html to Python backend subsystem services.
All slot methods are strictly typed, return serialized JSON, and handle exceptions defensibly.
"""

import os
import json
import logging
from typing import Any, Optional
from PySide6.QtCore import QObject, Slot, Signal, QUrl
from PySide6.QtWidgets import QFileDialog, QApplication
from PySide6.QtGui import QDesktopServices
from .database_manager import db_manager

from .modules.calendar_service import calendar_service
from .modules.browser_service import browser_service
from .modules.notepad_service import notepad_service
from .modules.music_service import music_service
from .modules.video_service import video_service
from .modules.document_service import document_service
from .modules.radio_service import radio_service
from .modules.weather_service import weather_service
from .modules.news_service import news_service
from .modules.calculator_service import calculator_service
from .modules.image_service import image_service
from .modules.clock_service import clock_service
from .modules.maps_service import maps_service
from .modules.world_monitor_service import world_monitor_service
from .modules.planner_service import planner_service
from .modules.contact_service import contact_service
from .modules.game_service import game_service
from .modules.system_service import system_service

logger = logging.getLogger("BackendBridge")


class BackendBridge(QObject):
    """
    Exposed QObject registered with QWebChannel.
    Every method marked with @Slot is directly invokable from frontend JavaScript.
    """

    # Optional signals for asynchronous telemetry broadcasts
    telemetryUpdated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("BackendBridge initialized and ready for QWebChannel connections.")

    def _safe_json(self, data: Any) -> str:
        """Serialize data structure to clean JSON string."""
        try:
            return json.dumps(data, default=str)
        except Exception as e:
            logger.error(f"JSON serialization error: {e}")
            return json.dumps({"error": str(e)})

    # =========================================================================
    # 1. CALENDAR SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, str, result=str)
    def listCalendarEvents(self, category: str = "", search: str = "") -> str:
        events = calendar_service.list_events(category=category or None, search=search or None)
        return self._safe_json(events)

    @Slot(str, result=str)
    def createCalendarEvent(self, data_json: str) -> str:
        data = json.loads(data_json)
        created = calendar_service.create_event(data)
        return self._safe_json(created)

    @Slot(int, str, result=str)
    def updateCalendarEvent(self, event_id: int, data_json: str) -> str:
        data = json.loads(data_json)
        updated = calendar_service.update_event(event_id, data)
        return self._safe_json(updated)

    @Slot(int, result=bool)
    def deleteCalendarEvent(self, event_id: int) -> bool:
        return calendar_service.delete_event(event_id)

    @Slot(result=str)
    def exportCalendarIcs(self) -> str:
        return calendar_service.export_ics()

    # =========================================================================
    # 2. PRIVACY BROWSER SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(result=str)
    def listBrowserBookmarks(self) -> str:
        return self._safe_json(browser_service.list_bookmarks())

    @Slot(str, str, str, str, result=str)
    def addBrowserBookmark(self, title: str, url: str, category: str, icon_svg: str) -> str:
        bm = browser_service.add_bookmark(title, url, category, icon_svg)
        return self._safe_json(bm)

    @Slot(int, result=bool)
    def deleteBrowserBookmark(self, bookmark_id: int) -> bool:
        return browser_service.delete_bookmark(bookmark_id)

    @Slot(result=str)
    def getPrivacySettings(self) -> str:
        return self._safe_json(browser_service.get_privacy_settings())

    @Slot(str, str, result=bool)
    def setPrivacySetting(self, key: str, value: str) -> bool:
        return browser_service.set_privacy_setting(key, value)

    @Slot(result=str)
    def getSearchEngines(self) -> str:
        return self._safe_json(browser_service.get_search_engines())

    @Slot(str, result=bool)
    def setActiveSearchEngine(self, engine_name: str) -> bool:
        return browser_service.set_active_engine(engine_name)

    @Slot(str, result=str)
    def getSearchUrl(self, query: str) -> str:
        return browser_service.get_search_url_for_query(query)

    # =========================================================================
    # 3. NOTEPAD SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, str, result=str)
    def listNotes(self, search: str = "", tag: str = "") -> str:
        return self._safe_json(notepad_service.list_notes(search=search, tag=tag))

    @Slot(int, result=str)
    def getNote(self, note_id: int) -> str:
        note = notepad_service.get_note(note_id)
        return self._safe_json(note)

    @Slot(int, str, str, str, int, result=str)
    def saveNote(self, note_id: int, title: str, content: str, tags: str, is_pinned: int) -> str:
        nid = None if note_id <= 0 else note_id
        saved = notepad_service.save_note(nid, title, content, tags, is_pinned)
        return self._safe_json(saved)

    @Slot(int, result=bool)
    def deleteNote(self, note_id: int) -> bool:
        return notepad_service.delete_note(note_id)

    @Slot(int, result=str)
    def toggleNotePin(self, note_id: int) -> str:
        updated = notepad_service.toggle_pin(note_id)
        return self._safe_json(updated)

    # =========================================================================
    # 4. MUSIC SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, result=str)
    def listMusicTracks(self, search: str = "") -> str:
        return self._safe_json(music_service.list_tracks(search=search))

    @Slot(int, result=str)
    def toggleMusicFavorite(self, track_id: int) -> str:
        return self._safe_json(music_service.toggle_favorite(track_id))

    @Slot(int, result=bool)
    def recordMusicPlay(self, track_id: int) -> bool:
        music_service.increment_play_count(track_id)
        return True

    @Slot(str, result=int)
    def scanMusicDirectory(self, folder_path: str) -> int:
        return music_service.scan_directory(folder_path)

    # =========================================================================
    # 5. VIDEO SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(result=str)
    def listVideos(self) -> str:
        return self._safe_json(video_service.list_videos())

    @Slot(int, float, result=bool)
    def updateVideoPosition(self, video_id: int, position: float) -> bool:
        return video_service.update_position(video_id, position)

    @Slot(int, float, str, result=str)
    def addVideoBookmark(self, video_id: int, timestamp: float, label: str) -> str:
        return self._safe_json(video_service.add_bookmark(video_id, timestamp, label))

    @Slot(int, result=str)
    def getVideoBookmarks(self, video_id: int) -> str:
        return self._safe_json(video_service.get_bookmarks(video_id))

    # =========================================================================
    # 6. DOCUMENT VIEWER SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(result=str)
    def listRecentDocuments(self) -> str:
        return self._safe_json(document_service.list_recent())

    @Slot(str, result=str)
    def openDocument(self, file_path: str) -> str:
        try:
            doc = document_service.open_document(file_path)
            return self._safe_json(doc)
        except Exception as e:
            return self._safe_json({"error": str(e)})

    @Slot(int, int, str, result=str)
    def addDocumentAnnotation(self, doc_id: int, page_number: int, note_text: str) -> str:
        return self._safe_json(document_service.add_annotation(doc_id, page_number, note_text))

    @Slot(int, result=str)
    def getDocumentAnnotations(self, doc_id: int) -> str:
        return self._safe_json(document_service.get_annotations(doc_id))

    # =========================================================================
    # 7. INTERNET RADIO SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, str, result=str)
    def listRadioStations(self, genre: str = "", search: str = "") -> str:
        return self._safe_json(radio_service.list_stations(genre=genre or None, search=search or None))

    @Slot(int, result=str)
    def toggleRadioFavorite(self, station_id: int) -> str:
        return self._safe_json(radio_service.toggle_favorite(station_id))

    @Slot(int, result=bool)
    def recordRadioListen(self, station_id: int) -> bool:
        radio_service.record_listen(station_id)
        return True

    @Slot(str, str, str, str, result=str)
    def addCustomRadioStation(self, name: str, url: str, genre: str, country: str) -> str:
        return self._safe_json(radio_service.add_custom_station(name, url, genre, country))

    # =========================================================================
    # 8. WEATHER SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, result=str)
    def getWeather(self, city_name: str = "") -> str:
        return self._safe_json(weather_service.get_weather(city_name=city_name or None))

    # =========================================================================
    # 9. NEWS VIEWER SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, bool, result=str)
    def listNewsArticles(self, category: str = "", bookmarked_only: bool = False) -> str:
        return self._safe_json(news_service.list_articles(category=category or None, bookmarked_only=bookmarked_only))

    @Slot(result=int)
    def syncNewsFeeds(self) -> int:
        return news_service.sync_feeds()

    @Slot(int, result=str)
    def toggleNewsBookmark(self, article_id: int) -> str:
        return self._safe_json(news_service.toggle_bookmark(article_id))

    @Slot(int, result=bool)
    def markNewsRead(self, article_id: int) -> bool:
        news_service.mark_read(article_id)
        return True

    # =========================================================================
    # 10. CALCULATOR SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, str, result=str)
    def calculate(self, expression: str, mode: str = "Scientific") -> str:
        return self._safe_json(calculator_service.calculate(expression, mode=mode))

    @Slot(result=str)
    def getCalculatorHistory(self) -> str:
        return self._safe_json(calculator_service.get_history())

    @Slot(result=bool)
    def clearCalculatorHistory(self) -> bool:
        return calculator_service.clear_history()

    # =========================================================================
    # 11. IMAGE VIEWER SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(result=str)
    def listImages(self) -> str:
        return self._safe_json(image_service.list_images())

    @Slot(int, result=str)
    def toggleImageFavorite(self, image_id: int) -> str:
        return self._safe_json(image_service.toggle_favorite(image_id))

    @Slot(str, result=int)
    def scanImageDirectory(self, folder_path: str) -> int:
        return image_service.scan_directory(folder_path)

    # =========================================================================
    # 12. CLOCK AND TIMERS SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(result=str)
    def getWorldClocks(self) -> str:
        return self._safe_json(clock_service.get_world_clocks())

    @Slot(str, int, int, int, result=str)
    def saveStopwatchLap(self, session_id: str, lap_number: int, lap_time_ms: int, total_time_ms: int) -> str:
        return self._safe_json(clock_service.save_stopwatch_lap(session_id, lap_number, lap_time_ms, total_time_ms))

    @Slot(str, result=str)
    def getStopwatchLaps(self, session_id: str) -> str:
        return self._safe_json(clock_service.get_stopwatch_laps(session_id))

    # =========================================================================
    # 13. MAPS AND NAVIGATION SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, result=str)
    def geocodeAddress(self, query: str) -> str:
        return self._safe_json(maps_service.geocode(query))

    @Slot(float, float, float, float, result=str)
    def calculateRoute(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> str:
        return self._safe_json(maps_service.calculate_route(start_lat, start_lon, end_lat, end_lon))

    @Slot(result=str)
    def listWaypoints(self) -> str:
        return self._safe_json(maps_service.list_waypoints())

    @Slot(str, float, float, str, str, result=str)
    def addWaypoint(self, name: str, latitude: float, longitude: float, category: str, notes: str) -> str:
        return self._safe_json(maps_service.add_waypoint(name, latitude, longitude, category, notes))

    # =========================================================================
    # 14. WORLD MONITOR SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(result=str)
    def getWorldMonitorSummary(self) -> str:
        return self._safe_json(world_monitor_service.get_world_monitor_summary())

    @Slot(result=str)
    def getSeismicFeed(self) -> str:
        return self._safe_json(world_monitor_service.get_seismic_feed())

    @Slot(result=str)
    def getIssTelemetry(self) -> str:
        return self._safe_json(world_monitor_service.get_iss_telemetry())

    @Slot(result=str)
    def getCyberVectors(self) -> str:
        return self._safe_json(world_monitor_service.get_cyber_threat_vectors())

    # =========================================================================
    # 15. PLANNER AND TASK SCHEDULE SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, str, result=str)
    def listTasks(self, status: str = "", eisenhower: str = "") -> str:
        return self._safe_json(planner_service.list_tasks(status=status or None, eisenhower=eisenhower or None))

    @Slot(str, result=str)
    def createTask(self, data_json: str) -> str:
        data = json.loads(data_json)
        return self._safe_json(planner_service.create_task(data))

    @Slot(int, str, result=str)
    def updateTaskStatus(self, task_id: int, status: str) -> str:
        return self._safe_json(planner_service.update_task_status(task_id, status))

    @Slot(int, result=bool)
    def deleteTask(self, task_id: int) -> bool:
        return planner_service.delete_task(task_id)

    @Slot(str, result=str)
    def listScheduleBlocks(self, day_date: str = "") -> str:
        return self._safe_json(planner_service.list_schedule_blocks(day_date=day_date or None))

    @Slot(str, str, str, str, str, str, result=str)
    def addScheduleBlock(self, day_date: str, start_time: str, end_time: str, title: str, category: str, color: str) -> str:
        return self._safe_json(planner_service.add_schedule_block(day_date, start_time, end_time, title, category, color))

    @Slot(int, result=bool)
    def deleteScheduleBlock(self, block_id: int) -> bool:
        return planner_service.delete_schedule_block(block_id)

    # =========================================================================
    # 16. CONTACT MANAGER SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(str, str, result=str)
    def listContacts(self, search: str = "", category: str = "") -> str:
        return self._safe_json(contact_service.list_contacts(search=search, category=category or None))

    @Slot(int, result=str)
    def getContact(self, contact_id: int) -> str:
        return self._safe_json(contact_service.get_contact(contact_id))

    @Slot(str, result=str)
    def createContact(self, data_json: str) -> str:
        data = json.loads(data_json)
        return self._safe_json(contact_service.create_contact(data))

    @Slot(int, str, result=str)
    def updateContact(self, contact_id: int, data_json: str) -> str:
        data = json.loads(data_json)
        return self._safe_json(contact_service.update_contact(contact_id, data))

    @Slot(int, result=bool)
    def deleteContact(self, contact_id: int) -> bool:
        return contact_service.delete_contact(contact_id)

    @Slot(int, str, str, result=str)
    def addContactLog(self, contact_id: int, log_type: str, summary: str) -> str:
        return self._safe_json(contact_service.add_interaction_log(contact_id, log_type, summary))

    @Slot(int, result=str)
    def exportContactVCard(self, contact_id: int) -> str:
        return contact_service.export_vcard(contact_id)

    # =========================================================================
    # 17. PYTHON GAME ENGINES SUBSYSTEM SLOTS
    # =========================================================================
    @Slot(result=str)
    def chessReset(self) -> str:
        return self._safe_json(game_service.chess_reset())

    @Slot(int, int, result=str)
    def chessGetValidMoves(self, r: int, c: int) -> str:
        return self._safe_json(game_service.chess_get_valid_moves(r, c))

    @Slot(int, int, int, int, result=str)
    def chessMovePlayer(self, sr: int, sc: int, er: int, ec: int) -> str:
        res = game_service.chess_move_player((sr, sc), (er, ec))
        return self._safe_json(res)

    @Slot(str, result=str)
    def chessComputerMove(self, difficulty: str = "Master") -> str:
        res = game_service.chess_computer_move(difficulty=difficulty)
        return self._safe_json(res)

    @Slot(result=str)
    def connect4Reset(self) -> str:
        return self._safe_json(game_service.connect4_reset())

    @Slot(int, result=str)
    def connect4Drop(self, col: int) -> str:
        res = game_service.connect4_drop(col)
        return self._safe_json(res)

    @Slot(str, str, str, int, int, result=bool)
    def recordGameMatch(self, game_title: str, game_mode: str, result: str, player_score: int, opponent_score: int) -> bool:
        game_service.record_match(game_title, game_mode, result, player_score, opponent_score)
        return True

    @Slot(str, result=str)
    def getGameLeaderboard(self, game_title: str = "") -> str:
        return self._safe_json(game_service.get_leaderboard(game_title=game_title or None))

    # =========================================================================
    # 18. SYSTEM TELEMETRY & NATIVE FILE DIALOG SLOTS
    # =========================================================================
    @Slot(result=str)
    def getSystemTelemetry(self) -> str:
        return self._safe_json(system_service.get_hardware_telemetry())

    @Slot(str, result=str)
    def openFileDialog(self, filter_pattern: str = "All Files (*.*)") -> str:
        """Opens native Qt file selection dialog."""
        file_path, _ = QFileDialog.getOpenFileName(None, "Select File", "", filter_pattern)
        return file_path or ""

    @Slot(str, result=bool)
    def openExternalUrl(self, url: str) -> bool:
        """Opens URL in system default external web browser."""
        try:
            return QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            logger.error(f"Error opening external URL {url}: {e}")
            return False

    @Slot(str, result=bool)
    def openFileExternally(self, file_path: str) -> bool:
        """Opens local document file with system default application."""
        try:
            return QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            logger.error(f"Error opening file externally {file_path}: {e}")
            return False

    @Slot(result=str)
    def getDatabasesStatus(self) -> str:
        """Returns health, size, and status for all 17 SQLite databases."""
        try:
            storage_dir = db_manager.storage_dir
            results = []
            for db_name in db_manager.DATABASE_NAMES:
                path = os.path.join(storage_dir, db_name)
                size_kb = round(os.path.getsize(path) / 1024, 1) if os.path.exists(path) else 0.0
                results.append({
                    "name": db_name,
                    "size_kb": size_kb,
                    "status": "Online",
                    "path": path
                })
            return self._safe_json(results)
        except Exception as e:
            logger.error(f"Error checking databases: {e}")
            return self._safe_json([])

    # =========================================================================
    # 19. ADVANCED SUBSYSTEM SLOTS & CORE BRIDGES
    # =========================================================================

    @Slot(result=str)
    def getDatabasesDiagnostics(self) -> str:
        """Returns deep B-tree page metrics, freelists, and record counts for all 17 databases."""
        return self._safe_json(db_manager.get_all_databases_diagnostics())

    @Slot(result=str)
    def backupDatabases(self) -> str:
        """Executes hot atomic backup of all 17 isolated databases using SQLite Online Backup API."""
        return self._safe_json(db_manager.backup_all_databases())

    @Slot(result=str)
    def optimizeDatabases(self) -> str:
        """Executes VACUUM and ANALYZE routines to defragment storage and update index statistics."""
        return self._safe_json(db_manager.optimize_all_databases())

    @Slot(result=str)
    def verifyDatabasesIntegrity(self) -> str:
        """Executes PRAGMA integrity_check and foreign_key_check across all 17 databases."""
        return self._safe_json(db_manager.verify_integrity_all_databases())

    @Slot(float, str, str, str, result=str)
    def convertUnits(self, value: float, from_unit: str, to_unit: str, category: str = "") -> str:
        """Convert across physical scientific and digital storage units."""
        return self._safe_json(calculator_service.convert_units(value, from_unit, to_unit, category or None))

    @Slot(float, float, int, result=str)
    def calculateLoan(self, principal: float, annual_rate: float, term_months: int) -> str:
        """Calculate amortized loan schedule."""
        return self._safe_json(calculator_service.calculate_loan(principal, annual_rate, term_months))

    @Slot(float, float, float, int, result=str)
    def calculateCompoundInterest(self, principal: float, annual_rate: float, years: float, times_per_year: int = 12) -> str:
        """Calculate compound investment growth."""
        return self._safe_json(calculator_service.calculate_compound_interest(principal, annual_rate, years, times_per_year))

    @Slot(str, result=str)
    def computeStatistics(self, numbers_json: str) -> str:
        """Compute full statistical telemetry for an array of numbers."""
        try:
            numbers = json.loads(numbers_json)
            return self._safe_json(calculator_service.compute_statistics(numbers))
        except Exception as e:
            return self._safe_json({"error": str(e)})

    @Slot(result=str)
    def detectCalendarConflicts(self) -> str:
        """Detect schedule collisions and overlapping events."""
        return self._safe_json(calendar_service.detect_schedule_conflicts())

    @Slot(result=str)
    def getCalendarAnalytics(self) -> str:
        """Calculate workload distribution and category time allocations."""
        return self._safe_json(calendar_service.get_schedule_analytics())

    @Slot(str, int, result=str)
    def findCalendarFreeSlots(self, target_date: str, duration_mins: int = 60) -> str:
        """Calculate open uncommitted time slots on given date."""
        return self._safe_json(calendar_service.find_free_slots(target_date, duration_minutes=duration_mins))

    @Slot(result=str)
    def getAstronomicalTelemetry(self) -> str:
        """Get Julian Date, MJD, and Greenwich Mean Sidereal Time."""
        return self._safe_json(clock_service.get_astronomical_telemetry())

    @Slot(str, result=str)
    def evaluateCronExpression(self, cron_expr: str) -> str:
        """Evaluate next occurrence for a cron schedule."""
        return self._safe_json(clock_service.evaluate_cron(cron_expr))

    @Slot(result=str)
    def getPlannerAnalytics(self) -> str:
        """Get Critical Path Method (CPM) and task velocity metrics."""
        return self._safe_json(planner_service.get_productivity_analytics())

    @Slot(result=str)
    def findDuplicateContacts(self) -> str:
        """Detect duplicate contacts using Jaro-Winkler fuzzy matching."""
        return self._safe_json(contact_service.find_duplicate_candidates())

    @Slot(str, str, float, float, result=str)
    def synthesizeBinauralAudio(self, track_name: str, band_name: str = "Alpha", base_hz: float = 432.0, duration_sec: float = 20.0) -> str:
        """Synthesize bespoke binaural soundscape track."""
        return self._safe_json(music_service.synthesize_custom_binaural(track_name, band_name, base_hz, duration_sec))

    @Slot(result=str)
    def exportRadioM3u(self) -> str:
        """Export internet radio stations to M3U playlist format."""
        return radio_service.export_m3u_playlist()

    @Slot(result=str)
    def exportRadioPls(self) -> str:
        """Export internet radio stations to PLS playlist format."""
        return radio_service.export_pls_playlist()

    @Slot(result=str)
    def getRadioEqualizerPresets(self) -> str:
        """Get 10-band audio equalizer profiles."""
        return self._safe_json(radio_service.get_equalizer_presets())

    @Slot(str, result=str)
    def testRadioStreamHealth(self, url: str) -> str:
        """Probe stream availability and latency."""
        return self._safe_json(radio_service.test_stream_health(url))

    @Slot(result=str)
    def exportNewsOpml(self) -> str:
        """Export RSS subscriptions to OPML 2.0 XML."""
        return news_service.export_feeds_opml()

    @Slot(result=str)
    def exportBookmarksHtml(self) -> str:
        """Export bookmarks in Netscape HTML standard format."""
        return browser_service.export_bookmarks_html()

    @Slot(str, result=str)
    def evaluateUrlSecurity(self, url: str) -> str:
        """Inspect URL for tracking tags and privacy compliance."""
        return self._safe_json(browser_service.evaluate_url_security(url))

    @Slot(result=str)
    def exportWaypointsGpx(self) -> str:
        """Export waypoints in GPS Exchange Format (GPX 1.1)."""
        return maps_service.export_waypoints_gpx()

    @Slot(result=str)
    def exportWaypointsKml(self) -> str:
        """Export waypoints in Google Earth KML 2.2."""
        return maps_service.export_waypoints_kml()

    @Slot(int, result=str)
    def exportVideoChaptersVtt(self, video_id: int) -> str:
        """Export video bookmarks as WebVTT chapter track."""
        return video_service.export_vtt_chapters(video_id) or ""

    @Slot(str, result=str)
    def sudokuGenerate(self, difficulty: str = "Medium") -> str:
        """Generate a new Sudoku puzzle with solution."""
        return self._safe_json(game_service.sudoku_generate(difficulty))

    @Slot(str, result=str)
    def sudokuSolve(self, grid_json: str) -> str:
        """Solve a 9x9 Sudoku grid."""
        try:
            grid = json.loads(grid_json)
            sol = game_service.sudoku_solve(grid)
            return self._safe_json({"success": sol is not None, "solution": sol})
        except Exception as e:
            return self._safe_json({"success": False, "error": str(e)})

    @Slot(result=str)
    def getSituationalSpaceWeather(self) -> str:
        """Get solar flare, geomagnetic Kp-index, and radio blackout data."""
        return self._safe_json(world_monitor_service.get_space_weather())

    @Slot(str, result=str)
    def analyzePasswordSecurity(self, password: str) -> str:
        """Evaluate password Shannon entropy, crack latency, and resilience."""
        from .core.crypto_utils import PasswordSecurityAnalyzer
        return self._safe_json(PasswordSecurityAnalyzer.analyze(password))

    @Slot(str, int, result=str)
    def summarizeText(self, text: str, num_sentences: int = 3) -> str:
        """Extractive text summarization using TextRank graph centrality."""
        from .core.nlp_engine import TextRankSummarizer
        return self._safe_json(TextRankSummarizer.summarize(text, num_sentences=num_sentences))

    @Slot(str, int, result=str)
    def extractKeywords(self, text: str, top_n: int = 10) -> str:
        """Extract multi-word key phrases using RAKE co-occurrence graph scoring."""
        from .core.nlp_engine import RAKEKeywordExtractor
        return self._safe_json(RAKEKeywordExtractor.extract_keywords(text, top_n=top_n))

    @Slot(str, result=str)
    def detectEntities(self, text: str) -> str:
        """Detect structured entities (emails, URLs, dates, currencies, IPs, phones)."""
        from .core.nlp_engine import EntityExtractor
        return self._safe_json(EntityExtractor.extract_all(text))

    @Slot(str, result=str)
    def detectLanguage(self, text: str) -> str:
        """Detect natural language and confidence ratio using N-gram frequency profiles."""
        from .core.nlp_engine import LanguageProfiler
        lang, conf = LanguageProfiler.detect_language(text)
        return self._safe_json({"language": lang, "confidence": conf})

    @Slot(str, result=str)
    def benchmarkCompression(self, text: str) -> str:
        """Evaluate RLE, Huffman, LZW, and Shannon entropy on text payload."""
        from .core.compression import CompressionBenchmark
        return self._safe_json(CompressionBenchmark.evaluate(text.encode("utf-8")))

    @Slot(str, int, result=str)
    def searchWorkstationContent(self, query: str, limit: int = 10) -> str:
        """Global Okapi BM25 cross-enclave search over local notepad notes and documents."""
        from .core.search_indexer import InvertedIndex
        try:
            indexer = InvertedIndex()
            # Index notepad notes
            notes = notepad_service.get_all_notes()
            for note in notes:
                doc_id = f"note_{note.get('id')}"
                content = f"{note.get('title', '')} {note.get('content', '')}"
                indexer.add_document(doc_id, content, metadata={"type": "note", "title": note.get("title"), "id": note.get("id")})

            # Index documents
            docs = document_service.get_all_documents()
            for doc in docs:
                doc_id = f"doc_{doc.get('id')}"
                content = f"{doc.get('title', '')} {doc.get('content', '')} {doc.get('tags', '')}"
                indexer.add_document(doc_id, content, metadata={"type": "document", "title": doc.get("title"), "id": doc.get("id")})

            results = indexer.search_bm25(query, limit=limit)
            return self._safe_json({"query": query, "count": len(results), "results": results})
        except Exception as e:
            return self._safe_json({"query": query, "count": 0, "results": [], "error": str(e)})

    @Slot(result=str)
    def getStorageAudit(self) -> str:
        """Audit storage, page count, and row metrics across 17 database enclaves."""
        from .database_manager import db_manager
        return self._safe_json(db_manager.get_storage_audit())

    @Slot(result=str)
    def runIntegrityCheck(self) -> str:
        """Run PRAGMA integrity_check across all 17 database enclaves."""
        from .database_manager import db_manager
        return self._safe_json(db_manager.verify_integrity_all_databases())

    @Slot(int, result=str)
    def getProcessDiagnostics(self, top_n: int = 5) -> str:
        """Inspect top local processes ranked by memory and CPU utilization."""
        return self._safe_json(system_service.get_top_processes(limit=top_n))

    @Slot(str, result=str)
    def evaluateMathExpression(self, expression: str) -> str:
        """Evaluate mathematical expression with scientific constants via AST parser."""
        return self.calculate(expression, mode="Scientific")

    @Slot(float, result=str)
    def decomposeFloatIeee754(self, value: float) -> str:
        """Decompose 64-bit float into IEEE-754 sign, exponent, and mantissa bits."""
        return self._safe_json(calculator_service.decompose_ieee754(value))

    @Slot(str, int, result=str)
    def fitPolynomialCurve(self, points_json: str, degree: int = 1) -> str:
        """Fit polynomial least-squares curve to 2D coordinate points."""
        from .core.statistics_engine import PolynomialEngine
        try:
            raw_pts = json.loads(points_json)
            pts = [(p["x"], p["y"]) if isinstance(p, dict) else (p[0], p[1]) for p in raw_pts]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            coeffs = PolynomialEngine.fit_polynomial(xs, ys, degree=degree)
            return self._safe_json({"success": True, "degree": degree, "coefficients": coeffs})
        except Exception as e:
            return self._safe_json({"success": False, "error": str(e)})

    @Slot(str, str, result=str)
    def solveLinearSystemAxEqB(self, matrix_a_json: str, vector_b_json: str) -> str:
        """Solve Ax = b linear equation system using Gaussian Elimination."""
        from .core.statistics_engine import MatrixEngine
        try:
            a = json.loads(matrix_a_json)
            b = json.loads(vector_b_json)
            sol = MatrixEngine.solve_linear_system(a, b)
            return self._safe_json({"success": True, "solution": sol})
        except Exception as e:
            return self._safe_json({"success": False, "error": str(e)})

    @Slot(str, result=str)
    def calculateAudioMetrics(self, samples_json: str) -> str:
        """Compute RMS, peak amplitude, crest factor, and dBFS for audio buffer."""
        from .core.audio_dsp import AudioMetrics
        try:
            samples = json.loads(samples_json)
            metrics = AudioMetrics.calculate(samples)
            return self._safe_json(metrics)
        except Exception as e:
            return self._safe_json({"error": str(e)})


# Global singleton instance
backend_bridge = BackendBridge()

