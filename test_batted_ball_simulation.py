# -*- coding: utf-8 -*-
"""
打球シミュレーションの精度テスト
NPBの実際のデータと比較して改善点を特定する
"""
import random
import math
from collections import defaultdict
from physics_engine import (
    PhysicsEngine, AtBatSimulator, BattedBallData, HitResult,
    GROUNDBALL_MAX_ANGLE, LINEDRIVE_MAX_ANGLE, FLYBALL_MIN_ANGLE
)

# NPB 2023年シーズンの実際の統計データ（参考値）
NPB_ACTUAL_STATS = {
    # リーグ全体の打撃成績（NPB平均）
    "batting_average": 0.247,  # 打率
    "on_base_percentage": 0.314,  # 出塁率
    "slugging_percentage": 0.377,  # 長打率
    "home_run_rate": 0.027,  # 打席あたりHR率（約2.7%）
    "strikeout_rate": 0.203,  # 三振率
    "walk_rate": 0.084,  # 四球率
    
    # 打球タイプ別比率（推定値）
    "groundball_rate": 0.44,  # ゴロ率
    "flyball_rate": 0.35,  # フライ率
    "linedrive_rate": 0.21,  # ライナー率
    
    # 打球タイプ別の被打率（BABIP参考）
    "groundball_hit_rate": 0.230,  # ゴロヒット率
    "linedrive_hit_rate": 0.680,  # ライナーヒット率
    "flyball_hit_rate": 0.140,  # フライヒット率（HRを含まず）
    
    # 長打率（ヒット全体に対する割合）
    "double_rate_of_hits": 0.20,  # 二塁打率（安打中）
    "triple_rate_of_hits": 0.015,  # 三塁打率（安打中）
    "home_run_rate_of_hits": 0.10,  # 本塁打率（安打中）
}


def create_average_batter():
    """NPB平均的な打者のステータス"""
    class BatterStats:
        def __init__(self):
            self.contact = 13  # コンタクト（1-20）
            self.power = 12    # パワー（1-20）
            self.eye = 12      # 選球眼（1-20）
            self.trajectory = 2  # 弾道（1-4）
            self.pull = 0      # 引っ張り傾向（-10〜10）
    return BatterStats()


def create_power_batter():
    """パワーヒッター"""
    class BatterStats:
        def __init__(self):
            self.contact = 11
            self.power = 17
            self.eye = 11
            self.trajectory = 4
            self.pull = 3
    return BatterStats()


def create_contact_batter():
    """アベレージヒッター"""
    class BatterStats:
        def __init__(self):
            self.contact = 17
            self.power = 10
            self.eye = 15
            self.trajectory = 2
            self.pull = -2
    return BatterStats()


def create_average_pitcher():
    """NPB平均的な投手のステータス"""
    class PitcherStats:
        def __init__(self):
            self.speed = 13     # 球速（1-20）
            self.control = 13   # コントロール（1-20）
            self.breaking = 13  # 変化球（1-20）
    return PitcherStats()


