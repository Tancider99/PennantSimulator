# -*- coding: utf-8 -*-
"""
選手生成ユーティリティ
"""
import random
from typing import Optional, List
from models import Player, PlayerStats, Position, PitchType, PlayerStatus, DraftProspect
from constants import JAPANESE_SURNAMES, JAPANESE_FIRSTNAMES, FOREIGN_SURNAMES, FOREIGN_FIRSTNAMES


def generate_japanese_name() -> str:
    """日本人選手名を生成"""
    return random.choice(JAPANESE_SURNAMES) + random.choice(JAPANESE_FIRSTNAMES)


def generate_foreign_name() -> str:
    """外国人選手名を生成"""
    return f"{random.choice(FOREIGN_FIRSTNAMES)} {random.choice(FOREIGN_SURNAMES)}"


def generate_high_school_name() -> str:
    """高校名を生成"""
    prefectures = ["北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島", "茨城", "栃木", "群馬",
                   "埼玉", "千葉", "東京", "神奈川", "新潟", "富山", "石川", "福井", "山梨", "長野",
                   "岐阜", "静岡", "愛知", "三重", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山",
                   "鳥取", "島根", "岡山", "広島", "山口", "徳島", "香川", "愛媛", "高知", "福岡",
                   "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"]
    school_types = ["高校", "学園", "学院", "高等学校"]
    school_names = ["第一", "第二", "中央", "東", "西", "南", "北", "商業", "工業", "農業"]
    
    return random.choice(prefectures) + random.choice(school_names) + random.choice(school_types)


def create_random_player(position: Position, 
                        pitch_type: Optional[PitchType] = None, 
                        status: PlayerStatus = PlayerStatus.ACTIVE, 
                        number: int = 0,
                        is_foreign: bool = False,
                        age: int = None) -> Player:
    """ランダムな選手を生成"""
    name = generate_foreign_name() if is_foreign else generate_japanese_name()
    if age is None:
        age = random.randint(18, 38) if not is_foreign else random.randint(22, 35)
    
    stats = PlayerStats()
    
    # ステータスによって能力値の範囲を調整
    if status == PlayerStatus.ACTIVE:
        if is_foreign:
            min_stat, max_stat = 10, 16  # 外国人選手は強め
        else:
            min_stat, max_stat = 7, 15
    else:
        min_stat, max_stat = 5, 12
    
    if position == Position.PITCHER:
        stats.speed = random.randint(min_stat, max_stat)
        stats.control = random.randint(min_stat, max_stat)
        stats.stamina = random.randint(min_stat, max_stat)
        stats.breaking = random.randint(min_stat, max_stat)
        stats.mental = random.randint(min_stat, max_stat)
        
        # 変化球を追加（投手のみ）
        stats.breaking_balls = generate_breaking_balls(pitch_type, stats.breaking)
        if stats.breaking_balls:
            stats.best_pitch = random.choice(stats.breaking_balls)
    else:
        stats.contact = random.randint(min_stat, max_stat)
        stats.power = random.randint(min_stat-1, max_stat)
        stats.run = random.randint(min_stat-1, max_stat)
        stats.arm = random.randint(min_stat-2, max_stat-1)
        stats.fielding = random.randint(min_stat-1, max_stat-1)
        stats.mental = random.randint(min_stat-1, max_stat)
        stats.clutch = random.randint(min_stat-2, max_stat)
        stats.consistency = random.randint(min_stat-1, max_stat)
    
    # 年俸計算（能力値ベース）
    if position == Position.PITCHER:
        overall = stats.overall_pitching()
    else:
        overall = stats.overall_batting()
    
    base_salary = 10000000  # 1000万円
    salary = int(base_salary * (1 + overall / 10) * (1 + age / 100))
    
    player = Player(
        name=name, 
        position=position, 
        pitch_type=pitch_type, 
        stats=stats, 
        age=age, 
        status=status, 
        uniform_number=number,
        is_foreign=is_foreign,
        salary=salary
    )
    
    # 特殊能力をランダム付与
    assign_random_abilities(player)
    
    return player


# 変化球リスト
BREAKING_BALL_TYPES = {
    "standard": ["スライダー", "カーブ", "フォーク", "チェンジアップ"],
    "advanced": ["カットボール", "ツーシーム", "シンカー", "スプリット"],
    "rare": ["ナックル", "スクリュー", "パーム", "Vスライダー", "縦スライダー", "高速スライダー"],
    "japanese": ["シュート", "縦カーブ", "Hシンカー"]
}


