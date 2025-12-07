# -*- coding: utf-8 -*-
"""
Baseball Team Architect 2027 - Order Page
Intuitive Lineup Management with 31-Player Roster Limit
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QAbstractItemView, QGridLayout, QScrollArea, QSplitter,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QDrag

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme
from UI.widgets.panels import ToolbarPanel


class PlayerSlot(QFrame):
    """A visual slot for a player in the lineup"""

    clicked = Signal(object)  # Emits slot data
    double_clicked = Signal(object)

    def __init__(self, slot_number: int, slot_type: str = "lineup", parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.slot_number = slot_number
        self.slot_type = slot_type
        self.player = None
        self.player_idx = -1
        self._selected = False
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Slot number
        self.number_label = QLabel(str(self.slot_number))
        self.number_label.setFixedWidth(24)
        self.number_label.setAlignment(Qt.AlignCenter)
        self.number_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {self.theme.primary};
            background: transparent;
        """)
        layout.addWidget(self.number_label)

        # Player info
        self.player_label = QLabel("- 空き -")
        self.player_label.setStyleSheet(f"""
            font-size: 13px;
            color: {self.theme.text_muted};
            background: transparent;
        """)
        layout.addWidget(self.player_label, 1)

        # Position badge
        self.pos_label = QLabel("")
        self.pos_label.setFixedWidth(36)
        self.pos_label.setAlignment(Qt.AlignCenter)
        self.pos_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {self.theme.text_secondary};
            background: {self.theme.bg_input};
            border-radius: 4px;
            padding: 2px 4px;
        """)
        layout.addWidget(self.pos_label)

        # Rating
        self.rating_label = QLabel("")
        self.rating_label.setFixedWidth(40)
        self.rating_label.setAlignment(Qt.AlignCenter)
        self.rating_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 700;
            color: {self.theme.text_primary};
            background: transparent;
        """)
        layout.addWidget(self.rating_label)

    def _update_style(self):
        if self._selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme.primary};
                    border: 2px solid {self.theme.primary_light};
                    border-radius: 8px;
                }}
            """)
        elif self.player:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme.bg_card};
                    border: 1px solid {self.theme.border};
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    background-color: {self.theme.bg_card_hover};
                    border-color: {self.theme.primary};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme.bg_input};
                    border: 1px dashed {self.theme.border_muted};
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    border-color: {self.theme.primary};
                    border-style: solid;
                }}
            """)

    def set_player(self, player, player_idx: int):
        """Set the player for this slot"""
        self.player = player
        self.player_idx = player_idx

        if player:
            self.player_label.setText(player.name)
            self.player_label.setStyleSheet(f"""
                font-size: 13px;
                font-weight: 600;
                color: {self.theme.text_primary};
                background: transparent;
            """)
            self.pos_label.setText(player.position.value[:2])
            self.rating_label.setText(str(player.overall_rating))
        else:
            self.player_label.setText("- 空き -")
            self.player_label.setStyleSheet(f"""
                font-size: 13px;
                color: {self.theme.text_muted};
                background: transparent;
            """)
            self.pos_label.setText("")
            self.rating_label.setText("")

        self._update_style()

    def clear_player(self):
        """Clear the player from this slot"""
        self.set_player(None, -1)

    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()
        if selected and self.player:
            self.player_label.setStyleSheet(f"""
                font-size: 13px;
                font-weight: 600;
                color: white;
                background: transparent;
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self)
        super().mouseDoubleClickEvent(event)


class PlayerListWidget(QFrame):
    """A list of available players with filtering"""

    player_selected = Signal(object, int)  # player, index
    player_double_clicked = Signal(object, int)

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.title = title
        self.players = []  # List of (player, index) tuples
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme.bg_card};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {self.theme.text_primary};
        """)
        header.addWidget(title_label)

        self.count_label = QLabel("0人")
        self.count_label.setStyleSheet(f"""
            font-size: 12px;
            color: {self.theme.text_muted};
        """)
        header.addStretch()
        header.addWidget(self.count_label)
        layout.addLayout(header)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.theme.bg_input};
                border: none;
                border-radius: 6px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {self.theme.border_muted};
                color: {self.theme.text_primary};
            }}
            QListWidget::item:selected {{
                background-color: {self.theme.primary};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {self.theme.bg_hover};
            }}
        """)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

    def set_players(self, players_with_idx: list):
        """Set the list of players: [(player, idx), ...]"""
        self.players = players_with_idx
        self.list_widget.clear()

        for player, idx in players_with_idx:
            pos = player.position.value[:2]
            item_text = f"{pos}  {player.name}  ({player.overall_rating})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, (player, idx))
            self.list_widget.addItem(item)

        self.count_label.setText(f"{len(players_with_idx)}人")

    def get_selected(self):
        """Get currently selected player and index"""
        items = self.list_widget.selectedItems()
        if items:
            return items[0].data(Qt.UserRole)
        return None, -1

    def _on_item_clicked(self, item):
        player, idx = item.data(Qt.UserRole)
        self.player_selected.emit(player, idx)

    def _on_item_double_clicked(self, item):
        player, idx = item.data(Qt.UserRole)
        self.player_double_clicked.emit(player, idx)


class RosterSection(QFrame):
    """A section showing roster assignments"""

    slot_clicked = Signal(object)
    slot_double_clicked = Signal(object)

    def __init__(self, title: str, num_slots: int, slot_type: str, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.title = title
        self.num_slots = num_slots
        self.slot_type = slot_type
        self.slots = []
        self._selected_slot = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme.bg_card};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {self.theme.text_primary};
        """)
        header.addWidget(title_label)

        self.filled_label = QLabel(f"0/{self.num_slots}")
        self.filled_label.setStyleSheet(f"""
            font-size: 12px;
            color: {self.theme.text_muted};
        """)
        header.addStretch()
        header.addWidget(self.filled_label)
        layout.addLayout(header)

        # Slots
        for i in range(self.num_slots):
            slot = PlayerSlot(i + 1, self.slot_type)
            slot.clicked.connect(self._on_slot_clicked)
            slot.double_clicked.connect(self._on_slot_double_clicked)
            self.slots.append(slot)
            layout.addWidget(slot)

        layout.addStretch()

    def _on_slot_clicked(self, slot):
        # Deselect previous
        if self._selected_slot and self._selected_slot != slot:
            self._selected_slot.set_selected(False)
        slot.set_selected(True)
        self._selected_slot = slot
        self.slot_clicked.emit(slot)

    def _on_slot_double_clicked(self, slot):
        self.slot_double_clicked.emit(slot)

    def get_selected_slot(self):
        return self._selected_slot

    def clear_selection(self):
        if self._selected_slot:
            self._selected_slot.set_selected(False)
            self._selected_slot = None

    def set_slot_player(self, slot_idx: int, player, player_idx: int):
        if 0 <= slot_idx < len(self.slots):
            self.slots[slot_idx].set_player(player, player_idx)
            self._update_filled_count()

    def clear_slot(self, slot_idx: int):
        if 0 <= slot_idx < len(self.slots):
            self.slots[slot_idx].clear_player()
            self._update_filled_count()

    def get_all_player_indices(self) -> list:
        """Get all assigned player indices"""
        return [s.player_idx for s in self.slots if s.player_idx >= 0]

    def find_empty_slot(self) -> int:
        """Find first empty slot index, -1 if none"""
        for i, slot in enumerate(self.slots):
            if slot.player_idx < 0:
                return i
        return -1

    def _update_filled_count(self):
        filled = sum(1 for s in self.slots if s.player_idx >= 0)
        color = self.theme.success if filled == self.num_slots else self.theme.text_muted
        self.filled_label.setText(f"{filled}/{self.num_slots}")
        self.filled_label.setStyleSheet(f"font-size: 12px; color: {color};")


