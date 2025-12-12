# -*- coding: utf-8 -*-
"""
選手生成ユーティリティ（OOTPスタイル対応・外野3ポジション版）
"""
import random
from typing import Optional, List
from models import Player, PlayerStats, Position, PitchType, PlayerStatus, DraftProspect
from constants import JAPANESE_SURNAMES, JAPANESE_FIRSTNAMES, FOREIGN_SURNAMES, FOREIGN_FIRSTNAMES


def generate_japanese_name() -> str:
    return random.choice(JAPANESE_SURNAMES) + random.choice(JAPANESE_FIRSTNAMES)

def generate_foreign_name() -> str:
    return f"{random.choice(FOREIGN_FIRSTNAMES)} {random.choice(FOREIGN_SURNAMES)}"

def generate_high_school_name() -> str:
    prefs = ["北海", "東都", "なにわ", "西京", "南国"]
    types = ["高校", "学園", "実業", "工業", "学院"]
    return random.choice(prefs) + random.choice(types)

def create_random_player(position: Position,
                        pitch_type: Optional[PitchType] = None,
                        status: PlayerStatus = PlayerStatus.ACTIVE,
                        number: int = 0,
                        is_foreign: bool = False,
                        age: int = None) -> Player:
    """ランダムな選手を生成（通常用）"""
    name = generate_foreign_name() if is_foreign else generate_japanese_name()
    if age is None:
        age = random.randint(18, 38) if not is_foreign else random.randint(22, 35)

    stats = PlayerStats()

    def get_stat(mu=50, sigma=15, min_val=1, max_val=99):
        val = int(random.gauss(mu, sigma))
        return max(min_val, min(max_val, val))

    if position == Position.PITCHER:
        # --- 投手能力 ---
        stats.velocity = int(random.gauss(145, 7))
        stats.velocity = max(120, min(170, stats.velocity))

        stats.stuff = get_stat(50)
        stats.movement = get_stat(50)
        stats.control = get_stat(50)
        stats.stamina = get_stat(50)
        stats.hold_runners = get_stat(50)
        stats.gb_tendency = get_stat(50, 20, 1, 99)
        
        stats.vs_left_pitcher = get_stat(50)
        stats.vs_pinch = get_stat(50)
        stats.stability = get_stat(50)

        stats.set_defense_range(Position.PITCHER, get_stat(50))
        stats.arm = get_stat(50)
        stats.error = get_stat(50)
        stats.turn_dp = get_stat(50)

        stats.contact = get_stat(15, 7, 1, 40)
        stats.gap = get_stat(15, 7, 1, 40)
        stats.power = get_stat(15, 7, 1, 40)
        stats.eye = get_stat(15, 7, 1, 40)
        stats.avoid_k = get_stat(15, 7, 1, 40)
        stats.trajectory = random.randint(1, 2)

        stats.speed = get_stat(20, 7, 1, 60)
        stats.steal = get_stat(10, 5, 1, 40)
        stats.baserunning = get_stat(15, 7, 1, 60)

        balls = ["ストレート", "スライダー", "カーブ", "フォーク", "チェンジアップ", "カットボール", "シンカー", "ツーシーム"]
        num_pitches = random.randint(3, 6)
        selected_balls = random.sample(balls, num_pitches)
        stats.pitches = {ball: get_stat(50) for ball in selected_balls}
        if "ストレート" not in stats.pitches:
            stats.pitches["ストレート"] = get_stat()

    else:
        # --- 野手能力 ---
        stats.contact = get_stat(50)
        stats.gap = get_stat(50)
        stats.power = get_stat(50)
        stats.eye = get_stat(50)
        stats.avoid_k = get_stat(50)
        
        if stats.power > 70: stats.trajectory = random.choice([3, 4, 4])
        elif stats.power > 50: stats.trajectory = random.choice([2, 3, 3])
        else: stats.trajectory = random.choice([1, 2, 2])
        
        stats.vs_left_batter = get_stat(50)
        stats.chance = get_stat(50)

        stats.speed = get_stat(50)
        stats.steal = get_stat(50)
        stats.baserunning = get_stat(50)

        stats.bunt_sac = get_stat(50)
        stats.bunt_hit = get_stat(50)

        stats.arm = get_stat(50)
        stats.error = get_stat(50)
        stats.turn_dp = get_stat(50)

        if position == Position.CATCHER:
            stats.catcher_lead = get_stat(50)
            stats.set_defense_range(Position.CATCHER, get_stat(50))
        elif position == Position.FIRST:
            stats.set_defense_range(Position.FIRST, get_stat(50))
        elif position == Position.SECOND:
            stats.set_defense_range(Position.SECOND, get_stat(50))
        elif position == Position.THIRD:
            stats.set_defense_range(Position.THIRD, get_stat(50))
        elif position == Position.SHORTSTOP:
            stats.set_defense_range(Position.SHORTSTOP, get_stat(50))
        elif position in [Position.LEFT, Position.CENTER, Position.RIGHT]:
            stats.set_defense_range(position, get_stat(50))

        stats.velocity = 130
        stats.control = 50
        stats.stuff = 50
        stats.movement = 50
        stats.stamina = 50

    stats.durability = get_stat(50)
    stats.recovery = get_stat(50)
    stats.work_ethic = get_stat(50)
    stats.intelligence = get_stat(50)
    stats.mental = get_stat(50)

    if random.random() < 0.7: player_throws = "右"
    else: player_throws = "左"
    
    if random.random() < 0.6: player_bats = "右"
    elif random.random() < 0.85: player_bats = "左"
    else: player_bats = "両"
    
    if position == Position.PITCHER:
        rating = stats.overall_pitching()
    else:
        rating = stats.overall_batting(position)

    base = 500
    salary = int(base * (rating ** 1.5) / 100) * 10000

    player = Player(
        name=name, position=position, pitch_type=pitch_type, stats=stats,
        age=age, status=status, uniform_number=number, is_foreign=is_foreign, salary=salary,
        bats=player_bats, throws=player_throws
    )

    return player

