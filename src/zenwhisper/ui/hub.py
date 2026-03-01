import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QFrame, 
                             QApplication, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit,
                             QListWidget, QListWidgetItem, QComboBox, 
                             QCheckBox, QProgressBar, QSlider, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent, QPointF
from PyQt6.QtGui import QIcon, QColor, QFont, QKeySequence, QPainter, QPen, QPixmap, QPolygonF
import sounddevice as sd
import tempfile

from zenwhisper.core.translator import translator
from zenwhisper.core.config import config
from zenwhisper.core.recorder import recorder
from zenwhisper.core.engine import engine
from zenwhisper.core.downloader import ModelDownloader, is_model_cached

def get_app_icon():
    """Helper to get the main application icon from standard paths."""
    icon_paths = [
        "/usr/share/zenwhisper/zenwhisper/assets/icon.png",
        "/usr/share/pixmaps/zenwhisper.png",
        str(Path(__file__).parent.parent / "assets" / "icon.png")
    ]
    for p in icon_paths:
        if os.path.exists(p):
            return QIcon(p)
    return QIcon()

def _create_zen_icons():
    """Generate PNG icon files on disk for use in QSS (Qt QSS only supports file:// paths)."""
    icon_dir = os.path.join(tempfile.gettempdir(), "zenwhisper_icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    # --- Checkmark icon (black check on transparent bg) ---
    check_path = os.path.join(icon_dir, "check.png")
    pm = QPixmap(16, 16)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor("black"), 2.5)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.drawLine(3, 8, 6, 12)
    p.drawLine(6, 12, 13, 4)
    p.end()
    pm.save(check_path)
    
    # --- Down arrow icon (cyan triangle on transparent bg) ---
    arrow_path = os.path.join(icon_dir, "arrow_down.png")
    pm2 = QPixmap(12, 12)
    pm2.fill(QColor(0, 0, 0, 0))
    p2 = QPainter(pm2)
    p2.setRenderHint(QPainter.RenderHint.Antialiasing)
    p2.setBrush(QColor("#00FFFF"))
    p2.setPen(Qt.PenStyle.NoPen)
    triangle = QPolygonF([QPointF(1, 3), QPointF(11, 3), QPointF(6, 9)])
    p2.drawPolygon(triangle)
    p2.end()
    pm2.save(arrow_path)
    
    return check_path, arrow_path

class HotkeyButton(QPushButton):
    """Custom button that captures keyboard shortcuts."""
    hotkey_changed = pyqtSignal(str)
    
    def __init__(self, current_hotkey="<alt>+z"):
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
        
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
        
        parts = []
        if modifiers & Qt.KeyboardModifier.ControlModifier: parts.append("<ctrl>")
        if modifiers & Qt.KeyboardModifier.AltModifier: parts.append("<alt>")
        if modifiers & Qt.KeyboardModifier.ShiftModifier: parts.append("<shift>")
        if modifiers & Qt.KeyboardModifier.MetaModifier: parts.append("<cmd>")
        
        key_text = QKeySequence(key).toString().lower()
        if key_text:
            # pynput requires special keys (F1-F12, etc.) wrapped in angle brackets
            # e.g. <f9>, <home>, <end>, <space>, <tab>, etc.
            # Single printable chars (a, z, 1, *) go as-is
            if len(key_text) > 1:
                key_text = f"<{key_text}>"
            parts.append(key_text)
        
        if parts:
            self.current_hotkey = "+".join(parts)
            self.hotkey_changed.emit(self.current_hotkey)
        
        self._recording = False
        self.releaseKeyboard()
        self.setStyleSheet("")
        self.update_label()

