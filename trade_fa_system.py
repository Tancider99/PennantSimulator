# -*- coding: utf-8 -*-
"""
トレード・FA・契約システム
"""
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple
from models import Player, Team, Position, PitchType


class ContractType(Enum):
    """契約タイプ"""
    STANDARD = ("通常契約", 1)
    LONG_TERM = ("複数年契約", 3)
    FA = ("FA契約", 1)
    ROOKIE = ("育成契約", 1)
    FOREIGN = ("外国人契約", 1)
    
    def __init__(self, display_name: str, max_years: int):
        self.display_name = display_name
        self.max_years = max_years


@dataclass
class Contract:
    """契約情報"""
    player: Player
    team: Team
    contract_type: ContractType
    salary: int
    years_remaining: int
    no_trade_clause: bool = False
    incentives: dict = None
    
    def __post_init__(self):
        if self.incentives is None:
            self.incentives = {}
    
    @property
    def annual_value(self) -> str:
        """年俸表示"""
        if self.salary >= 100000000:
            return f"{self.salary // 100000000}億{(self.salary % 100000000) // 10000:,}万円"
        else:
            return f"{self.salary // 10000:,}万円"


@dataclass
class TradeOffer:
    """トレードオファー"""
    offering_team: Team
    receiving_team: Team
    players_offered: List[Player]
    players_requested: List[Player]
    cash_offered: int = 0
    is_accepted: bool = False
    
    def evaluate_fairness(self) -> float:
        """トレードの公平性を評価 (0.0-2.0, 1.0が均衡)"""
        offered_value = sum(self._calculate_player_value(p) for p in self.players_offered)
        offered_value += self.cash_offered / 100000000  # 1億円 = 1ポイント
        
        requested_value = sum(self._calculate_player_value(p) for p in self.players_requested)
        
        if requested_value == 0:
            return 2.0 if offered_value > 0 else 1.0
        
        return offered_value / requested_value
    
    @staticmethod
    def _calculate_player_value(player: Player) -> float:
        """選手の価値を計算"""
        if player.position == Position.PITCHER:
            base_value = player.stats.overall_pitching()
        else:
            base_value = player.stats.overall_batting()
        
        # 年齢調整
        if player.age < 25:
            age_factor = 1.3  # 若手ボーナス
        elif player.age < 30:
            age_factor = 1.1
        elif player.age < 33:
            age_factor = 0.9
        else:
            age_factor = 0.7
        
        # 年俸調整（高年俸は価値減）
        salary_factor = 1.0 - (player.salary / 1000000000) * 0.2
        
        return base_value * age_factor * max(0.5, salary_factor)


class TradeManager:
    """トレード管理"""
    
    def __init__(self, teams: List[Team]):
        self.teams = teams
        self.completed_trades: List[TradeOffer] = []
        self.pending_offers: List[TradeOffer] = []
    
    def propose_trade(self, offer: TradeOffer) -> bool:
        """トレードを提案"""
        fairness = offer.evaluate_fairness()
        
        # AI判断: 0.8-1.3の範囲なら検討
        if 0.8 <= fairness <= 1.3:
            # ニーズに合っているかチェック
            if self._check_team_needs(offer):
                acceptance_chance = min(0.9, fairness * 0.6)
                if random.random() < acceptance_chance:
                    offer.is_accepted = True
                    self._execute_trade(offer)
                    return True
        
        return False
    
    def _check_team_needs(self, offer: TradeOffer) -> bool:
        """チームのニーズをチェック"""
        receiving_team = offer.receiving_team
        
        for player in offer.players_offered:
            # 弱いポジションの補強か
            position_strength = self._get_position_strength(receiving_team, player.position)
            if position_strength < 10:  # 弱いポジション
                return True
        
        return False
    
    def _get_position_strength(self, team: Team, position: Position) -> float:
        """ポジションの強さを取得"""
        players_at_position = [p for p in team.players if p.position == position]
        if not players_at_position:
            return 0
        
        if position == Position.PITCHER:
            return sum(p.stats.overall_pitching() for p in players_at_position) / len(players_at_position)
        else:
            return sum(p.stats.overall_batting() for p in players_at_position) / len(players_at_position)
    
    def _execute_trade(self, offer: TradeOffer):
        """トレードを実行"""
        # 選手移動
        for player in offer.players_offered:
            offer.offering_team.players.remove(player)
            offer.receiving_team.players.append(player)
        
        for player in offer.players_requested:
            offer.receiving_team.players.remove(player)
            offer.offering_team.players.append(player)
        
        # 金銭移動
        if offer.cash_offered > 0:
            offer.offering_team.budget -= offer.cash_offered
            offer.receiving_team.budget += offer.cash_offered
        
        self.completed_trades.append(offer)
    
    def generate_ai_trade_offers(self) -> List[TradeOffer]:
        """AIがトレードオファーを生成"""
        offers = []
        
        for team in self.teams:
            # 弱点ポジションを特定
            weakest_position = self._find_weakest_position(team)
            if weakest_position is None:
                continue
            
            # 他チームから適切な選手を探す
            for other_team in self.teams:
                if other_team == team:
                    continue
                
                # 候補選手を探す
                candidates = [p for p in other_team.players 
                             if p.position == weakest_position
                             and TradeOffer._calculate_player_value(p) > 8]
                
                if candidates:
                    target = random.choice(candidates)
                    
                    # 交換選手を選ぶ
                    tradeable = [p for p in team.players 
                                if TradeOffer._calculate_player_value(p) >= 
                                   TradeOffer._calculate_player_value(target) * 0.7]
                    
                    if tradeable:
                        offer_player = random.choice(tradeable)
                        offer = TradeOffer(
                            offering_team=team,
                            receiving_team=other_team,
                            players_offered=[offer_player],
                            players_requested=[target]
                        )
                        offers.append(offer)
        
        return offers[:3]  # 最大3件
    
    def _find_weakest_position(self, team: Team) -> Optional[Position]:
        """最も弱いポジションを見つける"""
        positions = [Position.CATCHER, Position.FIRST, Position.SECOND,
                    Position.THIRD, Position.SHORTSTOP, Position.OUTFIELD]
        
        weakest = None
        weakest_strength = float('inf')
        
        for pos in positions:
            strength = self._get_position_strength(team, pos)
            if strength < weakest_strength:
                weakest_strength = strength
                weakest = pos
        
        return weakest if weakest_strength < 10 else None


