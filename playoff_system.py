# -*- coding: utf-8 -*-
"""
プレーオフ・日本シリーズシステム
"""
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple
from models import Team


class PlayoffStage(Enum):
    """プレーオフステージ"""
    CLIMAX_FIRST = ("クライマックスシリーズ ファーストステージ", 3)  # 3戦制
    CLIMAX_FINAL = ("クライマックスシリーズ ファイナルステージ", 6)  # 6戦制（1勝アドバンテージ）
    JAPAN_SERIES = ("日本シリーズ", 7)  # 7戦制
    
    def __init__(self, display_name: str, games: int):
        self.display_name = display_name
        self.max_games = games


@dataclass
class PlayoffSeries:
    """プレーオフシリーズ"""
    stage: PlayoffStage
    team1: Team  # 上位チーム
    team2: Team  # 下位チーム
    team1_wins: int = 0
    team2_wins: int = 0
    games_played: List[Tuple[int, int]] = None  # (team1_score, team2_score)
    is_complete: bool = False
    winner: Optional[Team] = None
    mvp: Optional[str] = None
    
    def __post_init__(self):
        if self.games_played is None:
            self.games_played = []
    
    @property
    def wins_needed(self) -> int:
        """勝利に必要な勝数"""
        if self.stage == PlayoffStage.CLIMAX_FIRST:
            return 2
        elif self.stage == PlayoffStage.CLIMAX_FINAL:
            return 4  # 1勝アドバンテージなので実質4勝
        else:  # JAPAN_SERIES
            return 4
    
    @property
    def current_status(self) -> str:
        """現在の状況"""
        return f"{self.team1.name} {self.team1_wins} - {self.team2_wins} {self.team2.name}"
    
    def record_game(self, team1_score: int, team2_score: int):
        """試合結果を記録"""
        self.games_played.append((team1_score, team2_score))
        if team1_score > team2_score:
            self.team1_wins += 1
        else:
            self.team2_wins += 1
        
        self._check_winner()
    
    def _check_winner(self):
        """勝者チェック"""
        if self.team1_wins >= self.wins_needed:
            self.is_complete = True
            self.winner = self.team1
        elif self.team2_wins >= self.wins_needed:
            self.is_complete = True
            self.winner = self.team2


class PlayoffManager:
    """プレーオフ管理"""
    
    def __init__(self, central_teams: List[Team], pacific_teams: List[Team]):
        self.central_teams = central_teams
        self.pacific_teams = pacific_teams
        
        # 順位でソート
        self.central_standings = sorted(central_teams, 
            key=lambda t: (t.wins - t.losses, t.wins), reverse=True)
        self.pacific_standings = sorted(pacific_teams,
            key=lambda t: (t.wins - t.losses, t.wins), reverse=True)
        
        # プレーオフシリーズ
        self.central_first: Optional[PlayoffSeries] = None
        self.central_final: Optional[PlayoffSeries] = None
        self.pacific_first: Optional[PlayoffSeries] = None
        self.pacific_final: Optional[PlayoffSeries] = None
        self.japan_series: Optional[PlayoffSeries] = None
        
        self.current_stage = PlayoffStage.CLIMAX_FIRST
    
    def setup_climax_first(self):
        """CSファーストステージをセットアップ"""
        # セ・リーグ: 2位 vs 3位
        self.central_first = PlayoffSeries(
            stage=PlayoffStage.CLIMAX_FIRST,
            team1=self.central_standings[1],  # 2位
            team2=self.central_standings[2]   # 3位
        )
        
        # パ・リーグ: 2位 vs 3位
        self.pacific_first = PlayoffSeries(
            stage=PlayoffStage.CLIMAX_FIRST,
            team1=self.pacific_standings[1],
            team2=self.pacific_standings[2]
        )
    
    def setup_climax_final(self, central_winner: Team, pacific_winner: Team):
        """CSファイナルステージをセットアップ"""
        # セ・リーグ: 1位 vs ファースト勝者（1位に1勝アドバンテージ）
        self.central_final = PlayoffSeries(
            stage=PlayoffStage.CLIMAX_FINAL,
            team1=self.central_standings[0],
            team2=central_winner,
            team1_wins=1  # アドバンテージ
        )
        
        # パ・リーグ
        self.pacific_final = PlayoffSeries(
            stage=PlayoffStage.CLIMAX_FINAL,
            team1=self.pacific_standings[0],
            team2=pacific_winner,
            team1_wins=1
        )
    
    def setup_japan_series(self, central_champion: Team, pacific_champion: Team):
        """日本シリーズをセットアップ"""
        self.japan_series = PlayoffSeries(
            stage=PlayoffStage.JAPAN_SERIES,
            team1=central_champion,
            team2=pacific_champion
        )
        self.current_stage = PlayoffStage.JAPAN_SERIES
    
    def get_current_series(self) -> List[PlayoffSeries]:
        """現在のシリーズを取得"""
        series = []
        
        if self.current_stage == PlayoffStage.CLIMAX_FIRST:
            if self.central_first and not self.central_first.is_complete:
                series.append(self.central_first)
            if self.pacific_first and not self.pacific_first.is_complete:
                series.append(self.pacific_first)
        
        elif self.current_stage == PlayoffStage.CLIMAX_FINAL:
            if self.central_final and not self.central_final.is_complete:
                series.append(self.central_final)
            if self.pacific_final and not self.pacific_final.is_complete:
                series.append(self.pacific_final)
        
        elif self.current_stage == PlayoffStage.JAPAN_SERIES:
            if self.japan_series and not self.japan_series.is_complete:
                series.append(self.japan_series)
        
        return series
    
    def advance_stage(self) -> bool:
        """次のステージに進む"""
        if self.current_stage == PlayoffStage.CLIMAX_FIRST:
            if self.central_first.is_complete and self.pacific_first.is_complete:
                self.setup_climax_final(
                    self.central_first.winner,
                    self.pacific_first.winner
                )
                self.current_stage = PlayoffStage.CLIMAX_FINAL
                return True
        
        elif self.current_stage == PlayoffStage.CLIMAX_FINAL:
            if self.central_final.is_complete and self.pacific_final.is_complete:
                self.setup_japan_series(
                    self.central_final.winner,
                    self.pacific_final.winner
                )
                self.current_stage = PlayoffStage.JAPAN_SERIES
                return True
        
        return False
    
    def is_complete(self) -> bool:
        """全プレーオフが完了したか"""
        return (self.japan_series is not None and 
                self.japan_series.is_complete)
    
    def get_japan_champion(self) -> Optional[Team]:
        """日本一チームを取得"""
        if self.japan_series and self.japan_series.is_complete:
            return self.japan_series.winner
        return None


