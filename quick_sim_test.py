# -*- coding: utf-8 -*-
"""
高速打球シミュレーションテスト
目標: GB%=45%, LD%=10%, FB%=35%, IFFB%=10%
     Soft%=23%, Mid%=42%, Hard%=35%
"""
import random
from collections import defaultdict
from physics_engine import (
    PhysicsEngine, BattedBallData, AtBatSimulator,
    GROUNDBALL_MAX_ANGLE, LINEDRIVE_MAX_ANGLE, POPUP_MIN_ANGLE,
    SOFT_CONTACT_MAX_VELO, MID_CONTACT_MAX_VELO
)
import math

# NPB リーグ平均目標値
NPB_STATS = {
    "groundball_rate": 0.45,   # GB%=45%
    "linedrive_rate": 0.10,    # LD%=10%
    "flyball_rate": 0.35,      # FB%=35%
    "popup_rate": 0.10,        # IFFB%=10%
    "soft_rate": 0.23,         # Soft%=23%
    "mid_rate": 0.42,          # Mid%=42%
    "hard_rate": 0.35,         # Hard%=35%
}


def create_average_batter():
    """平均的な打者"""
    class BatterStats:
        def __init__(self):
            self.contact = 13
            self.power = 12
            self.eye = 12
            self.trajectory = 2  # 普通
            self.pull = 0
    return BatterStats()


def create_average_pitcher():
    """平均的な投手"""
    class PitcherStats:
        def __init__(self):
            self.speed = 13
            self.control = 13
            self.breaking = 13
    return PitcherStats()


def quick_test(n=5000):
    print(f"打球シミュレーション ({n}打球)\n")
    
    simulator = AtBatSimulator()
    batter = create_average_batter()
    pitcher = create_average_pitcher()
    
    results = defaultdict(int)
    hit_types = defaultdict(int)
    type_hits = defaultdict(lambda: defaultdict(int))
    
    # 打球の質カウント（contact_qualityベース）
    soft_count = 0
    mid_count = 0
    hard_count = 0
    exit_velocities = []
    launch_angles = []
    
    # デバッグ用
    fly_debug = {"caught": 0, "hit": 0, "hr": 0, "hang_times": [], "distances": []}
    
    batted_balls = 0
    
    for _ in range(n * 3):  # 打席数を増やして十分な打球数を確保
        # 投球を生成
        pitch = simulator.generate_pitch(pitcher, "ストレート")
        
        # スイングシミュレーション
        ball_data = simulator.simulate_swing(batter, pitch)
        
        if ball_data is None:
            continue  # 空振り/見逃し
        
        batted_balls += 1
        
        # 打球の質を分類（contact_qualityベース）
        if ball_data.contact_quality < 0.35:
            soft_count += 1
        elif ball_data.contact_quality < 0.70:
            mid_count += 1
        else:
            hard_count += 1
        
        exit_velocities.append(ball_data.exit_velocity)
        launch_angles.append(ball_data.launch_angle)
        
        # 打球タイプをカウント
        hit_types[ball_data.hit_type] += 1
        
        # 結果を計算
        result, distance, hang_time = simulator.physics.calculate_batted_ball(ball_data)
        results[result.value] += 1
        type_hits[ball_data.hit_type][result.value] += 1
        
        # フライのデバッグ
        if ball_data.hit_type == "fly":
            fly_debug["hang_times"].append(hang_time)
            fly_debug["distances"].append(distance)
            if result.value == "ホームラン":
                fly_debug["hr"] += 1
            elif result.value in ["単打", "二塁打", "三塁打"]:
                fly_debug["hit"] += 1
            else:
                fly_debug["caught"] += 1
        
        if batted_balls >= n:
            break
    
    # 結果表示
    print("=== 打球結果 ===")
    total = sum(results.values())
    hits = sum(results.get(h, 0) for h in ["単打", "二塁打", "三塁打", "ホームラン", "内野安打"])
    
    for r, c in sorted(results.items(), key=lambda x: -x[1]):
        print(f"  {r:12}: {c:4} ({c/total*100:5.1f}%)")
    
    print(f"\nBABIP(安打率): {hits/total:.3f}")
    
    # 打球タイプ別
    print("\n=== 打球タイプ別分布 ===")
    tt = sum(hit_types.values())
    for ht in ["ground", "line", "fly", "popup"]:
        cnt = hit_types[ht]
        th = type_hits[ht]
        h = sum(th.get(x, 0) for x in ["単打", "二塁打", "三塁打", "ホームラン", "内野安打"])
        rate = h/cnt if cnt > 0 else 0
        target = {"ground": 0.45, "line": 0.10, "fly": 0.35, "popup": 0.10}.get(ht, 0.25)
        actual = cnt/tt if tt > 0 else 0
        print(f"  {ht:6}: {cnt:4} ({actual*100:4.1f}%) 目標={target*100:.0f}% 安打率={rate:.3f}")
    
    # 打球の質（Soft/Mid/Hard） - contact_qualityベース
    print("\n=== 打球の質 (contact_quality) ===")
    total_quality = soft_count + mid_count + hard_count
    if total_quality > 0:
        print(f"  Soft  (cq<0.35): {soft_count:4} ({soft_count/total_quality*100:5.1f}%) 目標={NPB_STATS['soft_rate']*100:.0f}%")
        print(f"  Mid   (0.35-0.70): {mid_count:4} ({mid_count/total_quality*100:5.1f}%) 目標={NPB_STATS['mid_rate']*100:.0f}%")
        print(f"  Hard  (cq>0.70): {hard_count:4} ({hard_count/total_quality*100:5.1f}%) 目標={NPB_STATS['hard_rate']*100:.0f}%")
    
    # 統計
    print("\n=== 打球速度・角度の統計 ===")
    if exit_velocities:
        avg_velo = sum(exit_velocities) / len(exit_velocities)
        avg_angle = sum(launch_angles) / len(launch_angles)
        print(f"平均打球速度: {avg_velo:.1f} km/h")
        print(f"平均打球角度: {avg_angle:.1f}°")
    
    # フライのデバッグ
    print("\n=== フライ分析 ===")
    total_fly = fly_debug["caught"] + fly_debug["hit"] + fly_debug["hr"]
    if total_fly > 0:
        print(f"  捕球: {fly_debug['caught']} ({fly_debug['caught']/total_fly*100:.1f}%)")
        print(f"  安打: {fly_debug['hit']} ({fly_debug['hit']/total_fly*100:.1f}%)")
        print(f"  HR: {fly_debug['hr']} ({fly_debug['hr']/total_fly*100:.1f}%)")
        if fly_debug["hang_times"]:
            print(f"  平均滞空時間: {sum(fly_debug['hang_times'])/len(fly_debug['hang_times']):.2f}秒")
            print(f"  平均飛距離: {sum(fly_debug['distances'])/len(fly_debug['distances']):.1f}m")


if __name__ == "__main__":
    random.seed(42)
    quick_test(5000)
