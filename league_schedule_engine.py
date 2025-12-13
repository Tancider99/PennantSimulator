# -*- coding: utf-8 -*-
"""
日程作成エンジン（拡張版：二軍三軍対応 120/100試合制 + ランダム日程分散）
"""
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Set
import datetime
from models import Team, League, Schedule, ScheduledGame, GameStatus, TeamLevel

class LeagueScheduleEngine:
    """リーグ日程作成エンジン"""

    # 基本設定
    GAMES_PER_SEASON = 143
    INTRA_LEAGUE_GAMES = 25  # 同一リーグ対戦数
    INTERLEAGUE_GAMES = 18   # 交流戦

    def __init__(self, year: int = 2027):
        self.year = year

        # カレンダー設定
        self.opening_day = datetime.date(year, 3, 29)
        self.interleague_start = datetime.date(year, 5, 30)
        self.interleague_end = datetime.date(year, 6, 16)
        self.allstar_start = datetime.date(year, 7, 19)
        self.allstar_end = datetime.date(year, 7, 22)
        self.season_end = datetime.date(year, 10, 6)

        self.schedule = Schedule()
        self.north_teams = []
        self.south_teams = []
        self.all_teams = []

    def generate_schedule(self, north_teams: List[Team], south_teams: List[Team]) -> Schedule:
        """一軍日程を生成"""
        self.north_teams = [t.name for t in north_teams]
        self.south_teams = [t.name for t in south_teams]
        self.all_teams = self.north_teams + self.south_teams
        
        self.schedule = Schedule()
        
        # 全試合リストを生成して配置
        all_games = self.generate_all_games()
        # 一軍は従来通りの埋め込みロジック（連戦考慮などは今後の課題だが、今回は二軍修正が主）
        self._assign_games_to_dates_dense(self.schedule, all_games)
        
        return self.schedule

    def generate_farm_schedule(self, north_teams: List[Team], south_teams: List[Team], level: TeamLevel) -> Schedule:
        """
        二軍・三軍日程を生成
        二軍: 約120試合
        三軍: 約100試合
        バラバラに分散させる
        """
        n_names = [t.name for t in north_teams]
        s_names = [t.name for t in south_teams]
        all_names = n_names + s_names
        
        schedule = Schedule()
        games = []
        
        # 対戦回数の設定
        if level == TeamLevel.SECOND:
            # 11チーム相手に11試合ずつ = 121試合
            games_vs_opponent = 11
        else:
            # 11チーム相手に9試合ずつ = 99試合
            games_vs_opponent = 9
            
        # 総当たり戦生成
        for i, t1 in enumerate(all_names):
            for j, t2 in enumerate(all_names):
                if i >= j: continue
                
                count = games_vs_opponent
                home_games = count // 2
                away_games = count - home_games
                
                if (i + j) % 2 == 0:
                    home_games, away_games = away_games, home_games
                
                for _ in range(home_games): games.append((t1, t2, False))
                for _ in range(away_games): games.append((t2, t1, False))
        
        # 分散配置ロジックを使用
        self._assign_games_to_dates_scattered(schedule, games, level)
        return schedule

    def generate_all_games(self) -> List[Tuple[str, str, bool]]:
        """一軍の全試合を生成"""
        games = []
        # リーグ内対戦
        for teams in [self.north_teams, self.south_teams]:
            for i, team1 in enumerate(teams):
                for j, team2 in enumerate(teams):
                    if i >= j: continue
                    home1 = 13 if (i + j) % 2 == 0 else 12
                    home2 = 25 - home1
                    for _ in range(home1): games.append((team1, team2, False))
                    for _ in range(home2): games.append((team2, team1, False))

        # 交流戦
        for n_team in self.north_teams:
            for s_team in self.south_teams:
                if self.year % 2 == 0:
                    games.append((n_team, s_team, True))
                    games.append((n_team, s_team, True))
                    games.append((s_team, n_team, True))
                else:
                    games.append((s_team, n_team, True))
                    games.append((s_team, n_team, True))
                    games.append((n_team, s_team, True))
        return games

    def _get_valid_dates(self, level: TeamLevel) -> List[datetime.date]:
        """有効な試合開催日リストを取得"""
        valid_dates = []
        d = self.opening_day
        while d <= self.season_end:
            if d.weekday() != 0: # 月曜休み
                # 一軍はオールスター期間休み
                if level == TeamLevel.FIRST:
                    if not (self.allstar_start <= d <= self.allstar_end):
                        valid_dates.append(d)
                else:
                    valid_dates.append(d)
            d += datetime.timedelta(days=1)
        return valid_dates

    def _assign_games_to_dates_dense(self, schedule_obj: Schedule, all_games: List[Tuple[str, str, bool]]):
        """一軍用：できるだけ詰め込む配置ロジック"""
        random.shuffle(all_games)
        valid_dates = self._get_valid_dates(TeamLevel.FIRST)
        
        game_number = 1
        remaining = list(all_games)
        
        for date in valid_dates:
            if not remaining: break
            date_str = date.strftime("%Y-%m-%d")
            teams_playing = set()
            
            idx = 0
            while idx < len(remaining):
                home, away, _ = remaining[idx]
                if home not in teams_playing and away not in teams_playing:
                    schedule_obj.games.append(ScheduledGame(
                        game_number=game_number, date=date_str,
                        home_team_name=home, away_team_name=away
                    ))
                    teams_playing.add(home); teams_playing.add(away)
                    game_number += 1
                    remaining.pop(idx)
                else:
                    idx += 1
        
        # 残りがあれば末尾の日程に無理やり入れるなどの処理が必要だが、
        # ここではループで再試行して空きを探す
        if remaining:
            for date in valid_dates:
                if not remaining: break
                date_str = date.strftime("%Y-%m-%d")
                current_games = [g for g in schedule_obj.games if g.date == date_str]
                teams_playing = set()
                for g in current_games:
                    teams_playing.add(g.home_team_name)
                    teams_playing.add(g.away_team_name)
                
                idx = 0
                while idx < len(remaining):
                    home, away, _ = remaining[idx]
                    if home not in teams_playing and away not in teams_playing:
                        schedule_obj.games.append(ScheduledGame(
                            game_number=game_number, date=date_str,
                            home_team_name=home, away_team_name=away
                        ))
                        teams_playing.add(home); teams_playing.add(away)
                        game_number += 1
                        remaining.pop(idx)
                    else:
                        idx += 1

        schedule_obj.games.sort(key=lambda g: (g.date, g.game_number))
        for i, game in enumerate(schedule_obj.games): game.game_number = i + 1

    def _assign_games_to_dates_scattered(self, schedule_obj: Schedule, all_games: List[Tuple[str, str, bool]], level: TeamLevel):
        """二軍・三軍用：全期間に分散させる配置ロジック"""
        random.shuffle(all_games)
        valid_dates = self._get_valid_dates(level)
        
        # 日付ごとの対戦カード管理マップ
        date_schedule_map = {d: set() for d in valid_dates} # date -> set of team names playing
        scheduled_games_list = []
        
        game_number = 1
        
        # 全試合をランダムな日付に割り振る
        # ただし、その日に既に試合が入っているチームは避ける
        
        # 効率化のため、日付リストをシャッフルして回す
        # 試合ごとに「空いている日付」を探して割り当てる
        
        for home, away, _ in all_games:
            # 候補日をランダムに探す
            # 完全にランダムだと偏る可能性があるので、なるべく均等にしたいが
            # ここではシンプルに「空いているランダムな日」を選ぶ
            
            candidates = []
            # ランダムに100回試行して空きを探す（全走査は重いため）
            # もし見つからなければ全走査
            
            found_date = None
            
            # まずはランダムピック
            for _ in range(50):
                d = random.choice(valid_dates)
                teams_on_date = date_schedule_map[d]
                if home not in teams_on_date and away not in teams_on_date:
                    found_date = d
                    break
            
            # 見つからなければ全走査
            if found_date is None:
                random.shuffle(valid_dates) # 走査順をランダムに
                for d in valid_dates:
                    teams_on_date = date_schedule_map[d]
                    if home not in teams_on_date and away not in teams_on_date:
                        found_date = d
                        break
            
            if found_date:
                date_str = found_date.strftime("%Y-%m-%d")
                scheduled_games_list.append(ScheduledGame(
                    game_number=game_number, date=date_str,
                    home_team_name=home, away_team_name=away
                ))
                date_schedule_map[found_date].add(home)
                date_schedule_map[found_date].add(away)
                game_number += 1
            else:
                # どうしても入らない場合（理論上ありえないが）は無視するか、例外処理
                print(f"Warning: Could not schedule farm game {home} vs {away}")

        schedule_obj.games = scheduled_games_list
        schedule_obj.games.sort(key=lambda g: (g.date, g.game_number))
        for i, game in enumerate(schedule_obj.games):
            game.game_number = i + 1

    def get_team_schedule(self, team_name: str) -> List[ScheduledGame]:
        return [g for g in self.schedule.games
                if g.home_team_name == team_name or g.away_team_name == team_name]

    def get_next_game(self, team_name: str, after_date: str = None) -> Optional[ScheduledGame]:
        for game in self.schedule.games:
            if game.status != GameStatus.SCHEDULED: continue
            if after_date and game.date <= after_date: continue
            if game.home_team_name == team_name or game.away_team_name == team_name:
                return game
        return None
    
    def get_games_for_date(self, date_str: str) -> List[ScheduledGame]:
        return [g for g in self.schedule.games if g.date == date_str]

    def is_interleague_period(self, date_str: str) -> bool:
        try:
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return self.interleague_start <= d <= self.interleague_end
        except:
            return False

    def get_schedule_stats(self) -> Dict:
        stats = {"total_games": len(self.schedule.games), "teams": {}}
        for team in self.all_teams:
            team_games = self.get_team_schedule(team)
            home = len([g for g in team_games if g.home_team_name == team])
            away = len([g for g in team_games if g.away_team_name == team])
            stats["teams"][team] = {"total": len(team_games), "home": home, "away": away}
        return stats

def create_league_schedule(year: int, north_teams: List[Team], south_teams: List[Team]) -> Schedule:
    engine = LeagueScheduleEngine(year)
    return engine.generate_schedule(north_teams, south_teams)