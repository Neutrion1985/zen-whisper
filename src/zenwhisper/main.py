import sys
import os
import threading
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen, QPixmap
from PyQt6.QtCore import QCoreApplication, QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

# Force UTF-8 for all stdout/stderr communication
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from zenwhisper import __version__
from zenwhisper.core.audio_feedback import sounds
from zenwhisper.core.engine import engine
from zenwhisper.core.recorder import recorder
from zenwhisper.ui.waveform import WaveformWidget
from zenwhisper.ui.hub import HubWindow, SettingsPage
from zenwhisper.core.hotkey import HotkeyListener
from zenwhisper.core.typer import injector
from zenwhisper.core.config import config
from zenwhisper.core.translator import translator

# Global instance for cross-window communication
app_instance = None

class ZenController(QObject):
    transcription_ready = pyqtSignal(str)

    def __init__(self, app):
        super().__init__()
        self.app = app
        global app_instance
        app_instance = self
        
        # Ensure Autostart state is synced on launch
        try:
            self.settings_page = SettingsPage()
            self.settings_page._set_autostart(config.get("autostart"))
        except: pass

        self.app.setQuitOnLastWindowClosed(False)
        
        # 1. Apply Perspective/Config
        lang = config.get("language")
        translator.set_language(lang)
        
        mic_id = config.get("microphone_id")
        if mic_id is not None:
            recorder.device_id = mic_id
        
        # Apply mic gain
        recorder.gain = config.get("mic_gain") or 1.0
            
        sounds.enabled = config.get("sound_enabled")
        
        model_size = config.get("model_size")
        engine.set_model_size(model_size)
        engine.load_model()
        
        # Core windows
        self.waveform = WaveformWidget()
        self.hub_window = HubWindow()
        
        self.setup_tray()
        self.update_tray_menu()
        
        # 4. Engine & Hotkeys
        self.transcription_ready.connect(self.on_transcription_finished)
        engine.model_loaded.connect(self.on_model_loaded)
        
        self.hotkeys = HotkeyListener(self.on_toggle)
        self.hotkeys.start()
        
        # 5. IPC Server
        self.server = QLocalServer(self)
        self.server.removeServer("zenwhisper_socket")
        if self.server.listen("zenwhisper_socket"):
            self.server.newConnection.connect(self.handle_ipc)

        print(f"ZEN Whisper {__version__} Controller started. Language: {lang}")
        if engine.is_loading:
            self.tray.setToolTip(f"ZenWhisper - {translator.get('loading')}...")

    def on_model_loaded(self, success):
        if success:
            self.tray.setToolTip("ZenWhisper - Ready")
        else:
            self.tray.setToolTip("ZenWhisper - Error")

    def get_icon(self, state="normal"):
        # Base icon path search
        icon_paths = [
            "/usr/share/zenwhisper/zenwhisper/assets/icon.png",
            "/usr/share/pixmaps/zenwhisper.png",
            str(Path(__file__).parent / "assets" / "icon.png"),
            str(Path(__file__).parent.parent / "src" / "zenwhisper" / "assets" / "icon.png")
        ]
        base_icon_path = None
        for p in icon_paths:
            if os.path.exists(p):
                base_icon_path = p
                break
        
        if not base_icon_path:
            # Fallback
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QColor(150, 0, 255))
            painter.drawEllipse(16, 16, 32, 32)
            painter.end()
            base_icon = QIcon(pixmap)
        else:
            base_icon = QIcon(base_icon_path)

        if state == "normal":
            return base_icon
            
        # Create a dynamic icon with a colored border for 64x64 tray
        pixmap = base_icon.pixmap(64, 64)
        if pixmap.isNull():
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # High-visibility glow ring
        # recording -> Red (#FF0000), processing -> Green (#00FF00)
        ring_color = QColor(255, 0, 0) if state == "recording" else QColor(0, 255, 0)
        
        # Draw outer glow (semi-transparent)
        glow_pen = QPen(QColor(ring_color.red(), ring_color.green(), ring_color.blue(), 100))
        glow_pen.setWidth(8)
        painter.setPen(glow_pen)
        painter.drawEllipse(4, 4, 56, 56)
        
        # Draw core ring
        core_pen = QPen(ring_color)
        core_pen.setWidth(4)
        painter.setPen(core_pen)
        painter.drawEllipse(4, 4, 56, 56)
        
        painter.end()
        return QIcon(pixmap)

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self.app)
        self.tray.setIcon(self.get_icon())
        
        menu = QMenu()
        
        self.toggle_action = menu.addAction(translator.get("dictation_toggle"))
        self.toggle_action.triggered.connect(self.on_toggle)
        
        menu.addSeparator()
        
        settings_action = menu.addAction(translator.get("settings"))
        settings_action.triggered.connect(self.show_hub)
        
        menu.addSeparator()
        
        quit_action = menu.addAction(translator.get("quit"))
        quit_action.triggered.connect(self.quit_app)
        
        self.tray.setContextMenu(menu)
        self.tray.show()

    def update_tray_menu(self):
        # Fetch current hotkey and format it for display
        raw_hk = config.get("hotkey") or "<ctrl>+<f12>"
        # Simple formatting: remove angle brackets and capitalize
        display_hk = raw_hk.replace("<", "").replace(">", "").title()
        
        # Static label that covers both Start and Stop
        base_text = translator.get("dictation_toggle")
        self.toggle_action.setText(f"{base_text} ({display_hk})")

    def show_hub(self):
        self.hub_window.show()
        self.hub_window.raise_()
        self.hub_window.activateWindow()

    def show_settings(self):
        self.hub_window.switch_page(0) # Settings is index 0
        self.show_hub()

    def show_history(self):
        self.hub_window.switch_page(1) # History is index 1
        self.show_hub()

    def on_transcription_finished(self, text):
        if not text or not text.strip():
            # Reset icon to normal if nothing found
            self.tray.setIcon(self.get_icon("normal"))
            return
            
        start_t = time.perf_counter()
        # apply snippets expansion
        processed_text = self.apply_snippets(text)
        
        # Priority 1: Inject to editor immediately
        injector.inject(processed_text)
        
        # Priority 2: Update UI history
        self.hub_window.history_page.add_item(processed_text)
        
        # Reset tray icon and hide waveform
        self.tray.setIcon(self.get_icon("normal"))
        self.waveform.hide_zen()
        
        end_t = time.perf_counter()
        print(f"DEBUG: on_transcription_finished total took {end_t - start_t:.4f}s")

    def apply_snippets(self, text):
        snippets = config.get("snippets") or {}
        if not snippets:
            return text
            
        lower_text = text.lower()
        processed = text
        
        # Sort triggers by length descending to match longest first
        sorted_triggers = sorted(snippets.keys(), key=len, reverse=True)
        
        for trigger in sorted_triggers:
            expansion = snippets[trigger]
            # Case-insensitive replacement while preserving rest of text
            # Very simple implementation: replace all occurrences
            import re
            pattern = re.compile(re.escape(trigger), re.IGNORECASE)
            processed = pattern.sub(expansion, processed)
            
        return processed

    def update_translations(self):
        self.update_tray_menu()
        self.hub_window.retranslate_ui()

    def handle_ipc(self):
        socket = self.server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self.on_socket_read(socket))

    def on_socket_read(self, socket):
        try:
            # Explicitly decode from UTF-8
            msg_bytes = socket.readAll().data()
            msg = msg_bytes.decode("utf-8", errors="replace")
            print(f"DEBUG: IPC Message received: {msg}")
            if msg == "toggle":
                self.on_toggle()
            elif msg == "show_settings":
                self.show_settings()
            elif msg == "show_history":
                self.show_history()
            socket.close()
        except Exception as e:
            print(f"DEBUG: IPC Error: {e}")

    def on_toggle(self):
        if not engine.model:
            msg = translator.get("loading")
            self.tray.showMessage("ZenWhisper", msg, QSystemTrayIcon.MessageIcon.Information, 2000)
            return
            
        if not recorder.recording:
            # START RECORDING
            self.tray.setIcon(self.get_icon("recording"))
            recorder.start_recording(level_callback=self.waveform.set_amplitude)
            sounds.play_start()
            self.waveform.show_zen()
            self.update_tray_menu()
        else:
            # STOP RECORDING -> START THINKING
            self.tray.setIcon(self.get_icon("processing"))
            sounds.play_stop()
            self.waveform.show_processing()
            self.update_tray_menu()
            stop_recattr = time.perf_counter()
            wav_path = recorder.stop_recording()
            print(f"DEBUG: recorder.stop_recording() took {time.perf_counter() - stop_recattr:.4f}s")
            if wav_path:
                threading.Thread(target=self.process_transcription, args=(wav_path,), daemon=True).start()
            else:
                self.tray.setIcon(self.get_icon("normal"))

    def process_transcription(self, wav_path):
        # Already handled by state change in on_toggle
        try:
            text = engine.transcribe(wav_path)
            if text:
                self.transcription_ready.emit(text)
            else:
                self.tray.setIcon(self.get_icon("normal"))
        except Exception as e:
            print(f"DEBUG: Error during transcription: {e}")
            self.tray.setIcon(self.get_icon("normal"))
            self.waveform.hide_zen()

    def quit_app(self):
        print("Closing ZenWhisper...")
        try:
            self.server.close()
            self.server.removeServer("zenwhisper_socket")
        except:
            pass
        self.tray.hide()
        QCoreApplication.quit()

