#!/usr/bin/env python3
"""N-Ways Addressing for Senegal: reference engine (standard library only).

This file is the executable definition of engine/SPEC.md. Where the two
disagree, the SPEC wins and this file is a bug.

  python3 sn_engine.py encode 14.66810 -17.43170        spot code for a point
  python3 sn_engine.py decode "DKR 5553 1512"          point for a spot code
  python3 sn_engine.py check  "SN-DKR-0080-2512-J"       validate a code
  python3 sn_engine.py find   "Ouakam 2512"              resolve a remembered address (no context needed)
  python3 sn_engine.py vectors                           print the test vectors
  python3 sn_engine.py selftest                          run every check (and compare vectors.json)
  python3 sn_engine.py registry samples/dakar-medina.csv number a real sample's compounds
  python3 -m unittest test_sn                            the tests (selftest + the national-uniqueness rule)

The address (SPEC.md section 3) has three forms of one identity:
  remembered  Ouakam 2512              place word + 3-5 digit number, no letters; unique in all
                                       of Senegal on its own (SPEC 3.3: one national range per name)
  written     OUAKAM 2512 · DAKAR      plates and forms: + zone name (information only); no check
                                       letter, since people never see one
  canonical   SN-DKR-0080-2512-J       APIs and QR codes: zone key, place index, number, check
Spot codes cover any point with no compound: "DKR 5553 1512" (computed offline).
The check letter is ISO/IEC 7064 MOD 11-2 written with the eleven letters
FHJKMQRTWXZ; for an address it is computed over the name family and the
number; people never have to remember it.
"""
import csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, '..', '..', 'model')


def _load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# ---------------------------------------------------------------- check letter
# Eleven letters whose French names do not rhyme with each other or with a
# digit, and that Wolof speakers name the French way: no -é letters except T
# (B C D G P V dropped), one of each e-e pair (F not S, M not N, R not L),
# J kept and G dropped (gé/ji), no vowels, no Y (i grec), no O/I/L.
CHECK_LETTERS = 'FHJKMQRTWXZ'
SPOKEN_FR = {'F': 'effe', 'H': 'ache', 'J': 'ji', 'K': 'ka', 'M': 'emme', 'Q': 'ku', 'R': 'erre',
             'T': 'té', 'W': 'double vé', 'X': 'ixe', 'Z': 'zède'}
DIGITS_FR = ['zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf']
DIGITS_WO = ['tus', 'benn', 'ñaar', 'ñett', 'ñeent', 'juróom', 'juróom benn', 'juróom ñaar',
             'juróom ñett', 'juróom ñeent']


def mod11_2(digits):
    """ISO/IEC 7064 MOD 11-2 check value (0..10) of a digit string."""
    p = 0
    for ch in digits:
        p = ((p + int(ch)) * 2) % 11
    return (12 - p) % 11


def check_letter(zone_index, digits):
    return CHECK_LETTERS[mod11_2(f'{zone_index:02d}{digits}')]


# ---------------------------------------------------------------- UTM zone 28N
# WGS 84 / UTM zone 28N (EPSG:32628): Kruger series to n^4 (Karney 2011),
# sub-millimetre inside Senegal (the east tip is 3.65 degrees from -15).
A_ = 6378137.0
F_ = 1 / 298.257223563
K0, LON0, FE = 0.9996, math.radians(-15.0), 500000.0
_n = F_ / (2 - F_)
_A = A_ / (1 + _n) * (1 + _n ** 2 / 4 + _n ** 4 / 64)
_al = [_n / 2 - 2 * _n ** 2 / 3 + 5 * _n ** 3 / 16 + 41 * _n ** 4 / 180,
       13 * _n ** 2 / 48 - 3 * _n ** 3 / 5 + 557 * _n ** 4 / 1440,
       61 * _n ** 3 / 240 - 103 * _n ** 4 / 140,
       49561 * _n ** 4 / 161280]
_be = [_n / 2 - 2 * _n ** 2 / 3 + 37 * _n ** 3 / 96 - _n ** 4 / 360,
       _n ** 2 / 48 + _n ** 3 / 15 - 437 * _n ** 4 / 1440,
       17 * _n ** 3 / 480 - 37 * _n ** 4 / 840,
       4397 * _n ** 4 / 161280]
_de = [2 * _n - 2 * _n ** 2 / 3 - 2 * _n ** 3 + 116 * _n ** 4 / 45,
       7 * _n ** 2 / 3 - 8 * _n ** 3 / 5 - 227 * _n ** 4 / 45,
       56 * _n ** 3 / 15 - 136 * _n ** 4 / 35,
       4279 * _n ** 4 / 630]
_e2n = 2 * math.sqrt(_n) / (1 + _n)


def utm_forward(lat, lon):
    phi, lam = math.radians(lat), math.radians(lon) - LON0
    t = math.sinh(math.atanh(math.sin(phi)) - _e2n * math.atanh(_e2n * math.sin(phi)))
    xi_, eta_ = math.atan2(t, math.cos(lam)), math.atanh(math.sin(lam) / math.sqrt(1 + t * t))
    xi, eta = xi_, eta_
    for j, a in enumerate(_al, 1):
        xi += a * math.sin(2 * j * xi_) * math.cosh(2 * j * eta_)
        eta += a * math.cos(2 * j * xi_) * math.sinh(2 * j * eta_)
    return FE + K0 * _A * eta, K0 * _A * xi


def utm_inverse(e, n):
    xi, eta = n / (K0 * _A), (e - FE) / (K0 * _A)
    xi_, eta_ = xi, eta
    for j, b in enumerate(_be, 1):
        xi_ -= b * math.sin(2 * j * xi) * math.cosh(2 * j * eta)
        eta_ -= b * math.cos(2 * j * xi) * math.sinh(2 * j * eta)
    chi = math.asin(math.sin(xi_) / math.cosh(eta_))
    phi = chi + sum(d * math.sin(2 * j * chi) for j, d in enumerate(_de, 1))
    lam = LON0 + math.atan2(math.sinh(eta_), math.cos(xi_))
    return math.degrees(phi), math.degrees(lam)


# ---------------------------------------------------------------- zones
class Zones:
    """The 46 frozen code zones: metadata (zones.json) and outlines (zones.geojson)."""

    def __init__(self, model=MODEL):
        meta = _load_json(os.path.join(model, 'zones.json'))['zones']
        self.by_key = {z['key']: z for z in meta}
        self.by_index = {z['index']: z for z in meta}
        self.shapes = []  # (key, bbox, [rings])
        gj = _load_json(os.path.join(model, 'zones.geojson'))
        for f in gj['features']:
            g = f['geometry']
            polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
            for poly in polys:
                xs = [p[0] for p in poly[0]]
                ys = [p[1] for p in poly[0]]
                self.shapes.append((f['properties']['key'], (min(xs), min(ys), max(xs), max(ys)), poly))

    @staticmethod
    def _in_ring(x, y, ring):
        inside = False
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        return inside

    def lookup(self, lat, lon):
        """Zone key for a point: the first zone (by index) whose outline holds it,
        else the zone with the nearest outline vertex within 2 km (coast, rivers,
        the edges of the 2019 outlines), else None (outside Senegal)."""
        hits = []
        for key, (x0, y0, x1, y1), poly in self.shapes:
            if x0 <= lon <= x1 and y0 <= lat <= y1 and self._in_ring(lon, lat, poly[0]) \
                    and not any(self._in_ring(lon, lat, h) for h in poly[1:]):
                hits.append(self.by_key[key]['index'])
        if hits:
            return self.by_index[min(hits)]['key']
        best, bestd = None, 2000.0
        e0, n0 = utm_forward(lat, lon)
        for key, (x0, y0, x1, y1), poly in self.shapes:
            if not (x0 - 0.03 <= lon <= x1 + 0.03 and y0 - 0.03 <= lat <= y1 + 0.03):
                continue
            for x, y in poly[0]:
                if abs(x - lon) < 0.03 and abs(y - lat) < 0.03:
                    e, n = utm_forward(y, x)
                    d = math.hypot(e - e0, n - n0)
                    if d < bestd:
                        best, bestd = key, d
        return best


# ---------------------------------------------------------------- the national border (SPEC 2.3)
BORDER = os.path.join(HERE, '..', 'data', 'border.geojson')
BORDER_M = 300.0     # how far outside the national border an entrance may lie