def create_draft_prospect(position: Position, pitch_type: Optional[PitchType] = None, base_potential: int = 5) -> DraftProspect:
    """
    ドラフト候補専用の生成ロジック
    高校生: 総合180
    大学生: 総合220
    社会人: 総合240
    独立: 総合190~240 (年齢依存)
    """
    # 1. 年齢と出身区分の決定
    roll = random.random()
    if roll < 0.40: # 45% 高校生
        origin = "高校"
        age = random.randint(17, 18)
        target_total = 180
    elif roll < 0.66: # 30% 大学生
        origin = "大学"
        age = random.randint(21, 22)
        target_total = 220
    elif roll < 0.80: # 15% 社会人
        origin = "社会人"
        age = random.randint(23, 26)
        target_total = 240
    else: # 10% 独立
        origin = "独立リーグ"
        age = random.randint(19, 26)
        # 独立は年齢によってターゲットを変動 (若いほど低め)
        age_factor = (age - 19) / 7.0 # 0.0 ~ 1.0
        target_total = 190 + int(50 * age_factor)

    # 2. ターゲット総合力に基づいて能力値を生成
    # ランダムなブレ幅
    target_total += random.randint(-15, 15) 
    
    stats = PlayerStats()
    name = generate_japanese_name()

    if position == Position.PITCHER:
        # 投手: 3大要素 (球威, 制球, スタミナ) でターゲット合計を目指す
        avg = target_total / 3
        
        v1 = random.gauss(avg, 10)
        v2 = random.gauss(avg, 10)
        v3 = random.gauss(avg, 10)
        
        current_sum = v1 + v2 + v3
        ratio = target_total / current_sum if current_sum > 0 else 1
        
        stats.stuff = int(v1 * ratio)
        stats.control = int(v2 * ratio)
        stats.stamina = int(v3 * ratio)
        
        # 範囲制限 (1-99)
        stats.stuff = max(1, min(99, stats.stuff))
        stats.control = max(1, min(99, stats.control))
        stats.stamina = max(1, min(99, stats.stamina))
        
        # その他投手能力
        stats.velocity = int(random.gauss(140 + (target_total - 180)/4, 5)) 
        stats.velocity = max(125, min(165, stats.velocity))
        
        stats.movement = int(random.gauss(50, 15))
        stats.vs_left_pitcher = int(random.gauss(50, 15))
        stats.vs_pinch = int(random.gauss(50, 15))
        stats.stability = int(random.gauss(50, 15))
        stats.set_defense_range(Position.PITCHER, int(random.gauss(50, 15)))
        stats.arm = int(random.gauss(50, 15))
        stats.error = int(random.gauss(50, 15))
        stats.turn_dp = int(random.gauss(50, 15))
        
        # 変化球
        balls = ["ストレート", "スライダー", "カーブ", "フォーク", "チェンジアップ", "カットボール", "シンカー", "ツーシーム"]
        num_pitches = random.randint(2, 5)
        selected_balls = random.sample(balls, num_pitches)
        stats.pitches = {ball: int(random.gauss(stats.stuff, 10)) for ball in selected_balls}
        if "ストレート" not in stats.pitches:
            stats.pitches["ストレート"] = stats.stuff

    else:
        # 野手: 5大要素 (ミート, パワー, 走力, 肩力, 守備) でターゲット合計を目指す
        avg = target_total / 5
        
        v1 = random.gauss(avg, 12) # ミート
        v2 = random.gauss(avg, 12) # パワー
        v3 = random.gauss(avg, 12) # 走力
        v4 = random.gauss(avg, 12) # 肩力
        v5 = random.gauss(avg, 12) # 守備
        
        current_sum = v1 + v2 + v3 + v4 + v5
        ratio = target_total / current_sum if current_sum > 0 else 1
        
        stats.contact = int(v1 * ratio)
        stats.power = int(v2 * ratio)
        stats.speed = int(v3 * ratio)
        stats.arm = int(v4 * ratio)
        def_val = int(v5 * ratio)
        
        # 範囲制限
        stats.contact = max(1, min(99, stats.contact))
        stats.power = max(1, min(99, stats.power))
        stats.speed = max(1, min(99, stats.speed))
        stats.arm = max(1, min(99, stats.arm))
        def_val = max(1, min(99, def_val))
        
        # 守備範囲設定
        if position == Position.CATCHER:
            stats.catcher_lead = int(random.gauss(50, 10))
            stats.set_defense_range(Position.CATCHER, def_val)
        elif position == Position.FIRST:
            stats.set_defense_range(Position.FIRST, def_val)
        elif position == Position.SECOND:
            stats.set_defense_range(Position.SECOND, def_val)
        elif position == Position.THIRD:
            stats.set_defense_range(Position.THIRD, def_val)
        elif position == Position.SHORTSTOP:
            stats.set_defense_range(Position.SHORTSTOP, def_val)
        elif position in [Position.LEFT, Position.CENTER, Position.RIGHT]:
            stats.set_defense_range(position, def_val)
            
        stats.gap = stats.power 
        stats.eye = int(random.gauss(50, 15))
        stats.avoid_k = stats.contact 
        stats.error = int(random.gauss(50, 15))
        
        stats.velocity = 130
        stats.control = 50
        stats.stuff = 50

    stats.durability = int(random.gauss(50, 15))
    stats.recovery = int(random.gauss(50, 15))
    stats.work_ethic = int(random.gauss(50, 15))
    stats.intelligence = int(random.gauss(50, 15))
    stats.mental = int(random.gauss(50, 15))

    pot_bonus = 0
    if origin == "高校": pot_bonus = random.randint(10, 30)
    elif origin == "大学": pot_bonus = random.randint(5, 20)
    elif origin == "独立リーグ": pot_bonus = random.randint(5, 25)
    else: pot_bonus = random.randint(0, 15)
    
    potential = int((target_total / (3 if position == Position.PITCHER else 5)) + pot_bonus)
    potential = max(1, min(99, potential))

    return DraftProspect(name, position, pitch_type, stats, age, origin, potential)

