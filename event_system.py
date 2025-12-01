# -*- coding: utf-8 -*-
"""
イベントシステム - シーズン中のランダムイベント
"""
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Callable
from models import Player, Team, Position


class EventType(Enum):
    """イベントタイプ"""
    # ポジティブイベント
    SPECIAL_TRAINING = ("特別練習", "positive")
    HOT_STREAK = ("打撃好調", "positive")
    CONFIDENCE_BOOST = ("自信アップ", "positive")
    VETERAN_ADVICE = ("ベテランの助言", "positive")
    AWAKENING = ("覚醒", "positive")
    MEDIA_ATTENTION = ("メディア注目", "positive")
    FAN_SUPPORT = ("ファンの応援", "positive")
    LUCKY_ITEM = ("ラッキーアイテム", "positive")
    CONTRACT_BONUS = ("契約ボーナス", "positive")
    TEAMMATE_CHEMISTRY = ("チームワーク向上", "positive")
    
    # ネガティブイベント
    SLUMP = ("スランプ", "negative")
    MINOR_INJURY = ("軽い怪我", "negative")
    FATIGUE = ("疲労蓄積", "negative")
    CONFIDENCE_LOSS = ("自信喪失", "negative")
    MEDIA_PRESSURE = ("メディアプレッシャー", "negative")
    FAMILY_ISSUE = ("家庭の事情", "negative")
    
    # 中立イベント
    TRADE_RUMOR = ("トレード噂", "neutral")
    POSITION_CHANGE = ("コンバート", "neutral")
    NEW_PITCH = ("新球種習得", "neutral")
    RIVAL_EMERGENCE = ("ライバル出現", "neutral")
    
    # チームイベント
    TEAM_MEETING = ("ミーティング", "team")
    TEAM_DINNER = ("チーム食事会", "team")
    MANAGER_STRATEGY = ("監督の戦略", "team")
    SCOUTING_REPORT = ("スカウティング", "team")
    
    def __init__(self, display_name: str, category: str):
        self.display_name = display_name
        self.category = category


@dataclass
class GameEvent:
    """ゲームイベント"""
    event_type: EventType
    target_player: Optional[Player]
    target_team: Optional[Team]
    title: str
    description: str
    effects: dict
    choices: List[dict] = None  # 選択肢がある場合
    
    def apply_effects(self):
        """効果を適用"""
        if self.target_player:
            player = self.target_player
            
            # 能力値変更
            if "contact" in self.effects:
                player.stats.contact = max(1, min(20, 
                    player.stats.contact + self.effects["contact"]))
            if "power" in self.effects:
                player.stats.power = max(1, min(20, 
                    player.stats.power + self.effects["power"]))
            if "speed" in self.effects:
                player.stats.speed = max(1, min(20, 
                    player.stats.speed + self.effects["speed"]))
            if "control" in self.effects:
                player.stats.control = max(1, min(20, 
                    player.stats.control + self.effects["control"]))
            if "stamina" in self.effects:
                player.stats.stamina = max(1, min(20, 
                    player.stats.stamina + self.effects["stamina"]))
            
            # コンディション変更
            if player.player_status:
                if "motivation" in self.effects:
                    player.player_status.change_motivation(self.effects["motivation"])
                if "fatigue" in self.effects:
                    player.player_status.add_fatigue(self.effects["fatigue"])
            
            # 特殊能力追加
            if "add_ability" in self.effects and player.special_abilities:
                from special_abilities import SpecialAbility
                ability = self.effects["add_ability"]
                if hasattr(SpecialAbility, ability):
                    player.special_abilities.add_ability(getattr(SpecialAbility, ability))


