# -*- coding: utf-8 -*-
"""
日程作成エンジン（NPB完全準拠版）
- 一軍143試合（3連戦カード制）、二軍120試合、三軍100試合
- リーグ戦は同一リーグのみ対戦
- 交流戦（6月）は他リーグのみ対戦 + 予備日3日
- オールスター（7月下旬）本格実装
- 天候システム（雨天中止・コールド）
- 延期試合の振替
- ポストシーズン（CS・日本シリーズ）本格実装
"""
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set
import datetime
from enum import Enum
from models import Team, League, Schedule, ScheduledGame, GameStatus, TeamLevel, Player, Position


class WeatherCondition(Enum):
    CLEAR = "晴れ"
    CLOUDY = "曇り"
    LIGHT_RAIN = "小雨"
    RAIN = "雨"
    HEAVY_RAIN = "大雨"


class GameCancellationReason(Enum):
    NONE = ""
    RAIN = "雨天中止"
    RAIN_COLD = "雨天コールド"


@dataclass
class SeriesCard:
    """3連戦カード"""
    home_team: str
    away_team: str
    games: int = 3  # 通常3試合
    is_interleague: bool = False


@dataclass
class SeasonCalendar:
    """シーズンカレンダー設定"""
    year: int
    opening_day: datetime.date
    interleague_start: datetime.date
    interleague_end: datetime.date
    interleague_reserve_end: datetime.date
    allstar_day1: datetime.date
    allstar_day2: datetime.date
    regular_season_end: datetime.date
    max_season_end: datetime.date
    cs_first_start: datetime.date
    cs_final_start: datetime.date
    japan_series_start: datetime.date

    @classmethod
    def create(cls, year: int) -> 'SeasonCalendar':
        """NPB準拠のカレンダーを生成"""
        return cls(
            year=year,
            opening_day=datetime.date(year, 3, 29),
            interleague_start=datetime.date(year, 6, 3),
            interleague_end=datetime.date(year, 6, 20),
            interleague_reserve_end=datetime.date(year, 6, 23),
            allstar_day1=datetime.date(year, 7, 23),
            allstar_day2=datetime.date(year, 7, 24),
            regular_season_end=datetime.date(year, 9, 28),
            max_season_end=datetime.date(year, 10, 7),
            cs_first_start=datetime.date(year, 10, 12),
            cs_final_start=datetime.date(year, 10, 16),
            japan_series_start=datetime.date(year, 10, 26),
        )


class WeatherSystem:
    """天候シミュレーションシステム"""

    MONTHLY_RAIN_PROBABILITY = {
        3: 0.25, 4: 0.28, 5: 0.30, 6: 0.45,
        7: 0.35, 8: 0.30, 9: 0.35, 10: 0.25,
    }

    @classmethod
    def get_weather(cls, date: datetime.date) -> WeatherCondition:
        rain_prob = cls.MONTHLY_RAIN_PROBABILITY.get(date.month, 0.25)
        roll = random.random()
        if roll < rain_prob * 0.3:
            return WeatherCondition.HEAVY_RAIN
        elif roll < rain_prob * 0.6:
            return WeatherCondition.RAIN
        elif roll < rain_prob:
            return WeatherCondition.LIGHT_RAIN
        elif roll < rain_prob + 0.3:
            return WeatherCondition.CLOUDY
        return WeatherCondition.CLEAR

    @classmethod
    def should_cancel_game(cls, weather: WeatherCondition) -> bool:
        if weather == WeatherCondition.HEAVY_RAIN:
            return True
        elif weather == WeatherCondition.RAIN:
            return random.random() < 0.7
        elif weather == WeatherCondition.LIGHT_RAIN:
            return random.random() < 0.15
        return False

    @classmethod
    def should_call_game(cls, weather: WeatherCondition, inning: int) -> bool:
        if inning < 5:
            return False
        if weather == WeatherCondition.HEAVY_RAIN:
            return random.random() < 0.8
        elif weather == WeatherCondition.RAIN:
            return random.random() < 0.4
        return False


