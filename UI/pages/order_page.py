# -*- coding: utf-8 -*-
"""
Baseball Team Architect 2027 - Order Page
Advanced Drag & Drop Order Management with DH support
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QComboBox, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QScrollArea, QSizePolicy, QCheckBox, QStyledItemDelegate,
    QStyle # Added QStyle for StateFlag
)
from PySide6.QtCore import Qt, Signal, QMimeData, QByteArray, QDataStream, QIODevice, QPoint, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QDrag, QPixmap, QPainter, QBrush, QPen

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from UI.theme import get_theme
from UI.widgets.panels import ToolbarPanel
# RatingDelegate を追加インポート
from UI.widgets.tables import SortableTableWidgetItem, RatingDelegate
from models import PlayerStats

# MIME Types
MIME_PLAYER_DATA = "application/x-pennant-player-data"
MIME_POS_SWAP = "application/x-pennant-pos-swap"

# Custom Role for Drag & Drop Player Index (to avoid conflict with SortRole)
ROLE_PLAYER_IDX = Qt.UserRole + 1

# Note: get_rank_color is no longer used for stats but kept if needed for other things
def get_rank_color(rank: str, theme) -> QColor:
    """Return color based on rank (S-G)"""
    if rank == "S": return QColor("#FFD700") # Gold
    if rank == "A": return QColor("#FF4500") # Orange Red
    if rank == "B": return QColor("#FFA500") # Orange
    if rank == "C": return QColor("#32CD32") # Lime Green
    if rank == "D": return QColor(theme.text_primary)
    if rank == "E": return QColor(theme.text_secondary)
    if rank == "F": return QColor(theme.text_muted)
    if rank == "G": return QColor("#808080") # Gray
    return QColor(theme.text_primary)

def get_pos_color(pos: str) -> str:
    """Return background color code for position badge"""
    if pos == "投": return "#3498db"
    if pos == "捕": return "#27ae60"
    if pos in ["一", "二", "三", "遊"]: return "#e67e22"
    if pos in ["左", "中", "右"]: return "#9b59b6"
    if pos == "DH": return "#e74c3c"
    return "#7f8c8d"

class DefenseDelegate(QStyledItemDelegate):
    """Custom delegate to draw Main Position Large and Sub Positions Small"""
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme

    def paint(self, painter, option, index):
        painter.save()
        
        # Data format expected: "MainPos|SubPos1 SubPos2..."
        # Handle None or non-string gracefully
        raw_data = index.data(Qt.DisplayRole)
        text = str(raw_data) if raw_data is not None else ""

        if "|" in text:
            parts = text.split("|", 1)
            main_pos = parts[0]
            sub_pos = parts[1] if len(parts) > 1 else ""
        else:
            main_pos, sub_pos = text, ""

        rect = option.rect
        
        # 1. Main Position (Large)
        if option.state & QStyle.StateFlag.State_Selected:
             painter.setPen(QColor(self.theme.text_primary)) 
        else:
             fg_color = index.model().data(index, Qt.ForegroundRole)
             if isinstance(fg_color, QBrush): 
                 fg_color = fg_color.color()
             
             painter.setPen(fg_color if fg_color else QColor(self.theme.text_primary))
             
        font = painter.font()
        font.setPointSize(12) 
        font.setBold(True)
        painter.setFont(font)
        
        fm = painter.fontMetrics()
        main_width = fm.horizontalAdvance(main_pos)
        
        # Align Left with some padding
        main_rect = rect.adjusted(4, 0, 0, 0)
        painter.drawText(main_rect, Qt.AlignLeft | Qt.AlignVCenter, main_pos)
        
        # 2. Sub Positions (Small)
        if sub_pos:
            font.setPointSize(9)
            font.setBold(False)
            painter.setFont(font)
            
            if option.state & QStyle.StateFlag.State_Selected:
                painter.setPen(QColor(self.theme.text_secondary))
            else:
                painter.setPen(QColor(self.theme.text_secondary))
            
            # Draw to the right of Main
            sub_rect = rect.adjusted(main_width + 10, 0, 0, 0)
            painter.drawText(sub_rect, Qt.AlignLeft | Qt.AlignVCenter, sub_pos)
        
        # 3. Draw Bottom Border manually
        painter.setPen(QPen(QColor(self.theme.border_muted), 1))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
            
        painter.restore()

class DraggableTableWidget(QTableWidget):
    """Enhanced TableWidget supporting Drag & Drop for Order Management"""
    
    items_changed = Signal()
    position_swapped = Signal(int, int)

    def __init__(self, mode="batter", parent=None):
        super().__init__(parent)
        self.mode = mode 
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setViewportMargins(0, 0, 0, 0)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setStretchLastSection(True)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.ClickFocus)
        self.theme = get_theme()
        
        self.setSortingEnabled(False)
        
        if "farm" in mode:
            header = self.horizontalHeader()
            header.setSectionsClickable(True)
            header.setSortIndicatorShown(True)
            header.sectionClicked.connect(self._on_header_clicked)

    def _on_header_clicked(self, logicalIndex):
        """ヘッダークリック時のカスタムソート（最初は降順）"""
        header_text = self.horizontalHeaderItem(logicalIndex).text()
        if header_text in ["選手名", "適正", "守備適正"]:
            return

        header = self.horizontalHeader()
        current_column = header.sortIndicatorSection()
        current_order = header.sortIndicatorOrder()
        
        if current_column != logicalIndex:
            new_order = Qt.DescendingOrder
        else:
            if current_order == Qt.DescendingOrder:
                new_order = Qt.AscendingOrder
            else:
                new_order = Qt.DescendingOrder

        self.sortItems(logicalIndex, new_order)
        header.setSortIndicator(logicalIndex, new_order)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item: return

        row = item.row()
        col = item.column()
        player_idx = item.data(ROLE_PLAYER_IDX)
        
        mime = QMimeData()
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        
        is_pos_swap = (self.mode == "lineup" and col == 1)
        
        if is_pos_swap:
            stream.writeInt32(row)
            mime.setData(MIME_POS_SWAP, data)
            text = item.text()
            pixmap = self._create_drag_pixmap(text, is_pos=True)
        else:
            if player_idx is None: return
            stream.writeInt32(player_idx)
            stream.writeInt32(row)
            mime.setData(MIME_PLAYER_DATA, data)
            
            if self.mode == "lineup":
                name_col = 2
            elif self.mode == "bench":
                name_col = 1
            elif self.mode == "farm_batter":
                name_col = 0
            else:
                name_col = 1
            
            name_item = self.item(row, name_col)
            name_text = name_item.text() if name_item else "Player"
            pixmap = self._create_drag_pixmap(name_text, is_pos=False)

        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        drag.exec(Qt.MoveAction)

    def _create_drag_pixmap(self, text, is_pos=False):
        width = 40 if is_pos else 200
        height = 40
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg_color = QColor("#222222")
        if is_pos:
            bg_color = QColor("#c0392b") 

        painter.setBrush(bg_color)
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawRect(0, 0, width, height)
        
        painter.setPen(Qt.white)
        font = QFont("Yu Gothic UI", 11, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        return pixmap

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(MIME_PLAYER_DATA) or event.mimeData().hasFormat(MIME_POS_SWAP):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(MIME_PLAYER_DATA) or event.mimeData().hasFormat(MIME_POS_SWAP):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        pos = event.position().toPoint()
        target_item = self.itemAt(pos)
        target_row = target_item.row() if target_item else self.rowCount() - 1
        if target_row < 0: target_row = 0

        if event.mimeData().hasFormat(MIME_POS_SWAP):
            if self.mode != "lineup": return
            data = event.mimeData().data(MIME_POS_SWAP)
            stream = QDataStream(data, QIODevice.ReadOnly)
            source_row = stream.readInt32()
            if source_row != target_row:
                self.position_swapped.emit(source_row, target_row)
            event.accept()
            
        elif event.mimeData().hasFormat(MIME_PLAYER_DATA):
            data = event.mimeData().data(MIME_PLAYER_DATA)
            stream = QDataStream(data, QIODevice.ReadOnly)
            player_idx = stream.readInt32()
            
            self.dropped_player_idx = player_idx
            self.dropped_target_row = target_row
            
            event.accept()
            self.items_changed.emit()

class OrderPage(QWidget):
    """Redesigned Order Page with DH, Color Coding, and Advanced Filters"""
    
    order_saved = Signal()
    player_detail_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = get_theme()
        self.game_state = None
        self.current_team = None
        # Initialize Delegates with theme
        self.defense_delegate = DefenseDelegate(self.theme)
        self.rating_delegate = RatingDelegate(self) # インスタンス化
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Main Tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet(self._get_main_tab_style())
        
        self.batter_page = self._create_batter_page()
        self.main_tabs.addTab(self.batter_page, "野手オーダー")
        
        self.pitcher_page = self._create_pitcher_page()
        self.main_tabs.addTab(self.pitcher_page, "投手オーダー")
        
        layout.addWidget(self.main_tabs)

    def _create_toolbar(self) -> ToolbarPanel:
        toolbar = ToolbarPanel()
        toolbar.setFixedHeight(50)

        label = QLabel("チーム:")
        label.setStyleSheet(f"color: {self.theme.text_secondary}; margin-left: 12px;")
        toolbar.add_widget(label)

        self.team_selector = QComboBox()
        self.team_selector.setMinimumWidth(200)
        self.team_selector.setFixedHeight(32)
        self.team_selector.currentIndexChanged.connect(self._on_team_changed)
        self.team_selector.setStyleSheet(f"background: {self.theme.bg_input}; color: {self.theme.text_primary}; border: 1px solid {self.theme.border}; border-radius: 4px;")
        toolbar.add_widget(self.team_selector)
        
        self.status_label = QLabel("一軍登録: --/--")
        self.status_label.setStyleSheet(f"color: {self.theme.text_primary}; font-weight: bold; margin-left: 20px;")
        toolbar.add_widget(self.status_label)

        toolbar.add_stretch()
        
        detail_btn = QPushButton("選手詳細")
        detail_btn.setCursor(Qt.PointingHandCursor)
        detail_btn.setStyleSheet(f"background: {self.theme.bg_card}; color: {self.theme.text_primary}; padding: 6px 12px; border: 1px solid {self.theme.border}; border-radius: 4px;")
        detail_btn.clicked.connect(self._on_player_detail_clicked)
        toolbar.add_widget(detail_btn)
        
        toolbar.add_spacing(8)

        auto_btn = QPushButton("自動編成")
        auto_btn.setCursor(Qt.PointingHandCursor)
        auto_btn.setStyleSheet(f"background: {self.theme.bg_card}; color: {self.theme.text_primary}; padding: 6px 12px; border: 1px solid {self.theme.border}; border-radius: 4px;")
        auto_btn.clicked.connect(self._auto_fill)
        toolbar.add_widget(auto_btn)

        save_btn = QPushButton("保存")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"background: {self.theme.primary}; color: #222222; padding: 6px 20px; border: none; border-radius: 4px; font-weight: bold;")
        save_btn.clicked.connect(self._save_order)
        toolbar.add_widget(save_btn)

        return toolbar

    def _create_batter_page(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {self.theme.border}; width: 1px; }}")

        # LEFT
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(8, 8, 8, 8)
        
        l_header = QLabel("スタメン & ベンチ")
        l_header.setStyleSheet(f"font-weight: bold; color: {self.theme.text_secondary}; font-size: 13px;")
        left_layout.addWidget(l_header)
        
        self.lineup_table = self._create_table("lineup")
        self.lineup_table.setMinimumHeight(350)
        left_layout.addWidget(self.lineup_table)
        
        left_layout.addSpacing(4)
        
        self.bench_table = self._create_table("bench")
        left_layout.addWidget(self.bench_table)
        splitter.addWidget(left_widget)

        # RIGHT
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)
        
        ctrl_layout = QHBoxLayout()
        r_header = QLabel("野手リスト (支配下)")
        r_header.setStyleSheet(f"font-weight: bold; color: {self.theme.text_secondary}; font-size: 13px;")
        ctrl_layout.addWidget(r_header)
        
        ctrl_layout.addStretch()
        
        self.batter_pos_filter = QComboBox()
        self.batter_pos_filter.addItems(["全ポジション", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "外野手"])
        self.batter_pos_filter.currentIndexChanged.connect(self._refresh_batter_farm_list)
        self.batter_pos_filter.setStyleSheet(f"background: {self.theme.bg_input}; color: {self.theme.text_primary}; border: 1px solid {self.theme.border}; padding: 2px;")
        ctrl_layout.addWidget(self.batter_pos_filter)
        
        right_layout.addLayout(ctrl_layout)
        
        self.farm_batter_table = self._create_table("farm_batter")
        right_layout.addWidget(self.farm_batter_table)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)
        return page

    def _create_pitcher_page(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {self.theme.border}; width: 1px; }}")

        # LEFT
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(8, 8, 8, 8)
        
        l_header = QLabel("投手陣容 (先発・中継ぎ・抑え)")
        l_header.setStyleSheet(f"font-weight: bold; color: {self.theme.text_secondary}; font-size: 13px;")
        left_layout.addWidget(l_header)
        
        self.rotation_table = self._create_table("rotation")
        self.rotation_table.setMinimumHeight(240)
        left_layout.addWidget(self.rotation_table)
        
        left_layout.addSpacing(4)
        
        self.bullpen_table = self._create_table("bullpen")
        left_layout.addWidget(self.bullpen_table)
        splitter.addWidget(left_widget)

        # RIGHT
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)
        
        ctrl_layout = QHBoxLayout()
        r_header = QLabel("投手リスト (支配下)")
        r_header.setStyleSheet(f"font-weight: bold; color: {self.theme.text_secondary}; font-size: 13px;")
        ctrl_layout.addWidget(r_header)
        
        ctrl_layout.addStretch()
        
        self.pitcher_type_filter = QComboBox()
        self.pitcher_type_filter.addItems(["全タイプ", "先発", "中継ぎ", "抑え"])
        self.pitcher_type_filter.currentIndexChanged.connect(self._refresh_pitcher_farm_list)
        self.pitcher_type_filter.setStyleSheet(f"background: {self.theme.bg_input}; color: {self.theme.text_primary}; border: 1px solid {self.theme.border}; padding: 2px;")
        ctrl_layout.addWidget(self.pitcher_type_filter)
        
        right_layout.addLayout(ctrl_layout)
        
        self.farm_pitcher_table = self._create_table("farm_pitcher")
        right_layout.addWidget(self.farm_pitcher_table)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)
        return page

    def _create_table(self, mode) -> DraggableTableWidget:
        table = DraggableTableWidget(mode)
        table.items_changed.connect(lambda: self._on_table_changed(table))
        
        if mode == "lineup":
            cols = ["順", "守", "選手名", "ミ", "パ", "走", "肩", "守", "適正", "総合"]
            widths = [30, 40, 130, 35, 35, 35, 35, 35, 80, 45]
            table.position_swapped.connect(self._on_pos_swapped)
            
            # Set RatingDelegate for stats columns
            for c in [3, 4, 5, 6, 7]:
                table.setItemDelegateForColumn(c, self.rating_delegate)
            # Set Aptitude Delegate
            table.setItemDelegateForColumn(8, self.defense_delegate)
            
        elif mode == "bench":
            cols = ["適性", "選手名", "ミ", "パ", "走", "肩", "守", "適正", "総合"]
            widths = [70, 130, 35, 35, 35, 35, 35, 80, 45]
            
            for c in [2, 3, 4, 5, 6]:
                table.setItemDelegateForColumn(c, self.rating_delegate)
            table.setItemDelegateForColumn(7, self.defense_delegate)

        elif mode == "farm_batter":
            cols = ["選手名", "年齢", "ミ", "パ", "走", "肩", "守", "守備適正", "総合"]
            widths = [130, 40, 35, 35, 35, 35, 35, 80, 45]
            
            for c in [2, 3, 4, 5, 6]:
                table.setItemDelegateForColumn(c, self.rating_delegate)
            table.setItemDelegateForColumn(7, self.defense_delegate)

        elif mode == "rotation" or mode == "bullpen":
            # コ(3), ス(4), 変(5) のみランク表示（球速は数値テキスト）
            cols = ["役", "選手名", "球速", "コ", "ス", "変", "先", "中", "抑", "総合"]
            widths = [40, 130, 50, 35, 35, 35, 35, 35, 35, 45]
            
            for c in [3, 4, 5]:
                table.setItemDelegateForColumn(c, self.rating_delegate)

        elif mode == "farm_pitcher":
            # コ(4), ス(5), 変(6) のみランク表示
            cols = ["タイプ", "選手名", "年齢", "球速", "コ", "ス", "変", "先", "中", "抑", "総合"]
            widths = [45, 130, 40, 50, 35, 35, 35, 35, 35, 45]
            
            for c in [4, 5, 6]:
                table.setItemDelegateForColumn(c, self.rating_delegate)

        table.setColumnCount(len(cols))
        table.setHorizontalHeaderLabels(cols)
        for i, w in enumerate(widths):
            table.setColumnWidth(i, w)

        table.setStyleSheet(self._get_table_style())
        return table

    def _get_table_style(self):
        return f"""
            QTableWidget {{
                background-color: {self.theme.bg_card};
                border: 1px solid {self.theme.border};
                gridline-color: {self.theme.border_muted};
                selection-background-color: {self.theme.bg_input};
                outline: none;
            }}
            QTableWidget::item:selected {{
                background-color: {self.theme.bg_input};
                color: {self.theme.text_primary};
                border: none;
                outline: none;
            }}
            QTableWidget::item:focus {{
                background-color: {self.theme.bg_input};
                border: none;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {self.theme.bg_input};
                color: {self.theme.text_secondary};
                border: none;
                border-bottom: 1px solid {self.theme.border};
                padding: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            QHeaderView::section:hover {{
                background-color: {self.theme.bg_hover};
            }}
            QTableWidget::item {{
                padding: 2px;
                border-bottom: 1px solid {self.theme.border_muted};
            }}
        """
    
    def _get_main_tab_style(self):
        return f"""
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: {self.theme.bg_dark};
                color: {self.theme.text_secondary};
                padding: 8px 24px;
                border-bottom: 2px solid {self.theme.border};
                font-weight: bold;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                color: {self.theme.primary};
                border-bottom: 2px solid {self.theme.primary};
                background: {self.theme.bg_input};
            }}
        """

    def set_game_state(self, game_state):
        self.game_state = game_state
        if not game_state: return
        self.team_selector.clear()
        for team in game_state.teams:
            self.team_selector.addItem(team.name, team)
        
        if game_state.player_team:
            idx = game_state.teams.index(game_state.player_team)
            self.team_selector.setCurrentIndex(idx)

    def _on_team_changed(self, index):
        if index >= 0:
            self.current_team = self.team_selector.itemData(index)
            self._refresh_all()

    def _ensure_lists_initialized(self):
        team = self.current_team
        if not team: return
        
        while len(team.current_lineup) < 9: team.current_lineup.append(-1)
        while len(team.rotation) < 8: team.rotation.append(-1)
        while len(team.setup_pitchers) < 8: team.setup_pitchers.append(-1)
        if not hasattr(team, 'closers'):
            team.closers = []
        while len(team.closers) < 2: team.closers.append(-1)
            
        if not hasattr(team, 'lineup_positions') or len(team.lineup_positions) != 9:
            team.lineup_positions = ["捕", "一", "二", "三", "遊", "左", "中", "右", "DH"]

    def _refresh_all(self):
        if not self.current_team: return
        self._ensure_lists_initialized()
        
        self._refresh_lineup_table()
        self._refresh_bench_table()
        self._refresh_batter_farm_list()
        self._refresh_rotation_table()
        self._refresh_bullpen_table()
        self._refresh_pitcher_farm_list()
        self._update_status_label()

    def _get_active_player_count(self) -> int:
        if not self.current_team: return 0
        team = self.current_team
        active_set = set()
        active_set.update([x for x in team.current_lineup if x >= 0])
        active_set.update([x for x in team.bench_batters if x >= 0])
        active_set.update([x for x in team.rotation if x >= 0])
        active_set.update([x for x in team.setup_pitchers if x >= 0])
        active_set.update([x for x in team.closers if x >= 0])
        return len(active_set)

    def _update_status_label(self):
        if not self.current_team: return
        count = self._get_active_player_count()
        limit = 31
        if hasattr(self.current_team, 'ACTIVE_ROSTER_LIMIT'):
            limit = self.current_team.ACTIVE_ROSTER_LIMIT

        self.status_label.setText(f"一軍登録数: {count}/{limit}")
        color = self.theme.success if count <= limit else self.theme.danger
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; margin-left: 20px;")

    # === Data Helpers ===
    
    def _create_item(self, value, align=Qt.AlignCenter, rank_color=False, pos_badge=None, is_star=False, sort_val=None):
        """Rich Table Item Factory using SortableTableWidgetItem for correct sorting"""
        item = SortableTableWidgetItem()
        
        if rank_color:
            # RatingDelegate使用モード：数値データをUserRoleにセットし、表示テキストは空にする
            # 呼び出し元からは、valueに数値が渡されていることを前提とする
            if sort_val is None:
                sort_val = value # ソート用データとしてそのまま使用
            
            item.setData(Qt.UserRole, value)
            item.setData(Qt.DisplayRole, "") # Delegateが描画するため空
        else:
            item.setText(str(value))
            
            # 従来通りの色付け処理
            if pos_badge:
                item.setBackground(QColor(get_pos_color(pos_badge)))
                item.setForeground(Qt.white)
                font = QFont()
                font.setBold(True)
                item.setFont(font)
            elif is_star:
                item.setForeground(QColor("#FFD700"))
                font = QFont()
                font.setBold(True)
                item.setFont(font)

        item.setTextAlignment(align)
        
        # Store raw value for sorting (Qt.UserRole)
        if sort_val is not None:
             item.setData(Qt.UserRole, sort_val)
        elif not rank_color:
            try:
                if isinstance(value, str) and "★" in value:
                    num = int(value.replace("★", ""))
                    item.setData(Qt.UserRole, num)
                elif isinstance(value, (int, float)):
                    item.setData(Qt.UserRole, value)
            except:
                pass
            
        return item

    def _format_aptitude_delegate(self, p):
        main_pos = self._short_pos_name(p.position.value)
        subs = []
        if hasattr(p.stats, 'defense_ranges'):
            sorted_ranges = sorted(p.stats.defense_ranges.items(), key=lambda x: x[1], reverse=True)
            for pos_name, val in sorted_ranges:
                if pos_name != p.position.value and val > 10: 
                    subs.append(self._short_pos_name(pos_name))
        sub_str = " ".join(subs)
        return f"{main_pos}|{sub_str}"

    def _short_pos_name(self, long_name):
        mapping = {"投手":"投","捕手":"捕","一塁手":"一","二塁手":"二","三塁手":"三",
                   "遊撃手":"遊","左翼手":"左","中堅手":"中","右翼手":"右"}
        return mapping.get(long_name, long_name[0])

    # === Table Fillers (Modified to pass raw stats) ===

    def _refresh_lineup_table(self):
        team = self.current_team
        table = self.lineup_table
        table.setRowCount(9)
        pos_order = {"捕": 2, "一": 3, "二": 4, "三": 5, "遊": 6, "左": 7, "中": 8, "右": 9, "DH": 10}
            
        for i in range(9):
            p_idx = -1
            if i < len(team.current_lineup):
                p_idx = team.current_lineup[i]
            
            pos_label = team.lineup_positions[i]
            
            table.setItem(i, 0, self._create_item(f"{i+1}"))
            
            pos_item = self._create_item(pos_label, pos_badge=pos_label)
            pos_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            table.setItem(i, 1, pos_item)
            
            if p_idx != -1 and p_idx < len(team.players):
                p = team.players[p_idx]
                table.setItem(i, 2, self._create_item(p.name, Qt.AlignLeft))
                
                s = p.stats
                # Pass raw numeric stats with rank_color=True for RatingDelegate
                table.setItem(i, 3, self._create_item(s.contact, rank_color=True))
                table.setItem(i, 4, self._create_item(s.power, rank_color=True))
                table.setItem(i, 5, self._create_item(s.speed, rank_color=True))
                table.setItem(i, 6, self._create_item(s.arm, rank_color=True))
                table.setItem(i, 7, self._create_item(s.error, rank_color=True))
                
                apt_data = self._format_aptitude_delegate(p)
                p_pos_char = self._short_pos_name(p.position.value)
                sort_val = pos_order.get(p_pos_char, 99)
                table.setItem(i, 8, self._create_item(apt_data, sort_val=sort_val))
                
                table.setItem(i, 9, self._create_item(f"★{p.overall_rating}", is_star=True))
                
                for c in range(table.columnCount()):
                    if table.item(i, c): table.item(i, c).setData(ROLE_PLAYER_IDX, p_idx)
            else:
                self._clear_row(table, i, 2)

    def _refresh_bench_table(self):
        team = self.current_team
        table = self.bench_table
        table.setRowCount(len(team.bench_batters) + 2)
        pos_order = {"捕": 2, "一": 3, "二": 4, "三": 5, "遊": 6, "左": 7, "中": 8, "右": 9, "DH": 10}
        
        for i, p_idx in enumerate(team.bench_batters):
            if p_idx != -1 and p_idx < len(team.players):
                p = team.players[p_idx]
                main_pos = self._short_pos_name(p.position.value)
                table.setItem(i, 0, self._create_item(main_pos))
                table.setItem(i, 1, self._create_item(p.name, Qt.AlignLeft))
                
                s = p.stats
                table.setItem(i, 2, self._create_item(s.contact, rank_color=True))
                table.setItem(i, 3, self._create_item(s.power, rank_color=True))
                table.setItem(i, 4, self._create_item(s.speed, rank_color=True))
                table.setItem(i, 5, self._create_item(s.arm, rank_color=True))
                table.setItem(i, 6, self._create_item(s.error, rank_color=True))
                
                apt_data = self._format_aptitude_delegate(p)
                p_pos_char = main_pos
                sort_val = pos_order.get(p_pos_char, 99)
                table.setItem(i, 7, self._create_item(apt_data, sort_val=sort_val))

                table.setItem(i, 8, self._create_item(f"★{p.overall_rating}", is_star=True))
                
                for c in range(table.columnCount()):
                    if table.item(i, c): table.item(i, c).setData(ROLE_PLAYER_IDX, p_idx)
            else:
                self._clear_row(table, i, 0)
        
        for i in range(len(team.bench_batters), table.rowCount()):
             self._clear_row(table, i, 0)

    def _refresh_batter_farm_list(self):
        team = self.current_team
        table = self.farm_batter_table
        
        active_ids = set(team.current_lineup + team.bench_batters)
        
        candidates = []
        pos_filter = self.batter_pos_filter.currentText()
        
        for i, p in enumerate(team.players):
            if p.position.value != "投手" and i not in active_ids:
                if p.is_developmental: continue
                
                if pos_filter != "全ポジション" and p.position.value != pos_filter:
                    continue
                    
                candidates.append((i, p))
        
        pos_order = {"捕": 2, "一": 3, "二": 4, "三": 5, "遊": 6, "左": 7, "中": 8, "右": 9, "DH": 10}

        table.setRowCount(len(candidates))
        for i, (p_idx, p) in enumerate(candidates):
            table.setItem(i, 0, self._create_item(p.name, Qt.AlignLeft))
            table.setItem(i, 1, self._create_item(p.age)) 
            
            s = p.stats
            table.setItem(i, 2, self._create_item(s.contact, rank_color=True))
            table.setItem(i, 3, self._create_item(s.power, rank_color=True))
            table.setItem(i, 4, self._create_item(s.speed, rank_color=True))
            table.setItem(i, 5, self._create_item(s.arm, rank_color=True))
            table.setItem(i, 6, self._create_item(s.error, rank_color=True))
            
            apt_data = self._format_aptitude_delegate(p)
            p_pos_char = self._short_pos_name(p.position.value)
            sort_val = pos_order.get(p_pos_char, 99)
            
            apt_item = self._create_item(apt_data, sort_val=sort_val) 
            table.setItem(i, 7, apt_item)
            
            table.setItem(i, 8, self._create_item(f"★{p.overall_rating}", is_star=True))
            
            for c in range(table.columnCount()):
                if table.item(i, c): table.item(i, c).setData(ROLE_PLAYER_IDX, p_idx)

        header = table.horizontalHeader()
        table.sortItems(header.sortIndicatorSection(), header.sortIndicatorOrder())

    def _refresh_rotation_table(self):
        team = self.current_team
        table = self.rotation_table
        table.setRowCount(8)
        for i in range(8):
            p_idx = -1
            if i < len(team.rotation):
                p_idx = team.rotation[i]
            self._fill_pitcher_row_role(table, i, "先発", p_idx)

    def _refresh_bullpen_table(self):
        team = self.current_team
        table = self.bullpen_table
        table.setRowCount(10)
        
        for i in range(8):
            p_idx = -1
            if i < len(team.setup_pitchers):
                p_idx = team.setup_pitchers[i]
            self._fill_pitcher_row_role(table, i, "中継", p_idx)
            
        for i in range(2):
            p_idx = -1
            if i < len(team.closers):
                p_idx = team.closers[i]
            self._fill_pitcher_row_role(table, 8 + i, "抑え", p_idx)

    def _fill_pitcher_row_role(self, table, row, role_lbl, p_idx):
        table.setItem(row, 0, self._create_item(role_lbl, pos_badge=role_lbl[0]))
        if p_idx != -1 and p_idx < len(self.current_team.players):
            p = self.current_team.players[p_idx]
            self._fill_pitcher_data(table, row, p, p_idx, start_col=1)
        else:
            self._clear_row(table, row, 1)

    def _refresh_pitcher_farm_list(self):
        team = self.current_team
        table = self.farm_pitcher_table
        
        active_ids = set([x for x in team.rotation if x >= 0])
        active_ids.update([x for x in team.setup_pitchers if x >= 0])
        active_ids.update([x for x in team.closers if x >= 0])
        
        candidates = []
        type_filter = self.pitcher_type_filter.currentText()
        
        for i, p in enumerate(team.players):
            if p.position.value == "投手" and i not in active_ids:
                if p.is_developmental: continue
                
                if type_filter != "全タイプ" and p.pitch_type.value != type_filter:
                    continue
                
                candidates.append((i, p))
                
        table.setRowCount(len(candidates))
        for i, (p_idx, p) in enumerate(candidates):
            role = p.pitch_type.value[:2]
            table.setItem(i, 0, self._create_item(role))
            
            table.setItem(i, 1, self._create_item(p.name, Qt.AlignLeft))
            table.setItem(i, 2, self._create_item(p.age))
            
            kmh = p.stats.speed_to_kmh()
            table.setItem(i, 3, self._create_item(f"{kmh}km", sort_val=kmh))
            
            # Pass raw stats for RatingDelegate
            table.setItem(i, 4, self._create_item(p.stats.control, rank_color=True))
            table.setItem(i, 5, self._create_item(p.stats.stamina, rank_color=True))
            table.setItem(i, 6, self._create_item(p.stats.stuff, rank_color=True))
            
            st = "◎" if p.pitch_type.value == "先発" else "△"
            rl = "◎" if p.pitch_type.value == "中継ぎ" else "△"
            cl = "◎" if p.pitch_type.value == "抑え" else "△"
            table.setItem(i, 7, self._create_item(st, sort_val=2 if st=="◎" else 1))
            table.setItem(i, 8, self._create_item(rl, sort_val=2 if rl=="◎" else 1))
            table.setItem(i, 9, self._create_item(cl, sort_val=2 if cl=="◎" else 1))
            
            table.setItem(i, 10, self._create_item(f"★{p.overall_rating}", is_star=True))

            for c in range(table.columnCount()):
                if table.item(i, c): table.item(i, c).setData(ROLE_PLAYER_IDX, p_idx)
                
        header = table.horizontalHeader()
        table.sortItems(header.sortIndicatorSection(), header.sortIndicatorOrder())

    def _fill_pitcher_data(self, table, row, p, p_idx, start_col):
        table.setItem(row, start_col, self._create_item(p.name, Qt.AlignLeft))
        kmh = p.stats.speed_to_kmh()
        table.setItem(row, start_col+1, self._create_item(f"{kmh}km"))
        
        # Pass raw stats for RatingDelegate
        table.setItem(row, start_col+2, self._create_item(p.stats.control, rank_color=True))
        table.setItem(row, start_col+3, self._create_item(p.stats.stamina, rank_color=True))
        table.setItem(row, start_col+4, self._create_item(p.stats.stuff, rank_color=True))
        
        st = "◎" if p.pitch_type.value == "先発" else "△"
        rl = "◎" if p.pitch_type.value == "中継ぎ" else "△"
        cl = "◎" if p.pitch_type.value == "抑え" else "△"
        table.setItem(row, start_col+5, self._create_item(st))
        table.setItem(row, start_col+6, self._create_item(rl))
        table.setItem(row, start_col+7, self._create_item(cl))
        table.setItem(row, start_col+8, self._create_item(f"★{p.overall_rating}", is_star=True))

        for c in range(table.columnCount()):
            if table.item(row, c): table.item(row, c).setData(ROLE_PLAYER_IDX, p_idx)

    def _clear_row(self, table, row, start_col):
        for c in range(start_col, table.columnCount()):
            table.setItem(row, c, QTableWidgetItem(""))
        if start_col < table.columnCount():
            table.setItem(row, start_col, QTableWidgetItem("---"))

    # === Event Handlers ===
    
    def _on_table_changed(self, table):
        if not hasattr(table, 'dropped_player_idx'): return
        p_idx = table.dropped_player_idx
        row = table.dropped_target_row
        team = self.current_team
        
        source_list = None
        source_idx = -1
        
        if p_idx in team.current_lineup:
            source_list = team.current_lineup
            source_idx = team.current_lineup.index(p_idx)
        elif p_idx in team.bench_batters:
            source_list = team.bench_batters
            source_idx = team.bench_batters.index(p_idx)
        elif p_idx in team.rotation:
            source_list = team.rotation
            source_idx = team.rotation.index(p_idx)
        elif p_idx in team.setup_pitchers:
            source_list = team.setup_pitchers
            source_idx = team.setup_pitchers.index(p_idx)
        elif p_idx in team.closers:
            source_list = team.closers
            source_idx = team.closers.index(p_idx)
            
        target_list = None
        target_p_idx = -1
        
        if table == self.lineup_table:
            target_list = team.current_lineup
            while len(target_list) <= row: target_list.append(-1)
            target_p_idx = target_list[row]
            
        elif table == self.bench_table:
            target_list = team.bench_batters
            while len(target_list) <= row: target_list.append(-1)
            target_p_idx = target_list[row]
            
        elif table == self.rotation_table:
            target_list = team.rotation
            while len(target_list) <= row: target_list.append(-1)
            target_p_idx = target_list[row]
            
        elif table == self.bullpen_table:
            if row >= 8: # Closer
                target_list = team.closers
                c_row = row - 8
                while len(target_list) <= c_row: target_list.append(-1)
                target_p_idx = target_list[c_row]
                row = c_row 
            else:
                target_list = team.setup_pitchers
                while len(target_list) <= row: target_list.append(-1)
                target_p_idx = target_list[row]

        if source_list is None and target_p_idx == -1:
            active_count = self._get_active_player_count()
            limit = 31
            if hasattr(team, 'ACTIVE_ROSTER_LIMIT'):
                limit = team.ACTIVE_ROSTER_LIMIT
                
            if active_count >= limit:
                QMessageBox.warning(self, "登録制限", f"一軍登録枠({limit}人)を超えています。\n枠を空けるか、既存の選手と入れ替えてください。")
                self._refresh_all()
                del table.dropped_player_idx
                return
        
        if source_list is not None:
            target_list[row] = p_idx
            if source_idx < len(source_list):
                source_list[source_idx] = target_p_idx
        else:
            target_list[row] = p_idx
        
        self._refresh_all()
        del table.dropped_player_idx

    def _on_pos_swapped(self, r1, r2):
        team = self.current_team
        pos_list = team.lineup_positions
        if r1 < 9 and r2 < 9:
            pos_list[r1], pos_list[r2] = pos_list[r2], pos_list[r1]
            self._refresh_lineup_table()

    def _remove_player_from_active(self, idx):
        t = self.current_team
        if idx in t.current_lineup: t.current_lineup[t.current_lineup.index(idx)] = -1
        if idx in t.bench_batters: t.bench_batters.remove(idx)
        if idx in t.rotation: t.rotation[t.rotation.index(idx)] = -1
        if idx in t.setup_pitchers: t.setup_pitchers[t.setup_pitchers.index(idx)] = -1
        if idx in t.closers: t.closers[t.closers.index(idx)] = -1

    def _auto_fill(self):
        if not self.current_team: return
        t = self.current_team
        
        t.current_lineup = [-1] * 9
        t.lineup_positions = [""] * 9
        t.bench_batters = []
        t.rotation = [-1] * 8
        t.setup_pitchers = [-1] * 8 
        t.closers = [-1] * 2

        TOTAL_LIMIT = 31
        if hasattr(t, 'ACTIVE_ROSTER_LIMIT'):
            TOTAL_LIMIT = t.ACTIVE_ROSTER_LIMIT
            
        PITCHER_TARGET = int(TOTAL_LIMIT * (13/31))
        BATTER_TARGET = TOTAL_LIMIT - PITCHER_TARGET

        def get_condition_mult(p):
            return 1.0 + (p.condition - 5) * 0.05

        def get_batting_score(p):
            s = p.stats
            val = (s.contact * 1.0 + s.power * 1.2 + s.speed * 0.5 + s.eye * 0.5)
            return val * get_condition_mult(p)

        def get_defense_score(p, pos_name_long):
            apt = p.stats.defense_ranges.get(pos_name_long, 0)
            if apt < 20: return 0
            
            s = p.stats
            def_val = (apt * 1.5 + s.error * 0.5 + s.arm * 0.5)
            return def_val

        def get_pitcher_score(p, role):
            s = p.stats
            base = s.overall_pitching() * 99
            
            apt_mult = 1.0
            if role == 'starter':
                apt_mult = p.starter_aptitude / 50.0
                base += s.stamina * 0.5
            elif role == 'closer':
                apt_mult = p.closer_aptitude / 50.0
                base += (s.velocity - 130) * 2 + s.stuff * 0.5
            else:
                apt_mult = p.middle_aptitude / 50.0
            
            return base * apt_mult * get_condition_mult(p)

        pitchers = [i for i, p in enumerate(t.players) 
                   if p.position.value == "投手" and not p.is_developmental]
        
        pitchers.sort(key=lambda i: get_pitcher_score(t.players[i], 'starter'), reverse=True)
        
        rotation_count = 6
        rotation_candidates = pitchers[:rotation_count]
        remaining_pitchers = pitchers[rotation_count:]
        
        for i in range(min(rotation_count, len(rotation_candidates))):
            t.rotation[i] = rotation_candidates[i]
            
        if remaining_pitchers:
            remaining_pitchers.sort(key=lambda i: get_pitcher_score(t.players[i], 'closer'), reverse=True)
            t.closers[0] = remaining_pitchers.pop(0)
            
        remaining_pitchers.sort(key=lambda i: get_pitcher_score(t.players[i], 'relief'), reverse=True)
        
        used_p = len([x for x in t.rotation if x != -1]) + len([x for x in t.closers if x != -1])
        setup_limit = max(0, PITCHER_TARGET - used_p)
        
        for i in range(min(8, setup_limit, len(remaining_pitchers))):
            t.setup_pitchers[i] = remaining_pitchers[i]
            
        batters = [i for i, p in enumerate(t.players) 
                  if p.position.value != "投手" and not p.is_developmental]
        
        pos_map = {
            "捕": "捕手", "遊": "遊撃手", "二": "二塁手", "中": "中堅手", 
            "三": "三塁手", "右": "右翼手", "左": "左翼手", "一": "一塁手"
        }
        def_priority = ["捕", "遊", "二", "中", "三", "右", "左", "一"]
        
        selected_starters = {}
        used_indices = set()
        
        for short_pos in def_priority:
            long_pos = pos_map[short_pos]
            best_idx = -1
            best_score = -1
            
            for idx in batters:
                if idx in used_indices: continue
                p = t.players[idx]
                
                apt = p.stats.defense_ranges.get(long_pos, 0)
                if apt < 20: continue 
                
                def_weight = 1.0
                if short_pos in ["捕", "遊", "二"]: def_weight = 1.5
                
                score = (get_batting_score(p) + get_defense_score(p, long_pos) * def_weight)
                
                if score > best_score:
                    best_score = score
                    best_idx = idx
            
            if best_idx != -1:
                selected_starters[short_pos] = best_idx
                used_indices.add(best_idx)
        
        dh_candidates = [i for i in batters if i not in used_indices]
        dh_candidates.sort(key=lambda i: get_batting_score(t.players[i]), reverse=True)
        if dh_candidates:
            selected_starters["DH"] = dh_candidates[0]
            used_indices.add(dh_candidates[0])
            
        missing_positions = [p for p in def_priority + ["DH"] if p not in selected_starters]
        for p in missing_positions:
            remaining = [i for i in batters if i not in used_indices]
            if remaining:
                remaining.sort(key=lambda i: get_batting_score(t.players[i]), reverse=True)
                selected_starters[p] = remaining[0]
                used_indices.add(remaining[0])

        lineup_candidates = []
        for pos, idx in selected_starters.items():
            if idx == -1: continue
            lineup_candidates.append({"pos": pos, "idx": idx, "p": t.players[idx]})
            
        final_order = [None] * 9
        
        if len(lineup_candidates) >= 1:
            def pick_best(candidates, sort_key):
                if not candidates: return None
                best = max(candidates, key=sort_key)
                candidates.remove(best)
                return best

            final_order[3] = pick_best(lineup_candidates, lambda x: x['p'].stats.power)
            final_order[2] = pick_best(lineup_candidates, lambda x: get_batting_score(x['p']))
            final_order[0] = pick_best(lineup_candidates, lambda x: x['p'].stats.speed)
            final_order[4] = pick_best(lineup_candidates, lambda x: x['p'].stats.power)
            final_order[1] = pick_best(lineup_candidates, lambda x: x['p'].stats.contact + x['p'].stats.bunt_sac)
            
            lineup_candidates.sort(key=lambda x: get_batting_score(x['p']), reverse=True)
            for i in range(len(lineup_candidates)):
                found_slot = False
                for slot in range(5, 9):
                    if final_order[slot] is None:
                        final_order[slot] = lineup_candidates[i]
                        found_slot = True
                        break
                if not found_slot:
                     for slot in range(5):
                        if final_order[slot] is None:
                            final_order[slot] = lineup_candidates[i]
                            break

            for i in range(9):
                if final_order[i]:
                    t.current_lineup[i] = final_order[i]['idx']
                    t.lineup_positions[i] = final_order[i]['pos']

        remaining_bench = [i for i in batters if i not in used_indices]
        remaining_bench.sort(key=lambda i: t.players[i].overall_rating, reverse=True)
        
        bench_limit = max(0, BATTER_TARGET - 9)
        t.bench_batters = remaining_bench[:bench_limit]
        
        self._refresh_all()
        
    def _on_player_detail_clicked(self):
        if not self.current_team: return
        
        selected_player_idx = None
        
        tables = [
            self.lineup_table, self.bench_table, self.farm_batter_table,
            self.rotation_table, self.bullpen_table, self.farm_pitcher_table
        ]
        
        for table in tables:
            items = table.selectedItems()
            if items:
                item = items[0]
                idx = item.data(ROLE_PLAYER_IDX)
                if idx is not None and idx >= 0:
                    selected_player_idx = idx
                    break
        
        if selected_player_idx is not None and selected_player_idx < len(self.current_team.players):
            player = self.current_team.players[selected_player_idx]
            self.player_detail_requested.emit(player)
        else:
            QMessageBox.information(self, "情報", "詳細を表示する選手を選択してください。")

    def _save_order(self):
        if not self.current_team: return
        t = self.current_team
        
        valid_starters = len([x for x in t.current_lineup if x != -1])
        valid_rotation = len([x for x in t.rotation if x != -1])
        
        if valid_starters < 9:
            QMessageBox.warning(self, "エラー", "スタメンが9人未満です。試合を開始できません。")
            return
            
        if valid_rotation == 0:
            QMessageBox.warning(self, "エラー", "先発投手が設定されていません。試合を開始できません。")
            return

        self.order_saved.emit()
        self._update_status_label()
        QMessageBox.information(self, "保存", "オーダーを保存しました。")