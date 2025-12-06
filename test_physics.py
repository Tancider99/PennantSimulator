# -*- coding: utf-8 -*-
"""物理エンジンのテスト"""
from physics_engine import *
import random

def test_physics_engine():
    random.seed(42)
    pe = PhysicsEngine()

    # いくつかの打球パターンをテスト
    test_cases = [
        ('ホームラン級', 175, 28, 0, 2600, 0.95),
        ('深い外野フライ', 145, 32, -10, 2200, 0.75),
        ('センター前ライナー', 155, 12, 0, 1800, 0.70),
        ('浅いフライ', 120, 35, 15, 2000, 0.55),
        ('ゴロ', 130, 5, -20, 800, 0.60),
        ('弱いポップフライ', 90, 55, 5, 1500, 0.35),
    ]

    print('=== 外野打球処理テスト ===\n')
    for name, velo, angle, spray, spin, quality in test_cases:
        hit_type = 'fly' if angle > 20 else 'line' if angle > 8 else 'ground'
        bd = BattedBallData(
            exit_velocity=velo, 
            launch_angle=angle, 
            spray_angle=spray, 
            spin_rate=spin, 
            spin_axis=45, 
            contact_quality=quality, 
            hit_type=hit_type
        )
        result, dist, hang = pe.calculate_batted_ball(bd)
        
        print(f'【{name}】')
        print(f'  打球速度: {velo}km/h, 角度: {angle}度, 方向: {spray}度')
        print(f'  結果: {result.value}')
        print(f'  飛距離: {dist:.1f}m, 滞空時間: {hang:.2f}秒')
        
        if hit_type in ['fly', 'line'] and dist > 40:
            defense = pe.simulate_outfield_defense(bd)
            print(f'  担当: {defense.fielder_position}')
            print(f'  守備結果: {defense.description}')
            caught_str = '成功' if defense.is_caught else '失敗'
            print(f'  捕球: {caught_str}, 難易度: {defense.catch_difficulty:.2f}')
            if defense.is_diving_catch:
                print(f'  * ダイビングキャッチ！')
            if defense.is_wall_catch:
                print(f'  * フェンス際のキャッチ！')
        print()

def test_multiple_plays():
    """複数の打席をシミュレート"""
    print('\n=== 複数打球シミュレーション (10打球) ===\n')
    
    pe = PhysicsEngine()
    results_count = {}
    
    for i in range(10):
        # ランダムな打球を生成
        velo = random.gauss(130, 20)
        angle = random.gauss(15, 15)
        spray = random.gauss(0, 20)
        quality = random.betavariate(2.5, 3)
        
        hit_type = 'fly' if angle > 20 else 'line' if angle > 8 else 'ground'
        bd = BattedBallData(
            exit_velocity=max(60, min(190, velo)),
            launch_angle=max(-15, min(65, angle)),
            spray_angle=max(-45, min(45, spray)),
            spin_rate=int(1500 + angle * 25),
            spin_axis=random.uniform(0, 360),
            contact_quality=quality,
            hit_type=hit_type
        )
        
        result, dist, hang = pe.calculate_batted_ball(bd)
        result_name = result.value
        results_count[result_name] = results_count.get(result_name, 0) + 1
        
        print(f'{i+1}. {result_name:12} - {dist:5.1f}m ({hit_type})')
    
    print('\n--- 結果集計 ---')
    for result, count in sorted(results_count.items(), key=lambda x: -x[1]):
        print(f'  {result}: {count}回')

def test_game_simulation():
    """ゲームエンジンとの統合テスト"""
    print('\n=== ゲームエンジン統合テスト ===\n')
    
    try:
        from advanced_game_engine import AdvancedGameEngine, Weather, Stadium
        from models import Team, Player, Position, PlayerStats, League
        
        # ダミーチームを作成
        def create_dummy_team(name, league):
            team = Team(name=name, league=league)
            # 野手を追加
            positions = [Position.CATCHER, Position.FIRST, Position.SECOND, 
                        Position.THIRD, Position.SHORTSTOP, 
                        Position.OUTFIELD, Position.OUTFIELD, Position.OUTFIELD]
            for i, pos in enumerate(positions):
                stats = PlayerStats(
                    contact=random.randint(10, 18),
                    power=random.randint(8, 18),
                    run=random.randint(10, 18),
                    arm=random.randint(10, 16),
                    fielding=random.randint(10, 16),
                    speed=10, control=10, breaking=10
                )
                player = Player(
                    name=f"{name}選手{i+1}",
                    position=pos,
                    stats=stats
                )
                team.players.append(player)
            
            # 投手を追加
            for i in range(5):
                stats = PlayerStats(
                    contact=5, power=5, run=8, arm=12, fielding=10,
                    speed=random.randint(12, 18),
                    control=random.randint(10, 16),
                    breaking=random.randint(10, 16)
                )
                player = Player(
                    name=f"{name}投手{i+1}",
                    position=Position.PITCHER,
                    stats=stats
                )
                team.players.append(player)
            
            # ラインナップ設定
            team.current_lineup = list(range(8))
            team.starting_pitcher_idx = 8
            return team
        
        home = create_dummy_team("ホーム", League.CENTRAL)
        away = create_dummy_team("アウェイ", League.CENTRAL)
        
        engine = AdvancedGameEngine(home, away)
        
        # 数打席シミュレート
        print("打席シミュレーション:")
        for i in range(5):
            batter = away.players[i]
            pitcher = home.players[home.starting_pitcher_idx]
            result = engine.simulate_at_bat(batter, pitcher)
            print(f"  {i+1}. {result.description}")
        
        print("\n統合テスト成功！")
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_physics_engine()
    test_multiple_plays()
    test_game_simulation()
