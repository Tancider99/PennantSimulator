# -*- coding: utf-8 -*-
"""
Baseball Team Architect 2027 - Theme System
Dark/Light Theme with Font Size Support
"""
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget
from PySide6.QtGui import QColor, QPalette, QFont
from dataclasses import dataclass


@dataclass
class Theme:
    """Dark Industrial Theme (Default)"""
    
    name: str = "dark"
    
    # === Main Colors ===
    bg_darkest: str = "#0b0c10"       
    bg_dark: str = "#141619"          
    bg_card: str = "#1e2126"          
    bg_card_elevated: str = "#262a30" 
    bg_card_hover: str = "#323842"    
    bg_sidebar: str = "#0b0c10"       
    
    # === Compatibility Aliases ===
    bg_hover: str = "#323842"         
    bg_selected: str = "#2c313a"      
    
    # === Accents ===
    primary: str = "#ffffff"          
    primary_hover: str = "#e0e0e0"
    primary_dark: str = "#cccccc"
    primary_light: str = "#ffffff"    
    
    accent_blue: str = "#5fbcd3"      
    accent_blue_hover: str = "#78cce2" 
    accent_orange: str = "#d65d0e"    
    accent_orange_hover: str = "#e67f33" 
    accent_red: str = "#cc241d"       
    accent_red_hover: str = "#e04f4f" 
    
    # === Text Colors ===
    text_primary: str = "#f0f0f0"     
    text_secondary: str = "#9da5b4"   
    text_muted: str = "#5c6370"       
    text_highlight: str = "#0b0c10"   
    text_accent: str = "#5fbcd3"      
    text_link: str = "#5fbcd3"        

    # === Borders ===
    border: str = "#3e4451"
    border_light: str = "#4e5766"
    border_muted: str = "#2c313a"     
    border_focus: str = "#ffffff"
    
    # === Status Colors ===
    success: str = "#98c379"
    success_light: str = "#b5d49d"
    success_hover: str = "#86b366"
    
    warning: str = "#e5c07b"
    warning_light: str = "#ebd09e"
    warning_hover: str = "#d1ad6b"
    
    danger: str = "#e06c75"
    danger_light: str = "#ea959b"
    danger_hover: str = "#d65560"
    
    error: str = "#e06c75"
    
    info: str = "#61afef"
    info_light: str = "#8dc5f4"
    info_hover: str = "#4d9fe8"

    # === Premium Colors ===
    gold: str = "#d65d0e"             
    silver: str = "#9da5b4"
    bronze: str = "#8f5e38"
    accent_gold: str = "#d65d0e"      
    gradient_start: str = "#d65d0e"   
    gradient_end: str = "#e67f33"

    # === UI Elements ===
    bg_overlay: str = "#000000dd"
    bg_input: str = "#0b0c10"
    bg_header: str = "#141619"

    # === Team Colors ===
    north_league: str = "#5fbcd3"
    south_league: str = "#e06c75"

    # === Rating Colors ===
    rating_s: str = "#ff6b6b"   
    rating_a: str = "#ffa726"   
    rating_b: str = "#ffd700"   
    rating_c: str = "#ffee58"   
    rating_d: str = "#66bb6a"   
    rating_e: str = "#42a5f5"   
    rating_f: str = "#bdbdbd"   
    rating_g: str = "#757575"   

    # === Metrics ===
    radius_small: int = 0
    radius_medium: int = 0
    radius_large: int = 2
    
    shadow_color: str = "#000000"
    shadow_blur: int = 10

    @property
    def accent(self) -> str:
        return self.accent_blue

    @staticmethod
    def get_rating_color(value: int) -> str:
        t = Theme()
        if value >= 90: return t.rating_s
        elif value >= 80: return t.rating_a
        elif value >= 70: return t.rating_b
        elif value >= 60: return t.rating_c
        elif value >= 50: return t.rating_d
        elif value >= 40: return t.rating_e
        elif value >= 30: return t.rating_f
        else: return t.rating_g
        
    @staticmethod
    def get_rating_rank(value: int) -> str:
        if value >= 90: return "S"
        elif value >= 80: return "A"
        elif value >= 70: return "B"
        elif value >= 60: return "C"
        elif value >= 50: return "D"
        elif value >= 40: return "E"
        elif value >= 30: return "F"
        else: return "G"