def create_foreign_free_agent(position: Position, pitch_type: Optional[PitchType] = None) -> Player:
    """
    外国人選手生成ロジック
    年齢: 18-35歳
    能力: 年齢に応じて変動 (ピーク27-30歳付近)
    """
    age = random.randint(18, 35)
    name = generate_foreign_name()
    
    # 年齢に応じたターゲット総合力 (少し高めに設定)
    # 外国人なので「当たり」は非常に高く、「外れ」は低いという分散の大きさを持たせる
    
    # 基準値設定
    if age < 23: # 若手 (未完の大器が多い)
        base_target = 180 + (age - 18) * 12 # 180 - 240
        potential_bias = 20 # ポテンシャルは高め
    elif age <= 30: # 全盛期
        base_target = 240 + (age - 23) * 5 # 240 - 275
        potential_bias = 5
    else: # ベテラン (能力は高いがポテンシャルはない/衰え)
        base_target = 270 - (age - 30) * 12 # 270 - 210
        potential_bias = -10

    # 大きな分散 (当たり外れ)
    target_total = int(random.gauss(base_target, 35))
    target_total = max(150, min(380, target_total)) # 上限は高め

    # 能力生成 (DraftProspectと同様のロジックを使用するが、PlayerStatsを返す)
    stats = PlayerStats()

    if position == Position.PITCHER:
        # 投手: 球威重視の傾向
        avg = target_total / 3
        v1 = random.gauss(avg + 5, 15) # 球威強め
        v2 = random.gauss(avg - 5, 15) # 制球荒れ気味
        v3 = random.gauss(avg, 15)     # スタミナ
        
        current_sum = v1 + v2 + v3
        ratio = target_total / current_sum if current_sum > 0 else 1
        
        stats.stuff = int(v1 * ratio)
        stats.control = int(v2 * ratio)
        stats.stamina = int(v3 * ratio)
        
        stats.stuff = max(1, min(99, stats.stuff))
        stats.control = max(1, min(99, stats.control))
        stats.stamina = max(1, min(99, stats.stamina))
        
        # 球速は速め
        stats.velocity = int(random.gauss(150 + (target_total - 200)/5, 6))
        stats.velocity = max(130, min(175, stats.velocity))
        
        # その他
        stats.movement = int(random.gauss(50, 15))
        stats.set_defense_range(Position.PITCHER, int(random.gauss(45, 15)))
        stats.arm = int(random.gauss(50, 15))
        stats.error = int(random.gauss(45, 15))
        
        # 変化球 (少なめだが強力なものがある)
        balls = ["ストレート", "スライダー", "カーブ", "チェンジアップ", "ツーシーム", "カットボール", "SFF"]
        num_pitches = random.randint(2, 4)
        selected_balls = random.sample(balls, num_pitches)
        stats.pitches = {ball: int(random.gauss(stats.stuff, 12)) for ball in selected_balls}
        if "ストレート" not in stats.pitches:
            stats.pitches["ストレート"] = stats.stuff

    else:
        # 野手: パワー重視の傾向
        avg = target_total / 5
        
        v1 = random.gauss(avg - 5, 15) # ミート低め
        v2 = random.gauss(avg + 10, 15) # パワー高め
        v3 = random.gauss(avg, 15)
        v4 = random.gauss(avg + 5, 15) # 肩強め
        v5 = random.gauss(avg - 5, 15) # 守備粗め
        
        current_sum = v1 + v2 + v3 + v4 + v5
        ratio = target_total / current_sum if current_sum > 0 else 1
        
        stats.contact = int(v1 * ratio)
        stats.power = int(v2 * ratio)
        stats.speed = int(v3 * ratio)
        stats.arm = int(v4 * ratio)
        def_val = int(v5 * ratio)
        
        stats.contact = max(1, min(99, stats.contact))
        stats.power = max(1, min(99, stats.power))
        stats.speed = max(1, min(99, stats.speed))
        stats.arm = max(1, min(99, stats.arm))
        def_val = max(1, min(99, def_val))
        
        if position in [Position.LEFT, Position.CENTER, Position.RIGHT]:
            stats.set_defense_range(position, def_val)
        elif position == Position.FIRST:
            stats.set_defense_range(position, def_val)
        else:
            # 内野守備は重要なので少し補正
            stats.set_defense_range(position, def_val)

        stats.gap = stats.power 
        stats.eye = int(random.gauss(45, 15)) # 選球眼は低めになりがち
        stats.avoid_k = int(random.gauss(40, 15)) # 三振多い
        stats.error = int(random.gauss(45, 15))
        
        stats.velocity = 130
        stats.control = 50
        stats.stuff = 50

    # 共通
    stats.durability = int(random.gauss(60, 15)) # 体は強い
    stats.recovery = int(random.gauss(50, 15))
    stats.work_ethic = int(random.gauss(50, 20)) # バラつき大きい
    
    # 利き腕
    if random.random() < 0.75: player_throws = "右"
    else: player_throws = "左"
    
    if random.random() < 0.65: player_bats = "右"
    elif random.random() < 0.85: player_bats = "左"
    else: player_bats = "両"

    # 年俸計算 (能力依存)
    rating = target_total # 簡易的にターゲット合計を使用
    base_salary = 3000
    salary = int(base_salary * (rating / 200) ** 2) * 10000
    salary = max(50000000, salary) # 最低5000万

    player = Player(
        name=name, position=position, pitch_type=pitch_type, stats=stats,
        age=age, status=PlayerStatus.ACTIVE, uniform_number=0, is_foreign=True, salary=salary,
        bats=player_bats, throws=player_throws
    )
    
    # ポテンシャルなどをPlayerオブジェクトに持たせる場所がないので、
    # 呼び出し元で再計算するか、Playerクラスを拡張する必要があるが、
    # ここではPlayerオブジェクトを返す仕様に従う。
    # 呼び出し元(contracts_page)でDraftProspect的なオブジェクトに変換する際にポテンシャルを決定する。
    
    return player