class PlayoffSimulator:
    """プレーオフ試合シミュレーター"""
    
    @staticmethod
    def simulate_game(team1: Team, team2: Team) -> Tuple[int, int]:
        """1試合をシミュレート"""
        # チーム力計算
        team1_power = PlayoffSimulator._calculate_team_power(team1)
        team2_power = PlayoffSimulator._calculate_team_power(team2)
        
        # 得点計算
        base_runs = 4
        power_diff = (team1_power - team2_power) / 100
        
        team1_runs = max(0, int(base_runs + random.gauss(power_diff, 2)))
        team2_runs = max(0, int(base_runs + random.gauss(-power_diff, 2)))
        
        # 同点なら延長
        while team1_runs == team2_runs:
            if random.random() < 0.5:
                team1_runs += 1
            else:
                team2_runs += 1
        
        return team1_runs, team2_runs
    
    @staticmethod
    def _calculate_team_power(team: Team) -> float:
        """チーム総合力を計算"""
        if not team.players:
            return 50
        
        batting_power = 0
        pitching_power = 0
        batting_count = 0
        pitching_count = 0
        
        for player in team.players[:30]:  # 1軍登録選手
            if player.position.value == "投手":
                pitching_power += player.stats.overall_pitching()
                pitching_count += 1
            else:
                batting_power += player.stats.overall_batting()
                batting_count += 1
        
        avg_batting = batting_power / batting_count if batting_count > 0 else 10
        avg_pitching = pitching_power / pitching_count if pitching_count > 0 else 10
        
        # 勝率ボーナス
        win_rate_bonus = team.winning_percentage * 10
        
        return (avg_batting * 3 + avg_pitching * 2) / 5 * 10 + win_rate_bonus
    
    @staticmethod
    def simulate_series(series: PlayoffSeries) -> PlayoffSeries:
        """シリーズ全体をシミュレート"""
        while not series.is_complete:
            team1_score, team2_score = PlayoffSimulator.simulate_game(
                series.team1, series.team2
            )
            series.record_game(team1_score, team2_score)
        
        return series


@dataclass
class SeasonAwards:
    """シーズン表彰"""
    mvp_central: Optional[str] = None
    mvp_pacific: Optional[str] = None
    batting_champion_central: Optional[str] = None
    batting_champion_pacific: Optional[str] = None
    home_run_king_central: Optional[str] = None
    home_run_king_pacific: Optional[str] = None
    rbi_leader_central: Optional[str] = None
    rbi_leader_pacific: Optional[str] = None
    stolen_base_king_central: Optional[str] = None
    stolen_base_king_pacific: Optional[str] = None
    era_leader_central: Optional[str] = None
    era_leader_pacific: Optional[str] = None
    wins_leader_central: Optional[str] = None
    wins_leader_pacific: Optional[str] = None
    strikeout_leader_central: Optional[str] = None
    strikeout_leader_pacific: Optional[str] = None
    saves_leader_central: Optional[str] = None
    saves_leader_pacific: Optional[str] = None
    rookie_of_year_central: Optional[str] = None
    rookie_of_year_pacific: Optional[str] = None


