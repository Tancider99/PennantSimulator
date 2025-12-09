# -*- coding: utf-8 -*-
"""
セイバーメトリクス計算・統計処理エンジン (修正版: team_pf引数追加・wRC+計算式変更・PF補正適正化)
"""
from models import Team, Player, Position, TeamLevel, PlayerRecord
from typing import List, Dict

class LeagueStatsCalculator:
    """リーグ全体の統計と係数を計算する（レベル別）"""

    def __init__(self, teams: List[Team]):
        self.teams = teams
        # レベルごとの集計データを保持
        self.league_totals = {
            TeamLevel.FIRST: self._create_empty_totals(),
            TeamLevel.SECOND: self._create_empty_totals(),
            TeamLevel.THIRD: self._create_empty_totals()
        }
        self.coefficients = {
            TeamLevel.FIRST: {},
            TeamLevel.SECOND: {},
            TeamLevel.THIRD: {}
        }
        self.park_factor = 1.0 # 簡易的に1.0

    def _create_empty_totals(self):
        return {
            "PA": 0, "AB": 0, "H": 0, "1B": 0, "2B": 0, "3B": 0, "HR": 0,
            "BB": 0, "IBB": 0, "HBP": 0, "SF": 0, "SH": 0, 
            "R": 0,   # 打者の得点合計
            "RA": 0,  # 投手の失点合計 (リーグ総得点の算出に使用)
            "IP": 0.0, "K": 0,
            "TB": 0, "FB": 0, # Fly Balls
            "ROE": 0 # Reach On Error (失策出塁)
        }

    def calculate_all(self):
        """全レベルの計算を実行"""
        # 1. 集計
        self._aggregate_league_totals()
        
        # 2. 係数計算 & 適用
        for level in [TeamLevel.FIRST, TeamLevel.SECOND, TeamLevel.THIRD]:
            self._calculate_coefficients(level)
            self._calculate_player_advanced_stats(level)

    def _aggregate_league_totals(self):
        """全チーム・全レベルの合計値を集計"""
        for team in self.teams:
            for player in team.players:
                # 各レベルのレコードを集計
                self._add_to_totals(player.record, TeamLevel.FIRST)
                self._add_to_totals(player.record_farm, TeamLevel.SECOND)
                self._add_to_totals(player.record_third, TeamLevel.THIRD)

    def _add_to_totals(self, r: PlayerRecord, level: TeamLevel):
        """レコードを該当レベルの合計に加算"""
        t = self.league_totals[level]
        if r.plate_appearances == 0 and r.innings_pitched == 0:
            return

        t["PA"] += r.plate_appearances
        t["AB"] += r.at_bats
        t["H"] += r.hits
        t["1B"] += r.singles
        t["2B"] += r.doubles
        t["3B"] += r.triples
        t["HR"] += r.home_runs
        t["BB"] += r.walks
        t["IBB"] += r.intentional_walks
        t["HBP"] += r.hit_by_pitch
        t["SF"] += r.sacrifice_flies
        t["SH"] += r.sacrifice_hits
        t["R"] += r.runs
        t["RA"] += r.runs_allowed # 失点を集計（リーグ総得点用）
        t["IP"] += r.innings_pitched
        t["K"] += r.strikeouts
        t["TB"] += r.total_bases
        t["FB"] += r.fly_balls
        t["ROE"] += r.reach_on_error

    def _calculate_coefficients(self, level: TeamLevel):
        """リーグ成績から係数を算出 (レベル別 - 新計算式対応)"""
        t = self.league_totals[level]
        c = {}
        
        # --- 基礎データの準備 ---
        # リーグ総得点として、打者の得点合計(R)ではなく投手の失点合計(RA)を使用
        league_runs = t["RA"] if t["RA"] > 0 else t["R"]
        
        # リーグ打席数
        league_pa = t["PA"] if t["PA"] > 0 else 1

        # リーグR/PA (Runs per Plate Appearance)
        c["league_r_pa"] = league_runs / league_pa if league_pa > 0 else 0.12

        # ゼロ除算防止のための安全策
        if t["IP"] > 0:
            r_per_out = league_runs / (t["IP"] * 3)
        else:
            # IPが0の場合は簡易的な推計
            outs = max(1, t["AB"] - t["H"])
            r_per_out = league_runs / outs if outs > 0 else 0.15

        # uBB = 四球 - 故意四球
        uBB_total = max(0, t["BB"] - t["IBB"])

        # --- Run Values の計算 ---
        # runBB = RperOut + 0.14
        run_bb = r_per_out + 0.14
        
        # runHBP = runBB + 0.025
        run_hbp = run_bb + 0.025
        
        # run1B = runBB + 0.13
        run_1b = run_bb + 0.13
        
        # run2B = run1B + 0.3
        run_2b = run_1b + 0.3
        
        # run3B = run2B + 0.27
        run_3b = run_2b + 0.27
        
        # runHR = 1.4
        run_hr = 1.4

        # --- runPLUS / runMINUS の計算 ---
        # 分子: (runBB*(BB-IBB) + runHBP*HBP + run1B*1B + run2B*2B + run3B*3B + runHR*HR)
        numerator = (
            run_bb * uBB_total +
            run_hbp * t["HBP"] +
            run_1b * t["1B"] +
            run_2b * t["2B"] +
            run_3b * t["3B"] +
            run_hr * t["HR"]
        )

        # runPLUS = 分子 / (H + BB - IBB + HBP)
        denom_plus = t["H"] + uBB_total + t["HBP"]
        run_plus = numerator / denom_plus if denom_plus > 0 else 0.0

        # runMINUS = 分子 / (AB - H + SF)
        denom_minus = t["AB"] - t["H"] + t["SF"]
        run_minus = numerator / denom_minus if denom_minus > 0 else 0.0

        # --- wOBA Scale の計算 (動的計算) ---
        # リーグwOBAをリーグOBPに合わせるためのスケール
        raw_diff = run_plus - run_minus
        temp_scale = 1 / raw_diff if raw_diff != 0 else 1.0

        raw_weights = {
            "uBB": (run_bb + run_minus) * temp_scale,
            "HBP": (run_hbp + run_minus) * temp_scale,
            "1B": (run_1b + run_minus) * temp_scale,
            "2B": (run_2b + run_minus) * temp_scale,
            "3B": (run_3b + run_minus) * temp_scale,
            "HR": (run_hr + run_minus) * temp_scale,
            "ROE": 0.966
        }
        
        lg_woba_raw = self._calc_league_woba_val(t, raw_weights)
        denom_oba = t["AB"] + t["BB"] + t["HBP"] + t["SF"]
        lg_oba = (t["H"] + t["BB"] + t["HBP"]) / denom_oba if denom_oba > 0 else 0.320
        
        woba_scale = lg_oba / lg_woba_raw if lg_woba_raw > 0 else 1.20
        
        c["woba_weights"] = {k: v * woba_scale for k, v in raw_weights.items()}
        c["woba_weights"]["ROE"] = 0.966 * woba_scale
        c["woba_scale"] = woba_scale
        c["league_woba"] = self._calc_league_woba_val(t, c["woba_weights"])

        # --- FIP Constant ---
        if t["IP"] > 0:
            league_era = (league_runs * 9) / t["IP"]
            fip_raw = (13 * t["HR"] + 3 * (t["BB"] + t["HBP"]) - 2 * t["K"]) / t["IP"]
            c["fip_constant"] = league_era - fip_raw
            c["league_fip"] = league_era 
        else:
            c["fip_constant"] = 3.10
            c["league_fip"] = 4.00
            
        # --- League HR/FB ---
        if t["FB"] > 0:
            c["league_hr_fb"] = t["HR"] / t["FB"]
        else:
            c["league_hr_fb"] = 0.10 

        c["runs_per_win"] = 10.0 # 簡易値
        
        self.coefficients[level] = c

    def _calc_league_woba_val(self, t, w):
        # リーグ全体のwOBA計算
        denom = t["AB"] + t["BB"] - t["IBB"] + t["HBP"] + t["SF"]
        if denom <= 0: return 0.0
        
        uBB = max(0, t["BB"] - t["IBB"])
        
        val = (w["uBB"] * uBB + 
               w["HBP"] * t["HBP"] + 
               w["ROE"] * t["ROE"] +
               w["1B"] * t["1B"] + 
               w["2B"] * t["2B"] + 
               w["3B"] * t["3B"] + 
               w["HR"] * t["HR"])
        
        return val / denom

    def _calculate_player_advanced_stats(self, level: TeamLevel):
        """指定レベルの全選手の指標を更新"""
        c = self.coefficients[level]
        
        for team in self.teams:
            # チームの本拠地PFを取得
            # ここで team_pf を取得し、_update_single_record に渡す必要があります
            team_pf = team.stadium.pf_runs if team.stadium else 1.0
            
            for player in team.players:
                # 該当レベルのレコードを取得
                record = player.get_record_by_level(level)
                self._update_single_record(player, record, c, team_pf)

    def _update_single_record(self, player: Player, r: PlayerRecord, c: dict, team_pf: float):
        """
        個人の成績を更新する
        :param team_pf: 所属チームの本拠地パークファクター(得点)
        """
        if r.plate_appearances == 0 and r.innings_pitched == 0:
            return

        w = c["woba_weights"]
        lg_woba = c["league_woba"]
        lg_r_pa = c["league_r_pa"]
        woba_scale = c["woba_scale"]
        fip_const = c["fip_constant"]
        rpw = c["runs_per_win"]

        # ▼▼▼ PF算出 (経験PF累積値から計算) ▼▼▼
        if r.plate_appearances > 0:
            personal_pf_batter = r.sum_pf_runs / r.plate_appearances
        else:
            personal_pf_batter = 1.0
            
        tbf_approx = r.hits_allowed + r.walks_allowed + r.hit_batters + r.strikeouts_pitched + (r.innings_pitched * 3)
        if tbf_approx > 0:
            personal_pf_pitcher = r.sum_pf_runs / tbf_approx 
        else:
            personal_pf_pitcher = 1.0
            
        if personal_pf_batter == 0: personal_pf_batter = 1.0
        if personal_pf_pitcher == 0: personal_pf_pitcher = 1.0
        # ▲▲▲ PF算出終了 ▲▲▲

        # --- Batting Stats ---
        if r.plate_appearances > 0:
            # wOBA Calculation
            denominator = r.at_bats + r.walks - r.intentional_walks + r.hit_by_pitch + r.sacrifice_flies
            if denominator > 0:
                uBB = max(0, r.walks - r.intentional_walks)
                numerator = (w["uBB"] * uBB + 
                             w["HBP"] * r.hit_by_pitch + 
                             w["ROE"] * r.reach_on_error +
                             w["1B"] * r.singles + 
                             w["2B"] * r.doubles + 
                             w["3B"] * r.triples + 
                             w["HR"] * r.home_runs)
                r.woba_val = numerator / denominator
            else:
                r.woba_val = 0.0

            # --- wRAA Calculation ---
            if woba_scale > 0:
                wraa = ((r.woba_val - lg_woba) / woba_scale) * r.plate_appearances
            else:
                wraa = 0

            # ▼▼▼ パークファクター補正 ▼▼▼
            # 補正係数＝（本拠地試合／総試合）×PF＋（1－本拠地試合／総試合）×（6－PF）／5
            # ※リーグ球団数6を前提とした他球場平均PF近似式: (6 - PF) / 5
            
            games_ratio = r.home_games / r.games if r.games > 0 else 0.5
            pf_factor = games_ratio * team_pf + (1.0 - games_ratio) * ((6.0 - team_pf) / 5.0)
            
            # 補正値＝（1－補正係数）×リーグの平均打席あたり得点×打席
            pf_adjustment_value = (1.0 - pf_factor) * lg_r_pa * r.plate_appearances
            
            # 補正wRAA
            adjusted_wraa = wraa + pf_adjustment_value
            
            # wRC Calculation (補正wRAAベース)
            adjusted_wrc = adjusted_wraa + (lg_r_pa * r.plate_appearances)
            
            r.wrc_val = adjusted_wrc 

            # wRC+ Calculation
            # wRC+＝（パークファクターを考慮して計算したwRC÷打席）÷（リーグ総得点÷リーグ総打席）×100
            
            if lg_r_pa > 0:
                wrc_per_pa = adjusted_wrc / r.plate_appearances
                r.wrc_plus_val = (wrc_per_pa / lg_r_pa) * 100
            else:
                r.wrc_plus_val = 100.0
            
        # --- Pitching Stats ---
        if r.innings_pitched > 0:
            # FIP
            fip_val = (13 * r.home_runs_allowed + 3 * (r.walks_allowed + r.hit_batters) - 2 * r.strikeouts_pitched) / r.innings_pitched
            r.fip_val = fip_val + fip_const
            
            # xFIP
            lg_hr_fb = c.get("league_hr_fb", 0.10)
            expected_hr = r.fly_balls * lg_hr_fb
            xfip_val = (13 * expected_hr + 3 * (r.walks_allowed + r.hit_batters) - 2 * r.strikeouts_pitched) / r.innings_pitched
            r.xfip_val = xfip_val + fip_const

        # --- Defensive Stats ---
        r.drs_val = r.def_drs_raw
        r.uzr_val = r.def_drs_raw * 0.9

        # --- WAR Calculation (PF Adjusted) ---
        if player.position.value != "投手":
            # 野手WAR
            # Batting Runs: 補正wRAAを使用
            batting_runs = adjusted_wraa if r.plate_appearances > 0 else 0
            
            bsr = (r.stolen_bases * 0.2) - (r.caught_stealing * 0.4)
            fielding_runs = r.uzr_val
            
            pos_val_map = {
                "捕手": 12.5, "遊撃手": 7.5, "二塁手": 2.5, "三塁手": 2.5, "外野手": -2.5,
                "一塁手": -12.5, "DH": -17.5
            }
            pos_base = pos_val_map.get(player.position.value, 0)
            pos_adj = pos_base * (r.plate_appearances / 600.0)
            rep_runs = 20.0 * (r.plate_appearances / 600.0)
            
            # batting_runs には既にPF補正が含まれているため、そのまま足す
            total_runs = batting_runs + bsr + fielding_runs + pos_adj + rep_runs
            r.war_val = total_runs / rpw
            
        else:
            # 投手WAR (FIP Base with PF Adjustment)
            if r.innings_pitched > 0:
                lg_fip = c.get("league_fip", 4.00)
                
                # 投手用PF補正係数
                games_ratio_p = r.home_games_pitched / r.games_pitched if r.games_pitched > 0 else 0.5
                pf_factor_p = games_ratio_p * team_pf + (1.0 - games_ratio_p) * ((6.0 - team_pf) / 5.0)
                
                # FIPをPF係数で割って補正 (FIP / PF_Factor)
                if pf_factor_p > 0:
                    adjusted_fip = r.fip_val / pf_factor_p
                else:
                    adjusted_fip = r.fip_val

                ra9_diff = lg_fip - adjusted_fip
                runs_saved = ra9_diff * (r.innings_pitched / 9.0)
                
                rep_runs_per_9 = 2.06
                rep_runs = rep_runs_per_9 * (r.innings_pitched / 9.0)
                
                r.war_val = (runs_saved + rep_runs) / rpw


def update_league_stats(all_teams: List[Team]):
    """外部から呼び出すためのヘルパー関数"""
    calc = LeagueStatsCalculator(all_teams)
    calc.calculate_all()