class EventGenerator:
    """イベント生成システム"""
    
    POSITIVE_EVENTS = [
        {
            "type": EventType.SPECIAL_TRAINING,
            "title": "特別練習の成果",
            "description": "{player}が特別練習で能力アップ！",
            "effects": {"contact": 1, "power": 1},
            "weight": 10
        },
        {
            "type": EventType.HOT_STREAK,
            "title": "絶好調！",
            "description": "{player}の調子が急上昇！",
            "effects": {"motivation": 20},
            "weight": 15
        },
        {
            "type": EventType.AWAKENING,
            "title": "覚醒！",
            "description": "{player}が覚醒！大幅に能力アップ！",
            "effects": {"contact": 2, "power": 2, "speed": 1},
            "weight": 3,
            "rare": True
        },
        {
            "type": EventType.VETERAN_ADVICE,
            "title": "ベテランからの助言",
            "description": "{player}がベテラン選手からアドバイスを受けた",
            "effects": {"control": 1, "motivation": 10},
            "weight": 8
        },
        {
            "type": EventType.FAN_SUPPORT,
            "title": "ファンからの応援",
            "description": "{player}へファンからの応援メッセージが届いた！",
            "effects": {"motivation": 15},
            "weight": 12
        },
        {
            "type": EventType.LUCKY_ITEM,
            "title": "ラッキーアイテム発見",
            "description": "{player}がラッキーアイテムを見つけた！調子アップ！",
            "effects": {"motivation": 10, "fatigue": -5},
            "weight": 10
        },
        {
            "type": EventType.TEAMMATE_CHEMISTRY,
            "title": "チームメイトとの絆",
            "description": "{player}とチームメイトの連携が向上！",
            "effects": {"motivation": 12},
            "weight": 10
        },
    ]
    
    NEGATIVE_EVENTS = [
        {
            "type": EventType.SLUMP,
            "title": "スランプ突入",
            "description": "{player}がスランプに陥った...",
            "effects": {"motivation": -20},
            "weight": 10
        },
        {
            "type": EventType.MINOR_INJURY,
            "title": "軽い怪我",
            "description": "{player}が練習中に軽い怪我を負った",
            "effects": {"fatigue": 20},
            "weight": 8
        },
        {
            "type": EventType.FATIGUE,
            "title": "疲労蓄積",
            "description": "{player}に疲労が蓄積している",
            "effects": {"fatigue": 15, "motivation": -5},
            "weight": 12
        },
        {
            "type": EventType.CONFIDENCE_LOSS,
            "title": "自信喪失",
            "description": "{player}が自信を失っている...",
            "effects": {"motivation": -15},
            "weight": 8
        },
        {
            "type": EventType.MEDIA_PRESSURE,
            "title": "メディアの批判",
            "description": "{player}がメディアから批判を受けた",
            "effects": {"motivation": -10},
            "weight": 6
        },
    ]
    
    NEUTRAL_EVENTS = [
        {
            "type": EventType.NEW_PITCH,
            "title": "新球種習得！",
            "description": "{player}が新しい変化球を習得した！",
            "effects": {"control": 1, "speed": -1},
            "weight": 5,
            "position_filter": [Position.PITCHER]
        },
        {
            "type": EventType.RIVAL_EMERGENCE,
            "title": "ライバル出現",
            "description": "{player}に若手のライバルが出現！切磋琢磨！",
            "effects": {"motivation": 5},
            "weight": 7
        },
    ]
    
    TEAM_EVENTS = [
        {
            "type": EventType.TEAM_MEETING,
            "title": "チームミーティング",
            "description": "チーム全体でミーティングを行った。士気向上！",
            "effects": {"motivation": 5},
            "weight": 10,
            "team_wide": True
        },
        {
            "type": EventType.TEAM_DINNER,
            "title": "チーム食事会",
            "description": "チーム全員で食事会を開催！チームワーク向上！",
            "effects": {"motivation": 8, "fatigue": -3},
            "weight": 8,
            "team_wide": True
        },
        {
            "type": EventType.MANAGER_STRATEGY,
            "title": "監督の新戦略",
            "description": "監督が新しい戦略を発表！チーム全体の意識が変わった",
            "effects": {"motivation": 10},
            "weight": 5,
            "team_wide": True
        },
    ]
    
    @classmethod
    def generate_daily_events(cls, team: Team, day: int) -> List[GameEvent]:
        """1日のイベントを生成"""
        events = []
        
        # イベント発生確率（1日あたり）
        event_chance = 0.15
        
        if random.random() < event_chance:
            # 個人イベント
            event_data = cls._select_event()
            if event_data:
                player = cls._select_target_player(team, event_data)
                if player:
                    event = cls._create_event(event_data, player, team)
                    if event:
                        events.append(event)
        
        # チームイベント（より低確率）
        if random.random() < 0.05:
            team_event = random.choice(cls.TEAM_EVENTS)
            event = cls._create_team_event(team_event, team)
            events.append(event)
        
        # 特別な日のイベント（月初め、シーズン中盤など）
        if day % 30 == 0:  # 月初め
            special_event = cls._generate_monthly_event(team)
            if special_event:
                events.append(special_event)
        
        return events
    
    @classmethod
    def _select_event(cls) -> Optional[dict]:
        """重み付きでイベントを選択"""
        all_events = cls.POSITIVE_EVENTS + cls.NEGATIVE_EVENTS + cls.NEUTRAL_EVENTS
        
        # 重み付き選択
        total_weight = sum(e["weight"] for e in all_events)
        r = random.random() * total_weight
        
        cumulative = 0
        for event in all_events:
            cumulative += event["weight"]
            if r <= cumulative:
                # レアイベントは追加確率チェック
                if event.get("rare", False) and random.random() > 0.3:
                    return None
                return event
        
        return None
    
    @classmethod
    def _select_target_player(cls, team: Team, event_data: dict) -> Optional[Player]:
        """イベント対象選手を選択"""
        candidates = team.players
        
        # ポジションフィルター
        if "position_filter" in event_data:
            candidates = [p for p in candidates if p.position in event_data["position_filter"]]
        
        if not candidates:
            return None
        
        return random.choice(candidates)
    
    @classmethod
    def _create_event(cls, event_data: dict, player: Player, team: Team) -> GameEvent:
        """イベントオブジェクトを生成"""
        description = event_data["description"].format(player=player.name)
        
        return GameEvent(
            event_type=event_data["type"],
            target_player=player,
            target_team=team,
            title=event_data["title"],
            description=description,
            effects=event_data["effects"].copy()
        )
    
    @classmethod
    def _create_team_event(cls, event_data: dict, team: Team) -> GameEvent:
        """チームイベントを生成"""
        return GameEvent(
            event_type=event_data["type"],
            target_player=None,
            target_team=team,
            title=event_data["title"],
            description=event_data["description"],
            effects=event_data["effects"].copy()
        )
    
    @classmethod
    def _generate_monthly_event(cls, team: Team) -> Optional[GameEvent]:
        """月次イベントを生成"""
        monthly_events = [
            {
                "type": EventType.CONTRACT_BONUS,
                "title": "月間MVP！",
                "description": "チームの月間MVPが選ばれた！",
                "effects": {"motivation": 20}
            },
            {
                "type": EventType.SCOUTING_REPORT,
                "title": "スカウティング報告",
                "description": "相手チームの分析報告が完了",
                "effects": {"motivation": 5}
            }
        ]
        
        event_data = random.choice(monthly_events)
        best_player = max(team.players, 
                        key=lambda p: p.record.hits + p.record.home_runs * 2 + p.record.wins * 3,
                        default=None)
        
        if best_player:
            return GameEvent(
                event_type=event_data["type"],
                target_player=best_player,
                target_team=team,
                title=event_data["title"],
                description=f"{best_player.name}が{event_data['description']}",
                effects=event_data["effects"].copy()
            )
        return None


