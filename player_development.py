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
    ARM = "肩力強化"
    PITCHING = "投球練習"
    STAMINA = "スタミナ強化"
    CONTROL = "制球練習"
    BREAKING = "変化球練習"
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
    """選手の成長データ（XPベース）

    - `potential` (1-10): 成長ポテンシャル（高いほど経験値で成長しやすい）
    - `xp` : 各能力に積算される経験値（辞書）
    - `peak_age`, `decline_rate`: 従来の年齢依存成長のために保持
    """

    def __init__(self, potential: int = 5):
        self.potential = max(1, min(10, int(potential)))
        # XP per stat stored as { stat_name: xp }
        self.xp = {}
        self.peak_age = random.randint(27, 32)
        self.decline_rate = max(0.1, 1.0 - (self.potential * 0.05))

    def xp_required_for(self, stat_value: int) -> int:
        """現在の能力値に対して次の+1に必要なXPを計算する。

        要求XPは能力値が高いほど増加し、ポテンシャルが高いほど小さくなる。
        シンプルな式を採用: base + stat * (factor / potential)
        """
        base = 10
        factor = 6.0
        required = int(base + stat_value * (factor / max(1, self.potential)))
        return max(5, required)

    def add_xp(self, player_stats, stat_key: str, amount: int) -> int:
        """指定能力にXPを追加し、必要XPに達した分を能力値に反映する。

        Args:
            player_stats: Player.stats オブジェクト（属性名でアクセスされる）
            stat_key: 追加対象の属性名（例: 'contact', 'speed'）
            amount: 付与するXP量（整数）

        Returns:
            int:  実際に上がったステータスの増分（0以上）
        """
        if amount <= 0:
            return 0
        cur_xp = self.xp.get(stat_key, 0) + int(amount)
        self.xp[stat_key] = cur_xp

        # 現在の能力値を取得（PlayerStats の属性名を期待）
        cur_val = getattr(player_stats, stat_key, None)
        if cur_val is None:
            # 無効なキー
            return 0

        gained = 0
        # ループして複数レベル上がる場合にも対応
        while True:
            req = self.xp_required_for(cur_val + gained)
            if self.xp[stat_key] >= req:
                # レベルアップ
                self.xp[stat_key] -= req
                gained += 1
            else:
                break

        if gained > 0:
            # 累積で能力値に反映
            new_val = cur_val + gained
            # PlayerStats 値は 1-99 スケールとして扱う
            setattr(player_stats, stat_key, min(99, max(1, int(new_val))))

        return gained


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
    def train_player(player, training_type: TrainingType, xp_multiplier: float = 1.0, guaranteed: bool = False) -> dict:
        """選手を練習させる
        
        Args:
            player: 練習する選手
            training_type: トレーニング種別
            xp_multiplier: XP獲得量の倍率（キャンプでは0.6、試合後は0.5など）
            guaranteed: Trueの場合、成功判定をスキップして確実に経験値を付与
        """
        result = {
            "success": False,
            "stat_gains": {},
            "injury_occurred": False,
            "injury_type": InjuryType.NONE,
            "message": ""
        }
        
        # 疲労チェック (育成用の player_status を参照)
        p_status = getattr(player, 'player_status', None)
        if p_status is None:
            # 互換性のため従来の status フィールドも許容
            p_status = getattr(player, 'status', None)

        # 休養以外のトレーニングは疲労80以上で中止（試合後の自動練習の場合は免除）
        if not guaranteed and training_type != TrainingType.REST and p_status is not None and getattr(p_status, 'fatigue', 0) > 80:
            result["message"] = "疲労が溜まりすぎているため、練習を中止しました"
            return result
        
        # 怪我のリスク計算（試合後の自動練習の場合は怪我リスクなし）
        if not guaranteed:
            injury_risk = 0.02 + (getattr(p_status, 'fatigue', 0) * 0.0005)
            if random.random() < injury_risk:
                # 怪我発生
                injury_types = [InjuryType.MINOR, InjuryType.MODERATE, InjuryType.SERIOUS]
                weights = [0.6, 0.3, 0.1]
                # 怪我情報は育成用の player_status に格納
                if p_status is not None:
                    p_status.injury = random.choices(injury_types, weights=weights)[0]
                    p_status.injury_days_remaining = p_status.injury.recovery_days
                    result["injury_occurred"] = True
                    result["injury_type"] = p_status.injury
                    result["message"] = f"練習中に{p_status.injury.display_name}を負いました"
                else:
                    # 互換性: もし player.status がデータを持つ場合はそちらを使う
                    getattr(player, 'status', None)
                    result["injury_occurred"] = True
                    result["injury_type"] = InjuryType.MODERATE
                    result["message"] = "練習中に怪我を負いました"
                return result
        
        # growthがない場合は初期化（セーブデータ互換性のため）
        if not hasattr(player, 'growth') or player.growth is None:
            potential = 5 + (player.stats.overall_batting() if player.position.name != 'PITCHER' else player.stats.overall_pitching()) // 20
            player.growth = PlayerGrowth(int(min(10, max(1, potential))))
        
        # 練習によるXP付与と成功率（guaranteedの場合は常に成功）
        success_rate = 0.6 + (player.growth.potential * 0.03)
        if guaranteed or random.random() < success_rate:
            result["success"] = True

            # トレーニング種別ごとに付与XP量と対象ステータスを定義
            if training_type == TrainingType.BATTING:
                target = 'contact'
                base_xp = random.randint(8, 18)
            elif training_type == TrainingType.POWER:
                target = 'power'
                base_xp = random.randint(8, 18)
            elif training_type == TrainingType.RUNNING:
                target = 'run'
                base_xp = random.randint(6, 14)
            elif training_type == TrainingType.FIELDING:
                target = 'fielding'
                base_xp = random.randint(6, 14)
            elif training_type == TrainingType.ARM:
                target = 'arm'
                base_xp = random.randint(6, 14)
            elif training_type == TrainingType.PITCHING:
                target = 'speed'
                base_xp = random.randint(8, 18)
            elif training_type == TrainingType.STAMINA:
                target = 'stamina'
                base_xp = random.randint(8, 18)
            elif training_type == TrainingType.CONTROL:
                target = 'control'
                base_xp = random.randint(8, 18)
            elif training_type == TrainingType.BREAKING:
                target = 'breaking'
                base_xp = random.randint(8, 18)
            elif training_type == TrainingType.REST:
                if p_status is not None:
                    p_status.reduce_fatigue(30)
                else:
                    if hasattr(player, 'status'):
                        if hasattr(player.status, 'reduce_fatigue'):
                            player.status.reduce_fatigue(30)
                result["message"] = "十分な休養をとりました"
                base_xp = 0
                target = None
            else:
                base_xp = 0
                target = None

            if target:
                # XP獲得量に倍率を適用
                xp_gain = int(base_xp * xp_multiplier)
                # XP付与と実際の上昇数を計算
                gained = player.growth.add_xp(player.stats, target, xp_gain)
                if gained > 0:
                    # マッピング名を日本語で返す（既存UIに合わせる）
                    name_map = {
                        'contact': 'ミート力', 'power': 'パワー', 'run': '走力', 'fielding': '守備力',
                        'speed': '球速', 'stamina': 'スタミナ', 'control': '制球力'
                    }
                    result["stat_gains"][name_map.get(target, target)] = gained
                    result["message"] = f"練習成功！ {name_map.get(target, target)}+{gained}"
                else:
                    result["message"] = "練習で経験値を獲得しましたが、能力上昇はありませんでした"
        else:
            result["message"] = "練習の効果がありませんでした"
        
        # 疲労度上昇
        if training_type != TrainingType.REST:
            if p_status is not None:
                p_status.add_fatigue(random.randint(10, 20))
            else:
                if hasattr(player, 'status') and hasattr(player.status, 'add_fatigue'):
                    player.status.add_fatigue(random.randint(10, 20))

        # 調子を更新
        if p_status is not None and hasattr(p_status, 'update_condition'):
            p_status.update_condition()
        else:
            if hasattr(player, 'status') and hasattr(player.status, 'update_condition'):
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
        p_status = getattr(player, 'player_status', None)
        if p_status is None:
            p_status = getattr(player, 'status', None)

        if p_status is not None:
            p_status.recover_injury(1)
            # 疲労の自然回復
            if not p_status.is_injured():
                p_status.reduce_fatigue(5)
            # モチベーションの変動
            motivation_change = random.randint(-3, 3)
            if hasattr(p_status, 'change_motivation'):
                p_status.change_motivation(motivation_change)
            # 調子の更新
            if hasattr(p_status, 'update_condition'):
                p_status.update_condition()
