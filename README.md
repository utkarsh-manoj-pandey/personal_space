# AETHER // PERSONAL COMMAND WORKSTATION

Production-grade, offline-first personal command environment built purely on Python, PySide6, QtWebEngine, and 17 isolated SQLite databases. Engineered with a strictly deterministic, non-AI posture and zero telemetry.

The frontend is executed directly inside the PySide6 WebEngine sandbox using the local file URL protocol (`QUrl.fromLocalFile(...)`), communicating bidirectionally with the Python backend via `QWebChannel`. No local web ports or HTTP servers are run.

---

## 1. System Overview and Philosophy

Modern desktop productivity tools increasingly rely on mandatory cloud logins, proprietary copilot telemetry, remote subscription licensing, and opaque background data collection. 

Aether is designed with the opposing philosophy:
- **Absolute Local Sovereignty**: All data remains strictly on the host file system. There are no remote sync servers, no telemetry pings, and no cloud dependencies.
- **Deterministic, AI-Free Logic**: Every decision tree, scheduling algorithm, mathematical solver, and game engine executes through deterministic algorithms (such as Minimax with Alpha-Beta pruning) rather than stochastic Large Language Models.
- **Subsystem Database Isolation**: Rather than a monolithic database where corruption risks the entire suite, each of the 17 core subsystems maintains its own isolated SQLite database in Write-Ahead Logging (WAL) mode.
- **Sandboxed Local Execution**: The frontend application is a unified, cyber-tactical interface rendered via Chromium within PySide6's QtWebEngineView, communicating directly with native Python through IPC slots rather than exposed network sockets.

---

## 2. Persistence Architecture: 17 Isolated Subsystems

All databases reside in the `./data` directory. Each database enforces foreign keys (`PRAGMA foreign_keys = ON;`), enables Write-Ahead Logging (`PRAGMA journal_mode = WAL;`), and uses normal synchronous writes (`PRAGMA synchronous = NORMAL;`) for high concurrent read/write throughput.

