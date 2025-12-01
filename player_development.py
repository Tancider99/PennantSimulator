# -*- coding: utf-8 -*-
"""
選手育成システム - パワプロ風の育成・成長システム
"""
import random
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TrainingType(Enum):
    """練習タイプ"""
    BATTING = "打撃練習"
    POWER = "筋力トレーニング"
    RUNNING = "走塁練習"
    FIELDING = "守備練習"
    PITCHING = "投球練習"
    STAMINA = "スタミナ強化"
    CONTROL = "制球練習"
    MENTAL = "メンタル強化"
    REST = "休養"


class InjuryType(Enum):
    """怪我のタイプ"""
    NONE = ("なし", 0)
    MINOR = ("軽傷", 5)
    MODERATE = ("中傷", 15)
    SERIOUS = ("重傷", 30)
    SEVERE = ("重症", 60)
    
    def __init__(self, display_name: str, recovery_days: int):
        self.display_name = display_name
        self.recovery_days = recovery_days


class PlayerCondition(Enum):
    """選手の調子"""
    EXCELLENT = ("絶好調", 1.3)
    GOOD = ("好調", 1.15)
    NORMAL = ("普通", 1.0)
    POOR = ("不調", 0.85)
    TERRIBLE = ("絶不調", 0.7)
    
    def __init__(self, display_name: str, multiplier: float):
        self.display_name = display_name
        self.multiplier = multiplier


@dataclass
class PlayerGrowth:
    """選手の成長データ"""
    potential: int  # ポテンシャル (1-10)
    growth_rate: float  # 成長率 (0.5-2.0)
    peak_age: int  # ピーク年齢 (25-32)
    decline_rate: float  # 衰退率 (0.5-1.5)
    
    def __init__(self, potential: int = 5):
        self.potential = potential
        self.growth_rate = 0.8 + (potential * 0.15)
        self.peak_age = random.randint(27, 32)
        self.decline_rate = 1.0 - (potential * 0.05)


@dataclass
class PlayerStatus:
    """選手の状態"""
    condition: PlayerCondition
    injury: InjuryType
    injury_days_remaining: int
    fatigue: int  # 疲労度 (0-100)
    motivation: int  # モチベーション (0-100)
    
    def __init__(self):
        self.condition = PlayerCondition.NORMAL
        self.injury = InjuryType.NONE
        self.injury_days_remaining = 0
        self.fatigue = 0
        self.motivation = 50
    
    def is_injured(self) -> bool:
        """怪我をしているか"""
        return self.injury != InjuryType.NONE and self.injury_days_remaining > 0
    
    def can_play(self) -> bool:
        """試合に出場できるか"""
        return not self.is_injured() and self.fatigue < 80
    
    def update_condition(self):
        """調子を更新"""
        # モチベーションと疲労度から調子を決定
        score = self.motivation - self.fatigue
        
        if score >= 70:
            self.condition = PlayerCondition.EXCELLENT
        elif score >= 40:
            self.condition = PlayerCondition.GOOD
        elif score >= 10:
            self.condition = PlayerCondition.NORMAL
        elif score >= -20:
            self.condition = PlayerCondition.POOR
        else:
            self.condition = PlayerCondition.TERRIBLE
    
    def recover_injury(self, days: int = 1):
        """怪我から回復"""
        if self.is_injured():
            self.injury_days_remaining = max(0, self.injury_days_remaining - days)
            if self.injury_days_remaining == 0:
                self.injury = InjuryType.NONE
    
    def add_fatigue(self, amount: int):
        """疲労を追加"""
        self.fatigue = min(100, self.fatigue + amount)
    
    def reduce_fatigue(self, amount: int):
        """疲労を軽減"""
        self.fatigue = max(0, self.fatigue - amount)
    
    def change_motivation(self, amount: int):
        """モチベーションを変更"""
        self.motivation = max(0, min(100, self.motivation + amount))


