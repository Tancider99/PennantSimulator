# -*- coding: utf-8 -*-
"""
超強化版試合エンジン - 物理演算ベースの超現実的な試合シミュレーション
"""
import random
import math
from enum import Enum
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
from models import Team, Player, Position, PitchType
from physics_engine import (
    PhysicsEngine, AtBatSimulator, BattedBallData, HitResult,
    OutfieldCatchResult, get_physics_engine, get_at_bat_simulator,
    OUTFIELD_FENCE_CENTER, FENCE_HEIGHT,
    GROUNDBALL_MAX_ANGLE, LINEDRIVE_MAX_ANGLE, FLYBALL_MIN_ANGLE,
    MAX_EXIT_VELOCITY, AVG_EXIT_VELOCITY, MIN_EXIT_VELOCITY, OPTIMAL_HR_ANGLE
)


class Weather(Enum):
    """天候"""
    SUNNY = ("晴れ", 1.0, 0.0)
    CLOUDY = ("曇り", 0.98, 0.05)
    RAIN = ("雨", 0.92, 0.15)
    DOME = ("ドーム", 1.0, 0.0)
    WINDY = ("強風", 1.05, 0.1)
    HOT = ("猛暑", 0.95, 0.08)
    COLD = ("寒い", 0.93, 0.05)
    
    def __init__(self, display_name: str, hit_modifier: float, error_modifier: float):
        self.display_name = display_name
        self.hit_modifier = hit_modifier
        self.error_modifier = error_modifier


class Stadium(Enum):
    """球場"""
    TOKYO_DOME = ("東京ドーム", 1.15, True, "巨人")
    JINGU = ("神宮球場", 1.10, False, "ヤクルト")
    MAZDA = ("マツダスタジアム", 0.95, False, "広島")
    NAGOYA_DOME = ("バンテリンドーム", 0.90, True, "中日")
    KOSHIEN = ("甲子園", 0.98, False, "阪神")
    YOKOHAMA = ("横浜スタジアム", 1.08, False, "DeNA")
    PAYPAL_DOME = ("PayPayドーム", 1.05, True, "ソフトバンク")
    KYOCERA_DOME = ("京セラドーム", 0.92, True, "オリックス")
    RAKUTEN_SEIMEI = ("楽天モバイルパーク", 1.00, False, "楽天")
    ZOZO_MARINE = ("ZOZOマリン", 1.12, False, "ロッテ")
    SAPPORO_DOME = ("エスコンフィールド", 1.02, False, "日本ハム")
    BELLUNA_DOME = ("ベルーナドーム", 1.08, True, "西武")
    
    def __init__(self, display_name: str, hr_factor: float, is_dome: bool, home_team: str):
        self.display_name = display_name
        self.hr_factor = hr_factor  # ホームラン出やすさ
        self.is_dome = is_dome
        self.home_team = home_team


class BatResult(Enum):
    """打席結果の詳細タイプ"""
    HOME_RUN = "ホームラン"
    TRIPLE = "三塁打"
    DOUBLE = "二塁打"
    SINGLE = "シングルヒット"
    INFIELD_SINGLE = "内野安打"
    BUNT_HIT = "バントヒット"
    WALK = "四球"
    HIT_BY_PITCH = "死球"
    STRIKEOUT_SWINGING = "空振り三振"
    STRIKEOUT_LOOKING = "見逃し三振"
    GROUNDOUT = "ゴロアウト"
    FLYOUT = "フライアウト"
    LINEOUT = "ライナーアウト"
    POPOUT = "ファウルフライ"
    DOUBLE_PLAY = "併殺打"
    SACRIFICE_FLY = "犠牲フライ"
    SACRIFICE_BUNT = "犠打"
    ERROR = "エラー出塁"
    FIELDERS_CHOICE = "野選"
    
    
class PitchResult(Enum):
    """投球結果"""
    BALL = "ボール"
    STRIKE_CALLED = "見逃しストライク"
    STRIKE_SWINGING = "空振り"
    FOUL = "ファウル"
    IN_PLAY = "打球"


@dataclass
class AtBatDetail:
    """打席の詳細情報"""
    batter: Player
    pitcher: Player
    result: BatResult
    pitch_count: int
    runs_scored: int
    runners_advanced: List[int]
    description: str
    is_dramatic: bool = False


@dataclass
class GameMoment:
    """試合の重要場面"""
    inning: int
    is_top: bool
    outs: int
    runners: List[bool]
    score_diff: int
    description: str
    drama_level: int  # 1-10


class BreakingBall(Enum):
    """変化球タイプ"""
    SLIDER = ("スライダー", 0.95, 1.05)
    CURVE = ("カーブ", 0.90, 1.10)
    FORK = ("フォーク", 1.05, 1.00)
    CHANGE_UP = ("チェンジアップ", 0.92, 1.08)
    CUTTER = ("カットボール", 0.98, 1.02)
    SINKER = ("シンカー", 0.88, 1.12)
    SHOOT = ("シュート", 0.93, 1.05)
    KNUCKLE = ("ナックル", 0.80, 1.20)
    SPLITTER = ("スプリット", 1.03, 0.97)
    TWO_SEAM = ("ツーシーム", 0.96, 1.04)
    
    def __init__(self, display_name: str, strikeout_mod: float, groundball_mod: float):
        self.display_name = display_name
        self.strikeout_mod = strikeout_mod
        self.groundball_mod = groundball_mod


