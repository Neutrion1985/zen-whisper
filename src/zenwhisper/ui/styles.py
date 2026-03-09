from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtCore import Qt

class ZenColors:
    # Базовая палитра (Slate-950 / Slate-900 / Slate-800)
    BG_DARK = "#0b0f19"      # Основной фон (Углубленный Slate-950)
    SURFACE = "rgba(30, 41, 59, 0.4)"     # Slate-800 40% (Glassmorphism)
    SURFACE_HOVER = "rgba(255, 255, 255, 0.05)" # Легкая подсветка
    BORDER = "rgba(255, 255, 255, 0.05)"    # Утонченная прозрачная граница
    
    # Акцентные цвета (Blue-500)
    PRIMARY = "#3b82f6"      # Основной синий
    PRIMARY_GLASS = "rgba(59, 130, 246, 0.15)" # Синее стекло
    PRIMARY_BORDER = "rgba(59, 130, 246, 0.2)" # Акцентная граница
    
    # Текст (Slate-50 / Slate-400)
    TEXT_PRIMARY = "#f8fafc"   # Белый (Slate-50)
    TEXT_MUTED = "#94a3b8"     # Приглушенный (Slate-400)

class ZenStyles:
    # Плейсхолдер для динамических путей к иконкам
    DYNAMIC_ICON_PATH = "{{DYNAMIC_ICON_PATH}}"    
    # Стили для главного окна и базовых виджетовы
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {ZenColors.BG_DARK};
        }}
        QWidget {{
            color: {ZenColors.TEXT_PRIMARY};
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 14px;
        }}
        QLabel, QCheckBox, QRadioButton, QSlider {{
            background: transparent;
        }}
        QScrollArea, QScrollArea > QWidget > QWidget {{
            background: transparent;
            border: none;
        }}
    """
    
    # Карточки в стиле Glassmorphism с градиентом
    CARD = f"""
        QFrame#PremiumCard {{
            background-color: rgba(15, 23, 42, 0.4);
            border: 1px solid {ZenColors.BORDER};
            border-radius: 16px;
        }}
    """
    
    # Текстовые поля (Inputs)
    INPUT = f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: rgba(15, 23, 42, 0.4);
            border: 1px solid {ZenColors.BORDER};
            border-radius: 8px;
            padding: 10px 14px;
            color: {ZenColors.TEXT_PRIMARY};
            selection-background-color: {ZenColors.PRIMARY_GLASS};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {ZenColors.PRIMARY_BORDER};
            background-color: rgba(15, 23, 42, 0.6);
        }}
    """
    
    # Выпадающие списки (ComboBox) с кастомным шевроном
    COMBOBOX = f"""
        QComboBox {{
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px 12px;
            min-height: 35px;
            color: {ZenColors.TEXT_PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 40px;
        }}
        /* Отрисовка стрелки теперь происходит напрямую в paintEvent */
        QComboBox::down-arrow {{
            image: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: #0f172a;
            border: 1px solid {ZenColors.BORDER};
            selection-background-color: {ZenColors.PRIMARY_GLASS};
            outline: none;
            color: white;
            border-radius: 8px;
            padding: 4px;
        }}
    """
    
    # Премиум кнопки (Premium Glass)
    BUTTON_PREMIUM = f"""
        QPushButton {{
            background-color: {ZenColors.PRIMARY_GLASS};
            border: 1px solid {ZenColors.PRIMARY_BORDER};
            border-radius: 10px;
            color: #60a5fa;
            font-weight: 500;
            padding: 10px 20px;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: rgba(59, 130, 246, 0.25);
            border-color: {ZenColors.PRIMARY};
            color: white;
        }}
        QPushButton:pressed {{
            background-color: rgba(59, 130, 246, 0.35);
        }}
        QPushButton:disabled {{
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: {ZenColors.TEXT_MUTED};
        }}
    """
    
    # Второстепенные кнопки (Slate/Gray)
    BUTTON_SECONDARY = f"""
        QPushButton {{
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: {ZenColors.TEXT_MUTED};
            font-weight: 500;
            padding: 10px 20px;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.2);
            color: {ZenColors.TEXT_PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: rgba(255, 255, 255, 0.12);
        }}
    """
    
    # Боковое меню (Sidebar)
    SIDEBAR = f"""
        QWidget#Sidebar {{
            background-color: rgba(15, 23, 42, 0.7);
            border-right: 1px solid {ZenColors.BORDER};
        }}
    """
    
    # Навигационные кнопки в сайдбаре
    NAV_BUTTON = f"""
        QPushButton#NavBtn {{
            text-align: left;
            padding-left: 20px;
            border-radius: 10px;
            color: {ZenColors.TEXT_MUTED};
            border: none;
            background: transparent;
            font-weight: 500;
            margin: 2px 0px;
            font-size: 15px;
        }}
        QPushButton#NavBtn:hover {{
            background: {ZenColors.SURFACE_HOVER};
            color: {ZenColors.TEXT_PRIMARY};
        }}
        QPushButton#NavBtn[active="true"] {{
            background: {ZenColors.PRIMARY_GLASS};
            color: {ZenColors.TEXT_PRIMARY};
            font-weight: 600;
            border-left: 3px solid {ZenColors.PRIMARY};
            border-radius: 0px 10px 10px 0px;
        }}
    """
    
    # Таблицы (Data Grids)
    TABLE = f"""
        QTableWidget {{
            background-color: transparent;
            border: none;
            gridline-color: rgba(255, 255, 255, 0.05);
            color: {ZenColors.TEXT_PRIMARY};
            selection-background-color: {ZenColors.PRIMARY_GLASS};
            outline: none;
        }}
        QHeaderView::section {{
            background-color: transparent;
            color: {ZenColors.TEXT_MUTED};
            padding: 12px;
            border: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.05em;
        }}
        QTableWidget::item {{
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.02);
        }}
        QTableWidget::item:hover {{
            background-color: {ZenColors.SURFACE_HOVER};
        }}
        QTableWidget::item:selected {{
            background-color: {ZenColors.PRIMARY_GLASS};
            color: {ZenColors.PRIMARY};
        }}
    """
    
    # Вкладки (Tabs)
    TABS = f"""
        QTabWidget::pane {{
            border: 1px solid {ZenColors.BORDER};
            background: rgba(15, 23, 42, 0.4);
            border-radius: 12px;
            top: -1px;
        }}
        QTabBar::tab {{
            background: transparent;
            padding: 10px 20px;
            color: {ZenColors.TEXT_MUTED};
            font-weight: 500;
            border: 1px solid transparent;
            border-bottom: 2px solid transparent;
            margin-right: 4px;
        }}
        QTabBar::tab:hover {{
            color: {ZenColors.TEXT_PRIMARY};
        }}
        QTabBar::tab:selected {{
            color: {ZenColors.PRIMARY};
            border-bottom: 2px solid {ZenColors.PRIMARY};
        }}
    """
    
    ZEN_SWITCH = f"""
        QWidget#ZenSwitch {{
            background: transparent;
            border: none;
        }}
    """

    SIDEBAR_FOOTER = f"""
        QLabel#VersionLabel {{
            color: {ZenColors.TEXT_MUTED};
            font-size: 11px;
            font-weight: 500;
            padding-left: 20px;
            margin-top: 10px;
        }}
        QPushButton#DonateBtn {{
            background-color: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: 10px;
            color: #fbbf24;
            font-weight: 600;
            padding: 10px;
            margin: 10px 15px;
            font-size: 13px;
        }}
        QPushButton#DonateBtn:hover {{
            background-color: rgba(245, 158, 11, 0.2);
            border-color: #f59e0b;
            color: white;
        }}
    """

    # Премиальный скроллбар (тонкий и полупрозрачный)
    SCROLLBAR = f"""
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(255, 255, 255, 0.05);
            min-height: 30px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: rgba(255, 255, 255, 0.15);
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: rgba(255, 255, 255, 0.05);
            min-width: 30px;
            border-radius: 3px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: rgba(255, 255, 255, 0.15);
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}
    """
