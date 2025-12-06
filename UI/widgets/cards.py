# -*- coding: utf-8 -*-
"""
NPB Pennant Simulator - Premium Card Widgets
OOTP-Style Ultra Premium Information Cards
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QFont, QPen, QBrush

import sys
sys.path.insert(0, '..')
from UI.theme import get_theme, Theme


class Card(QFrame):
    """Ultra Premium Card Widget with hover effects and gradients"""

    clicked = Signal()

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._hover_progress = 0.0
        self._is_clickable = False

        self.setObjectName("Card")
        self._setup_style()
        self._setup_layout(title)
        self._setup_animation()
        self._add_shadow()

    def _setup_style(self):
        self.setStyleSheet(f"""
            #Card {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.bg_card_elevated},
                    stop:0.5 {self.theme.bg_card},
                    stop:1 {self.theme.bg_card_elevated});
                border: 1px solid {self.theme.border};
                border-radius: 12px;
            }}
            #Card:hover {{
                border-color: {self.theme.primary};
            }}
        """)

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

    def _setup_layout(self, title: str):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(16)

        if title:
            # Premium header with gradient accent
            header = QFrame()
            header.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.theme.primary}, stop:1 {self.theme.primary_light});
                    border-radius: 8px;
                    border: none;
                }}
            """)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(14, 10, 14, 10)

            self.title_label = QLabel(title)
            self.title_label.setStyleSheet(f"""
                font-size: 15px;
                font-weight: 700;
                color: white;
                background: transparent;
                border: none;
            """)
            header_layout.addWidget(self.title_label)
            header_layout.addStretch()

            self.main_layout.addWidget(header)

    def _setup_animation(self):
        self._animation = QPropertyAnimation(self, b"hover_progress")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def get_hover_progress(self):
        return self._hover_progress

    def set_hover_progress(self, value):
        self._hover_progress = value
        self._update_hover_style()

    hover_progress = Property(float, get_hover_progress, set_hover_progress)

    def _update_hover_style(self):
        progress = self._hover_progress
        if progress > 0:
            self.setStyleSheet(f"""
                #Card {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {self.theme.bg_card_hover},
                        stop:0.5 {self.theme.bg_card_elevated},
                        stop:1 {self.theme.bg_card_hover});
                    border: 1px solid {self.theme.primary};
                    border-radius: 12px;
                }}
            """)
        else:
            self._setup_style()

    def set_clickable(self, clickable: bool):
        self._is_clickable = clickable
        if clickable:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def enterEvent(self, event):
        if self._is_clickable:
            self._animation.stop()
            self._animation.setStartValue(self._hover_progress)
            self._animation.setEndValue(1.0)
            self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._is_clickable:
            self._animation.stop()
            self._animation.setStartValue(self._hover_progress)
            self._animation.setEndValue(0.0)
            self._animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._is_clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def add_widget(self, widget: QWidget):
        """Add a widget to the card's content area"""
        self.main_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the card's content area"""
        self.main_layout.addLayout(layout)


