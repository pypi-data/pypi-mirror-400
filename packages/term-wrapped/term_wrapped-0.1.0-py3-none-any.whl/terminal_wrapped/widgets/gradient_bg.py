"""Animated gradient background widget."""

from time import time

from textual.renderables.gradient import LinearGradient
from textual.widget import Widget

SYNTHWAVE_STOPS = [
    (0.0, "#ff00ff"),
    (0.2, "#ff0080"),
    (0.4, "#8000ff"),
    (0.6, "#0080ff"),
    (0.8, "#00ffff"),
    (1.0, "#ff00ff"),
]

RAINBOW_STOPS = [
    (0.0, "#ff0000"),
    (0.17, "#ff8000"),
    (0.33, "#ffff00"),
    (0.5, "#00ff00"),
    (0.67, "#0080ff"),
    (0.83, "#8000ff"),
    (1.0, "#ff0000"),
]

OCEAN_STOPS = [
    (0.0, "#000033"),
    (0.25, "#000066"),
    (0.5, "#0066cc"),
    (0.75, "#00ccff"),
    (1.0, "#000033"),
]


class AnimatedGradient(Widget):
    """An animated gradient background widget."""

    DEFAULT_CSS = """
    AnimatedGradient {
        width: 100%;
        height: 100%;
    }
    """

    def __init__(
        self,
        stops: list[tuple[float, str]] | None = None,
        speed: float = 45.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.stops = stops or SYNTHWAVE_STOPS
        self.speed = speed

    def on_mount(self) -> None:
        """Start animation on mount."""
        self.auto_refresh = 1 / 30

    def render(self) -> LinearGradient:
        """Render the animated gradient."""
        angle = time() * self.speed
        return LinearGradient(angle, self.stops)
