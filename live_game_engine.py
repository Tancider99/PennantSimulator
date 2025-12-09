# -*- coding: utf-8 -*-
"""
ライブ試合エンジン (修正版: get_rank復旧・本格UZR計算実装)
- 空間座標ベースの守備判定
- 1.02 Essence of Baseballに基づくUZR (RngR, ARM, ErrR) 計算
- 空気抵抗を考慮した飛距離計算によるHR抑制
"""
import random
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from enum import Enum
from models import Position, Player, Team, PlayerRecord, PitchType, TeamLevel, generate_best_lineup, Stadium

# ========================================
# 定数・ユーティリティ
# ========================================

STRIKE_ZONE = {
    'width': 0.432,
    'height': 0.56,
    'center_x': 0.0,
    'center_z': 0.75,
    'half_width': 0.216,
    'half_height': 0.28
}

# 守備定数 (メートル単位)
FIELD_COORDS = {
    # ホームベースを(0,0)、マウンド(0, 18.44)、二塁ベース(0, 38.795)
    # y軸がセンター方向、x軸が一三塁方向
    Position.PITCHER: (0, 18.0),
    Position.CATCHER: (0, -1.0),
    Position.FIRST: (18.0, 24.0),     # 1塁ベース付近より少し後ろ
    Position.SECOND: (10.0, 42.0),    # 2塁ベース右後方
    Position.THIRD: (-18.0, 24.0),    # 3塁ベース付近より少し後ろ
    Position.SHORTSTOP: (-10.0, 42.0),# 2塁ベース左後方
    Position.LEFT: (-35.0, 88.0),     # 左中間寄り
    Position.CENTER: (0.0, 95.0),     # センター深め
    Position.RIGHT: (35.0, 88.0),     # 右中間寄り
}

# Linear Weights (得点価値) の概算値 (1.02等の平均的な値を参照)
RUN_VALUES = {
    "Out": -0.27,
    "Single": 0.90,
    "Double": 1.27,
    "Triple": 1.62,
    "HomeRun": 2.10,
    "Error": 0.50 # エラーによる出塁の平均価値
}

def get_rank(value: int) -> str:
    """能力値からランク文字(S-G)を取得"""
    if value >= 90: return "S"
    if value >= 80: return "A"
    if value >= 70: return "B"
    if value >= 60: return "C"
    if value >= 50: return "D"
    if value >= 40: return "E"
    if value >= 30: return "F"
    return "G"

def get_effective_stat(player: Player, stat_name: str, opponent: Optional[Player] = None, is_risp: bool = False, is_close_game: bool = False) -> float:
    if not hasattr(player.stats, stat_name):
        return 50.0
    base_value = getattr(player.stats, stat_name)
    
    condition_diff = player.condition - 5
    condition_multiplier = 1.0 + (condition_diff * 0.02)
    
    value = base_value * condition_multiplier
    
    if player.position != Position.PITCHER:
        if stat_name in ['contact', 'power'] and opponent and opponent.position == Position.PITCHER:
            vs_left = getattr(player.stats, 'vs_left_batter', 50)
            value += (vs_left - 50) * 0.2
        if is_risp and stat_name in ['contact', 'power']:
            chance = getattr(player.stats, 'chance', 50)
            value += (chance - 50) * 0.5
        if is_close_game:
            mental = getattr(player.stats, 'mental', 50)
            value += (mental - 50) * 0.3
    else:
        if opponent and opponent.position != Position.PITCHER:
            vs_left = getattr(player.stats, 'vs_left_pitcher', 50)
            value += (vs_left - 50) * 0.2
        if is_risp:
            pinch = getattr(player.stats, 'vs_pinch', 50)
            if stat_name in ['stuff', 'movement', 'control']:
                value += (pinch - 50) * 0.5
        if stat_name == 'control':
            stability = getattr(player.stats, 'stability', 50)
            if condition_diff < 0:
                mitigation = (stability - 50) * 0.2
                value += max(0, mitigation)

    return max(1.0, value)

# ========================================
# 列挙型
# ========================================

class PitchResult(Enum):
    BALL = "ボール"
    STRIKE_CALLED = "見逃し"
    STRIKE_SWINGING = "空振り"
    FOUL = "ファウル"
    IN_PLAY = "インプレー"
    HIT_BY_PITCH = "死球"

class BattedBallType(Enum):
    GROUNDBALL = "ゴロ"
    LINEDRIVE = "ライナー"
    FLYBALL = "フライ"
    POPUP = "内野フライ"

class PlayResult(Enum):
    SINGLE = "安打"
    DOUBLE = "二塁打"
    TRIPLE = "三塁打"
    HOME_RUN = "本塁打"
    STRIKEOUT = "三振"
    GROUNDOUT = "ゴロ"
    FLYOUT = "フライ"
    LINEOUT = "ライナー"
    POPUP_OUT = "内野フライ"
    ERROR = "失策"
    SACRIFICE_FLY = "犠飛"
    SACRIFICE_BUNT = "犠打"
    DOUBLE_PLAY = "併殺打"
    FOUL = "ファウル"
    FIELDERS_CHOICE = "野選"

# ========================================
# データクラス
# ========================================

@dataclass
class PitchLocation:
    x: float
    z: float
    is_strike: bool

@dataclass
class PitchData:
    pitch_type: str
    velocity: float
    spin_rate: int
    horizontal_break: float
    vertical_break: float
    location: PitchLocation
    release_point: Tuple[float, float, float]
    trajectory: List[Tuple[float, float, float]] = field(default_factory=list)

@dataclass
class BattedBallData:
    exit_velocity: float
    launch_angle: float
    spray_angle: float
    hit_type: BattedBallType
    distance: float
    hang_time: float
    landing_x: float
    landing_y: float
    trajectory: List[Tuple[float, float, float]] = field(default_factory=list)
    contact_quality: str = "medium"

@dataclass
class GameState:
    inning: int = 1
    is_top: bool = True
    outs: int = 0
    balls: int = 0
    strikes: int = 0
    runner_1b: Optional[Player] = None 
    runner_2b: Optional[Player] = None
    runner_3b: Optional[Player] = None
    home_score: int = 0
    away_score: int = 0
    home_batter_order: int = 0
    away_batter_order: int = 0
    home_pitcher_idx: int = 0
    away_pitcher_idx: int = 0
    home_pitcher_stamina: float = 100.0
    away_pitcher_stamina: float = 100.0
    home_pitch_count: int = 0
    away_pitch_count: int = 0
    home_pitchers_used: List[Player] = field(default_factory=list)
    away_pitchers_used: List[Player] = field(default_factory=list)

    def is_runner_on(self) -> bool:
        return any([self.runner_1b, self.runner_2b, self.runner_3b])

    def is_risp(self) -> bool:
        return (self.runner_2b is not None) or (self.runner_3b is not None)

    def current_pitcher_stamina(self) -> float:
        return self.home_pitcher_stamina if self.is_top else self.away_pitcher_stamina

