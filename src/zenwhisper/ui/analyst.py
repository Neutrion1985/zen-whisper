import os
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QFileDialog, QTextEdit, 
                             QProgressBar, QTabWidget, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QThread
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor

from zenwhisper.core.translator import translator
from zenwhisper.core.engine import engine
from zenwhisper.core.config import config
from zenwhisper.ui.base import HubPage
from zenwhisper.ui.styles import ZenColors, ZenStyles

class TranscriptionWorker(QThread):
    finished = pyqtSignal(list, str, str) # segments, full_text, srt_text
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            # Load the specific model for analysis as per config
            target_model = config.get("analyst_model_size") or "medium"
            engine.load_model(force_size=target_model)
            
            # Wait for model to load if necessary (although load_model might be async, 
            # engine.transcribe will wait or fail if not ready, but we should be sure)
            while engine.is_loading:
                self.msleep(100)
                
            # Get segments for both text and SRT
            segments = engine.transcribe(self.file_path, return_segments=True)
            
            if isinstance(segments, str) and segments.startswith("Error"):
                self.error.emit(segments)
                return

            # Format text
            full_text = " ".join([s['text'] for s in segments])
            
            # Format SRT
            srt_text = engine.to_srt(segments)
            
            self.finished.emit(segments, full_text, srt_text)
        except Exception as e:
            self.error.emit(str(e))

