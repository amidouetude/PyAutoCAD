from pyautocad_lighting.models import FixtureType


FIXTURE_TYPES = {
    "Panneau LED 60×60": FixtureType(
        name="Panneau LED 60×60",
        block_name="Panneau LED 60x60",
        layer="ECLAIRAGE-PANNEAU",
    ),
    "Spot CoreLine DN140B": FixtureType(
        name="Spot CoreLine DN140B",
        block_name="Spot CoreLine DN140B",
        layer="ECLAIRAGE-SPOT",
    ),
    "Hublot étanche 11W": FixtureType(
        name="Hublot étanche 11W",
        block_name="Hublot étanche 11W",
        layer="ECLAIRAGE-HUBLOT",
    ),
    "Applique étanche 11W": FixtureType(
        name="Applique étanche 11W",
        block_name="Applique étanche 11W",
        layer="ECLAIRAGE-APPLIQUE",
    ),
    "Brasseur d'air 75W": FixtureType(
        name="Brasseur d'air 75W",
        block_name="Brasseur d'air 75W",
        layer="ECLAIRAGE-BRASSEUR",
    ),
}

WIRE_LAYER = "ECLAIRAGE-FIL"
LABEL_LAYER = "ECLAIRAGE-TEXTE"