class AwardsCalculator:
    """表彰計算"""
    
    @staticmethod
    def calculate_awards(central_teams: List[Team], pacific_teams: List[Team]) -> SeasonAwards:
        """シーズン表彰を計算"""
        awards = SeasonAwards()
        
        # セ・リーグ表彰
        central_players = []
        for team in central_teams:
            central_players.extend(team.players)
        
        AwardsCalculator._calculate_league_awards(
            central_players, awards, "central"
        )
        
        # パ・リーグ表彰
        pacific_players = []
        for team in pacific_teams:
            pacific_players.extend(team.players)
        
        AwardsCalculator._calculate_league_awards(
            pacific_players, awards, "pacific"
        )
        
        return awards
    
    @staticmethod
    def _calculate_league_awards(players: List, awards: SeasonAwards, league: str):
        """リーグ別表彰計算"""
        from models import Position
        
        # 野手と投手を分離
        batters = [p for p in players if p.position != Position.PITCHER]
        pitchers = [p for p in players if p.position == Position.PITCHER]
        
        # 首位打者（規定打席以上）
        qualified_batters = [b for b in batters if b.record.at_bats >= 100]
        if qualified_batters:
            champion = max(qualified_batters, key=lambda p: p.record.batting_average)
            setattr(awards, f"batting_champion_{league}", 
                   f"{champion.name} (.{int(champion.record.batting_average * 1000):03d})")
        
        # 本塁打王
        if batters:
            hr_king = max(batters, key=lambda p: p.record.home_runs)
            setattr(awards, f"home_run_king_{league}",
                   f"{hr_king.name} ({hr_king.record.home_runs}本)")
        
        # 打点王
        if batters:
            rbi_leader = max(batters, key=lambda p: p.record.rbis)
            setattr(awards, f"rbi_leader_{league}",
                   f"{rbi_leader.name} ({rbi_leader.record.rbis}打点)")
        
        # 盗塁王
        if batters:
            sb_king = max(batters, key=lambda p: p.record.stolen_bases)
            setattr(awards, f"stolen_base_king_{league}",
                   f"{sb_king.name} ({sb_king.record.stolen_bases}盗塁)")
        
        # 最優秀防御率（規定投球回以上）
        qualified_pitchers = [p for p in pitchers if p.record.innings_pitched >= 50]
        if qualified_pitchers:
            era_leader = min(qualified_pitchers, key=lambda p: p.record.era)
            setattr(awards, f"era_leader_{league}",
                   f"{era_leader.name} ({era_leader.record.era:.2f})")
        
        # 最多勝
        if pitchers:
            wins_leader = max(pitchers, key=lambda p: p.record.wins)
            setattr(awards, f"wins_leader_{league}",
                   f"{wins_leader.name} ({wins_leader.record.wins}勝)")
        
        # 最多奪三振
        if pitchers:
            k_leader = max(pitchers, key=lambda p: p.record.strikeouts_pitched)
            setattr(awards, f"strikeout_leader_{league}",
                   f"{k_leader.name} ({k_leader.record.strikeouts_pitched}奪三振)")
        
        # 最多セーブ
        if pitchers:
            save_leader = max(pitchers, key=lambda p: p.record.saves)
            setattr(awards, f"saves_leader_{league}",
                   f"{save_leader.name} ({save_leader.record.saves}S)")
        
        # MVP（勝利貢献度で計算）
        all_players = batters + pitchers
        if all_players:
            mvp = max(all_players, key=lambda p: AwardsCalculator._calculate_war(p))
            setattr(awards, f"mvp_{league}", mvp.name)
    
    @staticmethod
    def _calculate_war(player) -> float:
        """簡易WAR計算"""
        from models import Position
        
        if player.position == Position.PITCHER:
            # 投手WAR
            war = 0
            war += player.record.wins * 0.3
            if player.record.innings_pitched > 0:
                war += (4.50 - player.record.era) * player.record.innings_pitched / 50
            war += player.record.strikeouts_pitched * 0.01
            war += player.record.saves * 0.15
            return war
        else:
            # 野手WAR
            war = 0
            war += (player.record.batting_average - 0.250) * 10
            war += player.record.home_runs * 0.15
            war += player.record.rbis * 0.02
            war += player.record.stolen_bases * 0.05
            war += player.record.runs * 0.02
            return war