# ========================================
# AI マネージャー
# ========================================

class AIManager:
    def decide_strategy(self, state: GameState, offense_team, defense_team, batter: Player) -> str:
        score_diff = state.away_score - state.home_score if state.is_top else state.home_score - state.away_score
        is_late = state.inning >= 7
        is_close = abs(score_diff) <= 2
        
        bunt_skill = get_effective_stat(batter, 'bunt_sac')
        if state.outs == 0 and (state.runner_1b) and not state.runner_3b:
            batting_ab = batter.stats.overall_batting()
            if (is_close and is_late) or (bunt_skill > 70 and batting_ab < 45) or (state.runner_2b and is_close):
                return "BUNT"
        
        if state.runner_1b and not state.runner_2b and not state.runner_3b and state.outs < 2:
            runner_spd = get_effective_stat(state.runner_1b, 'speed')
            runner_stl = get_effective_stat(state.runner_1b, 'steal')
            base_threshold = 60
            if is_close and is_late: base_threshold = 70
            if runner_spd >= base_threshold and runner_stl >= 50:
                steal_attempt_prob = (runner_spd - 40) * 0.015 
                if random.random() < steal_attempt_prob:
                    return "STEAL"
        
        eff_power = get_effective_stat(batter, 'power', is_risp=state.is_risp())
        if state.balls >= 3 and state.strikes < 2 and eff_power > 65: 
            return "POWER"
        
        eff_contact = get_effective_stat(batter, 'contact', is_risp=state.is_risp())
        eff_avoid_k = get_effective_stat(batter, 'avoid_k')
        if state.strikes == 2 and eff_contact > 50 and eff_avoid_k > 50:
            return "MEET"
            
        return "SWING"

    def decide_pitch_strategy(self, state: GameState, pitcher: Player, batter: Player) -> str:
        eff_control = get_effective_stat(pitcher, 'control', opponent=batter, is_risp=state.is_risp())
        if state.balls >= 3: return "STRIKE" 
        if state.strikes == 2:
            has_breaking = len(pitcher.stats.pitches) > 0
            if has_breaking and eff_control > 40:
                return "BALL"
        eff_power = get_effective_stat(batter, 'power', is_risp=state.is_risp())
        if state.is_risp() and not state.runner_1b and eff_power > 85 and state.inning >= 8 and abs(state.home_score - state.away_score) <= 1:
            return "WALK"
        return "NORMAL"

# ========================================
# 投球・打球エンジン
# ========================================

class PitchGenerator:
    PITCH_DATA = {
        "ストレート": {"base_speed": 148, "h_break": 0, "v_break": 10},
        "ツーシーム": {"base_speed": 145, "h_break": 12, "v_break": 2},
        "カットボール": {"base_speed": 140, "h_break": -8, "v_break": 3},
        "スライダー": {"base_speed": 132, "h_break": -20, "v_break": -3},
        "カーブ":     {"base_speed": 115, "h_break": -12, "v_break": -25},
        "フォーク":   {"base_speed": 136, "h_break": 0, "v_break": -30},
        "チェンジアップ": {"base_speed": 128, "h_break": 8, "v_break": -15},
        "シュート":   {"base_speed": 140, "h_break": 18, "v_break": -6},
        "シンカー":   {"base_speed": 142, "h_break": 15, "v_break": -10},
        "スプリット": {"base_speed": 140, "h_break": 3, "v_break": -28}
    }

    def generate_pitch(self, pitcher: Player, batter: Player, catcher: Player, state: GameState, strategy="NORMAL", stadium: Stadium = None) -> PitchData:
        is_risp = state.is_risp()
        is_close = abs(state.home_score - state.away_score) <= 2
        
        velocity = get_effective_stat(pitcher, 'velocity', batter, is_risp, is_close)
        control = get_effective_stat(pitcher, 'control', batter, is_risp, is_close)
        movement = get_effective_stat(pitcher, 'movement', batter, is_risp, is_close)
        
        if stadium:
             control = control / max(0.5, stadium.pf_bb)

        if catcher:
            lead = get_effective_stat(catcher, 'catcher_lead', is_close_game=is_close)
            control += (lead - 50) * 0.2
        
        current_stamina = state.current_pitcher_stamina()
        fatigue = 1.0
        if current_stamina < 30: fatigue = 0.9 + (current_stamina / 300.0)
        if current_stamina <= 0: fatigue = 0.8
        
        pitch_cost = 0.5
        if is_risp: pitch_cost *= 1.2
        if state.is_top: state.home_pitcher_stamina = max(0, state.home_pitcher_stamina - pitch_cost)
        else: state.away_pitcher_stamina = max(0, state.away_pitcher_stamina - pitch_cost)
        
        pitch_type = None
        breaking_balls = getattr(pitcher.stats, 'breaking_balls', [])
        
        if strategy == "WALK": pitch_type = "ストレート"
        elif not breaking_balls: pitch_type = "ストレート"
        else:
            straight_prob = max(0.4, 0.7 - len(breaking_balls) * 0.1)
            if state.strikes == 2: straight_prob *= 0.7
            if random.random() < straight_prob: pitch_type = "ストレート"
            else:
                pitches = pitcher.stats.pitches
                if pitches:
                    total_val = sum(pitches.values())
                    r = random.uniform(0, total_val)
                    curr = 0
                    for p, v in pitches.items():
                        curr += v
                        if r <= curr:
                            pitch_type = p
                            break
                else: pitch_type = breaking_balls[0]
            
        base = self.PITCH_DATA.get(pitch_type, self.PITCH_DATA["ストレート"])
        base_velo = velocity * fatigue
        if pitch_type != "ストレート":
            speed_ratio = base["base_speed"] / 148.0
            base_velo *= speed_ratio
            
        velo = random.gauss(base_velo, 1.5)
        velo = max(80, min(170, velo))
        
        move_factor = 1.0 + (movement - 50) * 0.01
        h_brk = base["h_break"] * move_factor + random.gauss(0, 2)
        v_brk = base["v_break"] * move_factor + random.gauss(0, 2)
        loc = self._calc_location(control * fatigue, state, strategy)
        traj = self._calc_traj(velo, h_brk, v_brk, loc)
        
        return PitchData(pitch_type, round(velo,1), 2200, h_brk, v_brk, loc, (0,18.44,1.8), traj)

    def _calc_location(self, control, state, strategy):
        if strategy == "WALK": return PitchLocation(1.0, 1.5, False)
        zone_target_prob = 0.54 + (control - 50) * 0.003
        if strategy == "STRIKE": zone_target_prob += 0.3
        elif strategy == "BALL": zone_target_prob -= 0.3
        if state.balls == 3: zone_target_prob += 0.25
        if state.strikes == 0 and state.balls == 0: zone_target_prob += 0.1
        zone_target_prob = max(0.1, min(0.98, zone_target_prob))
        
        tx, tz = 0, STRIKE_ZONE['center_z']
        sigma = max(0.05, 0.22 - (control * 0.002))
        is_trying_strike = random.random() < zone_target_prob
        
        if is_trying_strike:
            if random.random() < 0.35:
                tx = 0
                tz = STRIKE_ZONE['center_z']
            else:
                tx = random.choice([-0.2, 0.2])
                tz = STRIKE_ZONE['center_z'] + random.choice([-0.25, 0.25])
        else:
            tx = random.choice([-0.35, 0.35])
            tz = STRIKE_ZONE['center_z'] + random.choice([-0.35, 0.35])

        ax = random.gauss(tx, sigma)
        az = random.gauss(tz, sigma)
        is_strike = (abs(ax) <= STRIKE_ZONE['half_width'] + 0.036 and
                     abs(az - STRIKE_ZONE['center_z']) <= STRIKE_ZONE['half_height'] + 0.036)
        return PitchLocation(ax, az, is_strike)

    def _calc_traj(self, velo, hb, vb, loc):
        path = []
        start = (random.uniform(-0.05, 0.05), 18.44, 1.8)
        end = (loc.x, 0, loc.z)
        steps = 15
        for i in range(steps + 1):
            t = i/steps
            x = start[0] + (end[0]-start[0])*t + (hb/100 * 0.3)*math.sin(t*math.pi)
            y = start[1] * (1-t)
            z = start[2] + (end[2]-start[2])*t + (vb/100 * 0.3)*(t**2)
            path.append((x,y,z))
        return path

