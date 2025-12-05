# -*- coding: utf-8 -*-
"""
設定管理システム
"""
import json
import os
from typing import Tuple, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class GameRuleSettings:
    """ゲームルール設定"""
    # DH制（常時オン）
    central_dh: bool = True  # セリーグDH制（常時オン）
    pacific_dh: bool = True   # パリーグDH制（常時オン）
    interleague_dh: bool = True  # 交流戦時のDH（常時オン）
    
    # シーズン構成
    enable_interleague: bool = True  # 交流戦を行う
    enable_climax_series: bool = True  # クライマックスシリーズを行う
    enable_allstar: bool = True  # オールスターを行う
    enable_spring_camp: bool = True  # 春季キャンプを行う
    
    # 試合数
    regular_season_games: int = 143  # レギュラーシーズン試合数
    interleague_games: int = 18  # 交流戦試合数
    
    # 延長・タイブレーク
    extra_innings_limit: int = 12  # 延長上限（0=無制限）
    enable_tiebreaker: bool = False  # タイブレーク制度
    
    # 外国人枠
    foreign_player_limit: int = 4  # 支配下外国人枠（0=無制限）
    foreign_bench_limit: int = 2  # ベンチ入り外国人枠
    unlimited_foreign: bool = False  # 外国人枠無制限
    
    # 選手登録
    roster_limit: int = 31  # 一軍登録人数上限
    farm_roster_limit: int = 70  # 育成枠人数上限（0=無制限）
    
    # 軍制度
    enable_third_team: bool = False  # 三軍制度を有効化
    first_team_limit: int = 31  # 一軍登録人数上限
    second_team_limit: int = 0  # 二軍登録人数上限（0=無制限）
    
    # キャンプ
    spring_camp_days: int = 28  # 春季キャンプ日数
    
    # 自動進行
    auto_simulate_other_games: bool = True  # 他チームの試合を自動進行
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameRuleSettings':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class SettingsManager:
    """ゲーム設定を管理するクラス"""
    
    def __init__(self):
        self.settings_file = "game_settings.json"
        self.screen_width = 1600
        self.screen_height = 1000
        self.fullscreen = False
        self.sound_enabled = True
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.auto_save = True
        self.graphics_quality = "medium"  # "low", "medium", "high"
        
        # ゲームルール設定
        self.game_rules = GameRuleSettings()
        
        self.load_settings()
    
    def load_settings(self):
        """設定ファイルから読み込み"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.screen_width = data.get('screen_width', 1600)
                    self.screen_height = data.get('screen_height', 1000)
                    self.fullscreen = data.get('fullscreen', False)
                    self.sound_enabled = data.get('sound_enabled', True)
                    self.music_volume = data.get('music_volume', 0.7)
                    self.sfx_volume = data.get('sfx_volume', 0.8)
                    self.auto_save = data.get('auto_save', True)
                    self.graphics_quality = data.get('graphics_quality', 'medium')
                    
                    # ゲームルール設定を読み込み
                    if 'game_rules' in data:
                        self.game_rules = GameRuleSettings.from_dict(data['game_rules'])
            except Exception as e:
                print(f"設定ファイルの読み込みエラー: {e}")
    
    def save_settings(self):
        """設定をファイルに保存"""
        try:
            data = {
                'screen_width': self.screen_width,
                'screen_height': self.screen_height,
                'fullscreen': self.fullscreen,
                'sound_enabled': self.sound_enabled,
                'music_volume': self.music_volume,
                'sfx_volume': self.sfx_volume,
                'auto_save': self.auto_save,
                'graphics_quality': self.graphics_quality,
                'game_rules': self.game_rules.to_dict()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存エラー: {e}")
    
    def get_resolution(self) -> Tuple[int, int]:
        """現在の解像度を取得"""
        return (self.screen_width, self.screen_height)
    
    def set_resolution(self, width: int, height: int):
        """解像度を設定"""
        self.screen_width = width
        self.screen_height = height
        self.save_settings()
    
    def toggle_fullscreen(self):
        """フルスクリーンの切り替え"""
        self.fullscreen = not self.fullscreen
        self.save_settings()
    
    def set_volume(self, music: float = None, sfx: float = None):
        """音量を設定"""
        if music is not None:
            self.music_volume = max(0.0, min(1.0, music))
        if sfx is not None:
            self.sfx_volume = max(0.0, min(1.0, sfx))
        self.save_settings()
    
    def toggle_sound(self):
        """サウンドのオン/オフ切り替え"""
        self.sound_enabled = not self.sound_enabled
        self.save_settings()


# グローバル設定インスタンス
settings = SettingsManager()
