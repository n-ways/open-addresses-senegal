# N-Ways Addressing for Senegal (`open-addresses-sn`)

**Status: issued on 20 October 2026.** Every compound in Senegal has its address: 3,597,128 of them, in all 46 zones. Each is provisional until residents confirm it. The registry in `registry/` publishes every one, with nothing held back. People get their address in the N-Ways app (map.nways.ng). Anyone can serve and look up the addresses with the ready-made server in `server/`.

The repository is open: the code is Apache 2.0, the data ODbL and the documents CC BY 4.0 ([LICENSING.md](LICENSING.md)). Credit: "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)". These are N-Ways addresses. They are not official addresses, not postcodes and not land titles.

This repository holds Senegal's addressing model, its reference engine, the issued registry, a server that serves and issues the addresses, and the research behind them. It is self-contained.

## In one paragraph

Senegal already has three partial systems:

- La Poste's 5-digit postcodes, which are area-level;
- blue street plates with metric door numbers in parts of nine cities;
- the state's Adressage Numérique National (ANN), relaunched in August 2026 and still in pilot.

N-Ways adds what none of them provides yet: an address every person can **remember**. It is a place word people already use plus a short number, like a house number: **`Ouakam 2512`**. Plates carry the same address as `OUAKAM 2512 · DAKAR`. Databases store it as `SN-DKR-0080-2512-J`, whose last letter is a check letter for systems that people never see.

The remembered address is **unique in all of Senegal on its own**. Places with the same name are normalised for case, accents, articles, trailing numerals and French/Wolof spelling. All places that share a name draw from one national number range for that name, one block per place. "Médina 12 149" is the Médina of Dakar and "Médina 23 151" the Médina of Ziguinchor, and no town is said after either ([SPEC 3.3](engine/SPEC.md)). 1,974 plate names repeat over 5,928 places. The largest shared range is Darou Salam's (23 places, 5 digits). No name needs a qualifier.

The name in the address is a short **plate name**: at most 12 characters and 2 words. "Liberté 6" stands for S.I.C.A.P. Liberté Six and "Saly" for Saly Portudal. The full official name is kept, printed in small type and accepted when typed. Of 14,997 places, 4,208 official names are over the limit. 1,119 names are shortened by rule. For 3,116, the commune chooses among candidates, and the first candidate serves until it does ([SPEC 3.2.1](engine/SPEC.md), `tools/sn_plates.py`).

- The address belongs to the compound (concession, villa, apartment block, school, shop) and leads to its gate.
- Any spot without a compound, such as a field, a market pitch or an empty plot, gets a code computed offline: **`DKR 5553 1512`**.
- The national border decides: no building more than 300 m outside it, in a neighbouring country, ever gets an address, whatever the zone outlines say ([SPEC 2.3](engine/SPEC.md)).
- Every address points to the La Poste zone, the street plate and, once it exists, the ANN address. Where the government already gives an address, that address is shown first. The model is designed to be handed to the ANN.

## What is here

| Path | What it is |
|---|---|
| [docs/existing-systems.md](docs/existing-systems.md) | What exists today: La Poste, street addressing, the ANN, the cadastre, data protection |
| [docs/model.md](docs/model.md) | The model and every design choice, argued from Senegal's facts |
| [docs/paper.md](docs/paper.md) / [docs/paper.fr.md](docs/paper.fr.md) | The research paper, in English and French (PDFs alongside) |
| [docs/paper/](docs/paper/build.sh), [docs/figures/](docs/figures/) | The paper's LaTeX build (template, style, bibliography `references.bib`) and its figures as TikZ sources with their data |
| [docs/api.md](docs/api.md) | Every endpoint of the server, with real requests and responses |
| [engine/SPEC.md](engine/SPEC.md) | The engine specification (normative) |
| engine/data/ | The national border (`border.geojson`), simplified from OpenStreetMap's admin_level=2 boundary: no address is issued more than 300 m outside it ([SPEC 2.3](engine/SPEC.md)) |
| [engine/reference/](engine/reference/) | The reference engine (`sn_engine.py`, `plate_names.py`; standard-library Python), its tests (`test_sn.py`), test vectors (`vectors.json`) and the real footprint samples they come from (`samples/`) |
| [registry/](registry/README.md) | The issued registry: one file per zone (3,597,128 addresses), each compound's centroid (`anchors/`), the frozen place list and blocks (`lieux.csv`), and the manifests |
| [server/](server/README.md) | The registry server: import, a JSON API, issuing by the issuer's rules, export; Docker files; tests |
| [model/design.json](model/design.json) | The model as data: zones, place words, formats, alphabet, building and compound profile schema, "Add my home" |
| [model/lieux.json](model/lieux.json), [model/lieux-stats.json](model/lieux-stats.json) | The place-word inventory: each place's plate name and official name, name family, number length and blocks, and the number-length statistics |
| [model/name-families.json](model/name-families.json) | The national per-name ranges: the block table, frozen at first issue, and the repeated-name counts |
| [model/zones.json](model/zones.json), [model/zones.geojson](model/zones.geojson) | The 46 frozen code zones: keys, spot grid, outlines |
| [model/building-stats.json](model/building-stats.json) | Statistics on buildings, compounds and classes by region and zone |
| model/country.json, model/regions.json | Country facts and the regions with their building counts, as gathered before the model was built |
| [tools/](tools/README.md) | The scripts that built the zones, the border, the inventory, the plate names, the ranges, the compounds and the statistics |
| [GOVERNANCE.md](GOVERNANCE.md) | Who runs it, the single-issuer rule, what may change and how, hand-over to a national body |
| [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) | How to propose a change; how to report a problem |
| [SOURCES.md](SOURCES.md), [LICENSING.md](LICENSING.md), [NOTICE](NOTICE), [CITATION.cff](CITATION.cff) | Every source, the licences and how to credit N-Ways, how to cite the paper |