class PlayerDevelopment:
    """選手育成システム"""
    
    @staticmethod
    def train_player(player, training_type: TrainingType) -> dict:
        """選手を練習させる"""
        result = {
            "success": False,
            "stat_gains": {},
            "injury_occurred": False,
            "injury_type": InjuryType.NONE,
            "message": ""
        }
        
        # 疲労チェック
        if player.status.fatigue > 80:
            result["message"] = "疲労が溜まりすぎているため、練習を中止しました"
            return result
        
        # 怪我のリスク計算
        injury_risk = 0.02 + (player.status.fatigue * 0.0005)
        if random.random() < injury_risk:
            # 怪我発生
            injury_types = [InjuryType.MINOR, InjuryType.MODERATE, InjuryType.SERIOUS]
            weights = [0.6, 0.3, 0.1]
            player.status.injury = random.choices(injury_types, weights=weights)[0]
            player.status.injury_days_remaining = player.status.injury.recovery_days
            
            result["injury_occurred"] = True
            result["injury_type"] = player.status.injury
            result["message"] = f"練習中に{player.status.injury.display_name}を負いました"
            return result
        
        # 練習による能力上昇
        success_rate = 0.6 + (player.growth.potential * 0.04)
        if random.random() < success_rate:
            result["success"] = True
            
            if training_type == TrainingType.BATTING:
                gain = random.randint(1, 3)
                player.stats.contact = min(20, player.stats.contact + gain)
                result["stat_gains"]["ミート力"] = gain
            
            elif training_type == TrainingType.POWER:
                gain = random.randint(1, 3)
                player.stats.power = min(20, player.stats.power + gain)
                result["stat_gains"]["パワー"] = gain
            
            elif training_type == TrainingType.RUNNING:
                gain = random.randint(1, 3)
                player.stats.run = min(20, player.stats.run + gain)
                result["stat_gains"]["走力"] = gain
            
            elif training_type == TrainingType.FIELDING:
                gain = random.randint(1, 3)
                player.stats.fielding = min(20, player.stats.fielding + gain)
                result["stat_gains"]["守備力"] = gain
            
            elif training_type == TrainingType.PITCHING:
                gain = random.randint(1, 3)
                player.stats.speed = min(20, player.stats.speed + gain)
                result["stat_gains"]["球速"] = gain
            
            elif training_type == TrainingType.STAMINA:
                gain = random.randint(1, 3)
                player.stats.stamina = min(20, player.stats.stamina + gain)
                result["stat_gains"]["スタミナ"] = gain
            
            elif training_type == TrainingType.CONTROL:
                gain = random.randint(1, 3)
                player.stats.control = min(20, player.stats.control + gain)
                result["stat_gains"]["制球力"] = gain
            
            elif training_type == TrainingType.MENTAL:
                player.status.change_motivation(random.randint(5, 15))
                result["message"] = "メンタルが強化されました"
            
            elif training_type == TrainingType.REST:
                player.status.reduce_fatigue(30)
                player.status.change_motivation(10)
                result["message"] = "十分な休養をとりました"
            
            if result["stat_gains"]:
                gains_text = ", ".join([f"{k}+{v}" for k, v in result["stat_gains"].items()])
                result["message"] = f"練習成功！ {gains_text}"
        else:
            result["message"] = "練習の効果がありませんでした"
        
        # 疲労度上昇
        if training_type != TrainingType.REST:
            player.status.add_fatigue(random.randint(10, 20))
        
        # 調子を更新
        player.status.update_condition()
        
        return result
    
    @staticmethod
    def age_player(player):
        """選手を年齢成長させる"""
        player.age += 1
        
        # ピーク前は成長
        if player.age < player.growth.peak_age:
            growth_amount = int(player.growth.growth_rate * 2)
            
            # ランダムに能力を成長
            if player.position.value == "投手":
                stats = ['speed', 'control', 'stamina']
            else:
                stats = ['contact', 'power', 'run', 'fielding']
            
            for _ in range(growth_amount):
                stat = random.choice(stats)
                current = getattr(player.stats, stat)
                if current < 20:
                    setattr(player.stats, stat, current + 1)
        
        # ピーク後は衰退
        elif player.age > player.growth.peak_age + 2:
            decline_amount = int(player.growth.decline_rate * 2)
            
            if player.position.value == "投手":
                stats = ['speed', 'control', 'stamina']
            else:
                stats = ['contact', 'power', 'run', 'fielding']
            
            for _ in range(decline_amount):
                stat = random.choice(stats)
                current = getattr(player.stats, stat)
                if current > 1:
                    setattr(player.stats, stat, current - 1)
    
    @staticmethod
    def daily_recovery(player):
        """日次回復処理"""
        # 怪我の回復
        player.status.recover_injury(1)
        
        # 疲労の自然回復
        if not player.status.is_injured():
            player.status.reduce_fatigue(5)
        
        # モチベーションの変動
        motivation_change = random.randint(-3, 3)
        player.status.change_motivation(motivation_change)
        
        # 調子の更新
        player.status.update_condition()