class CommentaryGenerator:
    """実況・解説生成システム"""
    
    HOME_RUN_COMMENTS = [
        "{batter}、打った！大きい！入った〜！ホームラン！",
        "{batter}の打球が舞い上がる！これは入った！第{hr_count}号ホームラン！",
        "甘く入った！完璧に捉えた！{batter}のホームラン！",
        "バックスクリーンに放り込んだ！{batter}！値千金のホームラン！",
        "{batter}、振り抜いた！ライトスタンドへ一直線！ホームラン！",
    ]
    
    STRIKEOUT_COMMENTS = [
        "{pitcher}、三振を奪った！{batter}手が出ず！",
        "空振り三振！{pitcher}の変化球にバットが回る！",
        "{pitcher}、素晴らしい！{batter}を三振に斬った！",
        "外角低めに決まって三振！{pitcher}絶好調！",
        "見逃し三振！{batter}、動けなかった！",
    ]
    
    CLUTCH_HIT_COMMENTS = [
        "打った！{batter}！タイムリーヒット！{runs}点が入る！",
        "これは大きい！{batter}の値千金の一打！",
        "勝負強い！{batter}がここで打った！",
        "さすが{batter}！チャンスで決める！",
    ]
    
    DRAMATIC_MOMENTS = [
        "球場が揺れる！この瞬間を見逃すな！",
        "手に汗握る展開！どうなる！？",
        "逆転のチャンス！ここが勝負どころ！",
        "ピンチを迎えた{pitcher}！踏ん張れるか！？",
    ]
    
    DOUBLE_PLAY_COMMENTS = [
        "{batter}、痛恨の併殺打！ピンチを脱した！",
        "ゲッツー！これで流れが変わるか！？",
        "4-6-3のダブルプレー！見事な連携！",
    ]
    
    ERROR_COMMENTS = [
        "あ〜っと！エラー！{fielder}が弾いた！",
        "まさかの失策！{fielder}痛い！",
        "送球が逸れた！これは記録はエラー！",
    ]
    
    @classmethod
    def generate_home_run_comment(cls, batter: Player, hr_count: int, runners: int) -> str:
        comment = random.choice(cls.HOME_RUN_COMMENTS)
        return comment.format(batter=batter.name, hr_count=hr_count)
    
    @classmethod
    def generate_strikeout_comment(cls, batter: Player, pitcher: Player) -> str:
        comment = random.choice(cls.STRIKEOUT_COMMENTS)
        return comment.format(batter=batter.name, pitcher=pitcher.name)
    
    @classmethod
    def generate_clutch_comment(cls, batter: Player, runs: int) -> str:
        comment = random.choice(cls.CLUTCH_HIT_COMMENTS)
        return comment.format(batter=batter.name, runs=runs)