@dataclass
class LightTheme:
    """Light Theme"""
    
    name: str = "light"
    
    # === Main Colors ===
    bg_darkest: str = "#e8e8e8"       
    bg_dark: str = "#f5f5f5"          
    bg_card: str = "#ffffff"          
    bg_card_elevated: str = "#fafafa" 
    bg_card_hover: str = "#f0f0f0"    
    bg_sidebar: str = "#e8e8e8"       
    
    # === Compatibility Aliases ===
    bg_hover: str = "#f0f0f0"         
    bg_selected: str = "#e0e0e0"      
    
    # === Accents ===
    primary: str = "#1a1a1a"          
    primary_hover: str = "#333333"
    primary_dark: str = "#000000"
    primary_light: str = "#333333"    
    
    accent_blue: str = "#0066cc"      
    accent_blue_hover: str = "#0055aa" 
    accent_orange: str = "#d65d0e"    
    accent_orange_hover: str = "#e67f33" 
    accent_red: str = "#cc241d"       
    accent_red_hover: str = "#e04f4f" 
    
    # === Text Colors ===
    text_primary: str = "#1a1a1a"     
    text_secondary: str = "#555555"   
    text_muted: str = "#888888"       
    text_highlight: str = "#ffffff"   
    text_accent: str = "#0066cc"      
    text_link: str = "#0066cc"        

    # === Borders ===
    border: str = "#cccccc"
    border_light: str = "#dddddd"
    border_muted: str = "#e0e0e0"     
    border_focus: str = "#1a1a1a"
    
    # === Status Colors ===
    success: str = "#2e7d32"
    success_light: str = "#4caf50"
    success_hover: str = "#1b5e20"
    
    warning: str = "#ef6c00"
    warning_light: str = "#ff9800"
    warning_hover: str = "#e65100"
    
    danger: str = "#c62828"
    danger_light: str = "#ef5350"
    danger_hover: str = "#b71c1c"
    
    error: str = "#c62828"
    
    info: str = "#1565c0"
    info_light: str = "#1e88e5"
    info_hover: str = "#0d47a1"

    # === Premium Colors ===
    gold: str = "#d65d0e"             
    silver: str = "#757575"
    bronze: str = "#8f5e38"
    accent_gold: str = "#d65d0e"      
    gradient_start: str = "#d65d0e"   
    gradient_end: str = "#e67f33"

    # === UI Elements ===
    bg_overlay: str = "#00000099"
    bg_input: str = "#ffffff"
    bg_header: str = "#f5f5f5"

    # === Team Colors ===
    north_league: str = "#0066cc"
    south_league: str = "#c62828"

    # === Rating Colors ===
    rating_s: str = "#d32f2f"   
    rating_a: str = "#e65100"   
    rating_b: str = "#f9a825"   
    rating_c: str = "#c0ca33"   
    rating_d: str = "#43a047"   
    rating_e: str = "#1e88e5"   
    rating_f: str = "#757575"   
    rating_g: str = "#9e9e9e"   

    # === Metrics ===
    radius_small: int = 0
    radius_medium: int = 0
    radius_large: int = 2
    
    shadow_color: str = "#00000033"
    shadow_blur: int = 10

    @property
    def accent(self) -> str:
        return self.accent_blue

    @staticmethod
    def get_rating_color(value: int) -> str:
        t = LightTheme()
        if value >= 90: return t.rating_s
        elif value >= 80: return t.rating_a
        elif value >= 70: return t.rating_b
        elif value >= 60: return t.rating_c
        elif value >= 50: return t.rating_d
        elif value >= 40: return t.rating_e
        elif value >= 30: return t.rating_f
        else: return t.rating_g
        
    @staticmethod
    def get_rating_rank(value: int) -> str:
        if value >= 90: return "S"
        elif value >= 80: return "A"
        elif value >= 70: return "B"
        elif value >= 60: return "C"
        elif value >= 50: return "D"
        elif value >= 40: return "E"
        elif value >= 30: return "F"
        else: return "G"


