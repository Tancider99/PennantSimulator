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
    
    # ステータスによって能力値の範囲を調整（1-99スケール）
    # プロ選手の平均はDランク（50前後）、一流はB-Aランク（70-80）、トップはSランク（90+）
    if status == PlayerStatus.ACTIVE:
        if is_foreign:
            # 外国人選手は一定以上の能力が期待される（平均C-Bランク）
            min_stat, max_stat = 55, 85
        else:
            # 一般的な支配下選手：平均Dランク（40-65が多い、稀に70+）
            min_stat, max_stat = 40, 75
    else:
        # 育成選手：伸びしろあるが現時点では平均E-Dランク
        min_stat, max_stat = 30, 55
    
    if position == Position.PITCHER:
        # 投手の投球能力
        stats.speed = random.randint(min_stat, max_stat)
        stats.control = random.randint(min_stat, max_stat)
        stats.stamina = random.randint(min_stat, max_stat)
        stats.breaking = random.randint(min_stat, max_stat)
        stats.mental = random.randint(max(1, min_stat - 5), max_stat - 5)
        
        # 投手の打撃能力は低い（G-Fランク：10-35程度）
        stats.contact = random.randint(10, 30)
        stats.power = random.randint(5, 25)
        stats.run = random.randint(20, 45)  # 走力は多少あり
        stats.arm = random.randint(10, 30)  # 野手としての肩は低い
        stats.fielding = random.randint(25, 50)  # 投手守備は一応
        stats.catching = random.randint(10, 25)
        stats.trajectory = random.randint(1, 2)  # グラウンダー〜ライナー
        
        # 変化球を追加（投手のみ）- 能力値を1-99スケールで判定
        stats.breaking_balls = generate_breaking_balls(pitch_type, stats.breaking)
        if stats.breaking_balls:
            stats.best_pitch = random.choice(stats.breaking_balls)
    else:
        # 野手の打撃能力
        stats.contact = random.randint(min_stat, max_stat)
        stats.power = random.randint(max(1, min_stat - 5), max_stat)
        stats.run = random.randint(max(1, min_stat - 5), max_stat)
        stats.arm = random.randint(max(1, min_stat - 10), max_stat - 5)
        stats.fielding = random.randint(max(1, min_stat - 5), max_stat - 5)
        stats.catching = random.randint(max(1, min_stat - 5), max_stat - 5)
        stats.mental = random.randint(max(1, min_stat - 10), max_stat - 5)
        stats.clutch = random.randint(max(1, min_stat - 10), max_stat - 5)
        stats.consistency = random.randint(max(1, min_stat - 10), max_stat - 5)
        
        # 野手の投球能力は不要（設定しない - デフォルト値のまま）
        stats.speed = 1  # 球速は野手には不要
        stats.control = 1
        stats.stamina = 1
        stats.breaking = 1
        
        # 弾道（1-4、パワーに応じて）
        if stats.power >= 70:
            stats.trajectory = random.randint(3, 4)
        elif stats.power >= 50:
            stats.trajectory = random.randint(2, 3)
        else:
            stats.trajectory = random.randint(1, 2)
    
    # 年俸計算（能力値ベース）
    if position == Position.PITCHER:
        overall = stats.overall_pitching()
    else:
        overall = stats.overall_batting()
    
    base_salary = 10000000  # 1000万円
    salary = int(base_salary * (1 + overall / 10) * (1 + age / 100))
    
    # 投手適性値の設定（投手のみ）
    starter_apt = 50
    middle_apt = 50
    closer_apt = 50
    
    if position == Position.PITCHER:
        if pitch_type == PitchType.STARTER:
            starter_apt = random.randint(70, 100)
            middle_apt = random.randint(30, 60)
            closer_apt = random.randint(20, 50)
        elif pitch_type == PitchType.RELIEVER:
            starter_apt = random.randint(20, 50)
            middle_apt = random.randint(70, 100)
            closer_apt = random.randint(40, 70)
        elif pitch_type == PitchType.CLOSER:
            starter_apt = random.randint(10, 40)
            middle_apt = random.randint(50, 80)
            closer_apt = random.randint(80, 100)
        else:
            # pitch_typeが未設定の場合はランダム
            starter_apt = random.randint(30, 80)
            middle_apt = random.randint(30, 80)
            closer_apt = random.randint(30, 80)
    
    player = Player(
        name=name, 
        position=position, 
        pitch_type=pitch_type, 
        stats=stats, 
        age=age, 
        status=status, 
        uniform_number=number,
        is_foreign=is_foreign,
        salary=salary,
        starter_aptitude=starter_apt,
        middle_aptitude=middle_apt,
        closer_aptitude=closer_apt
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
    """変化球をランダム生成（能力値は1-99スケール）"""
    balls = []
    
    # 基本変化球（1-2種類）
    num_standard = random.randint(1, 2)
    balls.extend(random.sample(BREAKING_BALL_TYPES["standard"], min(num_standard, len(BREAKING_BALL_TYPES["standard"]))))
    
    # 変化球能力値が高いほど追加球種（1-99スケール）
    if breaking_stat >= 50:
        num_advanced = random.randint(0, 2)
        balls.extend(random.sample(BREAKING_BALL_TYPES["advanced"], min(num_advanced, len(BREAKING_BALL_TYPES["advanced"]))))
    
    if breaking_stat >= 65:
        if random.random() < 0.3:
            balls.append(random.choice(BREAKING_BALL_TYPES["rare"]))
    
    if breaking_stat >= 40 and random.random() < 0.4:
        balls.append(random.choice(BREAKING_BALL_TYPES["japanese"]))
    
    return list(set(balls))  # 重複削除


def assign_random_abilities(player: Player):
    """特殊能力をランダム付与（1-99スケール対応）"""
    from special_abilities import SpecialAbility, SpecialAbilityType
    
    if player.special_abilities is None:
        from special_abilities import PlayerAbilities
        player.special_abilities = PlayerAbilities()
    
    # 能力値ベースで特殊能力を付与（1-99スケール）
    abilities = player.special_abilities
    
    if player.position == Position.PITCHER:
        # 投手用能力
        if player.stats.control >= 65 and random.random() < 0.4:
            abilities.add_ability(SpecialAbility.CONTROL)
        if player.stats.speed >= 70 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.STRIKEOUT)
        if player.stats.stamina >= 65 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.RECOVERY)
        if player.stats.breaking >= 65 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.HEAVY_BALL)
        if player.pitch_type == PitchType.CLOSER and random.random() < 0.5:
            abilities.add_ability(SpecialAbility.CLOSER_ABILITY)
        
        # マイナス能力
        if player.stats.control <= 35 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.WILD_PITCH)
        if player.stats.stamina <= 35 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.POOR_STAMINA)
    else:
        # 野手用能力
        if player.stats.contact >= 65 and random.random() < 0.4:
            abilities.add_ability(SpecialAbility.CONTACT_HITTER)
        if player.stats.power >= 70 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.POWER_HITTER)
        if player.stats.clutch >= 65 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.CLUTCH)
        if player.stats.run >= 70 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.SPEED_STAR)
        if player.stats.fielding >= 65 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.GOLD_GLOVE)
        if player.stats.arm >= 65 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.STRONG_ARM)
        
        # マイナス能力
        if player.stats.contact <= 30 and random.random() < 0.3:
            abilities.add_ability(SpecialAbility.POOR_CONTACT)
        if player.stats.power <= 30 and random.random() < 0.3:
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
    
    # ポテンシャルベースで能力値を設定（1-99スケール）
    # ドラフト入団時は低めの能力値、成長で伸びる
    # potential 1-10 → 能力値範囲調整
    base_min = max(15, potential * 4 - 10)  # potential 5なら min=10
    base_max = min(60, potential * 6 + 5)   # potential 5なら max=35
    
    if position == Position.PITCHER:
        stats.speed = random.randint(base_min, base_max)
        stats.control = random.randint(base_min, base_max)
        stats.stamina = random.randint(base_min, base_max)
        stats.breaking = random.randint(base_min, base_max)
    else:
        stats.contact = random.randint(base_min, base_max)
        stats.power = random.randint(base_min, base_max)
        stats.run = random.randint(base_min, base_max)
        stats.arm = random.randint(max(1, base_min-5), base_max)
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
