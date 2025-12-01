# -*- coding: utf-8 -*-
"""
物理演算ベースの野球シミュレーションエンジン

打球の軌道、投球の変化、守備の動きなどを物理法則に基づいて計算
"""
import math
import random
from dataclasses import dataclass
from typing import Tuple, Optional, List
from enum import Enum


# ===== 定数 =====
GRAVITY = 9.8  # 重力加速度 (m/s^2)
AIR_DENSITY = 1.225  # 空気密度 (kg/m^3)
BALL_MASS = 0.145  # ボール質量 (kg)
BALL_RADIUS = 0.0365  # ボール半径 (m)
BALL_AREA = math.pi * BALL_RADIUS ** 2  # ボール断面積
DRAG_COEFFICIENT = 0.3  # 抗力係数
MAGNUS_COEFFICIENT = 0.25  # マグナス係数

# フィールド寸法 (m)
MOUND_DISTANCE = 18.44  # マウンドからホームベースまでの距離
OUTFIELD_FENCE_CENTER = 122  # センターフェンスまでの距離
OUTFIELD_FENCE_CORNER = 100  # コーナーフェンスまでの距離
FENCE_HEIGHT = 3.0  # フェンスの高さ


class HitResult(Enum):
    """打球結果"""
    HOME_RUN = "ホームラン"
    TRIPLE = "三塁打"
    DOUBLE = "二塁打"
    SINGLE = "単打"
    INFIELD_HIT = "内野安打"
    FLYOUT = "フライアウト"
    GROUNDOUT = "ゴロアウト"
    LINEOUT = "ライナーアウト"
    STRIKEOUT = "三振"
    WALK = "四球"
    HIT_BY_PITCH = "死球"
    FOUL = "ファウル"
    ERROR = "エラー"


class PitchType(Enum):
    """球種"""
    FASTBALL = "ストレート"
    SLIDER = "スライダー"
    CURVE = "カーブ"
    CHANGEUP = "チェンジアップ"
    FORK = "フォーク"
    SINKER = "シンカー"
    CUTTER = "カットボール"
    SPLITTER = "スプリット"
    SCREWBALL = "シュート"


