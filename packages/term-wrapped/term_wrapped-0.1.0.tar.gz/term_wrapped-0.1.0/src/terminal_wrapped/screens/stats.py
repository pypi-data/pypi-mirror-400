"""Statistics screens for Terminal Wrapped."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from terminal_wrapped.widgets.gradient_bg import (
    OCEAN_STOPS,
    SYNTHWAVE_STOPS,
    AnimatedGradient,
)

if TYPE_CHECKING:
    from terminal_wrapped.analyzer import WrappedStats


class StatBar(Static):
    """An animated stat bar that fills to a percentage."""

    DEFAULT_CSS = """
    StatBar {
        width: 100%;
        height: 1;
        background: #333333;
    }
    """

    def __init__(self, percentage: float = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.percentage = percentage
        self._current = 0

    def on_mount(self) -> None:
        """Start the fill animation."""
        self.animate_fill()

    @work
    async def animate_fill(self) -> None:
        """Animate the bar filling up."""
        target = int(self.percentage)
        for i in range(target + 1):
            self._current = i
            self._update_display()
            await asyncio.sleep(0.01)

    def _update_display(self) -> None:
        """Update the bar display."""
        width = self.size.width or 40
        filled = int((self._current / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        self.update(bar)


class BaseStatScreen(Screen):
    """Base class for stat screens with common navigation."""

    BINDINGS = [
        Binding("space", "next_screen", "Next", show=True),
        Binding("enter", "next_screen", "Next", show=False),
        Binding("escape", "prev_screen", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    next_screen_name: str = ""
    prev_screen_name: str = "splash"
    title_text: str = "Stats"
    gradient_stops = SYNTHWAVE_STOPS

    def __init__(self, stats: WrappedStats, **kwargs) -> None:
        super().__init__(**kwargs)
        self.stats = stats

    def action_next_screen(self) -> None:
        """Go to next screen."""
        if self.next_screen_name:
            self.app.switch_screen(self.next_screen_name)

    def action_prev_screen(self) -> None:
        """Go to previous screen."""
        self.app.switch_screen(self.prev_screen_name)

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class TopCommandsScreen(BaseStatScreen):
    """Shows top commands with animated bars."""

    next_screen_name = "git_subcommands"
    prev_screen_name = "splash"
    title_text = "YOUR TOP COMMANDS"

    DEFAULT_CSS = """
    TopCommandsScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 80;
        height: auto;
        padding: 1 2;
    }

    .stat-row {
        width: 100%;
        height: 3;
        margin-bottom: 1;
        background: transparent;
    }

    .rank {
        width: 4;
        color: #ffff00;
        text-style: bold;
    }

    .command-name {
        width: 20;
        color: #00ffff;
        text-style: bold;
    }

    .bar-container {
        width: 1fr;
        height: 1;
        margin: 0 2;
    }

    .count {
        width: 10;
        text-align: right;
        color: #ff00ff;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the top commands screen."""
        yield AnimatedGradient(stops=self.gradient_stops, speed=20, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    if self.stats.top_commands:
                        max_count = self.stats.top_commands[0][1]
                        for i, (cmd, count) in enumerate(
                            self.stats.top_commands[:8], 1
                        ):
                            pct = (count / max_count) * 100 if max_count > 0 else 0
                            with Horizontal(classes="stat-row"):
                                yield Static(f"{i}.", classes="rank")
                                yield Static(cmd[:18], classes="command-name")
                                with Container(classes="bar-container"):
                                    yield StatBar(pct)
                                yield Static(f"{count:,}", classes="count")
                    else:
                        yield Static("No command history found", id="no-data")

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")


class CdTargetsScreen(BaseStatScreen):
    """Shows top cd/z targets."""

    next_screen_name = "day_of_week"
    prev_screen_name = "git_subcommands"
    title_text = "WHERE YOU WENT"
    gradient_stops = OCEAN_STOPS

    DEFAULT_CSS = """
    CdTargetsScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #section-title {
        text-style: bold;
        color: #00ffff;
        text-align: center;
        margin: 1 0;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 80;
        height: auto;
        padding: 1 2;
    }

    .stat-row {
        width: 100%;
        height: 3;
        margin-bottom: 1;
        background: transparent;
    }

    .rank {
        width: 4;
        color: #ffff00;
        text-style: bold;
    }

    .target-name {
        width: 40;
        color: #00ffff;
    }

    .bar-container {
        width: 1fr;
        height: 1;
        margin: 0 2;
    }

    .count {
        width: 8;
        text-align: right;
        color: #ff00ff;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the cd targets screen."""
        yield AnimatedGradient(stops=self.gradient_stops, speed=15, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    all_targets = []
                    for target, count in self.stats.top_cd_targets:
                        all_targets.append((target, count, "cd"))
                    for target, count in self.stats.top_z_targets:
                        all_targets.append((target, count, "z"))

                    all_targets.sort(key=lambda x: x[1], reverse=True)
                    top_targets = all_targets[:8]

                    if top_targets:
                        max_count = top_targets[0][1]
                        yield Static("Top directories (cd & z)", id="section-title")
                        for i, (target, count, cmd_type) in enumerate(top_targets, 1):
                            pct = (count / max_count) * 100 if max_count > 0 else 0
                            display_target = (
                                target if len(target) <= 38 else "..." + target[-35:]
                            )
                            with Horizontal(classes="stat-row"):
                                yield Static(f"{i}.", classes="rank")
                                yield Static(display_target, classes="target-name")
                                with Container(classes="bar-container"):
                                    yield StatBar(pct)
                                yield Static(f"{count:,}", classes="count")
                    else:
                        yield Static("No directory changes found", id="no-data")

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")


class DayOfWeekScreen(BaseStatScreen):
    """Shows command usage by day of week."""

    next_screen_name = "time_of_day"
    prev_screen_name = "cd_targets"
    title_text = "YOUR BUSIEST DAYS"

    DEFAULT_CSS = """
    DayOfWeekScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 60;
        height: auto;
        padding: 1 2;
    }

    .day-row {
        width: 100%;
        height: 3;
        margin-bottom: 1;
        background: transparent;
    }

    .day-name {
        width: 12;
        color: #00ffff;
        text-style: bold;
    }

    .bar-container {
        width: 1fr;
        height: 1;
        margin: 0 2;
    }

    .count {
        width: 10;
        text-align: right;
        color: #ff00ff;
    }

    #no-timestamps {
        text-align: center;
        color: #ff8800;
        margin: 2;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    DAYS_ORDER = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    def compose(self) -> ComposeResult:
        """Compose the day of week screen."""
        yield AnimatedGradient(stops=SYNTHWAVE_STOPS, speed=25, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    if self.stats.commands_by_day:
                        max_count = max(self.stats.commands_by_day.values())
                        for day in self.DAYS_ORDER:
                            count = self.stats.commands_by_day.get(day, 0)
                            pct = (count / max_count) * 100 if max_count > 0 else 0
                            with Horizontal(classes="day-row"):
                                yield Static(day[:3], classes="day-name")
                                with Container(classes="bar-container"):
                                    yield StatBar(pct)
                                yield Static(f"{count:,}", classes="count")
                    else:
                        yield Static(
                            "No timestamp data available.\n"
                            "Timestamps require EXTENDED_HISTORY in zsh.",
                            id="no-timestamps",
                        )

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")


class MostPipesScreen(BaseStatScreen):
    """Shows commands with the most pipes."""

    next_screen_name = "finale"
    prev_screen_name = "typos"
    title_text = "PIPE DREAMS"

    DEFAULT_CSS = """
    MostPipesScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 90%;
        max-width: 100;
        height: auto;
        padding: 1 2;
    }

    .command-entry {
        width: 100%;
        height: auto;
        margin-bottom: 2;
        background: transparent;
    }

    .command-rank {
        color: #ffff00;
        text-style: bold;
        margin-bottom: 1;
    }

    .command-text {
        color: #00ffff;
        width: 100%;
        height: auto;
        padding: 0 2;
    }

    #no-data {
        color: #00ff00;
        text-align: center;
        width: 100%;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the most pipes screen."""
        yield AnimatedGradient(stops=OCEAN_STOPS, speed=30, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    if self.stats.most_piped_commands:
                        for i, (cmd, pipe_count) in enumerate(
                            self.stats.most_piped_commands[:3], 1
                        ):
                            with Vertical(classes="command-entry"):
                                label = "pipe" if pipe_count == 1 else "pipes"
                                yield Static(
                                    f"#{i} ({pipe_count} {label})",
                                    classes="command-rank",
                                )
                                yield Static(cmd, classes="command-text")
                    else:
                        yield Static("No commands with pipes found", id="no-data")

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")


class GitSubcommandsScreen(BaseStatScreen):
    """Shows git subcommand breakdown."""

    next_screen_name = "cd_targets"
    prev_screen_name = "top_commands"
    title_text = "YOUR GIT LIFE"

    DEFAULT_CSS = """
    GitSubcommandsScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 70;
        height: auto;
        padding: 1 2;
    }

    .stat-row {
        width: 100%;
        height: 3;
        margin-bottom: 1;
        background: transparent;
    }

    .rank {
        width: 4;
        color: #ffff00;
        text-style: bold;
    }

    .command-name {
        width: 16;
        color: #ff6600;
        text-style: bold;
    }

    .bar-container {
        width: 1fr;
        height: 1;
        margin: 0 2;
    }

    .count {
        width: 10;
        text-align: right;
        color: #ff00ff;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the git subcommands screen."""
        from terminal_wrapped.widgets.gradient_bg import RAINBOW_STOPS

        yield AnimatedGradient(stops=RAINBOW_STOPS, speed=25, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    if self.stats.git_subcommands:
                        max_count = self.stats.git_subcommands[0][1]
                        for i, (cmd, count) in enumerate(
                            self.stats.git_subcommands[:8], 1
                        ):
                            pct = (count / max_count) * 100 if max_count > 0 else 0
                            with Horizontal(classes="stat-row"):
                                yield Static(f"{i}.", classes="rank")
                                yield Static(f"git {cmd}", classes="command-name")
                                with Container(classes="bar-container"):
                                    yield StatBar(pct)
                                yield Static(f"{count:,}", classes="count")
                    else:
                        yield Static("No git commands found", id="no-data")

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")


class TimeOfDayScreen(BaseStatScreen):
    """Shows command usage by time of day."""

    next_screen_name = "power_stats"
    prev_screen_name = "day_of_week"
    title_text = "WHEN YOU WORK"

    DEFAULT_CSS = """
    TimeOfDayScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 70;
        height: auto;
        padding: 1 2;
    }

    .time-row {
        width: 100%;
        height: 2;
        background: transparent;
    }

    .time-label {
        width: 14;
        color: #00ffff;
    }

    .bar-container {
        width: 1fr;
        height: 1;
        margin: 0 2;
    }

    .count {
        width: 8;
        text-align: right;
        color: #ff00ff;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    TIME_PERIODS = [
        ("Night", range(0, 6)),
        ("Morning", range(6, 12)),
        ("Afternoon", range(12, 18)),
        ("Evening", range(18, 24)),
    ]

    def compose(self) -> ComposeResult:
        """Compose the time of day screen."""
        yield AnimatedGradient(stops=OCEAN_STOPS, speed=20, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    if self.stats.commands_by_hour:
                        period_counts = {}
                        for label, hours in self.TIME_PERIODS:
                            period_counts[label] = sum(
                                self.stats.commands_by_hour.get(h, 0) for h in hours
                            )

                        max_count = max(period_counts.values()) if period_counts else 1

                        for label, hours in self.TIME_PERIODS:
                            count = period_counts[label]
                            pct = (count / max_count) * 100 if max_count > 0 else 0
                            with Horizontal(classes="time-row"):
                                yield Static(label, classes="time-label")
                                with Container(classes="bar-container"):
                                    yield StatBar(pct)
                                yield Static(f"{count:,}", classes="count")
                    else:
                        yield Static("No timestamp data available", id="no-data")

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")


class PowerStatsScreen(BaseStatScreen):
    """Shows power user statistics."""

    next_screen_name = "useless_cat"
    prev_screen_name = "time_of_day"
    title_text = "POWER USER STATS"

    DEFAULT_CSS = """
    PowerStatsScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 50;
        height: auto;
        padding: 2;
    }

    .stat-item {
        width: 100%;
        height: 4;
        background: transparent;
        margin-bottom: 1;
    }

    .stat-label {
        color: #888888;
        text-align: center;
        width: 100%;
    }

    .stat-value {
        color: #00ffff;
        text-style: bold;
        text-align: center;
        width: 100%;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the power stats screen."""
        yield AnimatedGradient(stops=SYNTHWAVE_STOPS, speed=35, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    with Vertical(classes="stat-item"):
                        yield Static("Unique Commands", classes="stat-label")
                        yield Static(
                            f"{self.stats.unique_commands:,}", classes="stat-value"
                        )

                    with Vertical(classes="stat-item"):
                        yield Static("Pipes Used |", classes="stat-label")
                        yield Static(f"{self.stats.pipe_count:,}", classes="stat-value")

                    with Vertical(classes="stat-item"):
                        yield Static("Sudo Commands", classes="stat-label")
                        yield Static(f"{self.stats.sudo_count:,}", classes="stat-value")

                    with Vertical(classes="stat-item"):
                        yield Static("Avg Command Length", classes="stat-label")
                        yield Static(
                            f"{self.stats.avg_command_length:.1f} chars",
                            classes="stat-value",
                        )

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")


class UselessCatScreen(BaseStatScreen):
    """Shows useless use of cat awards."""

    next_screen_name = "typos"
    prev_screen_name = "power_stats"
    title_text = "USELESS USE OF CAT AWARDS"

    DEFAULT_CSS = """
    UselessCatScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 80;
        height: auto;
        padding: 1 2;
    }

    #cat-count {
        text-align: center;
        width: 100%;
        margin-bottom: 2;
    }

    .count-number {
        color: #ff6600;
        text-style: bold;
    }

    .count-label {
        color: #888888;
    }

    #examples-label {
        color: #ffff00;
        text-align: center;
        width: 100%;
        margin: 1 0;
    }

    .example {
        color: #00ffff;
        width: 100%;
        margin-bottom: 1;
        padding: 0 2;
    }

    #no-data {
        color: #00ff00;
        text-align: center;
        width: 100%;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the useless cat screen."""
        from terminal_wrapped.widgets.gradient_bg import RAINBOW_STOPS

        yield AnimatedGradient(stops=RAINBOW_STOPS, speed=40, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    if self.stats.useless_cat_count > 0:
                        with Horizontal(id="cat-count"):
                            yield Static(
                                f"{self.stats.useless_cat_count:,}",
                                classes="count-number",
                            )
                            yield Static(
                                " times you could have skipped cat",
                                classes="count-label",
                            )

                        if self.stats.useless_cat_examples:
                            yield Static("Examples of shame:", id="examples-label")
                            for example in self.stats.useless_cat_examples[:3]:
                                display = (
                                    example
                                    if len(example) <= 70
                                    else example[:67] + "..."
                                )
                                yield Static(f"$ {display}", classes="example")
                    else:
                        yield Static("Congrats! No useless cats found!", id="no-data")

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")


class TyposScreen(BaseStatScreen):
    """Shows typo hall of fame."""

    next_screen_name = "most_pipes"
    prev_screen_name = "useless_cat"
    title_text = "TYPO HALL OF FAME"

    DEFAULT_CSS = """
    TyposScreen {
        layers: background foreground;
    }

    #gradient-bg {
        layer: background;
        width: 100%;
        height: 100%;
    }

    #content {
        layer: foreground;
        width: 100%;
        height: 100%;
        background: transparent;
        padding: 2 4;
    }

    #header {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: transparent;
    }

    #title {
        text-style: bold;
        color: #ffffff;
        text-align: center;
    }

    #stats-wrapper {
        width: 100%;
        height: auto;
        align: center top;
    }

    #stats-container {
        width: 60;
        height: auto;
        padding: 1 2;
    }

    .typo-row {
        width: 100%;
        height: 3;
        margin-bottom: 1;
        background: transparent;
    }

    .typo-text {
        width: 12;
        color: #ff0000;
        text-style: bold;
    }

    .arrow {
        width: 4;
        color: #888888;
    }

    .correct-text {
        width: 12;
        color: #00ff00;
    }

    .typo-count {
        width: 1fr;
        text-align: right;
        color: #ff00ff;
    }

    #no-data {
        color: #00ff00;
        text-align: center;
        width: 100%;
    }

    #nav-hint {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: transparent;
        color: #666666;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the typos screen."""
        from terminal_wrapped.analyzer import KNOWN_TYPOS

        yield AnimatedGradient(stops=OCEAN_STOPS, speed=30, id="gradient-bg")

        with Container(id="content"):
            with Container(id="header"):
                yield Static(self.title_text, id="title")

            with Container(id="stats-wrapper"):
                with Vertical(id="stats-container"):
                    if self.stats.typos:
                        for typo, count in self.stats.typos[:8]:
                            correct = KNOWN_TYPOS.get(typo, "?")
                            with Horizontal(classes="typo-row"):
                                yield Static(typo, classes="typo-text")
                                yield Static("->", classes="arrow")
                                yield Static(correct, classes="correct-text")
                                yield Static(f"{count:,}x", classes="typo-count")
                    else:
                        yield Static("Perfect typing! No typos found!", id="no-data")

            yield Static("SPACE: next  ESC: back  Q: quit", id="nav-hint")