## Run the reference engine

The engine needs Python 3.9 or later, the standard library only, and the files in `model/`.

```sh
cd engine/reference
python3 sn_engine.py selftest                        # UTM, check letter, spot round trips, numbering, name ranges, vectors.json
python3 -m unittest test_sn                          # the selftest and the national-uniqueness tests (same-named places)
python3 sn_engine.py encode 14.66810 -17.43170       # -> DKR 5553 1512  (Place de l'Indépendance)
python3 sn_engine.py decode "TBA 5330 3234"          # -> centre of a 5 m cell at the Grande Mosquée de Touba
python3 sn_engine.py check  "DKR 5553 1512 F"        # a spot code written with a wrong check letter -> (False, 'check letter does not match…')
python3 sn_engine.py find   "Ouakam 2512"            # -> the address in all its forms, with no context
python3 sn_engine.py find   "Médina 23 151"          # -> the Médina of Ziguinchor (Dakar's is "Médina 12 149")
python3 sn_engine.py vectors                         # every test vector (--write to refresh vectors.json)
python3 sn_engine.py registry samples/dakar-medina.csv   # group, place and number a real block of footprints
```

## Run the server

The server serves the whole registry as a JSON API and needs nothing beyond Python. With Docker, from this directory:

```sh
docker compose up -d                                  # imports registry/ on first start (about 2 minutes), then serves
curl 'http://localhost:8080/v1/find?q=Ouakam%202512'
```

Or with Python alone:

```sh
python3 -m server import --registry registry --db data/addresses.sqlite
python3 -m server serve  --db data/addresses.sqlite --port 8080
python3 -m unittest server.test_server                # import/export round trip, every endpoint, issuing parity
```

A deployment is read-only unless the State or N-WAYS LIMITED has designated it as Senegal's issuer: one issuer per country, so that no number is given twice ([server/README.md](server/README.md), [GOVERNANCE.md](GOVERNANCE.md)). Endpoints, with real requests and responses: [docs/api.md](docs/api.md) and [server/openapi.yaml](server/openapi.yaml).

## Build the paper

The paper is pandoc Markdown with TeX mathematics (`docs/paper.md`, `docs/paper.fr.md`), typeset with LaTeX:

```sh
python3 tools/paper-figures.py                          # the figures' data (docs/figures/data) from the registry and model
python3 tools/paper-evaluation.py > docs/figures/data/evaluation.json   # the measurements of the evaluation chapter
sh docs/paper/build.sh        # needs pandoc, tectonic and pdftocairo; writes docs/n-ways-addressing-senegal-{en,fr}.pdf
```

The figures are TikZ/pgfplots sources (`docs/figures/*.tikz`, one wrapper per language); the build compiles them to PDF for the paper and SVG for the Markdown. References are in `docs/paper/references.bib`; `references.fr.bib` holds the same entries with their descriptive fields in French, for the French edition.

## Rebuild the data

The tools in `tools/` rebuild the zones, the inventory and the statistics from the source data (OpenStreetMap, the Google and Microsoft footprints, geoBoundaries, GeoNames; [SOURCES.md](SOURCES.md)). Most need DuckDB and are heavy, so run one at a time. `tools/name-ranges.py` is light and works on `model/lieux.json` alone. A rebuild never renumbers: the zones, the lieux and the blocks are frozen.

```sh
python3 tools/build-zones.py <dir with geoBoundaries adm2.geojson + adm3.geojson>
python3 tools/build_border.py build <region.osm.pbf>   # the national border (engine/data/border.geojson)
python3 tools/extract-buildings.py <work-dir> <data-root>
python3 tools/building-stats.py   <work-dir> <data-root>
python3 tools/build-lieux.py      <work-dir>            # ends with tools/name-ranges.py
python3 tools/name-ranges.py                            # plate names (tools/sn_plates.py) and national per-name ranges
python3 tools/make-samples.py     <work-dir>
```
