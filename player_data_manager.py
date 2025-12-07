# filename: tancider99/pennantsimulator/PennantSimulator-dc826ddd1c528c22b1587f45283260277b108bea/player_data_manager.py
# -*- coding: utf-8 -*-
"""
固定選手データ管理モジュール
選手データを球団ごとのJSONファイルに保存・読み込み
ファイルを直接編集して選手の名前・能力・背番号などを変更可能
"""
import json
import os
from typing import Dict, List, Any, Optional
from models import (
    Team, Player, PlayerStats, Position, PitchType, 
    PlayerStatus, League, TeamLevel, PlayerRecord
)


class PlayerDataManager:
    """選手データの保存・読み込み管理クラス（球団別ファイル）"""
    
    # スクリプトのディレクトリを基準にデータディレクトリを設定
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(_SCRIPT_DIR, "player_data")
    
    def __init__(self):
        """初期化"""
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """データディレクトリを作成"""
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)
            print(f"データディレクトリを作成しました: {self.DATA_DIR}")
    
    def _get_team_filepath(self, team_name: str) -> str:
        """チームごとのファイルパスを取得"""
        # ファイル名に使えない文字を置換
        safe_name = team_name.replace(" ", "_").replace("/", "_")
        return os.path.join(self.DATA_DIR, f"{safe_name}.json")
    
    def player_to_dict(self, player: Player) -> Dict[str, Any]:
        """PlayerオブジェクトをDict形式に変換（編集しやすい形式・投手/野手別）"""
        from models import Position
        
        is_pitcher = player.position == Position.PITCHER
        
        base_data = {
            "名前": player.name,
            "背番号": player.uniform_number,
            "年齢": player.age,
            "ポジション": player.position.value,
            "外国人": player.is_foreign,
            "年俸": player.salary,
            "プロ年数": player.years_pro,
            "ドラフト順位": player.draft_round,
            "育成選手": player.is_developmental,
            "チームレベル": player.team_level.value if player.team_level else None,
        }
        
        if is_pitcher:
            # 投手の場合
            base_data["球種"] = player.pitch_type.value if player.pitch_type else None
            base_data["先発適性"] = player.starter_aptitude
            base_data["中継ぎ適性"] = player.middle_aptitude
            base_data["抑え適性"] = player.closer_aptitude
            base_data["能力値"] = {
                "球速": player.stats.velocity,       # 修正: speed(走力)ではなくvelocity(球速)
                "コントロール": player.stats.control,
                "スタミナ": player.stats.stamina,
                "変化球": player.stats.stuff,        # 修正: breaking(prop)ではなくstuff(field)
                "精神力": player.stats.intelligence, # 修正: mental(prop)ではなくintelligence(field)
                "ムーブメント": player.stats.movement,
                "持ち球": player.stats.pitches,      # 修正: 辞書形式で保存
            }
        else:
            # 野手の場合
            base_data["サブポジション"] = [p.value for p in player.sub_positions]
            base_data["サブポジション評価"] = player.sub_position_ratings
            base_data["能力値"] = {
                "ミート": player.stats.contact,
                "パワー": player.stats.power,
                "走力": player.stats.speed,          # 修正: run(prop)ではなくspeed(field)
                "盗塁": player.stats.steal,
                "走塁": player.stats.baserunning,
                "肩力": player.stats.arm,            # プロパティ値を保存(読み込み時に各fieldへ展開)
                "守備": player.stats.fielding,       # プロパティ値を保存
                "捕球": player.stats.catching,       # プロパティ値を保存
                "精神力": player.stats.intelligence,
                "ギャップ": player.stats.gap,
                "選球眼": player.stats.eye,
                "三振回避": player.stats.avoid_k
            }
        
        return base_data
    
    def _get_value(self, data: Dict[str, Any], jp_key: str, en_key: str, default):
        """日本語キーと英語キーの両方をチェックして値を取得"""
        if jp_key in data and data[jp_key] is not None:
            return data[jp_key]
        if en_key in data and data[en_key] is not None:
            return data[en_key]
        return default
    
    def dict_to_player(self, data: Dict[str, Any]) -> Player:
        """Dict形式からPlayerオブジェクトを復元（日本語キー対応）"""
        name = self._get_value(data, "名前", "name", "選手")
        uniform_number = self._get_value(data, "背番号", "uniform_number", 0)
        age = self._get_value(data, "年齢", "age", 25)
        position_value = self._get_value(data, "ポジション", "position", "右翼手")
        pitch_type_value = self._get_value(data, "球種", "pitch_type", None)
        is_foreign = self._get_value(data, "外国人", "is_foreign", False)
        salary = self._get_value(data, "年俸", "salary", 10000000)
        years_pro = self._get_value(data, "プロ年数", "years_pro", 0)
        draft_round = self._get_value(data, "ドラフト順位", "draft_round", 0)
        is_developmental = self._get_value(data, "育成選手", "is_developmental", False)
        team_level_value = self._get_value(data, "チームレベル", "team_level", None)
        starter_aptitude = self._get_value(data, "先発適性", "starter_aptitude", 50)
        middle_aptitude = self._get_value(data, "中継ぎ適性", "middle_aptitude", 50)
        closer_aptitude = self._get_value(data, "抑え適性", "closer_aptitude", 50)
        sub_positions_data = self._get_value(data, "サブポジション", "sub_positions", [])
        sub_position_ratings = self._get_value(data, "サブポジション評価", "sub_position_ratings", {})
        
        # Position変換
        position = None
        for p in Position:
            if p.value == position_value:
                position = p
                break
        if position is None:
            position = Position.OUTFIELDER_RIGHT if hasattr(Position, 'OUTFIELDER_RIGHT') else Position.OUTFIELD
        
        # PitchType変換
        pitch_type = None
        if pitch_type_value:
            for pt in PitchType:
                if pt.value == pitch_type_value:
                    pitch_type = pt
                    break
        
        # TeamLevel変換
        team_level = None
        if team_level_value:
            for tl in TeamLevel:
                if tl.value == team_level_value:
                    team_level = tl
                    break
        
        # PlayerStats復元（日本語キー対応）
        stats_data = self._get_value(data, "能力値", "stats", {})
        
        def get_stat(jp_key: str, en_key: str, default):
            """statsからの値取得"""
            if jp_key in stats_data and stats_data[jp_key] is not None:
                return stats_data[jp_key]
            if en_key in stats_data and stats_data[en_key] is not None:
                return stats_data[en_key]
            return default
        
        # 旧形式のデータを読み込んで変数に格納
        run_val = get_stat("走力", "run", 50)
        arm_val = get_stat("肩力", "arm", 50)
        fielding_val = get_stat("守備", "fielding", 50)
        catching_val = get_stat("捕球", "catching", 50)
        breaking_val = get_stat("変化球", "breaking", 50)
        mental_val = get_stat("精神力", "mental", 50)
        
        # 持ち球の処理（リストか辞書か判別）
        pitches_data = get_stat("持ち球", "breaking_balls", {})
        pitches_dict = {}
        if isinstance(pitches_data, list):
            # リストの場合は全て同じ値（変化球値）で辞書化
            for p_name in pitches_data:
                pitches_dict[p_name] = breaking_val
        elif isinstance(pitches_data, dict):
            pitches_dict = pitches_data

        # PlayerStatsの生成（正しいフィールド引数のみを使用）
        stats = PlayerStats(
            # 打撃
            contact = get_stat("ミート", "contact", 50),
            gap = get_stat("ギャップ", "gap", 50),
            power = get_stat("パワー", "power", 50),
            eye = get_stat("選球眼", "eye", 50),
            avoid_k = get_stat("三振回避", "avoid_k", 50),
            
            # 走塁
            speed = run_val,
            steal = get_stat("盗塁", "stealing", 50),
            baserunning = get_stat("走塁", "baserunning", 50),
            
            # 守備 (統合値を各ポジションへ展開)
            catcher_ability = fielding_val,
            catcher_arm = arm_val,
            inf_range = fielding_val,
            inf_error = catching_val,
            inf_arm = arm_val,
            turn_dp = fielding_val,
            of_range = fielding_val,
            of_error = catching_val,
            of_arm = arm_val,
            
            # 投手
            stuff = breaking_val,
            movement = get_stat("ムーブメント", "movement", 50),
            control = get_stat("コントロール", "control", 50),
            velocity = get_stat("球速", "speed", 145), # speedキーで球速が入っている場合に対応
            stamina = get_stat("スタミナ", "stamina", 50),
            
            # 共通
            intelligence = mental_val,
            pitches = pitches_dict
        )
        
        # サブポジション復元
        sub_positions = []
        for sp_value in sub_positions_data:
            for p in Position:
                if p.value == sp_value:
                    sub_positions.append(p)
                    break
        
        player = Player(
            name=name,
            position=position,
            pitch_type=pitch_type,
            stats=stats,
            age=age,
            status=PlayerStatus.FARM if is_developmental else PlayerStatus.ACTIVE,
            uniform_number=uniform_number,
            is_foreign=is_foreign,
            salary=salary,
            years_pro=years_pro,
            draft_round=draft_round,
            is_developmental=is_developmental,
            team_level=team_level,
            sub_positions=sub_positions,
            sub_position_ratings=sub_position_ratings,
            starter_aptitude=starter_aptitude,
            middle_aptitude=middle_aptitude,
            closer_aptitude=closer_aptitude
        )
        
        return player
    
    def team_to_dict(self, team: Team) -> Dict[str, Any]:
        """TeamオブジェクトをDict形式に変換（球団別ファイル用）"""
        return {
            "球団名": team.name,
            "リーグ": team.league.value,
            "予算": team.budget,
            "選手一覧": [self.player_to_dict(p) for p in team.players]
        }
    
    def dict_to_team(self, data: Dict[str, Any]) -> Team:
        """Dict形式からTeamオブジェクトを復元（日本語キー対応）"""
        name = data.get("球団名") or data.get("name", "チーム")
        league_value = data.get("リーグ") or data.get("league", "セントラル・リーグ")
        budget = data.get("予算") or data.get("budget", 5000000000)
        players_data = data.get("選手一覧") or data.get("players", [])
        
        # League変換
        league = None
        for lg in League:
            if lg.value == league_value:
                league = lg
                break
        if league is None:
            league = League.CENTRAL
        
        team = Team(
            name=name,
            league=league,
            budget=budget
        )
        
        # 選手を復元
        for player_data in players_data:
            player = self.dict_to_player(player_data)
            team.players.append(player)
        
        return team
    
    def save_team(self, team: Team) -> bool:
        """球団データを個別ファイルに保存
        
        Args:
            team: 保存するチーム
        
        Returns:
            成功したかどうか
        """
        try:
            filepath = self._get_team_filepath(team.name)
            
            data = {
                "説明": "このファイルを編集して選手の能力値・名前・背番号などを変更できます",
                "能力値の範囲": "1～200（100が平均）", # メッセージ修正
                "バージョン": "2.0",
                **self.team_to_dict(team)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"球団データを保存しました: {filepath}")
            return True
        
        except Exception as e:
            print(f"球団データ保存エラー: {e}")
            return False
    
    def load_team(self, team_name: str) -> Optional[Team]:
        """球団データを個別ファイルから読み込み
        
        Args:
            team_name: チーム名
        
        Returns:
            チームオブジェクト（失敗時はNone）
        """
        try:
            filepath = self._get_team_filepath(team_name)
            
            if not os.path.exists(filepath):
                print(f"球団データファイルが見つかりません: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            team = self.dict_to_team(data)
            print(f"球団データを読み込みました: {filepath}")
            return team
        
        except Exception as e:
            print(f"球団データ読み込みエラー: {e}")
            return None
    
    def save_all_teams(self, teams: List[Team]) -> bool:
        """全チームの選手データを個別ファイルに保存
        
        Args:
            teams: 保存するチームリスト
        
        Returns:
            成功したかどうか
        """
        success = True
        for team in teams:
            if not self.save_team(team):
                success = False
        return success
    
    def load_all_teams(self, team_names: List[str]) -> Optional[List[Team]]:
        """全チームの選手データを個別ファイルから読み込み
        
        Args:
            team_names: 読み込むチーム名のリスト
        
        Returns:
            チームリスト（失敗時はNone）
        """
        teams = []
        for team_name in team_names:
            team = self.load_team(team_name)
            if team:
                teams.append(team)
        
        return teams if teams else None
    
    def has_team_data(self, team_name: str) -> bool:
        """球団の保存済みデータが存在するかチェック"""
        filepath = self._get_team_filepath(team_name)
        return os.path.exists(filepath)
    
    def has_all_team_data(self, team_names: List[str]) -> bool:
        """全球団の保存済みデータが存在するかチェック"""
        return all(self.has_team_data(name) for name in team_names)
    
    def get_all_team_files(self) -> List[str]:
        """データディレクトリにある全球団ファイルのリストを取得"""
        if not os.path.exists(self.DATA_DIR):
            return []
        
        files = []
        for filename in os.listdir(self.DATA_DIR):
            if filename.endswith('.json'):
                files.append(filename)
        return files


# グローバルインスタンス
player_data_manager = PlayerDataManager()