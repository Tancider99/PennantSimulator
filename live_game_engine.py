# -*- coding: utf-8 -*-
"""
ライブ試合エンジン (修正版: 全能力・調子反映 + get_rank復活)
"""
import random
import math
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from enum import Enum
from models import Position, Player, Team # 型ヒント用にインポート

# ========================================
# 定数・ユーティリティ
# ========================================

STRIKE_ZONE = {
    'width': 0.432,
    'height': 0.56,
    'center_x': 0.0,
    'center_z': 0.75, # 地面から75cm
    'half_width': 0.216,
    'half_height': 0.28
}

def get_rank(value: int) -> str:
    """能力値をランクに変換 (UI側で使用)"""
    if value >= 90: return "S"
    if value >= 80: return "A"
    if value >= 70: return "B"
    if value >= 60: return "C"
    if value >= 50: return "D"
    if value >= 40: return "E"
    if value >= 30: return "F"
    return "G"

def get_effective_stat(player: Player, stat_name: str, opponent: Optional[Player] = None, is_risp: bool = False, is_close_game: bool = False) -> float:
    """
    状況と調子を考慮した有効能力値を計算
    
    Args:
        player: 対象選手
        stat_name: 能力値のフィールド名
        opponent: 対戦相手（投手なら打者、打者なら投手）
        is_risp: 得点圏に走者がいるか (Runner In Scoring Position)
        is_close_game: 接戦かどうか (点差2点以内、7回以降など)
    """
    # 1. 基本値の取得
    if not hasattr(player.stats, stat_name):
        return 50.0
    base_value = getattr(player.stats, stat_name)
    
    # 2. 調子による補正 (基準5, 1につき±2%)
    # condition: 1(絶不調) - 9(絶好調)
    condition_diff = player.condition - 5
    condition_multiplier = 1.0 + (condition_diff * 0.02)
    
    value = base_value * condition_multiplier
    
    # 3. 特殊能力補正
    # --- 打者 ---
    if player.position != Position.PITCHER:
        # 対左投手
        if stat_name in ['contact', 'power'] and opponent and opponent.position == Position.PITCHER:
            # 投手の利き腕判定があればここで使うが、簡易的に左投手能力を参照して判定も可能
            # ここではopponentが左腕であるというフラグがないため、models.pyの設計に合わせて
            # 簡易的に「相手が左投手用能力を持っている＝左」とみなすか、ランダム性を残す
            # ※今回はデータ構造上利き腕がないため、vs_left能力自体の偏差を加味する
            
            # 自分の対左能力 (50が基準)
            vs_left = getattr(player.stats, 'vs_left_batter', 50)
            # 相手が左かどうか不明なため、50%の確率で適用、あるいは平均的に適用
            # ここでは「能力値としての対左」を、コンタクト・パワーへの永続的な微補正として扱う
            value += (vs_left - 50) * 0.2

        # チャンス
        if is_risp and stat_name in ['contact', 'power']:
            chance = getattr(player.stats, 'chance', 50)
            value += (chance - 50) * 0.5
            
        # メンタル (接戦時)
        if is_close_game:
            mental = getattr(player.stats, 'mental', 50)
            value += (mental - 50) * 0.3

    # --- 投手 ---
    else:
        # 対左打者
        if opponent and opponent.position != Position.PITCHER:
            # 打者の利き打席があれば判定。ここでは同様に補正のみ
            vs_left = getattr(player.stats, 'vs_left_pitcher', 50)
            value += (vs_left - 50) * 0.2
            
        # 対ピンチ
        if is_risp:
            pinch = getattr(player.stats, 'vs_pinch', 50)
            # ピンチに強いと変化球、制球、球威が上がる
            if stat_name in ['stuff', 'movement', 'control']:
                value += (pinch - 50) * 0.5
                
        # 安定感 (調子の影響度を緩和/増幅するが、ここでは能力への直接加算とする)
        if stat_name == 'control':
            stability = getattr(player.stats, 'stability', 50)
            # 安定感が高いと、調子が悪い時のマイナスを軽減
            if condition_diff < 0:
                mitigation = (stability - 50) * 0.2
                value += max(0, mitigation)

    return max(1.0, value)

# ========================================
# 列挙型
# ========================================

class PitchType(Enum):
    FASTBALL = "ストレート"
    SLIDER = "スライダー"
    CURVE = "カーブ"
    CHANGEUP = "チェンジアップ"
    FORK = "フォーク"
    SINKER = "シンカー"
    CUTTER = "カットボール"
    TWOSEAM = "ツーシーム"
    SHOOT = "シュート"
    SPLIT = "スプリット"

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
    INFIELD_HIT = "内野安打"
    STRIKEOUT = "三振"
    GROUNDOUT = "ゴロ"
    FLYOUT = "フライ"
    LINEOUT = "ライナー"
    POPUP_OUT = "内野フライ"
    DOUBLE_PLAY = "併殺打"
    WALK = "四球"
    HIT_BY_PITCH = "死球"
    SACRIFICE_FLY = "犠飛"
    SACRIFICE_BUNT = "犠打"
    STOLEN_BASE = "盗塁成功"
    CAUGHT_STEALING = "盗塁死"
    ERROR = "失策"
    
    # 内部処理用
    FOUL = "ファウル"
    BALL = "ボール"
    STRIKE = "ストライク"

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
    
    # 走者 (Player Object)
    runner_1b: Optional[Player] = None 
    runner_2b: Optional[Player] = None
    runner_3b: Optional[Player] = None
    
    home_score: int = 0
    away_score: int = 0
    
    home_batter_order: int = 0
    away_batter_order: int = 0
    
    home_pitcher_idx: int = 0
    away_pitcher_idx: int = 0
    
    # スタミナ (0-100)
    home_pitcher_stamina: float = 100.0
    away_pitcher_stamina: float = 100.0
    
    home_pitch_count: int = 0
    away_pitch_count: int = 0

    def is_runner_on(self) -> bool:
        return any([self.runner_1b, self.runner_2b, self.runner_3b])

    def is_risp(self) -> bool:
        return (self.runner_2b is not None) or (self.runner_3b is not None)

    def current_pitcher_stamina(self) -> float:
        return self.away_pitcher_stamina if self.is_top else self.home_pitcher_stamina

