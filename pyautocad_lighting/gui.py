import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Iterable, List

from pyautocad_lighting.autocad import AutoCADClient
from pyautocad_lighting.catalog import FIXTURE_TYPES
from pyautocad_lighting.models import PlacementOptions, Room
from pyautocad_lighting.planner import build_batch_plan
from pyautocad_lighting.worker import COMWorker


class TkLogHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def emit(self, record):
        self._callback(self.format(record))


class LightingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PyAutoCAD Lighting Planner")
        self.geometry("900x650")

        self._worker = COMWorker()
        self._client = AutoCADClient()
        self._rooms: List[Room] = []
        self._next_circuit = 1
        self._room_lookup = {}

        self.status_var = tk.StringVar(value="Ready")
        self.fixture_var = tk.StringVar(value=next(iter(FIXTURE_TYPES)))
        self.lights_var = tk.IntVar(value=4)
        self.draw_wires_var = tk.BooleanVar(value=True)
        self.add_labels_var = tk.BooleanVar(value=True)
        self.bulge_var = tk.DoubleVar(value=0.25)
        self.prefix_var = tk.StringVar(value="C")
        self.auto_increment_var = tk.BooleanVar(value=True)
        self.fixed_label_var = tk.StringVar(value="")
        self.offset_x_var = tk.DoubleVar(value=300.0)
        self.offset_y_var = tk.DoubleVar(value=300.0)
        self.label_height_var = tk.DoubleVar(value=250.0)

        self._logger = logging.getLogger("pyautocad_lighting")
        self._logger.setLevel(logging.INFO)
        self._logger.handlers.clear()
        handler = TkLogHandler(lambda message: self.after(0, self._append_log, message))
        handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        self._logger.addHandler(handler)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        controls = ttk.Frame(self, padding=12)
        controls.pack(fill=tk.X)

        ttk.Button(controls, text="Connect", command=self.connect).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(controls, text="Scan", command=self.scan_rooms).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(controls, text="Place Lights", command=self.place_lights).grid(row=0, column=2, padx=4, pady=4)

        ttk.Label(controls, text="Fixture").grid(row=1, column=0, sticky=tk.W, padx=4)
        ttk.Combobox(
            controls,
            textvariable=self.fixture_var,
            values=list(FIXTURE_TYPES),
            state="readonly",
            width=30,
        ).grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=4, pady=4)

        ttk.Label(controls, text="Lights/room").grid(row=2, column=0, sticky=tk.W, padx=4)
        ttk.Spinbox(controls, from_=1, to=64, textvariable=self.lights_var, width=8).grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Checkbutton(controls, text="Draw wires", variable=self.draw_wires_var).grid(row=3, column=0, sticky=tk.W, padx=4)
        ttk.Checkbutton(controls, text="Add labels", variable=self.add_labels_var).grid(row=3, column=1, sticky=tk.W, padx=4)
        ttk.Checkbutton(controls, text="Auto increment labels", variable=self.auto_increment_var).grid(row=3, column=2, sticky=tk.W, padx=4)

        ttk.Label(controls, text="Wire bulge").grid(row=4, column=0, sticky=tk.W, padx=4)
        ttk.Entry(controls, textvariable=self.bulge_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(controls, text="Label prefix").grid(row=5, column=0, sticky=tk.W, padx=4)
        ttk.Entry(controls, textvariable=self.prefix_var, width=10).grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(controls, text="Fixed label").grid(row=5, column=2, sticky=tk.W, padx=4)
        ttk.Entry(controls, textvariable=self.fixed_label_var, width=14).grid(row=5, column=3, sticky=tk.W, padx=4, pady=4)

        ttk.Label(controls, text="Label offset X").grid(row=6, column=0, sticky=tk.W, padx=4)
        ttk.Entry(controls, textvariable=self.offset_x_var, width=10).grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(controls, text="Label offset Y").grid(row=6, column=2, sticky=tk.W, padx=4)
        ttk.Entry(controls, textvariable=self.offset_y_var, width=10).grid(row=6, column=3, sticky=tk.W, padx=4, pady=4)

        ttk.Label(controls, text="Label height").grid(row=7, column=0, sticky=tk.W, padx=4)
        ttk.Entry(controls, textvariable=self.label_height_var, width=10).grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)

        body = ttk.Frame(self, padding=(12, 0, 12, 12))
        body.pack(fill=tk.BOTH, expand=True)

        room_frame = ttk.LabelFrame(body, text="Detected Rooms")
        room_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        self.room_listbox = tk.Listbox(room_frame, selectmode=tk.EXTENDED)
        self.room_listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        log_frame = ttk.LabelFrame(body, text="Log")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        self.log_text = tk.Text(log_frame, state=tk.DISABLED, height=18)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

    def connect(self) -> None:
        self._set_status("Connecting to AutoCAD...")
        self._worker.submit(self._client.connect, on_success=lambda _: self.after(0, self._connected), on_error=self._async_error)

    def scan_rooms(self) -> None:
        self._set_status("Scanning rooms...")
        self._worker.submit(self._client.scan_rooms, on_success=lambda rooms: self.after(0, self._show_rooms, rooms), on_error=self._async_error)

    def place_lights(self) -> None:
        selected_rooms = self._selected_rooms()
        if not selected_rooms:
            messagebox.showwarning("No rooms selected", "Select at least one room before placing fixtures.")
            return

        try:
            options = self._options()
        except ValueError as error:
            messagebox.showwarning("Invalid settings", str(error))
            return

        plans, next_circuit = build_batch_plan(selected_rooms, options, self._next_circuit)
        self._set_status(f"Placing lights in {len(plans)} room(s)...")

        def success(_: None) -> None:
            self._next_circuit = next_circuit
            self.after(0, lambda: self._set_status("Placement complete"))

        self._worker.submit(
            self._client.apply_plans,
            plans,
            self._logger,
            on_success=success,
            on_error=self._async_error,
        )

    def _connected(self) -> None:
        self._append_log("INFO - Connected to AutoCAD")
        self._set_status("Connected")

    def _show_rooms(self, rooms: Iterable[Room]) -> None:
        self._rooms = list(rooms)
        self._room_lookup = {}
        self.room_listbox.delete(0, tk.END)
        for index, room in enumerate(self._rooms):
            self.room_listbox.insert(tk.END, room.name)
            self._room_lookup[index] = room
        self._append_log(f"INFO - Detected {len(self._rooms)} room(s)")
        self._set_status(f"Detected {len(self._rooms)} room(s)")

    def _selected_rooms(self) -> List[Room]:
        return [self._room_lookup[index] for index in self.room_listbox.curselection()]

    def _options(self) -> PlacementOptions:
        lights_per_room = int(self.lights_var.get())
        if lights_per_room < 1:
            raise ValueError("Lights per room must be at least 1.")

        return PlacementOptions(
            fixture=FIXTURE_TYPES[self.fixture_var.get()],
            lights_per_room=lights_per_room,
            draw_wires=bool(self.draw_wires_var.get()),
            add_labels=bool(self.add_labels_var.get()),
            wire_bulge=float(self.bulge_var.get()),
            label_prefix=self.prefix_var.get(),
            auto_increment_labels=bool(self.auto_increment_var.get()),
            fixed_label=self.fixed_label_var.get(),
            label_offset_x=float(self.offset_x_var.get()),
            label_offset_y=float(self.offset_y_var.get()),
            label_height=float(self.label_height_var.get()),
        )

    def _async_error(self, error: Exception) -> None:
        self.after(0, lambda: self._show_error(error))

    def _show_error(self, error: Exception) -> None:
        self._append_log(f"ERROR - {error}")
        self._set_status("Operation failed")
        messagebox.showerror("PyAutoCAD", str(error))

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _on_close(self) -> None:
        self._worker.shutdown()
        self.destroy()
