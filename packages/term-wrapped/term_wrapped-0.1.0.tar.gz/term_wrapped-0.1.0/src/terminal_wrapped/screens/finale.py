"""Finale summary screen for Terminal Wrapped."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Static

from terminal_wrapped.widgets.gradient_bg import RAINBOW_STOPS, AnimatedGradient

if TYPE_CHECKING:
    from terminal_wrapped.analyzer import WrappedStats


BIG_DIGITS = {
    "0": ["  ███  ", " █   █ ", " █   █ ", " █   █ ", "  ███  "],
    "1": ["   █   ", "  ██   ", "   █   ", "   █   ", "  ███  "],
    "2": ["  ███  ", " █   █ ", "    █  ", "   █   ", " █████ "],
    "3": ["  ███  ", " █   █ ", "   ██  ", " █   █ ", "  ███  "],
    "4": ["    █  ", "   ██  ", "  █ █  ", " █████ ", "    █  "],
    "5": [" █████ ", " █     ", " ████  ", "     █ ", " ████  "],
    "6": ["  ███  ", " █     ", " ████  ", " █   █ ", "  ███  "],
    "7": [" █████ ", "    █  ", "   █   ", "  █    ", "  █    "],
    "8": ["  ███  ", " █   █ ", "  ███  ", " █   █ ", "  ███  "],
    "9": ["  ███  ", " █   █ ", "  ████ ", "     █ ", "  ███  "],
    ",": ["       ", "       ", "       ", "   █   ", "  █    "],
}


def render_big_number(n: int) -> str:
    """Render a number in big ASCII digits."""
    s = f"{n:,}"
    lines = ["", "", "", "", ""]
    for char in s:
        if char in BIG_DIGITS:
            for i, digit_line in enumerate(BIG_DIGITS[char]):
                lines[i] += digit_line
        else:
            for i in range(5):
                lines[i] += "  "
    return "\n".join(lines)


class FinaleScreen(Screen):
    """Final summary screen with big stats."""

    BINDINGS = [
        Binding("space", "restart", "Start Over", show=True),
        Binding("enter", "restart", "Start Over", show=False),
        Binding("escape", "prev_screen", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_CSS = """
    FinaleScreen {
        background: #220033;
        align: center middle;
    }

    #summary-box {
        width: 70;
        height: auto;
        padding: 2 4;
        background: #1a0a2e;
        border: heavy #ff00ff;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
        width: 100%;
    }

    #big-number {
        color: #00ffff;
        text-align: center;
        text-style: bold;
        width: 100%;
        margin: 1 0;
    }

    #subtitle {
        color: #ffff00;
        text-align: center;
        width: 100%;
    }

    .section-label {
        color: #888888;
        text-align: center;
        width: 100%;
        margin-top: 1;
    }

    .section-value {
        color: #00ffff;
        text-align: center;
        width: 100%;
    }

    #date-range {
        color: #666666;
        text-align: center;
        width: 100%;
        margin-top: 1;
    }

    #thanks {
        color: #ffffff;
        text-align: center;
        width: 100%;
        margin-top: 2;
        text-style: italic;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        color: #888888;
    }
    """

    def __init__(self, stats: WrappedStats, **kwargs) -> None:
        super().__init__(**kwargs)
        self.stats = stats

    def compose(self) -> ComposeResult:
        """Compose the finale screen."""
        top_cmds = (
            ", ".join(c[0] for c in self.stats.top_commands[:3])
            if self.stats.top_commands
            else "N/A"
        )
        top_git = (
            ", ".join(f"git {c[0]}" for c in self.stats.git_subcommands[:3])
            if self.stats.git_subcommands
            else "N/A"
        )
        top_dirs = (
            ", ".join(c[0] for c in self.stats.top_cd_targets[:3])
            if self.stats.top_cd_targets
            else "N/A"
        )

        date_text = ""
        if self.stats.date_range:
            start, end = self.stats.date_range
            date_text = f"{start.strftime('%b %Y')} - {end.strftime('%b %Y')}"

        with Vertical(id="summary-box"):
            yield Static("YOUR YEAR IN THE TERMINAL", id="title")
            yield Static(render_big_number(self.stats.total_commands), id="big-number")
            yield Static("total commands", id="subtitle")

            yield Static("Top Commands", classes="section-label")
            yield Static(top_cmds, classes="section-value")

            yield Static("Top Git", classes="section-label")
            yield Static(top_git, classes="section-value")

            yield Static("Top Directories", classes="section-label")
            yield Static(top_dirs, classes="section-value")

            yield Static(date_text, id="date-range")
            yield Static("Thanks for being a power user!", id="thanks")

        yield Static("SPACE: start over  ESC: back  Q: quit", id="nav-hint")

    def action_restart(self) -> None:
        """Go back to splash screen."""
        self.app.switch_screen("splash")

    def action_prev_screen(self) -> None:
        """Go to previous screen."""
        self.app.switch_screen("most_pipes")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