class LeagueScheduleEngine:
    """NPB準拠リーグ日程作成エンジン（3連戦カード制）"""

    GAMES_PER_SEASON = 143
    LEAGUE_GAMES_PER_OPPONENT = 25  # 同一リーグ: 5チーム × 25試合 = 125試合
    INTERLEAGUE_GAMES_PER_OPPONENT = 3  # 交流戦: 6チーム × 3試合 = 18試合

    def __init__(self, year: int = 2027):
        self.year = year
        self.calendar = SeasonCalendar.create(year)
        self.schedule = Schedule()
        self.north_teams: List[str] = []
        self.south_teams: List[str] = []
        self.all_teams: List[str] = []
        self.postponed_games: List[ScheduledGame] = []
        self.weather_enabled = True

    @property
    def opening_day(self) -> datetime.date:
        return self.calendar.opening_day

    def generate_schedule(self, north_teams: List[Team], south_teams: List[Team]) -> Schedule:
        """一軍日程を生成（NPB準拠・3連戦カード制）"""
        self.north_teams = [t.name for t in north_teams]
        self.south_teams = [t.name for t in south_teams]
        self.all_teams = self.north_teams + self.south_teams

        self.schedule = Schedule()
        self.postponed_games = []

        # 1. リーグ内カード（3連戦）を生成
        north_cards = self._generate_league_cards(self.north_teams)
        south_cards = self._generate_league_cards(self.south_teams)

        # 2. 交流戦カード（3連戦）を生成
        interleague_cards = self._generate_interleague_cards()

        # 3. 日程に配置
        self._assign_cards_to_calendar(north_cards, south_cards, interleague_cards)

        return self.schedule

    def _generate_league_cards(self, teams: List[str]) -> List[SeriesCard]:
        """リーグ内3連戦カードを生成（各対戦25試合）

        各チームペア25試合の内訳:
        - 8つの3連戦カード = 24試合
        - 1つの1試合カード = 1試合
        合計: 25試合

        ホーム・アウェイ配分:
        - team1ホーム: 4カード(12試合) + 調整1試合 = 13試合 or 12試合
        - team2ホーム: 4カード(12試合) = 12試合 or 13試合
        """
        cards = []

        for i, team1 in enumerate(teams):
            for j, team2 in enumerate(teams):
                if i >= j:
                    continue

                # team1がホームの3連戦カード × 4
                for _ in range(4):
                    cards.append(SeriesCard(home_team=team1, away_team=team2, games=3))

                # team2がホームの3連戦カード × 4
                for _ in range(4):
                    cards.append(SeriesCard(home_team=team2, away_team=team1, games=3))

                # 調整用1試合（ペアのインデックスで交互にホームを決定）
                if (i + j) % 2 == 0:
                    cards.append(SeriesCard(home_team=team1, away_team=team2, games=1))
                else:
                    cards.append(SeriesCard(home_team=team2, away_team=team1, games=1))

        return cards

    def _generate_interleague_cards(self) -> List[SeriesCard]:
        """交流戦3連戦カードを生成（各チーム18試合）"""
        cards = []

        for n_team in self.north_teams:
            for s_team in self.south_teams:
                # 3試合1カード
                if self.year % 2 == 0:
                    # 偶数年: 北リーグがホーム2試合、南リーグがホーム1試合
                    cards.append(SeriesCard(home_team=n_team, away_team=s_team, games=3, is_interleague=True))
                else:
                    # 奇数年: 南リーグがホーム2試合、北リーグがホーム1試合
                    cards.append(SeriesCard(home_team=s_team, away_team=n_team, games=3, is_interleague=True))

        return cards

    def _assign_cards_to_calendar(self, north_cards: List[SeriesCard],
                                   south_cards: List[SeriesCard],
                                   interleague_cards: List[SeriesCard]):
        """カードを日程に配置（3連戦単位）"""
        random.shuffle(north_cards)
        random.shuffle(south_cards)
        random.shuffle(interleague_cards)

        game_number = 1

        # 期間を分類
        pre_il_dates = []  # 交流戦前
        il_dates = []      # 交流戦期間
        post_il_dates = [] # 交流戦後

        d = self.calendar.opening_day
        while d <= self.calendar.regular_season_end:
            if d.weekday() == 0:  # 月曜休み
                d += datetime.timedelta(days=1)
                continue

            # オールスター期間スキップ
            allstar_rest_start = self.calendar.allstar_day1 - datetime.timedelta(days=1)
            allstar_rest_end = self.calendar.allstar_day2 + datetime.timedelta(days=1)
            if allstar_rest_start <= d <= allstar_rest_end:
                d += datetime.timedelta(days=1)
                continue

            if d < self.calendar.interleague_start:
                pre_il_dates.append(d)
            elif self.calendar.interleague_start <= d <= self.calendar.interleague_end:
                il_dates.append(d)
            elif d > self.calendar.interleague_reserve_end:
                post_il_dates.append(d)

            d += datetime.timedelta(days=1)

        # === 交流戦前のリーグ戦 ===
        game_number = self._schedule_league_cards(
            north_cards[:len(north_cards)//2],
            south_cards[:len(south_cards)//2],
            pre_il_dates, game_number
        )

        # === 交流戦期間 ===
        game_number = self._schedule_interleague_cards(
            interleague_cards, il_dates, game_number
        )

        # === 交流戦後のリーグ戦 ===
        game_number = self._schedule_league_cards(
            north_cards[len(north_cards)//2:],
            south_cards[len(south_cards)//2:],
            post_il_dates, game_number
        )

        # ソートして番号振り直し
        self.schedule.games.sort(key=lambda g: (g.date, g.game_number))
        for i, game in enumerate(self.schedule.games):
            game.game_number = i + 1

    def _schedule_league_cards(self, north_cards: List[SeriesCard],
                                south_cards: List[SeriesCard],
                                dates: List[datetime.date],
                                start_game_number: int) -> int:
        """リーグ戦カードを日程に配置（同一リーグのみ）"""
        game_number = start_game_number
        date_idx = 0

        all_cards = north_cards + south_cards
        random.shuffle(all_cards)

        for card in all_cards:
            if date_idx + card.games > len(dates):
                # 日程不足時は残りの日に詰める
                for remaining_game in range(card.games):
                    if date_idx < len(dates):
                        date_str = dates[date_idx].strftime("%Y-%m-%d")
                        self.schedule.games.append(ScheduledGame(
                            game_number=game_number, date=date_str,
                            home_team_name=card.home_team, away_team_name=card.away_team
                        ))
                        game_number += 1
                        date_idx += 1
                continue

            # 3連戦を連続日程に配置
            for g in range(card.games):
                if date_idx < len(dates):
                    date_str = dates[date_idx].strftime("%Y-%m-%d")

                    # 同日に既に試合があるチームはスキップ
                    games_on_date = [x for x in self.schedule.games if x.date == date_str]
                    teams_playing = set()
                    for x in games_on_date:
                        teams_playing.add(x.home_team_name)
                        teams_playing.add(x.away_team_name)

                    if card.home_team in teams_playing or card.away_team in teams_playing:
                        # 次の空き日を探す
                        for future_idx in range(date_idx + 1, len(dates)):
                            future_date = dates[future_idx].strftime("%Y-%m-%d")
                            future_games = [x for x in self.schedule.games if x.date == future_date]
                            future_teams = set()
                            for x in future_games:
                                future_teams.add(x.home_team_name)
                                future_teams.add(x.away_team_name)
                            if card.home_team not in future_teams and card.away_team not in future_teams:
                                date_str = future_date
                                break

                    self.schedule.games.append(ScheduledGame(
                        game_number=game_number, date=date_str,
                        home_team_name=card.home_team, away_team_name=card.away_team
                    ))
                    game_number += 1
                    date_idx += 1

        return game_number

    def _schedule_interleague_cards(self, cards: List[SeriesCard],
                                     dates: List[datetime.date],
                                     start_game_number: int) -> int:
        """交流戦カードを日程に配置（他リーグのみ）"""
        game_number = start_game_number
        date_idx = 0

        random.shuffle(cards)

        for card in cards:
            for g in range(card.games):
                if date_idx < len(dates):
                    date_str = dates[date_idx].strftime("%Y-%m-%d")

                    # 同日に既に試合があるチームはスキップ
                    games_on_date = [x for x in self.schedule.games if x.date == date_str]
                    teams_playing = set()
                    for x in games_on_date:
                        teams_playing.add(x.home_team_name)
                        teams_playing.add(x.away_team_name)

                    if card.home_team not in teams_playing and card.away_team not in teams_playing:
                        self.schedule.games.append(ScheduledGame(
                            game_number=game_number, date=date_str,
                            home_team_name=card.home_team, away_team_name=card.away_team
                        ))
                        game_number += 1

                date_idx += 1

        return game_number

    # ========================================
    # 天候・振替システム
    # ========================================

    def process_weather_for_date(self, date_str: str) -> List[ScheduledGame]:
        if not self.weather_enabled:
            return []

        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return []

        cancelled_games = []
        weather = WeatherSystem.get_weather(date)

        games_today = [g for g in self.schedule.games if g.date == date_str and g.status == GameStatus.SCHEDULED]

        for game in games_today:
            if WeatherSystem.should_cancel_game(weather):
                game.status = GameStatus.COMPLETED
                self.postponed_games.append(game)
                cancelled_games.append(game)

        return cancelled_games

    def reschedule_postponed_games(self) -> List[Tuple[ScheduledGame, str]]:
        rescheduled = []

        for game in self.postponed_games[:]:
            new_date = self._find_makeup_date(game)
            if new_date:
                game.status = GameStatus.SCHEDULED
                old_date = game.date
                game.date = new_date.strftime("%Y-%m-%d")
                self.postponed_games.remove(game)
                rescheduled.append((game, old_date))

        return rescheduled

    def _find_makeup_date(self, game: ScheduledGame) -> Optional[datetime.date]:
        try:
            original_date = datetime.datetime.strptime(game.date, "%Y-%m-%d").date()
        except:
            return None

        # シーズン延長期間を探す
        d = self.calendar.regular_season_end + datetime.timedelta(days=1)
        while d <= self.calendar.max_season_end:
            if d.weekday() != 0:
                if self._can_schedule_on_date(d, game.home_team_name, game.away_team_name):
                    return d
            d += datetime.timedelta(days=1)

        return None

    def _can_schedule_on_date(self, date: datetime.date, home: str, away: str) -> bool:
        date_str = date.strftime("%Y-%m-%d")
        games_on_date = [g for g in self.schedule.games if g.date == date_str]

        if len(games_on_date) >= 6:
            return False

        for g in games_on_date:
            if g.home_team_name in [home, away] or g.away_team_name in [home, away]:
                return False

        return True

    def is_regular_season_complete(self) -> bool:
        scheduled_games = [g for g in self.schedule.games if g.status == GameStatus.SCHEDULED]
        return len(scheduled_games) == 0 and len(self.postponed_games) == 0

    def get_postseason_start_date(self) -> datetime.date:
        return self.calendar.cs_first_start

    # ========================================
    # 二軍・三軍日程生成
    # ========================================

    def generate_farm_schedule(self, north_teams: List[Team], south_teams: List[Team], level: TeamLevel) -> Schedule:
        n_names = [t.name for t in north_teams]
        s_names = [t.name for t in south_teams]
        all_names = n_names + s_names
        n_teams = len(all_names)

        schedule = Schedule()
        games = []

        special_pairings = set()
        for i in range(0, n_teams, 2):
            if i + 1 < n_teams:
                special_pairings.add((i, i + 1))

        if level == TeamLevel.SECOND:
            base_games = 11
            special_games = 10
        else:
            base_games = 9
            special_games = 10

        for i, t1 in enumerate(all_names):
            for j, t2 in enumerate(all_names):
                if i >= j:
                    continue

                is_special = (i, j) in special_pairings or (j, i) in special_pairings
                count = special_games if is_special else base_games

                home_games = count // 2
                away_games = count - home_games

                if (i + j) % 2 == 0:
                    home_games, away_games = away_games, home_games

                for _ in range(home_games):
                    games.append((t1, t2, False))
                for _ in range(away_games):
                    games.append((t2, t1, False))

        self._assign_games_to_dates_scattered(schedule, games, level)
        return schedule

    def _assign_games_to_dates_scattered(self, schedule_obj: Schedule, all_games: List[Tuple[str, str, bool]], level: TeamLevel):
        random.shuffle(all_games)
        valid_dates = self._get_farm_valid_dates(level)

        date_schedule_map = {d: set() for d in valid_dates}
        scheduled_games_list = []
        game_number = 1

        for home, away, _ in all_games:
            found_date = None

            for _ in range(50):
                d = random.choice(valid_dates)
                teams_on_date = date_schedule_map[d]
                if home not in teams_on_date and away not in teams_on_date:
                    found_date = d
                    break

            if found_date is None:
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

        schedule_obj.games = scheduled_games_list
        schedule_obj.games.sort(key=lambda g: (g.date, g.game_number))
        for i, game in enumerate(schedule_obj.games):
            game.game_number = i + 1

    def _get_farm_valid_dates(self, level: TeamLevel) -> List[datetime.date]:
        valid_dates = []
        d = self.calendar.opening_day

        while d <= self.calendar.regular_season_end:
            if d.weekday() != 0:
                valid_dates.append(d)
            d += datetime.timedelta(days=1)

        return valid_dates

    # ========================================
    # ユーティリティ
    # ========================================

    def get_team_schedule(self, team_name: str) -> List[ScheduledGame]:
        return [g for g in self.schedule.games
                if g.home_team_name == team_name or g.away_team_name == team_name]

    def get_next_game(self, team_name: str, after_date: str = None) -> Optional[ScheduledGame]:
        for game in self.schedule.games:
            if game.status != GameStatus.SCHEDULED:
                continue
            if after_date and game.date <= after_date:
                continue
            if game.home_team_name == team_name or game.away_team_name == team_name:
                return game
        return None

    def get_games_for_date(self, date_str: str) -> List[ScheduledGame]:
        return [g for g in self.schedule.games if g.date == date_str]

    def is_interleague_period(self, date_str: str) -> bool:
        try:
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return self.calendar.interleague_start <= d <= self.calendar.interleague_end
        except:
            return False

    def is_allstar_break(self, date_str: str) -> bool:
        try:
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            allstar_rest_start = self.calendar.allstar_day1 - datetime.timedelta(days=1)
            allstar_rest_end = self.calendar.allstar_day2 + datetime.timedelta(days=1)
            return allstar_rest_start <= d <= allstar_rest_end
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


# ========================================
# オールスターゲームエンジン
# ========================================

@dataclass
class AllStarSelection:
    """オールスター選出選手"""
    player: Player
    team_name: str
    position: Position
    votes: int = 0
    is_starter: bool = False


class AllStarGameEngine:
    """オールスターゲーム管理"""

    def __init__(self, year: int, all_teams: List[Team]):
        self.year = year
        self.all_teams = all_teams
        self.north_roster: List[AllStarSelection] = []
        self.south_roster: List[AllStarSelection] = []
        self.game1_result: Optional[Tuple[int, int]] = None
        self.game2_result: Optional[Tuple[int, int]] = None

    def select_allstar_players(self) -> Tuple[List[AllStarSelection], List[AllStarSelection]]:
        """オールスター選手を選出（成績ベース）"""
        from models import League

        north_teams = [t for t in self.all_teams if t.league == League.NORTH]
        south_teams = [t for t in self.all_teams if t.league == League.SOUTH]

        self.north_roster = self._select_league_roster(north_teams)
        self.south_roster = self._select_league_roster(south_teams)

        return self.north_roster, self.south_roster

    def _select_league_roster(self, teams: List[Team]) -> List[AllStarSelection]:
        """リーグのオールスターロースターを選出（28名）"""
        roster = []

        # 各ポジション最低1名 + 成績上位者
        all_players = []
        for team in teams:
            for player in team.players:
                if player.team_level == TeamLevel.FIRST and not player.is_injured:
                    all_players.append((player, team.name))

        # 投手（12名）
        pitchers = [(p, t) for p, t in all_players if p.position == Position.PITCHER]
        pitchers.sort(key=lambda x: (x[0].record.wins, -x[0].record.era), reverse=True)
        for i, (p, t) in enumerate(pitchers[:12]):
            roster.append(AllStarSelection(
                player=p, team_name=t, position=p.position,
                votes=1000 - i * 50, is_starter=(i < 1)
            ))

        # 捕手（3名）
        catchers = [(p, t) for p, t in all_players if p.position == Position.CATCHER]
        catchers.sort(key=lambda x: x[0].record.ops, reverse=True)
        for i, (p, t) in enumerate(catchers[:3]):
            roster.append(AllStarSelection(
                player=p, team_name=t, position=p.position,
                votes=800 - i * 50, is_starter=(i == 0)
            ))

        # 内野手（7名）
        infielders = [(p, t) for p, t in all_players if p.position in [
            Position.FIRST, Position.SECOND, Position.THIRD, Position.SHORTSTOP
        ]]
        infielders.sort(key=lambda x: x[0].record.ops, reverse=True)
        for i, (p, t) in enumerate(infielders[:7]):
            roster.append(AllStarSelection(
                player=p, team_name=t, position=p.position,
                votes=900 - i * 40, is_starter=(i < 4)
            ))

        # 外野手（6名）
        outfielders = [(p, t) for p, t in all_players if p.position in [
            Position.LEFT, Position.CENTER, Position.RIGHT
        ]]
        outfielders.sort(key=lambda x: x[0].record.ops, reverse=True)
        for i, (p, t) in enumerate(outfielders[:6]):
            roster.append(AllStarSelection(
                player=p, team_name=t, position=p.position,
                votes=850 - i * 40, is_starter=(i < 3)
            ))

        return roster

    def simulate_allstar_games(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """オールスター2試合をシミュレート"""
        # 簡易シミュレーション
        self.game1_result = (random.randint(2, 8), random.randint(2, 8))
        self.game2_result = (random.randint(2, 8), random.randint(2, 8))

        return self.game1_result, self.game2_result

    def get_winner(self) -> str:
        """オールスター勝利リーグを取得"""
        if not self.game1_result or not self.game2_result:
            return "未定"

        north_wins = 0
        south_wins = 0

        if self.game1_result[0] > self.game1_result[1]:
            north_wins += 1
        elif self.game1_result[1] > self.game1_result[0]:
            south_wins += 1

        if self.game2_result[0] > self.game2_result[1]:
            north_wins += 1
        elif self.game2_result[1] > self.game2_result[0]:
            south_wins += 1

        if north_wins > south_wins:
            return "North League"
        elif south_wins > north_wins:
            return "South League"
        return "引き分け"


# ========================================
# ポストシーズン（CS・日本シリーズ）エンジン
# ========================================

class PostseasonStage(Enum):
    CS_FIRST = "CSファーストステージ"
    CS_FINAL = "CSファイナルステージ"
    JAPAN_SERIES = "日本シリーズ"


@dataclass
class PostseasonSeries:
    """ポストシーズンシリーズ"""
    stage: PostseasonStage
    league: str  # "north", "south", or "japan_series"
    team1: str  # 上位チーム（ホームアドバンテージ）
    team2: str
    team1_wins: int = 0
    team2_wins: int = 0
    games_played: int = 0
    max_games: int = 3  # CSファースト=3, CSファイナル=6, 日本S=7
    team1_advantage: int = 0  # CSファイナルで1位チームに1勝アドバンテージ
    winner: Optional[str] = None
    schedule: List[ScheduledGame] = field(default_factory=list)


class PostseasonEngine:
    """ポストシーズン管理エンジン"""

    def __init__(self, year: int, calendar: SeasonCalendar):
        self.year = year
        self.calendar = calendar
        self.cs_north_first: Optional[PostseasonSeries] = None
        self.cs_south_first: Optional[PostseasonSeries] = None
        self.cs_north_final: Optional[PostseasonSeries] = None
        self.cs_south_final: Optional[PostseasonSeries] = None
        self.japan_series: Optional[PostseasonSeries] = None
        self.current_stage: Optional[PostseasonStage] = None

    def initialize_climax_series(self, north_standings: List[Tuple[str, int]],
                                   south_standings: List[Tuple[str, int]]):
        """クライマックスシリーズを初期化"""

        # CSファーストステージ（2位 vs 3位、2勝先勝、2位ホーム）
        if len(north_standings) >= 3:
            self.cs_north_first = PostseasonSeries(
                stage=PostseasonStage.CS_FIRST,
                league="north",
                team1=north_standings[1][0],  # 2位
                team2=north_standings[2][0],  # 3位
                max_games=3
            )
            self._generate_series_schedule(self.cs_north_first, self.calendar.cs_first_start)

        if len(south_standings) >= 3:
            self.cs_south_first = PostseasonSeries(
                stage=PostseasonStage.CS_FIRST,
                league="south",
                team1=south_standings[1][0],
                team2=south_standings[2][0],
                max_games=3
            )
            self._generate_series_schedule(self.cs_south_first, self.calendar.cs_first_start)

        # CSファイナルステージ（1位 vs ファースト勝者、4勝先勝、1位に1勝アドバンテージ）
        if len(north_standings) >= 1:
            self.cs_north_final = PostseasonSeries(
                stage=PostseasonStage.CS_FINAL,
                league="north",
                team1=north_standings[0][0],  # 1位
                team2="ファースト勝者",  # プレースホルダー
                max_games=6,
                team1_advantage=1  # 1勝アドバンテージ
            )

        if len(south_standings) >= 1:
            self.cs_south_final = PostseasonSeries(
                stage=PostseasonStage.CS_FINAL,
                league="south",
                team1=south_standings[0][0],
                team2="ファースト勝者",
                max_games=6,
                team1_advantage=1
            )

        self.current_stage = PostseasonStage.CS_FIRST

    def _generate_series_schedule(self, series: PostseasonSeries, start_date: datetime.date):
        """シリーズの日程を生成"""
        series.schedule = []
        current_date = start_date

        for i in range(series.max_games):
            date_str = current_date.strftime("%Y-%m-%d")

            # ホーム・アウェイの決定
            if series.stage == PostseasonStage.JAPAN_SERIES:
                # 2-3-2方式
                if i < 2 or i >= 5:
                    home = series.team1
                    away = series.team2
                else:
                    home = series.team2
                    away = series.team1
            else:
                # CS: 上位チームが全試合ホーム
                home = series.team1
                away = series.team2

            series.schedule.append(ScheduledGame(
                game_number=i + 1, date=date_str,
                home_team_name=home, away_team_name=away
            ))

            current_date += datetime.timedelta(days=1)

            # 日本シリーズ移動日
            if series.stage == PostseasonStage.JAPAN_SERIES and (i == 1 or i == 4):
                current_date += datetime.timedelta(days=1)

    def record_game_result(self, series: PostseasonSeries, team1_score: int, team2_score: int):
        """試合結果を記録"""
        series.games_played += 1

        if team1_score > team2_score:
            series.team1_wins += 1
        else:
            series.team2_wins += 1

        # 勝敗判定
        wins_needed = (series.max_games // 2) + 1
        if series.stage == PostseasonStage.CS_FINAL:
            wins_needed = 4  # アドバンテージ込みで4勝必要

        total_team1_wins = series.team1_wins + series.team1_advantage

        if total_team1_wins >= wins_needed:
            series.winner = series.team1
        elif series.team2_wins >= wins_needed:
            series.winner = series.team2

    def advance_to_cs_final(self):
        """CSファイナルに進出"""
        if self.cs_north_first and self.cs_north_first.winner:
            self.cs_north_final.team2 = self.cs_north_first.winner
            self._generate_series_schedule(self.cs_north_final, self.calendar.cs_final_start)

        if self.cs_south_first and self.cs_south_first.winner:
            self.cs_south_final.team2 = self.cs_south_first.winner
            self._generate_series_schedule(self.cs_south_final, self.calendar.cs_final_start)

        self.current_stage = PostseasonStage.CS_FINAL

    def initialize_japan_series(self):
        """日本シリーズを初期化"""
        if not self.cs_north_final or not self.cs_south_final:
            return

        north_champion = self.cs_north_final.winner
        south_champion = self.cs_south_final.winner

        if not north_champion or not south_champion:
            return

        # 年によってホームアドバンテージを交互
        if self.year % 2 == 0:
            team1 = south_champion
            team2 = north_champion
        else:
            team1 = north_champion
            team2 = south_champion

        self.japan_series = PostseasonSeries(
            stage=PostseasonStage.JAPAN_SERIES,
            league="japan_series",
            team1=team1,
            team2=team2,
            max_games=7
        )
        self._generate_series_schedule(self.japan_series, self.calendar.japan_series_start)
        self.current_stage = PostseasonStage.JAPAN_SERIES

    def is_postseason_complete(self) -> bool:
        """ポストシーズンが完了したか"""
        return self.japan_series is not None and self.japan_series.winner is not None

    def get_japan_champion(self) -> Optional[str]:
        """日本一チームを取得"""
        if self.japan_series:
            return self.japan_series.winner
        return None


# ========================================
# シーズン状態管理
# ========================================

class SeasonPhase(Enum):
    PRE_SEASON = "プレシーズン"
    REGULAR_SEASON = "レギュラーシーズン"
    INTERLEAGUE = "交流戦"
    ALLSTAR_BREAK = "オールスター"
    CLIMAX_SERIES = "クライマックスシリーズ"
    JAPAN_SERIES = "日本シリーズ"
    OFF_SEASON = "オフシーズン"


class SeasonManager:
    """シーズン全体の状態管理"""

    def __init__(self, year: int):
        self.year = year
        self.calendar = SeasonCalendar.create(year)
        self.phase = SeasonPhase.PRE_SEASON
        self.postseason_complete = False
        self.allstar_engine: Optional[AllStarGameEngine] = None
        self.postseason_engine: Optional[PostseasonEngine] = None

    def get_current_phase(self, date_str: str) -> SeasonPhase:
        try:
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return SeasonPhase.REGULAR_SEASON

        if d < self.calendar.opening_day:
            return SeasonPhase.PRE_SEASON

        allstar_rest_start = self.calendar.allstar_day1 - datetime.timedelta(days=1)
        allstar_rest_end = self.calendar.allstar_day2 + datetime.timedelta(days=1)
        if allstar_rest_start <= d <= allstar_rest_end:
            return SeasonPhase.ALLSTAR_BREAK

        if self.calendar.interleague_start <= d <= self.calendar.interleague_reserve_end:
            return SeasonPhase.INTERLEAGUE

        if d <= self.calendar.max_season_end:
            return SeasonPhase.REGULAR_SEASON

        if d >= self.calendar.cs_first_start:
            if self.postseason_complete:
                return SeasonPhase.OFF_SEASON
            if self.postseason_engine:
                if self.postseason_engine.current_stage == PostseasonStage.JAPAN_SERIES:
                    return SeasonPhase.JAPAN_SERIES
            return SeasonPhase.CLIMAX_SERIES

        return SeasonPhase.REGULAR_SEASON

    def is_off_season(self, date_str: str) -> bool:
        return self.get_current_phase(date_str) == SeasonPhase.OFF_SEASON

    def mark_postseason_complete(self):
        self.postseason_complete = True
        self.phase = SeasonPhase.OFF_SEASON

    def initialize_allstar(self, all_teams: List[Team]):
        """オールスターを初期化"""
        self.allstar_engine = AllStarGameEngine(self.year, all_teams)
        self.allstar_engine.select_allstar_players()

    def initialize_postseason(self, north_standings: List[Tuple[str, int]],
                               south_standings: List[Tuple[str, int]]):
        """ポストシーズンを初期化"""
        self.postseason_engine = PostseasonEngine(self.year, self.calendar)
        self.postseason_engine.initialize_climax_series(north_standings, south_standings)


def create_league_schedule(year: int, north_teams: List[Team], south_teams: List[Team]) -> Schedule:
    engine = LeagueScheduleEngine(year)
    return engine.generate_schedule(north_teams, south_teams)
