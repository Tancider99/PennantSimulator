# -*- coding: utf-8 -*-
"""
NPBペナントシミュレーター - プロフェッショナルUI
洗練されたモダンなデザインのUIシステム
"""
import pygame
import math
import time
from typing import Callable, Optional, List, Dict, Tuple
from enum import Enum
from constants import (
    WHITE, BLACK, GOLD, LIGHT_GRAY, GRAY, DARK_GRAY,
    BLUE, DARK_BLUE, GREEN, DARK_GREEN, RED, DARK_RED,
    CYAN, ORANGE, PURPLE, NAVY, DARK_NAVY, TEAM_COLORS
)


# ============================================================
# カラーパレット（プロフェッショナル）
# ============================================================
class Colors:
    """統一されたカラーパレット"""
    # 背景
    BG_DARK = (12, 14, 18)
    BG_CARD = (22, 26, 32)
    BG_CARD_HOVER = (32, 38, 48)
    BG_HOVER = (32, 38, 48)  # BG_CARD_HOVERのエイリアス
    BG_INPUT = (18, 22, 28)
    
    # アクセント
    PRIMARY = (59, 130, 246)      # ブルー
    PRIMARY_HOVER = (96, 165, 250)
    PRIMARY_DARK = (37, 99, 235)
    
    SECONDARY = (168, 85, 247)    # パープル
    SUCCESS = (34, 197, 94)       # グリーン
    SUCCESS_HOVER = (74, 222, 128)
    WARNING = (251, 191, 36)      # イエロー
    DANGER = (239, 68, 68)        # レッド
    DANGER_HOVER = (248, 113, 113)
    INFO = (56, 189, 248)         # シアン/スカイブルー
    
    # テキスト
    TEXT_PRIMARY = (248, 250, 252)
    TEXT_SECONDARY = (148, 163, 184)
    TEXT_MUTED = (100, 116, 139)
    
    # ボーダー
    BORDER = (51, 65, 85)
    BORDER_LIGHT = (71, 85, 105)
    
    # 特別色
    GOLD = (251, 191, 36)
    GOLD_LIGHT = (253, 224, 71)


# ============================================================
# フォント管理
# ============================================================
class FontManager:
    """フォント管理クラス（おしゃれフォント対応）"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def init(self):
        if self._initialized:
            return
        
        if not pygame.font.get_init():
            pygame.font.init()
        
        import os
        
        # モダンなフォントを優先的に検索
        modern_fonts = [
            "YuGothic-Bold.ttf",    # 游ゴシック（ボールド）
            "yugothb.ttc",           # 游ゴシック太字
            "YuGothB.ttc",           # 游ゴシックボールド
            "MEIRYOB.TTC",           # メイリオボールド
            "meiryob.ttc",           # メイリオボールド
            "meiryo.ttc",            # メイリオ
            "NotoSansJP-Bold.otf",   # Noto Sans JP
            "NotoSansCJKjp-Bold.otf", # Noto Sans CJK
            "msgothic.ttc",          # MSゴシック
        ]
        
        font_dirs = [
            "C:\\Windows\\Fonts",
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\Fonts"),
        ]
        
        font_path = None
        for font_name in modern_fonts:
            for font_dir in font_dirs:
                path = os.path.join(font_dir, font_name)
                if os.path.exists(path):
                    font_path = path
                    break
            if font_path:
                break
        
        # フォントサイズをやや大きめに（読みやすさ向上）
        if font_path:
            self.title = pygame.font.Font(font_path, 52)
            self.h1 = pygame.font.Font(font_path, 38)
            self.h2 = pygame.font.Font(font_path, 30)
            self.h3 = pygame.font.Font(font_path, 24)
            self.body = pygame.font.Font(font_path, 18)
            self.small = pygame.font.Font(font_path, 15)
            self.tiny = pygame.font.Font(font_path, 13)
            self.icon = pygame.font.Font(font_path, 22)  # アイコン用
        else:
            self.title = pygame.font.Font(None, 52)
            self.h1 = pygame.font.Font(None, 38)
            self.h2 = pygame.font.Font(None, 30)
            self.h3 = pygame.font.Font(None, 24)
            self.body = pygame.font.Font(None, 18)
            self.small = pygame.font.Font(None, 15)
            self.tiny = pygame.font.Font(None, 13)
            self.icon = pygame.font.Font(None, 22)
        
        self._initialized = True


# グローバルフォントマネージャー
fonts = FontManager()


# ============================================================
# ユーティリティ関数
# ============================================================
def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    """色の線形補間"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def ease_out_cubic(t: float) -> float:
    """イージング関数"""
    return 1 - pow(1 - t, 3)


