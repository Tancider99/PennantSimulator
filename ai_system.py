"""
AI System - 高度なゲーム支援システム
選手育成、ラインナップ最適化、投手ローテーション管理、試合戦術、チーム編成などを自動化
"""

from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import random
import math


class AITrainingStrategy(Enum):
    """育成戦略"""
    BALANCED = "バランス"      # 全体的に均等に育成
    WEAKNESS = "弱点強化"      # 弱点を優先的に強化
    STRENGTH = "長所伸ばし"    # 長所をさらに伸ばす
    YOUNG_FOCUS = "若手重視"   # 若手選手に投資
    VETERAN_MAINTAIN = "主力維持"  # ベテランの能力維持
    POSITION_FOCUS = "ポジション特化"  # ポジション別に最適化


class AITacticStrategy(Enum):
    """試合戦術戦略"""
    AGGRESSIVE = "攻撃的"      # 積極的に攻める
    CONSERVATIVE = "堅実"      # 確実に得点を狙う
    BALANCED = "バランス"      # 状況に応じて判断
    SMALL_BALL = "スモールボール"  # 機動力重視
    POWER_GAME = "パワー野球"   # 長打力重視


class AILineupStrategy(Enum):
    """ラインナップ戦略"""
    STANDARD = "標準"          # 従来型の打順
    OBP_FOCUSED = "出塁重視"   # 出塁率重視の打順
    POWER_TOP = "パワー上位"   # 上位打線に強打者
    SPEED_TOP = "機動力上位"   # 上位に俊足打者
    BALANCED = "バランス型"    # 能力バランス重視


@dataclass
class AIRecommendation:
    """AI推奨結果"""
    action: str
    reason: str
    confidence: float  # 0.0-1.0
    priority: int  # 1-10 (10が最高)
    details: Dict = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class PlayerEvaluation:
    """選手評価結果"""
    overall_score: float
    offense_score: float
    defense_score: float
    potential_score: float
    value_score: float  # 年俸対比価値
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str


@dataclass
class TeamAnalysis:
    """チーム分析結果"""
    overall_rating: float
    offense_rating: float
    defense_rating: float
    pitching_rating: float
    depth_rating: float  # 層の厚さ
    weak_positions: List[str]
    strong_positions: List[str]
    recommendations: List[str]