class Border:
    """The national border (engine/data/border.geojson): the OpenStreetMap
    admin_level=2 boundary of Senegal, simplified. A building more than
    BORDER_M outside it is in a neighbouring country and never has an address,
    whatever the zone outlines say. The file records the largest distance
    between the simplified line and the true one (maxDeviationM); the limit
    applied here is BORDER_M less that deviation, rounded up, so nothing it
    accepts lies more than BORDER_M outside the true border."""

    CELL = 1000.0

    def __init__(self, path=BORDER, limit_m=None):
        gj = _load_json(path)
        props = gj.get('properties') or {}
        geom = gj['geometry'] if gj.get('type') == 'Feature' else gj
        polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
        dev = float(props.get('maxDeviationM', 0.0))
        self.limit = float(limit_m) if limit_m is not None else BORDER_M - math.ceil(dev)
        self.segs = []
        for poly in polys:
            for ring in poly:
                pts = [utm_forward(y, x) for x, y in ring]
                if pts and pts[0] == pts[-1]:
                    pts = pts[:-1]
                for i in range(len(pts)):
                    self.segs.append((pts[i - 1], pts[i]))
        c, r = self.CELL, self.limit
        self.bands = {}     # horizontal band -> segments crossing it (inside test)
        self.cells = {}     # grid cell -> segments within the limit of it (distance)
        for k, ((ax, ay), (bx, by)) in enumerate(self.segs):
            for b in range(int(min(ay, by) // c), int(max(ay, by) // c) + 1):
                self.bands.setdefault(b, []).append(k)
            for gx in range(int((min(ax, bx) - r) // c), int((max(ax, bx) + r) // c) + 1):
                for gy in range(int((min(ay, by) - r) // c), int((max(ay, by) + r) // c) + 1):
                    self.cells.setdefault((gx, gy), []).append(k)

    def _inside(self, e, n):
        inside = False
        for k in self.bands.get(int(n // self.CELL), ()):
            (ax, ay), (bx, by) = self.segs[k]
            if (ay > n) != (by > n) and e < (bx - ax) * (n - ay) / (by - ay) + ax:
                inside = not inside
        return inside

    def outside_m(self, lat, lon):
        """0 inside the border; else the metres to it, or infinity beyond the limit."""
        e, n = utm_forward(lat, lon)
        if self._inside(e, n):
            return 0.0
        best = math.inf
        for k in self.cells.get((int(e // self.CELL), int(n // self.CELL)), ()):
            (ax, ay), (bx, by) = self.segs[k]
            dx, dy = bx - ax, by - ay
            L = dx * dx + dy * dy
            t = 0.0 if L == 0 else max(0.0, min(1.0, ((e - ax) * dx + (n - ay) * dy) / L))
            best = min(best, math.hypot(e - ax - t * dx, n - ay - t * dy))
        return best if best <= self.limit else math.inf

    def holds(self, lat, lon):
        """True for a point inside the border or within the limit of it."""
        return self.outside_m(lat, lon) <= self.limit


# ---------------------------------------------------------------- spot codes
def encode_spot(lat, lon, zones, key=None):
    key = key or zones.lookup(lat, lon)
    if key is None:
        raise ValueError('point is outside Senegal')
    z = zones.by_key[key]
    e, n = utm_forward(lat, lon)
    c, d = z['cellMetres'], z['digits']
    x, y = math.floor((e - z['originE']) / c), math.floor((n - z['originN']) / c)
    if not (0 <= x < 10 ** d and 0 <= y < 10 ** d):
        raise ValueError(f'point is outside the frame of zone {key}')
    ds = f'{x:0{d}d}{y:0{d}d}'
    # No check letter is written: a spot code is typed by people, and every extra
    # character is one more to get wrong. validate() still verifies a letter when
    # a code written with one is typed.
    return f'{key} {ds[:d]} {ds[d:]}'


SPOT_RE = __import__('re').compile(r'^\s*([A-Za-z]{3})[\s.-]*(\d{4,5})[\s.-]*(\d{4,5})(?:[\s.-]*([A-Za-z]))?\s*$')
CANON_RE = __import__('re').compile(r'^\s*SN-([A-Z]{3})-(\d{4})-(\d{3,5})-([A-Z])(?:[·/|](\d+)(?:\.(\d+))?)?\s*$', 2)


def fold(s):
    import unicodedata
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
                    .lower().replace('-', ' ').replace("'", ' ').split())


# ---------------------------------------------------------------- national name ranges (SPEC 3.3)
# The remembered address 'Ouakam 2512' must be unique in the whole country on
# its own: no zone, no town after a comma, no position of the phone. Every lieu
# whose name folds to the same name key belongs to one name family; the family
# has ONE national number range, cut into one block per lieu. A number therefore
# falls in exactly one block, and 'name + number' decodes to one lieu and one
# compound anywhere in Senegal.
_NAME_RULES = [  # applied in order to the joined, accent-free, lower-case name
    (r'ou(?=[aeiy])', 'w'),   # French 'ou' before a vowel = Wolof w: Ouakam = Wakam, Taoua = Tawa
    (r'ou', 'u'),             # French 'ou' = Wolof u: Darou = Daru, Diokoul = Diokul
    (r'eu', 'e'),             # Keur = Kër
    (r'ch', '§'),             # keep French ch apart from k (restored below)
    (r'kh', 'x'),             # Khoudoss = Xudoss
    (r'th', 't'),             # Thiès = Ties, Santhiaba = Santiaba
    (r'ph', 'f'),
    (r'dj', 'j'),             # Djidda = Jidda
    (r'di(?=[aeou])', 'j'),   # Ndiaye = Njaay, Diamaguène = Jamaguen
    (r'gn', 'ny'),            # Sakhagne = Saxanye (Wolof ñ)
    (r'c(?=[eiy])', 's'),
    (r'ck', 'k'), (r'qu', 'k'), (r'q', 'k'), (r'c', 'k'),   # Mbacké = Mbakke, Thieckene = Tiekene
    (r'§', 'ch'),
    (r'y', 'i'),              # Mbayène = Mbaiene
    (r'h', ''),               # silent h: Hamdallaye = Amdalaye, Missirah = Missira
]
_NAME_DROP_LEAD = {'le', 'la', 'les', 'l', 'quartier', 'village', 'hameau', 'de', 'du', 'd'}
_NAME_DROP_TAIL = {'numero', 'no', 'n'}


def name_key(s):
    """The national name key of a place word (SPEC 3.3.1). Two names with one key
    share one national number range. The folding is deliberately generous:
    names people can confuse by ear or in spelling must never give two places
    the same remembered address."""
    import re as _re
    import unicodedata
    s = s.replace('ñ', 'ny').replace('Ñ', 'ny')
    s = s.replace('œ', 'oe').replace('Œ', 'oe').replace('æ', 'ae').replace('Æ', 'ae')   # Sacré-Cœur = Sacré Coeur
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower()
    toks = _re.sub(r"[-'’.()/,·]", ' ', s).split()
    toks = ['saint' if t in ('st', 'ste', 'sainte') else t for t in toks]
    while toks and (toks[-1].isdigit() or toks[-1] in _NAME_DROP_TAIL):   # HLM 5 -> HLM, Pikine 3 -> Pikine
        toks.pop()
    while len(toks) > 1 and toks[0] in _NAME_DROP_LEAD:
        toks.pop(0)
    s = ''.join(toks)                                   # Keur Massar = Keurmassar
    for a, b in _NAME_RULES:
        s = _re.sub(a, b, s)
    s = _re.sub(r'(.)\1+', r'\1', s)                   # Gounass = Gounas, Mbakke = Mbake
    s = _re.sub(r'(?<=..)e$', '', s)                    # silent final e: Ndiayène/Ndiayene, Salame = Salam
    return s


def name_numeral(s):
    """The trailing numeral of a place word, if any ('HLM 5' -> '5'), else ''."""
    toks = fold(s).split()
    return toks[-1] if toks and toks[-1].isdigit() else ''


# ---------------------------------------------------------------- plate names (SPEC 3.2.1)
# The place word of the address is the lieu's PLATE name: at most 12 characters
# (an accented letter, a space, a hyphen or an apostrophe count one each) and
# 2 words (linking words de, du, des... do not count; a hyphen separates words).
# A trailing sector numeral ('HLM 5', 'Liberté 6') counts in the characters,
# not as a word. The full official name is kept and accepted as an alias.
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import plate_names as _P  # noqa: E402

_NUM_WORDS = {'un': 1, 'une': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5, 'six': 6, 'sept': 7, 'huit': 8,
              'neuf': 9, 'dix': 10}
_NUM_RE = __import__('re').compile(r'^(.*?\S)[\s-]*(?:(?:numero|numéro|no|n°)\s*)?(\d{1,2})$', 2)


def split_numeral(name):
    """'HLM 5' -> ('HLM', '5'); 'Plan Jaxaay 01' -> ('Plan Jaxaay', '1');
    'S.I.C.A.P. Liberté Six' -> ('S.I.C.A.P. Liberté', '6'); 'Gorom2' -> ('Gorom', '2')."""
    import re as _re
    s = _P.nfc(name).strip()
    m = _NUM_RE.match(s)
    if m and _re.search(r'[^\W\d]', m.group(1)):
        return m.group(1).strip(' -'), str(int(m.group(2)))
    ws = s.split()
    if len(ws) >= 2 and _P.plain(ws[-1]) in _NUM_WORDS:
        return ' '.join(ws[:-1]), str(_NUM_WORDS[_P.plain(ws[-1])])
    return s, ''


def plate_ok(plate):
    """True if a plate name keeps the limit: the name without its numeral has at
    most 2 words and no digit, the whole plate name at most 12 characters."""
    stem, num = split_numeral(plate)
    if num and plate != f'{stem} {num}':
        return False
    return _P.plate_length(plate) <= _P.MAX_CHARS and _P.fits(stem, 'fr')


SPARE_SHARE = 0.10  # at first issue at least 10 % of every name's range stays unallocated, for new same-named lieux


def block_grain(d):
    """Blocks start and end on round numbers: tens in 3-digit ranges, hundreds in 4- and 5-digit ranges."""
    return 10 if d == 3 else 100


def block_size(n_compounds, d):
    g = block_grain(d)
    return max(g, -(-HEADROOM * n_compounds // g) * g)


def allocatable(d):
    return int(round((1 - SPARE_SHARE) * 9 * 10 ** (d - 1)))   # 810, 8,100, 81,000


def family_digits(compound_counts):
    """Smallest d in {3,4,5} whose national range holds a block for every lieu of
    the name (3x headroom each) and still keeps 10 % spare; None if 5 digits
    are not enough (the name then needs a qualifier, SPEC 3.3.4)."""
    for d in (3, 4, 5):
        if sum(block_size(n, d) for n in compound_counts) <= allocatable(d):
            return d
    return None


def allocate_families(items, frozen=None, qualifiers=None):
    """First issue (and every rebuild before it): group lieux by name key, give
    each name a 5-digit family id and one national range, and cut one block per
    lieu in (zone key, lieu index) order from the bottom of the range. Sets on
    every item: placeWord, nameKey, family, digits, blocks [[lo, hi]].

    frozen: a previous allocation {key: {'id', 'digits', 'blocks': {"ZONE/index": [[lo, hi], ...]}}};
    its families and blocks are kept exactly (SPEC 3.3.5) and only new lieux get
    new blocks from their name's spare space. qualifiers: {(zone, index): qualifier}
    for names that do not fit 5 digits (SPEC 3.3.4)."""
    qualifiers = qualifiers or {}
    frozen = frozen or {}
    fam = {}
    for it in items:
        if not plate_ok(it['name']) and not it.get('needsCouncilChoice'):
            raise ValueError(f"plate name {it['name']!r} is over 12 characters or 2 words (SPEC 3.2.1)")
        q = qualifiers.get((it['zone'], it['index']))
        it['placeWord'] = it['name'] + (f' {q}' if q else '')
        it['nameKey'] = name_key(it['placeWord'])
        fam.setdefault(it['nameKey'], []).append(it)
    next_id = max([f['id'] for f in frozen.values()], default=-1) + 1
    out = {}
    for key in sorted(fam):
        members = sorted(fam[key], key=lambda it: (it['zone'], it['index']))
        if key in frozen:
            fz = frozen[key]
            fid, d = fz['id'], fz['digits']
            blocks = {k: [list(b) for b in v] for k, v in fz['blocks'].items()}
        else:
            fid, next_id = next_id, next_id + 1
            d = family_digits([it['compounds'] for it in members])
            if d is None:
                raise ValueError(f'name {members[0]["name"]!r}: {len(members)} lieux do not fit 5 digits; '
                                 f'give the largest a qualifier (SPEC 3.3.4)')
            blocks = {}
        top = max([b[1] for bl in blocks.values() for b in bl], default=10 ** (d - 1) - 1)
        for it in members:
            k = f"{it['zone']}/{it['index']}"
            if k not in blocks:
                size = block_size(it['compounds'], d)
                if top + size > 10 ** d - 1:
                    raise ValueError(f'name {it["name"]!r}: no spare room left for {k}; it needs a qualifier')
                blocks[k] = [[top + 1, top + size]]
                top += size
            it['family'], it['digits'], it['blocks'] = fid, d, blocks[k]
        out[key] = {'id': fid, 'digits': d, 'blocks': blocks}
    return out


def address_check(family_id, number):
    """SPEC 4: the check letter of an address binds the name (its family id), the
    number and, through the frozen block table, the lieu: one number of a name
    belongs to exactly one lieu. A single wrong digit or a swap of two adjacent
    digits in the number changes one payload position and is always caught,
    also when the wrong number falls in another same-named lieu's block."""
    return CHECK_LETTERS[mod11_2(f'{family_id:05d}{number:05d}')]


def validate(code, zones, lieux=None):
    """Validate a spot code or a canonical address (the forms that carry a check letter).
    A canonical address needs the lieu inventory: its letter is computed over the
    lieu's name family and the number, and the number must lie in that lieu's block."""
    m = CANON_RE.match(code)
    if m:
        key, li, num_, chk = m.group(1).upper(), int(m.group(2)), int(m.group(3)), m.group(4).upper()
        z = zones.by_key.get(key)
        if z is None:
            return False, f'unknown zone key {key}'
        if len(m.group(3)) not in (3, 4, 5) or m.group(3)[0] == '0':
            return False, 'house numbers have 3-5 digits and never start with 0'
        if lieux is None:
            return False, 'the lieu inventory (model/lieux.json) is needed to check an address'
        lieu = lieux.by_zone.get(key, {}).get(li)
        if lieu is None:
            return False, f'no lieu {li} in zone {key}'
        if len(m.group(3)) != lieu['digits'] or not in_blocks(lieu, num_):
            return False, f"{num_} is not a number of {lieu['placeWord']} in {key} (wrong lieu or number)"
        if address_check(lieu['family'], num_) != chk:
            return False, 'check letter does not match: a character is wrong or two are swapped'
        return True, 'address'
    m = SPOT_RE.match(code)
    if m:
        key, x, y, chk = m.group(1).upper(), m.group(2), m.group(3), (m.group(4) or '').upper()
        z = zones.by_key.get(key)
        if z is None:
            return False, f'unknown zone key {key}'
        if len(x) != z['digits'] or len(y) != z['digits']:
            return False, f'zone {key} spot codes have {z["digits"]}+{z["digits"]} digits'
        if chk and check_letter(z['index'], x + y) != chk:
            return False, 'check letter does not match: a character is wrong or two are swapped'
        return True, 'spot'
    return False, 'not an N-Ways Senegal code'


def decode_spot(code, zones):
    ok, why = validate(code, zones)
    if not ok:
        raise ValueError(why)
    if why != 'spot':
        raise ValueError('an address is looked up in the registry, not computed')
    m = SPOT_RE.match(code)
    z = zones.by_key[m.group(1).upper()]
    c = z['cellMetres']
    x, y = int(m.group(2)), int(m.group(3))
    e, n = z['originE'] + (x + 0.5) * c, z['originN'] + (y + 0.5) * c
    lat, lon = utm_inverse(e, n)
    return lat, lon, c


# ---------------------------------------------------------------- spoken forms
_FR = ['zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix', 'onze', 'douze',
       'treize', 'quatorze', 'quinze', 'seize']
_FR_TENS = {2: 'vingt', 3: 'trente', 4: 'quarante', 5: 'cinquante', 6: 'soixante'}


def fr_number(n):
    """French words for 0-999, as a house number is read ('cent vingt', 'quatre-vingt-onze')."""
    if n < 17:
        return _FR[n]
    if n < 20:
        return 'dix-' + _FR[n - 10]
    if n < 100:
        t, u = divmod(n, 10)
        if t in _FR_TENS:
            return _FR_TENS[t] + ('' if u == 0 else ' et un' if u == 1 else '-' + _FR[u])
        if t == 7:
            return 'soixante' + (' et onze' if u == 1 else '-' + fr_number(10 + u))
        return 'quatre-vingts' if n == 80 else 'quatre-vingt-' + fr_number(n - 80)
    h, r = divmod(n, 100)
    head = 'cent' if h == 1 else _FR[h] + (' cents' if r == 0 else ' cent')
    return head + ('' if r == 0 else ' ' + fr_number(r))


def fr_pair(p):
    """A two-digit group the way phone numbers are read: '07' -> 'zéro sept'."""
    return f'zéro {_FR[int(p[1])]}' if p[0] == '0' else fr_number(int(p))


def group_number(num_):
    """How a house number is written and grouped: 120 | 4512 -> '45 12' when read | 45128 -> '45 128'."""
    s_ = str(num_)
    return s_ if len(s_) <= 4 else f'{s_[:2]} {s_[2:]}'


def say_number(num_, lang='fr'):
    s_ = str(num_)
    if lang == 'wo':
        return ', '.join(DIGITS_WO[int(c)] for c in s_)
    if len(s_) == 3:
        return fr_number(num_)                                          # cent vingt
    if len(s_) == 4:
        return f'{fr_pair(s_[:2])}, {fr_pair(s_[2:])}'                  # quarante-cinq, douze
    return f'{fr_pair(s_[:2])}, {fr_number(int(s_[2:])) if s_[2] != "0" else "zéro " + fr_pair(s_[3:])}'


def spoken_spot(code, lang='fr'):
    m = SPOT_RE.match(code)
    key, x, y = m.group(1).upper(), m.group(2), m.group(3)
    parts = [' '.join(key)]
    for g in (x, y):
        if lang == 'wo':
            parts.append(', '.join(DIGITS_WO[int(c)] for c in g))
        elif len(g) == 4:
            parts.append(f'{fr_pair(g[:2])}, {fr_pair(g[2:])}')
        else:
            parts.append(f'{_FR[int(g[0])]}, {fr_pair(g[1:3])}, {fr_pair(g[3:])}')
    return ' | '.join(parts)


# ---------------------------------------------------------------- place words (lieux)
def in_blocks(lieu, number):
    return any(lo <= number <= hi for lo, hi in lieu['blocks'])


class Lieux:
    """The place-word inventory (model/lieux.json): per zone, an index, a name,
    aliases, a position, and its name family: the family id, the number length
    shared by every lieu of the name, and the lieu's block(s) of the name's
    national range (SPEC 3.3), all frozen at first issue."""

    def __init__(self, model=MODEL, items=None):
        p = os.path.join(model, 'lieux.json')
        if items is None:
            items = _load_json(p)['lieux'] if os.path.exists(p) else []
        self.items = items
        self.by_zone = {}
        self.families = {}   # name key -> {'id', 'digits', 'lieux': [...]}
        self.names = {}      # name key of a name or alias -> set of family keys
        for it in self.items:
            self._index(it)

    def _index(self, it):
        self.by_zone.setdefault(it['zone'], {})[it['index']] = it
        f = self.families.setdefault(it['nameKey'], {'id': it['family'], 'digits': it['digits'], 'lieux': []})
        f['lieux'].append(it)
        for nm in [it['placeWord']] + it.get('aliases', []):
            self.names.setdefault(name_key(nm), set()).add(it['nameKey'])

    def get(self, zone, index):
        return self.by_zone[zone][index]

    def owner(self, key, number):
        """The one lieu of name family `key` whose block holds `number`, or None."""
        for it in self.families.get(key, {}).get('lieux', ()):
            if in_blocks(it, number):
                return it
        return None

    def spare_top(self, key):
        f = self.families[key]
        return max(b[1] for it in f['lieux'] for b in it['blocks'])

    def add_block(self, lieu, size=None):
        """Give a lieu one more block from its name's spare space (SPEC 3.3.5):
        when a new same-named lieu appears, or a lieu's own block is used up.
        Existing blocks never move. Returns the block, or None when the name's
        range is full (a new lieu then needs a qualifier)."""
        f = self.families[lieu['nameKey']]
        d = f['digits']
        size = size or block_grain(d)
        top = self.spare_top(lieu['nameKey'])
        if top + size > 10 ** d - 1:
            return None
        b = [top + 1, top + size]
        lieu['blocks'].append(b)
        return b

    def add_lieu(self, it):
        """A lieu created after first issue (curation, Extension): it joins its
        name's family and gets a block from the spare space, or starts a new
        family with the next family id."""
        if not plate_ok(it.get('placeWord') or it['name']) and not it.get('needsCouncilChoice'):
            raise ValueError(f"plate name {it.get('placeWord') or it['name']!r} is over 12 characters or 2 words")
        it.update(placeWord=it.get('placeWord') or it['name'], blocks=[])
        it['nameKey'] = name_key(it['placeWord'])
        self.by_zone.setdefault(it['zone'], {})[it['index']] = it
        self.items.append(it)
        if it['nameKey'] in self.families:
            f = self.families[it['nameKey']]
            it['family'], it['digits'] = f['id'], f['digits']
            f['lieux'].append(it)
            if self.add_block(it, block_size(it.get('compounds', 1), f['digits'])) is None:
                raise ValueError(f"no spare room left in {it['placeWord']!r}: the new lieu needs a qualifier (SPEC 3.3.4)")
        else:
            it['family'] = max(f['id'] for f in self.families.values()) + 1
            it['digits'] = it.get('digits') or 3
            it['blocks'] = [[10 ** (it['digits'] - 1), 10 ** (it['digits'] - 1) + block_size(it.get('compounds', 1), it['digits']) - 1]]
            self.families[it['nameKey']] = {'id': it['family'], 'digits': it['digits'], 'lieux': [it]}
        for nm in [it['placeWord']] + it.get('aliases', []):
            self.names.setdefault(name_key(nm), set()).add(it['nameKey'])
        return it

    def nearest(self, zone, e, n):
        """SPEC 3.2: nearest quartier/village within 2.5 km, else town within 10 km, else nearest."""
        cands = list(self.by_zone.get(zone, {}).values())
        for kinds, lim in (({'neighbourhood', 'suburb', 'village', 'locality', 'extension'}, 2500),
                           ({'town'}, 10000), (None, 1e12)):
            pool = [(math.hypot(c['e'] - e, c['n'] - n), c['index'], c) for c in cands
                    if (kinds is None or c['kind'] in kinds)]
            pool = [x for x in pool if x[0] <= lim]
            if pool:
                return min(pool)[2]
        return None

    def add_extension(self, parent):
        """When a name's whole national range is used up, a full lieu continues as
        '<name> Extension' (SPEC 7.4): a new name, so a new family with its own
        national range; new index in the zone, same number length."""
        zl = self.by_zone[parent['zone']]
        it = {k: v for k, v in parent.items() if k not in ('blocks', 'family', 'nameKey')}
        plate = f"{parent['placeWord']} Extension"
        it.update(index=max(zl) + 1, name=plate, placeWord=plate,
                  officialName=f"{parent.get('officialName', parent['placeWord'])} Extension",
                  kind='extension', coverage=parent.get('coverage', 'nways'), aliases=[],
                  source=f"extension-of:{parent['index']}", needsCouncilChoice=False,
                  compounds=(parent['blocks'][0][1] - parent['blocks'][0][0] + 1) // HEADROOM)
        for k in ('plateCandidates', 'plateReason', 'plateSource', 'aliasesDropped'):
            it.pop(k, None)
        if not plate_ok(plate):
            # 'Darou Salam Extension' is over 12 characters: provisional, the commune names it (SPEC 3.2.1)
            it.update(plateRule='council', needsCouncilChoice=True, plateCandidates=[plate],
                      plateReason='an extension whose name is over the limit: the commune chooses its plate name')
        else:
            it['plateRule'] = 'as-is'
        return self.add_lieu(it)


def address_forms(zones, lieu, number, structure=None, unit=None):
    z = zones.by_key[lieu['zone']]
    zname = z['name'].split(' (')[0]  # 'Touba-Mbacké (arr. de Ndame)' -> 'Touba-Mbacké' on plates
    chk = address_check(lieu['family'], number)
    place = lieu['placeWord']
    sub = '' if structure is None else f'·{structure}' + ('' if unit is None else f'.{unit}')
    return {
        'officialName': lieu.get('officialName', lieu['name']),   # small print on cards and plates, never required
        'remembered': f'{place} {group_number(number) if len(str(number)) == 5 else number}',
        # Plates and forms carry the name, number and zone only; the check letter
        # lives in the canonical form, for machines.
        'written': f"{place.upper()} {group_number(number)} · {zname.upper()}",
        'canonical': f"SN-{z['key']}-{lieu['index']:04d}-{number}-{chk}{sub}",
        'spokenFr': f"{place}, {say_number(number)}",
        'spokenWo': f"{place}, {say_number(number, 'wo')}",
    }


def shown_address(zones, lieu, number, official=None, ann=None):
    """What the app shows for a compound (SPEC 3.6, the coverage mask).

    official: the government address as written (e.g. '120 Rue PE-44, Point E'
    from the municipal street-addressing data or a confirmed plate); ann: the
    ANN address once the ANN covers the area. Government data always wins; the
    N-Ways address is proposed only where nothing official exists, and stays an
    alias that resolves to the official address."""
    forms = address_forms(zones, lieu, number)
    if ann:
        return {'shown': ann, 'source': 'ANN', 'nwaysAlias': forms['canonical'], 'plate': None}
    if official:
        return {'shown': official, 'source': 'government (municipal addressing)', 'nwaysAlias': forms['canonical'],
                'plate': None}
    if lieu.get('coverage', 'nways') != 'nways':
        # official area, official address not yet obtained for this door
        return {'shown': forms['remembered'], 'source': 'N-Ways (temporary, until the official address is confirmed)',
                'nwaysAlias': forms['canonical'], 'plate': None}
    return {'shown': forms['remembered'], 'source': 'N-Ways', 'nwaysAlias': forms['canonical'],
            'plate': forms['written']}


def find(text, zones, lieux):
    """Resolve a remembered or written address ('Ouakam 2512', 'HLM 5 6095',
    'DAROU KHOUDOSS 45 128 · TOUBA-MBACKÉ') with no context: no zone, no
    position. The name gives its national family, the family gives the number
    length, and the number falls in exactly one lieu's block (SPEC 3.3).
    A zone name, or a check letter copied from a machine form, is only checked. Returns a list of
    candidates (zone, lieu, number); it has one entry, or none for an address
    that does not exist (several only if an alias joins two families)."""
    t = text.replace('·', ',')
    parts = [p.strip() for p in t.split(',') if p.strip()]
    zone_name = None
    chk = None
    if len(parts) >= 2 and len(parts[-1]) == 1 and parts[-1].isalpha():
        chk = parts.pop().upper()
    if len(parts) >= 2:
        zone_name = fold(parts.pop())
    head = parts[0].split() if parts else []
    if len(head) >= 2 and len(head[-1]) == 1 and head[-1].isalpha() and head[-2].isdigit():
        chk = head.pop().upper()
    digits = ''
    while head and head[-1].isdigit():
        digits = head.pop() + digits
    if not (head and digits):
        return []
    zk = None
    if zone_name:
        keyed = {fold(z['name']): k for k, z in zones.by_key.items()}
        keyed.update({fold(z['name'].split(' (')[0]): k for k, z in zones.by_key.items()})
        keyed.update({fold(k): k for k in zones.by_key})
        zk = keyed.get(zone_name) or next((k for nm, k in keyed.items() if nm.startswith(zone_name)), None)
    out = []
    for fk in sorted(lieux.names.get(name_key(' '.join(head)), ())):
        d = lieux.families[fk]['digits']
        if len(digits) < d or digits[-d] == '0':
            continue
        number, extra = int(digits[-d:]), digits[:-d]
        lieu = lieux.owner(fk, number)
        if lieu is None:
            continue
        if extra and extra != name_numeral(lieu['placeWord']):
            continue                     # 'HLM 5 6095' must be HLM 5's block, not HLM 3's
        if zk and lieu['zone'] != zk:
            continue                     # the zone said does not match: a wrong address
        if chk and address_check(lieu['family'], number) != chk:
            continue
        out.append((lieu['zone'], lieu, number))
    return out


# ---------------------------------------------------------------- Hilbert order
def hilbert_d(order, x, y):
    """Index of cell (x, y) on a Hilbert curve covering 2^order x 2^order cells."""
    d, s = 0, 1 << (order - 1)
    while s > 0:
        rx = 1 if x & s else 0
        ry = 1 if y & s else 0
        d += s * s * ((3 * rx) ^ ry)
        if ry == 0:
            if rx == 1:
                x, y = s - 1 - x, s - 1 - y
            x, y = y, x
        s >>= 1
    return d


def hilbert_key(zone, e, n, order=16):
    side = zone['frameMetres'] / (1 << order)
    x = min((1 << order) - 1, max(0, int((e - zone['originE']) / side)))
    y = min((1 << order) - 1, max(0, int((n - zone['originN']) / side)))
    return hilbert_d(order, x, y)


# ---------------------------------------------------------------- building profile
# Use classes (SPEC.md section 6). OSM building=* values first, then
# amenity/shop/office/tourism/religion tags, then N-Ways places inside the
# footprint, then shape and height. Each rule gives a confidence.
OSM_BUILDING = {
    'house': 'res.maison', 'detached': 'res.maison', 'semidetached_house': 'res.maison', 'bungalow': 'res.maison',
    'residential': 'res.maison', 'terrace': 'res.maison', 'apartments': 'res.immeuble', 'dormitory': 'res.immeuble',
    'hut': 'res.case', 'farm': 'res.concession',
    'commercial': 'com.bureau', 'office': 'com.bureau', 'retail': 'com.boutique', 'kiosk': 'com.boutique',
    'supermarket': 'com.boutique', 'warehouse': 'com.entrepot', 'storage_tank': 'ind.usine',
    'industrial': 'ind.usine', 'factory': 'ind.usine', 'manufacture': 'ind.usine',
    'hotel': 'hot.hotel', 'government': 'gov.admin', 'public': 'gov.admin', 'civic': 'gov.admin',
    'school': 'edu.ecole', 'kindergarten': 'edu.ecole', 'university': 'edu.universite', 'college': 'edu.universite',
    'hospital': 'san.hopital', 'clinic': 'san.centre', 'mosque': 'rel.mosquee', 'church': 'rel.eglise',
    'cathedral': 'rel.eglise', 'chapel': 'rel.eglise', 'religious': 'rel.mosquee', 'shrine': 'rel.mausolee',
    'train_station': 'tra.gare', 'transportation': 'tra.gare', 'hangar': 'tra.gare',
    'barn': 'agr.magasin', 'farm_auxiliary': 'agr.magasin', 'granary': 'agr.grenier', 'greenhouse': 'agr.ferme',
    'stable': 'agr.ferme', 'cowshed': 'agr.ferme', 'construction': 'chantier', 'ruins': 'ruine',
    'market': 'com.marche', 'service': 'ind.usine', 'garage': 'res.annexe', 'garages': 'com.entrepot',
    'toilets': 'res.annexe', 'shed': 'res.annexe', 'roof': 'com.marche', 'sports_hall': 'edu.ecole',
    'stadium': 'gov.admin', 'fire_station': 'gov.admin', 'military': 'gov.admin',
}
OSM_AMENITY = {
    'townhall': 'gov.admin', 'courthouse': 'gov.admin', 'police': 'gov.admin', 'post_office': 'gov.admin',
    'prison': 'gov.admin', 'fire_station': 'gov.admin', 'school': 'edu.ecole', 'kindergarten': 'edu.ecole',
    'university': 'edu.universite', 'college': 'edu.universite', 'hospital': 'san.hopital', 'clinic': 'san.centre',
    'doctors': 'san.centre', 'pharmacy': 'san.pharmacie', 'place_of_worship': 'rel.mosquee',
    'marketplace': 'com.marche', 'bank': 'com.bureau', 'fuel': 'com.station', 'restaurant': 'hot.restaurant',
    'fast_food': 'hot.restaurant', 'cafe': 'hot.restaurant', 'bus_station': 'tra.gare', 'ferry_terminal': 'tra.gare',
}
PLACES = {  # N-Ways places categories
    'shop': 'com.boutique', 'supermarket': 'com.boutique', 'phones': 'com.boutique', 'salon': 'com.boutique',
    'pos': 'com.boutique', 'office': 'com.bureau', 'bank': 'com.bureau', 'school': 'edu.ecole',
    'hospital': 'san.centre', 'pharmacy': 'san.pharmacie', 'food': 'hot.restaurant', 'fastfood': 'hot.restaurant',
    'cafe': 'hot.restaurant', 'bar': 'hot.restaurant', 'hotel': 'hot.hotel', 'mosque': 'rel.mosquee',
    'church': 'rel.eglise', 'market': 'com.marche', 'petrol': 'com.station', 'police': 'gov.admin',
    'motorpark': 'tra.gare', 'mechanic': 'com.atelier', 'vulcanizer': 'com.atelier', 'carwash': 'com.atelier',
}
GROUPS = {  # class -> top-level group used in statistics
    'res': 'residential', 'com': 'commercial', 'hot': 'hospitality', 'gov': 'government', 'edu': 'education',
    'san': 'health', 'rel': 'religious', 'ind': 'industrial', 'tra': 'transport', 'pec': 'fishing',
    'agr': 'agricultural', 'mix': 'mixed-use', 'chantier': 'under construction', 'ruine': 'ruin',
    'inconnu': 'unknown',
}
FLOOR_M = 3.0  # storey height used to turn a height into floors (R+n = floors - 1)


def num(v):
    try:
        return float(str(v).replace(',', '.').split(';')[0].strip().rstrip('m').strip())
    except (TypeError, ValueError):
        return None


def size_profile(area, perimeter, h_ml, osm_height, osm_levels, h_measured=False):
    """Height, floors and floor area, with the source of each.

    Only measured heights count: OSM height, OSM building:levels, or a
    machine-learned height flagged as measured (h_measured). The footprint
    datasets used for Senegal carry no measured height (a value present there
    is a rendering filler, not a measurement), so it is ignored: the height is
    unknown and floors default to 1 with source 'default' (low confidence).
    """
    lv, hh = num(osm_levels), num(osm_height)
    if hh and 2 <= hh <= 250:
        height, hsrc = hh, 'osm:height'
    elif lv and 1 <= lv <= 60:
        height, hsrc = lv * FLOOR_M, 'osm:building:levels'
    elif h_measured and h_ml and h_ml > 0:
        height, hsrc = h_ml, 'ml:height'
    else:
        height, hsrc = None, None
    if lv and 1 <= lv <= 60:
        floors, fsrc = int(lv), 'osm:building:levels'
    elif height:
        floors, fsrc = max(1, round(height / FLOOR_M)), f'derived:{hsrc}'
    else:
        floors, fsrc = 1, 'default'
    return {'footprintM2': round(area, 1), 'perimeterM': round(perimeter, 1),
            'heightM': round(height, 1) if height else None, 'heightSource': hsrc,
            'floors': floors, 'floorsSource': fsrc, 'rPlus': f'R+{floors - 1}' if floors > 1 else 'RDC',
            'floorAreaM2': round(area * floors, 1), 'floorAreaIsEstimate': fsrc == 'default'}


def classify(t, area, floors, poi_cat=None, rural=False, in_multi=False, satellite=False):
    """(class, confidence, evidence) for one structure. t: dict of OSM tags."""
    b = (t.get('building') or '').lower()
    if b in ('construction',):
        return 'chantier', 0.9, 'osm:building=construction'
    if b in ('ruins',):
        return 'ruine', 0.9, 'osm:building=ruins'
    am = (t.get('amenity') or '').lower()
    if am == 'place_of_worship':
        rel = (t.get('religion') or '').lower()
        return ('rel.eglise' if rel == 'christian' else 'rel.mosquee'), 0.9, 'osm:amenity=place_of_worship'
    if am in OSM_AMENITY:
        return OSM_AMENITY[am], 0.9, f'osm:amenity={am}'
    if t.get('shop'):
        return ('mix.immeuble' if floors >= 3 else 'com.boutique'), 0.85, f'osm:shop={t["shop"]}'
    if t.get('office') or t.get('government'):
        if t.get('government') or (t.get('office') or '') == 'government':
            return 'gov.admin', 0.9, 'osm:office=government'
        return 'com.bureau', 0.85, f'osm:office={t.get("office")}'
    if t.get('tourism') in ('hotel', 'guest_house', 'motel', 'hostel', 'chalet', 'apartment'):
        return 'hot.hotel', 0.9, f'osm:tourism={t["tourism"]}'
    if t.get('healthcare'):
        return 'san.centre', 0.85, f'osm:healthcare={t["healthcare"]}'
    if t.get('industrial') or t.get('craft') == 'fishing' or t.get('man_made') == 'works':
        if (t.get('industrial') or '') in ('fishery', 'fish_processing'):
            return 'pec.quai', 0.8, 'osm:industrial=fishery'
        return 'ind.usine', 0.8, 'osm:industrial'
    if b in OSM_BUILDING:
        c = OSM_BUILDING[b]
        if c == 'res.maison' and floors >= 3:
            c = 'res.immeuble'
        return c, 0.85, f'osm:building={b}'
    if poi_cat in PLACES:
        c = PLACES[poi_cat]
        if c in ('com.boutique', 'hot.restaurant', 'com.atelier') and floors >= 3:
            return 'mix.immeuble', 0.6, f'places:{poi_cat}+floors'
        return c, 0.7, f'places:{poi_cat}'
    # Shape and height (no tag, no place).
    if satellite:
        return 'res.annexe', 0.4, 'shape:satellite'
    if floors >= 3 and area >= 60:
        return 'res.immeuble', 0.45, 'shape:floors>=3'
    if area < 25 and rural:
        return 'res.case', 0.5, 'shape:small+rural'
    if area >= 1500 and floors <= 2:
        return 'com.entrepot', 0.3, 'shape:large-low'
    if in_multi:
        return 'res.concession', 0.45, 'shape:multi-structure compound'
    if 25 <= area < 600:
        return 'res.maison', 0.45, 'shape:house-size'
    return 'inconnu', 0.2, 'none'


# ---------------------------------------------------------------- compounds
SATELLITE_M2 = 30.0       # kitchen, toilet, gatehouse, boys' quarters, store
SAT_GAP_URBAN = 4.0       # metres between equivalent circles
SAT_GAP_RURAL = 8.0
CASE_M2 = 120.0           # rural concession structures (cases, small houses)
CASE_GAP = 6.0
CASE_MAX = 30             # structures in one rural concession
URBAN_TILE = 250.0        # metres
URBAN_MIN = 100           # structures per 250 m tile (1,600 per km2) = urban fabric


def _ring_area(ring):
    return abs(sum(ring[i][0] * ring[i - 1][1] - ring[i - 1][0] * ring[i][1] for i in range(len(ring)))) / 2


def radius(a):
    return math.sqrt(max(a, 1.0) / math.pi)


def group_compounds(structs, enclosures=()):
    """Group structures into compounds (SPEC.md section 5).

    structs: list of dicts with e, n (UTM metres), area (m2), id.
    enclosures: list of (enclosure id, kind, [(e, n) ring]) - walls, fences,
    N-Ways sites; every structure whose centre lies inside one is that
    compound's. Returns list of compounds: dict(members=[ids], rule, conf,
    urban). Deterministic: input order does not matter.
    """
    structs = sorted(structs, key=lambda s: (s['e'], s['n'], s['id']))
    idx = {s['id']: i for i, s in enumerate(structs)}
    tiles = {}
    for s in structs:
        k = (int(s['e'] // URBAN_TILE), int(s['n'] // URBAN_TILE))
        tiles[k] = tiles.get(k, 0) + 1
    for s in structs:  # a precomputed tileCount (whole-zone density) wins over the local count
        s['urban'] = s.get('tileCount', tiles[(int(s['e'] // URBAN_TILE), int(s['n'] // URBAN_TILE))]) >= URBAN_MIN
    parent = list(range(len(structs)))
    size = [1] * len(structs)
    rule = ['single'] * len(structs)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        a, b = find(i), find(j)
        if a != b:
            lo, hi = min(a, b), max(a, b)
            parent[hi] = lo
            size[lo] += size[hi]

    # spatial hash for neighbour search
    G = 40.0
    grid = {}
    for i, s in enumerate(structs):
        grid.setdefault((int(s['e'] // G), int(s['n'] // G)), []).append(i)
    # R0 enclosures (smallest first, so a house wall inside an estate wins)
    enclosed = set()
    encl = sorted(enclosures, key=lambda x: _ring_area(x[2]))
    for _, _, ring in encl:
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        cand = [i for gx in range(int(min(xs) // G), int(max(xs) // G) + 1)
                for gy in range(int(min(ys) // G), int(max(ys) // G) + 1) for i in grid.get((gx, gy), ())]
        inside = sorted(i for i in cand if i not in enclosed and Zones._in_ring(structs[i]['e'], structs[i]['n'], ring))
        for i in inside[1:]:
            union(inside[0], i)
        for i in inside:
            rule[i] = 'enclosure'
            enclosed.add(i)

    def near(i):
        s = structs[i]
        gx, gy = int(s['e'] // G), int(s['n'] // G)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in grid.get((gx + dx, gy + dy), ()):
                    if j != i:
                        yield j

    def gap(i, j):
        a, b = structs[i], structs[j]
        return math.hypot(a['e'] - b['e'], a['n'] - b['n']) - radius(a['area']) - radius(b['area'])

    # R1 satellites: a small structure joins the nearest main structure
    for i, s in enumerate(structs):
        if i in enclosed or s['area'] >= SATELLITE_M2:
            continue
        lim = SAT_GAP_URBAN if s['urban'] else SAT_GAP_RURAL
        best = min(((gap(i, j), j) for j in near(i)
                    if structs[j]['area'] >= SATELLITE_M2 and j not in enclosed), default=None)
        if best and best[0] <= lim:
            union(i, best[1])
            rule[i] = 'satellite'
            s['satellite'] = True
    # R2 rural concessions: small structures single-linked in rural fabric
    for i, s in enumerate(structs):
        if i in enclosed or s['urban'] or s['area'] >= CASE_M2:
            continue
        for j in near(i):
            t = structs[j]
            if j in enclosed or t['urban'] or t['area'] >= CASE_M2 or j < i:
                continue
            if gap(i, j) <= CASE_GAP:
                a, b = find(i), find(j)
                if a != b and size[a] + size[b] <= CASE_MAX:
                    union(a, b)
                    for k in (i, j):
                        if rule[k] == 'single':
                            rule[k] = 'rural-concession'
    comps = {}
    for i in range(len(structs)):
        comps.setdefault(find(i), []).append(i)
    out = []
    for root, members in comps.items():
        rules = {rule[i] for i in members}
        r = 'enclosure' if 'enclosure' in rules else 'rural-concession' if 'rural-concession' in rules \
            else 'satellite' if 'satellite' in rules else 'single'
        conf = {'enclosure': 0.9, 'single': 0.7, 'satellite': 0.6, 'rural-concession': 0.5}[r]
        # main structure first (largest), then the rest by distance from it
        members.sort(key=lambda i: (-structs[i]['area'], structs[i]['id']))
        m0 = structs[members[0]]
        members[1:] = sorted(members[1:], key=lambda i: (math.hypot(structs[i]['e'] - m0['e'],
                                                                    structs[i]['n'] - m0['n']), structs[i]['id']))
        tot = sum(structs[i]['area'] for i in members)
        ce = sum(structs[i]['e'] * structs[i]['area'] for i in members) / tot
        cn = sum(structs[i]['n'] * structs[i]['area'] for i in members) / tot
        ext = max(math.hypot(structs[i]['e'] - ce, structs[i]['n'] - cn) + radius(structs[i]['area']) for i in members)
        out.append({'members': [structs[i]['id'] for i in members], 'rule': r, 'confidence': conf,
                    'urban': m0['urban'], 'e': ce, 'n': cn, 'extentM': round(ext, 1)})
    return out


# ---------------------------------------------------------------- registry
HEADROOM = 3  # numbers for three times today's compounds (urban growth ~3.7 %/yr -> about 30 years)


def number_lieu(zone, lieu, compounds):
    """First issue in one lieu: Hilbert order, numbers spread evenly over the lieu's block."""
    lo, hi = lieu['blocks'][0]   # the lieu's block of its name's national range (SPEC 3.3)
    span = hi - lo + 1
    comps = sorted(compounds, key=lambda c: (hilbert_key(zone, c['e'], c['n']), c['e'], c['n']))
    nb = len(comps)
    if HEADROOM * nb > span:
        raise ValueError(f"lieu {lieu['placeWord']}: {nb} compounds do not fit its block {lo}-{hi} with headroom")
    for i, c in enumerate(comps):
        c['number'] = lo + int((i + 0.5) * span / nb)
    return comps


def insert_in_lieu(zone, lieu, issued, e, n, lieux=None):
    """A new compound after first issue (SPEC 7.4): the free number midway
    between its Hilbert neighbours in the lieu's first block; else the lowest
    free number of the lieu's further blocks; else a new block from the name's
    spare space (needs `lieux`); else None (the caller then numbers it in
    '<lieu> Extension'). Issued numbers and blocks never change."""
    import bisect
    lo_r, hi_r = lieu['blocks'][0]
    used = {c['number'] for c in issued}
    first = [c for c in issued if lo_r <= c['number'] <= hi_r]
    h = hilbert_key(zone, e, n)
    seq = sorted(first, key=lambda c: (hilbert_key(zone, c['e'], c['n']), c['number']))
    keys = [hilbert_key(zone, c['e'], c['n']) for c in seq]
    k = bisect.bisect_right(keys, h)
    a = seq[k - 1]['number'] if k > 0 else lo_r - 1
    b = seq[k]['number'] if k < len(seq) else hi_r + 1
    if b - a >= 2:
        mid = (a + b) // 2
        if mid not in used and lo_r <= mid <= hi_r:
            return mid
    for lo, hi in lieu['blocks'][1:]:
        free = next((x for x in range(lo, hi + 1) if x not in used), None)
        if free is not None:
            return free
    if lieux is not None:
        blk = lieux.add_block(lieu)
        if blk:
            return blk[0]
    return None


def reserve_provisional(zones, lieux, issued_by_lieu, gate_lat, gate_lon, outline_m2=None):
    """'Add my home' (SPEC section 8): the registry (the single issuer) reserves
    the next number for a new compound whose gate is at (gate_lat, gate_lon).
    issued_by_lieu: {(zone, lieu index): [issued compounds with e, n, number, extentM]}."""
    key = zones.lookup(gate_lat, gate_lon)
    if key is None:
        return {'status': 'refused', 'reason': 'outside Senegal'}
    z = zones.by_key[key]
    e, n = utm_forward(gate_lat, gate_lon)
    for comps in issued_by_lieu.values():
        for c in comps:
            if math.hypot(c['e'] - e, c['n'] - n) < c.get('extentM', 0):
                return {'status': 'flagged', 'reason': f"gate inside existing compound {c.get('canonical', '')}".strip()}
    if outline_m2 is not None and not (20 <= outline_m2 <= 20000):
        return {'status': 'flagged', 'reason': 'implausible plot size'}
    lieu = lieux.nearest(key, e, n)
    if lieu is None:
        return {'status': 'refused', 'reason': f'no place word in zone {key}'}
    issued = issued_by_lieu.get((key, lieu['index']), [])
    num_ = insert_in_lieu(z, lieu, issued, e, n, lieux)
    if num_ is None:
        ext = next((x for x in lieux.by_zone[key].values() if x['source'] == f"extension-of:{lieu['index']}"), None) \
            or lieux.add_extension(lieu)
        lieu = ext
        num_ = insert_in_lieu(z, lieu, issued_by_lieu.get((key, lieu['index']), []), e, n, lieux)
    out = {'status': 'provisional', 'number': num_, **address_forms(zones, lieu, num_),
           'coverage': lieu.get('coverage', 'nways'), 'spotCode': encode_spot(gate_lat, gate_lon, zones)}
    if out['coverage'] != 'nways':
        # government addresses first (SPEC 3.6): no N-Ways plate; the official number comes from the commune
        out.update(status='provisional-alias', written=None,
                   note='official addressing area: the N-Ways address is only an alias until the commune gives the official number')
    return out


# ---------------------------------------------------------------- sample registries
def load_sample(path):
    structs = []
    with open(path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        e, n = utm_forward(float(r['lat']), float(r['lon']))
        st = {'id': r['id'], 'e': e, 'n': n, 'area': float(r['area_m2']), 'row': r}
        if r.get('tile_count'):
            st['tileCount'] = int(r['tile_count'])
        structs.append(st)
    return structs


def sample_registry(path, zones, lieux):
    """Group a sample's footprints, assign each compound its lieu, number it
    within its lieu (numbers from this sample alone: the national first issue
    numbers all of a lieu's compounds at once), and profile its structures."""
    structs = load_sample(path)
    by_id = {s['id']: s for s in structs}
    comps = group_compounds(structs)
    groups = {}
    for c in comps:
        lat, lon = utm_inverse(c['e'], c['n'])
        key = zones.lookup(lat, lon)
        lieu = lieux.nearest(key, c['e'], c['n'])
        c['zone'] = key
        groups.setdefault((key, lieu['index']), (lieu, []))[1].append(c)
    out = []
    for (key, li), (lieu, cs) in sorted(groups.items()):
        for c in number_lieu(zones.by_key[key], lieu, cs):
            prof = []
            for k, sid in enumerate(c['members'], 1):
                s = by_id[sid]
                r = s['row']
                sz = size_profile(s['area'], float(r['perimeter_m']), None, r.get('height'), r.get('building_levels'))
                tags = {t: r.get(t) for t in ('building', 'amenity', 'shop', 'office', 'tourism', 'religion', 'craft',
                                              'industrial', 'man_made', 'healthcare', 'government') if r.get(t)}
                cls, conf, ev = classify(tags, s['area'], sz['floors'], r.get('poi_cat') or None,
                                         rural=not s['urban'], in_multi=len(c['members']) > 1,
                                         satellite=s.get('satellite', False))
                prof.append({'structure': k, 'id': sid, 'class': cls, 'confidence': conf, 'evidence': ev, **sz})
            forms = address_forms(zones, lieu, c['number'])
            shown = shown_address(zones, lieu, c['number'])
            out.append({**forms, 'coverage': lieu.get('coverage', 'nways'), 'shown': shown['shown'],
                        'shownSource': shown['source'], 'zone': key, 'lieu': lieu['index'], 'number': c['number'],
                        'e': round(c['e'], 1),
                        'n': round(c['n'], 1), 'extentM': c['extentM'], 'rule': c['rule'],
                        'groupingConfidence': c['confidence'], 'structures': prof})
    return out


# ---------------------------------------------------------------- vectors
POINTS = [  # (label, lat, lon) - public places, positions from OpenStreetMap or hand-placed (approx.)
    ("Place de l'Indépendance, Dakar-Plateau", 14.66810, -17.43170),
    ('Grande Mosquée de Touba', 14.86130, -15.87700),
    ('Pont Faidherbe, Saint-Louis', 16.02470, -16.50440),
    ('Gare routière de Ziguinchor (approx.)', 12.56500, -16.27300),
    ('Marché Sandaga, Dakar', 14.67190, -17.43390),
    ('Sphères ministérielles, Diamniadio (approx.)', 14.71630, -17.19800),
    ('Saly Portudal (beach front, approx.)', 14.44700, -17.01200),
    ('Kédougou town centre (approx.)', 12.55600, -12.17500),
    ('Guédiawaye, Golf Sud (approx.)', 14.77700, -17.40200),
]
SAMPLES = ['dakar-medina.csv', 'touba.csv', 'bambey-village.csv']


def vectors(zones, lieux):
    spot = []
    for label, lat, lon in POINTS:
        code = encode_spot(lat, lon, zones)
        dlat, dlon, cell = decode_spot(code, zones)
        e0, n0 = utm_forward(lat, lon)
        e1, n1 = utm_forward(dlat, dlon)
        spot.append({'place': label, 'lat': lat, 'lon': lon, 'code': code, 'decoded': [round(dlat, 6), round(dlon, 6)],
                     'cellMetres': cell, 'errorMetres': round(math.hypot(e1 - e0, n1 - n0), 2),
                     'spokenFr': spoken_spot(code), 'spokenWo': spoken_spot(code, 'wo')})
    fid = {nm: lieux.families[name_key(nm)]['id'] for nm in ('Ouakam', 'Médina')} if lieux.items else {'Ouakam': 1, 'Médina': 2}
    checks = [{'name': nm_, 'family': fid.get(nm_, 0), 'number': nm, 'payload': f"{fid.get(nm_, 0):05d}{nm:05d}",
               'letter': address_check(fid.get(nm_, 0), nm)}
              for nm_, nm in (('Ouakam', 2512), ('Médina', 12150), ('Médina', 23150), ('-', 100))]
    numbers = [{'number': nm, 'written': group_number(nm), 'spokenFr': say_number(nm), 'spokenWo': say_number(nm, 'wo')}
               for nm in (120, 4512, 9071, 45128, 10307)]
    samples = {}
    amh = {}
    for f in SAMPLES:
        path = os.path.join(HERE, 'samples', f)
        if not os.path.exists(path) or not lieux.items:
            continue
        reg = sample_registry(path, zones, lieux)
        multi = sum(1 for c in reg if len(c['structures']) > 1)
        samples[f] = {'footprints': sum(len(c['structures']) for c in reg), 'compounds': len(reg),
                      'multiStructureCompounds': multi,
                      'first': [{k: c[k] for k in ('remembered', 'written', 'canonical', 'coverage', 'shownSource', 'rule')} |
                                {'structures': len(c['structures']), 'classes': [x['class'] for x in c['structures']]}
                                for c in reg[:5]]}
        issued = {}
        for c in reg:
            issued.setdefault((c['zone'], c['lieu']), []).append(c)
        c0 = reg[len(reg) // 2]
        lat_in, lon_in = utm_inverse(c0['e'] + 0.5, c0['n'] + 0.5)
        far = max(reg, key=lambda c: c['e'])
        lat_new, lon_new = utm_inverse(far['e'] + far['extentM'] + 40, far['n'])
        amh[f] = {'gateInsideExisting': {'gate': [round(lat_in, 6), round(lon_in, 6)],
                                         **reserve_provisional(zones, lieux, issued, lat_in, lon_in, 300)},
                  'newHome': {'gate': [round(lat_new, 6), round(lon_new, 6)],
                              **reserve_provisional(zones, lieux, issued, lat_new, lon_new, 300)}}
    return {'spot': spot, 'addressCheck': checks, 'numbers': numbers, 'sameName': same_name_vectors(zones, lieux),
            'plateNames': plate_vectors(zones, lieux), 'samples': samples, 'addMyHome': amh}


PLATE_LONG = [  # (zone, lieu index): a long official name and its plate name (SPEC 3.2.1)
    ('DKR', 94),    # S.I.C.A.P. Liberté Six -> Liberté 6 (scheme label dropped, numeral in digits)
    ('MBR', 347),   # Saly Portudal -> Saly (documented short form)
    ('KBM', 319),   # Mbenguène Diawar -> Diawar (most distinctive word)
    ('DKR', 81),    # Parcelles Assainies -> Parcelles (provisional: the commune confirms)
]
PLATE_COLLIDE = [  # pairs whose plate names are the same only after shortening: one range, two places
    (('DAG', 35), ('KBM', 319)),    # Diawar / Mbenguène Diawar -> Diawar
    (('BKL', 70), ('DAG', 102)),    # Gabou / Massara Gabou -> Gabou
]


def plate_vectors(zones, lieux):
    """SPEC 3.2.1 / 11: (a) a long official name gives a short plate name, and the
    official name typed still decodes to the same compound; (b) two lieux whose
    plate names collide only after shortening share one range and decode, from
    the plate name and the number alone, to two different places."""
    if not lieux.items:
        return {'long': [], 'collide': []}

    def mid(lieu):
        lo, hi = lieu['blocks'][0]
        return lo + (hi - lo + 1) * 15 // 100

    def dec(text):
        return [f"{z_}/{c['index']}" for z_, c, _ in find(text, zones, lieux)]

    long_ = []
    for zk, li in PLATE_LONG:
        it = lieux.get(zk, li)
        nm = mid(it)
        f = address_forms(zones, it, nm)
        long_.append({'officialName': it['officialName'], 'plateName': it['placeWord'],
                      'plateLength': _P.plate_length(it['placeWord']), 'plateRule': it.get('plateRule'),
                      'needsCouncilChoice': bool(it.get('needsCouncilChoice')), 'source': it.get('plateSource'),
                      'remembered': f['remembered'], 'written': f['written'], 'canonical': f['canonical'],
                      'decodedPlate': dec(f'{it["placeWord"]} {nm}'), 'decodedOfficial': dec(f'{it["officialName"]} {nm}'),
                      'lieu': f'{zk}/{li}'})
    col = []
    for pair in PLATE_COLLIDE:
        rows = []
        for zk, li in pair:
            it = lieux.get(zk, li)
            nm = mid(it)
            f = address_forms(zones, it, nm)
            rows.append({'lieu': f'{zk}/{li}', 'officialName': it['officialName'], 'plateName': it['placeWord'],
                         'family': it['family'], 'digits': it['digits'], 'block': it['blocks'][0],
                         'remembered': f['remembered'], 'decoded': dec(f['remembered'])})
        col.append(rows)
    return {'long': long_, 'collide': col}


SAME_NAME = [  # (name typed, zone, lieu index): same-named lieux in different places, each decoded with no context
    ('Médina', 'DKR', 71), ('Medina', 'ZIG', 155), ('Médina', 'STL', 90),
    ('Pikine', 'DBL', 329), ('Pikine', 'STL', 151), ('Pikine 3', 'STL', 152),
    ('Darou Salam', 'PKN', 10), ('Darou Salam', 'TBA', 54),
    ('Gounas', 'GDW', 6), ('Gounas', 'VEL', 204),   # plate names of 'Médina Gounas' (provisional, SPEC 3.2.1)
    ('HLM 2', 'DKR', 51), ('HLM 5', 'DKR', 54),
]


def same_name_vectors(zones, lieux):
    """SPEC 3.3 / 11: same-named lieux decode to different places from 'name + number'
    alone. For each lieu: its block, a number in it (the block's 15th %), the forms,
    what find() returns with no context, and a one-digit slip that falls in ANOTHER
    same-named lieu's block, rejected by the check letter."""
    out = []
    if not lieux.items:
        return out
    for typed, zk, li in SAME_NAME:
        lieu = lieux.get(zk, li)
        lo, hi = lieu['blocks'][0]
        nm = lo + (hi - lo + 1) * 15 // 100
        forms = address_forms(zones, lieu, nm)
        found = find(f'{typed} {nm}', zones, lieux)
        chk = address_check(lieu['family'], nm)
        slip = None
        s_ = str(nm)
        for pos in range(len(s_)):
            for dgt in '0123456789':
                if dgt == s_[pos] or (pos == 0 and dgt == '0'):
                    continue
                other = int(s_[:pos] + dgt + s_[pos + 1:])
                o = lieux.owner(lieu['nameKey'], other)
                if o is not None and o is not lieu and slip is None:
                    slip = {'typed': f'{typed} {other} {chk}', 'wouldBe': f"{o['zone']}/{o['index']}",
                            'withoutLetter': [f"{z_}/{c['index']}" for z_, c, _ in find(f'{typed} {other}', zones, lieux)],
                            'withLetter': [f"{z_}/{c['index']}" for z_, c, _ in find(f'{typed} {other} {chk}', zones, lieux)]}
        out.append({'typed': f'{typed} {nm}', 'zone': zk, 'zoneName': zones.by_key[zk]['name'], 'lieu': li,
                    'family': lieu['family'], 'digits': lieu['digits'], 'block': [lo, hi],
                    'decoded': [f"{z_}/{c['index']}" for z_, c, _ in found],
                    'remembered': forms['remembered'], 'written': forms['written'], 'canonical': forms['canonical'],
                    'slipIntoOtherLieu': slip})
    return out


def E_same(a, b):
    """Two plate vectors of one shared range: same plate key and family, disjoint blocks."""
    return (name_key(a['plateName']) == name_key(b['plateName']) and a['family'] == b['family']
            and (a['block'][1] < b['block'][0] or b['block'][1] < a['block'][0])
            and name_key(a['officialName']) != name_key(b['officialName']))


def selftest(zones, lieux):
    import random
    rnd = random.Random(221)
    for _ in range(2000):  # 1. UTM round trip
        lat, lon = rnd.uniform(12.3, 16.7), rnd.uniform(-17.6, -11.3)
        la, lo = utm_inverse(*utm_forward(lat, lon))
        assert abs(la - lat) < 1e-9 and abs(lo - lon) < 1e-9
    for _ in range(3000):  # 2. every single substitution and adjacent swap is caught (spot payloads)
        zi = rnd.randrange(46)
        d = ''.join(rnd.choice('0123456789') for _ in range(rnd.choice((8, 9, 10))))
        c = check_letter(zi, d)
        p_ = f'{zi:02d}{d}'
        for k in range(len(p_)):
            for x in '0123456789':
                if x != p_[k]:
                    q = p_[:k] + x + p_[k + 1:]
                    assert check_letter(int(q[:2]), q[2:]) != c
            if k + 1 < len(p_) and p_[k] != p_[k + 1]:
                q = p_[:k] + p_[k + 1] + p_[k] + p_[k + 2:]
                assert check_letter(int(q[:2]), q[2:]) != c
    for label, lat, lon in POINTS:  # 3. spot round trip
        code = encode_spot(lat, lon, zones)
        assert validate(code, zones)[0]
        la, lo, cell = decode_spot(code, zones)
        assert encode_spot(la, lo, zones, key=code[:3]) == code
    z = zones.by_key['DKR']  # 4. numbering and insertion inside a block
    lieu = {'zone': 'DKR', 'index': 0, 'name': 'Test', 'placeWord': 'Test', 'digits': 3, 'kind': 'village',
            'blocks': [[100, 999]]}
    comps = [{'e': z['originE'] + rnd.uniform(0, 3000), 'n': z['originN'] + rnd.uniform(0, 3000)} for _ in range(300)]
    nums = [c['number'] for c in number_lieu(z, lieu, comps)]
    assert len(set(nums)) == 300 and min(nums) >= 100 and max(nums) <= 999
    new = insert_in_lieu(z, lieu, comps, comps[7]['e'] + 1, comps[7]['n'] + 1)
    assert new is None or new not in nums
    # 5. national name ranges (SPEC 3.3): normalisation, lengths, allocation, stability
    for a, b in (('Ouakam', 'Wakam'), ('Mbacké', 'Mbakke'), ('Thiès', 'Thies'), ('Kër Massar', 'Keur Massar'),
                 ('Médina Gounass', 'Medina Gounas'), ('Darou Salam', 'Daru-Salaam'), ('Ndiaye', 'Njaay'),
                 ('Khoudoss', 'Xudoss'), ('HLM 5', 'HLM'), ('Saint-Louis', 'St Louis'), ('Hamdallaye', 'Amdalaye')):
        assert name_key(a) == name_key(b), (a, b)
    assert name_key('Médina') != name_key('Médina Gounass') and name_key('Ouakam') != name_key('Yoff')
    assert family_digits([270]) == 3 and family_digits([271]) == 4 and family_digits([90, 90, 90]) == 3
    assert family_digits([27000]) == 5 and family_digits([27001]) is None
    toy = [{'zone': zk, 'index': i, 'name': nm, 'compounds': c} for zk, i, nm, c in
           (('DKR', 1, 'Médina', 2000), ('ZIG', 5, 'Medina', 150), ('STL', 2, 'Médina', 1000), ('DKR', 2, 'Ouakam', 789))]
    fams = allocate_families(toy)
    med = [it for it in toy if it['nameKey'] == name_key('Médina')]
    assert len({it['digits'] for it in med}) == 1 and len({it['family'] for it in med}) == 1
    spans = sorted(b for it in med for b in it['blocks'])
    assert all(spans[i][1] < spans[i + 1][0] for i in range(len(spans) - 1))          # blocks never overlap
    used = sum(b[1] - b[0] + 1 for b in spans)
    assert used <= allocatable(med[0]['digits'])                                     # >= 10 % spare
    toy2 = [dict(t) for t in toy] + [{'zone': 'KLD', 'index': 9, 'name': 'Médina', 'compounds': 40}]
    allocate_families(toy2, frozen=fams)                                             # stability: frozen blocks kept
    for a, b in zip(toy, toy2):
        assert a['blocks'] == b['blocks'] and a['family'] == b['family']
    assert toy2[-1]['blocks'][0][0] > max(b[1] for b in spans)                        # new lieu from spare space
    n_same = 0
    if lieux.items:  # 6. the real inventory: every name key one family, blocks disjoint, unique decoding
        for key, f in lieux.families.items():
            assert len({it['family'] for it in f['lieux']}) == 1 and len({it['digits'] for it in f['lieux']}) == 1
            bl = sorted(b for it in f['lieux'] for b in it['blocks'])
            assert bl[0][0] >= 10 ** (f['digits'] - 1) and bl[-1][1] <= 10 ** f['digits'] - 1
            assert all(bl[i][1] < bl[i + 1][0] for i in range(len(bl) - 1)), key
        assert len({f['id'] for f in lieux.families.values()}) == len(lieux.families)
        for v in same_name_vectors(zones, lieux):
            assert v['decoded'] == [f"{v['zone']}/{v['lieu']}"], v                     # no context needed
            sl = v['slipIntoOtherLieu']
            if sl:
                # without the letter the slip lands in the other lieu (or is refused because that lieu's
                # name has no / another trailing numeral: 'HLM 2 1185' is not HLM 2); with the letter it is refused
                assert sl['withoutLetter'] in ([sl['wouldBe']], []) and sl['withLetter'] == [], sl
            n_same += 1
        med = lieux.families[name_key('Médina')]
        for it in med['lieux']:  # every one-digit slip from a Médina number into another Médina is caught by the letter
            lo, hi = it['blocks'][0]
            for nm in range(lo, hi + 1, 97):
                chk = address_check(it['family'], nm)
                s_ = str(nm)
                for pos in range(len(s_)):
                    for dgt in '0123456789':
                        if dgt != s_[pos] and not (pos == 0 and dgt == '0'):
                            other = int(s_[:pos] + dgt + s_[pos + 1:])
                            assert address_check(it['family'], other) != chk
    # 7. plate names (SPEC 3.2.1): the limit, and the plate vectors decode as stated
    for good in ('Ouakam', 'Liberté 6', 'Sacré-Cœur', 'HLM 5', 'Point E', 'Grand Médine'):
        assert plate_ok(good), good
    for bad in ('Parcelles Assainies', 'Keur Mbaye Fal', 'Cité Keur Gorgui', 'Diabrikindiong', 'Liberté 6 7'):
        assert not plate_ok(bad), bad
    assert split_numeral('S.I.C.A.P. Liberté Six') == ('S.I.C.A.P. Liberté', '6')
    assert split_numeral('Plan Jaxaay 01') == ('Plan Jaxaay', '1') and split_numeral('Ouakam') == ('Ouakam', '')
    if lieux.items:
        for it in lieux.items:
            assert plate_ok(it['placeWord']) or it.get('needsCouncilChoice'), it['placeWord']
        pv = plate_vectors(zones, lieux)
        for v in pv['long']:
            assert v['decodedPlate'] == [v['lieu']] and v['decodedOfficial'] == [v['lieu']], v
        for a, b in pv['collide']:
            assert E_same(a, b) and a['decoded'] == [a['lieu']] and b['decoded'] == [b['lieu']], (a, b)
    n_vec = 0
    vpath = os.path.join(HERE, 'vectors.json')
    if lieux.items and os.path.exists(vpath):  # 5. recompute the published vectors
        want = _load_json(vpath)
        got = json.loads(json.dumps(vectors(zones, lieux), ensure_ascii=False))
        assert got == want, 'vectors.json differs from the engine output'
        n_vec = (len(want['spot']) + len(want['addressCheck']) + len(want['samples']) + len(want['sameName'])
                 + len(want['plateNames']['long']) + len(want['plateNames']['collide']))
    print(f'selftest ok: UTM, check letter (all single errors and adjacent swaps), spot round trips, '
          f'numbering, national name ranges ({n_same} same-name decodings), {n_vec} published vectors')


def main(argv):
    zones, lieux = Zones(), Lieux()
    cmd = argv[1] if len(argv) > 1 else 'selftest'
    if cmd == 'encode':
        print(encode_spot(float(argv[2]), float(argv[3]), zones))
    elif cmd == 'decode':
        la, lo, c = decode_spot(argv[2], zones)
        print(f'{la:.6f} {lo:.6f}  (cell {c} m)')
    elif cmd == 'check':
        print(validate(argv[2], zones, lieux))
    elif cmd == 'find':
        for zk, lieu, nm in find(argv[2], zones, lieux):
            print(json.dumps(address_forms(zones, lieu, nm), ensure_ascii=False))
    elif cmd == 'vectors':
        out = vectors(zones, lieux)
        if len(argv) > 2 and argv[2] == '--write':
            with open(os.path.join(HERE, 'vectors.json'), 'w', encoding='utf-8') as f:
                json.dump(out, f, ensure_ascii=False, indent=1)
        print(json.dumps(out, ensure_ascii=False, indent=1))
    elif cmd == 'registry':
        print(json.dumps(sample_registry(argv[2], zones, lieux), ensure_ascii=False, indent=1))
    elif cmd == 'selftest':
        selftest(zones, lieux)
    else:
        sys.exit('usage:\n' + __doc__.split('\n\n')[2])


if __name__ == '__main__':
    main(sys.argv)
