"""StainSTORM Jena Orchestrator as an Arkitekt workflow app.

Coordinates the Fairino robot arm (fairinogale), the Opentrons OT-2 (ot2windy),
and the ImSwitch microscope (imswitch) using the Jena station layout.

Run locally with uv:
    uv run app.py   # then open http://localhost:8080/ to bind it.

Or with Docker Compose:
    docker compose up -d --build   # then open http://localhost:8082/ to bind it.

ORCHESTRATOR_CONFIG picks another config.yaml (default: next to this file).
"""

import os
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Annotated, Protocol

import yaml
from arkitekt import App, Description, Effects, Task
from arkitekt.widgets import withChoices
from arkitekt_spec.declare.definition.demands import demand
from mikro.arkitekt.specs import MultichannelImage

from arkitekt_bind import serve

HERE = Path(__file__).resolve().parent
CONFIG = Path(os.getenv("ORCHESTRATOR_CONFIG", HERE / "config.yaml"))

if not CONFIG.exists():  # first start: copy the defaults where they can be edited
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE / "config.example.yaml", CONFIG)

cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

APP_NAME = cfg.get("app", "stainstorm_orchestrator_jena")
FAIRINO_APP = cfg.get("fairino_app", "arkirino")
OPENTRONS_APP = cfg.get("opentrons_app", "ot2")
MICROSCOPE_APP = cfg.get("microscope_app", "imswitch")
PICKUP_STATION = cfg.get("stations", {}).get("pickup", "pickupstation")
OPENTRONS_STATION = cfg.get("stations", {}).get("opentrons", "opentrons")
MICROSCOPE_STATION = cfg.get("stations", {}).get("microscope", "microscope")
PROTOCOLS = list(cfg.get("protocols", ["staining", "staining_full", "dummy"]))
DEFAULT_PROTOCOL = str(cfg.get("default_protocol", "dummy" if "dummy" in PROTOCOLS else PROTOCOLS[0]))
DEFAULT_SPEED = int(cfg.get("speed", 20))
DEFAULT_ACC = int(cfg.get("acceleration", 70))
DEFAULT_DANGER_SPEED = int(cfg.get("danger_speed", 10))
MICROSCOPE_CFG = cfg.get("microscope", {})
DEFAULT_SCAN_MODE = str(MICROSCOPE_CFG.get("scan_mode", "tile_scan"))
DEFAULT_MOVE_TO_LOADING = bool(MICROSCOPE_CFG.get("move_to_loading_position", True))
DEFAULT_RANGE_X_UM = float(MICROSCOPE_CFG.get("range_x_um", 1000.0))
DEFAULT_RANGE_Y_UM = float(MICROSCOPE_CFG.get("range_y_um", 1000.0))
DEFAULT_OVERLAP_PERCENT = float(MICROSCOPE_CFG.get("overlap_percent", 10.0))
DEFAULT_AUTOFOCUS = bool(MICROSCOPE_CFG.get("autofocus", False))

app = App(APP_NAME, "1.0.0", effects=Effects.NONE)

ProtocolChoice = Annotated[str, withChoices(*PROTOCOLS), Description("Opentrons-Protokoll aus config.yaml")]
ScanMode = Annotated[
    str,
    withChoices("tile_scan", "single_frame", "none"),
    Description("Mikroskop-Scan nach der Färbung (tile_scan, single_frame oder none)"),
]
MoveToLoading = Annotated[bool, Description("Vor Ablegen/Abholen am Mikroskop Ladeposition anfahren")]
RangeUm = Annotated[float, Description("Scan-Bereich am Mikroskop in µm")]
OverlapPercent = Annotated[float, Description("Überlappung zwischen Kacheln beim Tile-Scan in %")]
Autofocus = Annotated[bool, Description("Autofokus während des Tile-Scans aktivieren")]
InitRobot = Annotated[bool, Description("Vorab init_robot_and_gripper am Fairino ausführen")]
Speed = Annotated[int, Description("Fairino Geschwindigkeit in % außerhalb von Gefahrenzonen")]
Acceleration = Annotated[int, Description("Fairino Beschleunigung in %")]
DangerSpeed = Annotated[int, Description("Fairino Geschwindigkeit in % an Gefahren-/Greifpunkten")]