class ThemeManager:
    """Manages application theming with Dark/Light support"""

    _instance = None
    _theme = Theme()  # Default dark theme
    _current_scale = 1.0
    _font_size = 1  # 0=小, 1=中, 2=大
    _app = None
    _theme_change_callbacks = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_theme(cls):
        return cls._theme
    
    @classmethod
    def set_theme(cls, theme_name: str):
        """Switch between dark and light themes"""
        if theme_name == "light":
            cls._theme = LightTheme()
        else:
            cls._theme = Theme()
        
        # Reapply theme if app is set
        if cls._app:
            cls.apply_theme(cls._app)
            
        # Notify callbacks
        for callback in cls._theme_change_callbacks:
            try:
                callback()
            except:
                pass
    
    @classmethod
    def set_font_size(cls, size: int):
        """Set font size: 0=小(10px), 1=中(12px), 2=大(14px)"""
        cls._font_size = size
        
        # Reapply if app exists
        if cls._app:
            cls.apply_theme(cls._app)
    
    @classmethod
    def get_font_size_px(cls) -> int:
        """Get current font size in pixels"""
        sizes = {0: 10, 1: 12, 2: 14}
        return sizes.get(cls._font_size, 12)
    
    @classmethod
    def register_theme_change_callback(cls, callback):
        """Register callback to be called when theme changes"""
        if callback not in cls._theme_change_callbacks:
            cls._theme_change_callbacks.append(callback)

    @classmethod
    def set_scale(cls, scale: float):
        cls._current_scale = scale

    @classmethod
    def apply_theme(cls, app: QApplication):
        cls._app = app
        theme = cls._theme
        palette = QPalette()
        
        # Base setup
        palette.setColor(QPalette.Window, QColor(theme.bg_dark))
        palette.setColor(QPalette.WindowText, QColor(theme.text_primary))
        palette.setColor(QPalette.Base, QColor(theme.bg_input))
        palette.setColor(QPalette.AlternateBase, QColor(theme.bg_card))
        palette.setColor(QPalette.Text, QColor(theme.text_primary))
        palette.setColor(QPalette.Button, QColor(theme.bg_card))
        palette.setColor(QPalette.ButtonText, QColor(theme.text_primary))
        palette.setColor(QPalette.Highlight, QColor(theme.primary))
        palette.setColor(QPalette.HighlightedText, QColor(theme.text_highlight))
        
        app.setPalette(palette)
        app.setStyleSheet(cls.get_stylesheet())

    @classmethod
    def get_stylesheet(cls) -> str:
        t = cls._theme
        font_size = cls.get_font_size_px()
        
        return f"""
        * {{
            font-family: "Yu Gothic UI", "Meiryo UI", sans-serif;
            font-size: {font_size}px;
            outline: none;
        }}
        QMainWindow, QDialog, QWidget {{
            background-color: {t.bg_dark};
            color: {t.text_primary};
        }}
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {t.bg_darkest};
            width: 12px; margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background-color: {t.border_light};
            min-height: 40px; margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {t.primary};
        }}
        QScrollBar:horizontal {{
            background-color: {t.bg_darkest};
            height: 12px; margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {t.border_light};
            min-width: 40px; margin: 2px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {t.primary};
        }}
        
        /* Buttons - Sharp Industrial Style */
        QPushButton {{
            background-color: {t.bg_card};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: 0px;
            padding: 8px 16px;
            font-size: {font_size + 1}px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        QPushButton:hover {{
            background-color: {t.bg_card_hover};
            border-color: {t.primary};
            color: {t.primary};
        }}
        QPushButton:pressed {{
            background-color: {t.primary};
            color: {t.text_highlight};
        }}
        QPushButton:disabled {{
            color: {t.text_muted};
            background-color: {t.bg_darkest};
            border-color: {t.bg_card};
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {t.border};
            background-color: {t.bg_dark};
            border-top: 1px solid {t.primary};
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {t.text_secondary};
            padding: 8px 16px;
            border: none;
            font-weight: 600;
            text-transform: uppercase;
        }}
        QTabBar::tab:selected {{
            color: {t.primary};
            border-bottom: 2px solid {t.primary};
        }}
        
        /* Labels */
        QLabel {{
            color: {t.text_primary};
        }}
        
        /* ComboBox */
        QComboBox {{
            background-color: {t.bg_input};
            color: {t.text_primary};
            border: 1px solid {t.border};
            padding: 6px 10px;
        }}
        
        /* SpinBox */
        QSpinBox {{
            background-color: {t.bg_input};
            color: {t.text_primary};
            border: 1px solid {t.border};
            padding: 4px 8px;
        }}
        
        /* LineEdit */
        QLineEdit {{
            background-color: {t.bg_input};
            color: {t.text_primary};
            border: 1px solid {t.border};
            padding: 6px 10px;
        }}
        """

    @classmethod
    def create_shadow_effect(cls, widget: QWidget, blur: int = 10, color: str = None):
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(blur)
        effect.setColor(QColor(color or "#000000"))
        effect.setOffset(0, 2)
        widget.setGraphicsEffect(effect)
        return effect


def get_theme():
    return ThemeManager.get_theme()