@dataclass
class Vector3D:
    """3次元ベクトル"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self) -> 'Vector3D':
        mag = self.magnitude()
        if mag == 0:
            return Vector3D()
        return Vector3D(self.x/mag, self.y/mag, self.z/mag)
    
    def __add__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)


@dataclass
class BallTrajectory:
    """ボールの軌道データ"""
    position: Vector3D
    velocity: Vector3D
    spin: Vector3D  # 回転軸と回転数 (rpm)
    time: float = 0.0


@dataclass
class PitchData:
    """投球データ"""
    pitch_type: str
    velocity: float  # km/h
    spin_rate: int  # rpm
    horizontal_break: float  # 横変化量 (cm)
    vertical_break: float  # 縦変化量 (cm)
    release_point: Vector3D
    target_zone: Tuple[float, float]  # ストライクゾーン内の位置 (-1〜1)


@dataclass
class BattedBallData:
    """打球データ"""
    exit_velocity: float  # 打球速度 (km/h)
    launch_angle: float  # 打球角度 (度)
    spray_angle: float  # 打球方向 (度、0=センター)
    spin_rate: int  # 回転数 (rpm)
    spin_axis: float  # 回転軸 (度)
    contact_quality: float  # 芯を捉えた度合い (0-1)


class PhysicsEngine:
    """物理演算エンジン"""
    
    def __init__(self):
        self.dt = 0.001  # 計算時間刻み (秒)
        self.wind_velocity = Vector3D()  # 風速
        self.temperature = 20  # 気温 (℃)
        self.humidity = 50  # 湿度 (%)
        self.altitude = 0  # 標高 (m)
    
    def set_weather(self, wind_x: float = 0, wind_y: float = 0, temp: float = 20, 
                    humidity: float = 50, altitude: float = 0):
        """気象条件を設定"""
        self.wind_velocity = Vector3D(wind_x, wind_y, 0)
        self.temperature = temp
        self.humidity = humidity
        self.altitude = altitude
    
    def get_air_density(self) -> float:
        """現在の気象条件での空気密度を計算"""
        # 気温による補正
        temp_factor = 273.15 / (273.15 + self.temperature)
        # 標高による補正
        altitude_factor = math.exp(-self.altitude / 8500)
        # 湿度による補正（簡略化）
        humidity_factor = 1 - 0.0012 * (self.humidity - 50) / 50
        
        return AIR_DENSITY * temp_factor * altitude_factor * humidity_factor
    
    def calculate_pitch_trajectory(self, pitch: PitchData) -> List[BallTrajectory]:
        """投球の軌道を計算"""
        trajectory = []
        
        # 初速度をベクトルに変換 (km/h -> m/s)
        initial_speed = pitch.velocity / 3.6
        
        # リリースポイントからホームベース方向
        position = Vector3D(
            pitch.release_point.x,
            pitch.release_point.y,
            pitch.release_point.z
        )
        
        # 投球方向（ホームベース方向）
        velocity = Vector3D(
            0,
            -initial_speed,  # ホームベース方向
            -initial_speed * 0.05  # わずかな下向き成分
        )
        
        # 回転による変化量を設定
        spin = Vector3D(
            pitch.horizontal_break * 10,  # 横回転
            0,
            pitch.vertical_break * 10  # 縦回転
        )
        
        t = 0
        air_density = self.get_air_density()
        
        while position.y > 0 and t < 1.0:  # ホームベースに到達するまで
            # 空気抵抗
            speed = velocity.magnitude()
            drag = air_density * BALL_AREA * DRAG_COEFFICIENT * speed**2 / (2 * BALL_MASS)
            drag_vec = velocity.normalize() * (-drag)
            
            # マグナス力（回転による変化）
            magnus_force = Vector3D(
                spin.x * MAGNUS_COEFFICIENT * speed / 1000,
                0,
                spin.z * MAGNUS_COEFFICIENT * speed / 1000
            )
            
            # 重力
            gravity_vec = Vector3D(0, 0, -GRAVITY)
            
            # 風の影響
            wind_effect = (self.wind_velocity - velocity) * 0.001
            
            # 加速度を計算
            acceleration = drag_vec + magnus_force + gravity_vec + wind_effect
            
            # 速度と位置を更新
            velocity = velocity + acceleration * self.dt
            position = position + velocity * self.dt
            t += self.dt
            
            if t % 0.05 < self.dt:  # 50msごとに記録
                trajectory.append(BallTrajectory(
                    position=Vector3D(position.x, position.y, position.z),
                    velocity=Vector3D(velocity.x, velocity.y, velocity.z),
                    spin=spin,
                    time=t
                ))
        
        return trajectory
    
    def calculate_batted_ball(self, ball_data: BattedBallData) -> Tuple[HitResult, float, float]:
        """打球の結果を計算
        
        Returns:
            (結果, 飛距離, 滞空時間)
        """
        # 初速度 (km/h -> m/s)
        v0 = ball_data.exit_velocity / 3.6
        
        # 角度をラジアンに
        launch_rad = math.radians(ball_data.launch_angle)
        spray_rad = math.radians(ball_data.spray_angle)
        
        # 初速度ベクトル
        vx = v0 * math.cos(launch_rad) * math.sin(spray_rad)  # 左右方向
        vy = v0 * math.cos(launch_rad) * math.cos(spray_rad)  # 前方向
        vz = v0 * math.sin(launch_rad)  # 上方向
        
        velocity = Vector3D(vx, vy, vz)
        position = Vector3D(0, 0, 1)  # バットの高さから
        
        # 回転の影響
        spin_factor = ball_data.spin_rate / 2000  # 正規化
        
        t = 0
        max_height = 0
        air_density = self.get_air_density()
        
        trajectory = []
        
        while position.z >= 0 and t < 15:
            # 空気抵抗
            speed = velocity.magnitude()
            drag = air_density * BALL_AREA * DRAG_COEFFICIENT * speed**2 / (2 * BALL_MASS)
            drag_vec = velocity.normalize() * (-drag)
            
            # バックスピンによる揚力
            lift = spin_factor * speed * 0.001 * ball_data.contact_quality
            lift_vec = Vector3D(0, 0, lift)
            
            # 重力
            gravity_vec = Vector3D(0, 0, -GRAVITY)
            
            # 風の影響
            wind_effect = self.wind_velocity * 0.01
            
            # 加速度
            acceleration = drag_vec + lift_vec + gravity_vec
            
            # 更新
            velocity = velocity + acceleration * self.dt
            position = position + velocity * self.dt
            position = position + wind_effect * self.dt
            
            max_height = max(max_height, position.z)
            t += self.dt
            
            trajectory.append(position)
        
        # 飛距離を計算
        distance = math.sqrt(position.x**2 + position.y**2)
        
        # フェンスまでの距離を計算（角度に応じて）
        fence_distance = self._get_fence_distance(ball_data.spray_angle)
        
        # 結果判定
        result = self._determine_hit_result(
            distance, max_height, ball_data.launch_angle, 
            ball_data.exit_velocity, fence_distance
        )
        
        return result, distance, t
    
    def _get_fence_distance(self, spray_angle: float) -> float:
        """打球方向に応じたフェンスまでの距離を取得"""
        # センターが最も遠く、両翼に行くほど近くなる
        angle_factor = abs(spray_angle) / 45  # 0〜1に正規化
        angle_factor = min(1.0, angle_factor)
        
        return OUTFIELD_FENCE_CENTER - (OUTFIELD_FENCE_CENTER - OUTFIELD_FENCE_CORNER) * angle_factor
    
    def _determine_hit_result(self, distance: float, max_height: float, 
                              launch_angle: float, exit_velocity: float,
                              fence_distance: float) -> HitResult:
        """打球の結果を判定"""
        
        # ホームラン判定
        if distance >= fence_distance and max_height > FENCE_HEIGHT:
            return HitResult.HOME_RUN
        
        # 内野の範囲（約30m以内）
        if distance < 30:
            if launch_angle < 10:
                # ゴロ
                if exit_velocity < 80:  # 弱いゴロは内野安打の可能性
                    if random.random() < 0.15:
                        return HitResult.INFIELD_HIT
                return HitResult.GROUNDOUT
            elif launch_angle < 25:
                # 低いライナー
                if random.random() < 0.3:
                    return HitResult.SINGLE
                return HitResult.LINEOUT
            else:
                # 内野フライ
                return HitResult.FLYOUT
        
        # 外野の範囲
        if distance < 60:
            if launch_angle < 15:
                # 外野への速いゴロ→シングル
                return HitResult.SINGLE
            elif launch_angle < 30:
                # ライナー
                if exit_velocity > 140:
                    return HitResult.DOUBLE
                return HitResult.SINGLE
            else:
                # 外野フライ
                if random.random() < 0.7:
                    return HitResult.FLYOUT
                return HitResult.SINGLE
        
        # 深い外野
        if distance < 90:
            if launch_angle > 25:
                if random.random() < 0.4:
                    return HitResult.FLYOUT
                if exit_velocity > 150:
                    return HitResult.TRIPLE
                return HitResult.DOUBLE
            return HitResult.DOUBLE
        
        # フェンス際
        if distance < fence_distance:
            if max_height > FENCE_HEIGHT * 0.8:
                return HitResult.TRIPLE
            return HitResult.DOUBLE
        
        # フェンス直撃
        return HitResult.DOUBLE


class AtBatSimulator:
    """打席シミュレーター"""
    
    def __init__(self, physics: PhysicsEngine = None):
        self.physics = physics or PhysicsEngine()
        
        # 球種リスト
        self.pitch_types = {
            "ストレート": {"base_speed": 145, "h_break": 0, "v_break": 10, "spin": 2200},
            "スライダー": {"base_speed": 130, "h_break": -15, "v_break": 0, "spin": 2400},
            "カーブ": {"base_speed": 115, "h_break": -5, "v_break": -20, "spin": 2600},
            "チェンジアップ": {"base_speed": 125, "h_break": 5, "v_break": -10, "spin": 1600},
            "フォーク": {"base_speed": 135, "h_break": 0, "v_break": -25, "spin": 1200},
            "シンカー": {"base_speed": 140, "h_break": 10, "v_break": -5, "spin": 2000},
            "カットボール": {"base_speed": 140, "h_break": -5, "v_break": 5, "spin": 2300},
            "シュート": {"base_speed": 135, "h_break": 15, "v_break": 0, "spin": 2100},
        }
    
    def generate_pitch(self, pitcher_stats, pitch_name: str = None) -> PitchData:
        """投球を生成"""
        if pitch_name is None or pitch_name not in self.pitch_types:
            pitch_name = "ストレート"
        
        base = self.pitch_types[pitch_name]
        
        # 投手能力による補正
        speed_bonus = (pitcher_stats.speed - 10) * 1.5  # 球速
        control_factor = pitcher_stats.control / 20  # コントロール
        break_bonus = (pitcher_stats.breaking - 10) * 0.5  # 変化量
        
        # ランダム変動を追加
        velocity = base["base_speed"] + speed_bonus + random.gauss(0, 2)
        h_break = base["h_break"] * (1 + break_bonus * 0.1) + random.gauss(0, 2)
        v_break = base["v_break"] * (1 + break_bonus * 0.1) + random.gauss(0, 2)
        
        # コントロールによる制球のばらつき
        target_x = random.gauss(0, 0.5 / control_factor)
        target_z = random.gauss(0, 0.5 / control_factor)
        target_x = max(-1.5, min(1.5, target_x))
        target_z = max(-1.5, min(1.5, target_z))
        
        return PitchData(
            pitch_type=pitch_name,
            velocity=velocity,
            spin_rate=base["spin"] + random.randint(-200, 200),
            horizontal_break=h_break,
            vertical_break=v_break,
            release_point=Vector3D(0, MOUND_DISTANCE, 1.8),
            target_zone=(target_x, target_z)
        )
    
    def simulate_swing(self, batter_stats, pitch: PitchData) -> Optional[BattedBallData]:
        """スイングをシミュレート
        
        Returns:
            打球データ（空振り/見逃しの場合はNone）
        """
        # 打者の能力
        contact = batter_stats.contact
        power = batter_stats.power
        eye = getattr(batter_stats, 'eye', batter_stats.contact)  # 選球眼
        trajectory = getattr(batter_stats, 'trajectory', 2)  # 弾道
        
        # ストライクゾーン判定
        is_strike = abs(pitch.target_zone[0]) < 1.0 and abs(pitch.target_zone[1]) < 1.0
        
        # スイング判定
        # ボール球に手を出す確率（選球眼が低いほど高い）
        ball_swing_chance = 0.4 - eye * 0.02
        # ストライクを見逃す確率（選球眼が低いほど高い）
        strike_looking_chance = 0.15 - eye * 0.008
        
        if is_strike:
            if random.random() < strike_looking_chance:
                return None  # 見逃し
        else:
            if random.random() > ball_swing_chance:
                return None  # ボール見逃し
        
        # スイング実行
        # コンタクト率の計算
        base_contact_rate = 0.7 + contact * 0.015  # 基本コンタクト率
        
        # 球速、変化量によるペナルティ
        speed_penalty = max(0, (pitch.velocity - 140)) * 0.005
        break_penalty = (abs(pitch.horizontal_break) + abs(pitch.vertical_break)) * 0.005
        
        contact_rate = base_contact_rate - speed_penalty - break_penalty
        contact_rate = max(0.3, min(0.95, contact_rate))
        
        if random.random() > contact_rate:
            return None  # 空振り
        
        # コンタクト成功 - 打球データを生成
        # 芯を捉えた度合い
        contact_quality = random.betavariate(2 + contact * 0.2, 3)
        
        # 打球速度 (パワーとコンタクト品質に依存)
        base_exit_velo = 100 + power * 3
        exit_velocity = base_exit_velo * (0.6 + contact_quality * 0.5)
        exit_velocity += random.gauss(0, 5)
        exit_velocity = max(60, min(190, exit_velocity))
        
        # 打球角度 (弾道タイプとコンタクト位置に依存)
        base_angle = {1: 5, 2: 12, 3: 18, 4: 25}.get(trajectory, 15)
        launch_angle = base_angle + random.gauss(0, 12)
        # 芯を外すと角度が極端になりやすい
        if contact_quality < 0.3:
            launch_angle += random.choice([-20, 20])
        launch_angle = max(-15, min(60, launch_angle))
        
        # 打球方向 (ランダム、プルヒッター傾向など)
        spray_angle = random.gauss(0, 25)
        spray_angle = max(-45, min(45, spray_angle))
        
        # 回転数
        spin_rate = 2000 + int(launch_angle * 30) + random.randint(-300, 300)
        
        return BattedBallData(
            exit_velocity=exit_velocity,
            launch_angle=launch_angle,
            spray_angle=spray_angle,
            spin_rate=spin_rate,
            spin_axis=random.uniform(0, 360),
            contact_quality=contact_quality
        )
    
    def simulate_at_bat(self, batter_stats, pitcher_stats, pitch_list: List[str] = None) -> Tuple[HitResult, dict]:
        """1打席をシミュレート
        
        Returns:
            (結果, 詳細データ)
        """
        if pitch_list is None:
            pitch_list = ["ストレート"]
        
        balls = 0
        strikes = 0
        pitch_count = 0
        pitches = []
        
        while True:
            pitch_count += 1
            
            # 球種選択（状況に応じて）
            if strikes == 2:
                # 追い込んだら決め球
                pitch_name = random.choice(pitch_list)
            elif balls >= 2:
                # ボール先行ならストライク取りに
                pitch_name = "ストレート" if random.random() < 0.6 else random.choice(pitch_list)
            else:
                pitch_name = random.choice(pitch_list)
            
            # 投球生成
            pitch = self.generate_pitch(pitcher_stats, pitch_name)
            is_strike = abs(pitch.target_zone[0]) < 1.0 and abs(pitch.target_zone[1]) < 1.0
            
            # スイングシミュレーション
            batted_ball = self.simulate_swing(batter_stats, pitch)
            
            if batted_ball is None:
                # スイングなし または 空振り
                swing = random.random() < (0.5 + batter_stats.contact * 0.02)
                
                if swing:
                    # 空振り
                    strikes += 1
                    pitches.append({"type": pitch_name, "result": "空振り"})
                    if strikes >= 3:
                        return HitResult.STRIKEOUT, {"pitches": pitches, "count": f"{balls}-{strikes}"}
                else:
                    # 見逃し
                    if is_strike:
                        strikes += 1
                        pitches.append({"type": pitch_name, "result": "見逃しストライク"})
                        if strikes >= 3:
                            return HitResult.STRIKEOUT, {"pitches": pitches, "count": f"{balls}-{strikes}"}
                    else:
                        balls += 1
                        pitches.append({"type": pitch_name, "result": "ボール"})
                        if balls >= 4:
                            return HitResult.WALK, {"pitches": pitches, "count": f"{balls}-{strikes}"}
            else:
                # 打球あり
                result, distance, hang_time = self.physics.calculate_batted_ball(batted_ball)
                
                # ファウル判定
                if abs(batted_ball.spray_angle) > 45 or result == HitResult.FOUL:
                    if strikes < 2:
                        strikes += 1
                    pitches.append({"type": pitch_name, "result": "ファウル"})
                    continue
                
                pitches.append({
                    "type": pitch_name, 
                    "result": result.value,
                    "exit_velo": batted_ball.exit_velocity,
                    "launch_angle": batted_ball.launch_angle,
                    "distance": distance
                })
                
                return result, {
                    "pitches": pitches, 
                    "count": f"{balls}-{strikes}",
                    "exit_velocity": batted_ball.exit_velocity,
                    "launch_angle": batted_ball.launch_angle,
                    "distance": distance,
                    "hang_time": hang_time
                }
            
            # 無限ループ防止
            if pitch_count > 20:
                return HitResult.WALK, {"pitches": pitches, "count": f"{balls}-{strikes}"}


# グローバルインスタンス
_physics_engine = None


def get_physics_engine() -> PhysicsEngine:
    """シングルトンの物理エンジンを取得"""
    global _physics_engine
    if _physics_engine is None:
        _physics_engine = PhysicsEngine()
    return _physics_engine


def get_at_bat_simulator() -> AtBatSimulator:
    """打席シミュレーターを取得"""
    return AtBatSimulator(get_physics_engine())
