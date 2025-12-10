# -*- coding: utf-8 -*-
"""
Baseball Team Architect 2027 - Stats Page
Premium Statistics Dashboard with Categorized Views (Standard, Advanced, Fielding, etc.)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QComboBox, QPushButton, QScrollArea, QAbstractItemView, QButtonGroup,
    QScrollBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme
from UI.widgets.panels import ToolbarPanel
from UI.widgets.tables import SortableTableWidgetItem
from models import TeamLevel, PlayerRecord
from stats_records import update_league_stats

class StatsTable(QTableWidget):
    """
    Custom Table for displaying statistics with sorting & horizontal scrolling
    Supports multiple categories of stats columns.
    """
    player_double_clicked = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                gridline-color: {self.theme.border_muted};
            }}
            QTableWidget::item {{
                padding: 4px;
                color: {self.theme.text_primary};
                border-bottom: 1px solid {self.theme.border_muted};
            }}
            QTableWidget::item:selected {{
                background-color: {self.theme.primary};
                color: #111111;
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
                padding: 8px 4px;
                border: none;
                border-bottom: 2px solid {self.theme.primary};
                border-right: 1px solid {self.theme.border_muted};
            }}
        """)

        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(32)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setShowGrid(True)
        self.setAlternatingRowColors(False)
        self.setWordWrap(False)

        # Sort setup
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        
        # Horizontal Scroll Setup
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.cellDoubleClicked.connect(self._on_double_click)

    def _on_header_clicked(self, logicalIndex):
        header = self.horizontalHeader()
        current_column = header.sortIndicatorSection()
        current_order = header.sortIndicatorOrder()
        
        if current_column != logicalIndex:
            new_order = Qt.DescendingOrder
        else:
            new_order = Qt.AscendingOrder if current_order == Qt.DescendingOrder else Qt.DescendingOrder

        self.sortItems(logicalIndex, new_order)
        header.setSortIndicator(logicalIndex, new_order)

    def _on_double_click(self, row, col):
        item = self.item(row, 0)
        if item:
            player = item.data(Qt.UserRole + 1)
            if player:
                self.player_double_clicked.emit(player)

    def _get_column_config(self, mode: str, category: str):
        """
        Returns (headers, widths, value_extractor_func) based on mode and category
        """
        # 共通ヘルパー: 属性が存在しない場合の安全策
        def safe_get(obj, attr, default=0.0):
            return getattr(obj, attr, default)

        if mode == "batter":
            if category == "Standard":
                headers = ["名前", "チーム", "Pos", "試合", "打席", "打数", "安打", "二塁", "三塁", "本塁", "得点", "打点", "盗塁", "盗刺", "四球", "三振", "打率", "出塁", "長打", "OPS"]
                widths = [140, 60, 40, 40, 45, 45, 45, 40, 40, 40, 40, 40, 40, 40, 40, 40, 55, 55, 55, 55]
                def extractor(p, t, r):
                    avg = r.batting_average; ops = r.ops
                    return (
                        [p.name, t, p.position.value, r.games, r.plate_appearances, r.at_bats, r.hits, r.doubles, r.triples, r.home_runs, r.runs, r.rbis, r.stolen_bases, r.caught_stealing, r.walks, r.strikeouts, f".{int(avg*1000):03d}", f".{int(r.obp*1000):03d}", f".{int(r.slg*1000):03d}", f".{int(ops*1000):03d}"],
                        [p.name, t, p.position.value, r.games, r.plate_appearances, r.at_bats, r.hits, r.doubles, r.triples, r.home_runs, r.runs, r.rbis, r.stolen_bases, r.caught_stealing, r.walks, r.strikeouts, avg, r.obp, r.slg, ops]
                    )

            elif category == "Advanced":
                headers = ["名前", "チーム", "Pos", "打席", "BB%", "K%", "BB/K", "ISO", "BABIP", "wOBA", "wRC", "wRC+", "wRAA", "WAR"]
                widths = [140, 60, 40, 45, 50, 50, 50, 50, 55, 55, 50, 50, 50, 50]
                def extractor(p, t, r):
                    bb_k = r.walks / r.strikeouts if r.strikeouts > 0 else r.walks
                    # wRAA 簡易計算: (wOBA - LeaguewOBA) / 1.2 * PA (ここでは正確なLeague値不明のため仮置き、もしくはrecordにあれば使う)
                    # 今回はPlayerRecordにないのでwRC+から推測表示などはせず、プレースホルダーまたは0
                    w_raa = (r.woba - 0.320) / 1.2 * r.plate_appearances # 仮のリーグwOBA 0.320
                    return (
                        [p.name, t, p.position.value, r.plate_appearances, f"{r.bb_pct*100:.1f}%", f"{r.k_pct*100:.1f}%", f"{bb_k:.2f}", f"{r.iso:.3f}", f"{r.babip:.3f}", f".{int(r.woba*1000):03d}", f"{r.wrc:.1f}", int(r.wrc_plus), f"{w_raa:.1f}", f"{r.war:.1f}"],
                        [p.name, t, p.position.value, r.plate_appearances, r.bb_pct, r.k_pct, bb_k, r.iso, r.babip, r.woba, r.wrc, r.wrc_plus, w_raa, r.war]
                    )

            elif category == "BattedBall":
                headers = ["名前", "チーム", "Pos", "GB%", "FB%", "LD%", "IFFB%", "HR/FB", "Pull%", "Cent%", "Oppo%", "Hard%", "Mid%", "Soft%"]
                widths = [140, 60, 40, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
                def extractor(p, t, r):
                    return (
                        [p.name, t, p.position.value, f"{r.gb_pct*100:.1f}%", f"{r.fb_pct*100:.1f}%", f"{r.ld_pct*100:.1f}%", f"{r.iffb_pct*100:.1f}%", f"{r.hr_fb*100:.1f}%", f"{r.pull_pct*100:.1f}%", f"{r.cent_pct*100:.1f}%", f"{r.oppo_pct*100:.1f}%", f"{r.hard_pct*100:.1f}%", f"{r.mid_pct*100:.1f}%", f"{r.soft_pct*100:.1f}%"],
                        [p.name, t, p.position.value, r.gb_pct, r.fb_pct, r.ld_pct, r.iffb_pct, r.hr_fb, r.pull_pct, r.cent_pct, r.oppo_pct, r.hard_pct, r.mid_pct, r.soft_pct]
                    )

            elif category == "PlateDiscipline":
                headers = ["名前", "チーム", "Pos", "O-Swing%", "Z-Swing%", "Swing%", "O-Contact%", "Z-Contact%", "Contact%", "Whiff%", "SwStr%"]
                widths = [140, 60, 40, 65, 65, 60, 65, 65, 60, 60, 60]
                def extractor(p, t, r):
                    return (
                        [p.name, t, p.position.value, f"{r.o_swing_pct*100:.1f}%", f"{r.z_swing_pct*100:.1f}%", f"{r.swing_pct*100:.1f}%", f"{r.o_contact_pct*100:.1f}%", f"{r.z_contact_pct*100:.1f}%", f"{r.contact_pct*100:.1f}%", f"{r.whiff_pct*100:.1f}%", f"{r.swstr_pct*100:.1f}%"],
                        [p.name, t, p.position.value, r.o_swing_pct, r.z_swing_pct, r.swing_pct, r.o_contact_pct, r.z_contact_pct, r.contact_pct, r.whiff_pct, r.swstr_pct]
                    )

            elif category == "Fielding":
                headers = ["名前", "チーム", "Pos", "Inn", "RngR", "ErrR", "ARM", "DPR", "rSB", "rBlk", "UZR", "UZR/1000", "UZR/1200"]
                widths = [140, 60, 40, 50, 50, 50, 50, 50, 50, 50, 60, 70, 70]
                def extractor(p, t, r):
                    # PlayerRecordに新規追加されたフィールドを使用
                    inn = safe_get(r, "defensive_innings", 0.0)
                    rng = safe_get(r, "uzr_rngr", 0.0)
                    err = safe_get(r, "uzr_errr", 0.0)
                    arm = safe_get(r, "uzr_arm", 0.0)
                    dpr = safe_get(r, "uzr_dpr", 0.0)
                    rsb = safe_get(r, "uzr_rsb", 0.0)
                    blk = safe_get(r, "uzr_rblk", 0.0)
                    uzr = safe_get(r, "uzr", 0.0)
                    u1000 = safe_get(r, "uzr_1000", 0.0)
                    u1200 = safe_get(r, "uzr_1200", 0.0)
                    
                    return (
                        [p.name, t, p.position.value, f"{inn:.1f}", f"{rng:+.1f}", f"{err:+.1f}", f"{arm:+.1f}", f"{dpr:+.1f}", f"{rsb:+.1f}", f"{blk:+.1f}", f"{uzr:+.1f}", f"{u1000:+.1f}", f"{u1200:+.1f}"],
                        [p.name, t, p.position.value, inn, rng, err, arm, dpr, rsb, blk, uzr, u1000, u1200]
                    )

            elif category == "Value":
                headers = ["名前", "チーム", "Pos", "WAR", "wRC+", "wOBA", "UZR", "wSB", "UBR", "ISO"]
                widths = [140, 60, 40, 50, 50, 55, 60, 50, 50, 50]
                def extractor(p, t, r):
                    return (
                        [p.name, t, p.position.value, f"{r.war:.1f}", int(r.wrc_plus), f".{int(r.woba*1000):03d}", f"{safe_get(r, 'uzr', 0.0):.1f}", f"{r.wsb:.1f}", f"{r.ubr:.1f}", f"{r.iso:.3f}"],
                        [p.name, t, p.position.value, r.war, r.wrc_plus, r.woba, safe_get(r, 'uzr', 0.0), r.wsb, r.ubr, r.iso]
                    )
            
            else: # Default fallback
                return self._get_column_config("batter", "Standard")

        else: # Pitcher
            if category == "Standard":
                headers = ["名前", "チーム", "Type", "試合", "先発", "完投", "完封", "投球回", "被安", "被本", "与四", "奪三", "失点", "自責", "防御率", "勝利", "敗戦", "S", "H", "WHIP"]
                widths = [140, 60, 40, 40, 40, 40, 40, 55, 45, 40, 40, 45, 40, 40, 55, 40, 40, 35, 35, 50]
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if p.pitch_type else "投"
                    era = r.era if r.innings_pitched > 0 else 99.99
                    whip = r.whip if r.innings_pitched > 0 else 99.99
                    return (
                        [p.name, t, ptype, r.games_pitched, r.games_started, r.complete_games, r.shutouts, f"{r.innings_pitched:.1f}", r.hits_allowed, r.home_runs_allowed, r.walks_allowed, r.strikeouts_pitched, r.runs_allowed, r.earned_runs, f"{r.era:.2f}", r.wins, r.losses, r.saves, r.holds, f"{r.whip:.2f}"],
                        [p.name, t, "P", r.games_pitched, r.games_started, r.complete_games, r.shutouts, r.innings_pitched, r.hits_allowed, r.home_runs_allowed, r.walks_allowed, r.strikeouts_pitched, r.runs_allowed, r.earned_runs, era, r.wins, r.losses, r.saves, r.holds, whip]
                    )

            elif category == "Advanced":
                headers = ["名前", "チーム", "Type", "投球回", "K/9", "BB/9", "K/BB", "HR/9", "AVG", "WHIP", "FIP", "xFIP", "K%", "BB%", "LOB%", "WAR"]
                widths = [140, 60, 40, 55, 50, 50, 50, 50, 55, 50, 50, 50, 50, 50, 50, 50]
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if p.pitch_type else "投"
                    avg_allowed = r.hits_allowed / (r.hits_allowed + r.strikeouts_pitched + r.ground_outs + r.fly_outs) if (r.hits_allowed + r.strikeouts_pitched) > 0 else 0.0 # 簡易
                    return (
                        [p.name, t, ptype, f"{r.innings_pitched:.1f}", f"{r.k_per_9:.2f}", f"{r.bb_per_9:.2f}", f"{r.k_bb_ratio:.2f}", f"{r.hr_per_9:.2f}", f".{int(avg_allowed*1000):03d}", f"{r.whip:.2f}", f"{r.fip:.2f}", f"{r.xfip:.2f}", f"{r.k_rate_pitched*100:.1f}%", f"{r.bb_rate_pitched*100:.1f}%", f"{r.lob_rate*100:.1f}%", f"{r.war:.1f}"],
                        [p.name, t, "P", r.innings_pitched, r.k_per_9, r.bb_per_9, r.k_bb_ratio, r.hr_per_9, avg_allowed, r.whip, r.fip, r.xfip, r.k_rate_pitched, r.bb_rate_pitched, r.lob_rate, r.war]
                    )

            elif category == "BattedBall":
                headers = ["名前", "チーム", "Type", "GB%", "FB%", "LD%", "IFFB%", "HR/FB", "Hard%", "Mid%", "Soft%"]
                widths = [140, 60, 40, 50, 50, 50, 50, 50, 50, 50, 50]
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if p.pitch_type else "投"
                    return (
                        [p.name, t, ptype, f"{r.gb_pct*100:.1f}%", f"{r.fb_pct*100:.1f}%", f"{r.ld_pct*100:.1f}%", f"{r.iffb_pct*100:.1f}%", f"{r.hr_fb*100:.1f}%", f"{r.hard_pct*100:.1f}%", f"{r.mid_pct*100:.1f}%", f"{r.soft_pct*100:.1f}%"],
                        [p.name, t, "P", r.gb_pct, r.fb_pct, r.ld_pct, r.iffb_pct, r.hr_fb, r.hard_pct, r.mid_pct, r.soft_pct]
                    )

            elif category == "PlateDiscipline":
                headers = ["名前", "チーム", "Type", "O-Swing%", "Z-Swing%", "Swing%", "O-Contact%", "Z-Contact%", "Contact%", "Whiff%", "SwStr%"]
                widths = [140, 60, 40, 65, 65, 60, 65, 65, 60, 60, 60]
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if p.pitch_type else "投"
                    return (
                        [p.name, t, ptype, f"{r.o_swing_pct*100:.1f}%", f"{r.z_swing_pct*100:.1f}%", f"{r.swing_pct*100:.1f}%", f"{r.o_contact_pct*100:.1f}%", f"{r.z_contact_pct*100:.1f}%", f"{r.contact_pct*100:.1f}%", f"{r.whiff_pct*100:.1f}%", f"{r.swstr_pct*100:.1f}%"],
                        [p.name, t, "P", r.o_swing_pct, r.z_swing_pct, r.swing_pct, r.o_contact_pct, r.z_contact_pct, r.contact_pct, r.whiff_pct, r.swstr_pct]
                    )

            elif category == "Value":
                headers = ["名前", "チーム", "Type", "投球回", "ERA", "FIP", "xFIP", "WAR"]
                widths = [140, 60, 40, 60, 50, 50, 50, 50]
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if p.pitch_type else "投"
                    return (
                        [p.name, t, ptype, f"{r.innings_pitched:.1f}", f"{r.era:.2f}", f"{r.fip:.2f}", f"{r.xfip:.2f}", f"{r.war:.1f}"],
                        [p.name, t, "P", r.innings_pitched, r.era, r.fip, r.xfip, r.war]
                    )
            
            # Pitchers: Fielding view is usually N/A, but we can default to Standard or simple fielding stats
            elif category == "Fielding":
                headers = ["名前", "チーム", "Type", "Inn", "RngR", "ErrR", "ARM", "DPR", "UZR", "UZR/1000"]
                widths = [140, 60, 40, 50, 50, 50, 50, 50, 60, 70]
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if p.pitch_type else "投"
                    inn = safe_get(r, "defensive_innings", 0.0)
                    rng = safe_get(r, "uzr_rngr", 0.0)
                    err = safe_get(r, "uzr_errr", 0.0)
                    arm = safe_get(r, "uzr_arm", 0.0)
                    dpr = safe_get(r, "uzr_dpr", 0.0)
                    uzr = safe_get(r, "uzr", 0.0)
                    u1000 = safe_get(r, "uzr_1000", 0.0)
                    return (
                        [p.name, t, ptype, f"{inn:.1f}", f"{rng:+.1f}", f"{err:+.1f}", f"{arm:+.1f}", f"{dpr:+.1f}", f"{uzr:+.1f}", f"{u1000:+.1f}"],
                        [p.name, t, "P", inn, rng, err, arm, dpr, uzr, u1000]
                    )

            else:
                return self._get_column_config("pitcher", "Standard")

        return headers, widths, extractor

    def set_data(self, data_list: list, mode: str = "batter", category: str = "Standard"):
        self.clear()
        
        headers, widths, extractor = self._get_column_config(mode, category)

        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        header = self.horizontalHeader()
        for i, width in enumerate(widths):
            header.resizeSection(i, width)
        
        self.setRowCount(len(data_list))

        for row, (player, team_name, record) in enumerate(data_list):
            display_vals, sort_vals = extractor(player, team_name, record)
            
            for col, (disp, sort) in enumerate(zip(display_vals, sort_vals)):
                item = SortableTableWidgetItem(str(disp))
                item.setData(Qt.UserRole, sort)
                if col == 0:
                    item.setData(Qt.UserRole + 1, player)
                
                if col < 3: item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else: item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)


