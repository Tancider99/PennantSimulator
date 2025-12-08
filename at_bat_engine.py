# -*- coding: utf-8 -*-
"""
打席結果判定エンジン（全能力値完全反映版）

models.py で定義されたすべての能力値を計算ロジックに組み込み、
状況（得点圏、イニング、点差など）に応じた動的な能力変動をシミュレートします。
"""
import random
import math
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from enum import Enum
from models import Position, PitchType

# ========================================
# 列挙型
# ========================================

class AtBatResult(Enum):
    SINGLE = "単打"
    DOUBLE = "二塁打"
    TRIPLE = "三塁打"
    HOME_RUN = "本塁打"
    INFIELD_HIT = "内野安打"
    STRIKEOUT = "三振"
    GROUNDOUT = "ゴロ"
    FLYOUT = "飛球"
    LINEOUT = "ライナー"
    POP_OUT = "邪飛"
    DOUBLE_PLAY = "併殺打"
    SACRIFICE_FLY = "犠飛"
    SACRIFICE_BUNT = "犠打"
    WALK = "四球"
    HIT_BY_PITCH = "死球"
    ERROR = "失策"

class PitchLocation(Enum):
    HIGH_INSIDE = "高め内角"
    HIGH_MIDDLE = "高め中央"
    HIGH_OUTSIDE = "高め外角"
    MIDDLE_INSIDE = "真ん中内角"
    MIDDLE_MIDDLE = "真ん中中央"
    MIDDLE_OUTSIDE = "真ん中外角"
    LOW_INSIDE = "低め内角"
    LOW_MIDDLE = "低め中央"
    LOW_OUTSIDE = "低め外角"
    BALL_ZONE = "ボールゾーン"

# ========================================
# データクラス
# ========================================

@dataclass
class BattedBall:
    exit_velocity: float
    launch_angle: float
    spray_angle: float
    hit_type: str
    contact_quality: str
    distance: float = 0.0
    landing_x: float = 0.0
    landing_y: float = 0.0

@dataclass
class PitchData:
    pitch_type: str
    velocity: float
    location: PitchLocation
    horizontal_break: float
    vertical_break: float
    spin_rate: int
    is_strike_zone: bool
    quality_score: float = 50.0 # 投球の質（失投度合いなど）

@dataclass
class DefenseData:
    """守備データ"""
    ranges: Dict[str, int] = field(default_factory=dict)
    arms: Dict[str, int] = field(default_factory=dict)
    errors: Dict[str, int] = field(default_factory=dict)
    catcher_lead: int = 50
    turn_dp: int = 50

    def get_range(self, pos: Position) -> int:
        return self.ranges.get(pos.value, 1)

    def get_arm(self, pos: Position) -> int:
        return self.arms.get(pos.value, 50)

    def get_error(self, pos: Position) -> int:
        return self.errors.get(pos.value, 50)

@dataclass
class AtBatContext:
    balls: int = 0
    strikes: int = 0
    outs: int = 0
    runners: List[bool] = field(default_factory=lambda: [False, False, False])
    inning: int = 1
    is_top: bool = True
    score_diff: int = 0 # 攻撃側から見た点差（マイナスはビハインド）
    
    # 利き腕情報（デフォルトは右）
    batter_is_left: bool = False
    pitcher_is_left: bool = False
    
    @property
    def is_scoring_position(self) -> bool:
        return self.runners[1] or self.runners[2]
        
    @property
    def is_runner_on(self) -> bool:
        return any(self.runners)
        
    @property
    def is_clutch(self) -> bool:
        """プレッシャーのかかる場面か"""
        # 7回以降で3点差以内
        return self.inning >= 7 and abs(self.score_diff) <= 3

# ========================================
# ユーティリティ関数
# ========================================

def apply_modifier(value: int, modifier: float) -> int:
    """能力値に補正を掛ける（1-99の範囲に収める）"""
    new_val = int(value * modifier)
    return max(1, min(99, new_val))

def get_stat(stats_obj, name: str, default: int = 50) -> int:
    """安全に属性を取得"""
    return getattr(stats_obj, name, default)

# ========================================
# 打球生成エンジン
# ========================================

