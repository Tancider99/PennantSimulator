# -*- coding: utf-8 -*-
"""
NPB Pennant Simulator - Team Selection Screen
Ultra Premium OOTP-Style Team Selection Interface
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QGridLayout, QSizePolicy,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Property, QTimer
from PySide6.QtGui import (
    QColor, QPainter, QLinearGradient, QRadialGradient,
    QFont, QPen, QBrush, QPainterPath
)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme, ThemeManager


class TeamCard(QFrame):
    """Ultra Premium Team Selection Card"""

    clicked = Signal()

    def __init__(self, team_name: str, league: str, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._team_name = team_name
        self._league = league
        self._selected = False
        self._hover_progress = 0.0

        self.setFixedHeight(56)
        self.setCursor(Qt.PointingHandCursor)

        self._setup_ui()
        self._setup_animation()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # League color indicator
        league_color = self.theme.central_league if self._league == "central" else self.theme.pacific_league
        self.indicator = QFrame()
        self.indicator.setFixedSize(4, 32)
        self.indicator.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {league_color}, stop:1 {self._darken_color(league_color)});
            border-radius: 2px;
        """)
        layout.addWidget(self.indicator)

        # Team name
        self.name_label = QLabel(self._team_name)
        self.name_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme.text_secondary};
            background: transparent;
        """)
        layout.addWidget(self.name_label)
        layout.addStretch()

        # Selection arrow (hidden by default)
        self.arrow_label = QLabel("→")
        self.arrow_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {self.theme.primary};
            background: transparent;
        """)
        self.arrow_label.hide()
        layout.addWidget(self.arrow_label)

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color"""
        color = QColor(hex_color)
        return color.darker(150).name()

    def _setup_animation(self):
        self._animation = QPropertyAnimation(self, b"hover_progress")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def get_hover_progress(self):
        return self._hover_progress

    def set_hover_progress(self, value):
        self._hover_progress = value
        self.update()

    hover_progress = Property(float, get_hover_progress, set_hover_progress)

    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.name_label.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 600;
                color: {self.theme.text_primary};
                background: transparent;
            """)
            self.arrow_label.show()
        else:
            self.name_label.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 500;
                color: {self.theme.text_secondary};
                background: transparent;
            """)
            self.arrow_label.hide()
        self.update()

    def is_selected(self) -> bool:
        return self._selected

    def get_team_name(self) -> str:
        return self._team_name

    def enterEvent(self, event):
        if not self._selected:
            self._animation.stop()
            self._animation.setStartValue(self._hover_progress)
            self._animation.setEndValue(1.0)
            self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._selected:
            self._animation.stop()
            self._animation.setStartValue(self._hover_progress)
            self._animation.setEndValue(0.0)
            self._animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        if self._selected:
            # Selected state - premium gradient
            gradient = QLinearGradient(0, 0, rect.width(), 0)
            gradient.setColorAt(0, QColor(self.theme.primary + "30"))
            gradient.setColorAt(1, QColor(self.theme.primary + "10"))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(self.theme.primary), 1))
        else:
            # Normal/hover state
            alpha = int(30 + 40 * self._hover_progress)
            painter.setBrush(QColor(self.theme.bg_card_elevated + f"{alpha:02x}"))
            border_alpha = int(40 + 60 * self._hover_progress)
            painter.setPen(QPen(QColor(self.theme.border + f"{border_alpha:02x}"), 1))

        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 10, 10)


class PremiumStatBox(QFrame):
    """Premium stat display box with gradient background"""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._label = label
        self._value = "--"
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.bg_card_elevated},
                    stop:1 {self.theme.bg_card});
                border: 1px solid {self.theme.border};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Label
        label_widget = QLabel(self._label)
        label_widget.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {self.theme.text_muted};
            letter-spacing: 1px;
            text-transform: uppercase;
            background: transparent;
            border: none;
        """)
        layout.addWidget(label_widget)

        # Value
        self.value_widget = QLabel(self._value)
        self.value_widget.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.value_widget)

    def set_value(self, value: str, color: str = None):
        self._value = value
        if color:
            self.value_widget.setStyleSheet(f"""
                font-size: 20px;
                font-weight: 700;
                color: {color};
                background: transparent;
                border: none;
            """)
        else:
            self.value_widget.setStyleSheet(f"""
                font-size: 20px;
                font-weight: 700;
                color: {self.theme.text_primary};
                background: transparent;
                border: none;
            """)
        self.value_widget.setText(value)