class BattedBallGenerator:
    def generate(self, batter: Player, pitcher: Player, pitch: PitchData, state: GameState, strategy="SWING"):
        is_risp = state.is_risp()
        is_close = abs(state.home_score - state.away_score) <= 2

        power = get_effective_stat(batter, 'power', opponent=pitcher, is_risp=is_risp, is_close_game=is_close)
        contact = get_effective_stat(batter, 'contact', opponent=pitcher, is_risp=is_risp, is_close_game=is_close)
        gap = get_effective_stat(batter, 'gap', opponent=pitcher, is_risp=is_risp)
        trajectory = getattr(batter.stats, 'trajectory', 2)
        
        p_movement = get_effective_stat(pitcher, 'movement', opponent=batter, is_risp=is_risp)
        p_gb_tendency = getattr(pitcher.stats, 'gb_tendency', 50)
        
        meet_bonus = 0
        if strategy == "MEET": meet_bonus = 15
        if strategy == "POWER": meet_bonus = -20 
        
        ball_penalty = 0 if pitch.location.is_strike else 20
        con_eff = contact + meet_bonus - (p_movement - 50) * 0.4 - ball_penalty
        
        power_bonus_factor = (power - 50) * 0.4
        hard_chance = (con_eff * 0.5) + power_bonus_factor
        hard_chance = max(1.0, hard_chance)
        
        medium_limit = (con_eff * 0.85)
        if medium_limit < hard_chance + 10: medium_limit = hard_chance + 10
        
        quality_roll = random.uniform(0, 100)
        if quality_roll < hard_chance: quality = "hard"
        elif quality_roll < medium_limit: quality = "medium"
        else: quality = "soft"
        
        base_v = 132 + (power - 50) * 0.6
        if strategy == "POWER": base_v += 9
        if quality == "hard": base_v += 10 + (power / 5.0) 
        if quality == "soft": base_v -= 35 
        
        traj_bias = 5 + (trajectory * 5)
        gb_effect = (p_gb_tendency - 50) * 0.2
        angle_center = traj_bias - gb_effect
        
        if pitch.location.z < 0.5: angle_center -= 5
        if pitch.location.z > 0.9: angle_center += 5
        if gap > 60 and quality != "soft":
            if random.random() < (gap/150): angle_center = 15
        
        if strategy == "BUNT":
            angle = -20; velo = 30 + random.uniform(-5, 5)
            bunt_skill = get_effective_stat(batter, 'bunt_sac')
            if random.uniform(0, 100) > bunt_skill:
                if random.random() < 0.5: angle = 30
                else: velo += 20
            quality = "soft"
        else:
            angle = random.gauss(angle_center, 12)
        
        velo = max(40, base_v + random.gauss(0, 5))
        if quality == "hard": velo = max(velo, 140)
        
        if angle < 7: htype = BattedBallType.GROUNDBALL
        elif angle < 20: htype = BattedBallType.LINEDRIVE
        elif angle < 50: htype = BattedBallType.FLYBALL
        else: htype = BattedBallType.POPUP
        
        v_ms = velo / 3.6
        vacuum_dist = (v_ms**2 * math.sin(math.radians(2 * angle))) / 9.8
        
        # 空気抵抗: 速度が速いほど係数を下げる
        drag_factor = max(0.3, 1.0 - (velo / 350.0))
        if angle > 45 or angle < 10:
             drag_factor *= 0.85
             
        dist = vacuum_dist * drag_factor
        
        if htype == BattedBallType.GROUNDBALL: dist *= 0.5
        elif htype == BattedBallType.POPUP: dist *= 0.3
        
        dist = max(0, dist)
        spray = random.gauss(0, 25)
        
        rad = math.radians(spray)
        land_x = dist * math.sin(rad)
        land_y = dist * math.cos(rad)
        
        v_y = v_ms * math.sin(math.radians(angle))
        hang_time = (2 * v_y) / 9.8
        if htype == BattedBallType.GROUNDBALL:
            hang_time = dist / (v_ms * 0.8)
        
        return BattedBallData(velo, angle, spray, htype, dist, hang_time, land_x, land_y, [], quality)