class BattedBallGenerator:
    """打球生成・判定クラス"""

    def generate_pitch(self, pitcher_stats, defense: DefenseData, context: AtBatContext, pitch_type: str = None) -> PitchData:
        """
        投球生成
        反映能力: Velocity, Control, Movement, Stuff, Stability, Mental, 
                 Catcher Lead, Hold Runners(Quick), Vs Pinch, Vs Left
        """
        # 基本能力
        velocity_stat = get_stat(pitcher_stats, 'velocity', 145)
        control = get_stat(pitcher_stats, 'control', 50)
        movement = get_stat(pitcher_stats, 'movement', 50)
        stuff = get_stat(pitcher_stats, 'stuff', 50)
        stability = get_stat(pitcher_stats, 'stability', 50)
        mental = get_stat(pitcher_stats, 'mental', 50)
        
        # 特殊能力・状況補正
        
        # 1. 対左打者
        if context.batter_is_left and context.pitcher_is_left:
             # 左対左は一般的に投手が有利になりがちだが、statsで制御
             pass 
        if context.batter_is_left:
            vs_left = get_stat(pitcher_stats, 'vs_left_pitcher', 50)
            # 50を基準に補正
            mod = 1.0 + (vs_left - 50) * 0.005
            control = apply_modifier(control, mod)
            stuff = apply_modifier(stuff, mod)

        # 2. 対ピンチ (得点圏)
        if context.is_scoring_position:
            vs_pinch = get_stat(pitcher_stats, 'vs_pinch', 50)
            mod = 1.0 + (vs_pinch - 50) * 0.008
            stuff = apply_modifier(stuff, mod)
            control = apply_modifier(control, mod)
            velocity_stat += (vs_pinch - 50) * 0.1 # 球速も少し変わる
            
        # 3. クイック (ランナーあり)
        if context.is_runner_on:
            quick = get_stat(pitcher_stats, 'hold_runners', 50)
            # クイックが低いと球威・制球が落ちる
            if quick < 50:
                penalty = (50 - quick) * 0.005
                velocity_stat *= (1.0 - penalty)
                control *= (1.0 - penalty)
                
        # 4. メンタル (接戦・ビハインド)
        if context.is_clutch and context.score_diff < 0:
            if mental < 50:
                control *= 0.9
            elif mental > 70:
                control *= 1.05

        # 5. 捕手リード
        lead_bonus = (defense.catcher_lead - 50) * 0.1
        control += lead_bonus
        stuff += lead_bonus * 0.5

        # --- 投球パラメータ決定 ---
        
        # 安定感 (乱数の幅に影響)
        # Stabilityが高いほど、能力通りの球が行きやすい
        variance = 2.0 * (1.5 - (stability / 100)) 
        
        # 球速
        base_velo = velocity_stat
        velo = random.gauss(base_velo, variance)
        
        # ストライク判定率 (Control依存)
        strike_prob = 0.45 + (control * 0.004)
        is_strike = random.random() < strike_prob
        
        # コース決定
        if is_strike:
            locations = [l for l in PitchLocation if l != PitchLocation.BALL_ZONE]
            location = random.choice(locations)
        else:
            location = PitchLocation.BALL_ZONE
            
        # 投球の質 (Quality Score)
        # Movement, Stuff, Control の複合
        quality = (stuff + movement + control) / 3
        quality += random.gauss(0, 10) # 1球ごとのブレ
        
        return PitchData(
            pitch_type=pitch_type or "ストレート",
            velocity=velo,
            location=location,
            horizontal_break=0, 
            vertical_break=0,
            spin_rate=2200 + (stuff - 50)*10,
            is_strike_zone=is_strike,
            quality_score=quality
        )

    def calculate_swing_decision(self, batter_stats, pitch: PitchData, context: AtBatContext) -> bool:
        """
        スイング判定
        反映能力: Eye, Intelligence, Mental, Strike Count
        """
        eye = get_stat(batter_stats, 'eye', 50)
        intelligence = get_stat(batter_stats, 'intelligence', 50)
        
        # 基本スイング確率
        swing_prob = 0.5
        
        # ストライクゾーンの判断
        if pitch.is_strike_zone:
            swing_prob = 0.75 + (eye - 50) * 0.005
        else:
            swing_prob = 0.30 - (eye - 50) * 0.005 - (intelligence - 50) * 0.002
            
        # カウントによる補正
        if context.strikes == 2:
            swing_prob += 0.20 # 追い込まれると手を出す
            # メンタルが低いとボール球に手を出しやすくなる（焦り）
            mental = get_stat(batter_stats, 'mental', 50)
            if not pitch.is_strike_zone and mental < 50:
                swing_prob += 0.1
        
        if context.balls == 3:
            swing_prob -= 0.3 # 3ボールは待つ
            
        return random.random() < max(0.05, min(0.99, swing_prob))

    def calculate_contact(self, batter_stats, pitcher_stats, pitch: PitchData, context: AtBatContext) -> Tuple[bool, bool]:
        """
        コンタクト判定
        反映能力: Contact, Avoid K, Vs Left Batter, Chance, Mental
                 Pitcher's Quality, Velocity
        """
        contact = get_stat(batter_stats, 'contact', 50)
        avoid_k = get_stat(batter_stats, 'avoid_k', 50)
        
        # 特殊能力補正
        if context.is_scoring_position:
            chance = get_stat(batter_stats, 'chance', 50)
            contact = apply_modifier(contact, 1.0 + (chance - 50) * 0.008)
            
        if context.pitcher_is_left:
            vs_left = get_stat(batter_stats, 'vs_left_batter', 50)
            contact = apply_modifier(contact, 1.0 + (vs_left - 50) * 0.006)
            
        # 打者スキル値 (Contact重視、Avoid Kも加味)
        batter_skill = contact * 0.7 + avoid_k * 0.3
        
        # 投手スキル値 (Pitch Quality, Velocity)
        # 球速150km/hを超えるとコンタクト難易度急上昇
        velo_penalty = max(0, (pitch.velocity - 150) * 0.5)
        pitcher_skill = pitch.quality_score * 0.8 + velo_penalty
        
        # 基準コンタクト率
        base_rate = 0.82
        rate = base_rate + (batter_skill - pitcher_skill) * 0.005
        
        if not pitch.is_strike_zone:
            rate -= 0.15
            # 悪球打ち (Bad Ball Hitter) のような能力があればここで補正できるが
            # 今回は Intelligence/Eye でスイング自体をしないことで表現
            
        contact_success = random.random() < max(0.20, min(0.98, rate))
        
        # ファウル判定
        is_foul = False
        if contact_success:
            # 振り遅れや芯を外す要素
            foul_prob = 0.28
            if not pitch.is_strike_zone: foul_prob += 0.2
            if pitch.velocity > 155: foul_prob += 0.1
            
            # Avoid Kが高いと、三振するよりはファウルで粘る
            if context.strikes == 2:
                foul_prob += (avoid_k - 50) * 0.005
                
            is_foul = random.random() < foul_prob
            
        return contact_success, is_foul

    def generate_batted_ball(self, batter_stats, pitcher_stats, pitch: PitchData, context: AtBatContext) -> BattedBall:
        """
        打球生成
        反映能力: Power, Gap, Trajectory, Chance, Vs Left
                 Pitcher Movement, GB Tendency
        """
        power = get_stat(batter_stats, 'power', 50)
        gap = get_stat(batter_stats, 'gap', 50)
        trajectory = get_stat(batter_stats, 'trajectory', 2)
        
        # 状況補正
        if context.is_scoring_position:
            chance = get_stat(batter_stats, 'chance', 50)
            power = apply_modifier(power, 1.0 + (chance - 50) * 0.008)
            
        if context.pitcher_is_left:
            vs_left = get_stat(batter_stats, 'vs_left_batter', 50)
            power = apply_modifier(power, 1.0 + (vs_left - 50) * 0.006)
            
        movement = get_stat(pitcher_stats, 'movement', 50)
        gb_tendency = get_stat(pitcher_stats, 'gb_tendency', 50)
        
        # 打球速度
        # Power 50 -> 140km/h avg (max ~160)
        base_exit_velo = 135 + (power - 50) * 0.9
        
        # 芯を捉えたか (Pitch Quality vs Batter Contact/Eye)
        # ランダム要素にMovementが影響（芯を外す）
        core_hit_prob = 0.5 - (movement - 50) * 0.005
        is_core_hit = random.random() < core_hit_prob
        
        if is_core_hit:
            quality = "hard"
            base_exit_velo += 15
        else:
            quality = "medium"
            base_exit_velo -= 10
            
        exit_velocity = random.gauss(base_exit_velo, 8)
        
        # 打球角度
        # Trajectory: 1(低) ~ 4(高)
        base_angle_map = {1: 5, 2: 12, 3: 20, 4: 28}
        base_angle = base_angle_map.get(trajectory, 12)
        
        # 投手のゴロ傾向
        base_angle -= (gb_tendency - 50) * 0.25
        
        # Gapが高いと、ライナー性（10-25度）が増える
        if gap > 60 and random.random() < (gap / 150):
            base_angle = 18 # 最適ライナー角度
            
        launch_angle = random.gauss(base_angle, 14)
        
        # タイプ判定
        if launch_angle < 10: hit_type = "groundball"
        elif launch_angle < 25: hit_type = "linedrive"
        elif launch_angle < 50: hit_type = "flyball"
        else: hit_type = "popup"
        
        # 簡易飛距離計算
        v0 = exit_velocity / 3.6
        angle_rad = math.radians(launch_angle)
        g = 9.8
        # 空気抵抗などを簡易的に係数で表現
        distance = (v0**2 * math.sin(2 * angle_rad)) / g * 0.75
        
        if hit_type == "groundball":
            distance *= 0.5 # ゴロは距離が出ない
            
        # スプレーアングル（引っ張り傾向などあればここで処理）
        spray_angle = random.gauss(0, 25)
        
        return BattedBall(exit_velocity, launch_angle, spray_angle, hit_type, quality, distance)

