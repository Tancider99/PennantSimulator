# -*- coding: utf-8 -*-
"""
試合シミュレーター（打球物理演算版 - OOTP Stats対応）
"""
import random
import math
from typing import Tuple, List, Optional, Dict
from enum import Enum
from dataclasses import dataclass, field
from models import Team, Player, PitchType

# ========================================
# 打球物理計算モジュール
# ========================================
@dataclass
class BattedBall:
    """打球データ"""
    exit_velocity: float    # 打球速度 (km/h)
    launch_angle: float     # 打球角度 (度)
    spray_angle: float      # 打球方向 (度)
    hang_time: float = 0.0
    distance: float = 0.0
    
    def __post_init__(self):
        # 簡易飛距離計算
        v0 = self.exit_velocity / 3.6
        angle_rad = math.radians(self.launch_angle)
        g = 9.8
        drag = 0.35 # 空気抵抗係数
        
        vx = v0 * math.cos(angle_rad)
        vy = v0 * math.sin(angle_rad)
        
        if self.launch_angle > 0:
            t_flight = (2 * vy / g) * (1 - drag * 0.3)
            self.hang_time = max(0.5, t_flight)
            self.distance = vx * self.hang_time * (1 - drag)
        else:
            self.hang_time = 0.3 + abs(self.launch_angle) / 30
            self.distance = vx * self.hang_time * 0.7


class BattedBallCalculator:
    """打球物理計算クラス"""
    
    CENTER_FIELD_FENCE = 122.0
    OUTFIELD_START = 75.0
    
    @staticmethod
    def calculate_batted_ball(batter_stats, pitcher_stats) -> BattedBall:
        """打球データを計算 (OOTP Stats対応)"""
        # 打者能力
        contact = batter_stats.contact
        power = batter_stats.power
        # 投手能力
        velocity = pitcher_stats.velocity # 実数値 (km/h)
        movement = pitcher_stats.movement # 被本塁打抑制
        
        # ===== 打球速度 (km/h) =====
        base_velocity = 95
        power_bonus = (power - 40) * 0.9
        
        # 球速の反発 (145km/h基準で増減)
        pitch_vel_factor = (velocity - 130) * 0.4
        
        sweet_spot = random.gauss(0, 18)
        
        exit_velocity = base_velocity + power_bonus + pitch_vel_factor + sweet_spot
        # Movementが高いと芯を外させ、打球速度を下げる
        if movement > 60:
            exit_velocity -= (movement - 50) * 0.3
            
        exit_velocity = max(70, min(180, exit_velocity))
        
        # ===== 打球角度 (度) =====
        # Powerが高いほど角度がつく、Contactが低いとブレる
        target_angle = 12 + (power - 50) * 0.15
        
        control_effect = (100 - contact) * 0.2
        angle_deviation = random.gauss(0, 15 + control_effect)
        
        launch_angle = target_angle + angle_deviation
        launch_angle = max(-20, min(65, launch_angle))
        
        # ===== 打球方向 (度) =====
        spray_angle = random.gauss(0, 25)
        if contact >= 70: spray_angle *= 0.85
        spray_angle = max(-45, min(45, spray_angle))
        
        return BattedBall(exit_velocity, launch_angle, spray_angle)
    
    @staticmethod
    def judge_result(ball: BattedBall, fielding_stats: Dict = None) -> Tuple[str, str]:
        ev = ball.exit_velocity
        la = ball.launch_angle
        dist = ball.distance
        
        avg_fielding = 50 # 仮
        
        # HR判定
        fence_dist = 115.0 # 平均フェンス距離
        if 20 <= la <= 45 and dist >= fence_dist:
            return "home_run", f"HR {dist:.0f}m"
            
        # フライ
        if la >= 15:
            if dist >= 75: # 外野
                catch_chance = 0.85 - (dist - 75)/60
                if random.random() > catch_chance:
                    if dist >= 105: return "triple", "三塁打"
                    if dist >= 90: return "double", "二塁打"
                    return "single", "ヒット"
                return "flyout", "外野フライ"
            return "flyout", "内野フライ"
            
        # ライナー
        elif 5 <= la < 15:
            if ev >= 145:
                if random.random() > 0.6: return "single", "ヒット"
                return "lineout", "ライナーアウト"
            if random.random() > 0.7: return "single", "ヒット"
            return "lineout", "ライナーアウト"
            
        # ゴロ
        else:
            if ev >= 140:
                if random.random() < 0.35: return "single", "強襲ヒット"
            return "groundout", "ゴロアウト"

    @staticmethod
    def simulate_swing(batter_stats, pitcher_stats) -> Tuple[str, Optional[BattedBall], str]:
        """スイング結果シミュレーション"""
        # OOTP Stats
        eye = batter_stats.eye
        avoid_k = batter_stats.avoid_k
        contact = batter_stats.contact
        
        control = pitcher_stats.control
        stuff = pitcher_stats.stuff
        
        # ストライク判定 (Control vs Eye)
        strike_prob = 0.45 + (control - 50) * 0.003 - (eye - 50) * 0.002
        is_strike = random.random() < strike_prob
        
        if is_strike:
            # スイング判定
            swing_prob = 0.7
            if random.random() < swing_prob:
                # コンタクト判定 (Avoid K vs Stuff)
                # Stuffが高いと空振りしやすい、Avoid Kが高いと当てやすい
                contact_prob = 0.80 + (avoid_k - 50)*0.004 - (stuff - 50)*0.005
                contact_prob = max(0.4, min(0.95, contact_prob))
                
                if random.random() < contact_prob:
                    # インプレー
                    ball = BattedBallCalculator.calculate_batted_ball(batter_stats, pitcher_stats)
                    res, desc = BattedBallCalculator.judge_result(ball)
                    return res, ball, desc
                else:
                    return "swing_miss", None, "空振り"
            else:
                return "called_strike", None, "見逃し"
        else:
            # ボール球
            # 選球眼 (Eye) が高いと振らない
            chase_prob = 0.30 - (eye - 50) * 0.005
            chase_prob = max(0.05, min(0.5, chase_prob))
            
            if random.random() < chase_prob:
                # ボール球を振った -> 空振りor弱い当たり
                if random.random() < 0.6:
                    return "swing_miss", None, "空振り"
                else:
                    return "foul", None, "ファウル" # 簡易化
            else:
                return "ball", None, "ボール"