@app.declare(app=FAIRINO_APP, auto_resolvable=True, min=1)
class FairinoArm(Protocol):
    """Fairino Roboterarm (fairinogale)."""

    def init_robot_and_gripper(self) -> None:
        """Init Robot and Gripper"""
        ...

    def pick_up(
        self,
        station: str,
        sample: str = "",
        speed: int = DEFAULT_SPEED,
        acceleration: int = DEFAULT_ACC,
        danger_speed: int = DEFAULT_DANGER_SPEED,
    ) -> None:
        """Pick Up"""
        ...

    def release_at(
        self,
        station: str,
        sample: str = "",
        speed: int = DEFAULT_SPEED,
        acceleration: int = DEFAULT_ACC,
        danger_speed: int = DEFAULT_DANGER_SPEED,
    ) -> None:
        """Release At"""
        ...

    def home_robot(self, speed: int = 30, acceleration: int = 30) -> None:
        """Home Robot"""
        ...


@app.declare(app=OPENTRONS_APP, auto_resolvable=True, min=1)
class OpentronsOT2(Protocol):
    """Opentrons OT-2 Pipettierroboter (ot2windy)."""

    def run_protocol(self, protocol: str) -> None:
        """Run Protocol"""
        ...

    def get_robot_status(self) -> str:
        """Robot Status"""
        ...

    def set_lights(self, on: bool = True) -> None:
        """Set Lights"""
        ...


@app.declare(app=MICROSCOPE_APP, auto_resolvable=True, min=1)
class Microscope(Protocol):
    """ImSwitch Mikroskop (imswitch)."""

    @demand(match_ports=False, optional=True)
    def move_to_sample_loading_position(self) -> None:
        """Move To Sample Loading Position"""
        ...

    @demand(match_ports=False, optional=True)
    def acquire_frame(self, name: str | None = None) -> MultichannelImage:
        """Acquire Frame"""
        ...

    @demand(match_ports=False, optional=True)
    def run_tile_scan(
        self,
        range_x_um: float = DEFAULT_RANGE_X_UM,
        range_y_um: float = DEFAULT_RANGE_Y_UM,
        center_x_um: float | None = None,
        center_y_um: float | None = None,
        overlap_percent: float = DEFAULT_OVERLAP_PERCENT,
        autofocus: bool = DEFAULT_AUTOFOCUS,
    ) -> Generator[MultichannelImage, None, None]:
        """Run Tile Scan"""
        ...


