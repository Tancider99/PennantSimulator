# -*- coding: utf-8 -*-
"""
NPB Pennant Simulator - Ultra Premium Theme System
OOTP-Inspired Professional Dark Theme with Premium Effects
"""
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget
from PySide6.QtGui import QColor, QPalette, QFont, QFontDatabase, QLinearGradient, QBrush
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from dataclasses import dataclass
from typing import Dict, Optional
import os


@dataclass
class Theme:
    """Ultra Premium OOTP-Style Dark Theme"""

    # === Premium Primary Colors (Rich Blue Accent) ===
    primary: str = "#0066cc"
    primary_hover: str = "#0080ff"
    primary_dark: str = "#004c99"
    primary_light: str = "#3399ff"
    primary_glow: str = "#0066cc40"  # For glow effects

    # === Secondary Accent (Gold for Premium Feel) ===
    accent_gold: str = "#ffd700"
    accent_gold_dark: str = "#cc9900"
    accent_gold_light: str = "#ffeb3b"
    accent_gold_glow: str = "#ffd70030"

    # === Background Colors (Rich Dark Mode) ===
    bg_darkest: str = "#080a0e"       # Ultra dark
    bg_dark: str = "#0d1117"          # Main background
    bg_card: str = "#161b22"          # Card/Panel background
    bg_card_elevated: str = "#1c2128" # Elevated cards
    bg_card_hover: str = "#21262d"    # Hover state
    bg_input: str = "#0d1117"         # Input fields
    bg_header: str = "#0d1117"        # Header areas
    bg_sidebar: str = "#0a0c10"       # Sidebar
    bg_overlay: str = "#000000cc"     # Modal overlay
    bg_hover: str = "#21262d"         # Hover state (alias)

    # === Gradient Backgrounds ===
    gradient_header_start: str = "#161b22"
    gradient_header_end: str = "#0d1117"
    gradient_card_start: str = "#1c2128"
    gradient_card_end: str = "#161b22"
    gradient_accent_start: str = "#0066cc"
    gradient_accent_end: str = "#004c99"

    # === Text Colors ===
    text_primary: str = "#f0f6fc"     # Bright white
    text_secondary: str = "#8b949e"   # Secondary text
    text_muted: str = "#6e7681"       # Muted text
    text_link: str = "#58a6ff"        # Links
    text_accent: str = "#79c0ff"      # Accent text
    text_highlight: str = "#ffffff"   # Highlighted text

    # === Border Colors ===
    border: str = "#30363d"
    border_light: str = "#3d444d"
    border_focus: str = "#1f6feb"
    border_muted: str = "#21262d"
    border_glow: str = "#1f6feb50"

    # === Status Colors (Premium Vibrant) ===
    success: str = "#238636"
    success_hover: str = "#2ea043"
    success_light: str = "#3fb950"
    success_glow: str = "#23863630"

    warning: str = "#d29922"
    warning_hover: str = "#e3b341"
    warning_light: str = "#f0c84d"
    warning_glow: str = "#d2992230"

    danger: str = "#da3633"
    danger_hover: str = "#f85149"
    danger_light: str = "#ff7b72"
    danger_glow: str = "#da363330"

    info: str = "#1f6feb"
    info_hover: str = "#388bfd"
    info_light: str = "#58a6ff"
    info_glow: str = "#1f6feb30"

    # === Special Premium Colors ===
    gold: str = "#ffd700"
    gold_dark: str = "#b8860b"
    gold_shimmer: str = "#ffed4a"
    silver: str = "#c0c0c0"
    silver_shimmer: str = "#e8e8e8"
    bronze: str = "#cd7f32"
    platinum: str = "#e5e4e2"

    # === Glass Effect Colors ===
    glass_bg: str = "#ffffff08"
    glass_border: str = "#ffffff15"
    glass_highlight: str = "#ffffff10"

    # === Team Colors (NPB) ===
    central_league: str = "#1a5fb4"
    pacific_league: str = "#e01b24"

    # === Stat Rating Colors (Power Pro Style - Premium) ===
    rating_s: str = "#ff3333"   # S Rank (90+) - Vibrant Red
    rating_a: str = "#ff8c00"   # A Rank (80-89) - Orange
    rating_b: str = "#ffd700"   # B Rank (70-79) - Gold
    rating_c: str = "#ffff00"   # C Rank (60-69) - Yellow
    rating_d: str = "#00ff00"   # D Rank (50-59) - Green
    rating_e: str = "#00bfff"   # E Rank (40-49) - Sky Blue
    rating_f: str = "#a0a0a0"   # F Rank (30-39) - Gray
    rating_g: str = "#606060"   # G Rank (1-29) - Dark Gray

    # === Shadow/Glow Properties ===
    shadow_color: str = "#00000080"
    shadow_blur: int = 20
    glow_color: str = "#0066cc40"
    glow_blur: int = 30

    # === Animation Durations (ms) ===
    anim_fast: int = 150
    anim_normal: int = 250
    anim_slow: int = 400

    # === Border Radii ===
    radius_small: int = 4
    radius_medium: int = 8
    radius_large: int = 12
    radius_xl: int = 16
    radius_round: int = 9999

    # === Spacing ===
    spacing_xs: int = 4
    spacing_sm: int = 8
    spacing_md: int = 16
    spacing_lg: int = 24
    spacing_xl: int = 32

    # === Aliases for compatibility ===
    @property
    def accent(self) -> str:
        return self.primary

    @property
    def card_bg(self) -> str:
        return self.bg_card

    @property
    def bg_secondary(self) -> str:
        return self.bg_card_hover

    @staticmethod
    def get_rating_color(value: int) -> str:
        """Get color based on stat rating (1-99 scale)"""
        t = Theme()
        if value >= 90:
            return t.rating_s
        elif value >= 80:
            return t.rating_a
        elif value >= 70:
            return t.rating_b
        elif value >= 60:
            return t.rating_c
        elif value >= 50:
            return t.rating_d
        elif value >= 40:
            return t.rating_e
        elif value >= 30:
            return t.rating_f
        else:
            return t.rating_g

    @staticmethod
    def get_rating_rank(value: int) -> str:
        """Get rank letter based on stat value"""
        if value >= 90:
            return "S"
        elif value >= 80:
            return "A"
        elif value >= 70:
            return "B"
        elif value >= 60:
            return "C"
        elif value >= 50:
            return "D"
        elif value >= 40:
            return "E"
        elif value >= 30:
            return "F"
        else:
            return "G"


