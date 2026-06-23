import math
from typing import Iterable, List, Optional, Tuple

from pyautocad_lighting.models import Point, Room


def _almost_equal(left: float, right: float, tolerance: float = 1e-6) -> bool:
    return abs(left - right) <= tolerance


def _normalize_polyline(points: Iterable[Point]) -> List[Point]:
    normalized = [(float(x), float(y)) for x, y in points]
    if len(normalized) >= 2 and normalized[0] == normalized[-1]:
        normalized = normalized[:-1]
    return normalized


def rectangle_from_polyline(identifier: str, points: Iterable[Point]) -> Optional[Room]:
    vertices = _normalize_polyline(points)
    if len(vertices) != 4:
        return None

    xs = sorted({point[0] for point in vertices})
    ys = sorted({point[1] for point in vertices})
    if len(xs) != 2 or len(ys) != 2:
        return None

    expected_corners = {
        (xs[0], ys[0]),
        (xs[0], ys[1]),
        (xs[1], ys[0]),
        (xs[1], ys[1]),
    }
    if set(vertices) != expected_corners:
        return None

    return Room(identifier=identifier, min_x=xs[0], min_y=ys[0], max_x=xs[1], max_y=ys[1])


def _candidate_layouts(count: int):
    for rows in range(1, count + 1):
        cols = math.ceil(count / rows)
        yield rows, cols


def _layout_score(room: Room, rows: int, cols: int, count: int) -> float:
    aspect_ratio = room.width / room.height if room.height else float("inf")
    grid_ratio = cols / rows
    unused = rows * cols - count
    return abs(grid_ratio - aspect_ratio) + unused * 0.1


def grid_points(room: Room, count: int) -> List[Point]:
    if count <= 0:
        return []
    if count == 1:
        return [room.center]

    rows, cols = min(
        _candidate_layouts(count),
        key=lambda layout: _layout_score(room, layout[0], layout[1], count),
    )

    x_spacing = room.width / (cols + 1)
    y_spacing = room.height / (rows + 1)

    points: List[Point] = []
    for row in range(rows):
        y = room.min_y + y_spacing * (row + 1)
        for col in range(cols):
            x = room.min_x + x_spacing * (col + 1)
            points.append((x, y))

    if len(points) == count:
        return points

    overflow = len(points) - count
    trim_start = overflow // 2
    trim_end = trim_start + count
    return points[trim_start:trim_end]


def ordered_connections(points: List[Point]) -> List[Tuple[Point, Point]]:
    if len(points) < 2:
        return []

    ordered = sorted(points, key=lambda point: (point[1], point[0]))
    return list(zip(ordered, ordered[1:]))


def label_position(room: Room, offset_x: float, offset_y: float) -> Point:
    return (room.max_x + offset_x, room.max_y + offset_y)