class SeasonEvent:
    """シーズン特別イベント"""
    
    @staticmethod
    def all_star_game(central_teams: List[Team], pacific_teams: List[Team]) -> dict:
        """オールスターゲーム"""
        # 各リーグのベスト選手を選出
        central_stars = SeasonEvent._select_all_stars(central_teams)
        pacific_stars = SeasonEvent._select_all_stars(pacific_teams)
        
        # 簡易シミュレーション
        central_score = random.randint(2, 8)
        pacific_score = random.randint(2, 8)
        
        winner = "セ・リーグ" if central_score > pacific_score else "パ・リーグ"
        if central_score == pacific_score:
            winner = "引き分け"
        
        return {
            "title": "オールスターゲーム",
            "central_stars": central_stars,
            "pacific_stars": pacific_stars,
            "central_score": central_score,
            "pacific_score": pacific_score,
            "winner": winner,
            "mvp": random.choice(central_stars + pacific_stars)
        }
    
    @staticmethod
    def _select_all_stars(teams: List[Team], count: int = 9) -> List[Player]:
        """オールスター選手を選出"""
        all_players = []
        for team in teams:
            all_players.extend(team.players)
        
        # 成績順にソート
        batters = [p for p in all_players if p.position != Position.PITCHER]
        pitchers = [p for p in all_players if p.position == Position.PITCHER]
        
        batters.sort(key=lambda p: p.record.batting_average, reverse=True)
        pitchers.sort(key=lambda p: p.record.era if p.record.innings_pitched > 0 else 99)
        
        return batters[:6] + pitchers[:3]
    
    @staticmethod
    def draft_lottery() -> List[int]:
        """ドラフト抽選順を決定"""
        order = list(range(1, 13))
        random.shuffle(order)
        return order
    
    @staticmethod
    def golden_glove_awards(teams: List[Team]) -> dict:
        """ゴールデングラブ賞"""
        positions = [Position.CATCHER, Position.FIRST, Position.SECOND, 
                    Position.THIRD, Position.SHORTSTOP, Position.OUTFIELD, Position.PITCHER]
        
        awards = {}
        all_players = []
        for team in teams:
            all_players.extend(team.players)
        
        for pos in positions:
            candidates = [p for p in all_players if p.position == pos]
            if candidates:
                # 守備力でソート
                winner = max(candidates, key=lambda p: p.stats.fielding + p.stats.arm)
                awards[pos.value] = winner
        
        return awards


