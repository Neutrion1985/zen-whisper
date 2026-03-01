import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QCheckBox, QScrollArea, 
                             QFrame, QApplication, QProgressBar, QSlider,
                             QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QIcon, QFont, QKeySequence
import sounddevice as sd
from zenwhisper.core.recorder import recorder
from zenwhisper.core.translator import translator
from zenwhisper.core.config import config

class GlassWindow(QWidget):
    """Base class for premium glassmorphic windows."""
    def __init__(self, title_key="app_title", width=400, height=500):
        super().__init__()
        self.title_key = title_key
        self.setWindowTitle(translator.get(title_key))
        self.setFixedSize(width, height)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #121218;
                color: #E0E0E0;
                font-family: 'Segoe UI', Roboto, sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                background-color: #1F1F2E;
                border: 1px solid #33334D;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                color: #00FFFF;
            }
            QPushButton:hover {
                background-color: #2D2D44;
                border-color: #00FFFF;
            }
            QComboBox {
                background-color: #1F1F2E;
                border: 1px solid #33334D;
                border-radius: 8px;
                padding: 5px;
                color: white;
            }
            QCheckBox {
                spacing: 10px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QSlider::groove:horizontal {
                border: 1px solid #33334D;
                height: 8px;
                background: #1F1F2E;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00FFFF;
                border: 1px solid #00CCCC;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #006666, stop:1 #00FFFF);
                border-radius: 4px;
            }
        """)

    def retranslate_ui(self):
        self.setWindowTitle(translator.get(self.title_key))


class HotkeyButton(QPushButton):
    """Custom button that captures keyboard shortcuts."""
    hotkey_changed = pyqtSignal(str)
    
    def __init__(self, current_hotkey="<ctrl>+<f12>"):
        super().__init__()
        self.current_hotkey = current_hotkey
        self._recording = False
        self._keys = []
        self.update_label()
        self.clicked.connect(self.start_recording)
        
    def update_label(self):
        display = self.current_hotkey.replace("<", "").replace(">", "").replace("+", " + ").title()
        self.setText(f"🎹 {display}")
    
    def start_recording(self):
        self._recording = True
        self._keys = []
        self.setText(translator.get("hotkey_press"))
        self.setStyleSheet("background-color: #2D2D44; border-color: #FF6600; color: #FF6600;")
        self.grabKeyboard()
    
    def keyPressEvent(self, event):
        if not self._recording:
            super().keyPressEvent(event)
            return
        
        key = event.key()
        modifiers = event.modifiers()
        
        # Ignore lone modifier keys
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
        
        # Build pynput-compatible hotkey string
        parts = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("<ctrl>")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("<alt>")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("<shift>")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            parts.append("<cmd>")
        
        # Get key character
        key_text = QKeySequence(key).toString().lower()
        if key_text:
            parts.append(key_text)
        
        if parts:
            self.current_hotkey = "+".join(parts)
            self.hotkey_changed.emit(self.current_hotkey)
        
        self._recording = False
        self.releaseKeyboard()
        self.setStyleSheet("")  # Reset style
        self.update_label()
    
    def focusOutEvent(self, event):
        if self._recording:
            self._recording = False
            self.releaseKeyboard()
            self.setStyleSheet("")
            self.update_label()
        super().focusOutEvent(event)


class SettingsWindow(GlassWindow):
    def __init__(self):
        super().__init__("app_title", 600, 850)
        
        # Use a scroll area for the entire settings to handle overflow
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        # Header
        self.header = QLabel(translator.get("settings"))
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00FFFF;")
        layout.addWidget(self.header)
        
        # Language Selection
        lang_layout = QVBoxLayout()
        self.lang_label = QLabel(translator.get("lang_select"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.setCurrentText("Русский" if config.get("language") == "ru" else "English")
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # Microphone
        mic_layout = QVBoxLayout()
        self.mic_label = QLabel(translator.get("mic_device"))
        self.mic_combo = QComboBox()
        self.refresh_mic_list()
        mic_layout.addWidget(self.mic_label)
        mic_layout.addWidget(self.mic_combo)
        layout.addLayout(mic_layout)
        
        # Microphone Gain Slider
        gain_layout = QVBoxLayout()
        gain_value = config.get("mic_gain") or 1.0
        self.gain_label = QLabel(translator.get("mic_gain"))
        self.gain_value_label = QLabel(f"× {gain_value:.1f}")
        self.gain_value_label.setStyleSheet("color: #00FFFF; font-weight: bold; font-size: 16px;")
        
        gain_header = QHBoxLayout()
        gain_header.addWidget(self.gain_label)
        gain_header.addStretch()
        gain_header.addWidget(self.gain_value_label)
        
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setMinimum(10)  # 1.0x
        self.gain_slider.setMaximum(50)  # 5.0x
        self.gain_slider.setValue(int(gain_value * 10))
        self.gain_slider.valueChanged.connect(self._on_gain_changed)
        
        gain_layout.addLayout(gain_header)
        gain_layout.addWidget(self.gain_slider)
        layout.addLayout(gain_layout)
        
        # Hotkey
        hotkey_layout = QVBoxLayout()
        self.hotkey_label = QLabel(translator.get("hotkey_label"))
        current_hk = config.get("hotkey") or "<ctrl>+<f12>"
        self.hotkey_btn = HotkeyButton(current_hk)
        hotkey_layout.addWidget(self.hotkey_label)
        hotkey_layout.addWidget(self.hotkey_btn)
        layout.addLayout(hotkey_layout)
        
        # Sound Toggle
        self.sound_check = QCheckBox(translator.get("sound_feedback"))
        self.sound_check.setChecked(config.get("sound_enabled"))
        layout.addWidget(self.sound_check)
        
        # Autostart Toggle
        self.autostart_check = QCheckBox(translator.get("autostart"))
        self.autostart_check.setChecked(config.get("autostart"))
        layout.addWidget(self.autostart_check)
        
        # Model Selection
        model_layout = QVBoxLayout()
        self.model_label = QLabel(translator.get("ai_model"))
        self.model_desc = QLabel(translator.get("model_desc"))
        self.model_desc.setStyleSheet("font-size: 11px; color: #8888AA; font-style: italic;")
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large-v3"])
        self.model_combo.setCurrentText(config.get("model_size"))
        
        # Download Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #33334D;
                border-radius: 5px;
                text-align: center;
                height: 15px;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #00FFFF;
                width: 10px;
            }
        """)
        
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.progress_bar)
        model_layout.addWidget(self.model_desc)
        layout.addLayout(model_layout)
        
        layout.addStretch()
        
        # Save Button
        self.save_btn = QPushButton(translator.get("save_apply"))
        self.save_btn.clicked.connect(self.apply_settings)
        layout.addWidget(self.save_btn)

    def _on_gain_changed(self, value):
        gain = value / 10.0
        self.gain_value_label.setText(f"× {gain:.1f}")

    def retranslate_ui(self):
        try:
            super().retranslate_ui()
            self.header.setText(translator.get("settings"))
            self.lang_label.setText(translator.get("lang_select"))
            self.mic_label.setText(translator.get("mic_device"))
            self.gain_label.setText(translator.get("mic_gain"))
            self.hotkey_label.setText(translator.get("hotkey_label"))
            self.sound_check.setText(translator.get("sound_feedback"))
            self.autostart_check.setText(translator.get("autostart"))
            self.model_label.setText(translator.get("ai_model"))
            self.model_desc.setText(translator.get("model_desc"))
            self.save_btn.setText(translator.get("save_apply"))
            self.refresh_mic_list()
        except Exception as e:
            print(f"DEBUG: retranslate_ui error: {e}")

    def refresh_mic_list(self):
        current_data = self.mic_combo.currentData()
        
        self.mic_combo.clear()
        try:
            devices = sd.query_devices()
            default_idx = sd.default.device[0]
            
            self.mic_combo.addItem(translator.get("sys_default"), default_idx)
            
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    name = dev['name']
                    if "monitor" in name.lower() or "bridge" in name.lower():
                        continue
                    self.mic_combo.addItem(name, i)
        except Exception as e:
            print(f"DEBUG: Error refreshing mic list: {e}")
            self.mic_combo.addItem("Default", None)
        
        if current_data is not None:
            idx = self.mic_combo.findData(current_data)
            if idx >= 0:
                self.mic_combo.setCurrentIndex(idx)

    def apply_settings(self):
        old_lang = config.get("language")
        new_lang = self.lang_combo.currentData()
        
        # Save language
        config.set("language", new_lang)
        translator.set_language(new_lang)
        
        # Apply microphone
        device_idx = self.mic_combo.currentData()
        if device_idx is not None:
            config.set("microphone_id", device_idx)
            recorder.device_id = device_idx
        
        # Apply gain
        gain = self.gain_slider.value() / 10.0
        config.set("mic_gain", gain)
        recorder.gain = gain
        
        # Apply hotkey
        new_hotkey = self.hotkey_btn.current_hotkey
        old_hotkey = config.get("hotkey")
        config.set("hotkey", new_hotkey)
        
        # Apply sound feedback toggle
        from zenwhisper.core.audio_feedback import sounds
        enabled = self.sound_check.isChecked()
        config.set("sound_enabled", enabled)
        sounds.enabled = enabled
        
        # Apply autostart
        autostart_enabled = self.autostart_check.isChecked()
        config.set("autostart", autostart_enabled)
        self._set_autostart(autostart_enabled)
        
        # Apply model
        from zenwhisper.core.engine import engine
        new_model = self.model_combo.currentText()
        config.set("model_size", new_model)
        
        # Update UI text globally
        from zenwhisper.main import app_instance
        if app_instance:
            app_instance.update_translations()
            # Restart hotkey listener if hotkey changed
            if new_hotkey != old_hotkey:
                app_instance.hotkeys.restart(new_hotkey)

        if engine.set_model_size(new_model):
            self.start_model_download(new_model)
        else:
            self.hide()
        
        # Show restart hint if language changed
        if new_lang != old_lang:
            msg = QMessageBox(self)
            msg.setWindowTitle("ZenWhisper")
            msg.setText(translator.get("restart_required"))
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("QLabel { color: white; } QPushButton { min-width: 100px; }")
            restart_btn = msg.addButton(translator.get("restart_now"), QMessageBox.ButtonRole.AcceptRole)
            msg.addButton(translator.get("restart_later"), QMessageBox.ButtonRole.RejectRole)
            msg.exec()
            
            if msg.clickedButton() == restart_btn:
                # Restart the application
                os.execv(sys.executable, [sys.executable] + sys.argv)

    def _set_autostart(self, enabled):
        """Create or remove ~/.config/autostart/zenwhisper.desktop"""
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_file = autostart_dir / "zenwhisper.desktop"
        
        if enabled:
            autostart_dir.mkdir(parents=True, exist_ok=True)
            desktop_content = """[Desktop Entry]
Type=Application
Name=ZenWhisper
Comment=AI Voice Dictation
Exec=zenwhisper
Icon=zenwhisper
Terminal=false
Categories=Utility;Audio;
X-GNOME-Autostart-enabled=true
"""
            with open(autostart_file, 'w') as f:
                f.write(desktop_content)
            print(f"DEBUG: Autostart enabled: {autostart_file}")
        else:
            if autostart_file.exists():
                autostart_file.unlink()
                print(f"DEBUG: Autostart disabled: removed {autostart_file}")

    def start_model_download(self, model_name):
        from zenwhisper.core.downloader import ModelDownloader
        self.save_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.dl_thread = ModelDownloader(model_name)
        self.dl_thread.progress.connect(self.progress_bar.setValue)
        self.dl_thread.finished.connect(self.on_download_finished)
        self.dl_thread.start()

    def on_download_finished(self, success, message):
        self.save_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            from zenwhisper.core.engine import engine
            engine.load_model()
            self.hide()
        else:
            QMessageBox.critical(self, translator.get("download_error"), f"{translator.get('failed_download')}: {message}")

class HistoryWindow(GlassWindow):
    def __init__(self):
        super().__init__("history_title", 500, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.header = QLabel(translator.get("transcription_history"))
        self.header.setStyleSheet("font-size: 20px; font-weight: bold; color: #BF00FF;")
        layout.addWidget(self.header)
        
        # Scroll Area for history items
        self.scroll = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)
        
        # Initial placeholder
        self.add_item(translator.get("welcome"))

    def retranslate_ui(self):
        try:
            super().retranslate_ui()
            self.header.setText(translator.get("transcription_history"))
        except Exception as e:
            print(f"DEBUG: HistoryWindow retranslate error: {e}")

    def add_item(self, text):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1F1F2E;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 5px;
            }
        """)
        item_layout = QVBoxLayout(frame)
        
        label = QLabel(text)
        label.setWordWrap(True)
        item_layout.addWidget(label)
        
        copy_btn = QPushButton(translator.get("copy"))
        copy_btn.setFixedWidth(80)
        copy_btn.setStyleSheet("padding: 2px; font-size: 10px;")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(text))
        item_layout.addWidget(copy_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.scroll_layout.insertWidget(0, frame)