# ========================================
# AI マネージャー
# ========================================

class AIManager:
    """AIによる采配決定"""
    
    def decide_strategy(self, state: GameState, offense_team, defense_team, batter: Player) -> str:
        """攻撃側の作戦を決定"""
        score_diff = state.away_score - state.home_score if state.is_top else state.home_score - state.away_score
        is_late = state.inning >= 7
        is_close = abs(score_diff) <= 2
        
        # バント職人
        bunt_skill = get_effective_stat(batter, 'bunt_sac')
        
        # バント: 無死1塁/2塁、接戦、終盤、打力低め or バント職人
        if state.outs == 0 and (state.runner_1b or state.runner_2b) and not state.runner_3b:
            # 打撃力が低い(40以下) かつ 接戦
            batting_ab = batter.stats.overall_batting()
            if (is_close and is_late) or (bunt_skill > 70 and batting_ab < 45):
                return "BUNT"
        
        # 盗塁: ランナー1塁、俊足、接戦
        if state.runner_1b and not state.runner_2b and not state.runner_3b and state.outs < 2:
            runner_spd = get_effective_stat(state.runner_1b, 'speed')
            runner_stl = get_effective_stat(state.runner_1b, 'steal')
            
            steal_threshold = 80
            if is_close and is_late: steal_threshold = 70
            
            if runner_spd >= steal_threshold and runner_stl >= 60:
                if random.random() < 0.25: # 常に走るわけではない
                    return "STEAL"
        
        # 強振: 3-0, 3-1 カウントでパワーヒッター
        eff_power = get_effective_stat(batter, 'power', is_risp=state.is_risp())
        if state.balls >= 3 and state.strikes < 2 and eff_power > 60:
            return "POWER"
        
        # ミート打ち: 追い込まれていて、かつミートが得意
        eff_contact = get_effective_stat(batter, 'contact', is_risp=state.is_risp())
        eff_avoid_k = get_effective_stat(batter, 'avoid_k')
        if state.strikes == 2 and eff_contact > 50 and eff_avoid_k > 50:
            return "MEET"
            
        return "SWING"

    def decide_pitch_strategy(self, state: GameState, pitcher: Player, batter: Player) -> str:
        """守備側の配球方針"""
        # 投手能力
        eff_control = get_effective_stat(pitcher, 'control', opponent=batter, is_risp=state.is_risp())
        
        if state.balls >= 3:
            # 制球が良いなら際どく、悪いなら置きに行く
            return "STRIKE" 
        
        if state.strikes == 2:
            # 決め球を持っているか
            has_breaking = len(pitcher.stats.pitches) > 0
            if has_breaking and eff_control > 40:
                return "BALL" # 誘い球
        
        # 敬遠 (強打者かつ一塁空き、接戦終盤)
        eff_power = get_effective_stat(batter, 'power', is_risp=state.is_risp())
        if state.is_risp() and not state.runner_1b and eff_power > 85 and state.inning >= 8 and abs(state.home_score - state.away_score) <= 1:
             # 満塁策などは考慮せず簡易的に
            return "WALK"

        return "NORMAL"

