# -*- coding: utf-8 -*-
"""
ペナントシミュレーター - プロフェッショナルUI
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
    """統一されたカラーパレット（プロフェッショナル・シャープ）"""
    # 背景（より深いダーク）
    BG_DARK = (12, 14, 18)        # よりダークに
    BG_CARD = (22, 26, 32)        # カード背景
    BG_CARD_HOVER = (32, 38, 48)  # ホバー時
    BG_HOVER = (32, 38, 48)       # エイリアス
    BG_INPUT = (18, 21, 27)       # 入力フィールド
    BG_DARKER = (8, 10, 13)       # 最も暗い背景
    
    # アクセント（シャープで落ち着いた色調）
    PRIMARY = (60, 100, 150)       # 深いブルー
    PRIMARY_HOVER = (75, 115, 165)
    PRIMARY_DARK = (45, 80, 120)
    PRIMARY_LIGHT = (80, 130, 180)
    
    SECONDARY = (90, 75, 130)      # 深いパープル
    SUCCESS = (50, 130, 80)        # 深いグリーン
    SUCCESS_HOVER = (65, 145, 95)
    WARNING = (170, 140, 50)       # 深いイエロー
    DANGER = (150, 70, 70)         # 深いレッド
    DANGER_HOVER = (165, 85, 85)
    INFO = (60, 120, 150)          # 深いシアン
    
    # テキスト（コントラスト強化）
    TEXT_PRIMARY = (235, 240, 245)
    TEXT_SECONDARY = (130, 140, 155)
    TEXT_MUTED = (85, 95, 110)
    TEXT_ACCENT = (100, 160, 220)  # アクセントテキスト
    
    # ボーダー（シャープなエッジ）
    BORDER = (45, 52, 65)
    BORDER_LIGHT = (60, 70, 85)
    BORDER_FOCUS = (70, 110, 160)  # フォーカス時
    
    # 特別色（控えめだが印象的）
    GOLD = (200, 170, 60)
    GOLD_LIGHT = (220, 195, 90)
    SILVER = (160, 170, 185)
    BRONZE = (180, 130, 70)


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


def draw_rounded_rect(surface, rect, color, radius=2, border=0, border_color=None):
    """角丸四角形を描画（シャープなデザイン）"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_shadow(surface, rect, offset=3, blur=6, alpha=50):
    """シャドウを描画（シャープなエッジ）"""
    shadow_surf = pygame.Surface((rect.width + blur*2, rect.height + blur*2), pygame.SRCALPHA)
    shadow_rect = pygame.Rect(blur, blur, rect.width, rect.height)
    pygame.draw.rect(shadow_surf, (0, 0, 0, alpha), shadow_rect, border_radius=2)
    surface.blit(shadow_surf, (rect.x - blur + offset, rect.y - blur + offset))


