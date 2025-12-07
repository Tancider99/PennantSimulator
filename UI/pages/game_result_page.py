# -*- coding: utf-8 -*-
"""
Baseball Team Architect 2027 - Game Result Page
Official Style Game Result Screen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme
from UI.widgets.panels import ContentPanel
from UI.widgets.cards import Card

class ScoreboardTable(QTableWidget):
    """Line Score Table Widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_ui()

    def _setup_ui(self):
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(True)
        self.setShowGrid(True)
        self.setAlternatingRowColors(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Style
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.theme.bg_card};
                gridline-color: {self.theme.border_light};
                border: 1px solid {self.theme.border};
                color: {self.theme.text_primary};
                font-family: "Consolas", monospace;
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {self.theme.bg_card_elevated};
                color: {self.theme.text_muted};
                border: none;
                border-bottom: 1px solid {self.theme.border};
                border-right: 1px solid {self.theme.border_light};
                padding: 4px;
                font-size: 11px;
                font-weight: 700;
            }}
            QTableWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {self.theme.border_light};
            }}
        """)

class GameResultPage(ContentPanel):
    """Detailed Game Result Screen"""
    
    return_home_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        # 1. Header (Date & Stadium)
        header_layout = QHBoxLayout()
        self.date_label = QLabel("2027年4月1日")
        self.date_label.setStyleSheet(f"font-size: 14px; color: {self.theme.text_secondary}; font-weight: 600;")
        self.stadium_label = QLabel("スカイドーム")
        self.stadium_label.setStyleSheet(f"font-size: 14px; color: {self.theme.text_muted}; margin-left: 16px;")
        
        header_layout.addWidget(self.date_label)
        header_layout.addWidget(self.stadium_label)
        header_layout.addStretch()
        
        # Return Button
        self.return_btn = QPushButton("トップへ戻る")
        self.return_btn.setCursor(Qt.PointingHandCursor)
        self.return_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.primary};
                color: white;
                font-weight: 700;
                padding: 10px 24px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.primary_light};
            }}
        """)
        self.return_btn.clicked.connect(lambda: self.return_home_requested.emit())
        header_layout.addWidget(self.return_btn)
        
        layout.addLayout(header_layout)

        # 2. Main Score Section (Big Score)
        score_card = QFrame()
        score_card.setStyleSheet(f"""
            QFrame {{
                background: {self.theme.bg_card};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
            }}
        """)
        score_layout = QHBoxLayout(score_card)
        score_layout.setContentsMargins(32, 24, 32, 24)
        score_layout.setSpacing(40)

        # Away Team
        self.away_team_name = QLabel("AWAY")
        self.away_team_name.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {self.theme.text_primary};")
        self.away_score = QLabel("0")
        self.away_score.setStyleSheet(f"font-size: 64px; font-weight: 800; color: {self.theme.text_primary};")
        
        away_container = QVBoxLayout()
        away_container.setAlignment(Qt.AlignCenter)
        away_container.addWidget(self.away_team_name, 0, Qt.AlignCenter)
        away_container.addWidget(self.away_score, 0, Qt.AlignCenter)
        score_layout.addLayout(away_container)

        # VS / Result
        result_info = QVBoxLayout()
        self.win_lose_label = QLabel("WIN")
        self.win_lose_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {self.theme.accent_blue};")
        result_info.addWidget(self.win_lose_label, 0, Qt.AlignCenter)
        score_layout.addLayout(result_info)

        # Home Team
        self.home_team_name = QLabel("HOME")
        self.home_team_name.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {self.theme.text_primary};")
        self.home_score = QLabel("0")
        self.home_score.setStyleSheet(f"font-size: 64px; font-weight: 800; color: {self.theme.text_primary};")
        
        home_container = QVBoxLayout()
        home_container.setAlignment(Qt.AlignCenter)
        home_container.addWidget(self.home_team_name, 0, Qt.AlignCenter)
        home_container.addWidget(self.home_score, 0, Qt.AlignCenter)
        score_layout.addLayout(home_container)

        layout.addWidget(score_card)

        # 3. Line Score Table
        self.line_score_table = ScoreboardTable()
        self.line_score_table.setFixedHeight(105) # Header + 2 rows
        layout.addWidget(self.line_score_table)

        # 4. Game Details Grid (Pitchers & Home Runs)
        details_grid = QGridLayout()
        details_grid.setSpacing(16)

        # Pitcher Stats Card
        pitcher_card = Card("投手成績")
        pitcher_content = QWidget()
        pitcher_layout = QGridLayout(pitcher_content)
        pitcher_layout.setContentsMargins(0, 0, 0, 0)
        pitcher_layout.setSpacing(12)

        labels = ["勝利投手", "敗戦投手", "セーブ"]
        self.pitcher_labels = {}
        for i, label in enumerate(labels):
            l = QLabel(label)
            l.setStyleSheet(f"font-size: 12px; color: {self.theme.text_muted}; font-weight: 600;")
            pitcher_layout.addWidget(l, i, 0)
            
            val = QLabel("-")
            val.setStyleSheet(f"font-size: 13px; color: {self.theme.text_primary}; font-weight: 600;")
            pitcher_layout.addWidget(val, i, 1)
            self.pitcher_labels[label] = val

        pitcher_card.add_widget(pitcher_content)
        details_grid.addWidget(pitcher_card, 0, 0)

        # Home Run Card
        hr_card = Card("本塁打")
        self.hr_content = QVBoxLayout()
        self.hr_content.setSpacing(4)
        hr_card.add_layout(self.hr_content)
        details_grid.addWidget(hr_card, 0, 1)

        # Battery Card
        battery_card = Card("バッテリー")
        self.battery_content = QVBoxLayout()
        battery_card.add_layout(self.battery_content)
        details_grid.addWidget(battery_card, 1, 0, 1, 2)

        layout.addLayout(details_grid)
        layout.addStretch()

    def set_result(self, result_data: dict):
        """Set game result data"""
        home_team = result_data.get('home_team')
        away_team = result_data.get('away_team')
        h_score = result_data.get('home_score', 0)
        a_score = result_data.get('away_score', 0)
        
        # Header
        self.away_team_name.setText(away_team.name)
        self.home_team_name.setText(home_team.name)
        self.away_score.setText(str(a_score))
        self.home_score.setText(str(h_score))

        if h_score > a_score:
            self.win_lose_label.setText(f"{home_team.name} WIN")
            self.win_lose_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {self.theme.success};")
        elif a_score > h_score:
            self.win_lose_label.setText(f"{away_team.name} WIN")
            self.win_lose_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {self.theme.success};")
        else:
            self.win_lose_label.setText("DRAW")
            self.win_lose_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {self.theme.text_muted};")

        # Line Score
        inning_h = result_data.get('inning_scores_home', [])
        inning_a = result_data.get('inning_scores_away', [])
        
        total_innings = max(len(inning_h), 9)
        self.line_score_table.setColumnCount(total_innings + 3) # + R, H, E
        self.line_score_table.setRowCount(2)
        
        headers = [str(i+1) for i in range(total_innings)] + ["R", "H", "E"]
        self.line_score_table.setHorizontalHeaderLabels(headers)
        
        # Resize columns
        header_view = self.line_score_table.horizontalHeader()
        for i in range(total_innings):
            header_view.setSectionResizeMode(i, QHeaderView.Stretch)
        header_view.setSectionResizeMode(total_innings, QHeaderView.Fixed)
        header_view.setSectionResizeMode(total_innings+1, QHeaderView.Fixed)
        header_view.setSectionResizeMode(total_innings+2, QHeaderView.Fixed)
        self.line_score_table.setColumnWidth(total_innings, 40)
        self.line_score_table.setColumnWidth(total_innings+1, 40)
        self.line_score_table.setColumnWidth(total_innings+2, 40)

        # Fill Data
        # Away
        for i, sc in enumerate(inning_a):
            self.line_score_table.setItem(0, i, QTableWidgetItem(str(sc)))
        self.line_score_table.setItem(0, total_innings, QTableWidgetItem(str(a_score)))
        # Hits/Errors (Mock data if not available, or calculate from box score if passed)
        self.line_score_table.setItem(0, total_innings+1, QTableWidgetItem(str(result_data.get('away_hits', '-'))))
        self.line_score_table.setItem(0, total_innings+2, QTableWidgetItem("-")) # Errors not tracked yet

        # Home
        for i, sc in enumerate(inning_h):
            self.line_score_table.setItem(1, i, QTableWidgetItem(str(sc)))
        self.line_score_table.setItem(1, total_innings, QTableWidgetItem(str(h_score)))
        self.line_score_table.setItem(1, total_innings+1, QTableWidgetItem(str(result_data.get('home_hits', '-'))))
        self.line_score_table.setItem(1, total_innings+2, QTableWidgetItem("-"))

        # Pitchers (Simplified logic)
        win_p = "-"
        lose_p = "-"
        save_p = "-"
        
        # Check starters for decision (Naive implementation)
        if h_score > a_score:
            if home_team.starting_pitcher_idx >= 0:
                p = home_team.players[home_team.starting_pitcher_idx]
                win_p = f"{p.name} ({p.record.wins}-{p.record.losses})"
            if away_team.starting_pitcher_idx >= 0:
                p = away_team.players[away_team.starting_pitcher_idx]
                lose_p = f"{p.name} ({p.record.wins}-{p.record.losses})"
        elif a_score > h_score:
            if away_team.starting_pitcher_idx >= 0:
                p = away_team.players[away_team.starting_pitcher_idx]
                win_p = f"{p.name} ({p.record.wins}-{p.record.losses})"
            if home_team.starting_pitcher_idx >= 0:
                p = home_team.players[home_team.starting_pitcher_idx]
                lose_p = f"{p.name} ({p.record.wins}-{p.record.losses})"

        self.pitcher_labels["勝利投手"].setText(win_p)
        self.pitcher_labels["敗戦投手"].setText(lose_p)
        self.pitcher_labels["セーブ"].setText(save_p)

        # Clear layouts
        while self.hr_content.count():
            child = self.hr_content.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        while self.battery_content.count():
            child = self.battery_content.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        # Mock Battery Info
        home_starter = home_team.players[home_team.starting_pitcher_idx].name if home_team.starting_pitcher_idx >= 0 else "不明"
        away_starter = away_team.players[away_team.starting_pitcher_idx].name if away_team.starting_pitcher_idx >= 0 else "不明"
        
        l1 = QLabel(f"[{away_team.name[:2]}] {away_starter} - (捕手)")
        l1.setStyleSheet(f"color: {self.theme.text_primary}; font-size: 12px;")
        l2 = QLabel(f"[{home_team.name[:2]}] {home_starter} - (捕手)")
        l2.setStyleSheet(f"color: {self.theme.text_primary}; font-size: 12px;")
        self.battery_content.addWidget(l1)
        self.battery_content.addWidget(l2)

        # Home Runs (Extract from players)
        hr_text = []
        for p in home_team.players + away_team.players:
            # Note: This is a hacky way to check HRs in this game. 
            # Ideally simulator should return a list of HR events.
            pass 
        
        no_hr = QLabel("本塁打なし")
        no_hr.setStyleSheet(f"color: {self.theme.text_muted}; font-size: 12px;")
        self.hr_content.addWidget(no_hr)