# -*- coding: utf-8 -*-
"""
Baseball Team Architect 2027 - Farm Swap Page
Manage roster moves between Farm (2nd Team) and Third Team (3rd Team)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView, QFrame, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont, QIcon

import sys
import os

# パス設定（他のファイルと同様）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme
from UI.widgets.panels import ToolbarPanel
from UI.widgets.tables import SortableTableWidgetItem, RatingDelegate
from models import TeamLevel, Position

# ユーザーロール定義
ROLE_PLAYER_IDX = Qt.UserRole + 1
ROLE_ORIGINAL_LEVEL = Qt.UserRole + 2

class FarmSwapPage(QWidget):
    """二軍・三軍 入れ替え管理ページ"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.game_state = None
        self.current_team = None
        
        # フィルタ状態 (0: 投手, 1: 野手)
        self.current_filter_mode = "pitcher" 
        
        self.rating_delegate = RatingDelegate(self)
        
        self._setup_ui()

    def _setup_ui(self):
        """UIレイアウトの作成"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. ツールバー（チーム名表示・フィルタ切り替え）
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # 2. メインコンテンツ（左右分割）
        content_frame = QFrame()
        content_frame.setStyleSheet(f"background-color: {self.theme.bg_dark};")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        # 左側：二軍リスト
        self.farm_panel = self._create_roster_panel("二軍", TeamLevel.SECOND)
        content_layout.addWidget(self.farm_panel, 1)

        # 中央：操作ボタンエリア
        btn_layout = QVBoxLayout()
        btn_layout.addStretch()
        
        self.to_third_btn = self._create_move_button(">>", "三軍へ移動")
        self.to_third_btn.clicked.connect(self._move_selected_to_third)
        btn_layout.addWidget(self.to_third_btn)
        
        btn_layout.addSpacing(16)
        
        self.to_farm_btn = self._create_move_button("<<", "二軍へ移動")
        self.to_farm_btn.clicked.connect(self._move_selected_to_farm)
        btn_layout.addWidget(self.to_farm_btn)
        
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)

        # 右側：三軍リスト
        self.third_panel = self._create_roster_panel("三軍", TeamLevel.THIRD)
        content_layout.addWidget(self.third_panel, 1)

        layout.addWidget(content_frame)

    def _create_toolbar(self) -> ToolbarPanel:
        """ツールバーの作成"""
        toolbar = ToolbarPanel()
        toolbar.setFixedHeight(50)

        # チーム名表示
        self.team_label = QLabel("チーム名")
        self.team_label.setStyleSheet(f"color: {self.theme.text_primary}; font-weight: bold; font-size: 16px; margin-left: 12px;")
        toolbar.add_widget(self.team_label)

        toolbar.add_stretch()

        # フィルタボタン
        self.filter_pitcher_btn = QPushButton("投手")
        self.filter_pitcher_btn.setCheckable(True)
        self.filter_pitcher_btn.setChecked(True)
        self.filter_pitcher_btn.clicked.connect(lambda: self._set_filter("pitcher"))
        self._apply_filter_btn_style(self.filter_pitcher_btn)
        toolbar.add_widget(self.filter_pitcher_btn)

        self.filter_fielder_btn = QPushButton("野手")
        self.filter_fielder_btn.setCheckable(True)
        self.filter_fielder_btn.clicked.connect(lambda: self._set_filter("fielder"))
        self._apply_filter_btn_style(self.filter_fielder_btn)
        toolbar.add_widget(self.filter_fielder_btn)

        return toolbar

    def _apply_filter_btn_style(self, btn):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedWidth(80)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.bg_card};
                color: {self.theme.text_secondary};
                border: 1px solid {self.theme.border};
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }}
            QPushButton:checked {{
                background-color: {self.theme.primary};
                color: {self.theme.text_highlight};
                border-color: {self.theme.primary};
            }}
            QPushButton:hover {{
                border-color: {self.theme.primary};
            }}
        """)

    def _create_move_button(self, text, tooltip):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(50, 50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.bg_card};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme.primary};
                color: {self.theme.text_highlight};
                border-color: {self.theme.primary};
            }}
            QPushButton:pressed {{
                background-color: {self.theme.primary_hover};
            }}
        """)
        return btn

    def _create_roster_panel(self, title, level):
        """各軍のリストパネルを作成"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # ヘッダー (タイトル + 人数)
        header_layout = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {self.theme.text_primary}; font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_lbl)
        
        count_lbl = QLabel("0人")
        count_lbl.setStyleSheet(f"color: {self.theme.text_secondary}; font-size: 13px;")
        header_layout.addWidget(count_lbl)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        # テーブル作成
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table.horizontalHeader().setStretchLastSection(True)
        table.setShowGrid(False)
        
        # スタイル適用 (OrderPageと同様のスタイル)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.theme.bg_card};
                border: 1px solid {self.theme.border};
                gridline-color: {self.theme.border_muted};
                selection-background-color: {self.theme.primary}40; /* 半透明のプライマリ色 */
                selection-color: {self.theme.text_primary};
                outline: none;
            }}
            QTableWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {self.theme.border_muted};
            }}
            QHeaderView::section {{
                background-color: {self.theme.bg_input};
                color: {self.theme.text_secondary};
                border: none;
                border-bottom: 1px solid {self.theme.border};
                padding: 4px;
                font-weight: bold;
            }}
        """)

        # ダブルクリックで移動
        if level == TeamLevel.SECOND:
            table.itemDoubleClicked.connect(self._move_selected_to_third)
            self.farm_table = table
            self.farm_count_lbl = count_lbl
        else:
            table.itemDoubleClicked.connect(self._move_selected_to_farm)
            self.third_table = table
            self.third_count_lbl = count_lbl

        layout.addWidget(table)
        return container

    def _setup_table_columns(self, table, is_pitcher):
        """テーブルの列定義を設定"""
        table.clear()
        
        if is_pitcher:
            headers = ["守", "調", "選手名", "年齢", "球速", "コ", "ス", "変", "総合"]
            widths = [40, 30, 140, 40, 50, 35, 35, 35, 45]
            delegate_cols = [5, 6, 7]
        else:
            headers = ["守", "調", "選手名", "年齢", "ミ", "パ", "走", "守", "総合"]
            widths = [40, 30, 140, 40, 35, 35, 35, 35, 45]
            delegate_cols = [4, 5, 6, 7]

        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        for i, w in enumerate(widths):
            table.setColumnWidth(i, w)
            
        # レーティング表示用のデリゲート適用
        for col in delegate_cols:
            table.setItemDelegateForColumn(col, self.rating_delegate)

    def set_game_state(self, game_state):
        """ゲーム状態のセット"""
        self.game_state = game_state
        if not game_state or not game_state.player_team:
            return

        self.current_team = game_state.player_team
        self.team_label.setText(self.current_team.name)
        
        self._refresh_tables()

    def _set_filter(self, mode):
        """投手・野手フィルタの切り替え"""
        if self.current_filter_mode == mode:
            return
            
        self.current_filter_mode = mode
        
        # ボタン状態更新
        self.filter_pitcher_btn.setChecked(mode == "pitcher")
        self.filter_fielder_btn.setChecked(mode == "fielder")
        
        self._refresh_tables()

    def _refresh_tables(self):
        """テーブルの内容を更新"""
        if not self.current_team:
            return

        is_pitcher = (self.current_filter_mode == "pitcher")
        
        # 列定義の更新
        self._setup_table_columns(self.farm_table, is_pitcher)
        self._setup_table_columns(self.third_table, is_pitcher)

        # 選手データの取得と振り分け
        farm_players = []
        third_players = []
        
        # チームリストから走査
        for i, p in enumerate(self.current_team.players):
            # ポジションフィルタ
            p_is_pitcher = (p.position.value == "投手")
            if p_is_pitcher != is_pitcher:
                continue

            # 所属軍判定
            if i in self.current_team.farm_roster:
                farm_players.append((i, p))
            elif i in self.current_team.third_roster:
                third_players.append((i, p))

        # ソート（背番号順など）
        farm_players.sort(key=lambda x: x[1].uniform_number)
        third_players.sort(key=lambda x: x[1].uniform_number)

        # テーブルへの入力
        self._fill_table(self.farm_table, farm_players, is_pitcher)
        self._fill_table(self.third_table, third_players, is_pitcher)

        # 人数表示更新
        farm_limit = getattr(self.current_team, 'FARM_ROSTER_LIMIT', 40)
        third_limit = getattr(self.current_team, 'THIRD_ROSTER_LIMIT', 30)
        
        farm_total = len(self.current_team.farm_roster)
        third_total = len(self.current_team.third_roster)
        
        self.farm_count_lbl.setText(f"{farm_total}/{farm_limit}人")
        self.third_count_lbl.setText(f"{third_total}人")
        
        # 色分け (制限を超えていたら赤くする)
        if farm_total > farm_limit:
             self.farm_count_lbl.setStyleSheet(f"color: {self.theme.danger}; font-weight: bold;")
        else:
             self.farm_count_lbl.setStyleSheet(f"color: {self.theme.text_secondary};")

    def _fill_table(self, table, players_data, is_pitcher):
        """テーブルに行データを追加"""
        table.setRowCount(len(players_data))
        
        for row, (p_idx, p) in enumerate(players_data):
            # 怪我状態などによる文字色
            text_color = None
            if p.is_injured:
                text_color = QColor("#95a5a6")
            
            # 0: 守備位置/タイプ
            pos_str = p.pitch_type.value[:2] if is_pitcher else p.position.value[0]
            item_pos = self._create_item(pos_str, text_color=text_color)
            if is_pitcher:
                 # 投手タイプに応じた色分け
                 badge_color = "#3498db" # Default blue
                 if pos_str == "先発": badge_color = "#e67e22" # Orange
                 elif pos_str == "抑え": badge_color = "#e74c3c" # Red
                 
                 item_pos.setBackground(QColor(badge_color))
                 item_pos.setForeground(Qt.white)
                 item_pos.setFont(QFont("Yu Gothic UI", 9, QFont.Bold))
            else:
                 # 野手ポジション色
                 from UI.pages.order_page import get_pos_color
                 color_code = get_pos_color(p.position.value[0])
                 item_pos.setBackground(QColor(color_code))
                 item_pos.setForeground(Qt.white)
                 item_pos.setFont(QFont("Yu Gothic UI", 9, QFont.Bold))
                 
            table.setItem(row, 0, item_pos)

            # 1: 調子
            table.setItem(row, 1, self._create_condition_item(p))

            # 2: 名前
            name_item = self._create_item(p.name, align=Qt.AlignLeft, text_color=text_color)
            # 怪我情報をツールチップに
            if p.is_injured:
                name_item.setToolTip(f"怪我: {p.injury_name} (残{p.injury_days}日)")
            table.setItem(row, 2, name_item)

            # 3: 年齢
            table.setItem(row, 3, self._create_item(str(p.age), text_color=text_color))

            # Stats
            if is_pitcher:
                kmh = p.stats.speed_to_kmh()
                table.setItem(row, 4, self._create_item(f"{kmh}km", text_color=text_color))
                table.setItem(row, 5, self._create_item(p.stats.control, is_rating=True))
                table.setItem(row, 6, self._create_item(p.stats.stamina, is_rating=True))
                table.setItem(row, 7, self._create_item(p.stats.stuff, is_rating=True))
            else:
                table.setItem(row, 4, self._create_item(p.stats.contact, is_rating=True))
                table.setItem(row, 5, self._create_item(p.stats.power, is_rating=True))
                table.setItem(row, 6, self._create_item(p.stats.speed, is_rating=True))
                table.setItem(row, 7, self._create_item(p.stats.fielding, is_rating=True))

            # 総合
            star_item = self._create_item(f"★{p.overall_rating}")
            star_item.setForeground(QColor("#FFD700"))
            star_item.setFont(QFont("Yu Gothic UI", 9, QFont.Bold))
            table.setItem(row, len(players_data[0]) if not is_pitcher else 8, star_item)

            # ユーザーデータとしてプレイヤーインデックスを保存
            for c in range(table.columnCount()):
                item = table.item(row, c)
                if item:
                    item.setData(ROLE_PLAYER_IDX, p_idx)

    def _create_item(self, text, align=Qt.AlignCenter, is_rating=False, text_color=None):
        item = SortableTableWidgetItem(str(text))
        item.setTextAlignment(align)
        if text_color:
            item.setForeground(text_color)
        
        if is_rating:
            try:
                val = int(text)
                item.setData(Qt.UserRole, val) # ソート用数値
                item.setData(Qt.DisplayRole, "") # 表示はデリゲートに任せるか、空にする
                # RatingDelegateを使う場合、数値データはUserRoleに入れておくと良いが、
                # ここでは簡易的に実装。RatingDelegateの仕様に合わせる。
                # 既存のRatingDelegateはDisplayRoleの値を参照して描画しているはずなので値を戻す
                item.setText(str(text)) 
            except:
                pass
        
        return item

    def _create_condition_item(self, player):
        item = SortableTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)
        
        if hasattr(player, 'is_injured') and player.is_injured:
            item.setText("傷")
            item.setForeground(QColor("#95a5a6"))
            item.setToolTip(f"全治まであと{player.injury_days}日")
            item.setData(Qt.UserRole, -1)
        else:
            cond = player.condition
            if cond >= 8:
                text, color, sort_val = "絶", "#e67e22", 5
            elif cond >= 6:
                text, color, sort_val = "好", "#f1c40f", 4
            elif cond >= 4:
                text, color, sort_val = "普", "#ecf0f1", 3
            elif cond >= 2:
                text, color, sort_val = "不", "#3498db", 2
            else:
                text, color, sort_val = "絶", "#9b59b6", 1
            
            item.setText(text)
            item.setForeground(QColor(color))
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            item.setData(Qt.UserRole, sort_val)
            
        return item

    def _move_selected_to_third(self):
        """二軍 -> 三軍 移動"""
        selected_items = self.farm_table.selectedItems()
        if not selected_items:
            return
            
        # 1行選択されているので、その行のPlayerIdxを取得
        p_idx = selected_items[0].data(ROLE_PLAYER_IDX)
        if p_idx is None: return

        # モデル操作
        self.current_team.move_to_third_roster(p_idx)
        
        # 画面更新
        self._refresh_tables()

    def _move_selected_to_farm(self):
        """三軍 -> 二軍 移動"""
        selected_items = self.third_table.selectedItems()
        if not selected_items:
            return
            
        p_idx = selected_items[0].data(ROLE_PLAYER_IDX)
        if p_idx is None: return

        # 制限チェック
        farm_limit = getattr(self.current_team, 'FARM_ROSTER_LIMIT', 40)
        if len(self.current_team.farm_roster) >= farm_limit:
            QMessageBox.warning(self, "登録上限", f"二軍の登録枠({farm_limit}人)がいっぱいです。")
            return

        # モデル操作
        self.current_team.move_to_farm_roster(p_idx)
        
        # 画面更新
        self._refresh_tables()