def draw_selection_effect(surface, rect, color=None, intensity=1.0):
    """選手選択時のエフェクトを描画（シャープなグロー）"""
    if color is None:
        color = Colors.PRIMARY
    
    # グロー効果（複数レイヤー - よりシャープに）
    glow_layers = [
        (6, 0.12 * intensity),
        (4, 0.20 * intensity),
        (2, 0.30 * intensity),
    ]
    
    for offset, alpha_mult in glow_layers:
        glow_rect = rect.inflate(offset * 2, offset * 2)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        glow_color = (*color[:3], int(70 * alpha_mult))
        pygame.draw.rect(glow_surf, glow_color, (0, 0, glow_rect.width, glow_rect.height), border_radius=2)
        surface.blit(glow_surf, glow_rect.topleft)
    
    # 枠線（シャープ）
    border_color = (*color[:3], int(220 * intensity))
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=1)


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
        """スタイルに応じた色を設定（落ち着いた色調）"""
        styles = {
            "primary": (Colors.PRIMARY, Colors.PRIMARY_HOVER, Colors.PRIMARY_DARK),
            "secondary": (Colors.SECONDARY, (115, 100, 155), (85, 70, 125)),
            "success": (Colors.SUCCESS, Colors.SUCCESS_HOVER, (50, 120, 75)),
            "danger": (Colors.DANGER, Colors.DANGER_HOVER, (140, 65, 65)),
            "warning": (Colors.WARNING, (195, 165, 75), (160, 130, 50)),
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
        
        # シャドウ（ホバー時 - よりシャープ）
        if self.hover_progress > 0.1 and self.enabled:
            shadow_alpha = int(40 * self.hover_progress)
            draw_shadow(surface, scaled_rect, 2, 4, shadow_alpha)
        
        # 背景（シャープなエッジ）
        draw_rounded_rect(surface, scaled_rect, bg_color, 3)
        
        # アウトラインスタイルの場合はボーダーを追加
        if self.style == "outline":
            border_color = lerp_color(Colors.BORDER, Colors.PRIMARY, self.hover_progress)
            draw_rounded_rect(surface, scaled_rect, bg_color, 3, 2, border_color)
        
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
        
        # 背景（シャープな角）
        bg_color = lerp_color(Colors.BG_CARD, Colors.BG_CARD_HOVER, self.hover_progress)
        draw_rounded_rect(surface, draw_rect, bg_color, 3)
        
        # ボーダー（シャープ）
        border_color = lerp_color(Colors.BORDER, Colors.PRIMARY, self.hover_progress * 0.5)
        draw_rounded_rect(surface, draw_rect, bg_color, 3, 1, border_color)
        
        # タイトル
        if self.title:
            title_surf = fonts.body.render(self.title, True, Colors.TEXT_PRIMARY)
            surface.blit(title_surf, (draw_rect.x + 15, draw_rect.y + 12))
        
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
        
        # 背景（シャープ）
        draw_rounded_rect(surface, self.rect, Colors.BG_INPUT, 2)
        
        # プログレス
        if self.display_value > 0:
            fill_width = int(self.rect.width * self.display_value)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            draw_rounded_rect(surface, fill_rect, self.color, 2)
        
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
        # 背景（シャープ）
        bg_color = Colors.BG_INPUT if not self.is_focused else Colors.BG_CARD_HOVER
        draw_rounded_rect(surface, self.rect, bg_color, 2)
        
        # ボーダー（シャープ）
        border_color = Colors.PRIMARY if self.is_focused else (
            Colors.BORDER_LIGHT if self.is_hovered else Colors.BORDER
        )
        draw_rounded_rect(surface, self.rect, bg_color, 2, 2, border_color)
        
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
        # カード背景（シャープ）
        draw_rounded_rect(surface, self.rect, Colors.BG_CARD, 3)
        draw_rounded_rect(surface, self.rect, Colors.BG_CARD, 3, 1, Colors.BORDER)
        
        # ヘッダー（シャープ）
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.header_height)
        pygame.draw.rect(surface, Colors.BG_INPUT, header_rect)
        
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
            
            # 選択・ホバー背景（シャープ）
            if i == self.selected_index:
                pygame.draw.rect(surface, (*Colors.PRIMARY[:3], 40), row_rect, border_radius=2)
            elif i == self.hover_index:
                pygame.draw.rect(surface, Colors.BG_CARD_HOVER, row_rect, border_radius=2)
            
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
        
        # 背景（シャープ）
        toast_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(toast_surf, (*Colors.BG_CARD[:3], alpha), (0, 0, width, height), border_radius=3)
        
        # 左側のアクセント（シャープ）
        pygame.draw.rect(toast_surf, (*self.color[:3], alpha), (0, 0, 4, height))
        
        # テキスト
        text_surf.set_alpha(alpha)
        toast_surf.blit(text_surf, (20, (height - text_surf.get_height()) // 2))
        
        surface.blit(toast_surf, (x, y))


class ToastManager:
    """トースト管理"""
    _toasts: List[Toast] = []
    _enabled: bool = False  # トースト通知を無効化
    
    @classmethod
    def show(cls, message: str, toast_type: str = "info", duration: float = 3.0):
        if cls._enabled:
            cls._toasts.append(Toast(message, toast_type, duration))
    
    @classmethod
    def update_and_draw(cls, surface: pygame.Surface):
        if not cls._enabled:
            return
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
    """背景を描画（プロフェッショナルなダークグラデーション）"""
    width = surface.get_width()
    height = surface.get_height()
    
    if pattern == "gradient":
        # 深いダークグラデーション（上から下へ）
        for y in range(height):
            ratio = y / height
            # 微妙なグラデーション（より暗く）
            r = int(8 + 10 * ratio)
            g = int(10 + 12 * ratio)
            b = int(14 + 14 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # 角のビネット効果（没入感向上）
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        for corner in [(0, 0), (width, 0), (0, height), (width, height)]:
            for radius in range(200, 0, -10):
                alpha = int(15 * (1 - radius / 200))
                pygame.draw.circle(vignette, (0, 0, 0, alpha), corner, radius)
        surface.blit(vignette, (0, 0))
        
        # チームカラーのサブトルなアクセント（右下角）
        if team_color:
            accent_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            # 対角線のグラデーション光
            for i in range(80):
                alpha = int(12 * (1 - i / 80))
                start_x = width - 300 + i * 3
                accent_color = (*team_color[:3], alpha)
                pygame.draw.line(accent_surf, accent_color, 
                               (start_x, height), (start_x + 200, 0), 1)
            surface.blit(accent_surf, (0, 0))
            
    elif pattern == "solid":
        surface.fill(Colors.BG_DARK)
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


# ============================================================
# 画面遷移エフェクト
# ============================================================
class ScreenTransition:
    """画面遷移エフェクト（没入感向上）"""
    
    def __init__(self, duration: float = 0.25):
        self.duration = duration
        self.start_time = 0
        self.is_active = False
        self.fade_in = True  # True=フェードイン, False=フェードアウト
    
    def start(self, fade_in: bool = True):
        """トランジション開始"""
        self.start_time = time.time()
        self.is_active = True
        self.fade_in = fade_in
    
    def update(self) -> bool:
        """更新。完了時にTrueを返す"""
        if not self.is_active:
            return True
        
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.is_active = False
            return True
        return False
    
    def draw(self, surface: pygame.Surface):
        """オーバーレイを描画"""
        if not self.is_active:
            return
        
        elapsed = time.time() - self.start_time
        progress = min(1.0, elapsed / self.duration)
        
        # イージング適用
        eased = ease_out_cubic(progress)
        
        if self.fade_in:
            alpha = int(255 * (1 - eased))
        else:
            alpha = int(255 * eased)
        
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((12, 14, 18, alpha))
        surface.blit(overlay, (0, 0))


# ============================================================
# パルス効果（選択項目のハイライト）
# ============================================================
class PulseEffect:
    """パルス効果（重要な項目のハイライト用）"""
    
    def __init__(self, rect: pygame.Rect, color: tuple = None, frequency: float = 2.0):
        self.rect = rect
        self.color = color or Colors.PRIMARY
        self.frequency = frequency
        self.start_time = time.time()
    
    def draw(self, surface: pygame.Surface):
        elapsed = time.time() - self.start_time
        pulse = (math.sin(elapsed * self.frequency * math.pi * 2) + 1) / 2
        
        # パルス強度（0.3～0.7）
        intensity = 0.3 + 0.4 * pulse
        
        # グロー描画
        glow_rect = self.rect.inflate(6, 6)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        glow_color = (*self.color[:3], int(80 * intensity))
        pygame.draw.rect(glow_surf, glow_color, (0, 0, glow_rect.width, glow_rect.height), border_radius=2)
        surface.blit(glow_surf, glow_rect.topleft)
        
        # 枠線
        border_alpha = int(180 + 75 * pulse)
        pygame.draw.rect(surface, (*self.color[:3], border_alpha), self.rect, 2, border_radius=1)


# ============================================================
# スコアボード表示（試合結果の没入感）
# ============================================================
def draw_scoreboard(surface: pygame.Surface, x: int, y: int, width: int,
                    home_name: str, away_name: str,
                    home_score: int, away_score: int,
                    inning: int = 0, is_top: bool = True,
                    home_color: tuple = None, away_color: tuple = None):
    """スコアボード描画（野球中継風）"""
    height = 100
    board_rect = pygame.Rect(x, y, width, height)
    
    # 背景（ダークでシャープ）
    pygame.draw.rect(surface, (15, 17, 22), board_rect, border_radius=2)
    pygame.draw.rect(surface, Colors.BORDER, board_rect, 1, border_radius=2)
    
    # チーム行
    row_height = 40
    half_width = width // 2
    
    for i, (name, score, team_color, is_batting) in enumerate([
        (away_name, away_score, away_color, is_top and inning > 0),
        (home_name, home_score, home_color, not is_top and inning > 0)
    ]):
        row_y = y + 10 + i * row_height
        
        # チームカラーアクセント
        if team_color:
            accent_rect = pygame.Rect(x + 2, row_y, 4, row_height - 5)
            pygame.draw.rect(surface, team_color, accent_rect)
        
        # 攻撃中インジケーター
        if is_batting:
            indicator_rect = pygame.Rect(x + 10, row_y + row_height // 2 - 4, 8, 8)
            pygame.draw.polygon(surface, Colors.GOLD, [
                (indicator_rect.x, indicator_rect.centery),
                (indicator_rect.right, indicator_rect.y),
                (indicator_rect.right, indicator_rect.bottom)
            ])
        
        # チーム名
        name_surf = fonts.h3.render(name[:10], True, Colors.TEXT_PRIMARY)
        surface.blit(name_surf, (x + 25, row_y + 5))
        
        # スコア
        score_surf = fonts.h2.render(str(score), True, Colors.TEXT_PRIMARY)
        score_rect = score_surf.get_rect(right=x + width - 15, centery=row_y + row_height // 2)
        surface.blit(score_surf, score_rect)
    
    # イニング表示
    if inning > 0:
        inning_str = f"{'▲' if is_top else '▼'}{inning}"
        inning_surf = fonts.body.render(inning_str, True, Colors.GOLD)
        inning_rect = inning_surf.get_rect(center=(x + width // 2, y + height - 15))
        surface.blit(inning_surf, inning_rect)
    
    return height


# グローバルエクスポート
__all__ = [
    'Colors', 'fonts', 'FontManager',
    'Button', 'Card', 'ProgressBar', 'InputField', 'Table',
    'Toast', 'ToastManager', 'RadarChart',
    'ScreenTransition', 'PulseEffect',
    'draw_background', 'draw_header', 'draw_rounded_rect', 'draw_shadow',
    'draw_scoreboard', 'draw_selection_effect',
    'lerp_color', 'ease_out_cubic'
]
