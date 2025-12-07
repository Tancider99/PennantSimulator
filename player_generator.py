# -*- coding: utf-8 -*-
"""
選手生成ユーティリティ
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
    """ランダムな選手を生成（OOTP強化版）"""
    name = generate_foreign_name() if is_foreign else generate_japanese_name()
    if age is None:
        age = random.randint(18, 38) if not is_foreign else random.randint(22, 35)
    
    stats = PlayerStats()
    
    # 能力値生成ヘルパー (正規分布)
    def get_stat(mu=50, sigma=15, min_val=1, max_val=99):
        val = int(random.gauss(mu, sigma))
        return max(min_val, min(max_val, val))

    if position == Position.PITCHER:
        # --- 投手能力 ---
        # 球速: 平均146km/h, 標準偏差5km/h, 範囲130-165
        stats.velocity = get_stat(146, 5, 130, 165)
        
        # 基本3能力
        stats.stuff = get_stat(50, 18)
        stats.movement = get_stat(50, 15)
        stats.control = get_stat(50, 18)
        stats.stamina = get_stat(50, 20)
        
        # 守備 (投手)
        stats.inf_range = get_stat(40, 10)
        stats.inf_arm = get_stat(40, 10)
        stats.inf_error = get_stat(50, 10)
        
        # 打撃 (投手は低い)
        stats.contact = get_stat(15, 5, 1, 40)
        stats.power = get_stat(15, 5, 1, 40)
        stats.eye = get_stat(15, 5, 1, 40)
        
        # 変化球
        balls = ["ストレート", "スライダー", "カーブ", "フォーク", "チェンジアップ", "カットボール", "シンカー"]
        num_pitches = random.randint(2, 5)
        stats.breaking_balls = random.sample(balls, num_pitches)
        
    else:
        # --- 野手能力 ---
        stats.contact = get_stat(50, 18)
        stats.gap = get_stat(50, 15)
        stats.power = get_stat(50, 20)
        stats.eye = get_stat(50, 18)
        stats.avoid_k = get_stat(50, 15)
        
        stats.speed = get_stat(50, 18)
        stats.steal = get_stat(stats.speed, 10) # 足が速いと盗塁も上手い傾向
        stats.baserunning = get_stat(stats.speed, 10)
        
        # 守備 (ポジション別補正)
        if position == Position.CATCHER:
            stats.catcher_ab = get_stat(55, 15)
            stats.catcher_arm = get_stat(55, 15)
            stats.inf_range = get_stat(30, 10) # 捕手の内野守備は低い
        elif position in [Position.SHORTSTOP, Position.SECOND]:
            stats.inf_range = get_stat(60, 15)
            stats.inf_arm = get_stat(50, 15)
            stats.inf_dp = get_stat(55, 15)
        elif position == Position.THIRD:
            stats.inf_range = get_stat(50, 15)
            stats.inf_arm = get_stat(65, 15) # 三塁は肩
        elif position == Position.OUTFIELD:
            stats.of_range = get_stat(55, 15)
            stats.of_arm = get_stat(55, 15)
            
        stats.inf_error = get_stat(50, 15)
        stats.of_error = get_stat(50, 15)
        
        # 投手能力 (野手)
        stats.velocity = 130
        stats.control = 1
        stats.stuff = 1

    # 共通
    stats.mental = get_stat(50, 15)
    stats.injury_res = get_stat(50, 20)
    stats.bunt = get_stat(50, 20)

    # 年俸計算
    if position == Position.PITCHER:
        rating = stats.overall_pitching()
    else:
        rating = stats.overall_batting()
    
    base = 1000
    salary = int(base * (rating ** 2) / 20) * 10000
    
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