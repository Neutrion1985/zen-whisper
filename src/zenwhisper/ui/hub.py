import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QFrame, 
                             QApplication, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit,
                             QListWidget, QListWidgetItem, QComboBox, 
                             QCheckBox, QProgressBar, QSlider, QMessageBox,
                             QGridLayout, QSizePolicy, QAbstractButton)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent, QPointF, QByteArray, QBuffer, QIODevice, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt6.QtGui import QIcon, QColor, QFont, QKeySequence, QPainter, QPen, QBrush, QPixmap, QPolygonF, QRadialGradient
import sounddevice as sd
import tempfile

from zenwhisper.core.translator import translator
from zenwhisper.core.config import config
from zenwhisper.core.recorder import recorder
from zenwhisper.core.engine import engine
from zenwhisper.core.downloader import ModelDownloader, is_model_cached
from zenwhisper.ui.base import HubPage
from zenwhisper.ui.styles import ZenColors, ZenStyles
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

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
    """Generate PNG icons. Returns (check_path, arrow_base64)."""
    icon_dir = os.path.join(tempfile.gettempdir(), "zenwhisper_icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    # 1. Check icon (stays as file for QTableWidget/QIcon)
    check_path = os.path.join(icon_dir, "check.png")
    pm = QPixmap(16, 16)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor("black"), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.drawLine(3, 8, 6, 12)
    p.drawLine(6, 12, 13, 4)
    p.end()
    pm.save(check_path)
    
    # 2. Arrow icon as Base64 for QSS
    pm2 = QPixmap(16, 16)
    pm2.fill(QColor(0, 0, 0, 0))
    p2 = QPainter(pm2)
    p2.setRenderHint(QPainter.RenderHint.Antialiasing)
    p2.setPen(QPen(QColor(ZenColors.PRIMARY), 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p2.drawLine(4, 6, 8, 10)
    p2.drawLine(8, 10, 12, 6)
    p2.end()
    
    ba = QByteArray()
    buffer = QBuffer(ba)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pm2.save(buffer, "PNG")
    arrow_base64 = f"data:image/png;base64,{ba.toBase64().data().decode()}"
    
    return check_path, arrow_base64

class PremiumAddButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(45, 45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(ZenStyles.BUTTON_PREMIUM + "padding: 0px;")

    def paintEvent(self, event):
        # Draw the button base (hover/pressed effects from QSS)
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        margin = 14
        
        # Use white for the plus, with 3px thickness
        pen = QPen(QColor("white"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw Plus
        painter.drawLine(margin, h // 2, w - margin, h // 2)
        painter.drawLine(w // 2, margin, w // 2, h - margin)

class PremiumCopyButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(ZenStyles.BUTTON_PREMIUM + "padding: 0px; border-radius: 6px;")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        
        # Draw Copy Icon (two overlapping squares)
        pen = QPen(QColor("white"), 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        # Sizes
        sw = 9
        sh = 11
        
        # Bottom/Back paper
        painter.drawRoundedRect(w // 2 - sw // 2 + 2, h // 2 - sh // 2 + 2, sw, sh, 1, 1)
        # Top/Front paper
        painter.setBrush(QBrush(QColor(ZenColors.PRIMARY)))
        painter.drawRoundedRect(w // 2 - sw // 2 - 1, h // 2 - sh // 2 - 1, sw, sh, 1, 1)

class HotkeyButton(QPushButton):
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
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta): return
        parts = []
        if modifiers & Qt.KeyboardModifier.ControlModifier: parts.append("<ctrl>")
        if modifiers & Qt.KeyboardModifier.AltModifier: parts.append("<alt>")
        if modifiers & Qt.KeyboardModifier.ShiftModifier: parts.append("<shift>")
        if modifiers & Qt.KeyboardModifier.MetaModifier: parts.append("<cmd>")
        key_text = QKeySequence(key).toString().lower()
        if key_text:
            if len(key_text) > 1: key_text = f"<{key_text}>"
            parts.append(key_text)
        if parts:
            self.current_hotkey = "+".join(parts)
            self.hotkey_changed.emit(self.current_hotkey)
        self._recording = False
        self.releaseKeyboard()
        self.setStyleSheet("")
        self.update_label()

class NoWheelComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def wheelEvent(self, event): event.ignore()
    
    def paintEvent(self, event):
        # Сначала вызываем стандартную отрисовку для текста и фона
        super().paintEvent(event)
        
        # Затем рисуем нашу стрелочку-шеврон поверх в правой части
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Определяем область для стрелки (та же, что и QComboBox::drop-down)
        # В QSS у нас width: 40px
        arrow_rect = self.rect()
        arrow_rect.setLeft(arrow_rect.right() - 40)
        
        # Рисуем Chevron (V-shape)
        cx = arrow_rect.center().x()
        cy = arrow_rect.center().y()
        
        from zenwhisper.ui.styles import ZenColors
        # Используем яркий первичный цвет, чтобы было точно видно
        pen = QPen(QColor(ZenColors.PRIMARY), 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Птичка размером ~10x6
        painter.drawLine(cx - 5, cy - 2, cx, cy + 3)
        painter.drawLine(cx, cy + 3, cx + 5, cy - 2)
        painter.end()

class NoWheelSlider(QSlider):
    def wheelEvent(self, event): event.ignore()

class ZenSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(44, 24)
        self._thumb_pos = 2.0
        self._anim = QPropertyAnimation(self, b"thumb_pos", self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.setObjectName("ZenSwitch")

    @pyqtProperty(float)
    def thumb_pos(self): return self._thumb_pos
    @thumb_pos.setter
    def thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()

    def setChecked(self, checked):
        super().setChecked(checked)
        self._thumb_pos = 22.0 if checked else 2.0
        self.setProperty("checked", checked)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def nextCheckState(self):
        super().nextCheckState()
        end = 22.0 if self.isChecked() else 2.0
        self._anim.stop()
        self._anim.setEndValue(end)
        self._anim.start()
        self.setProperty("checked", self.isChecked())
        self.style().unpolish(self)
        self.style().polish(self)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        checked = self.isChecked()
        track_opacity = self._thumb_pos / 22.0 # 0.1 to 1.0 approx
        
        # 1. Свечение (Glow / Halo) - рисуем только если включено или в процессе анимации
        if self._thumb_pos > 5:
            glow_color = QColor(ZenColors.PRIMARY)
            glow_color.setAlpha(int(60 * (self._thumb_pos / 22.0)))
            gradient = QRadialGradient(self._thumb_pos + 10, 12, 20)
            gradient.setColorAt(0, glow_color)
            gradient.setColorAt(1, Qt.GlobalColor.transparent)
            p.setBrush(QBrush(gradient))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(self.rect())

        # 2. Отрисовка трека (фон переключателя)
        track_rect = QRect(0, 2, 44, 20)
        p.setPen(QPen(QColor(ZenColors.BORDER), 1))
        
        if checked:
            bg_color = QColor(ZenColors.PRIMARY)
            p.setBrush(QBrush(bg_color))
            p.setPen(Qt.PenStyle.NoPen)
        else:
            p.setBrush(QBrush(QColor(ZenColors.BG_DARK)))
        
        p.drawRoundedRect(track_rect, 10, 10)

        # 3. Отрисовка ползунка (Thumb)
        thumb_color = QColor("white")
        p.setBrush(QBrush(thumb_color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(self._thumb_pos), 2, 20, 20)

# HubPage moved to base.py

class SettingsPage(HubPage):
    def __init__(self):
        super().__init__("nav_settings")
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        self.page_layout = QVBoxLayout(container)
        self.page_layout.setContentsMargins(0, 0, 15, 0)
        self.page_layout.setSpacing(30)
        def create_card(title_txt, layout_to_add=None):
            card = QFrame()
            card.setObjectName("PremiumCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(30, 25, 30, 30)
            card_layout.setSpacing(15)
            
            if title_txt:
                t = QLabel(title_txt)
                t.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {ZenColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.1em; background: transparent; padding: 0px;")
                card_layout.addWidget(t)
                card_layout.addSpacing(5)
            
            if layout_to_add:
                card_layout.addLayout(layout_to_add)
                
            return card, card_layout

        # 1. Секция: Основные
        main_group = QGridLayout()
        main_group.setSpacing(20)
        main_group.setColumnStretch(1, 1)

        main_group.addWidget(QLabel(translator.get("lang_select")), 0, 0)
        self.lang_combo = NoWheelComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.setCurrentText("Русский" if config.get("language") == "ru" else "English")
        self.lang_combo.setFixedWidth(200)
        main_group.addWidget(self.lang_combo, 0, 1)

        main_group.addWidget(QLabel(translator.get("mic_device")), 1, 0)
        self.mic_combo = NoWheelComboBox()
        self.refresh_mic_list()
        main_group.addWidget(self.mic_combo, 1, 1)

        card1, _ = create_card("🌐 " + "Основные настройки", main_group)
        self.page_layout.addWidget(card1)

        # 2. Секция: Аудио и Ввод
        audio_group = QVBoxLayout()
        gain_row = QHBoxLayout()
        gain_val = config.get("mic_gain") or 1.0
        self.gain_value_lbl = QLabel(f"{gain_val:.1f}x")
        self.gain_value_lbl.setStyleSheet(f"color: {ZenColors.PRIMARY}; font-weight: 600;")
        gain_lbl = QLabel(translator.get("mic_gain"))
        gain_row.addWidget(gain_lbl)
        gain_row.addStretch()
        gain_row.addWidget(self.gain_value_lbl)
        audio_group.addLayout(gain_row)
        self.gain_slider = NoWheelSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setRange(10, 50)
        self.gain_slider.setValue(int(gain_val * 10))
        self.gain_slider.valueChanged.connect(self._on_gain_changed)
        audio_group.addWidget(self.gain_slider)

        audio_group.addSpacing(15)
        
        shortcut_row = QHBoxLayout()
        shortcut_row.addWidget(QLabel(translator.get("hotkey_label")))
        shortcut_row.addStretch()
        self.hotkey_btn = HotkeyButton(config.get("hotkey") or "<ctrl>+<f12>")
        self.hotkey_btn.setFixedWidth(200)
        shortcut_row.addWidget(self.hotkey_btn)
        audio_group.addLayout(shortcut_row)

        card2, _ = create_card("🎙️ " + "Звук и Управление", audio_group)
        self.page_layout.addWidget(card2)

        # 3. Секция: Система
        sys_group = QVBoxLayout()
        sys_group.setSpacing(15)
        
        def create_switch_row(label_text, switch_obj):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(switch_obj)
            return row

        self.sound_check = ZenSwitch()
        self.sound_check.setChecked(config.get("sound_enabled"))
        self.autostart_check = ZenSwitch()
        self.autostart_check.setChecked(config.get("autostart"))
        
        sys_group.addLayout(create_switch_row(translator.get("sound_feedback"), self.sound_check))
        sys_group.addLayout(create_switch_row(translator.get("autostart"), self.autostart_check))
        
        card3, _ = create_card("⚙️ " + "Система", sys_group)
        self.page_layout.addWidget(card3)

        # 4. Секция: Нейросети
        model_container = QVBoxLayout()
        model_grid = QGridLayout()
        model_grid.setSpacing(15)
        model_grid.setContentsMargins(0, 5, 0, 5)
        
        # Headers
        h1 = QLabel(translator.get("model_type"))
        h2 = QLabel(translator.get("model_selection"))
        h3 = QLabel(translator.get("model_status_col"))
        for h in [h1, h2, h3]:
            h.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {ZenColors.TEXT_MUTED}; text-transform: uppercase;")
        
        model_grid.addWidget(h1, 0, 0)
        model_grid.addWidget(h2, 0, 1)
        model_grid.addWidget(h3, 0, 2, Qt.AlignmentFlag.AlignCenter)

        # Row 1: Dictation
        model_grid.addWidget(QLabel("🎙️ " + translator.get("model_dictation")), 1, 0)
        self.model_combo = NoWheelComboBox()
        model_grid.addWidget(self.model_combo, 1, 1)
        self.dict_status_icon = QLabel("✅")
        self.dict_status_icon.setFixedWidth(30)
        model_grid.addWidget(self.dict_status_icon, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        # Row 2: Analyst
        model_grid.addWidget(QLabel("🎬 " + translator.get("model_analyst")), 2, 0)
        self.analyst_model_combo = NoWheelComboBox()
        model_grid.addWidget(self.analyst_model_combo, 2, 1)
        self.anal_status_icon = QLabel("✅")
        self.anal_status_icon.setFixedWidth(30)
        model_grid.addWidget(self.anal_status_icon, 2, 2, Qt.AlignmentFlag.AlignCenter)
        
        models = [("tiny (~75MB)", "tiny"), ("base (~145MB)", "base"), ("small (~485MB)", "small"), ("medium (~1.5GB)", "medium"), ("large-v3 (~3.1GB)", "large-v3")]
        for name, key in models:
            self.model_combo.addItem(name, key)
            self.analyst_model_combo.addItem(name, key)
            
        current_dict_model = config.get("model_size")
        current_anal_model = config.get("analyst_model_size")
        
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == current_dict_model:
                self.model_combo.setCurrentIndex(i)
            if self.analyst_model_combo.itemData(i) == current_anal_model:
                self.analyst_model_combo.setCurrentIndex(i)

        model_container.addLayout(model_grid)
        model_container.addSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        model_container.addWidget(self.progress_bar)
        
        card4, _ = create_card("🤖 " + translator.get("ai_model"), model_container)
        self.page_layout.addWidget(card4)
        
        self.model_combo.currentIndexChanged.connect(self._on_model_selected)
        self.analyst_model_combo.currentIndexChanged.connect(self._on_model_selected)
        
        self.page_layout.addStretch()
        self.scroll.setWidget(container)
        self.layout.addWidget(self.scroll)
        
        self.save_btn = QPushButton(translator.get("btn_save"))
        self.save_btn.clicked.connect(self.save_and_restart)
        self.save_btn.setMinimumHeight(45)
        self.layout.addWidget(self.save_btn)
        
        self._on_model_selected()

    def _on_gain_changed(self, val): self.gain_value_lbl.setText(f"{val/10.0:.1f}x")
    
    def _on_model_selected(self):
        size_dict = self.model_combo.currentData()
        size_anal = self.analyst_model_combo.currentData()
        
        dict_cached = is_model_cached(size_dict)
        anal_cached = is_model_cached(size_anal)
        
        self.dict_status_icon.setText("✅" if dict_cached else "☁️")
        self.anal_status_icon.setText("✅" if anal_cached else "☁️")
        
        if dict_cached and anal_cached:
            self.save_btn.setText(translator.get("btn_save"))
        else:
            self.save_btn.setText(translator.get("btn_download"))

    def start_download(self):
        size_dict = self.model_combo.currentData()
        size_anal = self.analyst_model_combo.currentData()
        
        # Download first non-cached model
        target = None
        if not is_model_cached(size_dict): target = size_dict
        elif not is_model_cached(size_anal): target = size_anal
        
        if not target:
            self._on_model_selected()
            return

        self.downloader = ModelDownloader(target)
        self.downloader.progress.connect(self.progress_bar.setValue)
        self.downloader.finished.connect(self._on_download_finished)
        self.progress_bar.show(); self.progress_bar.setValue(0)
        self.model_status.setText(f"🚀 {translator.get('downloading')} ({target})")
        self.save_btn.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.analyst_model_combo.setEnabled(False)
        self.downloader.start()
        
    def _on_download_finished(self, success, message):
        self.save_btn.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.analyst_model_combo.setEnabled(True)
        if success:
            # Check if there is another one to download
            size_dict = self.model_combo.currentData()
            size_anal = self.analyst_model_combo.currentData()
            if not is_model_cached(size_dict) or not is_model_cached(size_anal):
                self.start_download() # Continue with next
            else:
                self.model_status.setText(f"✅ {translator.get('ready_to_apply')}")
                self.save_btn.setText(translator.get("btn_save"))
        else:
            self.model_status.setText(f"❌ {translator.get('download_error')}: {message}")

    def _set_autostart(self, enabled):
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_file = autostart_dir / "zenwhisper.desktop"
        if enabled:
            autostart_dir.mkdir(parents=True, exist_ok=True)
            desktop_content = """[Desktop Entry]\nType=Application\nName=ZenWhisper\nComment=AI Voice Dictation\nExec=zenwhisper\nIcon=zenwhisper\nTerminal=false\nCategories=Utility;Audio;\nX-GNOME-Autostart-enabled=true\n"""
            with open(autostart_file, 'w') as f: f.write(desktop_content)
        elif autostart_file.exists(): autostart_file.unlink()
    def refresh_mic_list(self):
        self.mic_combo.clear()
        try:
            self.mic_combo.addItem(translator.get("sys_default"), sd.default.device[0])
            for i, dev in enumerate(sd.query_devices()):
                if dev['max_input_channels'] > 0 and "monitor" not in dev['name'].lower():
                    self.mic_combo.addItem(dev['name'], i)
        except: pass
    def save_and_restart(self):
        if self.save_btn.text() == translator.get("btn_download"):
            self.start_download(); return
        config.set("language", self.lang_combo.currentData())
        config.set("microphone_id", self.mic_combo.currentData())
        config.set("mic_gain", self.gain_slider.value() / 10.0)
        config.set("hotkey", self.hotkey_btn.current_hotkey)
        config.set("sound_enabled", self.sound_check.isChecked())
        config.set("autostart", self.autostart_check.isChecked())
        self._set_autostart(self.autostart_check.isChecked())
        config.set("model_size", self.model_combo.currentData())
        config.set("analyst_model_size", self.analyst_model_combo.currentData())
        os.execv(sys.executable, [sys.executable] + sys.argv)

class HistoryPage(HubPage):
    def __init__(self):
        super().__init__("nav_history")
        
        card = QFrame()
        card.setObjectName("PremiumCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(1, 1, 1, 1) # Minimal margins to let table span
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([translator.get("history_text"), translator.get("actions")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 120)
        self.table.setStyleSheet(ZenStyles.TABLE)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(60) # Increased for better spacing
        
        card_layout.addWidget(self.table)
        self.layout.addWidget(card)
        self._load_history()

    def _load_history(self):
        self.add_item(translator.get("welcome"))

    def add_item(self, text):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        text_item = QTableWidgetItem(text)
        self.table.setItem(row, 0, text_item)
        
        btn_copy = PremiumCopyButton()
        btn_copy.setToolTip(translator.get("copy_text"))
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(text))
        
        container = QWidget()
        cl = QHBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(btn_copy)
        
        self.table.setCellWidget(row, 1, container)

class VocabularyPage(HubPage):
    def __init__(self):
        super().__init__("nav_vocabulary")
        
        card = QFrame()
        card.setObjectName("PremiumCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        self.list = QListWidget()
        self.list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent; border: none; color: {ZenColors.TEXT_PRIMARY}; outline: none;
            }}
            QListWidget::item {{
                padding: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            QListWidget::item:hover {{
                background-color: {ZenColors.SURFACE_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {ZenColors.PRIMARY_GLASS}; color: {ZenColors.PRIMARY};
            }}
        """)
        card_layout.addWidget(self.list)
        words = config.get("vocabulary") or []
        for w in words: self.list.addItem(w)
        
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Добавить слово...")
        self.input.setStyleSheet(ZenStyles.INPUT)
        
        add_btn = PremiumAddButton()
        add_btn.clicked.connect(self.add_word)
        
        row.addWidget(self.input)
        row.addWidget(add_btn)
        card_layout.addLayout(row)
        
        del_btn = QPushButton(translator.get("delete"))
        del_btn.setStyleSheet(ZenStyles.BUTTON_PREMIUM + f"""
            QPushButton {{ background: rgba(255, 50, 50, 0.05); color: #FF5555; border-color: rgba(255, 50, 50, 0.2); }}
            QPushButton:hover {{ background: rgba(255, 50, 50, 0.15); border-color: rgba(255, 50, 50, 0.4); }}
        """)
        del_btn.clicked.connect(self.delete_selected)
        card_layout.addWidget(del_btn)
        
        self.layout.addWidget(card)

    def add_word(self):
        word = self.input.text().strip()
        if word: self.list.addItem(word); self.input.clear(); self.save()
    def delete_selected(self):
        for item in self.list.selectedItems(): self.list.takeItem(self.list.row(item))
        self.save()
    def save(self):
        words = [self.list.item(i).text() for i in range(self.list.count())]
        config.set("vocabulary", words)

class SnippetsPage(HubPage):
    def __init__(self):
        super().__init__("nav_snippets")
        
        card = QFrame()
        card.setObjectName("PremiumCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(1, 1, 1, 1)
        
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([translator.get("trigger"), translator.get("expansion")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(ZenStyles.TABLE)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        card_layout.addWidget(self.table)
        
        snippets = config.get("snippets") or {}
        for k, v in snippets.items(): self.add_row(k, v)
        
        controls = QWidget()
        cl = QVBoxLayout(controls)
        cl.setContentsMargins(20, 15, 20, 20)
        
        row = QHBoxLayout()
        row.setSpacing(10)
        self.trigger_in = QLineEdit()
        self.trigger_in.setPlaceholderText(translator.get("trigger"))
        self.trigger_in.setStyleSheet(ZenStyles.INPUT)
        
        self.expansion_in = QLineEdit()
        self.expansion_in.setPlaceholderText(translator.get("expansion"))
        self.expansion_in.setStyleSheet(ZenStyles.INPUT)
        
        add_btn = PremiumAddButton()
        add_btn.clicked.connect(self.add_snippet)
        
        row.addWidget(self.trigger_in)
        row.addWidget(self.expansion_in)
        row.addWidget(add_btn)
        cl.addLayout(row)
        
        del_btn = QPushButton(translator.get("delete"))
        del_btn.setStyleSheet(ZenStyles.BUTTON_PREMIUM + f"""
            QPushButton {{ background: rgba(255, 50, 50, 0.05); color: #FF5555; border-color: rgba(255, 50, 50, 0.2); margin-top: 10px; }}
            QPushButton:hover {{ background: rgba(255, 50, 50, 0.15); border-color: rgba(255, 50, 50, 0.4); }}
        """)
        del_btn.clicked.connect(self.delete_selected)
        cl.addWidget(del_btn)
        
        card_layout.addWidget(controls)
        self.layout.addWidget(card)

    def add_row(self, trigger, expansion):
        r = self.table.rowCount(); self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(trigger)); self.table.setItem(r, 1, QTableWidgetItem(expansion))
    def add_snippet(self):
        t = self.trigger_in.text().strip(); e = self.expansion_in.text().strip()
        if t and e: self.add_row(t, e); self.trigger_in.clear(); self.expansion_in.clear(); self.save()
    def delete_selected(self):
        row = self.table.currentRow()
        if row >= 0: self.table.removeRow(row); self.save()
    def save(self):
        snips = {}
        for r in range(self.table.rowCount()): snips[self.table.item(r, 0).text()] = self.table.item(r, 1).text()
        config.set("snippets", snips)

from zenwhisper.ui.analyst import AnalystPage

class NavigationSidebar(QFrame):
    page_changed = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.setFixedWidth(240); self.setObjectName("Sidebar")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 30, 0, 30); self.layout.setSpacing(5)
        self.setStyleSheet(ZenStyles.SIDEBAR + ZenStyles.NAV_BUTTON)
        
        self.title_container = QWidget()
        title_layout = QVBoxLayout(self.title_container)
        title_layout.setContentsMargins(0, 0, 0, 10)
        title_layout.setSpacing(2)
        
        self.title = QLabel("ZEN Whisper")
        self.title.setStyleSheet(f"font-size: 20px; font-weight: 900; color: #f8fafc; padding-left: 20px; letter-spacing: 0.05em;")
        self.subtitle = QLabel("AI DICTATION HUB")
        self.subtitle.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {ZenColors.PRIMARY}; padding-left: 22px; letter-spacing: 0.15em;")
        
        title_layout.addWidget(self.title)
        title_layout.addWidget(self.subtitle)
        self.layout.addWidget(self.title_container)
        self.layout.addSpacing(15)
        
        self.buttons = []
        nav_items = [("nav_settings", "⚙️", "nav_settings_desc"), ("nav_analyst", "🎬", "nav_analyst_desc"), ("nav_history", "🕒", "nav_history_desc"), ("nav_vocabulary", "📚", "nav_vocabulary_desc"), ("nav_snippets", "✂️", "nav_snippets_desc")]
        for i, (key, icon, desc) in enumerate(nav_items):
            btn = self._create_nav_btn(translator.get(key), icon, i)
            self.buttons.append(btn); self.layout.addWidget(btn)
        
        self.layout.addStretch()
        
        # Footer: Donate and Version
        try:
            from zenwhisper import __version__
        except ImportError:
            __version__ = "1.1.2"
            
        self.donate_btn = QPushButton("☕ " + translator.get("donate"))
        self.donate_btn.setObjectName("DonateBtn")
        self.donate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.version_lbl = QLabel(f"{translator.get('version')}: {__version__}")
        self.version_lbl.setObjectName("VersionLabel")
        
        self.layout.addWidget(self.donate_btn)
        self.layout.addWidget(self.version_lbl)
        
        self.set_active(0)
    def _create_nav_btn(self, name, icon, index):
        btn = QPushButton(f" {icon}  {name}"); btn.setObjectName("NavBtn"); btn.setCheckable(True); btn.setFixedHeight(45)
        btn.setProperty("active", "false")
        btn.clicked.connect(lambda: self.on_btn_clicked(index))
        return btn
    def on_btn_clicked(self, index): self.set_active(index); self.page_changed.emit(index)
    def set_active(self, index):
        for i, btn in enumerate(self.buttons):
            is_active = (i == index)
            btn.setChecked(is_active)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

class HubWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(translator.get("hub_title")); self.setMinimumSize(1000, 750)
        self._check_path, self._arrow_path = _create_zen_icons()
        cw = QWidget(); self.setCentralWidget(cw); l = QHBoxLayout(cw); l.setContentsMargins(0,0,0,0)
        self.sidebar = NavigationSidebar(); self.sidebar.page_changed.connect(self.switch_page); l.addWidget(self.sidebar)
        self.stack = QStackedWidget(); l.addWidget(self.stack)
        self.settings_page = SettingsPage(); self.analyst_page = AnalystPage(); self.history_page = HistoryPage()
        self.vocab_page = VocabularyPage(); self.snippets_page = SnippetsPage()
        for p in [self.settings_page, self.analyst_page, self.history_page, self.vocab_page, self.snippets_page]: self.stack.addWidget(p)
        
        # Apply Global Style
        full_qss = ZenStyles.MAIN_WINDOW + ZenStyles.CARD + ZenStyles.INPUT + ZenStyles.BUTTON_PREMIUM + ZenStyles.TABS + ZenStyles.COMBOBOX + ZenStyles.SCROLLBAR + ZenStyles.ZEN_SWITCH + ZenStyles.SIDEBAR_FOOTER
        self.setStyleSheet(full_qss)
    def switch_page(self, i): self.stack.setCurrentIndex(i); self.sidebar.set_active(i)
    def show_page(self, i): self.switch_page(i); self.show(); self.activateWindow(); self.raise_()
    def closeEvent(self, e): self.hide(); e.ignore()
    def retranslate_ui(self):
        self.setWindowTitle(translator.get("hub_title"))
        nav_keys = ["nav_settings", "nav_analyst", "nav_history", "nav_vocabulary", "nav_snippets"]
        nav_icons = ["⚙️", "🎬", "🕒", "📚", "✂️"]
        for i, btn in enumerate(self.sidebar.buttons): btn.setText(f" {nav_icons[i]}  {translator.get(nav_keys[i])}")
        for p in [self.settings_page, self.analyst_page, self.history_page, self.vocab_page, self.snippets_page]: p.retranslate_ui()