def draw_rounded_rect(surface, rect, color, radius=8, border=0, border_color=None):
    """角丸四角形を描画"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_shadow(surface, rect, offset=4, blur=8, alpha=40):
    """シャドウを描画"""
    shadow_surf = pygame.Surface((rect.width + blur*2, rect.height + blur*2), pygame.SRCALPHA)
    shadow_rect = pygame.Rect(blur, blur, rect.width, rect.height)
    pygame.draw.rect(shadow_surf, (0, 0, 0, alpha), shadow_rect, border_radius=12)
    surface.blit(shadow_surf, (rect.x - blur + offset, rect.y - blur + offset))


# ============================================================
# ボタンコンポーネント
# ============================================================
class Button:
    """プロフェッショナルなボタン"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 style: str = "primary", icon: str = None,
                 font: pygame.font.Font = None, callback: Callable = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.style = style
        self.icon = icon
        self.font = font or fonts.h3
        self.callback = callback
        self.enabled = True
        
        # 状態
        self.is_hovered = False
        self.is_pressed = False
        self.hover_progress = 0.0
        self.press_progress = 0.0
        self.last_time = time.time()
        
        # スタイル設定
        self._set_style_colors()
    
    def _set_style_colors(self):
        """スタイルに応じた色を設定"""
        styles = {
            "primary": (Colors.PRIMARY, Colors.PRIMARY_HOVER, Colors.PRIMARY_DARK),
            "secondary": (Colors.SECONDARY, (188, 115, 255), (138, 65, 217)),
            "success": (Colors.SUCCESS, Colors.SUCCESS_HOVER, (22, 163, 74)),
            "danger": (Colors.DANGER, Colors.DANGER_HOVER, (220, 38, 38)),
            "warning": (Colors.WARNING, Colors.GOLD_LIGHT, (234, 179, 8)),
            "ghost": (Colors.BG_CARD, Colors.BG_CARD_HOVER, Colors.BORDER),
            "outline": ((0, 0, 0, 0), Colors.BG_CARD_HOVER, Colors.BORDER),
        }
        self.color_normal, self.color_hover, self.color_active = styles.get(
            self.style, styles["primary"]
        )
    
    def update(self):
        """アニメーション更新"""
        current_time = time.time()
        dt = min(current_time - self.last_time, 0.1)
        self.last_time = current_time
        
        # ホバーアニメーション
        target_hover = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target_hover - self.hover_progress) * min(1.0, dt * 12)
        
        # プレスアニメーション
        target_press = 1.0 if self.is_pressed else 0.0
        self.press_progress += (target_press - self.press_progress) * min(1.0, dt * 15)
    
    def draw(self, surface: pygame.Surface):
        self.update()
        
        # 色計算
        if not self.enabled:
            bg_color = Colors.BG_INPUT
            text_color = Colors.TEXT_MUTED
        else:
            bg_color = lerp_color(self.color_normal, self.color_hover, self.hover_progress)
            if self.is_pressed:
                bg_color = lerp_color(bg_color, self.color_active, self.press_progress)
            text_color = Colors.TEXT_PRIMARY
        
        # スケール効果
        scale = 1.0 - self.press_progress * 0.02
        scaled_rect = self.rect.inflate(
            int(self.rect.width * (scale - 1)),
            int(self.rect.height * (scale - 1))
        )
        
        # シャドウ（ホバー時）
        if self.hover_progress > 0.1 and self.enabled:
            shadow_alpha = int(30 * self.hover_progress)
            draw_shadow(surface, scaled_rect, 3, 6, shadow_alpha)
        
        # 背景
        draw_rounded_rect(surface, scaled_rect, bg_color, 10)
        
        # アウトラインスタイルの場合はボーダーを追加
        if self.style == "outline":
            border_color = lerp_color(Colors.BORDER, Colors.PRIMARY, self.hover_progress)
            draw_rounded_rect(surface, scaled_rect, bg_color, 10, 2, border_color)
        
        # テキスト
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                # MOUSEBUTTONDOWNでクリックを検知（ボタンが毎フレーム再生成される場合の対策）
                if self.callback:
                    self.callback()
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False
        
        return False