def simulate_batted_balls(num_simulations: int = 10000):
    """打球のみをシミュレート（スイングが成功した場合のみ）"""
    print(f"\n=== 打球シミュレーション ({num_simulations:,}打球) ===\n")
    
    physics = PhysicsEngine()
    results = defaultdict(int)
    hit_types = defaultdict(int)
    exit_velocities = []
    launch_angles = []
    distances = []
    
    batter = create_average_batter()
    
    for _ in range(num_simulations):
        # ランダムな打球を生成（打者能力に基づく）
        # 芯を捉えた度合い
        alpha = 2.0 + batter.contact * 0.15
        beta = 3.5 - batter.contact * 0.05
        contact_quality = random.betavariate(alpha, max(1.5, beta))
        
        # 打球速度
        if contact_quality > 0.8:
            base_exit_velo = 145 + batter.power * 2.2
            exit_velocity = base_exit_velo * (0.9 + contact_quality * 0.15)
        elif contact_quality > 0.5:
            base_exit_velo = 120 + batter.power * 1.8
            exit_velocity = base_exit_velo * (0.8 + contact_quality * 0.25)
        else:
            base_exit_velo = 80 + batter.power * 1.2
            exit_velocity = base_exit_velo * (0.6 + contact_quality * 0.5)
        
        exit_velocity += random.gauss(0, 4)
        exit_velocity = max(60, min(193, exit_velocity))
        
        # 打球角度
        trajectory = batter.trajectory
        trajectory_base = {1: 2, 2: 10, 3: 16, 4: 22}.get(trajectory, 12)
        
        if contact_quality > 0.7:
            if trajectory >= 3:
                target_angle = 28 - (4 - trajectory) * 3
            else:
                target_angle = trajectory_base + random.gauss(5, 3)
            launch_angle = target_angle + random.gauss(0, 6)
        elif contact_quality > 0.4:
            launch_angle = trajectory_base + random.gauss(0, 10)
        else:
            if random.random() < 0.6:
                launch_angle = random.gauss(-5, 8)
            else:
                launch_angle = random.gauss(50, 10)
        
        launch_angle = max(-15, min(65, launch_angle))
        
        # 打球方向
        spray_angle = random.gauss(0, 22)
        spray_angle = max(-45, min(45, spray_angle))
        
        # 打球タイプ
        if launch_angle < GROUNDBALL_MAX_ANGLE:
            hit_type = "ground"
        elif launch_angle < LINEDRIVE_MAX_ANGLE:
            hit_type = "line"
        elif launch_angle < FLYBALL_MIN_ANGLE + 20:
            hit_type = "fly"
        else:
            hit_type = "popup"
        
        hit_types[hit_type] += 1
        
        # 回転数
        if launch_angle > 20:
            base_spin = 2200 + launch_angle * 25
        elif launch_angle > 0:
            base_spin = 1800 + launch_angle * 20
        else:
            base_spin = 800 + abs(launch_angle) * 30
        
        spin_rate = int(base_spin + random.gauss(0, 200))
        spin_rate = max(500, min(3500, spin_rate))
        
        # 打球データ作成
        ball_data = BattedBallData(
            exit_velocity=exit_velocity,
            launch_angle=launch_angle,
            spray_angle=spray_angle,
            spin_rate=spin_rate,
            spin_axis=random.uniform(0, 360),
            contact_quality=contact_quality,
            hit_type=hit_type
        )
        
        # 結果を計算
        result, distance, hang_time = physics.calculate_batted_ball(ball_data)
        
        results[result.value] += 1
        exit_velocities.append(exit_velocity)
        launch_angles.append(launch_angle)
        distances.append(distance)
    
    # 結果を表示
    print("--- 打球結果の分布 ---")
    total = sum(results.values())
    
    # 分類して表示
    hits = results.get("単打", 0) + results.get("二塁打", 0) + results.get("三塁打", 0) + results.get("ホームラン", 0) + results.get("内野安打", 0)
    outs = results.get("ゴロアウト", 0) + results.get("フライアウト", 0) + results.get("ライナーアウト", 0)
    
    print(f"\n安打: {hits}/{total} ({hits/total*100:.1f}%)")
    print(f"アウト: {outs}/{total} ({outs/total*100:.1f}%)")
    
    print("\n詳細:")
    for result, count in sorted(results.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"  {result:12}: {count:5} ({pct:5.1f}%) {bar}")
    
    # 打球タイプ別の分布
    print("\n--- 打球タイプ別分布 ---")
    total_types = sum(hit_types.values())
    for ht, count in sorted(hit_types.items(), key=lambda x: -x[1]):
        pct = count / total_types * 100
        print(f"  {ht:10}: {count:5} ({pct:5.1f}%)")
    
    # NPBとの比較
    print("\n--- NPB実データとの比較 ---")
    
    # 打球タイプ比較
    sim_gb_rate = hit_types["ground"] / total_types
    sim_fb_rate = (hit_types["fly"] + hit_types["popup"]) / total_types
    sim_ld_rate = hit_types["line"] / total_types
    
    print(f"\nゴロ率:    シミュ {sim_gb_rate*100:.1f}%  vs  NPB {NPB_ACTUAL_STATS['groundball_rate']*100:.1f}%")
    print(f"フライ率:  シミュ {sim_fb_rate*100:.1f}%  vs  NPB {NPB_ACTUAL_STATS['flyball_rate']*100:.1f}%")
    print(f"ライナー率: シミュ {sim_ld_rate*100:.1f}%  vs  NPB {NPB_ACTUAL_STATS['linedrive_rate']*100:.1f}%")
    
    # 安打率（インプレイ時）
    batting_avg = hits / total
    print(f"\nBABIP:     シミュ {batting_avg:.3f}  vs  NPB ~0.290-0.300")
    
    # 長打率
    hr_rate = results.get("ホームラン", 0) / total
    doubles = results.get("二塁打", 0) / total
    triples = results.get("三塁打", 0) / total
    print(f"\nHR率:      シミュ {hr_rate*100:.2f}%  vs  NPB ~2-3%")
    print(f"二塁打率:  シミュ {doubles*100:.2f}%")
    print(f"三塁打率:  シミュ {triples*100:.2f}%")
    
    # 統計
    print("\n--- 打球速度・角度の統計 ---")
    avg_velo = sum(exit_velocities) / len(exit_velocities)
    avg_angle = sum(launch_angles) / len(launch_angles)
    avg_dist = sum(distances) / len(distances)
    
    print(f"平均打球速度: {avg_velo:.1f} km/h")
    print(f"平均打球角度: {avg_angle:.1f}°")
    print(f"平均飛距離:   {avg_dist:.1f} m")
    
    return results, hit_types