class AIManager:
    """AI管理クラス - チーム運営を高度にサポート"""
    
    def __init__(self):
        self.training_strategy = AITrainingStrategy.WEAKNESS
        self.tactic_strategy = AITacticStrategy.BALANCED
        self.lineup_strategy = AILineupStrategy.STANDARD
        
        # 学習データ（試合結果から戦術を調整）
        self._game_history = []
        self._tactic_success_rate = {}
    
    # ===============================
    # チーム分析AI
    # ===============================
    
    def analyze_team(self, team) -> TeamAnalysis:
        """チームを総合分析"""
        batters = [p for p in team.players if p.position.name != 'PITCHER']
        pitchers = [p for p in team.players if p.position.name == 'PITCHER']
        
        # 攻撃力評価
        if batters:
            offense = sum(p.stats.contact * 0.35 + p.stats.power * 0.35 + 
                         p.stats.run * 0.15 + getattr(p.stats, 'eye', 50) * 0.15 
                         for p in batters) / len(batters)
        else:
            offense = 50
        
        # 守備力評価
        if batters:
            defense = sum(p.stats.fielding * 0.6 + p.stats.arm * 0.4 
                         for p in batters) / len(batters)
        else:
            defense = 50
        
        # 投手力評価
        if pitchers:
            pitching = sum(p.stats.control * 0.35 + p.stats.breaking * 0.30 + 
                          p.stats.speed * 0.20 + p.stats.stamina * 0.15 
                          for p in pitchers) / len(pitchers)
        else:
            pitching = 50
        
        # 層の厚さ（控え選手の能力）
        depth = self._calculate_depth(team)
        
        # 弱点・強みポジション分析
        weak_positions = self._find_weak_positions(team)
        strong_positions = self._find_strong_positions(team)
        
        # 総合評価
        overall = offense * 0.35 + defense * 0.15 + pitching * 0.40 + depth * 0.10
        
        # 改善推奨
        recommendations = self._generate_team_recommendations(team, weak_positions)
        
        return TeamAnalysis(
            overall_rating=overall,
            offense_rating=offense,
            defense_rating=defense,
            pitching_rating=pitching,
            depth_rating=depth,
            weak_positions=weak_positions,
            strong_positions=strong_positions,
            recommendations=recommendations
        )
    
    def _calculate_depth(self, team) -> float:
        """チームの層の厚さを計算"""
        if len(team.players) < 25:
            return 30
        
        # スタメン外の選手の平均能力
        starters = set(getattr(team, 'current_lineup', []))
        starters.add(getattr(team, 'starting_pitcher_idx', -1))
        
        bench = [p for i, p in enumerate(team.players) if i not in starters]
        if not bench:
            return 50
        
        bench_avg = sum(p.stats.overall_batting() if p.position.name != 'PITCHER' 
                       else p.stats.overall_pitching() for p in bench) / len(bench)
        return min(100, bench_avg * 1.2)
    
    def _find_weak_positions(self, team) -> List[str]:
        """弱点ポジションを特定"""
        position_scores = {}
        for p in team.players:
            pos = p.position.name
            score = p.stats.overall_batting() if pos != 'PITCHER' else p.stats.overall_pitching()
            if pos not in position_scores:
                position_scores[pos] = []
            position_scores[pos].append(score)
        
        weak = []
        for pos, scores in position_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 50:
                weak.append(pos)
        
        return weak
    
    def _find_strong_positions(self, team) -> List[str]:
        """強みポジションを特定"""
        position_scores = {}
        for p in team.players:
            pos = p.position.name
            score = p.stats.overall_batting() if pos != 'PITCHER' else p.stats.overall_pitching()
            if pos not in position_scores:
                position_scores[pos] = []
            position_scores[pos].append(score)
        
        strong = []
        for pos, scores in position_scores.items():
            avg = sum(scores) / len(scores)
            if avg >= 65:
                strong.append(pos)
        
        return strong
    
    def _generate_team_recommendations(self, team, weak_positions: List[str]) -> List[str]:
        """チーム改善の推奨を生成"""
        recs = []
        
        if weak_positions:
            for pos in weak_positions[:3]:
                recs.append(f"{pos}の補強が必要")
        
        # 年齢構成チェック
        avg_age = sum(p.age for p in team.players) / len(team.players) if team.players else 25
        if avg_age > 30:
            recs.append("チームの高齢化が進行中。若手の育成を推奨")
        elif avg_age < 25:
            recs.append("若手中心のチーム。経験豊富な選手の獲得を検討")
        
        # 投手陣チェック
        pitchers = [p for p in team.players if p.position.name == 'PITCHER']
        if len(pitchers) < 10:
            recs.append("投手陣の層が薄い。補強が必要")
        
        return recs[:5]  # 最大5件
    
    # ===============================
    # 選手評価AI
    # ===============================
    
    def evaluate_player(self, player) -> PlayerEvaluation:
        """選手を総合評価"""
        is_pitcher = player.position.name == 'PITCHER'
        
        if is_pitcher:
            offense = 0
            defense = (player.stats.control * 0.40 + player.stats.breaking * 0.30 + 
                      player.stats.speed * 0.20 + player.stats.stamina * 0.10)
        else:
            offense = (player.stats.contact * 0.35 + player.stats.power * 0.30 + 
                      player.stats.run * 0.20 + getattr(player.stats, 'eye', 50) * 0.15)
            defense = player.stats.fielding * 0.7 + player.stats.arm * 0.3
        
        # ポテンシャル評価
        potential = player.growth.potential if hasattr(player, 'growth') and player.growth else 5
        potential_score = potential * 10
        
        # 年俸対比価値
        salary = getattr(player, 'salary', 1000)
        if is_pitcher:
            performance = defense
        else:
            performance = offense * 0.6 + defense * 0.4
        
        expected_salary = performance * 50  # 能力50で2500万程度
        value_score = min(100, (expected_salary / max(salary, 100)) * 50)
        
        # 総合スコア
        overall = performance * 0.7 + potential_score * 0.2 + value_score * 0.1
        
        # 強み・弱み分析
        strengths, weaknesses = self._analyze_player_traits(player)
        
        # 推奨コメント
        recommendation = self._generate_player_recommendation(player, overall, potential)
        
        return PlayerEvaluation(
            overall_score=overall,
            offense_score=offense,
            defense_score=defense,
            potential_score=potential_score,
            value_score=value_score,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation
        )
    
    def _analyze_player_traits(self, player) -> Tuple[List[str], List[str]]:
        """選手の強み・弱みを分析"""
        strengths = []
        weaknesses = []
        
        if player.position.name == 'PITCHER':
            stats = {
                '球速': player.stats.speed,
                '制球': player.stats.control,
                '変化球': player.stats.breaking,
                'スタミナ': player.stats.stamina
            }
        else:
            stats = {
                'ミート': player.stats.contact,
                'パワー': player.stats.power,
                '走力': player.stats.run,
                '守備': player.stats.fielding,
                '肩力': player.stats.arm
            }
        
        for name, value in stats.items():
            if value >= 70:
                strengths.append(f"{name}が優秀")
            elif value <= 35:
                weaknesses.append(f"{name}が課題")
        
        # 年齢による評価
        if player.age <= 23:
            strengths.append("若手有望株")
        elif player.age >= 35:
            weaknesses.append("ベテラン（衰え注意）")
        
        return strengths[:3], weaknesses[:3]
    
    def _generate_player_recommendation(self, player, overall: float, potential: int) -> str:
        """選手への推奨コメントを生成"""
        if overall >= 75:
            if potential >= 7:
                return "チームの柱として期待。長期契約を検討"
            return "即戦力として活躍中"
        elif overall >= 60:
            if potential >= 7:
                return "将来性あり。育成次第で主力に"
            return "堅実な戦力。現状維持"
        elif overall >= 45:
            if player.age <= 25 and potential >= 5:
                return "まだ伸びしろあり。重点育成を"
            return "控えとして起用"
        else:
            if player.age <= 22:
                return "素材型。長期的な視点で育成"
            return "戦力外候補。トレード検討"
    
    # ===============================
    # 育成AI
    # ===============================
    
    def get_smart_training_menu(self, player, strategy: AITrainingStrategy = None) -> int:
        """選手に最適な練習メニューをAIで選択
        
        Args:
            player: 選手オブジェクト
            strategy: 育成戦略（デフォルトはインスタンスの戦略）
            
        Returns:
            int: 練習メニューのインデックス
        """
        if strategy is None:
            strategy = self.training_strategy
        
        if player.position.name == 'PITCHER':
            return self._get_pitcher_training(player, strategy)
        else:
            return self._get_batter_training(player, strategy)
    
    def _get_pitcher_training(self, player, strategy: AITrainingStrategy) -> int:
        """投手の練習メニューを選択
        投手メニュー: [0=球速, 1=制球, 2=変化球, 3=スタミナ]
        """
        stats = {
            'speed': getattr(player.stats, 'speed', 50),
            'control': getattr(player.stats, 'control', 50),
            'breaking': getattr(player.stats, 'breaking', 50),
            'stamina': getattr(player.stats, 'stamina', 50),
        }
        
        # ポテンシャルによる重み付け（高ポテンシャルは長所を伸ばしやすい）
        potential = player.growth.potential if hasattr(player, 'growth') and player.growth else 5
        
        if strategy == AITrainingStrategy.WEAKNESS:
            # 弱点強化: 最も低いステータスを選択
            stats_list = [stats['speed'], stats['control'], stats['breaking'], stats['stamina']]
            min_val = min(stats_list)
            # 同値の場合は優先度: 制球 > 球速 > 変化球 > スタミナ
            priorities = [1, 0, 2, 3]  # 制球優先
            candidates = [(i, priorities[i]) for i, v in enumerate(stats_list) if v == min_val]
            candidates.sort(key=lambda x: x[1])
            return candidates[0][0]
            
        elif strategy == AITrainingStrategy.STRENGTH:
            # 長所伸ばし: 最も高いステータスを選択（99未満の場合）
            stats_list = [stats['speed'], stats['control'], stats['breaking'], stats['stamina']]
            max_val = max([v for v in stats_list if v < 99] or stats_list)
            candidates = [i for i, v in enumerate(stats_list) if v == max_val and v < 99]
            return random.choice(candidates) if candidates else 0
            
        elif strategy == AITrainingStrategy.YOUNG_FOCUS:
            # 若手重視: 年齢が若い（25歳以下）なら球速、それ以外は制球
            if player.age <= 25:
                return 0  # 球速
            else:
                return 1  # 制球
                
        elif strategy == AITrainingStrategy.VETERAN_MAINTAIN:
            # 主力維持: 30歳以上はスタミナ、それ以外は弱点
            if player.age >= 30:
                return 3  # スタミナ
            else:
                return self._get_pitcher_training(player, AITrainingStrategy.WEAKNESS)
        
        else:  # BALANCED
            # バランス: ランダムだが極端に低いステータスには確率を上げる
            weights = [max(1, 80 - v) for v in [stats['speed'], stats['control'], 
                                                 stats['breaking'], stats['stamina']]]
            return random.choices([0, 1, 2, 3], weights=weights)[0]
    
    def _get_batter_training(self, player, strategy: AITrainingStrategy) -> int:
        """野手の練習メニューを選択
        野手メニュー: [0=ミート, 1=パワー, 2=走力, 3=守備, 4=スタミナ]
        """
        stats = {
            'contact': getattr(player.stats, 'contact', 50),
            'power': getattr(player.stats, 'power', 50),
            'run': getattr(player.stats, 'run', 50),
            'fielding': getattr(player.stats, 'fielding', 50),
            'stamina': getattr(player.stats, 'stamina', 50),
        }
        
        if strategy == AITrainingStrategy.WEAKNESS:
            # 弱点強化
            stats_list = [stats['contact'], stats['power'], stats['run'], 
                          stats['fielding'], stats['stamina']]
            min_val = min(stats_list)
            # 優先度: ミート > パワー > 守備 > 走力 > スタミナ
            priorities = [0, 1, 3, 2, 4]
            candidates = [(i, priorities[i]) for i, v in enumerate(stats_list) if v == min_val]
            candidates.sort(key=lambda x: x[1])
            return candidates[0][0]
            
        elif strategy == AITrainingStrategy.STRENGTH:
            # 長所伸ばし
            stats_list = [stats['contact'], stats['power'], stats['run'],
                          stats['fielding'], stats['stamina']]
            max_val = max([v for v in stats_list if v < 99] or stats_list)
            candidates = [i for i, v in enumerate(stats_list) if v == max_val and v < 99]
            return random.choice(candidates) if candidates else 0
            
        elif strategy == AITrainingStrategy.YOUNG_FOCUS:
            # 若手重視: 若手はパワー、それ以外はミート
            if player.age <= 25:
                return 1  # パワー
            else:
                return 0  # ミート
                
        elif strategy == AITrainingStrategy.VETERAN_MAINTAIN:
            # 主力維持
            if player.age >= 30:
                return 4  # スタミナ
            else:
                return self._get_batter_training(player, AITrainingStrategy.WEAKNESS)
        
        else:  # BALANCED
            weights = [max(1, 80 - v) for v in [stats['contact'], stats['power'],
                                                 stats['run'], stats['fielding'], stats['stamina']]]
            return random.choices([0, 1, 2, 3, 4], weights=weights)[0]
    
    def auto_set_all_training(self, players: List, strategy: AITrainingStrategy = None) -> Dict[int, int]:
        """全選手の練習メニューを自動設定
        
        Returns:
            Dict[int, int]: {選手インデックス: メニューインデックス}
        """
        result = {}
        for idx, player in enumerate(players):
            result[idx] = self.get_smart_training_menu(player, strategy)
        return result
    
    # ===============================
    # ラインナップAI
    # ===============================
    
    def optimize_lineup(self, team) -> Tuple[List, List]:
        """最適なスタメンラインナップを生成
        
        Args:
            team: チームオブジェクト
            
        Returns:
            Tuple[スタメン野手リスト(9名), 先発投手]
        """
        pitchers = [p for p in team.players if p.position.name == 'PITCHER']
        batters = [p for p in team.players if p.position.name != 'PITCHER']
        
        # 先発投手: 最も球速と制球のバランスが良い投手
        def pitcher_score(p):
            speed = getattr(p.stats, 'speed', 50)
            control = getattr(p.stats, 'control', 50)
            stamina = getattr(p.stats, 'stamina', 50)
            # 疲労度を考慮
            fatigue = 0
            if hasattr(p, 'player_status') and p.player_status:
                fatigue = getattr(p.player_status, 'fatigue', 0)
            elif hasattr(p, 'status') and p.status:
                fatigue = getattr(p.status, 'fatigue', 0)
            fatigue_penalty = fatigue * 0.5
            return speed * 0.4 + control * 0.35 + stamina * 0.25 - fatigue_penalty
        
        starting_pitcher = max(pitchers, key=pitcher_score) if pitchers else None
        
        # 野手: ポジション別に最適な選手を選ぶ
        position_priority = ['CATCHER', 'SHORTSTOP', 'SECOND_BASE', 'THIRD_BASE', 
                            'FIRST_BASE', 'LEFT_FIELD', 'CENTER_FIELD', 'RIGHT_FIELD']
        
        def batter_score(p):
            contact = getattr(p.stats, 'contact', 50)
            power = getattr(p.stats, 'power', 50)
            run = getattr(p.stats, 'run', 50)
            fielding = getattr(p.stats, 'fielding', 50)
            return contact * 0.35 + power * 0.25 + run * 0.2 + fielding * 0.2
        
        # ポジション別に最適選手を選択
        lineup = []
        used_players = set()
        
        for pos in position_priority:
            candidates = [p for p in batters 
                          if p.position.name == pos and p not in used_players]
            if candidates:
                best = max(candidates, key=batter_score)
                lineup.append(best)
                used_players.add(best)
        
        # 足りない場合は残りから補充
        while len(lineup) < 9:
            remaining = [p for p in batters if p not in used_players]
            if not remaining:
                break
            best = max(remaining, key=batter_score)
            lineup.append(best)
            used_players.add(best)
        
        # 打順の最適化
        lineup = self._optimize_batting_order(lineup)
        
        return lineup, starting_pitcher
    
    def _optimize_batting_order(self, lineup: List) -> List:
        """打順を最適化
        1番: 出塁率重視（ミート+走力）
        2番: バント・進塁重視（ミート重視）
        3番: 総合力（ミート+パワー）
        4番: パワー最大
        5番: パワー2番手
        6-9番: 残りを守備力順
        """
        if len(lineup) < 9:
            return lineup
        
        def obp_score(p):
            return getattr(p.stats, 'contact', 50) * 0.6 + getattr(p.stats, 'run', 50) * 0.4
        
        def power_score(p):
            return getattr(p.stats, 'power', 50)
        
        def overall_score(p):
            return (getattr(p.stats, 'contact', 50) * 0.5 + 
                    getattr(p.stats, 'power', 50) * 0.5)
        
        sorted_lineup = list(lineup)
        optimized = [None] * 9
        used = set()
        
        # 4番: パワー最大
        cleanup = max(sorted_lineup, key=power_score)
        optimized[3] = cleanup
        used.add(cleanup)
        
        # 3番: 総合力（4番除く）
        remaining = [p for p in sorted_lineup if p not in used]
        third = max(remaining, key=overall_score)
        optimized[2] = third
        used.add(third)
        
        # 5番: パワー2番手
        remaining = [p for p in sorted_lineup if p not in used]
        fifth = max(remaining, key=power_score)
        optimized[4] = fifth
        used.add(fifth)
        
        # 1番: 出塁率重視
        remaining = [p for p in sorted_lineup if p not in used]
        leadoff = max(remaining, key=obp_score)
        optimized[0] = leadoff
        used.add(leadoff)
        
        # 2番: ミート重視
        remaining = [p for p in sorted_lineup if p not in used]
        second = max(remaining, key=lambda p: getattr(p.stats, 'contact', 50))
        optimized[1] = second
        used.add(second)
        
        # 残り（6-9番）
        remaining = [p for p in sorted_lineup if p not in used]
        remaining.sort(key=lambda p: getattr(p.stats, 'fielding', 50), reverse=True)
        for i, p in enumerate(remaining):
            if 5 + i < 9:
                optimized[5 + i] = p
        
        return [p for p in optimized if p is not None]
    
    def optimize_lineup_advanced(self, team, strategy: AILineupStrategy = None) -> Tuple[List, str]:
        """高度なラインナップ最適化
        
        Args:
            team: チームオブジェクト
            strategy: ラインナップ戦略
        
        Returns:
            Tuple[最適化されたラインアップ, 説明]
        """
        if strategy is None:
            strategy = self.lineup_strategy
        
        batters = [p for p in team.players if p.position.name != 'PITCHER'
                  and getattr(p, 'team_level', 'first') == 'first']
        
        if len(batters) < 9:
            return [], "野手が不足しています"
        
        # ポジション別に最適な選手を選択
        lineup = self._select_best_by_position(batters)
        
        if strategy == AILineupStrategy.STANDARD:
            optimized = self._optimize_batting_order(lineup)
            desc = "標準的な打順に最適化"
        
        elif strategy == AILineupStrategy.OBP_FOCUSED:
            optimized = self._optimize_obp_focused(lineup)
            desc = "出塁率重視の打順に最適化"
        
        elif strategy == AILineupStrategy.POWER_TOP:
            optimized = self._optimize_power_top(lineup)
            desc = "上位に強打者を配置"
        
        elif strategy == AILineupStrategy.SPEED_TOP:
            optimized = self._optimize_speed_top(lineup)
            desc = "上位に俊足打者を配置"
        
        else:  # BALANCED
            optimized = self._optimize_balanced(lineup)
            desc = "バランス型の打順に最適化"
        
        return optimized, desc
    
    def _select_best_by_position(self, batters: List) -> List:
        """ポジション別に最適な選手を選択"""
        position_priority = ['CATCHER', 'SHORTSTOP', 'SECOND_BASE', 'THIRD_BASE', 
                            'FIRST_BASE', 'LEFT_FIELD', 'CENTER_FIELD', 'RIGHT_FIELD', 'DH']
        
        def batter_score(p):
            contact = getattr(p.stats, 'contact', 50)
            power = getattr(p.stats, 'power', 50)
            run = getattr(p.stats, 'run', 50)
            fielding = getattr(p.stats, 'fielding', 50)
            return contact * 0.35 + power * 0.25 + run * 0.2 + fielding * 0.2
        
        lineup = []
        used_players = set()
        
        for pos in position_priority:
            candidates = [p for p in batters 
                          if p.position.name == pos and p not in used_players]
            if candidates:
                best = max(candidates, key=batter_score)
                lineup.append(best)
                used_players.add(best)
        
        # 足りない場合は残りから補充
        while len(lineup) < 9:
            remaining = [p for p in batters if p not in used_players]
            if not remaining:
                break
            best = max(remaining, key=batter_score)
            lineup.append(best)
            used_players.add(best)
        
        return lineup
    
    def _optimize_obp_focused(self, lineup: List) -> List:
        """出塁率重視の打順最適化"""
        if len(lineup) < 9:
            return lineup
        
        def obp_score(p):
            contact = getattr(p.stats, 'contact', 50)
            eye = getattr(p.stats, 'eye', contact)
            run = getattr(p.stats, 'run', 50)
            return contact * 0.4 + eye * 0.35 + run * 0.25
        
        sorted_by_obp = sorted(lineup, key=obp_score, reverse=True)
        optimized = [None] * 9
        
        # 1-3番に出塁率上位3人
        for i in range(min(3, len(sorted_by_obp))):
            optimized[i] = sorted_by_obp[i]
        
        # 4-5番はパワー重視
        remaining = [p for p in lineup if p not in optimized[:3]]
        remaining.sort(key=lambda p: getattr(p.stats, 'power', 50), reverse=True)
        
        if remaining:
            optimized[3] = remaining[0]
        if len(remaining) > 1:
            optimized[4] = remaining[1]
        
        # 残りを配置
        placed = [p for p in optimized if p is not None]
        for p in lineup:
            if p not in placed:
                for i in range(9):
                    if optimized[i] is None:
                        optimized[i] = p
                        break
        
        return [p for p in optimized if p is not None]
    
    def _optimize_power_top(self, lineup: List) -> List:
        """パワー上位打順の最適化"""
        if len(lineup) < 9:
            return lineup
        
        sorted_by_power = sorted(lineup, key=lambda p: getattr(p.stats, 'power', 50), reverse=True)
        optimized = [None] * 9
        
        # 3-5番にパワー上位3人
        if sorted_by_power:
            optimized[2] = sorted_by_power[0]  # 3番
        if len(sorted_by_power) > 1:
            optimized[3] = sorted_by_power[1]  # 4番
        if len(sorted_by_power) > 2:
            optimized[4] = sorted_by_power[2]  # 5番
        
        # 1番は足の速い選手
        remaining = [p for p in lineup if p not in [optimized[2], optimized[3], optimized[4]]]
        if remaining:
            fastest = max(remaining, key=lambda p: getattr(p.stats, 'run', 50))
            optimized[0] = fastest
            remaining.remove(fastest)
        
        # 2番はミート
        if remaining:
            best_contact = max(remaining, key=lambda p: getattr(p.stats, 'contact', 50))
            optimized[1] = best_contact
            remaining.remove(best_contact)
        
        # 残りを配置
        for p in remaining:
            for i in range(9):
                if optimized[i] is None:
                    optimized[i] = p
                    break
        
        return [p for p in optimized if p is not None]
    
    def _optimize_speed_top(self, lineup: List) -> List:
        """機動力上位打順の最適化"""
        if len(lineup) < 9:
            return lineup
        
        sorted_by_speed = sorted(lineup, key=lambda p: getattr(p.stats, 'run', 50), reverse=True)
        optimized = [None] * 9
        
        # 1-2番に足の速い選手
        if sorted_by_speed:
            optimized[0] = sorted_by_speed[0]
        if len(sorted_by_speed) > 1:
            optimized[1] = sorted_by_speed[1]
        
        # 3-5番はパワー
        remaining = [p for p in lineup if p not in [optimized[0], optimized[1]]]
        remaining.sort(key=lambda p: getattr(p.stats, 'power', 50), reverse=True)
        
        for i, idx in enumerate([2, 3, 4]):
            if i < len(remaining):
                optimized[idx] = remaining[i]
        
        # 残りを配置
        placed = [p for p in optimized if p is not None]
        for p in lineup:
            if p not in placed:
                for i in range(9):
                    if optimized[i] is None:
                        optimized[i] = p
                        break
        
        return [p for p in optimized if p is not None]
    
    def _optimize_balanced(self, lineup: List) -> List:
        """バランス型打順の最適化"""
        if len(lineup) < 9:
            return lineup
        
        def overall_score(p):
            return (getattr(p.stats, 'contact', 50) * 0.3 + 
                    getattr(p.stats, 'power', 50) * 0.3 +
                    getattr(p.stats, 'run', 50) * 0.2 +
                    getattr(p.stats, 'fielding', 50) * 0.2)
        
        sorted_lineup = sorted(lineup, key=overall_score, reverse=True)
        
        # 能力順に配置（3,4,5,1,2,6,7,8,9の順）
        order = [2, 3, 4, 0, 1, 5, 6, 7, 8]
        optimized = [None] * 9
        
        for i, slot in enumerate(order):
            if i < len(sorted_lineup):
                optimized[slot] = sorted_lineup[i]
        
        return [p for p in optimized if p is not None]
    
    # ===============================
    # 投手ローテーションAI
    # ===============================
    
    def manage_pitcher_rotation(self, pitchers: List, games_played: int) -> List:
        """投手ローテーションを管理
        
        Args:
            pitchers: 投手リスト
            games_played: 経過試合数
            
        Returns:
            List: 推奨先発順のリスト
        """
        # 先発向き（スタミナ60以上）の投手を抽出
        starters = [p for p in pitchers 
                    if getattr(p.stats, 'stamina', 50) >= 60]
        
        # 足りない場合は全投手から
        if len(starters) < 5:
            starters = pitchers[:5] if len(pitchers) >= 5 else pitchers
        
        def starter_rating(p):
            speed = getattr(p.stats, 'speed', 50)
            control = getattr(p.stats, 'control', 50)
            stamina = getattr(p.stats, 'stamina', 50)
            # 疲労度ペナルティ
            fatigue = 0
            if hasattr(p, 'player_status') and p.player_status:
                fatigue = getattr(p.player_status, 'fatigue', 0)
            elif hasattr(p, 'status') and p.status:
                fatigue = getattr(p.status, 'fatigue', 0)
            return speed * 0.3 + control * 0.35 + stamina * 0.35 - fatigue * 0.5
        
        # 疲労度を考慮してソート
        rotation = sorted(starters, key=starter_rating, reverse=True)
        
        # 6人ローテーション推奨（疲労軽減）
        return rotation[:6] if len(rotation) >= 6 else rotation
    
    def recommend_relief_pitchers(self, pitchers: List) -> Dict[str, List]:
        """リリーフ投手の推奨
        
        Returns:
            Dict: {'closer': 抑え候補, 'setup': セットアップ候補, 'middle': 中継ぎ候補}
        """
        # スタミナ60未満 or 球速・制球が高い投手はリリーフ向き
        relief_candidates = []
        for p in pitchers:
            stamina = getattr(p.stats, 'stamina', 50)
            speed = getattr(p.stats, 'speed', 50)
            control = getattr(p.stats, 'control', 50)
            
            if stamina < 60 or speed >= 70 or control >= 70:
                relief_candidates.append(p)
        
        def closer_rating(p):
            return (getattr(p.stats, 'speed', 50) * 0.5 + 
                    getattr(p.stats, 'control', 50) * 0.5)
        
        sorted_relief = sorted(relief_candidates, key=closer_rating, reverse=True)
        
        return {
            'closer': sorted_relief[:1] if sorted_relief else [],
            'setup': sorted_relief[1:3] if len(sorted_relief) > 1 else [],
            'middle': sorted_relief[3:] if len(sorted_relief) > 3 else []
        }
    
    def optimize_pitcher_rotation(self, team) -> Dict[str, Any]:
        """投手ローテーションを総合的に最適化
        
        Returns:
            Dict: {
                'rotation': 先発ローテーション（6人）,
                'closer': 抑え（1人）,
                'setup': セットアップ（2-3人）,
                'middle': 中継ぎ（残り）,
                'description': 説明
            }
        """
        pitchers = [p for p in team.players if p.position.name == 'PITCHER'
                   and getattr(p, 'team_level', 'first') == 'first']
        
        if not pitchers:
            return {'rotation': [], 'closer': None, 'setup': [], 'middle': [], 
                   'description': '投手がいません'}
        
        # 先発適性でソート
        def starter_score(p):
            stamina = getattr(p.stats, 'stamina', 50)
            control = getattr(p.stats, 'control', 50)
            breaking = getattr(p.stats, 'breaking', 50)
            speed = getattr(p.stats, 'speed', 50)
            starter_apt = getattr(p, 'starter_aptitude', 50)
            return stamina * 0.35 + control * 0.25 + breaking * 0.20 + speed * 0.10 + starter_apt * 0.10
        
        # 抑え適性でソート
        def closer_score(p):
            speed = getattr(p.stats, 'speed', 50)
            control = getattr(p.stats, 'control', 50)
            breaking = getattr(p.stats, 'breaking', 50)
            closer_apt = getattr(p, 'closer_aptitude', 50)
            # 短期集中型（スタミナ低め）を優先
            stamina_penalty = max(0, (getattr(p.stats, 'stamina', 50) - 60)) * 0.1
            return speed * 0.35 + control * 0.30 + breaking * 0.20 + closer_apt * 0.15 - stamina_penalty
        
        # 中継ぎ適性
        def middle_score(p):
            speed = getattr(p.stats, 'speed', 50)
            control = getattr(p.stats, 'control', 50)
            stamina = getattr(p.stats, 'stamina', 50)
            middle_apt = getattr(p, 'middle_aptitude', 50)
            return control * 0.35 + speed * 0.25 + stamina * 0.20 + middle_apt * 0.20
        
        used = set()
        
        # 先発（6人）
        starters = sorted(pitchers, key=starter_score, reverse=True)
        rotation = []
        for p in starters[:6]:
            if getattr(p.stats, 'stamina', 50) >= 50:  # スタミナ50以上
                rotation.append(p)
                used.add(p)
        
        # 抑え（1人）
        remaining = [p for p in pitchers if p not in used]
        closer = None
        if remaining:
            closer_candidates = sorted(remaining, key=closer_score, reverse=True)
            closer = closer_candidates[0]
            used.add(closer)
        
        # セットアップ（2-3人）
        remaining = [p for p in pitchers if p not in used]
        setup_candidates = sorted(remaining, key=middle_score, reverse=True)
        setup = setup_candidates[:3]
        for p in setup:
            used.add(p)
        
        # 中継ぎ（残り）
        middle = [p for p in pitchers if p not in used]
        
        desc = f"先発{len(rotation)}人、抑え{1 if closer else 0}人、セットアップ{len(setup)}人、中継ぎ{len(middle)}人で構成"
        
        return {
            'rotation': rotation,
            'closer': closer,
            'setup': setup,
            'middle': middle,
            'description': desc
        }
    
    # ===============================
    # 戦術AI
    # ===============================
    
    def recommend_strategy(self, game_state: dict) -> dict:
        """試合状況に応じた戦術推奨
        
        Args:
            game_state: {'inning': int, 'outs': int, 'runners': list, 
                        'score_diff': int, 'batter': Player}
        
        Returns:
            dict: {'action': str, 'reason': str}
        """
        inning = game_state.get('inning', 1)
        outs = game_state.get('outs', 0)
        runners = game_state.get('runners', [])  # [1塁, 2塁, 3塁]
        score_diff = game_state.get('score_diff', 0)  # 正=リード、負=ビハインド
        batter = game_state.get('batter')
        
        # デフォルト
        action = "通常"
        reason = "通常の打撃"
        
        if batter:
            contact = getattr(batter.stats, 'contact', 50)
            power = getattr(batter.stats, 'power', 50)
            run = getattr(batter.stats, 'run', 50)
        else:
            contact = power = run = 50
        
        # 終盤で僅差の場合
        if inning >= 7:
            if score_diff == 0:
                # 同点
                if runners and outs < 2:
                    if run >= 60:
                        action = "盗塁"
                        reason = "同点終盤、足を使って揺さぶる"
                    elif contact >= 60:
                        action = "進塁打"
                        reason = "同点終盤、確実に進塁"
            elif score_diff < 0:
                # ビハインド
                if abs(score_diff) <= 2:
                    action = "積極打法"
                    reason = "終盤ビハインド、積極的に行く"
            else:
                # リード
                if score_diff >= 3:
                    action = "慎重打法"
                    reason = "リード安定、無理しない"
        
        # ランナー状況
        if runners:
            runner_1b = runners[0] if len(runners) > 0 else False
            runner_2b = runners[1] if len(runners) > 1 else False
            runner_3b = runners[2] if len(runners) > 2 else False
            
            # 送りバント状況
            if runner_1b and outs == 0 and inning <= 6:
                if contact >= 50 and power < 60:
                    action = "送りバント"
                    reason = "ランナー1塁ノーアウト、堅実に"
            
            # スクイズ状況
            if runner_3b and outs < 2 and score_diff >= -1 and score_diff <= 1:
                if inning >= 7:
                    action = "スクイズ検討"
                    reason = "僅差終盤で3塁ランナー"
        
        return {'action': action, 'reason': reason}
    
    def recommend_strategy_advanced(self, game_state: dict, 
                                    strategy: AITacticStrategy = None) -> AIRecommendation:
        """高度な戦術推奨
        
        Args:
            game_state: 試合状況
            strategy: 戦術戦略
        
        Returns:
            AIRecommendation: 推奨アクション
        """
        if strategy is None:
            strategy = self.tactic_strategy
        
        inning = game_state.get('inning', 1)
        outs = game_state.get('outs', 0)
        runners = game_state.get('runners', [False, False, False])
        score_diff = game_state.get('score_diff', 0)
        batter = game_state.get('batter')
        pitcher = game_state.get('pitcher')
        next_batter = game_state.get('next_batter')
        pitch_count = game_state.get('pitch_count', 0)
        
        # 打者・投手能力
        if batter:
            b_contact = getattr(batter.stats, 'contact', 50)
            b_power = getattr(batter.stats, 'power', 50)
            b_run = getattr(batter.stats, 'run', 50)
        else:
            b_contact = b_power = b_run = 50
        
        # 状況分析
        is_late = inning >= 7
        is_close = abs(score_diff) <= 2
        runners_on = sum(1 for r in runners if r)
        scoring_position = runners[1] or runners[2]
        
        # 戦略に基づいた判断
        recommendations = []
        
        # 盗塁推奨
        if runners[0] and not runners[1] and outs < 2:
            if b_run >= 65:
                steal_conf = 0.3 + (b_run - 50) * 0.01
                if strategy == AITacticStrategy.AGGRESSIVE:
                    steal_conf += 0.15
                elif strategy == AITacticStrategy.SMALL_BALL:
                    steal_conf += 0.20
                recommendations.append(AIRecommendation(
                    action="盗塁",
                    reason=f"走力{b_run}の足を活かす",
                    confidence=min(0.85, steal_conf),
                    priority=6 if is_late and is_close else 4
                ))
        
        # 送りバント推奨
        if runners[0] and outs == 0 and not is_late:
            if b_contact >= 50 and b_power < 55:
                bunt_conf = 0.5
                if strategy == AITacticStrategy.CONSERVATIVE:
                    bunt_conf += 0.2
                elif strategy == AITacticStrategy.SMALL_BALL:
                    bunt_conf += 0.25
                recommendations.append(AIRecommendation(
                    action="送りバント",
                    reason="確実に走者を進める",
                    confidence=bunt_conf,
                    priority=5
                ))
        
        # スクイズ推奨
        if runners[2] and outs < 2 and is_late and is_close:
            squeeze_conf = 0.4
            if strategy in [AITacticStrategy.CONSERVATIVE, AITacticStrategy.SMALL_BALL]:
                squeeze_conf += 0.2
            recommendations.append(AIRecommendation(
                action="スクイズ",
                reason="1点を確実に取る",
                confidence=squeeze_conf,
                priority=8 if score_diff <= 0 else 6
            ))
        
        # 敬遠推奨（守備側）
        if game_state.get('is_defending', False):
            if batter and next_batter:
                b_overall = b_contact * 0.5 + b_power * 0.5
                n_contact = getattr(next_batter.stats, 'contact', 50)
                n_power = getattr(next_batter.stats, 'power', 50)
                n_overall = n_contact * 0.5 + n_power * 0.5
                
                if b_overall > n_overall + 15 and not runners[0]:
                    recommendations.append(AIRecommendation(
                        action="敬遠",
                        reason=f"強打者を避けて次打者と勝負",
                        confidence=0.5 + (b_overall - n_overall) * 0.01,
                        priority=7 if scoring_position else 4
                    ))
        
        # 代打推奨
        if is_late and scoring_position and outs < 2:
            if b_contact < 45 and b_power < 45:
                recommendations.append(AIRecommendation(
                    action="代打検討",
                    reason="チャンスで打力不足",
                    confidence=0.6,
                    priority=7
                ))
        
        # 継投推奨
        if game_state.get('is_defending', False) and pitcher:
            p_stamina = getattr(pitcher.stats, 'stamina', 50)
            pitch_limit = 100 + (p_stamina - 50) * 0.6
            
            if pitch_count >= pitch_limit * 0.85:
                recommendations.append(AIRecommendation(
                    action="継投検討",
                    reason=f"球数{pitch_count}球、疲労の兆候",
                    confidence=0.7,
                    priority=8
                ))
        
        # 最も優先度の高い推奨を返す
        if recommendations:
            best = max(recommendations, key=lambda r: (r.priority, r.confidence))
            return best
        
        # デフォルト
        if strategy == AITacticStrategy.AGGRESSIVE:
            return AIRecommendation("積極打法", "初球から積極的に", 0.5, 3)
        elif strategy == AITacticStrategy.CONSERVATIVE:
            return AIRecommendation("慎重打法", "球を見ていく", 0.5, 3)
        else:
            return AIRecommendation("通常", "状況に応じた打撃", 0.5, 3)
    
    # ===============================
    # ドラフト・FA評価AI
    # ===============================
    
    def evaluate_draft_prospect(self, prospect) -> Dict[str, Any]:
        """ドラフト候補を評価
        
        Returns:
            Dict: {
                'score': 総合スコア,
                'rank': 推奨順位,
                'strengths': 強み,
                'concerns': 懸念点,
                'recommendation': 推奨コメント
            }
        """
        overall = getattr(prospect, 'overall', 50)
        potential = getattr(prospect, 'potential', 5)
        age = getattr(prospect, 'age', 18)
        position = getattr(prospect, 'position', None)
        
        # 基本スコア
        score = overall * 0.4 + potential * 8 * 0.4 + (30 - age) * 2 * 0.2
        
        # ポジション補正
        premium_positions = ['CATCHER', 'SHORTSTOP', 'PITCHER']
        if position and position.name in premium_positions:
            score *= 1.1
        
        strengths = []
        concerns = []
        
        if potential >= 8:
            strengths.append("高いポテンシャル")
        elif potential <= 3:
            concerns.append("伸びしろに不安")
        
        if age <= 18:
            strengths.append("若さ（長期的育成可能）")
        elif age >= 23:
            concerns.append("年齢が高め（即戦力期待）")
        
        if overall >= 60:
            strengths.append("即戦力級の能力")
        elif overall <= 40:
            concerns.append("育成に時間が必要")
        
        # 推奨順位
        if score >= 70:
            rank = "1位指名候補"
        elif score >= 60:
            rank = "2位指名候補"
        elif score >= 50:
            rank = "3-4位指名候補"
        else:
            rank = "下位指名候補"
        
        # 推奨コメント
        if score >= 65 and potential >= 7:
            rec = "チームの将来を担う逸材。上位指名を強く推奨"
        elif score >= 55:
            rec = "確実な戦力。指名する価値あり"
        elif score >= 45:
            rec = "素材型。長期的な視点で育成を"
        else:
            rec = "下位指名での獲得を検討"
        
        return {
            'score': score,
            'rank': rank,
            'strengths': strengths,
            'concerns': concerns,
            'recommendation': rec
        }
    
    def evaluate_fa_player(self, player, team=None) -> Dict[str, Any]:
        """FA選手を評価
        
        Returns:
            Dict: {
                'value': 推定価値,
                'fit_score': チームへのフィット度,
                'risk': リスク評価,
                'recommendation': 推奨コメント
            }
        """
        is_pitcher = player.position.name == 'PITCHER'
        
        if is_pitcher:
            ability = (player.stats.control * 0.35 + player.stats.breaking * 0.30 + 
                      player.stats.speed * 0.20 + player.stats.stamina * 0.15)
        else:
            ability = (player.stats.contact * 0.35 + player.stats.power * 0.30 + 
                      player.stats.run * 0.15 + player.stats.fielding * 0.20)
        
        # 年齢リスク
        age = player.age
        if age <= 28:
            age_factor = 1.0
            risk = "低"
        elif age <= 32:
            age_factor = 0.9
            risk = "中"
        elif age <= 35:
            age_factor = 0.75
            risk = "高"
        else:
            age_factor = 0.6
            risk = "非常に高"
        
        value = ability * age_factor
        
        # チームへのフィット度
        fit_score = 50
        if team:
            analysis = self.analyze_team(team)
            if player.position.name in analysis.weak_positions:
                fit_score = 80
            elif player.position.name in analysis.strong_positions:
                fit_score = 30
        
        # 推奨
        if value >= 65 and fit_score >= 60:
            rec = "獲得を強く推奨。チームの弱点補強に最適"
        elif value >= 55:
            rec = "獲得を検討。戦力アップが見込める"
        elif fit_score >= 70:
            rec = "弱点補強として検討の価値あり"
        else:
            rec = "他の候補を優先すべき"
        
        return {
            'value': value,
            'fit_score': fit_score,
            'risk': risk,
            'recommendation': rec
        }
    
    # ===============================
    # 試合中AI支援
    # ===============================
    
    def suggest_pinch_hitter(self, team, current_batter_idx: int, 
                             game_state: dict) -> Optional[Tuple[int, str]]:
        """代打を提案
        
        Returns:
            Tuple[代打候補のインデックス, 理由] or None
        """
        if current_batter_idx < 0 or current_batter_idx >= len(team.players):
            return None
        
        current = team.players[current_batter_idx]
        
        # 現在の打者が投手の場合、代打を強く推奨
        is_pitcher = current.position.name == 'PITCHER'
        
        inning = game_state.get('inning', 1)
        runners = game_state.get('runners', [False, False, False])
        outs = game_state.get('outs', 0)
        scoring_position = runners[1] or runners[2]
        
        # 終盤でチャンスの場合
        if inning >= 7 and (scoring_position or is_pitcher):
            # ベンチから代打候補を探す
            lineup = set(getattr(team, 'current_lineup', []))
            bench = [i for i, p in enumerate(team.players) 
                    if i not in lineup and p.position.name != 'PITCHER']
            
            if not bench:
                return None
            
            # 最も打撃能力の高い選手
            best_idx = max(bench, key=lambda i: 
                          team.players[i].stats.contact * 0.5 + team.players[i].stats.power * 0.5)
            best = team.players[best_idx]
            
            current_score = current.stats.contact * 0.5 + current.stats.power * 0.5 if not is_pitcher else 30
            best_score = best.stats.contact * 0.5 + best.stats.power * 0.5
            
            if best_score > current_score + 10 or is_pitcher:
                reason = "投手に代わって" if is_pitcher else f"打力向上（+{int(best_score - current_score)}）"
                return (best_idx, reason)
        
        return None
    
    def suggest_pitching_change(self, team, current_pitcher_idx: int,
                                pitch_count: int, game_state: dict) -> Optional[Tuple[int, str]]:
        """継投を提案
        
        Returns:
            Tuple[交代投手のインデックス, 理由] or None
        """
        if current_pitcher_idx < 0 or current_pitcher_idx >= len(team.players):
            return None
        
        current = team.players[current_pitcher_idx]
        stamina = getattr(current.stats, 'stamina', 50)
        
        # 球数上限
        pitch_limit = 100 + (stamina - 50) * 0.6
        
        inning = game_state.get('inning', 1)
        score_diff = game_state.get('score_diff', 0)
        runners = game_state.get('runners', [False, False, False])
        hits_allowed = game_state.get('hits_allowed', 0)
        
        should_change = False
        reason = ""
        
        # 球数超過
        if pitch_count >= pitch_limit:
            should_change = True
            reason = f"球数{pitch_count}球（上限{int(pitch_limit)}）"
        
        # 終盤のリードで抑え
        elif inning >= 9 and 0 < score_diff <= 3:
            should_change = True
            reason = "終盤のリードを守る"
        
        # 炎上気味
        elif hits_allowed >= 8 and inning <= 5:
            should_change = True
            reason = "被安打多数"
        
        if not should_change:
            return None
        
        # 交代投手を探す
        rotation = set(getattr(team, 'rotation', []))
        setup = getattr(team, 'setup_pitchers', [])
        closer_idx = getattr(team, 'closer_idx', -1)
        
        # 9回でリードなら抑え
        if inning >= 9 and score_diff > 0 and closer_idx >= 0:
            return (closer_idx, reason + " - 抑え投入")
        
        # それ以外はセットアップ
        for idx in setup:
            if idx != current_pitcher_idx:
                return (idx, reason + " - 中継ぎ投入")
        
        return None
    
    def suggest_steal(self, runner, catcher=None, game_state: dict = None) -> AIRecommendation:
        """盗塁を提案"""
        run = getattr(runner.stats, 'run', 50) if runner else 50
        catcher_arm = getattr(catcher.stats, 'arm', 50) if catcher else 50
        
        success_rate = 0.5 + (run - catcher_arm) * 0.01
        success_rate = max(0.2, min(0.9, success_rate))
        
        if success_rate >= 0.65:
            return AIRecommendation(
                action="盗塁を推奨",
                reason=f"成功率約{int(success_rate * 100)}%",
                confidence=success_rate,
                priority=7
            )
        elif success_rate >= 0.5:
            return AIRecommendation(
                action="盗塁を検討",
                reason=f"成功率約{int(success_rate * 100)}%（やや低め）",
                confidence=success_rate,
                priority=4
            )
        else:
            return AIRecommendation(
                action="盗塁は控えめに",
                reason=f"成功率約{int(success_rate * 100)}%（リスク高）",
                confidence=1 - success_rate,
                priority=2
            )


# グローバルインスタンス
ai_manager = AIManager()