# ... (TacticManager, GameSimulatorクラスの残りは既存ロジックを維持しつつStats参照先を修正) ...

class TacticManager:
    @staticmethod
    def should_change_pitcher(pitcher: Player, game_state, team, stats) -> Tuple[bool, str]:
        # スタミナベースの交代判定
        stamina = pitcher.stats.stamina
        limit = 80 + (stamina - 50) * 0.8
        limit = max(50, min(130, limit))
        
        pitch_count = stats.get('pitch_count', 0)
        if pitch_count >= limit: return True, "スタミナ切れ"
        return False, ""

class GameSimulator:
    def __init__(self, home_team, away_team, use_physics=True, fast_mode=False, use_new_engine=False):
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = 0
        self.away_score = 0
        self.inning = 1
        self.max_innings = 9
        self.log = []
        self.tactic_manager = TacticManager()
        
        # 投手成績管理用
        self.home_pitcher_stats = {'pitch_count': 0, 'hits': 0, 'runs': 0, 'innings': 0}
        self.away_pitcher_stats = {'pitch_count': 0, 'hits': 0, 'runs': 0, 'innings': 0}
        self.current_home_pitcher_idx = home_team.starting_pitcher_idx
        self.current_away_pitcher_idx = away_team.starting_pitcher_idx
        
        self.inning_scores_home = []
        self.inning_scores_away = []

    def simulate_at_bat(self, batter, pitcher) -> Tuple[str, int]:
        """1打席シミュレーション"""
        balls = 0
        strikes = 0
        
        while balls < 4 and strikes < 3:
            res, ball, desc = BattedBallCalculator.simulate_swing(batter.stats, pitcher.stats)
            
            if res == "ball": balls += 1
            elif res in ["called_strike", "swing_miss"]: strikes += 1
            elif res == "foul":
                if strikes < 2: strikes += 1
            else:
                # インプレー結果
                if res == "home_run": return "home_run", 1
                if res in ["single", "double", "triple"]: return res, 0
                return "out", 0
                
        if balls >= 4: return "walk", 0
        return "strikeout", 0

    # ... (simulate_inning, simulate_game 等は既存の構造を維持) ...
    
    def simulate_inning(self, batting_team, pitching_team, batter_idx):
        outs = 0
        runs = 0
        runners = [False, False, False]
        
        # 投手取得 (簡易)
        is_home_pitching = (pitching_team == self.home_team)
        p_idx = self.current_home_pitcher_idx if is_home_pitching else self.current_away_pitcher_idx
        pitcher = pitching_team.players[p_idx]
        p_stats = self.home_pitcher_stats if is_home_pitching else self.away_pitcher_stats
        
        while outs < 3:
            # 打者取得
            b_idx = batting_team.current_lineup[batter_idx % 9]
            batter = batting_team.players[b_idx]
            
            # 打席結果
            res, dr = self.simulate_at_bat(batter, pitcher)
            p_stats['pitch_count'] += random.randint(3, 6)
            
            if res == "out" or res == "strikeout":
                outs += 1
                self.log.append(f"  {batter.name}: {res}")
            elif res == "walk":
                # 押し出し簡易処理
                if all(runners): runs += 1
                runners = [True, runners[0], runners[1]]
                self.log.append(f"  {batter.name}: 四球")
            elif res == "home_run":
                score = 1 + sum(runners)
                runs += score
                runners = [False, False, False]
                self.log.append(f"  {batter.name}: ホームラン！")
            else: # Hit
                runs += sum(runners) # 全員生還(簡易)
                if res == "single": runners = [True, False, False]
                elif res == "double": runners = [False, True, False]
                elif res == "triple": runners = [False, False, True]
                self.log.append(f"  {batter.name}: {res}")
            
            batter_idx += 1
            
        return runs, batter_idx

    def simulate_game(self):
        self.log = ["=== PLAY BALL ==="]
        h_idx = 0
        a_idx = 0
        
        for i in range(9):
            self.inning = i + 1
            self.log.append(f"--- {i+1}回表 ---")
            r, a_idx = self.simulate_inning(self.away_team, self.home_team, a_idx)
            self.away_score += r
            self.inning_scores_away.append(r)
            
            if i == 8 and self.home_score > self.away_score:
                self.inning_scores_home.append('X')
                break
                
            self.log.append(f"--- {i+1}回裏 ---")
            r, h_idx = self.simulate_inning(self.home_team, self.away_team, h_idx)
            self.home_score += r
            self.inning_scores_home.append(r)
            
        return self.home_score, self.away_score