# -*- coding: utf-8 -*-
from models import Team, Stadium

def initialize_stadiums(teams: list[Team]):
    """
    各チームに本拠地球場とパークファクターを割り当てる
    1.00を基準に、1.02なら2%出やすい、0.98なら2%出にくい設定
    """
    
    stadium_configs = {
        # セ・リーグ モデル
        "Tokyo Bravers": Stadium(
            name="東京スタジアム", 
            pf_runs=1.02, pf_hr=1.07, pf_1b=0.99, pf_2b=1.02, pf_3b=0.89, pf_so=1.00, pf_bb=1.01
        ),
        "Osaka Thunders": Stadium(
            name="大阪球場", 
            pf_runs=0.98, pf_hr=0.94, pf_1b=1.01, pf_2b=0.93, pf_3b=1.01, pf_so=1.01, pf_bb=0.99
        ),
        "Nagoya Sparks": Stadium(
            name="愛知ドーム", 
            pf_runs=0.96, pf_hr=0.91, pf_1b=0.99, pf_2b=0.98, pf_3b=1.13, pf_so=1.02, pf_bb=0.99
        ),
        "Hiroshima Phoenix": Stadium(
            name="広島野球場", 
            pf_runs=0.98, pf_hr=0.96, pf_1b=1.01, pf_2b=0.95, pf_3b=1.06, pf_so=1.00, pf_bb=1.00
        ),
        "Yokohama Mariners": Stadium(
            name="横浜ベイサイドパーク", 
            pf_runs=1.02, pf_hr=1.05, pf_1b=1.01, pf_2b=1.08, pf_3b=0.90, pf_so=0.98, pf_bb=1.01
        ),
        "Shinjuku Spirits": Stadium(
            name="新宿球場", 
            pf_runs=1.04, pf_hr=1.14, pf_1b=0.99, pf_2b=1.04, pf_3b=1.01, pf_so=0.99, pf_bb=1.00
        ),

        # パ・リーグ モデル
        "Fukuoka Phoenix": Stadium(
            name="博多ドーム", 
            pf_runs=1.00, pf_hr=1.09, pf_1b=0.98, pf_2b=0.98, pf_3b=1.02, pf_so=1.02, pf_bb=0.99
        ),
        "Saitama Bears": Stadium(
            name="埼玉フォレストドーム", 
            pf_runs=0.99, pf_hr=0.99, pf_1b=0.99, pf_2b=0.99, pf_3b=1.03, pf_so=1.00, pf_bb=0.99
        ),
        "Sendai Flames": Stadium(
            name="仙台ゴールデンパーク", 
            pf_runs=1.02, pf_hr=0.98, pf_1b=1.02, pf_2b=0.94, pf_3b=0.92, pf_so=0.99, pf_bb=1.00
        ),
        "Chiba Mariners": Stadium(
            name="千葉スタジアム", 
            pf_runs=1.02, pf_hr=1.04, pf_1b=1.00, pf_2b=1.01, pf_3b=0.97, pf_so=1.00, pf_bb=1.00
        ),
        "Sapporo Fighters": Stadium(
            name="北海道パーク", 
            pf_runs=1.05, pf_hr=1.08, pf_1b=1.01, pf_2b=1.04, pf_3b=0.99, pf_so=0.98, pf_bb=1.00
        ),
        "Kobe Buffaloes": Stadium(
            name="神戸大阪ドーム", 
            pf_runs=0.97, pf_hr=0.96, pf_1b=1.00, pf_2b=1.03, pf_3b=1.06, pf_so=1.00, pf_bb=1.00
        )
    }

    for team in teams:
        if team.name in stadium_configs:
            team.stadium = stadium_configs[team.name]
        else:
            team.stadium = Stadium(name=f"{team.name} Stadium")