# ========================================
# 投球・打球エンジン (全能力値反映)
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

    def generate_pitch(self, pitcher: Player, batter: Player, catcher: Player, state: GameState, strategy="NORMAL") -> PitchData:
        is_risp = state.is_risp()
        is_close = abs(state.home_score - state.away_score) <= 2
        
        # 能力値取得 (調子・対戦相手・状況込み)
        velocity = get_effective_stat(pitcher, 'velocity', batter, is_risp, is_close)
        control = get_effective_stat(pitcher, 'control', batter, is_risp, is_close)
        movement = get_effective_stat(pitcher, 'movement', batter, is_risp, is_close)
        stamina = get_effective_stat(pitcher, 'stamina', batter, is_risp, is_close)
        
        # 捕手リード補正 (controlに加算)
        if catcher:
            lead = get_effective_stat(catcher, 'catcher_lead', is_close_game=is_close)
            # リード50を基準に、Controlに±5%程度影響
            control += (lead - 50) * 0.2
        
        # スタミナ消費
        current_stamina = state.current_pitcher_stamina()
        # スタミナ限界付近で能力低下
        fatigue = 1.0
        if current_stamina < 30:
            fatigue = 0.9 + (current_stamina / 300.0) # 0.9 ~ 1.0
        if current_stamina <= 0:
            fatigue = 0.8
        
        # スタミナ減少計算
        pitch_cost = 0.5
        # 全力投球や変化球多用で消費増
        if is_risp: pitch_cost *= 1.2
        
        if state.is_top: state.away_pitcher_stamina = max(0, state.away_pitcher_stamina - pitch_cost)
        else: state.home_pitcher_stamina = max(0, state.home_pitcher_stamina - pitch_cost)
        
        # 球種決定
        pitch_type = None
        breaking_balls = getattr(pitcher.stats, 'breaking_balls', [])
        
        if strategy == "WALK":
            pitch_type = "ストレート" # 敬遠ストレート
        elif not breaking_balls:
            pitch_type = "ストレート"
        else:
            # 変化球割合 (球種が多いほどストレート率が下がるが最低40%)
            straight_prob = max(0.4, 0.7 - len(breaking_balls) * 0.1)
            # 決め球 (2ストライク)
            if state.strikes == 2: straight_prob *= 0.7
            
            if random.random() < straight_prob:
                pitch_type = "ストレート"
            else:
                # 変化球の中で、得意なものがあれば優先したいが、
                # 現在のデータ構造は {球種名: 数値} なので数値が高いものを優先
                pitches = pitcher.stats.pitches
                total_val = sum(pitches.values())
                r = random.uniform(0, total_val)
                curr = 0
                for p, v in pitches.items():
                    curr += v
                    if r <= curr:
                        pitch_type = p
                        break
                if not pitch_type: pitch_type = breaking_balls[0]
            
        base = self.PITCH_DATA.get(pitch_type, self.PITCH_DATA["ストレート"])
        
        # 球速決定
        base_velo = velocity * fatigue
        # ストレート以外は減速
        if pitch_type != "ストレート":
            speed_ratio = base["base_speed"] / 148.0
            base_velo *= speed_ratio
            
        velo = random.gauss(base_velo, 1.5) # バラつき
        velo = max(80, min(170, velo))
        
        # 変化量 (Movementが高いとキレが増す = 変化量増)
        move_factor = 1.0 + (movement - 50) * 0.01
        h_brk = base["h_break"] * move_factor + random.gauss(0, 2)
        v_brk = base["v_break"] * move_factor + random.gauss(0, 2)
        
        # ロケーション決定
        loc = self._calc_location(control * fatigue, state, strategy)
        
        # 軌道計算
        traj = self._calc_traj(velo, h_brk, v_brk, loc)
        
        return PitchData(pitch_type, round(velo,1), 2200, h_brk, v_brk, loc, (0,18.44,1.8), traj)

    def _calc_location(self, control, state, strategy):
        if strategy == "WALK":
            return PitchLocation(1.0, 1.5, False) # 完全なボール球

        # 精度 (Control 1-99)
        # 99 -> sigma 0.05m (約ボール半個分)
        # 50 -> sigma 0.15m
        # 1  -> sigma 0.25m
        sigma = max(0.05, 0.25 - (control * 0.002))
        
        # ターゲット中心
        tx, tz = 0, STRIKE_ZONE['center_z']
        
        if strategy == "STRIKE":
            sigma *= 0.8 # ストライクを取りに行くときは甘くなりやすいがバラつきは減る？
                         # ここでは「四隅を狙わず真ん中付近」にする
            pass 
        elif strategy == "BALL":
            # 誘い球 (低め or 外角)
            if random.random() < 0.6: tz -= 0.25 # 低め
            else: tx = 0.25 if random.random() < 0.5 else -0.25
        else:
            # 通常: 四隅を散らす
            if random.random() < 0.7: # 四隅狙い
                tx = random.choice([-0.2, 0.2])
                tz += random.choice([-0.2, 0.2])
                
        # 実際の投球位置 (正規分布)
        ax = random.gauss(tx, sigma)
        az = random.gauss(tz, sigma)
        
        # ストライク判定
        is_strike = (abs(ax) <= STRIKE_ZONE['half_width'] + 0.036 and  # ボール半径分少し広げる
                     abs(az - STRIKE_ZONE['center_z']) <= STRIKE_ZONE['half_height'] + 0.036)
                     
        return PitchLocation(ax, az, is_strike)

    def _calc_traj(self, velo, hb, vb, loc):
        path = []
        start = (random.uniform(-0.05, 0.05), 18.44, 1.8)
        end = (loc.x, 0, loc.z)
        steps = 15
        for i in range(steps + 1):
            t = i/steps
            # 簡易物理演算: 変化量は終端でのズレとして近似
            # sinカーブで変化を表現
            x = start[0] + (end[0]-start[0])*t + (hb/100 * 0.3)*math.sin(t*math.pi)
            y = start[1] * (1-t)
            # 重力 + 縦変化
            gravity_drop = 0.5 * 9.8 * (t * (18.44 / (velo/3.6)))**2
            # zは線形補間 + 変化 + 重力成分(v_breakに含まれると仮定するか、別途引くか)
            # ここではv_breakは重力以外の変化成分とする
            z = start[2] + (end[2]-start[2])*t + (vb/100 * 0.3)*(t**2)
            path.append((x,y,z))
        return path

