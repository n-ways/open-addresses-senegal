"""The register in force and the pieces of an address that are computed,
not stored: zones, lieux and their blocks, forms, spot and Plus Codes,
distances and outline geometry.

Parsing, check letters, spot codes, name keys, plate names and numbering all
come from the reference engine (engine/reference/sn_engine.py); nothing here
re-implements them.
"""
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENGINE_DIR = os.path.join(ROOT, 'engine', 'reference')
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)
import sn_engine as E  # noqa: E402

COUNTRY = 'SN'
COUNTRY_NAME = 'Senegal'
CREDIT = 'N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)'
CREDIT_URL = 'https://github.com/n-ways/open-addresses-senegal'
LICENCES = {'data': 'ODbL 1.0 (LICENSE-DATA)', 'code': 'Apache-2.0 (LICENSE)', 'documents': 'CC BY 4.0 (LICENSE-DOCS)'}
SPEC = 'engine/SPEC.md v0.2'

# Columns of the published files, in order (registry/README.md).
CODE_COLUMNS = ['canonical', 'remembered', 'written', 'lieu', 'official_name', 'number', 'check', 'status', 'issued',
                'issued_at', 'entrance_lat', 'entrance_lng', 'entrance_kind', 'spot_code', 'class', 'use', 'kind',
                'structures', 'floor_area_m2', 'postcode', 'coverage', 'official_address']
LIEU_COLUMNS = ['lieu', 'zone', 'index', 'plate_name', 'official_name', 'kind', 'name_key', 'family', 'digits', 'blocks',
                'needs_commune_choice', 'aliases', 'near_town', 'coverage', 'e_utm28n', 'n_utm28n']

# Distances of the N-Ways issuer: a point within FOUND_M of a
# compound's entrance is at that compound; a new compound within EXISTS_M of
# one already issued is the same building; a second door is within DOOR_M of
# the first; an entrance moves at most MOVE_M.
FOUND_M = 12.0
EXISTS_M = 3.0
DOOR_M = 80.0
MOVE_M = 80.0
MIN_AREA_M2 = 12.0
MAX_AREA_M2 = 20000.0


def model_dir():
    return os.environ.get('MODEL_DIR') or os.path.join(ROOT, 'model')


def border_file():
    """The national border (engine/SPEC.md 2.3), simplified from OpenStreetMap's
    admin_level=2 boundary of Senegal."""
    return os.environ.get('BORDER_FILE') or os.path.join(ROOT, 'engine', 'data', 'border.geojson')


def dist_m(lat1, lng1, lat2, lng2):
    """Equirectangular distance in metres: the issuer's rule for gates and doors."""
    dy = (lat2 - lat1) * 111320
    dx = (lng2 - lng1) * 111320 * math.cos((lat1 + lat2) / 2 * math.pi / 180)
    return math.hypot(dx, dy)


def round1(x):
    """One decimal, ties to even, as the issuer rounds floor areas."""
    return round(x * 10) / 10


def fold(s):
    """Lower case, no accents, single spaces: the key for typed text."""
    return E.fold(s or '')


# ---------------------------------------------------------------- lieux
def lieu_from_row(r, precise=None):
    """A registry/lieux.csv row as the engine's lieu dict. precise: (e, n)
    at full precision from model/lieux.json when it agrees with the row."""
    blocks = [[int(a), int(b)] for a, b in (x.split('-') for x in r['blocks'].split('|') if x)]
    e, n = float(r['e_utm28n']), float(r['n_utm28n'])
    if precise and f'{precise[0]:.0f}' == r['e_utm28n'] and f'{precise[1]:.0f}' == r['n_utm28n']:
        e, n = precise
    return {'zone': r['zone'], 'index': int(r['index']), 'name': r['official_name'], 'officialName': r['official_name'],
            'placeWord': r['plate_name'], 'kind': r['kind'], 'nameKey': r['name_key'], 'family': int(r['family']),
            'digits': int(r['digits']), 'blocks': blocks, 'needsCouncilChoice': r['needs_commune_choice'] == 'true',
            'aliases': [a for a in r['aliases'].split('|') if a], 'nearTown': r['near_town'] or None,
            'coverage': r['coverage'], 'e': e, 'n': n}


def blocks_text(lieu):
    return '|'.join(f'{a}-{b}' for a, b in lieu['blocks'])


def ref(lieu):
    return f"{lieu['zone']}-{lieu['index']:04d}"


