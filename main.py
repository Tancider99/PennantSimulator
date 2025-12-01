# -*- coding: utf-8 -*-
"""
NPBペナントシミュレーター - メインファイル（プロフェッショナル版）
洗練されたUIと安定したゲームプレイを実現
"""
import pygame
import sys
import random

from constants import *
from models import Team, League, GameStatus, Player
from team_generator import create_team
from ui_pro import fonts, Colors, Button, ToastManager
from screens import ScreenRenderer
from game_simulator import GameSimulator
from player_generator import create_draft_prospect, create_foreign_free_agent
from models import Position, PitchType, PlayerStatus
from game_state import GameStateManager, GameState, DifficultyLevel
from schedule_manager import ScheduleManager
from settings_manager import settings
from pennant_mode import PennantManager, PennantPhase
from pennant_screens import PennantScreens
from save_manager import SaveManager


class NPBGame:
    """NPBゲームメインクラス"""
    
    def __init__(self):
        pygame.init()
        
        # 画面設定
        self.settings = settings  # 設定オブジェクトへの参照
        screen_width, screen_height = settings.get_resolution()
        set_screen_size(screen_width, screen_height)
        
        if settings.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            actual_size = self.screen.get_size()
            set_screen_size(actual_size[0], actual_size[1])
        else:
            self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        
        pygame.display.set_caption("NPB プロ野球ペナントシミュレーター")
        
        # レンダラーと状態管理
        self.renderer = ScreenRenderer(self.screen)
        self.state_manager = GameStateManager()
        self.schedule_manager = None
        self.game_simulator = None
        
        # ペナントモード
        self.pennant_manager = None
        self.pennant_screens = PennantScreens(self.screen)
        self.pennant_draft_picks = []  # ドラフト指名リスト
        self.pennant_camp_results = None  # キャンプ結果
        self.camp_daily_result = None  # キャンプ1日の結果
        self.camp_training_menu = None  # トレーニングメニュー設定
        
        # UI状態
        self.buttons = {}
        self.scroll_offset = 0
        self.result_scroll = 0
        self.show_title_start_menu = False  # タイトル画面のスタートメニュー表示
        
        # 各画面のスクロール位置
        self.lineup_scroll = 0
        self.draft_scroll = 0
        self.ikusei_draft_scroll = 0
        self.fa_scroll = 0
        self.standings_scroll = 0
        self.player_detail_scroll = 0
        
        # チーム名編集用
        self.custom_team_names = {}  # {元の名前: カスタム名}
        self.editing_team_idx = -1
        self.team_name_input = ""
        
        # チーム選択画面用
        self.preview_team_name = None  # 選択中（プレビュー中）のチーム名
        self.team_preview_scroll = 0  # チーム詳細プレビューのスクロール
        
        # スケジュール選択用
        self.selected_game_idx = -1  # 選択した日程のインデックス
        
        # 育成システム用
        self.selected_training_player_idx = -1
        self.training_points = 100  # 初期育成ポイント
        
        # 設定タブとスクロール
        self.settings_tab = "display"
        self.settings_scroll = 0  # 設定画面のスクロール位置
        
        # ドラフト/FA用
        self.hover_draft_index = -1
        self.selected_fa_idx = -1  # 外国人FA選択
        
        # 育成ドラフト用
        self.developmental_prospects = []  # 育成ドラフト候補
        self.developmental_draft_round = 1
        self.developmental_draft_messages = []
        self.selected_developmental_idx = -1
        self.ikusei_draft_prospects = []  # 育成ドラフト候補（別名）
        self.selected_ikusei_draft_idx = -1
        
        # 選手詳細画面用
        self.detail_player = None  # 詳細表示中の選手
        self.selected_detail_player = None  # 詳細表示中の選手（別名）
        
        # ダブルクリック検出用
        self._last_click_time = 0
        self._last_click_pos = (0, 0)
        
        # オーダー画面用（ドラッグ&ドロップ）
        self.dragging_player_idx = -1
        self.drag_pos = None
        self.lineup_tab = "all"  # "all", "batters" or "pitchers"
        self.drop_zones = {}  # ドロップゾーン情報
        self.selected_lineup_slot = -1  # 選択中のラインアップスロット
        
        # ポジションドラッグ&ドロップ用
        self.dragging_position_slot = -1  # ドラッグ中の打順スロット（ポジション用）
        self.position_drag_pos = None  # ポジションドラッグの現在位置
        self.lineup_edit_mode = "player"  # "player" or "position" - 編集モード
        
        # 投手オーダー・ベンチ設定用
        self.pitcher_order_tab = "rotation"  # "rotation", "relief", "closer"
        self.selected_rotation_slot = -1  # 選択中のローテーションスロット
        self.selected_relief_slot = -1  # 選択中の中継ぎスロット
        self.bench_setting_tab = "batters"  # "batters" or "pitchers"
        self.pitcher_scroll = 0  # 投手リストスクロール
        self.bench_scroll = 0  # ベンチ設定スクロール
        
        # 経営画面用
        self.management_tab = "overview"
        
        # 記録画面用
        self.standings_tab = "standings"  # "standings", "batting", "pitching"
        
        # 新規ゲーム設定用
        self.new_game_setup_state = {"difficulty": "normal"}
        
        # ニュースリスト（メイン画面表示用）
        self.news_list = []  # 最近のニュース [{"date": "4/1", "text": "開幕戦勝利！"}, ...]
        
        # セーブ状態管理
        self.has_unsaved_changes = False  # 未保存の変更があるか
        self.show_confirm_dialog = False  # 確認ダイアログ表示中
        self.confirm_action = None  # 確認後に実行するアクション
        
        # ポジション重複警告
        self.show_lineup_conflict_warning = False
        self.lineup_conflict_message = ""
        
        # 試合中の戦略操作
        self.game_strategy_mode = None  # "pinch_hit", "pinch_run", "pitching_change" など
        self.strategy_candidates = []  # 交代候補選手リスト
        self.selected_strategy_idx = -1
    
    def _apply_game_preset(self, preset: str):
        """ゲームプリセットを適用"""
        rules = self.settings.game_rules
        
        if preset == "real_2024":
            # 2027年NPB公式ルール（セリーグDH導入）
            rules.central_dh = True
            rules.pacific_dh = True
            rules.interleague_dh = True
            rules.regular_season_games = 143
            rules.enable_interleague = True
            rules.enable_climax_series = True
            rules.enable_spring_camp = True
            rules.enable_allstar = True
            ToastManager.show("2027年NPB公式ルールを適用", "success")
        
        elif preset == "classic":
            # 従来ルール（セDHなし）
            rules.central_dh = False
            rules.pacific_dh = True
            rules.interleague_dh = True
            rules.regular_season_games = 143
            rules.enable_interleague = True
            rules.enable_climax_series = True
            rules.enable_spring_camp = True
            rules.enable_allstar = True
            ToastManager.show("クラシックルールを適用（セDHなし）", "success")
        
        elif preset == "short":
            # ショートシーズン
            rules.central_dh = True
            rules.pacific_dh = True
            rules.regular_season_games = 120
            rules.enable_interleague = False
            rules.enable_climax_series = False
            rules.enable_spring_camp = False
            rules.enable_allstar = False
            ToastManager.show("ショートシーズンを適用", "success")
        
        elif preset == "full":
            # フルシーズン
            rules.central_dh = True
            rules.pacific_dh = True
            rules.interleague_dh = True
            rules.regular_season_games = 143
            rules.enable_interleague = True
            rules.enable_climax_series = True
            rules.enable_spring_camp = True
            rules.enable_allstar = True
            ToastManager.show("フルシーズンを適用", "success")
    
    def add_news(self, text: str, date: str = None):
        """ニュースを追加（最大10件保持）"""
        if date is None:
            # 次の試合の日付または完了した試合の日付から取得
            if self.schedule_manager and self.state_manager.player_team:
                try:
                    next_game = self.schedule_manager.get_next_game_for_team(self.state_manager.player_team.name)
                    if next_game and next_game.date:
                        if hasattr(next_game.date, 'month'):
                            date = f"{next_game.date.month}/{next_game.date.day}"
                        else:
                            date = str(next_game.date)
                    else:
                        # 完了した試合から最新の日付を探す
                        team_schedule = self.schedule_manager.get_team_schedule(self.state_manager.player_team.name)
                        completed = [g for g in team_schedule if g.is_completed]
                        if completed and completed[-1].date:
                            last_date = completed[-1].date
                            if hasattr(last_date, 'month'):
                                date = f"{last_date.month}/{last_date.day}"
                            else:
                                date = str(last_date)
                        else:
                            date = "--"
                except Exception:
                    date = "--"
            else:
                date = "--"
        
        self.news_list.insert(0, {"date": date, "text": text})
        # 最大10件に制限
        if len(self.news_list) > 10:
            self.news_list = self.news_list[:10]
    
    def init_teams(self):
        """チームを初期化"""
        self.state_manager.central_teams = []
        self.state_manager.pacific_teams = []
        
        for team_name in NPB_CENTRAL_TEAMS:
            team = create_team(team_name, League.CENTRAL)
            self.state_manager.central_teams.append(team)
        
        for team_name in NPB_PACIFIC_TEAMS:
            team = create_team(team_name, League.PACIFIC)
            self.state_manager.pacific_teams.append(team)
        
        self.state_manager.all_teams = self.state_manager.central_teams + self.state_manager.pacific_teams
    
    def init_schedule(self):
        """スケジュールを初期化"""
        self.schedule_manager = ScheduleManager(self.state_manager.current_year)
        self.schedule_manager.generate_season_schedule(
            self.state_manager.central_teams,
            self.state_manager.pacific_teams
        )
    
    def check_lineup_position_conflicts(self) -> str:
        """ラインナップのポジション重複をチェックし、エラーメッセージを返す"""
        team = self.state_manager.player_team
        if not team or not team.current_lineup:
            return ""
        
        from models import Position
        
        # 各ポジションの選手カウント
        position_counts = {}
        lineup = team.current_lineup
        
        # lineup_positions を取得（独立したポジション管理）
        if hasattr(team, 'lineup_positions') and team.lineup_positions:
            lineup_positions = team.lineup_positions
        else:
            lineup_positions = None
        
        # ポジション別にカウント
        for i, player_idx in enumerate(lineup):
            if player_idx < 0 or player_idx >= len(team.players):
                continue
            
            # lineup_positions がある場合はそれを使用
            if lineup_positions and i < len(lineup_positions):
                pos = lineup_positions[i]
                # 短縮名を正式名に変換
                pos_map = {"捕": "捕手", "一": "一塁手", "二": "二塁手", "三": "三塁手",
                          "遊": "遊撃手", "左": "左翼手", "中": "中堅手", "右": "右翼手", "DH": "DH", "投": "投手"}
                pos = pos_map.get(pos, pos)
            else:
                # 選手の本来のポジションを使用
                player = team.players[player_idx]
                pos = player.position.value
            
            if pos == "DH":
                continue  # DHは重複OK
            if pos == "投手":
                continue  # 投手は打順に入らない（DH制）
            
            # 外野手は左中右を合計3人まで
            if pos in ["左翼手", "中堅手", "右翼手", "外野手"]:
                pos = "外野"
            
            if pos not in position_counts:
                position_counts[pos] = 0
            position_counts[pos] += 1
        
        # 重複チェック
        errors = []
        for pos, count in position_counts.items():
            if pos == "外野":
                if count > 3:
                    errors.append(f"外野手が{count}人います（最大3人）")
            else:
                if count > 1:
                    errors.append(f"{pos}が{count}人います")
        
        if errors:
            return "⚠ ポジション重複: " + ", ".join(errors)
        
        # 必須ポジションのチェック
        rules = self.settings.game_rules
        team_league = getattr(team, 'league', None)
        from models import League
        
        use_dh = True
        if team_league == League.CENTRAL:
            use_dh = rules.central_dh
        elif team_league == League.PACIFIC:
            use_dh = rules.pacific_dh
        
        required_positions = ["捕手", "一塁手", "二塁手", "三塁手", "遊撃手"]
        missing = []
        for pos in required_positions:
            if pos not in position_counts or position_counts[pos] == 0:
                missing.append(pos)
        
        if "外野" not in position_counts or position_counts.get("外野", 0) < 3:
            outfield_count = position_counts.get("外野", 0)
            missing.append(f"外野手（あと{3 - outfield_count}人必要）")
        
        if missing:
            return "⚠ 守備位置が不足: " + ", ".join(missing)
        
        return ""
    
    def auto_set_lineup(self):
        """自動でオーダーを設定"""
        self.auto_set_lineup_for_team(self.state_manager.player_team)
    
    def auto_set_lineup_for_team(self, team: Team):
        """指定チームの自動オーダー設定（ポジション考慮・DH対応）"""
        if not team:
            return
        
        from models import Position
        from settings_manager import settings
        
        # DH制の判定（リーグに応じて）
        is_pacific = hasattr(team, 'league') and team.league.value == "パシフィック"
        use_dh = (is_pacific and settings.game_rules.pacific_dh) or (not is_pacific and settings.game_rules.central_dh)
        
        # 支配下選手のみ（野手）
        batters = [p for p in team.players if not getattr(p, 'is_developmental', False) 
                   and p.position != Position.PITCHER]
        
        if len(batters) < 9:
            # 選手不足時は単純に上位9人
            batters.sort(key=lambda p: p.stats.overall_batting(), reverse=True)
            team.current_lineup = [team.players.index(b) for b in batters[:9]]
            return
        
        # ポジション別に最適選手を選ぶ
        lineup = []
        position_assignments = {}
        used_players = set()
        
        # DH制の場合は8ポジション + DH、そうでなければ8ポジション + 投手
        if use_dh:
            # 各ポジションに配置（捕手→内野→外野→DH）
            positions_order = [
                ("捕手", Position.CATCHER, 1),
                ("一塁手", Position.FIRST, 1),
                ("二塁手", Position.SECOND, 1),
                ("三塁手", Position.THIRD, 1),
                ("遊撃手", Position.SHORTSTOP, 1),
                ("外野手", Position.OUTFIELD, 3),
            ]
        else:
            # DH無しの場合は8ポジション（投手は9番）
            positions_order = [
                ("捕手", Position.CATCHER, 1),
                ("一塁手", Position.FIRST, 1),
                ("二塁手", Position.SECOND, 1),
                ("三塁手", Position.THIRD, 1),
                ("遊撃手", Position.SHORTSTOP, 1),
                ("外野手", Position.OUTFIELD, 3),
            ]
        
        # まず各本職ポジションに配置
        for pos_name, pos_enum, count in positions_order:
            candidates = [p for p in batters if p.position == pos_enum and team.players.index(p) not in used_players]
            candidates.sort(key=lambda p: p.stats.overall_batting(), reverse=True)
            
            for i in range(min(count, len(candidates))):
                player = candidates[i]
                player_idx = team.players.index(player)
                lineup.append(player_idx)
                used_players.add(player_idx)
                
                if pos_enum == Position.OUTFIELD:
                    outfield_pos = ["左翼手", "中堅手", "右翼手"][i % 3]
                    position_assignments[outfield_pos] = player_idx
                else:
                    position_assignments[pos_name] = player_idx
        
        # 8人に満たない場合、サブポジション対応選手を追加
        needed_positions = [pos for pos, _, _ in positions_order if pos not in position_assignments]
        
        # 不足ポジションを埋める（サブポジション考慮）
        while len(lineup) < 8 and len(used_players) < len(batters):
            remaining = [p for p in batters if team.players.index(p) not in used_players]
            if not remaining:
                break
            remaining.sort(key=lambda p: p.stats.overall_batting(), reverse=True)
            player = remaining[0]
            player_idx = team.players.index(player)
            lineup.append(player_idx)
            used_players.add(player_idx)
        
        # DHまたは9番目の野手を追加
        if use_dh:
            # DH: 打撃力が最も高い未使用選手
            dh_candidates = [p for p in batters if team.players.index(p) not in used_players]
            if dh_candidates:
                dh_candidates.sort(key=lambda p: p.stats.overall_batting(), reverse=True)
                dh_player = dh_candidates[0]
                dh_idx = team.players.index(dh_player)
                lineup.append(dh_idx)
                used_players.add(dh_idx)
                position_assignments["指名打者"] = dh_idx
        
        # 9人に満たない場合はさらに補充
        while len(lineup) < 9:
            remaining = [p for p in batters if team.players.index(p) not in used_players]
            if not remaining:
                break
            remaining.sort(key=lambda p: p.stats.overall_batting(), reverse=True)
            player = remaining[0]
            player_idx = team.players.index(player)
            lineup.append(player_idx)
            used_players.add(player_idx)
        
        # 打順を能力と役割で最適化
        if len(lineup) >= 9:
            lineup_players = [(idx, team.players[idx]) for idx in lineup]
            
            def get_batting_score(p, role):
                stats = p.stats
                if role == 1:  # 1番: 走力・ミート
                    return stats.contact * 1.5 + stats.run * 2 + stats.speed
                elif role == 2:  # 2番: ミート・繋ぎ
                    return stats.contact * 2 + stats.run + getattr(stats, 'clutch', 50)
                elif role == 3:  # 3番: 打率・長打
                    return stats.contact * 1.5 + stats.power * 1.5 + getattr(stats, 'clutch', 50)
                elif role == 4:  # 4番: 最強打者
                    return stats.power * 2 + stats.contact + getattr(stats, 'clutch', 50) * 1.5
                elif role == 5:  # 5番: 長打
                    return stats.power * 1.8 + stats.contact + getattr(stats, 'clutch', 50)
                else:  # 6-8番
                    return stats.overall_batting()
            
            final_lineup = [None] * 9
            remaining_players = list(lineup_players)
            
            # 4番から決定（最強打者）
            for role in [4, 3, 5, 1, 2, 6, 7, 8, 9]:
                if not remaining_players:
                    break
                best = max(remaining_players, key=lambda x: get_batting_score(x[1], role))
                final_lineup[role - 1] = best[0]
                remaining_players.remove(best)
            
            team.current_lineup = final_lineup
        else:
            team.current_lineup = lineup[:9]
        
        # position_assignmentsを設定
        if not hasattr(team, 'position_assignments'):
            team.position_assignments = {}
        team.position_assignments = position_assignments
        
        # lineup_positionsを設定（オーダー画面用）
        lineup_positions = []
        pos_short = {"捕手": "捕", "一塁手": "一", "二塁手": "二", "三塁手": "三", 
                     "遊撃手": "遊", "左翼手": "左", "中堅手": "中", "右翼手": "右", 
                     "指名打者": "DH", "外野手": "外"}
        
        for idx in team.current_lineup:
            if idx is None:
                lineup_positions.append("DH" if use_dh else "投")
                continue
            player = team.players[idx]
            # position_assignmentsから検索
            assigned_pos = None
            for pos_name, p_idx in position_assignments.items():
                if p_idx == idx:
                    assigned_pos = pos_short.get(pos_name, pos_name[:1])
                    break
            if assigned_pos:
                lineup_positions.append(assigned_pos)
            else:
                # ポジションから推測
                pos_val = player.position.value
                if pos_val == "外野手":
                    lineup_positions.append("外")
                else:
                    lineup_positions.append(pos_short.get(pos_val, pos_val[:1]))
        
        team.lineup_positions = lineup_positions
        
        # 先発投手を設定
        pitchers = [p for p in team.players if not getattr(p, 'is_developmental', False) 
                    and p.position == Position.PITCHER and p.pitch_type == PitchType.STARTER]
        if pitchers:
            pitchers.sort(key=lambda p: p.stats.overall_pitching(), reverse=True)
            team.starting_pitcher_idx = team.players.index(pitchers[0])
    
    def save_current_game(self):
        """現在のゲームをセーブ"""
        if not self.state_manager.player_team:
            ToastManager.show("セーブするデータがありません", "error")
            return
        
        try:
            from save_manager import SaveManager, create_save_data
            
            # SaveManagerインスタンスを作成
            save_mgr = SaveManager()
            
            # セーブデータを作成
            save_data = create_save_data(self)
            
            # スロット1に保存（自動セーブ）
            success = save_mgr.save_game(1, save_data)
            
            if success:
                ToastManager.show("ゲームをセーブしました", "success")
                self.has_unsaved_changes = False  # 未保存フラグをリセット
            else:
                ToastManager.show("セーブに失敗しました", "error")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Save error: {e}")
            ToastManager.show(f"セーブエラー: {str(e)[:30]}", "error")
    
    def load_saved_game(self):
        """セーブデータをロード"""
        try:
            from save_manager import SaveManager, load_save_data
            
            save_mgr = SaveManager()
            slots = save_mgr.get_save_slots()
            
            # スロット1にデータがあるか確認
            slot1 = slots[0] if slots else None
            if slot1 and slot1.get("exists"):
                save_data = save_mgr.load_game(1)
                if save_data:
                    success = load_save_data(self, save_data)
                    if success:
                        ToastManager.show("ゲームをロードしました", "success")
                        self.state_manager.change_state(GameState.MENU)
                    else:
                        ToastManager.show("ロードに失敗しました", "error")
                else:
                    ToastManager.show("セーブデータがありません", "warning")
            else:
                ToastManager.show("セーブデータがありません", "warning")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Load error: {e}")
            ToastManager.show(f"ロードエラー: {str(e)[:30]}", "error")
    
    def start_game(self):
        """試合開始"""
        if not self.state_manager.player_team:
            return
        
        # ポジション重複チェック
        position_error = self.check_lineup_position_conflicts()
        if position_error:
            self.show_lineup_conflict_warning = True
            self.lineup_conflict_message = position_error
            ToastManager.show(position_error, "error")
            return  # 試合開始をブロック
        
        next_game = self.schedule_manager.get_next_game_for_team(self.state_manager.player_team.name)
        if not next_game:
            # シーズン終了 -> ドラフトへ
            self.generate_draft_prospects()
            self.state_manager.change_state(GameState.DRAFT)
            return
        
        # オーダー未設定なら自動設定
        if len(self.state_manager.player_team.current_lineup) < 9 or self.state_manager.player_team.starting_pitcher_idx < 0:
            self.auto_set_lineup()
        
        # 対戦相手を決定
        is_home = next_game.home_team_name == self.state_manager.player_team.name
        opponent_name = next_game.away_team_name if is_home else next_game.home_team_name
        self.state_manager.current_opponent = next((t for t in self.state_manager.all_teams if t.name == opponent_name), None)
        
        if self.state_manager.current_opponent:
            self.auto_set_lineup_for_team(self.state_manager.current_opponent)
        
        self.state_manager.change_state(GameState.GAME)
    
    def generate_draft_prospects(self):
        """NPB式ドラフト候補を生成"""
        self.state_manager.draft_prospects = []
        
        # ドラフト状態を初期化
        self.draft_round = 1  # 現在の指名順位（1巡目、2巡目...）
        self.max_draft_rounds = 8  # 最大8巡
        self.draft_picks = {}  # チーム名 -> 獲得選手リスト
        self.draft_order = []  # 指名順（ウェーバー方式）
        self.draft_lottery_results = {}  # 1巡目のくじ引き結果
        self.draft_waiting_for_other_teams = False  # 他チームの指名待ち
        self.current_picking_team_idx = 0  # 現在指名中のチームインデックス
        self.draft_messages = []  # ドラフト中のメッセージログ
        
        # 投手候補（40人）
        for i in range(40):
            pitch_type = random.choice([PitchType.STARTER, PitchType.RELIEVER, PitchType.CLOSER])
            potential = random.choices([9, 8, 7, 6, 5, 4], weights=[2, 5, 10, 20, 30, 33])[0]
            prospect = create_draft_prospect(Position.PITCHER, pitch_type, potential)
            self.state_manager.draft_prospects.append(prospect)
        
        # 野手候補（60人）
        positions = [Position.CATCHER, Position.FIRST, Position.SECOND, Position.THIRD,
                    Position.SHORTSTOP, Position.OUTFIELD, Position.OUTFIELD]
        for i in range(60):
            position = random.choice(positions)
            potential = random.choices([9, 8, 7, 6, 5, 4], weights=[2, 5, 10, 20, 30, 33])[0]
            prospect = create_draft_prospect(position, None, potential)
            self.state_manager.draft_prospects.append(prospect)
        
        # ポテンシャル順にソート
        self.state_manager.draft_prospects.sort(key=lambda p: p.potential, reverse=True)
        
        # 指名順を設定（前シーズン下位チームから）
        all_teams = self.state_manager.all_teams[:]
        all_teams.sort(key=lambda t: t.winning_percentage)  # 勝率低い順
        self.draft_order = [t.name for t in all_teams]
        
        # 各チームの指名リストを初期化
        for team in self.state_manager.all_teams:
            self.draft_picks[team.name] = []
        
        # プレイヤーチームの指名順を探す
        player_team_name = self.state_manager.player_team.name
        self.player_draft_order_idx = self.draft_order.index(player_team_name)
        
        # プレイヤーの番までCPUチームが指名
        self._process_cpu_draft_picks()
    
    def _process_cpu_draft_picks(self):
        """CPUチームのドラフト指名を処理"""
        if not self.state_manager.draft_prospects:
            return
        
        player_team_name = self.state_manager.player_team.name
        
        # 現在の巡でプレイヤーの番が来るまでCPUが指名
        while True:
            if self.draft_round > self.max_draft_rounds:
                break
            
            current_team_name = self.draft_order[self.current_picking_team_idx]
            
            # プレイヤーチームの番が来たら終了
            if current_team_name == player_team_name:
                break
            
            # CPUチームが指名
            cpu_team = next((t for t in self.state_manager.all_teams if t.name == current_team_name), None)
            if cpu_team:
                self._cpu_draft_pick(cpu_team)
            
            # 次のチームへ
            self._advance_draft_turn()
    
    def _cpu_draft_pick(self, team):
        """CPUチームがドラフト指名"""
        if not self.state_manager.draft_prospects:
            return
        
        # チーム状況に応じて候補を選ぶ
        pitchers = [p for p in team.players if p.position == Position.PITCHER]
        catchers = [p for p in team.players if p.position == Position.CATCHER]
        
        need_pitcher = len(pitchers) < 15
        need_catcher = len(catchers) < 3
        
        best_prospect = None
        
        # 優先順位: ポテンシャルトップ10 → ポジション補強 → ベスト残り
        top_prospects = self.state_manager.draft_prospects[:10]
        
        if self.draft_round <= 2:
            # 上位巡は基本的にベスト候補
            best_prospect = self.state_manager.draft_prospects[0]
        else:
            # 下位巡はチーム状況考慮
            if need_pitcher:
                pitcher_prospects = [p for p in self.state_manager.draft_prospects if p.position == Position.PITCHER]
                if pitcher_prospects:
                    best_prospect = max(pitcher_prospects, key=lambda p: p.potential)
            elif need_catcher:
                catcher_prospects = [p for p in self.state_manager.draft_prospects if p.position == Position.CATCHER]
                if catcher_prospects:
                    best_prospect = max(catcher_prospects, key=lambda p: p.potential)
            
            if not best_prospect:
                best_prospect = self.state_manager.draft_prospects[0]
        
        # 指名完了
        self._complete_draft_pick_for_team(best_prospect, team)
        
        # メッセージ記録
        msg = f"【{self.draft_round}巡目】{team.name}: {best_prospect.name} ({best_prospect.position.value})"
        self.draft_messages.append(msg)
    
    def _advance_draft_turn(self):
        """ドラフト指名順を進める"""
        self.current_picking_team_idx += 1
        
        # 全チーム指名完了 → 次巡へ
        if self.current_picking_team_idx >= len(self.draft_order):
            self.draft_round += 1
            self.current_picking_team_idx = 0
            
            # 偶数巡は逆順（ウェーバー方式）
            if self.draft_round % 2 == 0:
                self.draft_order = self.draft_order[::-1]
    
    def draft_player(self):
        """NPB式ドラフト指名（1巡目はくじ引き対応）"""
        if self.state_manager.selected_draft_pick is None or self.state_manager.selected_draft_pick < 0:
            ToastManager.show("選手を選択してください", "warning")
            return
        
        if self.state_manager.selected_draft_pick >= len(self.state_manager.draft_prospects):
            return
        
        prospect = self.state_manager.draft_prospects[self.state_manager.selected_draft_pick]
        team = self.state_manager.player_team
        
        # 1巡目は競合の可能性（他チームも指名するか判定）
        if self.draft_round == 1:
            # 上位候補は競合しやすい
            competing_teams = []
            for other_team in self.state_manager.all_teams:
                if other_team.name == team.name:
                    continue
                # ポテンシャル高い選手は競合率高い
                compete_chance = prospect.potential * 8  # 最大72%
                if random.randint(1, 100) <= compete_chance:
                    competing_teams.append(other_team.name)
            
            if competing_teams:
                # くじ引き
                all_bidders = [team.name] + competing_teams
                winner = random.choice(all_bidders)
                
                if winner == team.name:
                    ToastManager.show(f"🎊 {len(competing_teams)}球団競合を制しました！", "success")
                    self._complete_draft_pick(prospect, team)
                    msg = f"【{self.draft_round}巡目】{team.name}: {prospect.name} ({len(competing_teams)}球団競合制す)"
                else:
                    ToastManager.show(f"😢 {len(competing_teams)}球団競合、{winner}が獲得", "warning")
                    # 他チームが獲得
                    winner_team = next((t for t in self.state_manager.all_teams if t.name == winner), None)
                    if winner_team:
                        self._complete_draft_pick_for_team(prospect, winner_team)
                    msg = f"【{self.draft_round}巡目】{winner}: {prospect.name} (競合制す)"
                    # プレイヤーは再選択が必要
                    self.draft_messages.append(msg)
                    ToastManager.show("再度指名してください", "info")
                    self.state_manager.selected_draft_pick = None
                    return
            else:
                # 単独指名
                self._complete_draft_pick(prospect, team)
                msg = f"【{self.draft_round}巡目】{team.name}: {prospect.name} ({prospect.position.value})"
        else:
            # 2巡目以降は単独指名
            self._complete_draft_pick(prospect, team)
            msg = f"【{self.draft_round}巡目】{team.name}: {prospect.name} ({prospect.position.value})"
        
        self.draft_messages.append(msg)
        self.state_manager.selected_draft_pick = None
        
        # 指名順を進める
        self._advance_draft_turn()
        
        # ドラフト終了判定
        if self.draft_round > self.max_draft_rounds or not self.state_manager.draft_prospects:
            self._finish_draft()
            return
        
        # 次のプレイヤーの番までCPU処理
        self._process_cpu_draft_picks()
        
        # ドラフト終了判定（CPU処理後）
        if self.draft_round > self.max_draft_rounds or not self.state_manager.draft_prospects:
            self._finish_draft()
    
    def _finish_draft(self):
        """ドラフト終了処理 → 育成ドラフトへ"""
        # プレイヤーチームの獲得選手を表示
        acquired = self.draft_picks.get(self.state_manager.player_team.name, [])
        if acquired:
            ToastManager.show(f"支配下ドラフト終了！ {len(acquired)}選手を獲得", "success")
        
        # 育成ドラフト候補を生成
        self.generate_developmental_prospects()
        self.state_manager.change_state(GameState.DEVELOPMENTAL_DRAFT)
    
    def generate_developmental_prospects(self):
        """育成ドラフト候補を生成"""
        self.developmental_prospects = []
        self.developmental_draft_round = 1
        self.developmental_draft_messages = []
        self.selected_developmental_idx = -1
        
        # 育成候補は支配下より能力は低いがポテンシャル高い選手も
        # 投手候補（30人）
        for i in range(30):
            pitch_type = random.choice([PitchType.STARTER, PitchType.RELIEVER, PitchType.CLOSER])
            # 育成はポテンシャル低めの選手が多い
            potential = random.choices([7, 6, 5, 4, 3, 2], weights=[5, 10, 20, 30, 25, 10])[0]
            prospect = create_draft_prospect(Position.PITCHER, pitch_type, potential)
            prospect.is_developmental = True
            self.developmental_prospects.append(prospect)
        
        # 野手候補（40人）
        positions = [Position.CATCHER, Position.FIRST, Position.SECOND, Position.THIRD,
                    Position.SHORTSTOP, Position.OUTFIELD, Position.OUTFIELD]
        for i in range(40):
            position = random.choice(positions)
            potential = random.choices([7, 6, 5, 4, 3, 2], weights=[5, 10, 20, 30, 25, 10])[0]
            prospect = create_draft_prospect(position, None, potential)
            prospect.is_developmental = True
            self.developmental_prospects.append(prospect)
        
        # ポテンシャル順にソート
        self.developmental_prospects.sort(key=lambda p: p.potential, reverse=True)
    
    def draft_developmental_player(self):
        """育成ドラフト指名"""
        if self.selected_developmental_idx < 0 or self.selected_developmental_idx >= len(self.developmental_prospects):
            ToastManager.show("選手を選択してください", "warning")
            return
        
        prospect = self.developmental_prospects[self.selected_developmental_idx]
        team = self.state_manager.player_team
        
        # 育成選手として登録
        player = Player(
            name=prospect.name,
            position=prospect.position,
            pitch_type=prospect.pitch_type,
            stats=prospect.stats,
            age=prospect.age,
            status=PlayerStatus.FARM,
            uniform_number=0,
            is_developmental=True,
            draft_round=100 + self.developmental_draft_round  # 育成は100+
        )
        
        # 背番号（育成は3桁）
        used_numbers = [p.uniform_number for p in team.players]
        for num in range(101, 200):
            if num not in used_numbers:
                player.uniform_number = num
                break
        
        team.players.append(player)
        
        # メッセージ
        msg = f"【育成{self.developmental_draft_round}位】{team.name}: {prospect.name}"
        self.developmental_draft_messages.append(msg)
        ToastManager.show(f"✨ 育成{self.developmental_draft_round}位 {prospect.name} を獲得！", "success")
        
        # リストから削除
        self.developmental_prospects.pop(self.selected_developmental_idx)
        self.selected_developmental_idx = -1
        self.developmental_draft_round += 1
        
        # 最大5人まで
        if self.developmental_draft_round > 5 or not self.developmental_prospects:
            self._finish_developmental_draft()
    
    def _finish_developmental_draft(self):
        """育成ドラフト終了処理"""
        dev_count = len([p for p in self.state_manager.player_team.players if p.is_developmental and p.draft_round >= 100])
        ToastManager.show(f"育成ドラフト終了！", "success")
        
        # 外国人FA画面へ
        self.generate_foreign_free_agents()
        self.state_manager.change_state(GameState.FREE_AGENT)
    
    def _complete_draft_pick(self, prospect, team):
        """ドラフト指名完了（プレイヤーチーム）"""
        self._complete_draft_pick_for_team(prospect, team)
        ToastManager.show(f"✨ {prospect.name} を獲得！", "success")
    
    def _complete_draft_pick_for_team(self, prospect, team):
        """ドラフト指名完了（任意チーム）"""
        player = Player(
            name=prospect.name,
            position=prospect.position,
            pitch_type=prospect.pitch_type,
            stats=prospect.stats,
            age=prospect.age,
            status=PlayerStatus.ACTIVE,
            uniform_number=0,
            draft_round=self.draft_round
        )
        
        # 空き背番号を探す
        used_numbers = [p.uniform_number for p in team.players]
        for num in range(1, 100):
            if num not in used_numbers:
                player.uniform_number = num
                break
        
        team.players.append(player)
        
        # ドラフトリストから削除
        if prospect in self.state_manager.draft_prospects:
            self.state_manager.draft_prospects.remove(prospect)
        
        # 指名記録
        if hasattr(self, 'draft_picks'):
            self.draft_picks[team.name].append(prospect.name)
    
    def generate_foreign_free_agents(self):
        """外国人FA選手を生成"""
        self.state_manager.foreign_free_agents = []
        self.selected_fa_idx = -1  # FA選択リセット
        
        for _ in range(5):
            pitch_type = random.choice([PitchType.STARTER, PitchType.RELIEVER, PitchType.CLOSER])
            player = create_foreign_free_agent(Position.PITCHER, pitch_type)
            self.state_manager.foreign_free_agents.append(player)
        
        positions = [Position.FIRST, Position.THIRD, Position.OUTFIELD]
        for _ in range(5):
            position = random.choice(positions)
            player = create_foreign_free_agent(position)
            self.state_manager.foreign_free_agents.append(player)
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # ウィンドウリサイズ
            if event.type == pygame.VIDEORESIZE:
                if not settings.fullscreen:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    set_screen_size(event.w, event.h)
                    self.renderer.screen = self.screen
            
            # キー入力
            if event.type == pygame.KEYDOWN:
                # チーム名編集中のテキスト入力
                if self.state_manager.current_state == GameState.TEAM_EDIT and self.editing_team_idx >= 0:
                    if event.key == pygame.K_BACKSPACE:
                        self.team_name_input = self.team_name_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        self._confirm_team_name_edit()
                    elif event.key == pygame.K_ESCAPE:
                        self._cancel_team_name_edit()
                    elif event.unicode and len(self.team_name_input) < 20:
                        self.team_name_input += event.unicode
                    continue  # テキスト入力中は他のキー処理をスキップ
                
                if event.key == pygame.K_F11:
                    settings.toggle_fullscreen()
                    if settings.fullscreen:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        actual_size = self.screen.get_size()
                        set_screen_size(actual_size[0], actual_size[1])
                    else:
                        width, height = settings.get_resolution()
                        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                    self.renderer.screen = self.screen
                
                if event.key == pygame.K_ESCAPE:
                    if self.state_manager.current_state != GameState.TITLE:
                        self.state_manager.change_state(GameState.MENU)
                
                # スクロール
                if self.state_manager.current_state in [GameState.LINEUP, GameState.SCHEDULE_VIEW, GameState.DRAFT]:
                    if event.key == pygame.K_UP:
                        self.scroll_offset = max(0, self.scroll_offset - 1)
                    elif event.key == pygame.K_DOWN:
                        self.scroll_offset += 1
                
                # 選手詳細画面でのスクロール
                if self.state_manager.current_state == GameState.PLAYER_DETAIL:
                    if event.key == pygame.K_UP:
                        self.player_detail_scroll = max(0, self.player_detail_scroll - 30)
                    elif event.key == pygame.K_DOWN:
                        self.player_detail_scroll += 30
                    elif event.key == pygame.K_ESCAPE:
                        # 前の画面に戻る
                        self.selected_detail_player = None
                        self.player_detail_scroll = 0
                        self.state_manager.change_state(GameState.LINEUP)
            
            # マウスホイール
            if event.type == pygame.MOUSEWHEEL:
                current_state = self.state_manager.current_state
                
                # 各画面ごとのスクロール処理（上限・下限を設定）
                if current_state == GameState.LINEUP:
                    # オーダー画面：選手リストのスクロール上限を計算
                    if self.state_manager.player_team:
                        if self.lineup_tab == "pitchers":
                            players = self.state_manager.player_team.get_active_pitchers()
                        elif self.lineup_tab == "batters":
                            players = self.state_manager.player_team.get_active_batters()
                        else:
                            players = [p for p in self.state_manager.player_team.players if not getattr(p, 'is_developmental', False)]
                        visible_count = 12  # 表示可能な行数
                        max_scroll = max(0, len(players) - visible_count)
                        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y))
                    else:
                        self.scroll_offset = max(0, self.scroll_offset - event.y)
                elif current_state == GameState.SCHEDULE_VIEW:
                    # スケジュール画面：試合数に基づく上限
                    if self.schedule_manager and self.state_manager.player_team:
                        games = self.schedule_manager.get_team_schedule(self.state_manager.player_team.name)
                        max_scroll = max(0, len(games) - 10)
                        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y * 3))
                    else:
                        self.scroll_offset = max(0, self.scroll_offset - event.y * 3)
                elif current_state == GameState.DRAFT:
                    max_scroll = max(0, len(self.state_manager.draft_prospects) - 12)
                    self.draft_scroll = max(0, min(max_scroll, self.draft_scroll - event.y))
                elif current_state in [GameState.IKUSEI_DRAFT, GameState.DEVELOPMENTAL_DRAFT]:
                    max_scroll = max(0, len(getattr(self, 'developmental_prospects', [])) - 12)
                    self.ikusei_draft_scroll = getattr(self, 'ikusei_draft_scroll', 0)
                    self.ikusei_draft_scroll = max(0, min(max_scroll, self.ikusei_draft_scroll - event.y))
                elif current_state == GameState.FREE_AGENT:
                    # FA画面：外国人FA選手数に基づく上限
                    fa_count = len(self.state_manager.foreign_free_agents) if self.state_manager.foreign_free_agents else 0
                    max_scroll = max(0, (fa_count - 8) * 30)
                    self.fa_scroll = max(0, min(max_scroll, self.fa_scroll - event.y * 30))
                elif current_state == GameState.STANDINGS:
                    # 記録画面：固定の上限（コンテンツ量に応じて）
                    max_scroll = 500  # 最大スクロール量
                    self.standings_scroll = max(0, min(max_scroll, self.standings_scroll - event.y * 30))
                elif current_state == GameState.PLAYER_DETAIL:
                    # 選手詳細画面：固定の上限
                    max_scroll = 400  # 最大スクロール量
                    self.player_detail_scroll = max(0, min(max_scroll, self.player_detail_scroll - event.y * 30))
                elif current_state == GameState.TEAM_SELECT:
                    # チーム選択画面のプレビュースクロール
                    max_scroll = 600  # 最大スクロール量
                    self.team_preview_scroll = max(0, min(max_scroll, self.team_preview_scroll - event.y * 30))
                elif current_state == GameState.SETTINGS:
                    # 設定画面のスクロール（ゲームルールタブのみ）
                    if self.settings_tab == "game_rules":
                        max_scroll = 400  # 最大スクロール量
                        self.settings_scroll = max(0, min(max_scroll, self.settings_scroll - event.y * 30))
                elif current_state == GameState.ROSTER_MANAGEMENT:
                    # 登録管理画面のスクロール
                    roster_tab = getattr(self, 'roster_tab', 'roster')
                    if roster_tab == 'roster':
                        players = [p for p in self.state_manager.player_team.players if not p.is_developmental]
                    else:
                        players = [p for p in self.state_manager.player_team.players if p.is_developmental]
                    max_scroll = max(0, len(players) - 12)
                    self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y))
            
            # マウスクリック
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # オーダー画面でのドラッグ開始または選手詳細表示
                if self.state_manager.current_state in [GameState.LINEUP, GameState.ROSTER_MANAGEMENT]:
                    # 右クリック相当（ダブルクリックで詳細を開く代替として、通常のクリック処理）
                    self.handle_lineup_drag_start(mouse_pos)
                
                # ドラフト画面での選手選択
                if self.state_manager.current_state == GameState.DRAFT:
                    self.handle_draft_click(mouse_pos)
                
                # 育成ドラフト画面での選手選択
                if self.state_manager.current_state in [GameState.IKUSEI_DRAFT, GameState.DEVELOPMENTAL_DRAFT]:
                    self.handle_ikusei_draft_click(mouse_pos)
                
                # FA画面での選手選択
                if self.state_manager.current_state == GameState.FREE_AGENT:
                    self.handle_fa_click(mouse_pos)
                
                # チーム選択画面
                if self.state_manager.current_state == GameState.TEAM_SELECT:
                    self.handle_team_select_click(mouse_pos)
                
                # 難易度選択画面
                if self.state_manager.current_state == GameState.DIFFICULTY_SELECT:
                    self.handle_difficulty_click(mouse_pos)
            
            # ダブルクリックで選手詳細画面へ
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self, '_last_click_time') and hasattr(self, '_last_click_pos'):
                    import time
                    current_time = time.time()
                    if current_time - self._last_click_time < 0.3:  # 300ms以内
                        dist = ((event.pos[0] - self._last_click_pos[0])**2 + 
                               (event.pos[1] - self._last_click_pos[1])**2)**0.5
                        if dist < 20:  # 近い位置
                            self.handle_double_click(event.pos)
                self._last_click_time = time.time() if 'time' in dir() else __import__('time').time()
                self._last_click_pos = event.pos
            
            # マウスドラッグ（移動）
            if event.type == pygame.MOUSEMOTION:
                if self.dragging_player_idx >= 0:
                    self.drag_pos = pygame.mouse.get_pos()
                if self.dragging_position_slot >= 0:
                    self.position_drag_pos = pygame.mouse.get_pos()
            
            # マウスリリース（ドロップ）
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging_player_idx >= 0:
                    self.handle_lineup_drop(pygame.mouse.get_pos())
                if self.dragging_position_slot >= 0:
                    self.handle_position_drop(pygame.mouse.get_pos())
            
            # ボタンイベント
            for button_name, button in self.buttons.items():
                # Buttonオブジェクトの場合のみ処理（Rectなどは無視）
                if hasattr(button, 'handle_event') and button.handle_event(event):
                    self.handle_button_click(button_name)
        
        return True
    
    def _confirm_team_name_edit(self):
        """チーム名編集を確定"""
        if self.editing_team_idx >= 0 and self.team_name_input.strip():
            team = self.state_manager.all_teams[self.editing_team_idx]
            self.custom_team_names[team.name] = self.team_name_input.strip()
            ToastManager.show(f"チーム名を変更: {self.team_name_input}", "success")
        self.editing_team_idx = -1
        self.team_name_input = ""
    
    def _cancel_team_name_edit(self):
        """チーム名編集をキャンセル"""
        self.editing_team_idx = -1
        self.team_name_input = ""
    
    def handle_draft_click(self, mouse_pos):
        """ドラフト画面のクリック処理（スクロール対応）"""
        # 選手リストの領域を計算（簡易版）
        header_h = 120
        card_y = header_h + 20 + 65  # カード上部 + ヘッダー行
        draft_scroll = getattr(self, 'draft_scroll', 0)
        
        for i in range(min(12, len(self.state_manager.draft_prospects) - draft_scroll)):
            actual_idx = i + draft_scroll
            row_y = card_y + i * 38
            row_rect = pygame.Rect(45, row_y - 5, self.screen.get_width() - 90, 34)
            
            if row_rect.collidepoint(mouse_pos):
                self.state_manager.selected_draft_pick = actual_idx
                return
    
    def handle_fa_click(self, mouse_pos):
        """FA画面のクリック処理"""
        # rendererのfa_row_rectsを使用
        if hasattr(self.renderer, 'fa_row_rects'):
            for i, rect in enumerate(self.renderer.fa_row_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_fa_idx = i
                    return
    
    def handle_double_click(self, mouse_pos):
        """ダブルクリックで選手詳細画面を開く"""
        current_state = self.state_manager.current_state
        
        if current_state == GameState.LINEUP:
            # オーダー画面の選手をクリック
            team = self.state_manager.player_team
            if team and team.players:
                # 行の高さとヘッダーからどの選手か計算
                header_h = 120
                row_h = 45
                y_offset = mouse_pos[1] - header_h - 70 + self.lineup_scroll
                if y_offset >= 0:
                    idx = int(y_offset / row_h)
                    if 0 <= idx < len(team.players):
                        self.selected_detail_player = team.players[idx]
                        self.player_detail_scroll = 0
                        self.state_manager.change_state(GameState.PLAYER_DETAIL)
                        return
        
        elif current_state == GameState.DRAFT:
            # ドラフト画面の候補選手をクリック
            if self.state_manager.draft_prospects:
                header_h = 120
                row_h = 42
                y_offset = mouse_pos[1] - header_h - 85 + self.draft_scroll
                if y_offset >= 0:
                    idx = int(y_offset / row_h)
                    if 0 <= idx < len(self.state_manager.draft_prospects):
                        prospect = self.state_manager.draft_prospects[idx]
                        # DraftProspectからPlayerを作成して表示
                        temp_player = Player(
                            name=prospect.name,
                            position=prospect.position,
                            age=prospect.age,
                            stats=prospect.potential_stats
                        )
                        self.selected_detail_player = temp_player
                        self.player_detail_scroll = 0
                        # 状態は変えずに詳細を表示（モーダル風）
                        ToastManager.show(f"{prospect.name}の詳細", "info")
                        return
    
    def handle_ikusei_draft_click(self, mouse_pos):
        """育成ドラフト画面のクリック処理（スクロール対応）"""
        header_h = 120
        row_h = 38  # draw_ikusei_draft_screenと一致
        card_y = header_h + 70 + 20 + 25 + 8  # カード開始位置 + パディング + ヘッダー + 区切り線
        ikusei_scroll = getattr(self, 'ikusei_draft_scroll', 0)
        
        for i in range(min(12, len(self.developmental_prospects) - ikusei_scroll)):
            actual_idx = i + ikusei_scroll
            row_y = card_y + i * row_h
            row_rect = pygame.Rect(40, row_y - 3, self.screen.get_width() - 400, 34)
            
            if row_rect.collidepoint(mouse_pos):
                self.selected_developmental_idx = actual_idx
                return
    
    def sign_fa_player(self):
        """外国人FA選手を獲得"""
        if self.selected_fa_idx < 0 or self.selected_fa_idx >= len(self.state_manager.foreign_free_agents):
            ToastManager.show("選手を選択してください", "warning")
            return
        
        player = self.state_manager.foreign_free_agents[self.selected_fa_idx]
        team = self.state_manager.player_team
        
        # 空き背番号を探す
        used_numbers = [p.uniform_number for p in team.players]
        for num in range(1, 100):
            if num not in used_numbers:
                player.uniform_number = num
                break
        
        # チームに追加
        team.players.append(player)
        
        # FAリストから削除
        self.state_manager.foreign_free_agents.pop(self.selected_fa_idx)
        self.selected_fa_idx = -1
        
        ToastManager.show(f"✨ {player.name} と契約！", "success")
    
    def start_new_season(self):
        """新シーズンを開始"""
        # シーズン番号を進める
        self.state_manager.current_year += 1
        
        # 全選手の年齢を+1、引退処理
        for team in self.state_manager.all_teams:
            retired_players = []
            for player in team.players:
                player.age += 1
                
                # 引退判定（38歳以上で確率）
                if player.age >= 38:
                    retire_chance = (player.age - 37) * 15  # 38歳15%, 39歳30%...
                    if random.randint(1, 100) <= retire_chance:
                        retired_players.append(player)
            
            # 引退選手を除外
            for retired in retired_players:
                if retired in team.players:
                    team.players.remove(retired)
            
            # チーム成績リセット
            team.wins = 0
            team.losses = 0
            team.draws = 0
        
        # スケジュール再生成
        self.init_schedule()
        
        # オーダーをリセット
        for team in self.state_manager.all_teams:
            team.current_lineup = []
            team.starting_pitcher_idx = -1
        
        # メニューへ
        ToastManager.show(f"🌸 {self.state_manager.current_year}年シーズン開幕！", "success")
        self.state_manager.change_state(GameState.MENU)
    
    def handle_team_select_click(self, mouse_pos):
        """チーム選択画面のクリック処理"""
        # ボタンのコールバックで処理される
        pass
    
    def handle_difficulty_click(self, mouse_pos):
        """難易度選択画面のクリック処理"""
        # カードクリックで難易度選択
        header_h = 120
        card_y = header_h + 60
        card_width = 220
        card_height = 200
        total_width = card_width * 4 + 30 * 3
        start_x = (self.screen.get_width() - total_width) // 2
        
        difficulties = [DifficultyLevel.EASY, DifficultyLevel.NORMAL, DifficultyLevel.HARD, DifficultyLevel.VERY_HARD]
        
        for i, level in enumerate(difficulties):
            x = start_x + i * (card_width + 30)
            card_rect = pygame.Rect(x, card_y, card_width, card_height)
            
            if card_rect.collidepoint(mouse_pos):
                self.state_manager.difficulty = level
                ToastManager.show(f"難易度: {level.value} を選択", "info")
                return
    
    def handle_button_click(self, button_name: str):
        """ボタンクリック処理"""
        # タイトル画面
        if button_name == "start":
            # スタートメニューを表示
            self.show_title_start_menu = True
        
        elif button_name == "back_to_title":
            # スタートメニューを閉じる
            self.show_title_start_menu = False
        
        elif button_name == "new_game":
            # 新規ゲーム設定画面へ遷移
            self.show_title_start_menu = False
            self.new_game_setup_state = {"difficulty": "normal"}
            self.state_manager.change_state(GameState.NEW_GAME_SETUP)
        
        elif button_name == "load_game":
            # ロード画面へ遷移（将来実装）
            self.show_title_start_menu = False
            self.load_saved_game()
        
        elif button_name == "return_to_title":
            # セーブしていない場合は確認ダイアログを表示
            if self.has_unsaved_changes:
                self.show_confirm_dialog = True
                self.confirm_action = "return_to_title"
            else:
                self.state_manager.change_state(GameState.TITLE)
                self.show_title_start_menu = False
        
        elif button_name == "confirm_yes":
            # 確認ダイアログでYES
            self.show_confirm_dialog = False
            if self.confirm_action == "return_to_title":
                self.state_manager.change_state(GameState.TITLE)
                self.show_title_start_menu = False
                self.has_unsaved_changes = False
            self.confirm_action = None
        
        elif button_name == "confirm_no":
            # 確認ダイアログでNO（キャンセル）
            self.show_confirm_dialog = False
            self.confirm_action = None
        
        elif button_name == "settings":
            self.state_manager.change_state(GameState.SETTINGS)
        
        elif button_name == "quit":
            pygame.quit()
            sys.exit()
        
        # === 新規ゲーム設定画面 ===
        elif button_name.startswith("diff_"):
            # 難易度選択
            diff = button_name.replace("diff_", "")
            self.new_game_setup_state["difficulty"] = diff
            diff_names = {"easy": "イージー", "normal": "ノーマル", "hard": "ハード"}
            ToastManager.show(f"難易度: {diff_names.get(diff, diff)}", "info")
        
        elif button_name.startswith("setup_toggle_"):
            # DH制・シーズンイベント切り替え
            key = button_name.replace("setup_toggle_", "")
            rules = self.settings.game_rules
            if hasattr(rules, key):
                current = getattr(rules, key)
                setattr(rules, key, not current)
                status = "ON" if not current else "OFF"
                ToastManager.show(f"{key} を {status} に変更", "info")
        
        elif button_name.startswith("setup_games_"):
            # 試合数設定
            games = int(button_name.replace("setup_games_", ""))
            self.settings.game_rules.regular_season_games = games
            ToastManager.show(f"シーズン {games}試合 に設定", "info")
        
        elif button_name.startswith("preset_"):
            # プリセット設定
            preset = button_name.replace("preset_", "")
            self._apply_game_preset(preset)
        
        elif button_name == "advanced_settings":
            # 詳細設定（既存の設定画面へ）
            self.settings_tab = "game_rules"
            self.state_manager.change_state(GameState.SETTINGS)
        
        elif button_name == "confirm_start":
            # ゲーム開始確定 → チーム選択へ
            self.init_teams()
            self.state_manager.change_state(GameState.TEAM_SELECT)
            ToastManager.show("チームを選択してください！", "success")
        
        # 難易度選択（互換性のため残す）
        elif button_name == "confirm" and self.state_manager.current_state == GameState.DIFFICULTY_SELECT:
            self.init_teams()
            self.state_manager.change_state(GameState.TEAM_SELECT)
        
        elif button_name == "back_title":
            self.state_manager.change_state(GameState.TITLE)
        
        # チーム名編集画面への遷移
        elif button_name == "edit_team_names":
            self.state_manager.change_state(GameState.TEAM_EDIT)
            self.editing_team_idx = -1
            self.team_name_input = ""
        
        # チーム編集画面のボタン
        elif button_name.startswith("edit_team_"):
            idx = int(button_name.replace("edit_team_", ""))
            self.editing_team_idx = idx
            team = self.state_manager.all_teams[idx]
            self.team_name_input = self.custom_team_names.get(team.name, "")
        
        elif button_name.startswith("confirm_edit_"):
            self._confirm_team_name_edit()
        
        elif button_name.startswith("cancel_edit_"):
            self._cancel_team_name_edit()
        
        elif button_name.startswith("reset_team_"):
            idx = int(button_name.replace("reset_team_", ""))
            team = self.state_manager.all_teams[idx]
            if team.name in self.custom_team_names:
                del self.custom_team_names[team.name]
                ToastManager.show("チーム名をリセットしました", "info")
        
        elif button_name == "back_to_select":
            self.state_manager.change_state(GameState.TEAM_SELECT)
            self.editing_team_idx = -1
            self.team_name_input = ""
        
        elif button_name == "apply_names":
            self.state_manager.change_state(GameState.TEAM_SELECT)
            ToastManager.show("チーム名を適用しました", "success")
        
        # チーム選択（プレビュー）
        elif button_name.startswith("team_"):
            team_name = button_name.replace("team_", "")
            # プレビュー用にチーム名を保持
            self.preview_team_name = team_name
            self.team_preview_scroll = 0  # スクロールリセット
            display_name = self.custom_team_names.get(team_name, team_name)
            ToastManager.show(f"{display_name} を選択中", "info")
        
        # チーム確定
        elif button_name == "confirm_team":
            if self.preview_team_name:
                for team in self.state_manager.all_teams:
                    if team.name == self.preview_team_name:
                        self.state_manager.player_team = team
                        self.init_schedule()
                        display_name = self.custom_team_names.get(self.preview_team_name, self.preview_team_name)
                        ToastManager.show(f"{display_name} で開始します！", "success")
                        self.preview_team_name = None
                        self.team_preview_scroll = 0
                        # 自動でペナントモード開始（春季キャンプから）
                        self.start_pennant_mode()
                        return
            else:
                ToastManager.show("チームを選択してください", "warning")
        
        # ========================================
        # メインメニュー（新項目）
        # ========================================
        # 試合メニュー
        elif button_name == "game_menu":
            self.start_game()
        
        # スケジュール
        elif button_name == "schedule":
            self.state_manager.change_state(GameState.SCHEDULE_VIEW)
            self.selected_game_idx = -1  # 選択リセット
            # 次の試合位置へスクロール
            if self.schedule_manager and self.state_manager.player_team:
                games = self.schedule_manager.get_team_schedule(self.state_manager.player_team.name)
                next_idx = next((i for i, g in enumerate(games) if not g.is_completed), 0)
                self.scroll_offset = max(0, next_idx - 3)
                self.selected_game_idx = next_idx  # デフォルトで次の試合を選択
            else:
                self.scroll_offset = 0
        
        # 日程選択
        elif button_name.startswith("select_game_"):
            idx = int(button_name.replace("select_game_", ""))
            self.selected_game_idx = idx
            ToastManager.show(f"第{idx + 1}戦を選択しました", "info")
        
        # 選択した日程までスキップ
        elif button_name == "skip_to_date":
            if self.selected_game_idx >= 0:
                self.simulate_all_games_until(self.selected_game_idx)
        
        # 育成画面
        elif button_name == "training":
            self.state_manager.change_state(GameState.TRAINING)
            self.selected_training_player_idx = -1
        
        # 育成: 選手選択
        elif button_name.startswith("select_player_"):
            idx = int(button_name.replace("select_player_", ""))
            self.selected_training_player_idx = idx
        
        # 育成: トレーニング実行
        elif button_name.startswith("train_"):
            self.execute_training(button_name)
        
        # 編成（新しい編成画面へ）
        elif button_name == "roster":
            self.roster_tab = "order"  # デフォルトをオーダータブに
            self.selected_roster_player_idx = -1
            self.scroll_offset = 0
            self.state_manager.change_state(GameState.ROSTER_MANAGEMENT)
        
        # 編成画面から選手詳細を表示
        elif button_name.startswith("player_detail_"):
            player_idx = int(button_name.replace("player_detail_", ""))
            if player_idx < len(self.state_manager.player_team.players):
                self.selected_detail_player = self.state_manager.player_team.players[player_idx]
                self.player_detail_scroll = 0
                self._previous_state = self.state_manager.current_state  # 戻り先を記憶
                self.state_manager.change_state(GameState.PLAYER_DETAIL)
        
        # 選手登録管理（旧ルートからも対応）
        elif button_name == "roster_management":
            self.roster_tab = "order"  # デフォルトをオーダータブに
            self.selected_roster_player_idx = -1
            self.scroll_offset = 0
            self.state_manager.change_state(GameState.ROSTER_MANAGEMENT)
        
        # 選手登録管理タブ切り替え
        elif button_name.startswith("tab_"):
            tab_name = button_name.replace("tab_", "")
            if tab_name in ["order", "players", "promote", "release", "foreign", "trade"]:
                self.roster_tab = tab_name
                self.scroll_offset = 0
        
        # ラインアップに選手追加
        elif button_name.startswith("add_lineup_"):
            player_idx = int(button_name.replace("add_lineup_", ""))
            self.add_player_to_lineup(player_idx)
        
        # ラインアップから選手削除
        elif button_name.startswith("remove_lineup_"):
            slot = int(button_name.replace("remove_lineup_", ""))
            self.remove_player_from_lineup(slot)
        
        # ポジション変更（守備位置をサイクル or スロット選択）
        elif button_name.startswith("change_pos_"):
            slot = int(button_name.replace("change_pos_", ""))
            # スロットを選択状態にする
            if self.selected_lineup_slot == slot:
                # 既に選択中なら守備位置をサイクル
                self.cycle_lineup_position(slot)
            else:
                # 選択状態にする
                self.selected_lineup_slot = slot
                ToastManager.show(f"{slot+1}番を選択中", "info")
        
        # クイックポジション選択（選択中のスロットに適用）
        elif button_name.startswith("quick_pos_"):
            pos = button_name.replace("quick_pos_", "")
            self.set_lineup_position_direct(pos)
        
        # 打順入れ替え（上へ）- 複数ボタン名に対応
        elif button_name.startswith("swap_up_") or button_name.startswith("lineup_swap_up_"):
            if button_name.startswith("lineup_swap_up_"):
                slot = int(button_name.replace("lineup_swap_up_", ""))
            else:
                slot = int(button_name.replace("swap_up_", ""))
            self.swap_lineup_order(slot, slot - 1)
        
        # 打順入れ替え（下へ）- 複数ボタン名に対応
        elif button_name.startswith("swap_down_") or button_name.startswith("lineup_swap_down_"):
            if button_name.startswith("lineup_swap_down_"):
                slot = int(button_name.replace("lineup_swap_down_", ""))
            else:
                slot = int(button_name.replace("swap_down_", ""))
            self.swap_lineup_order(slot, slot + 1)
        
        # ポジション入れ替え（上へ）
        elif button_name.startswith("pos_swap_up_"):
            slot = int(button_name.replace("pos_swap_up_", ""))
            self.swap_lineup_position(slot, slot - 1)
        
        # ポジション入れ替え（下へ）
        elif button_name.startswith("pos_swap_down_"):
            slot = int(button_name.replace("pos_swap_down_", ""))
            self.swap_lineup_position(slot, slot + 1)
        
        # 編集モード切り替え（選手 / ポジション）
        elif button_name == "edit_mode_player":
            self.lineup_edit_mode = "player"
            ToastManager.show("選手編集モード", "info")
        
        elif button_name == "edit_mode_position":
            self.lineup_edit_mode = "position"
            ToastManager.show("ポジション編集モード", "info")
        
        # ポジションドラッグ開始
        elif button_name.startswith("drag_position_"):
            slot = int(button_name.replace("drag_position_", ""))
            self.dragging_position_slot = slot
            self.position_drag_pos = pygame.mouse.get_pos()
        
        # オーダー最適化（能力順でソート）
        elif button_name == "optimize_lineup":
            self.optimize_lineup_by_stats()
        
        # ラインナップ全入れ替え（シャッフル）
        elif button_name == "shuffle_lineup":
            self.shuffle_lineup()
        
        # ラインナップ保存
        elif button_name == "save_lineup_preset":
            self.save_lineup_preset()
        
        # ラインナップ読み込み
        elif button_name == "load_lineup_preset":
            self.load_lineup_preset()
        
        # ========================================
        # 投手オーダー画面
        # ========================================
        elif button_name == "to_pitcher_order":
            self.pitcher_order_tab = "rotation"
            self.selected_rotation_slot = -1
            self.selected_relief_slot = -1
            self.pitcher_scroll = 0
            self.state_manager.change_state(GameState.PITCHER_ORDER)
        
        elif button_name == "tab_rotation":
            self.pitcher_order_tab = "rotation"
            self.pitcher_scroll = 0
        
        elif button_name == "tab_relief":
            self.pitcher_order_tab = "relief"
            self.pitcher_scroll = 0
        
        elif button_name == "tab_closer":
            self.pitcher_order_tab = "closer"
            self.pitcher_scroll = 0
        
        elif button_name.startswith("rotation_slot_"):
            slot = int(button_name.replace("rotation_slot_", ""))
            self.selected_rotation_slot = slot
            self.selected_relief_slot = -1
        
        elif button_name.startswith("relief_slot_"):
            slot = int(button_name.replace("relief_slot_", ""))
            self.selected_relief_slot = slot
            self.selected_rotation_slot = -1
        
        elif button_name == "closer_slot":
            self.selected_rotation_slot = -1
            self.selected_relief_slot = -1
        
        elif button_name.startswith("pitcher_") and not button_name.startswith("pitcher_scroll"):
            # 投手を選択してスロットに配置
            player_idx = int(button_name.replace("pitcher_", ""))
            team = self.state_manager.player_team
            if team:
                if self.pitcher_order_tab == "rotation" and self.selected_rotation_slot >= 0:
                    # ローテーションに追加
                    while len(team.rotation) <= self.selected_rotation_slot:
                        team.rotation.append(-1)
                    team.rotation[self.selected_rotation_slot] = player_idx
                    ToastManager.show(f"ローテーション{self.selected_rotation_slot+1}番手に設定", "success")
                    self.selected_rotation_slot = -1
                elif self.pitcher_order_tab == "relief" and self.selected_relief_slot >= 0:
                    # 中継ぎに追加
                    if player_idx not in team.bench_pitchers:
                        team.add_to_bench_pitchers(player_idx)
                    if player_idx not in team.setup_pitchers:
                        team.setup_pitchers.append(player_idx)
                    ToastManager.show("中継ぎ投手に追加", "success")
                    self.selected_relief_slot = -1
                elif self.pitcher_order_tab == "closer":
                    # 抑えに設定
                    team.closer_idx = player_idx
                    ToastManager.show("抑え投手に設定", "success")
        
        elif button_name == "pitcher_scroll_up":
            self.pitcher_scroll = max(0, self.pitcher_scroll - 1)
        
        elif button_name == "pitcher_scroll_down":
            self.pitcher_scroll += 1
        
        elif button_name == "pitcher_auto_set":
            team = self.state_manager.player_team
            if team:
                team.auto_set_pitching_staff()
                ToastManager.show("投手陣を自動設定しました", "success")
        
        elif button_name == "pitcher_back":
            self.state_manager.change_state(GameState.LINEUP)
        
        elif button_name == "to_bench_setting":
            self.bench_setting_tab = "batters"
            self.bench_scroll = 0
            self.state_manager.change_state(GameState.BENCH_SETTING)
        
        # ========================================
        # ベンチ設定画面
        # ========================================
        elif button_name == "bench_tab_batters":
            self.bench_setting_tab = "batters"
            self.bench_scroll = 0
        
        elif button_name == "bench_tab_pitchers":
            self.bench_setting_tab = "pitchers"
            self.bench_scroll = 0
        
        elif button_name.startswith("add_bench_"):
            player_idx = int(button_name.replace("add_bench_", ""))
            team = self.state_manager.player_team
            if team:
                if self.bench_setting_tab == "batters":
                    if team.add_to_bench_batters(player_idx):
                        ToastManager.show("野手をベンチに追加", "success")
                    else:
                        ToastManager.show("ベンチが満員です", "warning")
                else:
                    if team.add_to_bench_pitchers(player_idx):
                        ToastManager.show("投手をベンチに追加", "success")
                    else:
                        ToastManager.show("ベンチが満員です", "warning")
        
        elif button_name.startswith("remove_bench_batter_"):
            idx = int(button_name.replace("remove_bench_batter_", ""))
            team = self.state_manager.player_team
            if team and idx < len(team.bench_batters):
                player_idx = team.bench_batters[idx]
                team.remove_from_bench_batters(player_idx)
                ToastManager.show("ベンチから外しました", "info")
        
        elif button_name.startswith("remove_bench_pitcher_"):
            idx = int(button_name.replace("remove_bench_pitcher_", ""))
            team = self.state_manager.player_team
            if team and idx < len(team.bench_pitchers):
                player_idx = team.bench_pitchers[idx]
                team.remove_from_bench_pitchers(player_idx)
                ToastManager.show("ベンチから外しました", "info")
        
        elif button_name == "bench_scroll_up":
            self.bench_scroll = max(0, self.bench_scroll - 1)
        
        elif button_name == "bench_scroll_down":
            self.bench_scroll += 1
        
        elif button_name == "bench_auto_set":
            team = self.state_manager.player_team
            if team:
                team.auto_set_bench()
                ToastManager.show("ベンチを自動設定しました", "success")
        
        elif button_name == "bench_back":
            self.state_manager.change_state(GameState.PITCHER_ORDER)
        
        elif button_name == "to_lineup":
            self.state_manager.change_state(GameState.LINEUP)
        
        # 選手解雇
        elif button_name.startswith("release_"):
            player_idx = int(button_name.replace("release_", ""))
            self.release_player(player_idx)
        
        # 外国人FA市場を開く
        elif button_name == "open_foreign_fa":
            if len(self.state_manager.foreign_free_agents) == 0:
                self.generate_foreign_free_agents()
            self.state_manager.change_state(GameState.FREE_AGENT)
        
        # トレード市場を開く（未実装なのでToast）
        elif button_name == "open_trade_market":
            ToastManager.show("トレード機能は現在開発中です", "info")
        
        # 育成選手を支配下昇格
        elif button_name.startswith("promote_"):
            player_idx = int(button_name.replace("promote_", ""))
            self.promote_player_to_roster(player_idx)
        
        # 経営
        elif button_name == "management":
            self.management_tab = "overview"
            self.state_manager.change_state(GameState.MANAGEMENT)
        
        # 経営タブ切り替え
        elif button_name.startswith("mgmt_tab_"):
            self.management_tab = button_name.replace("mgmt_tab_", "")
        
        # 記録
        elif button_name == "records":
            self.standings_tab = "standings"
            self.state_manager.change_state(GameState.STANDINGS)
        
        # 記録画面タブ切り替え
        elif button_name.startswith("standings_tab_"):
            self.standings_tab = button_name.replace("standings_tab_", "")
        
        # 設定メニュー
        elif button_name == "settings_menu":
            self.state_manager.change_state(GameState.SETTINGS)
        
        # セーブ機能
        elif button_name == "save_game":
            self.save_current_game()
        
        # ========================================
        # 旧メニュー項目（互換性維持）
        # ========================================
        elif button_name == "lineup":
            self.state_manager.change_state(GameState.LINEUP)
            self.scroll_offset = 0
        
        elif button_name == "jump_next":
            # 次の試合へジャンプ
            if self.schedule_manager and self.state_manager.player_team:
                games = self.schedule_manager.get_team_schedule(self.state_manager.player_team.name)
                next_idx = next((i for i, g in enumerate(games) if not g.is_completed), 0)
                self.scroll_offset = max(0, next_idx - 3)
        
        elif button_name == "start_game":
            self.start_game()
        
        elif button_name == "standings":
            self.state_manager.change_state(GameState.STANDINGS)
        
        elif button_name == "free_agent":
            if len(self.state_manager.foreign_free_agents) == 0:
                self.generate_foreign_free_agents()
            self.state_manager.change_state(GameState.FREE_AGENT)
        
        elif button_name == "team_stats":
            self.state_manager.change_state(GameState.TEAM_STATS)
        
        # ========================================
        # ペナントモード
        # ========================================
        # 春季キャンプ
        elif button_name == "advance_day":
            self.advance_camp_day()
        
        elif button_name == "auto_camp":
            self.auto_camp()
        
        elif button_name == "intrasquad":
            self.execute_intrasquad_game()
        
        elif button_name == "practice_game":
            self.execute_practice_game()
        
        elif button_name.startswith("menu_"):
            # トレーニングメニュー変更 (menu_batting_3 など)
            parts = button_name.split("_")
            if len(parts) == 3:
                key = parts[1]
                value = int(parts[2])
                if self.camp_training_menu is None:
                    self.camp_training_menu = {"batting": 3, "pitching": 3, "fielding": 3, "physical": 3, "rest": 3}
                self.camp_training_menu[key] = value
        
        elif button_name == "camp_training" or button_name == "camp_skip":
            self.process_pennant_camp()
        
        elif button_name == "end_camp":
            # 春季キャンプ終了 → メニューに戻る（自動で試合開始しない）
            self.end_pennant_camp()
        
        elif button_name == "draft_start":
            self.pennant_manager.generate_draft_pool()
            self.pennant_draft_picks = []
            self.state_manager.change_state(GameState.PENNANT_DRAFT)
        
        elif button_name == "confirm_draft":
            self.complete_pennant_draft()
        
        elif button_name == "next_phase":
            self.pennant_manager.advance_phase()
            self.update_pennant_phase()
        
        elif button_name == "play_game":
            self.start_game()
        
        elif button_name == "sim_week":
            self.simulate_games(7)
        
        elif button_name == "sim_month":
            self.simulate_games(30)
        
        elif button_name == "menu":
            self.state_manager.change_state(GameState.MENU)
        
        # オーダー設定
        elif button_name == "auto_lineup":
            self.auto_set_lineup()
            ToastManager.show("オーダーを自動設定しました", "success")
        
        elif button_name == "clear_lineup":
            self.clear_lineup()
        
        # タブ切り替え（オーダー画面）
        elif button_name == "tab_all":
            self.lineup_tab = "all"
            self.scroll_offset = 0
        
        elif button_name == "tab_batters":
            self.lineup_tab = "batters"
            self.scroll_offset = 0
        
        elif button_name == "tab_pitchers":
            self.lineup_tab = "pitchers"
            self.scroll_offset = 0
        
        # ドラフト
        elif button_name == "draft_player":
            self.draft_player()
        
        # 育成ドラフト
        elif button_name == "draft_ikusei_player":
            self.draft_developmental_player()  # 既存の関数を使用
        
        elif button_name == "skip_ikusei":
            # この巡をパス
            ToastManager.show("この巡をパスしました", "info")
            self.developmental_draft_round += 1
            if self.developmental_draft_round > 5:
                self._finish_developmental_draft()
        
        elif button_name == "finish_ikusei_draft":
            # 育成ドラフト終了 → FAへ
            self._finish_developmental_draft()
        
        # 選手詳細画面の戻るボタン
        elif button_name == "back" and self.state_manager.current_state == GameState.PLAYER_DETAIL:
            self.selected_detail_player = None
            self.player_detail_scroll = 0
            # 前の画面に戻る
            previous = getattr(self, '_previous_state', GameState.LINEUP)
            self.state_manager.change_state(previous)
        
        # FA
        elif button_name == "sign_fa":
            self.sign_fa_player()
        
        elif button_name == "next_season":
            self.start_new_season()
        
        # 試合結果
        elif button_name == "next_game":
            self.result_scroll = 0  # スクロールリセット
            self.state_manager.change_state(GameState.MENU)
        
        # 試合結果画面スクロール
        elif button_name == "result_scroll_up":
            self.result_scroll = max(0, self.result_scroll - 3)
        
        elif button_name == "result_scroll_down":
            self.result_scroll += 3
        
        # 設定
        elif button_name.startswith("resolution_"):
            res_str = button_name.split("_")[1]
            width, height = map(int, res_str.split("x"))
            settings.set_resolution(width, height)
            set_screen_size(width, height)
            
            if not settings.fullscreen:
                self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                self.renderer.screen = self.screen
            
            ToastManager.show(f"解像度を {width}x{height} に変更", "info")
        
        elif button_name == "toggle_fullscreen":
            settings.toggle_fullscreen()
            if settings.fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                actual_size = self.screen.get_size()
                set_screen_size(actual_size[0], actual_size[1])
            else:
                width, height = settings.get_resolution()
                self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            self.renderer.screen = self.screen
        
        elif button_name == "toggle_sound":
            settings.toggle_sound()
            status = "ON" if settings.sound_enabled else "OFF"
            ToastManager.show(f"サウンド: {status}", "info")
        
        # ========================================
        # 試合中の戦略操作
        # ========================================
        elif button_name == "strategy_bunt":
            ToastManager.show("バント指示", "info")
            if self.game_simulator:
                self.game_simulator.next_tactic = "bunt"
        
        elif button_name == "strategy_squeeze":
            ToastManager.show("スクイズ指示", "info")
            if self.game_simulator:
                self.game_simulator.next_tactic = "squeeze"
        
        elif button_name == "strategy_steal":
            ToastManager.show("盗塁指示", "info")
            if self.game_simulator:
                self.game_simulator.next_tactic = "steal"
        
        elif button_name == "strategy_hit_run":
            ToastManager.show("エンドラン指示", "info")
            if self.game_simulator:
                self.game_simulator.next_tactic = "hit_and_run"
        
        elif button_name == "strategy_pinch_hit":
            # 代打選手候補を表示
            self.game_strategy_mode = "pinch_hit"
            self.strategy_candidates = self._get_pinch_hit_candidates()
            if not self.strategy_candidates:
                ToastManager.show("代打候補がいません", "warning")
                self.game_strategy_mode = None
        
        elif button_name == "strategy_pinch_run":
            # 代走選手候補を表示
            self.game_strategy_mode = "pinch_run"
            self.strategy_candidates = self._get_pinch_run_candidates()
            if not self.strategy_candidates:
                ToastManager.show("代走候補がいません", "warning")
                self.game_strategy_mode = None
        
        elif button_name == "strategy_intentional_walk":
            ToastManager.show("敬遠指示", "info")
            if self.game_simulator:
                self.game_simulator.next_tactic = "intentional_walk"
        
        elif button_name == "strategy_pitch_out":
            ToastManager.show("ピッチアウト指示", "info")
            if self.game_simulator:
                self.game_simulator.next_tactic = "pitch_out"
        
        elif button_name == "strategy_infield_in":
            ToastManager.show("前進守備指示", "info")
            if self.game_simulator:
                self.game_simulator.defensive_shift = "infield_in"
        
        elif button_name == "strategy_pitching_change":
            # 継投候補を表示
            self.game_strategy_mode = "pitching_change"
            self.strategy_candidates = self._get_relief_pitcher_candidates()
            if not self.strategy_candidates:
                ToastManager.show("継投候補がいません", "warning")
                self.game_strategy_mode = None
        
        elif button_name == "strategy_mound_visit":
            ToastManager.show("マウンド訪問（投手の疲労回復）", "info")
            if self.game_simulator:
                # 簡易的に球数リセット
                self.game_simulator.home_pitcher_stats['pitch_count'] = max(0, 
                    self.game_simulator.home_pitcher_stats.get('pitch_count', 0) - 10)
        
        elif button_name == "cancel_strategy":
            self.game_strategy_mode = None
            self.strategy_candidates = []
        
        elif button_name.startswith("select_candidate_"):
            idx = int(button_name.replace("select_candidate_", ""))
            if self.strategy_candidates and idx < len(self.strategy_candidates):
                self._execute_strategy_substitution(idx)
        
        elif button_name == "game_auto_play":
            # 自動再生（試合を高速進行）
            if self.game_simulator:
                self._run_game_simulation()
        
        elif button_name == "game_next_play":
            # 1プレイ進める
            ToastManager.show("次のプレイへ", "info")
            # 実際の実装では1打席分のシミュレーションを実行
        
        elif button_name in ["speed_slow", "speed_normal", "speed_fast"]:
            speed_map = {"speed_slow": 1, "speed_normal": 2, "speed_fast": 5}
            self.game_speed = speed_map.get(button_name, 1)
            ToastManager.show(f"速度: {self.game_speed}x", "info")
        
        # 設定タブ切り替え
        elif button_name.startswith("settings_tab_"):
            self.settings_tab = button_name.replace("settings_tab_", "")
            self.settings_scroll = 0  # タブ切り替え時にスクロールリセット
        
        # ゲームルール設定のトグル
        elif button_name.startswith("toggle_"):
            rule_key = button_name.replace("toggle_", "")
            if hasattr(settings.game_rules, rule_key):
                current_value = getattr(settings.game_rules, rule_key)
                setattr(settings.game_rules, rule_key, not current_value)
                settings.save_settings()
                status = "ON" if not current_value else "OFF"
                rule_names = {
                    "central_dh": "セリーグDH制",
                    "pacific_dh": "パリーグDH制",
                    "interleague_dh": "交流戦DH（ホームルール）",
                    "enable_interleague": "交流戦",
                    "enable_climax_series": "クライマックスシリーズ",
                    "enable_allstar": "オールスター",
                    "enable_spring_camp": "春季キャンプ",
                    "enable_tiebreaker": "タイブレーク制度",
                    "unlimited_foreign": "外国人枠無制限",
                }
                rule_name = rule_names.get(rule_key, rule_key)
                ToastManager.show(f"{rule_name}: {status}", "info")
        
        # ゲームルール設定の数値変更
        elif button_name.startswith("set_"):
            parts = button_name.split("_")
            # set_rule_key_value 形式
            value = int(parts[-1])
            key = "_".join(parts[1:-1])
            if hasattr(settings.game_rules, key):
                setattr(settings.game_rules, key, value)
                settings.save_settings()
                key_names = {
                    "regular_season_games": "レギュラーシーズン試合数",
                    "interleague_games": "交流戦試合数",
                    "extra_innings_limit": "延長上限",
                    "foreign_player_limit": "外国人枠",
                    "roster_limit": "一軍登録枠",
                    "farm_roster_limit": "育成枠上限",
                    "spring_camp_days": "キャンプ日数",
                }
                key_name = key_names.get(key, key)
                if value == 0:
                    if "foreign" in key or "farm" in key or "innings" in key:
                        display_value = "無制限"
                    else:
                        display_value = str(value)
                else:
                    display_value = str(value)
                ToastManager.show(f"{key_name}: {display_value}", "info")
        
        # 戻る
        elif button_name == "back":
            if self.state_manager.current_state == GameState.SETTINGS:
                # 設定画面からは前の画面に戻る（メニューかタイトル）
                if self.state_manager.previous_state and self.state_manager.previous_state != GameState.SETTINGS:
                    self.state_manager.change_state(self.state_manager.previous_state)
                elif self.state_manager.player_team:
                    self.state_manager.change_state(GameState.MENU)
                else:
                    self.state_manager.change_state(GameState.TITLE)
            elif self.state_manager.current_state == GameState.STANDINGS:
                self.state_manager.change_state(GameState.MENU)
            elif self.state_manager.current_state == GameState.DRAFT:
                # ドラフトを終了して育成ドラフトへ
                ToastManager.show("支配下ドラフト終了", "info")
                self.generate_developmental_prospects()
                self.state_manager.change_state(GameState.DEVELOPMENTAL_DRAFT)
            elif self.state_manager.current_state in [GameState.DEVELOPMENTAL_DRAFT, GameState.IKUSEI_DRAFT]:
                # 育成ドラフト終了 → FA画面へ
                ToastManager.show("育成ドラフト終了", "info")
                self.generate_foreign_free_agents()
                self.state_manager.change_state(GameState.FREE_AGENT)
            elif self.state_manager.current_state == GameState.ROSTER_MANAGEMENT:
                self.state_manager.change_state(GameState.MENU)
            else:
                self.state_manager.change_state(GameState.MENU)
        
        # 登録管理画面から選手詳細を表示
        elif button_name.startswith("roster_detail_"):
            player_idx = int(button_name.replace("roster_detail_", ""))
            if player_idx < len(self.state_manager.player_team.players):
                self.selected_detail_player = self.state_manager.player_team.players[player_idx]
                self.player_detail_scroll = 0
                self._previous_state = self.state_manager.current_state
                self.state_manager.change_state(GameState.PLAYER_DETAIL)
        
        # ドラフト画面から選手詳細を表示
        elif button_name.startswith("draft_detail_"):
            player_idx = int(button_name.replace("draft_detail_", ""))
            if player_idx < len(self.state_manager.draft_prospects):
                self.selected_detail_player = self.state_manager.draft_prospects[player_idx]
                self.player_detail_scroll = 0
                self._previous_state = self.state_manager.current_state
                self.state_manager.change_state(GameState.PLAYER_DETAIL)
        
        # 育成ドラフト画面から選手詳細を表示
        elif button_name.startswith("ikusei_detail_"):
            player_idx = int(button_name.replace("ikusei_detail_", ""))
            dev_prospects = getattr(self, 'developmental_prospects', [])
            if player_idx < len(dev_prospects):
                self.selected_detail_player = dev_prospects[player_idx]
                self.player_detail_scroll = 0
                self._previous_state = self.state_manager.current_state
                self.state_manager.change_state(GameState.PLAYER_DETAIL)
    
    def update(self):
        """ゲーム状態更新"""
        if self.state_manager.current_state == GameState.GAME and self.state_manager.current_opponent:
            # 試合シミュレーション
            pygame.time.wait(1500)
            
            next_game = self.schedule_manager.get_next_game_for_team(self.state_manager.player_team.name)
            if next_game:
                is_home = next_game.home_team_name == self.state_manager.player_team.name
                
                if is_home:
                    self.game_simulator = GameSimulator(self.state_manager.player_team, self.state_manager.current_opponent)
                else:
                    self.game_simulator = GameSimulator(self.state_manager.current_opponent, self.state_manager.player_team)
                
                self.game_simulator.simulate_game()
                
                self.schedule_manager.complete_game(next_game, self.game_simulator.home_score, self.game_simulator.away_score)
                
                # ニュースに試合結果を追加
                player_team = self.state_manager.player_team
                home_score = self.game_simulator.home_score
                away_score = self.game_simulator.away_score
                
                if is_home:
                    opponent_name = self.state_manager.current_opponent.name
                    if home_score > away_score:
                        self.add_news(f"vs {opponent_name} {home_score}-{away_score} 勝利！")
                    elif home_score < away_score:
                        self.add_news(f"vs {opponent_name} {home_score}-{away_score} 敗戦")
                    else:
                        self.add_news(f"vs {opponent_name} {home_score}-{away_score} 引き分け")
                else:
                    opponent_name = self.state_manager.current_opponent.name
                    if away_score > home_score:
                        self.add_news(f"@ {opponent_name} {away_score}-{home_score} 勝利！")
                    elif away_score < home_score:
                        self.add_news(f"@ {opponent_name} {away_score}-{home_score} 敗戦")
                    else:
                        self.add_news(f"@ {opponent_name} {away_score}-{home_score} 引き分け")
                
                # 未保存の変更フラグを立てる
                self.has_unsaved_changes = True
                
                self.state_manager.change_state(GameState.RESULT)
    
    def draw(self):
        """描画"""
        state = self.state_manager.current_state
        
        if state == GameState.TITLE:
            self.buttons = self.renderer.draw_title_screen(self.show_title_start_menu)
        
        elif state == GameState.NEW_GAME_SETUP:
            self.buttons = self.renderer.draw_new_game_setup_screen(
                self.settings,
                self.new_game_setup_state
            )
        
        elif state == GameState.SETTINGS:
            self.buttons = self.renderer.draw_settings_screen(settings, self.settings_tab, self.settings_scroll)
        
        elif state == GameState.DIFFICULTY_SELECT:
            self.buttons = self.renderer.draw_difficulty_screen(self.state_manager.difficulty)
        
        elif state == GameState.TEAM_SELECT:
            self.buttons = self.renderer.draw_team_select_screen(
                self.state_manager.central_teams,
                self.state_manager.pacific_teams,
                self.custom_team_names,
                self.preview_team_name,
                self.team_preview_scroll
            )
        
        elif state == GameState.TEAM_EDIT:
            self.buttons = self.renderer.draw_team_edit_screen(
                self.state_manager.all_teams,
                self.editing_team_idx,
                self.team_name_input,
                self.custom_team_names
            )
        
        elif state == GameState.MENU:
            self.buttons = self.renderer.draw_menu_screen(
                self.state_manager.player_team,
                self.state_manager.current_year,
                self.schedule_manager,
                self.news_list,
                self.state_manager.central_teams,
                self.state_manager.pacific_teams
            )
        
        elif state == GameState.LINEUP:
            # タブに応じたフィルタ指定
            if self.lineup_tab == "pitchers":
                selected_position = "pitcher"
            elif self.lineup_tab == "batters":
                selected_position = "batters"
            else:
                selected_position = "all"
            self.buttons = self.renderer.draw_lineup_screen(
                self.state_manager.player_team,
                self.scroll_offset,
                self.dragging_player_idx,
                self.drag_pos,
                selected_position,
                self.dragging_position_slot,
                self.position_drag_pos,
                self.lineup_edit_mode
            )
            # ドロップゾーン情報を保存
            if "_drop_zones" in self.buttons:
                self.drop_zones = self.buttons.pop("_drop_zones")
        
        elif state == GameState.PITCHER_ORDER:
            self.buttons = self.renderer.draw_pitcher_order_screen(
                self.state_manager.player_team,
                self.pitcher_order_tab,
                self.selected_rotation_slot,
                self.selected_relief_slot,
                self.pitcher_scroll
            )
        
        elif state == GameState.BENCH_SETTING:
            self.buttons = self.renderer.draw_bench_setting_screen(
                self.state_manager.player_team,
                self.bench_setting_tab,
                self.bench_scroll
            )
        
        elif state == GameState.SCHEDULE_VIEW:
            self.buttons = self.renderer.draw_schedule_screen(
                self.schedule_manager,
                self.state_manager.player_team,
                self.scroll_offset,
                self.selected_game_idx
            )
        
        elif state == GameState.GAME:
            # 試合状態を構築
            game_state = {}
            if self.game_simulator:
                game_state = {
                    'inning': self.game_simulator.inning,
                    'is_top': getattr(self.game_simulator, 'is_top_inning', True),
                    'outs': getattr(self.game_simulator, 'current_outs', 0),
                    'runners': getattr(self.game_simulator, 'current_runners', [False, False, False]),
                    'home_score': self.game_simulator.home_score,
                    'away_score': self.game_simulator.away_score,
                    'pitch_count': getattr(self.game_simulator, 'home_pitcher_stats', {}).get('pitch_count', 0),
                }
                # 現在の打者・投手
                if hasattr(self.game_simulator, 'current_batter_idx'):
                    batting_team = self.game_simulator.away_team if game_state['is_top'] else self.game_simulator.home_team
                    batter_idx = self.game_simulator.current_batter_idx
                    if 0 <= batter_idx < len(batting_team.current_lineup):
                        player_idx = batting_team.current_lineup[batter_idx]
                        if 0 <= player_idx < len(batting_team.players):
                            game_state['current_batter'] = batting_team.players[player_idx]
                
                if hasattr(self.game_simulator, 'current_pitcher_idx'):
                    pitching_team = self.game_simulator.home_team if game_state['is_top'] else self.game_simulator.away_team
                    pitcher_idx = self.game_simulator.current_pitcher_idx
                    if 0 <= pitcher_idx < len(pitching_team.players):
                        game_state['current_pitcher'] = pitching_team.players[pitcher_idx]
            
            self.buttons = self.renderer.draw_game_screen(
                self.state_manager.player_team,
                self.state_manager.current_opponent,
                game_state,
                self.game_strategy_mode,
                self.strategy_candidates
            )
        
        elif state == GameState.RESULT:
            self.buttons = self.renderer.draw_result_screen(
                self.game_simulator,
                self.result_scroll
            )
        
        elif state == GameState.STANDINGS:
            self.buttons = self.renderer.draw_standings_screen(
                self.state_manager.central_teams,
                self.state_manager.pacific_teams,
                self.state_manager.player_team,
                self.standings_tab,
                self.scroll_offset
            )
        
        elif state == GameState.DRAFT:
            draft_msgs = getattr(self, 'draft_messages', [])
            draft_rnd = getattr(self, 'draft_round', 1)
            draft_scroll = getattr(self, 'draft_scroll', 0)
            self.buttons = self.renderer.draw_draft_screen(
                self.state_manager.draft_prospects,
                self.state_manager.selected_draft_pick if self.state_manager.selected_draft_pick is not None else -1,
                draft_rnd,
                draft_msgs,
                draft_scroll
            )
        
        elif state == GameState.IKUSEI_DRAFT or state == GameState.DEVELOPMENTAL_DRAFT:
            # 育成ドラフト画面（2つのステート名を統一）
            dev_msgs = getattr(self, 'developmental_draft_messages', [])
            dev_rnd = getattr(self, 'developmental_draft_round', 1)
            ikusei_scroll = getattr(self, 'ikusei_draft_scroll', 0)
            self.buttons = self.renderer.draw_ikusei_draft_screen(
                self.developmental_prospects,
                self.selected_developmental_idx,
                dev_rnd,
                dev_msgs,
                ikusei_scroll
            )
        
        elif state == GameState.PLAYER_DETAIL:
            # 選手詳細画面
            player = self.selected_detail_player
            if player:
                self.buttons = self.renderer.draw_player_detail_screen(
                    player,
                    self.player_detail_scroll
                )
        
        elif state == GameState.FREE_AGENT:
            self.buttons = self.renderer.draw_free_agent_screen(
                self.state_manager.player_team,
                self.state_manager.foreign_free_agents,
                self.selected_fa_idx
            )
        
        elif state == GameState.TEAM_STATS:
            self.buttons = self.renderer.draw_team_stats_screen(
                self.state_manager.player_team,
                self.state_manager.current_year
            )
        
        elif state == GameState.TRAINING:
            self.buttons = self.renderer.draw_training_screen(
                self.state_manager.player_team,
                self.selected_training_player_idx,
                self.training_points
            )
        
        elif state == GameState.MANAGEMENT:
            # 財務情報を取得
            finances = None
            if self.pennant_manager and self.state_manager.player_team:
                finances = self.pennant_manager.team_finances.get(self.state_manager.player_team.name)
            self.buttons = self.renderer.draw_management_screen(
                self.state_manager.player_team,
                finances,
                self.management_tab
            )
        
        elif state == GameState.ROSTER_MANAGEMENT:
            self.buttons = self.renderer.draw_roster_management_screen(
                self.state_manager.player_team,
                getattr(self, 'roster_tab', 'roster'),
                self.selected_lineup_slot,  # 選択中のラインアップスロット
                self.scroll_offset,
                self.dragging_player_idx,
                self.drag_pos
            )
            # ドロップゾーン情報を保存
            if "_drop_zones" in self.buttons:
                self.drop_zones = self.buttons.pop("_drop_zones")
        
        # ペナントモード画面
        elif state == GameState.PENNANT_HOME:
            self.buttons = self.pennant_screens.draw_pennant_home(
                self.pennant_manager,
                self.state_manager.player_team
            )
        
        elif state == GameState.PENNANT_DRAFT:
            self.buttons = self.pennant_screens.draw_draft_screen(
                self.pennant_manager,
                self.state_manager.player_team,
                self.pennant_draft_picks,
                self.scroll_offset
            )
        
        elif state == GameState.PENNANT_CAMP:
            self.buttons = self.pennant_screens.draw_spring_camp(
                self.pennant_manager,
                self.state_manager.player_team,
                self.pennant_camp_results,
                self.camp_daily_result,
                self.camp_training_menu
            )
        
        elif state == GameState.PENNANT_CS:
            central_sorted = sorted(self.state_manager.central_teams, key=lambda t: (-t.win_rate, -t.wins))
            pacific_sorted = sorted(self.state_manager.pacific_teams, key=lambda t: (-t.win_rate, -t.wins))
            self.buttons = self.pennant_screens.draw_climax_series(
                self.pennant_manager,
                central_sorted,
                pacific_sorted
            )
        
        # 確認ダイアログを表示（セーブ確認など）
        if self.show_confirm_dialog:
            self._draw_confirm_dialog()
    
    def _draw_confirm_dialog(self):
        """確認ダイアログを描画"""
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        # 半透明オーバーレイ
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # ダイアログボックス
        dialog_w = 400
        dialog_h = 180
        dialog_x = (width - dialog_w) // 2
        dialog_y = (height - dialog_h) // 2
        
        from ui_pro import Colors, fonts, Button
        
        # ダイアログ背景
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(self.screen, Colors.BG_CARD, dialog_rect, border_radius=12)
        pygame.draw.rect(self.screen, Colors.WARNING, dialog_rect, 2, border_radius=12)
        
        # タイトル
        title_surf = fonts.h2.render("確認", True, Colors.WARNING)
        title_rect = title_surf.get_rect(centerx=width // 2, top=dialog_y + 20)
        self.screen.blit(title_surf, title_rect)
        
        # メッセージ
        msg_text = "セーブしていないデータがあります。"
        msg_surf = fonts.body.render(msg_text, True, Colors.TEXT_PRIMARY)
        msg_rect = msg_surf.get_rect(centerx=width // 2, top=dialog_y + 60)
        self.screen.blit(msg_surf, msg_rect)
        
        msg2_text = "タイトルに戻りますか？"
        msg2_surf = fonts.body.render(msg2_text, True, Colors.TEXT_SECONDARY)
        msg2_rect = msg2_surf.get_rect(centerx=width // 2, top=dialog_y + 85)
        self.screen.blit(msg2_surf, msg2_rect)
        
        # ボタン
        btn_y = dialog_y + 125
        yes_btn = Button(dialog_x + 60, btn_y, 120, 40, "はい", "danger", font=fonts.body)
        yes_btn.draw(self.screen)
        self.buttons["confirm_yes"] = yes_btn
        
        no_btn = Button(dialog_x + 220, btn_y, 120, 40, "いいえ", "outline", font=fonts.body)
        no_btn.draw(self.screen)
        self.buttons["confirm_no"] = no_btn
    
    # ========================================
    # ペナントモード メソッド
    # ========================================
    def start_pennant_mode(self):
        """ペナントモード開始（春季キャンプから）"""
        from settings_manager import settings
        
        self.pennant_manager = PennantManager(max_years=30)
        self.pennant_manager.initialize_pennant(
            self.state_manager.all_teams,
            self.state_manager.player_team
        )
        
        # 全チームの投手陣・ベンチを初期化
        for team in self.state_manager.all_teams:
            # 投手陣を自動設定
            team.auto_set_pitching_staff()
            # ベンチを自動設定
            if hasattr(team, 'auto_set_bench'):
                team.auto_set_bench()
        
        # キャンプ設定を確認
        if settings.game_rules.enable_spring_camp:
            # 春季キャンプフェーズから開始
            self.pennant_manager.current_phase = PennantPhase.SPRING_CAMP
            
            # キャンプを開始（設定から日数取得、チーム情報も渡す）
            camp_days = settings.game_rules.spring_camp_days
            self.pennant_manager.start_spring_camp(
                total_days=camp_days,
                team=self.state_manager.player_team
            )
            
            # キャンプ関連変数を初期化
            self.pennant_camp_results = None
            self.camp_daily_result = None
            self.camp_training_menu = {
                "batting": 3, "pitching": 3, "fielding": 3, "physical": 3, "rest": 3, "mental": 3
            }
            
            self.state_manager.change_state(GameState.PENNANT_CAMP)
            
            # キャンプ地情報を表示
            camp_state = self.pennant_manager.spring_camp_state
            camp_loc = camp_state.camp_location if camp_state else "沖縄"
            ToastManager.show(f"{self.state_manager.current_year}年 春季キャンプ開始！（{camp_loc}・{camp_days}日間）", "success")
        else:
            # キャンプをスキップしてメニューへ
            self.pennant_manager.current_phase = PennantPhase.REGULAR_SEASON
            self.state_manager.change_state(GameState.MENU)
            ToastManager.show(f"{self.state_manager.current_year}年 シーズン開始！", "success")
    
    def advance_camp_day(self):
        """キャンプを1日進める"""
        if not self.pennant_manager or not self.pennant_manager.spring_camp_state:
            return
        
        # トレーニングメニューを設定
        if self.camp_training_menu:
            self.pennant_manager.set_camp_training_menu(
                batting=self.camp_training_menu.get("batting", 3),
                pitching=self.camp_training_menu.get("pitching", 3),
                fielding=self.camp_training_menu.get("fielding", 3),
                physical=self.camp_training_menu.get("physical", 3),
                rest=self.camp_training_menu.get("rest", 3)
            )
        
        # 1日進める
        self.camp_daily_result = self.pennant_manager.advance_camp_day(
            self.state_manager.player_team
        )
        
        day = self.camp_daily_result.get("day", 0)
        growth_count = len(self.camp_daily_result.get("growth", {}))
        
        if growth_count > 0:
            ToastManager.show(f"Day{day}: {growth_count}人が成長！", "success")
        else:
            ToastManager.show(f"Day{day}: 練習終了", "info")
        
        # キャンプ終了判定
        camp = self.pennant_manager.spring_camp_state
        if camp and camp.current_day > camp.total_days:
            self.end_pennant_camp()
    
    def auto_camp(self):
        """キャンプを一括で進める"""
        if not self.pennant_manager or not self.pennant_manager.spring_camp_state:
            return
        
        camp = self.pennant_manager.spring_camp_state
        remaining = camp.total_days - camp.current_day + 1
        
        # トレーニングメニューを設定
        if self.camp_training_menu:
            self.pennant_manager.set_camp_training_menu(
                batting=self.camp_training_menu.get("batting", 3),
                pitching=self.camp_training_menu.get("pitching", 3),
                fielding=self.camp_training_menu.get("fielding", 3),
                physical=self.camp_training_menu.get("physical", 3),
                rest=self.camp_training_menu.get("rest", 3)
            )
        
        # 残りの日数を一括処理
        for _ in range(remaining):
            self.pennant_manager.advance_camp_day(self.state_manager.player_team)
        
        self.camp_daily_result = None  # 一括の場合は日次結果をクリア
        self.end_pennant_camp()
    
    def execute_intrasquad_game(self):
        """紅白戦を実行"""
        if not self.pennant_manager:
            return
        
        result = self.pennant_manager.execute_intrasquad_game(self.state_manager.player_team)
        mvp = result.get("mvp", "")
        ToastManager.show(f"紅白戦終了！ MVP: {mvp}", "success")
    
    def execute_practice_game(self):
        """オープン戦を実行"""
        if not self.pennant_manager:
            return
        
        # ランダムに対戦相手を選ぶ
        opponents = [t for t in self.state_manager.all_teams if t != self.state_manager.player_team]
        opponent = opponents[0] if opponents else None
        
        if opponent:
            result = self.pennant_manager.execute_practice_game(
                self.state_manager.player_team, opponent.name
            )
            score = result.get("score", "0-0")
            win_text = "勝利！" if result.get("win") else "敗北..."
            ToastManager.show(f"オープン戦 vs {opponent.name}: {score} {win_text}", "info")
    
    def end_pennant_camp(self):
        """キャンプを終了してシーズンへ"""
        if not self.pennant_manager:
            return
        
        summary = self.pennant_manager.end_spring_camp()
        self.pennant_camp_results = summary
        
        growth_count = len(summary.get("growth_results", {}))
        ToastManager.show(f"キャンプ終了！{growth_count}人が成長しました", "success")
        
        # フェーズを進める
        self.pennant_manager.advance_phase()
        self.state_manager.change_state(GameState.MENU)
    
    def process_pennant_camp(self):
        """春季キャンプ処理（簡易版 - 互換性のため残す）"""
        if not self.pennant_manager:
            return
        
        self.pennant_camp_results = self.pennant_manager.process_spring_camp(
            self.state_manager.player_team
        )
        self.state_manager.change_state(GameState.PENNANT_CAMP)
        
        # 成長した選手数をトースト表示
        growth_count = len(self.pennant_camp_results.get("growth", {}))
        ToastManager.show(f"キャンプ完了！{growth_count}人が成長", "success")
    
    def execute_training(self, training_type: str):
        """育成トレーニングを実行"""
        if not self.state_manager.player_team:
            return
        
        if self.selected_training_player_idx < 0:
            ToastManager.show("選手を選択してください", "warning")
            return
        
        players = self.state_manager.player_team.players
        if self.selected_training_player_idx >= len(players):
            return
        
        player = players[self.selected_training_player_idx]
        
        # トレーニングコストと効果を定義
        training_costs = {
            "train_velocity": 50,
            "train_control": 40,
            "train_breaking": 45,
            "train_stamina": 35,
            "train_contact": 40,
            "train_power": 50,
            "train_speed": 35,
            "train_defense": 40,
        }
        
        cost = training_costs.get(training_type, 50)
        
        if self.training_points < cost:
            ToastManager.show("育成ポイントが足りません", "warning")
            return
        
        # 能力値を上昇
        stat_name = ""
        if training_type == "train_velocity":
            player.stats.speed = min(20, player.stats.speed + 1)
            stat_name = "球速"
        elif training_type == "train_control":
            player.stats.control = min(20, player.stats.control + 1)
            stat_name = "制球"
        elif training_type == "train_breaking":
            player.stats.breaking = min(20, player.stats.breaking + 1)
            stat_name = "変化"
        elif training_type == "train_stamina":
            player.stats.stamina = min(20, player.stats.stamina + 1)
            stat_name = "スタミナ"
        elif training_type == "train_contact":
            player.stats.contact = min(20, player.stats.contact + 1)
            stat_name = "ミート"
        elif training_type == "train_power":
            player.stats.power = min(20, player.stats.power + 1)
            stat_name = "パワー"
        elif training_type == "train_speed":
            player.stats.run = min(20, player.stats.run + 1)
            stat_name = "走力"
        elif training_type == "train_defense":
            player.stats.fielding = min(20, player.stats.fielding + 1)
            stat_name = "守備"
        
        self.training_points -= cost
        ToastManager.show(f"{player.name}の{stat_name}が上昇！", "success")
    
    def handle_lineup_drag_start(self, mouse_pos):
        """オーダー画面でのドラッグ開始処理"""
        if not self.state_manager.player_team:
            return
        
        # ドロップゾーン情報から選手リストの領域をチェック
        if "_drop_zones" in self.buttons:
            drop_zones = self.buttons["_drop_zones"]
        else:
            drop_zones = self.drop_zones
        
        # 選手一覧のボタンをチェック
        for button_name, button in self.buttons.items():
            if button_name.startswith("drag_player_"):
                if hasattr(button, 'rect') and button.rect.collidepoint(mouse_pos):
                    player_idx = int(button_name.replace("drag_player_", ""))
                    self.dragging_player_idx = player_idx
                    self.drag_pos = mouse_pos
                    return
            # オーダータブの選手リストからのドラッグ
            elif button_name.startswith("add_lineup_"):
                if hasattr(button, 'rect') and button.rect.collidepoint(mouse_pos):
                    player_idx = int(button_name.replace("add_lineup_", ""))
                    self.dragging_player_idx = player_idx
                    self.drag_pos = mouse_pos
                    return
            # スタメンスロットからのドラッグ
            elif button_name.startswith("lineup_slot_"):
                if hasattr(button, 'rect') and button.rect.collidepoint(mouse_pos):
                    slot_idx = int(button_name.replace("lineup_slot_", ""))
                    lineup = self.state_manager.player_team.current_lineup or []
                    if slot_idx < len(lineup) and lineup[slot_idx] is not None and lineup[slot_idx] >= 0:
                        self.dragging_player_idx = lineup[slot_idx]
                        self.drag_pos = mouse_pos
                        return
        
        # 打順スロットからのドラッグ（既存の選手を移動）
        lineup = self.state_manager.player_team.current_lineup or []
        for key, rect in drop_zones.items():
            if isinstance(rect, pygame.Rect) and rect.collidepoint(mouse_pos):
                if key.startswith("order_"):
                    order_idx = int(key.replace("order_", ""))
                    if order_idx < len(lineup):
                        self.dragging_player_idx = lineup[order_idx]
                        self.drag_pos = mouse_pos
                        return
    
    def handle_lineup_drop(self, mouse_pos):
        """オーダー画面でのドロップ処理"""
        if self.dragging_player_idx < 0 or not self.state_manager.player_team:
            self.dragging_player_idx = -1
            self.drag_pos = None
            return
        
        team = self.state_manager.player_team
        player = team.players[self.dragging_player_idx]
        
        # ドロップゾーンを取得
        if "_drop_zones" in self.buttons:
            drop_zones = self.buttons["_drop_zones"]
        else:
            drop_zones = self.drop_zones
        
        # ラインナップの初期化
        if not team.current_lineup:
            team.current_lineup = []
        
        # どのドロップゾーンに落としたか判定
        dropped = False
        
        for key, rect in drop_zones.items():
            if not isinstance(rect, pygame.Rect):
                continue
            if not rect.collidepoint(mouse_pos):
                continue
            
            # 打順スロットへのドロップ
            if key.startswith("order_"):
                order_idx = int(key.replace("order_", ""))
                
                # 投手は打順に入れられない（DH制でない場合の9番を除く）
                if player.position.value == "投手":
                    # DH制確認（リーグによって異なる）
                    is_dh_enabled = self._is_dh_enabled_for_team(team)
                    if is_dh_enabled or order_idx != 8:  # DH制ありなら投手不可、DH制なしでも9番以外は不可
                        ToastManager.show("投手は打順に入れません", "warning")
                        break
                
                # 守備位置の重複チェック（position_assignmentsを使用）
                if not hasattr(team, 'position_assignments'):
                    team.position_assignments = {}
                
                # この選手がどの守備位置で出場するか確認
                assigned_pos = None
                for pos_name, assigned_idx in team.position_assignments.items():
                    if assigned_idx == self.dragging_player_idx:
                        assigned_pos = pos_name
                        break
                
                # まだ守備位置が割り当てられていない場合、自動で割り当てを試みる
                if assigned_pos is None and player.position.value != "投手":
                    assigned_pos = self._try_auto_assign_position(team, player, self.dragging_player_idx)
                    if assigned_pos:
                        team.position_assignments[assigned_pos] = self.dragging_player_idx
                        ToastManager.show(f"{player.name}を{assigned_pos}に自動配置", "info")
                
                # 同一ポジションの選手が既に打順にいるかチェック
                position_conflict = self._check_position_conflict(team, self.dragging_player_idx, order_idx)
                if position_conflict:
                    ToastManager.show(position_conflict, "warning")
                    # 警告は出すが配置は許可（ユーザーが手動で調整）
                
                # 既存のラインナップでの元の位置を記録（まだ消さない）
                old_idx = None
                if self.dragging_player_idx in team.current_lineup:
                    old_idx = team.current_lineup.index(self.dragging_player_idx)

                # 指定位置に配置（リスト長を確保）
                while len(team.current_lineup) <= order_idx:
                    team.current_lineup.append(-1)

                # 既にその位置に誰かいる場合は入れ替えを行う
                if team.current_lineup[order_idx] >= 0:
                    old_player_idx = team.current_lineup[order_idx]
                    # もし元のスロットがあれば、そこにold_playerを戻す（入れ替え）
                    if old_idx is not None:
                        team.current_lineup[old_idx] = old_player_idx
                    else:
                        # 元の位置が存在しない（外部から追加された選手）なら、探して置換
                        for i, idx in enumerate(team.current_lineup):
                            if idx == self.dragging_player_idx:
                                team.current_lineup[i] = old_player_idx
                                break
                else:
                    # その位置が空だった場合、元のスロットは空にする
                    if old_idx is not None:
                        team.current_lineup[old_idx] = -1

                # 最後に指定位置へ配置
                team.current_lineup[order_idx] = self.dragging_player_idx
                ToastManager.show(f"{player.name}を{order_idx + 1}番に配置", "success")
                dropped = True
                break
            
            # 守備位置スロットへのドロップ
            elif key.startswith("pos_"):
                pos_name = key.replace("pos_", "")
                
                # サブポジション対応の守備位置チェック
                from models import Position
                
                # 守備位置名からPositionへの変換
                pos_name_to_position = {
                    "捕手": Position.CATCHER,
                    "一塁手": Position.FIRST,
                    "二塁手": Position.SECOND,
                    "三塁手": Position.THIRD,
                    "遊撃手": Position.SHORTSTOP,
                    "左翼手": Position.OUTFIELD,
                    "中堅手": Position.OUTFIELD,
                    "右翼手": Position.OUTFIELD,
                    "DH": None,  # DHは特別
                }
                
                target_position = pos_name_to_position.get(pos_name)
                player_pos = player.position
                
                # DHでない場合、適切なポジションかチェック
                if target_position is not None:
                    # 投手はフィールドに配置できない
                    if player_pos == Position.PITCHER:
                        ToastManager.show("投手はフィールドに配置できません", "warning")
                        break
                    
                    # メインポジションまたはサブポジションで守れるかチェック
                    can_play = player.can_play_position(target_position)
                    
                    # 外野手の特別処理（左翼・中堅・右翼は同じOUTFIELDポジション）
                    if pos_name in ["左翼手", "中堅手", "右翼手"]:
                        can_play = (player_pos == Position.OUTFIELD or 
                                   Position.OUTFIELD in getattr(player, 'sub_positions', []))
                    
                    if not can_play:
                        if hasattr(player, 'sub_positions') and player.sub_positions:
                            sub_pos_names = [p.value for p in player.sub_positions]
                            ToastManager.show(f"{player.name}は{pos_name}を守れません（サブ: {', '.join(sub_pos_names)}）", "warning")
                        else:
                            ToastManager.show(f"{player.name}は{pos_name}を守れません", "warning")
                        break
                else:
                    # DH: 投手以外なら誰でも可
                    if player_pos == Position.PITCHER:
                        ToastManager.show("投手はDHに配置できません", "warning")
                        break
                
                # position_assignmentsの初期化
                if not hasattr(team, 'position_assignments'):
                    team.position_assignments = {}
                
                # 既にこの選手がどこかに配置されていたら削除
                for p_key in list(team.position_assignments.keys()):
                    if team.position_assignments[p_key] == self.dragging_player_idx:
                        del team.position_assignments[p_key]
                
                # 既にこの位置に誰かがいたら削除
                if pos_name in team.position_assignments:
                    old_idx = team.position_assignments[pos_name]
                    if old_idx != self.dragging_player_idx:
                        old_player = team.players[old_idx]
                        ToastManager.show(f"{old_player.name}の配置を解除", "info")
                
                team.position_assignments[pos_name] = self.dragging_player_idx
                
                # サブポジションで守る場合は適性値も表示
                rating = player.get_position_rating(target_position) if target_position else 1.0
                if rating < 1.0:
                    ToastManager.show(f"{player.name}を{pos_name}に配置（適性{int(rating*100)}%）", "success")
                else:
                    ToastManager.show(f"{player.name}を{pos_name}に配置", "success")
                dropped = True
                break
            
            # 先発投手スロットへのドロップ
            elif key == "starting_pitcher":
                if player.position.value != "投手":
                    ToastManager.show("投手以外は先発に設定できません", "warning")
                    break
                
                team.starting_pitcher_idx = self.dragging_player_idx
                ToastManager.show(f"{player.name}を先発投手に設定", "success")
                dropped = True
                break
        
        # ドラッグ状態リセット
        self.dragging_player_idx = -1
        self.drag_pos = None
    
    def handle_position_drop(self, mouse_pos):
        """ポジションのドラッグ&ドロップ処理"""
        if self.dragging_position_slot < 0 or not self.state_manager.player_team:
            self.dragging_position_slot = -1
            self.position_drag_pos = None
            return
        
        team = self.state_manager.player_team
        from_slot = self.dragging_position_slot
        
        # lineup_positionsの初期化
        if not hasattr(team, 'lineup_positions') or team.lineup_positions is None:
            team.lineup_positions = ["捕", "一", "二", "三", "遊", "左", "中", "右", "DH"]
        while len(team.lineup_positions) < 9:
            team.lineup_positions.append("DH")
        
        # ドロップゾーンを取得
        if "_drop_zones" in self.buttons:
            drop_zones = self.buttons["_drop_zones"]
        else:
            drop_zones = self.drop_zones
        
        # どのスロットにドロップしたかを判定
        for key, rect in drop_zones.items():
            if not isinstance(rect, pygame.Rect):
                continue
            if not rect.collidepoint(mouse_pos):
                continue
            
            # 打順スロットへのポジションドロップ
            if key.startswith("order_") or key.startswith("position_slot_"):
                if key.startswith("order_"):
                    to_slot = int(key.replace("order_", ""))
                else:
                    to_slot = int(key.replace("position_slot_", ""))
                
                if to_slot != from_slot and 0 <= to_slot < 9:
                    # ポジションを入れ替え
                    team.lineup_positions[from_slot], team.lineup_positions[to_slot] = \
                        team.lineup_positions[to_slot], team.lineup_positions[from_slot]
                    ToastManager.show(f"{from_slot+1}番と{to_slot+1}番のポジションを入れ替え", "success")
                break
        
        # ドラッグ状態リセット
        self.dragging_position_slot = -1
        self.position_drag_pos = None
    
    def optimize_lineup_by_stats(self):
        """ラインナップを能力順に最適化"""
        team = self.state_manager.player_team
        if not team or not team.current_lineup:
            ToastManager.show("オーダーが設定されていません", "warning")
            return
        
        lineup = team.current_lineup
        
        # 有効な選手のみフィルタリング
        valid_entries = []
        for idx in lineup:
            if idx >= 0 and idx < len(team.players):
                player = team.players[idx]
                # 打撃能力スコアを計算
                score = player.stats.contact * 2 + player.stats.power * 1.5 + player.stats.speed_run
                valid_entries.append((idx, score))
        
        if len(valid_entries) < 2:
            ToastManager.show("最適化する選手が不足しています", "warning")
            return
        
        # スコア順にソート（高い順）
        valid_entries.sort(key=lambda x: x[1], reverse=True)
        
        # 典型的な打順配置（1番: 出塁、3-5番: クリーンアップ）
        # 3番が最高スコア、4番が2番目、5番が3番目、1番が4番目...
        order_priority = [2, 3, 4, 0, 1, 5, 6, 7, 8]  # 0-indexed
        
        # 新しいラインナップを構築
        new_lineup = [-1] * 9
        for i, (player_idx, _) in enumerate(valid_entries):
            if i < len(order_priority):
                slot = order_priority[i]
                new_lineup[slot] = player_idx
        
        # 残りのスロットを埋める
        for i, idx in enumerate(lineup):
            if idx >= 0 and idx not in new_lineup:
                for j in range(9):
                    if new_lineup[j] == -1:
                        new_lineup[j] = idx
                        break
        
        team.current_lineup = new_lineup
        ToastManager.show("ラインナップを最適化しました", "success")
    
    def shuffle_lineup(self):
        """ラインナップをシャッフル"""
        team = self.state_manager.player_team
        if not team or not team.current_lineup:
            ToastManager.show("オーダーが設定されていません", "warning")
            return
        
        import random
        valid_players = [idx for idx in team.current_lineup if idx >= 0]
        random.shuffle(valid_players)
        
        new_lineup = [-1] * 9
        for i, player_idx in enumerate(valid_players):
            if i < 9:
                new_lineup[i] = player_idx
        
        team.current_lineup = new_lineup
        ToastManager.show("ラインナップをシャッフルしました", "info")
    
    def save_lineup_preset(self):
        """現在のラインナップをプリセットとして保存"""
        team = self.state_manager.player_team
        if not team or not team.current_lineup:
            ToastManager.show("保存するオーダーがありません", "warning")
            return
        
        if not hasattr(team, 'lineup_presets'):
            team.lineup_presets = []
        
        preset = {
            'lineup': list(team.current_lineup),
            'positions': list(getattr(team, 'lineup_positions', [])),
            'pitcher': team.starting_pitcher_idx
        }
        team.lineup_presets.append(preset)
        
        # 最大5件まで保持
        if len(team.lineup_presets) > 5:
            team.lineup_presets = team.lineup_presets[-5:]
        
        ToastManager.show(f"オーダープリセット{len(team.lineup_presets)}を保存", "success")
    
    def load_lineup_preset(self):
        """最後に保存したラインナッププリセットを読み込み"""
        team = self.state_manager.player_team
        if not team:
            return
        
        if not hasattr(team, 'lineup_presets') or not team.lineup_presets:
            ToastManager.show("保存されたプリセットがありません", "warning")
            return
        
        # 最後のプリセットを読み込み
        preset = team.lineup_presets[-1]
        team.current_lineup = list(preset.get('lineup', []))
        if 'positions' in preset and preset['positions']:
            team.lineup_positions = list(preset['positions'])
        if 'pitcher' in preset:
            team.starting_pitcher_idx = preset['pitcher']
        
        ToastManager.show("オーダープリセットを読み込みました", "success")
    
    def _is_dh_enabled_for_team(self, team: Team) -> bool:
        """チームのリーグに応じてDH制が有効かどうかを返す"""
        rules = self.settings.game_rules
        
        # チームのリーグを確認
        from models import League
        if team.league == League.CENTRAL:
            return rules.central_dh
        elif team.league == League.PACIFIC:
            return rules.pacific_dh
        else:
            # 不明な場合はDHありとする
            return True
    
    def _try_auto_assign_position(self, team: Team, player, player_idx: int) -> str:
        """打順配置時に守備位置を自動割り当て"""
        from models import Position
        
        # 既に割り当て済みのポジションを取得
        assigned_positions = set(team.position_assignments.keys()) if hasattr(team, 'position_assignments') else set()
        
        # 選手のメインポジションに基づいて割り当て
        pos_map = {
            Position.CATCHER: "捕手",
            Position.FIRST: "一塁手",
            Position.SECOND: "二塁手",
            Position.THIRD: "三塁手",
            Position.SHORTSTOP: "遊撃手",
        }
        
        main_pos = player.position
        
        # メインポジションが空いていれば割り当て
        if main_pos in pos_map:
            pos_name = pos_map[main_pos]
            if pos_name not in assigned_positions:
                return pos_name
        
        # 外野手の場合は左中右を順に試す
        if main_pos == Position.OUTFIELD:
            for outfield_pos in ["左翼手", "中堅手", "右翼手"]:
                if outfield_pos not in assigned_positions:
                    return outfield_pos
        
        # メインポジションが埋まっている場合、サブポジションを試す
        if hasattr(player, 'sub_positions'):
            for sub_pos in player.sub_positions:
                if sub_pos in pos_map:
                    sub_pos_name = pos_map[sub_pos]
                    if sub_pos_name not in assigned_positions:
                        return sub_pos_name
                elif sub_pos == Position.OUTFIELD:
                    for outfield_pos in ["左翼手", "中堅手", "右翼手"]:
                        if outfield_pos not in assigned_positions:
                            return outfield_pos
        
        # DH制が有効で、DHが空いていればDHに配置
        if self._is_dh_enabled_for_team(team) and "DH" not in assigned_positions:
            return "DH"
        
        return None
    
    def _check_position_conflict(self, team: Team, player_idx: int, target_order: int) -> str:
        """ポジション重複をチェックし、問題があればメッセージを返す"""
        from models import Position
        
        if not hasattr(team, 'position_assignments'):
            return None
        
        player = team.players[player_idx]
        
        # この選手の守備位置を取得
        player_pos = None
        for pos_name, assigned_idx in team.position_assignments.items():
            if assigned_idx == player_idx:
                player_pos = pos_name
                break
        
        if player_pos is None:
            # 守備位置未割り当て
            return None
        
        # 同じ守備位置の選手が既にラインナップにいるか
        for i, lineup_idx in enumerate(team.current_lineup):
            if lineup_idx < 0 or lineup_idx == player_idx:
                continue
            
            # この選手の守備位置を取得
            for pos_name, assigned_idx in team.position_assignments.items():
                if assigned_idx == lineup_idx:
                    if pos_name == player_pos and pos_name != "DH":
                        other_player = team.players[lineup_idx]
                        return f"注意: {other_player.name}と同じ守備位置（{pos_name}）です"
        
        # 外野の特別処理（左中右は別々にカウント）
        if player_pos in ["左翼手", "中堅手", "右翼手"]:
            outfield_count = 0
            for pos_name in team.position_assignments.keys():
                if pos_name in ["左翼手", "中堅手", "右翼手"]:
                    assigned_idx = team.position_assignments[pos_name]
                    if assigned_idx in team.current_lineup:
                        outfield_count += 1
            
            if outfield_count >= 3 and player_idx not in team.current_lineup:
                return "外野手が既に3人います"
        
        return None
    
    def promote_player_to_roster(self, player_idx: int):
        """育成選手を支配下登録に昇格"""
        team = self.state_manager.player_team
        if not team or player_idx < 0 or player_idx >= len(team.players):
            return
        
        player = team.players[player_idx]
        if not player.is_developmental:
            ToastManager.show(f"{player.name}は既に支配下登録です", "warning")
            return
        
        if team.promote_to_roster(player):
            ToastManager.show(f"{player.name}を支配下登録しました！", "success")
            # 背番号を変更（3桁から2桁へ）
            used_numbers = {p.uniform_number for p in team.players if not p.is_developmental and p != player}
            for num in range(1, 100):
                if num not in used_numbers:
                    player.uniform_number = num
                    break
        else:
            ToastManager.show("支配下枠が一杯です", "error")
    
    def add_player_to_lineup(self, player_idx: int):
        """選手をラインアップに追加"""
        team = self.state_manager.player_team
        if not team or player_idx < 0 or player_idx >= len(team.players):
            return
        
        player = team.players[player_idx]
        
        # 既にラインアップに入っているか確認
        if player_idx in team.current_lineup:
            ToastManager.show(f"{player.name}は既にスタメンです", "warning")
            return
        
        # 9人未満なら追加
        if len(team.current_lineup) < 9:
            team.current_lineup.append(player_idx)
            ToastManager.show(f"{player.name}をスタメンに追加", "success")
        else:
            ToastManager.show("スタメンは9人までです", "warning")
    
    def remove_player_from_lineup(self, slot: int):
        """ラインアップから選手を削除"""
        team = self.state_manager.player_team
        if not team:
            return
        
        if 0 <= slot < len(team.current_lineup):
            player_idx = team.current_lineup[slot]
            if player_idx is not None and 0 <= player_idx < len(team.players):
                player_name = team.players[player_idx].name
                team.current_lineup[slot] = None
                # Noneを詰める
                team.current_lineup = [p for p in team.current_lineup if p is not None]
                ToastManager.show(f"{player_name}をスタメンから外しました", "info")
    
    def cycle_lineup_position(self, slot: int):
        """守備位置をサイクル（次のポジションへ変更）"""
        team = self.state_manager.player_team
        if not team:
            return
        
        from settings_manager import settings
        
        # DH制の判定
        is_pacific = hasattr(team, 'league') and team.league.value == "パシフィック"
        use_dh = (is_pacific and settings.game_rules.pacific_dh) or (not is_pacific and settings.game_rules.central_dh)
        
        # 利用可能なポジション
        positions = ["捕", "一", "二", "三", "遊", "左", "中", "右"]
        if use_dh:
            positions.append("DH")
        
        # lineup_positionsを初期化
        if not hasattr(team, 'lineup_positions') or team.lineup_positions is None:
            team.lineup_positions = positions[:9] if use_dh else ["捕", "一", "二", "三", "遊", "左", "中", "右", "投"]
        
        # 9スロット分確保
        while len(team.lineup_positions) < 9:
            team.lineup_positions.append("DH" if use_dh else "投")
        
        if slot < 0 or slot >= 9:
            return
        
        current_pos = team.lineup_positions[slot]
        try:
            current_idx = positions.index(current_pos)
            next_idx = (current_idx + 1) % len(positions)
        except ValueError:
            next_idx = 0
        
        team.lineup_positions[slot] = positions[next_idx]
        ToastManager.show(f"{slot+1}番の守備を{positions[next_idx]}に変更", "info")
    
    def swap_lineup_order(self, from_slot: int, to_slot: int):
        """打順を入れ替える（選手のみ、ポジションは維持）"""
        team = self.state_manager.player_team
        if not team:
            return
        
        lineup = team.current_lineup
        if not lineup:
            return
        
        # lineupの長さが足りない場合は拡張
        while len(lineup) < 9:
            lineup.append(-1)
        
        # インデックスチェック
        if from_slot < 0 or from_slot >= 9 or to_slot < 0 or to_slot >= 9:
            return
        
        # 選手のみを入れ替え（ポジションは維持）
        from_player = lineup[from_slot] if from_slot < len(lineup) else -1
        to_player = lineup[to_slot] if to_slot < len(lineup) else -1
        
        lineup[from_slot] = to_player
        lineup[to_slot] = from_player
        
        ToastManager.show(f"{from_slot+1}番と{to_slot+1}番を入れ替え", "info")
    
    def swap_lineup_position(self, from_slot: int, to_slot: int):
        """ポジションのみを入れ替える"""
        team = self.state_manager.player_team
        if not team:
            return
        
        # lineup_positionsの初期化
        if not hasattr(team, 'lineup_positions') or team.lineup_positions is None:
            team.lineup_positions = ["捕", "一", "二", "三", "遊", "左", "中", "右", "DH"]
        
        while len(team.lineup_positions) < 9:
            team.lineup_positions.append("DH")
        
        # インデックスチェック
        if from_slot < 0 or from_slot >= 9 or to_slot < 0 or to_slot >= 9:
            return
        
        # ポジションのみを入れ替え
        team.lineup_positions[from_slot], team.lineup_positions[to_slot] = \
            team.lineup_positions[to_slot], team.lineup_positions[from_slot]
        
        ToastManager.show(f"{from_slot+1}番と{to_slot+1}番の守備位置を入れ替え", "info")
    
    def set_lineup_position_direct(self, position: str):
        """選択中のスロットに直接ポジションを設定"""
        team = self.state_manager.player_team
        if not team:
            return
        
        # 選択中のスロットがなければ、最後に選択したスロットか最初の空きスロットを使用
        slot = self.selected_lineup_slot
        if slot < 0 or slot >= 9:
            # 空きスロットを探す
            slot = 0
        
        # lineup_positionsを初期化
        if not hasattr(team, 'lineup_positions') or team.lineup_positions is None:
            team.lineup_positions = ["捕", "一", "二", "三", "遊", "左", "中", "右", "DH"]
        
        while len(team.lineup_positions) < 9:
            team.lineup_positions.append("DH")
        
        team.lineup_positions[slot] = position
        ToastManager.show(f"{slot+1}番を{position}に変更", "info")
    
    def _get_pinch_hit_candidates(self) -> list:
        """代打候補選手を取得"""
        team = self.state_manager.player_team
        if not team:
            return []
        
        from models import Position
        
        # 現在のラインナップに入っていない野手
        lineup_set = set(team.current_lineup or [])
        candidates = []
        
        for i, player in enumerate(team.players):
            if i in lineup_set:
                continue
            if player.position == Position.PITCHER:
                continue
            if getattr(player, 'is_developmental', False):
                continue
            candidates.append(player)
        
        # ミートとパワーの合計でソート
        candidates.sort(key=lambda p: p.stats.contact + p.stats.power, reverse=True)
        return candidates[:10]
    
    def _get_pinch_run_candidates(self) -> list:
        """代走候補選手を取得"""
        team = self.state_manager.player_team
        if not team:
            return []
        
        from models import Position
        
        lineup_set = set(team.current_lineup or [])
        candidates = []
        
        for i, player in enumerate(team.players):
            if i in lineup_set:
                continue
            if player.position == Position.PITCHER:
                continue
            if getattr(player, 'is_developmental', False):
                continue
            candidates.append(player)
        
        # 走力でソート
        candidates.sort(key=lambda p: p.stats.speed, reverse=True)
        return candidates[:10]
    
    def _get_relief_pitcher_candidates(self) -> list:
        """継投候補投手を取得"""
        team = self.state_manager.player_team
        if not team:
            return []
        
        from models import Position, PitchType
        
        candidates = []
        current_pitcher_idx = team.starting_pitcher_idx
        
        for i, player in enumerate(team.players):
            if player.position != Position.PITCHER:
                continue
            if i == current_pitcher_idx:
                continue
            if getattr(player, 'is_developmental', False):
                continue
            # 先発投手は中継ぎに使わない（オプション）
            if getattr(player, 'pitch_type', None) == PitchType.STARTER:
                continue
            candidates.append(player)
        
        # 能力でソート（球速 + 制球）
        candidates.sort(key=lambda p: p.stats.speed + p.stats.control, reverse=True)
        return candidates[:8]
    
    def _execute_strategy_substitution(self, candidate_idx: int):
        """戦略的選手交代を実行"""
        if not self.strategy_candidates or candidate_idx >= len(self.strategy_candidates):
            return
        
        new_player = self.strategy_candidates[candidate_idx]
        team = self.state_manager.player_team
        
        if not team:
            return
        
        new_player_idx = team.players.index(new_player)
        
        if self.game_strategy_mode == "pinch_hit":
            # 代打: 現在の打者と交代
            ToastManager.show(f"代打: {new_player.name}", "success")
            # 実際のゲームシミュレータに交代を通知
            if self.game_simulator and hasattr(self.game_simulator, 'substitute_batter'):
                self.game_simulator.substitute_batter(new_player_idx)
        
        elif self.game_strategy_mode == "pinch_run":
            # 代走: 走者と交代
            ToastManager.show(f"代走: {new_player.name}", "success")
            if self.game_simulator and hasattr(self.game_simulator, 'substitute_runner'):
                self.game_simulator.substitute_runner(new_player_idx)
        
        elif self.game_strategy_mode == "pitching_change":
            # 継投
            ToastManager.show(f"継投: {new_player.name}", "success")
            team.starting_pitcher_idx = new_player_idx
            if self.game_simulator:
                self.game_simulator.current_home_pitcher_idx = new_player_idx
                self.game_simulator.home_pitcher_stats = {
                    'pitch_count': 0, 'hits': 0, 'walks': 0, 'runs': 0, 'innings': 0
                }
        
        # ダイアログを閉じる
        self.game_strategy_mode = None
        self.strategy_candidates = []
    
    def _run_game_simulation(self):
        """試合をシミュレーションして結果画面へ"""
        if not self.game_simulator:
            return
        
        # 試合をシミュレート
        self.game_simulator.simulate()
        self.result_scroll = 0
        self.state_manager.change_state(GameState.RESULT)
    
    def release_player(self, player_idx: int):
        """選手を解雇（自由契約）"""
        team = self.state_manager.player_team
        if not team or player_idx < 0 or player_idx >= len(team.players):
            return
        
        player = team.players[player_idx]
        player_name = player.name
        
        # ラインアップから削除
        if player_idx in team.current_lineup:
            team.current_lineup.remove(player_idx)
        
        # 選手リストから削除
        team.players.remove(player)
        
        # ラインアップのインデックスを調整
        team.current_lineup = [i if i < player_idx else i - 1 for i in team.current_lineup if i != player_idx]
        
        if team.starting_pitcher_idx == player_idx:
            team.starting_pitcher_idx = -1
        elif team.starting_pitcher_idx > player_idx:
            team.starting_pitcher_idx -= 1
        
        ToastManager.show(f"{player_name}を自由契約にしました", "warning")
    
    def clear_lineup(self):
        """ラインナップをクリア"""
        if self.state_manager.player_team:
            self.state_manager.player_team.current_lineup = []
            self.state_manager.player_team.starting_pitcher_idx = -1
            if hasattr(self.state_manager.player_team, 'position_assignments'):
                self.state_manager.player_team.position_assignments = {}
            ToastManager.show("オーダーをクリアしました", "info")
    
    def complete_pennant_draft(self):
        """ペナントドラフト確定"""
        if not self.pennant_manager or not self.pennant_draft_picks:
            return
        
        for idx in self.pennant_draft_picks:
            if idx < len(self.pennant_manager.draft_pool):
                draft_player = self.pennant_manager.draft_pool[idx]
                new_player = self.pennant_manager.convert_draft_to_player(draft_player)
                
                # 空き背番号を探す
                used = [p.uniform_number for p in self.state_manager.player_team.players]
                for num in range(1, 100):
                    if num not in used:
                        new_player.uniform_number = num
                        break
                
                self.state_manager.player_team.players.append(new_player)
        
        count = len(self.pennant_draft_picks)
        ToastManager.show(f"{count}人を指名しました！", "success")
        
        self.pennant_draft_picks = []
        self.pennant_manager.advance_phase()
        self.state_manager.change_state(GameState.PENNANT_HOME)
    
    def update_pennant_phase(self):
        """ペナントフェーズに応じて画面遷移"""
        if not self.pennant_manager:
            return
        
        phase = self.pennant_manager.current_phase
        
        if phase == PennantPhase.SPRING_CAMP:
            self.state_manager.change_state(GameState.PENNANT_HOME)
        elif phase == PennantPhase.DRAFT:
            self.state_manager.change_state(GameState.PENNANT_HOME)
        elif phase == PennantPhase.CLIMAX_SERIES:
            self.state_manager.change_state(GameState.PENNANT_CS)
        else:
            self.state_manager.change_state(GameState.PENNANT_HOME)
    
    def simulate_games(self, days: int):
        """指定日数分の試合をシミュレート"""
        if not self.schedule_manager or not self.state_manager.player_team:
            return
        
        simulated = 0
        for _ in range(days):
            # 全球団の試合をシミュレート
            simulated += self.simulate_all_teams_one_day()
            
            # プレイヤーチームの試合がなくなったら終了
            next_game = self.schedule_manager.get_next_game_for_team(self.state_manager.player_team.name)
            if not next_game:
                break
        
        ToastManager.show(f"{simulated}試合をシミュレートしました", "info")
    
    def simulate_all_teams_one_day(self) -> int:
        """全チームの1日分の試合をシミュレート"""
        if not self.schedule_manager:
            return 0
        
        simulated = 0
        
        # 未完了の試合を日付順に取得
        pending_games = [g for g in self.schedule_manager.schedule.games if not g.is_completed]
        if not pending_games:
            return 0
        
        # 最も早い日付の試合を取得
        min_date = min(pending_games, key=lambda g: (g.month, g.day))
        today_games = [g for g in pending_games if g.month == min_date.month and g.day == min_date.day]
        
        for game in today_games:
            home_team = next((t for t in self.state_manager.all_teams if t.name == game.home_team_name), None)
            away_team = next((t for t in self.state_manager.all_teams if t.name == game.away_team_name), None)
            
            if home_team and away_team:
                # 両チームのオーダーを自動設定
                self.auto_set_lineup_for_team(home_team)
                self.auto_set_lineup_for_team(away_team)
                
                # 試合シミュレーション
                sim = GameSimulator(home_team, away_team)
                sim.simulate_game()
                self.schedule_manager.complete_game(game, sim.home_score, sim.away_score)
                simulated += 1
                
                # ペナントモード時は疲労加算
                if self.pennant_manager:
                    for player in home_team.players:
                        self.pennant_manager.add_fatigue(player, random.randint(2, 5))
                    for player in away_team.players:
                        self.pennant_manager.add_fatigue(player, random.randint(2, 5))
        
        return simulated
    
    def simulate_all_games_until(self, target_game_idx: int):
        """指定した試合インデックスまで全球団の試合をシミュレート"""
        if not self.schedule_manager or not self.state_manager.player_team:
            return
        
        games = self.schedule_manager.get_team_schedule(self.state_manager.player_team.name)
        if target_game_idx >= len(games):
            return
        
        target_game = games[target_game_idx]
        simulated_total = 0
        
        # 選択した試合の直前まで全チームの試合をシミュレート
        while True:
            # 次の試合を確認
            next_idx = next((i for i, g in enumerate(games) if not g.is_completed), len(games))
            
            # 目標の試合に到達したら終了
            if next_idx >= target_game_idx:
                break
            
            # 1日分の全試合をシミュレート
            simulated = self.simulate_all_teams_one_day()
            if simulated == 0:
                break
            simulated_total += simulated
        
        if simulated_total > 0:
            ToastManager.show(f"{simulated_total}試合をシミュレートしました", "success")
        
        # 選択をリセットして次の試合に移動
        self.selected_game_idx = target_game_idx
        
        # スクロール位置を更新
        self.scroll_offset = max(0, target_game_idx - 3)
    
    def run(self):
        """メインループ"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """エントリーポイント"""
    game = NPBGame()
    game.run()


if __name__ == "__main__":
    main()
