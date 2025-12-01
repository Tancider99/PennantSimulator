# -*- coding: utf-8 -*-
"""
特殊能力システム - パワプロ風の特殊能力を実装
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class SpecialAbilityType(Enum):
    """特殊能力のタイプ"""
    BATTING = "打撃系"
    PITCHING = "投球系"
    FIELDING = "守備系"
    RUNNING = "走塁系"
    MENTAL = "精神系"


class SpecialAbility(Enum):
    """特殊能力"""
    # 打撃系 - 青能力（プラス）
    CONTACT_HITTER = ("アベレージヒッター", SpecialAbilityType.BATTING, 1, "ミート力UP")
    POWER_HITTER = ("パワーヒッター", SpecialAbilityType.BATTING, 1, "パワーUP")
    CLUTCH = ("チャンス", SpecialAbilityType.BATTING, 1, "得点圏打率UP")
    AGAINST_LEFTY = ("対左投手", SpecialAbilityType.BATTING, 1, "左投手に強い")
    AGAINST_RIGHTY = ("対右投手", SpecialAbilityType.BATTING, 1, "右投手に強い")
    PULL_HITTER = ("プルヒッター", SpecialAbilityType.BATTING, 1, "引っ張り方向に強い")
    SPRAY_HITTER = ("広角打法", SpecialAbilityType.BATTING, 1, "全方向に打ち分け")
    LINE_DRIVE = ("ライナー", SpecialAbilityType.BATTING, 1, "ライナー性の打球")
    FIRST_PITCH = ("初球○", SpecialAbilityType.BATTING, 1, "初球に強い")
    
    # 打撃系 - 赤能力（マイナス）
    POOR_CONTACT = ("三振", SpecialAbilityType.BATTING, -1, "ミート力DOWN")
    POOR_POWER = ("非力", SpecialAbilityType.BATTING, -1, "パワーDOWN")
    WEAK_CLUTCH = ("チャンス×", SpecialAbilityType.BATTING, -1, "得点圏打率DOWN")
    
    # 投球系 - 青能力
    STRIKEOUT = ("奪三振", SpecialAbilityType.PITCHING, 1, "三振を奪いやすい")
    CONTROL = ("制球力", SpecialAbilityType.PITCHING, 1, "制球力UP")
    QUICK = ("クイック", SpecialAbilityType.PITCHING, 1, "牽制◎")
    RECOVERY = ("回復", SpecialAbilityType.PITCHING, 1, "スタミナ回復早い")
    HEAVY_BALL = ("重い球", SpecialAbilityType.PITCHING, 1, "打たれにくい")
    PINCH = ("対ピンチ", SpecialAbilityType.PITCHING, 1, "ピンチに強い")
    CLUTCH_PITCHER = ("打たれ強さ", SpecialAbilityType.PITCHING, 1, "連打されにくい")
    CLOSER_ABILITY = ("抑え◎", SpecialAbilityType.PITCHING, 1, "抑え適性")
    
    # 投球系 - 赤能力
    WILD_PITCH = ("ノーコン", SpecialAbilityType.PITCHING, -1, "制球力DOWN")
    POOR_STAMINA = ("低スタミナ", SpecialAbilityType.PITCHING, -1, "スタミナDOWN")
    WEAK_PINCH = ("対ピンチ×", SpecialAbilityType.PITCHING, -1, "ピンチに弱い")
    
    # 守備系 - 青能力
    STRONG_ARM = ("強肩", SpecialAbilityType.FIELDING, 1, "送球◎")
    GOLD_GLOVE = ("守備職人", SpecialAbilityType.FIELDING, 1, "守備範囲UP")
    QUICK_CATCH = ("捕球◎", SpecialAbilityType.FIELDING, 1, "捕球能力UP")
    
    # 守備系 - 赤能力
    WEAK_ARM = ("弱肩", SpecialAbilityType.FIELDING, -1, "送球×")
    ERROR_PRONE = ("エラー", SpecialAbilityType.FIELDING, -1, "エラーしやすい")
    
    # 走塁系 - 青能力
    SPEED_STAR = ("盗塁", SpecialAbilityType.RUNNING, 1, "盗塁◎")
    BASE_RUNNING = ("走塁", SpecialAbilityType.RUNNING, 1, "走塁能力UP")
    
    # 走塁系 - 赤能力
    SLOW_RUNNER = ("走塁×", SpecialAbilityType.RUNNING, -1, "走塁DOWN")
    
    # 精神系 - 青能力
    HOT_HITTER = ("ハイボールヒッター", SpecialAbilityType.MENTAL, 1, "高めに強い")
    LOW_HITTER = ("ローボールヒッター", SpecialAbilityType.MENTAL, 1, "低めに強い")
    PATIENT = ("選球眼", SpecialAbilityType.MENTAL, 1, "四球を選べる")
    AGGRESSIVE = ("積極打法", SpecialAbilityType.MENTAL, 1, "初球から積極的")
    
    def __init__(self, display_name: str, ability_type: SpecialAbilityType, effect_value: int, description: str):
        self.display_name = display_name
        self.ability_type = ability_type
        self.effect_value = effect_value  # valueから名前を変更
        self.description = description
    
    def is_positive(self) -> bool:
        """プラス能力かどうか"""
        return self.value > 0
    
    def is_negative(self) -> bool:
        """マイナス能力かどうか"""
        return self.value < 0


@dataclass
class PlayerAbilities:
    """選手の特殊能力セット"""
    abilities: List[SpecialAbility]
    
    def __init__(self):
        self.abilities = []
    
    def add_ability(self, ability: SpecialAbility):
        """特殊能力を追加"""
        if ability not in self.abilities:
            self.abilities.append(ability)
    
    def remove_ability(self, ability: SpecialAbility):
        """特殊能力を削除"""
        if ability in self.abilities:
            self.abilities.remove(ability)
    
    def has_ability(self, ability: SpecialAbility) -> bool:
        """特殊能力を持っているか"""
        return ability in self.abilities
    
    def get_abilities_by_type(self, ability_type: SpecialAbilityType) -> List[SpecialAbility]:
        """タイプ別に特殊能力を取得"""
        return [a for a in self.abilities if a.ability_type == ability_type]
    
    def get_positive_abilities(self) -> List[SpecialAbility]:
        """プラス能力を取得"""
        return [a for a in self.abilities if a.is_positive()]
    
    def get_negative_abilities(self) -> List[SpecialAbility]:
        """マイナス能力を取得"""
        return [a for a in self.abilities if a.is_negative()]
    
    def count_abilities(self) -> int:
        """特殊能力の数"""
        return len(self.abilities)
    
    def get_ability_bonus(self, stat_name: str) -> int:
        """能力値ボーナスを計算"""
        bonus = 0
        
        # 打撃系
        if stat_name == "contact":
            if self.has_ability(SpecialAbility.CONTACT_HITTER):
                bonus += 2
            if self.has_ability(SpecialAbility.POOR_CONTACT):
                bonus -= 2
        
        elif stat_name == "power":
            if self.has_ability(SpecialAbility.POWER_HITTER):
                bonus += 2
            if self.has_ability(SpecialAbility.POOR_POWER):
                bonus -= 2
        
        # 投球系
        elif stat_name == "control":
            if self.has_ability(SpecialAbility.CONTROL):
                bonus += 2
            if self.has_ability(SpecialAbility.WILD_PITCH):
                bonus -= 3
        
        elif stat_name == "stamina":
            if self.has_ability(SpecialAbility.RECOVERY):
                bonus += 2
            if self.has_ability(SpecialAbility.POOR_STAMINA):
                bonus -= 2
        
        # 守備系
        elif stat_name == "fielding":
            if self.has_ability(SpecialAbility.GOLD_GLOVE):
                bonus += 2
            if self.has_ability(SpecialAbility.ERROR_PRONE):
                bonus -= 2
        
        # 走塁系
        elif stat_name == "run":
            if self.has_ability(SpecialAbility.SPEED_STAR):
                bonus += 2
            if self.has_ability(SpecialAbility.SLOW_RUNNER):
                bonus -= 2
        
        return bonus
    
    def get_display_string(self) -> str:
        """特殊能力を表示用文字列に変換"""
        if not self.abilities:
            return "なし"
        
        positive = []
        negative = []
        
        for ability in self.abilities:
            if ability.effect_value > 0:
                positive.append(f"🔵{ability.display_name}")
            else:
                negative.append(f"🔴{ability.display_name}")
        
        result = ""
        if positive:
            result += " ".join(positive)
        if negative:
            if result:
                result += " "
            result += " ".join(negative)
        
        return result
    
    def get_abilities_for_situation(self, situation: str) -> list:
        """特定状況で発動する能力を取得"""
        relevant = []
        
        if situation == "clutch":
            if self.has_ability(SpecialAbility.CLUTCH):
                relevant.append(SpecialAbility.CLUTCH)
            if self.has_ability(SpecialAbility.WEAK_CLUTCH):
                relevant.append(SpecialAbility.WEAK_CLUTCH)
        
        elif situation == "pinch":
            if self.has_ability(SpecialAbility.PINCH):
                relevant.append(SpecialAbility.PINCH)
            if self.has_ability(SpecialAbility.WEAK_PINCH):
                relevant.append(SpecialAbility.WEAK_PINCH)
        
        elif situation == "vs_lefty":
            if self.has_ability(SpecialAbility.AGAINST_LEFTY):
                relevant.append(SpecialAbility.AGAINST_LEFTY)
        
        elif situation == "vs_righty":
            if self.has_ability(SpecialAbility.AGAINST_RIGHTY):
                relevant.append(SpecialAbility.AGAINST_RIGHTY)
        
        elif situation == "steal":
            if self.has_ability(SpecialAbility.SPEED_STAR):
                relevant.append(SpecialAbility.SPEED_STAR)
        
        return relevant


# 追加の特殊能力（超レア）
class SuperAbility(Enum):
    """超レア特殊能力"""
    LEGEND = ("レジェンド", "全能力+3", 3.0)
    SUPER_STAR = ("スーパースター", "注目度大幅UP", 2.5)
    IRON_MAN = ("鉄人", "怪我しにくい", 2.0)
    CLUTCH_MASTER = ("勝負師", "勝負所で+20%", 2.0)
    NATURAL_TALENT = ("天才", "成長率+50%", 2.5)
    
    def __init__(self, display_name: str, description: str, multiplier: float):
        self.display_name = display_name
        self.description = description
        self.multiplier = multiplier


def generate_random_abilities(position_type: str, num_abilities: int = 3) -> PlayerAbilities:
    """ランダムに特殊能力を生成"""
    import random
    
    abilities = PlayerAbilities()
    
    if position_type == "PITCHER":
        # 投手用
        positive_pitching = [
            SpecialAbility.STRIKEOUT,
            SpecialAbility.CONTROL,
            SpecialAbility.QUICK,
            SpecialAbility.RECOVERY,
            SpecialAbility.HEAVY_BALL,
            SpecialAbility.PINCH,
            SpecialAbility.CLUTCH_PITCHER,
        ]
        
        negative_pitching = [
            SpecialAbility.WILD_PITCH,
            SpecialAbility.POOR_STAMINA,
            SpecialAbility.WEAK_PINCH,
        ]
        
        # 70%の確率でプラス能力、30%でマイナス能力
        for _ in range(num_abilities):
            if random.random() < 0.7:
                ability = random.choice(positive_pitching)
            else:
                ability = random.choice(negative_pitching)
            abilities.add_ability(ability)
    
    else:
        # 野手用
        positive_batting = [
            SpecialAbility.CONTACT_HITTER,
            SpecialAbility.POWER_HITTER,
            SpecialAbility.CLUTCH,
            SpecialAbility.AGAINST_LEFTY,
            SpecialAbility.AGAINST_RIGHTY,
            SpecialAbility.SPRAY_HITTER,
        ]
        
        positive_fielding = [
            SpecialAbility.STRONG_ARM,
            SpecialAbility.GOLD_GLOVE,
            SpecialAbility.QUICK_CATCH,
        ]
        
        positive_running = [
            SpecialAbility.SPEED_STAR,
            SpecialAbility.BASE_RUNNING,
        ]
        
        negative_abilities = [
            SpecialAbility.POOR_CONTACT,
            SpecialAbility.POOR_POWER,
            SpecialAbility.WEAK_ARM,
            SpecialAbility.ERROR_PRONE,
            SpecialAbility.SLOW_RUNNER,
        ]
        
        all_positive = positive_batting + positive_fielding + positive_running
        
        for _ in range(num_abilities):
            if random.random() < 0.75:
                ability = random.choice(all_positive)
            else:
                ability = random.choice(negative_abilities)
            abilities.add_ability(ability)
    
    return abilities


def get_ability_description_detailed(ability: SpecialAbility) -> dict:
    """特殊能力の詳細情報を取得"""
    descriptions = {
        SpecialAbility.CONTACT_HITTER: {
            "effect": "ミート力+2",
            "trigger": "常時発動",
            "detail": "バットコントロールに優れ、安定してヒットを打てる"
        },
        SpecialAbility.POWER_HITTER: {
            "effect": "パワー+2",
            "trigger": "常時発動",
            "detail": "長打力があり、ホームランを打ちやすい"
        },
        SpecialAbility.CLUTCH: {
            "effect": "得点圏打率+15%",
            "trigger": "得点圏にランナーがいる時",
            "detail": "チャンスに強く、大事な場面で力を発揮する"
        },
        SpecialAbility.STRIKEOUT: {
            "effect": "奪三振率+8%",
            "trigger": "常時発動",
            "detail": "決め球の威力が高く、三振を奪いやすい"
        },
        SpecialAbility.CONTROL: {
            "effect": "制球力+2",
            "trigger": "常時発動",
            "detail": "コーナーワークが巧みで、四球が少ない"
        },
        SpecialAbility.PINCH: {
            "effect": "ピンチ時の能力+12%",
            "trigger": "ピンチ（得点圏にランナー）",
            "detail": "ピンチに強く、踏ん張れる精神力を持つ"
        },
        SpecialAbility.SPEED_STAR: {
            "effect": "盗塁成功率+15%",
            "trigger": "盗塁時",
            "detail": "俊足でスタートも良く、盗塁が得意"
        },
        SpecialAbility.GOLD_GLOVE: {
            "effect": "守備範囲+2",
            "trigger": "常時発動",
            "detail": "広い守備範囲と安定した捕球を誇る"
        },
    }
    
    return descriptions.get(ability, {
        "effect": ability.description,
        "trigger": "常時発動",
        "detail": ""
    })

