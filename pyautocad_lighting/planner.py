from typing import Iterable, List, Tuple

from pyautocad_lighting.catalog import LABEL_LAYER, WIRE_LAYER
from pyautocad_lighting.geometry import grid_points, label_position, ordered_connections
from pyautocad_lighting.models import (
    FixturePlacement,
    LabelPlacement,
    PlacementOptions,
    Room,
    RoomPlan,
    WirePlacement,
)


def _label_text(options: PlacementOptions, circuit_number: int) -> str:
    """Build the circuit label from either an incrementing index or a fixed value."""
    if options.auto_increment_labels:
        return f"{options.label_prefix}{circuit_number}"
    return options.fixed_label or options.label_prefix


def build_room_plan(room: Room, options: PlacementOptions, circuit_number: int) -> RoomPlan:
    fixture_points = grid_points(room, options.lights_per_room)
    fixtures = [
        FixturePlacement(
            position=point,
            block_name=options.fixture.block_name,
            layer=options.fixture.layer,
        )
        for point in fixture_points
    ]

    wires = [] if not options.draw_wires else [
        WirePlacement(start=start, end=end, bulge=options.wire_bulge, layer=WIRE_LAYER)
        for start, end in ordered_connections(fixture_points)
    ]

    labels = []
    if options.add_labels:
        labels.append(
            LabelPlacement(
                text=_label_text(options, circuit_number),
                position=label_position(room, options.label_offset_x, options.label_offset_y),
                layer=LABEL_LAYER,
                height=options.label_height,
            )
        )

    return RoomPlan(room=room, fixtures=fixtures, wires=wires, labels=labels)


def build_batch_plan(
    rooms: Iterable[Room],
    options: PlacementOptions,
    starting_circuit: int,
) -> Tuple[List[RoomPlan], int]:
    plans: List[RoomPlan] = []
    circuit_number = starting_circuit
    for room in rooms:
        plans.append(build_room_plan(room, options, circuit_number))
        if options.auto_increment_labels:
            circuit_number += 1
    return plans, circuit_number