class FreeAgentMarket:
    """FA市場"""
    
    def __init__(self):
        self.available_fas: List[Player] = []
        self.domestic_fas: List[Player] = []
        self.international_fas: List[Player] = []
    
    def generate_fa_class(self, teams: List[Team]):
        """FA資格選手を生成"""
        self.domestic_fas = []
        
        for team in teams:
            for player in team.players:
                # FA資格: 8年以上または7年目で優秀成績
                if player.years_pro >= 8:
                    if random.random() < 0.3:  # 30%がFA宣言
                        self.domestic_fas.append(player)
                elif player.years_pro >= 7:
                    if player.position == Position.PITCHER:
                        if player.record.wins >= 10 or player.record.saves >= 20:
                            if random.random() < 0.4:
                                self.domestic_fas.append(player)
                    else:
                        if player.record.batting_average >= 0.280 or player.record.home_runs >= 20:
                            if random.random() < 0.4:
                                self.domestic_fas.append(player)
    
    def generate_international_fas(self, count: int = 10):
        """外国人FA選手を生成"""
        from player_generator import create_foreign_free_agent
        
        self.international_fas = []
        
        positions = [Position.PITCHER, Position.PITCHER, Position.PITCHER,
                    Position.CATCHER, Position.FIRST, Position.SECOND,
                    Position.THIRD, Position.SHORTSTOP, Position.OUTFIELD, Position.OUTFIELD]
        
        for pos in random.sample(positions, count):
            pitch_type = None
            if pos == Position.PITCHER:
                pitch_type = random.choice([PitchType.STARTER, PitchType.RELIEVER, PitchType.CLOSER])
            
            player = create_foreign_free_agent(pos, pitch_type)
            self.international_fas.append(player)
    
    def sign_player(self, player: Player, team: Team, salary: int, years: int) -> Contract:
        """選手と契約"""
        # FA市場から削除
        if player in self.domestic_fas:
            self.domestic_fas.remove(player)
        if player in self.international_fas:
            self.international_fas.remove(player)
        
        # チームに追加
        player.salary = salary
        team.players.append(player)
        team.budget -= salary
        
        contract_type = ContractType.FA if player in self.domestic_fas else ContractType.FOREIGN
        
        return Contract(
            player=player,
            team=team,
            contract_type=contract_type,
            salary=salary,
            years_remaining=years
        )
    
    def estimate_market_value(self, player: Player) -> Tuple[int, int]:
        """市場価値を推定 (最低, 最高)"""
        if player.position == Position.PITCHER:
            base_value = player.stats.overall_pitching() * 10000000
        else:
            base_value = player.stats.overall_batting() * 10000000
        
        # 年齢調整
        if player.age < 28:
            base_value *= 1.3
        elif player.age < 32:
            base_value *= 1.0
        else:
            base_value *= 0.7
        
        # 成績ボーナス
        if player.position == Position.PITCHER:
            if player.record.wins >= 15:
                base_value *= 1.5
            elif player.record.saves >= 30:
                base_value *= 1.4
        else:
            if player.record.home_runs >= 30:
                base_value *= 1.4
            if player.record.batting_average >= 0.300:
                base_value *= 1.3
        
        min_value = int(base_value * 0.8)
        max_value = int(base_value * 1.4)
        
        return min_value, max_value


