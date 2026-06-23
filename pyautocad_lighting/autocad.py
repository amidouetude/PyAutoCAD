import logging
from typing import Any, Iterable, List, Sequence

from pyautocad_lighting.geometry import rectangle_from_polyline
from pyautocad_lighting.models import Point, Room, RoomPlan


class AutoCADError(RuntimeError):
    pass


class AutoCADClient:
    def __init__(self) -> None:
        self._application = None
        self._document = None
        self._model_space = None

    @property
    def connected(self) -> bool:
        return self._model_space is not None

    def connect(self) -> None:
        try:
            import win32com.client
        except ImportError as exc:
            raise AutoCADError(
                "pywin32 is required on Windows to connect to AutoCAD."
            ) from exc

        self._application = win32com.client.Dispatch("AutoCAD.Application")
        self._document = self._application.ActiveDocument
        self._model_space = self._document.ModelSpace

    def scan_rooms(self) -> List[Room]:
        self._ensure_connected()
        rooms: List[Room] = []
        for entity in self._model_space:
            object_name = getattr(entity, "ObjectName", "")
            if object_name not in {"AcDbPolyline", "AcDb2dPolyline"}:
                continue
            if not getattr(entity, "Closed", False):
                continue

            room = rectangle_from_polyline(
                identifier=f"Room {len(rooms) + 1}",
                points=_polyline_points(entity.Coordinates),
            )
            if room is not None:
                rooms.append(room)
        return rooms

    def apply_plans(self, plans: Sequence[RoomPlan], logger: logging.Logger) -> None:
        self._ensure_connected()
        for plan in plans:
            logger.info("Placing %s fixtures in %s", len(plan.fixtures), plan.room.name)
            for fixture in plan.fixtures:
                self._ensure_layer(fixture.layer)
                self._insert_block(fixture.position, fixture.block_name, fixture.layer)

            for wire in plan.wires:
                self._ensure_layer(wire.layer)
                self._draw_wire(wire.start, wire.end, wire.bulge, wire.layer)

            for label in plan.labels:
                self._ensure_layer(label.layer)
                self._add_label(label.text, label.position, label.height, label.layer)

    def _ensure_connected(self) -> None:
        if not self.connected:
            raise AutoCADError("Connect to AutoCAD before scanning or placing fixtures.")

    def _ensure_layer(self, layer_name: str) -> None:
        try:
            self._document.Layers.Item(layer_name)
        except Exception:
            self._document.Layers.Add(layer_name)

    def _insert_block(self, point: Point, block_name: str, layer_name: str) -> None:
        block = self._model_space.InsertBlock(_point3d(point), block_name, 1.0, 1.0, 1.0, 0.0)
        block.Layer = layer_name

    def _draw_wire(self, start: Point, end: Point, bulge: float, layer_name: str) -> None:
        line = self._model_space.AddLightWeightPolyline([start[0], start[1], end[0], end[1]])
        line.Layer = layer_name
        if bulge:
            line.SetBulge(0, bulge)

    def _add_label(self, text: str, point: Point, height: float, layer_name: str) -> None:
        label = self._model_space.AddText(text, _point3d(point), height)
        label.Layer = layer_name


def _polyline_points(coordinates: Iterable[float]) -> List[Point]:
    """Convert flat polyline coordinates into consecutive (x, y) point tuples."""
    values = list(coordinates)
    return [(values[index], values[index + 1]) for index in range(0, len(values), 2)]


def _point3d(point: Point) -> Any:
    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        raise AutoCADError("pywin32 is required on Windows to connect to AutoCAD.") from exc

    return win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8,
        (point[0], point[1], 0.0),
    )
