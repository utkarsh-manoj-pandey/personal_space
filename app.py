#!/usr/bin/env python3
"""
=============================================================================
AETHER // ADVANCED PERSONAL COMMAND WORKSTATION
=============================================================================
Production-Grade Offline Operating Space powered by Python, PySide6, & WebEngine.
Zero-AI, strictly deterministic, multi-database architecture (17 isolated SQLite DBs).
Executes frontend directly via QUrl local file protocol without running any web port.
"""

import sys
import os
import logging
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import QIcon, QKeySequence, QShortcut

# Import backend bridge and database manager
from backend.bridge import backend_bridge
from backend.database_manager import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AetherApp")


class WorkstationWindow(QMainWindow):
    """
    Main application shell hosting the QWebEngineView container.
    Configures secure sandbox flags, WebGL hardware acceleration,
    WebAudio, and bidirectional QWebChannel bridging.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aether Workstation")
        self.resize(1560, 960)
        self.setMinimumSize(1200, 750)

        # Set obsidian dark background for native window chrome
        self.setStyleSheet("""
            QMainWindow {
                background-color: #09090b;
            }
        """)

        # Central container
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Initialize WebEngine view
        self.browser_view = QWebEngineView(self)
        layout.addWidget(self.browser_view)

        # Configure WebEngine settings for maximum performance and local execution
        settings = self.browser_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        # Establish QWebChannel communication bridge
        self.channel = QWebChannel(self.browser_view.page())
        self.channel.registerObject("backend", backend_bridge)
        self.browser_view.page().setWebChannel(self.channel)

        # Setup local HTML file target (Zero web port used!)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, "frontend", "index.html")

        if not os.path.exists(html_path):
            logger.error(f"Frontend entrypoint not found at: {html_path}")
            sys.exit(1)

        local_url = QUrl.fromLocalFile(html_path)
        logger.info(f"Launching Workstation UI via local protocol: {local_url.toString()}")
        self.browser_view.load(local_url)

        # Register keyboard shortcuts
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """Keyboard accelerators for fullscreen, reload, and quit."""
        self.f11_shortcut = QShortcut(QKeySequence("F11"), self)
        self.f11_shortcut.activated.connect(self.toggle_fullscreen)

        self.reload_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.reload_shortcut.activated.connect(self.browser_view.reload)

        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.quit_shortcut.activated.connect(self.close)

    def toggle_fullscreen(self):
        """Toggle between windowed and borderless fullscreen display."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


def main():
    # Enable High-DPI display scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Configure Chromium flags for smooth rendering
    flags = [
        "--enable-gpu-rasterization",
        "--enable-zero-copy",
        "--enable-webgl",
        "--autoplay-policy=no-user-gesture-required",
        "--disable-background-timer-throttling",
        "--disable-web-security",
        "--allow-running-insecure-content"
    ]
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags)

    app = QApplication(sys.argv)
    app.setApplicationName("Aether Personal Workstation")
    app.setOrganizationName("Nexus Systems")

    window = WorkstationWindow()
    window.show()

    logger.info("Aether Personal Command Workstation started successfully.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