@dataclass
class ContractNegotiation:
    """契約交渉"""
    player: Player
    team: Team
    initial_offer: int
    player_demand: int
    rounds: int = 0
    final_salary: int = 0
    is_agreed: bool = False
    
    def negotiate_round(self) -> bool:
        """交渉ラウンド"""
        self.rounds += 1
        
        gap = self.player_demand - self.initial_offer
        
        if gap <= 0:
            self.final_salary = self.initial_offer
            self.is_agreed = True
            return True
        
        # 各ラウンドで歩み寄り
        if self.rounds <= 3:
            self.initial_offer = int(self.initial_offer * 1.1)
            self.player_demand = int(self.player_demand * 0.95)
            
            new_gap = self.player_demand - self.initial_offer
            
            if new_gap <= self.initial_offer * 0.05:  # 5%以内
                self.final_salary = (self.initial_offer + self.player_demand) // 2
                self.is_agreed = True
                return True
        
        return False
    
    def auto_negotiate(self) -> bool:
        """自動交渉"""
        while self.rounds < 5 and not self.is_agreed:
            self.negotiate_round()
        
        if not self.is_agreed:
            # 最終オファー
            if random.random() < 0.5:
                self.final_salary = self.player_demand
                self.is_agreed = True
        
        return self.is_agreed


class SalaryManager:
    """年俸管理"""
    
    @staticmethod
    def calculate_raise(player: Player) -> int:
        """年俸アップを計算"""
        current_salary = player.salary
        
        # 成績ベースの査定
        if player.position == Position.PITCHER:
            performance_factor = SalaryManager._evaluate_pitcher_performance(player)
        else:
            performance_factor = SalaryManager._evaluate_batter_performance(player)
        
        # 年齢調整
        if player.age < 28:
            age_factor = 1.1
        elif player.age < 32:
            age_factor = 1.0
        elif player.age < 35:
            age_factor = 0.9
        else:
            age_factor = 0.8
        
        # 年俸アップ率 (-20% ~ +50%)
        raise_rate = (performance_factor - 1.0) * 0.5 * age_factor
        raise_rate = max(-0.2, min(0.5, raise_rate))
        
        new_salary = int(current_salary * (1 + raise_rate))
        
        # 最低保証
        new_salary = max(4400000, new_salary)  # 最低年俸440万円
        
        return new_salary
    
    @staticmethod
    def _evaluate_pitcher_performance(player: Player) -> float:
        """投手成績評価"""
        factor = 1.0
        
        if player.record.wins >= 15:
            factor += 0.3
        elif player.record.wins >= 10:
            factor += 0.15
        elif player.record.wins >= 5:
            factor += 0.05
        
        if player.record.saves >= 30:
            factor += 0.25
        elif player.record.saves >= 20:
            factor += 0.15
        
        if player.record.innings_pitched >= 100:
            if player.record.era < 2.50:
                factor += 0.3
            elif player.record.era < 3.00:
                factor += 0.15
            elif player.record.era > 4.50:
                factor -= 0.15
        
        return factor
    
    @staticmethod
    def _evaluate_batter_performance(player: Player) -> float:
        """野手成績評価"""
        factor = 1.0
        
        if player.record.at_bats >= 300:
            if player.record.batting_average >= 0.320:
                factor += 0.3
            elif player.record.batting_average >= 0.300:
                factor += 0.2
            elif player.record.batting_average >= 0.280:
                factor += 0.1
            elif player.record.batting_average < 0.220:
                factor -= 0.15
        
        if player.record.home_runs >= 40:
            factor += 0.3
        elif player.record.home_runs >= 30:
            factor += 0.2
        elif player.record.home_runs >= 20:
            factor += 0.1
        
        if player.record.rbis >= 100:
            factor += 0.15
        elif player.record.rbis >= 80:
            factor += 0.08
        
        return factor
    
    @staticmethod
    def format_salary(salary: int) -> str:
        """年俸を表示用にフォーマット"""
        if salary >= 100000000:
            oku = salary // 100000000
            man = (salary % 100000000) // 10000
            if man > 0:
                return f"{oku}億{man:,}万円"
            return f"{oku}億円"
        else:
            return f"{salary // 10000:,}万円"
