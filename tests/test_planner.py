import unittest

from pyautocad_lighting.catalog import FIXTURE_TYPES
from pyautocad_lighting.models import PlacementOptions, Room
from pyautocad_lighting.planner import build_batch_plan, build_room_plan


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.room = Room(identifier="Room 1", min_x=0, min_y=0, max_x=6, max_y=4)
        self.options = PlacementOptions(
            fixture=FIXTURE_TYPES["Panneau LED 60×60"],
            lights_per_room=4,
            draw_wires=True,
            add_labels=True,
            wire_bulge=0.3,
            label_prefix="C",
            auto_increment_labels=True,
            fixed_label="",
            label_offset_x=100,
            label_offset_y=200,
            label_height=250,
        )

    def test_room_plan_creates_fixtures_wires_and_labels(self):
        plan = build_room_plan(self.room, self.options, 7)

        self.assertEqual(len(plan.fixtures), 4)
        self.assertEqual(len(plan.wires), 3)
        self.assertEqual(plan.labels[0].text, "C7")
        self.assertEqual(plan.labels[0].position, (106, 204))

    def test_batch_plan_advances_circuit_numbers(self):
        second_room = Room(identifier="Room 2", min_x=10, min_y=0, max_x=16, max_y=4)

        plans, next_circuit = build_batch_plan([self.room, second_room], self.options, 3)

        self.assertEqual([plan.labels[0].text for plan in plans], ["C3", "C4"])
        self.assertEqual(next_circuit, 5)


if __name__ == "__main__":
    unittest.main()
