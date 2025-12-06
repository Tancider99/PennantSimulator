# -*- coding: utf-8 -*-
"""
NPB Pennant Simulator - Panel Widgets
OOTP-Style Layout Panels and Containers
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QStackedWidget, QSplitter, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QBrush

import sys
sys.path.insert(0, '..')
from UI.theme import get_theme


class PageHeader(QFrame):
    """Premium page header with title, subtitle and actions area"""

    def __init__(self, title: str, subtitle: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._title = title
        self._subtitle = subtitle
        self._icon = icon

        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self):
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.bg_card},
                    stop:0.5 {self.theme.bg_card_elevated},
                    stop:1 {self.theme.bg_card});
                border: 1px solid {self.theme.border};
                border-radius: 16px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # Title area
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title_text = f"{self._icon}  {self._title}" if self._icon else self._title
        self.title_label = QLabel(title_text)
        self.title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        title_layout.addWidget(self.title_label)

        if self._subtitle:
            self.subtitle_label = QLabel(self._subtitle)
            self.subtitle_label.setStyleSheet(f"""
                font-size: 12px;
                color: {self.theme.text_muted};
                background: transparent;
            """)
            title_layout.addWidget(self.subtitle_label)

        layout.addLayout(title_layout)
        layout.addStretch()

        # Actions area
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(12)
        layout.addLayout(self.actions_layout)

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

    def set_title(self, title: str, icon: str = None):
        """Update the title"""
        if icon is not None:
            self._icon = icon
        self._title = title
        title_text = f"{self._icon}  {title}" if self._icon else title
        self.title_label.setText(title_text)

    def add_action(self, widget):
        """Add a widget to the actions area"""
        self.actions_layout.addWidget(widget)


class SidebarPanel(QWidget):
    """Left sidebar navigation panel - Premium design"""

    navigation_clicked = Signal(str)  # Emits section name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.setFixedWidth(200)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            background-color: {self.theme.bg_sidebar};
            border-right: 1px solid {self.theme.border_muted};
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(4)

        # Logo/Title area - Premium style
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(2)

        self.title_label = QLabel("NPB")
        self.title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 200;
            letter-spacing: 8px;
            color: {self.theme.text_primary};
            padding: 0;
        """)
        logo_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("PENNANT SIM")
        self.subtitle_label.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 3px;
            color: {self.theme.text_muted};
            padding: 0 0 16px 0;
        """)
        logo_layout.addWidget(self.subtitle_label)

        layout.addWidget(logo_container)

        # Separator line
        sep_line = QFrame()
        sep_line.setFrameShape(QFrame.HLine)
        sep_line.setStyleSheet(f"background-color: {self.theme.border_muted}; max-height: 1px;")
        layout.addWidget(sep_line)

        layout.addSpacing(16)

        # Navigation items will be added here
        self.nav_layout = QVBoxLayout()
        self.nav_layout.setSpacing(2)
        layout.addLayout(self.nav_layout)

        layout.addStretch()

        # Version info at bottom - Premium style
        version_container = QWidget()
        version_layout = QVBoxLayout(version_container)
        version_layout.setContentsMargins(0, 0, 0, 0)
        version_layout.setSpacing(4)

        version_sep = QFrame()
        version_sep.setFrameShape(QFrame.HLine)
        version_sep.setStyleSheet(f"background-color: {self.theme.border_muted}; max-height: 1px;")
        version_layout.addWidget(version_sep)

        version_label = QLabel("VERSION 2.0")
        version_label.setStyleSheet(f"""
            font-size: 9px;
            font-weight: 500;
            letter-spacing: 2px;
            color: {self.theme.text_muted};
            padding-top: 12px;
        """)
        version_layout.addWidget(version_label)

        layout.addWidget(version_container)

    def add_nav_item(self, icon: str, text: str, section: str):
        """Add a navigation item - icon parameter kept for compatibility but not used"""
        from .buttons import TabButton
        btn = TabButton(text)
        btn.clicked.connect(lambda: self._on_nav_click(section, btn))
        btn.setProperty("section", section)
        self.nav_layout.addWidget(btn)
        return btn

    def add_separator(self, label: str = ""):
        """Add a section separator"""
        if label:
            sep_label = QLabel(label)
            sep_label.setStyleSheet(f"""
                font-size: 9px;
                font-weight: 600;
                color: {self.theme.text_muted};
                padding: 20px 12px 8px 12px;
                letter-spacing: 2px;
            """)
            self.nav_layout.addWidget(sep_label)
        else:
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet(f"background-color: {self.theme.border_muted};")
            separator.setFixedHeight(1)
            self.nav_layout.addWidget(separator)

    def _on_nav_click(self, section: str, clicked_btn):
        """Handle navigation click"""
        # Deselect all buttons
        for i in range(self.nav_layout.count()):
            item = self.nav_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'set_active'):
                    widget.set_active(False)

        # Select clicked button
        clicked_btn.set_active(True)

        self.navigation_clicked.emit(section)


class HeaderPanel(QWidget):
    """Top header panel with title and actions"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._title = title
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            background-color: {self.theme.bg_header};
            border-bottom: 1px solid {self.theme.border};
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # Title
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 600;
            color: {self.theme.text_primary};
        """)
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Actions area
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(12)
        layout.addLayout(self.actions_layout)

    def set_title(self, title: str):
        self._title = title
        self.title_label.setText(title)

    def add_action_widget(self, widget: QWidget):
        """Add a widget to the actions area"""
        self.actions_layout.addWidget(widget)


class ContentPanel(QScrollArea):
    """Scrollable content panel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_base_ui()
        self._setup_ui()

    def _setup_base_ui(self):
        """Setup base panel - must be called before subclass _setup_ui"""
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.theme.bg_dark};
                border: none;
            }}
        """)

        # Content widget
        self.content = QWidget()
        self.content.setStyleSheet(f"background-color: {self.theme.bg_dark};")
        self.setWidget(self.content)

        # Layout
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(20)

    def _setup_ui(self):
        """Override in subclasses to add custom UI elements"""
        pass

    def add_widget(self, widget: QWidget):
        """Add widget to content"""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add layout to content"""
        self.content_layout.addLayout(layout)

    def add_stretch(self):
        """Add stretch to content"""
        self.content_layout.addStretch()

    def clear(self):
        """Clear all content"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class InfoPanel(QFrame):
    """Information display panel with title"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._title = title
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme.bg_card};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
            }}
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        if self._title:
            title_label = QLabel(self._title)
            title_label.setStyleSheet(f"""
                font-size: 16px;
                font-weight: 600;
                color: {self.theme.text_primary};
                padding-bottom: 8px;
                border-bottom: 1px solid {self.theme.border_muted};
            """)
            self.main_layout.addWidget(title_label)

        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        self.main_layout.addLayout(self.content_layout)

    def add_row(self, label: str, value: str, value_color: str = None):
        """Add a label-value row"""
        row = QHBoxLayout()

        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            font-size: 13px;
            color: {self.theme.text_secondary};
        """)

        value_widget = QLabel(value)
        color = value_color or self.theme.text_primary
        value_widget.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 500;
            color: {color};
        """)

        row.addWidget(label_widget)
        row.addStretch()
        row.addWidget(value_widget)

        self.content_layout.addLayout(row)

    def add_widget(self, widget: QWidget):
        """Add widget to content"""
        self.content_layout.addWidget(widget)