class AdvancedDefenseEngine:
    """
    超本格守備エンジン: 空間座標・時間・UZR計算
    """
    def judge(self, ball: BattedBallData, defense_team: Team, team_level: TeamLevel = TeamLevel.FIRST, stadium: Stadium = None):
        abs_spray = abs(ball.spray_angle)
        
        # HR判定
        base_fence = 122 - (abs_spray / 45.0) * (122 - 100)
        pf_hr = stadium.pf_hr if stadium else 1.0
        fence_dist = base_fence / math.sqrt(pf_hr) 
        if ball.hit_type == BattedBallType.FLYBALL and ball.distance > fence_dist and abs_spray < 45:
            return PlayResult.HOME_RUN
        
        if abs_spray > 45: return PlayResult.FOUL

        # 1. 最適な野手を探す
        target_pos = (ball.landing_x, ball.landing_y)
        best_fielder, fielder_type, initial_pos = self._find_nearest_fielder(target_pos, defense_team, team_level)
        
        if not best_fielder:
            return PlayResult.SINGLE 

        # 2. 捕球判定 (Intercept Logic)
        dist_to_ball = math.sqrt((target_pos[0] - initial_pos[0])**2 + (target_pos[1] - initial_pos[1])**2)
        
        range_stat = best_fielder.stats.get_defense_range(getattr(Position, fielder_type))
        range_stat = range_stat * (1.0 + (best_fielder.condition - 5) * 0.02)
        speed_stat = get_effective_stat(best_fielder, 'speed')
        
        max_speed = 5.0 + (speed_stat / 100.0) * 4.5
        reaction_delay = 0.5 - (range_stat / 200.0)
        
        time_needed = reaction_delay + (dist_to_ball / max_speed)
        
        if ball.hit_type in [BattedBallType.FLYBALL, BattedBallType.POPUP, BattedBallType.LINEDRIVE]:
            time_available = ball.hang_time
            if ball.hit_type == BattedBallType.LINEDRIVE:
                 if dist_to_ball < 3.0: time_needed = 0 
        else:
            ball_speed_ms = (ball.exit_velocity / 3.6) * 0.6 
            time_available = dist_to_ball / max(1.0, ball_speed_ms)
            if ball.hit_type == BattedBallType.GROUNDBALL and ball.distance < 30:
                 time_available = 10.0 

        # 3. 捕球確率 (Catch Probability)
        time_diff = time_available - time_needed
        catch_prob = 0.0
        if time_diff > 0.5: catch_prob = 0.99
        elif time_diff > 0.0: catch_prob = 0.5 + time_diff 
        elif time_diff > -0.3: catch_prob = 0.5 + (time_diff / 0.6) 
        else: catch_prob = 0.0
        
        if ball.contact_quality == "hard": catch_prob *= 0.85
        if ball.hit_type == BattedBallType.LINEDRIVE: catch_prob *= 0.9
        
        if stadium: catch_prob /= stadium.pf_1b

        catch_prob = max(0.0, min(0.99, catch_prob))
        
        is_caught = random.random() < catch_prob
        
        # 4. ヒットの種類を予測 (UZR計算用)
        # もし捕れなかったらどういう結果になっていたか？
        potential_hit_result = self._judge_hit_type_potential(ball, target_pos, stadium)
        
        # 5. 指標計算 (UZR - RngR)
        # RngR = (PlaysMade - CatchProb) * RunValue_of_Hit
        # このプレーの得点価値（守備側視点）：
        # ヒットなら -RunValue(Hit) + RunValue(Out) 分の失点
        # アウトなら +RunValue(Hit) - RunValue(Out) 分の得点阻止
        
        # ここではシンプルに「その打球の潜在的得点価値」を防いだかどうかで計算
        # Out Valueは-0.27だが、UZRの文脈では「平均的な野手との差」を見る
        # ここでは「得点を防いだ量」として計算
        
        potential_rv = RUN_VALUES.get("Single", 0.9)
        if potential_hit_result == PlayResult.DOUBLE: potential_rv = RUN_VALUES.get("Double", 1.27)
        elif potential_hit_result == PlayResult.TRIPLE: potential_rv = RUN_VALUES.get("Triple", 1.62)
        
        # 捕球の価値 = ヒットを防いだ価値 - アウトの価値(アウトは当たり前なので、その分引くというより、ヒットとの差分が価値)
        # 厳密な1.02方式: 
        # Plus (Catch): (1 - Prob) * (RV_Hit - RV_Out)
        # Minus (Miss): (0 - Prob) * (RV_Hit - RV_Out)
        # RV_Outはマイナスなので、 (RV_Hit - RV_Out) は大きなプラスになる（例: 0.9 - (-0.27) = 1.17）
        
        play_value = potential_rv - RUN_VALUES["Out"]
        
        self._update_defensive_metrics(best_fielder, team_level, catch_prob, is_caught, play_value)

        # 6. 結果の確定と返却
        if is_caught:
            error_rating = get_effective_stat(best_fielder, 'error')
            error_prob = max(0.001, 0.03 - (error_rating * 0.0003))
            if random.random() < error_prob:
                # エラー時のUZR計算 (ErrR)
                # エラーによって失った価値 = play_value + エラー出塁の価値
                # 簡易的に ErrR = - (play_value + 0.5)
                self._update_metrics_error(best_fielder, team_level, play_value)
                return PlayResult.ERROR
            
            if ball.hit_type == BattedBallType.FLYBALL: return PlayResult.FLYOUT
            if ball.hit_type == BattedBallType.POPUP: return PlayResult.POPUP_OUT
            if ball.hit_type == BattedBallType.LINEDRIVE: return PlayResult.LINEOUT
            
            return self._judge_grounder_throw(best_fielder, ball, team_level)
            
        else:
            return potential_hit_result

    def _find_nearest_fielder(self, ball_pos, team, team_level):
        min_dist = 999.0
        best_f = None
        best_type = ""
        best_init = (0,0)
        
        lineup = team.current_lineup
        if team_level == TeamLevel.SECOND: lineup = team.farm_lineup
        elif team_level == TeamLevel.THIRD: lineup = team.third_lineup
        
        pos_map = {}
        for idx in lineup:
            if 0 <= idx < len(team.players):
                p = team.players[idx]
                if p.position != Position.DH and p.position != Position.PITCHER:
                    pos_map[p.position] = p
        
        pitcher = team.players[team.starting_pitcher_idx] 
        pos_map[Position.PITCHER] = pitcher

        for pos_enum, coords in FIELD_COORDS.items():
            if pos_enum in pos_map:
                dist = math.sqrt((ball_pos[0] - coords[0])**2 + (ball_pos[1] - coords[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    best_f = pos_map[pos_enum]
                    best_type = pos_enum.name 
                    best_init = coords
        
        return best_f, best_type, best_init

    def _judge_grounder_throw(self, fielder, ball, team_level):
        # 内野ゴロ送球・ARM計算
        base_1b_pos = (20.0, 20.0) 
        ball_x = ball.landing_x
        ball_y = ball.landing_y
        dist_to_1b = math.sqrt((ball_x - base_1b_pos[0])**2 + (ball_y - base_1b_pos[1])**2)
        
        arm = get_effective_stat(fielder, 'arm')
        throw_speed = 30 + (arm / 100.0) * 15
        transfer_time = 0.8 - (get_effective_stat(fielder, 'error') / 200.0)
        throw_time = transfer_time + (dist_to_1b / throw_speed)
        
        runner_time = 4.1 # リーグ平均
        
        # ARM評価 (送球によるアウト寄与)
        # 際どいタイミング(±0.2秒)でアウトにしたらARM評価プラス
        time_margin = runner_time - throw_time
        rec = fielder.get_record_by_level(team_level)
        
        if throw_time < runner_time:
            if 0 < time_margin < 0.3:
                 # ギリギリのアウト: 肩のおかげ
                 rec.def_drs_raw += 0.2 # ARM加点
            return PlayResult.GROUNDOUT
        else:
            if -0.3 < time_margin < 0:
                 # ギリギリのセーフ: 肩が弱かったせい?
                 rec.def_drs_raw -= 0.1 # ARM減点
            return PlayResult.SINGLE 

    def _judge_hit_type_potential(self, ball, ball_pos, stadium):
        dist = ball.distance
        pf_2b = stadium.pf_2b if stadium else 1.0
        pf_3b = stadium.pf_3b if stadium else 1.0
        
        double_threshold = 65.0 / math.sqrt(pf_2b)
        triple_threshold = 105.0 / math.sqrt(pf_3b)
        
        is_behind_fielder = ball_pos[1] > 80 
        
        if dist > triple_threshold and is_behind_fielder:
             if random.random() < 0.3: return PlayResult.TRIPLE
             return PlayResult.DOUBLE
        
        if dist > double_threshold:
            if ball.hit_type == BattedBallType.LINEDRIVE: return PlayResult.DOUBLE
            if is_behind_fielder: return PlayResult.DOUBLE
        
        return PlayResult.SINGLE

    def _update_defensive_metrics(self, fielder, team_level, catch_prob, is_caught, play_value):
        # 1.02 UZR (RngR) Calculation
        rec = fielder.get_record_by_level(team_level)
        rec.def_opportunities += 1
        rec.def_difficulty_sum += (1.0 - catch_prob) # 参考用
        
        if is_caught:
            # Plus: (1 - CatchProb) * Value
            rng_r = (1.0 - catch_prob) * play_value
            rec.def_plays_made += 1
            rec.def_drs_raw += rng_r
        else:
            # Minus: (0 - CatchProb) * Value
            rng_r = (0.0 - catch_prob) * play_value
            rec.def_drs_raw += rng_r # マイナス値を加算

    def _update_metrics_error(self, fielder, team_level, play_value):
        # ErrR (Error Runs)
        # エラーをしなかった場合の期待値(RngRに含まれる)を取り消し、さらにペナルティ
        # ここでは簡易的に DRS Raw から大きく引く
        rec = fielder.get_record_by_level(team_level)
        rec.def_drs_raw -= (play_value + 0.5)

class LiveGameEngine:
    def __init__(self, home: Team, away: Team, team_level: TeamLevel = TeamLevel.FIRST):
        self.home_team = home
        self.away_team = away
        self.team_level = team_level
        self.state = GameState()
        self.pitch_gen = PitchGenerator()
        self.bat_gen = BattedBallGenerator()
        self.def_eng = AdvancedDefenseEngine()
        self.ai = AIManager()
        self.game_stats = defaultdict(lambda: defaultdict(int))
        
        self.stadium = getattr(self.home_team, 'stadium', None)
        if not self.stadium:
             self.stadium = Stadium(name=f"{home.name} Stadium")

        self._init_starters()

        if self.team_level == TeamLevel.FIRST:
            self._ensure_valid_lineup(self.home_team)
            self._ensure_valid_lineup(self.away_team)

    def _ensure_valid_lineup(self, team: Team):
        if not team.current_lineup or len(team.current_lineup) < 9:
            players = team.get_active_roster_players()
            new_lineup = generate_best_lineup(team, players)
            team.current_lineup = new_lineup
            return

        has_valid_catcher = False
        catcher_idx = -1
        if hasattr(team, 'lineup_positions') and len(team.lineup_positions) == 9:
            for i, pos_str in enumerate(team.lineup_positions):
                if pos_str in ["捕", "捕手"]:
                    catcher_idx = team.current_lineup[i]
                    break
        
        if catcher_idx == -1:
            for idx in team.current_lineup:
                if 0 <= idx < len(team.players):
                    p = team.players[idx]
                    if p.position == Position.CATCHER:
                        has_valid_catcher = True
                        break
        else:
            if 0 <= catcher_idx < len(team.players):
                p = team.players[catcher_idx]
                if p.stats.get_defense_range(Position.CATCHER) >= 20:
                    has_valid_catcher = True

        if not has_valid_catcher:
            players = team.get_active_roster_players()
            batters = [p for p in players if p.position != Position.PITCHER]
            new_lineup = generate_best_lineup(team, batters)
            team.current_lineup = new_lineup

    def _init_starters(self):
        hp = self.home_team.get_today_starter() or self.home_team.players[0]
        ap = self.away_team.get_today_starter() or self.away_team.players[0]
        
        try:
            self.state.home_pitcher_idx = self.home_team.players.index(hp)
        except ValueError:
            self.state.home_pitcher_idx = 0
            hp = self.home_team.players[0]
            
        try:
            self.state.away_pitcher_idx = self.away_team.players.index(ap)
        except ValueError:
            self.state.away_pitcher_idx = 0
            ap = self.away_team.players[0]

        self.state.home_pitchers_used.append(hp)
        self.state.away_pitchers_used.append(ap)
        self.game_stats[hp]['games_pitched'] = 1
        self.game_stats[ap]['games_pitched'] = 1
        self.game_stats[hp]['games_started'] = 1
        self.game_stats[ap]['games_started'] = 1

    def get_current_batter(self) -> Tuple[Player, int]:
        team = self.away_team if self.state.is_top else self.home_team
        order_idx = self.state.away_batter_order if self.state.is_top else self.state.home_batter_order
        lineup = team.current_lineup
        if self.team_level == TeamLevel.SECOND: lineup = team.farm_lineup
        elif self.team_level == TeamLevel.THIRD: lineup = team.third_lineup
        if not lineup: return team.players[0], 0
        p_idx = lineup[order_idx % len(lineup)]
        return team.players[p_idx], order_idx

    def get_current_pitcher(self) -> Tuple[Player, int]:
        team = self.home_team if self.state.is_top else self.away_team
        idx = self.state.home_pitcher_idx if self.state.is_top else self.state.away_pitcher_idx
        return team.players[idx], idx

    def get_current_catcher(self) -> Optional[Player]:
        team = self.home_team if self.state.is_top else self.away_team
        lineup = team.current_lineup
        if self.team_level == TeamLevel.SECOND: lineup = team.farm_lineup
        elif self.team_level == TeamLevel.THIRD: lineup = team.third_lineup
        if not lineup: return None
        for p_idx in lineup:
            if team.players[p_idx].position == Position.CATCHER:
                return team.players[p_idx]
        return None

    def simulate_pitch(self, manual_strategy=None):
        batter, _ = self.get_current_batter()
        pitcher, _ = self.get_current_pitcher()
        catcher = self.get_current_catcher()
        
        defense_team = self.home_team if self.state.is_top else self.away_team
        offense_team = self.away_team if self.state.is_top else self.home_team
        
        strategy = manual_strategy or self.ai.decide_strategy(self.state, offense_team, defense_team, batter)
        pitch_strategy = self.ai.decide_pitch_strategy(self.state, pitcher, batter)
        
        if strategy == "STEAL":
            res = self._attempt_steal(catcher)
            if res: return PitchResult.BALL, None, None

        pitch = self.pitch_gen.generate_pitch(pitcher, batter, catcher, self.state, pitch_strategy, self.stadium)
        
        if self.state.is_top: self.state.away_pitch_count += 1
        else: self.state.home_pitch_count += 1
        
        res, ball = self._resolve_contact(batter, pitcher, pitch, strategy)
        self.process_pitch_result(res, pitch, ball, strategy)
        return res, pitch, ball

    def _resolve_contact(self, batter, pitcher, pitch, strategy):
        if not pitch.location.is_strike:
            control = get_effective_stat(pitcher, 'control')
            hbp_prob = 0.003 + max(0, (50 - control) * 0.0003)
            if random.random() < hbp_prob:
                return PitchResult.HIT_BY_PITCH, None

        if strategy == "BUNT":
            bunt_skill = get_effective_stat(batter, 'bunt_sac')
            difficulty = 20 if not pitch.location.is_strike else 0
            if random.uniform(0, 100) > (bunt_skill - difficulty):
                return PitchResult.FOUL if random.random() < 0.8 else PitchResult.STRIKE_SWINGING, None
            else:
                ball = self.bat_gen.generate(batter, pitcher, pitch, self.state, strategy)
                return PitchResult.IN_PLAY, ball

        eye = get_effective_stat(batter, 'eye')
        
        z_swing_base = 0.75 + (eye - 50) * 0.002 
        o_swing_base = 0.32 - (eye - 50) * 0.005 
        
        if pitch.location.is_strike:
            swing_prob = z_swing_base
            if self.state.strikes == 2: swing_prob = min(0.98, swing_prob + 0.2)
        else:
            swing_prob = o_swing_base
            if self.state.strikes == 2: swing_prob += 0.15

        if strategy == "POWER": swing_prob += 0.1 
        if strategy == "MEET": swing_prob -= 0.1 

        swing_prob = max(0.01, min(0.99, swing_prob))
        
        if random.random() >= swing_prob:
            return PitchResult.STRIKE_CALLED if pitch.location.is_strike else PitchResult.BALL, None
            
        contact = get_effective_stat(batter, 'contact', opponent=pitcher)
        hit_prob = 0.78 + (contact - 50)*0.005
        if not pitch.location.is_strike: hit_prob -= 0.2
        
        if self.stadium:
            hit_prob /= max(0.5, self.stadium.pf_so)

        if random.random() > hit_prob: return PitchResult.STRIKE_SWINGING, None
        if random.random() < 0.35: return PitchResult.FOUL, None
             
        ball = self.bat_gen.generate(batter, pitcher, pitch, self.state, strategy)
        return PitchResult.IN_PLAY, ball

    def _attempt_steal(self, catcher):
        runner = self.state.runner_1b
        if not runner: return False
        
        runner_spd = get_effective_stat(runner, 'speed')
        catcher_arm = get_effective_stat(catcher, 'arm') if catcher else 50
        
        success_prob = 0.70 + (runner_spd - 50)*0.01 - (catcher_arm - 50)*0.01
        
        if random.random() < success_prob:
            self.state.runner_2b = runner; self.state.runner_1b = None
            self.game_stats[runner]['stolen_bases'] += 1
            return True
        else:
            self.state.runner_1b = None; self.state.outs += 1
            self.game_stats[runner]['caught_stealing'] += 1
            return True

    def process_pitch_result(self, res, pitch, ball, strategy="NORMAL"):
        pitcher, _ = self.get_current_pitcher()
        batter, _ = self.get_current_batter()

        is_in_zone = pitch.location.is_strike
        is_swing = res in [PitchResult.STRIKE_SWINGING, PitchResult.FOUL, PitchResult.IN_PLAY]
        is_contact = res in [PitchResult.FOUL, PitchResult.IN_PLAY]
        is_whiff = res == PitchResult.STRIKE_SWINGING
        
        self.game_stats[pitcher]['pitches_thrown'] += 1
        self.game_stats[batter]['pitches_seen'] += 1

        if is_in_zone:
            self.game_stats[pitcher]['zone_pitches'] += 1
            self.game_stats[batter]['zone_pitches'] += 1
        else:
            self.game_stats[pitcher]['chase_pitches'] += 1
            self.game_stats[batter]['chase_pitches'] += 1

        if is_swing:
            self.game_stats[pitcher]['swings'] += 1
            self.game_stats[batter]['swings'] += 1
            
            if is_in_zone:
                self.game_stats[pitcher]['zone_swings'] += 1
                self.game_stats[batter]['zone_swings'] += 1
                if is_contact:
                    self.game_stats[pitcher]['zone_contact'] += 1
                    self.game_stats[batter]['zone_contact'] += 1
            else:
                self.game_stats[pitcher]['chase_swings'] += 1
                self.game_stats[batter]['chase_swings'] += 1
                if is_contact:
                    self.game_stats[pitcher]['chase_contact'] += 1
                    self.game_stats[batter]['chase_contact'] += 1
            
            if is_whiff:
                self.game_stats[pitcher]['whiffs'] += 1
                self.game_stats[batter]['whiffs'] += 1

        is_strike_result = res in [PitchResult.STRIKE_CALLED, PitchResult.STRIKE_SWINGING, PitchResult.FOUL, PitchResult.IN_PLAY]
        
        if is_strike_result:
            self.game_stats[pitcher]['strikes_thrown'] += 1
            if self.state.balls == 0 and self.state.strikes == 0:
                self.game_stats[pitcher]['first_pitch_strikes'] += 1
                self.game_stats[batter]['first_pitch_strikes'] += 1
        else:
            self.game_stats[pitcher]['balls_thrown'] += 1

        if res == PitchResult.BALL:
            self.state.balls += 1
            if self.state.balls >= 4: self._walk()
        
        elif res == PitchResult.HIT_BY_PITCH:
            self._walk(is_hbp=True)

        elif res in [PitchResult.STRIKE_CALLED, PitchResult.STRIKE_SWINGING]:
            self.state.strikes += 1
            if self.state.strikes >= 3: 
                self.game_stats[pitcher]['strikeouts_pitched'] += 1
                self.game_stats[batter]['plate_appearances'] += 1
                self.game_stats[batter]['at_bats'] += 1
                self.game_stats[batter]['strikeouts'] += 1
                self._out() 

        elif res == PitchResult.FOUL:
            if self.state.strikes < 2: self.state.strikes += 1
        
        elif res == PitchResult.IN_PLAY:
            defense_team = self.home_team if self.state.is_top else self.away_team
            play = self.def_eng.judge(ball, defense_team, self.team_level, self.stadium)
            
            if ball.contact_quality == "hard":
                self.game_stats[batter]['hard_hit_balls'] += 1
                self.game_stats[pitcher]['hard_hit_balls'] += 1
            elif ball.contact_quality == "medium":
                self.game_stats[batter]['medium_hit_balls'] += 1
                self.game_stats[pitcher]['medium_hit_balls'] += 1
            elif ball.contact_quality == "soft":
                self.game_stats[batter]['soft_hit_balls'] += 1
                self.game_stats[pitcher]['soft_hit_balls'] += 1
                
            batter_hand = getattr(batter, 'bats', "右")
            if batter_hand == "両":
                pitcher_hand = getattr(pitcher, 'throws', "右")
                batter_hand = "左" if pitcher_hand == "右" else "右"
                
            angle = ball.spray_angle
            is_pull = False
            is_oppo = False
            is_cent = False
            
            if abs(angle) <= 15:
                is_cent = True
            elif batter_hand == "右":
                if angle < -15: is_pull = True 
                else: is_oppo = True 
            else: 
                if angle > 15: is_pull = True 
                else: is_oppo = True 
            
            if is_pull:
                self.game_stats[batter]['pull_balls'] += 1
                self.game_stats[pitcher]['pull_balls'] += 1
            elif is_cent:
                self.game_stats[batter]['center_balls'] += 1
                self.game_stats[pitcher]['center_balls'] += 1
            elif is_oppo:
                self.game_stats[batter]['oppo_balls'] += 1
                self.game_stats[pitcher]['oppo_balls'] += 1

            if ball.hit_type == BattedBallType.GROUNDBALL:
                self.game_stats[pitcher]['ground_balls'] += 1
                self.game_stats[batter]['ground_balls'] += 1
            elif ball.hit_type == BattedBallType.FLYBALL:
                self.game_stats[pitcher]['fly_balls'] += 1
                self.game_stats[batter]['fly_balls'] += 1
            elif ball.hit_type == BattedBallType.LINEDRIVE:
                self.game_stats[pitcher]['line_drives'] += 1
                self.game_stats[batter]['line_drives'] += 1
            elif ball.hit_type == BattedBallType.POPUP:
                self.game_stats[pitcher]['popups'] += 1
                self.game_stats[batter]['popups'] += 1
                
            self.game_stats[pitcher]['balls_in_play'] += 1
            self.game_stats[batter]['balls_in_play'] += 1

            if play == PlayResult.FOUL:
                if self.state.strikes < 2: self.state.strikes += 1
            else:
                self._resolve_play(play, strategy)
        
        return res

    def _record_pf(self, batter: Player, pitcher: Player):
        pf = self.stadium.pf_runs if self.stadium else 1.0
        self.game_stats[batter]['sum_pf_runs'] += pf
        self.game_stats[pitcher]['sum_pf_runs'] += pf

    def _walk(self, is_hbp=False):
        batter, _ = self.get_current_batter()
        pitcher, _ = self.get_current_pitcher()
        self.game_stats[batter]['plate_appearances'] += 1
        
        if is_hbp:
            self.game_stats[batter]['hit_by_pitch'] += 1
            self.game_stats[pitcher]['hit_batters'] += 1
        else:
            self.game_stats[batter]['walks'] += 1
            self.game_stats[pitcher]['walks_allowed'] += 1
        
        self._record_pf(batter, pitcher)
        self._advance_runners(1, batter, is_walk=True)
        self._reset_count(); self._next_batter()

    def _out(self):
        pitcher, _ = self.get_current_pitcher()
        self.state.outs += 1
        self.game_stats[pitcher]['innings_pitched'] += 0.333
        
        batter, _ = self.get_current_batter()
        self._record_pf(batter, pitcher)

        self._reset_count(); self._next_batter()
        if self.state.outs >= 3: self._change_inning()

    def _resolve_play(self, play, strategy):
        batter, _ = self.get_current_batter()
        pitcher, _ = self.get_current_pitcher()
        
        self.game_stats[batter]['plate_appearances'] += 1
        
        if play in [PlayResult.SINGLE, PlayResult.DOUBLE, PlayResult.TRIPLE, PlayResult.HOME_RUN]:
            self.game_stats[batter]['at_bats'] += 1
            self.game_stats[batter]['hits'] += 1
            self.game_stats[pitcher]['hits_allowed'] += 1
            if play == PlayResult.DOUBLE: self.game_stats[batter]['doubles'] += 1
            if play == PlayResult.TRIPLE: self.game_stats[batter]['triples'] += 1
            if play == PlayResult.HOME_RUN: 
                self.game_stats[batter]['home_runs'] += 1
                self.game_stats[pitcher]['home_runs_allowed'] += 1
            
            self._record_pf(batter, pitcher)
            self._reset_count(); self._next_batter()
            
            scored = 0
            if play == PlayResult.HOME_RUN:
                scored = 1 + (1 if self.state.runner_1b else 0) + (1 if self.state.runner_2b else 0) + (1 if self.state.runner_3b else 0)
                self.state.runner_1b = self.state.runner_2b = self.state.runner_3b = None
            elif play == PlayResult.SINGLE: scored = self._advance_runners(1, batter)
            elif play == PlayResult.DOUBLE: scored = self._advance_runners(2, batter)
            elif play == PlayResult.TRIPLE: scored = self._advance_runners(3, batter)
            
            if scored > 0:
                self.game_stats[batter]['rbis'] += scored
                self.game_stats[pitcher]['runs_allowed'] += scored
                self.game_stats[pitcher]['earned_runs'] += scored
                self._score(scored)
            return play

        if play == PlayResult.ERROR:
            self.game_stats[batter]['at_bats'] += 1
            self.game_stats[batter]['reach_on_error'] += 1
            self._record_pf(batter, pitcher)
            self._reset_count(); self._next_batter()
            scored = self._advance_runners(1, batter)
            if scored > 0:
                self.game_stats[batter]['rbis'] += scored
                self.game_stats[pitcher]['runs_allowed'] += scored
                self._score(scored)
            return play

        is_sac_fly = False
        is_sac_bunt = False
        is_double_play = False
        
        scored = 0
        
        if play == PlayResult.FLYOUT and self.state.runner_3b and self.state.outs < 2:
            if random.random() < 0.85:
                is_sac_fly = True
                scored = 1
                self.state.runner_3b = None
        
        elif play == PlayResult.GROUNDOUT and self.state.runner_1b and self.state.outs < 2 and strategy != "BUNT":
            dp_prob = 0.6
            if random.random() < dp_prob:
                is_double_play = True
                self.state.runner_1b = None
        
        elif strategy == "BUNT" and play == PlayResult.GROUNDOUT:
             if self.state.is_runner_on():
                 is_sac_bunt = True
                 scored = self._advance_runners_bunt()
        
        self._record_pf(batter, pitcher)
        self.game_stats[pitcher]['innings_pitched'] += 0.333
        self.state.outs += 1

        if is_sac_fly:
            self.game_stats[batter]['sacrifice_flies'] += 1
            self.game_stats[batter]['rbis'] += scored
            self.game_stats[pitcher]['runs_allowed'] += scored
            self.game_stats[pitcher]['earned_runs'] += scored
            self._score(scored)
        
        elif is_sac_bunt:
            self.game_stats[batter]['sacrifice_hits'] += 1
            if scored > 0:
                self.game_stats[batter]['rbis'] += scored
                self.game_stats[pitcher]['runs_allowed'] += scored
                self.game_stats[pitcher]['earned_runs'] += scored
                self._score(scored)

        elif is_double_play:
            self.game_stats[batter]['at_bats'] += 1
            self.game_stats[batter]['grounded_into_dp'] += 1
            self.state.outs += 1
            self.game_stats[pitcher]['innings_pitched'] += 0.333
            
        else:
            self.game_stats[batter]['at_bats'] += 1
            if scored > 0 and is_sac_fly == False: 
                self.game_stats[batter]['rbis'] += scored
                self.game_stats[pitcher]['runs_allowed'] += scored
                self.game_stats[pitcher]['earned_runs'] += scored
                self._score(scored)

        self._reset_count(); self._next_batter()
        if self.state.outs >= 3: self._change_inning()
        
        return play

    def _advance_runners_bunt(self) -> int:
        score = 0
        if self.state.runner_3b:
            score += 1
            self.state.runner_3b = None
        if self.state.runner_2b:
            self.state.runner_3b = self.state.runner_2b
            self.state.runner_2b = None
        if self.state.runner_1b:
            self.state.runner_2b = self.state.runner_1b
            self.state.runner_1b = None
        return score

    def _advance_runners(self, bases, batter, is_walk=False):
        score = 0
        if is_walk:
            if self.state.runner_1b:
                if self.state.runner_2b:
                    if self.state.runner_3b: score += 1
                    self.state.runner_3b = self.state.runner_3b if self.state.runner_3b else self.state.runner_2b
                self.state.runner_2b = self.state.runner_2b if self.state.runner_2b else self.state.runner_1b
            self.state.runner_1b = batter
        else:
            if bases == 4: pass
            elif bases == 3:
                if self.state.runner_3b: score += 1
                if self.state.runner_2b: score += 1
                if self.state.runner_1b: score += 1
                self.state.runner_1b = self.state.runner_2b = None
                self.state.runner_3b = batter
            elif bases == 2:
                if self.state.runner_3b: score += 1; self.state.runner_3b = None
                if self.state.runner_2b: score += 1; self.state.runner_2b = None
                if self.state.runner_1b:
                    if random.random() < 0.4: score += 1; self.state.runner_1b = None
                    else: self.state.runner_3b = self.state.runner_1b; self.state.runner_1b = None
                self.state.runner_2b = batter
            elif bases == 1:
                if self.state.runner_3b: score += 1; self.state.runner_3b = None
                if self.state.runner_2b:
                    if random.random() < 0.6: score += 1; self.state.runner_2b = None
                    else: self.state.runner_3b = self.state.runner_2b; self.state.runner_2b = None
                if self.state.runner_1b: self.state.runner_2b = self.state.runner_1b
                self.state.runner_1b = batter
        return score
    
    def _score(self, pts):
        if self.state.is_top: self.state.away_score += pts
        else: self.state.home_score += pts

    def _reset_count(self):
        self.state.balls = 0; self.state.strikes = 0

    def _next_batter(self):
        team = self.away_team if self.state.is_top else self.home_team
        lineup = team.current_lineup
        if self.team_level == TeamLevel.SECOND: lineup = team.farm_lineup
        elif self.team_level == TeamLevel.THIRD: lineup = team.third_lineup
        n = len(lineup)
        if n == 0:
            if self.state.is_top: self.state.away_batter_order = 0
            else: self.state.home_batter_order = 0
            return
        if self.state.is_top: self.state.away_batter_order = (self.state.away_batter_order + 1) % n
        else: self.state.home_batter_order = (self.state.home_batter_order + 1) % n

    def _change_inning(self):
        self.state.outs = 0
        self.state.runner_1b = self.state.runner_2b = self.state.runner_3b = None
        if not self.state.is_top: self.state.inning += 1
        self.state.is_top = not self.state.is_top

    def is_game_over(self):
        if self.state.inning > 9:
             if self.state.is_top: return False
             if self.state.home_score != self.state.away_score: return True
             if self.state.inning >= 12 and self.state.outs >= 3: return True
        if self.state.inning >= 9 and not self.state.is_top and self.state.home_score > self.state.away_score: return True
        return False

    def finalize_game_stats(self):
        win_p, loss_p = None, None
        if not self.state.home_pitchers_used or not self.state.away_pitchers_used: return

        if self.state.home_score > self.state.away_score:
            starter = self.state.home_pitchers_used[0]
            if self.game_stats[starter]['innings_pitched'] >= 5: win_p = starter
            else: win_p = self.state.home_pitchers_used[-1]
            loss_p = self.state.away_pitchers_used[0]
        elif self.state.away_score > self.state.home_score:
            starter = self.state.away_pitchers_used[0]
            if self.game_stats[starter]['innings_pitched'] >= 5: win_p = starter
            else: win_p = self.state.away_pitchers_used[-1]
            loss_p = self.state.home_pitchers_used[0]

        if win_p: self.game_stats[win_p]['wins'] = 1
        if loss_p: self.game_stats[loss_p]['losses'] = 1

        for player, stats in self.game_stats.items():
            record = player.get_record_by_level(self.team_level)
            for key, val in stats.items():
                if hasattr(record, key):
                    current = getattr(record, key)
                    setattr(record, key, current + val)
            record.games += 1
            
            is_home_player = player in self.home_team.players
            if is_home_player:
                if player.position == Position.PITCHER:
                    record.home_games_pitched += 1
                else:
                    record.home_games += 1

    def get_winner(self):
        if self.state.home_score > self.state.away_score: return self.home_team.name
        if self.state.away_score > self.state.home_score: return self.away_team.name
        return "DRAW"