# -*- coding: utf-8 -*-
"""
チーム生成ユーティリティ
"""
from models import Team, Position, PitchType, PlayerStatus, League
from player_generator import create_random_player
import random


def create_team(team_name: str, league: League) -> Team:
    """チームを生成（支配下70人＋育成30人）"""
    team = Team(name=team_name, league=league)
    number = 1
    
    # ==============================
    # 支配下選手 (70人)
    # ==============================
    # 投手 (28人)
    for _ in range(8):
        p = create_random_player(Position.PITCHER, PitchType.STARTER, PlayerStatus.ACTIVE, number)
        p.is_developmental = False
        _add_sub_positions_pitcher(p)
        team.players.append(p)
        number += 1
    for _ in range(14):
        p = create_random_player(Position.PITCHER, PitchType.RELIEVER, PlayerStatus.ACTIVE, number)
        p.is_developmental = False
        _add_sub_positions_pitcher(p)
        team.players.append(p)
        number += 1
    for _ in range(6):
        p = create_random_player(Position.PITCHER, PitchType.CLOSER, PlayerStatus.ACTIVE, number)
        p.is_developmental = False
        _add_sub_positions_pitcher(p)
        team.players.append(p)
        number += 1
    
    # 野手 (42人)
    for _ in range(4):
        p = create_random_player(Position.CATCHER, status=PlayerStatus.ACTIVE, number=number)
        p.is_developmental = False
        _add_sub_positions_catcher(p)
        team.players.append(p)
        number += 1
    for _ in range(5):
        p = create_random_player(Position.FIRST, status=PlayerStatus.ACTIVE, number=number)
        p.is_developmental = False
        _add_sub_positions_infielder(p, Position.FIRST)
        team.players.append(p)
        number += 1
    for _ in range(6):
        p = create_random_player(Position.SECOND, status=PlayerStatus.ACTIVE, number=number)
        p.is_developmental = False
        _add_sub_positions_infielder(p, Position.SECOND)
        team.players.append(p)
        number += 1
    for _ in range(5):
        p = create_random_player(Position.THIRD, status=PlayerStatus.ACTIVE, number=number)
        p.is_developmental = False
        _add_sub_positions_infielder(p, Position.THIRD)
        team.players.append(p)
        number += 1
    for _ in range(6):
        p = create_random_player(Position.SHORTSTOP, status=PlayerStatus.ACTIVE, number=number)
        p.is_developmental = False
        _add_sub_positions_infielder(p, Position.SHORTSTOP)
        team.players.append(p)
        number += 1
    for _ in range(16):
        p = create_random_player(Position.OUTFIELD, status=PlayerStatus.ACTIVE, number=number)
        p.is_developmental = False
        _add_sub_positions_outfielder(p)
        team.players.append(p)
        number += 1
    
    # ==============================
    # 育成選手 (30人) - 背番号は3桁
    # ==============================
    dev_number = 101
    
    # 育成投手 (12人)
    for _ in range(12):
        p = create_random_player(
            Position.PITCHER, 
            random.choice(list(PitchType)), 
            PlayerStatus.FARM, 
            dev_number
        )
        p.is_developmental = True
        _add_sub_positions_pitcher(p)
        # 育成選手は能力を少し下げる
        _adjust_developmental_stats(p)
        team.players.append(p)
        dev_number += 1
    
    # 育成野手 (18人)
    positions = [Position.CATCHER, Position.FIRST, Position.SECOND, Position.THIRD, 
                Position.SHORTSTOP, Position.OUTFIELD, Position.OUTFIELD, Position.OUTFIELD]
    for _ in range(18):
        pos = random.choice(positions)
        p = create_random_player(pos, status=PlayerStatus.FARM, number=dev_number)
        p.is_developmental = True
        if pos == Position.CATCHER:
            _add_sub_positions_catcher(p)
        elif pos == Position.OUTFIELD:
            _add_sub_positions_outfielder(p)
        else:
            _add_sub_positions_infielder(p, pos)
        _adjust_developmental_stats(p)
        team.players.append(p)
        dev_number += 1
    
    return team


def _add_sub_positions_pitcher(player):
    """投手のサブポジション（基本なし）"""
    pass


def _add_sub_positions_catcher(player):
    """捕手のサブポジション"""
    if random.random() < 0.3:
        player.add_sub_position(Position.FIRST, random.uniform(0.5, 0.7))
    if random.random() < 0.1:
        player.add_sub_position(Position.THIRD, random.uniform(0.4, 0.6))


def _add_sub_positions_infielder(player, main_pos: Position):
    """内野手のサブポジション"""
    infield_positions = [Position.FIRST, Position.SECOND, Position.THIRD, Position.SHORTSTOP]
    
    # 二遊間はお互い守りやすい
    if main_pos == Position.SECOND:
        if random.random() < 0.6:
            player.add_sub_position(Position.SHORTSTOP, random.uniform(0.6, 0.85))
        if random.random() < 0.3:
            player.add_sub_position(Position.THIRD, random.uniform(0.5, 0.7))
    elif main_pos == Position.SHORTSTOP:
        if random.random() < 0.6:
            player.add_sub_position(Position.SECOND, random.uniform(0.6, 0.85))
        if random.random() < 0.5:
            player.add_sub_position(Position.THIRD, random.uniform(0.6, 0.8))
    elif main_pos == Position.THIRD:
        if random.random() < 0.4:
            player.add_sub_position(Position.FIRST, random.uniform(0.6, 0.8))
        if random.random() < 0.3:
            player.add_sub_position(Position.SHORTSTOP, random.uniform(0.5, 0.7))
    elif main_pos == Position.FIRST:
        if random.random() < 0.2:
            player.add_sub_position(Position.THIRD, random.uniform(0.5, 0.7))
        if random.random() < 0.2:
            player.add_sub_position(Position.OUTFIELD, random.uniform(0.5, 0.7))


def _add_sub_positions_outfielder(player):
    """外野手のサブポジション"""
    # 外野手は外野全ポジション可能（外野手同士のサブポジは不要、同一ポジション扱い）
    # 一塁や三塁を守れる選手もいる
    if random.random() < 0.25:
        player.add_sub_position(Position.FIRST, random.uniform(0.5, 0.75))
    if random.random() < 0.1:
        player.add_sub_position(Position.THIRD, random.uniform(0.4, 0.6))


def _adjust_developmental_stats(player):
    """育成選手の能力調整（やや低め）"""
    stats = player.stats
    factor = random.uniform(0.7, 0.9)
    stats.contact = max(1, int(stats.contact * factor))
    stats.power = max(1, int(stats.power * factor))
    stats.run = max(1, int(stats.run * factor))
    stats.arm = max(1, int(stats.arm * factor))
    stats.fielding = max(1, int(stats.fielding * factor))
    stats.speed = max(1, int(stats.speed * factor))
    stats.control = max(1, int(stats.control * factor))
    stats.stamina = max(1, int(stats.stamina * factor))
    stats.breaking = max(1, int(stats.breaking * factor))