@app.workflow
def run_staining_cycle(
    fairino: FairinoArm,
    opentrons: OpentronsOT2,
    microscope: Microscope,
    protocol: ProtocolChoice = DEFAULT_PROTOCOL,
    scan_mode: ScanMode = DEFAULT_SCAN_MODE,
    move_to_loading_position: MoveToLoading = DEFAULT_MOVE_TO_LOADING,
    range_x_um: RangeUm = DEFAULT_RANGE_X_UM,
    range_y_um: RangeUm = DEFAULT_RANGE_Y_UM,
    overlap_percent: OverlapPercent = DEFAULT_OVERLAP_PERCENT,
    autofocus: Autofocus = DEFAULT_AUTOFOCUS,
    init_robot: InitRobot = True,
    speed: Speed = DEFAULT_SPEED,
    acceleration: Acceleration = DEFAULT_ACC,
    danger_speed: DangerSpeed = DEFAULT_DANGER_SPEED,
    *,
    task: Task,
) -> list[MultichannelImage]:
    """Run Staining Cycle (Jena)

    Führt den vollständigen Färbe- und Mikroskopie-Zyklus aus:
    Pickupstation -> Opentrons (Protokoll) -> Mikroskop (Scan) -> Pickupstation.
    Gibt die am Mikroskop aufgenommenen Bilder zurück.
    """
    images: list[MultichannelImage] = []

    if init_robot:
        task.log("Schritt 1/11: Initialisiere Fairino Roboter und Greifer...")
        task.progress(5, "Initialisiere Fairino & Greifer")
        fairino.init_robot_and_gripper()

    task.log(f"Schritt 2/11: Hole Slice von Station '{PICKUP_STATION}' ab...")
    task.progress(10, f"Abholen von {PICKUP_STATION}")
    fairino.pick_up(
        station=PICKUP_STATION,
        sample="",
        speed=speed,
        acceleration=acceleration,
        danger_speed=danger_speed,
    )

    task.log(f"Schritt 3/11: Lege Slice in Station '{OPENTRONS_STATION}' ab...")
    task.progress(20, f"Ablegen in {OPENTRONS_STATION}")
    fairino.release_at(
        station=OPENTRONS_STATION,
        sample="",
        speed=speed,
        acceleration=acceleration,
        danger_speed=danger_speed,
    )

    task.log(f"Schritt 4/11: Starte Opentrons-Protokoll '{protocol}' und warte auf Abschluss...")
    task.progress(30, f"Opentrons Protokoll '{protocol}' läuft")
    opentrons.run_protocol(protocol=protocol)  # die Run-ID steht im Log des OT-2-Tasks
    task.log(f"Opentrons-Protokoll '{protocol}' abgeschlossen.")

    task.log(f"Schritt 5/11: Hole Slice aus Station '{OPENTRONS_STATION}' ab...")
    task.progress(50, f"Abholen aus {OPENTRONS_STATION}")
    fairino.pick_up(
        station=OPENTRONS_STATION,
        sample="",
        speed=speed,
        acceleration=acceleration,
        danger_speed=danger_speed,
    )

    if move_to_loading_position:
        task.log("Schritt 6/11: Fahre Mikroskop in Ladeposition...")
        task.progress(55, "Mikroskop Ladeposition")
        microscope.move_to_sample_loading_position()

    task.log(f"Schritt 7/11: Lege Slice auf Station '{MICROSCOPE_STATION}' ab...")
    task.progress(60, f"Ablegen auf {MICROSCOPE_STATION}")
    fairino.release_at(
        station=MICROSCOPE_STATION,
        sample="",
        speed=speed,
        acceleration=acceleration,
        danger_speed=danger_speed,
    )

    if scan_mode == "tile_scan":
        task.log(f"Schritt 8/11: Starte Mikroskop Tile-Scan ({range_x_um}x{range_y_um} µm)...")
        task.progress(70, "Mikroskop Tile-Scan läuft")
        for image in microscope.run_tile_scan(
            range_x_um=range_x_um,
            range_y_um=range_y_um,
            overlap_percent=overlap_percent,
            autofocus=autofocus,
        ):
            images.append(image)
        task.log(f"Mikroskop Tile-Scan abgeschlossen ({len(images)} Kachel(n)).")
    elif scan_mode == "single_frame":
        task.log("Schritt 8/11: Nehme einzelnes Mikroskop-Bild auf...")
        task.progress(70, "Mikroskop Einzelbild")
        image = microscope.acquire_frame(name=f"StainSTORM {protocol}")
        if image is not None:
            images.append(image)
        task.log("Mikroskop Einzelbild abgeschlossen.")
    else:
        task.log("Schritt 8/11: Mikroskop-Scan übersprungen (scan_mode='none').")
        task.progress(70, "Mikroskop-Scan übersprungen")

    if move_to_loading_position:
        task.log("Schritt 9/11: Fahre Mikroskop wieder in Ladeposition...")
        task.progress(80, "Mikroskop Ladeposition")
        microscope.move_to_sample_loading_position()

    task.log(f"Schritt 10/11: Hole Slice von Station '{MICROSCOPE_STATION}' ab...")
    task.progress(85, f"Abholen von {MICROSCOPE_STATION}")
    fairino.pick_up(
        station=MICROSCOPE_STATION,
        sample="",
        speed=speed,
        acceleration=acceleration,
        danger_speed=danger_speed,
    )

    task.log(f"Schritt 11/11: Bringe Slice zurück zur Station '{PICKUP_STATION}'...")
    task.progress(95, f"Zurückbringen zu {PICKUP_STATION}")
    fairino.release_at(
        station=PICKUP_STATION,
        sample="",
        speed=speed,
        acceleration=acceleration,
        danger_speed=danger_speed,
    )

    task.progress(100, "Ablauf erfolgreich abgeschlossen")
    task.log(
        f"Workflow fertig! Slice ist zurück in '{PICKUP_STATION}' "
        f"(Mikroskop-Bilder: {len(images)})."
    )
    return images


if __name__ == "__main__":
    serve(app, CONFIG, int(os.getenv("PORT", "8080")))