@dataclass
class TitleRace:
    """タイトル争い状況"""
    category: str
    leader: Player
    leader_value: float
    chasers: List[tuple]  # (Player, value)
    
    def get_description(self) -> str:
        """タイトル争い状況の説明を取得"""
        desc = f"【{self.category}】\n"
        desc += f"1位: {self.leader.name} - {self.leader_value:.3f}\n"
        for i, (player, value) in enumerate(self.chasers[:3], 2):
            desc += f"{i}位: {player.name} - {value:.3f}\n"
        return desc


class TitleTracker:
    """タイトル争い追跡システム"""
    
    @staticmethod
    def get_batting_title_race(teams: List[Team], min_at_bats: int = 100) -> TitleRace:
        """首位打者争い"""
        all_batters = []
        for team in teams:
            for p in team.players:
                if p.position != Position.PITCHER and p.record.at_bats >= min_at_bats:
                    all_batters.append((p, p.record.batting_average))
        
        if not all_batters:
            return None
        
        all_batters.sort(key=lambda x: x[1], reverse=True)
        leader = all_batters[0]
        
        return TitleRace(
            category="首位打者",
            leader=leader[0],
            leader_value=leader[1],
            chasers=all_batters[1:5]
        )
    
    @staticmethod
    def get_home_run_title_race(teams: List[Team]) -> TitleRace:
        """本塁打王争い"""
        all_batters = []
        for team in teams:
            for p in team.players:
                if p.position != Position.PITCHER:
                    all_batters.append((p, p.record.home_runs))
        
        if not all_batters:
            return None
        
        all_batters.sort(key=lambda x: x[1], reverse=True)
        leader = all_batters[0]
        
        return TitleRace(
            category="本塁打王",
            leader=leader[0],
            leader_value=float(leader[1]),
            chasers=all_batters[1:5]
        )
    
    @staticmethod
    def get_rbi_title_race(teams: List[Team]) -> TitleRace:
        """打点王争い"""
        all_batters = []
        for team in teams:
            for p in team.players:
                if p.position != Position.PITCHER:
                    all_batters.append((p, p.record.rbis))
        
        if not all_batters:
            return None
        
        all_batters.sort(key=lambda x: x[1], reverse=True)
        leader = all_batters[0]
        
        return TitleRace(
            category="打点王",
            leader=leader[0],
            leader_value=float(leader[1]),
            chasers=all_batters[1:5]
        )
    
    @staticmethod
    def get_era_title_race(teams: List[Team], min_innings: float = 50.0) -> TitleRace:
        """最優秀防御率争い"""
        all_pitchers = []
        for team in teams:
            for p in team.players:
                if p.position == Position.PITCHER and p.record.innings_pitched >= min_innings:
                    all_pitchers.append((p, p.record.era))
        
        if not all_pitchers:
            return None
        
        all_pitchers.sort(key=lambda x: x[1])  # 低い方が良い
        leader = all_pitchers[0]
        
        return TitleRace(
            category="最優秀防御率",
            leader=leader[0],
            leader_value=leader[1],
            chasers=all_pitchers[1:5]
        )
    
    @staticmethod
    def get_wins_title_race(teams: List[Team]) -> TitleRace:
        """最多勝争い"""
        all_pitchers = []
        for team in teams:
            for p in team.players:
                if p.position == Position.PITCHER:
                    all_pitchers.append((p, p.record.wins))
        
        if not all_pitchers:
            return None
        
        all_pitchers.sort(key=lambda x: x[1], reverse=True)
        leader = all_pitchers[0]
        
        return TitleRace(
            category="最多勝",
            leader=leader[0],
            leader_value=float(leader[1]),
            chasers=all_pitchers[1:5]
        )
    
    @staticmethod
    def get_strikeout_title_race(teams: List[Team]) -> TitleRace:
        """最多奪三振争い"""
        all_pitchers = []
        for team in teams:
            for p in team.players:
                if p.position == Position.PITCHER:
                    all_pitchers.append((p, p.record.strikeouts_pitched))
        
        if not all_pitchers:
            return None
        
        all_pitchers.sort(key=lambda x: x[1], reverse=True)
        leader = all_pitchers[0]
        
        return TitleRace(
            category="最多奪三振",
            leader=leader[0],
            leader_value=float(leader[1]),
            chasers=all_pitchers[1:5]
        )
    
    @staticmethod
    def get_saves_title_race(teams: List[Team]) -> TitleRace:
        """最多セーブ争い"""
        all_pitchers = []
        for team in teams:
            for p in team.players:
                if p.position == Position.PITCHER:
                    all_pitchers.append((p, p.record.saves))
        
        if not all_pitchers:
            return None
        
        all_pitchers.sort(key=lambda x: x[1], reverse=True)
        leader = all_pitchers[0]
        
        return TitleRace(
            category="最多セーブ",
            leader=leader[0],
            leader_value=float(leader[1]),
            chasers=all_pitchers[1:5]
        )
    
    @staticmethod
    def get_stolen_base_title_race(teams: List[Team]) -> TitleRace:
        """盗塁王争い"""
        all_batters = []
        for team in teams:
            for p in team.players:
                if p.position != Position.PITCHER:
                    all_batters.append((p, p.record.stolen_bases))
        
        if not all_batters:
            return None
        
        all_batters.sort(key=lambda x: x[1], reverse=True)
        leader = all_batters[0]
        
        return TitleRace(
            category="盗塁王",
            leader=leader[0],
            leader_value=float(leader[1]),
            chasers=all_batters[1:5]
        )