# ========================================
# 守備判定エンジン
# ========================================

class DefenseEngine:
    """
    守備結果判定クラス
    反映能力: Defense Range, Arm, Error, Turn DP,
             Runner Speed, Baserunning
    """
    
    def judge_result(self, ball: BattedBall, defense: DefenseData, runner_stats) -> AtBatResult:
        
        runner_speed = get_stat(runner_stats, 'speed', 50)
        
        # 1. ホームラン判定
        # フェンス距離は球場依存だが、ここでは標準的な115mとする
        if ball.hit_type == "flyball" and ball.distance > 115:
            return AtBatResult.HOME_RUN
            
        # 守備位置の特定
        position = self._determine_fielder(ball.spray_angle, ball.distance)
        
        # 2. エラー判定
        error_stat = defense.get_error(position)
        
        # 打球が速いほどエラーしやすい
        difficulty = 0
        if ball.contact_quality == "hard": difficulty += 15
        
        # ポジション難易度 (二遊間、サードは難しい)
        if position in [Position.SHORTSTOP, Position.SECOND, Position.THIRD]:
            difficulty += 10
            
        error_prob = max(0.002, (100 - error_stat + difficulty) * 0.0004)
        if random.random() < error_prob:
            return AtBatResult.ERROR
            
        # 3. アウト/ヒット判定
        range_stat = defense.get_range(position)
        
        # 基本ヒット率 (BABIP)
        hit_prob = 0.30
        
        if ball.hit_type == "groundball": hit_prob = 0.24
        elif ball.hit_type == "linedrive": hit_prob = 0.68
        elif ball.hit_type == "flyball": hit_prob = 0.14
        elif ball.hit_type == "popup": hit_prob = 0.01
        
        # 守備範囲補正 (10あたり1%程度の変動)
        hit_prob -= (range_stat - 50) * 0.0025
        
        # 打球強さ補正
        if ball.contact_quality == "hard": hit_prob += 0.12
        if ball.contact_quality == "soft": hit_prob -= 0.08
        
        # 内野安打判定 (ゴロのみ)
        if ball.hit_type == "groundball" and ball.distance < 45:
            # 走力 vs 守備力 (範囲 + 肩)
            arm_stat = defense.get_arm(position)
            
            # 深いゴロ(rangeが低いと追いつけない)はヒットになりやすい
            # ここでは range_stat が捕球までの時間を表すとする
            
            # 内野安打確率計算
            # 走力が高いほど有利、肩と守備範囲が良いほど不利
            inf_hit_prob = 0.05 + (runner_speed - 50)*0.004 - (arm_stat - 50)*0.001 - (range_stat - 50)*0.002
            inf_hit_prob = max(0.0, inf_hit_prob)
            
            # 通常のヒット判定（間を抜ける）
            if random.random() < hit_prob:
                return AtBatResult.SINGLE
            # 間を抜けなかったが、足で稼ぐ
            elif random.random() < inf_hit_prob:
                return AtBatResult.INFIELD_HIT
            else:
                return AtBatResult.GROUNDOUT
        
        # フライ/ライナー判定
        if random.random() < hit_prob:
            # 長打判定
            if ball.hit_type == "linedrive":
                if ball.distance > 70: return AtBatResult.DOUBLE
                return AtBatResult.SINGLE
            
            if ball.hit_type == "flyball":
                # 外野手の頭を超えるか、ギャップを抜くか
                # 飛距離と守備範囲の関係
                if ball.distance > 95: return AtBatResult.DOUBLE
                if ball.distance > 110: return AtBatResult.TRIPLE
                return AtBatResult.SINGLE
                
            return AtBatResult.SINGLE
        else:
            # アウト
            if ball.hit_type == "linedrive": return AtBatResult.LINEOUT
            if ball.hit_type == "popup": return AtBatResult.POP_OUT
            return AtBatResult.FLYOUT

    def _determine_fielder(self, angle, distance) -> Position:
        """打球方向と距離から担当野手を決定"""
        if distance < 45: # 内野
            if -45 <= angle < -15: return Position.THIRD
            elif -15 <= angle < 5: return Position.SHORTSTOP
            elif 5 <= angle < 20: return Position.SECOND
            else: return Position.FIRST
        else: # 外野
            if angle < -15: return Position.OUTFIELD # LEFT
            elif angle > 15: return Position.OUTFIELD # RIGHT
            else: return Position.OUTFIELD # CENTER