def simulate_at_bats(num_at_bats: int = 5000):
    """完全な打席シミュレーション"""
    print(f"\n=== 打席シミュレーション ({num_at_bats:,}打席) ===\n")
    
    simulator = AtBatSimulator()
    batter = create_average_batter()
    pitcher = create_average_pitcher()
    
    results = defaultdict(int)
    pitch_counts = []
    
    for _ in range(num_at_bats):
        result, details = simulator.simulate_at_bat(
            batter, 
            pitcher, 
            ["ストレート", "スライダー", "フォーク", "チェンジアップ"]
        )
        results[result.value] += 1
        pitch_counts.append(len(details.get("pitches", [])))
    
    # 結果表示
    total = sum(results.values())
    
    # 安打/アウト/四球/三振を分類
    hits = (results.get("単打", 0) + results.get("二塁打", 0) + 
            results.get("三塁打", 0) + results.get("ホームラン", 0) + 
            results.get("内野安打", 0))
    outs = (results.get("ゴロアウト", 0) + results.get("フライアウト", 0) + 
            results.get("ライナーアウト", 0) + results.get("三振", 0))
    walks = results.get("四球", 0) + results.get("死球", 0)
    
    # 打席結果（三振・四球込み）
    at_bats = total - walks  # 規定打数
    
    print("--- 打席結果の分布 ---")
    for result, count in sorted(results.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"  {result:12}: {count:5} ({pct:5.1f}%) {bar}")
    
    # 成績計算
    batting_avg = hits / at_bats if at_bats > 0 else 0
    obp = (hits + walks) / total
    
    # 長打率計算（簡易）
    singles = results.get("単打", 0) + results.get("内野安打", 0)
    doubles = results.get("二塁打", 0)
    triples = results.get("三塁打", 0)
    home_runs = results.get("ホームラン", 0)
    total_bases = singles + doubles * 2 + triples * 3 + home_runs * 4
    slg = total_bases / at_bats if at_bats > 0 else 0
    
    strikeout_rate = results.get("三振", 0) / total
    walk_rate = walks / total
    
    print("\n--- 成績 ---")
    print(f"打率:    {batting_avg:.3f}  (NPB平均: {NPB_ACTUAL_STATS['batting_average']:.3f})")
    print(f"出塁率:  {obp:.3f}  (NPB平均: {NPB_ACTUAL_STATS['on_base_percentage']:.3f})")
    print(f"長打率:  {slg:.3f}  (NPB平均: {NPB_ACTUAL_STATS['slugging_percentage']:.3f})")
    print(f"三振率:  {strikeout_rate:.3f}  (NPB平均: {NPB_ACTUAL_STATS['strikeout_rate']:.3f})")
    print(f"四球率:  {walk_rate:.3f}  (NPB平均: {NPB_ACTUAL_STATS['walk_rate']:.3f})")
    
    print(f"\n平均球数: {sum(pitch_counts)/len(pitch_counts):.1f}球")
    
    return results


