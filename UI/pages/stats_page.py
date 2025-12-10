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
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QBrush, QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme
from UI.widgets.panels import ToolbarPanel
from UI.widgets.tables import SortableTableWidgetItem
from models import TeamLevel, PlayerRecord
from stats_records import update_league_stats

def safe_enum_val(obj):
    """Safely get value from Enum or return string representation"""
    return obj.value if hasattr(obj, "value") else str(obj)

def safe_fmt(val, fmt="{:.3f}"):
    """Safely format float value"""
    try:
        return fmt.format(float(val))
    except:
        return ".000"

def safe_int_fmt(val):
    """Safely format avg-like float to .XXX string"""
    try:
        return f".{int(float(val)*1000):03d}"
    except:
        return ".000"

class StatsTable(QTableWidget):
    """
    Custom Table for displaying statistics with sorting & full-width layout
    """
    player_double_clicked = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        # ソート状態の記憶用
        self._current_sort_col = -1
        self._current_sort_order = Qt.DescendingOrder
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.theme.bg_card};
                border: none;
                gridline-color: {self.theme.border_muted};
                selection-background-color: {self.theme.primary};
                selection-color: #ffffff;
            }}
            QTableWidget::item {{
                padding: 8px 4px;
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
                background-color: {self.theme.bg_card_elevated};
                color: {self.theme.text_primary};
                font-weight: bold;
                font-size: 12px;
                padding: 10px 4px;
                border: none;
                border-bottom: 2px solid {self.theme.primary};
                border-right: 1px solid {self.theme.border_muted};
            }}
            QScrollBar:vertical {{
                background: {self.theme.bg_dark};
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme.text_muted};
                border-radius: 6px;
            }}
        """)

        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(40)
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
        
        # 画面いっぱいに広げる設定
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setStretchLastSection(True)
        
        self.cellDoubleClicked.connect(self._on_double_click)

    def _on_header_clicked(self, logicalIndex):
        header = self.horizontalHeader()
        
        # ソート順の決定ロジック
        if self._current_sort_col != logicalIndex:
            # 別の列をクリックした場合 -> 降順(大きい順)からスタート
            new_order = Qt.DescendingOrder
        else:
            # 同じ列をクリックした場合 -> 昇順・降順をトグル
            if self._current_sort_order == Qt.DescendingOrder:
                new_order = Qt.AscendingOrder
            else:
                new_order = Qt.DescendingOrder

        # 状態を保存
        self._current_sort_col = logicalIndex
        self._current_sort_order = new_order

        # ソート実行
        self.sortItems(logicalIndex, new_order)
        header.setSortIndicator(logicalIndex, new_order)

    def restore_sort_state(self):
        """保存されたソート状態を再適用する"""
        if self._current_sort_col >= 0:
            self.horizontalHeader().setSortIndicator(self._current_sort_col, self._current_sort_order)
            self.sortItems(self._current_sort_col, self._current_sort_order)

    def _on_double_click(self, row, col):
        item = self.item(row, 0)
        if item:
            player = item.data(Qt.UserRole + 1)
            if player:
                self.player_double_clicked.emit(player)

    def _get_column_config(self, mode: str, category: str):
        
        def safe_get(obj, attr, default=0.0):
            return getattr(obj, attr, default)

        if mode == "batter":
            if category == "Standard":
                headers = ["名前", "チーム", "Pos", "試合", "打席", "打数", "安打", "二塁", "三塁", "本塁", "得点", "打点", "盗塁", "盗刺", "四球", "三振", "打率", "出塁", "長打", "OPS"]
                widths = [100] * len(headers) 
                def extractor(p, t, r):
                    avg = r.batting_average; ops = r.ops
                    pos_str = safe_enum_val(p.position)
                    return (
                        [p.name, t, pos_str, r.games, r.plate_appearances, r.at_bats, r.hits, r.doubles, r.triples, r.home_runs, r.runs, r.rbis, r.stolen_bases, r.caught_stealing, r.walks, r.strikeouts, safe_int_fmt(avg), safe_int_fmt(r.obp), safe_int_fmt(r.slg), safe_int_fmt(ops)],
                        [p.name, t, pos_str, r.games, r.plate_appearances, r.at_bats, r.hits, r.doubles, r.triples, r.home_runs, r.runs, r.rbis, r.stolen_bases, r.caught_stealing, r.walks, r.strikeouts, avg, r.obp, r.slg, ops]
                    )
            elif category == "Advanced":
                headers = ["名前", "チーム", "Pos", "打席", "BB%", "K%", "BB/K", "ISO", "BABIP", "wOBA", "wRC", "wRC+", "wRAA", "WAR"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    bb_k = r.walks / r.strikeouts if r.strikeouts > 0 else r.walks
                    w_raa = (r.woba - 0.320) / 1.2 * r.plate_appearances
                    pos_str = safe_enum_val(p.position)
                    return (
                        [p.name, t, pos_str, r.plate_appearances, f"{r.bb_pct*100:.1f}%", f"{r.k_pct*100:.1f}%", f"{bb_k:.2f}", f"{r.iso:.3f}", f"{r.babip:.3f}", safe_int_fmt(r.woba), f"{r.wrc:.1f}", int(r.wrc_plus), f"{w_raa:.1f}", f"{r.war:.1f}"],
                        [p.name, t, pos_str, r.plate_appearances, r.bb_pct, r.k_pct, bb_k, r.iso, r.babip, r.woba, r.wrc, r.wrc_plus, w_raa, r.war]
                    )
            elif category == "BattedBall":
                headers = ["名前", "チーム", "Pos", "GB%", "FB%", "LD%", "IFFB%", "HR/FB", "Pull%", "Cent%", "Oppo%", "Hard%", "Mid%", "Soft%"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    pos_str = safe_enum_val(p.position)
                    return (
                        [p.name, t, pos_str, f"{r.gb_pct*100:.1f}%", f"{r.fb_pct*100:.1f}%", f"{r.ld_pct*100:.1f}%", f"{r.iffb_pct*100:.1f}%", f"{r.hr_fb*100:.1f}%", f"{r.pull_pct*100:.1f}%", f"{r.cent_pct*100:.1f}%", f"{r.oppo_pct*100:.1f}%", f"{r.hard_pct*100:.1f}%", f"{r.mid_pct*100:.1f}%", f"{r.soft_pct*100:.1f}%"],
                        [p.name, t, pos_str, r.gb_pct, r.fb_pct, r.ld_pct, r.iffb_pct, r.hr_fb, r.pull_pct, r.cent_pct, r.oppo_pct, r.hard_pct, r.mid_pct, r.soft_pct]
                    )
            elif category == "PlateDiscipline":
                headers = ["名前", "チーム", "Pos", "O-Swing%", "Z-Swing%", "Swing%", "O-Contact%", "Z-Contact%", "Contact%", "Whiff%", "SwStr%"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    pos_str = safe_enum_val(p.position)
                    return (
                        [p.name, t, pos_str, f"{r.o_swing_pct*100:.1f}%", f"{r.z_swing_pct*100:.1f}%", f"{r.swing_pct*100:.1f}%", f"{r.o_contact_pct*100:.1f}%", f"{r.z_contact_pct*100:.1f}%", f"{r.contact_pct*100:.1f}%", f"{r.whiff_pct*100:.1f}%", f"{r.swstr_pct*100:.1f}%"],
                        [p.name, t, pos_str, r.o_swing_pct, r.z_swing_pct, r.swing_pct, r.o_contact_pct, r.z_contact_pct, r.contact_pct, r.whiff_pct, r.swstr_pct]
                    )
            elif category == "Fielding":
                headers = ["名前", "チーム", "Pos", "Inn", "RngR", "ErrR", "ARM", "DPR", "rSB", "rBlk", "UZR", "UZR/1000", "UZR/1200"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
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
                    pos_str = safe_enum_val(p.position)
                    return (
                        [p.name, t, pos_str, f"{inn:.1f}", f"{rng:+.1f}", f"{err:+.1f}", f"{arm:+.1f}", f"{dpr:+.1f}", f"{rsb:+.1f}", f"{blk:+.1f}", f"{uzr:+.1f}", f"{u1000:+.1f}", f"{u1200:+.1f}"],
                        [p.name, t, pos_str, inn, rng, err, arm, dpr, rsb, blk, uzr, u1000, u1200]
                    )
            elif category == "Value":
                headers = ["名前", "チーム", "Pos", "WAR", "wRC+", "wOBA", "UZR", "wSB", "UBR", "ISO"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    pos_str = safe_enum_val(p.position)
                    return (
                        [p.name, t, pos_str, f"{r.war:.1f}", int(r.wrc_plus), safe_int_fmt(r.woba), f"{safe_get(r, 'uzr', 0.0):.1f}", f"{r.wsb:.1f}", f"{r.ubr:.1f}", f"{r.iso:.3f}"],
                        [p.name, t, pos_str, r.war, r.wrc_plus, r.woba, safe_get(r, 'uzr', 0.0), r.wsb, r.ubr, r.iso]
                    )
            else:
                 return self._get_column_config("batter", "Standard")

        else: # Pitcher
            if category == "Standard":
                headers = ["名前", "チーム", "Type", "試合", "先発", "完投", "完封", "投球回", "被安", "被本", "与四", "奪三", "失点", "自責", "防御率", "勝利", "敗戦", "S", "H", "WHIP"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if hasattr(p.pitch_type, "value") else "投"
                    era = r.era if r.innings_pitched > 0 else 99.99
                    whip = r.whip if r.innings_pitched > 0 else 99.99
                    return (
                        [p.name, t, ptype, r.games_pitched, r.games_started, r.complete_games, r.shutouts, f"{r.innings_pitched:.1f}", r.hits_allowed, r.home_runs_allowed, r.walks_allowed, r.strikeouts_pitched, r.runs_allowed, r.earned_runs, f"{r.era:.2f}", r.wins, r.losses, r.saves, r.holds, f"{r.whip:.2f}"],
                        [p.name, t, "P", r.games_pitched, r.games_started, r.complete_games, r.shutouts, r.innings_pitched, r.hits_allowed, r.home_runs_allowed, r.walks_allowed, r.strikeouts_pitched, r.runs_allowed, r.earned_runs, era, r.wins, r.losses, r.saves, r.holds, whip]
                    )
            elif category == "Advanced":
                headers = ["名前", "チーム", "Type", "投球回", "K/9", "BB/9", "K/BB", "HR/9", "AVG", "WHIP", "FIP", "xFIP", "K%", "BB%", "LOB%", "WAR"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if hasattr(p.pitch_type, "value") else "投"
                    avg_allowed = r.hits_allowed / (r.hits_allowed + r.strikeouts_pitched + r.ground_outs + r.fly_outs) if (r.hits_allowed + r.strikeouts_pitched) > 0 else 0.0
                    return (
                        [p.name, t, ptype, f"{r.innings_pitched:.1f}", f"{r.k_per_9:.2f}", f"{r.bb_per_9:.2f}", f"{r.k_bb_ratio:.2f}", f"{r.hr_per_9:.2f}", safe_int_fmt(avg_allowed), f"{r.whip:.2f}", f"{r.fip:.2f}", f"{r.xfip:.2f}", f"{r.k_rate_pitched*100:.1f}%", f"{r.bb_rate_pitched*100:.1f}%", f"{r.lob_rate*100:.1f}%", f"{r.war:.1f}"],
                        [p.name, t, "P", r.innings_pitched, r.k_per_9, r.bb_per_9, r.k_bb_ratio, r.hr_per_9, avg_allowed, r.whip, r.fip, r.xfip, r.k_rate_pitched, r.bb_rate_pitched, r.lob_rate, r.war]
                    )
            elif category == "BattedBall":
                headers = ["名前", "チーム", "Type", "GB%", "FB%", "LD%", "IFFB%", "HR/FB", "Hard%", "Mid%", "Soft%"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if hasattr(p.pitch_type, "value") else "投"
                    return (
                        [p.name, t, ptype, f"{r.gb_pct*100:.1f}%", f"{r.fb_pct*100:.1f}%", f"{r.ld_pct*100:.1f}%", f"{r.iffb_pct*100:.1f}%", f"{r.hr_fb*100:.1f}%", f"{r.hard_pct*100:.1f}%", f"{r.mid_pct*100:.1f}%", f"{r.soft_pct*100:.1f}%"],
                        [p.name, t, "P", r.gb_pct, r.fb_pct, r.ld_pct, r.iffb_pct, r.hr_fb, r.hard_pct, r.mid_pct, r.soft_pct]
                    )
            elif category == "PlateDiscipline":
                headers = ["名前", "チーム", "Type", "O-Swing%", "Z-Swing%", "Swing%", "O-Contact%", "Z-Contact%", "Contact%", "Whiff%", "SwStr%"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if hasattr(p.pitch_type, "value") else "投"
                    return (
                        [p.name, t, ptype, f"{r.o_swing_pct*100:.1f}%", f"{r.z_swing_pct*100:.1f}%", f"{r.swing_pct*100:.1f}%", f"{r.o_contact_pct*100:.1f}%", f"{r.z_contact_pct*100:.1f}%", f"{r.contact_pct*100:.1f}%", f"{r.whiff_pct*100:.1f}%", f"{r.swstr_pct*100:.1f}%"],
                        [p.name, t, "P", r.o_swing_pct, r.z_swing_pct, r.swing_pct, r.o_contact_pct, r.z_contact_pct, r.contact_pct, r.whiff_pct, r.swstr_pct]
                    )
            elif category == "Value":
                headers = ["名前", "チーム", "Type", "投球回", "ERA", "FIP", "xFIP", "WAR"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if hasattr(p.pitch_type, "value") else "投"
                    return (
                        [p.name, t, ptype, f"{r.innings_pitched:.1f}", f"{r.era:.2f}", f"{r.fip:.2f}", f"{r.xfip:.2f}", f"{r.war:.1f}"],
                        [p.name, t, "P", r.innings_pitched, r.era, r.fip, r.xfip, r.war]
                    )
            elif category == "Fielding":
                headers = ["名前", "チーム", "Type", "Inn", "RngR", "ErrR", "ARM", "DPR", "UZR", "UZR/1000"]
                widths = [100] * len(headers)
                def extractor(p, t, r):
                    ptype = p.pitch_type.value[:2] if hasattr(p.pitch_type, "value") else "投"
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
        self.setSortingEnabled(False)
        self.clear()
        
        headers, widths, extractor = self._get_column_config(mode, category)

        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.setRowCount(len(data_list))

        for row, (player, team_name, record) in enumerate(data_list):
            try:
                display_vals, sort_vals = extractor(player, team_name, record)
                
                for col, (disp, sort) in enumerate(zip(display_vals, sort_vals)):
                    item = SortableTableWidgetItem(str(disp))
                    item.setData(Qt.UserRole, sort) 
                    
                    if col == 0:
                        item.setData(Qt.UserRole + 1, player)
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    elif col == 1 or col == 2:
                        item.setTextAlignment(Qt.AlignCenter)
                    else: 
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    self.setItem(row, col, item)
            except Exception as e:
                print(f"Stats Table Error on row {row}: {e}")
                self.setItem(row, 0, SortableTableWidgetItem("Error"))
                continue

        self.restore_sort_state()


class StatsPage(QWidget):
    """
    Redesigned Stats Page with Persistence and Full Screen Layout
    """
    player_detail_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.game_state = None
        
        self.current_team = None 
        self.current_league = "All"
        self.current_level = TeamLevel.FIRST
        self.current_category = "Standard"
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.toolbar = self._create_toolbar()
        layout.addWidget(self.toolbar)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ 
                border: 1px solid {self.theme.border}; 
                border-radius: 8px; 
                background-color: {self.theme.bg_card}; 
            }}
            QTabBar::tab {{ 
                background-color: transparent; 
                color: {self.theme.text_secondary}; 
                padding: 10px 20px; 
                font-weight: bold; 
                font-size: 14px; 
                min-width: 120px;
            }}
            QTabBar::tab:selected {{ 
                color: {self.theme.primary}; 
                border-bottom: 3px solid {self.theme.primary}; 
            }}
            QTabBar::tab:hover {{ 
                color: {self.theme.text_primary}; 
                background-color: {self.theme.bg_hover};
            }}
        """)

        self.batter_table = StatsTable()
        self.tabs.addTab(self.batter_table, "野手成績") 
        self.batter_table.player_double_clicked.connect(self.player_detail_requested.emit)

        self.pitcher_table = StatsTable()
        self.tabs.addTab(self.pitcher_table, "投手成績")
        self.pitcher_table.player_double_clicked.connect(self.player_detail_requested.emit)

        self.tabs.currentChanged.connect(self._refresh_stats)

        layout.addWidget(self.tabs)

    def showEvent(self, event):
        """タブが表示されたときにデータを更新する（レイアウト確定後の描画保証）"""
        super().showEvent(event)
        # 画面表示時にリフレッシュすることで、Stretchレイアウト計算を正しく行わせる
        QTimer.singleShot(0, self._refresh_stats)

    def _create_toolbar(self) -> ToolbarPanel:
        toolbar = ToolbarPanel(); toolbar.setFixedHeight(60)
        toolbar.setStyleSheet(f"background-color: {self.theme.bg_card}; border-radius: 8px; padding: 0 10px;")
        
        lbl_lg = QLabel("リーグ:"); lbl_lg.setStyleSheet(f"color: {self.theme.text_secondary}; font-weight:bold;")
        toolbar.add_widget(lbl_lg)
        self.league_combo = QComboBox(); self.league_combo.setMinimumWidth(120); self.league_combo.addItems(["全リーグ", "North League", "South League"])
        self.league_combo.setStyleSheet(self._get_combo_style())
        self.league_combo.currentIndexChanged.connect(self._on_league_changed)
        toolbar.add_widget(self.league_combo)
        
        toolbar.add_spacing(20)

        lbl_tm = QLabel("チーム:"); lbl_tm.setStyleSheet(f"color: {self.theme.text_secondary}; font-weight:bold;")
        toolbar.add_widget(lbl_tm)
        self.team_combo = QComboBox(); self.team_combo.setMinimumWidth(180)
        self.team_combo.setStyleSheet(self._get_combo_style())
        self.team_combo.currentIndexChanged.connect(self._on_team_changed)
        toolbar.add_widget(self.team_combo)
        
        toolbar.add_spacing(20)

        lbl_cat = QLabel("表示項目:"); lbl_cat.setStyleSheet(f"color: {self.theme.text_secondary}; font-weight:bold;")
        toolbar.add_widget(lbl_cat)
        self.category_combo = QComboBox(); self.category_combo.setMinimumWidth(150)
        self.category_combo.addItems(["Standard", "Advanced", "BattedBall", "PlateDiscipline", "Fielding", "Value"])
        self.category_combo.setStyleSheet(self._get_combo_style())
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        toolbar.add_widget(self.category_combo)
        
        toolbar.add_stretch()

        self.btn_group = QButtonGroup(self); self.btn_group.setExclusive(True)
        self.btn_first = self._create_toggle_btn("一軍", True)
        self.btn_second = self._create_toggle_btn("二軍")
        self.btn_third = self._create_toggle_btn("三軍")
        self.btn_group.addButton(self.btn_first, 1)
        self.btn_group.addButton(self.btn_second, 2)
        self.btn_group.addButton(self.btn_third, 3)
        self.btn_group.idClicked.connect(self._on_level_changed)
        toolbar.add_widget(self.btn_first); toolbar.add_widget(self.btn_second); toolbar.add_widget(self.btn_third)
        
        return toolbar

    def _get_combo_style(self):
        return f"""
            QComboBox {{ 
                background-color: {self.theme.bg_input}; 
                color: {self.theme.text_primary}; 
                border: 1px solid {self.theme.border}; 
                border-radius: 4px; 
                padding: 6px 12px; 
            }} 
            QComboBox::drop-down {{ 
                border: none; 
            }} 
            QComboBox::down-arrow {{ 
                image: none; 
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.theme.text_secondary};
                width: 0;
                height: 0;
                margin-right: 10px; 
                margin-top: 2px;
            }}
            QComboBox QAbstractItemView {{ 
                background-color: {self.theme.bg_card}; 
                color: {self.theme.text_primary}; 
                selection-background-color: {self.theme.primary}; 
            }}
        """

    def _create_toggle_btn(self, text, checked=False):
        btn = QPushButton(text); btn.setCheckable(True); btn.setChecked(checked); btn.setFixedSize(80, 32); btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {self.theme.bg_input}; 
                color: {self.theme.text_secondary}; 
                border: 1px solid {self.theme.border}; 
                border-radius: 4px; 
                font-weight: bold; 
                margin-left: 4px; 
            }} 
            QPushButton:checked {{ 
                background-color: #ffffff; 
                color: #111111; 
                border-color: #ffffff; 
            }} 
            QPushButton:hover {{ 
                background-color: {self.theme.bg_hover}; 
            }}
        """)
        return btn

    def set_game_state(self, game_state):
        self.game_state = game_state
        if not game_state: return
        
        try:
            update_league_stats(game_state.teams)
        except Exception as e:
            print(f"Stats Update Error: {e}")

        current_team_data = self.current_team
        self.team_combo.blockSignals(True)
        self.team_combo.clear()
        self.team_combo.addItem("全チーム", None)
        
        index_to_set = 0
        for i, team in enumerate(game_state.teams):
            name = team.name + (" (自チーム)" if game_state.player_team and team == game_state.player_team else "")
            self.team_combo.addItem(name, team)
            if current_team_data and team.name == current_team_data.name:
                index_to_set = i + 1
        
        self.team_combo.setCurrentIndex(index_to_set)
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
        
        update_league_stats(self.game_state.teams)
        
        level = self.current_level
        batters_data = []
        pitchers_data = []
        
        target_teams = [self.current_team] if self.current_team else (self.game_state.teams if self.current_league == "All" else [t for t in self.game_state.teams if t.league.value == self.current_league])

        for team in target_teams:
            for player in team.players:
                record = player.get_record_by_level(level)
                
                # 修正: 試合数が0の選手はリストに表示しない
                if player.position.value == "投手":
                    if record.games_pitched > 0:
                        pitchers_data.append((player, team.name, record))
                else:
                    if record.games > 0:
                        batters_data.append((player, team.name, record))

        current_tab_idx = self.tabs.currentIndex()
        if current_tab_idx == 0:
            self.batter_table.set_data(batters_data, mode="batter", category=self.current_category)
        else:
            self.pitcher_table.set_data(pitchers_data, mode="pitcher", category=self.current_category)