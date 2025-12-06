# -*- coding: utf-8 -*-
"""
NPB Pennant Simulator - Page Modules
OOTP-Style Application Pages
"""
from .home_page import HomePage
from .roster_page import RosterPage
from .game_page import GamePage
from .standings_page import StandingsPage
from .schedule_page import SchedulePage
from .stats_page import StatsPage
from .draft_page import DraftPage
from .trade_page import TradePage
from .fa_page import FAPage
from .settings_page import SettingsPage

__all__ = [
    "HomePage",
    "RosterPage",
    "GamePage",
    "StandingsPage",
    "SchedulePage",
    "StatsPage",
    "DraftPage",
    "TradePage",
    "FAPage",
    "SettingsPage",
]