def analyze_by_hit_type(num_simulations: int = 20000):
    """打球タイプ別の結果を詳細分析"""
    print(f"\n=== 打球タイプ別詳細分析 ({num_simulations:,}打球) ===\n")
    
    physics = PhysicsEngine()
    
    type_results = {
        "ground": defaultdict(int),
        "line": defaultdict(int),
        "fly": defaultdict(int),
        "popup": defaultdict(int)
    }
    type_counts = defaultdict(int)
    
    for _ in range(num_simulations):
        # ランダムな打球
        exit_velocity = random.gauss(130, 20)
        exit_velocity = max(60, min(190, exit_velocity))
        
        launch_angle = random.gauss(12, 15)
        launch_angle = max(-15, min(65, launch_angle))
        
        spray_angle = random.gauss(0, 22)
        spray_angle = max(-45, min(45, spray_angle))
        
        contact_quality = random.betavariate(2.5, 3)
        
        # 打球タイプ判定
        if launch_angle < GROUNDBALL_MAX_ANGLE:
            hit_type = "ground"
        elif launch_angle < LINEDRIVE_MAX_ANGLE:
            hit_type = "line"
        elif launch_angle < FLYBALL_MIN_ANGLE + 20:
            hit_type = "fly"
        else:
            hit_type = "popup"
        
        if launch_angle > 20:
            base_spin = 2200 + launch_angle * 25
        elif launch_angle > 0:
            base_spin = 1800 + launch_angle * 20
        else:
            base_spin = 800 + abs(launch_angle) * 30
        spin_rate = int(base_spin + random.gauss(0, 200))
        
        ball_data = BattedBallData(
            exit_velocity=exit_velocity,
            launch_angle=launch_angle,
            spray_angle=spray_angle,
            spin_rate=spin_rate,
            spin_axis=random.uniform(0, 360),
            contact_quality=contact_quality,
            hit_type=hit_type
        )
        
        result, distance, hang_time = physics.calculate_batted_ball(ball_data)
        
        type_results[hit_type][result.value] += 1
        type_counts[hit_type] += 1
    
    # 結果表示
    for hit_type in ["ground", "line", "fly", "popup"]:
        total = type_counts[hit_type]
        results = type_results[hit_type]
        
        hits = sum(results.get(h, 0) for h in ["単打", "二塁打", "三塁打", "ホームラン", "内野安打"])
        hit_rate = hits / total if total > 0 else 0
        
        print(f"\n【{hit_type.upper()}】 ({total}打球)")
        print(f"  安打率: {hit_rate:.3f}")
        
        target_rate = {
            "ground": NPB_ACTUAL_STATS["groundball_hit_rate"],
            "line": NPB_ACTUAL_STATS["linedrive_hit_rate"],
            "fly": NPB_ACTUAL_STATS["flyball_hit_rate"],
            "popup": 0.02  # ポップフライはほぼアウト
        }.get(hit_type, 0.2)
        
        print(f"  目標:   {target_rate:.3f}")
        
        for result, count in sorted(results.items(), key=lambda x: -x[1]):
            pct = count / total * 100 if total > 0 else 0
            print(f"    {result:12}: {count:4} ({pct:5.1f}%)")


if __name__ == "__main__":
    random.seed(42)
    
    # 打球シミュレーション
    batted_results, hit_types = simulate_batted_balls(15000)
    
    # 打球タイプ別分析
    analyze_by_hit_type(20000)
    
    # 打席シミュレーション
    at_bat_results = simulate_at_bats(3000)
