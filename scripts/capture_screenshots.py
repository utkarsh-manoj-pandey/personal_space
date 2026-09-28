import sys
import os
from pathlib import Path
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from PySide6.QtWebEngineCore import QWebEngineSettings
from backend.bridge import BackendBridge

def main():
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    app = QApplication(sys.argv)
    
    view = QWebEngineView()
    view.resize(1440, 900)
    view.setWindowTitle("Aether Screenshot Capture Pipeline")

    settings = view.settings()
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
    
    channel = QWebChannel()
    bridge = BackendBridge(view)
    channel.registerObject("backend", bridge)
    view.page().setWebChannel(channel)
    
    html_path = BASE_DIR / "frontend" / "index.html"
    view.load(QUrl.fromLocalFile(str(html_path)))
    view.show()
    
    out_dir = BASE_DIR / "docs" / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    tabs_to_capture = [
        ("home", "00_home_dashboard.png", "", 3000),
        ("world_monitor", "01_world_monitor.png", "", 3500),
        ("maps", "02_maps_navigation.png", "if(leafletMapInstance){leafletMapInstance.invalidateSize(); calculateRouteBtn();}", 3500),
        ("documents", "03_document_viewer.png", "", 2500),
        ("browser", "04_privacy_browser.png", "", 2500),
        ("notepad", "05_notepad_markdown.png", "", 2000),
        ("games", "06_chess_game_engine.png", "onChessSquareClick(6, 4);", 2000),
        ("planner", "07_task_planner.png", "", 2000),
        ("calculator", "08_tactical_calculator.png", "setCalcMode('Programmer'); calcInput('255'); setTimeout(calcCompute, 200);", 2500),
        ("weather", "09_weather_systems.png", "", 2500),
        ("calendar", "10_personal_calendar.png", "", 2000),
        ("music", "11_music_soundscapes.png", "", 2000),
        ("settings", "12_workspace_settings.png", "", 2500),
    ]
    
    step = 0
    
    def process_step():
        nonlocal step
        if step < len(tabs_to_capture):
            tab_id, filename, extra_js, wait_ms = tabs_to_capture[step]
            print(f"[SCREENSHOT] Switching to tab: {tab_id}...")
            view.page().runJavaScript(f"switchTab('{tab_id}');")
            if extra_js:
                QTimer.singleShot(600, lambda js=extra_js: view.page().runJavaScript(js))
            
            def grab_and_next():
                nonlocal step
                target_file = out_dir / filename
                pixmap = view.grab()
                pixmap.save(str(target_file), "PNG")
                print(f"[SCREENSHOT] Saved: {target_file} ({pixmap.width()}x{pixmap.height()})")
                step += 1
                QTimer.singleShot(400, process_step)
                
            QTimer.singleShot(wait_ms, grab_and_next)
        else:
            print("[SCREENSHOT] All captures completed successfully.")
            app.quit()
            
    # Initial page startup delay
    QTimer.singleShot(4000, process_step)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