class SidebarButton(QPushButton):
    def __init__(self, icon_char, index):
        super().__init__()
        self.index = index
        self.setCheckable(True)
        self.setFixedSize(80, 80)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
                color: #8888AA;
                font-size: 28px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #1F1F2E;
                color: #00FFFF;
            }
            QPushButton:checked {
                background-color: #2D2D44;
                color: #00FFFF;
                border-left: 4px solid #00FFFF;
                border-radius: 0px 12px 12px 0px;
            }
        """)
        self.setText(icon_char)

class NavigationSidebar(QFrame):
    page_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(110)
        self.setStyleSheet("background-color: #121218; border-right: 1px solid #1F1F2E;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(10)
        
        self.buttons = []
        items = [("⚙️", "nav_settings"), ("🕒", "nav_history"), ("📚", "nav_vocabulary"), ("⚡", "nav_snippets")]
        
        for i, (icon, key) in enumerate(items):
            btn = SidebarButton(icon, i)
            btn.setToolTip(translator.get(key))
            btn.clicked.connect(self._on_btn_clicked)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            self.buttons.append(btn)
            
        layout.addStretch()
        self.buttons[0].setChecked(True)

    def _on_btn_clicked(self):
        btn = self.sender()
        for b in self.buttons: b.setChecked(False)
        btn.setChecked(True)
        self.page_changed.emit(btn.index)

class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        # Always ignore wheel events to let them bubble up to the scroll area
        event.ignore()

class NoWheelSlider(QSlider):
    def wheelEvent(self, event):
        # Always ignore wheel events to let them bubble up to the scroll area
        event.ignore()

class HubPage(QWidget):
    def __init__(self, title_key):
        super().__init__()
        self.title_key = title_key
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        self.header = QLabel(translator.get(title_key))
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00FFFF; margin-bottom: 0px;")
        
        self.description = QLabel(translator.get(title_key + "_desc"))
        self.description.setStyleSheet("font-size: 13px; color: #8888AA; font-style: italic; margin-top: -10px; margin-bottom: 10px;")
        self.description.setWordWrap(True)
        
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.description)

    def retranslate_ui(self):
        self.header.setText(translator.get(self.title_key))
        self.description.setText(translator.get(self.title_key + "_desc"))

class SettingsPage(HubPage):
    def __init__(self):
        super().__init__("nav_settings")
        
        # Main scroll area for the settings
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        self.page_layout = QVBoxLayout(container)
        self.page_layout.setContentsMargins(0, 0, 15, 0) # Margin for scrollbar
        self.page_layout.setSpacing(30) # More "air" between cards
        
        # Helper for glass cards
        def create_card(title_txt, layout_to_add=None):
            card = QFrame()
            card.setObjectName("PremiumCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(25, 25, 25, 25) # Professional padding
            card_layout.setSpacing(20)
            
            if title_txt:
                t = QLabel(title_txt)
                t.setStyleSheet("font-size: 13px; font-weight: bold; color: rgba(136, 136, 170, 0.8); text-transform: uppercase; letter-spacing: 1.5px;")
                card_layout.addWidget(t)
            
            if layout_to_add:
                card_layout.addLayout(layout_to_add)
            return card, card_layout

        # Language & Interface Card
        lang_group = QVBoxLayout()
        self.lang_combo = NoWheelComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.setCurrentText("Русский" if config.get("language") == "ru" else "English")
        lang_group.addWidget(self.lang_combo)
        
        card1, _ = create_card("🌐 " + translator.get("lang_select"), lang_group)
        self.page_layout.addWidget(card1)

        # Audio Input Card
        audio_group = QVBoxLayout()
        self.mic_combo = NoWheelComboBox()
        self.refresh_mic_list()
        audio_group.addWidget(self.mic_combo)

        gain_row = QHBoxLayout()
        gain_val = config.get("mic_gain") or 1.0
        self.gain_value_lbl = QLabel(f"{gain_val:.1f}x")
        self.gain_value_lbl.setStyleSheet("color: #00FFFF; font-weight: bold; min-width: 40px;")
        gain_row.addWidget(QLabel(translator.get("mic_gain")))
        gain_row.addStretch()
        gain_row.addWidget(self.gain_value_lbl)
        audio_group.addLayout(gain_row)
        
        self.gain_slider = NoWheelSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setRange(10, 50)
        self.gain_slider.setValue(int(gain_val * 10))
        self.gain_slider.valueChanged.connect(self._on_gain_changed)
        audio_group.addWidget(self.gain_slider)
        
        card2, _ = create_card("🎙️ " + translator.get("mic_device"), audio_group)
        self.page_layout.addWidget(card2)

        # Hotkey & System Card
        sys_group = QVBoxLayout()
        self.hotkey_btn = HotkeyButton(config.get("hotkey") or "<alt>+z")
        sys_group.addWidget(self.hotkey_btn)

        row_checks = QHBoxLayout()
        self.sound_check = QCheckBox(translator.get("sound_feedback"))
        self.sound_check.setChecked(config.get("sound_enabled"))
        self.autostart_check = QCheckBox(translator.get("autostart"))
        self.autostart_check.setChecked(config.get("autostart"))
        row_checks.addWidget(self.sound_check)
        row_checks.addSpacing(40)
        row_checks.addWidget(self.autostart_check)
        sys_group.addLayout(row_checks)
        
        card3, _ = create_card("⌨️ " + translator.get("hotkey_label"), sys_group)
        self.page_layout.addWidget(card3)

        # AI Model Card
        model_group = QVBoxLayout()
        self.model_combo = NoWheelComboBox()
        # capacities: tiny ~75MB, base ~145MB, small ~485MB, medium ~1.5GB, large-v3 ~3.1GB
        models = [
            ("tiny (~75MB)", "tiny"),
            ("base (~145MB)", "base"),
            ("small (~485MB)", "small"),
            ("medium (~1.5GB)", "medium"),
            ("large-v3 (~3.1GB)", "large-v3")
        ]
        for name, key in models:
            self.model_combo.addItem(name, key)
            
        current_model = config.get("model_size")
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == current_model:
                self.model_combo.setCurrentIndex(i)
                break
        
        # Progress Card
        card4_content = QVBoxLayout()
        card4_content.addWidget(self.model_combo)
        
        self.model_status = QLabel("")
        self.model_status.setStyleSheet("color: #8888AA; font-size: 12px; font-style: italic;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #0A0A0F; border: 1px solid #1F1F2E; border-radius: 5px; text-align: center; height: 10px; color: transparent; }
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00FFFF, stop:1 #0088FF); border-radius: 4px; }
        """)
        self.progress_bar.hide()
        card4_content.addWidget(self.model_status)
        card4_content.addWidget(self.progress_bar)
        
        card4, _ = create_card("🤖 " + translator.get("ai_model"), card4_content)
        self.page_layout.addWidget(card4)

        self.model_combo.currentIndexChanged.connect(self._on_model_selected)
        self.page_layout.addStretch()
        
        self.scroll.setWidget(container)
        self.layout.addWidget(self.scroll)
        
        self.page_layout.addStretch()

        self.save_btn = QPushButton(translator.get("btn_save"))
        self.save_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BC13FE, stop:1 #8A2BE2);
                border: none; 
                color: white; 
                font-weight: bold; 
                font-size: 14px;
                padding: 12px;
                margin-top: 10px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #CE46FF, stop:1 #9932CC); }
        """)
        self.save_btn.clicked.connect(self.save_and_restart)
        self.layout.addWidget(self.save_btn)

        # Initial check must happen AFTER save_btn is created
        self._on_model_selected()
    
    def _on_gain_changed(self, val):
        self.gain_value_lbl.setText(f"{val/10.0:.1f}x")

    def _on_model_selected(self):
        size = self.model_combo.currentData()
        if is_model_cached(size):
            self.model_status.setText(f"✅ {translator.get('model_installed')} ({size})")
            self.save_btn.setText(translator.get("btn_save"))
            self.progress_bar.hide()
        else:
            self.model_status.setText(f"☁️ {translator.get('model_not_installed')} ({size})")
            self.save_btn.setText(translator.get("btn_download"))
            self.progress_bar.hide()

    def start_download(self):
        size = self.model_combo.currentData()
        self.downloader = ModelDownloader(size)
        self.downloader.progress.connect(self.progress_bar.setValue)
        self.downloader.finished.connect(self._on_download_finished)
        
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.model_status.setText(f"🚀 {translator.get('downloading')} ({size})")
        
        self.save_btn.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.downloader.start()

    def _on_download_finished(self, success, message):
        self.save_btn.setEnabled(True)
        self.model_combo.setEnabled(True)
        if success:
            self.model_status.setText(f"✅ {translator.get('ready_to_apply')}")
            self.save_btn.setText(translator.get("btn_save"))
            self.progress_bar.setValue(100)
        else:
            self.model_status.setText(f"❌ {translator.get('download_error')}: {message}")
            self.save_btn.setText(translator.get("btn_download"))

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
            try:
                with open(autostart_file, 'w') as f:
                    f.write(desktop_content)
                print(f"DEBUG: Autostart enabled: {autostart_file}")
            except Exception as e:
                print(f"DEBUG: Error writing autostart file: {e}")
        else:
            if autostart_file.exists():
                try:
                    autostart_file.unlink()
                    print(f"DEBUG: Autostart disabled: removed {autostart_file}")
                except Exception as e:
                    print(f"DEBUG: Error removing autostart file: {e}")

    def refresh_mic_list(self):
        self.mic_combo.clear()
        try:
            self.mic_combo.addItem(translator.get("sys_default"), sd.default.device[0])
            for i, dev in enumerate(sd.query_devices()):
                if dev['max_input_channels'] > 0 and "monitor" not in dev['name'].lower():
                    self.mic_combo.addItem(dev['name'], i)
        except: pass

    def save_and_restart(self):
        # If button is in Download mode, start download instead
        if self.save_btn.text() == translator.get("btn_download"):
            self.start_download()
            return

        # Save all
        new_lang = self.lang_combo.currentData()
        config.set("language", new_lang)
        config.set("microphone_id", self.mic_combo.currentData())
        config.set("mic_gain", self.gain_slider.value() / 10.0)
        config.set("hotkey", self.hotkey_btn.current_hotkey)
        config.set("sound_enabled", self.sound_check.isChecked())
        autostart_enabled = self.autostart_check.isChecked()
        config.set("autostart", autostart_enabled)
        self._set_autostart(autostart_enabled)
        config.set("model_size", self.model_combo.currentData())
        
        # Immediate restart
        os.execv(sys.executable, [sys.executable] + sys.argv)

class HistoryPage(HubPage):
    def __init__(self):
        super().__init__("nav_history")
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.content = QWidget()
        self.hist_layout = QVBoxLayout(self.content)
        self.hist_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.content)
        self.layout.addWidget(self.scroll)
        self.add_item(translator.get("welcome"))

    def add_item(self, text):
        frame = QFrame()
        frame.setStyleSheet("background-color: #1F1F2E; border-radius: 10px; padding: 10px; margin-bottom: 5px;")
        l = QVBoxLayout(frame)
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        l.addWidget(lbl)
        copy_btn = QPushButton(translator.get("copy"))
        copy_btn.setFixedWidth(80)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(text))
        l.addWidget(copy_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.hist_layout.insertWidget(0, frame)

class VocabularyPage(HubPage):
    def __init__(self):
        super().__init__("nav_vocabulary")
        self.list = QListWidget()
        self.list.setStyleSheet("background-color: #1F1F2E; border-radius: 8px; padding: 5px;")
        self.layout.addWidget(self.list)
        
        # Load existing
        words = config.get("vocabulary") or []
        for w in words: self.list.addItem(w)
        
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText(translator.get("add_word"))
        add_btn = QPushButton("+")
        add_btn.setFixedWidth(40)
        add_btn.clicked.connect(self.add_word)
        row.addWidget(self.input)
        row.addWidget(add_btn)
        self.layout.addLayout(row)
        
        del_btn = QPushButton(translator.get("delete"))
        del_btn.clicked.connect(self.delete_selected)
        self.layout.addWidget(del_btn)

    def add_word(self):
        word = self.input.text().strip()
        if word:
            self.list.addItem(word)
            self.input.clear()
            self.save()

    def delete_selected(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))
        self.save()

    def save(self):
        words = [self.list.item(i).text() for i in range(self.list.count())]
        config.set("vocabulary", words)

class SnippetsPage(HubPage):
    def __init__(self):
        super().__init__("nav_snippets")
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([translator.get("trigger"), translator.get("expansion")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: #1F1F2E; gridline-color: #33334D;")
        self.layout.addWidget(self.table)
        
        # Load
        snippets = config.get("snippets") or {}
        for k, v in snippets.items(): self.add_row(k, v)
        
        row = QHBoxLayout()
        self.trigger_in = QLineEdit()
        self.trigger_in.setPlaceholderText(translator.get("trigger"))
        self.expansion_in = QLineEdit()
        self.expansion_in.setPlaceholderText(translator.get("expansion"))
        add_btn = QPushButton("+")
        add_btn.clicked.connect(self.add_snippet)
        row.addWidget(self.trigger_in)
        row.addWidget(self.expansion_in)
        row.addWidget(add_btn)
        self.layout.addLayout(row)
        
        del_btn = QPushButton(translator.get("delete"))
        del_btn.clicked.connect(self.delete_selected)
        self.layout.addWidget(del_btn)

    def add_row(self, trigger, expansion):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(trigger))
        self.table.setItem(r, 1, QTableWidgetItem(expansion))

    def add_snippet(self):
        t = self.trigger_in.text().strip()
        e = self.expansion_in.text().strip()
        if t and e:
            self.add_row(t, e)
            self.trigger_in.clear()
            self.expansion_in.clear()
            self.save()

    def delete_selected(self):
        self.table.removeRow(self.table.currentRow())
        self.save()

    def save(self):
        snips = {}
        for r in range(self.table.rowCount()):
            k = self.table.item(r, 0).text()
            v = self.table.item(r, 1).text()
            snips[k] = v
        config.set("snippets", snips)

class HubWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zen Hub")
        self.setMinimumSize(900, 850)
        self.setWindowIcon(get_app_icon())
        
        # Generate icon files on disk (Qt QSS only supports file:// paths, NOT data: URIs)
        self._check_path, self._arrow_path = _create_zen_icons()
        
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #050510; color: #E0E0E0; font-family: 'Segoe UI', 'Roboto', sans-serif; }
            
            #PremiumCard {
                background-color: rgba(31, 31, 46, 0.3);
                border: 1px solid rgba(0, 255, 255, 0.08);
                border-radius: 16px;
            }
            
            QPushButton { 
                background: rgba(31, 31, 46, 0.6); 
                border: 1px solid rgba(0, 255, 255, 0.15); 
                border-radius: 10px; 
                padding: 12px 20px; 
                color: #00FFFF;
                font-weight: 600;
                font-size: 13px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover { 
                background-color: rgba(0, 255, 255, 0.1); 
                border-color: #00FFFF;
                color: #FFFFFF;
            }
            
            QComboBox, QLineEdit { 
                background-color: #0A0A15; 
                border: 1px solid rgba(255, 255, 255, 0.05); 
                border-radius: 8px; 
                padding: 10px 35px 10px 10px; 
                color: white; 
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(""" + self._arrow_path + """);
                width: 10px;
                height: 10px;
                margin-right: 12px;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: #00FFFF;
                background-color: #0F0F20;
            }
            
            QCheckBox { spacing: 15px; color: #AAAAAA; font-size: 13px; }
            QCheckBox::indicator { width: 22px; height: 22px; border-radius: 6px; background: #0A0A15; border: 1px solid rgba(0, 255, 255, 0.2); }
            QCheckBox::indicator:checked { 
                background: #00FFFF; 
                border-color: #00FFFF; 
                padding: 3px;
                image: url(""" + self._check_path + """);
            }
            
            /* Enhanced Slider */
            QSlider::groove:horizontal { 
                border: none; 
                height: 10px; 
                background: rgba(255,255,255,0.05); 
                border-radius: 5px; 
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00FFFF, stop:1 #0088FF);
                border-radius: 5px;
            }
            QSlider::handle:horizontal { 
                background: #FFFFFF; 
                border: 2px solid #00FFFF;
                width: 14px; 
                height: 22px; 
                margin: -7px 0; 
                border-radius: 5px; /* Square-oval shape */
            }
            
            /* Custom Scrollbar */
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 255, 255, 0.5);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollArea { border: none; background: transparent; }
        """)
        
        cw = QWidget()
        self.setCentralWidget(cw)
        l = QHBoxLayout(cw)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(0)
        
        self.sidebar = NavigationSidebar()
        self.sidebar.page_changed.connect(self.switch_page)
        l.addWidget(self.sidebar)
        
        self.stack = QStackedWidget()
        l.addWidget(self.stack)
        
        self.settings_page = SettingsPage()
        self.history_page = HistoryPage()
        self.vocab_page = VocabularyPage()
        self.snippets_page = SnippetsPage()
        
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.vocab_page)
        self.stack.addWidget(self.snippets_page)

        # Ensure autostart state is synced on launch
        self.settings_page._set_autostart(config.get("autostart"))

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

    def update_translations(self):
        self.setWindowTitle(translator.get("hub_title"))
        self.settings_page.retranslate_ui()
        self.history_page.retranslate_ui()
        self.vocab_page.retranslate_ui()
        self.snippets_page.retranslate_ui()