class BattedBallGenerator:
    def generate(self, batter: Player, pitcher: Player, pitch: PitchData, state: GameState, strategy="SWING"):
        is_risp = state.is_risp()
        is_close = abs(state.home_score - state.away_score) <= 2

        # 打者能力 (調子込み)
        power = get_effective_stat(batter, 'power', opponent=pitcher, is_risp=is_risp, is_close_game=is_close)
        contact = get_effective_stat(batter, 'contact', opponent=pitcher, is_risp=is_risp, is_close_game=is_close)
        gap = get_effective_stat(batter, 'gap', opponent=pitcher, is_risp=is_risp)
        trajectory = getattr(batter.stats, 'trajectory', 2) # 1-4
        
        # 投手能力 (被弾しにくさに関係)
        p_movement = get_effective_stat(pitcher, 'movement', opponent=batter, is_risp=is_risp)
        p_gb_tendency = getattr(pitcher.stats, 'gb_tendency', 50)
        
        # 戦術補正
        meet_bonus = 0
        if strategy == "MEET": meet_bonus = 15
        if strategy == "POWER": meet_bonus = -15
        
        # コンタクト品質 (Contact vs Pitch Quality)
        # pitch.location.is_strike でないボールを打つと品質低下
        ball_penalty = 0 if pitch.location.is_strike else 20
        
        # Movementが高いと芯を外しやすくなる
        con_eff = contact + meet_bonus - (p_movement - 50) * 0.4 - ball_penalty
        
        quality_roll = random.uniform(0, 100)
        
        # ジャストミート判定
        # Contact 50 -> con_eff 50 -> 20% Hard, 45% Medium, 35% Soft
        if quality_roll < con_eff * 0.4: quality = "hard"
        elif quality_roll < con_eff * 0.9: quality = "medium"
        else: quality = "soft"
        
        # 打球速度 (Exit Velocity)
        # Power 50 -> ~140km/h (Medium)
        base_v = 110 + (power - 50) * 0.8
        
        if strategy == "POWER": base_v += 10
        if quality == "hard": base_v += 20 + (power/10) # パワーがあるほど芯で捉えた時速い
        if quality == "soft": base_v -= 30
        
        # 弾道 (Trajectory 1:低 ~ 4:高)
        # Trajectory 2 (中弾道) -> 10~25度くらい
        traj_bias = 5 + (trajectory * 5) # 1->10, 4->25
        
        # 投手ゴロ傾向の影響
        gb_effect = (p_gb_tendency - 50) * 0.2
        angle_center = traj_bias - gb_effect
        
        # 高めはフライになりやすく、低めはゴロになりやすい
        if pitch.location.z < 0.5: angle_center -= 5
        if pitch.location.z > 0.9: angle_center += 5
        
        # Gap能力: 二・三塁打が多い(=ラインドライブ傾向)
        if gap > 60 and quality != "soft":
            # ライナー性の角度 (10-20度) に収束しやすくなる
            if random.random() < (gap/150):
                angle_center = 15
        
        if strategy == "BUNT":
            angle = -20
            velo = 30 + random.uniform(-5, 5)
            # 犠打/セーフティの技術
            bunt_skill = get_effective_stat(batter, 'bunt_sac')
            if strategy == "SAFETY_BUNT": # もしあれば
                 bunt_skill = get_effective_stat(batter, 'bunt_hit')
            
            # 下手だとフライになったり強すぎたり
            if random.uniform(0, 100) > bunt_skill:
                if random.random() < 0.5: angle = 30 # フライ
                else: velo += 20 # 強すぎ
            
            quality = "soft"
        else:
            angle = random.gauss(angle_center, 12) # 角度のばらつき
        
        # 速度に乱数
        velo = max(40, base_v + random.gauss(0, 5))
        if quality == "hard": velo = max(velo, 130) # Hardなら最低でもある程度速い
        
        # 打球タイプ判定
        if angle < 7: htype = BattedBallType.GROUNDBALL
        elif angle < 20: htype = BattedBallType.LINEDRIVE
        elif angle < 50: htype = BattedBallType.FLYBALL
        else: htype = BattedBallType.POPUP
        
        # 飛距離概算 (空気抵抗簡易無視モデル + 補正)
        v_ms = velo / 3.6
        # 真空での飛距離
        dist = (v_ms**2 * math.sin(math.radians(2 * angle))) / 9.8
        
        # 簡易空気抵抗 & スピン補正
        # フライ・ライナーは伸びる(バックスピン)、ゴロは落ちる
        if htype == BattedBallType.GROUNDBALL:
            dist *= 0.5 # 地面摩擦で止まる
        elif htype == BattedBallType.POPUP:
            dist *= 0.3 # 滞空時間の割に飛ばない
        else:
            dist *= 0.8 # 空気抵抗
            # Powerがあると押し込みで飛ぶ
            dist *= (1.0 + (power-50)*0.002)
            
        dist = max(0, dist)
        
        # スプレーアングル (引っ張り/流し)
        # Powerヒッターは引っ張り傾向、Contactヒッターは広角傾向などあり得るが
        # ここではシンプルにタイミング(random)で
        spray = random.gauss(0, 25) # -90(左) ~ 90(右)
        
        # 座標計算
        rad = math.radians(spray)
        land_x = dist * math.sin(rad)
        land_y = dist * math.cos(rad)
        
        # 軌道生成
        traj = []
        steps = 10
        for i in range(steps+1):
            t = i/steps
            d = dist * t
            # 放物線
            h = max(0, d * math.tan(math.radians(angle)) - (9.8 * d**2) / (2 * (v_ms * math.cos(math.radians(angle)))**2))
            
            lx = d * math.sin(rad)
            ly = d * math.cos(rad)
            traj.append((lx, ly, h))
            
        return BattedBallData(velo, angle, spray, htype, dist, 4.0, land_x, land_y, traj, quality)

