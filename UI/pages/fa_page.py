# -*- coding: utf-8 -*-
"""
NPB Pennant Simulator - Free Agent Page
OOTP-Style Premium Professional Free Agent System
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QPushButton,
    QComboBox, QSpinBox, QFrame, QMessageBox, QProgressBar,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme
from UI.widgets.charts import RadarChart
from UI.widgets.cards import PremiumCard


class FAPage(QWidget):
    """Premium styled Free Agent page with player signing interface"""

    player_signed = Signal(object, int, int)  # player, years, salary

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.game_state = None
        self.user_team = None
        self.fa_players = []
        self.selected_player = None

        self._setup_ui()

    def _setup_ui(self):
        """Create the FA page layout"""
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

        title = QLabel("🏷️  フリーエージェント市場")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        title_layout.addWidget(title)

        subtitle = QLabel("Free Agent Market")
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {self.theme.text_muted};
            background: transparent;
        """)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Budget info badge
        budget_frame = QFrame()
        budget_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.success},
                    stop:1 #2ecc71);
                border-radius: 8px;
            }}
        """)
        budget_layout = QHBoxLayout(budget_frame)
        budget_layout.setContentsMargins(16, 8, 16, 8)

        budget_icon = QLabel("💰")
        budget_icon.setStyleSheet("background: transparent;")
        budget_layout.addWidget(budget_icon)

        self.budget_label = QLabel("予算: ¥0")
        self.budget_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: white;
            background: transparent;
        """)
        budget_layout.addWidget(self.budget_label)

        header_layout.addWidget(budget_frame)
        main_layout.addWidget(header_frame)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {self.theme.border};
                width: 2px;
            }}
        """)

        # Left side - FA list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Filter controls
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.theme.bg_card};
                border: 1px solid {self.theme.border_muted};
                border-radius: 8px;
            }}
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(12, 8, 12, 8)

        position_label = QLabel("🎯 ポジション:")
        position_label.setStyleSheet(f"color: {self.theme.text_secondary}; background: transparent;")
        filter_layout.addWidget(position_label)

        self.position_filter = QComboBox()
        self.position_filter.addItems(["全て", "投手", "捕手", "内野手", "外野手"])
        self.position_filter.setStyleSheet(f"""
            QComboBox {{
                background: {self.theme.bg_input};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {self.theme.primary};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {self.theme.bg_card};
                color: {self.theme.text_primary};
                selection-background-color: {self.theme.primary};
            }}
        """)
        self.position_filter.currentIndexChanged.connect(self._filter_players)
        filter_layout.addWidget(self.position_filter)

        filter_layout.addSpacing(16)

        age_label = QLabel("📅 年齢:")
        age_label.setStyleSheet(f"color: {self.theme.text_secondary}; background: transparent;")
        filter_layout.addWidget(age_label)

        self.age_filter = QComboBox()
        self.age_filter.addItems(["全て", "25歳以下", "26-30歳", "31-35歳", "36歳以上"])
        self.age_filter.setStyleSheet(f"""
            QComboBox {{
                background: {self.theme.bg_input};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {self.theme.primary};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {self.theme.bg_card};
                color: {self.theme.text_primary};
                selection-background-color: {self.theme.primary};
            }}
        """)
        self.age_filter.currentIndexChanged.connect(self._filter_players)
        filter_layout.addWidget(self.age_filter)

        filter_layout.addStretch()
        left_layout.addWidget(filter_frame)

        # FA table
        fa_card = PremiumCard("FA選手一覧", "👥")

        self.fa_table = QTableWidget()
        self.fa_table.setColumnCount(7)
        self.fa_table.setHorizontalHeaderLabels([
            "名前", "ポジション", "年齢", "総合", "前所属", "希望年俸", "希望年数"
        ])

        self.fa_table.setStyleSheet(f"""
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

        header = self.fa_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.fa_table.verticalHeader().setVisible(False)
        self.fa_table.verticalHeader().setDefaultSectionSize(40)
        self.fa_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.fa_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.fa_table.setSelectionMode(QTableWidget.SingleSelection)
        self.fa_table.setShowGrid(False)
        self.fa_table.itemSelectionChanged.connect(self._on_player_selected)

        fa_card.add_widget(self.fa_table)
        left_layout.addWidget(fa_card)

        splitter.addWidget(left_widget)

        # Right side - Player detail and offer
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Player detail card
        self.detail_card = PremiumCard("選手詳細", "📊")

        # Player info
        self.player_name = QLabel("選手を選択してください")
        self.player_name.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        self.detail_card.add_widget(self.player_name)

        self.player_info = QLabel("")
        self.player_info.setStyleSheet(f"""
            font-size: 14px;
            color: {self.theme.text_secondary};
            margin-bottom: 12px;
            background: transparent;
        """)
        self.detail_card.add_widget(self.player_info)

        # Radar chart
        self.radar_chart = RadarChart()
        self.radar_chart.setFixedHeight(180)
        self.detail_card.add_widget(self.radar_chart)

        # Career stats
        self.career_label = QLabel("")
        self.career_label.setStyleSheet(f"""
            color: {self.theme.text_secondary};
            font-size: 12px;
            padding: 12px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self.theme.bg_input},
                stop:1 {self.theme.bg_card});
            border-radius: 8px;
            border: 1px solid {self.theme.border_muted};
        """)
        self.detail_card.add_widget(self.career_label)

        right_layout.addWidget(self.detail_card)

        # Offer card
        self.offer_card = PremiumCard("オファー", "📝")

        # Years
        years_layout = QHBoxLayout()
        years_label = QLabel("📆 契約年数:")
        years_label.setStyleSheet(f"color: {self.theme.text_secondary}; background: transparent;")
        years_layout.addWidget(years_label)

        self.years_spin = QSpinBox()
        self.years_spin.setRange(1, 7)
        self.years_spin.setValue(2)
        self.years_spin.setStyleSheet(f"""
            QSpinBox {{
                background: {self.theme.bg_input};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 80px;
            }}
            QSpinBox:hover {{
                border-color: {self.theme.primary};
            }}
        """)
        self.years_spin.valueChanged.connect(self._update_offer)
        years_layout.addWidget(self.years_spin)

        years_layout.addStretch()
        self.offer_card.add_layout(years_layout)

        # Salary
        salary_layout = QHBoxLayout()
        salary_label = QLabel("💴 年俸（万円）:")
        salary_label.setStyleSheet(f"color: {self.theme.text_secondary}; background: transparent;")
        salary_layout.addWidget(salary_label)

        self.salary_spin = QSpinBox()
        self.salary_spin.setRange(1000, 100000)
        self.salary_spin.setSingleStep(1000)
        self.salary_spin.setValue(5000)
        self.salary_spin.setStyleSheet(f"""
            QSpinBox {{
                background: {self.theme.bg_input};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 100px;
            }}
            QSpinBox:hover {{
                border-color: {self.theme.primary};
            }}
        """)
        self.salary_spin.valueChanged.connect(self._update_offer)
        salary_layout.addWidget(self.salary_spin)

        salary_layout.addStretch()
        self.offer_card.add_layout(salary_layout)

        # Total cost
        total_frame = QFrame()
        total_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.theme.bg_input};
                border-radius: 8px;
                border: 1px solid {self.theme.border_muted};
            }}
        """)
        total_layout = QHBoxLayout(total_frame)
        total_layout.setContentsMargins(12, 10, 12, 10)

        total_icon = QLabel("💰")
        total_icon.setStyleSheet("background: transparent;")
        total_layout.addWidget(total_icon)

        self.total_label = QLabel("総額: ¥0")
        self.total_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()

        self.offer_card.add_widget(total_frame)

        # Interest meter
        interest_frame = QFrame()
        interest_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.theme.bg_input};
                border-radius: 8px;
                border: 1px solid {self.theme.border_muted};
            }}
        """)
        interest_layout = QVBoxLayout(interest_frame)
        interest_layout.setContentsMargins(12, 10, 12, 10)
        interest_layout.setSpacing(6)

        interest_header = QHBoxLayout()
        interest_label = QLabel("📈 選手の興味:")
        interest_label.setStyleSheet(f"color: {self.theme.text_secondary}; background: transparent;")
        interest_header.addWidget(interest_label)

        self.interest_value = QLabel("50%")
        self.interest_value.setStyleSheet(f"""
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        interest_header.addWidget(self.interest_value)
        interest_header.addStretch()

        interest_layout.addLayout(interest_header)

        self.interest_bar = QProgressBar()
        self.interest_bar.setRange(0, 100)
        self.interest_bar.setValue(50)
        self.interest_bar.setTextVisible(False)
        self.interest_bar.setFixedHeight(8)
        self.interest_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {self.theme.bg_card};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.primary},
                    stop:1 {self.theme.accent});
                border-radius: 4px;
            }}
        """)
        interest_layout.addWidget(self.interest_bar)

        self.offer_card.add_widget(interest_frame)

        right_layout.addWidget(self.offer_card)

        # Sign button
        self.sign_button = QPushButton("契約オファーを送る")
        self.sign_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.primary},
                    stop:1 {self.theme.accent});
                color: white;
                border: none;
                border-radius: 12px;
                padding: 16px 32px;
                font-size: 15px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme.accent},
                    stop:1 {self.theme.primary});
            }}
            QPushButton:disabled {{
                background: {self.theme.bg_input};
                color: {self.theme.text_muted};
            }}
        """)
        self.sign_button.clicked.connect(self._make_offer)
        self.sign_button.setEnabled(False)
        right_layout.addWidget(self.sign_button)

        splitter.addWidget(right_widget)
        splitter.setSizes([550, 450])

        main_layout.addWidget(splitter)

    def set_game_state(self, game_state):
        """Update with game state"""
        self.game_state = game_state
        if not game_state:
            return

        self.user_team = game_state.teams[0]  # Assuming first team is user's

        # Calculate budget
        budget = 500000  # Base budget in 万円
        current_payroll = sum(p.salary for p in self.user_team.players) // 10000
        remaining = budget - current_payroll
        self.budget_label.setText(f"予算: ¥{remaining:,}万")

        self._generate_fa_pool()
        self._update_fa_table()

    def _generate_fa_pool(self):
        """Generate FA player pool"""
        import random

        positions = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "外野手"]
        teams = ["読売", "阪神", "中日", "広島", "横浜", "ヤクルト",
                "ソフトバンク", "西武", "楽天", "ロッテ", "日本ハム", "オリックス"]

        surnames = ["田中", "鈴木", "佐藤", "山田", "伊藤", "高橋", "渡辺", "中村"]
        first_names = ["大翔", "翔太", "健太", "拓也", "雄太", "達也", "和也", "直樹"]

        self.fa_players = []

        for i in range(30):
            name = random.choice(surnames) + " " + random.choice(first_names)
            position = random.choice(positions)
            age = random.randint(26, 38)
            overall = random.randint(45, 85)
            prev_team = random.choice(teams)

            # Calculate expected salary based on overall and age
            base_salary = overall * 100  # Base salary in 万円
            age_factor = max(0.5, 1.5 - (age - 25) * 0.05)
            expected_salary = int(base_salary * age_factor)
            expected_years = min(5, max(1, 7 - (age - 25) // 3))

            # Generate abilities
            if position == "投手":
                abilities = {
                    "球速": random.randint(overall - 15, overall + 10),
                    "変化球": random.randint(overall - 15, overall + 10),
                    "コントロール": random.randint(overall - 15, overall + 10),
                    "スタミナ": random.randint(overall - 15, overall + 10),
                }
            else:
                abilities = {
                    "ミート": random.randint(overall - 15, overall + 10),
                    "パワー": random.randint(overall - 15, overall + 10),
                    "走力": random.randint(overall - 15, overall + 10),
                    "肩力": random.randint(overall - 15, overall + 10),
                    "守備力": random.randint(overall - 15, overall + 10),
                }

            # Clamp abilities
            abilities = {k: max(1, min(99, v)) for k, v in abilities.items()}

            # Generate career stats
            if position == "投手":
                career = {
                    "通算勝利": random.randint(0, 150),
                    "通算セーブ": random.randint(0, 100),
                    "通算奪三振": random.randint(0, 1500),
                    "通算防御率": round(random.uniform(2.5, 5.0), 2)
                }
            else:
                career = {
                    "通算安打": random.randint(0, 2000),
                    "通算本塁打": random.randint(0, 400),
                    "通算打点": random.randint(0, 1200),
                    "通算打率": round(random.uniform(0.220, 0.320), 3)
                }

            fa_player = {
                "name": name,
                "position": position,
                "age": age,
                "overall": overall,
                "prev_team": prev_team,
                "expected_salary": expected_salary,
                "expected_years": expected_years,
                "abilities": abilities,
                "career": career
            }
            self.fa_players.append(fa_player)

        # Sort by overall
        self.fa_players.sort(key=lambda x: x["overall"], reverse=True)

    def _update_fa_table(self):
        """Update FA table"""
        self.fa_table.setRowCount(len(self.fa_players))

        for row, player in enumerate(self.fa_players):
            # Name
            name_item = QTableWidgetItem(player["name"])
            name_item.setData(Qt.UserRole, player)
            name_item.setFont(QFont("", -1, QFont.Bold))
            self.fa_table.setItem(row, 0, name_item)

            # Position
            pos_item = QTableWidgetItem(player["position"])
            pos_item.setTextAlignment(Qt.AlignCenter)
            self.fa_table.setItem(row, 1, pos_item)

            # Age
            age_item = QTableWidgetItem(str(player["age"]))
            age_item.setTextAlignment(Qt.AlignCenter)
            self.fa_table.setItem(row, 2, age_item)

            # Overall
            ovr_item = QTableWidgetItem(str(player["overall"]))
            ovr_item.setTextAlignment(Qt.AlignCenter)
            ovr_item.setForeground(QBrush(QColor(self._get_rating_color(player["overall"]))))
            font = QFont()
            font.setBold(True)
            ovr_item.setFont(font)
            self.fa_table.setItem(row, 3, ovr_item)

            # Previous team
            team_item = QTableWidgetItem(player["prev_team"])
            team_item.setTextAlignment(Qt.AlignCenter)
            self.fa_table.setItem(row, 4, team_item)

            # Expected salary
            salary_item = QTableWidgetItem(f"¥{player['expected_salary']:,}万")
            salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.fa_table.setItem(row, 5, salary_item)

            # Expected years
            years_item = QTableWidgetItem(f"{player['expected_years']}年")
            years_item.setTextAlignment(Qt.AlignCenter)
            self.fa_table.setItem(row, 6, years_item)

    def _get_rating_color(self, rating: int) -> str:
        """Get color for rating value"""
        if rating >= 80:
            return self.theme.rating_s
        elif rating >= 70:
            return self.theme.rating_a
        elif rating >= 60:
            return self.theme.rating_b
        elif rating >= 50:
            return self.theme.rating_c
        elif rating >= 40:
            return self.theme.rating_d
        else:
            return self.theme.rating_e

    def _on_player_selected(self):
        """Handle player selection"""
        selected = self.fa_table.selectedItems()
        if not selected:
            self.selected_player = None
            self.sign_button.setEnabled(False)
            return

        row = selected[0].row()
        self.selected_player = self.fa_table.item(row, 0).data(Qt.UserRole)
        self._update_player_detail()
        self._update_offer()
        self.sign_button.setEnabled(True)

    def _update_player_detail(self):
        """Update player detail panel"""
        if not self.selected_player:
            self.player_name.setText("選手を選択してください")
            self.player_info.setText("")
            self.career_label.setText("")
            return

        p = self.selected_player

        self.player_name.setText(p["name"])
        self.player_info.setText(f"{p['position']} | {p['age']}歳 | 前所属: {p['prev_team']}")

        # Update radar chart
        abilities = list(p["abilities"].values())
        labels = list(p["abilities"].keys())
        self.radar_chart.set_data(abilities, labels)

        # Career stats
        career_text = "  |  ".join(f"{k}: {v}" for k, v in p["career"].items())
        self.career_label.setText(career_text)

        # Set default offer values
        self.salary_spin.setValue(p["expected_salary"])
        self.years_spin.setValue(p["expected_years"])

    def _update_offer(self):
        """Update offer display"""
        years = self.years_spin.value()
        salary = self.salary_spin.value()
        total = years * salary

        self.total_label.setText(f"総額: ¥{total:,}万")

        # Calculate interest
        if self.selected_player:
            p = self.selected_player
            expected_total = p["expected_years"] * p["expected_salary"]
            offer_total = years * salary

            ratio = offer_total / expected_total if expected_total > 0 else 0

            # Interest based on offer vs expectation
            if ratio >= 1.3:
                interest = 95
            elif ratio >= 1.1:
                interest = 80
            elif ratio >= 0.9:
                interest = 60
            elif ratio >= 0.7:
                interest = 40
            else:
                interest = 20

            # Age factor - older players more likely to accept
            if p["age"] >= 35:
                interest = min(100, interest + 15)
            elif p["age"] >= 32:
                interest = min(100, interest + 10)

            self.interest_bar.setValue(interest)
            self.interest_value.setText(f"{interest}%")

            # Color the progress bar based on interest
            if interest >= 70:
                bar_color = self.theme.success
                text_color = self.theme.success
            elif interest >= 50:
                bar_color = self.theme.warning
                text_color = self.theme.warning
            else:
                bar_color = self.theme.danger
                text_color = self.theme.danger

            self.interest_bar.setStyleSheet(f"""
                QProgressBar {{
                    background: {self.theme.bg_card};
                    border-radius: 4px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {bar_color},
                        stop:1 {bar_color});
                    border-radius: 4px;
                }}
            """)
            self.interest_value.setStyleSheet(f"""
                font-weight: 700;
                color: {text_color};
                background: transparent;
            """)

    def _filter_players(self):
        """Filter FA players"""
        pos_filter = self.position_filter.currentText()
        age_filter = self.age_filter.currentText()

        for row in range(self.fa_table.rowCount()):
            pos_item = self.fa_table.item(row, 1)
            age_item = self.fa_table.item(row, 2)

            if not pos_item or not age_item:
                continue

            position = pos_item.text()
            age = int(age_item.text())

            # Position filter
            pos_match = True
            if pos_filter == "投手":
                pos_match = position == "投手"
            elif pos_filter == "捕手":
                pos_match = position == "捕手"
            elif pos_filter == "内野手":
                pos_match = position in ["一塁手", "二塁手", "三塁手", "遊撃手"]
            elif pos_filter == "外野手":
                pos_match = position == "外野手"

            # Age filter
            age_match = True
            if age_filter == "25歳以下":
                age_match = age <= 25
            elif age_filter == "26-30歳":
                age_match = 26 <= age <= 30
            elif age_filter == "31-35歳":
                age_match = 31 <= age <= 35
            elif age_filter == "36歳以上":
                age_match = age >= 36

            self.fa_table.setRowHidden(row, not (pos_match and age_match))

    def _make_offer(self):
        """Make contract offer"""
        if not self.selected_player or not self.user_team:
            return

        p = self.selected_player
        years = self.years_spin.value()
        salary = self.salary_spin.value()
        interest = self.interest_bar.value()

        # Random chance based on interest
        import random
        success = random.randint(1, 100) <= interest

        if success:
            # Remove from FA pool
            self.fa_players.remove(p)
            self._update_fa_table()

            # Emit signal
            self.player_signed.emit(p, years, salary)

            self.selected_player = None
            self._update_player_detail()
            self.sign_button.setEnabled(False)

            QMessageBox.information(
                self, "🎉 契約成立！",
                f"{p['name']}と{years}年¥{salary:,}万で契約しました！"
            )
        else:
            QMessageBox.warning(
                self, "契約失敗",
                f"{p['name']}はオファーを断りました。\nより良い条件を提示してください。"
            )
