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


# ===== 物理定数 =====
GRAVITY = 9.80665  # 重力加速度 (m/s^2)
AIR_DENSITY_SEA_LEVEL = 1.225  # 海面での空気密度 (kg/m^3)
BALL_MASS = 0.1417  # NPB公式球質量 (kg) - 141.7g〜148.8g
BALL_RADIUS = 0.0365  # ボール半径 (m) - 72.93mm〜74.84mm
BALL_AREA = math.pi * BALL_RADIUS ** 2  # ボール断面積
BALL_CIRCUMFERENCE = 2 * math.pi * BALL_RADIUS  # ボール周長

# 空力係数 (実測データに基づく)
DRAG_COEFFICIENT_BASE = 0.35  # 基本抗力係数 (回転なし)
MAGNUS_COEFFICIENT = 0.30  # マグナス係数
LIFT_COEFFICIENT = 0.25  # 揚力係数

# フィールド寸法 (m) - NPB標準
MOUND_DISTANCE = 18.44  # マウンドからホームベースまでの距離
BASE_DISTANCE = 27.431  # 塁間距離 (90フィート)
HOME_TO_SECOND = 38.795  # ホームから二塁まで
INFIELD_GRASS_LINE = 29.0  # 内野芝生ラインまでの距離

# 外野フェンス寸法 (NPB各球場の平均値ベース)
OUTFIELD_FENCE_CENTER = 122.0  # センターフェンスまでの距離 (m)
OUTFIELD_FENCE_LEFT_CENTER = 116.0  # 左中間
OUTFIELD_FENCE_RIGHT_CENTER = 116.0  # 右中間  
OUTFIELD_FENCE_LEFT = 100.0  # レフトポール
OUTFIELD_FENCE_RIGHT = 100.0  # ライトポール
FENCE_HEIGHT = 4.2  # フェンスの高さ (m)

# 外野手の標準守備位置 (ホームからの距離, m) - NPBの実際の位置に近い値
OF_POSITION_DEEP = 95.0  # 深めの守備位置（強打者対策）
OF_POSITION_NORMAL = 85.0  # 通常の守備位置
OF_POSITION_SHALLOW = 75.0  # 前進守備位置

# 外野手の守備パラメータ（実測値に基づく）
OF_REACTION_TIME = 0.20  # 反応時間 (秒) - プロは0.2秒程度
OF_FIRST_STEP_TIME = 0.35  # 一歩目までの時間 (秒)
OF_MAX_SPEED_TIME = 1.0  # 最高速度到達までの時間 (秒)
OF_ACCELERATION = 5.0  # 加速度 (m/s^2) - 優秀な選手で5m/s^2程度

# 打球の現実的パラメータ (Statcastデータベース)
MAX_EXIT_VELOCITY = 193.0  # 最高打球速度 (km/h) - 大谷翔平など
AVG_EXIT_VELOCITY = 140.0  # 平均打球速度 (km/h)
MIN_EXIT_VELOCITY = 60.0  # 最低打球速度 (km/h)

# 打球角度の実測値（新しい目標値に基づく）
# 目標: LD%=10%, GB%=45%, FB%=45%(IFFB10%含む)
BARREL_ZONE_MIN_ANGLE = 8  # バレルゾーン最小角度
BARREL_ZONE_MAX_ANGLE = 32  # バレルゾーン最大角度
OPTIMAL_HR_ANGLE = 28  # ホームラン最適角度
GROUNDBALL_MAX_ANGLE = 10  # ゴロと判定される最大角度（10度以下）
LINEDRIVE_MIN_ANGLE = 10  # ライナーの最小角度
LINEDRIVE_MAX_ANGLE = 25  # ライナーの最大角度（10-25度）
FLYBALL_MIN_ANGLE = 25  # フライの最小角度（25度以上）
POPUP_MIN_ANGLE = 50  # ポップアップの最小角度（内野フライ）

# 打球の質の目標値
# Soft%: 23%, Mid%: 42%, Hard%: 35%
SOFT_CONTACT_MAX_VELO = 95  # Soft contact: 95km/h以下
MID_CONTACT_MAX_VELO = 135  # Mid contact: 95-135km/h
# Hard contact: 135km/h以上


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
    spray_angle: float  # 打球方向 (度、0=センター、正=ライト方向)
    spin_rate: int  # 回転数 (rpm)
    spin_axis: float  # 回転軸 (度)
    contact_quality: float  # 芯を捉えた度合い (0-1)
    hit_type: str = "fly"  # "ground", "line", "fly", "popup"


@dataclass
class OutfielderPosition:
    """外野手の位置と能力"""
    x: float  # 左右位置 (m, 正=ライト方向)
    y: float  # 前後位置 (m, ホームからの距離)
    speed: float  # 走力 (1-20)
    fielding: float  # 守備力 (1-20)
    arm: float  # 肩力 (1-20)
    reaction: float  # 反応速度補正 (0.8-1.2)


@dataclass 
class OutfieldCatchResult:
    """外野守備の結果"""
    is_caught: bool  # 捕球成功
    fielder_position: str  # "LF", "CF", "RF"
    catch_difficulty: float  # 捕球難易度 (0-1)
    distance_to_ball: float  # 打球への移動距離 (m)
    hang_time: float  # 滞空時間 (s)
    landing_point: Tuple[float, float]  # 落下地点 (x, y)
    throw_distance: float = 0  # 送球距離
    is_diving_catch: bool = False  # ダイビングキャッチ
    is_wall_catch: bool = False  # フェンス際のキャッチ
    description: str = ""  # 守備の説明