class StatsPage(QWidget):
    """
    Redesigned Stats Page with Sabermetrics, Categories, and Horizontal Scrolling
    """
    player_detail_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.game_state = None
        self.current_team = None 
        self.current_league = "All"
        self.current_level = TeamLevel.FIRST
        self.current_category = "Standard" # Default category
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toolbar = self._create_toolbar()
        layout.addWidget(self.toolbar)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {self.theme.border}; border-radius: 8px; background-color: {self.theme.bg_card}; margin: 16px; }}
            QTabBar::tab {{ background-color: transparent; color: {self.theme.text_secondary}; padding: 10px 30px; font-weight: bold; font-size: 13px; }}
            QTabBar::tab:selected {{ color: {self.theme.primary}; border-bottom: 2px solid {self.theme.primary}; }}
            QTabBar::tab:hover {{ color: {self.theme.text_primary}; }}
        """)

        self.batter_table = StatsTable()
        self.tabs.addTab(self.batter_table, "野手成績") 
        self.batter_table.player_double_clicked.connect(self.player_detail_requested.emit)

        self.pitcher_table = StatsTable()
        self.tabs.addTab(self.pitcher_table, "投手成績")
        self.pitcher_table.player_double_clicked.connect(self.player_detail_requested.emit)

        # タブ切り替え時に更新
        self.tabs.currentChanged.connect(self._refresh_stats)

        layout.addWidget(self.tabs)

    def _create_toolbar(self) -> ToolbarPanel:
        toolbar = ToolbarPanel(); toolbar.setFixedHeight(50)
        
        # League Selector
        lbl_lg = QLabel("リーグ:"); lbl_lg.setStyleSheet(f"color: {self.theme.text_secondary}; margin-left: 16px;")
        toolbar.add_widget(lbl_lg)
        self.league_combo = QComboBox(); self.league_combo.setMinimumWidth(110); self.league_combo.addItems(["全リーグ", "North League", "South League"])
        self.league_combo.setStyleSheet(self._get_combo_style())
        self.league_combo.currentIndexChanged.connect(self._on_league_changed)
        toolbar.add_widget(self.league_combo)
        toolbar.add_separator()

        # Team Selector
        lbl_tm = QLabel("チーム:"); lbl_tm.setStyleSheet(f"color: {self.theme.text_secondary};")
        toolbar.add_widget(lbl_tm)
        self.team_combo = QComboBox(); self.team_combo.setMinimumWidth(160)
        self.team_combo.setStyleSheet(self._get_combo_style())
        self.team_combo.currentIndexChanged.connect(self._on_team_changed)
        toolbar.add_widget(self.team_combo)
        toolbar.add_separator()

        # Category Selector (New)
        lbl_cat = QLabel("表示:"); lbl_cat.setStyleSheet(f"color: {self.theme.text_secondary};")
        toolbar.add_widget(lbl_cat)
        self.category_combo = QComboBox(); self.category_combo.setMinimumWidth(130)
        self.category_combo.addItems(["Standard", "Advanced", "BattedBall", "PlateDiscipline", "Fielding", "Value"])
        self.category_combo.setStyleSheet(self._get_combo_style())
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        toolbar.add_widget(self.category_combo)
        toolbar.add_separator()

        # Level Toggle
        self.btn_group = QButtonGroup(self); self.btn_group.setExclusive(True)
        self.btn_first = self._create_toggle_btn("一軍", True)
        self.btn_second = self._create_toggle_btn("二軍")
        self.btn_third = self._create_toggle_btn("三軍")
        self.btn_group.addButton(self.btn_first, 1)
        self.btn_group.addButton(self.btn_second, 2)
        self.btn_group.addButton(self.btn_third, 3)
        self.btn_group.idClicked.connect(self._on_level_changed)
        toolbar.add_widget(self.btn_first); toolbar.add_widget(self.btn_second); toolbar.add_widget(self.btn_third)
        
        toolbar.add_stretch()
        return toolbar

    def _get_combo_style(self):
        return f"QComboBox {{ background-color: {self.theme.bg_input}; color: {self.theme.text_primary}; border: 1px solid {self.theme.border}; border-radius: 4px; padding: 4px 8px; }} QComboBox::drop-down {{ border: none; }} QComboBox QAbstractItemView {{ background-color: {self.theme.bg_card}; color: {self.theme.text_primary}; selection-background-color: {self.theme.primary}; }}"

    def _create_toggle_btn(self, text, checked=False):
        btn = QPushButton(text); btn.setCheckable(True); btn.setChecked(checked); btn.setFixedSize(70, 30); btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"QPushButton {{ background-color: {self.theme.bg_card}; color: {self.theme.text_primary}; border: 1px solid {self.theme.border}; border-radius: 4px; font-weight: bold; margin-right: 6px; }} QPushButton:checked {{ background-color: {self.theme.primary}; color: {self.theme.text_highlight}; border-color: {self.theme.primary}; }} QPushButton:hover {{ background-color: {self.theme.bg_card_hover}; }}")
        return btn

    def set_game_state(self, game_state):
        self.game_state = game_state
        if not game_state: return
        
        update_league_stats(game_state.teams)

        self.team_combo.blockSignals(True)
        self.team_combo.clear()
        self.team_combo.addItem("全チーム", None)
        for team in game_state.teams:
            name = team.name + (" (自チーム)" if game_state.player_team and team == game_state.player_team else "")
            self.team_combo.addItem(name, team)
        self.team_combo.setCurrentIndex(0)
        self.team_combo.blockSignals(False)
        self._refresh_stats()

    def _on_league_changed(self, index):
        if index == 0: self.current_league = "All"
        elif index == 1: self.current_league = "North League"
        elif index == 2: self.current_league = "South League"
        self._refresh_stats()

    def _on_team_changed(self, index):
        self.current_team = self.team_combo.itemData(index)
        self._refresh_stats()

    def _on_category_changed(self, index):
        self.current_category = self.category_combo.currentText()
        self._refresh_stats()

    def _on_level_changed(self, btn_id):
        if btn_id == 1: self.current_level = TeamLevel.FIRST
        elif btn_id == 2: self.current_level = TeamLevel.SECOND
        elif btn_id == 3: self.current_level = TeamLevel.THIRD
        self._refresh_stats()

    def _refresh_stats(self):
        if not self.game_state: return
        level = self.current_level
        batters_data = []
        pitchers_data = []
        
        target_teams = [self.current_team] if self.current_team else (self.game_state.teams if self.current_league == "All" else [t for t in self.game_state.teams if t.league.value == self.current_league])

        for team in target_teams:
            for player in team.players:
                record = player.get_record_by_level(level)
                if player.position.value == "投手":
                    if record.games_pitched > 0: pitchers_data.append((player, team.name, record))
                else:
                    if record.games > 0: batters_data.append((player, team.name, record))

        # 現在のアクティブなタブだけ更新する（パフォーマンス考慮）
        current_tab_idx = self.tabs.currentIndex()
        if current_tab_idx == 0:
            self.batter_table.set_data(batters_data, mode="batter", category=self.current_category)
        else:
            self.pitcher_table.set_data(pitchers_data, mode="pitcher", category=self.current_category)