class Register:
    """Zones (model/zones.json, zones.geojson) and the frozen lieux with
    their blocks (registry/lieux.csv, plus any block added since)."""

    def __init__(self, lieux_items, model=None):
        self.zones = E.Zones(model or model_dir())
        self.border = E.Border(border_file())
        self.lieux = E.Lieux(model='', items=lieux_items)
        self.by_ref = {ref(it): it for it in lieux_items}

    def zone(self, key):
        return self.zones.by_key.get(key)

    def lieu(self, r):
        return self.by_ref.get(r)

    def zone_at(self, lat, lng):
        """The zone of a point, or None outside Senegal: in no zone, or more than
        300 m outside the national border whatever the zone outlines say (SPEC 2.3)."""
        zk = self.zones.lookup(lat, lng)
        if zk is None or not self.border.holds(lat, lng):
            return None
        return zk

    def forms(self, lieu, number):
        return E.address_forms(self.zones, lieu, number)

    def spot(self, lat, lng, key=None):
        return E.encode_spot(lat, lng, self.zones, key)

    def zone_info(self, z):
        return {'key': z['key'], 'index': z['index'], 'name': z['name'], 'plateName': z['name'].split(' (')[0],
                'region': z['region'], 'digits': z['digits'], 'cellMetres': z['cellMetres'],
                'origin': {'e': z['originE'], 'n': z['originN']}, 'frameMetres': z['frameMetres']}

    def lieu_info(self, lieu):
        lat, lng = E.utm_inverse(lieu['e'], lieu['n'])
        fam = self.lieux.families.get(lieu['nameKey'], {})
        return {'id': ref(lieu), 'zone': lieu['zone'], 'index': lieu['index'], 'plateName': lieu['placeWord'],
                'officialName': lieu['officialName'], 'kind': lieu['kind'], 'aliases': lieu['aliases'],
                'nearTown': lieu['nearTown'], 'coverage': lieu['coverage'] or None,
                'needsCommuneChoice': lieu['needsCouncilChoice'], 'nameKey': lieu['nameKey'], 'family': lieu['family'],
                'digits': lieu['digits'], 'blocks': [list(b) for b in lieu['blocks']],
                'sameName': sorted(ref(x) for x in fam.get('lieux', ()) if x is not lieu),
                'position': {'lat': round(lat, 7), 'lng': round(lng, 7), 'e': round(lieu['e'], 1), 'n': round(lieu['n'], 1)}}

    def find_areas(self, name):
        """Lieux whose plate name, official name or an alias has the name key
        of `name`, plus those whose folded official name starts with it."""
        k = E.name_key(name)
        out = []
        for fk in sorted(self.lieux.names.get(k, ())):
            for it in self.lieux.families[fk]['lieux']:
                names = [it['placeWord'], it['officialName']] + it['aliases']
                if any(E.name_key(x) == k for x in names):
                    out.append(it)
        f = fold(name)
        if f:
            seen = {id(x) for x in out}
            for it in self.lieux.items:
                if id(it) not in seen and (fold(it['officialName']).startswith(f) or fold(it['placeWord']).startswith(f)):
                    out.append(it)
        return out


# ---------------------------------------------------------------- Plus Codes
_OLC = '23456789CFGHJMPQRVWX'


def plus_code(lat, lng):
    """Open Location Code of a point, 11 characters (about 3.5 m x 2.8 m),
    as the N-Ways card gives it for sharing outside Senegal (SPEC 9)."""
    lat = min(max(lat, -90.0), 90.0)
    lng = ((lng + 180) % 360 + 360) % 360 - 180
    lat_v = int(math.floor(round((lat + 90) * 25000000 * 1e6) / 1e6))
    lng_v = int(math.floor(round((lng + 180) * 8192000 * 1e6) / 1e6))
    lat_v = min(lat_v, 180 * 25000000 - 1)
    code = ''
    for _ in range(5):
        code = _OLC[(lat_v % 5) * 4 + lng_v % 4] + code
        lat_v //= 5
        lng_v //= 4
    for _ in range(5):
        code = _OLC[lng_v % 20] + code
        code = _OLC[lat_v % 20] + code
        lat_v //= 20
        lng_v //= 20
    return code[:8] + '+' + code[8:11]


# ---------------------------------------------------------------- outlines
def ring_area_m2(ring):
    """Area of a [lng, lat] ring, shoelace formula in UTM 28N metres."""
    if len(ring) < 3:
        return 0.0
    pts = [E.utm_forward(p[1], p[0]) for p in ring]
    a = 0.0
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        a += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
    return abs(a) / 2


