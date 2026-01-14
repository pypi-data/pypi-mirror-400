"""Screens for Terminal Wrapped."""

from terminal_wrapped.screens.finale import FinaleScreen
from terminal_wrapped.screens.splash import SplashScreen
from terminal_wrapped.screens.stats import (
    CdTargetsScreen,
    DayOfWeekScreen,
    GitSubcommandsScreen,
    MostPipesScreen,
    PowerStatsScreen,
    TimeOfDayScreen,
    TopCommandsScreen,
    TyposScreen,
    UselessCatScreen,
)

__all__ = [
    "SplashScreen",
    "TopCommandsScreen",
    "GitSubcommandsScreen",
    "CdTargetsScreen",
    "DayOfWeekScreen",
    "TimeOfDayScreen",
    "PowerStatsScreen",
    "UselessCatScreen",
    "TyposScreen",
    "MostPipesScreen",
    "FinaleScreen",
]