class DefenseEngine:
    """
    守備判定エンジン
    野手の守備力(Range, Error, Arm)を使用して結果を判定
    """
    def judge(self, ball: BattedBallData, defense_team: Team):
        # ホームラン判定
        # フェンス距離計算 (簡易的に扇形球場とする: 両翼100m, 中堅122m)
        # 角度spray: 0がセンター, -45がレフト, 45がライト
        abs_spray = abs(ball.spray_angle)
        fence_dist = 122 - (abs_spray / 45.0) * (122 - 100) # 簡易補間
        
        if ball.hit_type == BattedBallType.FLYBALL and ball.distance > fence_dist and abs_spray < 45:
             # フェアゾーンかつフェンス越え
            return PlayResult.HOME_RUN
        
        # ファウル判定
        if abs_spray > 45:
            # ファウルフライを捕れるかどうか
            # ここでは簡易的にファウルはすべてファウルとする(捕球実装は複雑になるため)
            return PlayResult.FOUL # 呼び出し元でカウント処理
            
        # 担当野手の決定
        fielder, position_name = self._get_responsible_fielder(ball, defense_team)
        
        # 守備パラメータ取得
        if fielder:
            # 守備範囲
            defense_range = getattr(fielder.stats, 'defense_ranges', {}).get(position_name, 1)
            # 調子補正
            defense_range = defense_range * (1.0 + (fielder.condition - 5) * 0.02)
            
            # エラー率 (Error能力が高いほどエラーしにくい)
            error_rating = get_effective_stat(fielder, 'error')
        else:
            defense_range = 1
            error_rating = 1
            
        # 捕球確率計算 (Range vs Ball Distance/Speed)
        # 定位置からの距離を計算すべきだが、ここでは「ヒット確率」に対するマイナス補正として扱う
        
        # 基本ヒット確率
        hit_prob = 0.0
        
        if ball.hit_type == BattedBallType.GROUNDBALL:
            hit_prob = 0.45
            # ゴロは内野守備範囲で防ぐ
            if ball.distance < 45: # 内野
                 hit_prob -= (defense_range - 50) * 0.01
            else: # 内野を抜けた
                 hit_prob = 0.8 # ほぼヒット、外野が前進ならアウトあり？
                 
        elif ball.hit_type == BattedBallType.LINEDRIVE:
            hit_prob = 0.75
            # ライナーは守備範囲の影響小（反応速度）、正面ならアウト
            hit_prob -= (defense_range - 50) * 0.005
            
        elif ball.hit_type == BattedBallType.FLYBALL:
            hit_prob = 0.2 # フライは基本アウト
            # 守備範囲が広いとポテンヒットを防ぐ
            # 逆にDeepなフライは追いつけるか
            hit_prob -= (defense_range - 50) * 0.005
            
        elif ball.hit_type == BattedBallType.POPUP:
            hit_prob = 0.01 # ほぼアウト
        
        # 打球品質補正
        if ball.contact_quality == "hard": hit_prob += 0.3
        if ball.contact_quality == "soft": hit_prob -= 0.1
        
        # 最終判定
        is_hit = random.random() < hit_prob
        
        if is_hit:
            # ヒットの種類
            if ball.distance > 100 or (ball.distance > 80 and ball.hit_type == BattedBallType.LINEDRIVE):
                # 3塁打判定: 走力と外野手の肩/守備
                if random.random() < 0.1: return PlayResult.TRIPLE
                return PlayResult.DOUBLE
            return PlayResult.SINGLE
        else:
            # エラー判定
            # Error値 50 -> 1%エラー, 90 -> 0.1%, 10 -> 3%
            error_prob = max(0.001, 0.02 - (error_rating * 0.0002))
            if random.random() < error_prob:
                return PlayResult.ERROR
            
            # アウトの種類
            if ball.hit_type == BattedBallType.GROUNDBALL: return PlayResult.GROUNDOUT
            if ball.hit_type == BattedBallType.LINEDRIVE: return PlayResult.LINEOUT
            if ball.hit_type == BattedBallType.POPUP: return PlayResult.POPUP_OUT
            return PlayResult.FLYOUT

    def _get_responsible_fielder(self, ball: BattedBallData, team: Team) -> Tuple[Optional[Player], str]:
        # 座標と角度から担当ポジションを推定
        # ポジション定数: '捕手', '一塁手', '二塁手', '三塁手', '遊撃手', '外野手'
        angle = ball.spray_angle
        dist = ball.distance
        
        pos_enum = Position
        
        # 内野 (距離45m未満 または ゴロ)
        if dist < 45 or ball.hit_type == BattedBallType.GROUNDBALL:
            if angle < -20: return self._get_player_by_pos(team, pos_enum.THIRD), pos_enum.THIRD.value
            elif angle < -5: return self._get_player_by_pos(team, pos_enum.SHORTSTOP), pos_enum.SHORTSTOP.value
            elif angle < 15: return self._get_player_by_pos(team, pos_enum.SECOND), pos_enum.SECOND.value
            else: return self._get_player_by_pos(team, pos_enum.FIRST), pos_enum.FIRST.value
        
        # 外野
        else:
            # 外野手は全員 '外野手' ポジションだが、配列内の誰か特定が必要
            # ここでは簡易的に、現在の守備ラインナップから外野手属性を持つ人を抽出して割り当てる
            outfielders = [p for i, p in enumerate(team.players) if i in team.current_lineup and p.position == pos_enum.OUTFIELD]
            
            # 3人いると仮定 (LF, CF, RF)
            # いなければ適当に返す
            if not outfielders: return None, "外野手"
            
            # 角度で分割 (Left: <-15, Center: -15~15, Right: >15)
            # Lineupの順序や守備適正詳細がないため、リストのインデックスで簡易割り当て
            # 実際には「レフトを守っている選手」の情報が必要だが、モデルにはPosition.OUTFIELDしかない
            # ランダムまたはリスト順で返す
            idx = 0
            if angle < -15: idx = 0 # LF
            elif angle > 15: idx = min(2, len(outfielders)-1) # RF
            else: idx = min(1, len(outfielders)-1) # CF
            
            return outfielders[idx], pos_enum.OUTFIELD.value

    def _get_player_by_pos(self, team: Team, pos: Position) -> Optional[Player]:
        for idx in team.current_lineup:
            if 0 <= idx < len(team.players):
                p = team.players[idx]
                # メインポジションが一致、あるいは守備位置割り当てロジックが必要
                # ここでは簡易的にメインポジションで判定
                if p.position == pos:
                    return p
        return None