class AdvancedGameEngine:
    """超強化版試合エンジン - 物理演算ベース"""
    
    def __init__(self, home_team: Team, away_team: Team, 
                 stadium: Stadium = None, weather: Weather = None):
        self.home_team = home_team
        self.away_team = away_team
        
        # 物理エンジン初期化
        self.physics_engine = get_physics_engine()
        self.at_bat_simulator = get_at_bat_simulator()
        
        # 球場設定（ホームチーム基準）
        self.stadium = stadium or self._get_team_stadium(home_team.name)
        
        # 天候設定
        if self.stadium.is_dome:
            self.weather = Weather.DOME
        else:
            self.weather = weather or random.choice([
                Weather.SUNNY, Weather.CLOUDY, Weather.SUNNY, 
                Weather.WINDY, Weather.SUNNY
            ])
        
        # 物理エンジンに天候を設定
        self._setup_physics_weather()
        
        # スコア
        self.home_score = 0
        self.away_score = 0
        self.inning = 1
        self.is_top = True  # True=表, False=裏
        self.outs = 0
        self.runners = [False, False, False]  # 1塁, 2塁, 3塁
        
        # 打順管理
        self.home_batter_index = 0
        self.away_batter_index = 0
        
        # 投手管理
        self.home_current_pitcher_idx = home_team.starting_pitcher_idx
        self.away_current_pitcher_idx = away_team.starting_pitcher_idx
        self.home_pitch_count = 0
        self.away_pitch_count = 0
        self.home_pitchers_used = []
        self.away_pitchers_used = []
        
        # ログ
        self.log = []
        self.detailed_log = []
        self.key_moments: List[GameMoment] = []
        self.inning_scores = {"home": [], "away": []}
        
        # 統計
        self.total_hits = {"home": 0, "away": 0}
        self.total_errors = {"home": 0, "away": 0}
    
    def _setup_physics_weather(self):
        """物理エンジンに天候条件を設定"""
        if self.weather == Weather.DOME:
            self.physics_engine.set_weather(wind_x=0, wind_y=0, temp=25, humidity=50, altitude=0)
        elif self.weather == Weather.WINDY:
            # 風向きをランダムに設定 (センター方向への追い風 or 向かい風)
            wind_strength = random.uniform(3, 8)  # m/s
            wind_direction = random.choice([-1, 1])  # 追い風か向かい風
            self.physics_engine.set_weather(
                wind_x=random.uniform(-2, 2),
                wind_y=wind_direction * wind_strength,
                temp=22, humidity=55, altitude=0
            )
        elif self.weather == Weather.HOT:
            self.physics_engine.set_weather(wind_x=0.5, wind_y=0.5, temp=35, humidity=70, altitude=0)
        elif self.weather == Weather.COLD:
            self.physics_engine.set_weather(wind_x=1, wind_y=0, temp=8, humidity=40, altitude=0)
        elif self.weather == Weather.RAIN:
            self.physics_engine.set_weather(wind_x=0, wind_y=0, temp=18, humidity=95, altitude=0)
        else:
            # SUNNY, CLOUDY
            self.physics_engine.set_weather(wind_x=0.3, wind_y=0.3, temp=25, humidity=55, altitude=0)
        self.total_errors = {"home": 0, "away": 0}
        
    def _get_team_stadium(self, team_name: str) -> Stadium:
        """チーム名から本拠地球場を取得"""
        stadium_map = {
            "読売ジャイアンツ": Stadium.TOKYO_DOME,
            "東京ヤクルトスワローズ": Stadium.JINGU,
            "広島東洋カープ": Stadium.MAZDA,
            "中日ドラゴンズ": Stadium.NAGOYA_DOME,
            "阪神タイガース": Stadium.KOSHIEN,
            "横浜DeNAベイスターズ": Stadium.YOKOHAMA,
            "福岡ソフトバンクホークス": Stadium.PAYPAL_DOME,
            "オリックス・バファローズ": Stadium.KYOCERA_DOME,
            "東北楽天ゴールデンイーグルス": Stadium.RAKUTEN_SEIMEI,
            "千葉ロッテマリーンズ": Stadium.ZOZO_MARINE,
            "北海道日本ハムファイターズ": Stadium.SAPPORO_DOME,
            "埼玉西武ライオンズ": Stadium.BELLUNA_DOME,
        }
        return stadium_map.get(team_name, Stadium.TOKYO_DOME)
    
    def _get_condition_modifier(self, player: Player) -> float:
        """選手のコンディション補正を取得"""
        if player.player_status is None:
            return 1.0
        return player.player_status.condition.multiplier
    
    def _get_ability_modifier(self, player: Player, ability_name: str) -> float:
        """特殊能力による補正を取得"""
        if player.special_abilities is None:
            return 0
        
        from special_abilities import SpecialAbility
        
        modifier = 0
        abilities = player.special_abilities
        
        # 打撃系
        if ability_name == "clutch":
            if abilities.has_ability(SpecialAbility.CLUTCH):
                modifier += 0.15
            if abilities.has_ability(SpecialAbility.WEAK_CLUTCH):
                modifier -= 0.15
        
        elif ability_name == "power":
            if abilities.has_ability(SpecialAbility.POWER_HITTER):
                modifier += 0.10
            if abilities.has_ability(SpecialAbility.POOR_POWER):
                modifier -= 0.10
        
        elif ability_name == "contact":
            if abilities.has_ability(SpecialAbility.CONTACT_HITTER):
                modifier += 0.08
            if abilities.has_ability(SpecialAbility.POOR_CONTACT):
                modifier -= 0.08
        
        # 投球系
        elif ability_name == "pinch":
            if abilities.has_ability(SpecialAbility.PINCH):
                modifier += 0.12
            if abilities.has_ability(SpecialAbility.WEAK_PINCH):
                modifier -= 0.12
        
        elif ability_name == "strikeout":
            if abilities.has_ability(SpecialAbility.STRIKEOUT):
                modifier += 0.08
        
        return modifier
    
    def _is_clutch_situation(self) -> bool:
        """チャンス/ピンチ場面かどうか"""
        runners_on = sum(1 for r in self.runners if r)
        score_diff = abs(self.home_score - self.away_score)
        
        # 得点圏にランナー && 接戦
        return (self.runners[1] or self.runners[2]) and score_diff <= 3
    
    def _calculate_hit_probability(self, batter: Player, pitcher: Player) -> float:
        """打率計算（詳細版）"""
        # 基本能力値
        batter_skill = (batter.stats.contact * 2 + batter.stats.power) / 3
        pitcher_skill = (pitcher.stats.control * 2 + pitcher.stats.speed + pitcher.stats.breaking) / 4
        
        # 基本打率
        base_prob = 0.18 + (batter_skill - pitcher_skill) * 0.015
        
        # コンディション補正
        base_prob *= self._get_condition_modifier(batter)
        base_prob /= max(0.7, self._get_condition_modifier(pitcher))
        
        # チャンス補正
        if self._is_clutch_situation():
            base_prob += self._get_ability_modifier(batter, "clutch")
            base_prob -= self._get_ability_modifier(pitcher, "pinch")
        
        # 天候補正
        base_prob *= self.weather.hit_modifier
        
        # 範囲制限
        return max(0.05, min(0.45, base_prob))
    
    def _calculate_hr_probability(self, batter: Player, pitcher: Player) -> float:
        """ホームラン確率計算"""
        power_factor = batter.stats.power / 20  # 0.0 ~ 1.0
        base_hr_prob = 0.02 + power_factor * 0.05
        
        # パワーヒッター補正
        base_hr_prob *= (1 + self._get_ability_modifier(batter, "power"))
        
        # 球場補正
        base_hr_prob *= self.stadium.hr_factor
        
        # コンディション補正
        base_hr_prob *= self._get_condition_modifier(batter)
        
        return max(0.01, min(0.15, base_hr_prob))
    
    def _calculate_strikeout_probability(self, batter: Player, pitcher: Player) -> float:
        """三振確率計算"""
        base_k_prob = 0.15 + (pitcher.stats.speed - batter.stats.contact) * 0.01
        base_k_prob += (pitcher.stats.breaking / 20) * 0.05
        
        # 三振能力補正
        base_k_prob += self._get_ability_modifier(pitcher, "strikeout")
        
        # コンタクトヒッター補正（三振しにくい）
        base_k_prob -= self._get_ability_modifier(batter, "contact") * 0.5
        
        return max(0.05, min(0.35, base_k_prob))
    
    def _calculate_walk_probability(self, batter: Player, pitcher: Player) -> float:
        """四球確率計算"""
        control_factor = pitcher.stats.control / 20
        base_walk = 0.12 - control_factor * 0.06
        
        # 選球眼補正
        from special_abilities import SpecialAbility
        if batter.special_abilities and batter.special_abilities.has_ability(SpecialAbility.PATIENT):
            base_walk += 0.04
        
        # ノーコン補正
        if pitcher.special_abilities and pitcher.special_abilities.has_ability(SpecialAbility.WILD_PITCH):
            base_walk += 0.05
        
        return max(0.03, min(0.15, base_walk))
    
    def _calculate_error_probability(self) -> float:
        """エラー確率計算"""
        base_error = 0.015
        base_error += self.weather.error_modifier
        return base_error
    
    def _setup_outfield_defense(self, fielding_team: Team):
        """外野守備の設定"""
        # 外野手を探す
        lf_stats = cf_stats = rf_stats = None
        
        for i, player in enumerate(fielding_team.players):
            if player.position == Position.OUTFIELD:
                # 簡易的に3人の外野手を設定
                stats_dict = {
                    'run': player.stats.run,
                    'fielding': player.stats.fielding,
                    'arm': player.stats.arm
                }
                if lf_stats is None:
                    lf_stats = stats_dict
                elif cf_stats is None:
                    cf_stats = stats_dict
                elif rf_stats is None:
                    rf_stats = stats_dict
        
        self.physics_engine.set_outfielders(lf_stats, cf_stats, rf_stats)
    
    def _generate_batted_ball(self, batter: Player, pitcher: Player) -> BattedBallData:
        """物理演算ベースで打球を生成"""
        # 打者の能力値
        contact = batter.stats.contact
        power = batter.stats.power
        trajectory = getattr(batter.stats, 'trajectory', 2)  # 弾道 (1-4)
        
        # 投手の能力値
        p_speed = pitcher.stats.speed
        p_breaking = pitcher.stats.breaking
        p_control = pitcher.stats.control
        
        # コンディション補正
        batter_condition = self._get_condition_modifier(batter)
        pitcher_condition = self._get_condition_modifier(pitcher)
        
        # チャンス補正
        clutch_bonus = 0
        if self._is_clutch_situation():
            clutch_bonus = self._get_ability_modifier(batter, "clutch")
        
        # 芯を捉えた度合い (コンタクト能力と投手の球威/変化球に依存)
        contact_difficulty = (p_speed - 10 + p_breaking - 10) / 20
        base_quality = 0.4 + (contact - 10) * 0.025 - contact_difficulty * 0.1
        base_quality = base_quality * batter_condition / pitcher_condition
        base_quality += clutch_bonus * 0.1
        
        # ベータ分布でコンタクト品質を生成
        alpha = max(1.5, 2.0 + (contact - 12) * 0.2)
        beta = max(1.5, 3.5 - (contact - 12) * 0.1)
        contact_quality = random.betavariate(alpha, beta) * min(1.2, max(0.8, base_quality / 0.5))
        contact_quality = max(0.05, min(1.0, contact_quality))
        
        # 打球速度の計算 (パワーとコンタクト品質に依存)
        if contact_quality > 0.75:
            # 完璧なコンタクト - バレルゾーン
            base_velo = AVG_EXIT_VELOCITY + (power - 10) * 2.5
            exit_velocity = base_velo * (0.85 + contact_quality * 0.2)
        elif contact_quality > 0.45:
            # 良いコンタクト
            base_velo = 115 + (power - 10) * 2.0
            exit_velocity = base_velo * (0.75 + contact_quality * 0.3)
        else:
            # 芯を外した
            base_velo = 80 + (power - 10) * 1.0
            exit_velocity = base_velo * (0.6 + contact_quality * 0.5)
        
        # 球場補正 (ドームは打球が伸びやすい)
        exit_velocity *= (0.98 + self.stadium.hr_factor * 0.02)
        
        # ランダム変動
        exit_velocity += random.gauss(0, 4)
        exit_velocity = max(MIN_EXIT_VELOCITY, min(MAX_EXIT_VELOCITY, exit_velocity))
        
        # 打球角度の計算 (弾道タイプとコンタクト位置に依存)
        trajectory_base = {1: 0, 2: 8, 3: 14, 4: 20}.get(trajectory, 10)
        
        if contact_quality > 0.7:
            # 芯を捉えると最適な角度になりやすい
            target_angle = OPTIMAL_HR_ANGLE if power >= 15 else trajectory_base + 8
            launch_angle = target_angle + random.gauss(0, 5)
        elif contact_quality > 0.4:
            launch_angle = trajectory_base + random.gauss(3, 9)
        else:
            # 芯を外すとゴロかポップアップ
            if random.random() < 0.55:
                launch_angle = random.gauss(-3, 7)  # ゴロ
            else:
                launch_angle = random.gauss(48, 10)  # ポップアップ
        
        launch_angle = max(-15, min(65, launch_angle))
        
        # 打球方向
        pull_tendency = getattr(batter.stats, 'pull', 0)
        spray_angle = random.gauss(pull_tendency * 1.2, 20)
        spray_angle = max(-45, min(45, spray_angle))
        
        # 回転数
        if launch_angle > 20:
            spin_rate = 2200 + int(launch_angle * 22) + random.randint(-200, 200)
        elif launch_angle > 5:
            spin_rate = 1800 + int(launch_angle * 18) + random.randint(-200, 200)
        else:
            spin_rate = 900 + random.randint(-200, 200)
        
        # 打球タイプ判定
        if launch_angle < GROUNDBALL_MAX_ANGLE:
            hit_type = "ground"
        elif launch_angle < LINEDRIVE_MAX_ANGLE:
            hit_type = "line"
        elif launch_angle < FLYBALL_MIN_ANGLE + 18:
            hit_type = "fly"
        else:
            hit_type = "popup"
        
        return BattedBallData(
            exit_velocity=exit_velocity,
            launch_angle=launch_angle,
            spray_angle=spray_angle,
            spin_rate=spin_rate,
            spin_axis=random.uniform(0, 360),
            contact_quality=contact_quality,
            hit_type=hit_type
        )
    
    def _convert_physics_result_to_bat_result(self, hit_result: HitResult, 
                                               defense_result: OutfieldCatchResult = None) -> Tuple[BatResult, str]:
        """物理エンジンの結果をBatResultに変換"""
        descriptions = {
            HitResult.HOME_RUN: ("ホームラン！！", BatResult.HOME_RUN),
            HitResult.TRIPLE: ("三塁打！", BatResult.TRIPLE),
            HitResult.DOUBLE: ("二塁打！", BatResult.DOUBLE),
            HitResult.SINGLE: ("ヒット！", BatResult.SINGLE),
            HitResult.INFIELD_HIT: ("内野安打！", BatResult.INFIELD_SINGLE),
            HitResult.FLYOUT: ("フライアウト", BatResult.FLYOUT),
            HitResult.GROUNDOUT: ("ゴロアウト", BatResult.GROUNDOUT),
            HitResult.LINEOUT: ("ライナーアウト", BatResult.LINEOUT),
        }
        
        base_desc, bat_result = descriptions.get(hit_result, ("アウト", BatResult.GROUNDOUT))
        
        # 守備結果があればより詳細な説明を追加
        if defense_result and defense_result.description:
            if defense_result.is_diving_catch:
                base_desc = f"ダイビングキャッチ！{defense_result.fielder_position}の好守！"
            elif defense_result.is_wall_catch:
                base_desc = f"フェンス際でスーパーキャッチ！"
            elif not defense_result.is_caught and bat_result == BatResult.FLYOUT:
                # 守備が追いつけなかった場合
                base_desc = defense_result.description
        
        return bat_result, base_desc
    
    def simulate_at_bat_physics(self, batter: Player, pitcher: Player) -> AtBatDetail:
        """物理演算ベースの詳細な打席シミュレーション"""
        pitch_count = random.randint(2, 9)
        
        # 外野守備を設定
        fielding_team = self.home_team if self.is_top else self.away_team
        self._setup_outfield_defense(fielding_team)
        
        # まず四球/三振/死球の判定
        walk_prob = self._calculate_walk_probability(batter, pitcher)
        k_prob = self._calculate_strikeout_probability(batter, pitcher)
        
        roll = random.random()
        
        # 四球
        if roll < walk_prob:
            runs = 1 if all(self.runners) else 0
            batter.record.walks += 1
            pitcher.record.walks_allowed += 1
            return AtBatDetail(
                batter=batter, pitcher=pitcher, result=BatResult.WALK,
                pitch_count=pitch_count, runs_scored=runs,
                runners_advanced=[1], description=f"{batter.name}、四球を選ぶ"
            )
        
        # 三振
        if roll < walk_prob + k_prob:
            batter.record.strikeouts += 1
            batter.record.at_bats += 1
            pitcher.record.strikeouts_pitched += 1
            is_swinging = random.random() < 0.6
            result = BatResult.STRIKEOUT_SWINGING if is_swinging else BatResult.STRIKEOUT_LOOKING
            return AtBatDetail(
                batter=batter, pitcher=pitcher, result=result,
                pitch_count=pitch_count, runs_scored=0,
                runners_advanced=[],
                description=CommentaryGenerator.generate_strikeout_comment(batter, pitcher)
            )
        
        # 死球
        if random.random() < 0.008:
            runs = 1 if all(self.runners) else 0
            return AtBatDetail(
                batter=batter, pitcher=pitcher, result=BatResult.HIT_BY_PITCH,
                pitch_count=pitch_count, runs_scored=runs,
                runners_advanced=[1], description=f"{batter.name}、死球！"
            )
        
        # 打球を生成
        batted_ball = self._generate_batted_ball(batter, pitcher)
        
        # 物理エンジンで打球結果を計算
        hit_result, distance, hang_time = self.physics_engine.calculate_batted_ball(batted_ball)
        
        # 外野フライの場合は守備シミュレーションを実行
        defense_result = None
        if batted_ball.hit_type in ["fly", "line"] and distance > 40:
            defense_result = self.physics_engine.simulate_outfield_defense(batted_ball)
            if defense_result.is_caught:
                hit_result = HitResult.FLYOUT
        
        # 結果を変換
        bat_result, base_desc = self._convert_physics_result_to_bat_result(hit_result, defense_result)
        
        # 併殺打チェック (ゴロアウトで1塁ランナーがいる場合)
        if bat_result == BatResult.GROUNDOUT and self.runners[0] and self.outs < 2:
            dp_chance = 0.12 + (batted_ball.exit_velocity - 100) * 0.001
            if batted_ball.hit_type == "ground" and random.random() < dp_chance:
                batter.record.at_bats += 1
                return AtBatDetail(
                    batter=batter, pitcher=pitcher, result=BatResult.DOUBLE_PLAY,
                    pitch_count=pitch_count, runs_scored=0,
                    runners_advanced=[],
                    description=random.choice(CommentaryGenerator.DOUBLE_PLAY_COMMENTS).format(batter=batter.name)
                )
        
        # エラー判定
        error_prob = self._calculate_error_probability()
        if bat_result in [BatResult.GROUNDOUT, BatResult.FLYOUT] and random.random() < error_prob:
            self.total_errors["away" if self.is_top else "home"] += 1
            return AtBatDetail(
                batter=batter, pitcher=pitcher, result=BatResult.ERROR,
                pitch_count=pitch_count, runs_scored=0,
                runners_advanced=[1],
                description=random.choice(CommentaryGenerator.ERROR_COMMENTS).format(fielder="守備陣")
            )
        
        # 得点計算と記録
        runs = 0
        description = f"{batter.name}、{base_desc}"
        is_dramatic = False
        
        if bat_result == BatResult.HOME_RUN:
            runs = 1 + sum(1 for r in self.runners if r)
            batter.record.home_runs += 1
            batter.record.hits += 1
            batter.record.at_bats += 1
            batter.record.rbis += runs
            pitcher.record.hits_allowed += 1
            description = CommentaryGenerator.generate_home_run_comment(batter, batter.record.home_runs, runs - 1)
            is_dramatic = True
            
        elif bat_result == BatResult.TRIPLE:
            runs = sum(1 for r in self.runners if r)
            batter.record.triples += 1
            batter.record.hits += 1
            batter.record.at_bats += 1
            batter.record.rbis += runs
            pitcher.record.hits_allowed += 1
            if runs > 0:
                description = CommentaryGenerator.generate_clutch_comment(batter, runs)
            
        elif bat_result == BatResult.DOUBLE:
            if self.runners[2]: runs += 1
            if self.runners[1]: runs += 1
            batter.record.doubles += 1
            batter.record.hits += 1
            batter.record.at_bats += 1
            batter.record.rbis += runs
            pitcher.record.hits_allowed += 1
            if runs > 0:
                description = CommentaryGenerator.generate_clutch_comment(batter, runs)
            
        elif bat_result in [BatResult.SINGLE, BatResult.INFIELD_SINGLE]:
            if self.runners[2]: runs += 1
            if self.runners[1] and random.random() < 0.55: runs += 1
            batter.record.hits += 1
            batter.record.at_bats += 1
            batter.record.rbis += runs
            pitcher.record.hits_allowed += 1
            if runs > 0:
                description = CommentaryGenerator.generate_clutch_comment(batter, runs)
        
        elif bat_result == BatResult.FLYOUT:
            batter.record.at_bats += 1
            # 犠牲フライ判定
            if self.runners[2] and self.outs < 2 and hang_time > 3.5:
                if random.random() < 0.65:
                    runs = 1
                    batter.record.rbis += 1
                    bat_result = BatResult.SACRIFICE_FLY
                    description = f"{batter.name}、犠牲フライ！1点が入る！"
        
        elif bat_result in [BatResult.GROUNDOUT, BatResult.LINEOUT]:
            batter.record.at_bats += 1
        
        return AtBatDetail(
            batter=batter, pitcher=pitcher, result=bat_result,
            pitch_count=pitch_count, runs_scored=runs,
            runners_advanced=self._get_runners_advanced(bat_result),
            description=description, is_dramatic=is_dramatic
        )
    
    def _get_runners_advanced(self, result: BatResult) -> List[int]:
        """結果に応じた進塁ベースを取得"""
        if result == BatResult.HOME_RUN:
            return []
        elif result == BatResult.TRIPLE:
            return [3]
        elif result == BatResult.DOUBLE:
            return [2]
        elif result in [BatResult.SINGLE, BatResult.INFIELD_SINGLE, BatResult.WALK, 
                        BatResult.HIT_BY_PITCH, BatResult.ERROR]:
            return [1]
        return []
    
    def simulate_at_bat(self, batter: Player, pitcher: Player) -> AtBatDetail:
        """打席シミュレーション（物理演算版を使用）"""
        return self.simulate_at_bat_physics(batter, pitcher)
    
    def process_at_bat_result(self, detail: AtBatDetail) -> int:
        """打席結果を処理してスコアを更新"""
        runs = detail.runs_scored
        
        if detail.result == BatResult.HOME_RUN:
            self.runners = [False, False, False]
        
        elif detail.result == BatResult.TRIPLE:
            self.runners = [False, False, True]
        
        elif detail.result == BatResult.DOUBLE:
            self.runners = [False, True, self.runners[0]]
        
        elif detail.result in [BatResult.SINGLE, BatResult.INFIELD_SINGLE]:
            new_runners = [True, self.runners[0], self.runners[1]]
            self.runners = new_runners
        
        elif detail.result in [BatResult.WALK, BatResult.HIT_BY_PITCH, BatResult.ERROR]:
            if all(self.runners):
                pass  # 押し出し、runsは既に計算済み
            elif self.runners[0] and self.runners[1]:
                self.runners = [True, True, True]
            elif self.runners[0]:
                self.runners = [True, True, self.runners[2]]
            else:
                self.runners = [True, self.runners[1], self.runners[2]]
        
        elif detail.result == BatResult.DOUBLE_PLAY:
            self.outs += 2
            self.runners[0] = False
            if self.runners[1]:
                self.runners[1] = False
        
        elif detail.result in [BatResult.STRIKEOUT_SWINGING, BatResult.STRIKEOUT_LOOKING,
                               BatResult.GROUNDOUT, BatResult.FLYOUT, BatResult.LINEOUT,
                               BatResult.POPOUT]:
            self.outs += 1
        
        elif detail.result == BatResult.SACRIFICE_FLY:
            self.outs += 1
            self.runners[2] = False
        
        elif detail.result == BatResult.SACRIFICE_BUNT:
            self.outs += 1
            # ランナー進塁
            if self.runners[1]:
                self.runners[2] = True
            if self.runners[0]:
                self.runners[1] = True
            self.runners[0] = False
        
        return runs
    
    def should_change_pitcher(self, team: Team, is_home: bool) -> bool:
        """投手交代が必要か判定"""
        if is_home:
            pitch_count = self.home_pitch_count
            pitcher_idx = self.home_current_pitcher_idx
        else:
            pitch_count = self.away_pitch_count
            pitcher_idx = self.away_current_pitcher_idx
        
        if pitcher_idx == -1 or pitcher_idx >= len(team.players):
            return False
        
        pitcher = team.players[pitcher_idx]
        
        # 100球以上で交代検討
        if pitch_count >= 100:
            return random.random() < 0.7
        
        # 7回以降で中継ぎ・抑えを検討
        if self.inning >= 7 and pitcher.pitch_type == PitchType.STARTER:
            return random.random() < 0.5
        
        # 9回で抑え投入
        if self.inning == 9 and pitcher.pitch_type != PitchType.CLOSER:
            return random.random() < 0.8
        
        return False
    
    def change_pitcher(self, team: Team, is_home: bool):
        """投手を交代"""
        current_inning = self.inning
        
        # 適切な投手タイプを選択
        if current_inning >= 9:
            target_type = PitchType.CLOSER
        elif current_inning >= 7:
            target_type = PitchType.RELIEVER
        else:
            target_type = PitchType.RELIEVER
        
        # 該当タイプの投手を探す
        used = self.home_pitchers_used if is_home else self.away_pitchers_used
        
        for i, p in enumerate(team.players):
            if p.position == Position.PITCHER and p.pitch_type == target_type:
                if i not in used:
                    if is_home:
                        self.home_current_pitcher_idx = i
                        self.home_pitchers_used.append(i)
                        self.home_pitch_count = 0
                    else:
                        self.away_current_pitcher_idx = i
                        self.away_pitchers_used.append(i)
                        self.away_pitch_count = 0
                    
                    self.log.append(f"  投手交代: {p.name}")
                    return
    
    def simulate_half_inning(self) -> int:
        """半イニングをシミュレート"""
        batting_team = self.away_team if self.is_top else self.home_team
        pitching_team = self.home_team if self.is_top else self.away_team
        
        self.outs = 0
        self.runners = [False, False, False]
        runs_this_inning = 0
        
        if len(batting_team.current_lineup) == 0:
            return 0
        
        pitcher_idx = self.home_current_pitcher_idx if self.is_top else self.away_current_pitcher_idx
        if pitcher_idx == -1 or pitcher_idx >= len(pitching_team.players):
            return 0
        
        pitcher = pitching_team.players[pitcher_idx]
        batter_idx = self.away_batter_index if self.is_top else self.home_batter_index
        
        while self.outs < 3:
            # 投手交代チェック
            if self.should_change_pitcher(pitching_team, self.is_top):
                self.change_pitcher(pitching_team, self.is_top)
                pitcher_idx = self.home_current_pitcher_idx if self.is_top else self.away_current_pitcher_idx
                pitcher = pitching_team.players[pitcher_idx]
            
            # 打者取得
            lineup_idx = batter_idx % len(batting_team.current_lineup)
            batter = batting_team.players[batting_team.current_lineup[lineup_idx]]
            
            # 打席シミュレーション
            detail = self.simulate_at_bat(batter, pitcher)
            
            # 投球数加算
            if self.is_top:
                self.home_pitch_count += detail.pitch_count
            else:
                self.away_pitch_count += detail.pitch_count
            
            # 結果処理
            runs = self.process_at_bat_result(detail)
            runs_this_inning += runs
            
            # ログ追加
            self.log.append(f"  {detail.description}")
            self.detailed_log.append(detail)
            
            # 重要場面記録
            if detail.is_dramatic or runs >= 2:
                self.key_moments.append(GameMoment(
                    inning=self.inning,
                    is_top=self.is_top,
                    outs=self.outs,
                    runners=self.runners.copy(),
                    score_diff=self.home_score - self.away_score,
                    description=detail.description,
                    drama_level=min(10, runs * 3 + (5 if detail.is_dramatic else 0))
                ))
            
            batter_idx += 1
        
        # 打順保存
        if self.is_top:
            self.away_batter_index = batter_idx
        else:
            self.home_batter_index = batter_idx
        
        # 投手成績更新
        pitcher.record.innings_pitched += 1
        pitcher.record.earned_runs += runs_this_inning
        
        return runs_this_inning
    
    def simulate_game(self) -> Tuple[int, int]:
        """試合全体をシミュレート"""
        self.log = [
            f"{self.away_team.name} vs {self.home_team.name}",
            f"{self.stadium.display_name} / {self.weather.display_name}",
            "=" * 50
        ]
        
        # 9イニング
        for inning in range(1, 10):
            self.inning = inning
            
            # 表
            self.is_top = True
            self.log.append(f"\n◆ {inning}回表 {self.away_team.name}の攻撃")
            runs = self.simulate_half_inning()
            self.away_score += runs
            self.inning_scores["away"].append(runs)
            
            # 9回裏、ホームチームがリードしていたら終了
            if inning == 9 and self.home_score > self.away_score:
                self.inning_scores["home"].append(0)
                break
            
            # 裏
            self.is_top = False
            self.log.append(f"\n◇ {inning}回裏 {self.home_team.name}の攻撃")
            runs = self.simulate_half_inning()
            self.home_score += runs
            self.inning_scores["home"].append(runs)
            
            # サヨナラ勝ち
            if inning >= 9 and self.home_score > self.away_score:
                self.log.append("\nサヨナラ勝ち！")
                break
        
        # 延長戦
        while self.home_score == self.away_score and self.inning < 12:
            self.inning += 1
            
            self.is_top = True
            self.log.append(f"\n◆ {self.inning}回表（延長）")
            runs = self.simulate_half_inning()
            self.away_score += runs
            self.inning_scores["away"].append(runs)
            
            self.is_top = False
            self.log.append(f"\n◇ {self.inning}回裏（延長）")
            runs = self.simulate_half_inning()
            self.home_score += runs
            self.inning_scores["home"].append(runs)
            
            if self.home_score > self.away_score:
                self.log.append("\nサヨナラ勝ち！")
                break
        
        # 勝敗決定
        self._record_game_result()
        
        # 最終スコア
        self.log.append("\n" + "=" * 50)
        self.log.append(f"最終スコア: {self.away_team.name} {self.away_score} - {self.home_score} {self.home_team.name}")
        
        return self.home_score, self.away_score
    
    def _record_game_result(self):
        """試合結果を記録"""
        if self.home_score > self.away_score:
            self.home_team.wins += 1
            self.away_team.losses += 1
            # 勝利投手
            if self.home_current_pitcher_idx >= 0:
                self.home_team.players[self.home_current_pitcher_idx].record.wins += 1
        elif self.away_score > self.home_score:
            self.away_team.wins += 1
            self.home_team.losses += 1
            if self.away_current_pitcher_idx >= 0:
                self.away_team.players[self.away_current_pitcher_idx].record.wins += 1
        else:
            self.home_team.draws += 1
            self.away_team.draws += 1
    
    def get_box_score(self) -> str:
        """ボックススコアを生成"""
        lines = ["", "【ボックススコア】"]
        
        # イニングスコア
        header = "チーム　　　　"
        for i in range(len(self.inning_scores["away"])):
            header += f" {i+1}"
        header += "  計"
        lines.append(header)
        
        away_line = f"{self.away_team.name[:6]:　<6}"
        for r in self.inning_scores["away"]:
            away_line += f" {r}"
        away_line += f"  {self.away_score}"
        lines.append(away_line)
        
        home_line = f"{self.home_team.name[:6]:　<6}"
        for r in self.inning_scores["home"]:
            home_line += f" {r}"
        home_line += f"  {self.home_score}"
        lines.append(home_line)
        
        return "\n".join(lines)
    
    def get_key_moments_summary(self) -> List[str]:
        """重要場面のサマリーを取得"""
        moments = sorted(self.key_moments, key=lambda x: x.drama_level, reverse=True)
        return [m.description for m in moments[:5]]
