#!/usr/bin/env python3
"""Write the data files behind the paper's figures (docs/figures/data/*.dat)
from the published registry, the model files and the reference engine.

  python3 tools/paper-figures.py

The figures themselves are the TikZ/pgfplots sources in docs/figures/*.tex;
docs/paper/build.sh compiles them. Standard library only; one pass over
registry/anchors (about a minute)."""
import csv, glob, gzip, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
OUT = os.path.join(ROOT, 'docs', 'figures', 'data')
sys.path.insert(0, os.path.join(ROOT, 'engine', 'reference'))
import sn_engine as E  # noqa: E402

M = os.path.join(ROOT, 'model')


def load(name):
    return json.load(open(os.path.join(M, name), encoding='utf-8'))


def simplify(pts, tol):
    """Douglas-Peucker on a list of (x, y); a closed ring is cut in two halves first."""
    if len(pts) < 3:
        return pts
    if pts[0] == pts[-1] and len(pts) > 4:
        h = len(pts) // 2
        return simplify(pts[:h + 1], tol)[:-1] + simplify(pts[h:], tol)
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        (x1, y1), (x2, y2) = pts[i], pts[j]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1e-9
        best, bk = -1, None
        for k in range(i + 1, j):
            x, y = pts[k]
            d = abs(dy * (x - x1) - dx * (y - y1)) / L
            if d > best:
                best, bk = d, k
        if bk is not None and best > tol:
            keep[bk] = True
            stack += [(i, bk), (bk, j)]
    return [p for p, k in zip(pts, keep) if k]


def write(name, header, rows):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(header + '\n')
        for r in rows:
            f.write((' '.join(str(v) for v in r) if r else 'nan nan') + '\n')


# The map's raster: one pixel per 4 km cell over E 196-904 km, N 1360-1848 km,
# coloured on a log scale (1 to 10,000 compounds), empty cells transparent.
MAP_E0, MAP_N0, MAP_W, MAP_H = 49, 340, 177, 122
STOPS = [(253, 239, 66), (120, 190, 60), (0, 133, 63), (8, 60, 32)]


def ramp(t):
    t = max(0.0, min(1.0, t)) * (len(STOPS) - 1)
    i = min(int(t), len(STOPS) - 2)
    f = t - i
    return tuple(round(a + (b - a) * f) for a, b in zip(STOPS[i], STOPS[i + 1]))


def density_png(cells):
    import struct, zlib
    raw = bytearray()
    for row in range(MAP_H):
        y = MAP_N0 + MAP_H - 1 - row
        raw.append(0)
        for col in range(MAP_W):
            c = cells.get((MAP_E0 + col, y), 0)
            raw += bytes(ramp(math.log10(c) / 4) + (255,)) if c else b'\0\0\0\0'

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', MAP_W, MAP_H, 8, 6, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))
    with open(os.path.join(OUT, 'density.png'), 'wb') as f:
        f.write(png)


def zones_outline():
    """Zone outlines in UTM 28N kilometres, one ring per block, simplified to 400 m."""
    gj = load('zones.geojson')
    rows, labels = [], []
    for feat in gj['features']:
        g = feat['geometry']
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        big = None
        for poly in polys:
            full = [E.utm_forward(lat, lon) for lon, lat in poly[0]]
            ring = simplify(full, 400.0)
            if len(ring) < 4:
                ring = simplify(full, 50.0)
            if len(ring) < 4:
                continue
            for e, n in ring:
                rows.append((round(e / 1000, 2), round(n / 1000, 2)))
            rows.append(())
            area = abs(sum(ring[i][0] * ring[i - 1][1] - ring[i - 1][0] * ring[i][1] for i in range(len(ring)))) / 2
            if big is None or area > big[0]:
                cx = sum(p[0] for p in ring) / len(ring)
                cy = sum(p[1] for p in ring) / len(ring)
                big = (area, cx, cy)
        labels.append((feat['properties']['key'], round(big[1] / 1000, 1), round(big[2] / 1000, 1),
                       round(big[0] / 1e6)))
    write('zones-outline.dat', 'x y', rows)
    write('zones-labels.dat', 'key x y areakm2', sorted(labels))