def ring_perimeter_m(ring):
    return sum(dist_m(ring[i][1], ring[i][0], ring[(i + 1) % len(ring)][1], ring[(i + 1) % len(ring)][0])
               for i in range(len(ring)))


def in_ring(lng, lat, ring):
    return E.Zones._in_ring(lng, lat, ring)


def _utm_ring(ring):
    return [E.utm_forward(p[1], p[0]) for p in ring]


def _signed(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts))) / 2


def _convex(pts):
    sign = 0
    for i in range(len(pts)):
        a, b, c = pts[i], pts[(i + 1) % len(pts)], pts[(i + 2) % len(pts)]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if cr:
            if sign and (cr > 0) != (sign > 0):
                return False
            sign = cr
    return True


def _clip(subject, clip):
    """Sutherland-Hodgman: subject polygon clipped by a convex, counter-clockwise clip polygon."""
    out = subject
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        inp, out = out, []
        if not inp:
            break
        inside = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            if inside(q):
                if not inside(p):
                    out.append(_cross(p, q, a, b))
                out.append(q)
            elif inside(p):
                out.append(_cross(p, q, a, b))
    return out


def _cross(p, q, a, b):
    x1, y1, x2, y2, x3, y3, x4, y4 = p[0], p[1], q[0], q[1], a[0], a[1], b[0], b[1]
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return q
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def overlap_m2(ring_a, ring_b):
    """Area shared by two [lng, lat] rings, in m². Exact when either ring is
    convex (clipping); otherwise counted on a grid of at most 200 x 200 points."""
    a, b = _utm_ring(ring_a), _utm_ring(ring_b)
    for s, c in ((a, b), (b, a)):
        if _convex(c):
            if _signed(c) < 0:
                c = c[::-1]
            r = _clip(s, c)
            return abs(_signed(r)) if len(r) >= 3 else 0.0
    x0, y0 = max(min(p[0] for p in a), min(p[0] for p in b)), max(min(p[1] for p in a), min(p[1] for p in b))
    x1, y1 = min(max(p[0] for p in a), max(p[0] for p in b)), min(max(p[1] for p in a), max(p[1] for p in b))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    n = 200
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    hits = sum(1 for i in range(n) for j in range(n)
               if in_ring(x0 + (i + .5) * dx, y0 + (j + .5) * dy, a) and in_ring(x0 + (i + .5) * dx, y0 + (j + .5) * dy, b))
    return hits * dx * dy


def ring_bbox(ring):
    return min(p[1] for p in ring), max(p[1] for p in ring), min(p[0] for p in ring), max(p[0] for p in ring)


# ---------------------------------------------------------------- compound profile
def compound_use(classes):
    """Use of a compound from its main structure's class (SPEC 6.3)."""
    if not classes:
        return 'unknown'
    g = classes[0].split('.', 1)[0]
    mixed = any(c.split('.', 1)[0] not in (g, 'res', 'inconnu', 'chantier', 'ruine') for c in classes[1:])
    if g == 'res':
        return 'mixed' if mixed else 'residential'
    return {'com': 'commercial', 'hot': 'commercial', 'mix': 'commercial', 'gov': 'public', 'edu': 'public',
            'san': 'public', 'tra': 'public', 'rel': 'religious', 'ind': 'industrial', 'pec': 'industrial',
            'agr': 'industrial'}.get(g, 'unknown')


def new_compound_profile(area, perimeter, door):
    """Profile of an address issued on demand: one structure drawn by people
    (classified by size alone, in town), or none when no outline was given.
    A second door of a compound is kind 'porte'."""
    if area > 0:
        sz = E.size_profile(area, perimeter, None, None, None)
        floor_area = round1(area * sz['floors'])
        cls, _, _ = E.classify({}, area, sz['floors'], None, rural=False, in_multi=False, satellite=False)
        prof = {'class': cls, 'use': compound_use([cls]), 'kind': 'un_batiment', 'structures': 1, 'floorAreaM2': floor_area}
    else:
        prof = {'class': '', 'use': 'unknown', 'kind': 'un_batiment', 'structures': 0, 'floorAreaM2': 0.0}
    if door:
        prof['kind'] = 'porte'
    return prof


SPLIT_LETTERS_DIGITS = re.compile(r'(?<=[^\W\d_])(?=\d)|(?<=\d)(?=[^\W\d_])')


def loosen(text):
    """Typed text as the finder reads it: letters and digits run together are
    split ('Ouakam2512' -> 'Ouakam 2512'), spaces collapsed."""
    return ' '.join(SPLIT_LETTERS_DIGITS.sub(' ', text or '').split())
