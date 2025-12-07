# -*- coding: utf-8 -*-
"""
選手生成ユーティリティ（OOTPスタイル対応版）
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
    """ランダムな選手を生成（OOTPスタイル対応版）

    能力値は1-200スケール（平均100）
    """
    name = generate_foreign_name() if is_foreign else generate_japanese_name()
    if age is None:
        age = random.randint(18, 38) if not is_foreign else random.randint(22, 35)

    stats = PlayerStats()

    # 能力値生成ヘルパー (正規分布、1-200スケール)
    def get_stat(mu=100, sigma=30, min_val=20, max_val=200):
        val = int(random.gauss(mu, sigma))
        return max(min_val, min(max_val, val))

    if position == Position.PITCHER:
        # --- 投手能力 ---
        # 球速: 平均146km/h, 標準偏差5km/h, 範囲130-165
        stats.velocity = get_stat(146, 5, 130, 165)

        # 基本3能力 (1-200)
        stats.stuff = get_stat(100, 35)
        stats.movement = get_stat(100, 30)
        stats.control = get_stat(100, 35)
        stats.stamina = get_stat(100, 40)
        stats.hold_runners = get_stat(100, 25)
        stats.gb_tendency = get_stat(50, 20, 0, 100)  # ゴロ傾向は0-100

        # 守備 (投手)
        stats.inf_range = get_stat(80, 20)
        stats.inf_arm = get_stat(80, 20)
        stats.inf_error = get_stat(100, 20)

        # 打撃 (投手は低い)
        stats.contact = get_stat(30, 10, 20, 80)
        stats.gap = get_stat(30, 10, 20, 80)
        stats.power = get_stat(30, 10, 20, 80)
        stats.eye = get_stat(30, 10, 20, 80)
        stats.avoid_k = get_stat(30, 10, 20, 80)

        # 走塁 (投手は低い)
        stats.speed = get_stat(60, 15, 20, 100)
        stats.steal = get_stat(40, 10, 20, 80)
        stats.baserunning = get_stat(50, 15, 20, 100)

        # 変化球 (pitchesディクショナリに格納)
        balls = ["ストレート", "スライダー", "カーブ", "フォーク", "チェンジアップ", "カットボール", "シンカー", "ツーシーム"]
        num_pitches = random.randint(3, 6)
        selected_balls = random.sample(balls, num_pitches)
        stats.pitches = {ball: get_stat(100, 30, 40, 180) for ball in selected_balls}
        # ストレートは必ず含める
        if "ストレート" not in stats.pitches:
            stats.pitches["ストレート"] = get_stat(120, 25, 60, 180)

    else:
        # --- 野手能力 ---
        stats.contact = get_stat(100, 35)
        stats.gap = get_stat(100, 30)
        stats.power = get_stat(100, 40)
        stats.eye = get_stat(100, 35)
        stats.avoid_k = get_stat(100, 30)

        stats.speed = get_stat(100, 35)
        stats.steal = get_stat(stats.speed, 20)  # 足が速いと盗塁も上手い傾向
        stats.baserunning = get_stat(stats.speed, 20)

        # バント
        stats.bunt_sac = get_stat(100, 40)
        stats.bunt_hit = get_stat(80, 30, 20, 160)

        # 守備 (ポジション別補正)
        if position == Position.CATCHER:
            stats.catcher_ability = get_stat(110, 30)
            stats.catcher_arm = get_stat(110, 30)
            stats.inf_range = get_stat(60, 20)  # 捕手の内野守備は低い
            stats.inf_error = get_stat(80, 20)
            stats.turn_dp = get_stat(60, 20)
        elif position in [Position.SHORTSTOP, Position.SECOND]:
            stats.inf_range = get_stat(120, 30)
            stats.inf_arm = get_stat(100, 30)
            stats.inf_error = get_stat(110, 25)
            stats.turn_dp = get_stat(110, 30)
        elif position == Position.THIRD:
            stats.inf_range = get_stat(100, 30)
            stats.inf_arm = get_stat(130, 30)  # 三塁は肩
            stats.inf_error = get_stat(100, 25)
            stats.turn_dp = get_stat(90, 25)
        elif position == Position.FIRST:
            stats.inf_range = get_stat(80, 25)
            stats.inf_arm = get_stat(80, 25)
            stats.inf_error = get_stat(110, 25)
            stats.turn_dp = get_stat(80, 25)
        elif position == Position.OUTFIELD:
            stats.of_range = get_stat(110, 30)
            stats.of_arm = get_stat(110, 30)
            stats.of_error = get_stat(100, 25)

        # 投手能力 (野手)
        stats.velocity = 130
        stats.control = 20
        stats.stuff = 20
        stats.movement = 20
        stats.stamina = 40

    # 共通能力
    stats.durability = get_stat(100, 40)
    stats.work_ethic = get_stat(100, 30)
    stats.intelligence = get_stat(100, 30)

    # 年俸計算
    if position == Position.PITCHER:
        rating = stats.overall_pitching()
    else:
        rating = stats.overall_batting()

    base = 500
    salary = int(base * (rating ** 1.5) / 100) * 10000

    player = Player(
        name=name, position=position, pitch_type=pitch_type, stats=stats,
        age=age, status=status, uniform_number=number, is_foreign=is_foreign, salary=salary
    )

    return player

def create_draft_prospect(position: Position, pitch_type: Optional[PitchType] = None, base_potential: int = 5) -> DraftProspect:
    player = create_random_player(position, pitch_type, age=18)
    return DraftProspect(player.name, position, pitch_type, player.stats, 18, "高校", base_potential)

def create_foreign_free_agent(position: Position, pitch_type: Optional[PitchType] = None) -> Player:
    return create_random_player(position, pitch_type, is_foreign=True, age=27)
