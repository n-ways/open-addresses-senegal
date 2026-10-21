# tools/

How the zones, the place inventory, the plate names and ranges, the border and the compounds of Senegal were built (engine/SPEC.md), and the paper's measures. Python 3.9 or later; the heavy steps also need `duckdb` (with its spatial extension) and, for N-Ways' own data, `psql` with `NWAYS_DB` (read-only). Run one heavy job at a time.

| Script | What it does |
|---|---|
| `build-zones.py <dir>` | The 46 frozen code zones from geoBoundaries SEN ADM2/ADM3 (2019) -> `model/zones.json`, `model/zones.geojson` (SPEC 2.1) |
| `build_border.py build <extract.osm.pbf>` | The national border from the OpenStreetMap admin_level=2 relation of Senegal -> `engine/data/border.geojson` (SPEC 2.3) |
| `build_border.py check` | Counts the published addresses whose entrance lies more than 300 m outside the border; exits non-zero if there is any |
| `extract-buildings.py`, `building-stats.py` | The building profile: one row per footprint, then compounds, classes and sizes by region and zone -> `model/building-stats.json` |
| `build-lieux.py`, `name-ranges.py`, `sn_plates.py` | The place inventory, the plate names and the national per-name ranges -> `model/lieux.json`, `model/lieux-stats.json`, `model/name-families.json` (SPEC 3.2, 3.3) |
| `issue_registry.py extract`, `group`, `counts` | Every structure, grouped into compounds with their gate, lieu and coverage, one JSON line per compound, for the issuer to number (SPEC 7) |
| `make-samples.py` | The footprint samples behind the test vectors (`engine/reference/samples/`) |
| `paper-figures.py`, `paper-evaluation.py`, `stats-tables.py`, `examples-text.py` | The paper's figure data, its evaluation measures, its statistics tables and its worked examples, from the registry, the model and the engine |

## The border decides

An address is only ever issued for a building whose entrance lies inside Senegal's national border, OpenStreetMap's admin_level=2 boundary, or within 300 m of it. Zone outlines from any source (the 2019 geoBoundaries départements, GADM and the like) may spill over the border, and the zone rule reaches 2 km beyond the outlines along rivers and coasts; none of them decides.

`build_border.py build` reads the relation tagged `boundary=administrative`, `admin_level=2`, `ISO3166-1=SN` from an OpenStreetMap extract with DuckDB's `ST_ReadOSM`, joins its member ways into closed rings, simplifies them by Douglas-Peucker at 50 m on the UTM 28N grid and writes `engine/data/border.geojson` (about 70 kB). The extract must hold the relation whole: a country extract clipped at its own outline usually misses some of the border ways, and the tool then stops with "the border does not close". Use an extract of the region around Senegal, or of the boundary relations alone (for example `osmium tags-filter <planet or region>.osm.pbf r/admin_level=2`). The file records the largest distance between the simplified line and the true one, measured both ways (`maxDeviationM`, 50.4 m), and the limit the engine applies, 300 m less that deviation rounded up (`limitM`, 249 m), so a point accepted is never more than 300 m outside the true border. `--full FILE` also writes the unsimplified border, which `check --border FILE` uses with the full 300 m.

`issue_registry.py group` loads that border (`sn_engine.Border`) and drops every structure whose centre lies beyond it, and then every compound whose entrance (its gate, else its main building's centre) lies beyond it, before any lieu is chosen; the counts it prints show how many (`abroadStructure`, `abroadCompound`). The registry server applies the same rule to every address issued on demand and every entrance moved (`422 outside`). `build_border.py check` verifies the published registry: 0 of 3,597,128 addresses lie more than 249 m outside the simplified border, and 0 more than 300 m outside the full one.

## Order

```sh
python3 tools/build-zones.py <dir with geoBoundaries adm2.geojson + adm3.geojson>    # once, before first issue
python3 tools/build_border.py build region.osm.pbf               # the border; re-run when OpenStreetMap corrects it
python3 tools/extract-buildings.py <work-dir> <data-root>
python3 tools/building-stats.py   <work-dir> <data-root>
python3 tools/build-lieux.py      <work-dir>                     # ends with tools/name-ranges.py
NWAYS_DB=... python3 tools/issue_registry.py extract --root <data-root> --work work
python3 tools/issue_registry.py group --work work --out compounds.jsonl.gz
python3 tools/issue_registry.py counts --work work               # before first issue only
python3 tools/build_border.py check                              # after every export of the registry
python3 tools/paper-figures.py                                   # the paper's figure data
python3 tools/paper-evaluation.py > docs/figures/data/evaluation.json
```
