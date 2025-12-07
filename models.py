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
    """選手能力値（OOTPスタイル完全版）

    基本能力値は1〜200の範囲（20刻みで表示: 20=★1, 80=★4, 200=★10）
    OOTPでは20-80スケールだが、内部的には1-200で管理
    """
    # ===== 打撃能力 (Batting Ratings) =====
    contact: int = 100         # コンタクト - ヒット性の打球を打つ能力
    gap: int = 100             # ギャップパワー - 中距離打者能力（二塁打・三塁打）
    power: int = 100           # ホームランパワー - 長打力
    eye: int = 100             # 選球眼 - 四球を選ぶ能力
    avoid_k: int = 100         # 三振回避 - 三振しにくさ

    # ===== 走塁能力 (Running Ratings) =====
    speed: int = 100           # 走塁速度 - 足の速さ
    steal: int = 100           # 盗塁技術 - スタートの上手さ
    baserunning: int = 100     # 走塁判断 - 次の塁を狙う判断力

    # ===== バント能力 =====
    bunt_sac: int = 100        # 送りバント - 犠牲バントの上手さ
    bunt_hit: int = 100        # セーフティバント - セーフティバントの上手さ

    # ===== 守備能力 (Fielding Ratings) =====
    # 捕手 (Catcher)
    catcher_ability: int = 100 # 配球・フレーミング - リード・ブロック能力
    catcher_arm: int = 100     # 盗塁阻止能力 - 肩の強さ

    # 内野 (Infield)
    inf_range: int = 100       # 内野守備範囲 - 守備範囲の広さ
    inf_error: int = 100       # 内野守備技術 - エラー回避能力
    inf_arm: int = 100         # 内野肩の強さ - 送球の強さ
    turn_dp: int = 100         # ダブルプレー能力 - 併殺処理の上手さ

    # 外野 (Outfield)
    of_range: int = 100        # 外野守備範囲 - 守備範囲の広さ
    of_error: int = 100        # 外野守備技術 - エラー回避能力
    of_arm: int = 100          # 外野肩の強さ - 送球の強さ

    # ===== 投球能力 (Pitching Ratings) =====
    stuff: int = 100           # スタッフ - 持ち球の質（奪三振能力）
    movement: int = 100        # ムーブメント - 変化量とゴロ率
    control: int = 100         # コントロール - 制球力

    # ===== 投手追加能力 =====
    velocity: int = 145        # 球速 (km/h) - 130-165の実数値
    stamina: int = 100         # スタミナ - 持久力
    hold_runners: int = 100    # ホールドランナーズ - 走者を釘付けにする能力
    gb_tendency: int = 50      # ゴロ傾向 (0-100) - 50が中立、高いほどゴロ投手

    # ===== その他能力 =====
    durability: int = 100      # 耐久性 - ケガしにくさ
    work_ethic: int = 100      # 練習態度 - 成長に影響
    intelligence: int = 100    # 野球IQ - 判断力全般

    # ===== 投手専用 =====
    pitches: Dict[str, int] = field(default_factory=dict)  # 球種と能力値 {"ストレート": 150, "スライダー": 120}

    # ===== 互換性・エイリアス =====
    @property
    def run(self) -> int: return self.speed
    @property
    def arm(self) -> int:
        return max(self.inf_arm, self.of_arm, self.catcher_arm)
    @property
    def fielding(self) -> int:
        return max(self.inf_range, self.of_range, self.catcher_ability)
    @property
    def catching(self) -> int:
        return max(self.inf_error, self.of_error)
    @property
    def breaking(self) -> int: return self.stuff
    @property
    def bunt(self) -> int: return self.bunt_sac
    @property
    def mental(self) -> int: return self.intelligence
    @property
    def injury_res(self) -> int: return self.durability
    @property
    def injury_resistance(self) -> int: return self.durability
    @property
    def recovery(self) -> int: return self.durability
    @property
    def trajectory(self) -> int: return min(4, max(1, self.power // 50 + 1))
    @property
    def chance(self) -> int: return self.intelligence
    @property
    def vs_left_batter(self) -> int: return self.contact
    @property
    def vs_left_pitcher(self) -> int: return self.stuff
    @property
    def vs_pinch(self) -> int: return self.intelligence
    @property
    def quick(self) -> int: return self.hold_runners
    @property
    def stability(self) -> int: return self.control
    @property
    def inf_dp(self) -> int: return self.turn_dp
    @property
    def catcher_ab(self) -> int: return self.catcher_ability
    @property
    def breaking_balls(self) -> List[str]: return list(self.pitches.keys()) if self.pitches else []

    # 互換性セッター
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
        self.catcher_ability = value
    @breaking.setter
    def breaking(self, value): self.stuff = value
    @bunt.setter
    def bunt(self, value): self.bunt_sac = value

    def to_star_rating(self, value: int) -> float:
        """能力値を★評価に変換 (0.5-5.0)"""
        return max(0.5, min(5.0, value / 40))

    def to_display_value(self, value: int) -> int:
        """能力値を20-80スケール表示に変換"""
        return max(20, min(80, value // 2.5 + 20))

    def overall_batting(self) -> float:
        """野手の総合値を計算"""
        batting = (self.contact * 2 + self.gap * 1.5 + self.power * 1.5 + self.eye + self.avoid_k) / 7
        running = (self.speed + self.steal + self.baserunning) / 3
        defense = (self.inf_range + self.of_range + self.catcher_ability) / 3
        return (batting * 0.5 + running * 0.2 + defense * 0.3)

    def overall_pitching(self) -> float:
        """投手の総合値を計算"""
        vel_rating = self.kmh_to_rating(self.velocity)
        return (self.stuff * 2 + self.movement * 1.5 + self.control * 2 + vel_rating + self.stamina * 0.5) / 7

    def speed_to_kmh(self) -> int:
        """球速をkm/hで返す"""
        return self.velocity

    @staticmethod
    def kmh_to_rating(kmh: int) -> int:
        """km/hを1-200評価値に変換"""
        # 130km/h -> 20, 145km/h -> 100, 160km/h -> 180
        val = (kmh - 130) * 160 / 30 + 20
        return int(max(20, min(200, val)))

    def get_rank(self, value: int) -> str:
        """能力値をランクに変換（1-200スケール）"""
        if value >= 180: return "S"
        elif value >= 160: return "A"
        elif value >= 140: return "B"
        elif value >= 120: return "C"
        elif value >= 100: return "D"
        elif value >= 80: return "E"
        elif value >= 60: return "F"
        else: return "G"

    def get_rank_color(self, value: int) -> str:
        """ランクに応じた色コード（1-200スケール）"""
        if value >= 180: return "#FFD700"  # Gold (S)
        elif value >= 160: return "#FF4500"  # Red-Orange (A)
        elif value >= 140: return "#FFA500"  # Orange (B)
        elif value >= 120: return "#FFFF00"  # Yellow (C)
        elif value >= 100: return "#32CD32"  # Lime Green (D)
        elif value >= 80: return "#1E90FF"  # Dodger Blue (E)
        elif value >= 60: return "#4682B4"  # Steel Blue (F)
        return "#808080"  # Gray (G)

    def get_star_display(self, value: int) -> str:
        """能力値を★表示に変換"""
        stars = self.to_star_rating(value)
        full = int(stars)
        half = 1 if stars - full >= 0.5 else 0
        return "★" * full + ("☆" if half else "")

    def get_breaking_balls_display(self) -> str:
        if not self.pitches: return "なし"
        return "、".join(self.pitches.keys())


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
    active_roster: List[int] = field(default_factory=list)  # 一軍登録選手（最大31人）
    farm_roster: List[int] = field(default_factory=list)    # 二軍選手

    # 出場登録上限
    ACTIVE_ROSTER_LIMIT = 31

    def get_today_starter(self) -> Optional[Player]:
        if not self.rotation: return None
        idx = self.rotation[self.rotation_index % len(self.rotation)]
        if 0 <= idx < len(self.players): return self.players[idx]
        return None

    def get_roster_players(self) -> List[Player]:
        """支配下選手を取得"""
        return [p for p in self.players if not p.is_developmental]

    def get_active_roster_players(self) -> List[Player]:
        """一軍登録選手を取得"""
        return [self.players[i] for i in self.active_roster if 0 <= i < len(self.players)]

    def get_farm_roster_players(self) -> List[Player]:
        """二軍選手を取得"""
        return [self.players[i] for i in self.farm_roster if 0 <= i < len(self.players)]

    def get_active_roster_count(self) -> int:
        """一軍登録人数を取得"""
        return len(self.active_roster)

    def can_add_to_active_roster(self) -> bool:
        """一軍に追加可能かどうか"""
        return len(self.active_roster) < self.ACTIVE_ROSTER_LIMIT

    def add_to_active_roster(self, player_idx: int) -> bool:
        """一軍に選手を追加"""
        if not self.can_add_to_active_roster():
            return False
        if player_idx in self.active_roster:
            return False
        if player_idx in self.farm_roster:
            self.farm_roster.remove(player_idx)
        self.active_roster.append(player_idx)
        return True

    def remove_from_active_roster(self, player_idx: int) -> bool:
        """一軍から選手を外す（二軍へ）"""
        if player_idx not in self.active_roster:
            return False
        self.active_roster.remove(player_idx)
        if player_idx not in self.farm_roster:
            self.farm_roster.append(player_idx)
        return True

    def auto_set_bench(self):
        """ベンチメンバーを自動設定"""
        # スタメン・ローテ・中継ぎ・抑え以外の一軍メンバーをベンチに
        assigned = set(self.current_lineup + self.rotation + self.setup_pitchers)
        if self.closer_idx >= 0:
            assigned.add(self.closer_idx)

        self.bench_batters = []
        self.bench_pitchers = []

        for idx in self.active_roster:
            if idx not in assigned and 0 <= idx < len(self.players):
                p = self.players[idx]
                if p.position.value == "投手":
                    self.bench_pitchers.append(idx)
                else:
                    self.bench_batters.append(idx)

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