class PhysicsEngine:
    """物理演算エンジン - 超現実的な野球物理シミュレーション"""
    
    def __init__(self):
        self.dt = 0.02  # 計算時間刻み (秒) - 高速化のため調整
        self.wind_velocity = Vector3D()  # 風速
        self.temperature = 25  # 気温 (℃)
        self.humidity = 60  # 湿度 (%)
        self.altitude = 0  # 標高 (m)
        
        # 外野手の標準守備位置 (x=左右, y=ホームからの距離)
        self.outfielder_positions = {
            "LF": OutfielderPosition(x=-25.0, y=OF_POSITION_NORMAL, speed=14, fielding=14, arm=14, reaction=1.0),
            "CF": OutfielderPosition(x=0.0, y=OF_POSITION_NORMAL, speed=15, fielding=15, arm=15, reaction=1.0),
            "RF": OutfielderPosition(x=25.0, y=OF_POSITION_NORMAL, speed=14, fielding=14, arm=14, reaction=1.0)
        }
    
    def set_outfielders(self, lf_stats=None, cf_stats=None, rf_stats=None):
        """外野手の能力を設定"""
        if lf_stats:
            self.outfielder_positions["LF"] = OutfielderPosition(
                x=-25.0, y=OF_POSITION_NORMAL,
                speed=lf_stats.get('run', 14),
                fielding=lf_stats.get('fielding', 14),
                arm=lf_stats.get('arm', 14),
                reaction=1.0 + (lf_stats.get('fielding', 14) - 14) * 0.02
            )
        if cf_stats:
            self.outfielder_positions["CF"] = OutfielderPosition(
                x=0.0, y=OF_POSITION_NORMAL,
                speed=cf_stats.get('run', 15),
                fielding=cf_stats.get('fielding', 15),
                arm=cf_stats.get('arm', 15),
                reaction=1.0 + (cf_stats.get('fielding', 15) - 15) * 0.02
            )
        if rf_stats:
            self.outfielder_positions["RF"] = OutfielderPosition(
                x=25.0, y=OF_POSITION_NORMAL,
                speed=rf_stats.get('run', 14),
                fielding=rf_stats.get('fielding', 14),
                arm=rf_stats.get('arm', 14),
                reaction=1.0 + (rf_stats.get('fielding', 14) - 14) * 0.02
            )
    
    def set_weather(self, wind_x: float = 0, wind_y: float = 0, temp: float = 25, 
                    humidity: float = 60, altitude: float = 0):
        """気象条件を設定"""
        self.wind_velocity = Vector3D(wind_x, wind_y, 0)
        self.temperature = temp
        self.humidity = humidity
        self.altitude = altitude
    
    def get_air_density(self) -> float:
        """現在の気象条件での空気密度を計算（より正確な計算）"""
        # 理想気体の状態方程式に基づく計算
        T = self.temperature + 273.15  # ケルビン
        
        # 飽和水蒸気圧 (Pa) - Magnus式
        es = 610.78 * math.exp((17.27 * self.temperature) / (self.temperature + 237.3))
        # 実際の水蒸気圧
        e = (self.humidity / 100) * es
        
        # 標準気圧 (Pa)
        P0 = 101325
        # 標高による気圧補正
        P = P0 * math.exp(-self.altitude / 8500)
        
        # 乾燥空気の気体定数
        Rd = 287.05
        # 水蒸気の気体定数  
        Rv = 461.5
        
        # 湿潤空気の密度
        rho = (P - e) / (Rd * T) + e / (Rv * T)
        
        return rho
    
    def get_drag_coefficient(self, velocity: float, spin_rate: float) -> float:
        """速度と回転数に応じた抗力係数を計算"""
        # 基本抗力係数
        Cd = DRAG_COEFFICIENT_BASE
        
        # 高速時は抗力係数がやや低下
        speed_mps = velocity / 3.6
        if speed_mps > 40:
            Cd -= (speed_mps - 40) * 0.001
        
        # 高回転時は抗力係数がやや増加（表面の乱流）
        if spin_rate > 2500:
            Cd += (spin_rate - 2500) * 0.00001
        
        return max(0.28, min(0.42, Cd))
    
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
    
    def calculate_batted_ball_trajectory(self, ball_data: BattedBallData) -> Tuple[List[Vector3D], float, float, Tuple[float, float]]:
        """打球の軌道を詳細に計算
        
        Returns:
            (軌道リスト, 飛距離, 滞空時間, 落下地点(x,y))
        """
        # 初速度 (km/h -> m/s)
        v0 = ball_data.exit_velocity / 3.6
        
        # 角度をラジアンに
        launch_rad = math.radians(ball_data.launch_angle)
        spray_rad = math.radians(ball_data.spray_angle)
        
        # 初速度ベクトル
        vx = v0 * math.cos(launch_rad) * math.sin(spray_rad)  # 左右方向 (正=ライト)
        vy = v0 * math.cos(launch_rad) * math.cos(spray_rad)  # 前方向 (センター方向)
        vz = v0 * math.sin(launch_rad)  # 上方向
        
        velocity = Vector3D(vx, vy, vz)
        position = Vector3D(0, 0, 1.0)  # バットの高さから (約1m)
        
        # 回転の影響を計算
        # バックスピン量を打球角度から推定 (高い打球ほどバックスピン)
        if ball_data.launch_angle > 0:
            backspin_factor = min(1.0, ball_data.launch_angle / 30) * ball_data.contact_quality
        else:
            backspin_factor = 0  # ゴロにはバックスピンなし
        
        spin_factor = ball_data.spin_rate / 2500  # 正規化
        
        t = 0
        max_height = 0
        air_density = self.get_air_density()
        
        trajectory = []
        
        # 高速化のため時間ステップを最適化
        dt = 0.02  # 20ms（高速化）
        
        while position.z >= 0 and t < 12:
            speed = velocity.magnitude()
            
            # 動的抗力係数
            Cd = self.get_drag_coefficient(speed * 3.6, ball_data.spin_rate)
            
            # 空気抵抗 (より正確な計算)
            drag_magnitude = 0.5 * air_density * BALL_AREA * Cd * speed**2 / BALL_MASS
            drag_vec = velocity.normalize() * (-drag_magnitude) if speed > 0 else Vector3D()
            
            # マグナス力（バックスピンによる揚力）
            # 実際のマグナス効果: F_M = 0.5 * rho * A * C_L * v^2
            # C_Lはスピンパラメータに依存
            spin_parameter = (ball_data.spin_rate * BALL_CIRCUMFERENCE) / (60 * speed) if speed > 0 else 0
            lift_coefficient = LIFT_COEFFICIENT * spin_parameter * backspin_factor
            lift_magnitude = 0.5 * air_density * BALL_AREA * lift_coefficient * speed**2 / BALL_MASS
            lift_vec = Vector3D(0, 0, lift_magnitude)
            
            # サイドスピンの影響（スライス/フック）
            side_spin = ball_data.spin_rate * math.sin(math.radians(ball_data.spin_axis)) * 0.0001
            side_vec = Vector3D(side_spin, 0, 0)
            
            # 重力
            gravity_vec = Vector3D(0, 0, -GRAVITY)
            
            # 風の影響（打球の速度が遅いほど影響大）
            wind_factor = max(0.1, 1.0 - speed / 50)  # 速い打球は風の影響を受けにくい
            wind_effect = self.wind_velocity * (wind_factor * dt)
            
            # 加速度を合成
            acceleration = drag_vec + lift_vec + side_vec + gravity_vec
            
            # 速度と位置を更新（オイラー法）
            velocity = velocity + acceleration * dt
            position = position + velocity * dt + wind_effect
            
            max_height = max(max_height, position.z)
            t += dt
            
            # 軌道を記録（10msごと）
            if int(t * 1000) % 10 == 0:
                trajectory.append(Vector3D(position.x, position.y, position.z))
        
        # 飛距離を計算
        distance = math.sqrt(position.x**2 + position.y**2)
        landing_point = (position.x, position.y)
        
        return trajectory, distance, t, landing_point
    
    def simulate_outfield_defense(self, ball_data: BattedBallData) -> OutfieldCatchResult:
        """外野守備を超現実的にシミュレート"""
        
        # 打球軌道を計算
        trajectory, distance, hang_time, landing_point = self.calculate_batted_ball_trajectory(ball_data)
        
        # 打球タイプを判定
        hit_type = self._classify_hit_type(ball_data.launch_angle, ball_data.exit_velocity)
        
        # ゴロの場合は外野守備は異なる処理
        if hit_type == "ground":
            return self._simulate_outfield_grounder(ball_data, distance, landing_point)
        
        # フェンス距離を取得
        fence_distance = self._get_fence_distance(ball_data.spray_angle)
        
        # ホームラン判定
        max_height = max(p.z for p in trajectory) if trajectory else 0
        if distance >= fence_distance and max_height > FENCE_HEIGHT:
            return OutfieldCatchResult(
                is_caught=False,
                fielder_position="",
                catch_difficulty=0,
                distance_to_ball=0,
                hang_time=hang_time,
                landing_point=landing_point,
                description="ホームラン！フェンスを越えた！"
            )
        
        # 担当外野手を決定
        responsible_fielder = self._get_responsible_fielder(landing_point)
        fielder = self.outfielder_positions[responsible_fielder]
        
        # 外野手から落下地点までの距離
        fielder_distance = math.sqrt(
            (landing_point[0] - fielder.x)**2 + 
            (landing_point[1] - fielder.y)**2
        )
        
        # 外野手の到達可能時間を計算
        arrival_time = self._calculate_fielder_arrival_time(fielder, fielder_distance)
        
        # 捕球判定
        catch_result = self._determine_catch_result(
            fielder, fielder_distance, hang_time, arrival_time,
            distance, fence_distance, max_height, hit_type, landing_point
        )
        
        catch_result.fielder_position = responsible_fielder
        catch_result.hang_time = hang_time
        catch_result.landing_point = landing_point
        catch_result.distance_to_ball = fielder_distance
        
        # 送球距離を計算（ホームへの送球想定）
        catch_result.throw_distance = math.sqrt(landing_point[0]**2 + landing_point[1]**2)
        
        return catch_result
    
    def _classify_hit_type(self, launch_angle: float, exit_velocity: float) -> str:
        """打球タイプを分類"""
        if launch_angle < GROUNDBALL_MAX_ANGLE:
            return "ground"
        elif launch_angle < LINEDRIVE_MAX_ANGLE:
            if exit_velocity > 150:  # 速いライナー
                return "line_hard"
            return "line"
        elif launch_angle < FLYBALL_MIN_ANGLE + 15:
            return "fly"
        else:
            return "popup"
    
    def _get_responsible_fielder(self, landing_point: Tuple[float, float]) -> str:
        """担当外野手を決定"""
        x, y = landing_point
        
        # 打球方向で判定
        if x < -15:  # レフト方向
            return "LF"
        elif x > 15:  # ライト方向
            return "RF"
        else:  # センター方向
            # センター寄りの打球はCFが追う
            if abs(x) < 10:
                return "CF"
            # ギャップの打球は近い外野手
            lf_dist = math.sqrt((x - self.outfielder_positions["LF"].x)**2 + 
                               (y - self.outfielder_positions["LF"].y)**2)
            cf_dist = math.sqrt((x - self.outfielder_positions["CF"].x)**2 + 
                               (y - self.outfielder_positions["CF"].y)**2)
            rf_dist = math.sqrt((x - self.outfielder_positions["RF"].x)**2 + 
                               (y - self.outfielder_positions["RF"].y)**2)
            
            min_dist = min(lf_dist, cf_dist, rf_dist)
            if min_dist == lf_dist:
                return "LF"
            elif min_dist == rf_dist:
                return "RF"
            return "CF"
    
    def _calculate_fielder_arrival_time(self, fielder: OutfielderPosition, distance: float) -> float:
        """外野手の到達時間を計算（加速度を考慮）"""
        if distance <= 0:
            return 0
        
        # 反応時間（プロは速い）
        reaction_time = OF_REACTION_TIME * fielder.reaction * 0.9
        
        # 最高速度 (走力に基づく) - プロの外野手は速い
        # 走力20 = 約32km/h (8.9m/s)、走力10 = 約27km/h (7.5m/s)
        max_speed = 6.2 + fielder.speed * 0.15  # m/s
        
        # 加速度（守備力で補正）- より高い加速度
        acceleration = OF_ACCELERATION * (1.1 + (fielder.fielding - 14) * 0.04)
        
        # 最高速度に達するまでの時間
        time_to_max_speed = max_speed / acceleration
        
        # 最高速度に達するまでの距離
        distance_to_max_speed = 0.5 * acceleration * time_to_max_speed**2
        
        if distance <= distance_to_max_speed:
            # 最高速度に達する前に到達
            arrival_time = math.sqrt(2 * distance / acceleration)
        else:
            # 最高速度に達した後も移動
            remaining_distance = distance - distance_to_max_speed
            arrival_time = time_to_max_speed + remaining_distance / max_speed
        
        return reaction_time + OF_FIRST_STEP_TIME + arrival_time
    
    def _determine_catch_result(self, fielder: OutfielderPosition, fielder_distance: float,
                                 hang_time: float, arrival_time: float,
                                 distance: float, fence_distance: float,
                                 max_height: float, hit_type: str,
                                 landing_point: Tuple[float, float] = (0, 0)) -> OutfieldCatchResult:
        """捕球結果を判定"""
        
        # 時間的余裕
        time_margin = hang_time - arrival_time
        
        # 捕球難易度を計算 (0-1)
        base_difficulty = 0
        
        # 移動距離による難易度
        if fielder_distance > 20:
            base_difficulty += 0.3
        if fielder_distance > 30:
            base_difficulty += 0.3
        if fielder_distance > 40:
            base_difficulty += 0.3
        
        # ライナーは捕りにくい（滞空時間が短い）
        if hit_type == "line" or hit_type == "line_hard":
            base_difficulty += 0.20
            # 非常に速いライナーはさらに難しい
            if hit_type == "line_hard":
                base_difficulty += 0.15
        
        # フェンス際の打球
        is_near_wall = distance > fence_distance - 5
        if is_near_wall:
            base_difficulty += 0.2
        
        # 背走の打球（外野手の後ろへの打球）
        is_going_back = fielder_distance > 0 and distance > fielder.y
        if is_going_back and fielder_distance > 15:
            base_difficulty += 0.12
        
        # 左右への移動（真横方向）
        lateral_distance = abs(landing_point[0] - fielder.x)
        if lateral_distance > 20:
            base_difficulty += 0.10
        
        # 守備力による補正
        difficulty = base_difficulty * (1 - (fielder.fielding - 12) * 0.025)
        difficulty = max(0, min(1, difficulty))
        
        # 捕球判定 - NPBフライ安打率14%に合わせて捕球率を上げる
        is_caught = False
        is_diving = False
        is_wall_catch = False
        description = ""
        
        if time_margin > 2.0:
            # 非常に余裕がある - ほぼ確実に捕球
            catch_chance = 0.999 - difficulty * 0.005
            is_caught = random.random() < catch_chance
            if is_caught:
                description = "余裕を持って捕球"
        elif time_margin > 1.0:
            # 余裕を持って捕球
            catch_chance = 0.995 - difficulty * 0.02
            is_caught = random.random() < catch_chance
            if is_caught:
                description = "楽に捕球"
        elif time_margin > 0.4:
            # 普通の捕球
            catch_chance = 0.98 - difficulty * 0.06
            is_caught = random.random() < catch_chance
            if is_caught:
                description = "落下点に入って捕球"
        elif time_margin > 0:
            # ぎりぎりの捕球
            catch_chance = 0.90 - difficulty * 0.12 + (fielder.fielding - 14) * 0.015
            is_caught = random.random() < catch_chance
            if is_caught:
                description = "ナイスキャッチ！"
            else:
                description = "あとわずか届かず"
        elif time_margin > -0.4:
            # ダイビングキャッチの可能性
            diving_chance = 0.65 + (fielder.fielding - 14) * 0.025 - difficulty * 0.10
            is_caught = random.random() < max(0.20, diving_chance)
            is_diving = is_caught
            if is_caught:
                description = "ダイビングキャッチ！！"
            else:
                description = "飛び込むも届かず"
        else:
            # 到達不可能
            is_caught = False
            description = "打球に追いつけず"
        
        # フェンス際の特別処理
        if is_near_wall and is_caught:
            wall_catch_chance = 0.55 + (fielder.fielding - 14) * 0.05
            if random.random() < 0.25:  # 25%の確率でフェンス際のプレー
                is_wall_catch = True
                if random.random() < wall_catch_chance:
                    description = "フェンス際でスーパーキャッチ！！"
                else:
                    is_caught = False
                    description = "フェンスに阻まれた"
        
        return OutfieldCatchResult(
            is_caught=is_caught,
            fielder_position="",
            catch_difficulty=difficulty,
            distance_to_ball=fielder_distance,
            hang_time=hang_time,
            landing_point=(0, 0),
            is_diving_catch=is_diving,
            is_wall_catch=is_wall_catch,
            description=description
        )
    
    def _simulate_outfield_grounder(self, ball_data: BattedBallData, 
                                     distance: float, landing_point: Tuple[float, float]) -> OutfieldCatchResult:
        """外野ゴロの処理"""
        # ゴロは必ず処理できるが、ランナーの進塁がある
        responsible_fielder = self._get_responsible_fielder(landing_point)
        fielder = self.outfielder_positions[responsible_fielder]
        
        fielder_distance = math.sqrt(
            (landing_point[0] - fielder.x)**2 + 
            (landing_point[1] - fielder.y)**2
        )
        
        return OutfieldCatchResult(
            is_caught=True,  # ゴロは基本処理可能
            fielder_position=responsible_fielder,
            catch_difficulty=0.1,
            distance_to_ball=fielder_distance,
            hang_time=0,  # ゴロには滞空時間なし
            landing_point=landing_point,
            throw_distance=math.sqrt(landing_point[0]**2 + landing_point[1]**2),
            description="外野ゴロを処理"
        )
    
    def calculate_batted_ball(self, ball_data: BattedBallData) -> Tuple[HitResult, float, float]:
        """打球の結果を計算（後方互換性のため維持）
        
        Returns:
            (結果, 飛距離, 滞空時間)
        """
        # 新しい詳細シミュレーションを使用
        trajectory, distance, hang_time, landing_point = self.calculate_batted_ball_trajectory(ball_data)
        
        # フェンスまでの距離を計算（角度に応じて）
        fence_distance = self._get_fence_distance(ball_data.spray_angle)
        
        # 最高高度を取得
        max_height = max(p.z for p in trajectory) if trajectory else 0
        
        # 外野守備シミュレーション
        defense_result = self.simulate_outfield_defense(ball_data)
        
        # 結果判定
        result = self._determine_hit_result_advanced(
            ball_data, distance, max_height, fence_distance, 
            hang_time, defense_result
        )
        
        return result, distance, hang_time
    
    def _get_fence_distance(self, spray_angle: float) -> float:
        """打球方向に応じたフェンスまでの距離を取得"""
        # センターが最も遠く、両翼に行くほど近くなる
        angle_factor = abs(spray_angle) / 45  # 0〜1に正規化
        angle_factor = min(1.0, angle_factor)
        
        # 左中間・右中間を考慮したより現実的な距離計算
        abs_angle = abs(spray_angle)
        if abs_angle < 15:  # センター方向
            return OUTFIELD_FENCE_CENTER
        elif abs_angle < 30:  # 中間方向
            # 中間は少し短い
            t = (abs_angle - 15) / 15
            return OUTFIELD_FENCE_CENTER - (OUTFIELD_FENCE_CENTER - OUTFIELD_FENCE_LEFT_CENTER) * t
        else:  # ポール方向
            t = (abs_angle - 30) / 15
            return OUTFIELD_FENCE_LEFT_CENTER - (OUTFIELD_FENCE_LEFT_CENTER - OUTFIELD_FENCE_LEFT) * min(1.0, t)
    
    def _determine_hit_result_advanced(self, ball_data: BattedBallData, distance: float, 
                                        max_height: float, fence_distance: float,
                                        hang_time: float, defense_result: OutfieldCatchResult) -> HitResult:
        """打球の結果を外野守備を考慮して判定（NPBデータベース）
        
        NPB実データ目標値:
        - ゴロ安打率: 約23% (内野安打含む)
        - ライナー安打率: 約68%
        - フライ安打率: 約14% (HR除く)
        - 全体BABIP: 約0.290-0.300
        - HR率: 約2.5-3% (打球の約3-5%)
        """
        
        launch_angle = ball_data.launch_angle
        exit_velocity = ball_data.exit_velocity
        hit_type = self._classify_hit_type(launch_angle, exit_velocity)
        
        # ===== ホームラン判定 (NPB: 打球の約3-5%がHR) =====
        # フェンスを十分超える打球のみ
        if distance >= fence_distance + 3 and max_height > FENCE_HEIGHT * 1.2:
            return HitResult.HOME_RUN
        
        # フェンスを超える打球
        if distance >= fence_distance and max_height > FENCE_HEIGHT:
            # ギリギリの場合は確率判定
            margin = distance - fence_distance
            height_margin = max_height - FENCE_HEIGHT
            if margin > 0 and height_margin > 1.0:
                return HitResult.HOME_RUN
            elif random.random() < 0.7:  # 70%の確率でHR
                return HitResult.HOME_RUN
        
        # バレルゾーンの打球でもフェンスを超えないと安打止まり
        # HR判定を厳しくする
        
        # ===== ポップフライ判定 (ほぼ確実にアウト、目標安打率2%以下) =====
        if hit_type == "popup":
            # ポップフライは基本的にアウト - プロはほぼ確実に捕球
            if random.random() < 0.988:  # 98.8%アウト
                return HitResult.FLYOUT
            return HitResult.SINGLE  # 極稀に落球
        
        # ===== 内野の範囲（約40m以内） =====
        if distance < 40:
            if hit_type == "ground":
                # === ゴロの処理 (目標安打率: 23%) ===
                
                # 打球速度による内野安打判定
                # 速い打球は守備の間を抜けやすい
                if exit_velocity > 145:
                    # 非常に強烈なゴロは内野の間を抜ける可能性が高い
                    gap_hit_chance = 0.15 + (exit_velocity - 145) * 0.003
                    if random.random() < gap_hit_chance:
                        return HitResult.SINGLE
                elif exit_velocity > 125:
                    # 中程度のゴロも一定確率で抜ける
                    gap_hit_chance = 0.06 + (exit_velocity - 125) * 0.002
                    if random.random() < gap_hit_chance:
                        return HitResult.SINGLE
                
                # 遅い打球は内野安打の可能性（足が速い場合を想定）
                if exit_velocity < 90:
                    infield_hit_chance = 0.10 + (90 - exit_velocity) * 0.002
                    if random.random() < infield_hit_chance:
                        return HitResult.INFIELD_HIT
                
                # 通常の内野ゴロでも一定確率で安打
                # 打球方向による補正（三遊間・一二塁間は抜けやすい）
                spray_factor = 1.0
                if abs(ball_data.spray_angle) > 28:
                    spray_factor = 1.6  # 三遊間・一二塁間は抜けやすい
                
                # 基本安打率を調整（目標約28%のゴロ安打率でBABIP=0.290）
                base_hit_chance = 0.11 * spray_factor
                if random.random() < base_hit_chance:
                    return HitResult.INFIELD_HIT
                
                return HitResult.GROUNDOUT
                
            elif hit_type == "line" or hit_type == "line_hard":
                # === ライナーの処理 (目標安打率: 68%) ===
                
                if hit_type == "line_hard":
                    # 非常に速いライナー（150km/h以上）
                    hit_chance = 0.88 + (exit_velocity - 150) * 0.002
                elif exit_velocity > 140:
                    hit_chance = 0.80
                elif exit_velocity > 120:
                    hit_chance = 0.70
                else:
                    hit_chance = 0.55
                
                if random.random() < hit_chance:
                    return HitResult.SINGLE
                return HitResult.LINEOUT
                
            elif hit_type == "popup":
                # 内野フライは確実にアウト
                return HitResult.FLYOUT
            else:
                # 通常の内野フライ
                return HitResult.FLYOUT
        
        # ===== 浅い外野の範囲（40-55m） =====
        if distance < 55:
            if hit_type == "ground":
                # 外野まで転がるゴロは基本単打
                if exit_velocity > 135 and random.random() < 0.12:
                    return HitResult.DOUBLE
                return HitResult.SINGLE
            
            elif hit_type == "line" or hit_type == "line_hard":
                # 浅い外野へのライナー - 大半が安打
                if defense_result.is_caught:
                    return HitResult.LINEOUT
                # ライナーで外野に抜ければほぼ安打
                return HitResult.SINGLE
            
            elif hit_type == "popup":
                # ポップフライはほぼ確実にアウト（目標2%以下）
                if random.random() < 0.995:
                    return HitResult.FLYOUT
                return HitResult.SINGLE
            
            else:  # fly
                # 浅いフライは外野手が前進して捕る
                # フライ安打率を下げる（目標14%）
                if defense_result.is_caught:
                    return HitResult.FLYOUT
                # 浅いフライは追加の捕球チャンス（NPB外野手は上手い）
                # 距離40-55mの浅いフライは高確率で捕球
                shallow_catch_chance = 0.85 - (distance - 40) * 0.025
                if random.random() < shallow_catch_chance:
                    return HitResult.FLYOUT
                # 落下した場合は単打
                return HitResult.SINGLE
        
        # ===== 外野の範囲 (55m-フェンス) =====
        # 守備結果を使用
        if defense_result.is_caught:
            if hit_type == "line" or hit_type == "line_hard":
                return HitResult.LINEOUT
            return HitResult.FLYOUT
        
        # ===== 捕球できなかった場合の追加判定（フライ） =====
        # NPB外野手はフライを高確率で捕球（目標フライBABIP=0.220）
        if hit_type == "fly":
            # 距離に基づく追加の捕球チャンス
            # 55-90mの範囲では捕球率を調整
            if distance < 90:
                additional_catch = 0.35 - (distance - 55) * 0.007  # 捕球率を下げてBABIP上昇
                if random.random() < additional_catch:
                    return HitResult.FLYOUT
            elif distance < 100:
                # フェンス手前の深いフライ
                additional_catch = 0.12 - (distance - 90) * 0.008
                if random.random() < additional_catch:
                    return HitResult.FLYOUT
        
        # ===== 捕球できなかった場合の結果判定 =====
        # この時点で外野守備を突破した打球
        
        if hit_type == "ground":
            # 外野への強いゴロ
            if exit_velocity > 140:
                if random.random() < 0.25:
                    return HitResult.DOUBLE
            return HitResult.SINGLE
        
        elif hit_type == "line" or hit_type == "line_hard":
            # ライナー（外野へ抜けた）
            if distance < 70:
                if exit_velocity > 150 and random.random() < 0.2:
                    return HitResult.DOUBLE
                return HitResult.SINGLE
            elif distance < 90:
                # 中間距離のライナー
                if exit_velocity > 150:
                    if random.random() < 0.15:
                        return HitResult.TRIPLE
                    if random.random() < 0.6:
                        return HitResult.DOUBLE
                    return HitResult.SINGLE
                return HitResult.DOUBLE if random.random() < 0.5 else HitResult.SINGLE
            else:
                # 深いライナー
                if random.random() < 0.25:
                    return HitResult.TRIPLE
                return HitResult.DOUBLE
        
        elif hit_type == "fly":
            # フライボール（外野守備を突破したもの）
            # NPB目標: フライ安打率 約14%（HR除く）
            # 守備を突破したフライは長打になりやすい
            if distance < 65:
                return HitResult.SINGLE
            elif distance < 80:
                if random.random() < 0.50:
                    return HitResult.DOUBLE
                return HitResult.SINGLE
            elif distance < 100:
                if random.random() < 0.20:
                    return HitResult.TRIPLE
                return HitResult.DOUBLE
            else:
                # フェンス際
                if random.random() < 0.35:
                    return HitResult.TRIPLE
                return HitResult.DOUBLE
        
        else:  # popup
            # 外野への高い打球（稀に落ちる）
            return HitResult.SINGLE
    
    def _determine_hit_result(self, distance: float, max_height: float, 
                              launch_angle: float, exit_velocity: float,
                              fence_distance: float) -> HitResult:
        """打球の結果を判定（旧バージョン - 互換性のため維持）"""
        
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
        """スイングをシミュレート（超現実的バージョン）
        
        Returns:
            打球データ（空振り/見逃しの場合はNone）
        """
        # 打者の能力
        contact = batter_stats.contact
        power = batter_stats.power
        eye = getattr(batter_stats, 'eye', batter_stats.contact)  # 選球眼
        trajectory = getattr(batter_stats, 'trajectory', 2)  # 弾道
        
        # ストライクゾーン判定（より詳細）
        zone_x = abs(pitch.target_zone[0])
        zone_z = abs(pitch.target_zone[1])
        is_strike = zone_x < 1.0 and zone_z < 1.0
        is_borderline = 0.8 < zone_x < 1.2 or 0.8 < zone_z < 1.2
        is_far_outside = zone_x > 1.5 or zone_z > 1.5
        
        # スイング判定（選球眼に基づく現実的な判定）
        if is_strike:
            # ストライクを見逃す確率
            strike_looking_chance = 0.12 - eye * 0.006
            # コーナー付近は見逃しやすい
            if is_borderline:
                strike_looking_chance += 0.08
            if random.random() < strike_looking_chance:
                return None  # 見逃し
        else:
            # ボール球に手を出す確率
            if is_far_outside:
                ball_swing_chance = 0.08 - eye * 0.004  # 明らかなボールには振らない
            elif is_borderline:
                ball_swing_chance = 0.35 - eye * 0.015  # きわどい球は振りやすい
            else:
                ball_swing_chance = 0.25 - eye * 0.012
            
            if random.random() > ball_swing_chance:
                return None  # ボール見逃し
        
        # スイング実行 - コンタクト率の計算（より詳細）
        base_contact_rate = 0.68 + contact * 0.016
        
        # 球速によるペナルティ（150km/h以上は難しい）
        speed_penalty = 0
        if pitch.velocity > 150:
            speed_penalty = (pitch.velocity - 150) * 0.008
        elif pitch.velocity > 145:
            speed_penalty = (pitch.velocity - 145) * 0.004
        
        # 変化量によるペナルティ（大きな変化は難しい）
        total_break = abs(pitch.horizontal_break) + abs(pitch.vertical_break)
        if total_break > 30:
            break_penalty = (total_break - 30) * 0.006
        else:
            break_penalty = total_break * 0.003
        
        # ボール球はコンタクトしにくい
        if not is_strike:
            zone_penalty = (zone_x - 1.0 + zone_z - 1.0) * 0.08 if zone_x > 1.0 or zone_z > 1.0 else 0
        else:
            zone_penalty = 0
        
        contact_rate = base_contact_rate - speed_penalty - break_penalty - zone_penalty
        contact_rate = max(0.25, min(0.92, contact_rate))
        
        if random.random() > contact_rate:
            return None  # 空振り
        
        # コンタクト成功 - 打球データを生成
        # ===== 打球の質（Soft/Mid/Hard）の決定 =====
        # 目標: Soft%=23%, Mid%=42%, Hard%=35%
        # コンタクト能力とパワーで調整
        
        quality_roll = random.random()
        # 打者能力による補正（contact+power平均が高いほどHard%が増加）
        ability_factor = (contact + power) / 40  # 0.5-1.0程度
        
        # Soft/Mid/Hard の閾値を設定
        # 目標値に直接近づける
        soft_threshold = 0.23
        hard_threshold = 0.35
        mid_threshold = 1.0 - soft_threshold - hard_threshold  # 0.42
        
        if quality_roll < soft_threshold:
            contact_quality = random.uniform(0.0, 0.35)  # Soft contact
        elif quality_roll < soft_threshold + mid_threshold:
            contact_quality = random.uniform(0.35, 0.70)  # Mid contact
        else:
            contact_quality = random.uniform(0.70, 1.0)  # Hard contact
        
        # ===== 打球速度の計算（Soft/Mid/Hardに基づく） =====
        # 目標: Soft%=23%(95km/h以下), Mid%=42%(95-135km/h), Hard%=35%(135km/h以上)
        
        if contact_quality < 0.35:
            # Soft contact: 60-95 km/h
            base_exit_velo = 60 + power * 0.8
            exit_velocity = base_exit_velo + contact_quality * 80
            exit_velocity = min(SOFT_CONTACT_MAX_VELO, exit_velocity)
        elif contact_quality < 0.70:
            # Mid contact: 95-135 km/h
            normalized_q = (contact_quality - 0.35) / 0.35  # 0-1に正規化
            base_exit_velo = SOFT_CONTACT_MAX_VELO + power * 0.5
            exit_velocity = base_exit_velo + normalized_q * (MID_CONTACT_MAX_VELO - SOFT_CONTACT_MAX_VELO)
        else:
            # Hard contact: 135-193 km/h
            normalized_q = (contact_quality - 0.70) / 0.30  # 0-1に正規化
            base_exit_velo = MID_CONTACT_MAX_VELO + power * 1.5
            exit_velocity = base_exit_velo + normalized_q * (MAX_EXIT_VELOCITY - MID_CONTACT_MAX_VELO) * 0.6
        
        # ランダム変動を追加
        exit_velocity += random.gauss(0, 4)
        exit_velocity = max(MIN_EXIT_VELOCITY, min(MAX_EXIT_VELOCITY, exit_velocity))
        
        # ===== 打球角度の計算（目標: GB%=45%, LD%=10%, FB%=45%, IFFB%=10%） =====
        # 弾道: 1=ゴロ打ち, 2=普通, 3=ライナー, 4=フライ打ち
        
        # 打球タイプをまず決定（目標比率に基づく）
        type_roll = random.random()
        
        # 弾道タイプによる補正
        # trajectory: 1=ゴロ打ち(GB+10%), 2=普通, 3=ライナー(LD+5%), 4=フライ打ち(FB+10%)
        gb_boost = {1: 0.12, 2: 0.00, 3: -0.05, 4: -0.10}.get(trajectory, 0)
        ld_boost = {1: -0.03, 2: 0, 3: 0.05, 4: -0.02}.get(trajectory, 0)
        
        # 基本確率 (GB=45%, LD=10%, FB=35%, IFFB=10%)
        gb_chance = 0.43 + gb_boost  # 少し下げる
        ld_chance = 0.10 + ld_boost
        fb_chance = 0.37 - gb_boost * 0.4  # 少し上げる
        iffb_chance = 0.10  # 内野フライは固定
        
        # コンタクトの質による補正（影響を弱める）
        # Soft contactはゴロかポップアップになりやすい
        if contact_quality < 0.35:
            gb_chance += 0.05  # 0.08→0.05
            ld_chance -= 0.01
            fb_chance -= 0.05
            iffb_chance += 0.01
        # Hard contactはライナーやフライになりやすい
        elif contact_quality > 0.70:
            gb_chance -= 0.04  # 0.06→0.04
            ld_chance += 0.01
            fb_chance += 0.03
            iffb_chance -= 0.01
        
        # 正規化
        total = gb_chance + ld_chance + fb_chance + iffb_chance
        gb_chance /= total
        ld_chance /= total
        fb_chance /= total
        iffb_chance /= total
        
        # 打球タイプと角度を決定
        if type_roll < gb_chance:
            # ゴロ: -15度 〜 10度
            launch_angle = random.gauss(2, 5)
            launch_angle = max(-15, min(GROUNDBALL_MAX_ANGLE, launch_angle))
        elif type_roll < gb_chance + ld_chance:
            # ライナー: 10度 〜 25度
            launch_angle = random.gauss(17, 4)
            launch_angle = max(LINEDRIVE_MIN_ANGLE, min(LINEDRIVE_MAX_ANGLE, launch_angle))
        elif type_roll < gb_chance + ld_chance + fb_chance:
            # 通常フライ: 25度 〜 50度
            # 角度を高めに設定して飛距離を抑える（平均38度、外野フライ捕球率向上のため）
            launch_angle = random.gauss(38, 6)
            launch_angle = max(FLYBALL_MIN_ANGLE, min(POPUP_MIN_ANGLE - 1, launch_angle))
        else:
            # 内野フライ（ポップアップ）: 50度 〜 65度
            launch_angle = random.gauss(55, 5)
            launch_angle = max(POPUP_MIN_ANGLE, min(65, launch_angle))
        
        launch_angle = max(-15, min(65, launch_angle))
        
        # 打球方向（打者の特性を考慮）
        # プル（引っ張り）: 左打者→ライト、右打者→レフト
        pull_tendency = getattr(batter_stats, 'pull', 0)  # -10〜10
        spray_center = pull_tendency * 1.5  # 傾向による中心のずれ
        spray_angle = random.gauss(spray_center, 22)
        spray_angle = max(-45, min(45, spray_angle))
        
        # 回転数の計算（打球角度と打球速度に依存）
        if launch_angle > 20:
            # フライボールはバックスピンが多い
            base_spin = 2200 + launch_angle * 25
        elif launch_angle > 0:
            # ライナーは中程度の回転
            base_spin = 1800 + launch_angle * 20
        else:
            # ゴロは回転が少ない
            base_spin = 800 + abs(launch_angle) * 30
        
        spin_rate = int(base_spin + random.gauss(0, 200))
        spin_rate = max(500, min(3500, spin_rate))
        
        # 打球タイプの判定（新しい角度基準）
        if launch_angle <= GROUNDBALL_MAX_ANGLE:
            hit_type = "ground"
        elif launch_angle <= LINEDRIVE_MAX_ANGLE:
            hit_type = "line"
        elif launch_angle < POPUP_MIN_ANGLE:
            hit_type = "fly"
        else:
            hit_type = "popup"
        
        # フライとポップアップは飛距離を抑えるために打球速度を調整
        # （contact_qualityには影響させず、最終的な速度のみ調整）
        final_exit_velocity = exit_velocity
        if hit_type == "fly":
            final_exit_velocity *= 0.88
        elif hit_type == "popup":
            final_exit_velocity *= 0.70
        
        return BattedBallData(
            exit_velocity=final_exit_velocity,
            launch_angle=launch_angle,
            spray_angle=spray_angle,
            spin_rate=spin_rate,
            spin_axis=random.uniform(0, 360),
            contact_quality=contact_quality,
            hit_type=hit_type
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