# ========================================
# シミュレーター本体
# ========================================

class AtBatSimulator:
    def __init__(self):
        self.ball_gen = BattedBallGenerator()
        self.defense = DefenseEngine()

    def simulate_at_bat(self, batter_stats, pitcher_stats, defense_data: DefenseData, 
                       context: AtBatContext, pitch_list: List[str] = None) -> Tuple[AtBatResult, Dict]:
        """打席シミュレーション実行"""
        
        pitch_count = 0
        
        while True:
            pitch_count += 1
            
            # 1. 投球
            pitch = self.ball_gen.generate_pitch(pitcher_stats, defense_data, context)
            
            # 2. スイング判定
            swing = self.ball_gen.calculate_swing_decision(batter_stats, pitch, context)
            
            if not swing:
                if pitch.is_strike_zone:
                    context.strikes += 1
                else:
                    context.balls += 1
            else:
                # 3. コンタクト判定
                contact, is_foul = self.ball_gen.calculate_contact(batter_stats, pitcher_stats, pitch, context)
                
                if not contact:
                    context.strikes += 1
                elif is_foul:
                    if context.strikes < 2: context.strikes += 1
                else:
                    # 4. インプレー - 打球生成
                    batted_ball = self.ball_gen.generate_batted_ball(batter_stats, pitcher_stats, pitch, context)
                    
                    # 5. 守備判定
                    result = self.defense.judge_result(batted_ball, defense_data, batter_stats)
                    
                    # 併殺判定 (ゴロアウトかつ走者1塁、かつノーアウトorワンアウト)
                    if result == AtBatResult.GROUNDOUT and context.runners[0] and context.outs < 2:
                        # 併殺阻止能力 (Baserunning vs Turn DP)
                        # 右打ちのゴロはゲッツーになりやすいなどの補正も考えられるが、ここでは能力値のみ
                        runner_run = get_stat(batter_stats, 'baserunning', 50) # 打者の走塁（一塁駆け抜け）
                        # ※本来は1塁ランナーの走塁能力を見るべきだが、ContextにRunner Objectがないため簡易的に打者能力を使用
                        # またはRunner Speedが高いと併殺崩れの確率UP
                        runner_speed = get_stat(batter_stats, 'speed', 50)
                        
                        dp_prob = 0.15 + (defense_data.turn_dp - 50) * 0.004 - (runner_speed - 50) * 0.003
                        
                        if random.random() < dp_prob:
                            result = AtBatResult.DOUBLE_PLAY
                            
                    return result, {'pitch_count': pitch_count}

            # カウント判定
            if context.balls >= 4:
                return AtBatResult.WALK, {'pitch_count': pitch_count}
            if context.strikes >= 3:
                return AtBatResult.STRIKEOUT, {'pitch_count': pitch_count}

_at_bat_simulator = AtBatSimulator()
def get_at_bat_simulator():
    return _at_bat_simulator