class DropZoneWidget(QFrame):
    file_dropped = pyqtSignal(str)
    file_removed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(160)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.icon_label = QLabel("📥")
        self.icon_label.setStyleSheet("font-size: 38px; margin-bottom: 5px; color: #60a5fa;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_label = QLabel(translator.get("drop_file_here"))
        self.text_label.setStyleSheet(f"font-size: 15px; color: {ZenColors.TEXT_MUTED}; font-weight: 500;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(f"font-size: 13px; color: {ZenColors.PRIMARY}; font-weight: 600;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.hide()

        self.btn_remove = QPushButton("✕ " + translator.get("delete"))
        self.btn_remove.setFixedWidth(100)
        self.btn_remove.setStyleSheet(f"""
            QPushButton {{ 
                background: rgba(255, 50, 50, 0.05); color: #FF5555; border: 1px solid rgba(255, 50, 50, 0.2);
                border-radius: 8px; padding: 6px; font-size: 12px; margin-top: 10px; font-weight: 600;
            }}
            QPushButton:hover {{ background: rgba(255, 50, 50, 0.15); border-color: rgba(255, 50, 50, 0.4); }}
        """)
        self.btn_remove.clicked.connect(self._on_remove_clicked)
        self.btn_remove.hide()
        
        self.layout.addStretch()
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.info_label)
        
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(self.btn_remove)
        btn_container.addStretch()
        self.layout.addLayout(btn_container)
        
        self.layout.addStretch()
        
        self.has_file = False
        self._update_style()

    def set_file(self, file_path):
        self.has_file = True
        name = os.path.basename(file_path)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        self.icon_label.setText("📄")
        self.icon_label.setStyleSheet("font-size: 38px; margin-bottom: 5px; color: #f8fafc;")
        self.text_label.setText(name)
        self.text_label.setStyleSheet("font-size: 16px; color: #FFFFFF; font-weight: bold;")
        self.info_label.setText(f"{size_mb:.1f} MB")
        self.info_label.show()
        self.btn_remove.show()
        self._update_style()

    def clear(self):
        self.has_file = False
        self.icon_label.setText("📥")
        self.icon_label.setStyleSheet("font-size: 38px; margin-bottom: 5px; color: #60a5fa;")
        self.text_label.setText(translator.get("drop_file_here"))
        self.text_label.setStyleSheet(f"font-size: 15px; color: {ZenColors.TEXT_MUTED}; font-weight: 500;")
        self.info_label.hide()
        self.btn_remove.hide()
        self._update_style()

    def _on_remove_clicked(self):
        self.clear()
        self.file_removed.emit()

    def retranslate_ui(self):
        if not self.has_file:
            self.text_label.setText(translator.get("drop_file_here"))
        self.btn_remove.setText("✕ " + translator.get("delete"))

    def _update_style(self):
        border_color = ZenColors.PRIMARY if self.has_file else "rgba(255, 255, 255, 0.1)"
        bg_color = "rgba(15, 23, 42, 0.4)" if not self.has_file else ZenColors.PRIMARY_GLASS
        border_style = f"2px solid {border_color}" if self.has_file else f"2px dashed {border_color}"
        
        self.setStyleSheet(f"""
            #DropZone {{
                background-color: {bg_color};
                border: {border_style};
                border-radius: 20px;
            }}
            #DropZone[hover="true"] {{
                background-color: {ZenColors.SURFACE_HOVER};
                border: 2px dashed {ZenColors.PRIMARY};
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.setProperty("hover", "true")
            self.setStyle(self.style())
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setProperty("hover", "false")
        self.setStyle(self.style())

    def dropEvent(self, event: QDropEvent):
        self.setProperty("hover", "false")
        self.setStyle(self.style())
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)

    def mousePressEvent(self, event):
        if self.has_file: return # Don't open dialog if clicking background of filled zone
        file_path, _ = QFileDialog.getOpenFileName(
            self, translator.get("nav_analyst"), "", 
            "Media Files (*.mp3 *.wav *.flac *.m4a *.mp4 *.mkv *.avi);;All Files (*)"
        )
        if file_path:
            self.file_dropped.emit(file_path)

class AnalystPage(HubPage):
    def __init__(self):
        super().__init__("nav_analyst")
        self.current_file = None
        self.segments = None
        self.worker = None
        
        # UI Elements
        self.drop_zone = DropZoneWidget()
        self.drop_zone.file_dropped.connect(self.on_file_selected)
        self.drop_zone.file_removed.connect(self.reset_ui) # Link removal to UI reset
        
        self.btn_analyze = QPushButton(translator.get("start_analysis"))
        self.btn_analyze.hide()
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.clicked.connect(self.start_analysis)
        self.btn_analyze.setMinimumHeight(45)
        self.btn_analyze.setStyleSheet(ZenStyles.BUTTON_PREMIUM)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{ background-color: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px; text-align: center; height: 12px; color: transparent; }}
            QProgressBar::chunk {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ZenColors.PRIMARY}, stop:1 #60a5fa); border-radius: 5px; }}
        """)

        self.results_tabs = QTabWidget()
        self.results_tabs.setObjectName("ResultTabs")
        self.results_tabs.hide()
        self.results_tabs.setStyleSheet(ZenStyles.TABS)
        
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.text_result.setStyleSheet(ZenStyles.INPUT)
        self.srt_result = QTextEdit()
        self.srt_result.setReadOnly(True)
        self.srt_result.setStyleSheet(ZenStyles.INPUT)
        
        self.results_tabs.addTab(self.text_result, translator.get("view_text"))
        self.results_tabs.addTab(self.srt_result, translator.get("view_srt"))
        
        # Action buttons (Bottom Layout)
        self.bottom_actions = QWidget()
        self.bottom_actions.hide()
        bottom_l = QHBoxLayout(self.bottom_actions)
        bottom_l.setContentsMargins(0, 10, 0, 0)
        
        self.btn_copy = QPushButton(f"📋 {translator.get('copy')}")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        self.btn_copy.setStyleSheet(ZenStyles.BUTTON_PREMIUM)
        
        self.btn_download = QPushButton(f"💾 {translator.get('download_result')}")
        self.btn_download.clicked.connect(self.download_result)
        self.btn_download.setStyleSheet(ZenStyles.BUTTON_SECONDARY)
        self.btn_download.setMinimumWidth(180)
        
        self.btn_new_analysis = QPushButton(f"🆕 {translator.get('new_analysis')}")
        self.btn_new_analysis.clicked.connect(self.reset_ui)
        self.btn_new_analysis.setStyleSheet(ZenStyles.BUTTON_PREMIUM)
        self.btn_new_analysis.setMinimumWidth(180)
        
        bottom_l.addWidget(self.btn_copy)
        bottom_l.addWidget(self.btn_download)
        bottom_l.addWidget(self.btn_new_analysis)
        
        # Add to main layout
        self.layout.addWidget(self.drop_zone)
        self.layout.addWidget(self.btn_analyze)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.results_tabs)
        self.layout.addWidget(self.bottom_actions)
        self.layout.addStretch()

    def on_file_selected(self, file_path):
        self.current_file = file_path
        self.drop_zone.set_file(file_path)
        self.btn_analyze.show()
        self.btn_analyze.setEnabled(True)
        self.results_tabs.hide()
        self.bottom_actions.hide()

    def reset_ui(self):
        self.current_file = None
        self.segments = None
        self.drop_zone.clear()
        self.drop_zone.show()
        self.drop_zone.setEnabled(True) # Unblock interactivity
        self.btn_analyze.hide()
        self.results_tabs.hide()
        self.bottom_actions.hide()
        self.progress_bar.hide()

    def start_analysis(self):
        if not self.current_file: return
        
        self.btn_analyze.setEnabled(False)
        self.drop_zone.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0) # Pulsing
        
        self.worker = TranscriptionWorker(self.current_file)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_finished(self, segments, full_text, srt_text):
        self.segments = segments
        self.progress_bar.hide()
        self.text_result.setPlainText(full_text)
        self.srt_result.setPlainText(srt_text)
        
        self.btn_analyze.hide()
        self.drop_zone.hide()
        
        self.results_tabs.show()
        self.bottom_actions.show()

    def on_analysis_error(self, err_msg):
        self.progress_bar.hide()
        self.btn_analyze.setEnabled(True)
        self.drop_zone.setEnabled(True)
        
        final_msg = f"❌ Error: {err_msg}"
        if "out of memory" in err_msg.lower():
            suggestion = "\n\n💡 TIP: Your GPU is out of memory. Please go to Settings and select a smaller model (e.g., 'medium' or 'small') or try a shorter file."
            if config.get("language") == "ru":
                suggestion = "\n\n💡 СОВЕТ: Недостаточно видеопамяти (GPU). Пожалуйста, перейдите в Настройки и выберите модель поменьше (например, 'medium' или 'small') или попробуйте файл меньшей длительности."
            final_msg += suggestion
            
        self.text_result.setPlainText(final_msg)
        self.results_tabs.show()
        self.bottom_actions.show() # Show buttons to allow "New Analysis"
        print(f"Analyst Error: {err_msg}")

    def copy_to_clipboard(self):
        if not self.segments: return
        idx = self.results_tabs.currentIndex()
        content = self.srt_result.toPlainText() if idx == 1 else self.text_result.toPlainText()
        QApplication.clipboard().setText(content)

    def download_result(self):
        if not self.segments: return
        idx = self.results_tabs.currentIndex()
        is_srt = (idx == 1)
        ext = ".srt" if is_srt else ".txt"
        content = self.srt_result.toPlainText() if is_srt else self.text_result.toPlainText()
        
        default_name = os.path.splitext(os.path.basename(self.current_file))[0] + ext
        save_path, _ = QFileDialog.getSaveFileName(self, translator.get("download_result"), default_name)
        
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.drop_zone.retranslate_ui()
        self.btn_analyze.setText(translator.get("start_analysis"))
        self.btn_download.setText(translator.get("download_result"))
        self.btn_copy.setText(translator.get("copy"))
        self.btn_new_analysis.setText(translator.get("new_analysis"))
        self.results_tabs.setTabText(0, translator.get("view_text"))
        self.results_tabs.setTabText(1, translator.get("view_srt"))
