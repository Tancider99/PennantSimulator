# -*- coding: utf-8 -*-
"""
NPBペナントシミュレーター - 画面描画モジュール
すべての画面をプロフェッショナルなデザインで統一
"""
import pygame
import math
import time
import random
from typing import Dict, List, Optional, Tuple

from ui_pro import (
    Colors, fonts, FontManager,
    Button, Card, ProgressBar, Table, RadarChart,
    Toast, ToastManager,
    draw_background, draw_header, draw_rounded_rect, draw_shadow,
    lerp_color
)
from constants import (
    TEAM_COLORS, NPB_CENTRAL_TEAMS, NPB_PACIFIC_TEAMS,
    NPB_STADIUMS, TEAM_ABBREVIATIONS, NPB_BATTING_TITLES, NPB_PITCHING_TITLES
)
from game_state import DifficultyLevel
from models import Team, Player


class ScreenRenderer:
    """すべての画面を描画するレンダラー"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        fonts.init()  # フォント初期化
        self.title_animation_time = 0
        self.baseball_particles = []
    
    def get_team_color(self, team_name: str) -> tuple:
        """チームカラーを取得"""
        colors = TEAM_COLORS.get(team_name, (Colors.PRIMARY, Colors.TEXT_PRIMARY))
        if isinstance(colors, tuple) and len(colors) == 2 and isinstance(colors[0], tuple):
            return colors[0]  # プライマリカラーを返す
        return colors if isinstance(colors, tuple) else Colors.PRIMARY
    
    def get_team_abbr(self, team_name: str) -> str:
        """チーム略称を取得"""
        return TEAM_ABBREVIATIONS.get(team_name, team_name[:4])
    
    def get_stadium_name(self, team_name: str) -> str:
        """本拠地球場名を取得"""
        stadium = NPB_STADIUMS.get(team_name, {})
        return stadium.get("name", "球場")
    
    def _draw_gradient_background(self, team_color=None, style="default"):
        """共通のグラデーション背景を描画"""
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        # 基本グラデーション
        for y in range(height):
            ratio = y / height
            if style == "dark":
                r = int(15 + 12 * ratio)
                g = int(17 + 13 * ratio)
                b = int(22 + 16 * ratio)
            else:
                r = int(18 + 10 * ratio)
                g = int(20 + 12 * ratio)
                b = int(28 + 14 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (width, y))
        
        # チームカラーがある場合、装飾を追加
        if team_color:
            # 斜めのアクセントライン
            for i in range(3):
                start_x = width - 350 + i * 100
                line_alpha = 15 - i * 3
                line_color = (team_color[0] // 5, team_color[1] // 5, team_color[2] // 5)
                pygame.draw.line(self.screen, line_color, (start_x, 0), (start_x - 200, height), 2)
            
            # 上部アクセントライン
            pygame.draw.rect(self.screen, team_color, (0, 0, width, 3))
    
    # ========================================
    # タイトル画面
    # ========================================
    def draw_title_screen(self, show_start_menu: bool = False) -> Dict[str, Button]:
        """タイトル画面を描画（シンプル＆スタイリッシュ版）"""
        # シンプルな暗いグラデーション背景
        self._draw_gradient_background(style="dark")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        self.title_animation_time += 0.02
        
        # 中央に縦のアクセントライン（チームカラーのグラデーション）
        line_surf = pygame.Surface((4, height), pygame.SRCALPHA)
        for y in range(height):
            alpha = int(80 * (1 - abs(y - height/2) / (height/2)))
            line_surf.set_at((0, y), (*Colors.PRIMARY[:3], alpha))
            line_surf.set_at((1, y), (*Colors.PRIMARY[:3], alpha))
            line_surf.set_at((2, y), (*Colors.PRIMARY[:3], alpha))
            line_surf.set_at((3, y), (*Colors.PRIMARY[:3], alpha))
        self.screen.blit(line_surf, (center_x - 2, 0))
        
        # ロゴエリア
        logo_y = height // 3
        
        # メインタイトル（シンプルに）
        title_text = "PENNANT"
        title = fonts.title.render(title_text, True, Colors.TEXT_PRIMARY)
        title_rect = title.get_rect(center=(center_x, logo_y - 30))
        self.screen.blit(title, title_rect)
        
        # サブタイトル
        subtitle_text = "SIMULATOR"
        subtitle = fonts.h2.render(subtitle_text, True, Colors.TEXT_SECONDARY)
        subtitle_rect = subtitle.get_rect(center=(center_x, logo_y + 30))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 年度表示
        year_text = "2025"
        year_surf = fonts.tiny.render(year_text, True, Colors.PRIMARY)
        year_rect = year_surf.get_rect(center=(center_x, logo_y + 70))
        self.screen.blit(year_surf, year_rect)
        
        # ボタンエリア（シンプルに）
        btn_width = 250
        btn_height = 55
        btn_x = center_x - btn_width // 2
        btn_y = height // 2 + 50
        btn_spacing = 70
        
        buttons = {}
        
        if show_start_menu:
            # スタートメニュー表示中（ニューゲーム/ロード選択）
            # 半透明のオーバーレイ
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            # メニューボックス
            menu_w, menu_h = 320, 280
            menu_rect = pygame.Rect(center_x - menu_w // 2, height // 2 - menu_h // 2, menu_w, menu_h)
            draw_rounded_rect(self.screen, menu_rect, Colors.BG_CARD, 16)
            
            # タイトル
            menu_title = fonts.h2.render("GAME START", True, Colors.TEXT_PRIMARY)
            menu_title_rect = menu_title.get_rect(centerx=center_x, top=menu_rect.y + 25)
            self.screen.blit(menu_title, menu_title_rect)
            
            # ボタン
            menu_btn_y = menu_rect.y + 80
            menu_btn_spacing = 60
            
            buttons["new_game"] = Button(
                center_x - btn_width // 2, menu_btn_y, btn_width, btn_height,
                "NEW GAME", "primary", font=fonts.h3
            )
            
            buttons["load_game"] = Button(
                center_x - btn_width // 2, menu_btn_y + menu_btn_spacing, btn_width, btn_height,
                "LOAD GAME", "outline", font=fonts.body
            )
            
            buttons["back_to_title"] = Button(
                center_x - btn_width // 2, menu_btn_y + menu_btn_spacing * 2, btn_width, btn_height,
                "BACK", "ghost", font=fonts.body
            )
            
            for btn in buttons.values():
                btn.draw(self.screen)
        else:
            # 通常のタイトル画面
            # スタートボタン（プライマリ）
            buttons["start"] = Button(
                btn_x, btn_y, btn_width, btn_height,
                "START", "primary", font=fonts.h3
            )
            
            # 設定ボタン（ゴースト）
            buttons["settings"] = Button(
                btn_x, btn_y + btn_spacing, btn_width, btn_height,
                "SETTINGS", "ghost", font=fonts.body
            )
            
            # 終了ボタン（アウトライン）
            buttons["quit"] = Button(
                btn_x, btn_y + btn_spacing * 2, btn_width, btn_height,
                "QUIT", "outline", font=fonts.body
            )
            
            for btn in buttons.values():
                btn.draw(self.screen)
            
            # フッター
            footer = fonts.tiny.render("Press START to begin your journey", True, Colors.TEXT_MUTED)
            footer_rect = footer.get_rect(center=(center_x, height - 40))
            
            # 点滅エフェクト
            alpha = int(128 + 127 * math.sin(self.title_animation_time * 3))
            footer.set_alpha(alpha)
            self.screen.blit(footer, footer_rect)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    def draw_new_game_setup_screen(self, settings_obj, setup_state: dict = None) -> Dict[str, Button]:
        """新規ゲーム開始設定画面を描画
        
        Args:
            settings_obj: 設定オブジェクト（game_rulesを含む）
            setup_state: 設定状態を保持する辞書
        """
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        # デフォルト状態
        if setup_state is None:
            setup_state = {}
        
        # ヘッダー
        header_h = draw_header(self.screen, "NEW GAME")
        
        # サブヘッダー
        subtitle = fonts.body.render("ゲーム設定を確認してスタート", True, Colors.TEXT_SECONDARY)
        self.screen.blit(subtitle, (center_x - subtitle.get_width() // 2, header_h + 10))
        
        buttons = {}
        rules = settings_obj.game_rules
        
        # カードエリア開始位置
        card_top = header_h + 50
        
        # 画面幅に応じてレイアウト調整
        card_spacing = 15
        available_width = width - 60  # 左右30pxマージン
        
        if available_width >= 1100:
            # 3列レイアウト
            card_width = min(340, (available_width - card_spacing * 2) // 3)
            card_height = 220
            col1_x = 30
            col2_x = col1_x + card_width + card_spacing
            col3_x = col2_x + card_width + card_spacing
        else:
            # 2列レイアウト
            card_width = min(400, (available_width - card_spacing) // 2)
            card_height = 200
            col1_x = 30
            col2_x = col1_x + card_width + card_spacing
            col3_x = col1_x  # 3番目は下に配置
        
        # === 左カード: 難易度・モード設定 ===
        left_card = Card(col1_x, card_top, card_width, card_height, "難易度")
        left_rect = left_card.draw(self.screen)
        
        y = left_rect.y + 50
        
        # 難易度選択
        difficulty_options = [
            ("easy", "イージー", "のんびりプレイ"),
            ("normal", "ノーマル", "標準的な難易度"),
            ("hard", "ハード", "やりごたえあり"),
        ]
        
        current_diff = setup_state.get("difficulty", "normal")
        
        for key, label, desc in difficulty_options:
            is_selected = current_diff == key
            style = "primary" if is_selected else "ghost"
            
            btn = Button(left_rect.x + 15, y, card_width - 30, 38, label, style, font=fonts.body)
            btn.draw(self.screen)
            buttons[f"diff_{key}"] = btn
            
            y += 50
        
        # === 中央カード: DH制設定 ===
        center_card = Card(col2_x, card_top, card_width, card_height, "DH制ルール")
        center_rect = center_card.draw(self.screen)
        
        y = center_rect.y + 50
        
        dh_settings = [
            ("セリーグ DH制", "central_dh", rules.central_dh),
            ("パリーグ DH制", "pacific_dh", rules.pacific_dh),
            ("交流戦 DH", "interleague_dh", rules.interleague_dh),
        ]
        
        for label, key, value in dh_settings:
            label_surf = fonts.small.render(label, True, Colors.TEXT_PRIMARY)
            self.screen.blit(label_surf, (center_rect.x + 15, y + 8))
            
            status = "ON" if value else "OFF"
            style = "success" if value else "ghost"
            btn = Button(center_rect.right - 95, y, 75, 32, status, style, font=fonts.small)
            btn.draw(self.screen)
            buttons[f"setup_toggle_{key}"] = btn
            
            y += 45
        
        # === 右カード: シーズン設定 ===
        if available_width >= 1100:
            right_card_y = card_top
        else:
            right_card_y = card_top + card_height + card_spacing
            
        right_card = Card(col3_x if available_width >= 1100 else col2_x, 
                         right_card_y, card_width, card_height, "シーズン設定")
        right_rect = right_card.draw(self.screen)
        
        y = right_rect.y + 50
        
        # シーズン試合数
        label_surf = fonts.small.render("試合数", True, Colors.TEXT_PRIMARY)
        self.screen.blit(label_surf, (right_rect.x + 15, y))
        y += 28
        
        game_options = [120, 130, 143]
        btn_x = right_rect.x + 15
        btn_w = min(85, (card_width - 45) // 3)
        for games in game_options:
            is_selected = rules.regular_season_games == games
            style = "primary" if is_selected else "outline"
            btn = Button(btn_x, y, btn_w, 32, f"{games}", style, font=fonts.small)
            btn.draw(self.screen)
            buttons[f"setup_games_{games}"] = btn
            btn_x += btn_w + 10
        
        y += 50
        
        # シーズンイベント
        event_settings = [
            ("交流戦", "enable_interleague", rules.enable_interleague),
            ("CS", "enable_climax_series", rules.enable_climax_series),
            ("キャンプ", "enable_spring_camp", rules.enable_spring_camp),
        ]
        
        btn_x = right_rect.x + 15
        btn_w = min(90, (card_width - 40) // 3)
        for label, key, value in event_settings:
            style = "success" if value else "ghost"
            status_icon = "ON " if value else "OFF"
            btn = Button(btn_x, y, btn_w, 32, f"{status_icon}{label}", style, font=fonts.tiny)
            btn.draw(self.screen)
            buttons[f"setup_toggle_{key}"] = btn
            btn_x += btn_w + 5
        
        # === 下部カード: クイック設定 ===
        bottom_y = max(left_rect.bottom, center_rect.bottom, right_rect.bottom) + card_spacing
        bottom_card = Card(30, bottom_y, width - 60, 100, "クイック設定")
        bottom_rect = bottom_card.draw(self.screen)
        
        preset_y = bottom_rect.y + 50
        
        presets = [
            ("real_2024", "リアル2027"),
            ("classic", "クラシック"),
            ("short", "ショート"),
            ("full", "フル"),
        ]
        
        preset_btn_w = min(180, (width - 100) // 4)
        btn_x = bottom_rect.x + 20
        for key, label in presets:
            btn = Button(btn_x, preset_y, preset_btn_w, 40, label, "outline", font=fonts.small)
            btn.draw(self.screen)
            buttons[f"preset_{key}"] = btn
            btn_x += preset_btn_w + 15
        
        # === フッター: ボタンエリア ===
        footer_y = height - 80
        
        # 戻るボタン
        buttons["back_title"] = Button(
            30, footer_y, 140, 50,
            "タイトル", "ghost", font=fonts.body
        )
        buttons["back_title"].draw(self.screen)
        
        # 詳細設定ボタン
        buttons["advanced_settings"] = Button(
            center_x - 90, footer_y, 180, 50,
            "詳細設定", "outline", font=fonts.body
        )
        buttons["advanced_settings"].draw(self.screen)
        
        # ゲームスタートボタン
        buttons["confirm_start"] = Button(
            width - 200, footer_y, 170, 50,
            "ゲーム開始", "primary", font=fonts.h3
        )
        buttons["confirm_start"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    def _draw_baseball(self, x: int, y: int, radius: int):
        """野球ボールを描画"""
        # 白い円
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius)
        pygame.draw.circle(self.screen, (200, 200, 200), (x, y), radius, 2)
        
        # 縫い目（簡略版）
        seam_color = (200, 50, 50)
        # 左側の縫い目
        pygame.draw.arc(self.screen, seam_color, 
                       (x - radius - 5, y - radius//2, radius, radius), 
                       -0.5, 0.5, 2)
        # 右側の縫い目
        pygame.draw.arc(self.screen, seam_color,
                       (x + 5, y - radius//2, radius, radius),
                       2.6, 3.6, 2)
    
    def _draw_title_decorations(self, width: int, height: int):
        """タイトル画面の装飾を描画"""
        # チームカラーの斜めストライプ（非常に薄く）
        team_colors = [
            (255, 102, 0),   # 巨人
            (255, 215, 0),   # 阪神
            (0, 90, 180),    # DeNA
            (200, 0, 0),     # 広島
            (0, 60, 125),    # ヤクルト
            (0, 80, 165),    # 中日
        ]
        
        stripe_width = 150
        for i, color in enumerate(team_colors):
            x = (i * stripe_width + int(self.title_animation_time * 20)) % (width + stripe_width * 2) - stripe_width
            stripe_surf = pygame.Surface((stripe_width, height), pygame.SRCALPHA)
            pygame.draw.polygon(stripe_surf, (*color, 8), [
                (0, 0), (stripe_width, 0), 
                (stripe_width - 50, height), (-50, height)
            ])
            self.screen.blit(stripe_surf, (x, 0))
    
    def _draw_team_ticker(self, height: int):
        """画面下部にチーム名をスクロール表示"""
        all_teams = NPB_CENTRAL_TEAMS + NPB_PACIFIC_TEAMS
        
        ticker_y = height - 80
        ticker_text = "  |  ".join(all_teams)
        ticker_text = ticker_text + "  |  " + ticker_text  # 繰り返し
        
        # スクロールオフセット
        offset = int(self.title_animation_time * 50) % (len(all_teams) * 200)
        
        ticker_surf = fonts.small.render(ticker_text, True, Colors.TEXT_MUTED)
        self.screen.blit(ticker_surf, (-offset, ticker_y))

    # ========================================
    # 難易度選択画面
    # ========================================
    def draw_difficulty_screen(self, current_difficulty: DifficultyLevel) -> Dict[str, Button]:
        """難易度選択画面を描画"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        # ヘッダー
        header_h = draw_header(self.screen, "難易度選択", "ゲームの難しさを選択してください")
        
        # 難易度カード
        difficulties = [
            (DifficultyLevel.EASY, "イージー", "初心者向け", Colors.SUCCESS, "選手能力UP、相手弱体化"),
            (DifficultyLevel.NORMAL, "ノーマル", "標準的な難易度", Colors.PRIMARY, "バランスの取れた設定"),
            (DifficultyLevel.HARD, "ハード", "上級者向け", Colors.WARNING, "相手の能力強化"),
            (DifficultyLevel.VERY_HARD, "ベリーハード", "最高難度", Colors.DANGER, "極限の挑戦"),
        ]
        
        card_width = 220
        card_height = 200
        total_width = card_width * 4 + 30 * 3
        start_x = (width - total_width) // 2
        card_y = header_h + 60
        
        buttons = {}
        
        for i, (level, name, desc, color, detail) in enumerate(difficulties):
            x = start_x + i * (card_width + 30)
            
            # 選択中かどうか
            is_selected = current_difficulty == level
            
            # カード背景
            card_rect = pygame.Rect(x, card_y, card_width, card_height)
            
            if is_selected:
                draw_shadow(self.screen, card_rect, 4, 10, 50)
                bg_color = lerp_color(Colors.BG_CARD, color, 0.15)
                draw_rounded_rect(self.screen, card_rect, bg_color, 16)
                pygame.draw.rect(self.screen, color, card_rect, 3, border_radius=16)
            else:
                draw_shadow(self.screen, card_rect, 2, 6, 25)
                draw_rounded_rect(self.screen, card_rect, Colors.BG_CARD, 16)
                draw_rounded_rect(self.screen, card_rect, Colors.BG_CARD, 16, 1, Colors.BORDER)
            
            # アイコン（色付き円）
            pygame.draw.circle(self.screen, color, (x + card_width // 2, card_y + 45), 25)
            icon_text = fonts.h2.render(str(i + 1), True, Colors.TEXT_PRIMARY)
            icon_rect = icon_text.get_rect(center=(x + card_width // 2, card_y + 45))
            self.screen.blit(icon_text, icon_rect)
            
            # 難易度名
            name_surf = fonts.h3.render(name, True, Colors.TEXT_PRIMARY)
            name_rect = name_surf.get_rect(center=(x + card_width // 2, card_y + 95))
            self.screen.blit(name_surf, name_rect)
            
            # 説明
            desc_surf = fonts.small.render(desc, True, Colors.TEXT_SECONDARY)
            desc_rect = desc_surf.get_rect(center=(x + card_width // 2, card_y + 125))
            self.screen.blit(desc_surf, desc_rect)
            
            # 詳細
            detail_surf = fonts.tiny.render(detail, True, Colors.TEXT_MUTED)
            detail_rect = detail_surf.get_rect(center=(x + card_width // 2, card_y + 155))
            self.screen.blit(detail_surf, detail_rect)
            
            # ボタン（カード全体）
            btn = Button(x, card_y, card_width, card_height, "", "ghost")
            btn.callback = None  # 視覚的なボタン
            buttons[f"difficulty_{level.name}"] = btn
        
        # 決定ボタン
        btn_y = card_y + card_height + 60
        buttons["confirm"] = Button(
            center_x - 150, btn_y, 300, 60,
            "決定して次へ →", "success", font=fonts.h3
        )
        buttons["confirm"].draw(self.screen)
        
        # 戻るボタン
        buttons["back_title"] = Button(
            50, height - 80, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back_title"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # チーム選択画面（超強化版）
    # ========================================
    def draw_team_select_screen(self, central_teams: List, pacific_teams: List, 
                                   custom_names: Dict = None, selected_team_name: str = None,
                                   preview_scroll: int = 0) -> Dict[str, Button]:
        """チーム選択画面を描画（超強化版 - スクロール対応）"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        custom_names = custom_names or {}
        
        # ヘッダー
        header_h = draw_header(self.screen, "TEAM SELECT", "監督としてチームを率いる球団を選んでください")
        
        buttons = {}
        
        # チーム名編集ボタン
        edit_names_btn = Button(
            width - 200, header_h - 45, 160, 36,
            "チーム名編集", "ghost", font=fonts.small
        )
        edit_names_btn.draw(self.screen)
        buttons["edit_team_names"] = edit_names_btn
        
        # 左側: チームリスト（2リーグ）
        list_width = 420
        panel_height = height - header_h - 50
        
        # 選択されたチームを見つける
        all_teams = central_teams + pacific_teams
        selected_team = None
        if selected_team_name:
            for team in all_teams:
                if team.name == selected_team_name:
                    selected_team = team
                    break
        
        mouse_pos = pygame.mouse.get_pos()
        hovered_team = None
        hovered_team_obj = None
        
        # リーグパネル（左側）
        leagues = [
            ("セントラル・リーグ", central_teams, 25, Colors.PRIMARY),
            ("パシフィック・リーグ", pacific_teams, 25 + list_width // 2 + 10, Colors.DANGER),
        ]
        
        for league_name, teams, panel_x, accent_color in leagues:
            # パネル背景
            panel_w = list_width // 2 - 5
            panel_rect = pygame.Rect(panel_x, header_h + 15, panel_w, panel_height)
            draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 12)
            draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 12, 1, Colors.BORDER)
            
            # リーグ名
            league_surf = fonts.body.render(league_name, True, accent_color)
            league_rect = league_surf.get_rect(center=(panel_x + panel_w // 2, header_h + 38))
            self.screen.blit(league_surf, league_rect)
            
            # 区切り線
            pygame.draw.line(self.screen, Colors.BORDER,
                           (panel_x + 15, header_h + 58),
                           (panel_x + panel_w - 15, header_h + 58), 1)
            
            # チームボタン
            btn_width = panel_w - 24
            btn_height = 68
            btn_x = panel_x + 12
            btn_y = header_h + 70
            btn_spacing = 74
            
            for i, team in enumerate(teams):
                team_color = self.get_team_color(team.name)
                btn_rect = pygame.Rect(btn_x, btn_y + i * btn_spacing, btn_width, btn_height)
                
                # ホバー・選択検出
                is_hovered = btn_rect.collidepoint(mouse_pos)
                is_selected = selected_team_name == team.name
                
                if is_hovered:
                    hovered_team = team.name
                    hovered_team_obj = team
                
                # ボタン背景
                if is_selected:
                    bg_color = lerp_color(Colors.BG_CARD, team_color, 0.35)
                    border_color = team_color
                elif is_hovered:
                    bg_color = lerp_color(Colors.BG_CARD, team_color, 0.2)
                    border_color = Colors.BORDER_LIGHT
                else:
                    bg_color = lerp_color(Colors.BG_CARD, team_color, 0.08)
                    border_color = Colors.BORDER
                
                draw_rounded_rect(self.screen, btn_rect, bg_color, 10)
                draw_rounded_rect(self.screen, btn_rect, bg_color, 10, 2 if is_selected else 1, border_color)
                
                # チームカラーのアクセント
                color_rect = pygame.Rect(btn_x, btn_y + i * btn_spacing, 5, btn_height)
                pygame.draw.rect(self.screen, team_color, color_rect, border_radius=2)
                
                # チーム名
                display_name = custom_names.get(team.name, team.name)
                team_name_surf = fonts.body.render(display_name, True, Colors.TEXT_PRIMARY)
                self.screen.blit(team_name_surf, (btn_x + 15, btn_y + i * btn_spacing + 10))
                
                # 総合戦力（5段階バー）
                power_rating = self._calculate_team_power(team)
                power_y = btn_y + i * btn_spacing + 38
                power_label = fonts.tiny.render("戦力:", True, Colors.TEXT_MUTED)
                self.screen.blit(power_label, (btn_x + 15, power_y))
                
                # 5つ星表示
                star_x = btn_x + 55
                for s in range(5):
                    star_color = Colors.GOLD if s < power_rating else Colors.BORDER
                    star_surf = fonts.tiny.render("★", True, star_color)
                    self.screen.blit(star_surf, (star_x + s * 14, power_y - 1))
                
                # 登録ボタン（選択用）
                btn = Button(
                    btn_x, btn_y + i * btn_spacing, btn_width, btn_height,
                    "", "ghost", font=fonts.body
                )
                btn.is_hovered = is_hovered
                buttons[f"team_{team.name}"] = btn
        
        # 右側: 選択したチームの詳細プレビュー
        preview_x = 25 + list_width + 20
        preview_width = width - preview_x - 25
        
        # プレビューチーム（選択優先）
        preview_team = selected_team or hovered_team_obj
        
        if preview_team:
            self._draw_team_preview_panel_scrollable(preview_team, preview_x, header_h + 15, 
                                          preview_width, panel_height, custom_names, buttons, preview_scroll)
        else:
            # 未選択時のガイド
            self._draw_team_select_guide(preview_x, header_h + 15, preview_width, panel_height)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    def _calculate_team_power(self, team) -> int:
        """チームの総合戦力を5段階で計算"""
        if not team.players:
            return 3
        
        total_overall = sum(
            p.stats.overall_batting() if p.position.value != "P" else p.stats.overall_pitching()
            for p in team.players[:25]
        )
        avg_overall = total_overall / min(25, len(team.players))
        
        if avg_overall >= 14:
            return 5
        elif avg_overall >= 12:
            return 4
        elif avg_overall >= 10:
            return 3
        elif avg_overall >= 8:
            return 2
        else:
            return 1
    
    def _draw_team_preview_panel(self, team, x: int, y: int, width: int, height: int, 
                                  custom_names: Dict, buttons: Dict):
        """チーム詳細プレビューパネル（レガシー互換）"""
        self._draw_team_preview_panel_scrollable(team, x, y, width, height, custom_names, buttons, 0)
    
    def _draw_team_preview_panel_scrollable(self, team, x: int, y: int, width: int, height: int, 
                                  custom_names: Dict, buttons: Dict, scroll_offset: int = 0):
        """チーム詳細プレビューパネル（スクロール対応）"""
        team_color = self.get_team_color(team.name)
        
        # メインパネル背景
        panel_rect = pygame.Rect(x, y, width, height)
        draw_shadow(self.screen, panel_rect, 3, 8, 30)
        draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 16)
        
        # クリッピング領域を設定
        clip_rect = pygame.Rect(x, y, width, height - 70)  # 下部ボタン分を除く
        
        # チームカラーのヘッダー（固定）
        header_rect = pygame.Rect(x, y, width, 70)
        draw_rounded_rect(self.screen, header_rect, lerp_color(Colors.BG_CARD, team_color, 0.2), 16)
        
        # チーム名
        display_name = custom_names.get(team.name, team.name)
        team_name_surf = fonts.h2.render(display_name, True, team_color)
        self.screen.blit(team_name_surf, (x + 20, y + 12))
        
        # 球場情報
        stadium = NPB_STADIUMS.get(team.name, {})
        if stadium:
            stadium_text = f"{stadium.get('name', '')} / {stadium.get('location', '')}"
            stadium_surf = fonts.tiny.render(stadium_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(stadium_surf, (x + 20, y + 45))
        
        # スクロール可能なコンテンツエリア
        content_y = y + 80 - scroll_offset
        content_start_y = y + 80
        content_end_y = y + height - 80
        
        # クリッピング
        self.screen.set_clip(pygame.Rect(x, content_start_y, width, content_end_y - content_start_y))
        
        # ===== 戦力分析（コンパクト版）=====
        if content_y + 100 > content_start_y and content_y < content_end_y:
            analysis_rect = pygame.Rect(x + 12, content_y, width - 24, 90)
            draw_rounded_rect(self.screen, analysis_rect, Colors.BG_INPUT, 10)
            
            analysis_label = fonts.small.render("戦力分析", True, Colors.TEXT_PRIMARY)
            self.screen.blit(analysis_label, (x + 22, content_y + 8))
            
            # 攻撃力・守備力・投手力を計算
            batters = [p for p in team.players if p.position.value != "P"]
            pitchers = [p for p in team.players if p.position.value == "P"]
            
            offense_power = sum(p.stats.contact + p.stats.power for p in batters[:9]) / max(1, len(batters[:9])) / 2
            defense_power = sum(p.stats.fielding + p.stats.arm for p in batters[:9]) / max(1, len(batters[:9])) / 2
            pitching_power = sum(p.stats.speed + p.stats.control for p in pitchers[:6]) / max(1, len(pitchers[:6])) / 2
            
            # 3つのバー（横並び）
            bar_items = [
                ("攻撃", offense_power / 20, Colors.DANGER),
                ("守備", defense_power / 20, Colors.SUCCESS),
                ("投手", pitching_power / 20, Colors.PRIMARY),
            ]
            
            bar_width = (width - 80) // 3
            for i, (label, value, color) in enumerate(bar_items):
                bx = x + 22 + i * (bar_width + 10)
                by = content_y + 35
                
                label_surf = fonts.tiny.render(label, True, Colors.TEXT_MUTED)
                self.screen.blit(label_surf, (bx, by))
                
                bar = ProgressBar(bx, by + 18, bar_width - 10, 12, min(1.0, value), color)
                bar.draw(self.screen)
                
                value_surf = fonts.tiny.render(f"{int(value * 100)}%", True, Colors.TEXT_MUTED)
                self.screen.blit(value_surf, (bx + bar_width - 40, by))
        
        content_y += 100
        
        # ===== 主力野手 =====
        if content_y + 150 > content_start_y and content_y < content_end_y:
            batter_rect = pygame.Rect(x + 12, content_y, width - 24, 145)
            draw_rounded_rect(self.screen, batter_rect, Colors.BG_INPUT, 10)
            
            batter_label = fonts.small.render("主力野手", True, Colors.TEXT_PRIMARY)
            self.screen.blit(batter_label, (x + 22, content_y + 8))
            
            top_batters = sorted(batters, key=lambda p: p.stats.overall_batting(), reverse=True)[:5]
            for i, player in enumerate(top_batters):
                py = content_y + 32 + i * 22
                
                pos_surf = fonts.tiny.render(player.position.value, True, Colors.TEXT_SECONDARY)
                self.screen.blit(pos_surf, (x + 22, py))
                
                name_surf = fonts.small.render(player.name[:8], True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (x + 55, py - 2))
                
                # 能力値
                overall = player.stats.overall_batting()
                badge_color = self._get_overall_color(overall)
                badge_surf = fonts.tiny.render(f"総合{overall:.0f}", True, badge_color)
                self.screen.blit(badge_surf, (x + width - 80, py))
        
        content_y += 155
        
        # ===== 主力投手 =====
        if content_y + 150 > content_start_y and content_y < content_end_y:
            pitcher_rect = pygame.Rect(x + 12, content_y, width - 24, 145)
            draw_rounded_rect(self.screen, pitcher_rect, Colors.BG_INPUT, 10)
            
            pitcher_label = fonts.small.render("主力投手", True, Colors.TEXT_PRIMARY)
            self.screen.blit(pitcher_label, (x + 22, content_y + 8))
            
            top_pitchers = sorted(pitchers, key=lambda p: p.stats.overall_pitching(), reverse=True)[:5]
            for i, player in enumerate(top_pitchers):
                py = content_y + 32 + i * 22
                
                role = "先発" if i < 3 else "中継"
                pos_surf = fonts.tiny.render(role, True, Colors.TEXT_SECONDARY)
                self.screen.blit(pos_surf, (x + 22, py))
                
                name_surf = fonts.small.render(player.name[:8], True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (x + 55, py - 2))
                
                overall = player.stats.overall_pitching()
                badge_color = self._get_overall_color(overall)
                badge_surf = fonts.tiny.render(f"総合{overall:.0f}", True, badge_color)
                self.screen.blit(badge_surf, (x + width - 80, py))
        
        content_y += 155
        
        # ===== 球場情報 =====
        if content_y + 80 > content_start_y and content_y < content_end_y:
            stadium_rect = pygame.Rect(x + 12, content_y, width - 24, 75)
            draw_rounded_rect(self.screen, stadium_rect, Colors.BG_INPUT, 10)
            
            stadium_label = fonts.small.render("球場特性", True, Colors.TEXT_PRIMARY)
            self.screen.blit(stadium_label, (x + 22, content_y + 8))
            
            if stadium:
                sy = content_y + 35
                
                cap_text = f"収容: {stadium.get('capacity', 0):,}人"
                cap_surf = fonts.tiny.render(cap_text, True, Colors.TEXT_SECONDARY)
                self.screen.blit(cap_surf, (x + 22, sy))
                
                hr_factor = stadium.get("home_run_factor", 1.0)
                hr_text = f"HR係数: {hr_factor:.2f}"
                hr_color = Colors.DANGER if hr_factor > 1.0 else Colors.SUCCESS if hr_factor < 1.0 else Colors.TEXT_PRIMARY
                hr_surf = fonts.tiny.render(hr_text, True, hr_color)
                self.screen.blit(hr_surf, (x + 130, sy))
                
                if hr_factor > 1.05:
                    type_text = "打者有利"
                    type_color = Colors.DANGER
                elif hr_factor < 0.95:
                    type_text = "投手有利"
                    type_color = Colors.SUCCESS
                else:
                    type_text = "標準"
                    type_color = Colors.TEXT_MUTED
                type_surf = fonts.tiny.render(type_text, True, type_color)
                self.screen.blit(type_surf, (x + 240, sy))
        
        # クリッピング解除
        self.screen.set_clip(None)
        
        # 下部に固定ボタンエリア
        btn_area_rect = pygame.Rect(x, y + height - 70, width, 70)
        draw_rounded_rect(self.screen, btn_area_rect, Colors.BG_CARD, 0)
        
        # 決定ボタン
        confirm_btn = Button(
            x + 12, y + height - 60, width - 24, 50,
            f"{display_name} で始める", "success", font=fonts.h3
        )
        confirm_btn.draw(self.screen)
        buttons["confirm_team"] = confirm_btn
        
        # スクロールインジケーター（内容が多い場合）
        total_content_height = 100 + 155 + 155 + 80  # 各セクションの高さの合計
        visible_height = height - 150  # ヘッダーとボタンを除く
        
        if total_content_height > visible_height:
            # スクロールバー
            scrollbar_height = max(30, int(visible_height * visible_height / total_content_height))
            scrollbar_y = y + 80 + int((visible_height - scrollbar_height) * scroll_offset / max(1, total_content_height - visible_height))
            scrollbar_rect = pygame.Rect(x + width - 8, scrollbar_y, 4, scrollbar_height)
            pygame.draw.rect(self.screen, Colors.BORDER_LIGHT, scrollbar_rect, border_radius=2)
    
    def _draw_team_select_guide(self, x: int, y: int, width: int, height: int):
        """チーム未選択時のガイド"""
        panel_rect = pygame.Rect(x, y, width, height)
        draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 16)
        draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 16, 1, Colors.BORDER)
        
        # 中央にガイドテキスト
        center_x = x + width // 2
        center_y = y + height // 2
        
        # アイコン
        icon_surf = fonts.h1.render("TEAM", True, Colors.TEXT_MUTED)
        icon_rect = icon_surf.get_rect(center=(center_x, center_y - 50))
        self.screen.blit(icon_surf, icon_rect)
        
        # メインテキスト
        text1 = "チームを選択してください"
        text1_surf = fonts.h2.render(text1, True, Colors.TEXT_SECONDARY)
        text1_rect = text1_surf.get_rect(center=(center_x, center_y + 10))
        self.screen.blit(text1_surf, text1_rect)
        
        # サブテキスト
        text2 = "左のリストからチームをクリックすると"
        text3 = "詳細情報が表示されます"
        text2_surf = fonts.body.render(text2, True, Colors.TEXT_MUTED)
        text3_surf = fonts.body.render(text3, True, Colors.TEXT_MUTED)
        text2_rect = text2_surf.get_rect(center=(center_x, center_y + 60))
        text3_rect = text3_surf.get_rect(center=(center_x, center_y + 85))
        self.screen.blit(text2_surf, text2_rect)
        self.screen.blit(text3_surf, text3_rect)
    
    def _get_overall_color(self, overall: float) -> tuple:
        """総合力に応じた色を返す"""
        if overall >= 16:
            return Colors.GOLD
        elif overall >= 14:
            return Colors.SUCCESS
        elif overall >= 12:
            return Colors.PRIMARY
        elif overall >= 10:
            return Colors.TEXT_PRIMARY
        else:
            return Colors.TEXT_MUTED
    
    def _draw_team_info_tooltip(self, team_name: str, mouse_pos: tuple):
        """チーム情報のツールチップを描画（レガシー互換用）"""
        stadium = NPB_STADIUMS.get(team_name, {})
        if not stadium:
            return
        
        # ツールチップの内容
        lines = [
            f"{stadium.get('location', '')}",
            f"{stadium.get('name', '')}",
            f"収容: {stadium.get('capacity', 0):,}人",
            f"HR係数: {stadium.get('home_run_factor', 1.0):.2f}",
        ]
        
        # サイズ計算
        max_width = max(fonts.small.size(line)[0] for line in lines) + 30
        tooltip_height = len(lines) * 25 + 20
        
        # 位置調整（画面外に出ないように）
        x = min(mouse_pos[0] + 20, self.screen.get_width() - max_width - 10)
        y = min(mouse_pos[1] + 20, self.screen.get_height() - tooltip_height - 10)
        
        # 背景
        tooltip_rect = pygame.Rect(x, y, max_width, tooltip_height)
        draw_shadow(self.screen, tooltip_rect, 3, 6, 40)
        draw_rounded_rect(self.screen, tooltip_rect, Colors.BG_CARD, 8)
        draw_rounded_rect(self.screen, tooltip_rect, Colors.BG_CARD, 8, 1, Colors.BORDER_LIGHT)
        
        # テキスト
        text_y = y + 10
        for line in lines:
            line_surf = fonts.small.render(line, True, Colors.TEXT_PRIMARY)
            self.screen.blit(line_surf, (x + 15, text_y))
            text_y += 25

    # ========================================
    # メインメニュー画面（スタイリッシュ版）
    # ========================================
    def draw_menu_screen(self, player_team, current_year: int, schedule_manager, news_list: list = None, central_teams: list = None, pacific_teams: list = None) -> Dict[str, Button]:
        """メインメニュー画面を描画（洗練されたスポーツデザイン）"""
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        # グラデーション背景
        for y in range(height):
            ratio = y / height
            r = int(18 + 8 * ratio)
            g = int(20 + 10 * ratio)
            b = int(28 + 12 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (width, y))
        
        team_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        
        # 装飾ライン（斜めのアクセント）
        line_color = (*team_color[:3], 30) if len(team_color) == 3 else team_color
        for i in range(3):
            start_x = width - 300 + i * 80
            pygame.draw.line(self.screen, (team_color[0]//4, team_color[1]//4, team_color[2]//4), 
                           (start_x, 0), (start_x - 150, height), 2)
        
        # 上部アクセントライン
        pygame.draw.rect(self.screen, team_color, (0, 0, width, 3))
        
        buttons = {}
        
        # ========================================
        # 左上: チーム情報
        # ========================================
        if player_team:
            # チーム略称
            abbr = self.get_team_abbr(player_team.name)
            abbr_surf = fonts.title.render(abbr, True, team_color)
            self.screen.blit(abbr_surf, (30, 20))
            
            # チーム名
            team_name_surf = fonts.body.render(player_team.name, True, Colors.TEXT_SECONDARY)
            self.screen.blit(team_name_surf, (30, 75))
            
            # シーズン
            year_surf = fonts.small.render(f"{current_year}年シーズン", True, Colors.TEXT_MUTED)
            self.screen.blit(year_surf, (30, 100))
            
            # 成績
            record_y = 135
            record_surf = fonts.h2.render(f"{player_team.wins} - {player_team.losses} - {player_team.draws}", True, Colors.TEXT_PRIMARY)
            self.screen.blit(record_surf, (30, record_y))
            
            # 勝率
            rate = player_team.win_rate if player_team.games_played > 0 else 0
            rate_text = f"勝率 .{int(rate * 1000):03d}"
            rate_surf = fonts.body.render(rate_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(rate_surf, (30, record_y + 40))
            
            # 試合進行
            progress_text = f"{player_team.games_played} / 143 試合"
            progress_surf = fonts.small.render(progress_text, True, Colors.TEXT_MUTED)
            self.screen.blit(progress_surf, (30, record_y + 65))
        
        # ========================================
        # 左側: 次の試合情報
        # ========================================
        next_game = None
        if schedule_manager and player_team:
            next_game = schedule_manager.get_next_game_for_team(player_team.name)
        
        game_y = 245
        next_label = fonts.small.render("NEXT GAME", True, Colors.TEXT_MUTED)
        self.screen.blit(next_label, (30, game_y))
        
        if next_game:
            is_home = next_game.home_team_name == player_team.name
            opponent = next_game.away_team_name if is_home else next_game.home_team_name
            opp_abbr = self.get_team_abbr(opponent)
            
            # 対戦カード
            my_abbr = self.get_team_abbr(player_team.name)
            vs_text = f"{my_abbr}  vs  {opp_abbr}"
            vs_surf = fonts.h3.render(vs_text, True, Colors.TEXT_PRIMARY)
            self.screen.blit(vs_surf, (30, game_y + 25))
            
            # HOME/AWAY
            location = "（ホーム）" if is_home else "（アウェイ）"
            loc_surf = fonts.small.render(location, True, Colors.TEXT_MUTED)
            self.screen.blit(loc_surf, (30, game_y + 55))
        else:
            end_surf = fonts.h3.render("シーズン終了", True, Colors.GOLD)
            self.screen.blit(end_surf, (30, game_y + 25))
        
        # ========================================
        # 左側: ニュース（最新5件）
        # ========================================
        news_y = 340
        news_label = fonts.small.render("NEWS", True, Colors.TEXT_MUTED)
        self.screen.blit(news_label, (30, news_y))
        
        if news_list and len(news_list) > 0:
            for i, news_item in enumerate(news_list[:5]):
                # news_itemはdict形式 {"date": "...", "text": "..."} または文字列
                if isinstance(news_item, dict):
                    date_str = news_item.get("date", "")
                    text_str = news_item.get("text", "")
                    news_text = f"[{date_str}] {text_str}"
                else:
                    news_text = str(news_item)
                
                # 長すぎる場合は省略
                if len(news_text) > 35:
                    news_text = news_text[:35] + "..."
                
                news_surf = fonts.tiny.render(news_text, True, Colors.TEXT_SECONDARY)
                self.screen.blit(news_surf, (30, news_y + 22 + i * 20))
        else:
            no_news = fonts.tiny.render("ニュースはありません", True, Colors.TEXT_MUTED)
            self.screen.blit(no_news, (30, news_y + 22))
        
        # ========================================
        # 中央下部: 両リーグ順位表
        # ========================================
        standings_y = height - 220
        standings_width = 200
        
        # セ・リーグ
        cl_x = 30
        cl_label = fonts.small.render("セ・リーグ", True, Colors.TEXT_MUTED)
        self.screen.blit(cl_label, (cl_x, standings_y))
        
        if central_teams:
            c_teams = sorted(central_teams, key=lambda t: (t.wins - t.losses, t.wins), reverse=True)
            for i, team in enumerate(c_teams[:6]):
                is_player = player_team and team.name == player_team.name
                t_abbr = self.get_team_abbr(team.name)
                t_color = self.get_team_color(team.name)
                
                y = standings_y + 22 + i * 22
                
                # 順位
                rank_surf = fonts.tiny.render(f"{i+1}", True, Colors.TEXT_MUTED)
                self.screen.blit(rank_surf, (cl_x, y))
                
                # チーム名
                name_color = t_color if is_player else Colors.TEXT_SECONDARY
                name_surf = fonts.tiny.render(t_abbr, True, name_color)
                self.screen.blit(name_surf, (cl_x + 25, y))
                
                # 勝敗
                record_text = f"{team.wins}-{team.losses}"
                record_surf = fonts.tiny.render(record_text, True, Colors.TEXT_MUTED)
                self.screen.blit(record_surf, (cl_x + 85, y))
                
                # 勝率
                rate = team.win_rate if team.games_played > 0 else 0
                rate_text = f".{int(rate * 1000):03d}"
                rate_surf = fonts.tiny.render(rate_text, True, Colors.TEXT_MUTED)
                self.screen.blit(rate_surf, (cl_x + 140, y))
        
        # パ・リーグ
        pl_x = cl_x + standings_width + 30
        pl_label = fonts.small.render("パ・リーグ", True, Colors.TEXT_MUTED)
        self.screen.blit(pl_label, (pl_x, standings_y))
        
        if pacific_teams:
            p_teams = sorted(pacific_teams, key=lambda t: (t.wins - t.losses, t.wins), reverse=True)
            for i, team in enumerate(p_teams[:6]):
                is_player = player_team and team.name == player_team.name
                t_abbr = self.get_team_abbr(team.name)
                t_color = self.get_team_color(team.name)
                
                y = standings_y + 22 + i * 22
                
                # 順位
                rank_surf = fonts.tiny.render(f"{i+1}", True, Colors.TEXT_MUTED)
                self.screen.blit(rank_surf, (pl_x, y))
                
                # チーム名
                name_color = t_color if is_player else Colors.TEXT_SECONDARY
                name_surf = fonts.tiny.render(t_abbr, True, name_color)
                self.screen.blit(name_surf, (pl_x + 25, y))
                
                # 勝敗
                record_text = f"{team.wins}-{team.losses}"
                record_surf = fonts.tiny.render(record_text, True, Colors.TEXT_MUTED)
                self.screen.blit(record_surf, (pl_x + 85, y))
                
                # 勝率
                rate = team.win_rate if team.games_played > 0 else 0
                rate_text = f".{int(rate * 1000):03d}"
                rate_surf = fonts.tiny.render(rate_text, True, Colors.TEXT_MUTED)
                self.screen.blit(rate_surf, (pl_x + 140, y))
        
        # ========================================
        # 右下: メニューボタン（小型・英語+日本語）
        # ========================================
        btn_w = 120
        btn_h = 50
        btn_gap = 8
        # 右下に配置（3行2列 + システムボタン1行）
        total_btn_height = (btn_h + btn_gap) * 3 + 15 + 32  # メニュー3行 + gap + システム1行
        btn_area_x = width - 275
        btn_area_y = height - total_btn_height - 25  # 下から配置
        
        menu_buttons = [
            ("start_game", "PLAY", "試合"),
            ("roster", "ROSTER", "編成"),
            ("schedule", "SCHEDULE", "日程"),
            ("training", "TRAINING", "育成"),
            ("management", "FINANCE", "経営"),
            ("records", "RECORDS", "記録"),
        ]
        
        for i, (name, en_label, jp_label) in enumerate(menu_buttons):
            col = i % 2
            row = i // 2
            bx = btn_area_x + col * (btn_w + btn_gap)
            by = btn_area_y + row * (btn_h + btn_gap)
            
            # ボタン背景
            btn_rect = pygame.Rect(bx, by, btn_w, btn_h)
            
            # PLAYボタンは特別な色
            if name == "start_game":
                pygame.draw.rect(self.screen, (40, 45, 55), btn_rect, border_radius=8)
                pygame.draw.rect(self.screen, team_color, btn_rect, 2, border_radius=8)
            else:
                pygame.draw.rect(self.screen, (35, 38, 48), btn_rect, border_radius=8)
                pygame.draw.rect(self.screen, (60, 65, 75), btn_rect, 1, border_radius=8)
            
            # 英語ラベル
            en_surf = fonts.small.render(en_label, True, Colors.TEXT_PRIMARY)
            en_rect = en_surf.get_rect(centerx=bx + btn_w // 2, top=by + 8)
            self.screen.blit(en_surf, en_rect)
            
            # 日本語ラベル
            jp_surf = fonts.tiny.render(jp_label, True, Colors.TEXT_MUTED)
            jp_rect = jp_surf.get_rect(centerx=bx + btn_w // 2, top=by + 28)
            self.screen.blit(jp_surf, jp_rect)
            
            btn = Button(bx, by, btn_w, btn_h, "", "ghost")
            buttons[name] = btn
        
        # システムボタン（右下最下部）
        sys_y = btn_area_y + (btn_h + btn_gap) * 3 + 15
        sys_btn_w = 75
        sys_btn_h = 32
        
        sys_buttons = [
            ("save_game", "SAVE", "保存"),
            ("settings_menu", "CONFIG", "設定"),
            ("return_to_title", "TITLE", "戻る"),
        ]
        
        for i, (name, en_label, jp_label) in enumerate(sys_buttons):
            bx = btn_area_x + i * (sys_btn_w + 8)
            
            btn_rect = pygame.Rect(bx, sys_y, sys_btn_w, sys_btn_h)
            pygame.draw.rect(self.screen, (30, 32, 40), btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, (50, 55, 65), btn_rect, 1, border_radius=6)
            
            # ラベル
            label_surf = fonts.tiny.render(en_label, True, Colors.TEXT_SECONDARY)
            label_rect = label_surf.get_rect(center=(bx + sys_btn_w // 2, sys_y + sys_btn_h // 2))
            self.screen.blit(label_surf, label_rect)
            
            btn = Button(bx, sys_y, sys_btn_w, sys_btn_h, "", "ghost")
            buttons[name] = btn
        
        # 区切り線
        pygame.draw.line(self.screen, (40, 45, 55), (btn_area_x - 25, 30), (btn_area_x - 25, height - 30), 1)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    def _draw_league_standings_modern(self, x: int, y: int, width: int, height: int,
                                       player_team, schedule_manager, team_color):
        """モダンなリーグ順位パネル"""
        # パネル背景
        panel_rect = pygame.Rect(x, y, width, height)
        draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 16)
        
        if not player_team:
            return
        
        # プレイヤーのリーグ
        is_central = player_team.league.value == "セントラル"
        league_name = "CENTRAL" if is_central else "PACIFIC"
        accent_color = team_color
        
        # タイトル
        title_surf = fonts.small.render(league_name, True, accent_color)
        self.screen.blit(title_surf, (x + 20, y + 15))
        
        league_label = fonts.tiny.render("LEAGUE", True, Colors.TEXT_MUTED)
        self.screen.blit(league_label, (x + 20, y + 35))
        
        # 区切り線
        pygame.draw.line(self.screen, Colors.BORDER, (x + 15, y + 60), (x + width - 15, y + 60), 1)
        
        # 順位データ
        if schedule_manager:
            if is_central and hasattr(schedule_manager, 'central_teams'):
                teams = schedule_manager.central_teams
            elif hasattr(schedule_manager, 'pacific_teams'):
                teams = schedule_manager.pacific_teams
            else:
                teams = []
            
            sorted_teams = sorted(teams, key=lambda t: (-t.win_rate, -t.wins))
            
            row_y = y + 75
            row_height = 52
            
            for rank, team in enumerate(sorted_teams, 1):
                t_color = self.get_team_color(team.name)
                is_player_team = player_team and team.name == player_team.name
                
                # プレイヤーチームをハイライト
                if is_player_team:
                    highlight_rect = pygame.Rect(x + 10, row_y - 5, width - 20, row_height - 2)
                    draw_rounded_rect(self.screen, highlight_rect, lerp_color(Colors.BG_CARD, accent_color, 0.15), 8)
                
                # 順位バッジ
                rank_colors = {1: Colors.GOLD, 2: (192, 192, 192), 3: (205, 127, 50)}
                rank_color = rank_colors.get(rank, Colors.TEXT_MUTED)
                rank_surf = fonts.body.render(str(rank), True, rank_color)
                self.screen.blit(rank_surf, (x + 20, row_y + 10))
                
                # チーム略称
                abbr = self.get_team_abbr(team.name)
                name_color = Colors.TEXT_PRIMARY if is_player_team else Colors.TEXT_SECONDARY
                name_surf = fonts.body.render(abbr, True, t_color)
                self.screen.blit(name_surf, (x + 50, row_y + 10))
                
                # 勝敗
                record = f"{team.wins}-{team.losses}"
                record_surf = fonts.small.render(record, True, Colors.TEXT_SECONDARY)
                record_rect = record_surf.get_rect(right=x + width - 70, centery=row_y + 18)
                self.screen.blit(record_surf, record_rect)
                
                # 勝率
                rate = f".{int(team.win_rate * 1000):03d}" if team.games_played > 0 else ".000"
                rate_surf = fonts.small.render(rate, True, Colors.TEXT_PRIMARY)
                rate_rect = rate_surf.get_rect(right=x + width - 20, centery=row_y + 18)
                self.screen.blit(rate_surf, rate_rect)
                
                row_y += row_height
    
    def _draw_league_standings_compact(self, x: int, y: int, width: int, height: int,
                                        player_team, schedule_manager):
        """リーグ順位パネル（コンパクト版）- 後方互換用"""
        self._draw_league_standings_modern(x, y, width, height, player_team, schedule_manager,
                                           self.get_team_color(player_team.name) if player_team else Colors.PRIMARY)

    # 旧メソッド保持（後方互換）
    def _draw_league_standings_compact_old(self, x: int, y: int, width: int, height: int,
                                        player_team, schedule_manager):
        """リーグ順位パネル（コンパクト版）"""
        # パネル背景
        panel_rect = pygame.Rect(x, y, width, height)
        draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 12)
        
        # プレイヤーのリーグ
        is_central = player_team.league.value == "セントラル" if player_team else True
        league_name = "セ・リーグ" if is_central else "パ・リーグ"
        accent_color = Colors.PRIMARY if is_central else Colors.DANGER
        
        # タイトル
        title_surf = fonts.body.render(f"{league_name} 順位", True, accent_color)
        self.screen.blit(title_surf, (x + 15, y + 12))
        
        # 区切り線
        pygame.draw.line(self.screen, Colors.BORDER, (x + 12, y + 40), (x + width - 12, y + 40), 1)
        
        # 順位データ
        if schedule_manager:
            if is_central and hasattr(schedule_manager, 'central_teams'):
                teams = schedule_manager.central_teams
            elif hasattr(schedule_manager, 'pacific_teams'):
                teams = schedule_manager.pacific_teams
            else:
                teams = []
            
            sorted_teams = sorted(teams, key=lambda t: (-t.win_rate, -t.wins))
            
            row_y = y + 50
            row_height = 36
            
            for rank, team in enumerate(sorted_teams, 1):
                # プレイヤーチームをハイライト
                if player_team and team.name == player_team.name:
                    highlight_rect = pygame.Rect(x + 8, row_y - 2, width - 16, row_height - 4)
                    pygame.draw.rect(self.screen, lerp_color(Colors.BG_CARD, accent_color, 0.2), highlight_rect, border_radius=6)
                
                team_color = self.get_team_color(team.name)
                
                # 順位バッジ
                rank_colors = {1: Colors.GOLD, 2: (192, 192, 192), 3: (205, 127, 50)}
                rank_color = rank_colors.get(rank, Colors.TEXT_MUTED)
                rank_surf = fonts.body.render(str(rank), True, rank_color)
                self.screen.blit(rank_surf, (x + 15, row_y + 6))
                
                # チーム略称
                abbr = self.get_team_abbr(team.name)
                name_surf = fonts.body.render(abbr, True, team_color)
                self.screen.blit(name_surf, (x + 40, row_y + 6))
                
                # 勝敗（コンパクト）
                record = f"{team.wins}-{team.losses}"
                record_surf = fonts.small.render(record, True, Colors.TEXT_SECONDARY)
                self.screen.blit(record_surf, (x + 115, row_y + 8))
                
                # 勝率
                rate = f".{int(team.win_rate * 1000):03d}" if team.games_played > 0 else ".000"
                rate_surf = fonts.small.render(rate, True, Colors.TEXT_PRIMARY)
                self.screen.blit(rate_surf, (x + 175, row_y + 8))
                
                row_y += row_height
        
        # もう一方のリーグへの切り替えボタン（小さく）
        other_league = "パ・リーグ" if is_central else "セ・リーグ"
        switch_text = f"→ {other_league}"
        switch_surf = fonts.tiny.render(switch_text, True, Colors.TEXT_MUTED)
        self.screen.blit(switch_surf, (x + width - 80, y + 12))
    
    # ========================================
    # オーダー設定画面（ドラッグ&ドロップ対応）
    # ========================================
    def draw_lineup_screen(self, player_team, scroll_offset: int = 0,
                           dragging_player_idx: int = -1,
                           drag_pos: tuple = None,
                           selected_position: str = None,
                           dragging_position_slot: int = -1,
                           position_drag_pos: tuple = None,
                           lineup_edit_mode: str = "player") -> Dict[str, Button]:
        """オーダー設定画面を描画（ドラッグ&ドロップ対応）"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        team_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        header_h = draw_header(self.screen, "オーダー設定", 
                               "選手をドラッグして打順に配置", team_color)
        
        buttons = {}
        drop_zones = {}  # ドロップゾーン情報
        
        if not player_team:
            return buttons
        
        # ========================================
        # 左パネル: 野球場型のポジション配置
        # ========================================
        field_card = Card(30, header_h + 20, 480, 420, "POSITION")
        field_rect = field_card.draw(self.screen)
        
        # フィールドの中心
        field_cx = field_rect.x + field_rect.width // 2
        field_cy = field_rect.y + 220
        
        # 守備位置の座標（野球場型配置 - 位置調整）
        position_coords = {
            "捕手": (field_cx, field_cy + 100),
            "一塁手": (field_cx + 100, field_cy + 20),
            "二塁手": (field_cx + 45, field_cy - 50),
            "三塁手": (field_cx - 100, field_cy + 20),
            "遊撃手": (field_cx - 45, field_cy - 50),
            "左翼手": (field_cx - 110, field_cy - 130),
            "中堅手": (field_cx, field_cy - 160),
            "右翼手": (field_cx + 110, field_cy - 130),
        }
        
        # DHスロットの位置（フィールド下部）
        dh_position = (field_cx, field_cy + 165)
        
        # グラウンドを簡易的に描画
        # 外野の扇形
        pygame.draw.arc(self.screen, Colors.SUCCESS, 
                       (field_cx - 160, field_cy - 220, 320, 320),
                       3.14 * 0.75, 3.14 * 0.25, 2)
        
        # 内野ダイヤモンド
        diamond = [
            (field_cx, field_cy - 40),   # 2塁
            (field_cx + 60, field_cy + 30),  # 1塁
            (field_cx, field_cy + 100),  # ホーム
            (field_cx - 60, field_cy + 30),  # 3塁
        ]
        pygame.draw.polygon(self.screen, Colors.BORDER, diamond, 2)
        
        # 投手マウンド
        pygame.draw.circle(self.screen, Colors.BORDER, (field_cx, field_cy + 30), 8, 2)
        
        # 守備配置を取得（チームのposition_assignmentsを優先）
        lineup = player_team.current_lineup if player_team.current_lineup else []
        
        # チームに保存された守備位置情報を使用
        if hasattr(player_team, 'position_assignments') and player_team.position_assignments:
            position_assignments = dict(player_team.position_assignments)
        else:
            position_assignments = {}
            # 現在のラインナップから守備位置を自動割り当て
            for order_idx, player_idx in enumerate(lineup):
                if player_idx >= 0 and player_idx < len(player_team.players):
                    player = player_team.players[player_idx]
                    pos = player.position.value
                    
                    # 外野手は順番に配置
                    if pos == "外野手":
                        for field_pos in ["左翼手", "中堅手", "右翼手"]:
                            if field_pos not in position_assignments:
                                position_assignments[field_pos] = player_idx
                                break
                    elif pos in position_coords:
                        if pos not in position_assignments:
                            position_assignments[pos] = player_idx
        
        # 各守備位置を描画
        for pos_name, (px, py) in position_coords.items():
            # 短縮名
            short_names = {
                "捕手": "捕", "一塁手": "一", "二塁手": "二", "三塁手": "三",
                "遊撃手": "遊", "左翼手": "左", "中堅手": "中", "右翼手": "右"
            }
            display_name = short_names.get(pos_name, pos_name[:1])
            
            # スロット背景（小さめ）
            slot_rect = pygame.Rect(px - 38, py - 20, 76, 40)
            
            # ドロップゾーンとして登録
            drop_zones[f"pos_{pos_name}"] = slot_rect
            
            # ドラッグ中のハイライト
            if dragging_player_idx >= 0 and slot_rect.collidepoint(drag_pos or (0, 0)):
                pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 100), slot_rect, border_radius=6)
                pygame.draw.rect(self.screen, Colors.PRIMARY, slot_rect, 2, border_radius=6)
            else:
                pygame.draw.rect(self.screen, Colors.BG_CARD_HOVER, slot_rect, border_radius=6)
                pygame.draw.rect(self.screen, Colors.BORDER, slot_rect, 1, border_radius=6)
            
            # 配置済み選手
            if pos_name in position_assignments:
                player_idx = position_assignments[pos_name]
                player = player_team.players[player_idx]
                name = player.name[:3]
                name_surf = fonts.tiny.render(name, True, Colors.TEXT_PRIMARY)
                name_rect = name_surf.get_rect(center=(px, py - 3))
                self.screen.blit(name_surf, name_rect)
                
                pos_surf = fonts.tiny.render(display_name, True, Colors.TEXT_SECONDARY)
                pos_rect = pos_surf.get_rect(center=(px, py + 12))
                self.screen.blit(pos_surf, pos_rect)
            else:
                # 空きスロット
                empty_surf = fonts.small.render(display_name, True, Colors.TEXT_MUTED)
                empty_rect = empty_surf.get_rect(center=(px, py))
                self.screen.blit(empty_surf, empty_rect)
        
        # DHスロット描画
        dh_x, dh_y = dh_position
        dh_rect = pygame.Rect(dh_x - 38, dh_y - 20, 76, 40)
        drop_zones["pos_DH"] = dh_rect
        
        # ドラッグ中のハイライト
        if dragging_player_idx >= 0 and dh_rect.collidepoint(drag_pos or (0, 0)):
            pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 100), dh_rect, border_radius=6)
            pygame.draw.rect(self.screen, Colors.PRIMARY, dh_rect, 2, border_radius=6)
        else:
            pygame.draw.rect(self.screen, Colors.BG_CARD_HOVER, dh_rect, border_radius=6)
            pygame.draw.rect(self.screen, Colors.WARNING, dh_rect, 1, border_radius=6)  # DHは特別色
        
        # DHスロット内容
        if "DH" in position_assignments:
            dh_player_idx = position_assignments["DH"]
            dh_player = player_team.players[dh_player_idx]
            dh_name_surf = fonts.tiny.render(dh_player.name[:3], True, Colors.TEXT_PRIMARY)
            dh_name_rect = dh_name_surf.get_rect(center=(dh_x, dh_y - 3))
            self.screen.blit(dh_name_surf, dh_name_rect)
            
            dh_label = fonts.tiny.render("DH", True, Colors.WARNING)
            dh_label_rect = dh_label.get_rect(center=(dh_x, dh_y + 12))
            self.screen.blit(dh_label, dh_label_rect)
        else:
            dh_empty = fonts.small.render("DH", True, Colors.TEXT_MUTED)
            dh_empty_rect = dh_empty.get_rect(center=(dh_x, dh_y))
            self.screen.blit(dh_empty, dh_empty_rect)
        
        # ========================================
        # 中央パネル: 打順
        # ========================================
        order_card = Card(520, header_h + 20, 280, 480, "LINEUP")
        order_rect = order_card.draw(self.screen)
        
        # 編集モード切り替えボタン
        player_mode_style = "primary" if lineup_edit_mode == "player" else "ghost"
        pos_mode_style = "primary" if lineup_edit_mode == "position" else "ghost"
        
        mode_btn_y = order_rect.y + 45
        buttons["edit_mode_player"] = Button(order_rect.x + 10, mode_btn_y, 60, 24, "選手", player_mode_style, font=fonts.tiny)
        buttons["edit_mode_player"].draw(self.screen)
        buttons["edit_mode_position"] = Button(order_rect.x + 75, mode_btn_y, 60, 24, "守備", pos_mode_style, font=fonts.tiny)
        buttons["edit_mode_position"].draw(self.screen)
        
        # 最適化・シャッフルボタン
        buttons["optimize_lineup"] = Button(order_rect.x + 145, mode_btn_y, 50, 24, "最適", "secondary", font=fonts.tiny)
        buttons["optimize_lineup"].draw(self.screen)
        buttons["shuffle_lineup"] = Button(order_rect.x + 200, mode_btn_y, 50, 24, "🔀", "ghost", font=fonts.tiny)
        buttons["shuffle_lineup"].draw(self.screen)
        
        # ポジション重複チェック
        position_counts = {}
        position_conflicts = []
        if hasattr(player_team, 'position_assignments'):
            for pos_name, player_idx in player_team.position_assignments.items():
                if player_idx in lineup and pos_name != "DH":
                    # 外野は左中右をまとめてカウント
                    if pos_name in ["左翼手", "中堅手", "右翼手"]:
                        count_key = "外野手"
                    else:
                        count_key = pos_name
                    
                    if count_key not in position_counts:
                        position_counts[count_key] = []
                    position_counts[count_key].append(player_idx)
            
            # 重複を検出
            for pos_name, players in position_counts.items():
                if pos_name == "外野手" and len(players) > 3:
                    position_conflicts.append(f"外野手が{len(players)}人います")
                elif pos_name != "外野手" and len(players) > 1:
                    position_conflicts.append(f"{pos_name}が{len(players)}人います")
        
        # lineup_positionsを取得（独立したポジション管理）
        if hasattr(player_team, 'lineup_positions') and player_team.lineup_positions:
            lineup_positions = player_team.lineup_positions
        else:
            lineup_positions = ["捕", "一", "二", "三", "遊", "左", "中", "右", "DH"]
        while len(lineup_positions) < 9:
            lineup_positions.append("DH")
        
        y = order_rect.y + 78
        for i in range(9):
            # スロット全体の矩形（より広め）
            slot_rect = pygame.Rect(order_rect.x + 10, y, order_rect.width - 20, 40)
            drop_zones[f"order_{i}"] = slot_rect
            
            # ポジションスロット（独立してドラッグ可能）
            pos_slot_rect = pygame.Rect(order_rect.x + 10, y, 40, 38)
            drop_zones[f"position_slot_{i}"] = pos_slot_rect
            
            # ドラッグ中のハイライト（選手）
            is_player_drag_target = dragging_player_idx >= 0 and slot_rect.collidepoint(drag_pos or (0, 0))
            # ドラッグ中のハイライト（ポジション）
            is_pos_drag_target = dragging_position_slot >= 0 and pos_slot_rect.collidepoint(position_drag_pos or (0, 0))
            is_pos_dragging = dragging_position_slot == i
            
            if is_player_drag_target:
                pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 100), slot_rect, border_radius=5)
                pygame.draw.rect(self.screen, Colors.PRIMARY, slot_rect, 2, border_radius=5)
            elif is_pos_drag_target:
                pygame.draw.rect(self.screen, (*Colors.WARNING[:3], 100), slot_rect, border_radius=5)
                pygame.draw.rect(self.screen, Colors.WARNING, slot_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(self.screen, Colors.BG_INPUT, slot_rect, border_radius=5)
            
            # ポジションスロット（左側、独立）
            if is_pos_dragging:
                pos_bg_color = (*Colors.WARNING[:3], 80)
            else:
                pos_bg_color = Colors.BG_CARD_HOVER
            pygame.draw.rect(self.screen, pos_bg_color, pos_slot_rect, border_radius=4)
            pygame.draw.rect(self.screen, Colors.WARNING if lineup_edit_mode == "position" else Colors.BORDER, pos_slot_rect, 1, border_radius=4)
            
            # ポジション表示
            pos_text = lineup_positions[i] if i < len(lineup_positions) else "DH"
            pos_surf = fonts.small.render(pos_text, True, Colors.WARNING)
            pos_text_rect = pos_surf.get_rect(center=(pos_slot_rect.centerx, pos_slot_rect.centery))
            self.screen.blit(pos_surf, pos_text_rect)
            
            # ポジションドラッグ用ボタン
            buttons[f"drag_position_{i}"] = Button(pos_slot_rect.x, pos_slot_rect.y, pos_slot_rect.width, pos_slot_rect.height, "", "ghost")
            
            # 打順番号
            num_surf = fonts.small.render(f"{i + 1}", True, Colors.PRIMARY)
            self.screen.blit(num_surf, (slot_rect.x + 48, slot_rect.y + 11))
            
            # 配置済み選手
            if i < len(lineup) and lineup[i] >= 0 and lineup[i] < len(player_team.players):
                player = player_team.players[lineup[i]]
                name_surf = fonts.tiny.render(player.name[:5], True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (slot_rect.x + 68, slot_rect.y + 12))
                
                # 選手の本来のポジション（小さく表示）
                player_pos_short = player.position.value[:2]
                player_pos_surf = fonts.tiny.render(f"({player_pos_short})", True, Colors.TEXT_MUTED)
                self.screen.blit(player_pos_surf, (slot_rect.x + 130, slot_rect.y + 12))
                
                # 入れ替えボタン（上下）を各スロットに追加
                btn_x = slot_rect.right - 70
                if i > 0:
                    swap_up = Button(btn_x, slot_rect.y + 4, 22, 16, "↑", "ghost", font=fonts.tiny)
                    swap_up.draw(self.screen)
                    buttons[f"lineup_swap_up_{i}"] = swap_up
                if i < 8:
                    swap_down = Button(btn_x + 24, slot_rect.y + 4, 22, 16, "↓", "ghost", font=fonts.tiny)
                    swap_down.draw(self.screen)
                    buttons[f"lineup_swap_down_{i}"] = swap_down
                
                # ポジション入れ替えボタン
                if lineup_edit_mode == "position":
                    if i > 0:
                        pos_up = Button(slot_rect.x + 52, slot_rect.y + 22, 18, 14, "◀", "warning", font=fonts.tiny)
                        pos_up.draw(self.screen)
                        buttons[f"pos_swap_up_{i}"] = pos_up
                    if i < 8:
                        pos_down = Button(slot_rect.x + 72, slot_rect.y + 22, 18, 14, "▶", "warning", font=fonts.tiny)
                        pos_down.draw(self.screen)
                        buttons[f"pos_swap_down_{i}"] = pos_down
                
                # 削除ボタン（スロットから外す）
                remove_btn = Button(slot_rect.right - 22, slot_rect.y + 12, 18, 16, "×", "danger", font=fonts.tiny)
                remove_btn.draw(self.screen)
                buttons[f"lineup_remove_{i}"] = remove_btn
            else:
                # 空スロット
                empty_surf = fonts.tiny.render("- 空 -", True, Colors.TEXT_MUTED)
                self.screen.blit(empty_surf, (slot_rect.x + 50, slot_rect.y + 10))
            
            y += 42
        
        # ポジション重複警告表示
        if position_conflicts:
            warning_y = y + 2
            for conflict in position_conflicts[:2]:  # 最大2件表示
                warning_surf = fonts.tiny.render(f"⚠ {conflict}", True, Colors.ERROR)
                self.screen.blit(warning_surf, (order_rect.x + 10, warning_y))
                warning_y += 16
        
        # プリセット保存/読込ボタン
        preset_y = order_rect.bottom - 35
        buttons["save_lineup_preset"] = Button(order_rect.x + 10, preset_y, 80, 28, "💾保存", "ghost", font=fonts.tiny)
        buttons["save_lineup_preset"].draw(self.screen)
        buttons["load_lineup_preset"] = Button(order_rect.x + 95, preset_y, 80, 28, "📂読込", "ghost", font=fonts.tiny)
        buttons["load_lineup_preset"].draw(self.screen)
        
        # ポジションドラッグ中の表示
        if dragging_position_slot >= 0 and position_drag_pos:
            pos_text = lineup_positions[dragging_position_slot] if dragging_position_slot < len(lineup_positions) else "?"
            drag_pos_surf = fonts.body.render(pos_text, True, Colors.WARNING)
            drag_rect = pygame.Rect(position_drag_pos[0] - 20, position_drag_pos[1] - 15, 40, 30)
            pygame.draw.rect(self.screen, Colors.BG_CARD, drag_rect, border_radius=6)
            pygame.draw.rect(self.screen, Colors.WARNING, drag_rect, 2, border_radius=6)
            self.screen.blit(drag_pos_surf, (position_drag_pos[0] - 10, position_drag_pos[1] - 10))
        
        # ========================================
        # 右パネル: 選手一覧（ドラッグ元）
        # ========================================
        roster_card = Card(820, header_h + 20, width - 850, height - header_h - 100, "ROSTER")
        roster_rect = roster_card.draw(self.screen)
        
        # タブ: 全員 / 野手 / 投手
        tab_y = roster_rect.y + 45
        all_style = "primary" if selected_position == "all" or selected_position is None else "ghost"
        batter_style = "primary" if selected_position == "batters" else "ghost"
        pitcher_style = "primary" if selected_position == "pitcher" else "ghost"
        
        buttons["tab_all"] = Button(roster_rect.x + 10, tab_y, 55, 28, "全員", all_style, font=fonts.tiny)
        buttons["tab_all"].draw(self.screen)
        
        buttons["tab_batters"] = Button(roster_rect.x + 70, tab_y, 55, 28, "野手", batter_style, font=fonts.tiny)
        buttons["tab_batters"].draw(self.screen)
        
        buttons["tab_pitchers"] = Button(roster_rect.x + 130, tab_y, 55, 28, "投手", pitcher_style, font=fonts.tiny)
        buttons["tab_pitchers"].draw(self.screen)
        
        # 選手リスト取得（タブに応じて）
        if selected_position == "pitcher":
            players = player_team.get_active_pitchers()
            count_text = f"({len(players)}人)"
        elif selected_position == "batters":
            players = player_team.get_active_batters()
            count_text = f"({len(players)}人)"
        else:
            # 全員表示
            players = [p for p in player_team.players if not getattr(p, 'is_developmental', False)]
            count_text = f"({len(players)}人)"
        count_surf = fonts.tiny.render(count_text, True, Colors.TEXT_MUTED)
        self.screen.blit(count_surf, (roster_rect.x + 190, tab_y + 8))
        
        # 選手リスト（コンパクト表示）
        y = tab_y + 36
        row_height = 30  # コンパクト化
        visible_count = (roster_rect.height - 100) // row_height
        
        # ヘッダー
        header_surf = fonts.tiny.render("名前", True, Colors.TEXT_MUTED)
        self.screen.blit(header_surf, (roster_rect.x + 22, y))
        stat_header = fonts.tiny.render("能力", True, Colors.TEXT_MUTED)
        self.screen.blit(stat_header, (roster_rect.x + 100, y))
        y += 18
        
        for i in range(scroll_offset, min(len(players), scroll_offset + visible_count)):
            player = players[i]
            player_idx = player_team.players.index(player)
            
            row_rect = pygame.Rect(roster_rect.x + 8, y, roster_rect.width - 30, row_height - 2)
            
            # 選択済みマーキング
            is_in_lineup = player_idx in lineup
            
            if dragging_player_idx == player_idx:
                # ドラッグ中は半透明
                pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 30), row_rect, border_radius=4)
            elif is_in_lineup:
                pygame.draw.rect(self.screen, (*Colors.SUCCESS[:3], 40), row_rect, border_radius=4)
                pygame.draw.rect(self.screen, Colors.SUCCESS, row_rect, 1, border_radius=4)
            else:
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=4)
            
            # ドラッグ可能インジケータ（コンパクト）
            grip_x = row_rect.x + 5
            for dot_y in [row_rect.y + 8, row_rect.y + 14, row_rect.y + 20]:
                pygame.draw.circle(self.screen, Colors.TEXT_MUTED, (grip_x, dot_y), 1)
                pygame.draw.circle(self.screen, Colors.TEXT_MUTED, (grip_x + 4, dot_y), 1)
            
            # 選手情報（レイアウト調整して被り防止）
            name_surf = fonts.tiny.render(player.name[:4], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (row_rect.x + 14, row_rect.y + 7))
            
            pos_surf = fonts.tiny.render(player.position.value[:2], True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (row_rect.x + 58, row_rect.y + 7))
            
            # 能力値プレビュー（位置調整）
            if player.position.value == "投手":
                stat_text = f"球{player.stats.speed} 制{player.stats.control}"
            else:
                stat_text = f"ミ{player.stats.contact} パ{player.stats.power}"
            stat_preview = fonts.tiny.render(stat_text, True, Colors.TEXT_MUTED)
            self.screen.blit(stat_preview, (row_rect.x + 88, row_rect.y + 7))
            
            # 詳細ボタン（小さめ）
            detail_btn = Button(
                row_rect.right - 32, row_rect.y + 3, 28, row_height - 8,
                "詳", "outline", font=fonts.tiny
            )
            detail_btn.draw(self.screen)
            buttons[f"player_detail_{player_idx}"] = detail_btn
            
            # ドラッグ用ボタンとして登録（詳細ボタン以外の領域）
            buttons[f"drag_player_{player_idx}"] = Button(
                row_rect.x, row_rect.y, row_rect.width - 35, row_rect.height, "", "ghost"
            )
            
            y += row_height
        
        # スクロールバー表示
        if len(players) > visible_count:
            scroll_track_h = roster_rect.height - 120
            scroll_h = max(20, int(scroll_track_h * visible_count / len(players)))
            max_scroll = len(players) - visible_count
            scroll_y_pos = roster_rect.y + 100 + int((scroll_offset / max(1, max_scroll)) * (scroll_track_h - scroll_h))
            pygame.draw.rect(self.screen, Colors.BG_INPUT, 
                            (roster_rect.right - 10, roster_rect.y + 100, 5, scroll_track_h), border_radius=2)
            pygame.draw.rect(self.screen, Colors.PRIMARY, 
                            (roster_rect.right - 10, scroll_y_pos, 5, scroll_h), border_radius=2)
        
        # ドラッグ中の選手を描画
        if dragging_player_idx >= 0 and drag_pos and dragging_player_idx < len(player_team.players):
            player = player_team.players[dragging_player_idx]
            drag_surf = fonts.small.render(player.name[:6], True, Colors.PRIMARY)
            drag_rect = pygame.Rect(drag_pos[0] - 40, drag_pos[1] - 12, 80, 24)
            pygame.draw.rect(self.screen, Colors.BG_CARD, drag_rect, border_radius=4)
            pygame.draw.rect(self.screen, Colors.PRIMARY, drag_rect, 2, border_radius=4)
            self.screen.blit(drag_surf, (drag_pos[0] - 35, drag_pos[1] - 8))
        
        # ========================================
        # 先発投手選択
        # ========================================
        pitcher_card = Card(30, header_h + 470, 480, 90, "STARTER")
        pitcher_rect = pitcher_card.draw(self.screen)
        
        # 現在の先発投手
        if player_team.starting_pitcher_idx >= 0 and player_team.starting_pitcher_idx < len(player_team.players):
            pitcher = player_team.players[player_team.starting_pitcher_idx]
            pitcher_surf = fonts.body.render(pitcher.name, True, team_color)
            self.screen.blit(pitcher_surf, (pitcher_rect.x + 25, pitcher_rect.y + 50))
            
            stat_text = f"球速{pitcher.stats.speed} 制球{pitcher.stats.control}"
            stat_surf = fonts.tiny.render(stat_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(stat_surf, (pitcher_rect.x + 180, pitcher_rect.y + 55))
        else:
            empty_surf = fonts.small.render("投手タブから先発を選んでください", True, Colors.TEXT_MUTED)
            self.screen.blit(empty_surf, (pitcher_rect.x + 25, pitcher_rect.y + 50))
        
        # ドロップゾーンとして登録
        drop_zones["starting_pitcher"] = pitcher_rect
        
        # ========================================
        # 下部ボタン
        # ========================================
        # ヘルプテキスト（編集モードに応じて変更）
        if lineup_edit_mode == "position":
            help_text = "ポジション編集モード: 左のポジションをドラッグして入れ替え | ◀▶ボタンでも移動可能"
        else:
            help_text = "選手編集モード: 選手をドラッグして打順に配置 | ↑↓ボタンで順序入れ替え"
        help_surf = fonts.tiny.render(help_text, True, Colors.TEXT_MUTED)
        self.screen.blit(help_surf, (width // 2 - help_surf.get_width() // 2, height - 95))
        
        buttons["roster_management"] = Button(
            200, height - 65, 150, 45,
            "登録管理", "ghost", font=fonts.small
        )
        buttons["roster_management"].draw(self.screen)
        
        buttons["auto_lineup"] = Button(
            width - 340, height - 65, 130, 45,
            "AUTO", "secondary", font=fonts.small
        )
        buttons["auto_lineup"].draw(self.screen)
        
        buttons["clear_lineup"] = Button(
            width - 200, height - 65, 130, 45,
            "CLEAR", "ghost", font=fonts.small
        )
        buttons["clear_lineup"].draw(self.screen)
        
        buttons["to_pitcher_order"] = Button(
            360, height - 65, 150, 45,
            "投手設定", "warning", font=fonts.small
        )
        buttons["to_pitcher_order"].draw(self.screen)
        
        buttons["back"] = Button(
            50, height - 65, 130, 45,
            "← 戻る", "ghost", font=fonts.small
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        # ドロップゾーン情報を返す
        buttons["_drop_zones"] = drop_zones
        
        return buttons
    
    # ========================================
    # 試合進行画面（戦略オプション付き）
    # ========================================
    def draw_game_screen(self, player_team, opponent_team, game_state: dict = None,
                         strategy_mode: str = None, strategy_candidates: list = None) -> Dict[str, Button]:
        """試合進行画面を描画（戦略オプション付き）"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        buttons = {}
        
        if game_state is None:
            game_state = {}
        
        inning = game_state.get('inning', 1)
        is_top = game_state.get('is_top', True)
        outs = game_state.get('outs', 0)
        runners = game_state.get('runners', [False, False, False])
        home_score = game_state.get('home_score', 0)
        away_score = game_state.get('away_score', 0)
        current_batter = game_state.get('current_batter', None)
        current_pitcher = game_state.get('current_pitcher', None)
        pitch_count = game_state.get('pitch_count', 0)
        
        # ヘッダー部分
        team1_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        team2_color = self.get_team_color(opponent_team.name) if opponent_team else Colors.DANGER
        
        # イニング表示
        inning_text = f"{inning}回{'表' if is_top else '裏'}"
        inning_surf = fonts.h2.render(inning_text, True, Colors.TEXT_PRIMARY)
        inning_rect = inning_surf.get_rect(center=(center_x, 40))
        self.screen.blit(inning_surf, inning_rect)
        
        # スコアボード
        score_y = 80
        # アウェイチーム
        away_name = opponent_team.name[:4] if is_top else player_team.name[:4]
        home_name = player_team.name[:4] if is_top else opponent_team.name[:4]
        
        away_surf = fonts.h3.render(away_name, True, team2_color if is_top else team1_color)
        self.screen.blit(away_surf, (center_x - 180, score_y))
        
        away_score_surf = fonts.h1.render(str(away_score), True, Colors.TEXT_PRIMARY)
        away_score_rect = away_score_surf.get_rect(center=(center_x - 50, score_y + 15))
        self.screen.blit(away_score_surf, away_score_rect)
        
        vs_surf = fonts.body.render("-", True, Colors.TEXT_MUTED)
        self.screen.blit(vs_surf, (center_x - 8, score_y + 5))
        
        home_score_surf = fonts.h1.render(str(home_score), True, Colors.TEXT_PRIMARY)
        home_score_rect = home_score_surf.get_rect(center=(center_x + 50, score_y + 15))
        self.screen.blit(home_score_surf, home_score_rect)
        
        home_surf = fonts.h3.render(home_name, True, team1_color if is_top else team2_color)
        self.screen.blit(home_surf, (center_x + 100, score_y))
        
        # アウトカウント表示
        out_y = 130
        out_text = f"アウト: {'●' * outs}{'○' * (3 - outs)}"
        out_surf = fonts.body.render(out_text, True, Colors.TEXT_SECONDARY)
        out_rect = out_surf.get_rect(center=(center_x, out_y))
        self.screen.blit(out_surf, out_rect)
        
        # ダイヤモンド（走塁図）
        diamond_y = 220
        diamond_size = 80
        
        # ベースの位置
        bases = [
            (center_x, diamond_y + diamond_size),      # ホーム
            (center_x + diamond_size, diamond_y),      # 1塁
            (center_x, diamond_y - diamond_size),      # 2塁
            (center_x - diamond_size, diamond_y),      # 3塁
        ]
        
        # ダイヤモンド線
        for i in range(4):
            pygame.draw.line(self.screen, Colors.BORDER, bases[i], bases[(i+1)%4], 2)
        
        # ベースと走者
        base_colors = [Colors.BG_CARD, Colors.BG_CARD, Colors.BG_CARD]
        for i, has_runner in enumerate(runners):
            if has_runner:
                base_colors[i] = Colors.WARNING
        
        # 1塁
        pygame.draw.rect(self.screen, base_colors[0], 
                        (bases[1][0] - 12, bases[1][1] - 12, 24, 24), border_radius=3)
        if runners[0]:
            pygame.draw.rect(self.screen, Colors.WARNING, 
                            (bases[1][0] - 12, bases[1][1] - 12, 24, 24), 2, border_radius=3)
        # 2塁
        pygame.draw.rect(self.screen, base_colors[1], 
                        (bases[2][0] - 12, bases[2][1] - 12, 24, 24), border_radius=3)
        if runners[1]:
            pygame.draw.rect(self.screen, Colors.WARNING, 
                            (bases[2][0] - 12, bases[2][1] - 12, 24, 24), 2, border_radius=3)
        # 3塁
        pygame.draw.rect(self.screen, base_colors[2], 
                        (bases[3][0] - 12, bases[3][1] - 12, 24, 24), border_radius=3)
        if runners[2]:
            pygame.draw.rect(self.screen, Colors.WARNING, 
                            (bases[3][0] - 12, bases[3][1] - 12, 24, 24), 2, border_radius=3)
        # ホーム
        pygame.draw.polygon(self.screen, Colors.BG_CARD, 
                          [(bases[0][0], bases[0][1] - 10),
                           (bases[0][0] + 10, bases[0][1]),
                           (bases[0][0] + 10, bases[0][1] + 8),
                           (bases[0][0] - 10, bases[0][1] + 8),
                           (bases[0][0] - 10, bases[0][1])])
        
        # 現在の打者・投手情報
        info_y = 320
        if current_batter:
            batter_text = f"打者: {current_batter.name} ({current_batter.position.value[:2]})"
            batter_surf = fonts.body.render(batter_text, True, Colors.TEXT_PRIMARY)
            self.screen.blit(batter_surf, (50, info_y))
            
            # 打者成績
            avg = current_batter.record.batting_average
            stats_text = f"打率.{int(avg*1000):03d} {current_batter.record.home_runs}本 {current_batter.record.rbis}点"
            stats_surf = fonts.small.render(stats_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(stats_surf, (50, info_y + 25))
        
        if current_pitcher:
            pitcher_text = f"投手: {current_pitcher.name}"
            pitcher_surf = fonts.body.render(pitcher_text, True, Colors.TEXT_PRIMARY)
            self.screen.blit(pitcher_surf, (width - 280, info_y))
            
            # 投手成績
            era = current_pitcher.record.era
            p_stats = f"防{era:.2f} {pitch_count}球"
            p_stats_surf = fonts.small.render(p_stats, True, Colors.TEXT_SECONDARY)
            self.screen.blit(p_stats_surf, (width - 280, info_y + 25))
        
        # ========================================
        # 戦略パネル
        # ========================================
        strategy_panel_y = 400
        strategy_card = Card(30, strategy_panel_y, width - 60, 200, "作戦")
        strategy_rect = strategy_card.draw(self.screen)
        
        # 戦略ボタン群
        btn_y = strategy_rect.y + 50
        btn_h = 45
        btn_gap = 10
        
        # 攻撃時の戦略
        if is_top == (player_team == opponent_team):  # プレイヤーチームが攻撃中
            # 打撃戦略
            attack_x = strategy_rect.x + 20
            
            buttons["strategy_bunt"] = Button(attack_x, btn_y, 100, btn_h, "バント", "secondary", font=fonts.small)
            buttons["strategy_bunt"].draw(self.screen)
            
            buttons["strategy_squeeze"] = Button(attack_x + 110, btn_y, 110, btn_h, "スクイズ", "secondary", font=fonts.small)
            buttons["strategy_squeeze"].draw(self.screen)
            
            buttons["strategy_steal"] = Button(attack_x + 230, btn_y, 90, btn_h, "盗塁", "secondary", font=fonts.small)
            buttons["strategy_steal"].draw(self.screen)
            
            buttons["strategy_hit_run"] = Button(attack_x + 330, btn_y, 120, btn_h, "エンドラン", "secondary", font=fonts.small)
            buttons["strategy_hit_run"].draw(self.screen)
            
            # 選手交代
            btn_y2 = btn_y + btn_h + btn_gap
            buttons["strategy_pinch_hit"] = Button(attack_x, btn_y2, 100, btn_h, "代打", "warning", font=fonts.small)
            buttons["strategy_pinch_hit"].draw(self.screen)
            
            buttons["strategy_pinch_run"] = Button(attack_x + 110, btn_y2, 100, btn_h, "代走", "warning", font=fonts.small)
            buttons["strategy_pinch_run"].draw(self.screen)
        
        else:  # プレイヤーチームが守備中
            # 守備戦略
            defense_x = strategy_rect.x + 20
            
            buttons["strategy_intentional_walk"] = Button(defense_x, btn_y, 110, btn_h, "敬遠", "secondary", font=fonts.small)
            buttons["strategy_intentional_walk"].draw(self.screen)
            
            buttons["strategy_pitch_out"] = Button(defense_x + 120, btn_y, 120, btn_h, "ピッチアウト", "secondary", font=fonts.small)
            buttons["strategy_pitch_out"].draw(self.screen)
            
            buttons["strategy_infield_in"] = Button(defense_x + 250, btn_y, 130, btn_h, "前進守備", "secondary", font=fonts.small)
            buttons["strategy_infield_in"].draw(self.screen)
            
            # 投手交代
            btn_y2 = btn_y + btn_h + btn_gap
            buttons["strategy_pitching_change"] = Button(defense_x, btn_y2, 120, btn_h, "継投", "warning", font=fonts.small)
            buttons["strategy_pitching_change"].draw(self.screen)
            
            buttons["strategy_mound_visit"] = Button(defense_x + 130, btn_y2, 130, btn_h, "マウンド訪問", "ghost", font=fonts.small)
            buttons["strategy_mound_visit"].draw(self.screen)
        
        # クイック再生/一時停止
        control_x = strategy_rect.right - 200
        buttons["game_auto_play"] = Button(control_x, btn_y, 80, btn_h, "自動", "primary", font=fonts.small)
        buttons["game_auto_play"].draw(self.screen)
        
        buttons["game_next_play"] = Button(control_x + 90, btn_y, 80, btn_h, "次へ", "outline", font=fonts.small)
        buttons["game_next_play"].draw(self.screen)
        
        # 速度調整
        btn_y2 = btn_y + btn_h + btn_gap
        speed_label = fonts.tiny.render("速度:", True, Colors.TEXT_MUTED)
        self.screen.blit(speed_label, (control_x, btn_y2 + 12))
        
        buttons["speed_slow"] = Button(control_x + 40, btn_y2, 40, 35, "1x", "ghost", font=fonts.tiny)
        buttons["speed_slow"].draw(self.screen)
        buttons["speed_normal"] = Button(control_x + 85, btn_y2, 40, 35, "2x", "ghost", font=fonts.tiny)
        buttons["speed_normal"].draw(self.screen)
        buttons["speed_fast"] = Button(control_x + 130, btn_y2, 40, 35, "5x", "ghost", font=fonts.tiny)
        buttons["speed_fast"].draw(self.screen)
        
        # ========================================
        # 戦略選択ダイアログ（候補者選択）
        # ========================================
        if strategy_mode and strategy_candidates:
            # オーバーレイ
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            # ダイアログ
            dialog_w, dialog_h = 500, 400
            dialog_x = center_x - dialog_w // 2
            dialog_y = height // 2 - dialog_h // 2
            
            pygame.draw.rect(self.screen, Colors.BG_CARD, 
                           (dialog_x, dialog_y, dialog_w, dialog_h), border_radius=16)
            pygame.draw.rect(self.screen, Colors.PRIMARY, 
                           (dialog_x, dialog_y, dialog_w, dialog_h), 2, border_radius=16)
            
            # タイトル
            mode_titles = {
                "pinch_hit": "代打選手を選択",
                "pinch_run": "代走選手を選択",
                "pitching_change": "交代投手を選択",
            }
            title_text = mode_titles.get(strategy_mode, "選手を選択")
            title_surf = fonts.h3.render(title_text, True, Colors.TEXT_PRIMARY)
            title_rect = title_surf.get_rect(center=(center_x, dialog_y + 35))
            self.screen.blit(title_surf, title_rect)
            
            # 候補リスト
            list_y = dialog_y + 70
            for i, player in enumerate(strategy_candidates[:8]):  # 最大8人表示
                row_rect = pygame.Rect(dialog_x + 20, list_y, dialog_w - 40, 35)
                
                # ホバー効果用ボタン
                btn = Button(row_rect.x, row_rect.y, row_rect.width, row_rect.height, "", "ghost")
                btn.draw(self.screen)
                buttons[f"select_candidate_{i}"] = btn
                
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=6)
                
                # 選手名
                name_surf = fonts.body.render(player.name, True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (row_rect.x + 10, row_rect.y + 8))
                
                # ポジション
                pos_surf = fonts.small.render(player.position.value[:3], True, Colors.TEXT_SECONDARY)
                self.screen.blit(pos_surf, (row_rect.x + 150, row_rect.y + 10))
                
                # 能力値
                if strategy_mode == "pitching_change":
                    stat_text = f"球{player.stats.speed} 制{player.stats.control}"
                else:
                    stat_text = f"ミ{player.stats.contact} パ{player.stats.power}"
                stat_surf = fonts.small.render(stat_text, True, Colors.TEXT_MUTED)
                self.screen.blit(stat_surf, (row_rect.x + 250, row_rect.y + 10))
                
                list_y += 38
            
            # キャンセルボタン
            buttons["cancel_strategy"] = Button(center_x - 60, dialog_y + dialog_h - 55, 120, 40, "キャンセル", "ghost", font=fonts.body)
            buttons["cancel_strategy"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # 試合結果画面
    # ========================================
    def draw_result_screen(self, game_simulator, scroll_offset: int = 0) -> Dict[str, Button]:
        """試合結果画面を描画（全選手成績スクロール対応）"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        buttons = {}
        
        if not game_simulator:
            return buttons
        
        # ヘッダー
        header_h = draw_header(self.screen, "試合結果")
        
        home_team = game_simulator.home_team
        away_team = game_simulator.away_team
        home_color = self.get_team_color(home_team.name)
        away_color = self.get_team_color(away_team.name)
        
        # === スコアボード（イニングスコア付き）===
        score_card_w = min(800, width - 40)
        score_card = Card(center_x - score_card_w // 2, header_h + 10, score_card_w, 120)
        score_rect = score_card.draw(self.screen)
        
        # イニング数を取得
        innings_away = game_simulator.inning_scores_away if hasattr(game_simulator, 'inning_scores_away') else []
        innings_home = game_simulator.inning_scores_home if hasattr(game_simulator, 'inning_scores_home') else []
        num_innings = max(9, len(innings_away), len(innings_home))
        
        # イニングスコア表示
        table_y = score_rect.y + 20
        team_col_w = 80
        inning_col_w = 26
        total_col_w = 32
        
        # ヘッダー行（イニング番号）
        x = score_rect.x + team_col_w + 8
        for i in range(1, min(num_innings + 1, 13)):  # 最大12回まで表示
            inn_surf = fonts.tiny.render(str(i), True, Colors.TEXT_MUTED)
            inn_rect = inn_surf.get_rect(center=(x + inning_col_w // 2, table_y))
            self.screen.blit(inn_surf, inn_rect)
            x += inning_col_w
        
        # R/H/E ヘッダー
        for label in ["R", "H", "E"]:
            label_surf = fonts.tiny.render(label, True, Colors.TEXT_MUTED)
            label_rect = label_surf.get_rect(center=(x + total_col_w // 2, table_y))
            self.screen.blit(label_surf, label_rect)
            x += total_col_w
        
        # アウェイチーム行
        table_y += 22
        away_name_short = away_team.name[:4]
        away_surf = fonts.small.render(away_name_short, True, away_color)
        self.screen.blit(away_surf, (score_rect.x + 8, table_y))
        
        x = score_rect.x + team_col_w + 8
        for i in range(min(num_innings, 12)):
            if i < len(innings_away):
                score_val = innings_away[i]
                score_text = str(score_val) if score_val != 'X' else 'X'
                score_color = Colors.WARNING if score_val not in [0, 'X'] else Colors.TEXT_SECONDARY
            else:
                score_text = "-"
                score_color = Colors.TEXT_MUTED
            score_surf = fonts.small.render(score_text, True, score_color)
            score_r = score_surf.get_rect(center=(x + inning_col_w // 2, table_y + 6))
            self.screen.blit(score_surf, score_r)
            x += inning_col_w
        
        # アウェイ R/H/E
        away_hits = sum(v.get('hits', 0) for k, v in game_simulator.batting_results.items() 
                       if k[0] == away_team.name) if hasattr(game_simulator, 'batting_results') else 0
        away_errors = 0
        for val, color in [(game_simulator.away_score, Colors.TEXT_PRIMARY), (away_hits, Colors.TEXT_SECONDARY), (away_errors, Colors.TEXT_SECONDARY)]:
            val_surf = fonts.body.render(str(val), True, color)
            val_rect = val_surf.get_rect(center=(x + total_col_w // 2, table_y + 6))
            self.screen.blit(val_surf, val_rect)
            x += total_col_w
        
        # ホームチーム行
        table_y += 30
        home_name_short = home_team.name[:4]
        home_surf = fonts.small.render(home_name_short, True, home_color)
        self.screen.blit(home_surf, (score_rect.x + 8, table_y))
        
        x = score_rect.x + team_col_w + 8
        for i in range(min(num_innings, 12)):
            if i < len(innings_home):
                score_val = innings_home[i]
                score_text = str(score_val) if score_val != 'X' else 'X'
                score_color = Colors.WARNING if score_val not in [0, 'X'] else Colors.TEXT_SECONDARY
            else:
                score_text = "-"
                score_color = Colors.TEXT_MUTED
            score_surf = fonts.small.render(score_text, True, score_color)
            score_r = score_surf.get_rect(center=(x + inning_col_w // 2, table_y + 6))
            self.screen.blit(score_surf, score_r)
            x += inning_col_w
        
        # ホーム R/H/E
        home_hits = sum(v.get('hits', 0) for k, v in game_simulator.batting_results.items() 
                       if k[0] == home_team.name) if hasattr(game_simulator, 'batting_results') else 0
        home_errors = 0
        for val, color in [(game_simulator.home_score, Colors.TEXT_PRIMARY), (home_hits, Colors.TEXT_SECONDARY), (home_errors, Colors.TEXT_SECONDARY)]:
            val_surf = fonts.body.render(str(val), True, color)
            val_rect = val_surf.get_rect(center=(x + total_col_w // 2, table_y + 6))
            self.screen.blit(val_surf, val_rect)
            x += total_col_w
        
        # === 勝敗結果 ===
        result_y = score_rect.bottom + 5
        if game_simulator.home_score > game_simulator.away_score:
            winner_text = f"◯ {home_team.name} WIN"
            winner_color = home_color
        elif game_simulator.away_score > game_simulator.home_score:
            winner_text = f"◯ {away_team.name} WIN"
            winner_color = away_color
        else:
            winner_text = "△ DRAW"
            winner_color = Colors.WARNING
        
        winner_surf = fonts.h3.render(winner_text, True, winner_color)
        winner_rect = winner_surf.get_rect(center=(center_x, result_y + 12))
        self.screen.blit(winner_surf, winner_rect)
        
        # === 投手成績（左側）・打撃成績（右側）===
        content_y = result_y + 35
        panel_h = height - content_y - 80
        panel_w = (width - 50) // 2
        
        # 投手成績パネル
        pitcher_card = Card(20, content_y, panel_w - 5, panel_h, "投手成績")
        pitcher_rect = pitcher_card.draw(self.screen)
        
        py = pitcher_rect.y + 42
        # ヘッダー
        pitcher_headers = [("投手", 90), ("結", 28), ("回", 32), ("安", 28), ("失", 28), ("自", 28), ("四", 28), ("振", 28)]
        px = pitcher_rect.x + 8
        for hdr, w in pitcher_headers:
            h_surf = fonts.tiny.render(hdr, True, Colors.TEXT_MUTED)
            self.screen.blit(h_surf, (px, py))
            px += w
        py += 18
        
        # 投手データ（両チーム）
        all_pitchers = []
        for team in [away_team, home_team]:
            team_pitchers = []
            # 先発投手
            starter_idx = team.starting_pitcher_idx
            if 0 <= starter_idx < len(team.players):
                team_pitchers.append((team, starter_idx, "先発"))
            
            # 継投した投手を追加
            if hasattr(game_simulator, 'pitching_results'):
                for key, stats in game_simulator.pitching_results.items():
                    if key[0] == team.name and key[1] != starter_idx:
                        team_pitchers.append((team, key[1], "継投"))
            
            all_pitchers.extend(team_pitchers)
        
        # 投手成績表示
        for team, pitcher_idx, role in all_pitchers:
            if pitcher_idx < 0 or pitcher_idx >= len(team.players):
                continue
            pitcher = team.players[pitcher_idx]
            
            px = pitcher_rect.x + 8
            # チーム色バー
            pygame.draw.rect(self.screen, self.get_team_color(team.name), 
                           (px, py + 2, 3, 16), border_radius=1)
            
            # 投手名
            p_name = f"{pitcher.name[:5]}"
            name_surf = fonts.small.render(p_name, True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (px + 6, py))
            px += 90
            
            # 成績取得
            key = (team.name, pitcher_idx)
            if hasattr(game_simulator, 'pitching_results') and key in game_simulator.pitching_results:
                pstats = game_simulator.pitching_results[key]
                # 勝敗判定
                result_mark = ""
                if hasattr(game_simulator, 'winning_pitcher') and game_simulator.winning_pitcher == pitcher_idx:
                    result_mark = "○"
                elif hasattr(game_simulator, 'losing_pitcher') and game_simulator.losing_pitcher == pitcher_idx:
                    result_mark = "●"
                elif hasattr(game_simulator, 'save_pitcher') and game_simulator.save_pitcher == pitcher_idx:
                    result_mark = "S"
                
                ip = f"{pstats.get('ip', 0):.1f}"
                h, r, er = pstats.get('h', 0), pstats.get('r', 0), pstats.get('er', 0)
                bb, so = pstats.get('bb', 0), pstats.get('so', 0)
            else:
                result_mark = ""
                ip = "-"
                h, r, er, bb, so = "-", "-", "-", "-", "-"
            
            for val, w in [(result_mark, 28), (ip, 32), (h, 28), (r, 28), (er, 28), (bb, 28), (so, 28)]:
                v_surf = fonts.small.render(str(val), True, Colors.TEXT_SECONDARY)
                self.screen.blit(v_surf, (px, py))
                px += w
            py += 22
            
            if py > pitcher_rect.bottom - 30:
                break
        
        # 打撃成績パネル（スクロール対応）
        batting_card = Card(panel_w + 30, content_y, panel_w - 5, panel_h, "打撃成績")
        batting_rect = batting_card.draw(self.screen)
        
        by = batting_rect.y + 42
        # ヘッダー
        batting_headers = [("選手", 85), ("打", 28), ("安", 28), ("点", 28), ("本", 28), ("四", 28), ("三", 28)]
        bx = batting_rect.x + 8
        for hdr, w in batting_headers:
            h_surf = fonts.tiny.render(hdr, True, Colors.TEXT_MUTED)
            self.screen.blit(h_surf, (bx, by))
            bx += w
        by += 18
        
        # 全打撃データを収集
        all_batters = []
        for team in [away_team, home_team]:
            lineup = team.current_lineup or []
            for i, player_idx in enumerate(lineup):
                if player_idx is None or player_idx < 0 or player_idx >= len(team.players):
                    continue
                player = team.players[player_idx]
                key = (team.name, player_idx)
                if hasattr(game_simulator, 'batting_results') and key in game_simulator.batting_results:
                    stats = game_simulator.batting_results[key]
                else:
                    stats = {'ab': 0, 'hits': 0, 'rbi': 0, 'hr': 0, 'bb': 0, 'so': 0}
                all_batters.append((team, player, i + 1, stats))
        
        # スクロール対応
        row_height = 20
        visible_rows = (batting_rect.height - 80) // row_height
        max_scroll = max(0, len(all_batters) - visible_rows)
        actual_scroll = min(scroll_offset, max_scroll)
        
        # 打撃データ表示
        for idx, (team, player, order, bstats) in enumerate(all_batters[actual_scroll:actual_scroll + visible_rows]):
            bx = batting_rect.x + 8
            
            # チーム色バー
            pygame.draw.rect(self.screen, self.get_team_color(team.name), 
                           (bx, by + 2, 3, 14), border_radius=1)
            
            # 選手名（打順付き）
            b_name = f"{order}.{player.name[:4]}"
            name_surf = fonts.small.render(b_name, True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (bx + 6, by))
            bx += 85
            
            ab = bstats.get('ab', 0)
            h = bstats.get('hits', 0)
            rbi = bstats.get('rbi', 0)
            hr = bstats.get('hr', 0)
            bb = bstats.get('bb', 0)
            so = bstats.get('so', 0)
            
            for val, w in [(ab, 28), (h, 28), (rbi, 28), (hr, 28), (bb, 28), (so, 28)]:
                # ヒットや打点がある場合は強調
                if (w == 28 and val > 0 and bx < batting_rect.x + 200):
                    v_color = Colors.SUCCESS
                else:
                    v_color = Colors.TEXT_SECONDARY
                v_surf = fonts.small.render(str(val), True, v_color)
                self.screen.blit(v_surf, (bx, by))
                bx += w
            by += row_height
        
        # スクロールバー
        if len(all_batters) > visible_rows:
            scroll_track_h = batting_rect.height - 80
            scroll_h = max(20, int(scroll_track_h * visible_rows / len(all_batters)))
            scroll_y_pos = batting_rect.y + 60 + int((actual_scroll / max(1, max_scroll)) * (scroll_track_h - scroll_h))
            pygame.draw.rect(self.screen, Colors.BG_INPUT, 
                            (batting_rect.right - 12, batting_rect.y + 60, 6, scroll_track_h), border_radius=3)
            pygame.draw.rect(self.screen, Colors.PRIMARY, 
                            (batting_rect.right - 12, scroll_y_pos, 6, scroll_h), border_radius=3)
            
            # スクロールボタン
            if actual_scroll > 0:
                scroll_up_btn = Button(batting_rect.right - 35, batting_rect.y + 45, 25, 20, "▲", "ghost", font=fonts.tiny)
                scroll_up_btn.draw(self.screen)
                buttons["result_scroll_up"] = scroll_up_btn
            if actual_scroll < max_scroll:
                scroll_down_btn = Button(batting_rect.right - 35, batting_rect.bottom - 35, 25, 20, "▼", "ghost", font=fonts.tiny)
                scroll_down_btn.draw(self.screen)
                buttons["result_scroll_down"] = scroll_down_btn
        
        # ボタン
        buttons["next_game"] = Button(
            center_x - 80, height - 70, 160, 50,
            "次へ", "primary", font=fonts.h3
        )
        buttons["next_game"].draw(self.screen)
        
        buttons["back"] = Button(
            50, height - 65, 120, 45,
            "戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # 順位表画面（個人成績タブ付き）
    # ========================================
    def draw_standings_screen(self, central_teams: List, pacific_teams: List, player_team,
                              tab: str = "standings", scroll_offset: int = 0) -> Dict[str, Button]:
        """順位表・個人成績画面を描画"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        header_h = draw_header(self.screen, "RECORDS")
        
        buttons = {}
        
        # タブ
        tabs = [
            ("standings", "順位表"),
            ("batting", "打撃成績"),
            ("pitching", "投手成績"),
        ]
        
        tab_y = header_h + 15
        tab_x = 30
        
        for tab_id, tab_name in tabs:
            style = "primary" if tab == tab_id else "ghost"
            btn = Button(tab_x, tab_y, 120, 38, tab_name, style, font=fonts.small)
            btn.draw(self.screen)
            buttons[f"standings_tab_{tab_id}"] = btn
            tab_x += 130
        
        content_y = header_h + 65
        
        if tab == "standings":
            # 順位表タブ
            panel_width = (width - 80) // 2
            
            leagues = [
                ("セントラル・リーグ", central_teams, 30, Colors.PRIMARY),
                ("パシフィック・リーグ", pacific_teams, 30 + panel_width + 20, Colors.DANGER),
            ]
            
            for league_name, teams, panel_x, accent_color in leagues:
                sorted_teams = sorted(teams, key=lambda t: (-t.win_rate, -t.wins))
                
                panel_rect = pygame.Rect(panel_x, content_y, panel_width, height - content_y - 80)
                draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 16)
                draw_rounded_rect(self.screen, panel_rect, Colors.BG_CARD, 16, 1, Colors.BORDER)
                
                league_surf = fonts.h3.render(league_name, True, accent_color)
                league_rect = league_surf.get_rect(center=(panel_x + panel_width // 2, content_y + 30))
                self.screen.blit(league_surf, league_rect)
                
                headers = ["順", "チーム", "勝", "敗", "分", "率"]
                header_x = [15, 50, 200, 245, 290, 335]
                y = content_y + 55
                
                for i, header in enumerate(headers):
                    h_surf = fonts.tiny.render(header, True, Colors.TEXT_SECONDARY)
                    self.screen.blit(h_surf, (panel_x + header_x[i], y))
                
                y += 22
                pygame.draw.line(self.screen, Colors.BORDER,
                               (panel_x + 10, y), (panel_x + panel_width - 10, y), 1)
                y += 8
                
                for rank, team in enumerate(sorted_teams, 1):
                    row_rect = pygame.Rect(panel_x + 8, y - 3, panel_width - 16, 40)
                    
                    if player_team and team.name == player_team.name:
                        pygame.draw.rect(self.screen, (*accent_color[:3], 30), row_rect, border_radius=4)
                    
                    team_color = self.get_team_color(team.name)
                    
                    rank_color = Colors.GOLD if rank <= 3 else Colors.TEXT_SECONDARY
                    rank_surf = fonts.body.render(str(rank), True, rank_color)
                    self.screen.blit(rank_surf, (panel_x + header_x[0], y + 6))
                    
                    # チーム名を短縮
                    short_name = team.name[:6] if len(team.name) > 6 else team.name
                    name_surf = fonts.small.render(short_name, True, team_color)
                    self.screen.blit(name_surf, (panel_x + header_x[1], y + 8))
                    
                    wins_surf = fonts.small.render(str(team.wins), True, Colors.TEXT_PRIMARY)
                    self.screen.blit(wins_surf, (panel_x + header_x[2], y + 8))
                    
                    losses_surf = fonts.small.render(str(team.losses), True, Colors.TEXT_PRIMARY)
                    self.screen.blit(losses_surf, (panel_x + header_x[3], y + 8))
                    
                    ties_surf = fonts.small.render(str(team.draws), True, Colors.TEXT_PRIMARY)
                    self.screen.blit(ties_surf, (panel_x + header_x[4], y + 8))
                    
                    rate = f".{int(team.win_rate * 1000):03d}" if team.games_played > 0 else ".000"
                    rate_surf = fonts.small.render(rate, True, Colors.TEXT_PRIMARY)
                    self.screen.blit(rate_surf, (panel_x + header_x[5], y + 8))
                    
                    y += 42
        
        elif tab == "batting":
            # 打撃成績タブ
            self._draw_batting_leaders(central_teams + pacific_teams, player_team, 
                                       content_y, width, height, scroll_offset, buttons)
        
        elif tab == "pitching":
            # 投手成績タブ
            self._draw_pitching_leaders(central_teams + pacific_teams, player_team,
                                        content_y, width, height, scroll_offset, buttons)
        
        # 戻るボタン
        buttons["back"] = Button(
            50, height - 70, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    def _draw_batting_leaders(self, all_teams: List, player_team, content_y: int, 
                              width: int, height: int, scroll_offset: int, buttons: Dict):
        """打撃成績ランキングを描画（実績ベース）"""
        # 全選手を収集（野手のみ、規定打席以上）
        all_batters = []
        for team in all_teams:
            for player in team.players:
                if player.position.value != "投手" and player.record.at_bats >= 10:
                    all_batters.append((player, team.name))
        
        # 打撃タイトル別カード
        card_width = (width - 90) // 3
        
        titles = [
            ("打率ランキング", "avg", "打率"),
            ("本塁打ランキング", "hr", "本塁打"),
            ("打点ランキング", "rbi", "打点"),
        ]
        
        for i, (title, stat_type, stat_label) in enumerate(titles):
            card_x = 30 + i * (card_width + 15)
            card = Card(card_x, content_y, card_width, height - content_y - 80, title)
            card_rect = card.draw(self.screen)
            
            # 実績ベースでソート
            if stat_type == "avg":
                sorted_batters = sorted(all_batters, key=lambda x: -x[0].record.batting_average)
            elif stat_type == "hr":
                sorted_batters = sorted(all_batters, key=lambda x: -x[0].record.home_runs)
            else:
                sorted_batters = sorted(all_batters, key=lambda x: -x[0].record.rbis)
            
            y = card_rect.y + 50
            
            for rank, (player, team_name) in enumerate(sorted_batters[:10], 1):
                row_rect = pygame.Rect(card_rect.x + 10, y, card_rect.width - 20, 35)
                
                # 自チームハイライト
                if player_team and team_name == player_team.name:
                    pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 30), row_rect, border_radius=4)
                
                # 順位
                rank_color = Colors.GOLD if rank <= 3 else Colors.TEXT_MUTED
                rank_surf = fonts.small.render(f"{rank}", True, rank_color)
                self.screen.blit(rank_surf, (row_rect.x + 5, y + 8))
                
                # 選手名
                name_surf = fonts.small.render(player.name[:5], True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (row_rect.x + 30, y + 8))
                
                # チーム略称
                abbr = self.get_team_abbr(team_name)
                team_surf = fonts.tiny.render(abbr, True, Colors.TEXT_MUTED)
                self.screen.blit(team_surf, (row_rect.x + 100, y + 10))
                
                # 実績値表示
                if stat_type == "avg":
                    avg = player.record.batting_average
                    display_val = f".{int(avg * 1000):03d}" if avg > 0 else ".000"
                elif stat_type == "hr":
                    display_val = str(player.record.home_runs)
                else:
                    display_val = str(player.record.rbis)
                stat_surf = fonts.body.render(display_val, True, Colors.SUCCESS)
                stat_rect = stat_surf.get_rect(right=row_rect.right - 10, centery=y + 17)
                self.screen.blit(stat_surf, stat_rect)
                
                y += 38
    
    def _draw_pitching_leaders(self, all_teams: List, player_team, content_y: int,
                               width: int, height: int, scroll_offset: int, buttons: Dict):
        """投手成績ランキングを描画（実績ベース）"""
        # 全投手を収集（登板数1以上）
        all_pitchers = []
        for team in all_teams:
            for player in team.players:
                if player.position.value == "投手" and player.record.innings_pitched >= 1:
                    all_pitchers.append((player, team.name))
        
        card_width = (width - 90) // 3
        
        titles = [
            ("防御率ランキング", "era", "防御率"),
            ("奪三振ランキング", "k", "奪三振"),
            ("勝利数ランキング", "wins", "勝利"),
        ]
        
        for i, (title, stat_type, stat_label) in enumerate(titles):
            card_x = 30 + i * (card_width + 15)
            card = Card(card_x, content_y, card_width, height - content_y - 80, title)
            card_rect = card.draw(self.screen)
            
            # 実績ベースでソート
            if stat_type == "era":
                # 防御率は低い順、投球回5以上で
                qualified = [p for p in all_pitchers if p[0].record.innings_pitched >= 5]
                sorted_pitchers = sorted(qualified, key=lambda x: x[0].record.era if x[0].record.era > 0 else 99)
            elif stat_type == "k":
                sorted_pitchers = sorted(all_pitchers, key=lambda x: -x[0].record.strikeouts_pitched)
            else:
                sorted_pitchers = sorted(all_pitchers, key=lambda x: -x[0].record.wins)
            
            y = card_rect.y + 50
            
            for rank, (player, team_name) in enumerate(sorted_pitchers[:10], 1):
                row_rect = pygame.Rect(card_rect.x + 10, y, card_rect.width - 20, 35)
                
                if player_team and team_name == player_team.name:
                    pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 30), row_rect, border_radius=4)
                
                rank_color = Colors.GOLD if rank <= 3 else Colors.TEXT_MUTED
                rank_surf = fonts.small.render(f"{rank}", True, rank_color)
                self.screen.blit(rank_surf, (row_rect.x + 5, y + 8))
                
                name_surf = fonts.small.render(player.name[:5], True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (row_rect.x + 30, y + 8))
                
                abbr = self.get_team_abbr(team_name)
                team_surf = fonts.tiny.render(abbr, True, Colors.TEXT_MUTED)
                self.screen.blit(team_surf, (row_rect.x + 100, y + 10))
                
                # 実績値表示
                if stat_type == "era":
                    era = player.record.era
                    display_val = f"{era:.2f}" if era > 0 else "0.00"
                elif stat_type == "k":
                    display_val = str(player.record.strikeouts_pitched)
                else:
                    display_val = str(player.record.wins)
                stat_surf = fonts.body.render(display_val, True, Colors.SUCCESS)
                stat_rect = stat_surf.get_rect(right=row_rect.right - 10, centery=y + 17)
                self.screen.blit(stat_surf, stat_rect)
                
                y += 38

    # ========================================
    # スケジュール画面
    # ========================================
    def draw_schedule_screen(self, schedule_manager, player_team, scroll_offset: int = 0,
                               selected_game_idx: int = -1) -> Dict[str, Button]:
        """スケジュール画面を描画（NPB完全版）"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        team_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        header_h = draw_header(self.screen, "SCHEDULE", player_team.name if player_team else "", team_color)
        
        buttons = {}
        
        if schedule_manager and player_team:
            games = schedule_manager.get_team_schedule(player_team.name)
            
            # 統計情報を計算
            completed_games = [g for g in games if g.is_completed]
            wins = sum(1 for g in completed_games if g.get_winner() == player_team.name)
            losses = sum(1 for g in completed_games if g.get_winner() and g.get_winner() != player_team.name)
            draws = sum(1 for g in completed_games if g.is_draw())
            
            # 左パネル: シーズン概要
            summary_card = Card(30, header_h + 20, 280, 200, "シーズン概要")
            summary_rect = summary_card.draw(self.screen)
            
            y = summary_rect.y + 55
            summary_items = [
                ("総試合数", f"{len(games)}試合"),
                ("消化試合", f"{len(completed_games)}試合"),
                ("残り試合", f"{len(games) - len(completed_games)}試合"),
                ("", ""),
                ("成績", f"{wins}勝 {losses}敗 {draws}分"),
            ]
            
            for label, value in summary_items:
                if label == "":
                    y += 10
                    continue
                label_surf = fonts.small.render(label, True, Colors.TEXT_SECONDARY)
                value_surf = fonts.small.render(value, True, Colors.TEXT_PRIMARY)
                self.screen.blit(label_surf, (summary_rect.x + 20, y))
                self.screen.blit(value_surf, (summary_rect.x + 130, y))
                y += 28
            
            # 左パネル: 直近の成績
            recent_card = Card(30, header_h + 235, 280, 200, "直近5試合")
            recent_rect = recent_card.draw(self.screen)
            
            recent_games = completed_games[-5:] if len(completed_games) >= 5 else completed_games
            y = recent_rect.y + 55
            
            if recent_games:
                for game in reversed(recent_games):
                    is_home = game.home_team_name == player_team.name
                    opponent = game.away_team_name if is_home else game.home_team_name
                    opponent_abbr = self.get_team_abbr(opponent)
                    
                    my_score = game.home_score if is_home else game.away_score
                    opp_score = game.away_score if is_home else game.home_score
                    
                    # 勝敗マーク
                    if my_score > opp_score:
                        result_mark = "○"
                        result_color = Colors.SUCCESS
                    elif my_score < opp_score:
                        result_mark = "●"
                        result_color = Colors.DANGER
                    else:
                        result_mark = "△"
                        result_color = Colors.WARNING
                    
                    mark_surf = fonts.body.render(result_mark, True, result_color)
                    self.screen.blit(mark_surf, (recent_rect.x + 20, y))
                    
                    vs_text = f"vs {opponent_abbr}"
                    vs_surf = fonts.small.render(vs_text, True, Colors.TEXT_SECONDARY)
                    self.screen.blit(vs_surf, (recent_rect.x + 50, y))
                    
                    score_text = f"{my_score}-{opp_score}"
                    score_surf = fonts.small.render(score_text, True, Colors.TEXT_PRIMARY)
                    self.screen.blit(score_surf, (recent_rect.x + 180, y))
                    
                    y += 28
            else:
                no_game_surf = fonts.small.render("まだ試合がありません", True, Colors.TEXT_MUTED)
                self.screen.blit(no_game_surf, (recent_rect.x + 20, y))
            
            # 右パネル: 全試合日程
            schedule_card = Card(330, header_h + 20, width - 360, height - header_h - 100, "試合日程一覧")
            schedule_rect = schedule_card.draw(self.screen)
            
            # ヘッダー
            headers = [("#", 40), ("日付", 90), ("対戦相手", 160), ("場所", 80), ("スコア", 100), ("結果", 60)]
            x = schedule_rect.x + 20
            y = schedule_rect.y + 50
            
            for header_text, w in headers:
                h_surf = fonts.tiny.render(header_text, True, Colors.TEXT_MUTED)
                self.screen.blit(h_surf, (x, y))
                x += w
            
            y += 25
            pygame.draw.line(self.screen, Colors.BORDER,
                           (schedule_rect.x + 15, y), (schedule_rect.right - 15, y), 1)
            y += 8
            
            # 試合一覧
            row_height = 32
            visible_count = (schedule_rect.height - 100) // row_height
            
            # 次の試合を探す
            next_game_idx = next((i for i, g in enumerate(games) if not g.is_completed), len(games))
            
            for i in range(scroll_offset, min(len(games), scroll_offset + visible_count)):
                game = games[i]
                
                row_rect = pygame.Rect(schedule_rect.x + 10, y - 3, schedule_rect.width - 20, row_height - 2)
                
                # 選択された日程をハイライト
                if i == selected_game_idx and not game.is_completed:
                    pygame.draw.rect(self.screen, (*Colors.GOLD[:3], 60), row_rect, border_radius=4)
                    pygame.draw.rect(self.screen, Colors.GOLD, row_rect, 2, border_radius=4)
                # 次の試合をハイライト
                elif i == next_game_idx:
                    pygame.draw.rect(self.screen, (*team_color[:3], 40), row_rect, border_radius=4)
                    pygame.draw.rect(self.screen, team_color, row_rect, 2, border_radius=4)
                elif i % 2 == 0:
                    pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=2)
                
                # 未完了の試合はクリック可能なボタンとして登録
                if not game.is_completed:
                    row_btn = Button(row_rect.x, row_rect.y, row_rect.width, row_rect.height, "", "ghost")
                    row_btn.color_normal = (0, 0, 0, 0)  # 透明
                    row_btn.color_hover = (*team_color[:3], 30)
                    buttons[f"select_game_{i}"] = row_btn
                
                x = schedule_rect.x + 20
                
                # 試合番号
                num_color = Colors.TEXT_PRIMARY if not game.is_completed else Colors.TEXT_MUTED
                num_surf = fonts.small.render(str(i + 1), True, num_color)
                self.screen.blit(num_surf, (x, y))
                x += 40
                
                # 日付
                date_str = f"{game.month}/{game.day}"
                date_color = Colors.TEXT_PRIMARY if not game.is_completed else Colors.TEXT_MUTED
                date_surf = fonts.small.render(date_str, True, date_color)
                self.screen.blit(date_surf, (x, y))
                x += 90
                
                # 対戦相手
                is_home = game.home_team_name == player_team.name
                opponent = game.away_team_name if is_home else game.home_team_name
                opp_color = self.get_team_color(opponent)
                opp_abbr = self.get_team_abbr(opponent)
                opp_surf = fonts.small.render(opp_abbr, True, opp_color if not game.is_completed else Colors.TEXT_MUTED)
                self.screen.blit(opp_surf, (x, y))
                x += 160
                
                # 場所
                if is_home:
                    loc_text = "HOME"
                    loc_color = Colors.SUCCESS
                else:
                    loc_text = "AWAY"
                    loc_color = Colors.WARNING
                if game.is_completed:
                    loc_color = Colors.TEXT_MUTED
                loc_surf = fonts.tiny.render(loc_text, True, loc_color)
                self.screen.blit(loc_surf, (x, y + 2))
                x += 80
                
                # スコア
                if game.is_completed:
                    my_score = game.home_score if is_home else game.away_score
                    opp_score = game.away_score if is_home else game.home_score
                    score_text = f"{my_score} - {opp_score}"
                    score_surf = fonts.small.render(score_text, True, Colors.TEXT_SECONDARY)
                    self.screen.blit(score_surf, (x, y))
                else:
                    if i == next_game_idx:
                        next_surf = fonts.tiny.render("NEXT", True, team_color)
                        self.screen.blit(next_surf, (x + 10, y + 2))
                    else:
                        pending_surf = fonts.small.render("- - -", True, Colors.TEXT_MUTED)
                        self.screen.blit(pending_surf, (x, y))
                x += 100
                
                # 結果
                if game.is_completed:
                    winner = game.get_winner()
                    if winner == player_team.name:
                        result_text = "勝ち"
                        result_color = Colors.SUCCESS
                    elif winner is None:
                        result_text = "引分"
                        result_color = Colors.WARNING
                    else:
                        result_text = "負け"
                        result_color = Colors.DANGER
                    result_surf = fonts.small.render(result_text, True, result_color)
                    self.screen.blit(result_surf, (x, y))
                
                y += row_height
                
                if y > schedule_rect.bottom - 20:
                    break
            
            # スクロールインジケーター
            if len(games) > visible_count:
                total_pages = (len(games) + visible_count - 1) // visible_count
                current_page = scroll_offset // visible_count + 1
                page_text = f"{current_page}/{total_pages} ページ (スクロールで移動)"
                page_surf = fonts.tiny.render(page_text, True, Colors.TEXT_MUTED)
                self.screen.blit(page_surf, (schedule_rect.x + 20, schedule_rect.bottom - 25))
        
        # ボタン
        buttons["back"] = Button(
            50, height - 70, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        # 次の試合へジャンプボタン
        if schedule_manager and player_team:
            games = schedule_manager.get_team_schedule(player_team.name)
            next_idx = next((i for i, g in enumerate(games) if not g.is_completed), -1)
            if next_idx >= 0:
                buttons["jump_next"] = Button(
                    220, height - 70, 150, 50,
                    "NEXT GAME", "ghost", font=fonts.body
                )
                buttons["jump_next"].draw(self.screen)
                
                # 選択した日程までスキップボタン
                buttons["skip_to_date"] = Button(
                    390, height - 70, 200, 50,
                    "この日程まで進む", "primary", font=fonts.body
                )
                buttons["skip_to_date"].draw(self.screen)
                
                # ヒント
                hint_text = "日程をクリックして選択→「この日程まで進む」で試合をシミュレート"
                hint_surf = fonts.tiny.render(hint_text, True, Colors.TEXT_MUTED)
                self.screen.blit(hint_surf, (620, height - 55))
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # ドラフト画面
    # ========================================
    def draw_draft_screen(self, prospects: List, selected_idx: int = -1, 
                          draft_round: int = 1, draft_messages: List[str] = None,
                          scroll_offset: int = 0) -> Dict[str, Button]:
        """ドラフト画面を描画（スクロール対応）"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        # ヘッダーにラウンド表示
        round_text = f"第{draft_round}巡目"
        header_h = draw_header(self.screen, f"DRAFT - {round_text}", "有望な新人選手を獲得しよう")
        
        buttons = {}
        
        # 左側: 選手リストカード（高さを調整してはみ出し防止）
        card_width = width - 350 if draft_messages else width - 60
        card_height = height - header_h - 140  # ボタン用の余白を確保
        card = Card(30, header_h + 20, card_width - 30, card_height)
        card_rect = card.draw(self.screen)
        
        # ヘッダー
        headers = [("名前", 150), ("ポジション", 100), ("年齢", 60), ("ポテンシャル", 100), ("総合力", 80), ("", 50)]
        x = card_rect.x + 20
        y = card_rect.y + 20
        
        for header_text, w in headers:
            h_surf = fonts.small.render(header_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(h_surf, (x, y))
            x += w
        
        y += 25
        pygame.draw.line(self.screen, Colors.BORDER,
                       (card_rect.x + 15, y), (card_rect.right - 15, y), 1)
        y += 8
        
        # 表示可能な行数を動的に計算（はみ出し防止）
        row_height = 36
        available_height = card_rect.bottom - y - 20  # 余白を確保
        max_visible = available_height // row_height
        visible_count = min(max_visible, len(prospects) - scroll_offset)
        
        for i in range(scroll_offset, min(scroll_offset + visible_count, len(prospects))):
            prospect = prospects[i]
            display_i = i - scroll_offset  # 表示上のインデックス
            
            row_rect = pygame.Rect(card_rect.x + 10, y - 3, card_rect.width - 20, 34)
            
            # 選択中
            if i == selected_idx:
                pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 50), row_rect, border_radius=5)
                pygame.draw.rect(self.screen, Colors.PRIMARY, row_rect, 2, border_radius=5)
            elif display_i % 2 == 0:
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=4)
            
            x = card_rect.x + 20
            
            # 名前
            name_surf = fonts.body.render(prospect.name[:10], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (x, y + 3))
            x += 150
            
            # ポジション
            pos_text = prospect.position.value
            if prospect.pitch_type:
                pos_text += f" ({prospect.pitch_type.value[:2]})"
            pos_surf = fonts.small.render(pos_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (x, y + 5))
            x += 100
            
            # 年齢
            age_surf = fonts.body.render(f"{prospect.age}歳", True, Colors.TEXT_PRIMARY)
            self.screen.blit(age_surf, (x, y + 3))
            x += 60
            
            # ポテンシャル
            pot_color = Colors.GOLD if prospect.potential >= 8 else (
                Colors.SUCCESS if prospect.potential >= 6 else Colors.TEXT_PRIMARY
            )
            pot_surf = fonts.body.render(f"{'★' * min(prospect.potential, 5)}", True, pot_color)
            self.screen.blit(pot_surf, (x, y + 3))
            x += 100
            
            # 総合力
            overall = prospect.stats.overall_batting() if prospect.position.value != "投手" else prospect.stats.overall_pitching()
            overall_surf = fonts.body.render(f"{overall:.0f}", True, Colors.TEXT_PRIMARY)
            self.screen.blit(overall_surf, (x, y + 3))
            x += 80
            
            # 詳細ボタン
            detail_btn = Button(x, y, 40, 28, "詳細", "outline", font=fonts.tiny)
            detail_btn.draw(self.screen)
            buttons[f"draft_detail_{i}"] = detail_btn
            
            y += 36  # 行高さを調整してはみ出し防止
        
        # スクロールバー
        if len(prospects) > 12:
            scroll_track_h = card_rect.height - 80
            scroll_h = max(30, int(scroll_track_h * 12 / len(prospects)))
            scroll_y = card_rect.y + 50 + int((scroll_offset / max(1, len(prospects) - 12)) * (scroll_track_h - scroll_h))
            pygame.draw.rect(self.screen, Colors.BG_INPUT, 
                           (card_rect.right - 15, card_rect.y + 50, 8, scroll_track_h), border_radius=4)
            pygame.draw.rect(self.screen, Colors.PRIMARY,
                           (card_rect.right - 15, scroll_y, 8, scroll_h), border_radius=4)
        
        # 右側: ドラフトログ（メッセージがある場合）
        if draft_messages:
            log_card = Card(width - 310, header_h + 20, 280, height - header_h - 130, "PICK LOG")
            log_rect = log_card.draw(self.screen)
            
            log_y = log_rect.y + 45
            # 最新10件を表示
            recent_msgs = draft_messages[-10:] if len(draft_messages) > 10 else draft_messages
            for msg in recent_msgs:
                msg_surf = fonts.small.render(msg[:35], True, Colors.TEXT_SECONDARY)
                self.screen.blit(msg_surf, (log_rect.x + 10, log_y))
                log_y += 22
        
        # ボタン
        btn_y = height - 90
        
        buttons["draft_player"] = Button(
            center_x + 50, btn_y, 200, 55,
            "この選手を指名", "success", font=fonts.body
        )
        buttons["draft_player"].enabled = selected_idx >= 0
        buttons["draft_player"].draw(self.screen)
        
        buttons["back"] = Button(
            50, btn_y, 150, 50,
            "ドラフト終了", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # 育成ドラフト画面
    # ========================================
    def draw_ikusei_draft_screen(self, prospects: List, selected_idx: int = -1,
                                   draft_round: int = 1, draft_messages: List[str] = None,
                                   scroll_offset: int = 0) -> Dict[str, Button]:
        """育成ドラフト画面を描画（スクロール対応）"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        # ヘッダー
        round_text = f"第{draft_round}巡目"
        header_h = draw_header(self.screen, f"DEVELOPMENT DRAFT - {round_text}", "将来性のある選手を育成枠で獲得")
        
        buttons = {}
        
        # 説明カード
        info_card = Card(30, header_h + 10, 350, 50)
        info_rect = info_card.draw(self.screen)
        info_text = fonts.small.render("育成選手は背番号3桁で支配下登録枠外です", True, Colors.INFO)
        self.screen.blit(info_text, (info_rect.x + 15, info_rect.y + 15))
        
        # 選手リストカード
        card_width = width - 350 if draft_messages else width - 60
        card = Card(30, header_h + 70, card_width - 30, height - header_h - 180)
        card_rect = card.draw(self.screen)
        
        # ヘッダー
        headers = [("名前", 150), ("ポジション", 100), ("年齢", 60), ("伸びしろ", 100), ("総合力", 80), ("", 50)]
        x = card_rect.x + 20
        y = card_rect.y + 20
        
        for header_text, w in headers:
            h_surf = fonts.small.render(header_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(h_surf, (x, y))
            x += w
        
        y += 25
        pygame.draw.line(self.screen, Colors.BORDER,
                       (card_rect.x + 15, y), (card_rect.right - 15, y), 1)
        y += 8
        
        # 選手一覧（育成選手は少し能力が低め、スクロール対応）
        visible_count = min(12, len(prospects) - scroll_offset)
        
        for i in range(scroll_offset, min(scroll_offset + visible_count, len(prospects))):
            prospect = prospects[i]
            display_i = i - scroll_offset
            
            row_rect = pygame.Rect(card_rect.x + 10, y - 3, card_rect.width - 20, 34)
            
            # 選択中
            if i == selected_idx:
                pygame.draw.rect(self.screen, (*Colors.SUCCESS[:3], 50), row_rect, border_radius=5)
                pygame.draw.rect(self.screen, Colors.SUCCESS, row_rect, 2, border_radius=5)
            elif display_i % 2 == 0:
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=4)
            
            x = card_rect.x + 20
            
            # 名前（育成マーク）
            name_text = f"*{prospect.name[:9]}"
            name_surf = fonts.body.render(name_text, True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (x, y + 3))
            x += 150
            
            # ポジション
            pos_text = prospect.position.value
            if hasattr(prospect, 'pitch_type') and prospect.pitch_type:
                pos_text += f" ({prospect.pitch_type.value[:2]})"
            pos_surf = fonts.small.render(pos_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (x, y + 5))
            x += 100
            
            # 年齢
            age_surf = fonts.body.render(f"{prospect.age}歳", True, Colors.TEXT_PRIMARY)
            self.screen.blit(age_surf, (x, y + 3))
            x += 60
            
            # 伸びしろ（潜在能力）
            growth = getattr(prospect, 'growth_potential', prospect.potential)
            growth_color = Colors.SUCCESS if growth >= 7 else (
                Colors.PRIMARY if growth >= 5 else Colors.TEXT_SECONDARY
            )
            growth_bar = "▰" * growth + "▱" * (10 - growth)
            growth_surf = fonts.small.render(growth_bar, True, growth_color)
            self.screen.blit(growth_surf, (x, y + 5))
            x += 100
            
            # 総合力（育成なので低め）
            if hasattr(prospect, 'potential_stats'):
                overall = prospect.potential_stats.overall_batting() if prospect.position.value != "投手" else prospect.potential_stats.overall_pitching()
            else:
                overall = 30  # デフォルト値
            overall_surf = fonts.body.render(f"{overall:.0f}", True, Colors.TEXT_SECONDARY)
            self.screen.blit(overall_surf, (x, y + 3))
            x += 80
            
            # 詳細ボタン
            detail_btn = Button(x, y, 40, 28, "詳細", "outline", font=fonts.tiny)
            detail_btn.draw(self.screen)
            buttons[f"ikusei_detail_{i}"] = detail_btn
            
            y += 38
        
        # スクロールバー
        if len(prospects) > 12:
            scroll_track_h = card_rect.height - 80
            scroll_h = max(30, int(scroll_track_h * 12 / len(prospects)))
            scroll_y = card_rect.y + 50 + int((scroll_offset / max(1, len(prospects) - 12)) * (scroll_track_h - scroll_h))
            pygame.draw.rect(self.screen, Colors.BG_INPUT, 
                           (card_rect.right - 15, card_rect.y + 50, 8, scroll_track_h), border_radius=4)
            pygame.draw.rect(self.screen, Colors.SUCCESS,
                           (card_rect.right - 15, scroll_y, 8, scroll_h), border_radius=4)
        
        # 右側: ドラフトログ
        if draft_messages:
            log_card = Card(width - 310, header_h + 70, 280, height - header_h - 180, "PICK LOG")
            log_rect = log_card.draw(self.screen)
            
            log_y = log_rect.y + 45
            recent_msgs = draft_messages[-10:] if len(draft_messages) > 10 else draft_messages
            for msg in recent_msgs:
                msg_surf = fonts.small.render(msg[:35], True, Colors.TEXT_SECONDARY)
                self.screen.blit(msg_surf, (log_rect.x + 10, log_y))
                log_y += 22
        
        # ボタン
        btn_y = height - 90
        
        buttons["draft_ikusei_player"] = Button(
            center_x + 50, btn_y, 200, 55,
            "この選手を指名", "success", font=fonts.body
        )
        buttons["draft_ikusei_player"].enabled = selected_idx >= 0
        buttons["draft_ikusei_player"].draw(self.screen)
        
        buttons["skip_ikusei"] = Button(
            center_x - 180, btn_y, 180, 50,
            "この巡はパス", "outline", font=fonts.body
        )
        buttons["skip_ikusei"].draw(self.screen)
        
        buttons["finish_ikusei_draft"] = Button(
            50, btn_y, 150, 50,
            "育成終了 →FA", "ghost", font=fonts.body
        )
        buttons["finish_ikusei_draft"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # 選手詳細画面（パワプロ風）
    # ========================================
    def draw_player_detail_screen(self, player, scroll_y: int = 0) -> Dict[str, Button]:
        """選手詳細画面を描画（パワプロ風の能力表示）"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        # ヘッダー
        header_h = draw_header(self.screen, f"{player.name}", f"{player.position.value} / {player.age}歳")
        
        buttons = {}
        
        # スクロール対応の描画領域を設定
        content_y = header_h + 20 - scroll_y
        
        # ========== 基本情報カード ==========
        info_card = Card(30, content_y, 400, 200, "基本情報")
        info_rect = info_card.draw(self.screen)
        
        info_items = [
            ("背番号", f"#{player.uniform_number}"),
            ("ポジション", player.position.value),
            ("年齢", f"{player.age}歳"),
            ("投打", f"{getattr(player.stats, 'throwing_hand', '右')}投{getattr(player.stats, 'batting_hand', '右')}打"),
        ]
        
        y = info_rect.y + 45
        for label, value in info_items:
            label_surf = fonts.small.render(f"{label}:", True, Colors.TEXT_SECONDARY)
            value_surf = fonts.body.render(str(value), True, Colors.TEXT_PRIMARY)
            self.screen.blit(label_surf, (info_rect.x + 20, y))
            self.screen.blit(value_surf, (info_rect.x + 120, y))
            y += 32
        
        # ========== 打撃能力カード ==========
        if player.position.value != "投手":
            batting_card = Card(450, content_y, 400, 250, "BATTING")
            batting_rect = batting_card.draw(self.screen)
            
            batting_stats = [
                ("ミート", player.stats.contact, Colors.INFO),
                ("パワー", player.stats.power, Colors.DANGER),
                ("走力", player.stats.speed, Colors.SUCCESS),
                ("肩力", player.stats.throwing if hasattr(player.stats, 'throwing') else player.stats.arm, Colors.WARNING),
                ("守備", player.stats.fielding, Colors.PRIMARY),
                ("捕球", getattr(player.stats, 'catching', player.stats.fielding), Colors.GOLD),
            ]
            
            y = batting_rect.y + 45
            for stat_name, value, color in batting_stats:
                # ラベル
                label_surf = fonts.small.render(stat_name, True, Colors.TEXT_SECONDARY)
                self.screen.blit(label_surf, (batting_rect.x + 20, y + 3))
                
                # バー
                bar_x = batting_rect.x + 80
                bar_width = 200
                bar_height = 18
                
                # 背景バー
                pygame.draw.rect(self.screen, Colors.BG_INPUT, 
                               (bar_x, y, bar_width, bar_height), border_radius=3)
                
                # 値バー
                filled_width = int(bar_width * value / 100)
                if filled_width > 0:
                    pygame.draw.rect(self.screen, color,
                                   (bar_x, y, filled_width, bar_height), border_radius=3)
                
                # 数値
                value_surf = fonts.body.render(f"{value}", True, Colors.TEXT_PRIMARY)
                self.screen.blit(value_surf, (bar_x + bar_width + 10, y))
                
                # ランク表示
                rank = self._get_ability_rank(value)
                rank_color = self._get_rank_color(rank)
                rank_surf = fonts.body.render(rank, True, rank_color)
                self.screen.blit(rank_surf, (batting_rect.right - 40, y))
                
                y += 30
        
        # ========== 投球能力カード（投手の場合）==========
        if player.position.value == "投手":
            pitching_card = Card(450, content_y, 400, 250, "PITCHING")
            pitching_rect = pitching_card.draw(self.screen)
            
            pitching_stats = [
                ("球速", player.stats.velocity, Colors.DANGER),
                ("コントロール", player.stats.control, Colors.INFO),
                ("スタミナ", player.stats.stamina, Colors.SUCCESS),
                ("変化球", player.stats.breaking_ball, Colors.PRIMARY),
                ("キレ", getattr(player.stats, 'pitch_movement', 50), Colors.WARNING),
            ]
            
            y = pitching_rect.y + 45
            for stat_name, value, color in pitching_stats:
                label_surf = fonts.small.render(stat_name, True, Colors.TEXT_SECONDARY)
                self.screen.blit(label_surf, (pitching_rect.x + 20, y + 3))
                
                bar_x = pitching_rect.x + 100
                bar_width = 180
                bar_height = 18
                
                pygame.draw.rect(self.screen, Colors.BG_INPUT,
                               (bar_x, y, bar_width, bar_height), border_radius=3)
                
                filled_width = int(bar_width * value / 100)
                if filled_width > 0:
                    pygame.draw.rect(self.screen, color,
                                   (bar_x, y, filled_width, bar_height), border_radius=3)
                
                value_surf = fonts.body.render(f"{value}", True, Colors.TEXT_PRIMARY)
                self.screen.blit(value_surf, (bar_x + bar_width + 10, y))
                
                rank = self._get_ability_rank(value)
                rank_color = self._get_rank_color(rank)
                rank_surf = fonts.body.render(rank, True, rank_color)
                self.screen.blit(rank_surf, (pitching_rect.right - 40, y))
                
                y += 35
        
        # ========== 特殊能力カード ==========
        abilities_y = content_y + 260
        special_card = Card(30, abilities_y, width - 60, 150, "✨ 特殊能力")
        special_rect = special_card.draw(self.screen)
        
        special_abilities = []
        
        # パワプロ風特殊能力
        trajectory = getattr(player.stats, 'trajectory', 2)
        if trajectory == 4:
            special_abilities.append(("弾道4", Colors.GOLD))
        elif trajectory == 1:
            special_abilities.append(("弾道1", Colors.TEXT_SECONDARY))
        
        clutch = getattr(player.stats, 'clutch', 10)
        if clutch >= 15:
            special_abilities.append(("チャンス◎", Colors.SUCCESS))
        elif clutch >= 12:
            special_abilities.append(("チャンス○", Colors.INFO))
        elif clutch <= 5:
            special_abilities.append(("チャンスX", Colors.DANGER))
        
        eye = getattr(player.stats, 'eye', 10)
        if eye >= 15:
            special_abilities.append(("選球眼◎", Colors.SUCCESS))
        elif eye >= 12:
            special_abilities.append(("選球眼○", Colors.INFO))
        
        vs_left = getattr(player.stats, 'vs_left_pitching', 10)
        if vs_left >= 15:
            special_abilities.append(("対左投手A", Colors.SUCCESS))
        elif vs_left <= 5:
            special_abilities.append(("対左投手X", Colors.DANGER))
        
        # 投手特殊能力
        if player.position.value == "投手":
            vs_pinch = getattr(player.stats, 'vs_pinch', 10)
            if vs_pinch >= 15:
                special_abilities.append(("対ピンチA", Colors.SUCCESS))
            elif vs_pinch <= 5:
                special_abilities.append(("対ピンチX", Colors.DANGER))
            
            fatigue = getattr(player.stats, 'fatigue_resistance', 10)
            if fatigue >= 15:
                special_abilities.append(("回復A", Colors.SUCCESS))
        
        # 特殊能力表示
        x = special_rect.x + 20
        y = special_rect.y + 45
        for ability_name, color in special_abilities:
            # タグ風の表示
            text_surf = fonts.small.render(ability_name, True, Colors.WHITE)
            text_w = text_surf.get_width()
            tag_rect = pygame.Rect(x, y, text_w + 16, 28)
            pygame.draw.rect(self.screen, color, tag_rect, border_radius=14)
            self.screen.blit(text_surf, (x + 8, y + 6))
            x += text_w + 24
            
            # 折り返し
            if x > special_rect.right - 100:
                x = special_rect.x + 20
                y += 35
        
        # 特殊能力がない場合
        if not special_abilities:
            no_ability = fonts.small.render("特殊能力なし", True, Colors.TEXT_SECONDARY)
            self.screen.blit(no_ability, (special_rect.x + 20, special_rect.y + 55))
        
        # 戻るボタン
        buttons["back"] = Button(
            50, height - 80, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    def _get_ability_rank(self, value: int) -> str:
        """能力値をランクに変換"""
        if value >= 90:
            return "S"
        elif value >= 80:
            return "A"
        elif value >= 70:
            return "B"
        elif value >= 60:
            return "C"
        elif value >= 50:
            return "D"
        elif value >= 40:
            return "E"
        elif value >= 30:
            return "F"
        else:
            return "G"
    
    def _get_rank_color(self, rank: str):
        """ランクに応じた色を返す"""
        colors = {
            "S": Colors.GOLD,
            "A": Colors.DANGER,
            "B": Colors.WARNING,
            "C": Colors.SUCCESS,
            "D": Colors.INFO,
            "E": Colors.TEXT_SECONDARY,
            "F": Colors.TEXT_SECONDARY,
            "G": Colors.TEXT_SECONDARY,
        }
        return colors.get(rank, Colors.TEXT_PRIMARY)
    
    # ========================================
    # 外国人FA画面
    # ========================================
    def draw_free_agent_screen(self, player_team, free_agents: List, selected_idx: int = -1) -> Dict[str, Button]:
        """外国人FA画面を描画"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        team_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        header_h = draw_header(self.screen, "外国人選手市場", 
                               f"予算: {player_team.budget if player_team else 0}億円", team_color)
        
        buttons = {}
        
        # 選手リストカード
        card = Card(30, header_h + 20, width - 60, height - header_h - 130)
        card_rect = card.draw(self.screen)
        
        # ヘッダー
        headers = [("名前", 180), ("ポジション", 120), ("年俸", 100), ("総合力", 100)]
        x = card_rect.x + 25
        y = card_rect.y + 25
        
        for header_text, w in headers:
            h_surf = fonts.small.render(header_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(h_surf, (x, y))
            x += w
        
        y += 30
        pygame.draw.line(self.screen, Colors.BORDER,
                       (card_rect.x + 20, y), (card_rect.right - 20, y), 1)
        y += 10
        
        # 選手一覧（行をクリック可能にするためrect情報を保存）
        self.fa_row_rects = []
        for i, player in enumerate(free_agents[:10]):
            row_rect = pygame.Rect(card_rect.x + 15, y - 5, card_rect.width - 30, 38)
            self.fa_row_rects.append(row_rect)
            
            # 選択中の行はハイライト
            if i == selected_idx:
                pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 60), row_rect, border_radius=4)
                pygame.draw.rect(self.screen, Colors.PRIMARY, row_rect, 2, border_radius=4)
            elif i % 2 == 0:
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=4)
            
            x = card_rect.x + 25
            
            # 名前
            name_surf = fonts.body.render(player.name[:12], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (x, y + 5))
            x += 180
            
            # ポジション
            pos_text = player.position.value
            if player.pitch_type:
                pos_text += f" ({player.pitch_type.value[:2]})"
            pos_surf = fonts.body.render(pos_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (x, y + 5))
            x += 120
            
            # 年俸
            salary_surf = fonts.body.render(f"{player.salary}億", True, Colors.WARNING)
            self.screen.blit(salary_surf, (x, y + 5))
            x += 100
            
            # 総合力
            overall = player.stats.overall_batting() if player.position.value != "投手" else player.stats.overall_pitching()
            overall_surf = fonts.body.render(f"{overall:.0f}", True, Colors.TEXT_PRIMARY)
            self.screen.blit(overall_surf, (x, y + 5))
            
            y += 42
        
        # ボタン行
        btn_y = height - 90
        
        # 獲得ボタン
        sign_style = "primary" if selected_idx >= 0 else "ghost"
        buttons["sign_fa"] = Button(
            center_x - 200, btn_y, 180, 50,
            "SIGN", sign_style, font=fonts.body
        )
        buttons["sign_fa"].draw(self.screen)
        
        # 次へボタン（新シーズン開始）
        buttons["next_season"] = Button(
            center_x + 20, btn_y, 180, 50,
            "NEW SEASON", "success", font=fonts.body
        )
        buttons["next_season"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # 設定画面
    # ========================================
    def draw_settings_screen(self, settings_obj, settings_tab: str = "display", scroll_offset: int = 0) -> Dict[str, Button]:
        """設定画面を描画
        
        Args:
            settings_obj: 設定オブジェクト
            settings_tab: 表示するタブ ("display", "game_rules")
            scroll_offset: スクロールオフセット
        """
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        header_h = draw_header(self.screen, "SETTINGS")
        
        buttons = {}
        
        # タブボタン
        tab_y = header_h + 20
        tab_width = 200
        tabs = [
            ("display", "表示設定"),
            ("game_rules", "ゲームルール"),
        ]
        
        for i, (tab_key, tab_label) in enumerate(tabs):
            style = "primary" if settings_tab == tab_key else "ghost"
            btn = Button(center_x - 210 + i * 220, tab_y, tab_width, 45, tab_label, style, font=fonts.body)
            btn.draw(self.screen)
            buttons[f"settings_tab_{tab_key}"] = btn
        
        card_top = tab_y + 65
        content_height = height - card_top - 100  # 利用可能な高さ
        
        if settings_tab == "display":
            # 表示設定カード
            card = Card(center_x - 350, card_top, 700, 400, "表示設定")
            card_rect = card.draw(self.screen)
            
            y = card_rect.y + 55
            
            # 解像度設定
            res_label = fonts.h3.render("解像度", True, Colors.TEXT_PRIMARY)
            self.screen.blit(res_label, (card_rect.x + 30, y))
            y += 45
            
            resolutions = [(1280, 720), (1600, 900), (1920, 1080)]
            for i, (w, h) in enumerate(resolutions):
                btn_x = card_rect.x + 30 + i * 200
                is_current = (settings_obj.screen_width, settings_obj.screen_height) == (w, h)
                style = "primary" if is_current else "ghost"
                
                btn = Button(btn_x, y, 180, 45, f"{w}x{h}", style, font=fonts.body)
                btn.draw(self.screen)
                buttons[f"resolution_{w}x{h}"] = btn
            
            y += 75
            
            # フルスクリーン
            fullscreen_label = fonts.h3.render("フルスクリーン", True, Colors.TEXT_PRIMARY)
            self.screen.blit(fullscreen_label, (card_rect.x + 30, y))
            
            fullscreen_status = "ON" if settings_obj.fullscreen else "OFF"
            fullscreen_style = "success" if settings_obj.fullscreen else "ghost"
            buttons["toggle_fullscreen"] = Button(
                card_rect.x + 350, y - 5, 120, 45,
                fullscreen_status, fullscreen_style, font=fonts.body
            )
            buttons["toggle_fullscreen"].draw(self.screen)
            
            y += 70
            
            # サウンド
            sound_label = fonts.h3.render("サウンド", True, Colors.TEXT_PRIMARY)
            self.screen.blit(sound_label, (card_rect.x + 30, y))
            
            sound_status = "ON" if settings_obj.sound_enabled else "OFF"
            sound_style = "success" if settings_obj.sound_enabled else "ghost"
            buttons["toggle_sound"] = Button(
                card_rect.x + 350, y - 5, 120, 45,
                sound_status, sound_style, font=fonts.body
            )
            buttons["toggle_sound"].draw(self.screen)
        
        else:  # game_rules タブ
            # ゲームルール設定（スクロール対応）
            rules = settings_obj.game_rules
            
            # スクロール可能エリアの設定
            scroll_area_top = card_top
            scroll_area_height = height - card_top - 100
            max_scroll = max(0, 650 - scroll_area_height)  # コンテンツ高さ - 表示高さ
            scroll_offset = min(scroll_offset, max_scroll)
            
            # クリッピング領域を設定
            clip_rect = pygame.Rect(30, scroll_area_top, width - 60, scroll_area_height)
            self.screen.set_clip(clip_rect)
            
            # 単一カードに全設定を配置
            card = Card(50, card_top - scroll_offset, width - 100, 700, "ゲームルール設定")
            card_rect = card.draw(self.screen)
            
            y = card_rect.y + 55
            col1_x = card_rect.x + 30
            col2_x = card_rect.x + card_rect.width // 2 + 20
            
            # === 左列: DH・リーグ設定 ===
            section_label = fonts.h3.render("DH制ルール", True, Colors.PRIMARY)
            self.screen.blit(section_label, (col1_x, y))
            y += 40
            
            dh_settings = [
                ("セリーグDH制", "central_dh", rules.central_dh),
                ("パリーグDH制", "pacific_dh", rules.pacific_dh),
                ("交流戦DH（ホームルール）", "interleague_dh", rules.interleague_dh),
            ]
            
            for label, key, value in dh_settings:
                label_surf = fonts.small.render(label, True, Colors.TEXT_PRIMARY)
                self.screen.blit(label_surf, (col1_x, y + 6))
                
                status = "ON" if value else "OFF"
                style = "success" if value else "ghost"
                btn = Button(col1_x + 250, y, 80, 32, status, style, font=fonts.tiny)
                btn.draw(self.screen)
                buttons[f"toggle_{key}"] = btn
                y += 40
            
            y += 15
            pygame.draw.line(self.screen, Colors.BORDER, (col1_x, y), (col1_x + 330, y), 1)
            y += 15
            
            # シーズン構成
            section_label = fonts.h3.render("シーズン構成", True, Colors.PRIMARY)
            self.screen.blit(section_label, (col1_x, y))
            y += 40
            
            season_settings = [
                ("春季キャンプ", "enable_spring_camp", rules.enable_spring_camp),
                ("交流戦", "enable_interleague", rules.enable_interleague),
                ("オールスター", "enable_allstar", rules.enable_allstar),
                ("クライマックスシリーズ", "enable_climax_series", rules.enable_climax_series),
                ("タイブレーク制度", "enable_tiebreaker", rules.enable_tiebreaker),
            ]
            
            for label, key, value in season_settings:
                label_surf = fonts.small.render(label, True, Colors.TEXT_PRIMARY)
                self.screen.blit(label_surf, (col1_x, y + 6))
                
                status = "ON" if value else "OFF"
                style = "success" if value else "ghost"
                btn = Button(col1_x + 250, y, 80, 32, status, style, font=fonts.tiny)
                btn.draw(self.screen)
                buttons[f"toggle_{key}"] = btn
                y += 40
            
            # === 右列: 数値設定 ===
            y2 = card_rect.y + 55
            
            section_label = fonts.h3.render("外国人枠", True, Colors.PRIMARY)
            self.screen.blit(section_label, (col2_x, y2))
            y2 += 40
            
            # 外国人枠無制限
            label_surf = fonts.small.render("外国人枠無制限", True, Colors.TEXT_PRIMARY)
            self.screen.blit(label_surf, (col2_x, y2 + 6))
            status = "ON" if rules.unlimited_foreign else "OFF"
            style = "success" if rules.unlimited_foreign else "ghost"
            btn = Button(col2_x + 250, y2, 80, 32, status, style, font=fonts.tiny)
            btn.draw(self.screen)
            buttons["toggle_unlimited_foreign"] = btn
            y2 += 40
            
            # 外国人支配下枠
            label_surf = fonts.small.render("外国人支配下枠", True, Colors.TEXT_PRIMARY)
            self.screen.blit(label_surf, (col2_x, y2 + 6))
            y2 += 28
            btn_x = col2_x
            for opt in [0, 3, 4, 5]:
                display = "無制限" if opt == 0 else str(opt)
                is_selected = rules.foreign_player_limit == opt
                style = "primary" if is_selected else "outline"
                btn = Button(btn_x, y2, 70, 28, display, style, font=fonts.tiny)
                btn.draw(self.screen)
                buttons[f"set_foreign_player_limit_{opt}"] = btn
                btn_x += 78
            y2 += 45
            
            pygame.draw.line(self.screen, Colors.BORDER, (col2_x, y2), (col2_x + 330, y2), 1)
            y2 += 15
            
            section_label = fonts.h3.render("試合・登録設定", True, Colors.PRIMARY)
            self.screen.blit(section_label, (col2_x, y2))
            y2 += 40
            
            # 数値設定（コンパクト版）
            number_settings = [
                ("シーズン試合数", "regular_season_games", rules.regular_season_games, [120, 130, 143]),
                ("一軍登録枠", "roster_limit", rules.roster_limit, [25, 26, 28]),
                ("延長上限", "extra_innings_limit", rules.extra_innings_limit, [9, 12, 0]),
                ("キャンプ日数", "spring_camp_days", rules.spring_camp_days, [14, 21, 28]),
            ]
            
            for label, key, current_value, options in number_settings:
                label_surf = fonts.small.render(label, True, Colors.TEXT_PRIMARY)
                self.screen.blit(label_surf, (col2_x, y2 + 6))
                y2 += 28
                
                btn_x = col2_x
                for opt in options:
                    if opt == 0 and "innings" in key:
                        display = "無制限"
                    else:
                        display = str(opt)
                    
                    is_selected = current_value == opt
                    style = "primary" if is_selected else "outline"
                    btn = Button(btn_x, y2, 70, 28, display, style, font=fonts.tiny)
                    btn.draw(self.screen)
                    buttons[f"set_{key}_{opt}"] = btn
                    btn_x += 78
                y2 += 42
            
            # クリッピング解除
            self.screen.set_clip(None)
            
            # スクロールバー
            if max_scroll > 0:
                scrollbar_height = scroll_area_height * scroll_area_height / 650
                scrollbar_y = scroll_area_top + (scroll_offset / max_scroll) * (scroll_area_height - scrollbar_height)
                pygame.draw.rect(self.screen, Colors.BG_CARD_HOVER, 
                               (width - 25, scroll_area_top, 8, scroll_area_height), border_radius=4)
                pygame.draw.rect(self.screen, Colors.PRIMARY, 
                               (width - 25, scrollbar_y, 8, scrollbar_height), border_radius=4)
        
        # 戻るボタン
        buttons["back"] = Button(
            50, height - 70, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons

    # ========================================
    # チーム成績画面
    # ========================================
    def draw_team_stats_screen(self, player_team, current_year: int) -> Dict[str, Button]:
        """チーム成績詳細画面を描画"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        team_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        
        header_h = draw_header(self.screen, f"{player_team.name} 成績",
                               f"{current_year}年シーズン", team_color)
        
        buttons = {}
        
        if player_team:
            # 左パネル: チーム基本情報
            basic_card = Card(30, header_h + 20, 350, 450, "シーズン成績")
            basic_rect = basic_card.draw(self.screen)
            
            y = basic_rect.y + 55
            
            # 本拠地球場
            stadium = NPB_STADIUMS.get(player_team.name, {})
            stadium_name = stadium.get("name", "不明")
            stadium_capacity = stadium.get("capacity", 0)
            
            # チーム基本情報
            info_items = [
                ("本拠地", stadium_name),
                ("収容人数", f"{stadium_capacity:,}人" if stadium_capacity > 0 else "不明"),
                ("", ""),  # 空行
                ("勝利", f"{player_team.wins}"),
                ("敗北", f"{player_team.losses}"),
                ("引分", f"{player_team.draws}"),
                ("", ""),  # 空行
                ("勝率", f".{int(player_team.win_rate * 1000):03d}" if player_team.games_played > 0 else ".000"),
                ("消化試合", f"{player_team.games_played}/143"),
                ("残り試合", f"{143 - player_team.games_played}"),
            ]
            
            for label, value in info_items:
                if label == "":
                    y += 15
                    continue
                label_surf = fonts.body.render(label, True, Colors.TEXT_SECONDARY)
                value_surf = fonts.body.render(value, True, Colors.TEXT_PRIMARY)
                self.screen.blit(label_surf, (basic_rect.x + 25, y))
                self.screen.blit(value_surf, (basic_rect.x + 160, y))
                y += 32
            
            # シーズン進行バー
            y += 10
            progress = player_team.games_played / 143 if player_team.games_played > 0 else 0
            bar = ProgressBar(basic_rect.x + 25, y, 300, 18, progress, team_color)
            bar.draw(self.screen)
            
            # 中央パネル: 打撃成績上位
            batting_card = Card(400, header_h + 20, 360, 320, "🏏 打撃成績上位")
            bat_rect = batting_card.draw(self.screen)
            
            # 打者をフィルタ
            batters = [p for p in player_team.players if p.position.value != "投手"]
            # 打率でソート（仮の計算）
            sorted_batters = sorted(batters, 
                                   key=lambda p: p.stats.contact + p.stats.power + p.stats.speed, 
                                   reverse=True)[:6]
            
            y = bat_rect.y + 55
            headers = ["選手", "打率", "本", "打点"]
            header_x = [25, 150, 230, 280]
            
            for i, h in enumerate(headers):
                h_surf = fonts.tiny.render(h, True, Colors.TEXT_MUTED)
                self.screen.blit(h_surf, (bat_rect.x + header_x[i], y))
            
            y += 28
            
            for player in sorted_batters:
                # 選手名
                name_surf = fonts.small.render(player.name[:10], True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (bat_rect.x + header_x[0], y))
                
                # 仮のシーズン成績（実際のゲームでは累積する）
                avg = 0.220 + (player.stats.contact / 1000)
                hr = int(player.stats.power / 5)
                rbi = int((player.stats.power + player.stats.contact) / 4)
                
                avg_surf = fonts.small.render(f".{int(avg * 1000):03d}", True, Colors.TEXT_SECONDARY)
                self.screen.blit(avg_surf, (bat_rect.x + header_x[1], y))
                
                hr_surf = fonts.small.render(str(hr), True, Colors.TEXT_SECONDARY)
                self.screen.blit(hr_surf, (bat_rect.x + header_x[2], y))
                
                rbi_surf = fonts.small.render(str(rbi), True, Colors.TEXT_SECONDARY)
                self.screen.blit(rbi_surf, (bat_rect.x + header_x[3], y))
                
                y += 32
            
            # 投手成績
            pitching_card = Card(400, header_h + 360, 360, 180, "PITCHING TOP")
            pitch_rect = pitching_card.draw(self.screen)
            
            pitchers = [p for p in player_team.players if p.position.value == "投手"]
            sorted_pitchers = sorted(pitchers,
                                    key=lambda p: p.stats.overall_pitching(),
                                    reverse=True)[:3]
            
            y = pitch_rect.y + 55
            p_headers = ["選手", "防御率", "勝", "負", "S"]
            p_header_x = [25, 130, 205, 245, 285]
            
            for i, h in enumerate(p_headers):
                h_surf = fonts.tiny.render(h, True, Colors.TEXT_MUTED)
                self.screen.blit(h_surf, (pitch_rect.x + p_header_x[i], y))
            
            y += 28
            
            for player in sorted_pitchers:
                name_surf = fonts.small.render(player.name[:8], True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (pitch_rect.x + p_header_x[0], y))
                
                # 仮のシーズン成績
                era = 5.00 - (player.stats.control / 50) - (player.stats.stamina / 100)
                era = max(1.50, min(6.00, era))
                wins = int(player.stats.control / 10)
                losses = max(0, 10 - wins)
                saves = 0 if player.pitch_type and player.pitch_type.value != "クローザー" else int(player.stats.control / 5)
                
                era_surf = fonts.small.render(f"{era:.2f}", True, Colors.TEXT_SECONDARY)
                self.screen.blit(era_surf, (pitch_rect.x + p_header_x[1], y))
                
                w_surf = fonts.small.render(str(wins), True, Colors.TEXT_SECONDARY)
                self.screen.blit(w_surf, (pitch_rect.x + p_header_x[2], y))
                
                l_surf = fonts.small.render(str(losses), True, Colors.TEXT_SECONDARY)
                self.screen.blit(l_surf, (pitch_rect.x + p_header_x[3], y))
                
                s_surf = fonts.small.render(str(saves), True, Colors.TEXT_SECONDARY)
                self.screen.blit(s_surf, (pitch_rect.x + p_header_x[4], y))
                
                y += 28
            
            # 右パネル: タイトル候補
            title_card = Card(780, header_h + 20, 330, 520, "TITLE RACE")
            title_rect = title_card.draw(self.screen)
            
            y = title_rect.y + 55
            
            # 打撃タイトル
            bat_title_label = fonts.small.render("【打撃部門】", True, Colors.GOLD)
            self.screen.blit(bat_title_label, (title_rect.x + 20, y))
            y += 30
            
            for title_key, title_name in list(NPB_BATTING_TITLES.items())[:4]:
                title_surf = fonts.tiny.render(f"・{title_name}", True, Colors.TEXT_SECONDARY)
                self.screen.blit(title_surf, (title_rect.x + 30, y))
                
                # 最有力候補（チーム内）
                if sorted_batters:
                    candidate = sorted_batters[0]
                    cand_surf = fonts.tiny.render(f"→ {candidate.name[:6]}", True, Colors.TEXT_MUTED)
                    self.screen.blit(cand_surf, (title_rect.x + 170, y))
                y += 25
            
            y += 20
            
            # 投手タイトル
            pitch_title_label = fonts.small.render("【投手部門】", True, Colors.SECONDARY)
            self.screen.blit(pitch_title_label, (title_rect.x + 20, y))
            y += 30
            
            for title_key, title_name in list(NPB_PITCHING_TITLES.items())[:4]:
                title_surf = fonts.tiny.render(f"・{title_name}", True, Colors.TEXT_SECONDARY)
                self.screen.blit(title_surf, (title_rect.x + 30, y))
                
                if sorted_pitchers:
                    candidate = sorted_pitchers[0]
                    cand_surf = fonts.tiny.render(f"→ {candidate.name[:6]}", True, Colors.TEXT_MUTED)
                    self.screen.blit(cand_surf, (title_rect.x + 170, y))
                y += 25
        
        # 戻るボタン
        buttons["back"] = Button(
            50, height - 70, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons

    # ========================================
    # チーム編集画面
    # ========================================
    def draw_team_edit_screen(self, all_teams: List, editing_team_idx: int = -1, 
                               input_text: str = "", custom_names: Dict = None) -> Dict[str, Button]:
        """チーム名編集画面を描画"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        header_h = draw_header(self.screen, "チーム名編集", 
                               "各チームの名前をカスタマイズできます")
        
        buttons = {}
        custom_names = custom_names or {}
        
        # メインカード
        card_width = min(900, width - 60)
        card_x = (width - card_width) // 2
        main_card = Card(card_x, header_h + 20, card_width, height - header_h - 100, "チーム一覧")
        card_rect = main_card.draw(self.screen)
        
        # ヘッダー行
        y = card_rect.y + 55
        headers = [("リーグ", 80), ("デフォルト名", 220), ("カスタム名", 250), ("操作", 120)]
        x = card_rect.x + 25
        
        for header_text, col_width in headers:
            header_surf = fonts.small.render(header_text, True, Colors.TEXT_MUTED)
            self.screen.blit(header_surf, (x, y))
            x += col_width
        
        y += 35
        pygame.draw.line(self.screen, Colors.BORDER,
                        (card_rect.x + 20, y - 5),
                        (card_rect.x + card_width - 40, y - 5), 1)
        
        # チーム一覧
        for idx, team in enumerate(all_teams):
            row_y = y + idx * 45
            if row_y > card_rect.y + card_rect.height - 50:
                break
            
            # 編集中のチームをハイライト
            if idx == editing_team_idx:
                highlight_rect = pygame.Rect(card_rect.x + 15, row_y - 5, card_width - 50, 40)
                pygame.draw.rect(self.screen, (*Colors.PRIMARY[:3], 30), highlight_rect, border_radius=4)
            
            x = card_rect.x + 25
            
            # リーグ
            league_text = "セ" if idx < 6 else "パ"
            league_color = Colors.PRIMARY if idx < 6 else Colors.DANGER
            league_surf = fonts.body.render(league_text, True, league_color)
            self.screen.blit(league_surf, (x + 20, row_y))
            x += 80
            
            # デフォルト名
            team_color = self.get_team_color(team.name)
            default_name_surf = fonts.body.render(team.name[:12], True, team_color)
            self.screen.blit(default_name_surf, (x, row_y))
            x += 220
            
            # カスタム名（入力中 or 設定済み）
            if idx == editing_team_idx:
                # 入力ボックス
                input_rect = pygame.Rect(x, row_y - 3, 200, 32)
                pygame.draw.rect(self.screen, Colors.BG_INPUT, input_rect, border_radius=4)
                pygame.draw.rect(self.screen, Colors.PRIMARY, input_rect, 2, border_radius=4)
                
                display_text = input_text if input_text else "入力してください..."
                text_color = Colors.TEXT_PRIMARY if input_text else Colors.TEXT_MUTED
                input_surf = fonts.body.render(display_text[:14], True, text_color)
                self.screen.blit(input_surf, (x + 8, row_y + 2))
                
                # カーソル（点滅）
                if int(time.time() * 2) % 2 == 0:
                    cursor_x = x + 8 + fonts.body.size(input_text[:14])[0]
                    pygame.draw.line(self.screen, Colors.TEXT_PRIMARY,
                                   (cursor_x, row_y), (cursor_x, row_y + 24), 2)
            else:
                custom_name = custom_names.get(team.name, "")
                if custom_name:
                    custom_surf = fonts.body.render(custom_name[:14], True, Colors.SUCCESS)
                    self.screen.blit(custom_surf, (x, row_y))
                else:
                    no_custom_surf = fonts.body.render("---", True, Colors.TEXT_MUTED)
                    self.screen.blit(no_custom_surf, (x, row_y))
            
            x += 250
            
            # 編集ボタン
            if idx == editing_team_idx:
                # 確定・キャンセルボタン
                confirm_btn = Button(x, row_y - 5, 50, 32, "OK", "success", font=fonts.small)
                confirm_btn.draw(self.screen)
                buttons[f"confirm_edit_{idx}"] = confirm_btn
                
                cancel_btn = Button(x + 55, row_y - 5, 50, 32, "✗", "danger", font=fonts.small)
                cancel_btn.draw(self.screen)
                buttons[f"cancel_edit_{idx}"] = cancel_btn
            else:
                edit_btn = Button(x, row_y - 5, 70, 32, "編集", "ghost", font=fonts.small)
                edit_btn.draw(self.screen)
                buttons[f"edit_team_{idx}"] = edit_btn
                
                # リセットボタン（カスタム名がある場合）
                if team.name in custom_names:
                    reset_btn = Button(x + 75, row_y - 5, 45, 32, "X", "ghost", font=fonts.small)
                    reset_btn.draw(self.screen)
                    buttons[f"reset_team_{idx}"] = reset_btn
        
        # 下部ボタン
        buttons["back_to_select"] = Button(
            50, height - 70, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back_to_select"].draw(self.screen)
        
        buttons["apply_names"] = Button(
            width - 200, height - 70, 150, 50,
            "適用して選択へ", "primary", font=fonts.body
        )
        buttons["apply_names"].draw(self.screen)
        
        # ヒント
        hint_text = "チーム名を変更すると、ゲーム内のすべての表示に反映されます"
        hint_surf = fonts.tiny.render(hint_text, True, Colors.TEXT_MUTED)
        self.screen.blit(hint_surf, ((width - hint_surf.get_width()) // 2, height - 25))
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons

    # ========================================
    # 育成画面
    # ========================================
    def draw_training_screen(self, player_team, selected_player_idx: int = -1,
                              training_points: int = 0) -> Dict[str, Button]:
        """育成画面を描画"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        team_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        header_h = draw_header(self.screen, "💪 育成", "選手を鍛えて能力アップ！", team_color)
        
        buttons = {}
        
        if not player_team:
            return buttons
        
        # 左パネル: 選手一覧
        roster_card = Card(30, header_h + 20, 400, height - header_h - 100, "選手一覧")
        roster_rect = roster_card.draw(self.screen)
        
        # 育成ポイント表示
        points_text = f"育成ポイント: {training_points}pt"
        points_surf = fonts.h3.render(points_text, True, Colors.GOLD)
        self.screen.blit(points_surf, (roster_rect.x + 20, roster_rect.y + 50))
        
        # ヘッダー行
        y = roster_rect.y + 90
        headers = [("名前", 150), ("Pos", 60), ("年齢", 50), ("総合", 70)]
        x = roster_rect.x + 20
        
        for header_text, col_width in headers:
            h_surf = fonts.tiny.render(header_text, True, Colors.TEXT_MUTED)
            self.screen.blit(h_surf, (x, y))
            x += col_width
        
        y += 25
        pygame.draw.line(self.screen, Colors.BORDER,
                        (roster_rect.x + 15, y), (roster_rect.right - 15, y), 1)
        y += 8
        
        # 選手リスト
        players = player_team.players[:20]  # 最大20人表示
        for idx, player in enumerate(players):
            row_rect = pygame.Rect(roster_rect.x + 10, y - 3, roster_rect.width - 20, 28)
            
            # 選択中の選手をハイライト
            if idx == selected_player_idx:
                pygame.draw.rect(self.screen, (*team_color[:3], 50), row_rect, border_radius=4)
                pygame.draw.rect(self.screen, team_color, row_rect, 2, border_radius=4)
            elif idx % 2 == 0:
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=2)
            
            # クリック可能なボタンとして登録
            row_btn = Button(row_rect.x, row_rect.y, row_rect.width, row_rect.height, "", "ghost")
            row_btn.color_normal = (0, 0, 0, 0)
            row_btn.color_hover = (*team_color[:3], 30)
            buttons[f"select_player_{idx}"] = row_btn
            
            x = roster_rect.x + 20
            
            # 名前
            name_surf = fonts.small.render(player.name[:8], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (x, y))
            x += 150
            
            # ポジション
            pos_surf = fonts.tiny.render(player.position.value[:3], True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (x, y + 2))
            x += 60
            
            # 年齢
            age_surf = fonts.small.render(str(player.age), True, Colors.TEXT_SECONDARY)
            self.screen.blit(age_surf, (x, y))
            x += 50
            
            # 総合力
            if player.position.value == "投手":
                overall = player.stats.overall_pitching()
            else:
                overall = player.stats.overall_batting()
            overall_surf = fonts.small.render(f"{overall:.0f}", True, Colors.PRIMARY)
            self.screen.blit(overall_surf, (x, y))
            
            y += 30
            
            if y > roster_rect.bottom - 30:
                break
        
        # 右パネル: 選手詳細 & 育成メニュー
        if selected_player_idx >= 0 and selected_player_idx < len(players):
            player = players[selected_player_idx]
            
            # 選手詳細カード
            detail_card = Card(450, header_h + 20, width - 480, 280, f"{player.name}")
            detail_rect = detail_card.draw(self.screen)
            
            y = detail_rect.y + 55
            
            # 基本情報
            potential = player.growth.potential if player.growth else 5
            info_items = [
                ("ポジション", player.position.value),
                ("年齢", f"{player.age}歳"),
                ("ポテンシャル", f"{'★' * (potential // 2)}{'☆' * (5 - potential // 2)}"),
            ]
            
            for label, value in info_items:
                label_surf = fonts.small.render(label, True, Colors.TEXT_SECONDARY)
                value_surf = fonts.small.render(value, True, Colors.TEXT_PRIMARY)
                self.screen.blit(label_surf, (detail_rect.x + 20, y))
                self.screen.blit(value_surf, (detail_rect.x + 130, y))
                y += 28
            
            y += 10
            
            # 能力値表示
            if player.position.value == "投手":
                stats_items = [
                    ("球速", player.stats.speed, Colors.DANGER),
                    ("制球", player.stats.control, Colors.PRIMARY),
                    ("変化", player.stats.breaking, Colors.SUCCESS),
                    ("スタミナ", player.stats.stamina, Colors.WARNING),
                ]
            else:
                stats_items = [
                    ("ミート", player.stats.contact, Colors.PRIMARY),
                    ("パワー", player.stats.power, Colors.DANGER),
                    ("走力", player.stats.run, Colors.SUCCESS),
                    ("守備", player.stats.fielding, Colors.WARNING),
                ]
            
            for label, value, color in stats_items:
                label_surf = fonts.small.render(label, True, Colors.TEXT_SECONDARY)
                self.screen.blit(label_surf, (detail_rect.x + 20, y))
                
                # 能力バー
                bar_width = 200
                bar_rect = pygame.Rect(detail_rect.x + 100, y + 3, bar_width, 14)
                pygame.draw.rect(self.screen, Colors.BG_INPUT, bar_rect, border_radius=7)
                
                fill_width = int(bar_width * min(value, 20) / 20)
                fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, 14)
                pygame.draw.rect(self.screen, color, fill_rect, border_radius=7)
                
                value_surf = fonts.tiny.render(f"{value}", True, Colors.TEXT_PRIMARY)
                self.screen.blit(value_surf, (bar_rect.right + 10, y + 1))
                
                y += 28
            
            # 育成メニューカード
            training_card = Card(450, header_h + 320, width - 480, height - header_h - 420, "TRAINING MENU")
            training_rect = training_card.draw(self.screen)
            
            y = training_rect.y + 55
            
            # 育成オプション
            if player.position.value == "投手":
                training_options = [
                    ("train_velocity", "球速強化", "球速+1", 50),
                    ("train_control", "制球強化", "制球+1", 40),
                    ("train_breaking", "変化球強化", "変化+1", 45),
                    ("train_stamina", "スタミナ強化", "スタミナ+1", 35),
                ]
            else:
                training_options = [
                    ("train_contact", "ミート強化", "ミート+1", 40),
                    ("train_power", "パワー強化", "パワー+1", 50),
                    ("train_speed", "走力強化", "走力+1", 35),
                    ("train_defense", "守備強化", "守備+1", 40),
                ]
            
            for btn_name, btn_text, effect, cost in training_options:
                btn = Button(
                    training_rect.x + 20, y, 200, 40,
                    btn_text, "ghost" if training_points >= cost else "outline",
                    font=fonts.small
                )
                btn.draw(self.screen)
                buttons[btn_name] = btn
                
                # 効果とコスト
                effect_surf = fonts.tiny.render(effect, True, Colors.SUCCESS)
                cost_color = Colors.TEXT_PRIMARY if training_points >= cost else Colors.DANGER
                cost_surf = fonts.tiny.render(f"{cost}pt", True, cost_color)
                self.screen.blit(effect_surf, (training_rect.x + 240, y + 5))
                self.screen.blit(cost_surf, (training_rect.x + 240, y + 22))
                
                y += 50
        else:
            # 選手未選択時
            hint_card = Card(450, header_h + 20, width - 480, 200, "ヒント")
            hint_rect = hint_card.draw(self.screen)
            
            hint_text = "左の一覧から選手を選択してください"
            hint_surf = fonts.body.render(hint_text, True, Colors.TEXT_MUTED)
            self.screen.blit(hint_surf, (hint_rect.x + 30, hint_rect.y + 80))
        
        # 戻るボタン
        buttons["back"] = Button(
            50, height - 70, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons

    # ========================================
    # 経営画面
    # ========================================
    def draw_management_screen(self, player_team: Team, finances, tab: str = "overview") -> Dict[str, Button]:
        """経営画面を描画"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        buttons = {}
        
        # ヘッダー
        header_h = 80
        team_info = player_team.name if player_team else None
        draw_header(self.screen, "MANAGEMENT", team_info)
        
        # タブ
        tabs = [
            ("overview", "概要"),
            ("finances", "財務"),
            ("facilities", "施設"),
            ("sponsors", "スポンサー"),
            ("staff", "スタッフ"),
        ]
        
        tab_y = header_h + 15
        tab_x = 30
        
        for tab_id, tab_name in tabs:
            style = "primary" if tab == tab_id else "ghost"
            btn = Button(tab_x, tab_y, 130, 40, tab_name, style, font=fonts.small)
            btn.draw(self.screen)
            buttons[f"mgmt_tab_{tab_id}"] = btn
            tab_x += 140
        
        # 財務データの取得（デフォルト値）
        if finances:
            budget = finances.budget if hasattr(finances, 'budget') else 50.0
            payroll = finances.payroll if hasattr(finances, 'payroll') else 30.0
            revenue = finances.revenue if hasattr(finances, 'revenue') else 25.0
            sponsorship = finances.sponsorship if hasattr(finances, 'sponsorship') else 10.0
            ticket_sales = finances.ticket_sales if hasattr(finances, 'ticket_sales') else 5.0
            merchandise = finances.merchandise if hasattr(finances, 'merchandise') else 3.0
        else:
            budget = 50.0
            payroll = 30.0
            revenue = 25.0
            sponsorship = 10.0
            ticket_sales = 5.0
            merchandise = 3.0
        
        available = budget - payroll
        
        content_y = header_h + 70
        
        if tab == "overview":
            # 概要タブ
            # 左カード: 収支サマリー
            summary_card = Card(30, content_y, 380, 250, "SUMMARY")
            summary_rect = summary_card.draw(self.screen)
            
            y = summary_rect.y + 55
            summary_items = [
                ("総予算", f"{budget:.1f}億円", Colors.PRIMARY),
                ("年俸総額", f"{payroll:.1f}億円", Colors.DANGER),
                ("利用可能", f"{available:.1f}億円", Colors.SUCCESS if available > 0 else Colors.DANGER),
                ("年間収入", f"{revenue:.1f}億円", Colors.TEXT_PRIMARY),
            ]
            
            for label, value, color in summary_items:
                label_surf = fonts.body.render(label, True, Colors.TEXT_SECONDARY)
                value_surf = fonts.h3.render(value, True, color)
                self.screen.blit(label_surf, (summary_rect.x + 25, y))
                self.screen.blit(value_surf, (summary_rect.x + 200, y))
                y += 45
            
            # 右カード: 収入内訳
            income_card = Card(430, content_y, 350, 250, "INCOME")
            income_rect = income_card.draw(self.screen)
            
            y = income_rect.y + 55
            income_items = [
                ("スポンサー", sponsorship),
                ("チケット売上", ticket_sales),
                ("グッズ売上", merchandise),
            ]
            
            total_income = sponsorship + ticket_sales + merchandise
            
            for label, value in income_items:
                label_surf = fonts.body.render(label, True, Colors.TEXT_SECONDARY)
                self.screen.blit(label_surf, (income_rect.x + 20, y))
                
                # 棒グラフ
                bar_width = 150
                bar_rect = pygame.Rect(income_rect.x + 120, y + 3, bar_width, 20)
                pygame.draw.rect(self.screen, Colors.BG_INPUT, bar_rect, border_radius=10)
                
                if total_income > 0:
                    fill_ratio = value / total_income
                    fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_width * fill_ratio), 20)
                    pygame.draw.rect(self.screen, Colors.SUCCESS, fill_rect, border_radius=10)
                
                value_surf = fonts.small.render(f"{value:.1f}億", True, Colors.TEXT_PRIMARY)
                self.screen.blit(value_surf, (bar_rect.right + 10, y + 2))
                
                y += 40
            
            # 下カード: 今後の予定
            schedule_card = Card(30, content_y + 270, 750, 180, "SCHEDULE")
            schedule_rect = schedule_card.draw(self.screen)
            
            y = schedule_rect.y + 55
            schedule_items = [
                ("ドラフト契約金", "約5.0億円", "10月"),
                ("FA補強", "予算10.0億円", "11-12月"),
                ("施設維持費", "年間3.0億円", "通年"),
            ]
            
            for i, (item, amount, period) in enumerate(schedule_items):
                x_offset = schedule_rect.x + 25 + i * 240
                item_surf = fonts.body.render(item, True, Colors.TEXT_PRIMARY)
                amount_surf = fonts.small.render(amount, True, Colors.WARNING)
                period_surf = fonts.tiny.render(period, True, Colors.TEXT_MUTED)
                self.screen.blit(item_surf, (x_offset, y))
                self.screen.blit(amount_surf, (x_offset, y + 28))
                self.screen.blit(period_surf, (x_offset, y + 50))
        
        elif tab == "finances":
            # 財務タブ
            # 年俸一覧
            payroll_card = Card(30, content_y, 500, height - content_y - 100, "💵 選手年俸一覧")
            payroll_rect = payroll_card.draw(self.screen)
            
            y = payroll_rect.y + 55
            
            if player_team:
                # 年俸順にソート
                sorted_players = sorted(player_team.players, 
                    key=lambda p: p.salary if hasattr(p, 'salary') else 1000, reverse=True)
                
                for i, player in enumerate(sorted_players[:12]):
                    salary = player.salary if hasattr(player, 'salary') else 1000
                    salary_oku = salary / 10000  # 万円→億円
                    
                    # 行背景
                    row_rect = pygame.Rect(payroll_rect.x + 15, y, payroll_rect.width - 30, 35)
                    if i % 2 == 0:
                        pygame.draw.rect(self.screen, (*Colors.BG_CARD[:3], 100), row_rect, border_radius=4)
                    
                    name_surf = fonts.body.render(player.name[:8], True, Colors.TEXT_PRIMARY)
                    self.screen.blit(name_surf, (row_rect.x + 10, y + 7))
                    
                    pos_surf = fonts.tiny.render(player.position.value, True, Colors.TEXT_MUTED)
                    self.screen.blit(pos_surf, (row_rect.x + 150, y + 10))
                    
                    salary_color = Colors.DANGER if salary_oku > 3 else Colors.TEXT_PRIMARY
                    salary_surf = fonts.body.render(f"{salary_oku:.2f}億円", True, salary_color)
                    self.screen.blit(salary_surf, (row_rect.x + 250, y + 7))
                    
                    y += 38
            
            # 年俸ランキング（リーグ）
            rank_card = Card(550, content_y, 250, 200, "SALARY RANK")
            rank_rect = rank_card.draw(self.screen)
            
            rank_text = fonts.h2.render("3位", True, Colors.PRIMARY)
            rank_info = fonts.small.render("セ・リーグ", True, Colors.TEXT_MUTED)
            self.screen.blit(rank_text, (rank_rect.x + 90, rank_rect.y + 80))
            self.screen.blit(rank_info, (rank_rect.x + 85, rank_rect.y + 120))
        
        elif tab == "facilities":
            # 施設タブ
            facility_card = Card(30, content_y, 750, height - content_y - 100, "FACILITIES")
            facility_rect = facility_card.draw(self.screen)
            
            y = facility_rect.y + 55
            
            facilities = [
                ("本拠地球場", "レベル5", "収容: 40,000人", "良好", 95),
                ("室内練習場", "レベル3", "バッティング・ブルペン", "普通", 70),
                ("トレーニング施設", "レベル4", "筋力・走力強化", "良好", 85),
                ("リハビリ施設", "レベル2", "怪我からの復帰支援", "普通", 60),
                ("寮", "レベル3", "若手選手向け", "普通", 75),
                ("スカウティング設備", "レベル3", "ドラフト・FAの情報収集", "普通", 70),
            ]
            
            for name, level, desc, condition, rating in facilities:
                # 施設行
                row_rect = pygame.Rect(facility_rect.x + 20, y, facility_rect.width - 40, 60)
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=8)
                
                name_surf = fonts.body.render(name, True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (row_rect.x + 15, y + 8))
                
                level_surf = fonts.small.render(level, True, Colors.PRIMARY)
                self.screen.blit(level_surf, (row_rect.x + 180, y + 10))
                
                desc_surf = fonts.tiny.render(desc, True, Colors.TEXT_MUTED)
                self.screen.blit(desc_surf, (row_rect.x + 15, y + 35))
                
                # レーティングバー
                bar_x = row_rect.x + 400
                bar_rect = pygame.Rect(bar_x, y + 20, 150, 16)
                pygame.draw.rect(self.screen, Colors.BORDER, bar_rect, border_radius=8)
                
                fill_width = int(150 * rating / 100)
                if rating >= 80:
                    fill_color = Colors.SUCCESS
                elif rating >= 50:
                    fill_color = Colors.WARNING
                else:
                    fill_color = Colors.DANGER
                fill_rect = pygame.Rect(bar_x, y + 20, fill_width, 16)
                pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=8)
                
                # 投資ボタン
                buttons[f"upgrade_{name}"] = Button(
                    row_rect.right - 100, y + 15, 80, 35,
                    "投資", "ghost", font=fonts.tiny
                )
                buttons[f"upgrade_{name}"].draw(self.screen)
                
                y += 68
        
        elif tab == "sponsors":
            # スポンサータブ
            sponsor_card = Card(30, content_y, 500, height - content_y - 100, "スポンサー契約")
            sponsor_rect = sponsor_card.draw(self.screen)
            
            y = sponsor_rect.y + 55
            
            sponsors = [
                ("メインスポンサー", "AA自動車", "10.0億円/年", 3, "契約中"),
                ("ユニフォームスポンサー", "BB銀行", "5.0億円/年", 2, "契約中"),
                ("球場看板", "CC飲料", "2.0億円/年", 1, "更新可"),
                ("公式パートナー", "DD電機", "1.5億円/年", 5, "契約中"),
            ]
            
            for name, company, amount, years, status in sponsors:
                row_rect = pygame.Rect(sponsor_rect.x + 15, y, sponsor_rect.width - 30, 55)
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=8)
                
                name_surf = fonts.body.render(name, True, Colors.TEXT_SECONDARY)
                self.screen.blit(name_surf, (row_rect.x + 10, y + 5))
                
                company_surf = fonts.body.render(company, True, Colors.TEXT_PRIMARY)
                self.screen.blit(company_surf, (row_rect.x + 10, y + 28))
                
                amount_surf = fonts.small.render(amount, True, Colors.SUCCESS)
                self.screen.blit(amount_surf, (row_rect.x + 200, y + 15))
                
                years_surf = fonts.tiny.render(f"残{years}年", True, Colors.TEXT_MUTED)
                self.screen.blit(years_surf, (row_rect.x + 320, y + 18))
                
                status_color = Colors.SUCCESS if status == "契約中" else Colors.WARNING
                status_surf = fonts.small.render(status, True, status_color)
                self.screen.blit(status_surf, (row_rect.x + 400, y + 15))
                
                y += 62
            
            # 新規スポンサー獲得
            new_card = Card(550, content_y, 250, 150, "📢 新規獲得")
            new_rect = new_card.draw(self.screen)
            
            buttons["find_sponsors"] = Button(
                new_rect.x + 40, new_rect.y + 70, 170, 45,
                "🔍 営業活動", "secondary", font=fonts.body
            )
            buttons["find_sponsors"].draw(self.screen)
        
        elif tab == "staff":
            # スタッフタブ
            staff_card = Card(30, content_y, 750, height - content_y - 100, "👔 コーチングスタッフ")
            staff_rect = staff_card.draw(self.screen)
            
            y = staff_rect.y + 55
            
            staff_list = [
                ("監督", "山田一郎", "A", "チーム士気向上"),
                ("ヘッドコーチ", "佐藤二郎", "B", "総合指導"),
                ("打撃コーチ", "鈴木三郎", "A", "打撃能力向上"),
                ("投手コーチ", "高橋四郎", "B", "投球能力向上"),
                ("守備・走塁コーチ", "田中五郎", "C", "守備・走塁向上"),
                ("バッテリーコーチ", "伊藤六郎", "B", "捕手育成"),
                ("育成コーチ", "渡辺七郎", "A", "若手成長支援"),
            ]
            
            for role, name, rank, effect in staff_list:
                row_rect = pygame.Rect(staff_rect.x + 15, y, staff_rect.width - 30, 45)
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=6)
                
                role_surf = fonts.small.render(role, True, Colors.TEXT_MUTED)
                self.screen.blit(role_surf, (row_rect.x + 10, y + 13))
                
                name_surf = fonts.body.render(name, True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (row_rect.x + 160, y + 10))
                
                # ランク
                rank_colors = {"S": Colors.WARNING, "A": Colors.SUCCESS, "B": Colors.PRIMARY, "C": Colors.TEXT_MUTED}
                rank_color = rank_colors.get(rank, Colors.TEXT_MUTED)
                rank_surf = fonts.h3.render(rank, True, rank_color)
                self.screen.blit(rank_surf, (row_rect.x + 340, y + 8))
                
                effect_surf = fonts.tiny.render(effect, True, Colors.TEXT_SECONDARY)
                self.screen.blit(effect_surf, (row_rect.x + 400, y + 15))
                
                # 変更ボタン
                buttons[f"change_staff_{role}"] = Button(
                    row_rect.right - 90, y + 5, 70, 35,
                    "変更", "ghost", font=fonts.tiny
                )
                buttons[f"change_staff_{role}"].draw(self.screen)
                
                y += 52
        
        # 戻るボタン
        buttons["back"] = Button(
            50, height - 70, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    def draw_roster_management_screen(self, player_team: 'Team', selected_tab: str = "roster",
                                       selected_player_idx: int = -1, scroll_offset: int = 0,
                                       dragging_player_idx: int = -1, drag_pos: tuple = None) -> dict:
        """選手登録管理画面（支配下・育成管理）- 改良版"""
        buttons = {}
        width, height = self.screen.get_size()
        header_h = 70
        
        # 背景
        draw_background(self.screen, "gradient")
        
        # ヘッダー
        header_rect = pygame.Rect(0, 0, width, header_h)
        pygame.draw.rect(self.screen, Colors.BG_CARD, header_rect)
        
        title_surf = fonts.h2.render("ROSTER MANAGEMENT", True, Colors.TEXT_PRIMARY)
        self.screen.blit(title_surf, (30, 20))
        
        # 登録状況サマリー
        roster_count = player_team.get_roster_count()
        dev_count = player_team.get_developmental_count()
        
        summary_text = f"支配下: {roster_count}/70  育成: {dev_count}/30"
        summary_surf = fonts.body.render(summary_text, True, Colors.TEXT_SECONDARY)
        self.screen.blit(summary_surf, (width - summary_surf.get_width() - 30, 25))
        
        # タブ
        tab_y = header_h + 8
        tabs = [
            ("order", "オーダー"),
            ("players", "選手一覧"),
            ("promote", "支配下昇格"),
            ("release", "自由契約"),
            ("foreign", "外国人補強"),
            ("trade", "トレード"),
        ]
        
        tab_x = 30
        tab_width = 110
        for tab_id, tab_name in tabs:
            is_active = tab_id == selected_tab
            btn = Button(
                tab_x, tab_y, tab_width, 36,
                tab_name, "primary" if is_active else "ghost", font=fonts.small
            )
            btn.draw(self.screen)
            buttons[f"tab_{tab_id}"] = btn
            tab_x += tab_width + 10
        
        content_y = tab_y + 48
        content_height = height - content_y - 70
        
        if selected_tab == "order":
            self._draw_order_tab(player_team, content_y, content_height, scroll_offset, selected_player_idx, buttons)
        elif selected_tab == "players":
            self._draw_players_tab(player_team, content_y, content_height, scroll_offset, selected_player_idx, buttons)
        elif selected_tab == "promote":
            self._draw_promote_tab(player_team, content_y, content_height, scroll_offset, buttons, roster_count)
        elif selected_tab == "release":
            self._draw_release_tab(player_team, content_y, content_height, scroll_offset, buttons)
        elif selected_tab == "foreign":
            self._draw_foreign_tab(player_team, content_y, content_height, scroll_offset, buttons)
        elif selected_tab == "trade":
            self._draw_trade_tab(player_team, content_y, content_height, scroll_offset, buttons)
        
        # ドラッグ中の選手表示
        if dragging_player_idx >= 0 and drag_pos and dragging_player_idx < len(player_team.players):
            player = player_team.players[dragging_player_idx]
            drag_rect = pygame.Rect(drag_pos[0] - 50, drag_pos[1] - 15, 100, 30)
            pygame.draw.rect(self.screen, Colors.PRIMARY, drag_rect, border_radius=6)
            drag_surf = fonts.small.render(player.name[:6], True, Colors.TEXT_PRIMARY)
            self.screen.blit(drag_surf, (drag_pos[0] - 40, drag_pos[1] - 8))
        
        # 戻るボタン
        buttons["back"] = Button(
            30, height - 60, 130, 45,
            "戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    def _draw_roster_tab(self, player_team, content_y, content_height, scroll_offset, selected_player_idx, buttons):
        """支配下選手タブを描画（改良版：コンパクトで一覧性向上）"""
        width = self.screen.get_width()
        
        # 選手を投手/野手で分類
        pitchers = [(i, p) for i, p in enumerate(player_team.players) 
                   if not p.is_developmental and p.position.value == "投手"]
        batters = [(i, p) for i, p in enumerate(player_team.players) 
                  if not p.is_developmental and p.position.value != "投手"]
        
        # 左パネル: 投手一覧
        left_width = (width - 80) // 2
        left_card = Card(30, content_y, left_width, content_height, f"投手 ({len(pitchers)}人)")
        left_rect = left_card.draw(self.screen)
        
        # 右パネル: 野手一覧
        right_card = Card(50 + left_width, content_y, left_width, content_height, f"野手 ({len(batters)}人)")
        right_rect = right_card.draw(self.screen)
        
        row_height = 32
        header_height = 22
        
        # 投手リスト
        self._draw_player_list_compact(
            left_rect, pitchers, scroll_offset, selected_player_idx, 
            row_height, header_height, buttons, "pitcher",
            ["#", "名前", "タイプ", "球速", "制球", "スタミナ"]
        )
        
        # 野手リスト
        self._draw_player_list_compact(
            right_rect, batters, scroll_offset, selected_player_idx,
            row_height, header_height, buttons, "batter",
            ["#", "名前", "守備", "ミート", "パワー", "走力"]
        )
    
    def _draw_player_list_compact(self, card_rect, players, scroll_offset, selected_idx, 
                                   row_height, header_height, buttons, player_type, headers):
        """コンパクトな選手リストを描画"""
        y = card_rect.y + 45
        max_visible = (card_rect.height - 60) // row_height
        
        # ヘッダー
        col_widths = [35, 75, 55, 45, 45, 45] if player_type == "pitcher" else [35, 75, 55, 45, 45, 45]
        x = card_rect.x + 10
        for i, hdr in enumerate(headers):
            hdr_surf = fonts.tiny.render(hdr, True, Colors.TEXT_MUTED)
            self.screen.blit(hdr_surf, (x, y))
            x += col_widths[i]
        y += header_height
        
        # 選手行
        for i in range(scroll_offset, min(scroll_offset + max_visible, len(players))):
            idx, player = players[i]
            row_rect = pygame.Rect(card_rect.x + 5, y, card_rect.width - 25, row_height - 2)
            
            is_selected = idx == selected_idx
            bg_color = (*Colors.PRIMARY[:3], 60) if is_selected else Colors.BG_INPUT
            pygame.draw.rect(self.screen, bg_color, row_rect, border_radius=3)
            
            x = card_rect.x + 10
            
            # 背番号
            num_surf = fonts.tiny.render(str(player.uniform_number), True, Colors.TEXT_PRIMARY)
            self.screen.blit(num_surf, (x, y + 7))
            x += col_widths[0]
            
            # 名前
            name_surf = fonts.tiny.render(player.name[:5], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (x, y + 7))
            x += col_widths[1]
            
            if player_type == "pitcher":
                # タイプ
                type_text = player.pitch_type.value[:2] if player.pitch_type else "-"
                type_surf = fonts.tiny.render(type_text, True, Colors.TEXT_SECONDARY)
                self.screen.blit(type_surf, (x, y + 7))
                x += col_widths[2]
                
                # 球速
                speed_color = self._get_stat_color(player.stats.speed)
                speed_surf = fonts.tiny.render(str(player.stats.speed), True, speed_color)
                self.screen.blit(speed_surf, (x, y + 7))
                x += col_widths[3]
                
                # 制球
                ctrl_color = self._get_stat_color(player.stats.control)
                ctrl_surf = fonts.tiny.render(str(player.stats.control), True, ctrl_color)
                self.screen.blit(ctrl_surf, (x, y + 7))
                x += col_widths[4]
                
                # スタミナ
                stam_color = self._get_stat_color(player.stats.stamina)
                stam_surf = fonts.tiny.render(str(player.stats.stamina), True, stam_color)
                self.screen.blit(stam_surf, (x, y + 7))
            else:
                # 守備
                pos_text = player.position.value[:2]
                pos_surf = fonts.tiny.render(pos_text, True, Colors.TEXT_SECONDARY)
                self.screen.blit(pos_surf, (x, y + 7))
                x += col_widths[2]
                
                # ミート
                contact_color = self._get_stat_color(player.stats.contact)
                contact_surf = fonts.tiny.render(str(player.stats.contact), True, contact_color)
                self.screen.blit(contact_surf, (x, y + 7))
                x += col_widths[3]
                
                # パワー
                power_color = self._get_stat_color(player.stats.power)
                power_surf = fonts.tiny.render(str(player.stats.power), True, power_color)
                self.screen.blit(power_surf, (x, y + 7))
                x += col_widths[4]
                
                # 走力
                run_color = self._get_stat_color(player.stats.run)
                run_surf = fonts.tiny.render(str(player.stats.run), True, run_color)
                self.screen.blit(run_surf, (x, y + 7))
            
            # 詳細ボタン
            detail_btn = Button(row_rect.right - 40, y + 3, 35, row_height - 8, "詳", "outline", font=fonts.tiny)
            detail_btn.draw(self.screen)
            buttons[f"roster_detail_{idx}"] = detail_btn
            
            buttons[f"player_{idx}"] = row_rect
            y += row_height
        
        # スクロールバー
        if len(players) > max_visible:
            self._draw_scrollbar(card_rect, scroll_offset, len(players), max_visible)
    
    def _get_stat_color(self, value):
        """能力値に応じた色を返す"""
        if value >= 80:
            return Colors.WARNING  # 金
        elif value >= 70:
            return Colors.SUCCESS  # 緑
        elif value >= 50:
            return Colors.TEXT_PRIMARY  # 白
        else:
            return Colors.TEXT_MUTED  # グレー
    
    def _draw_scrollbar(self, card_rect, scroll_offset, total_items, visible_items):
        """スクロールバーを描画"""
        scroll_track_h = card_rect.height - 60
        scroll_h = max(20, int(scroll_track_h * visible_items / total_items))
        max_scroll = total_items - visible_items
        scroll_y = card_rect.y + 45 + int((scroll_offset / max(1, max_scroll)) * (scroll_track_h - scroll_h))
        pygame.draw.rect(self.screen, Colors.BG_INPUT, 
                        (card_rect.right - 12, card_rect.y + 45, 6, scroll_track_h), border_radius=3)
        pygame.draw.rect(self.screen, Colors.PRIMARY, 
                        (card_rect.right - 12, scroll_y, 6, scroll_h), border_radius=3)

    def _draw_developmental_tab(self, player_team, content_y, content_height, scroll_offset, selected_player_idx, buttons):
        """育成選手タブを描画"""
        width = self.screen.get_width()
        
        card = Card(30, content_y, width - 60, content_height, "育成選手一覧")
        card_rect = card.draw(self.screen)
        
        dev_players = [(i, p) for i, p in enumerate(player_team.players) if p.is_developmental]
        
        row_height = 32
        y = card_rect.y + 45
        max_visible = (card_rect.height - 60) // row_height
        
        # ヘッダー
        headers = ["#", "名前", "位置", "年齢", "Pot", "能力"]
        col_widths = [35, 65, 50, 40, 60, 120]
        hx = card_rect.x + 15
        for i, hdr in enumerate(headers):
            hdr_surf = fonts.tiny.render(hdr, True, Colors.TEXT_MUTED)
            self.screen.blit(hdr_surf, (hx, y))
            hx += col_widths[i]
        y += 22
        
        for i in range(scroll_offset, min(scroll_offset + max_visible, len(dev_players))):
            idx, player = dev_players[i]
            row_rect = pygame.Rect(card_rect.x + 10, y, card_rect.width - 60, row_height - 2)
            
            is_selected = idx == selected_player_idx
            bg_color = (*Colors.PRIMARY[:3], 60) if is_selected else Colors.BG_INPUT
            pygame.draw.rect(self.screen, bg_color, row_rect, border_radius=4)
            
            x = card_rect.x + 15
            
            # 背番号
            num_surf = fonts.tiny.render(str(player.uniform_number), True, Colors.TEXT_PRIMARY)
            self.screen.blit(num_surf, (x, y + 7))
            x += col_widths[0]
            
            # 名前
            name_surf = fonts.tiny.render(player.name[:5], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (x, y + 7))
            x += col_widths[1]
            
            # ポジション
            pos_text = player.position.value[:2]
            pos_surf = fonts.tiny.render(pos_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (x, y + 7))
            x += col_widths[2]
            
            # 年齢
            age_surf = fonts.tiny.render(f"{player.age}", True, Colors.TEXT_SECONDARY)
            self.screen.blit(age_surf, (x, y + 7))
            x += col_widths[3]
            
            # ポテンシャル
            if hasattr(player, 'growth') and player.growth:
                pot = player.growth.potential
                pot_color = Colors.WARNING if pot >= 7 else Colors.SUCCESS if pot >= 5 else Colors.TEXT_MUTED
                pot_surf = fonts.tiny.render("★" * min(pot, 5), True, pot_color)
                self.screen.blit(pot_surf, (x, y + 7))
            x += col_widths[4]
            
            # 主要能力
            if player.position.value == "投手":
                stat_text = f"球{player.stats.speed} 制{player.stats.control}"
            else:
                stat_text = f"ミ{player.stats.contact} パ{player.stats.power}"
            stat_surf = fonts.tiny.render(stat_text, True, Colors.TEXT_MUTED)
            self.screen.blit(stat_surf, (x, y + 7))
            
            # 詳細ボタン
            detail_btn = Button(row_rect.right - 40, y + 3, 35, row_height - 8, "詳", "outline", font=fonts.tiny)
            detail_btn.draw(self.screen)
            buttons[f"roster_detail_{idx}"] = detail_btn
            
            buttons[f"player_{idx}"] = row_rect
            y += row_height
        
        # スクロールバー
        if len(dev_players) > max_visible:
            self._draw_scrollbar(card_rect, scroll_offset, len(dev_players), max_visible)

    def _draw_promote_tab(self, player_team, content_y, content_height, scroll_offset, buttons, roster_count):
        """支配下昇格タブを描画"""
        width = self.screen.get_width()
        
        card = Card(30, content_y, width - 60, content_height, "育成 → 支配下 昇格")
        card_rect = card.draw(self.screen)
        
        # 説明と枠状況
        can_promote = player_team.can_add_roster_player()
        status_color = Colors.SUCCESS if can_promote else Colors.DANGER
        
        desc_surf = fonts.small.render("育成選手を支配下登録に昇格させます", True, Colors.TEXT_SECONDARY)
        self.screen.blit(desc_surf, (card_rect.x + 20, card_rect.y + 45))
        
        status_text = f"支配下枠: {roster_count}/70 {'(空きあり)' if can_promote else '(満員)'}"
        status_surf = fonts.body.render(status_text, True, status_color)
        self.screen.blit(status_surf, (card_rect.x + 20, card_rect.y + 70))
        
        dev_players = [(i, p) for i, p in enumerate(player_team.players) if p.is_developmental]
        
        row_height = 60  # 少し高くして詳細ボタンを収める
        y = card_rect.y + 110
        max_visible = (card_rect.height - 130) // row_height
        
        for i in range(scroll_offset, min(scroll_offset + max_visible, len(dev_players))):
            idx, player = dev_players[i]
            row_rect = pygame.Rect(card_rect.x + 15, y, card_rect.width - 180, row_height - 5)
            pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=6)
            
            # 選手情報（詳細表示）
            info_line1 = f"#{player.uniform_number} {player.name} ({player.position.value}) {player.age}歳"
            info_surf1 = fonts.small.render(info_line1, True, Colors.TEXT_PRIMARY)
            self.screen.blit(info_surf1, (row_rect.x + 15, y + 6))
            
            # 能力値
            if player.position.value == "投手":
                stat_text = f"球速:{player.stats.speed} 制球:{player.stats.control} スタミナ:{player.stats.stamina}"
            else:
                stat_text = f"ミート:{player.stats.contact} パワー:{player.stats.power} 走力:{player.stats.run}"
            
            # ポテンシャル
            pot_text = ""
            if hasattr(player, 'growth') and player.growth:
                pot_text = f"  ★{'★' * min(player.growth.potential - 1, 4)}"
            
            info_surf2 = fonts.tiny.render(stat_text + pot_text, True, Colors.TEXT_MUTED)
            self.screen.blit(info_surf2, (row_rect.x + 15, y + 28))
            
            # 詳細ボタン（能力詳細を見るため）
            detail_btn = Button(row_rect.x + row_rect.width - 50, y + 35, 45, 20, "詳細", "outline", font=fonts.tiny)
            detail_btn.draw(self.screen)
            buttons[f"roster_detail_{idx}"] = detail_btn
            
            # 昇格ボタン
            if can_promote:
                promote_btn = Button(row_rect.right + 15, y + 8, 100, 34, "昇格", "primary", font=fonts.small)
                promote_btn.draw(self.screen)
                buttons[f"promote_{idx}"] = promote_btn
            else:
                # 枠なしの場合はグレーアウト
                disabled_surf = fonts.small.render("枠なし", True, Colors.TEXT_MUTED)
                self.screen.blit(disabled_surf, (row_rect.right + 35, y + 15))
            
            y += row_height
        
        # スクロールバー
        if len(dev_players) > max_visible:
            self._draw_scrollbar(card_rect, scroll_offset, len(dev_players), max_visible)

    def _draw_order_tab(self, player_team, content_y, content_height, scroll_offset, selected_player_idx, buttons):
        """オーダー編成タブを描画（自由な打順・守備位置設定）"""
        width = self.screen.get_width()
        from settings_manager import settings
        from models import Position
        
        # ドロップゾーン情報を初期化
        drop_zones = {}
        
        # DH制の判定
        is_pacific = hasattr(player_team, 'league') and player_team.league.value == "パシフィック"
        use_dh = (is_pacific and settings.game_rules.pacific_dh) or (not is_pacific and settings.game_rules.central_dh)
        
        # ========================================
        # 左パネル: スタメン（打順と守備位置を自由に設定）
        # ========================================
        left_width = 430
        order_card = Card(30, content_y + 5, left_width, content_height - 70, "スタメン")
        order_rect = order_card.draw(self.screen)
        
        row_height = 34
        header_y = order_rect.y + 44
        y = header_y + 20
        
        # ヘッダー行（守備位置入れ替えボタン用に幅調整）
        headers = [("打順", 40), ("守備", 70), ("選手", 130), ("適性", 95), ("入替", 50)]
        hx = order_rect.x + 8
        for hdr, w in headers:
            hdr_surf = fonts.tiny.render(hdr, True, Colors.TEXT_MUTED)
            self.screen.blit(hdr_surf, (hx, header_y))
            hx += w
        
        # 守備位置選択肢（DH対応）
        all_positions = ["捕", "一", "二", "三", "遊", "左", "中", "右"]
        if use_dh:
            all_positions.append("DH")
        
        # lineup_positionsがない場合は初期化（打順に対するポジションを保持）
        if not hasattr(player_team, 'lineup_positions') or player_team.lineup_positions is None:
            player_team.lineup_positions = ["捕", "一", "二", "三", "遊", "左", "中", "右", "DH" if use_dh else "投"]
        
        for i in range(9):
            # 行の背景
            row_rect = pygame.Rect(order_rect.x + 6, y, left_width - 16, row_height - 2)
            
            # ドロップゾーンとして登録
            drop_zones[f"order_{i}"] = row_rect
            
            # 選手がいる場合の処理
            if i < len(player_team.current_lineup) and player_team.current_lineup[i] is not None:
                player_idx = player_team.current_lineup[i]
                if 0 <= player_idx < len(player_team.players):
                    player = player_team.players[player_idx]
                    
                    # 行の背景
                    pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=4)
                    
                    x = order_rect.x + 10
                    
                    # 打順番号（円形バッジ）
                    pygame.draw.circle(self.screen, Colors.PRIMARY, (x + 12, y + row_height // 2), 12)
                    num_surf = fonts.small.render(str(i + 1), True, Colors.TEXT_PRIMARY)
                    num_rect = num_surf.get_rect(center=(x + 12, y + row_height // 2))
                    self.screen.blit(num_surf, num_rect)
                    x += 40
                    
                    # 守備位置（クリックで変更可能なボタン）
                    current_pos = player_team.lineup_positions[i] if i < len(player_team.lineup_positions) else "DH"
                    pos_btn_rect = pygame.Rect(x, y + 3, 45, row_height - 8)
                    pos_hovered = pos_btn_rect.collidepoint(pygame.mouse.get_pos())
                    pos_bg = Colors.BG_HOVER if pos_hovered else Colors.BG_CARD
                    pygame.draw.rect(self.screen, pos_bg, pos_btn_rect, border_radius=4)
                    
                    is_dh = current_pos == "DH"
                    pos_border_color = Colors.WARNING if is_dh else Colors.SUCCESS
                    pygame.draw.rect(self.screen, pos_border_color, pos_btn_rect, 1, border_radius=4)
                    
                    pos_color = Colors.WARNING if is_dh else Colors.SUCCESS
                    pos_surf = fonts.small.render(current_pos, True, pos_color)
                    pos_rect = pos_surf.get_rect(center=pos_btn_rect.center)
                    self.screen.blit(pos_surf, pos_rect)
                    
                    # ポジション変更ボタンとして登録
                    pos_btn = Button(pos_btn_rect.x, pos_btn_rect.y, pos_btn_rect.width, pos_btn_rect.height, "", "ghost")
                    buttons[f"change_pos_{i}"] = pos_btn
                    
                    # ポジション入替ボタン（守備位置のみ入れ替え）
                    if i > 0:
                        pos_up_btn = Button(x + 47, y + 2, 18, 14, "^", "outline", font=fonts.tiny)
                        pos_up_btn.draw(self.screen)
                        buttons[f"pos_swap_up_{i}"] = pos_up_btn
                    if i < 8:
                        pos_down_btn = Button(x + 47, y + 17, 18, 14, "v", "outline", font=fonts.tiny)
                        pos_down_btn.draw(self.screen)
                        buttons[f"pos_swap_down_{i}"] = pos_down_btn
                    x += 70
                    
                    # 選手名（背番号付き）
                    name_text = f"#{player.uniform_number} {player.name}"
                    name_surf = fonts.small.render(name_text[:9], True, Colors.TEXT_PRIMARY)
                    self.screen.blit(name_surf, (x, y + 7))
                    x += 130
                    
                    # 守備適性表示
                    main_pos = player.position.value[:1] if player.position.value != "外野手" else "外"
                    sub_positions = getattr(player, 'sub_positions', []) or []
                    
                    apt_text = f"◎{main_pos}"
                    for sp in sub_positions[:1]:
                        sp_str = sp.value if hasattr(sp, 'value') else str(sp)
                        sp_short = sp_str[:1] if sp_str != "外野手" else "外"
                        apt_text += f" ○{sp_short}"
                    
                    apt_surf = fonts.tiny.render(apt_text, True, Colors.TEXT_MUTED)
                    self.screen.blit(apt_surf, (x, y + 9))
                    x += 95
                    
                    # 入替ボタン（上下）- UPとDNで表示
                    if i > 0:
                        up_btn = Button(x, y + 2, 22, 14, "^", "ghost", font=fonts.tiny)
                        up_btn.draw(self.screen)
                        buttons[f"swap_up_{i}"] = up_btn
                    if i < 8:
                        down_btn = Button(x, y + 17, 22, 14, "v", "ghost", font=fonts.tiny)
                        down_btn.draw(self.screen)
                        buttons[f"swap_down_{i}"] = down_btn
                    x += 25
                    
                    # 削除ボタン
                    remove_btn = Button(x, y + 5, 22, row_height - 12, "X", "danger", font=fonts.tiny)
                    remove_btn.draw(self.screen)
                    buttons[f"remove_lineup_{i}"] = remove_btn
                    
                    # 行全体をドラッグ可能なボタンとして登録
                    slot_btn = Button(row_rect.x, row_rect.y, row_rect.width - 50, row_rect.height, "", "ghost")
                    slot_btn.rect = pygame.Rect(row_rect.x, row_rect.y, row_rect.width - 50, row_rect.height)
                    buttons[f"lineup_slot_{i}"] = slot_btn
            else:
                # 空きスロット
                pygame.draw.rect(self.screen, Colors.BG_CARD, row_rect, border_radius=4)
                pygame.draw.rect(self.screen, Colors.BORDER, row_rect, 1, border_radius=4)
                
                x = order_rect.x + 10
                # 打順番号
                pygame.draw.circle(self.screen, Colors.BG_INPUT, (x + 12, y + row_height // 2), 12)
                pygame.draw.circle(self.screen, Colors.BORDER, (x + 12, y + row_height // 2), 12, 1)
                num_surf = fonts.small.render(str(i + 1), True, Colors.TEXT_MUTED)
                num_rect = num_surf.get_rect(center=(x + 12, y + row_height // 2))
                self.screen.blit(num_surf, num_rect)
                
                # 守備位置を選べるボタン
                x += 40
                current_pos = player_team.lineup_positions[i] if i < len(player_team.lineup_positions) else "?"
                pos_btn_rect = pygame.Rect(x, y + 3, 45, row_height - 8)
                pos_hovered = pos_btn_rect.collidepoint(pygame.mouse.get_pos())
                pos_bg = Colors.BG_HOVER if pos_hovered else Colors.BG_INPUT
                pygame.draw.rect(self.screen, pos_bg, pos_btn_rect, border_radius=4)
                pygame.draw.rect(self.screen, Colors.BORDER, pos_btn_rect, 1, border_radius=4)
                pos_surf = fonts.small.render(current_pos, True, Colors.TEXT_MUTED)
                pos_rect = pos_surf.get_rect(center=pos_btn_rect.center)
                self.screen.blit(pos_surf, pos_rect)
                
                pos_btn = Button(pos_btn_rect.x, pos_btn_rect.y, pos_btn_rect.width, pos_btn_rect.height, "", "ghost")
                buttons[f"change_pos_{i}"] = pos_btn
                
                # 空き表示
                empty_surf = fonts.small.render("-- 選手を選択 --", True, Colors.TEXT_MUTED)
                self.screen.blit(empty_surf, (x + 55, y + 7))
            
            y += row_height
        
        # 先発投手セクション
        y += 6
        pygame.draw.line(self.screen, Colors.BORDER, (order_rect.x + 8, y), (order_rect.x + left_width - 20, y), 1)
        y += 6
        
        sp_row = pygame.Rect(order_rect.x + 6, y, left_width - 16, row_height)
        pygame.draw.rect(self.screen, Colors.BG_INPUT, sp_row, border_radius=4)
        
        sp_label = fonts.body.render("先発", True, Colors.INFO)
        self.screen.blit(sp_label, (order_rect.x + 18, y + 7))
        
        if player_team.starting_pitcher_idx >= 0 and player_team.starting_pitcher_idx < len(player_team.players):
            sp = player_team.players[player_team.starting_pitcher_idx]
            sp_text = f"#{sp.uniform_number} {sp.name}"
            sp_surf = fonts.small.render(sp_text, True, Colors.TEXT_PRIMARY)
            self.screen.blit(sp_surf, (order_rect.x + 68, y + 7))
            
            # 投手能力
            sp_stat = f"球速{sp.stats.speed} 制球{sp.stats.control}"
            sp_stat_surf = fonts.tiny.render(sp_stat, True, Colors.TEXT_MUTED)
            self.screen.blit(sp_stat_surf, (order_rect.x + 220, y + 9))
        else:
            no_sp = fonts.small.render("-- 未設定 --", True, Colors.TEXT_MUTED)
            self.screen.blit(no_sp, (order_rect.x + 68, y + 7))
        
        # ========================================
        # 右パネル: 選手一覧（野手のみ・クリックで追加）
        # ========================================
        right_x = 30 + left_width + 15
        right_width = width - right_x - 30
        right_card = Card(right_x, content_y, right_width, content_height - 60, "野手一覧（クリックで追加）")
        right_rect = right_card.draw(self.screen)
        
        # 現在のラインアップに含まれない野手
        lineup_set = set(player_team.current_lineup) if player_team.current_lineup else set()
        available_batters = [(i, p) for i, p in enumerate(player_team.players) 
                            if not p.is_developmental and p.position != Position.PITCHER and i not in lineup_set]
        
        # ヘッダー
        row_height = 34
        list_y = right_rect.y + 45
        hdr_x = right_rect.x + 10
        for hdr, w in [("守備", 45), ("選手名", 115), ("ミ", 35), ("パ", 35), ("走", 35), ("適性", 80)]:
            hdr_surf = fonts.tiny.render(hdr, True, Colors.TEXT_MUTED)
            self.screen.blit(hdr_surf, (hdr_x, list_y))
            hdr_x += w
        list_y += 20
        
        max_visible = (right_rect.height - 80) // row_height
        
        for i in range(scroll_offset, min(scroll_offset + max_visible, len(available_batters))):
            idx, player = available_batters[i]
            row_rect = pygame.Rect(right_rect.x + 8, list_y, right_rect.width - 20, row_height - 2)
            
            is_hovered = row_rect.collidepoint(pygame.mouse.get_pos())
            bg_color = Colors.BG_HOVER if is_hovered else Colors.BG_INPUT
            pygame.draw.rect(self.screen, bg_color, row_rect, border_radius=4)
            
            x = right_rect.x + 12
            
            # 守備
            pos_text = player.position.value[:2] if player.position.value != "外野手" else "外"
            pos_surf = fonts.small.render(pos_text, True, Colors.SUCCESS)
            self.screen.blit(pos_surf, (x, list_y + 7))
            x += 45
            
            # 選手名
            name_text = f"#{player.uniform_number} {player.name}"
            name_surf = fonts.small.render(name_text[:8], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (x, list_y + 7))
            x += 115
            
            # ミート
            contact_color = self._get_stat_color(player.stats.contact)
            contact_surf = fonts.tiny.render(str(player.stats.contact), True, contact_color)
            self.screen.blit(contact_surf, (x + 5, list_y + 9))
            x += 35
            
            # パワー
            power_color = self._get_stat_color(player.stats.power)
            power_surf = fonts.tiny.render(str(player.stats.power), True, power_color)
            self.screen.blit(power_surf, (x + 5, list_y + 9))
            x += 35
            
            # 走力
            run_color = self._get_stat_color(player.stats.run)
            run_surf = fonts.tiny.render(str(player.stats.run), True, run_color)
            self.screen.blit(run_surf, (x + 5, list_y + 9))
            x += 35
            
            # 守備適性
            main_pos = player.position.value[:1] if player.position.value != "外野手" else "外"
            apt_text = f"◎{main_pos}"
            if hasattr(player, 'sub_positions') and player.sub_positions:
                for sp in player.sub_positions[:1]:
                    # Positionオブジェクトの場合は.valueを取得
                    sp_str = sp.value if hasattr(sp, 'value') else str(sp)
                    sp_short = sp_str[:1] if sp_str != "外野手" else "外"
                    apt_text += f" ○{sp_short}"
            apt_surf = fonts.tiny.render(apt_text, True, Colors.TEXT_MUTED)
            self.screen.blit(apt_surf, (x, list_y + 9))
            
            # クリック可能エリア
            btn = Button(row_rect.x, row_rect.y, row_rect.width, row_rect.height, "", "ghost")
            btn.is_hovered = is_hovered
            buttons[f"add_lineup_{idx}"] = btn
            
            list_y += row_height
        
        # スクロールバー
        if len(available_batters) > max_visible:
            self._draw_scrollbar(right_rect, scroll_offset, len(available_batters), max_visible)
        
        # 下部ボタン
        btn_y = content_y + content_height - 50
        auto_btn = Button(30, btn_y, 150, 42, "自動編成", "primary", font=fonts.body)
        auto_btn.draw(self.screen)
        buttons["auto_lineup"] = auto_btn
        
        clear_btn = Button(195, btn_y, 130, 42, "クリア", "danger", font=fonts.body)
        clear_btn.draw(self.screen)
        buttons["clear_lineup"] = clear_btn
        
        # ドロップゾーン情報をボタンに追加
        buttons["_drop_zones"] = drop_zones

    def _draw_release_tab(self, player_team, content_y, content_height, scroll_offset, buttons):
        """自由契約タブを描画"""
        width = self.screen.get_width()
        
        card = Card(30, content_y, width - 60, content_height, "自由契約（選手解雇）")
        card_rect = card.draw(self.screen)
        
        desc_surf = fonts.small.render("選手を自由契約にして登録枠を空けます。解雇した選手は戻ってきません。", True, Colors.TEXT_SECONDARY)
        self.screen.blit(desc_surf, (card_rect.x + 20, card_rect.y + 45))
        
        # 支配下選手のみ
        players = [(i, p) for i, p in enumerate(player_team.players) if not p.is_developmental]
        
        row_height = 36
        y = card_rect.y + 80
        max_visible = (card_rect.height - 100) // row_height
        
        for i in range(scroll_offset, min(scroll_offset + max_visible, len(players))):
            idx, player = players[i]
            row_rect = pygame.Rect(card_rect.x + 15, y, card_rect.width - 150, row_height - 4)
            pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=4)
            
            info_text = f"#{player.uniform_number} {player.name} ({player.position.value}) {player.age}歳"
            info_surf = fonts.small.render(info_text, True, Colors.TEXT_PRIMARY)
            self.screen.blit(info_surf, (row_rect.x + 10, y + 8))
            
            # 年俸
            if player.salary >= 100000000:
                salary_text = f"{player.salary // 100000000}億"
            else:
                salary_text = f"{player.salary // 10000}万"
            salary_surf = fonts.tiny.render(salary_text, True, Colors.WARNING)
            self.screen.blit(salary_surf, (row_rect.right - 80, y + 10))
            
            # 解雇ボタン
            release_btn = Button(row_rect.right + 15, y + 2, 80, 28, "解雇", "danger", font=fonts.small)
            release_btn.draw(self.screen)
            buttons[f"release_{idx}"] = release_btn
            
            y += row_height
        
        if len(players) > max_visible:
            self._draw_scrollbar(card_rect, scroll_offset, len(players), max_visible)

    def _draw_foreign_tab(self, player_team, content_y, content_height, scroll_offset, buttons):
        """新外国人補強タブを描画"""
        width = self.screen.get_width()
        
        card = Card(30, content_y, width - 60, content_height, "外国人選手補強")
        card_rect = card.draw(self.screen)
        
        desc_surf = fonts.small.render("外国人選手を獲得します。外国人枠は5名までです。", True, Colors.TEXT_SECONDARY)
        self.screen.blit(desc_surf, (card_rect.x + 20, card_rect.y + 45))
        
        # 現在の外国人数を計算
        foreign_count = sum(1 for p in player_team.players if hasattr(p, 'is_foreign') and p.is_foreign)
        status_text = f"現在の外国人選手: {foreign_count}/5"
        status_color = Colors.SUCCESS if foreign_count < 5 else Colors.DANGER
        status_surf = fonts.body.render(status_text, True, status_color)
        self.screen.blit(status_surf, (card_rect.x + 20, card_rect.y + 70))
        
        # 外国人FA市場へのリンク
        fa_btn = Button(card_rect.x + 20, card_rect.y + 110, 200, 45, "外国人FA市場を開く", "primary", font=fonts.body)
        fa_btn.draw(self.screen)
        buttons["open_foreign_fa"] = fa_btn
        
        info_text = "※ 外国人FA市場では世界各国のフリーエージェント選手と契約できます"
        info_surf = fonts.tiny.render(info_text, True, Colors.TEXT_MUTED)
        self.screen.blit(info_surf, (card_rect.x + 20, card_rect.y + 170))

    def _draw_trade_tab(self, player_team, content_y, content_height, scroll_offset, buttons):
        """トレードタブを描画"""
        width = self.screen.get_width()
        
        card = Card(30, content_y, width - 60, content_height, "トレード")
        card_rect = card.draw(self.screen)
        
        desc_surf = fonts.small.render("他球団と選手をトレードします。", True, Colors.TEXT_SECONDARY)
        self.screen.blit(desc_surf, (card_rect.x + 20, card_rect.y + 45))
        
        # トレード市場へのリンク
        trade_btn = Button(card_rect.x + 20, card_rect.y + 90, 200, 45, "トレード市場を開く", "primary", font=fonts.body)
        trade_btn.draw(self.screen)
        buttons["open_trade_market"] = trade_btn
        
        info_text = "※ トレードでは他球団の選手と交換できます。金銭トレードも可能です。"
        info_surf = fonts.tiny.render(info_text, True, Colors.TEXT_MUTED)
        self.screen.blit(info_surf, (card_rect.x + 20, card_rect.y + 150))

    def _draw_players_tab(self, player_team, content_y, content_height, scroll_offset, selected_player_idx, buttons):
        """選手一覧タブを描画"""
        width = self.screen.get_width()
        from models import Position
        
        # 投手/野手のフィルタボタン
        filter_y = content_y
        pitcher_btn = Button(30, filter_y, 100, 32, "投手", "outline", font=fonts.small)
        pitcher_btn.draw(self.screen)
        buttons["filter_pitcher"] = pitcher_btn
        
        batter_btn = Button(140, filter_y, 100, 32, "野手", "outline", font=fonts.small)
        batter_btn.draw(self.screen)
        buttons["filter_batter"] = batter_btn
        
        all_btn = Button(250, filter_y, 100, 32, "全員", "primary", font=fonts.small)
        all_btn.draw(self.screen)
        buttons["filter_all"] = all_btn
        
        # 選手リスト
        list_y = filter_y + 45
        list_height = content_height - 55
        
        card = Card(30, list_y, width - 60, list_height, "選手一覧")
        card_rect = card.draw(self.screen)
        
        # 全選手（支配下・育成含む）
        all_players = [(i, p) for i, p in enumerate(player_team.players)]
        
        row_height = 34
        y = card_rect.y + 45
        max_visible = (card_rect.height - 60) // row_height
        
        # ヘッダー
        headers = ["#", "名前", "ポジ", "年齢", "契約", "能力"]
        header_x = [15, 50, 200, 280, 330, 400]
        for h, hx in zip(headers, header_x):
            h_surf = fonts.tiny.render(h, True, Colors.TEXT_MUTED)
            self.screen.blit(h_surf, (card_rect.x + hx, card_rect.y + 45))
        
        y += 25
        
        for i in range(scroll_offset, min(scroll_offset + max_visible, len(all_players))):
            idx, player = all_players[i]
            row_rect = pygame.Rect(card_rect.x + 10, y, card_rect.width - 20, row_height - 4)
            
            is_selected = idx == selected_player_idx
            is_hovered = row_rect.collidepoint(pygame.mouse.get_pos())
            
            if is_selected:
                bg_color = lerp_color(Colors.BG_CARD, Colors.PRIMARY, 0.3)
            elif is_hovered:
                bg_color = Colors.BG_HOVER
            else:
                bg_color = Colors.BG_INPUT if i % 2 == 0 else Colors.BG_CARD
            
            pygame.draw.rect(self.screen, bg_color, row_rect, border_radius=4)
            
            # 背番号
            num_surf = fonts.small.render(str(player.uniform_number), True, Colors.TEXT_SECONDARY)
            self.screen.blit(num_surf, (card_rect.x + 20, y + 7))
            
            # 名前
            name_color = Colors.WARNING if player.is_developmental else Colors.TEXT_PRIMARY
            name_surf = fonts.small.render(player.name[:8], True, name_color)
            self.screen.blit(name_surf, (card_rect.x + 55, y + 7))
            
            # ポジション
            pos_surf = fonts.small.render(player.position.value[:3], True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (card_rect.x + 205, y + 7))
            
            # 年齢
            age_surf = fonts.small.render(str(player.age), True, Colors.TEXT_SECONDARY)
            self.screen.blit(age_surf, (card_rect.x + 285, y + 7))
            
            # 契約
            contract_text = "育成" if player.is_developmental else "支配下"
            contract_surf = fonts.tiny.render(contract_text, True, Colors.WARNING if player.is_developmental else Colors.SUCCESS)
            self.screen.blit(contract_surf, (card_rect.x + 335, y + 9))
            
            # 総合能力
            overall = player.stats.overall_pitching() if player.position == Position.PITCHER else player.stats.overall_batting()
            rank = player.stats.get_rank(overall)
            rank_color = player.stats.get_rank_color(overall)
            overall_surf = fonts.small.render(f"{rank} ({overall})", True, rank_color)
            self.screen.blit(overall_surf, (card_rect.x + 405, y + 7))
            
            # 詳細ボタン
            detail_btn = Button(row_rect.right - 55, y + 3, 50, 26, "詳細", "outline", font=fonts.tiny)
            detail_btn.draw(self.screen)
            buttons[f"player_detail_{idx}"] = detail_btn
            
            y += row_height
        
        if len(all_players) > max_visible:
            self._draw_scrollbar(card_rect, scroll_offset, len(all_players), max_visible)

    # ========================================
    # 選手詳細画面（パワプロ風）
    # ========================================
    def draw_player_detail_screen(self, player, scroll_offset: int = 0, team_color=None) -> Dict[str, Button]:
        """選手詳細画面を描画（パワプロ風能力表示・強化版）"""
        from models import Position
        
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        if team_color is None:
            team_color = Colors.PRIMARY
        
        # ヘッダー（選手情報をコンパクトに）
        pos_text = player.position.value
        if player.pitch_type:
            pos_text += f" ({player.pitch_type.value})"
        
        # カスタムヘッダー（より詳細な情報付き）
        header_h = 100
        pygame.draw.rect(self.screen, Colors.BG_CARD, (0, 0, width, header_h))
        
        # 背番号を大きく表示
        number_surf = fonts.h1.render(f"#{player.uniform_number}", True, team_color)
        self.screen.blit(number_surf, (30, 20))
        
        # 名前
        name_surf = fonts.h2.render(player.name, True, Colors.TEXT_PRIMARY)
        self.screen.blit(name_surf, (120, 25))
        
        # ポジション・年齢・契約タイプを横に
        contract_text = "育成" if player.is_developmental else "支配下"
        info_line = f"{pos_text}  |  {player.age}歳  |  {contract_text}  |  プロ{player.years_pro}年目"
        info_surf = fonts.body.render(info_line, True, Colors.TEXT_SECONDARY)
        self.screen.blit(info_surf, (120, 60))
        
        # 年俸表示（右側）
        if player.salary >= 100000000:
            salary_text = f"{player.salary // 100000000}億{(player.salary % 100000000) // 10000000}千万"
        else:
            salary_text = f"{player.salary // 10000}万円"
        salary_surf = fonts.body.render(salary_text, True, Colors.WARNING)
        self.screen.blit(salary_surf, (width - salary_surf.get_width() - 30, 35))
        
        buttons = {}
        stats = player.stats
        
        # ===== 能力値表示エリア =====
        content_y = header_h + 10
        
        if player.position == Position.PITCHER:
            # 投手能力カード（左側）
            ability_card = Card(20, content_y, 400, 260, "PITCHER")
            ability_rect = ability_card.draw(self.screen)
            
            # 基本能力（2x2グリッド）
            abilities = [
                ("球速", stats.speed, "", f"{130 + stats.speed * 2}km"),
                ("コントロール", stats.control, "", ""),
                ("スタミナ", stats.stamina, "", ""),
                ("変化球", stats.breaking, "", ""),
            ]
            
            y = ability_rect.y + 45
            for i, (name, value, icon, extra) in enumerate(abilities):
                col = i % 2
                x = ability_rect.x + 20 + col * 185
                if i == 2:
                    y += 55
                
                # 名前
                name_surf = fonts.small.render(f"{icon} {name}", True, Colors.TEXT_SECONDARY)
                self.screen.blit(name_surf, (x, y))
                
                # ランク（大きく）
                rank = stats.get_rank(value)
                rank_color = stats.get_rank_color(value)
                rank_surf = fonts.h2.render(rank, True, rank_color)
                self.screen.blit(rank_surf, (x, y + 18))
                
                # 数値とバー
                value_text = f"{value}" + (f" {extra}" if extra else "")
                val_surf = fonts.tiny.render(value_text, True, Colors.TEXT_MUTED)
                self.screen.blit(val_surf, (x + 35, y + 28))
                
                # バー
                bar_x = x + 80
                bar_y = y + 30
                pygame.draw.rect(self.screen, Colors.BG_INPUT, (bar_x, bar_y, 80, 6), border_radius=3)
                fill_w = int(80 * min(value / 20, 1.0))
                pygame.draw.rect(self.screen, rank_color, (bar_x, bar_y, fill_w, 6), border_radius=3)
            
            # 球種カード（右側）
            pitch_card = Card(430, content_y, width - 450, 260, "🎱 持ち球")
            pitch_rect = pitch_card.draw(self.screen)
            
            y = pitch_rect.y + 45
            if hasattr(stats, 'pitch_repertoire') and stats.pitch_repertoire:
                for pitch_name, break_value in list(stats.pitch_repertoire.items())[:8]:
                    # 球種名
                    pitch_surf = fonts.body.render(pitch_name, True, Colors.TEXT_PRIMARY)
                    self.screen.blit(pitch_surf, (pitch_rect.x + 20, y))
                    # 変化量バー
                    bar_x = pitch_rect.x + 150
                    pygame.draw.rect(self.screen, Colors.BG_INPUT, (bar_x, y + 5, 80, 8), border_radius=4)
                    fill_w = int(80 * min(break_value / 7, 1.0))
                    pygame.draw.rect(self.screen, Colors.INFO, (bar_x, y + 5, fill_w, 8), border_radius=4)
                    # 変化量
                    val_surf = fonts.small.render(f"{break_value}", True, Colors.TEXT_SECONDARY)
                    self.screen.blit(val_surf, (bar_x + 85, y + 2))
                    y += 26
            elif stats.breaking_balls:
                for pitch_name in stats.breaking_balls[:8]:
                    pitch_surf = fonts.body.render(f"• {pitch_name}", True, Colors.TEXT_PRIMARY)
                    self.screen.blit(pitch_surf, (pitch_rect.x + 20, y))
                    y += 26
            
        else:
            # 野手能力カード（左側）
            ability_card = Card(20, content_y, 400, 260, "🏏 野手能力")
            ability_rect = ability_card.draw(self.screen)
            
            # 弾道表示（上部に大きく）
            trajectory = getattr(stats, 'trajectory', 2)
            traj_names = {1: "グラウンダー", 2: "ライナー", 3: "普通", 4: "パワー"}
            
            traj_label = fonts.small.render("弾道", True, Colors.TEXT_SECONDARY)
            self.screen.blit(traj_label, (ability_rect.x + 20, ability_rect.y + 42))
            
            # 弾道アイコン（丸で表示）
            for i in range(4):
                color = Colors.WARNING if i < trajectory else Colors.BG_INPUT
                pygame.draw.circle(self.screen, color, (ability_rect.x + 80 + i * 25, ability_rect.y + 52), 8)
            traj_name_surf = fonts.small.render(traj_names.get(trajectory, '普通'), True, Colors.TEXT_MUTED)
            self.screen.blit(traj_name_surf, (ability_rect.x + 190, ability_rect.y + 45))
            
            # 基本能力（3列×2行）
            abilities = [
                ("ミート", stats.contact, ""),
                ("パワー", stats.power, ""),
                ("走力", stats.run, ""),
                ("肩力", stats.arm, ""),
                ("守備", stats.fielding, ""),
                ("捕球", getattr(stats, 'catching', stats.fielding), ""),
            ]
            
            y = ability_rect.y + 75
            for i, (name, value, icon) in enumerate(abilities):
                col = i % 3
                x = ability_rect.x + 15 + col * 125
                if i == 3:
                    y += 55
                
                # 名前
                name_surf = fonts.tiny.render(f"{icon}{name}", True, Colors.TEXT_SECONDARY)
                self.screen.blit(name_surf, (x, y))
                
                # ランク（大きく）
                rank = stats.get_rank(value)
                rank_color = stats.get_rank_color(value)
                rank_surf = fonts.h3.render(rank, True, rank_color)
                self.screen.blit(rank_surf, (x, y + 15))
                
                # 数値
                val_surf = fonts.tiny.render(f"{value}", True, Colors.TEXT_MUTED)
                self.screen.blit(val_surf, (x + 30, y + 22))
                
                # バー
                bar_x = x + 50
                bar_y = y + 25
                pygame.draw.rect(self.screen, Colors.BG_INPUT, (bar_x, bar_y, 60, 5), border_radius=2)
                fill_w = int(60 * min(value / 20, 1.0))
                pygame.draw.rect(self.screen, rank_color, (bar_x, bar_y, fill_w, 5), border_radius=2)
            
            # 守備適性カード（右側）
            pos_card = Card(430, content_y, width - 450, 260, "POSITION")
            pos_rect = pos_card.draw(self.screen)
            
            # メインポジション
            main_pos_surf = fonts.body.render(f"メイン: {player.position.value}", True, Colors.PRIMARY)
            self.screen.blit(main_pos_surf, (pos_rect.x + 20, pos_rect.y + 45))
            
            # サブポジション
            y = pos_rect.y + 75
            sub_label = fonts.small.render("サブポジション:", True, Colors.TEXT_SECONDARY)
            self.screen.blit(sub_label, (pos_rect.x + 20, y))
            y += 25
            
            if hasattr(player, 'sub_positions') and player.sub_positions:
                for sub_pos in player.sub_positions[:4]:
                    pos_surf = fonts.body.render(f"• {sub_pos.value}", True, Colors.TEXT_PRIMARY)
                    self.screen.blit(pos_surf, (pos_rect.x + 30, y))
                    y += 24
            else:
                none_surf = fonts.small.render("なし", True, Colors.TEXT_MUTED)
                self.screen.blit(none_surf, (pos_rect.x + 30, y))
        
        # 特殊能力カード（下部左）
        special_card = Card(20, content_y + 270, 400, 155, "SKILLS")
        special_rect = special_card.draw(self.screen)
        
        if player.position == Position.PITCHER:
            special_abilities = [
                ("対ピンチ", stats.clutch, ""),
                ("対左打者", getattr(stats, 'vs_left', 10), ""),
                ("メンタル", stats.mental, ""),
                ("安定感", stats.consistency, ""),
                ("クイック", getattr(stats, 'quick', 10), ""),
                ("牽制", getattr(stats, 'pickoff', 10), ""),
            ]
        else:
            special_abilities = [
                ("チャンス", stats.clutch, ""),
                ("対左投手", getattr(stats, 'vs_left', 10), ""),
                ("メンタル", stats.mental, ""),
                ("安定感", stats.consistency, ""),
                ("盗塁", getattr(stats, 'stealing', stats.run), ""),
                ("送球", getattr(stats, 'throwing', stats.arm), ""),
            ]
        
        y = special_rect.y + 42
        for i, (name, value, icon) in enumerate(special_abilities):
            col = i % 3
            x = special_rect.x + 15 + col * 125
            if i == 3:
                y += 38
            
            rank = stats.get_rank(value)
            rank_color = stats.get_rank_color(value)
            
            name_surf = fonts.tiny.render(f"{icon}{name}", True, Colors.TEXT_SECONDARY)
            rank_surf = fonts.body.render(rank, True, rank_color)
            
            self.screen.blit(name_surf, (x, y))
            self.screen.blit(rank_surf, (x, y + 16))
            
            # ミニバー
            bar_x = x + 30
            pygame.draw.rect(self.screen, Colors.BG_INPUT, (bar_x, y + 22, 50, 4), border_radius=2)
            fill = int(50 * min(value / 20, 1.0))
            pygame.draw.rect(self.screen, rank_color, (bar_x, y + 22, fill, 4), border_radius=2)
        
        # 成績カード（下部右）
        record = player.record
        record_card = Card(430, content_y + 270, width - 450, 155, "STATS")
        record_rect = record_card.draw(self.screen)
        
        if player.position == Position.PITCHER:
            stats_items = [
                ("登板", f"{record.games_pitched}", Colors.TEXT_PRIMARY),
                ("勝", f"{record.wins}", Colors.SUCCESS),
                ("敗", f"{record.losses}", Colors.DANGER),
                ("S", f"{record.saves}", Colors.INFO),
                ("防御率", f"{record.era:.2f}", Colors.WARNING if record.era < 3.0 else Colors.TEXT_PRIMARY),
                ("K", f"{record.strikeouts_pitched}", Colors.PRIMARY),
            ]
        else:
            avg = record.batting_average
            avg_color = Colors.WARNING if avg >= 0.300 else Colors.SUCCESS if avg >= 0.280 else Colors.TEXT_PRIMARY
            stats_items = [
                ("打率", f".{int(avg * 1000):03d}" if avg > 0 else ".000", avg_color),
                ("安打", f"{record.hits}", Colors.TEXT_PRIMARY),
                ("HR", f"{record.home_runs}", Colors.DANGER if record.home_runs >= 20 else Colors.TEXT_PRIMARY),
                ("打点", f"{record.rbis}", Colors.SUCCESS),
                ("盗塁", f"{record.stolen_bases}", Colors.INFO),
                ("OPS", f"{record.ops:.3f}" if hasattr(record, 'ops') else "-", Colors.WARNING),
            ]
        
        x = record_rect.x + 15
        y = record_rect.y + 45
        item_width = (record_rect.width - 30) // len(stats_items)
        for label, value, color in stats_items:
            label_surf = fonts.tiny.render(label, True, Colors.TEXT_SECONDARY)
            value_surf = fonts.h3.render(value, True, color)
            self.screen.blit(label_surf, (x, y))
            self.screen.blit(value_surf, (x, y + 18))
            x += item_width
        
        # 戻るボタン
        buttons["back"] = Button(
            50, height - 70, 150, 50,
            "← 戻る", "ghost", font=fonts.body
        )
        buttons["back"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # 育成ドラフト画面
    # ========================================
    def draw_developmental_draft_screen(self, prospects: List, selected_idx: int = -1,
                                        draft_round: int = 1, draft_messages: List[str] = None) -> Dict[str, Button]:
        """育成ドラフト画面を描画"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        center_x = width // 2
        
        # ヘッダー（育成は別色）
        round_text = f"育成第{draft_round}巡目"
        header_h = draw_header(self.screen, f"DEV DRAFT - {round_text}", "将来性のある選手を発掘", Colors.SUCCESS)
        
        buttons = {}
        
        # 左側: 候補者リスト
        card_width = width - 320 if draft_messages else width - 60
        card = Card(30, header_h + 15, card_width - 30, height - header_h - 120)
        card_rect = card.draw(self.screen)
        
        # ヘッダー行
        headers = [("名前", 140), ("ポジション", 90), ("年齢", 50), ("ポテンシャル", 90), ("総合", 70)]
        x = card_rect.x + 15
        y = card_rect.y + 18
        
        for header_text, w in headers:
            h_surf = fonts.tiny.render(header_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(h_surf, (x, y))
            x += w
        
        y += 22
        pygame.draw.line(self.screen, Colors.BORDER, (card_rect.x + 10, y), (card_rect.right - 10, y), 1)
        y += 8
        
        # 候補者一覧
        visible_count = min(12, len(prospects))
        
        for i in range(visible_count):
            prospect = prospects[i]
            row_rect = pygame.Rect(card_rect.x + 8, y - 2, card_rect.width - 16, 32)
            
            # 選択中
            if i == selected_idx:
                pygame.draw.rect(self.screen, (*Colors.SUCCESS[:3], 50), row_rect, border_radius=4)
                pygame.draw.rect(self.screen, Colors.SUCCESS, row_rect, 2, border_radius=4)
            elif i % 2 == 0:
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=3)
            
            x = card_rect.x + 15
            
            # 名前
            name_surf = fonts.small.render(prospect.name[:8], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (x, y + 4))
            x += 140
            
            # ポジション
            pos_text = prospect.position.value[:2]
            if prospect.pitch_type:
                pos_text += f"({prospect.pitch_type.value[0]})"
            pos_surf = fonts.tiny.render(pos_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (x, y + 6))
            x += 90
            
            # 年齢
            age_surf = fonts.small.render(f"{prospect.age}", True, Colors.TEXT_PRIMARY)
            self.screen.blit(age_surf, (x, y + 4))
            x += 50
            
            # ポテンシャル（星表示、育成は最大3つ）
            pot_stars = min(prospect.potential // 3, 3)
            pot_color = Colors.SUCCESS if pot_stars >= 2 else Colors.TEXT_SECONDARY
            pot_surf = fonts.small.render("★" * pot_stars, True, pot_color)
            self.screen.blit(pot_surf, (x, y + 4))
            x += 90
            
            # 総合力
            overall = prospect.stats.overall_batting() if prospect.position.value != "投手" else prospect.stats.overall_pitching()
            overall_surf = fonts.small.render(f"{overall:.0f}", True, Colors.TEXT_PRIMARY)
            self.screen.blit(overall_surf, (x, y + 4))
            
            y += 35
        
        # 右側: 指名履歴
        if draft_messages:
            log_card = Card(width - 280, header_h + 15, 250, height - header_h - 120, "PICK LOG")
            log_rect = log_card.draw(self.screen)
            
            log_y = log_rect.y + 42
            recent_msgs = draft_messages[-8:] if len(draft_messages) > 8 else draft_messages
            for msg in recent_msgs:
                msg_surf = fonts.tiny.render(msg[:28], True, Colors.TEXT_SECONDARY)
                self.screen.blit(msg_surf, (log_rect.x + 8, log_y))
                log_y += 20
        
        # ボタン
        btn_y = height - 85
        
        buttons["draft_developmental"] = Button(
            center_x + 30, btn_y, 180, 50,
            "この選手を指名", "success", font=fonts.body
        )
        buttons["draft_developmental"].enabled = selected_idx >= 0
        buttons["draft_developmental"].draw(self.screen)
        
        buttons["skip_developmental"] = Button(
            center_x - 210, btn_y, 180, 50,
            "育成ドラフト終了", "ghost", font=fonts.body
        )
        buttons["skip_developmental"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons

    def draw_pitcher_order_screen(self, player_team, pitcher_order_tab: str = "rotation",
                                  selected_rotation_slot: int = -1,
                                  selected_relief_slot: int = -1,
                                  scroll_offset: int = 0) -> Dict[str, Button]:
        """投手オーダー画面を描画（ローテーション・中継ぎ・抑え設定）"""
        from models import Position, PitchType
        
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        team_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        header_h = draw_header(self.screen, "投手起用設定", 
                               "先発ローテーション・中継ぎ・抑えを設定", team_color)
        
        buttons = {}
        
        if not player_team:
            return buttons
        
        # タブボタン
        tab_y = header_h + 15
        tab_items = [
            ("rotation", "先発ローテ"),
            ("relief", "中継ぎ"),
            ("closer", "抑え"),
        ]
        
        tab_x = 50
        for tab_id, tab_name in tab_items:
            is_active = pitcher_order_tab == tab_id
            btn_style = "primary" if is_active else "ghost"
            buttons[f"tab_{tab_id}"] = Button(tab_x, tab_y, 130, 40, tab_name, btn_style, font=fonts.body)
            buttons[f"tab_{tab_id}"].draw(self.screen)
            tab_x += 140
        
        content_y = tab_y + 55
        
        # ====================
        # 左パネル: 設定済み投手陣
        # ====================
        left_card = Card(30, content_y, 400, height - content_y - 90, "CURRENT STAFF")
        left_rect = left_card.draw(self.screen)
        
        staff_y = left_rect.y + 45
        
        if pitcher_order_tab == "rotation":
            # 先発ローテーション（6人）
            title_surf = fonts.body_bold.render("先発ローテーション (最大6人)", True, Colors.PRIMARY)
            self.screen.blit(title_surf, (left_rect.x + 15, staff_y))
            staff_y += 35
            
            rotation = player_team.rotation if player_team.rotation else []
            for i in range(6):
                slot_rect = pygame.Rect(left_rect.x + 10, staff_y, left_rect.width - 20, 45)
                is_selected = selected_rotation_slot == i
                
                bg_color = Colors.SECONDARY if is_selected else (Colors.SURFACE if i % 2 == 0 else Colors.BACKGROUND)
                pygame.draw.rect(self.screen, bg_color, slot_rect, border_radius=6)
                
                # スロット番号（曜日表示）
                weekdays = ["月", "火", "水", "木", "金", "土"]
                day_surf = fonts.body_bold.render(f"{weekdays[i]}", True, Colors.PRIMARY)
                self.screen.blit(day_surf, (slot_rect.x + 10, slot_rect.y + 12))
                
                if i < len(rotation) and 0 <= rotation[i] < len(player_team.players):
                    pitcher = player_team.players[rotation[i]]
                    name_surf = fonts.body.render(pitcher.name, True, Colors.TEXT_PRIMARY)
                    self.screen.blit(name_surf, (slot_rect.x + 50, slot_rect.y + 12))
                    
                    # 能力表示
                    stats = pitcher.stats
                    ability_text = f"球速{stats.speed} 制球{stats.control} 変化{stats.breaking}"
                    ability_surf = fonts.tiny.render(ability_text, True, Colors.TEXT_SECONDARY)
                    self.screen.blit(ability_surf, (slot_rect.x + 200, slot_rect.y + 15))
                else:
                    empty_surf = fonts.body.render("- 未設定 -", True, Colors.TEXT_MUTED)
                    self.screen.blit(empty_surf, (slot_rect.x + 50, slot_rect.y + 12))
                
                buttons[f"rotation_slot_{i}"] = Button(slot_rect.x, slot_rect.y, slot_rect.width, slot_rect.height, "", "ghost")
                staff_y += 50
        
        elif pitcher_order_tab == "relief":
            # 中継ぎ投手（最大8人）
            title_surf = fonts.body_bold.render("中継ぎ投手 (最大8人)", True, Colors.WARNING)
            self.screen.blit(title_surf, (left_rect.x + 15, staff_y))
            staff_y += 35
            
            bench_pitchers = player_team.bench_pitchers if hasattr(player_team, 'bench_pitchers') else []
            setup_pitchers = player_team.setup_pitchers if player_team.setup_pitchers else []
            
            # bench_pitchersとsetup_pitchersを統合
            relief_pitchers = list(set(bench_pitchers) | set(setup_pitchers))
            
            for i in range(8):
                slot_rect = pygame.Rect(left_rect.x + 10, staff_y, left_rect.width - 20, 45)
                is_selected = selected_relief_slot == i
                
                bg_color = Colors.SECONDARY if is_selected else (Colors.SURFACE if i % 2 == 0 else Colors.BACKGROUND)
                pygame.draw.rect(self.screen, bg_color, slot_rect, border_radius=6)
                
                slot_surf = fonts.body_bold.render(f"{i+1}", True, Colors.WARNING)
                self.screen.blit(slot_surf, (slot_rect.x + 10, slot_rect.y + 12))
                
                if i < len(relief_pitchers) and 0 <= relief_pitchers[i] < len(player_team.players):
                    pitcher = player_team.players[relief_pitchers[i]]
                    name_surf = fonts.body.render(pitcher.name, True, Colors.TEXT_PRIMARY)
                    self.screen.blit(name_surf, (slot_rect.x + 50, slot_rect.y + 12))
                    
                    stats = pitcher.stats
                    ability_text = f"球速{stats.speed} 制球{stats.control}"
                    ability_surf = fonts.tiny.render(ability_text, True, Colors.TEXT_SECONDARY)
                    self.screen.blit(ability_surf, (slot_rect.x + 220, slot_rect.y + 15))
                else:
                    empty_surf = fonts.body.render("- 未設定 -", True, Colors.TEXT_MUTED)
                    self.screen.blit(empty_surf, (slot_rect.x + 50, slot_rect.y + 12))
                
                buttons[f"relief_slot_{i}"] = Button(slot_rect.x, slot_rect.y, slot_rect.width, slot_rect.height, "", "ghost")
                staff_y += 50
        
        elif pitcher_order_tab == "closer":
            # 抑え投手（1人）
            title_surf = fonts.body_bold.render("守護神（クローザー）", True, Colors.DANGER)
            self.screen.blit(title_surf, (left_rect.x + 15, staff_y))
            staff_y += 40
            
            closer_rect = pygame.Rect(left_rect.x + 10, staff_y, left_rect.width - 20, 80)
            pygame.draw.rect(self.screen, Colors.SURFACE, closer_rect, border_radius=10)
            pygame.draw.rect(self.screen, Colors.DANGER, closer_rect, 2, border_radius=10)
            
            if player_team.closer_idx >= 0 and player_team.closer_idx < len(player_team.players):
                closer = player_team.players[player_team.closer_idx]
                
                # 大きめの名前表示
                name_surf = fonts.h2.render(closer.name, True, Colors.DANGER)
                self.screen.blit(name_surf, (closer_rect.x + 20, closer_rect.y + 10))
                
                # 能力表示
                stats = closer.stats
                ability_text = f"球速{stats.speed}  制球{stats.control}  変化{stats.breaking}  スタミナ{stats.stamina}"
                ability_surf = fonts.body.render(ability_text, True, Colors.TEXT_SECONDARY)
                self.screen.blit(ability_surf, (closer_rect.x + 20, closer_rect.y + 48))
            else:
                empty_surf = fonts.h3.render("- 未設定 -", True, Colors.TEXT_MUTED)
                self.screen.blit(empty_surf, (closer_rect.x + 100, closer_rect.y + 28))
            
            buttons["closer_slot"] = Button(closer_rect.x, closer_rect.y, closer_rect.width, closer_rect.height, "", "ghost")
        
        # ====================
        # 右パネル: 投手一覧
        # ====================
        right_card = Card(450, content_y, width - 480, height - content_y - 90, "PITCHERS")
        right_rect = right_card.draw(self.screen)
        
        # フィルター（タイプ別）
        pitchers = [p for p in player_team.players if p.position == Position.PITCHER and not p.is_developmental]
        
        # タブに応じたフィルタ
        if pitcher_order_tab == "rotation":
            # 先発投手を優先表示
            pitchers.sort(key=lambda p: (0 if p.pitch_type == PitchType.STARTER else 1, -p.stats.overall_pitching()))
        elif pitcher_order_tab == "relief":
            # 中継ぎを優先表示
            pitchers.sort(key=lambda p: (0 if p.pitch_type == PitchType.RELIEVER else 1, -p.stats.overall_pitching()))
        elif pitcher_order_tab == "closer":
            # 抑えを優先表示
            pitchers.sort(key=lambda p: (0 if p.pitch_type == PitchType.CLOSER else 1, -p.stats.overall_pitching()))
        
        list_y = right_rect.y + 45
        
        # ヘッダー
        headers = [("名前", 150), ("タイプ", 70), ("球速", 50), ("制球", 50), ("変化", 50), ("スタ", 50)]
        hx = right_rect.x + 15
        for h_name, h_width in headers:
            h_surf = fonts.small_bold.render(h_name, True, Colors.TEXT_MUTED)
            self.screen.blit(h_surf, (hx, list_y))
            hx += h_width
        list_y += 28
        
        pygame.draw.line(self.screen, Colors.BORDER, (right_rect.x + 10, list_y), (right_rect.right - 10, list_y))
        list_y += 8
        
        # 表示範囲を計算
        visible_count = (right_rect.bottom - list_y - 20) // 38
        start_idx = scroll_offset
        end_idx = min(start_idx + visible_count, len(pitchers))
        
        for i, pitcher in enumerate(pitchers[start_idx:end_idx], start_idx):
            row_rect = pygame.Rect(right_rect.x + 10, list_y, right_rect.width - 20, 35)
            
            bg_color = Colors.SURFACE if i % 2 == 0 else Colors.BACKGROUND
            pygame.draw.rect(self.screen, bg_color, row_rect, border_radius=4)
            
            rx = right_rect.x + 15
            
            # 名前
            name_surf = fonts.body.render(pitcher.name[:8], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (rx, list_y + 8))
            rx += 150
            
            # タイプ
            type_text = pitcher.pitch_type.value[:2] if pitcher.pitch_type else "-"
            type_color = Colors.PRIMARY if pitcher.pitch_type == PitchType.STARTER else (
                Colors.WARNING if pitcher.pitch_type == PitchType.RELIEVER else Colors.DANGER)
            type_surf = fonts.small.render(type_text, True, type_color)
            self.screen.blit(type_surf, (rx, list_y + 10))
            rx += 70
            
            # 能力値
            stats = pitcher.stats
            for val in [stats.speed, stats.control, stats.breaking, stats.stamina]:
                val_color = Colors.SUCCESS if val >= 70 else (Colors.WARNING if val >= 50 else Colors.TEXT_SECONDARY)
                val_surf = fonts.small.render(str(val), True, val_color)
                self.screen.blit(val_surf, (rx, list_y + 10))
                rx += 50
            
            # 選択ボタン
            player_idx = player_team.players.index(pitcher)
            buttons[f"pitcher_{player_idx}"] = Button(row_rect.x, row_rect.y, row_rect.width, row_rect.height, "", "ghost")
            
            list_y += 38
        
        # スクロールボタン
        if scroll_offset > 0:
            buttons["pitcher_scroll_up"] = Button(right_rect.right - 50, right_rect.y + 45, 40, 30, "▲", "secondary")
            buttons["pitcher_scroll_up"].draw(self.screen)
        
        if end_idx < len(pitchers):
            buttons["pitcher_scroll_down"] = Button(right_rect.right - 50, right_rect.bottom - 40, 40, 30, "▼", "secondary")
            buttons["pitcher_scroll_down"].draw(self.screen)
        
        # ====================
        # 下部ボタン
        # ====================
        btn_y = height - 75
        
        buttons["pitcher_auto_set"] = Button(50, btn_y, 150, 50, "自動設定", "warning", font=fonts.body)
        buttons["pitcher_auto_set"].draw(self.screen)
        
        buttons["pitcher_back"] = Button(220, btn_y, 150, 50, "戻る", "ghost", font=fonts.body)
        buttons["pitcher_back"].draw(self.screen)
        
        buttons["to_bench_setting"] = Button(width - 220, btn_y, 180, 50, "ベンチ設定へ", "primary", font=fonts.body)
        buttons["to_bench_setting"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons

    def draw_bench_setting_screen(self, player_team, bench_tab: str = "batters",
                                  scroll_offset: int = 0) -> Dict[str, Button]:
        """ベンチ入りメンバー設定画面を描画"""
        from models import Position, PitchType
        
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        team_color = self.get_team_color(player_team.name) if player_team else Colors.PRIMARY
        header_h = draw_header(self.screen, "ベンチ入りメンバー設定", 
                               "試合に出場する控え選手を選択", team_color)
        
        buttons = {}
        
        if not player_team:
            return buttons
        
        # タブボタン
        tab_y = header_h + 15
        buttons["bench_tab_batters"] = Button(50, tab_y, 150, 40, "野手ベンチ", 
                                               "primary" if bench_tab == "batters" else "ghost", font=fonts.body)
        buttons["bench_tab_batters"].draw(self.screen)
        
        buttons["bench_tab_pitchers"] = Button(210, tab_y, 150, 40, "投手ベンチ",
                                                "primary" if bench_tab == "pitchers" else "ghost", font=fonts.body)
        buttons["bench_tab_pitchers"].draw(self.screen)
        
        # 登録情報表示
        info_text = f"一軍登録: {len(player_team.active_roster)}/{player_team.MAX_ACTIVE_ROSTER}人"
        info_surf = fonts.body.render(info_text, True, Colors.TEXT_SECONDARY)
        self.screen.blit(info_surf, (width - 250, tab_y + 10))
        
        content_y = tab_y + 55
        
        # ====================
        # 左パネル: 現在のベンチ
        # ====================
        left_card = Card(30, content_y, 380, height - content_y - 90, "CURRENT BENCH")
        left_rect = left_card.draw(self.screen)
        
        bench_y = left_rect.y + 45
        
        if bench_tab == "batters":
            title_surf = fonts.body_bold.render(f"ベンチ野手 ({len(player_team.bench_batters)}/{player_team.MAX_BENCH_BATTERS})", True, Colors.PRIMARY)
            self.screen.blit(title_surf, (left_rect.x + 15, bench_y))
            bench_y += 35
            
            for i, player_idx in enumerate(player_team.bench_batters):
                if 0 <= player_idx < len(player_team.players):
                    player = player_team.players[player_idx]
                    
                    row_rect = pygame.Rect(left_rect.x + 10, bench_y, left_rect.width - 20, 40)
                    pygame.draw.rect(self.screen, Colors.SURFACE if i % 2 == 0 else Colors.BACKGROUND, row_rect, border_radius=4)
                    
                    # 名前とポジション
                    name_surf = fonts.body.render(player.name, True, Colors.TEXT_PRIMARY)
                    self.screen.blit(name_surf, (row_rect.x + 10, row_rect.y + 10))
                    
                    pos_surf = fonts.small.render(player.position.value[:2], True, Colors.TEXT_SECONDARY)
                    self.screen.blit(pos_surf, (row_rect.x + 180, row_rect.y + 12))
                    
                    # 総合力
                    overall = player.stats.overall_batting()
                    ov_surf = fonts.small.render(f"総合{overall:.0f}", True, Colors.TEXT_MUTED)
                    self.screen.blit(ov_surf, (row_rect.x + 230, row_rect.y + 12))
                    
                    # 外すボタン
                    buttons[f"remove_bench_batter_{i}"] = Button(row_rect.right - 60, row_rect.y + 5, 50, 30, "外す", "danger")
                    buttons[f"remove_bench_batter_{i}"].draw(self.screen)
                    
                    bench_y += 45
        
        else:  # pitchers
            title_surf = fonts.body_bold.render(f"ベンチ投手 ({len(player_team.bench_pitchers)}/{player_team.MAX_BENCH_PITCHERS})", True, Colors.WARNING)
            self.screen.blit(title_surf, (left_rect.x + 15, bench_y))
            bench_y += 35
            
            for i, player_idx in enumerate(player_team.bench_pitchers):
                if 0 <= player_idx < len(player_team.players):
                    pitcher = player_team.players[player_idx]
                    
                    row_rect = pygame.Rect(left_rect.x + 10, bench_y, left_rect.width - 20, 40)
                    pygame.draw.rect(self.screen, Colors.SURFACE if i % 2 == 0 else Colors.BACKGROUND, row_rect, border_radius=4)
                    
                    # 名前とタイプ
                    name_surf = fonts.body.render(pitcher.name, True, Colors.TEXT_PRIMARY)
                    self.screen.blit(name_surf, (row_rect.x + 10, row_rect.y + 10))
                    
                    type_text = pitcher.pitch_type.value[:2] if pitcher.pitch_type else "-"
                    type_surf = fonts.small.render(type_text, True, Colors.TEXT_SECONDARY)
                    self.screen.blit(type_surf, (row_rect.x + 180, row_rect.y + 12))
                    
                    # 総合力
                    overall = pitcher.stats.overall_pitching()
                    ov_surf = fonts.small.render(f"総合{overall:.0f}", True, Colors.TEXT_MUTED)
                    self.screen.blit(ov_surf, (row_rect.x + 230, row_rect.y + 12))
                    
                    # 外すボタン
                    buttons[f"remove_bench_pitcher_{i}"] = Button(row_rect.right - 60, row_rect.y + 5, 50, 30, "外す", "danger")
                    buttons[f"remove_bench_pitcher_{i}"].draw(self.screen)
                    
                    bench_y += 45
        
        # ====================
        # 右パネル: 選手一覧（追加可能な選手）
        # ====================
        right_card = Card(430, content_y, width - 460, height - content_y - 90, "AVAILABLE")
        right_rect = right_card.draw(self.screen)
        
        list_y = right_rect.y + 45
        
        if bench_tab == "batters":
            # スタメン・ベンチ以外の野手
            lineup_set = set(player_team.current_lineup) if player_team.current_lineup else set()
            bench_set = set(player_team.bench_batters)
            
            available = [p for p in player_team.players 
                        if p.position != Position.PITCHER 
                        and not p.is_developmental
                        and player_team.players.index(p) not in lineup_set
                        and player_team.players.index(p) not in bench_set]
            available.sort(key=lambda p: -p.stats.overall_batting())
        else:
            # ローテ・ベンチ以外の投手
            rotation_set = set(player_team.rotation) if player_team.rotation else set()
            bench_set = set(player_team.bench_pitchers)
            
            available = [p for p in player_team.players 
                        if p.position == Position.PITCHER 
                        and not p.is_developmental
                        and player_team.players.index(p) not in rotation_set
                        and player_team.players.index(p) not in bench_set]
            available.sort(key=lambda p: -p.stats.overall_pitching())
        
        # ヘッダー
        if bench_tab == "batters":
            headers = [("名前", 130), ("守備", 50), ("ミート", 55), ("パワー", 55), ("走力", 50)]
        else:
            headers = [("名前", 130), ("タイプ", 60), ("球速", 50), ("制球", 50), ("変化", 50)]
        
        hx = right_rect.x + 15
        for h_name, h_width in headers:
            h_surf = fonts.small_bold.render(h_name, True, Colors.TEXT_MUTED)
            self.screen.blit(h_surf, (hx, list_y))
            hx += h_width
        list_y += 28
        
        pygame.draw.line(self.screen, Colors.BORDER, (right_rect.x + 10, list_y), (right_rect.right - 10, list_y))
        list_y += 8
        
        # 表示範囲
        visible_count = (right_rect.bottom - list_y - 20) // 40
        start_idx = scroll_offset
        end_idx = min(start_idx + visible_count, len(available))
        
        for i, player in enumerate(available[start_idx:end_idx], start_idx):
            row_rect = pygame.Rect(right_rect.x + 10, list_y, right_rect.width - 20, 38)
            
            bg_color = Colors.SURFACE if i % 2 == 0 else Colors.BACKGROUND
            pygame.draw.rect(self.screen, bg_color, row_rect, border_radius=4)
            
            rx = right_rect.x + 15
            
            # 名前
            name_surf = fonts.body.render(player.name[:7], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (rx, list_y + 9))
            rx += 130
            
            if bench_tab == "batters":
                # 守備
                pos_surf = fonts.small.render(player.position.value[:2], True, Colors.TEXT_SECONDARY)
                self.screen.blit(pos_surf, (rx, list_y + 11))
                rx += 50
                
                # 能力値
                stats = player.stats
                for val in [stats.contact, stats.power, stats.speed]:
                    val_color = Colors.SUCCESS if val >= 70 else (Colors.WARNING if val >= 50 else Colors.TEXT_SECONDARY)
                    val_surf = fonts.small.render(str(val), True, val_color)
                    self.screen.blit(val_surf, (rx, list_y + 11))
                    rx += 55
            else:
                # タイプ
                type_text = player.pitch_type.value[:2] if player.pitch_type else "-"
                type_surf = fonts.small.render(type_text, True, Colors.TEXT_SECONDARY)
                self.screen.blit(type_surf, (rx, list_y + 11))
                rx += 60
                
                # 能力値
                stats = player.stats
                for val in [stats.speed, stats.control, stats.breaking]:
                    val_color = Colors.SUCCESS if val >= 70 else (Colors.WARNING if val >= 50 else Colors.TEXT_SECONDARY)
                    val_surf = fonts.small.render(str(val), True, val_color)
                    self.screen.blit(val_surf, (rx, list_y + 11))
                    rx += 50
            
            # 追加ボタン
            player_idx = player_team.players.index(player)
            buttons[f"add_bench_{player_idx}"] = Button(row_rect.right - 60, row_rect.y + 4, 50, 30, "追加", "success")
            buttons[f"add_bench_{player_idx}"].draw(self.screen)
            
            list_y += 40
        
        # スクロールボタン
        if scroll_offset > 0:
            buttons["bench_scroll_up"] = Button(right_rect.right - 50, right_rect.y + 45, 40, 30, "▲", "secondary")
            buttons["bench_scroll_up"].draw(self.screen)
        
        if end_idx < len(available):
            buttons["bench_scroll_down"] = Button(right_rect.right - 50, right_rect.bottom - 40, 40, 30, "▼", "secondary")
            buttons["bench_scroll_down"].draw(self.screen)
        
        # ====================
        # 下部ボタン
        # ====================
        btn_y = height - 75
        
        buttons["bench_auto_set"] = Button(50, btn_y, 150, 50, "自動設定", "warning", font=fonts.body)
        buttons["bench_auto_set"].draw(self.screen)
        
        buttons["bench_back"] = Button(220, btn_y, 150, 50, "戻る", "ghost", font=fonts.body)
        buttons["bench_back"].draw(self.screen)
        
        buttons["to_lineup"] = Button(width - 220, btn_y, 180, 50, "オーダーへ", "primary", font=fonts.body)
        buttons["to_lineup"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons