# stainstorm_orchestrator_jena

Eigene **Arkitekt-Workflow-/Orchestrator-App** für das Jena-Setup. Sie steuert über den Arkitekt-Server automatisch den Fairino-Roboterarm (`fairinogale`), den Opentrons OT-2 (`ot2windy`) und das ImSwitch-Mikroskop (`imswitch`) nacheinander an, ohne selbst Hardware-Treiber zu benötigen.

## Workflow-Ablauf (`run_staining_cycle`)

1. **Initialisierung (optional, Schalter `init_robot`, Standard `True`)**: Ruft `fairino.init_robot_and_gripper()` auf.
2. **Slice abholen**: Ruft `fairino.pick_up(station="pickupstation")` auf (Jena-Layout).
3. **Slice in den Opentrons legen**: Ruft `fairino.release_at(station="opentrons")` auf.
4. **Opentrons-Protokoll abspielen & warten**: Ruft `opentrons.run_protocol(protocol=...)` auf und wartet auf den Abschluss auf dem OT-2.
5. **Slice aus dem Opentrons holen**: Ruft `fairino.pick_up(station="opentrons")` auf.
6. **Ladeposition am Mikroskop anfahren (optional, Schalter `move_to_loading_position`, Standard `True`)**: Ruft `microscope.move_to_sample_loading_position()` auf.
7. **Slice aufs Mikroskop legen**: Ruft `fairino.release_at(station="microscope")` auf.
8. **Mikroskop-Scan (`scan_mode`: `tile_scan` | `single_frame` | `none`)**: Führt je nach Modus `microscope.run_tile_scan(...)` oder `microscope.acquire_frame(...)` aus und sammelt die erzeugten `MultichannelImage`-Bilder in Arkitekt (`mikro`).
9. **Ladeposition wieder anfahren (optional)**: Ruft `microscope.move_to_sample_loading_position()` auf.
10. **Slice vom Mikroskop holen**: Ruft `fairino.pick_up(station="microscope")` auf.
11. **Slice zurückbringen**: Ruft `fairino.release_at(station="pickupstation")` auf und gibt die aufgenommenen Mikroskop-Bilder zurück.

---

## Start mit Docker & Docker Compose (empfohlen)

```bash
docker compose up -d --build
```

Die Binding-Weboberfläche läuft anschließend unter:
<http://localhost:8082/>

Konfiguration (`config.yaml`) und gespeicherter Arkitekt-Login (`.state/`) werden persistent im Unterordner `./config` abgelegt. Beim ersten Start wird `config.example.yaml` automatisch dorthin kopiert.

Alternativ direkt mit `docker`:

```bash
docker build -t stainstorm_orchestrator_jena .
docker run -p 8082:8080 -v ./config:/config stainstorm_orchestrator_jena
```

---

## Lokal starten mit Astral `uv`

Voraussetzung: [Astral `uv`](https://docs.astral.sh/uv/) ist installiert.

```bash
uv sync
uv run app.py
```

Die Binding-Weboberfläche ist dann erreichbar unter:
<http://localhost:8080/>

Mit der Umgebungsvariable `ORCHESTRATOR_CONFIG` kann bei Bedarf eine andere `config.yaml` angegeben werden, mit `PORT` ein anderer Web-Port.

---

## Konfiguration (`config.yaml`)

* `fairino_app`, `opentrons_app`, `microscope_app`: Exakte App-Identifier (`appName`-Slug, z. B. `fairinogale`, `ot2windy`, `imswitch` oder `frame-fork`) auf der jeweiligen Binding-Seite bzw. im ImSwitch-Arkitekt-Panel.
* `stations.pickup`, `stations.opentrons`, `stations.microscope`: Stationsnamen in `fairinogale/config.yaml` (Standard: `pickupstation`, `opentrons`, `microscope`).
* `protocols` / `default_protocol`: Im Dropdown angebotene Opentrons-Protokolle (`staining_show`, `staining`, `staining_full`, `dummy`).
* `microscope.*`: Standardwerte für `scan_mode`, `move_to_loading_position`, `range_x_um`, `range_y_um`, `overlap_percent` und `autofocus`.

---

## An Arkitekt binden & ohne Einzelbestätigungen starten

1. Binding-Seite öffnen (`http://localhost:8082/` bei Docker Compose bzw. `http://localhost:8080/` bei `uv`).
2. Server-URL eingeben (z. B. `https://go.arkitekt.live`) und auf **Bind** klicken.
3. Angezeigten Code über den Bestätigungs-Link im Browser freigeben.
4. Sicherstellen, dass `fairino_app`, `opentrons_app` und `microscope_app` in der `config.yaml` exakt mit den gebundenen App-Namen in Arkitekt übereinstimmen (nach Änderungen **Save and restart** klicken).
5. **Keine Einzelbestätigungen (One-Click-Start):**
   * `stainstorm_orchestrator_jena` nutzt `effects=Effects.NONE`, damit der Orchestrator selbst keine Bestätigungsabfragen erzwingt.
   * Da Arkitekt (`rekuest`) Kind-Tasks eines Workflows standardmäßig mit `TaskPolicy.ASK` zur Freigabe anhält, beim Start von **`run_staining_cycle`** in Arkitekt den **Auto-Mode (`TaskPolicy.AUTO`)** aktivieren — oder bei der ersten Freigabe **„Always allow“ (`HoldRemember.ASKER` / `ALWAYS`)** wählen. Danach läuft der gesamte Zyklus nach einem einzigen Start ohne weitere Zwischenstopps durch.
