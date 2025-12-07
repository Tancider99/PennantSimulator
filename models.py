# -*- coding: utf-8 -*-
"""
データモデル定義
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import datetime


class Position(Enum):
    PITCHER = "投手"
    CATCHER = "捕手"
    FIRST = "一塁手"
    SECOND = "二塁手"
    THIRD = "三塁手"
    SHORTSTOP = "遊撃手"
    OUTFIELD = "外野手"


class PitchType(Enum):
    STARTER = "先発"
    RELIEVER = "中継ぎ"
    CLOSER = "抑え"


class TeamLevel(Enum):
    FIRST = "一軍"
    SECOND = "二軍"
    THIRD = "三軍"


class PlayerStatus(Enum):
    ACTIVE = "支配下"
    FARM = "育成"


class League(Enum):
    CENTRAL = "セントラル"
    PACIFIC = "パシフィック"


class GameStatus(Enum):
    SCHEDULED = "未消化"
    IN_PROGRESS = "試合中"
    COMPLETED = "終了"


@dataclass
class GameResult:
    home_team_name: str
    away_team_name: str
    home_score: int
    away_score: int
    date: str
    game_number: int


@dataclass
class ScheduledGame:
    game_number: int
    date: str
    home_team_name: str
    away_team_name: str
    status: GameStatus = GameStatus.SCHEDULED
    home_score: int = 0
    away_score: int = 0
    
    @property
    def is_completed(self) -> bool:
        return self.status == GameStatus.COMPLETED
    
    @property
    def month(self) -> int:
        try:
            return int(self.date.split('-')[1])
        except:
            return 0
    
    @property
    def day(self) -> int:
        try:
            return int(self.date.split('-')[2])
        except:
            return 0
            
    @property
    def year(self) -> int:
        try:
            return int(self.date.split('-')[0])
        except:
            return 0

    def get_winner(self) -> Optional[str]:
        if not self.is_completed:
            return None
        if self.home_score > self.away_score:
            return self.home_team_name
        elif self.away_score > self.home_score:
            return self.away_team_name
        return None  # 引き分け

    def is_draw(self) -> bool:
        return self.is_completed and self.home_score == self.away_score

    def to_result(self) -> GameResult:
        return GameResult(
            home_team_name=self.home_team_name,
            away_team_name=self.away_team_name,
            home_score=self.home_score,
            away_score=self.away_score,
            date=self.date,
            game_number=self.game_number
        )


@dataclass
class PlayerStats:
    """選手能力値（OOTPスタイル & パワプロ風ランク対応）
    
    基本能力値は1〜99の範囲（球速を除く）
    ランク: S(90-99), A(80-89), B(70-79), C(60-69), D(50-59), E(40-49), F(30-39), G(1-29)
    """
    # ===== 打撃能力 (Batting Ratings) =====
    contact: int = 50      # ミート (Contact / Batting Average)
    gap: int = 50          # ギャップ (Gap Power / Doubles & Triples)
    power: int = 50        # パワー (Home Run Power)
    eye: int = 50          # 選球眼 (Eye / Walks)
    avoid_k: int = 50      # 三振回避 (Avoid K / Strikeouts)
    
    # ===== 投球能力 (Pitching Ratings) =====
    velocity: int = 145    # 球速 (Velocity) - km/h 実数値 (例: 130-165)
    stuff: int = 50        # 球威 (Stuff / Strikeouts)
    movement: int = 50     # ムービング (Movement / Home Runs Allowed)
    control: int = 50      # コントロール (Control / Walks Allowed)
    stamina: int = 50      # スタミナ (Stamina)
    
    # ===== 守備能力 (Fielding Ratings) =====
    # 内野 (Infield)
    inf_range: int = 50    # 守備範囲
    inf_arm: int = 50      # 肩力
    inf_error: int = 50    # エラー回避 (高いほどエラーしない)
    inf_dp: int = 50       # 併殺処理
    
    # 外野 (Outfield)
    of_range: int = 50     # 守備範囲
    of_arm: int = 50       # 肩力
    of_error: int = 50     # エラー回避
    
    # 捕手 (Catcher)
    catcher_ab: int = 50   # リード・キャッチング
    catcher_arm: int = 50  # 肩力・盗塁阻止
    
    # ===== 走塁能力 (Running Ratings) =====
    speed: int = 50        # 走力 (Speed)
    steal: int = 50        # 盗塁技術 (Stealing)
    baserunning: int = 50  # 走塁技術 (Baserunning)
    
    # ===== その他 =====
    bunt: int = 50         # バント (Sacrifice Bunt)
    mental: int = 50       # メンタル・回復 (Personality/Durability)
    injury_res: int = 50   # ケガしにくさ (Injury Resistance)
    
    # ===== 投手専用 =====
    breaking_balls: List[str] = field(default_factory=list)  # 持ち球リスト
    pitch_repertoire: Dict[str, int] = field(default_factory=dict)  # 球種別変化量
    
    # ===== 互換性・エイリアス用プロパティ =====
    @property
    def run(self) -> int: return self.speed
    @property
    def arm(self) -> int: 
        # ポジション不明時は最大値を返す
        return max(self.inf_arm, self.of_arm, self.catcher_arm)
    @property
    def fielding(self) -> int:
        return max(self.inf_range, self.of_range, self.catcher_ab)
    @property
    def catching(self) -> int:
        return max(self.inf_error, self.of_error)
    @property
    def breaking(self) -> int: return self.stuff  # 互換性のためStuffを返す
    
    # 互換性セッター (ランダム生成時のエラー回避)
    @run.setter
    def run(self, value): self.speed = value
    @arm.setter
    def arm(self, value): 
        self.inf_arm = value
        self.of_arm = value
        self.catcher_arm = value
    @fielding.setter
    def fielding(self, value):
        self.inf_range = value
        self.of_range = value
        self.catcher_ab = value
    @breaking.setter
    def breaking(self, value): self.stuff = value

    
    def overall_batting(self) -> float:
        """野手の総合値を計算"""
        # ミート、パワー、選球眼、走力、守備を総合
        defense = (self.inf_range + self.of_range + self.catcher_ab) / 3
        return (self.contact * 2 + self.power * 1.5 + self.eye + self.speed + defense) / 6.0
    
    def overall_pitching(self) -> float:
        """投手の総合値を計算"""
        # 球速(km/h)を1-99スケールに換算して評価に加える
        vel_rating = self.kmh_to_rating(self.velocity)
        return (vel_rating * 1.5 + self.stuff * 1.5 + self.movement + self.control * 2 + self.stamina) / 7.0
    
    def speed_to_kmh(self) -> int:
        """互換性維持: そのままvelocityを返す"""
        return self.velocity
    
    @staticmethod
    def kmh_to_rating(kmh: int) -> int:
        """km/hを1-99評価値に変換"""
        # 130km/h -> 1, 145km/h -> 50, 160km/h -> 99
        val = (kmh - 130) * 99 / 30
        return int(max(1, min(99, val)))
    
    def get_rank(self, value: int) -> str:
        """能力値をランクに変換"""
        if value >= 90: return "S"
        elif value >= 80: return "A"
        elif value >= 70: return "B"
        elif value >= 60: return "C"
        elif value >= 50: return "D"
        elif value >= 40: return "E"
        elif value >= 30: return "F"
        else: return "G"
    
    def get_rank_color(self, value: int) -> str:
        """ランクに応じた色コード"""
        if value >= 90: return "#FFD700"  # Gold (S)
        elif value >= 80: return "#FF4500"  # Red-Orange (A)
        elif value >= 70: return "#FFA500"  # Orange (B)
        elif value >= 60: return "#FFFF00"  # Yellow (C)
        elif value >= 50: return "#32CD32"  # Lime Green (D)
        elif value >= 40: return "#1E90FF"  # Dodger Blue (E)
        elif value >= 30: return "#4682B4"  # Steel Blue (F)
        return "#808080"  # Gray (G)

    def get_breaking_balls_display(self) -> str:
        if not self.breaking_balls: return "なし"
        return "、".join(self.breaking_balls)


@dataclass
class PlayerRecord:
    at_bats: int = 0
    hits: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0
    rbis: int = 0
    runs: int = 0
    walks: int = 0
    strikeouts: int = 0
    stolen_bases: int = 0
    caught_stealing: int = 0
    sacrifice_hits: int = 0
    sacrifice_flies: int = 0
    grounded_into_dp: int = 0
    
    games_pitched: int = 0
    wins: int = 0
    losses: int = 0
    saves: int = 0
    innings_pitched: float = 0.0
    earned_runs: int = 0
    hits_allowed: int = 0
    walks_allowed: int = 0
    strikeouts_pitched: int = 0
    home_runs_allowed: int = 0
    runs_allowed: int = 0
    
    @property
    def batting_average(self) -> float:
        return self.hits / self.at_bats if self.at_bats > 0 else 0.0
    
    @property
    def era(self) -> float:
        return (self.earned_runs * 9) / self.innings_pitched if self.innings_pitched > 0 else 0.0


@dataclass
class Player:
    name: str
    position: Position
    pitch_type: Optional[PitchType] = None
    stats: PlayerStats = field(default_factory=PlayerStats)
    record: PlayerRecord = field(default_factory=PlayerRecord)
    age: int = 25
    status: PlayerStatus = PlayerStatus.ACTIVE
    uniform_number: int = 0
    is_foreign: bool = False
    salary: int = 10000000
    years_pro: int = 0
    draft_round: int = 0
    
    is_developmental: bool = False
    team_level: 'TeamLevel' = None
    
    sub_positions: List[Position] = field(default_factory=list)
    # サブポジション適性値（0.0〜1.0）
    sub_position_ratings: Dict[str, float] = field(default_factory=dict)
    
    starter_aptitude: int = 50
    middle_aptitude: int = 50
    closer_aptitude: int = 50
    
    special_abilities: Optional[object] = None
    player_status: Optional[object] = None
    growth: Optional[object] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        # 必要であればここで初期化を行う
        pass

    def add_sub_position(self, pos: Position, rating: float = 0.7):
        """サブポジションを追加"""
        if pos != self.position and pos not in self.sub_positions:
            self.sub_positions.append(pos)
            self.sub_position_ratings[pos.value] = min(1.0, max(0.3, rating))

    def can_play_position(self, pos: Position) -> bool:
        """指定位置を守れるかどうか"""
        if self.position == pos:
            return True
        return pos in self.sub_positions
    
    def get_position_rating(self, pos: Position) -> float:
        """指定位置の適性値を取得（1.0が最高）"""
        if self.position == pos:
            return 1.0
        if pos in self.sub_positions:
            return self.sub_position_ratings.get(pos.value, 0.7)
        return 0.0

    @property
    def overall_rating(self) -> int:
        """総合評価 (1-999)"""
        if self.position == Position.PITCHER:
            return int(self.stats.overall_pitching() * 8 + 100)
        else:
            return int(self.stats.overall_batting() * 8 + 100)


@dataclass
class Team:
    name: str
    league: League
    players: List[Player] = field(default_factory=list)
    wins: int = 0
    losses: int = 0
    draws: int = 0
    current_lineup: List[int] = field(default_factory=list)
    starting_pitcher_idx: int = -1
    budget: int = 5000000000
    color: str = None
    abbr: str = None
    
    rotation: List[int] = field(default_factory=list)
    rotation_index: int = 0
    setup_pitchers: List[int] = field(default_factory=list)
    closer_idx: int = -1
    
    bench_batters: List[int] = field(default_factory=list)
    bench_pitchers: List[int] = field(default_factory=list)
    active_roster: List[int] = field(default_factory=list)
    farm_roster: List[int] = field(default_factory=list)
    
    def get_today_starter(self) -> Optional[Player]:
        if not self.rotation: return None
        idx = self.rotation[self.rotation_index % len(self.rotation)]
        if 0 <= idx < len(self.players): return self.players[idx]
        return None
        
    def get_roster_players(self) -> List[Player]:
        return [p for p in self.players if not p.is_developmental]
        
    def auto_set_bench(self):
        pass # Placeholder for external logic

    def get_closer(self) -> Optional[Player]:
        if 0 <= self.closer_idx < len(self.players): return self.players[self.closer_idx]
        return None
        
    def get_setup_pitcher(self) -> Optional[Player]:
        if self.setup_pitchers:
            idx = self.setup_pitchers[0]
            if 0 <= idx < len(self.players): return self.players[idx]
        return None
    
    @property
    def winning_percentage(self) -> float:
        total = self.wins + self.losses
        return self.wins / total if total > 0 else 0.0

@dataclass
class DraftProspect:
    name: str
    position: Position
    pitch_type: Optional[PitchType]
    stats: PlayerStats
    age: int
    high_school: str
    potential: int
    is_developmental: bool = False

@dataclass
class Schedule:
    """シーズン日程"""
    games: List[ScheduledGame] = field(default_factory=list)
    current_game_index: int = 0
    
    def get_next_game(self, team_name: str) -> Optional[ScheduledGame]:
        """指定チームの次の試合を取得"""
        for i in range(self.current_game_index, len(self.games)):
            game = self.games[i]
            if game.status == GameStatus.SCHEDULED:
                if game.home_team_name == team_name or game.away_team_name == team_name:
                    return game
        return None
    
    def get_team_games(self, team_name: str, status: Optional[GameStatus] = None) -> List[ScheduledGame]:
        """指定チームの試合を取得"""
        games = [g for g in self.games if g.home_team_name == team_name or g.away_team_name == team_name]
        if status:
            games = [g for g in games if g.status == status]
        return games
    
    def complete_game(self, game: ScheduledGame, home_score: int, away_score: int):
        """試合を完了"""
        game.status = GameStatus.COMPLETED
        game.home_score = home_score
        game.away_score = away_score

TEAM_COLORS = {
    "Tokyo Bravers": "#FF6600",
    "Osaka Thunders": "#FFD700",
    "Nagoya Sparks": "#005BAC",
    "Hiroshima Phoenix": "#C20000",
    "Yokohama Mariners": "#0055B3",
    "Shinjuku Spirits": "#009944",
    "Fukuoka Phoenix": "#FFF200",
    "Saitama Bears": "#003366",
    "Sendai Flames": "#800000",
    "Chiba Mariners": "#222222",
    "Sapporo Fighters": "#0066B3",
    "Kobe Buffaloes": "#1B1B1B",
}

TEAM_ABBRS = {
    "Tokyo Bravers": "TB",
    "Osaka Thunders": "OT",
    "Nagoya Sparks": "NS",
    "Hiroshima Phoenix": "HP",
    "Yokohama Mariners": "YM",
    "Shinjuku Spirits": "SS",
    "Fukuoka Phoenix": "FP",
    "Saitama Bears": "SB",
    "Sendai Flames": "SF",
    "Chiba Mariners": "CM",
    "Sapporo Fighters": "SF",
    "Kobe Buffaloes": "KB",
}