# ============================================================
# カードコンポーネント
# ============================================================
class Card:
    """カードコンポーネント"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 title: str = "", clickable: bool = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.clickable = clickable
        self.is_hovered = False
        self.hover_progress = 0.0
        self.last_time = time.time()
    
    def update(self):
        current_time = time.time()
        dt = min(current_time - self.last_time, 0.1)
        self.last_time = current_time
        
        target = 1.0 if self.is_hovered and self.clickable else 0.0
        self.hover_progress += (target - self.hover_progress) * min(1.0, dt * 10)
    
    def draw(self, surface: pygame.Surface) -> pygame.Rect:
        self.update()
        
        # ホバー効果
        offset_y = int(-3 * self.hover_progress)
        draw_rect = self.rect.move(0, offset_y)
        
        # シャドウ
        shadow_alpha = 20 + int(15 * self.hover_progress)
        draw_shadow(surface, draw_rect, 4, 8, shadow_alpha)
        
        # 背景
        bg_color = lerp_color(Colors.BG_CARD, Colors.BG_CARD_HOVER, self.hover_progress)
        draw_rounded_rect(surface, draw_rect, bg_color, 12)
        
        # ボーダー
        border_color = lerp_color(Colors.BORDER, Colors.PRIMARY, self.hover_progress * 0.5)
        draw_rounded_rect(surface, draw_rect, bg_color, 12, 1, border_color)
        
        # タイトル
        if self.title:
            title_surf = fonts.h3.render(self.title, True, Colors.TEXT_PRIMARY)
            surface.blit(title_surf, (draw_rect.x + 20, draw_rect.y + 15))
        
        return draw_rect
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)


# ============================================================
# プログレスバー
# ============================================================
class ProgressBar:
    """プログレスバー"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 value: float = 0.0, color: tuple = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = value
        self.display_value = 0.0
        self.color = color or Colors.PRIMARY
        self.last_time = time.time()
    
    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))
    
    def update(self):
        current_time = time.time()
        dt = min(current_time - self.last_time, 0.1)
        self.last_time = current_time
        
        self.display_value += (self.value - self.display_value) * min(1.0, dt * 8)
    
    def draw(self, surface: pygame.Surface, show_text: bool = True):
        self.update()
        
        # 背景
        draw_rounded_rect(surface, self.rect, Colors.BG_INPUT, self.rect.height // 2)
        
        # プログレス
        if self.display_value > 0:
            fill_width = int(self.rect.width * self.display_value)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            draw_rounded_rect(surface, fill_rect, self.color, self.rect.height // 2)
        
        # テキスト
        if show_text and self.rect.height >= 20:
            text = f"{int(self.display_value * 100)}%"
            text_surf = fonts.small.render(text, True, Colors.TEXT_PRIMARY)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)


# ============================================================
# 入力フィールド
# ============================================================
class InputField:
    """入力フィールド（選択用）"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 placeholder: str = "", value: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.value = value
        self.is_focused = False
        self.is_hovered = False
    
    def draw(self, surface: pygame.Surface):
        # 背景
        bg_color = Colors.BG_INPUT if not self.is_focused else Colors.BG_CARD_HOVER
        draw_rounded_rect(surface, self.rect, bg_color, 8)
        
        # ボーダー
        border_color = Colors.PRIMARY if self.is_focused else (
            Colors.BORDER_LIGHT if self.is_hovered else Colors.BORDER
        )
        draw_rounded_rect(surface, self.rect, bg_color, 8, 2, border_color)
        
        # テキスト
        display_text = self.value if self.value else self.placeholder
        text_color = Colors.TEXT_PRIMARY if self.value else Colors.TEXT_MUTED
        text_surf = fonts.body.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_focused = self.rect.collidepoint(event.pos)


# ============================================================
# テーブル
# ============================================================
class Table:
    """データテーブル"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 columns: List[Tuple[str, int]], row_height: int = 40):
        self.rect = pygame.Rect(x, y, width, height)
        self.columns = columns  # [(name, width), ...]
        self.row_height = row_height
        self.header_height = 45
        self.data: List[List[str]] = []
        self.scroll_offset = 0
        self.selected_index = -1
        self.hover_index = -1
        self.on_select: Callable = None
    
    def set_data(self, data: List[List[str]]):
        self.data = data
        self.scroll_offset = 0
    
    def draw(self, surface: pygame.Surface):
        # カード背景
        draw_rounded_rect(surface, self.rect, Colors.BG_CARD, 12)
        draw_rounded_rect(surface, self.rect, Colors.BG_CARD, 12, 1, Colors.BORDER)
        
        # ヘッダー
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.header_height)
        draw_rounded_rect(surface, header_rect, Colors.BG_INPUT, 
                         border_top_left_radius=12, border_top_right_radius=12)
        
        x = self.rect.x + 15
        for col_name, col_width in self.columns:
            text_surf = fonts.small.render(col_name, True, Colors.TEXT_SECONDARY)
            surface.blit(text_surf, (x, self.rect.y + 13))
            x += col_width
        
        # 行
        content_rect = pygame.Rect(
            self.rect.x, self.rect.y + self.header_height,
            self.rect.width, self.rect.height - self.header_height
        )
        
        # クリップ
        clip = surface.get_clip()
        surface.set_clip(content_rect)
        
        y = self.rect.y + self.header_height
        visible_rows = (self.rect.height - self.header_height) // self.row_height
        
        for i in range(self.scroll_offset, min(len(self.data), self.scroll_offset + visible_rows + 1)):
            if y >= self.rect.bottom:
                break
            
            row_rect = pygame.Rect(self.rect.x + 2, y, self.rect.width - 4, self.row_height)
            
            # 選択・ホバー背景
            if i == self.selected_index:
                pygame.draw.rect(surface, (*Colors.PRIMARY[:3], 40), row_rect, border_radius=6)
            elif i == self.hover_index:
                pygame.draw.rect(surface, Colors.BG_CARD_HOVER, row_rect, border_radius=6)
            
            # データ
            x = self.rect.x + 15
            for j, (_, col_width) in enumerate(self.columns):
                if j < len(self.data[i]):
                    text = str(self.data[i][j])
                    text_surf = fonts.body.render(text[:20], True, Colors.TEXT_PRIMARY)
                    surface.blit(text_surf, (x, y + 10))
                x += col_width
            
            y += self.row_height
        
        surface.set_clip(clip)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                rel_y = event.pos[1] - self.rect.y - self.header_height
                if rel_y > 0:
                    self.hover_index = self.scroll_offset + rel_y // self.row_height
                    if self.hover_index >= len(self.data):
                        self.hover_index = -1
                else:
                    self.hover_index = -1
            else:
                self.hover_index = -1
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover_index >= 0 and self.hover_index < len(self.data):
                self.selected_index = self.hover_index
                if self.on_select:
                    self.on_select(self.selected_index)
                return True
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset = max(0, self.scroll_offset - event.y)
                max_scroll = max(0, len(self.data) - (self.rect.height - self.header_height) // self.row_height)
                self.scroll_offset = min(max_scroll, self.scroll_offset)
        
        return False


# ============================================================
# 通知トースト
# ============================================================
class Toast:
    """通知トースト"""
    
    def __init__(self, message: str, toast_type: str = "info", duration: float = 3.0):
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self.start_time = time.time()
        self.is_visible = True
        
        # 色設定
        type_colors = {
            "info": Colors.PRIMARY,
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "error": Colors.DANGER
        }
        self.color = type_colors.get(toast_type, Colors.PRIMARY)
    
    def update(self) -> bool:
        elapsed = time.time() - self.start_time
        if elapsed > self.duration:
            self.is_visible = False
        return self.is_visible
    
    def draw(self, surface: pygame.Surface, y_offset: int = 0):
        if not self.is_visible:
            return
        
        elapsed = time.time() - self.start_time
        
        # フェードイン/アウト
        if elapsed < 0.2:
            alpha = int(255 * elapsed / 0.2)
            slide = int(30 * (1 - elapsed / 0.2))
        elif elapsed > self.duration - 0.3:
            alpha = int(255 * (self.duration - elapsed) / 0.3)
            slide = 0
        else:
            alpha = 255
            slide = 0
        
        # サイズ計算
        text_surf = fonts.body.render(self.message, True, Colors.TEXT_PRIMARY)
        width = text_surf.get_width() + 40
        height = 45
        x = (surface.get_width() - width) // 2
        y = 20 + y_offset - slide
        
        # 背景
        toast_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(toast_surf, (*Colors.BG_CARD[:3], alpha), (0, 0, width, height), border_radius=8)
        
        # 左側のアクセント
        pygame.draw.rect(toast_surf, (*self.color[:3], alpha), (0, 0, 4, height),
                        border_top_left_radius=8, border_bottom_left_radius=8)
        
        # テキスト
        text_surf.set_alpha(alpha)
        toast_surf.blit(text_surf, (20, (height - text_surf.get_height()) // 2))
        
        surface.blit(toast_surf, (x, y))


class ToastManager:
    """トースト管理"""
    _toasts: List[Toast] = []
    
    @classmethod
    def show(cls, message: str, toast_type: str = "info", duration: float = 3.0):
        cls._toasts.append(Toast(message, toast_type, duration))
    
    @classmethod
    def update_and_draw(cls, surface: pygame.Surface):
        cls._toasts = [t for t in cls._toasts if t.update()]
        for i, toast in enumerate(cls._toasts):
            toast.draw(surface, i * 55)


# ============================================================
# レーダーチャート
# ============================================================
class RadarChart:
    """能力レーダーチャート"""
    
    def __init__(self, x: int, y: int, radius: int,
                 labels: List[str], values: List[int], max_value: int = 20):
        self.center = (x, y)
        self.radius = radius
        self.labels = labels
        self.values = values
        self.max_value = max_value
    
    def draw(self, surface: pygame.Surface):
        num_stats = len(self.labels)
        angle_step = 2 * math.pi / num_stats
        
        # グリッド
        for level in range(1, 5):
            points = []
            r = self.radius * level / 4
            for i in range(num_stats):
                angle = -math.pi / 2 + i * angle_step
                x = self.center[0] + r * math.cos(angle)
                y = self.center[1] + r * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(surface, Colors.BORDER, points, 1)
        
        # 軸
        for i in range(num_stats):
            angle = -math.pi / 2 + i * angle_step
            x = self.center[0] + self.radius * math.cos(angle)
            y = self.center[1] + self.radius * math.sin(angle)
            pygame.draw.line(surface, Colors.BORDER, self.center, (x, y), 1)
        
        # データ
        data_points = []
        for i, value in enumerate(self.values):
            ratio = value / self.max_value
            angle = -math.pi / 2 + i * angle_step
            x = self.center[0] + self.radius * ratio * math.cos(angle)
            y = self.center[1] + self.radius * ratio * math.sin(angle)
            data_points.append((x, y))
        
        # 塗りつぶし
        if len(data_points) >= 3:
            pygame.draw.polygon(surface, (*Colors.PRIMARY[:3], 60), data_points)
            pygame.draw.polygon(surface, Colors.PRIMARY, data_points, 2)
        
        # ポイント
        for point in data_points:
            pygame.draw.circle(surface, Colors.PRIMARY, (int(point[0]), int(point[1])), 5)
            pygame.draw.circle(surface, Colors.TEXT_PRIMARY, (int(point[0]), int(point[1])), 3)
        
        # ラベル
        for i, label in enumerate(self.labels):
            angle = -math.pi / 2 + i * angle_step
            x = self.center[0] + (self.radius + 25) * math.cos(angle)
            y = self.center[1] + (self.radius + 25) * math.sin(angle)
            
            text_surf = fonts.small.render(label, True, Colors.TEXT_SECONDARY)
            text_rect = text_surf.get_rect(center=(x, y))
            surface.blit(text_surf, text_rect)


# ============================================================
# 背景描画
# ============================================================
def draw_background(surface: pygame.Surface, pattern: str = "gradient", team_color: tuple = None):
    """背景を描画（スタイリッシュなグラデーション）"""
    width = surface.get_width()
    height = surface.get_height()
    
    if pattern == "gradient":
        # 滑らかなダークグラデーション
        for y in range(height):
            ratio = y / height
            r = int(12 + 14 * ratio)
            g = int(14 + 16 * ratio)
            b = int(20 + 18 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # 右側に微妙な装飾ライン（チームカラーがある場合）
        if team_color:
            for i in range(2):
                start_x = width - 250 + i * 80
                line_color = (team_color[0] // 6, team_color[1] // 6, team_color[2] // 6)
                pygame.draw.line(surface, line_color, (start_x, 0), (start_x - 150, height), 1)
    else:
        surface.fill(Colors.BG_DARK)


# ============================================================
# ヘッダー
# ============================================================
def draw_header(surface: pygame.Surface, title: str, subtitle: str = None,
                team_color: tuple = None):
    """ヘッダーを描画"""
    header_height = 120 if subtitle else 80
    header_rect = pygame.Rect(0, 0, surface.get_width(), header_height)
    
    # グラデーション背景
    if team_color:
        for y in range(header_height):
            ratio = y / header_height
            color = lerp_color(team_color, Colors.BG_DARK, ratio * 0.8)
            pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))
    else:
        pygame.draw.rect(surface, Colors.BG_CARD, header_rect)
    
    # 下線
    pygame.draw.line(surface, Colors.BORDER, (0, header_height - 1), 
                    (surface.get_width(), header_height - 1))
    
    # タイトル
    title_surf = fonts.h1.render(title, True, Colors.TEXT_PRIMARY)
    title_rect = title_surf.get_rect(center=(surface.get_width() // 2, 40 if subtitle else header_height // 2))
    surface.blit(title_surf, title_rect)
    
    # サブタイトル
    if subtitle:
        sub_surf = fonts.body.render(subtitle, True, Colors.TEXT_SECONDARY)
        sub_rect = sub_surf.get_rect(center=(surface.get_width() // 2, 80))
        surface.blit(sub_surf, sub_rect)
    
    return header_height


# グローバルエクスポート
__all__ = [
    'Colors', 'fonts', 'FontManager',
    'Button', 'Card', 'ProgressBar', 'InputField', 'Table',
    'Toast', 'ToastManager', 'RadarChart',
    'draw_background', 'draw_header', 'draw_rounded_rect', 'draw_shadow',
    'lerp_color', 'ease_out_cubic'
]