class SplitPanel(QSplitter):
    """Resizable split panel"""

    def __init__(self, orientation: Qt.Orientation = Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.theme = get_theme()
        self._setup_style()

    def _setup_style(self):
        self.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {self.theme.border};
            }}
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            QSplitter::handle:vertical {{
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.theme.primary};
            }}
        """)


class StatusPanel(QWidget):
    """Bottom status panel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(32)
        self.setStyleSheet(f"""
            background-color: {self.theme.bg_header};
            border-top: 1px solid {self.theme.border};
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        self.left_label = QLabel("")
        self.left_label.setStyleSheet(f"color: {self.theme.text_muted}; font-size: 12px;")
        layout.addWidget(self.left_label)

        layout.addStretch()

        self.right_label = QLabel("")
        self.right_label.setStyleSheet(f"color: {self.theme.text_muted}; font-size: 12px;")
        layout.addWidget(self.right_label)

    def set_left_text(self, text: str):
        self.left_label.setText(text)

    def set_right_text(self, text: str):
        self.right_label.setText(text)


class PageContainer(QStackedWidget):
    """Container for multiple pages with transitions"""

    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._pages = {}

    def add_page(self, name: str, widget: QWidget) -> int:
        """Add a page and return its index"""
        index = self.addWidget(widget)
        self._pages[name] = index
        return index

    def show_page(self, name: str):
        """Show a page by name"""
        if name in self._pages:
            self.setCurrentIndex(self._pages[name])
            self.page_changed.emit(self._pages[name])

    def get_page(self, name: str) -> QWidget:
        """Get a page widget by name"""
        if name in self._pages:
            return self.widget(self._pages[name])
        return None


class GradientPanel(QWidget):
    """Panel with gradient background"""

    def __init__(self, colors: list = None, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._colors = colors or [self.theme.primary_dark, self.theme.bg_dark]

    def set_colors(self, colors: list):
        self._colors = colors
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self.height())
        for i, color in enumerate(self._colors):
            gradient.setColorAt(i / (len(self._colors) - 1), QColor(color))

        painter.fillRect(self.rect(), gradient)


class FloatingPanel(QWidget):
    """Floating panel with shadow"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.bg_card};
                border: 1px solid {self.theme.border};
                border-radius: 12px;
            }}
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

        # Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(16)

    def add_widget(self, widget: QWidget):
        self.main_layout.addWidget(widget)


class ToolbarPanel(QWidget):
    """Toolbar panel with actions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            background-color: {self.theme.bg_card};
            border: 1px solid {self.theme.border};
            border-radius: 8px;
        """)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 12, 0)
        self.layout.setSpacing(8)

    def add_widget(self, widget: QWidget):
        self.layout.addWidget(widget)

    def add_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet(f"background-color: {self.theme.border};")
        separator.setFixedWidth(1)
        self.layout.addWidget(separator)

    def add_stretch(self):
        self.layout.addStretch()
