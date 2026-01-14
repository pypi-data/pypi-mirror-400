"""Terminal Wrapped - Your year in commands."""

from textual.app import App
from textual.binding import Binding

from terminal_wrapped.analyzer import WrappedStats, load_history
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


class TerminalWrappedApp(App):
    """Terminal Wrapped - A visual journey through your command history."""

    TITLE = "Terminal Wrapped"

    CSS = """
    Screen {
        background: #000000;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.stats: WrappedStats | None = None

    def on_mount(self) -> None:
        """Load stats and set up screens on mount."""
        self.stats = load_history()

        self.install_screen(SplashScreen(), name="splash")
        self.install_screen(TopCommandsScreen(self.stats), name="top_commands")
        self.install_screen(GitSubcommandsScreen(self.stats), name="git_subcommands")
        self.install_screen(CdTargetsScreen(self.stats), name="cd_targets")
        self.install_screen(DayOfWeekScreen(self.stats), name="day_of_week")
        self.install_screen(TimeOfDayScreen(self.stats), name="time_of_day")
        self.install_screen(PowerStatsScreen(self.stats), name="power_stats")
        self.install_screen(UselessCatScreen(self.stats), name="useless_cat")
        self.install_screen(TyposScreen(self.stats), name="typos")
        self.install_screen(MostPipesScreen(self.stats), name="most_pipes")
        self.install_screen(FinaleScreen(self.stats), name="finale")

        self.push_screen("splash")


def main():
    """Entry point for Terminal Wrapped."""
    app = TerminalWrappedApp()
    app.run()
