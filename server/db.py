"""The SQLite store: schema, import of the published registry, export back
to the published format, and the lookups the API needs.

One row per address in `codes`, with every published column kept as text
exactly as the registry wrote it, so an import followed by an export gives
the same files byte for byte. Typed columns beside them (family, number,
position) serve the indexes. `lieux` holds registry/lieux.csv; `meta` the
manifest; `issue_log` the issues made by each key (the daily limit).
"""
import csv
import gzip
import hashlib
import io
import json
import math
import os
import sqlite3
import time

from . import core

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lieux (
    ref TEXT PRIMARY KEY, seq INTEGER NOT NULL, e REAL NOT NULL, n REAL NOT NULL, {lieu_cols});
CREATE TABLE IF NOT EXISTS codes (
    id INTEGER PRIMARY KEY,
    {code_cols},
    zone TEXT NOT NULL, family INTEGER NOT NULL, num INTEGER NOT NULL,
    lat REAL NOT NULL, lng REAL NOT NULL, anchor_lat REAL NOT NULL, anchor_lng REAL NOT NULL, anchor TEXT NOT NULL,
    remembered_key TEXT NOT NULL, official_key TEXT,
    source TEXT NOT NULL DEFAULT 'registry', outline TEXT, cell INTEGER NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS codes_machine ON codes (canonical);
CREATE UNIQUE INDEX IF NOT EXISTS codes_family_num ON codes (family, num);
CREATE INDEX IF NOT EXISTS codes_remembered ON codes (remembered_key);
CREATE INDEX IF NOT EXISTS codes_official ON codes (official_key) WHERE official_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS codes_zone ON codes (zone, canonical);
CREATE INDEX IF NOT EXISTS codes_lieu ON codes (lieu);
CREATE INDEX IF NOT EXISTS codes_number ON codes (num);
CREATE INDEX IF NOT EXISTS codes_cell ON codes (cell);
CREATE INDEX IF NOT EXISTS codes_outline ON codes (lat, lng) WHERE outline IS NOT NULL;
CREATE TABLE IF NOT EXISTS issue_log (key_id TEXT NOT NULL, at REAL NOT NULL, machine TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS issue_log_key ON issue_log (key_id, at);
"""


def q(name):
    return '"' + name + '"'


LIEU_COLS = ', '.join(f'{q(c)} TEXT NOT NULL' for c in core.LIEU_COLUMNS)
CODE_COLS = ', '.join(f'{q(c)} TEXT NOT NULL' for c in core.CODE_COLUMNS)
CODE_SELECT = ', '.join(q(c) for c in core.CODE_COLUMNS)
LIEU_SELECT = ', '.join(q(c) for c in core.LIEU_COLUMNS)
# registry/anchors/<ZONE>.csv: the point each compound is ordered by when
# numbering (its centroid), at full precision, row for row with <ZONE>.csv.
ANCHOR_COLUMNS = ['canonical', 'anchor_lat', 'anchor_lng']

# The fallback spatial index: integer cells of 0.001 degree (about 110 m).
CELL = 1000


def cell_of(lat, lng):
    return int((lat + 90) * CELL) * 1000000 + int((lng + 180) * CELL)


def connect(path, readonly=False):
    if readonly:
        con = sqlite3.connect(f'file:{path}?mode=ro', uri=True, timeout=30, check_same_thread=False)
    else:
        d = os.path.dirname(os.path.abspath(path))
        os.makedirs(d, exist_ok=True)
        con = sqlite3.connect(path, timeout=30, check_same_thread=False)
        con.execute('PRAGMA journal_mode=WAL')
    con.isolation_level = None  # transactions are explicit (BEGIN IMMEDIATE ... COMMIT)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA busy_timeout=30000')
    return con


def has_rtree(con):
    return con.execute("SELECT 1 FROM sqlite_master WHERE name='codes_rtree'").fetchone() is not None


def create(con):
    con.executescript(SCHEMA.format(lieu_cols=LIEU_COLS, code_cols=CODE_COLS))
    try:
        con.execute('CREATE VIRTUAL TABLE IF NOT EXISTS codes_rtree USING rtree(id, min_lat, max_lat, min_lng, max_lng)')
    except sqlite3.OperationalError:
        pass  # SQLite built without R*Tree: the integer grid (codes.cell) serves instead


def meta(con, key, default=None):
    r = con.execute('SELECT value FROM meta WHERE key = ?', (key,)).fetchone()
    return r[0] if r else default


def set_meta(con, key, value):
    con.execute('INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = excluded.value',
                (key, value))


def count_codes(path):
    con = connect(path)
    try:
        return code_count(con)
    finally:
        con.close()


def code_count(con):
    try:
        return con.execute('SELECT count(*) FROM codes').fetchone()[0]
    except sqlite3.OperationalError:
        return 0


# ---------------------------------------------------------------- import
class RegistryError(Exception):
    pass


class _Hashing(io.RawIOBase):
    """Reads a gzip (or plain) file and hashes the uncompressed bytes."""

    def __init__(self, path):
        self.f = gzip.open(path, 'rb') if path.endswith('.gz') else open(path, 'rb')
        self.h = hashlib.sha256()
        self.lines = 0

    def readable(self):
        return True

    def readinto(self, b):
        data = self.f.read(len(b))
        self.h.update(data)
        self.lines += data.count(b'\n')
        b[:len(data)] = data
        return len(data)

    def close(self):
        self.f.close()
        super().close()


def _open_rows(path):
    raw = _Hashing(path)
    text = io.TextIOWrapper(io.BufferedReader(raw, 1 << 20), encoding='utf-8', newline='')
    return raw, text, csv.reader(text)


def _source(registry, name):
    for p in (os.path.join(registry, name + '.gz'), os.path.join(registry, name)):
        if os.path.exists(p):
            return p
    return None


def _precise_positions(model):
    p = os.path.join(model, 'lieux.json')
    if not os.path.exists(p):
        return {}
    with open(p, encoding='utf-8') as f:
        items = json.load(f)['lieux']
    return {f"{it['zone']}-{it['index']:04d}": (it['e'], it['n']) for it in items}


def import_registry(registry, db_path, model=None, log=print):
    """Stream registry/*.csv.gz into the database in one transaction. Every
    file's SHA-256 and row count must match MANIFEST.json, or nothing changes.
    Codes issued by this deployment (source 'local') are kept; a registry
    row that takes one of their numbers is refused."""
    t0 = time.time()
    man_path = os.path.join(registry, 'MANIFEST.json')
    if not os.path.exists(man_path):
        raise RegistryError(f'{man_path} not found')
    with open(man_path, encoding='utf-8') as f:
        man = json.load(f)
    if man.get('country') != core.COUNTRY:
        raise RegistryError(f"MANIFEST.json is for {man.get('country')!r}, this server serves {core.COUNTRY}")
    zones = sorted(man['byZone'])
    lieux_src = _source(registry, 'lieux.csv')
    if lieux_src is None:
        raise RegistryError('registry/lieux.csv(.gz) not found')
    for z in zones:
        if _source(registry, f'{z}.csv') is None:
            raise RegistryError(f'registry/{z}.csv.gz not found')
    precise = _precise_positions(model or core.model_dir())
    anchors_dir = os.path.join(registry, 'anchors')
    aman = None
    if os.path.exists(os.path.join(anchors_dir, 'MANIFEST.json')):
        with open(os.path.join(anchors_dir, 'MANIFEST.json'), encoding='utf-8') as f:
            aman = json.load(f)
        if aman.get('byZone') != man['byZone']:
            raise RegistryError('anchors/MANIFEST.json does not count the same addresses as MANIFEST.json')
    else:
        log('  no registry/anchors/: compounds are ordered by their entrance; a new number may then differ from the '
            "N-Ways issuer's")

    con = connect(db_path)
    create(con)
    con.execute('PRAGMA synchronous=OFF')
    con.execute('PRAGMA cache_size=-200000')
    con.execute('BEGIN IMMEDIATE')
    try:
        # lieux: replaced from the registry; a block added here since is kept.
        local_blocks = {r['ref']: r['blocks'] for r in con.execute('SELECT ref, blocks FROM lieux')}
        con.execute('DELETE FROM lieux')
        raw, text, rows = _open_rows(lieux_src)
        header = next(rows)
        if header != core.LIEU_COLUMNS:
            raise RegistryError(f'lieux.csv: unexpected columns {header}')
        lieux = {}
        for seq, r in enumerate(rows):
            d = dict(zip(header, r))
            lr = d['lieu']
            if lr in local_blocks and local_blocks[lr] != d['blocks'] and local_blocks[lr].startswith(d['blocks']):
                d['blocks'] = local_blocks[lr]
            it = core.lieu_from_row(d, precise.get(lr))
            lieux[lr] = it
            con.execute(f'INSERT INTO lieux (ref, seq, e, n, {LIEU_SELECT}) VALUES (?, ?, ?, ?, {",".join("?" * len(header))})',
                        [lr, seq, it['e'], it['n']] + [d[c] for c in header])
        text.close()
        _verify(man, 'lieux.csv', raw, None)

        con.execute("DELETE FROM codes WHERE source = 'registry'")
        if has_rtree(con):
            con.execute('DELETE FROM codes_rtree')
        total = 0
        ins = (f'INSERT INTO codes ({CODE_SELECT}, zone, family, num, lat, lng, anchor_lat, anchor_lng, anchor, remembered_key, '
               f'official_key, source, cell) VALUES ({",".join("?" * (len(core.CODE_COLUMNS) + 12))})')
        for z in zones:
            raw, text, rows = _open_rows(_source(registry, f'{z}.csv'))
            header = next(rows)
            if header != core.CODE_COLUMNS:
                raise RegistryError(f'{z}.csv: unexpected columns {header}')
            if aman:
                src = _source(anchors_dir, f'{z}.csv')
                if src is None:
                    raise RegistryError(f'registry/anchors/{z}.csv.gz not found')
                araw, atext, arows = _open_rows(src)
                if next(arows) != ANCHOR_COLUMNS:
                    raise RegistryError(f'anchors/{z}.csv: unexpected columns')
            batch = []
            n = 0
            for r in rows:
                it = lieux.get(r[3])
                if it is None:
                    raise RegistryError(f'{z}.csv: {r[0]} names lieu {r[3]}, which lieux.csv does not have')
                lat, lng = float(r[10]), float(r[11])
                if aman:
                    a = next(arows, None)
                    if a is None or a[0] != r[0]:
                        raise RegistryError(f'anchors/{z}.csv is not in step with {z}.csv at {r[0]}')
                    alat, alng, atxt = float(a[1]), float(a[2]), a[1] + ',' + a[2]
                else:
                    alat, alng, atxt = lat, lng, r[10] + ',' + r[11]
                off = core.fold(r[21]) or None
                batch.append(r + [it['zone'], it['family'], int(r[5]), lat, lng, alat, alng, atxt, core.fold(r[1]), off,
                                  'registry', cell_of(lat, lng)])
                n += 1
                if len(batch) >= 20000:
                    _insert(con, ins, batch)
                    batch = []
            if batch:
                _insert(con, ins, batch)
            text.close()
            _verify(man, f'{z}.csv', raw, man['byZone'][z])
            if aman:
                if next(arows, None) is not None:
                    raise RegistryError(f'anchors/{z}.csv has more rows than {z}.csv')
                atext.close()
                _verify(aman, f'{z}.csv', araw, man['byZone'][z])
            total += n
            log(f'  {z}: {n:,} addresses')
        if total != man['addresses']:
            raise RegistryError(f"the zones hold {total:,} addresses, MANIFEST.json says {man['addresses']:,}")
        if has_rtree(con):
            con.execute('INSERT INTO codes_rtree (id, min_lat, max_lat, min_lng, max_lng) SELECT id, lat, lat, lng, lng FROM codes')
        for k in ('country', 'exported', 'engine', 'credit', 'licence'):
            set_meta(con, k, str(man.get(k, '')))
        set_meta(con, 'imported', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
        set_meta(con, 'registryAddresses', str(total))
        set_meta(con, 'anchors', 'published' if aman else 'entrance')
        if aman:
            set_meta(con, 'anchorsExported', str(aman.get('exported', '')))
        con.execute('COMMIT')
    except BaseException:
        con.execute('ROLLBACK')
        con.close()
        raise
    con.execute('PRAGMA optimize')
    con.close()
    log(f'imported {total:,} addresses in {len(zones)} zones and {len(lieux):,} lieux in {time.time() - t0:.0f} s')
    return total


def _insert(con, sql, batch):
    try:
        con.executemany(sql, batch)
    except sqlite3.IntegrityError as e:
        raise RegistryError(f'a registry address takes a number or machine form already in the database ({e}); '
                           'the codes issued by this deployment would be overwritten') from e


def _verify(man, name, raw, rows):
    got = raw.h.hexdigest()
    want = man['sha256'].get(name)
    if want is None:
        raise RegistryError(f'MANIFEST.json has no SHA-256 for {name}')
    if got != want:
        raise RegistryError(f'{name}: SHA-256 {got} does not match MANIFEST.json ({want})')
    if rows is not None and raw.lines - 1 != rows:
        raise RegistryError(f'{name}: {raw.lines - 1:,} rows, MANIFEST.json says {rows:,}')


# ---------------------------------------------------------------- export
def _field(s):
    """A CSV field as the N-Ways exporter writes it (Go encoding/csv)."""
    if s == '':
        return s
    if s == r'\.' or any(c in s for c in ',"\r\n') or s[0] in ' \t\n\v\f\r\x85\xa0':
        return '"' + s.replace('"', '""') + '"'
    return s


def _line(fields):
    return (','.join(_field(f) for f in fields) + '\n').encode('utf-8')


def _write(out, name, header, rows, plain_too=False):
    h = hashlib.sha256()
    gz_path = os.path.join(out, name + '.gz')
    plain = open(os.path.join(out, name), 'wb') if plain_too else None
    with open(gz_path, 'wb') as f, gzip.GzipFile(filename='', mode='wb', fileobj=f, mtime=0, compresslevel=9) as g:
        for r in [header] + rows if isinstance(rows, list) else _chain(header, rows):
            b = _line(r)
            h.update(b)
            g.write(b)
            if plain:
                plain.write(b)
    if plain:
        plain.close()
    return h.hexdigest()


def _chain(header, rows):
    yield header
    yield from rows


def export_registry(db_path, out, log=print):
    """Write the registry in the published format: lieux.csv (+ .gz), one
    <ZONE>.csv.gz per zone (rows by name family, then number) and
    MANIFEST.json. Gzip without name or time, so a re-export is reproducible."""
    con = connect(db_path, readonly=True)
    adir = os.path.join(out, 'anchors')
    os.makedirs(adir, exist_ok=True)
    sha, asha = {}, {}
    lrows = [list(r) for r in con.execute(f'SELECT {LIEU_SELECT} FROM lieux ORDER BY ref')]
    sha['lieux.csv'] = _write(out, 'lieux.csv', core.LIEU_COLUMNS, lrows, plain_too=True)
    counts = {}
    zones = [r[0] for r in con.execute('SELECT DISTINCT zone FROM codes ORDER BY zone')]
    for z in zones:
        n = [0]

        def rows(z=z, n=n):
            for r in con.execute(f'SELECT {CODE_SELECT} FROM codes WHERE zone = ? ORDER BY family, num', (z,)):
                n[0] += 1
                yield list(r)
        sha[f'{z}.csv'] = _write(out, f'{z}.csv', core.CODE_COLUMNS, rows())
        counts[z] = n[0]
        asha[f'{z}.csv'] = _write(adir, f'{z}.csv', ANCHOR_COLUMNS,
                                  ([r[0]] + r[1].split(',') for r in con.execute(
                                      'SELECT canonical, anchor FROM codes WHERE zone = ? ORDER BY family, num', (z,))))
        log(f'  {z}: {n[0]:,} addresses')
    man = {'addresses': sum(counts.values()), 'byZone': counts, 'country': core.COUNTRY,
           'credit': meta(con, 'credit', core.CREDIT), 'engine': meta(con, 'engine', ''),
           'exported': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'licence': meta(con, 'licence', core.LICENCES['data']),
           'sha256': sha}
    with open(os.path.join(out, 'MANIFEST.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    aman = {k: man[k] for k in ('addresses', 'byZone', 'country', 'credit', 'exported', 'licence')}
    aman.update(registryExported=man['exported'], sha256=asha)
    with open(os.path.join(adir, 'MANIFEST.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(aman, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    con.close()
    log(f"exported {man['addresses']:,} addresses in {len(zones)} zones to {out}")
    return man


# ---------------------------------------------------------------- lookups
def load_lieux(con):
    return [core.lieu_from_row(dict(zip(core.LIEU_COLUMNS, list(r)[2:])), (r['e'], r['n']))
            for r in con.execute(f'SELECT e, n, {LIEU_SELECT} FROM lieux ORDER BY seq')]


def by_machine(con, machine):
    return con.execute('SELECT * FROM codes WHERE canonical = ?', (machine,)).fetchone()


def by_number(con, family, number):
    return con.execute('SELECT * FROM codes WHERE family = ? AND num = ?', (family, number)).fetchone()


def by_official(con, key):
    return con.execute('SELECT * FROM codes WHERE official_key = ? ORDER BY canonical', (key,)).fetchall()


def near(con, lat, lng, radius, limit, live_only=True):
    """Codes whose entrance is within radius metres, nearest first (ties by machine form)."""
    dlat = radius / 111320.0 + 1e-6
    dlng = radius / (111320.0 * max(0.2, math.cos(math.radians(lat)))) + 1e-6
    if has_rtree(con):
        rows = con.execute('SELECT c.* FROM codes_rtree r JOIN codes c ON c.id = r.id WHERE r.min_lat <= ? AND r.max_lat >= ? '
                           'AND r.min_lng <= ? AND r.max_lng >= ?', (lat + dlat, lat - dlat, lng + dlng, lng - dlng)).fetchall()
    else:
        cells = {cell_of(la, lo) for la in _steps(lat - dlat, lat + dlat) for lo in _steps(lng - dlng, lng + dlng)}
        rows = con.execute(f'SELECT * FROM codes WHERE cell IN ({",".join("?" * len(cells))}) AND lat BETWEEN ? AND ? '
                           'AND lng BETWEEN ? AND ?', [*cells, lat - dlat, lat + dlat, lng - dlng, lng + dlng]).fetchall()
    out = []
    for r in rows:
        if live_only and r['status'] == 'retired':
            continue
        d = core.dist_m(lat, lng, r['lat'], r['lng'])
        if d <= radius:
            out.append((d, r))
    out.sort(key=lambda x: (x[0], x[1]['canonical']))
    return out[:limit]


def _steps(a, b):
    x = a
    while x < b + 1.0 / CELL:
        yield min(x, b)
        x += 1.0 / CELL


def containing(con, lat, lng):
    """Live codes issued here with an outline that holds the point."""
    out = []
    for r in con.execute("SELECT * FROM codes WHERE outline IS NOT NULL AND status <> 'retired' "
                         'AND lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?', (lat - 0.002, lat + 0.002, lng - 0.002, lng + 0.002)):
        ring = json.loads(r['outline'])
        if core.in_ring(lng, lat, ring):
            out.append(r)
    return out


def outlines_near(con, ring):
    la0, la1, lo0, lo1 = core.ring_bbox(ring)
    return [r for r in con.execute("SELECT * FROM codes WHERE outline IS NOT NULL AND status <> 'retired' "
                                   'AND lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?',
                                   (la0 - 0.002, la1 + 0.002, lo0 - 0.002, lo1 + 0.002))]


def lieu_numbers(con, lieu_ref):
    """Every number of a lieu (retired too: a number is never reused), with the compound's position."""
    return [{'number': r['num'], 'e': None, 'n': None, 'lat': r['anchor_lat'], 'lng': r['anchor_lng']}
            for r in con.execute('SELECT num, anchor_lat, anchor_lng FROM codes WHERE lieu = ?', (lieu_ref,))]


def zone_counts(con):
    out = {}
    for r in con.execute('SELECT zone, status, count(*) FROM codes GROUP BY zone, status'):
        out.setdefault(r[0], {})[r[1]] = r[2]
    return out


def lieu_counts(con, zone):
    out = {}
    for r in con.execute('SELECT lieu, status, count(*) FROM codes WHERE zone = ? GROUP BY lieu, status', (zone,)):
        out.setdefault(r[0], {})[r[1]] = r[2]
    return out


def page(con, zone, after, limit):
    return con.execute('SELECT * FROM codes WHERE zone = ? AND canonical > ? ORDER BY canonical LIMIT ?',
                       (zone, after or '', limit)).fetchall()


def issued_by(con, key_id, since):
    return con.execute('SELECT count(*) FROM issue_log WHERE key_id = ? AND at >= ?', (key_id, since)).fetchone()[0]
