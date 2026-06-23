from dataclasses import dataclass
from typing import List, Tuple


Point = Tuple[float, float]


@dataclass(frozen=True)
class FixtureType:
    name: str
    block_name: str
    layer: str


@dataclass(frozen=True)
class Room:
    identifier: str
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def center(self) -> Point:
        return ((self.min_x + self.max_x) / 2.0, (self.min_y + self.max_y) / 2.0)

    @property
    def name(self) -> str:
        return (
            f"{self.identifier} ({self.width:.2f}×{self.height:.2f})"
        )


@dataclass(frozen=True)
class PlacementOptions:
    fixture: FixtureType
    lights_per_room: int
    draw_wires: bool
    add_labels: bool
    wire_bulge: float
    label_prefix: str
    auto_increment_labels: bool
    fixed_label: str
    label_offset_x: float = 0.0
    label_offset_y: float = 0.0
    label_height: float = 250.0


@dataclass(frozen=True)
class FixturePlacement:
    position: Point
    block_name: str
    layer: str


@dataclass(frozen=True)
class WirePlacement:
    start: Point
    end: Point
    bulge: float
    layer: str


@dataclass(frozen=True)
class LabelPlacement:
    text: str
    position: Point
    layer: str
    height: float


@dataclass(frozen=True)
class RoomPlan:
    room: Room
    fixtures: List[FixturePlacement]
    wires: List[WirePlacement]
    labels: List[LabelPlacement]

