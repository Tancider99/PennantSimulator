# -*- coding: utf-8 -*-
"""
ペナントモード専用UI画面
"""
import pygame
from typing import Dict, List, Optional, Tuple

from ui_pro import (
    Colors, fonts, Button, Card, ProgressBar, Table,
    ToastManager, draw_background, draw_header, draw_rounded_rect
)
from pennant_mode import (
    PennantManager, PennantPhase, DraftPlayer, DraftCategory,
    FAPlayer, TradeOffer, Coach, Slogan, Injury, SpringCampState
)
from models import Player, Team, Position


class PennantScreens:
    """ペナントモード専用画面"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.team_colors = {
            "読売ジャイアンツ": (255, 102, 0),
            "阪神タイガース": (255, 209, 0),
            "中日ドラゴンズ": (0, 45, 114),
            "横浜DeNAベイスターズ": (0, 93, 170),
            "広島東洋カープ": (218, 0, 22),
            "東京ヤクルトスワローズ": (20, 60, 100),
            "オリックス・バファローズ": (0, 30, 70),
            "福岡ソフトバンクホークス": (255, 209, 0),
            "埼玉西武ライオンズ": (0, 45, 114),
            "東北楽天ゴールデンイーグルス": (133, 0, 37),
            "千葉ロッテマリーンズ": (0, 0, 0),
            "北海道日本ハムファイターズ": (0, 51, 102),
        }
    
    def get_team_color(self, team_name: str) -> Tuple[int, int, int]:
        return self.team_colors.get(team_name, Colors.PRIMARY)
    
    # ========================================
    # ペナントホーム画面
    # ========================================
    def draw_pennant_home(self, pennant: PennantManager, player_team: Team) -> Dict[str, Button]:
        """ペナントホーム画面"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        team_color = self.get_team_color(player_team.name)
        header_h = draw_header(self.screen, f"PENNANT MODE {pennant.current_year}",
                               f"{pennant.year_count}年目 / {pennant.max_years}年",
                               team_color)
        
        buttons = {}
        
        # 左パネル: 現在のフェーズ情報
        phase_card = Card(30, header_h + 20, 350, 180, "現在のフェーズ")
        phase_rect = phase_card.draw(self.screen)
        
        y = phase_rect.y + 55
        
        # フェーズ名
        phase_surf = fonts.h2.render(pennant.current_phase.value, True, team_color)
        self.screen.blit(phase_surf, (phase_rect.x + 25, y))
        y += 50
        
        # 年度進行バー
        progress = pennant.year_count / pennant.max_years
        bar = ProgressBar(phase_rect.x + 25, y, 300, 20, progress, team_color)
        bar.draw(self.screen)
        y += 35
        
        progress_text = f"{pennant.year_count}年目 / 最大{pennant.max_years}年"
        prog_surf = fonts.small.render(progress_text, True, Colors.TEXT_SECONDARY)
        self.screen.blit(prog_surf, (phase_rect.x + 25, y))
        
        # 左パネル: チーム財政
        if player_team.name in pennant.team_finances:
            finance = pennant.team_finances[player_team.name]
            
            finance_card = Card(30, header_h + 215, 350, 200, "FINANCE")
            fin_rect = finance_card.draw(self.screen)
            
            y = fin_rect.y + 55
            fin_items = [
                ("総予算", f"{finance.budget:.1f}億円"),
                ("年俸総額", f"{finance.payroll:.1f}億円"),
                ("利用可能", f"{finance.available_funds:.1f}億円"),
                ("ドラフト予算", f"{finance.draft_budget:.1f}億円"),
            ]
            
            for label, value in fin_items:
                label_surf = fonts.small.render(label, True, Colors.TEXT_SECONDARY)
                value_surf = fonts.small.render(value, True, Colors.TEXT_PRIMARY)
                self.screen.blit(label_surf, (fin_rect.x + 25, y))
                self.screen.blit(value_surf, (fin_rect.x + 180, y))
                y += 32
        
        # 中央: フェーズ別アクションボタン
        action_x = 410
        action_y = header_h + 40
        btn_width = 280
        btn_height = 60
        btn_spacing = 72
        
        phase = pennant.current_phase
        
        if phase == PennantPhase.SPRING_CAMP:
            action_buttons = [
                ("camp_training", "キャンプ開始", "primary"),
                ("camp_practice", "練習試合", "ghost"),
                ("camp_skip", "キャンプ終了", "success"),
            ]
        elif phase in [PennantPhase.REGULAR_SEASON, PennantPhase.INTERLEAGUE]:
            action_buttons = [
                ("play_game", "試合を行う", "success"),
                ("sim_week", "1週間シム", "ghost"),
                ("sim_month", "1ヶ月シム", "ghost"),
                ("roster", "ロースター", "ghost"),
            ]
        elif phase == PennantPhase.DRAFT:
            action_buttons = [
                ("draft_start", "ドラフト会議", "primary"),
                ("scout_report", "スカウト情報", "ghost"),
            ]
        elif phase == PennantPhase.FA_PERIOD:
            action_buttons = [
                ("fa_list", "FA選手一覧", "primary"),
                ("free_agents", "自由契約・解雇", "ghost"),
            ]
        elif phase == PennantPhase.OFF_SEASON:
            action_buttons = [
                ("trade", "トレード", "primary"),
                ("foreign", "外国人補強", "ghost"),
                ("release", "戦力外通告", "danger"),
            ]
        else:
            action_buttons = [
                ("next_phase", "次のフェーズへ", "primary"),
            ]
        
        for i, (name, text, style) in enumerate(action_buttons):
            btn = Button(action_x, action_y + i * btn_spacing, btn_width, btn_height, text, style, font=fonts.h3)
            btn.draw(self.screen)
            buttons[name] = btn
        
        # 右パネル: チーム状況
        status_card = Card(720, header_h + 20, 380, 420, f"{player_team.name}")
        status_rect = status_card.draw(self.screen)
        
        y = status_rect.y + 55
        
        # 成績
        record_text = f"{player_team.wins}勝{player_team.losses}敗{player_team.draws}分"
        record_surf = fonts.h3.render(record_text, True, team_color)
        self.screen.blit(record_surf, (status_rect.x + 25, y))
        y += 40
        
        win_rate = f"勝率 .{int(player_team.win_rate * 1000):03d}" if player_team.games_played > 0 else "勝率 .000"
        rate_surf = fonts.body.render(win_rate, True, Colors.TEXT_SECONDARY)
        self.screen.blit(rate_surf, (status_rect.x + 25, y))
        y += 40
        
        # 選手数
        pygame.draw.line(self.screen, Colors.BORDER, 
                        (status_rect.x + 20, y), (status_rect.x + status_rect.width - 40, y), 1)
        y += 15
        
        roster_text = f"支配下登録: {len(player_team.players)}/70人"
        roster_surf = fonts.body.render(roster_text, True, Colors.TEXT_PRIMARY)
        self.screen.blit(roster_surf, (status_rect.x + 25, y))
        y += 30
        
        # ポジション別内訳
        pitchers = len([p for p in player_team.players if p.position == Position.PITCHER])
        batters = len(player_team.players) - pitchers
        
        pos_text = f"投手: {pitchers}人 / 野手: {batters}人"
        pos_surf = fonts.small.render(pos_text, True, Colors.TEXT_SECONDARY)
        self.screen.blit(pos_surf, (status_rect.x + 25, y))
        y += 35
        
        # 故障者
        injured_count = sum(1 for p in player_team.players if id(p) in pennant.injuries)
        if injured_count > 0:
            injury_text = f"故障者: {injured_count}人"
            injury_surf = fonts.body.render(injury_text, True, Colors.DANGER)
            self.screen.blit(injury_surf, (status_rect.x + 25, y))
        y += 35
        
        # コーチ情報
        if player_team.name in pennant.team_coaches:
            coaches = pennant.team_coaches[player_team.name]
            manager = next((c for c in coaches if c.role == "監督"), None)
            if manager:
                coach_text = f"監督: {manager.name} (指導力: {manager.ability})"
                coach_surf = fonts.small.render(coach_text, True, Colors.TEXT_SECONDARY)
                self.screen.blit(coach_surf, (status_rect.x + 25, y))
        
        # ナビゲーションボタン
        buttons["menu"] = Button(50, height - 70, 150, 50, "MENU", "ghost", font=fonts.body)
        buttons["menu"].draw(self.screen)
        
        buttons["save"] = Button(width - 200, height - 70, 150, 50, "SAVE", "ghost", font=fonts.body)
        buttons["save"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # ドラフト会議画面
    # ========================================
    def draw_draft_screen(self, pennant: PennantManager, player_team: Team,
                          selected_indices: List[int], scroll_offset: int = 0) -> Dict[str, Button]:
        """ドラフト会議画面"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        header_h = draw_header(self.screen, "DRAFT", 
                               f"{pennant.current_year}年度 新人選手選択会議")
        
        buttons = {}
        
        # 左パネル: カテゴリフィルター
        filter_card = Card(30, header_h + 20, 200, 200, "カテゴリ")
        filter_rect = filter_card.draw(self.screen)
        
        y = filter_rect.y + 55
        categories = [("all", "全て"), ("high", "高校生"), ("college", "大学生"), ("corp", "社会人")]
        
        for name, label in categories:
            btn = Button(filter_rect.x + 15, y, 170, 35, label, "ghost", font=fonts.small)
            btn.draw(self.screen)
            buttons[f"filter_{name}"] = btn
            y += 42
        
        # 左パネル: 指名枠
        pick_card = Card(30, header_h + 235, 200, 200, "指名状況")
        pick_rect = pick_card.draw(self.screen)
        
        y = pick_rect.y + 55
        max_picks = 10
        current_picks = len(selected_indices)
        
        pick_text = f"指名: {current_picks}/{max_picks}人"
        pick_surf = fonts.body.render(pick_text, True, Colors.TEXT_PRIMARY)
        self.screen.blit(pick_surf, (pick_rect.x + 20, y))
        y += 35
        
        # 指名済み選手
        for i, idx in enumerate(selected_indices[:5]):
            if idx < len(pennant.draft_pool):
                player = pennant.draft_pool[idx]
                name_text = f"{i+1}. {player.name[:6]}"
                name_surf = fonts.small.render(name_text, True, Colors.TEXT_SECONDARY)
                self.screen.blit(name_surf, (pick_rect.x + 20, y))
                y += 25
        
        # メインパネル: 選手一覧
        list_card = Card(250, header_h + 20, width - 280, height - header_h - 100, "ドラフト候補選手")
        list_rect = list_card.draw(self.screen)
        
        # ヘッダー
        headers = [("順位", 40), ("名前", 120), ("カテゴリ", 80), ("ポジション", 80), 
                   ("年齢", 50), ("ポテンシャル", 90), ("所属", 120)]
        x = list_rect.x + 20
        y = list_rect.y + 50
        
        for text, w in headers:
            h_surf = fonts.tiny.render(text, True, Colors.TEXT_MUTED)
            self.screen.blit(h_surf, (x, y))
            x += w
        
        y += 25
        pygame.draw.line(self.screen, Colors.BORDER,
                        (list_rect.x + 15, y), (list_rect.right - 15, y), 1)
        y += 8
        
        # 選手一覧
        row_height = 35
        visible_count = (list_rect.height - 100) // row_height
        
        for i in range(scroll_offset, min(len(pennant.draft_pool), scroll_offset + visible_count)):
            player = pennant.draft_pool[i]
            
            row_rect = pygame.Rect(list_rect.x + 10, y - 3, list_rect.width - 20, row_height - 2)
            
            # 選択済みハイライト
            if i in selected_indices:
                pygame.draw.rect(self.screen, (*Colors.SUCCESS[:3], 60), row_rect, border_radius=4)
            elif i % 2 == 0:
                pygame.draw.rect(self.screen, Colors.BG_INPUT, row_rect, border_radius=2)
            
            x = list_rect.x + 20
            
            # 順位
            rank_surf = fonts.small.render(str(player.scouting_rank), True, Colors.TEXT_SECONDARY)
            self.screen.blit(rank_surf, (x, y))
            x += 40
            
            # 名前（転生選手は金色）
            name_color = Colors.GOLD if player.is_reincarnation else Colors.TEXT_PRIMARY
            name_surf = fonts.small.render(player.name[:8], True, name_color)
            self.screen.blit(name_surf, (x, y))
            x += 120
            
            # カテゴリ
            cat_surf = fonts.tiny.render(player.category.value[:3], True, Colors.TEXT_SECONDARY)
            self.screen.blit(cat_surf, (x, y + 2))
            x += 80
            
            # ポジション
            pos_text = player.position.value
            if player.pitch_type:
                pos_text = player.pitch_type.value
            pos_surf = fonts.tiny.render(pos_text[:4], True, Colors.TEXT_SECONDARY)
            self.screen.blit(pos_surf, (x, y + 2))
            x += 80
            
            # 年齢
            age_surf = fonts.small.render(str(player.age), True, Colors.TEXT_SECONDARY)
            self.screen.blit(age_surf, (x, y))
            x += 50
            
            # ポテンシャル
            pot_color = Colors.GOLD if player.potential >= 9 else Colors.TEXT_PRIMARY
            pot_surf = fonts.small.render(player.potential_grade, True, pot_color)
            self.screen.blit(pot_surf, (x, y))
            x += 90
            
            # 所屁E
            school_surf = fonts.tiny.render(player.school[:10], True, Colors.TEXT_MUTED)
            self.screen.blit(school_surf, (x, y + 2))
            
            y += row_height
        
        # ボタン
        buttons["back"] = Button(50, height - 70, 150, 50, "BACK", "ghost", font=fonts.body)
        buttons["back"].draw(self.screen)
        
        if len(selected_indices) > 0:
            buttons["confirm_draft"] = Button(width - 220, height - 70, 180, 50, 
                                              "指名確定", "success", font=fonts.body)
            buttons["confirm_draft"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # FA交渉画面
    # ========================================
    def draw_fa_negotiation(self, fa_player: FAPlayer, player_team: Team,
                            offer_salary: float, offer_years: int) -> Dict[str, Button]:
        """FA交渉画面"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        header_h = draw_header(self.screen, "FA NEGOTIATION", f"{fa_player.player.name} との交渉")
        
        buttons = {}
        
        # 選手情報カード
        player_card = Card(30, header_h + 20, 400, 350, "選手情報")
        p_rect = player_card.draw(self.screen)
        
        player = fa_player.player
        y = p_rect.y + 55
        
        info_items = [
            ("名前", player.name),
            ("年齢", f"{player.age}歳"),
            ("ポジション", player.position.value),
            ("前所属", fa_player.original_team),
            ("FAランク", fa_player.rank),
            ("現年俸", f"{player.salary:.1f}億円"),
        ]
        
        for label, value in info_items:
            label_surf = fonts.body.render(label, True, Colors.TEXT_SECONDARY)
            value_surf = fonts.body.render(str(value), True, Colors.TEXT_PRIMARY)
            self.screen.blit(label_surf, (p_rect.x + 25, y))
            self.screen.blit(value_surf, (p_rect.x + 150, y))
            y += 35
        
        # 要求条件
        y += 20
        demand_label = fonts.body.render("【希望条件】", True, Colors.WARNING)
        self.screen.blit(demand_label, (p_rect.x + 25, y))
        y += 30
        
        demands = fa_player.demands
        demand_items = [
            ("希望年俸", f"{demands.get('min_salary', 0):.1f}億円以上"),
            ("希望年数", f"{demands.get('min_years', 1)}年以上"),
        ]
        
        for label, value in demand_items:
            label_surf = fonts.small.render(label, True, Colors.TEXT_SECONDARY)
            value_surf = fonts.small.render(value, True, Colors.TEXT_PRIMARY)
            self.screen.blit(label_surf, (p_rect.x + 40, y))
            self.screen.blit(value_surf, (p_rect.x + 150, y))
            y += 28
        
        # オファーカード
        offer_card = Card(460, header_h + 20, 400, 300, "オファー内訳")
        o_rect = offer_card.draw(self.screen)
        
        y = o_rect.y + 60
        
        # 年俸スライダー（簡易版）
        salary_label = fonts.body.render("提示年俸", True, Colors.TEXT_PRIMARY)
        self.screen.blit(salary_label, (o_rect.x + 25, y))
        
        salary_value = fonts.h3.render(f"{offer_salary:.1f}億円", True, Colors.GOLD)
        self.screen.blit(salary_value, (o_rect.x + 200, y - 5))
        y += 50
        
        # 年俸調整ボタン
        buttons["salary_down"] = Button(o_rect.x + 25, y, 80, 40, "- 0.5億", "ghost", font=fonts.small)
        buttons["salary_down"].draw(self.screen)
        
        buttons["salary_up"] = Button(o_rect.x + 120, y, 80, 40, "+ 0.5億", "ghost", font=fonts.small)
        buttons["salary_up"].draw(self.screen)
        y += 60
        
        # 契約年数
        years_label = fonts.body.render("契約年数", True, Colors.TEXT_PRIMARY)
        self.screen.blit(years_label, (o_rect.x + 25, y))
        
        years_value = fonts.h3.render(f"{offer_years}年", True, Colors.ACCENT)
        self.screen.blit(years_value, (o_rect.x + 200, y - 5))
        y += 50
        
        # 年数調整ボタン
        buttons["years_down"] = Button(o_rect.x + 25, y, 80, 40, "- 1年", "ghost", font=fonts.small)
        buttons["years_down"].draw(self.screen)
        
        buttons["years_up"] = Button(o_rect.x + 120, y, 80, 40, "+ 1年", "ghost", font=fonts.small)
        buttons["years_up"].draw(self.screen)
        
        # 補償情報
        if fa_player.requires_compensation:
            comp_card = Card(460, header_h + 340, 400, 100, "人的補償")
            comp_rect = comp_card.draw(self.screen)
            
            comp_text = f"ランク{fa_player.rank}のため人的補償が必要です"
            comp_surf = fonts.small.render(comp_text, True, Colors.WARNING)
            self.screen.blit(comp_surf, (comp_rect.x + 25, comp_rect.y + 55))
        
        # ボタン
        buttons["back"] = Button(50, height - 70, 150, 50, "BACK", "ghost", font=fonts.body)
        buttons["back"].draw(self.screen)
        
        buttons["make_offer"] = Button(width - 220, height - 70, 180, 50, 
                                       "オファー提示", "primary", font=fonts.body)
        buttons["make_offer"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # トレード画面
    # ========================================
    def draw_trade_screen(self, pennant: PennantManager, player_team: Team,
                          target_team: Optional[Team], 
                          my_offers: List[Player], their_requests: List[Player],
                          cash_offer: float) -> Dict[str, Button]:
        """トレード画面"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        header_h = draw_header(self.screen, "TRADE", "選手交換交渉")
        
        buttons = {}
        
        # 左パネル: 自チーム選手
        my_card = Card(30, header_h + 20, 350, height - header_h - 100, f"OUT {player_team.name}")
        my_rect = my_card.draw(self.screen)
        
        y = my_rect.y + 55
        
        for i, player in enumerate(player_team.players[:15]):
            is_offered = player in my_offers
            
            row_rect = pygame.Rect(my_rect.x + 10, y - 3, my_rect.width - 20, 28)
            if is_offered:
                pygame.draw.rect(self.screen, (*Colors.SUCCESS[:3], 60), row_rect, border_radius=4)
            
            name_surf = fonts.small.render(player.name[:10], True, Colors.TEXT_PRIMARY)
            self.screen.blit(name_surf, (my_rect.x + 20, y))
            
            pos_surf = fonts.tiny.render(player.position.value[:3], True, Colors.TEXT_MUTED)
            self.screen.blit(pos_surf, (my_rect.x + 200, y + 2))
            
            y += 30
        
        # 中央: トレード条件
        center_x = width // 2 - 100
        
        trade_card = Card(center_x, header_h + 150, 200, 200, "トレード内容")
        t_rect = trade_card.draw(self.screen)
        
        y = t_rect.y + 55
        
        offer_text = f"提供: {len(my_offers)}人"
        offer_surf = fonts.body.render(offer_text, True, Colors.TEXT_PRIMARY)
        self.screen.blit(offer_surf, (t_rect.x + 20, y))
        y += 35
        
        request_text = f"獲得: {len(their_requests)}人"
        request_surf = fonts.body.render(request_text, True, Colors.TEXT_PRIMARY)
        self.screen.blit(request_surf, (t_rect.x + 20, y))
        y += 35
        
        cash_text = f"金銭: {cash_offer:.1f}億円"
        cash_surf = fonts.body.render(cash_text, True, Colors.GOLD)
        self.screen.blit(cash_surf, (t_rect.x + 20, y))
        
        # 右パネル: 相手チーム選手
        if target_team:
            their_card = Card(width - 380, header_h + 20, 350, height - header_h - 100, 
                             f"IN {target_team.name}")
            their_rect = their_card.draw(self.screen)
            
            y = their_rect.y + 55
            
            for i, player in enumerate(target_team.players[:15]):
                is_requested = player in their_requests
                
                row_rect = pygame.Rect(their_rect.x + 10, y - 3, their_rect.width - 20, 28)
                if is_requested:
                    pygame.draw.rect(self.screen, (*Colors.WARNING[:3], 60), row_rect, border_radius=4)
                
                name_surf = fonts.small.render(player.name[:10], True, Colors.TEXT_PRIMARY)
                self.screen.blit(name_surf, (their_rect.x + 20, y))
                
                pos_surf = fonts.tiny.render(player.position.value[:3], True, Colors.TEXT_MUTED)
                self.screen.blit(pos_surf, (their_rect.x + 200, y + 2))
                
                y += 30
        
        # チーム選択�Eタン
        buttons["select_team"] = Button(center_x, header_h + 50, 200, 45, 
                                        "相手チーム選択", "ghost", font=fonts.small)
        buttons["select_team"].draw(self.screen)
        
        # ボタン
        buttons["back"] = Button(50, height - 70, 150, 50, "BACK", "ghost", font=fonts.body)
        buttons["back"].draw(self.screen)
        
        if my_offers and their_requests:
            buttons["propose_trade"] = Button(width - 220, height - 70, 180, 50,
                                              "トレード提案", "primary", font=fonts.body)
            buttons["propose_trade"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # 春季キャンプ画面（モダン版）
    # ========================================
    def draw_spring_camp(self, pennant: PennantManager, player_team: Team,
                         camp_results: Optional[Dict] = None,
                         daily_result: Optional[Dict] = None,
                         training_menu: Optional[Dict] = None) -> Dict[str, Button]:
        """春季キャンプ画面（モダンUI）"""
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        # 背景
        self.screen.fill(Colors.BG_DARK)
        
        team_color = self.get_team_color(player_team.name)
        camp_state = pennant.spring_camp_state
        
        buttons = {}
        
        # ========================================
        # ヘッダー
        # ========================================
        # チームカラーのアクセントライン
        pygame.draw.rect(self.screen, team_color, (0, 0, width, 4))
        
        # タイトル
        title_surf = fonts.h1.render("SPRING CAMP", True, Colors.TEXT_PRIMARY)
        self.screen.blit(title_surf, (40, 25))
        
        # キャンプ情報
        if camp_state:
            location_text = f"{camp_state.camp_location} / {camp_state.weather} {camp_state.temperature}℃"
            loc_surf = fonts.body.render(location_text, True, Colors.TEXT_SECONDARY)
            self.screen.blit(loc_surf, (40, 65))
            
            # 日程
            day_text = f"Day {camp_state.current_day} / {camp_state.total_days}"
            day_surf = fonts.h2.render(day_text, True, team_color)
            day_rect = day_surf.get_rect(right=width - 40, centery=45)
            self.screen.blit(day_surf, day_rect)
            
            # 週
            week_text = f"Week {camp_state.week}"
            week_surf = fonts.body.render(week_text, True, Colors.TEXT_MUTED)
            week_rect = week_surf.get_rect(right=width - 40, centery=70)
            self.screen.blit(week_surf, week_rect)
        
        content_y = 100
        
        # ========================================
        # 左パネル: 進行状況 & ステータス
        # ========================================
        left_x = 30
        left_width = 320
        
        # 進行バー
        if camp_state:
            progress = camp_state.current_day / camp_state.total_days
            bar_bg = pygame.Rect(left_x, content_y, left_width, 12)
            draw_rounded_rect(self.screen, bar_bg, Colors.BG_INPUT, 6)
            
            bar_fg = pygame.Rect(left_x, content_y, int(left_width * progress), 12)
            if bar_fg.width > 0:
                draw_rounded_rect(self.screen, bar_fg, team_color, 6)
        
        # ステータスカード
        status_y = content_y + 30
        status_card = pygame.Rect(left_x, status_y, left_width, 200)
        draw_rounded_rect(self.screen, status_card, Colors.BG_CARD, 16)
        
        y = status_y + 20
        
        if camp_state:
            # 士気
            morale_label = fonts.small.render("MORALE", True, Colors.TEXT_MUTED)
            self.screen.blit(morale_label, (left_x + 20, y))
            
            morale_bar_bg = pygame.Rect(left_x + 20, y + 25, left_width - 40, 10)
            draw_rounded_rect(self.screen, morale_bar_bg, Colors.BG_INPUT, 5)
            
            morale_color = Colors.SUCCESS if camp_state.team_morale >= 60 else Colors.WARNING if camp_state.team_morale >= 40 else Colors.DANGER
            morale_bar = pygame.Rect(left_x + 20, y + 25, int((left_width - 40) * camp_state.team_morale / 100), 10)
            if morale_bar.width > 0:
                draw_rounded_rect(self.screen, morale_bar, morale_color, 5)
            
            morale_val = fonts.body.render(f"{camp_state.team_morale}%", True, morale_color)
            morale_rect = morale_val.get_rect(right=left_x + left_width - 20, centery=y + 12)
            self.screen.blit(morale_val, morale_rect)
            
            y += 55
            
            # 疲労
            fatigue_label = fonts.small.render("FATIGUE", True, Colors.TEXT_MUTED)
            self.screen.blit(fatigue_label, (left_x + 20, y))
            
            fatigue_bar_bg = pygame.Rect(left_x + 20, y + 25, left_width - 40, 10)
            draw_rounded_rect(self.screen, fatigue_bar_bg, Colors.BG_INPUT, 5)
            
            fatigue_color = Colors.DANGER if camp_state.team_fatigue >= 60 else Colors.WARNING if camp_state.team_fatigue >= 40 else Colors.SUCCESS
            fatigue_bar = pygame.Rect(left_x + 20, y + 25, int((left_width - 40) * camp_state.team_fatigue / 100), 10)
            if fatigue_bar.width > 0:
                draw_rounded_rect(self.screen, fatigue_bar, fatigue_color, 5)
            
            fatigue_val = fonts.body.render(f"{camp_state.team_fatigue}%", True, fatigue_color)
            fatigue_rect = fatigue_val.get_rect(right=left_x + left_width - 20, centery=y + 12)
            self.screen.blit(fatigue_val, fatigue_rect)
            
            y += 55
            
            # 統計
            stats_items = [
                ("練習試合", f"{camp_state.intrasquad_games}回"),
                ("オープン戦", f"{camp_state.practice_wins}勝{camp_state.practice_games - camp_state.practice_wins}敗"),
            ]
            
            for label, value in stats_items:
                label_surf = fonts.small.render(label, True, Colors.TEXT_SECONDARY)
                self.screen.blit(label_surf, (left_x + 20, y))
                value_surf = fonts.body.render(value, True, Colors.TEXT_PRIMARY)
                value_rect = value_surf.get_rect(right=left_x + left_width - 20, centery=y + 8)
                self.screen.blit(value_surf, value_rect)
                y += 30
        
        # ========================================
        # 中央: トレーニング配分スライダー
        # ========================================
        center_x = left_x + left_width + 25
        center_width = 380
        
        training_card = pygame.Rect(center_x, content_y, center_width, 300)
        draw_rounded_rect(self.screen, training_card, Colors.BG_CARD, 16)
        
        training_title = fonts.body.render("TRAINING FOCUS", True, Colors.TEXT_MUTED)
        self.screen.blit(training_title, (center_x + 20, content_y + 15))
        
        if camp_state:
            current_menu = {
                "batting": camp_state.batting_focus,
                "pitching": camp_state.pitching_focus,
                "fielding": camp_state.fielding_focus,
                "conditioning": camp_state.conditioning_focus,
            }
        else:
            current_menu = {"batting": 25, "pitching": 25, "fielding": 25, "conditioning": 25}
        
        y = content_y + 55
        
        training_items = [
            ("batting", "BATTING", Colors.DANGER),
            ("pitching", "PITCHING", Colors.PRIMARY),
            ("fielding", "FIELDING", Colors.SUCCESS),
            ("conditioning", "CONDITIONING", Colors.WARNING),
        ]
        
        for key, label, color in training_items:
            value = current_menu.get(key, 25)
            
            # ラベル
            label_surf = fonts.small.render(label, True, Colors.TEXT_SECONDARY)
            self.screen.blit(label_surf, (center_x + 20, y))
            
            # 値
            value_surf = fonts.body.render(f"{value}%", True, color)
            value_rect = value_surf.get_rect(right=center_x + center_width - 20, centery=y + 8)
            self.screen.blit(value_surf, value_rect)
            
            # バー
            bar_y = y + 28
            bar_bg = pygame.Rect(center_x + 20, bar_y, center_width - 40, 12)
            draw_rounded_rect(self.screen, bar_bg, Colors.BG_INPUT, 6)
            
            bar_fg = pygame.Rect(center_x + 20, bar_y, int((center_width - 40) * value / 100), 12)
            if bar_fg.width > 0:
                draw_rounded_rect(self.screen, bar_fg, color, 6)
            
            # 調整ボタン
            btn_y = y + 2
            minus_btn = Button(center_x + center_width - 100, btn_y, 30, 30, "-", "ghost", font=fonts.body)
            minus_btn.draw(self.screen)
            buttons[f"train_{key}_minus"] = minus_btn
            
            plus_btn = Button(center_x + center_width - 65, btn_y, 30, 30, "+", "ghost", font=fonts.body)
            plus_btn.draw(self.screen)
            buttons[f"train_{key}_plus"] = plus_btn
            
            y += 58
        
        # ========================================
        # 右パネル: アクションボタン
        # ========================================
        right_x = center_x + center_width + 25
        right_width = width - right_x - 30
        
        action_card = pygame.Rect(right_x, content_y, right_width, 300)
        draw_rounded_rect(self.screen, action_card, Colors.BG_CARD, 16)
        
        action_title = fonts.body.render("ACTIONS", True, Colors.TEXT_MUTED)
        self.screen.blit(action_title, (right_x + 20, content_y + 15))
        
        y = content_y + 55
        btn_width = right_width - 40
        btn_height = 50
        
        actions = [
            ("advance_day", "1日進める", "primary"),
            ("intrasquad", "練習試合", "ghost"),
            ("practice_game", "オープン戦", "ghost"),
            ("auto_camp", "自動進行", "outline"),
        ]
        
        for btn_key, btn_label, style in actions:
            btn = Button(right_x + 20, y, btn_width, btn_height, btn_label, style, font=fonts.body)
            btn.draw(self.screen)
            buttons[btn_key] = btn
            y += btn_height + 12
        
        # ========================================
        # 下部: 結果表示エリア
        # ========================================
        result_y = content_y + 320
        result_height = height - result_y - 80
        
        result_card = pygame.Rect(left_x, result_y, width - 60, result_height)
        draw_rounded_rect(self.screen, result_card, Colors.BG_CARD, 16)
        
        result_title = fonts.body.render("DAILY REPORT", True, Colors.TEXT_MUTED)
        self.screen.blit(result_title, (left_x + 20, result_y + 15))
        
        if daily_result:
            y = result_y + 50
            
            # 成長情報
            growth = daily_result.get("growth", [])
            if growth:
                growth_text = f"成長: {len(growth)}人の選手が成長しました"
                growth_surf = fonts.body.render(growth_text, True, Colors.SUCCESS)
                self.screen.blit(growth_surf, (left_x + 20, y))
                y += 30
                
                # 詳細�E�最大5人�E�E
                for g in growth[:5]:
                    if g and "player" in g and "changes" in g:
                        detail = f"  {g['player']}: {', '.join(g['changes'])}"
                        detail_surf = fonts.small.render(detail, True, Colors.TEXT_SECONDARY)
                        self.screen.blit(detail_surf, (left_x + 30, y))
                        y += 22
            
            # 怪我情報
            injuries = daily_result.get("injuries", [])
            if injuries:
                injury_text = f"怪我: {', '.join(injuries)}"
                injury_surf = fonts.body.render(injury_text, True, Colors.DANGER)
                self.screen.blit(injury_surf, (left_x + 20, y))
        else:
            # デフォルトメッセージ
            no_result = fonts.body.render("アクションを選択してキャンプを進めてください", True, Colors.TEXT_MUTED)
            self.screen.blit(no_result, (left_x + 20, result_y + 50))
        
        # ========================================
        # フッター: 戻るボタン
        # ========================================
        back_btn = Button(30, height - 65, 150, 50, "BACK", "ghost", font=fonts.body)
        back_btn.draw(self.screen)
        buttons["back"] = back_btn
        
        # キャンプ終了ボタン
        if camp_state and camp_state.current_day >= camp_state.total_days:
            end_btn = Button(width - 200, height - 65, 170, 50, "キャンプ終了", "success", font=fonts.body)
            end_btn.draw(self.screen)
            buttons["end_camp"] = end_btn
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons
    
    # ========================================
    # クライマックスシリーズ画面
    # ========================================
    def draw_climax_series(self, pennant: PennantManager, 
                           central_standings: List[Team],
                           pacific_standings: List[Team]) -> Dict[str, Button]:
        """クライマックスシリーズ画面"""
        draw_background(self.screen, "gradient")
        
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        header_h = draw_header(self.screen, "CLIMAX SERIES", f"{pennant.current_year}年")
        
        buttons = {}
        
        # セ・リーグ
        central_card = Card(30, header_h + 20, 400, 350, "セ・リーグ")
        c_rect = central_card.draw(self.screen)
        
        y = c_rect.y + 55
        
        # 1stステージ (2位vs 3位)
        stage1_label = fonts.body.render("【1stステージ】", True, Colors.TEXT_SECONDARY)
        self.screen.blit(stage1_label, (c_rect.x + 20, y))
        y += 30
        
        if len(central_standings) >= 3:
            match1 = f"{central_standings[1].name[:6]} vs {central_standings[2].name[:6]}"
            match1_surf = fonts.body.render(match1, True, Colors.TEXT_PRIMARY)
            self.screen.blit(match1_surf, (c_rect.x + 40, y))
        y += 50
        
        # ファイナルステージ (1位vs 1st勝者)
        final_label = fonts.body.render("【ファイナルステージ】", True, Colors.GOLD)
        self.screen.blit(final_label, (c_rect.x + 20, y))
        y += 30
        
        if len(central_standings) >= 1:
            final_text = f"{central_standings[0].name[:6]} vs 1st勝者"
            final_surf = fonts.body.render(final_text, True, Colors.TEXT_PRIMARY)
            self.screen.blit(final_surf, (c_rect.x + 40, y))
        
        # パ・リーグ
        pacific_card = Card(width - 430, header_h + 20, 400, 350, "パ・リーグ")
        p_rect = pacific_card.draw(self.screen)
        
        y = p_rect.y + 55
        
        stage1_label = fonts.body.render("【1stステージ】", True, Colors.TEXT_SECONDARY)
        self.screen.blit(stage1_label, (p_rect.x + 20, y))
        y += 30
        
        if len(pacific_standings) >= 3:
            match1 = f"{pacific_standings[1].name[:6]} vs {pacific_standings[2].name[:6]}"
            match1_surf = fonts.body.render(match1, True, Colors.TEXT_PRIMARY)
            self.screen.blit(match1_surf, (p_rect.x + 40, y))
        y += 50
        
        final_label = fonts.body.render("【ファイナルステージ】", True, Colors.GOLD)
        self.screen.blit(final_label, (p_rect.x + 20, y))
        y += 30
        
        if len(pacific_standings) >= 1:
            final_text = f"{pacific_standings[0].name[:6]} vs 1st勝者"
            final_surf = fonts.body.render(final_text, True, Colors.TEXT_PRIMARY)
            self.screen.blit(final_surf, (p_rect.x + 40, y))
        
        # 日本シリーズへ
        js_card = Card(width // 2 - 150, header_h + 400, 300, 100, "JAPAN SERIES")
        js_rect = js_card.draw(self.screen)
        
        js_text = "セ王者 vs パ王者"
        js_surf = fonts.h3.render(js_text, True, Colors.GOLD)
        self.screen.blit(js_surf, (js_rect.x + 60, js_rect.y + 55))
        
        # ボタン
        buttons["back"] = Button(50, height - 70, 150, 50, "BACK", "ghost", font=fonts.body)
        buttons["back"].draw(self.screen)
        
        buttons["start_cs"] = Button(width - 220, height - 70, 180, 50,
                                     "CS開始", "success", font=fonts.body)
        buttons["start_cs"].draw(self.screen)
        
        ToastManager.update_and_draw(self.screen)
        
        return buttons