| # | Subsystem | Database Target | Schema and Capabilities |
|---|---|---|---|
| 1 | Personal Calendar | `data/calendar.db` | Event scheduling, recurring intervals (daily, weekly, monthly), priority levels, category color tagging, and RFC 5545 iCalendar (`.ics`) export/import. |
| 2 | Privacy Web Browser | `data/browser.db` | Anti-fingerprinting profiles, User-Agent rotation (Tor Browser hardened, Linux Firefox ESR, macOS Safari), zero-tracking search engine routing (DuckDuckGo, Brave, Startpage, SearXNG, Qwant), and local bookmark storage. |
| 3 | Notepad & Markdown Studio | `data/notepad.db` | Real-time word count, character count, estimated reading time, tag taxonomies, pinned documents, live rendered preview, and multi-format text export. |
| 4 | Music Player & Soundscapes | `data/music.db` | Dual-harmonic binaural ambient audio synthesizer (built with Python's standard `wave` and `math` libraries), WebAudio frequency oscilloscope visualizer, MP3/WAV/FLAC/OGG library indexing. |
| 5 | Video Cinema Player | `data/video.db` | Frame-accurate timestamp bookmarking, playback rate scaling (0.25x to 2.0x), aspect ratio control, local MP4/WebM/MKV playback engine. |
| 6 | Document Viewer | `data/documents.db` | Universal reader for PDF (text extraction via `pypdf`), Markdown, Plain Text, JSON, CSV, and Source Code with line enumeration and marginal annotations. |
| 7 | Internet Radio Streams | `data/radio.db` | High-definition curated global streaming matrix (SomaFM, Nightwave Plaza, BBC World Service, KUSC Classical, Swiss Jazz, Cyberpunk Industrial), stream health checker, custom station adder. |
| 8 | Weather Systems | `data/weather.db` | Keyless Open-Meteo scientific forecast models, IP-based auto-geolocation, 24-hour hourly trajectory, 7-day forecast cards, and offline SQLite telemetry caching. |
| 9 | News Aggregator | `data/news.db` | Multi-source RSS/Atom parser (Geopolitics, Technology, Cybersecurity, Space Exploration), distraction-free reader mode, unread/bookmark tracking, offline cache. |
| 10 | Tactical Calculator | `data/calculator.db` | Safe Abstract Syntax Tree (AST) expression evaluation (preventing arbitrary code execution), Scientific trigonometry/logarithms, and synchronized Programmer base registers (Hex, Dec, Oct, Bin). |
| 11 | Image Catalog & Lab | `data/images.db` | Image metadata extraction (dimensions, format, color space via `Pillow`), non-destructive real-time CSS filters (brightness, contrast, saturation, hue), 90-degree lossless rotation. |
| 12 | World Clocks & Timers | `data/clocks.db` | Synchronized global strategic timezones (UTC, New York, London, Zurich, Dubai, Tokyo, Sydney, Singapore), millisecond stopwatch with split lap ledger, Pomodoro focus sprints. |
| 13 | Maps & Navigation | `data/maps.db` | 100% Free OpenStreetMap vector tiles, CartoDB Dark Matter styling, Nominatim keyless geocoding, OSRM turn-by-turn routing with distance and travel time. |
| 14 | World Monitor Dashboard | `data/world_monitor.db` | Palantir-inspired tactical situational dashboard: Three.js 3D Earth wireframe globe, live USGS earthquake feeds, International Space Station (ISS) orbital track, cyber threat vectors, and subsea fiber corridors. |
| 15 | Task & Schedule Planner | `data/planner.db` | 4-Stage Kanban workflow (Backlog, InProgress, Review, Completed), Eisenhower Matrix quadrants (Urgent vs Important), and 24-hour daily hourly timeblock maker. |
| 16 | Contact Vault | `data/contacts.db` | Comprehensive address book, relationship categorizations, communication interaction logs (calls, meetings, notes), and RFC 2426 vCard 3.0 export. |
| 17 | Python Game Suite | `data/games.db` | Algorithmic game engines built purely with Python: Chess with Minimax search and Alpha-Beta pruning, Connect 4 gravity solver with heuristic weighting, Retro Space Defender, and Neural Minesweeper. |

---

## 3. Technology Stack

- **Backend**: Python 3.10+
  - `PySide6`: Desktop application framework, window chrome, and system integration.
  - `PySide6.QtWebEngineWidgets`: Chromium-based local runtime container.
  - `PySide6.QtWebChannel`: High-speed IPC bridge binding Python methods to JavaScript.
  - `sqlite3`: Isolated database engines running in WAL mode.
  - `psutil`: Real-time CPU, RAM, and hardware telemetry monitoring.
  - `pypdf`: Local PDF text and structural parsing.
  - `Pillow`: Image decoding and EXIF metadata extraction.
  - `wave` & `struct`: Algorithmic procedural audio synthesis.
- **Frontend**:
  - `Vanilla HTML5` & `Vanilla JavaScript (ES6+)`: Application logic, state management, and tab routing.
  - `Tailwind CSS`: Cyber-tactical obsidian UI framework.
  - `Three.js`: 3D WebGL Keplerian orbital mechanics and wireframe Earth globe.
  - `Leaflet.js`: Interactive mapping and OpenStreetMap rendering.
  - `Web Audio API`: Real-time audio spectrum analysis and canvas oscilloscope visualization.

---

## 4. Directory Structure

```text
personal_space/
├── app.py                      # Main PySide6 Qt application launcher
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
├── .gitignore                  # Git exclusions for cache and runtime files
├── data/                       # 17 Isolated Subsystem SQLite Databases & Media
│   ├── calendar.db
│   ├── browser.db
│   ├── notepad.db
│   ├── music.db
│   ├── video.db
│   ├── documents.db
│   ├── radio.db
│   ├── weather.db
│   ├── news.db
│   ├── calculator.db
│   ├── images.db
│   ├── clocks.db
│   ├── maps.db
│   ├── world_monitor.db
│   ├── planner.db
│   ├── contacts.db
│   ├── games.db
│   ├── audio/                  # Synthesized ambient master soundscapes
│   ├── documents/              # Stored local documentation
│   └── images/                 # Stored tactical wallpaper graphics
├── backend/
│   ├── __init__.py
│   ├── database_manager.py     # SQLite manager for the 17 isolated databases
│   ├── bridge.py               # QWebChannel RPC bridge exposing Python slots
│   └── modules/
│       ├── calendar_service.py
│       ├── browser_service.py
│       ├── notepad_service.py
│       ├── music_service.py
│       ├── video_service.py
│       ├── document_service.py
│       ├── radio_service.py
│       ├── weather_service.py
│       ├── news_service.py
│       ├── calculator_service.py
│       ├── image_service.py
│       ├── clock_service.py
│       ├── maps_service.py
│       ├── world_monitor_service.py
│       ├── planner_service.py
│       ├── contact_service.py
│       ├── game_service.py
│       └── system_service.py
├── frontend/
│   ├── index.html              # Unified futuristic single-page application
│   └── vendor/                 # Offline local libraries (Zero CDN reliance)
│       ├── qwebchannel.js
│       ├── tailwind.js
│       ├── three.min.js
│       ├── leaflet.js
│       └── leaflet.css
└── tests/
    └── test_subsystems.py      # Automated test suite covering all 17 subsystems
```

---

## 5. Installation & Setup

### Prerequisites

Ensure you have Python 3.10 or newer installed:
```bash
python3 --version
```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/utkarsh-manoj-pandey/personal_space.git
   cd personal_space
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## 6. Running the Application

Launch the desktop workstation:
```bash
python3 app.py
```

### System Hotkeys
- `Ctrl + K`: Open Universal Command Palette to search across all subsystems.
- `F11`: Toggle between windowed and borderless fullscreen display.
- `Ctrl + R`: Reload the active workstation interface.
- `Ctrl + Q`: Cleanly terminate the application and close all database connections.

---

## 7. Verification and Testing

A comprehensive automated test suite validates database integrity, RPC slot serialization, and service logic across all 17 subsystems:

```bash
PYTHONPATH=. pytest tests/test_subsystems.py -v
```

Expected output:
```text
============================= 19 passed in 14.09s ==============================
```

---

## 8. Continuous Git Update Workflow

To update your workstation, commit your work, and synchronize changes with GitHub:

1. Check current repository status:
   ```bash
   git status
   ```

2. Stage all modifications:
   ```bash
   git add .
   ```

3. Commit changes with a descriptive message:
   ```bash
   git commit -m "feat(subsystem): describe your updates here"
   ```

4. Push updates to the main branch:
   ```bash
   git push origin main
   ```

---

## 9. Security & Privacy Guarantees

- **Zero Cloud Leakage**: No telemetry, analytics, or behavioral cookies are embedded.
- **Local AST Evaluation**: The calculator avoids unsafe `eval()` calls by using Python's `ast.NodeVisitor` with an explicit whitelist of mathematical operations.
- **Parametrized SQL Queries**: Every database transaction is executed via prepared statements, neutralizing SQL injection vectors.
- **Independent Failure Domains**: If any single database encounters an issue, the remaining 16 subsystems operate unaffected.
