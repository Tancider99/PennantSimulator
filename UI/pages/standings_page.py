# -*- coding: utf-8 -*-
"""
NPB Pennant Simulator - Standings Page
OOTP-Style Premium League Standings Display
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme


class PremiumCard(QFrame):
    """Premium styled card with gradient background and shadow"""

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
        header = QFrame()
        header.setFixedHeight(48)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.primary},
                    stop:1 {self.theme.accent});
                border: none;
                border-radius: 16px 16px 0 0;
            }}
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title_label = QLabel(f"{self.icon}  {self.title_text}" if self.icon else self.title_text)
        title_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 700;
            color: white;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.main_layout.addWidget(header)

        # Content area
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent; border: none;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 16, 16, 0)
        self.content_layout.setSpacing(12)

        self.main_layout.addWidget(self.content_widget)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)


class StandingsPage(QWidget):
    """Premium styled league standings page"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.game_state = None

        self._setup_ui()

    def _setup_ui(self):
        """Create the standings page layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # Premium page header
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.bg_card},
                    stop:0.5 {self.theme.bg_card_elevated},
                    stop:1 {self.theme.bg_card});
                border: 1px solid {self.theme.border};
                border-radius: 16px;
            }}
        """)

        header_shadow = QGraphicsDropShadowEffect(header_frame)
        header_shadow.setBlurRadius(15)
        header_shadow.setOffset(0, 3)
        header_shadow.setColor(QColor(0, 0, 0, 60))
        header_frame.setGraphicsEffect(header_shadow)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 0, 24, 0)

        # Title with icon
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("🏆  リーグ順位表")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        title_layout.addWidget(title)

        subtitle = QLabel("League Standings")
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {self.theme.text_muted};
            background: transparent;
        """)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Season info badge
        season_badge = QFrame()
        season_badge.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.primary},
                    stop:1 {self.theme.accent});
                border-radius: 8px;
                padding: 8px 16px;
            }}
        """)
        badge_layout = QHBoxLayout(season_badge)
        badge_layout.setContentsMargins(12, 6, 12, 6)

        season_label = QLabel("2024シーズン")
        season_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: white;
            background: transparent;
        """)
        badge_layout.addWidget(season_label)
        header_layout.addWidget(season_badge)

        main_layout.addWidget(header_frame)

        # League tabs with premium styling
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: transparent;
            }}
            QTabBar::tab {{
                background: {self.theme.bg_card};
                color: {self.theme.text_secondary};
                border: 1px solid {self.theme.border};
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 12px 24px;
                margin-right: 4px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.primary},
                    stop:1 {self.theme.accent});
                color: white;
                border-color: {self.theme.primary};
            }}
            QTabBar::tab:hover:!selected {{
                background: {self.theme.bg_card_elevated};
                color: {self.theme.text_primary};
            }}
        """)

        # Central League
        self.central_table = self._create_standings_table()
        central_card = PremiumCard("セントラル・リーグ", "⚾")
        central_card.add_widget(self.central_table)
        self.tabs.addTab(central_card, "セ・リーグ")

        # Pacific League
        self.pacific_table = self._create_standings_table()
        pacific_card = PremiumCard("パシフィック・リーグ", "⚾")
        pacific_card.add_widget(self.pacific_table)
        self.tabs.addTab(pacific_card, "パ・リーグ")

        main_layout.addWidget(self.tabs)

        # Additional stats section
        self._create_additional_stats(main_layout)

    def _create_standings_table(self) -> QTableWidget:
        """Create a premium styled standings table"""
        table = QTableWidget()
        table.setRowCount(6)

        headers = [
            "順位", "チーム", "勝", "敗", "分", "勝率",
            "差", "残", "直近10", "ホーム", "ビジター"
        ]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {self.theme.text_primary};
                border-bottom: 1px solid {self.theme.border_muted};
            }}
            QTableWidget::item:selected {{
                background-color: {self.theme.primary};
                color: white;
            }}
            QTableWidget::item:hover {{
                background-color: {self.theme.bg_hover};
            }}
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.bg_card_elevated},
                    stop:1 {self.theme.bg_card});
                color: {self.theme.text_secondary};
                font-weight: 600;
                font-size: 11px;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid {self.theme.primary};
            }}
        """)

        # Column widths
        widths = [50, 150, 50, 50, 50, 70, 60, 50, 80, 80, 80]
        header = table.horizontalHeader()
        for i, width in enumerate(widths):
            header.resizeSection(i, width)
        header.setStretchLastSection(True)

        # Row height
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(44)

        # Selection
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)

        return table

    def _create_additional_stats(self, parent_layout):
        """Create additional statistics section"""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # Team batting leaders
        batting_card = PremiumCard("チーム打撃成績", "🏏")
        self.batting_table = self._create_team_stats_table("batting")
        batting_card.add_widget(self.batting_table)
        stats_layout.addWidget(batting_card)

        # Team pitching leaders
        pitching_card = PremiumCard("チーム投手成績", "⚾")
        self.pitching_table = self._create_team_stats_table("pitching")
        pitching_card.add_widget(self.pitching_table)
        stats_layout.addWidget(pitching_card)

        parent_layout.addLayout(stats_layout)

    def _create_team_stats_table(self, stat_type: str) -> QTableWidget:
        """Create team stats comparison table"""
        table = QTableWidget()
        table.setRowCount(12)

        if stat_type == "batting":
            headers = ["チーム", "打率", "HR", "打点", "得点", "盗塁"]
        else:
            headers = ["チーム", "防御率", "勝", "S", "奪三振", "失点"]

        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: 6px;
                color: {self.theme.text_primary};
                border-bottom: 1px solid {self.theme.border_muted};
            }}
            QTableWidget::item:selected {{
                background-color: {self.theme.primary};
                color: white;
            }}
            QTableWidget::item:hover {{
                background-color: {self.theme.bg_hover};
            }}
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.bg_card_elevated},
                    stop:1 {self.theme.bg_card});
                color: {self.theme.text_secondary};
                font-weight: 600;
                font-size: 11px;
                padding: 8px 6px;
                border: none;
                border-bottom: 2px solid {self.theme.primary};
            }}
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(32)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setShowGrid(False)

        return table

    def set_game_state(self, game_state):
        """Update with game state"""
        self.game_state = game_state
        if not game_state:
            return

        self._update_standings()

    def _update_standings(self):
        """Update standings tables"""
        if not self.game_state:
            return

        # Separate by league
        central_teams = []
        pacific_teams = []

        for team in self.game_state.teams:
            if team.league.value == "セントラル":
                central_teams.append(team)
            else:
                pacific_teams.append(team)

        # Sort by winning percentage
        central_teams.sort(key=lambda t: t.winning_percentage, reverse=True)
        pacific_teams.sort(key=lambda t: t.winning_percentage, reverse=True)

        # Update tables
        self._fill_standings_table(self.central_table, central_teams)
        self._fill_standings_table(self.pacific_table, pacific_teams)

        # Update team stats
        self._update_team_stats()

    def _fill_standings_table(self, table: QTableWidget, teams: list):
        """Fill a standings table with team data"""
        if not teams:
            return

        top_pct = teams[0].winning_percentage
        total_games = 143  # Standard NPB season

        for row, team in enumerate(teams):
            # Rank with medal colors for top 3
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            if row == 0:
                rank_item.setForeground(QBrush(QColor(self.theme.gold)))
                rank_item.setText("🥇")
            elif row == 1:
                rank_item.setForeground(QBrush(QColor("#C0C0C0")))
                rank_item.setText("🥈")
            elif row == 2:
                rank_item.setForeground(QBrush(QColor("#CD7F32")))
                rank_item.setText("🥉")
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            rank_item.setFont(font)
            table.setItem(row, 0, rank_item)

            # Team name
            name_item = QTableWidgetItem(team.name)
            name_item.setFont(QFont("", -1, QFont.Bold))
            if row < 3:
                name_item.setForeground(QBrush(QColor(self.theme.gold)))
            table.setItem(row, 1, name_item)

            # Wins
            wins_item = QTableWidgetItem(str(team.wins))
            wins_item.setTextAlignment(Qt.AlignCenter)
            wins_item.setForeground(QBrush(QColor(self.theme.success)))
            table.setItem(row, 2, wins_item)

            # Losses
            losses_item = QTableWidgetItem(str(team.losses))
            losses_item.setTextAlignment(Qt.AlignCenter)
            losses_item.setForeground(QBrush(QColor(self.theme.danger)))
            table.setItem(row, 3, losses_item)

            # Draws
            draws_item = QTableWidgetItem(str(team.draws))
            draws_item.setTextAlignment(Qt.AlignCenter)
            draws_item.setForeground(QBrush(QColor(self.theme.text_muted)))
            table.setItem(row, 4, draws_item)

            # Win %
            pct = team.winning_percentage
            pct_item = QTableWidgetItem(f".{int(pct * 1000):03d}")
            pct_item.setTextAlignment(Qt.AlignCenter)
            pct_item.setFont(QFont("", -1, QFont.Bold))
            pct_item.setForeground(QBrush(QColor(self.theme.accent)))
            table.setItem(row, 5, pct_item)

            # Games back
            if row == 0:
                gb_text = "-"
            else:
                gb = (top_pct - pct) * team.games_played / 2
                gb_text = f"{gb:.1f}"
            gb_item = QTableWidgetItem(gb_text)
            gb_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 6, gb_item)

            # Remaining games
            remaining = total_games - team.games_played
            remain_item = QTableWidgetItem(str(remaining))
            remain_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 7, remain_item)

            # Last 10 (placeholder)
            last10_item = QTableWidgetItem("---")
            last10_item.setTextAlignment(Qt.AlignCenter)
            last10_item.setForeground(QBrush(QColor(self.theme.text_muted)))
            table.setItem(row, 8, last10_item)

            # Home record (placeholder)
            home_item = QTableWidgetItem("---")
            home_item.setTextAlignment(Qt.AlignCenter)
            home_item.setForeground(QBrush(QColor(self.theme.text_muted)))
            table.setItem(row, 9, home_item)

            # Away record (placeholder)
            away_item = QTableWidgetItem("---")
            away_item.setTextAlignment(Qt.AlignCenter)
            away_item.setForeground(QBrush(QColor(self.theme.text_muted)))
            table.setItem(row, 10, away_item)

    def _update_team_stats(self):
        """Update team statistics tables"""
        if not self.game_state:
            return

        teams = self.game_state.teams

        # Calculate team batting stats
        batting_stats = []
        for team in teams:
            batters = [p for p in team.players if p.position.value != "投手"]
            total_ab = sum(p.record.at_bats for p in batters)
            total_hits = sum(p.record.hits for p in batters)
            total_hr = sum(p.record.home_runs for p in batters)
            total_rbi = sum(p.record.rbis for p in batters)
            total_runs = sum(p.record.runs for p in batters)
            total_sb = sum(p.record.stolen_bases for p in batters)

            avg = total_hits / total_ab if total_ab > 0 else 0
            batting_stats.append((team.name, avg, total_hr, total_rbi, total_runs, total_sb))

        # Sort by batting average
        batting_stats.sort(key=lambda x: x[1], reverse=True)

        # Fill batting table
        for row, (name, avg, hr, rbi, runs, sb) in enumerate(batting_stats):
            name_item = QTableWidgetItem(name)
            if row < 3:
                name_item.setForeground(QBrush(QColor(self.theme.gold)))
                name_item.setFont(QFont("", -1, QFont.Bold))
            self.batting_table.setItem(row, 0, name_item)

            avg_item = QTableWidgetItem(f".{int(avg * 1000):03d}")
            avg_item.setTextAlignment(Qt.AlignCenter)
            avg_item.setForeground(QBrush(QColor(self.theme.accent)))
            self.batting_table.setItem(row, 1, avg_item)

            hr_item = QTableWidgetItem(str(hr))
            hr_item.setTextAlignment(Qt.AlignCenter)
            self.batting_table.setItem(row, 2, hr_item)

            rbi_item = QTableWidgetItem(str(rbi))
            rbi_item.setTextAlignment(Qt.AlignCenter)
            self.batting_table.setItem(row, 3, rbi_item)

            runs_item = QTableWidgetItem(str(runs))
            runs_item.setTextAlignment(Qt.AlignCenter)
            self.batting_table.setItem(row, 4, runs_item)

            sb_item = QTableWidgetItem(str(sb))
            sb_item.setTextAlignment(Qt.AlignCenter)
            self.batting_table.setItem(row, 5, sb_item)

        # Calculate team pitching stats
        pitching_stats = []
        for team in teams:
            pitchers = [p for p in team.players if p.position.value == "投手"]
            total_ip = sum(p.record.innings_pitched for p in pitchers)
            total_er = sum(p.record.earned_runs for p in pitchers)
            total_wins = sum(p.record.wins for p in pitchers)
            total_saves = sum(p.record.saves for p in pitchers)
            total_so = sum(p.record.strikeouts_pitched for p in pitchers)
            total_runs = sum(p.record.runs_allowed for p in pitchers)

            era = (total_er * 9 / total_ip) if total_ip > 0 else 0
            pitching_stats.append((team.name, era, total_wins, total_saves, total_so, total_runs))

        # Sort by ERA
        pitching_stats.sort(key=lambda x: x[1])

        # Fill pitching table
        for row, (name, era, wins, saves, so, runs) in enumerate(pitching_stats):
            name_item = QTableWidgetItem(name)
            if row < 3:
                name_item.setForeground(QBrush(QColor(self.theme.gold)))
                name_item.setFont(QFont("", -1, QFont.Bold))
            self.pitching_table.setItem(row, 0, name_item)

            era_item = QTableWidgetItem(f"{era:.2f}")
            era_item.setTextAlignment(Qt.AlignCenter)
            era_item.setForeground(QBrush(QColor(self.theme.accent)))
            self.pitching_table.setItem(row, 1, era_item)

            wins_item = QTableWidgetItem(str(wins))
            wins_item.setTextAlignment(Qt.AlignCenter)
            self.pitching_table.setItem(row, 2, wins_item)

            saves_item = QTableWidgetItem(str(saves))
            saves_item.setTextAlignment(Qt.AlignCenter)
            self.pitching_table.setItem(row, 3, saves_item)

            so_item = QTableWidgetItem(str(so))
            so_item.setTextAlignment(Qt.AlignCenter)
            self.pitching_table.setItem(row, 4, so_item)

            runs_item = QTableWidgetItem(str(runs))
            runs_item.setTextAlignment(Qt.AlignCenter)
            self.pitching_table.setItem(row, 5, runs_item)