class OrderPage(QWidget):
    """Comprehensive lineup management page with 31-player roster limit"""

    order_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.game_state = None
        self.current_team = None
        self._selected_source = None  # Track what's selected
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Main content
        content = QWidget()
        content.setStyleSheet(f"background-color: {self.theme.bg_dark};")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        # Left panel - Available players
        left_panel = self._create_left_panel()
        content_layout.addWidget(left_panel, 1)

        # Center panel - Action buttons
        center_panel = self._create_center_panel()
        content_layout.addWidget(center_panel)

        # Right panel - Roster assignments (tabs)
        right_panel = self._create_right_panel()
        content_layout.addWidget(right_panel, 2)

        layout.addWidget(content, 1)

    def _create_toolbar(self) -> ToolbarPanel:
        toolbar = ToolbarPanel()
        toolbar.setFixedHeight(56)

        # Team selector
        team_label = QLabel("チーム:")
        team_label.setStyleSheet(f"color: {self.theme.text_secondary}; margin-left: 12px;")
        toolbar.add_widget(team_label)

        self.team_selector = QComboBox()
        self.team_selector.setMinimumWidth(200)
        self.team_selector.setFixedHeight(36)
        self.team_selector.currentIndexChanged.connect(self._on_team_changed)
        toolbar.add_widget(self.team_selector)

        toolbar.add_separator()

        # Roster count
        self.roster_count_label = QLabel("一軍登録: 0/31")
        self.roster_count_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {self.theme.text_primary};
            padding: 0 16px;
        """)
        toolbar.add_widget(self.roster_count_label)

        toolbar.add_stretch()

        # Auto-fill button
        auto_btn = QPushButton("自動編成")
        auto_btn.setFixedHeight(36)
        auto_btn.setCursor(Qt.PointingHandCursor)
        auto_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.bg_input};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 0 20px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self.theme.bg_card_hover};
            }}
        """)
        auto_btn.clicked.connect(self._auto_fill)
        toolbar.add_widget(auto_btn)

        # Save button
        save_btn = QPushButton("保存")
        save_btn.setFixedHeight(36)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 28px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self.theme.primary_hover};
            }}
        """)
        save_btn.clicked.connect(self._save_order)
        toolbar.add_widget(save_btn)

        return toolbar

    def _create_left_panel(self) -> QWidget:
        """Create the available players panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Title
        title = QLabel("選手一覧")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {self.theme.text_primary};
        """)
        layout.addWidget(title)

        # Tabs for filtering
        self.player_tabs = QTabWidget()
        self.player_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {self.theme.bg_card};
                color: {self.theme.text_secondary};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background: {self.theme.primary};
                color: white;
            }}
        """)

        # All batters
        self.batter_list = PlayerListWidget("野手")
        self.batter_list.player_double_clicked.connect(self._on_batter_double_clicked)
        self.player_tabs.addTab(self.batter_list, "野手")

        # All pitchers
        self.pitcher_list = PlayerListWidget("投手")
        self.pitcher_list.player_double_clicked.connect(self._on_pitcher_double_clicked)
        self.player_tabs.addTab(self.pitcher_list, "投手")

        # Farm players
        self.farm_list = PlayerListWidget("二軍")
        self.farm_list.player_double_clicked.connect(self._on_farm_double_clicked)
        self.player_tabs.addTab(self.farm_list, "二軍")

        layout.addWidget(self.player_tabs, 1)

        return panel

    def _create_center_panel(self) -> QWidget:
        """Create the action buttons panel"""
        panel = QWidget()
        panel.setFixedWidth(80)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addStretch()

        # Add to lineup
        add_btn = QPushButton("→")
        add_btn.setFixedSize(48, 48)
        add_btn.setStyleSheet(self._action_btn_style())
        add_btn.clicked.connect(self._add_to_roster)
        add_btn.setToolTip("一軍に追加")
        layout.addWidget(add_btn, 0, Qt.AlignCenter)

        # Remove from lineup
        remove_btn = QPushButton("←")
        remove_btn.setFixedSize(48, 48)
        remove_btn.setStyleSheet(self._action_btn_style())
        remove_btn.clicked.connect(self._remove_from_roster)
        remove_btn.setToolTip("一軍から外す")
        layout.addWidget(remove_btn, 0, Qt.AlignCenter)

        # Swap
        swap_btn = QPushButton("⇆")
        swap_btn.setFixedSize(48, 48)
        swap_btn.setStyleSheet(self._action_btn_style())
        swap_btn.clicked.connect(self._swap_players)
        swap_btn.setToolTip("入れ替え")
        layout.addWidget(swap_btn, 0, Qt.AlignCenter)

        layout.addStretch()

        return panel

    def _action_btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {self.theme.bg_card};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                font-size: 18px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {self.theme.primary};
                color: white;
                border-color: {self.theme.primary};
            }}
        """

    def _create_right_panel(self) -> QWidget:
        """Create the roster assignments panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Title
        title = QLabel("オーダー編成")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {self.theme.text_primary};
        """)
        layout.addWidget(title)

        # Tabs for different roster sections
        self.roster_tabs = QTabWidget()
        self.roster_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {self.theme.bg_card};
                color: {self.theme.text_secondary};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background: {self.theme.primary};
                color: white;
            }}
        """)

        # Scroll area for batting lineup
        batting_scroll = QScrollArea()
        batting_scroll.setWidgetResizable(True)
        batting_scroll.setFrameShape(QFrame.NoFrame)
        batting_scroll.setStyleSheet("background: transparent;")

        batting_content = QWidget()
        batting_layout = QVBoxLayout(batting_content)
        batting_layout.setSpacing(12)

        self.lineup_section = RosterSection("スターティングメンバー", 9, "lineup")
        self.lineup_section.slot_double_clicked.connect(self._on_lineup_slot_double_clicked)
        batting_layout.addWidget(self.lineup_section)

        self.bench_section = RosterSection("ベンチ野手", 6, "bench")
        self.bench_section.slot_double_clicked.connect(self._on_bench_slot_double_clicked)
        batting_layout.addWidget(self.bench_section)

        batting_layout.addStretch()
        batting_scroll.setWidget(batting_content)
        self.roster_tabs.addTab(batting_scroll, "打順・野手")

        # Scroll area for pitching staff
        pitching_scroll = QScrollArea()
        pitching_scroll.setWidgetResizable(True)
        pitching_scroll.setFrameShape(QFrame.NoFrame)
        pitching_scroll.setStyleSheet("background: transparent;")

        pitching_content = QWidget()
        pitching_layout = QVBoxLayout(pitching_content)
        pitching_layout.setSpacing(12)

        self.rotation_section = RosterSection("先発ローテーション", 6, "rotation")
        self.rotation_section.slot_double_clicked.connect(self._on_rotation_slot_double_clicked)
        pitching_layout.addWidget(self.rotation_section)

        self.relief_section = RosterSection("中継ぎ", 6, "relief")
        self.relief_section.slot_double_clicked.connect(self._on_relief_slot_double_clicked)
        pitching_layout.addWidget(self.relief_section)

        self.closer_section = RosterSection("抑え", 1, "closer")
        self.closer_section.slot_double_clicked.connect(self._on_closer_slot_double_clicked)
        pitching_layout.addWidget(self.closer_section)

        pitching_layout.addStretch()
        pitching_scroll.setWidget(pitching_content)
        self.roster_tabs.addTab(pitching_scroll, "投手")

        layout.addWidget(self.roster_tabs, 1)

        return panel

    def set_game_state(self, game_state):
        """Set game state and populate team selector"""
        self.game_state = game_state
        if not game_state:
            return

        self.team_selector.clear()
        for team in game_state.teams:
            self.team_selector.addItem(team.name, team)

        if game_state.player_team:
            idx = game_state.teams.index(game_state.player_team)
            self.team_selector.setCurrentIndex(idx)

    def _on_team_changed(self, index: int):
        if index < 0 or not self.game_state:
            return
        self.current_team = self.team_selector.itemData(index)
        self._refresh_all()

    def _refresh_all(self):
        """Refresh all displays"""
        if not self.current_team:
            return

        team = self.current_team

        # Initialize active_roster if empty
        if not team.active_roster:
            # Auto-populate with first 31 non-developmental players
            roster_players = team.get_roster_players()
            for i, p in enumerate(roster_players[:31]):
                team.active_roster.append(team.players.index(p))
            # Rest go to farm
            for i, p in enumerate(roster_players[31:]):
                team.farm_roster.append(team.players.index(p))

        # Get categorized players
        active_batters = []
        active_pitchers = []
        farm_players = []

        # Assigned indices (in lineup, rotation, etc.)
        assigned = set()
        assigned.update(team.current_lineup)
        assigned.update(team.rotation)
        assigned.update(team.setup_pitchers)
        assigned.update(team.bench_batters)
        assigned.update(team.bench_pitchers)
        if team.closer_idx >= 0:
            assigned.add(team.closer_idx)

        for idx in team.active_roster:
            if 0 <= idx < len(team.players):
                p = team.players[idx]
                if idx not in assigned:
                    if p.position.value == "投手":
                        active_pitchers.append((p, idx))
                    else:
                        active_batters.append((p, idx))

        for idx in team.farm_roster:
            if 0 <= idx < len(team.players):
                farm_players.append((team.players[idx], idx))

        # Update lists
        self.batter_list.set_players(active_batters)
        self.pitcher_list.set_players(active_pitchers)
        self.farm_list.set_players(farm_players)

        # Update roster sections
        self._update_lineup_display()
        self._update_pitching_display()
        self._update_roster_count()

    def _update_lineup_display(self):
        """Update batting lineup display"""
        team = self.current_team
        if not team:
            return

        # Starting lineup
        for i, slot in enumerate(self.lineup_section.slots):
            if i < len(team.current_lineup):
                idx = team.current_lineup[i]
                if 0 <= idx < len(team.players):
                    slot.set_player(team.players[idx], idx)
                else:
                    slot.clear_player()
            else:
                slot.clear_player()

        # Bench batters
        for i, slot in enumerate(self.bench_section.slots):
            if i < len(team.bench_batters):
                idx = team.bench_batters[i]
                if 0 <= idx < len(team.players):
                    slot.set_player(team.players[idx], idx)
                else:
                    slot.clear_player()
            else:
                slot.clear_player()

    def _update_pitching_display(self):
        """Update pitching staff display"""
        team = self.current_team
        if not team:
            return

        # Rotation
        for i, slot in enumerate(self.rotation_section.slots):
            if i < len(team.rotation):
                idx = team.rotation[i]
                if 0 <= idx < len(team.players):
                    slot.set_player(team.players[idx], idx)
                else:
                    slot.clear_player()
            else:
                slot.clear_player()

        # Relief
        for i, slot in enumerate(self.relief_section.slots):
            if i < len(team.setup_pitchers):
                idx = team.setup_pitchers[i]
                if 0 <= idx < len(team.players):
                    slot.set_player(team.players[idx], idx)
                else:
                    slot.clear_player()
            else:
                slot.clear_player()

        # Closer
        if team.closer_idx >= 0 and team.closer_idx < len(team.players):
            self.closer_section.slots[0].set_player(team.players[team.closer_idx], team.closer_idx)
        else:
            self.closer_section.slots[0].clear_player()

    def _update_roster_count(self):
        """Update roster count display"""
        if self.current_team:
            count = len(self.current_team.active_roster)
            limit = self.current_team.ACTIVE_ROSTER_LIMIT
            color = self.theme.success if count <= limit else self.theme.danger
            self.roster_count_label.setText(f"一軍登録: {count}/{limit}")
            self.roster_count_label.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 600;
                color: {color};
                padding: 0 16px;
            """)

    # === Event handlers ===
    def _on_batter_double_clicked(self, player, idx):
        """Add batter to lineup"""
        if not self.current_team:
            return
        # Find empty lineup slot, then bench
        empty_lineup = self.lineup_section.find_empty_slot()
        if empty_lineup >= 0:
            self._add_player_to_lineup(idx, empty_lineup)
        else:
            empty_bench = self.bench_section.find_empty_slot()
            if empty_bench >= 0:
                self._add_player_to_bench(idx, empty_bench)

    def _on_pitcher_double_clicked(self, player, idx):
        """Add pitcher to staff"""
        if not self.current_team:
            return
        # Try rotation, then relief, then closer
        empty_rotation = self.rotation_section.find_empty_slot()
        if empty_rotation >= 0:
            self._add_player_to_rotation(idx, empty_rotation)
        else:
            empty_relief = self.relief_section.find_empty_slot()
            if empty_relief >= 0:
                self._add_player_to_relief(idx, empty_relief)
            else:
                if self.closer_section.slots[0].player_idx < 0:
                    self._add_player_to_closer(idx)

    def _on_farm_double_clicked(self, player, idx):
        """Promote player from farm"""
        if not self.current_team:
            return
        if self.current_team.add_to_active_roster(idx):
            self._refresh_all()

    def _on_lineup_slot_double_clicked(self, slot):
        """Remove from lineup"""
        if slot.player_idx >= 0:
            self._remove_from_lineup(slot)

    def _on_bench_slot_double_clicked(self, slot):
        """Remove from bench"""
        if slot.player_idx >= 0:
            self._remove_from_bench(slot)

    def _on_rotation_slot_double_clicked(self, slot):
        """Remove from rotation"""
        if slot.player_idx >= 0:
            self._remove_from_rotation(slot)

    def _on_relief_slot_double_clicked(self, slot):
        """Remove from relief"""
        if slot.player_idx >= 0:
            self._remove_from_relief(slot)

    def _on_closer_slot_double_clicked(self, slot):
        """Remove closer"""
        if slot.player_idx >= 0:
            self._remove_from_closer()

    # === Roster modification methods ===
    def _add_player_to_lineup(self, player_idx: int, slot_idx: int):
        team = self.current_team
        while len(team.current_lineup) <= slot_idx:
            team.current_lineup.append(-1)
        team.current_lineup[slot_idx] = player_idx
        self._refresh_all()

    def _add_player_to_bench(self, player_idx: int, slot_idx: int):
        team = self.current_team
        while len(team.bench_batters) <= slot_idx:
            team.bench_batters.append(-1)
        team.bench_batters[slot_idx] = player_idx
        self._refresh_all()

    def _add_player_to_rotation(self, player_idx: int, slot_idx: int):
        team = self.current_team
        while len(team.rotation) <= slot_idx:
            team.rotation.append(-1)
        team.rotation[slot_idx] = player_idx
        self._refresh_all()

    def _add_player_to_relief(self, player_idx: int, slot_idx: int):
        team = self.current_team
        while len(team.setup_pitchers) <= slot_idx:
            team.setup_pitchers.append(-1)
        team.setup_pitchers[slot_idx] = player_idx
        self._refresh_all()

    def _add_player_to_closer(self, player_idx: int):
        self.current_team.closer_idx = player_idx
        self._refresh_all()

    def _remove_from_lineup(self, slot):
        idx = slot.slot_number - 1
        if idx < len(self.current_team.current_lineup):
            self.current_team.current_lineup[idx] = -1
        self._refresh_all()

    def _remove_from_bench(self, slot):
        idx = slot.slot_number - 1
        if idx < len(self.current_team.bench_batters):
            self.current_team.bench_batters[idx] = -1
        self._refresh_all()

    def _remove_from_rotation(self, slot):
        idx = slot.slot_number - 1
        if idx < len(self.current_team.rotation):
            self.current_team.rotation[idx] = -1
        self._refresh_all()

    def _remove_from_relief(self, slot):
        idx = slot.slot_number - 1
        if idx < len(self.current_team.setup_pitchers):
            self.current_team.setup_pitchers[idx] = -1
        self._refresh_all()

    def _remove_from_closer(self):
        self.current_team.closer_idx = -1
        self._refresh_all()

    def _add_to_roster(self):
        """Add selected player to appropriate roster slot"""
        tab_idx = self.player_tabs.currentIndex()
        if tab_idx == 0:  # Batters
            player, idx = self.batter_list.get_selected()
            if player:
                self._on_batter_double_clicked(player, idx)
        elif tab_idx == 1:  # Pitchers
            player, idx = self.pitcher_list.get_selected()
            if player:
                self._on_pitcher_double_clicked(player, idx)
        elif tab_idx == 2:  # Farm
            player, idx = self.farm_list.get_selected()
            if player:
                self._on_farm_double_clicked(player, idx)

    def _remove_from_roster(self):
        """Remove selected player from roster"""
        roster_tab_idx = self.roster_tabs.currentIndex()
        if roster_tab_idx == 0:  # Batting
            slot = self.lineup_section.get_selected_slot()
            if slot and slot.player_idx >= 0:
                self._remove_from_lineup(slot)
                return
            slot = self.bench_section.get_selected_slot()
            if slot and slot.player_idx >= 0:
                self._remove_from_bench(slot)
        else:  # Pitching
            slot = self.rotation_section.get_selected_slot()
            if slot and slot.player_idx >= 0:
                self._remove_from_rotation(slot)
                return
            slot = self.relief_section.get_selected_slot()
            if slot and slot.player_idx >= 0:
                self._remove_from_relief(slot)
                return
            slot = self.closer_section.get_selected_slot()
            if slot and slot.player_idx >= 0:
                self._remove_from_closer()

    def _swap_players(self):
        """Swap two players"""
        # TODO: Implement swap functionality
        pass

    def _auto_fill(self):
        """Auto-fill roster based on ratings"""
        if not self.current_team:
            return

        team = self.current_team
        roster = team.get_roster_players()

        # Clear current assignments
        team.current_lineup = []
        team.bench_batters = []
        team.rotation = []
        team.setup_pitchers = []
        team.closer_idx = -1
        team.active_roster = []
        team.farm_roster = []

        # Separate and sort players
        batters = [(team.players.index(p), p) for p in roster if p.position.value != "投手"]
        pitchers = [(team.players.index(p), p) for p in roster if p.position.value == "投手"]

        batters.sort(key=lambda x: x[1].overall_rating, reverse=True)
        pitchers.sort(key=lambda x: x[1].overall_rating, reverse=True)

        # Assign top 9 batters to lineup
        for idx, p in batters[:9]:
            team.current_lineup.append(idx)
            team.active_roster.append(idx)

        # Assign next batters to bench (up to 6)
        for idx, p in batters[9:15]:
            team.bench_batters.append(idx)
            team.active_roster.append(idx)

        # Sort pitchers by type
        starters = [(idx, p) for idx, p in pitchers if p.pitch_type and p.pitch_type.value == "先発"]
        relievers = [(idx, p) for idx, p in pitchers if p.pitch_type and p.pitch_type.value == "中継ぎ"]
        closers = [(idx, p) for idx, p in pitchers if p.pitch_type and p.pitch_type.value == "抑え"]

        starters.sort(key=lambda x: x[1].overall_rating, reverse=True)
        relievers.sort(key=lambda x: x[1].overall_rating, reverse=True)
        closers.sort(key=lambda x: x[1].overall_rating, reverse=True)

        # Assign rotation (up to 6)
        for idx, p in starters[:6]:
            team.rotation.append(idx)
            if idx not in team.active_roster:
                team.active_roster.append(idx)

        # Assign closer
        if closers:
            idx, p = closers[0]
            team.closer_idx = idx
            if idx not in team.active_roster:
                team.active_roster.append(idx)
            closers = closers[1:]
        elif relievers:
            idx, p = relievers[0]
            team.closer_idx = idx
            if idx not in team.active_roster:
                team.active_roster.append(idx)
            relievers = relievers[1:]

        # Assign relief (up to 6)
        remaining = starters[6:] + relievers + closers
        for idx, p in remaining[:6]:
            team.setup_pitchers.append(idx)
            if idx not in team.active_roster:
                team.active_roster.append(idx)

        # Rest go to farm
        all_assigned = set(team.active_roster)
        for p in roster:
            idx = team.players.index(p)
            if idx not in all_assigned:
                team.farm_roster.append(idx)

        self._refresh_all()

    def _save_order(self):
        """Save roster configuration"""
        if not self.current_team:
            return

        # Clean up empty slots
        team = self.current_team
        team.current_lineup = [i for i in team.current_lineup if i >= 0]
        team.bench_batters = [i for i in team.bench_batters if i >= 0]
        team.rotation = [i for i in team.rotation if i >= 0]
        team.setup_pitchers = [i for i in team.setup_pitchers if i >= 0]

        self.order_saved.emit()
        QMessageBox.information(self, "保存完了", "オーダーを保存しました。")