def density_and_ouakam():
    """Compounds per 4 km cell over the country; Ouakam's compounds with their numbers."""
    cells = {}
    ouakam = []
    lieu_of = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'registry', '*.csv.gz'))):
        base = os.path.basename(f)
        if base.startswith('lieux'):
            continue
        main = csv.DictReader(gzip.open(f, 'rt', encoding='utf-8'))
        anc = csv.DictReader(gzip.open(os.path.join(ROOT, 'registry', 'anchors', base), 'rt', encoding='utf-8'))
        for r, a in zip(main, anc):
            assert r['canonical'] == a['canonical']
            e, n = E.utm_forward(float(a['anchor_lat']), float(a['anchor_lng']))
            k = (int(e // 4000), int(n // 4000))
            cells[k] = cells.get(k, 0) + 1
            lieu_of[r['lieu']] = lieu_of.get(r['lieu'], 0) + 1
            if r['lieu'] == 'DKR-0080':
                ouakam.append((round(e - 227000, 1), round(n - 1620000, 1), int(r['number'])))
    write('density.dat', 'x y count',
          sorted((4 * x + 2, 4 * y + 2, c) for (x, y), c in cells.items()))
    density_png(cells)
    write('ouakam.dat', 'x y number', sorted(ouakam, key=lambda t: t[2]))
    return lieu_of


def lieu_sizes(lieu_of):
    """Histogram of compounds per lieu on logarithmic bins (5 per decade)."""
    bins = {}
    for c in lieu_of.values():
        b = math.floor(5 * math.log10(c))
        bins[b] = bins.get(b, 0) + 1
    rows = [(round(10 ** (b / 5), 3), round(10 ** ((b + 1) / 5), 3), bins.get(b, 0))
            for b in range(0, max(bins) + 1)]
    rows.append((rows[-1][1], rows[-1][1], 0))   # closes the last interval for pgfplots' ybar interval
    write('lieu-sizes.dat', 'lo hi lieux', rows)
    s = sorted(lieu_of.values())
    return {'lieux': len(s), 'median': s[len(s) // 2], 'max': s[-1],
            'le270': sum(1 for c in s if c <= 270), 'le2700': sum(1 for c in s if c <= 2700)}


def ranges():
    """The blocks of two national name ranges, with the compounds issued in each block."""
    fam = {f['key']: f for f in load('name-families.json')['families']}
    zname = {z['key']: z['name'].split(' (')[0] for z in load('zones.json')['zones']}
    counts = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'registry', '*.csv.gz'))):
        if os.path.basename(f).startswith('lieux'):
            continue
        for r in csv.DictReader(gzip.open(f, 'rt', encoding='utf-8')):
            counts[r['lieu']] = counts.get(r['lieu'], 0) + 1
    rows = []
    for row, key in ((2, 'medina'), (1, 'darusalam')):
        for ref, blocks in fam[key]['blocks'].items():
            z, i = ref.split('/')
            for lo, hi in blocks:
                rows.append((row, lo, hi, z, zname[z].replace(' ', '~'), counts.get(f'{z}-{int(i):04d}', 0)))
    write('ranges.dat', 'row lo hi zone name compounds', rows)


def dakar_frame():
    """Zone DKR in its spot frame: outline in cell units (2 m), and two reference points."""
    zones = E.Zones()
    z = zones.by_key['DKR']
    rows = []
    for key, _, poly in zones.shapes:
        if key != 'DKR':
            continue
        ring = simplify([E.utm_forward(lat, lon) for lon, lat in poly[0]], 30.0)
        for e, n in ring:
            rows.append((round((e - z['originE']) / z['cellMetres']), round((n - z['originN']) / z['cellMetres'])))
        rows.append(())
    write('dakar-frame.dat', 'x y', rows)
    pts = []
    for label, lat, lon in (('Place~de~l\'Indépendance', 14.6681, -17.4317),
                            ('Ouakam~2512', 14.7247067, -17.4849374)):
        code = E.encode_spot(lat, lon, zones, 'DKR')
        _, x, y = code.split()
        pts.append((x, y, label))
    write('dakar-points.dat', 'x y label', pts)


def sources():
    """Footprints by source and region (OpenStreetMap against the machine-learned sets)."""
    b = load('building-stats.json')['regions']
    REG = {'SN-DK': 'Dakar', 'SN-TH': 'Thiès', 'SN-DB': 'Diourbel', 'SN-FK': 'Fatick', 'SN-KL': 'Kaolack',
           'SN-KA': 'Kaffrine', 'SN-LG': 'Louga', 'SN-SL': 'Saint-Louis', 'SN-MT': 'Matam', 'SN-TC': 'Tambacounda',
           'SN-KE': 'Kédougou', 'SN-KD': 'Kolda', 'SN-SE': 'Sédhiou', 'SN-ZG': 'Ziguinchor'}
    rows = sorted(((REG[k].replace(' ', '~'), v['bySource']['osm'], v['bySource']['ml'],
                    round(100 * v['bySource']['osm'] / v['structures'], 1)) for k, v in b.items()),
                  key=lambda t: t[1] + t[2])
    write('sources.dat', 'region osm ml osmshare', rows)


def designs():
    s = load('name-families.json')['summary']
    per_lieu = s['shareCompoundsByDigitsPerLieuRangesBefore']
    official = s['plateNames']['before']['shareCompoundsByDigits']
    rows = [(1, 'one~range~per~place', *(round(100 * per_lieu[k], 1) for k in '345')),
            (2, 'per~name,~official~names', *(round(100 * official[k], 1) for k in '345'))]
    rows.append((3, 'per~name,~plate~names', *(round(100 * s['shareCompoundsByDigits'][k], 1) for k in '345')))
    write('designs.dat', 'row design d3 d4 d5', rows)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    zones_outline()
    lieu_of = density_and_ouakam()
    print(json.dumps(lieu_sizes(lieu_of)))
    ranges()
    dakar_frame()
    sources()
    designs()
