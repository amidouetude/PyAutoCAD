# PyAutoCAD

A Tkinter-based GUI application that automates the placement of lighting fixtures, wiring, and circuit labels in AutoCAD drawings.

## Key features

- Direct AutoCAD COM integration with no export/import step
- Detection of closed rectangular polylines as candidate rooms
- Grid-based fixture placement for one or many rooms at once
- Support for LED panels, spots, waterproof fixtures, wall fixtures, and exhaust fans
- Automatic layer management for fixtures, wires, and labels
- Curved wire drawing through AutoCAD polyline bulges
- Auto-incrementing or fixed circuit labels
- Threaded COM worker to keep the UI responsive during CAD operations

## Supported fixtures

- Panneau LED 60×60
- Spot CoreLine DN140B
- Hublot étanche 11W
- Applique étanche 11W
- Brasseur d'air 75W

## Installation

```bash
pip install pywin32
```

`pyautocad` can still be installed alongside the app if you want it available in your AutoCAD Python environment, but the current implementation talks to AutoCAD through `pywin32`.

## Usage

Run the application while AutoCAD is already open with the target drawing loaded:

```bash
python -m pyautocad_lighting
```

Workflow:

1. Click **Connect** to attach to the active AutoCAD session
2. Click **Scan** to list all closed rectangular rooms
3. Select one or more rooms
4. Configure fixture type, quantity, wire options, and labels
5. Click **Place Lights**

## Requirements

- Windows
- AutoCAD 2007 or newer
- Python 3.6+
- `pywin32` (`pyautocad` optional)
