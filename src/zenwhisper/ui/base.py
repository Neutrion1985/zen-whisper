from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from zenwhisper.core.translator import translator
from zenwhisper.ui.styles import ZenColors

class HubPage(QWidget):
    def __init__(self, title_key):
        super().__init__()
        self.title_key = title_key
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        self.header = QLabel(translator.get(title_key))
        self.header.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {ZenColors.TEXT_PRIMARY}; margin-bottom: 0px;")
        
        self.description = QLabel(translator.get(title_key + "_desc"))
        self.description.setStyleSheet(f"font-size: 14px; color: {ZenColors.TEXT_MUTED}; font-weight: 400; line-height: 1.5; margin-top: -5px; margin-bottom: 15px;")
        self.description.setWordWrap(True)
        
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.description)
        
    def retranslate_ui(self):
        self.header.setText(translator.get(self.title_key))
        self.description.setText(translator.get(self.title_key + "_desc"))