class TeamOverviewPanel(QFrame):
    """Ultra Premium Team Overview Panel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._team = None
        self._team_name = None
        self._setup_ui()
        self._setup_effects()

    def _setup_effects(self):
        """Add premium shadow effect"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.bg_card_elevated},
                    stop:0.5 {self.theme.bg_card},
                    stop:1 {self.theme.bg_card_elevated});
                border: 1px solid {self.theme.border};
                border-radius: 16px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === Header with gradient accent ===
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.primary},
                    stop:1 {self.theme.primary_dark});
                border: none;
                border-radius: 16px 16px 0 0;
            }}
        """)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(28, 16, 28, 16)
        header_layout.setSpacing(4)

        # Team name
        self.team_name_label = QLabel("チームを選択")
        self.team_name_label.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: white;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(self.team_name_label)

        # League label
        self.league_label = QLabel("")
        self.league_label.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2px;
            color: rgba(255, 255, 255, 0.8);
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(self.league_label)

        layout.addWidget(header)

        # === Content Area ===
        content = QWidget()
        content.setStyleSheet("background: transparent; border: none;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(20)

        # Placeholder message
        self.placeholder_container = QWidget()
        self.placeholder_container.setStyleSheet("background: transparent; border: none;")
        placeholder_layout = QVBoxLayout(self.placeholder_container)
        placeholder_layout.setContentsMargins(0, 40, 0, 40)

        placeholder_icon = QLabel("⚾")
        placeholder_icon.setStyleSheet("""
            font-size: 48px;
            background: transparent;
            border: none;
        """)
        placeholder_icon.setAlignment(Qt.AlignCenter)
        placeholder_layout.addWidget(placeholder_icon)

        self.placeholder_label = QLabel("左のリストからチームを選択してください")
        self.placeholder_label.setStyleSheet(f"""
            font-size: 14px;
            color: {self.theme.text_muted};
            background: transparent;
            border: none;
        """)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_layout.addWidget(self.placeholder_label)

        content_layout.addWidget(self.placeholder_container)

        # Stats grid (hidden initially)
        self.stats_widget = QWidget()
        self.stats_widget.setStyleSheet("background: transparent; border: none;")
        self.stats_widget.hide()
        stats_layout = QGridLayout(self.stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)

        # Create premium stat boxes
        self.stat_boxes = {}
        stats_config = [
            ("players", "選手数", 0, 0),
            ("pitchers", "投手", 0, 1),
            ("batters", "野手", 1, 0),
            ("avg_overall", "平均OVR", 1, 1),
            ("top_player", "看板選手", 2, 0),
            ("avg_age", "平均年齢", 2, 1),
        ]

        for key, label, row, col in stats_config:
            stat_box = PremiumStatBox(label)
            self.stat_boxes[key] = stat_box
            stats_layout.addWidget(stat_box, row, col)

        content_layout.addWidget(self.stats_widget)

        # === Top Players Section ===
        self.players_section = QWidget()
        self.players_section.setStyleSheet("background: transparent; border: none;")
        self.players_section.hide()
        players_layout = QVBoxLayout(self.players_section)
        players_layout.setContentsMargins(0, 0, 0, 0)
        players_layout.setSpacing(12)

        # Section header
        players_header = QLabel("主要選手")
        players_header.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 700;
            color: {self.theme.text_muted};
            letter-spacing: 2px;
            text-transform: uppercase;
            background: transparent;
            border: none;
        """)
        players_layout.addWidget(players_header)

        # Players container
        self.players_container = QFrame()
        self.players_container.setStyleSheet(f"""
            QFrame {{
                background: {self.theme.bg_card};
                border: 1px solid {self.theme.border_muted};
                border-radius: 12px;
            }}
        """)
        self.players_list_layout = QVBoxLayout(self.players_container)
        self.players_list_layout.setContentsMargins(0, 8, 0, 8)
        self.players_list_layout.setSpacing(0)

        players_layout.addWidget(self.players_container)

        content_layout.addWidget(self.players_section)
        content_layout.addStretch()

        layout.addWidget(content, 1)

        # === Footer with confirm button ===
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: {self.theme.bg_card};
                border: none;
                border-top: 1px solid {self.theme.border_muted};
                border-radius: 0 0 16px 16px;
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 16, 24, 16)

        self.confirm_btn = QPushButton("このチームで開始")
        self.confirm_btn.setFixedHeight(52)
        self.confirm_btn.setCursor(Qt.PointingHandCursor)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.success_light}, stop:1 {self.theme.success});
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.success_hover}, stop:1 {self.theme.success_light});
            }}
            QPushButton:disabled {{
                background: {self.theme.bg_card_hover};
                color: {self.theme.text_muted};
            }}
        """)
        footer_layout.addWidget(self.confirm_btn)

        layout.addWidget(footer)

    def set_team(self, team, team_name: str, league: str):
        """Update panel with team information"""
        self._team = team
        self._team_name = team_name

        # Update header
        self.team_name_label.setText(team_name)

        league_text = "CENTRAL LEAGUE" if league == "central" else "PACIFIC LEAGUE"
        self.league_label.setText(league_text)

        # Update header gradient based on league
        league_color = self.theme.central_league if league == "central" else self.theme.pacific_league
        header = self.findChildren(QFrame)[0]
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {league_color}, stop:1 {self._darken_color(league_color)});
                border: none;
                border-radius: 16px 16px 0 0;
            }}
        """)

        # Hide placeholder, show content
        self.placeholder_container.hide()
        self.stats_widget.show()
        self.players_section.show()
        self.confirm_btn.setEnabled(True)

        if team:
            self._update_stats(team)
            self._update_top_players(team)
        else:
            self._show_placeholder_stats()

    def _darken_color(self, hex_color: str) -> str:
        color = QColor(hex_color)
        return color.darker(140).name()

    def _update_stats(self, team):
        """Update stats display"""
        players = team.players if hasattr(team, 'players') else []
        pitchers = [p for p in players if getattr(p, 'is_pitcher', False)]
        batters = [p for p in players if not getattr(p, 'is_pitcher', True)]

        # Update stat values
        self.stat_boxes["players"].set_value(str(len(players)), self.theme.primary_light)
        self.stat_boxes["pitchers"].set_value(str(len(pitchers)), self.theme.info_light)
        self.stat_boxes["batters"].set_value(str(len(batters)), self.theme.success_light)

        if players:
            avg_overall = sum(getattr(p, 'overall', 50) for p in players) / len(players)
            overall_color = self.theme.get_rating_color(int(avg_overall))
            self.stat_boxes["avg_overall"].set_value(f"{avg_overall:.1f}", overall_color)

            avg_age = sum(getattr(p, 'age', 25) for p in players) / len(players)
            self.stat_boxes["avg_age"].set_value(f"{avg_age:.1f}歳")

            top = max(players, key=lambda p: getattr(p, 'overall', 0))
            self.stat_boxes["top_player"].set_value(getattr(top, 'name', '---'), self.theme.gold)
        else:
            self.stat_boxes["avg_overall"].set_value("--")
            self.stat_boxes["avg_age"].set_value("--")
            self.stat_boxes["top_player"].set_value("--")

    def _update_top_players(self, team):
        """Update top players list"""
        # Clear existing
        while self.players_list_layout.count():
            child = self.players_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        players = team.players if hasattr(team, 'players') else []
        if not players:
            return

        # Get top 5 players
        sorted_players = sorted(players, key=lambda p: getattr(p, 'overall', 0), reverse=True)[:5]

        for i, player in enumerate(sorted_players):
            player_row = self._create_player_row(player, i == len(sorted_players) - 1)
            self.players_list_layout.addWidget(player_row)

    def _create_player_row(self, player, is_last: bool = False) -> QWidget:
        """Create a premium player row"""
        row = QWidget()
        row.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                border-bottom: {"none" if is_last else f"1px solid {self.theme.border_muted}"};
            }}
        """)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        # Position badge
        pos = getattr(player, 'position', 'P' if getattr(player, 'is_pitcher', False) else 'POS')
        pos_label = QLabel(pos)
        pos_label.setFixedWidth(36)
        pos_label.setAlignment(Qt.AlignCenter)
        pos_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {self.theme.text_muted};
            background: {self.theme.bg_card_elevated};
            border-radius: 4px;
            padding: 4px 6px;
        """)
        layout.addWidget(pos_label)

        # Name
        name = getattr(player, 'name', '---')
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 500;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        layout.addWidget(name_label)

        layout.addStretch()

        # Overall rating with color
        overall = getattr(player, 'overall', 0)
        overall_color = self.theme.get_rating_color(overall)
        rank = self.theme.get_rating_rank(overall)

        overall_label = QLabel(f"{rank} {overall}")
        overall_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {overall_color};
            background: transparent;
        """)
        layout.addWidget(overall_label)

        return row

    def _show_placeholder_stats(self):
        """Show placeholder when no team data"""
        for box in self.stat_boxes.values():
            box.set_value("--")

    def clear(self):
        """Reset panel to initial state"""
        self._team = None
        self._team_name = None
        self.team_name_label.setText("チームを選択")
        self.league_label.setText("")
        self.placeholder_container.show()
        self.stats_widget.hide()
        self.players_section.hide()
        self.confirm_btn.setEnabled(False)


class TeamSelectScreen(QWidget):
    """Ultra Premium Team Selection Screen"""

    team_selected = Signal(str)
    back_clicked = Signal()
    confirm_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._selected_team = None
        self._selected_team_name = None
        self._selected_league = None
        self._team_cards = []
        self._teams_data = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(48, 32, 48, 32)
        main_layout.setSpacing(0)

        # === Premium Header ===
        header = self._create_header()
        main_layout.addWidget(header)

        main_layout.addSpacing(24)

        # === Main Content: Left (team list) + Right (overview) ===
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(32)

        # Left panel: Team list in premium card
        left_panel = self._create_team_list_panel()
        content_layout.addWidget(left_panel, 5)

        # Right panel: Team overview
        self.overview_panel = TeamOverviewPanel()
        self.overview_panel.confirm_btn.clicked.connect(self._on_confirm)
        content_layout.addWidget(self.overview_panel, 6)

        main_layout.addWidget(content, 1)

    def _create_header(self) -> QWidget:
        """Create premium header with back button and title"""
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.bg_card},
                    stop:0.5 {self.theme.bg_card_elevated},
                    stop:1 {self.theme.bg_card});
                border: 1px solid {self.theme.border};
                border-radius: 16px;
            }}
        """)

        # Add shadow
        shadow = QGraphicsDropShadowEffect(header)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        header.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)

        # Left side: Back button and title
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)

        # Back button
        back_btn = QPushButton("← 戻る")
        back_btn.setFixedWidth(80)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {self.theme.text_muted};
                font-size: 12px;
                font-weight: 500;
                text-align: left;
                padding: 0;
            }}
            QPushButton:hover {{
                color: {self.theme.text_primary};
            }}
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        left_layout.addWidget(back_btn)

        # Title
        title = QLabel("チーム選択")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        left_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("管理するチームを選択してください")
        subtitle.setStyleSheet(f"""
            font-size: 13px;
            color: {self.theme.text_muted};
            background: transparent;
        """)
        left_layout.addWidget(subtitle)

        header_layout.addLayout(left_layout)
        header_layout.addStretch()

        # Right side: Decorative badge
        badge = QFrame()
        badge.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.primary}, stop:1 {self.theme.primary_dark});
                border-radius: 8px;
            }}
        """)
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(16, 8, 16, 8)

        badge_label = QLabel("⚾ NPB 12球団")
        badge_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: white;
            background: transparent;
        """)
        badge_layout.addWidget(badge_label)

        header_layout.addWidget(badge)

        return header

    def _create_team_list_panel(self) -> QFrame:
        """Create the premium team list panel"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.bg_card_elevated},
                    stop:0.5 {self.theme.bg_card},
                    stop:1 {self.theme.bg_card_elevated});
                border: 1px solid {self.theme.border};
                border-radius: 16px;
            }}
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Central League section
        central_section = self._create_league_section("CENTRAL LEAGUE", "central", [
            "Yomiuri Giants",
            "Hanshin Tigers",
            "Chunichi Dragons",
            "Hiroshima Toyo Carp",
            "Yokohama DeNA BayStars",
            "Tokyo Yakult Swallows"
        ])
        layout.addWidget(central_section)

        # Pacific League section
        pacific_section = self._create_league_section("PACIFIC LEAGUE", "pacific", [
            "Fukuoka SoftBank Hawks",
            "Saitama Seibu Lions",
            "Tohoku Rakuten Golden Eagles",
            "Chiba Lotte Marines",
            "Hokkaido Nippon-Ham Fighters",
            "Orix Buffaloes"
        ])
        layout.addWidget(pacific_section)

        layout.addStretch()

        return panel

    def _create_league_section(self, title: str, league: str, teams: list) -> QWidget:
        """Create a premium league section"""
        section = QWidget()
        section.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # League title with accent line
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 8)
        title_layout.setSpacing(12)

        league_color = self.theme.central_league if league == "central" else self.theme.pacific_league

        # Color accent
        accent = QFrame()
        accent.setFixedSize(4, 16)
        accent.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {league_color}, stop:1 {self._darken_color(league_color)});
            border-radius: 2px;
        """)
        title_layout.addWidget(accent)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {league_color};
            letter-spacing: 2px;
            background: transparent;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        layout.addWidget(title_container)

        # Team cards
        for team_name in teams:
            card = TeamCard(team_name, league)
            card.clicked.connect(lambda checked=False, t=team_name, c=card, l=league:
                                self._on_team_clicked(t, c, l))
            self._team_cards.append(card)
            layout.addWidget(card)

        return section

    def _darken_color(self, hex_color: str) -> str:
        color = QColor(hex_color)
        return color.darker(150).name()

    def _on_team_clicked(self, team_name: str, card: TeamCard, league: str):
        """Handle team card click"""
        # Deselect all cards
        for c in self._team_cards:
            c.set_selected(False)

        # Select clicked card
        card.set_selected(True)
        self._selected_team_name = team_name
        self._selected_league = league

        # Find team object
        team_obj = self._teams_data.get(team_name)
        self._selected_team = team_obj

        # Update overview panel
        self.overview_panel.set_team(team_obj, team_name, league)

        self.team_selected.emit(team_name)

    def _on_confirm(self):
        """Handle confirm button click"""
        if self._selected_team_name:
            print(f"  Confirm clicked for team: {self._selected_team_name}")
            self.confirm_clicked.emit(self._selected_team_name)

    def set_teams(self, central_teams: list, pacific_teams: list):
        """Set team data for overview display"""
        self._teams_data.clear()
        for team in central_teams:
            self._teams_data[team.name] = team
        for team in pacific_teams:
            self._teams_data[team.name] = team
        print(f"  TeamSelectScreen: Loaded {len(self._teams_data)} teams")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Premium dark gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(self.theme.bg_darkest))
        gradient.setColorAt(0.3, QColor(self.theme.bg_dark))
        gradient.setColorAt(0.7, QColor(self.theme.bg_dark))
        gradient.setColorAt(1.0, QColor(self.theme.bg_darkest))

        painter.fillRect(self.rect(), gradient)

        # Subtle radial highlight
        center_gradient = QRadialGradient(self.width() / 2, 0, self.width())
        center_gradient.setColorAt(0, QColor(self.theme.primary + "10"))
        center_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), center_gradient)