# ========================================
# 統合エンジン
# ========================================

class LiveGameEngine:
    def __init__(self, home: Team, away: Team):
        self.home_team = home
        self.away_team = away
        self.state = GameState()
        self.pitch_gen = PitchGenerator()
        self.bat_gen = BattedBallGenerator()
        self.def_eng = DefenseEngine()
        self.ai = AIManager()
        
        self._init_starters()

    def _init_starters(self):
        # 先発投手を取得
        hp = self.home_team.get_today_starter()
        ap = self.away_team.get_today_starter()
        
        # いなければローテ1番手
        if not hp: hp = self.home_team.players[self.home_team.rotation[0]] if self.home_team.rotation else self.home_team.players[0]
        if not ap: ap = self.away_team.players[self.away_team.rotation[0]] if self.away_team.rotation else self.away_team.players[0]

        # インデックス検索
        self.state.home_pitcher_idx = self.home_team.players.index(hp)
        self.state.away_pitcher_idx = self.away_team.players.index(ap)

    def get_current_batter(self) -> Tuple[Player, int]:
        team = self.away_team if self.state.is_top else self.home_team
        order_idx = self.state.away_batter_order if self.state.is_top else self.state.home_batter_order
        # current_lineupは打順リスト(player_indexが入っている)
        if not team.current_lineup: return team.players[0], 0
        p_idx = team.current_lineup[order_idx % len(team.current_lineup)]
        return team.players[p_idx], order_idx

    def get_current_pitcher(self) -> Tuple[Player, int]:
        team = self.home_team if self.state.is_top else self.away_team
        idx = self.state.home_pitcher_idx if self.state.is_top else self.state.away_pitcher_idx
        return team.players[idx], idx

    def get_current_catcher(self) -> Optional[Player]:
        # 守備側の捕手を取得
        team = self.home_team if self.state.is_top else self.away_team
        # ラインナップから捕手を探す
        for p_idx in team.current_lineup:
            if team.players[p_idx].position == Position.CATCHER:
                return team.players[p_idx]
        return None

    def simulate_pitch(self, manual_strategy=None):
        batter, _ = self.get_current_batter()
        pitcher, _ = self.get_current_pitcher()
        catcher = self.get_current_catcher()
        
        defense_team = self.home_team if self.state.is_top else self.away_team
        offense_team = self.away_team if self.state.is_top else self.home_team
        
        # 作戦決定
        # 攻撃側
        if manual_strategy:
            strategy = manual_strategy
        else:
            strategy = self.ai.decide_strategy(self.state, offense_team, defense_team, batter)
            
        # 守備側
        pitch_strategy = self.ai.decide_pitch_strategy(self.state, pitcher, batter)
        
        # --------------------
        # プレイ処理
        # --------------------
        
        # 1. 盗塁判定 (投球前)
        if strategy == "STEAL":
            res = self._attempt_steal(catcher)
            if res: return res # 盗塁終了ならリターン
            # 盗塁しない/できない場合はスイングへ移行（あるいは失敗後の打席継続はないがコード上はこうなる）

        # 2. 投球生成
        pitch = self.pitch_gen.generate_pitch(pitcher, batter, catcher, self.state, pitch_strategy)
        
        # 3. バント処理
        if strategy == "BUNT":
            # バントは必ずインプレー（またはファウル/空振り）
            # バント成功率: bunt_sac能力
            bunt_skill = get_effective_stat(batter, 'bunt_sac')
            # 難しい球（ボール球や速球）は失敗しやすい
            difficulty = 0
            if not pitch.location.is_strike: difficulty += 20
            if pitch.velocity > 150: difficulty += 10
            
            if random.uniform(0, 100) > (bunt_skill - difficulty):
                # 失敗 -> ファウル or 空振り
                if random.random() < 0.8: return PitchResult.FOUL, pitch, None
                else: return PitchResult.STRIKE_SWINGING, pitch, None
            
            ball = self.bat_gen.generate(batter, pitcher, pitch, self.state, strategy)
            return PitchResult.IN_PLAY, pitch, ball

        # 4. スイング判定 (選球眼 Eye)
        eye = get_effective_stat(batter, 'eye')
        
        # ストライクなら振る確率高い
        if pitch.location.is_strike:
            swing_prob = 0.75 + (eye - 50) * 0.002 # 選球眼が良いと甘い球を振る? (逆かも: 際どい球を見極める)
            # 積極性(Aggressiveness)データがないのでEyeで代用
            # ストライクは振るのが正解
        else:
            # ボール球を振る確率 (選球眼が良いと振らない)
            swing_prob = 0.40 - (eye - 50) * 0.01
            
        # カウント別補正
        if self.state.strikes == 2: swing_prob += 0.3 # 追い込まれたら振る
        if self.state.balls == 3: swing_prob -= 0.3 # 3ボールなら待つ
        if strategy == "WAIT": swing_prob = 0.05
        
        is_swing = random.random() < swing_prob
        
        # 見逃し
        if not is_swing:
            res = PitchResult.STRIKE_CALLED if pitch.location.is_strike else PitchResult.BALL
            return res, pitch, None
            
        # 5. コンタクト判定 (空振り/ファウル/インプレー)
        # Contact能力 vs Pitch Control/Movement/Velocity
        contact = get_effective_stat(batter, 'contact', opponent=pitcher)
        avoid_k = get_effective_stat(batter, 'avoid_k')
        
        # 球威(Stuff)が高いと空振りしやすい
        p_stuff = get_effective_stat(pitcher, 'stuff', opponent=batter)
        
        # ヒット確率 (バットに当たる確率)
        # 基準: 80%程度
        hit_prob = 0.80 + (contact - 50)*0.005 - (p_stuff - 50)*0.005
        if not pitch.location.is_strike: hit_prob -= 0.2
        
        # 三振回避能力で補正
        hit_prob += (avoid_k - 50) * 0.003
        
        if random.random() > hit_prob:
            return PitchResult.STRIKE_SWINGING, pitch, None
            
        # 当たった -> ファウル or フェア
        # 振り遅れなどを考慮 (Velocity vs Power/SwingSpeed)
        
        # ファウル確率
        foul_prob = 0.35
        if self.state.strikes == 2: foul_prob += 0.1 # 粘る
        
        # ミート打ちならファウルで逃げやすい
        if strategy == "MEET": foul_prob += 0.1
        
        if random.random() < foul_prob:
             return PitchResult.FOUL, pitch, None
             
        # インプレー生成
        ball = self.bat_gen.generate(batter, pitcher, pitch, self.state, strategy)
        return PitchResult.IN_PLAY, pitch, ball

    def _attempt_steal(self, catcher: Player):
        runner = self.state.runner_1b
        if not runner: return None
        
        # 走力 vs 肩力 + クイック
        runner_spd = get_effective_stat(runner, 'speed')
        runner_stl = get_effective_stat(runner, 'steal')
        
        catcher_arm = get_effective_stat(catcher, 'arm') if catcher else 50
        pitcher, _ = self.get_current_pitcher()
        p_quick = get_effective_stat(pitcher, 'hold_runners') # クイック
        
        # 成功率計算
        # 基準 70%
        success_prob = 0.70 + (runner_spd + runner_stl - 100)*0.01 - (catcher_arm + p_quick - 100)*0.01
        
        if random.random() < success_prob:
            # 成功
            self.state.runner_2b = self.state.runner_1b
            self.state.runner_1b = None
            # 投球データはダミーを返すか、ボール扱いにする
            # ここでは「ボール」として処理しつつ、盗塁結果を返す設計が必要だが、
            # 簡易的にPitchResultではなく特別リターンが必要かも。
            # 一旦ボール扱いで返す
            return PitchResult.BALL, None, None # 実際にはここに盗塁フラグが必要
        else:
            # 失敗 (盗塁死)
            self.state.runner_1b = None
            self.state.outs += 1
            return PitchResult.STRIKE_SWINGING, None, None # 便宜上

    def process_pitch_result(self, res, pitch, ball):
        if res == PitchResult.BALL:
            self.state.balls += 1
            if self.state.balls >= 4: return self._walk()
        elif res in [PitchResult.STRIKE_CALLED, PitchResult.STRIKE_SWINGING]:
            self.state.strikes += 1
            if self.state.strikes >= 3: return self._out(PlayResult.STRIKEOUT)
        elif res == PitchResult.FOUL:
            if self.state.strikes < 2: self.state.strikes += 1
        elif res == PitchResult.IN_PLAY:
            defense_team = self.home_team if self.state.is_top else self.away_team
            play = self.def_eng.judge(ball, defense_team)
            
            # ファウルの場合
            if play == PlayResult.FOUL:
                if self.state.strikes < 2: self.state.strikes += 1
                return None
                
            return self._resolve_play(play)
        return None

    def _walk(self):
        batter, _ = self.get_current_batter()
        self._advance_runners(1, batter, is_walk=True)
        self._reset_count()
        self._next_batter()
        return PlayResult.WALK

    def _out(self, kind=PlayResult.STRIKEOUT):
        self.state.outs += 1
        self._reset_count()
        self._next_batter()
        if self.state.outs >= 3: self._change_inning()
        return kind

    def _resolve_play(self, play):
        batter, _ = self.get_current_batter()
        
        self._reset_count()
        self._next_batter()
        
        if play == PlayResult.HOME_RUN:
            self._score(1 + (1 if self.state.runner_1b else 0) + (1 if self.state.runner_2b else 0) + (1 if self.state.runner_3b else 0))
            self.state.runner_1b = self.state.runner_2b = self.state.runner_3b = None
        elif play in [PlayResult.SINGLE, PlayResult.INFIELD_HIT]:
            self._advance_runners(1, batter)
        elif play == PlayResult.DOUBLE:
            self._advance_runners(2, batter)
        elif play == PlayResult.TRIPLE:
            self._advance_runners(3, batter)
        elif play == PlayResult.ERROR:
             # エラーは1塁打扱い＋αだが簡易的に1塁打
             self._advance_runners(1, batter)
        else: # OUT
            # 併殺打判定
            if play == PlayResult.GROUNDOUT and self.state.runner_1b and self.state.outs < 2:
                # 併殺崩し vs 守備側の併殺能力
                # ここでは簡易的に確率で
                if random.random() < 0.6:
                    self.state.outs += 2
                    self.state.runner_1b = None # 1塁走者アウト
                    play = PlayResult.DOUBLE_PLAY
                else:
                    self.state.outs += 1
                    # 走者進塁処理が必要だが、ゴロアウトは進塁打になることも。
                    # 簡易化のため、走者そのままアウト増のみ
            else:
                self.state.outs += 1
                
            if self.state.outs >= 3: self._change_inning()
            
        return play

    def _advance_runners(self, bases, batter=None, is_walk=False):
        score = 0
        
        if is_walk:
            # 押し出し判定
            if self.state.runner_1b:
                if self.state.runner_2b:
                    if self.state.runner_3b:
                        score += 1 # 押し出し
                    self.state.runner_3b = self.state.runner_3b if self.state.runner_3b else self.state.runner_2b
                self.state.runner_2b = self.state.runner_2b if self.state.runner_2b else self.state.runner_1b
            self.state.runner_1b = batter
            
        else:
            # ヒットによる進塁 (走力を見て追加進塁判定をすべきだが簡易版)
            # base running capability check
            
            if bases == 1:
                if self.state.runner_3b: score += 1; self.state.runner_3b = None
                if self.state.runner_2b:
                    # 2塁走者が生還できるか (Speed > 70 なら確率高)
                    runner_spd = get_effective_stat(self.state.runner_2b, 'speed') if self.state.runner_2b else 50
                    if runner_spd > 60 and random.random() < 0.6:
                        score += 1; self.state.runner_2b = None
                    else:
                        self.state.runner_3b = self.state.runner_2b; self.state.runner_2b = None
                        
                if self.state.runner_1b: self.state.runner_2b = self.state.runner_1b
                self.state.runner_1b = batter
                
            elif bases == 2:
                if self.state.runner_3b: score += 1; self.state.runner_3b = None
                if self.state.runner_2b: score += 1; self.state.runner_2b = None
                if self.state.runner_1b:
                    # 1塁走者が生還できるか
                    runner_spd = get_effective_stat(self.state.runner_1b, 'speed') if self.state.runner_1b else 50
                    if runner_spd > 75 and random.random() < 0.4:
                        score += 1; self.state.runner_1b = None
                    else:
                        self.state.runner_3b = self.state.runner_1b; self.state.runner_1b = None
                self.state.runner_2b = batter
                
            elif bases == 3:
                if self.state.runner_3b: score += 1
                if self.state.runner_2b: score += 1
                if self.state.runner_1b: score += 1
                self.state.runner_1b = self.state.runner_2b = None
                self.state.runner_3b = batter
        
        self._score(score)

    def _score(self, pts):
        if pts == 0: return
        if self.state.is_top: self.state.away_score += pts
        else: self.state.home_score += pts

    def _reset_count(self):
        self.state.balls = 0
        self.state.strikes = 0

    def _next_batter(self):
        if self.state.is_top: self.state.away_batter_order = (self.state.away_batter_order + 1) % len(self.away_team.current_lineup)
        else: self.state.home_batter_order = (self.state.home_batter_order + 1) % len(self.home_team.current_lineup)

    def _change_inning(self):
        self.state.outs = 0
        self.state.runner_1b = None
        self.state.runner_2b = None
        self.state.runner_3b = None
        if not self.state.is_top: self.state.inning += 1
        self.state.is_top = not self.state.is_top
        
        # 投手交代判定（簡易: スタミナ切れなら交代...はManagerの仕事だが、ここではフラグだけ見る等）
        # (実装省略)

    def is_game_over(self):
        if self.state.inning > 9:
             if self.state.is_top: return False # 10回表開始直後など
             if self.state.home_score != self.state.away_score: return True # 裏終了で決着
             if self.state.inning >= 12 and self.state.outs >= 3: return True # 引き分け
        
        # サヨナラ勝ち
        if self.state.inning >= 9 and not self.state.is_top and self.state.home_score > self.state.away_score:
            return True
            
        return False

    def get_winner(self):
        if self.state.home_score > self.state.away_score: return self.home_team.name
        if self.state.away_score > self.state.home_score: return self.away_team.name
        return "DRAW"