def generate_breaking_balls(pitch_type: Optional[PitchType], breaking_stat: int) -> List[str]:
    """変化球をランダム生成"""
    balls = []
    
    # 基本変化球（1-2種類）
    num_standard = random.randint(1, 2)
    balls.extend(random.sample(BREAKING_BALL_TYPES["standard"], min(num_standard, len(BREAKING_BALL_TYPES["standard"]))))
    
    # 変化球能力値が高いほど追加球種
    if breaking_stat >= 10:
        num_advanced = random.randint(0, 2)
        balls.extend(random.sample(BREAKING_BALL_TYPES["advanced"], min(num_advanced, len(BREAKING_BALL_TYPES["advanced"]))))
    
    if breaking_stat >= 13:
        if random.random() < 0.3:
            balls.append(random.choice(BREAKING_BALL_TYPES["rare"]))
    
    if breaking_stat >= 8 and random.random() < 0.4:
        balls.append(random.choice(BREAKING_BALL_TYPES["japanese"]))
    
    return list(set(balls))  # 重複削除


def assign_random_abilities(player: Player):
    """特殊能力をランダム付与"""
    from special_abilities import SpecialAbility, SpecialAbilityType
    
    if player.special_abilities is None:
        from special_abilities import PlayerAbilities
        player.special_abilities = PlayerAbilities()
    
    # 能力値ベースで特殊能力を付与
    abilities = player.special_abilities
    
    if player.position == Position.PITCHER:
        # 投手用能力
        if player.stats.control >= 13 and random.random() < 0.4:
            abilities.add_ability(SpecialAbility.CONTROL)
        if player.stats.speed >= 14 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.STRIKEOUT)
        if player.stats.stamina >= 13 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.RECOVERY)
        if player.stats.breaking >= 13 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.HEAVY_BALL)
        if player.pitch_type == PitchType.CLOSER and random.random() < 0.5:
            abilities.add_ability(SpecialAbility.CLOSER_ABILITY)
        
        # マイナス能力
        if player.stats.control <= 7 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.WILD_PITCH)
        if player.stats.stamina <= 7 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.POOR_STAMINA)
    else:
        # 野手用能力
        if player.stats.contact >= 13 and random.random() < 0.4:
            abilities.add_ability(SpecialAbility.CONTACT_HITTER)
        if player.stats.power >= 14 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.POWER_HITTER)
        if player.stats.clutch >= 13 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.CLUTCH)
        if player.stats.run >= 14 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.SPEED_STAR)
        if player.stats.fielding >= 13 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.GOLD_GLOVE)
        if player.stats.arm >= 13 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.STRONG_ARM)
        
        # マイナス能力
        if player.stats.contact <= 6 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.POOR_CONTACT)
        if player.stats.power <= 6 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.POOR_POWER)


def create_draft_prospect(position: Position, 
                         pitch_type: Optional[PitchType] = None,
                         base_potential: int = 5) -> DraftProspect:
    """ドラフト候補選手を生成"""
    name = generate_japanese_name()
    age = random.randint(18, 22)
    high_school = generate_high_school_name()
    potential = max(1, min(10, base_potential + random.randint(-2, 2)))
    
    stats = PlayerStats()
    
    # ポテンシャルベースで能力値を設定（まだ荒削り）
    base_min = max(3, potential - 2)
    base_max = min(13, potential + 3)
    
    if position == Position.PITCHER:
        stats.speed = random.randint(base_min, base_max)
        stats.control = random.randint(base_min, base_max)
        stats.stamina = random.randint(base_min, base_max)
        stats.breaking = random.randint(base_min, base_max)
    else:
        stats.contact = random.randint(base_min, base_max)
        stats.power = random.randint(base_min, base_max)
        stats.run = random.randint(base_min, base_max)
        stats.arm = random.randint(base_min-1, base_max)
        stats.fielding = random.randint(base_min, base_max)
    
    return DraftProspect(
        name=name,
        position=position,
        pitch_type=pitch_type,
        stats=stats,
        age=age,
        high_school=high_school,
        potential=potential
    )


def create_foreign_free_agent(position: Position, 
                              pitch_type: Optional[PitchType] = None) -> Player:
    """外国人FA選手を生成"""
    player = create_random_player(
        position=position,
        pitch_type=pitch_type,
        status=PlayerStatus.ACTIVE,
        number=0,
        is_foreign=True
    )
    player.salary = random.randint(50000000, 300000000)  # 5000万〜3億円
    return player
