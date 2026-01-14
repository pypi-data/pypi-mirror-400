"""Splash screen with animated cube and gradient background."""

import asyncio

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Middle
from textual.screen import Screen
from textual.widgets import Static

from terminal_wrapped.widgets import AnimatedGradient, RotatingCube


class TypewriterText(Static):
    """A text widget with typewriter animation effect."""

    def __init__(self, text: str, speed: float = 0.05, **kwargs) -> None:
        super().__init__("", **kwargs)
        self.full_text = text
        self.speed = speed

    def on_mount(self) -> None:
        self.typewrite()

    @work
    async def typewrite(self) -> None:
        """Animate text appearing one character at a time."""
        for i in range(len(self.full_text) + 1):
            self.update(self.full_text[:i])
            await asyncio.sleep(self.speed)


class SplashScreen(Screen):
    """Animated splash screen with rotating cube."""

    BINDINGS = [
        Binding("space", "next_screen", "Continue", show=True),
        Binding("enter", "next_screen", "Continue", show=False),
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_CSS = """
    SplashScreen {
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
        align: center middle;
        background: transparent;
    }

    #splash-box {
        width: auto;
        height: auto;
        align: center middle;
        background: transparent;
    }

    #cube-container {
        width: 60;
        height: 24;
        background: transparent;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: #ffffff;
        background: transparent;
        width: 100%;
        margin-top: 1;
    }

    #prompt {
        text-align: center;
        color: #00ffff;
        background: transparent;
        width: 100%;
        margin-top: 2;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the splash screen."""
        from textual.containers import Vertical

        yield AnimatedGradient(id="gradient-bg")
        with Container(id="content"):
            with Vertical(id="splash-box"):
                with Container(id="cube-container"):
                    yield RotatingCube()
                yield TypewriterText("TERMINAL WRAPPED", speed=0.08, id="title")
                yield TypewriterText("PRESS ENTER TO CONTINUE", speed=0.04, id="prompt")

    def action_next_screen(self) -> None:
        """Advance to the first stats screen."""
        self.app.switch_screen("top_commands")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