def main():
    # Logging for debug during menu launch
    log_file = "/tmp/zenwhisper.log"
    try:
        # Use line-buffered output in UTF-8
        sys.stdout = open(log_file, "a", encoding="utf-8", buffering=1)
        sys.stderr = open(log_file, "a", encoding="utf-8", buffering=1)
    except Exception as e:
        print(f"DEBUG: Failed to redirect logs: {e}")
        
    print(f"\n--- ZenWhisper v{__version__} Starting ---")
    
    app = QApplication(sys.argv)
    
    # Critical for Linux taskbar icon association
    app.setApplicationName("zenwhisper")
    app.setDesktopFileName("zenwhisper")
    
    # Global taskbar icon (must be set BEFORE window creation)
    # Reuse controller's icon logic or a simple helper
    icon_paths = [
        "/usr/share/zenwhisper/zenwhisper/assets/icon.png",
        "/usr/share/pixmaps/zenwhisper.png",
        str(Path(__file__).parent / "assets" / "icon.png")
    ]
    for p in icon_paths:
        if os.path.exists(p):
            app.setWindowIcon(QIcon(p))
            break
            
    app_name = "zenwhisper_socket"
    
    if "--kill" in sys.argv:
        print("Killing any existing ZenWhisper instances...")
        # Simple cross-platform approach: remove socket and exit
        # On Linux, we can be more aggressive if needed
        QLocalServer.removeServer(app_name)
        # Also clean up /tmp if QLocalServer missed it
        if os.path.exists("/tmp/zenwhisper_socket"):
            os.remove("/tmp/zenwhisper_socket")
        print("Cleaned up IPC socket.")
        return

    # Check for another instance
    test_socket = QLocalSocket()
    test_socket.connectToServer(app_name)
    
    if test_socket.waitForConnected(300):
        # Found another instance!
        print("Found existing instance. Redirecting...")
        if "--toggle" in sys.argv:
            test_socket.write("toggle".encode())
        elif "--settings" in sys.argv:
            test_socket.write("show_settings".encode())
        elif "--history" in sys.argv:
            test_socket.write("show_history".encode())
        else:
            # Default behavior if run without args but already running
            test_socket.write("show_settings".encode())
            
        test_socket.waitForBytesWritten(500)
        test_socket.close()
        return
    else:
        # Connection failed. If socket file exists, it might be stale.
        if os.path.exists("/tmp/zenwhisper_socket"):
            print("Detected stale socket file. Removing...")
            os.remove("/tmp/zenwhisper_socket")
        # Ensure QLocalServer is ready
        QLocalServer.removeServer(app_name)

    # No other instance. Start the controller.
    try:
        controller = ZenController(app)
        sys.exit(app.exec())
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
