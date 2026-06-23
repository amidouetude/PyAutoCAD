import unittest

from pyautocad_lighting.geometry import grid_points, rectangle_from_polyline


class RectangleDetectionTests(unittest.TestCase):
    def test_detects_closed_rectangle(self):
        room = rectangle_from_polyline(
            "Room 1",
            [(0, 0), (4, 0), (4, 2), (0, 2), (0, 0)],
        )

        self.assertIsNotNone(room)
        self.assertEqual(room.width, 4)
        self.assertEqual(room.height, 2)

    def test_rejects_non_rectangle(self):
        room = rectangle_from_polyline(
            "Room 1",
            [(0, 0), (4, 0), (3, 2), (0, 2), (0, 0)],
        )

        self.assertIsNone(room)


class GridPlacementTests(unittest.TestCase):
    def test_single_fixture_uses_room_center(self):
        room = rectangle_from_polyline(
            "Room 1",
            [(0, 0), (6, 0), (6, 4), (0, 4), (0, 0)],
        )

        self.assertEqual(grid_points(room, 1), [(3.0, 2.0)])

    def test_multiple_fixtures_stay_inside_room(self):
        room = rectangle_from_polyline(
            "Room 1",
            [(0, 0), (8, 0), (8, 4), (0, 4), (0, 0)],
        )

        points = grid_points(room, 5)

        self.assertEqual(len(points), 5)
        for x, y in points:
            self.assertGreater(x, room.min_x)
            self.assertLess(x, room.max_x)
            self.assertGreater(y, room.min_y)
            self.assertLess(y, room.max_y)


if __name__ == "__main__":
    unittest.main()