class ThemeManager:
    """Manages application theming with premium effects"""

    _instance = None
    _theme = Theme()
    _current_scale = 1.0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_theme(cls) -> Theme:
        return cls._theme

    @classmethod
    def set_scale(cls, scale: float):
        """Set UI scale factor"""
        cls._current_scale = scale

    @classmethod
    def get_scale(cls) -> float:
        return cls._current_scale

    @classmethod
    def apply_theme(cls, app: QApplication):
        """Apply premium theme to the entire application"""
        theme = cls._theme

        # Set application-wide palette
        palette = QPalette()

        # Window colors
        palette.setColor(QPalette.Window, QColor(theme.bg_dark))
        palette.setColor(QPalette.WindowText, QColor(theme.text_primary))
        palette.setColor(QPalette.Base, QColor(theme.bg_input))
        palette.setColor(QPalette.AlternateBase, QColor(theme.bg_card))
        palette.setColor(QPalette.Text, QColor(theme.text_primary))
        palette.setColor(QPalette.BrightText, QColor(theme.text_accent))

        # Button colors
        palette.setColor(QPalette.Button, QColor(theme.bg_card))
        palette.setColor(QPalette.ButtonText, QColor(theme.text_primary))

        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(theme.primary))
        palette.setColor(QPalette.HighlightedText, QColor(theme.text_highlight))

        # Link colors
        palette.setColor(QPalette.Link, QColor(theme.text_link))
        palette.setColor(QPalette.LinkVisited, QColor(theme.primary_dark))

        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(theme.text_muted))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(theme.text_muted))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(theme.text_muted))

        app.setPalette(palette)

        # Set global stylesheet
        app.setStyleSheet(cls.get_stylesheet())

    @classmethod
    def get_stylesheet(cls) -> str:
        """Generate comprehensive premium stylesheet"""
        t = cls._theme

        return f"""
        /* === Global Styles === */
        * {{
            font-family: "Yu Gothic UI", "Meiryo UI", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        QMainWindow, QDialog, QWidget {{
            background-color: {t.bg_dark};
            color: {t.text_primary};
        }}

        /* === Premium Scroll Bars === */
        QScrollBar:vertical {{
            background-color: {t.bg_darkest};
            width: 10px;
            margin: 0;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.border_light}, stop:1 {t.border});
            min-height: 40px;
            border-radius: 5px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.primary_light}, stop:1 {t.primary});
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar:horizontal {{
            background-color: {t.bg_darkest};
            height: 10px;
            margin: 0;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.border_light}, stop:1 {t.border});
            min-width: 40px;
            border-radius: 5px;
            margin: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.primary_light}, stop:1 {t.primary});
        }}

        /* === Premium Buttons === */
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_card});
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 500;
            min-height: 20px;
        }}

        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_hover}, stop:1 {t.bg_card_elevated});
            border-color: {t.primary};
        }}

        QPushButton:pressed {{
            background: {t.bg_card};
            border-color: {t.primary_light};
        }}

        QPushButton:disabled {{
            background-color: {t.bg_input};
            color: {t.text_muted};
            border-color: {t.border_muted};
        }}

        QPushButton[class="primary"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.primary_light}, stop:1 {t.primary});
            border: 1px solid {t.primary};
            color: white;
            font-weight: 600;
        }}

        QPushButton[class="primary"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.primary_hover}, stop:1 {t.primary_light});
            border-color: {t.primary_hover};
        }}

        QPushButton[class="success"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.success_light}, stop:1 {t.success});
            border: 1px solid {t.success};
            color: white;
            font-weight: 600;
        }}

        QPushButton[class="success"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.success_hover}, stop:1 {t.success_light});
        }}

        QPushButton[class="danger"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.danger_light}, stop:1 {t.danger});
            border: 1px solid {t.danger};
            color: white;
            font-weight: 600;
        }}

        QPushButton[class="danger"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.danger_hover}, stop:1 {t.danger_light});
        }}

        QPushButton[class="gold"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.accent_gold_light}, stop:1 {t.accent_gold});
            border: 1px solid {t.accent_gold};
            color: #1a1a1a;
            font-weight: 600;
        }}

        /* === Premium Input Fields === */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {t.bg_input};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 14px;
            selection-background-color: {t.primary};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {t.primary};
            padding: 9px 13px;
            outline: none;
        }}

        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border-color: {t.border_light};
        }}

        /* === Premium Combo Box === */
        QComboBox {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_card});
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 14px;
            min-width: 120px;
        }}

        QComboBox:hover {{
            border-color: {t.primary};
        }}

        QComboBox:focus {{
            border: 2px solid {t.primary};
            padding: 9px 13px;
        }}

        QComboBox::drop-down {{
            border: none;
            padding-right: 12px;
            width: 24px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {t.text_secondary};
        }}

        QComboBox::down-arrow:hover {{
            border-top-color: {t.primary};
        }}

        QComboBox QAbstractItemView {{
            background-color: {t.bg_card_elevated};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 8px;
            selection-background-color: {t.primary};
            outline: none;
            padding: 4px;
        }}

        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: 4px;
            min-height: 24px;
        }}

        QComboBox QAbstractItemView::item:hover {{
            background-color: {t.bg_card_hover};
        }}

        /* === Premium Tables === */
        QTableWidget, QTableView {{
            background-color: {t.bg_card};
            alternate-background-color: {t.bg_card_elevated};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 12px;
            gridline-color: {t.border_muted};
            selection-background-color: {t.primary};
            font-size: 13px;
        }}

        QTableWidget::item, QTableView::item {{
            padding: 12px 8px;
            border-bottom: 1px solid {t.border_muted};
        }}

        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {t.primary};
            color: white;
        }}

        QTableWidget::item:hover, QTableView::item:hover {{
            background-color: {t.bg_card_hover};
        }}

        QHeaderView {{
            background-color: transparent;
        }}

        QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_card});
            color: {t.text_secondary};
            border: none;
            border-bottom: 2px solid {t.primary};
            border-right: 1px solid {t.border_muted};
            padding: 14px 12px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        QHeaderView::section:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_hover}, stop:1 {t.bg_card_elevated});
            color: {t.text_primary};
        }}

        QHeaderView::section:last {{
            border-right: none;
        }}

        /* === Premium Tab Widget === */
        QTabWidget::pane {{
            background-color: {t.bg_card};
            border: 1px solid {t.border};
            border-radius: 12px;
            border-top-left-radius: 0;
            margin-top: -1px;
        }}

        QTabBar::tab {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card}, stop:1 {t.bg_dark});
            color: {t.text_secondary};
            border: 1px solid {t.border};
            border-bottom: none;
            padding: 12px 24px;
            margin-right: 2px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            font-size: 13px;
            font-weight: 600;
        }}

        QTabBar::tab:selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_card});
            color: {t.text_primary};
            border-bottom: 3px solid {t.primary};
            margin-bottom: -1px;
        }}

        QTabBar::tab:hover:!selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_hover}, stop:1 {t.bg_card});
            color: {t.text_primary};
        }}

        /* === Premium Tree View === */
        QTreeView, QTreeWidget {{
            background-color: {t.bg_card};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 12px;
            selection-background-color: {t.primary};
            outline: none;
        }}

        QTreeView::item, QTreeWidget::item {{
            padding: 8px;
            border-radius: 6px;
            margin: 2px 4px;
        }}

        QTreeView::item:hover, QTreeWidget::item:hover {{
            background-color: {t.bg_card_hover};
        }}

        QTreeView::item:selected, QTreeWidget::item:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.primary}, stop:1 {t.primary_light});
            color: white;
        }}

        /* === Premium List Widget === */
        QListWidget, QListView {{
            background-color: {t.bg_card};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 12px;
            selection-background-color: {t.primary};
            outline: none;
            padding: 4px;
        }}

        QListWidget::item, QListView::item {{
            padding: 12px 16px;
            border-radius: 8px;
            margin: 2px 4px;
        }}

        QListWidget::item:hover, QListView::item:hover {{
            background-color: {t.bg_card_hover};
        }}

        QListWidget::item:selected, QListView::item:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.primary}, stop:1 {t.primary_light});
            color: white;
        }}

        /* === Premium Group Box === */
        QGroupBox {{
            background-color: {t.bg_card};
            border: 1px solid {t.border};
            border-radius: 12px;
            margin-top: 20px;
            padding: 20px 16px 16px 16px;
            font-size: 14px;
            font-weight: 600;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 6px 16px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.primary}, stop:1 {t.primary_dark});
            color: white;
            border-radius: 6px;
            left: 16px;
        }}

        /* === Labels === */
        QLabel {{
            color: {t.text_primary};
        }}

        QLabel[class="header"] {{
            font-size: 28px;
            font-weight: 700;
            color: {t.text_primary};
        }}

        QLabel[class="subheader"] {{
            font-size: 18px;
            font-weight: 600;
            color: {t.text_secondary};
        }}

        QLabel[class="muted"] {{
            color: {t.text_muted};
        }}

        QLabel[class="accent"] {{
            color: {t.primary_light};
            font-weight: 600;
        }}

        QLabel[class="gold"] {{
            color: {t.accent_gold};
            font-weight: 700;
        }}

        /* === Premium Progress Bar === */
        QProgressBar {{
            background-color: {t.bg_input};
            border: none;
            border-radius: 6px;
            height: 12px;
            text-align: center;
            font-size: 11px;
            font-weight: 600;
            color: {t.text_primary};
        }}

        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.primary}, stop:1 {t.primary_light});
            border-radius: 6px;
        }}

        /* === Premium Slider === */
        QSlider::groove:horizontal {{
            background-color: {t.bg_input};
            height: 8px;
            border-radius: 4px;
        }}

        QSlider::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.primary_light}, stop:1 {t.primary});
            width: 20px;
            height: 20px;
            margin: -6px 0;
            border-radius: 10px;
            border: 2px solid {t.primary_dark};
        }}

        QSlider::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.primary_hover}, stop:1 {t.primary_light});
            border-color: {t.primary};
        }}

        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.primary_dark}, stop:1 {t.primary});
            border-radius: 4px;
        }}

        /* === Premium Check Box & Radio === */
        QCheckBox, QRadioButton {{
            color: {t.text_primary};
            spacing: 10px;
            font-size: 14px;
        }}

        QCheckBox::indicator, QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_card});
            border: 2px solid {t.border};
            border-radius: 6px;
        }}

        QRadioButton::indicator {{
            border-radius: 11px;
        }}

        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.primary_light}, stop:1 {t.primary});
            border-color: {t.primary};
        }}

        QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
            border-color: {t.primary};
        }}

        /* === Premium Spin Box === */
        QSpinBox, QDoubleSpinBox {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_card});
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
        }}

        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {t.primary};
        }}

        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            background: {t.bg_card_hover};
            border: none;
            border-left: 1px solid {t.border};
            border-top-right-radius: 7px;
            width: 24px;
        }}

        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background: {t.bg_card_hover};
            border: none;
            border-left: 1px solid {t.border};
            border-bottom-right-radius: 7px;
            width: 24px;
        }}

        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background: {t.primary};
        }}

        /* === Premium Tool Tips === */
        QToolTip {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_card});
            color: {t.text_primary};
            border: 1px solid {t.primary};
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 13px;
        }}

        /* === Premium Menu === */
        QMenu {{
            background-color: {t.bg_card_elevated};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 12px;
            padding: 8px;
        }}

        QMenu::item {{
            padding: 10px 24px;
            border-radius: 6px;
            margin: 2px 4px;
        }}

        QMenu::item:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.primary}, stop:1 {t.primary_light});
            color: white;
        }}

        QMenu::separator {{
            height: 1px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.5 {t.border}, stop:1 transparent);
            margin: 8px 16px;
        }}

        QMenuBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_header});
            color: {t.text_primary};
            border-bottom: 1px solid {t.border};
            padding: 4px;
        }}

        QMenuBar::item {{
            padding: 8px 16px;
            border-radius: 6px;
        }}

        QMenuBar::item:selected {{
            background-color: {t.bg_card_hover};
        }}

        /* === Premium Status Bar === */
        QStatusBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_header}, stop:1 {t.bg_darkest});
            color: {t.text_secondary};
            border-top: 1px solid {t.border};
            font-size: 12px;
        }}

        /* === Premium Splitter === */
        QSplitter::handle {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.5 {t.border}, stop:1 transparent);
        }}

        QSplitter::handle:horizontal {{
            width: 4px;
        }}

        QSplitter::handle:vertical {{
            height: 4px;
        }}

        QSplitter::handle:hover {{
            background: {t.primary};
        }}

        /* === Message Box === */
        QMessageBox {{
            background-color: {t.bg_card};
        }}

        QMessageBox QLabel {{
            color: {t.text_primary};
            font-size: 14px;
        }}

        /* === Dialog === */
        QDialog {{
            background-color: {t.bg_card};
            border: 1px solid {t.border};
            border-radius: 12px;
        }}

        /* === Frame === */
        QFrame[class="card"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:1 {t.bg_card});
            border: 1px solid {t.border};
            border-radius: 12px;
        }}

        QFrame[class="card"]:hover {{
            border-color: {t.primary};
        }}

        QFrame[class="premium-card"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {t.bg_card_elevated}, stop:0.5 {t.bg_card}, stop:1 {t.bg_card_elevated});
            border: 1px solid {t.accent_gold};
            border-radius: 12px;
        }}
        """

    @classmethod
    def create_shadow_effect(cls, widget: QWidget, blur: int = 20, color: str = None, offset_y: int = 4):
        """Create a drop shadow effect for a widget"""
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(blur)
        effect.setColor(QColor(color or cls._theme.shadow_color))
        effect.setOffset(0, offset_y)
        widget.setGraphicsEffect(effect)
        return effect

    @classmethod
    def create_glow_effect(cls, widget: QWidget, color: str = None, blur: int = 30):
        """Create a glow effect for a widget"""
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(blur)
        effect.setColor(QColor(color or cls._theme.glow_color))
        effect.setOffset(0, 0)
        widget.setGraphicsEffect(effect)
        return effect


# Convenience function
def get_theme() -> Theme:
    return ThemeManager.get_theme()