class PremiumStatCard(Card):
    """Ultra Premium Card for displaying a single statistic"""

    def __init__(self, title: str, value: str, subtitle: str = "",
                 icon: str = None, color: str = None, parent=None):
        super().__init__(parent=parent)
        self.theme = get_theme()
        self._stat_color = color or self.theme.primary

        # Remove default layout
        while self.main_layout.count():
            self.main_layout.takeAt(0)

        # Create premium content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Icon with glow effect (optional)
        if icon:
            icon_frame = QFrame()
            icon_frame.setFixedSize(60, 60)
            icon_frame.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {self._stat_color}, stop:1 {self._stat_color}cc);
                    border-radius: 16px;
                }}
            """)
            icon_layout = QVBoxLayout(icon_frame)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet(f"""
                font-size: 28px;
                color: white;
                background: transparent;
            """)
            icon_layout.addWidget(icon_label)
            content_layout.addWidget(icon_frame)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {self.theme.text_secondary};
            text-transform: uppercase;
            letter-spacing: 1.5px;
        """)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 800;
            color: {self._stat_color};
        """)

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"""
                font-size: 13px;
                color: {self.theme.text_muted};
            """)
            text_layout.addWidget(subtitle_label)

        content_layout.addLayout(text_layout)
        content_layout.addStretch()

        self.main_layout.addLayout(content_layout)

        # Store for updates
        self._value_label = value_label
        self._subtitle_label = subtitle_label if subtitle else None

    def set_value(self, value: str):
        self._value_label.setText(value)

    def set_subtitle(self, subtitle: str):
        if self._subtitle_label:
            self._subtitle_label.setText(subtitle)


# Alias for backwards compatibility
StatCard = PremiumStatCard


class PremiumCard(QFrame):
    """Premium styled card with gradient header and shadow - Unified component"""

    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.title_text = title
        self.icon = icon

        self._setup_ui()

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

        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 16)
        self.main_layout.setSpacing(0)

        # Header with gradient accent
        self.header = QFrame()
        self.header.setFixedHeight(48)
        self.header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.primary},
                    stop:1 {self.theme.accent});
                border: none;
                border-radius: 16px 16px 0 0;
            }}
        """)

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.title_label = QLabel(f"{self.icon}  {self.title_text}" if self.icon else self.title_text)
        self.title_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 700;
            color: white;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Header actions area
        self.header_actions_layout = QHBoxLayout()
        self.header_actions_layout.setSpacing(8)
        header_layout.addLayout(self.header_actions_layout)

        self.main_layout.addWidget(self.header)

        # Content area
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent; border: none;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 16, 16, 0)
        self.content_layout.setSpacing(12)

        self.main_layout.addWidget(self.content_widget)

    def set_title(self, title: str):
        self.title_text = title
        self.title_label.setText(f"{self.icon}  {title}" if self.icon else title)

    def add_header_widget(self, widget):
        """Add a widget to the header actions area"""
        self.header_actions_layout.addWidget(widget)

    def add_widget(self, widget):
        """Add a widget to the content area"""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the content area"""
        self.content_layout.addLayout(layout)

    def add_stretch(self):
        """Add stretch to content area"""
        self.content_layout.addStretch()


class PlayerCard(Card):
    """Premium Card for displaying player information (OOTP Style)"""

    def __init__(self, player=None, show_stats: bool = True, parent=None):
        super().__init__(parent=parent)
        self.theme = get_theme()
        self.player = player
        self.set_clickable(True)

        # Clear default layout
        while self.main_layout.count():
            self.main_layout.takeAt(0)

        self._create_layout(show_stats)

        if player:
            self.set_player(player)

    def _create_layout(self, show_stats: bool):
        # Header: Name and Position with premium styling
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # Player number badge with gradient
        self.number_label = QLabel("00")
        self.number_label.setFixedSize(50, 50)
        self.number_label.setAlignment(Qt.AlignCenter)
        self.number_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self.theme.primary_light}, stop:1 {self.theme.primary});
            color: white;
            font-size: 18px;
            font-weight: 700;
            border-radius: 12px;
        """)
        header_layout.addWidget(self.number_label)

        # Name and position
        name_layout = QVBoxLayout()
        name_layout.setSpacing(4)

        self.name_label = QLabel("選手名")
        self.name_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {self.theme.text_primary};
        """)

        self.position_label = QLabel("ポジション")
        self.position_label.setStyleSheet(f"""
            font-size: 12px;
            color: {self.theme.text_secondary};
            font-weight: 500;
        """)

        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.position_label)
        header_layout.addLayout(name_layout)
        header_layout.addStretch()

        # Overall rating with gradient background
        self.overall_label = QLabel("--")
        self.overall_label.setAlignment(Qt.AlignCenter)
        self.overall_label.setFixedSize(60, 60)
        self.overall_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self.theme.bg_card_elevated}, stop:1 {self.theme.bg_input});
            color: {self.theme.text_primary};
            font-size: 24px;
            font-weight: 800;
            border-radius: 16px;
            border: 2px solid {self.theme.border};
        """)
        header_layout.addWidget(self.overall_label)

        self.main_layout.addLayout(header_layout)

        if show_stats:
            # Gradient separator
            separator = QFrame()
            separator.setFixedHeight(2)
            separator.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent, stop:0.2 {self.theme.primary},
                    stop:0.8 {self.theme.primary}, stop:1 transparent);
            """)
            self.main_layout.addWidget(separator)

            # Stats grid with premium styling
            self.stats_layout = QHBoxLayout()
            self.stats_layout.setSpacing(20)
            self.stat_labels = {}

            self.main_layout.addLayout(self.stats_layout)

    def set_player(self, player):
        """Update card with player data"""
        self.player = player
        if not player:
            return

        # Basic info
        self.number_label.setText(str(player.uniform_number))
        self.name_label.setText(player.name)

        # Position
        pos_text = player.position.value
        if hasattr(player, 'pitch_type') and player.pitch_type:
            pos_text += f" ({player.pitch_type.value})"
        self.position_label.setText(pos_text)

        # Overall rating with color based on value
        overall = player.overall_rating if hasattr(player, 'overall_rating') else 0
        self.overall_label.setText(str(overall))

        # Color based on rating
        rating_color = self._get_rating_color(overall)
        self.overall_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {rating_color}, stop:1 {rating_color}cc);
            color: white;
            font-size: 24px;
            font-weight: 800;
            border-radius: 16px;
            border: none;
        """)

        # Update stats
        self._update_stats(player)

    def _update_stats(self, player):
        # Clear existing stats
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        stats = player.stats
        if player.position.value == "投手":
            stat_names = [
                ("球速", stats.speed),
                ("制球", stats.control),
                ("スタ", stats.stamina),
                ("変化", stats.breaking),
            ]
        else:
            stat_names = [
                ("ミート", stats.contact),
                ("パワー", stats.power),
                ("走力", stats.run),
                ("守備", stats.fielding),
            ]

        for name, value in stat_names:
            stat_widget = self._create_stat_widget(name, value)
            self.stats_layout.addWidget(stat_widget)

    def _create_stat_widget(self, name: str, value: int) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Stat name
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {self.theme.text_muted};
            text-transform: uppercase;
        """)

        # Stat value with rank and gradient
        rank = Theme.get_rating_rank(value)
        color = Theme.get_rating_color(value)

        value_frame = QFrame()
        value_frame.setFixedSize(40, 28)
        value_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {color}cc);
                border-radius: 6px;
            }}
        """)
        value_layout = QVBoxLayout(value_frame)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_label = QLabel(rank)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: white;
            background: transparent;
        """)
        value_layout.addWidget(value_label)

        layout.addWidget(name_label)
        layout.addWidget(value_frame, alignment=Qt.AlignCenter)

        return widget

    def _get_rating_color(self, value: int) -> str:
        if value >= 400:
            return self.theme.rating_s
        elif value >= 350:
            return self.theme.rating_a
        elif value >= 300:
            return self.theme.rating_b
        elif value >= 250:
            return self.theme.rating_c
        elif value >= 200:
            return self.theme.rating_d
        else:
            return self.theme.rating_e


class TeamCard(Card):
    """Premium Card for displaying team information"""

    def __init__(self, team=None, parent=None):
        super().__init__(parent=parent)
        self.theme = get_theme()
        self.team = team
        self.set_clickable(True)

        # Clear and rebuild layout
        while self.main_layout.count():
            self.main_layout.takeAt(0)

        self._create_layout()

        if team:
            self.set_team(team)

    def _create_layout(self):
        # Team header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # Team logo placeholder with gradient
        self.logo_label = QLabel("🏟️")
        self.logo_label.setFixedSize(70, 70)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet(f"""
            font-size: 36px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self.theme.bg_card_elevated}, stop:1 {self.theme.bg_input});
            border-radius: 16px;
            border: 2px solid {self.theme.border};
        """)
        header_layout.addWidget(self.logo_label)

        # Team info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        self.team_name_label = QLabel("チーム名")
        self.team_name_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {self.theme.text_primary};
        """)

        self.league_label = QLabel("リーグ")
        self.league_label.setStyleSheet(f"""
            font-size: 13px;
            color: {self.theme.text_secondary};
            font-weight: 500;
        """)

        info_layout.addWidget(self.team_name_label)
        info_layout.addWidget(self.league_label)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()

        self.main_layout.addLayout(header_layout)

        # Gradient separator
        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.2 {self.theme.primary},
                stop:0.8 {self.theme.primary}, stop:1 transparent);
        """)
        self.main_layout.addWidget(separator)

        # Record with premium styling
        record_layout = QHBoxLayout()
        record_layout.setSpacing(32)

        self.wins_label = self._create_record_widget("勝", "0", self.theme.success)
        self.losses_label = self._create_record_widget("敗", "0", self.theme.danger)
        self.draws_label = self._create_record_widget("分", "0", self.theme.text_secondary)
        self.pct_label = self._create_record_widget("勝率", ".000", self.theme.accent_gold)

        record_layout.addWidget(self.wins_label)
        record_layout.addWidget(self.losses_label)
        record_layout.addWidget(self.draws_label)
        record_layout.addWidget(self.pct_label)
        record_layout.addStretch()

        self.main_layout.addLayout(record_layout)

    def _create_record_widget(self, label: str, value: str, color: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {self.theme.text_muted};
            text-transform: uppercase;
        """)

        value_widget = QLabel(value)
        value_widget.setObjectName("value")
        value_widget.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {color};
        """)

        layout.addWidget(label_widget, alignment=Qt.AlignCenter)
        layout.addWidget(value_widget, alignment=Qt.AlignCenter)

        return widget

    def set_team(self, team):
        """Update card with team data"""
        self.team = team
        if not team:
            return

        self.team_name_label.setText(team.name)
        self.league_label.setText(team.league.value)

        # Update record
        self.wins_label.findChild(QLabel, "value").setText(str(team.wins))
        self.losses_label.findChild(QLabel, "value").setText(str(team.losses))
        self.draws_label.findChild(QLabel, "value").setText(str(team.draws))

        pct = team.winning_percentage
        self.pct_label.findChild(QLabel, "value").setText(f".{int(pct * 1000):03d}")


class StandingsCard(Card):
    """Premium Card for displaying league standings"""

    def __init__(self, title: str = "順位表", parent=None):
        super().__init__(title=title, parent=parent)
        self.theme = get_theme()
        self._create_standings_layout()

    def _create_standings_layout(self):
        # Header row with premium styling
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.theme.bg_card_elevated};
                border-radius: 8px;
                margin-bottom: 8px;
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 10, 12, 10)
        headers = ["順", "チーム", "勝", "敗", "分", "勝率", "差"]
        widths = [35, 130, 45, 45, 45, 65, 55]

        for header, width in zip(headers, widths):
            label = QLabel(header)
            label.setFixedWidth(width)
            label.setStyleSheet(f"""
                font-size: 11px;
                font-weight: 700;
                color: {self.theme.text_secondary};
                text-transform: uppercase;
                letter-spacing: 1px;
            """)
            header_layout.addWidget(label)

        self.main_layout.addWidget(header_frame)

        # Team rows container
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(4)
        self.main_layout.addLayout(self.rows_layout)

    def set_standings(self, teams: list):
        """Update standings with team list (already sorted)"""
        # Clear existing rows
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        top_pct = teams[0].winning_percentage if teams else 0

        for i, team in enumerate(teams):
            row = self._create_team_row(i + 1, team, top_pct)
            self.rows_layout.addWidget(row)

    def _create_team_row(self, rank: int, team, top_pct: float) -> QWidget:
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-radius: 8px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.bg_card_hover}, stop:1 transparent);
            }}
        """)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(0)

        widths = [35, 130, 45, 45, 45, 65, 55]

        # Rank with medal colors
        rank_label = QLabel(str(rank))
        rank_label.setFixedWidth(widths[0])
        if rank == 1:
            rank_color = self.theme.gold
        elif rank == 2:
            rank_color = self.theme.silver
        elif rank == 3:
            rank_color = self.theme.bronze
        else:
            rank_color = self.theme.text_secondary
        rank_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 800;
            color: {rank_color};
        """)
        layout.addWidget(rank_label)

        # Team name
        name_label = QLabel(team.name)
        name_label.setFixedWidth(widths[1])
        name_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {self.theme.text_primary};
        """)
        layout.addWidget(name_label)

        # Wins
        wins_label = QLabel(str(team.wins))
        wins_label.setFixedWidth(widths[2])
        wins_label.setStyleSheet(f"""
            color: {self.theme.success_light};
            font-weight: 600;
        """)
        layout.addWidget(wins_label)

        # Losses
        losses_label = QLabel(str(team.losses))
        losses_label.setFixedWidth(widths[3])
        losses_label.setStyleSheet(f"""
            color: {self.theme.danger_light};
            font-weight: 600;
        """)
        layout.addWidget(losses_label)

        # Draws
        draws_label = QLabel(str(team.draws))
        draws_label.setFixedWidth(widths[4])
        draws_label.setStyleSheet(f"color: {self.theme.text_secondary};")
        layout.addWidget(draws_label)

        # Win %
        pct = team.winning_percentage
        pct_label = QLabel(f".{int(pct * 1000):03d}")
        pct_label.setFixedWidth(widths[5])
        pct_label.setStyleSheet(f"""
            color: {self.theme.accent_gold};
            font-weight: 700;
        """)
        layout.addWidget(pct_label)

        # Games back
        if rank == 1:
            gb = "-"
        else:
            gb_value = (top_pct - pct) * (team.wins + team.losses) / 2
            gb = f"{gb_value:.1f}"
        gb_label = QLabel(gb)
        gb_label.setFixedWidth(widths[6])
        gb_label.setStyleSheet(f"color: {self.theme.text_muted};")
        layout.addWidget(gb_label)

        return row
