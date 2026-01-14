"""Rotating 3D ASCII cube widget."""

import math
from time import time

from rich.text import Text
from textual.widget import Widget


class RotatingCube(Widget):
    """A rotating 3D ASCII cube rendered in the terminal."""

    DEFAULT_CSS = """
    RotatingCube {
        width: 100%;
        height: 100%;
    }
    """

    VERTICES = [
        (-1, -1, -1),
        (1, -1, -1),
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (1, 1, 1),
        (-1, 1, 1),
    ]

    EDGES = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]

    EDGE_CHAR = "#"
    VERTEX_CHAR = "@"

    def on_mount(self) -> None:
        """Start animation on mount."""
        self.auto_refresh = 1 / 30

    def rotate_point(
        self,
        x: float,
        y: float,
        z: float,
        angle_x: float,
        angle_y: float,
        angle_z: float,
    ) -> tuple[float, float, float]:
        """Apply 3D rotation matrices around X, Y, Z axes."""
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

        cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z

        return x, y, z

    def project(
        self, x: float, y: float, z: float, width: int, height: int, scale: float = 6
    ) -> tuple[int, int, float]:
        """Project 3D point to 2D screen coordinates with perspective."""
        distance = 5
        factor = distance / (distance + z)
        screen_x = int(width / 2 + x * factor * scale * 2)
        screen_y = int(height / 2 + y * factor * scale)
        return screen_x, screen_y, z

    def _draw_line(
        self,
        buffer: list[list[str]],
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        width: int,
        height: int,
        char: str = "#",
    ) -> None:
        """Draw a line using Bresenham's algorithm."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                buffer[y0][x0] = char
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def render(self) -> Text:
        """Render the rotating cube."""
        t = time()
        angle_x = t * 0.7
        angle_y = t * 1.0
        angle_z = t * 0.4

        width = self.size.width
        height = self.size.height

        if width < 4 or height < 4:
            return Text("")

        buffer = [[" " for _ in range(width)] for _ in range(height)]

        projected = []
        for vx, vy, vz in self.VERTICES:
            rx, ry, rz = self.rotate_point(vx, vy, vz, angle_x, angle_y, angle_z)
            px, py, pz = self.project(rx, ry, rz, width, height)
            projected.append((px, py, pz))

        edge_depths = []
        for start, end in self.EDGES:
            avg_z = (projected[start][2] + projected[end][2]) / 2
            edge_depths.append((avg_z, start, end))
        edge_depths.sort(reverse=True)

        for _, start, end in edge_depths:
            x0, y0, _ = projected[start]
            x1, y1, _ = projected[end]
            self._draw_line(buffer, x0, y0, x1, y1, width, height, self.EDGE_CHAR)

        for px, py, _ in projected:
            if 0 <= px < width and 0 <= py < height:
                buffer[py][px] = self.VERTEX_CHAR

        lines = []
        for row in buffer:
            line = "".join(row)
            lines.append(line)

        result = Text("\n".join(lines))
        result.stylize("bold cyan")
        return result
