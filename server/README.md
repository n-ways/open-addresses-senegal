# The registry server

A ready-made HTTP service for Senegal's N-Ways addresses. It loads the published registry (`registry/`), answers every lookup a ministry, a post office, an emergency service or a developer needs, and, on the one deployment designated as Senegal's issuer, issues new addresses by exactly the rules the N-Ways issuer uses. Two deployments loaded with the same registry give the same answers.

- Python 3.9 or later, standard library only (`http.server`, `sqlite3`, `json`, `gzip`, `hashlib`). Nothing to install.
- Parsing, check letters, spot codes, name keys, plate names and numbering come from the reference engine in `engine/reference/`. The server does not re-implement them.
- Every endpoint, with a real request and response: [docs/api.md](../docs/api.md). The OpenAPI 3.1 description: [openapi.yaml](openapi.yaml).

## Deploy

### With Docker (one command)

From the repository root:

```sh
docker compose up -d
curl http://localhost:8080/v1/health
```

On first start the container imports `registry/` into the `addresses-data` volume. Each file is checked against `registry/MANIFEST.json`. The whole country takes about two minutes and a 2.1 GB database. The container then serves on port 8080. Later starts reuse the volume and serve within seconds. The image is `python:3.12-slim` running as an unprivileged user (uid 10001), with a health check on `/v1/health`.

Settings go in the environment or in a `.env` file next to `docker-compose.yml`. Never commit that file:

```sh
PORT=8080
CORS_ORIGINS=*
# Only on the designated issuer (see "Who may issue"):
# ISSUE_KEYS=7f3c...,a91b...
# ISSUE_PER_DAY=200
```

### With plain Python

```sh
python3 -m server import --registry registry --db data/addresses.sqlite
python3 -m server serve  --db data/addresses.sqlite --port 8080
```

`python3 -m server start` does both: it imports when the database is empty, then serves. To run it as a service, point a systemd unit (or any supervisor) at `python3 -m server serve` with `WorkingDirectory` set to the repository and `Restart=always`. Run **one** server process per database. Reads are safe from any number of threads in that process; issuing takes a lock inside it.

### Behind a reverse proxy with TLS

The server speaks plain HTTP. Put it behind a proxy that holds the certificate, and bind it to localhost (`HOST=127.0.0.1`). With Caddy, which obtains certificates itself:

```
addresses.example.org {
    reverse_proxy 127.0.0.1:8080
}
```

With nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name addresses.example.org;
    ssl_certificate     /etc/letsencrypt/live/addresses.example.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/addresses.example.org/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 64k;
    }
}
```

Issuing keys travel in the `Authorization` header, so an issuing deployment must only be reachable over TLS.

## Configure

| Variable | Default | Meaning |
|---|---|---|
| `ADDRESSES_DB` | `data/addresses.sqlite` (`/data/addresses.sqlite` in the container) | the SQLite database |
| `PORT` | `8080` | port to listen on |
| `HOST` | `0.0.0.0` | address to listen on (`127.0.0.1` behind a proxy) |
| `REGISTRY_DIR` | `registry/` of this repository | what `import` and `start` load |
| `MODEL_DIR` | `model/` of this repository | zone grid and outlines (`zones.json`, `zones.geojson`), and the full-precision lieu positions (`lieux.json`) |
| `BORDER_FILE` | `engine/data/border.geojson` | the national border (SPEC 2.3) |
| `ISSUE_KEYS` | empty: read-only | comma-separated bearer keys allowed to issue and to change addresses |
| `ISSUE_PER_DAY` | `5` | addresses each key may issue in any 24 hours (the N-Ways app allows 5 per phone; an office issuing for many households sets more) |
| `CORS_ORIGINS` | empty: no CORS headers | comma-separated origins allowed to call from a browser, or `*` |

Make keys long and random, for example `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`, one per office or system, so that one can be withdrawn without the others. The server keeps a hash of the key with each address it issues (`issue_log`) and never stores the key itself.

## Commands

| Command | What it does |
|---|---|
| `import --registry DIR --db FILE` | Streams `lieux.csv` and every `<ZONE>.csv.gz` into SQLite in one transaction (WAL mode). It checks each file's SHA-256 (of the uncompressed bytes) and row count against `MANIFEST.json`, and the total, and refuses any mismatch: nothing changes. It reads `registry/anchors/` the same way when it is there. It can be re-run: registry rows are replaced, and addresses issued by this deployment are kept. |
| `serve --db FILE --port N` | Serves the API under `/v1`. |
| `start` | `import` when the database is empty, then `serve` (the container's command). |
| `export --db FILE --out DIR` | Writes the registry back in the published format: the same columns in the same order, rows by name family then number, `lieux.csv` (plain and gzip), `anchors/`, and `MANIFEST.json`, gzip without name or time. After importing the published registry, an export is byte-identical to it once uncompressed. This was checked on the full registry: all 46 zone files, `lieux.csv` and the 46 anchor files have the published SHA-256. |

Indexes cover the machine form, the remembered form, the official address, zone, area (lieu) and number, the name family and number (unique), and position. Position uses an SQLite R\*Tree, or an integer grid of 0.001° cells when SQLite was built without R\*Tree.

## Who may issue

**A deployment issues only if the State of Senegal or N-WAYS LIMITED has designated it as Senegal's issuer.** Every other deployment runs read-only, with no `ISSUE_KEYS`. It serves the published registry and refuses `POST` and `PATCH` with `403 read_only`.

The reason is arithmetic. A new address takes the next free number in its area's block, given everything issued so far. Two issuers working from the same registry would each see the same number as free and give it to two different compounds. "Ouakam 2510" would then lead to two gates, and nothing could later decide which one is right. One issuer per country keeps every number unique for good. Read-only copies can be as many as anyone needs: a ministry, a post office, a hospital network, a university. They update from the issuer's published exports.

There is one issuer at a time. A designated deployment that takes over issuing starts from the latest published registry (with `anchors/`), and the previous issuer stops on the same day.

## Keep it current, back it up

**A read-only deployment** follows the published registry. When a newer registry is published (a new `MANIFEST.json`), pull the repository and run `python3 -m server import` again, then restart `serve`. With Docker: `git pull && docker compose build && docker compose run --rm addresses python -m server import && docker compose up -d`. The import is one transaction, so the old data serves until the new data is complete. A file that fails its check leaves the database as it was.

**The issuing deployment** holds addresses that exist nowhere else until it publishes them. Back it up at least daily:

```sh
sqlite3 data/addresses.sqlite ".backup 'backup/addresses-$(date +%F).sqlite'"   # consistent while serving
python3 -m server export --db data/addresses.sqlite --out backup/registry-$(date +%F)   # the published format
```

With Docker, run the same inside the container (`docker compose exec addresses python -m server export --db /data/addresses.sqlite --out /data/export`) or back up the `addresses-data` volume. The export is what the issuer publishes. Read-only deployments import it.

## The issuing rules

`POST /v1/codes` follows the N-Ways issuer step by step, with the same checks in the same order:

1. The key's daily limit (`429 limit`).
2. The point must be in a Senegal zone and inside the national border or within 300 m of it (`422 outside`). The zone is the one whose outline holds it, or the one with the nearest outline vertex within 2 km. **The border decides** (SPEC 2.3): the border is OpenStreetMap's admin_level=2 boundary of Senegal, shipped simplified in `engine/data/border.geojson` (`BORDER_FILE` to use another), and a zone outline, or the 2 km reach of the zone rule along rivers and coasts, never carries an address into a neighbouring country. The limit applied is 300 m less the simplification's largest deviation (249 m), so nothing accepted lies more than 300 m outside the true border. `GET /v1/at` and `GET /v1/spot` answer `422 outside` there too.
3. For a new compound (no `of`):
   - A live address within 3 m, or an outline issued here that holds the point, means the building already has an address (`409 exists`, with that address).
   - An outline, when given, must cover 12 m² to 2 ha (`422 bad_outline`). It is also refused when it covers more than half of an outline issued here, or more than half of itself is covered by one (`409 exists`).
4. For another door (`of`), the compound must exist (`404`) and the door must be within 80 m of its entrance (`422 far`). The door takes the compound's area.
5. A new compound takes the zone's nearest lieu: a quartier, suburb, village, locality or extension within 2.5 km, else a town within 10 km, else the nearest. Ties go to the lower index (SPEC 3.2).
6. The number is decided by the area's compounds in Hilbert order (SPEC 7.4). It is the free number midway between the new compound's neighbours in the area's first block. Failing that, it is the lowest free number of its further blocks. Failing that, the name's national range gives the area a new block of 10 (3-digit names) or 100 (4- and 5-digit names) above the highest block of the name. The block is frozen in the database and appears in `lieux.csv` on export. When the whole range is used, the answer is `409 full`, and the commune names the area's extension. Retired numbers count as used: a number is never given twice.
7. The forms come from the engine: remembered `Ouakam 2510`, written `OUAKAM 2510 · DAKAR`, machine `SN-DKR-0080-2510-R`. The status is `provisional`, issued `on-demand`, with the entrance kind `centre` (`door` for another door) and a compound profile from the outline (`res.maison` for 25 to 600 m², and so on, SPEC 6).

`PATCH /v1/codes/{machine}` confirms an address, retires it (it is never reused), returns a confirmed address to provisional while a dispute is open, or moves its entrance to the real gate (at most 80 m, never more than 300 m outside the national border; the kind becomes `gate` and the spot code follows).

**Parity with the N-Ways issuer.** The issuer orders an area's compounds by their centroid, not by their entrance. `registry/anchors/` publishes that centroid for every address, at full precision, row for row with the zone files. The server uses it. Without `anchors/`, the server falls back to the entrance: in a test of 3,000 new compounds in Dakar and Touba, 264 then got a different number from the issuer's. `server/testdata/parity.json` holds 62 issue cases: new compounds, doors, outlines of every size class, extension blocks, a too-small outline and a point outside Senegal. Each case carries the answer the issuer's own Go package (`Nearest`, `InsertInLieu`, `AddressForms`, `Profile`) gave against the fixture registry, issued one after another. The tests replay them and require the same area, number, forms and profile every time. On the full registry, a new compound at the Place de l'Indépendance (`Plateau 1005`) and a second door of `Ouakam 2512` (`Ouakam 2510`) also matched the issuer.

**What a deployment cannot know.** The registry publishes each compound's entrance and centroid, not its building footprints. The issuer also counts a point inside a mapped footprint as "at" that compound, and refuses a new outline that overlaps a mapped footprint. The server applies both rules only to the outlines it issued itself. Elsewhere it uses the 12 m and 3 m entrance distances. In a sample of 200 points within 10 m of an entrance, the server and the issuer named the same compound 171 times. The issuer named a closer compound by footprint 8 times. In 21 cases near the borders the issuer's multi-country service answered for a neighbouring country.

## Test

```sh
python3 -m unittest server.test_server
```

The 32 tests cover import and export (byte-identical round trip, refused SHA-256, refused counts, re-import, anchors in step), every endpoint's answers and errors, issuing parity, extension blocks (frozen, persisted, exported and re-imported), the duplicate checks, the national border (a point the zone rule gives to Dagana but which lies across the Senegal river is refused; points inside and within the limit are issued; an entrance never moves across), the daily limit, read-only refusals, status changes and entrance moves. The fixture in `testdata/registry/` is the published registry cut to one zone, Salémata (SLM, 5,839 addresses), with the full lieux table so that national name ranges are real.

## Files

| File | What it is |
|---|---|
| `__main__.py` | the command line (`import`, `serve`, `start`, `export`) |
| `db.py` | SQLite schema, import, export, lookups |
| `core.py` | the register in force (zones, lieux, blocks), forms, Plus Codes, outline geometry, compound profile |
| `service.py` | what each endpoint does, and the issuing rules |
| `api.py` | HTTP: routes, JSON, CORS, errors |
| `test_server.py`, `testdata/` | the tests, the fixture registry and the parity cases |
| `Dockerfile`, `../docker-compose.yml` | the container |
| `openapi.yaml` | the API description |
