#!/usr/bin/env python3
"""Build Senegal's place-word inventory (model/lieux.json) and the
arithmetic behind the number lengths (model/lieux-stats.json).

A "lieu" is the place word of an N-Ways address ("Médina 4512"): a quartier
in towns, a village in the countryside (SPEC.md section 3). The inventory
comes from OpenStreetMap place nodes (neighbourhood, suburb, village, town,
city; ODbL) and GeoNames populated places (CC BY 4.0), and is assigned to
compounds with the SPEC's nearest-lieu rule. At first issue (20 October
2026) each lieu's index, name and number block were frozen; a rebuild serves
only to study a change, never to renumber.

The map name is the lieu's OFFICIAL name. tools/name-ranges.py derives from it
the PLATE name used in the address (at most 12 characters and 2 words,
tools/sn_plates.py, SPEC 3.2.1) and keeps the official name as an alias.

The number length and block of each lieu come from its NAME, not from the lieu
alone: every lieu with the same normalised name shares one national range
(SPEC 3.3). This script ends by running tools/name-ranges.py, which allocates
those ranges and rewrites lieux.json and lieux-stats.json.

  tools/build-lieux.py <work-dir>
    <work-dir>/lieux.csv      id,name,kind,lon,lat,popn,importance (geo_names, country SN)
    <work-dir>/compounds.csv  zone,e,n,structures,gate,rule,extent (tools/building-stats.py)
"""
import csv, json, math, os, re, sys, unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'engine', 'reference'))
import sn_engine as E  # noqa: E402

work = os.path.abspath(sys.argv[1])
zones = E.Zones()

JUNK = re.compile(r"^(place|rond[- ]point|ministere|groupe|chez|station|ecole|lycee|college|marche|hopital|"
                  r"mosquee|eglise|universite|zone industrielle|camp|caserne|cite administrative)\b")


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower().strip()


# 1. candidate lieux --------------------------------------------------------
raw = []
for r in csv.DictReader(open(os.path.join(work, 'lieux.csv'))):
    full = r['name'].strip()
    # "Golf Sud(Cité Aliou SOW)" -> place word "Golf Sud", the rest kept as an alias
    name = re.sub(r'\s*\(.*$', '', full).strip() or full
    if not name or len(name) > 40 or JUNK.match(fold(name)) or any(ch.isdigit() for ch in name[:1]):
        continue
    lat, lon = float(r['lat']), float(r['lon'])
    z = zones.lookup(lat, lon)
    if not z:
        continue
    e, n = E.utm_forward(lat, lon)
    tier = {'neighbourhood': 'A', 'suburb': 'A', 'village': 'A', 'locality': 'A', 'town': 'B', 'city': 'C'}[r['kind']]
    raw.append({'id': r['id'], 'name': name, 'alias': full if full != name else None, 'kind': r['kind'], 'tier': tier, 'zone': z, 'e': e, 'n': n,
                'popn': int(r['popn'] or 0), 'osm': r['id'].startswith('osm:')})
# GeoNames duplicates of OSM nodes: same folded name within 1 km, or any OSM node within 300 m
osm_grid = defaultdict(list)
for p in raw:
    if p['osm']:
        osm_grid[(int(p['e'] // 1000), int(p['n'] // 1000))].append(p)
lieux = []
dropped = Counter()
for p in raw:
    if not p['osm']:
        near = [q for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                for q in osm_grid.get((int(p['e'] // 1000) + dx, int(p['n'] // 1000) + dy), ())]
        dup = any(math.hypot(q['e'] - p['e'], q['n'] - p['n']) < 300 or
                  (fold(q['name']) == fold(p['name']) and math.hypot(q['e'] - p['e'], q['n'] - p['n']) < 1000)
                  for q in near)
        if dup:
            dropped['geonames-duplicate'] += 1
            continue
    lieux.append(p)

# 2. assign compounds to the nearest lieu (SPEC 3.2) -------------------------
by_zone = defaultdict(list)
for p in lieux:
    by_zone[p['zone']].append(p)
grids = {}
for z, ps in by_zone.items():
    g = defaultdict(list)
    for p in ps:
        g[(int(p['e'] // 2500), int(p['n'] // 2500))].append(p)
    grids[z] = g


def nearest(z, e, n):
    g = grids.get(z, {})
    gx, gy = int(e // 2500), int(n // 2500)
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for p in g.get((gx + dx, gy + dy), ()):
                if p['tier'] == 'A':
                    d = math.hypot(p['e'] - e, p['n'] - n)
                    if d <= 2500 and (best is None or d < best[0]):
                        best = (d, p)
    if best:
        return best[1]
    for tiers, lim in (('B', 10000), ('ABC', 1e9)):
        cands = [(math.hypot(p['e'] - e, p['n'] - n), p) for p in by_zone.get(z, ()) if p['tier'] in tiers]
        cands = [c for c in cands if c[0] <= lim]
        if cands:
            return min(cands, key=lambda c: c[0])[1]
    return None


counts = Counter()
structs = Counter()
orphans = Counter()
for r in csv.DictReader(open(os.path.join(work, 'compounds.csv'))):
    p = nearest(r['zone'], float(r['e']), float(r['n']))
    if p is None:
        orphans[r['zone']] += 1
        continue
    counts[p['id']] += 1
    structs[p['id']] += int(r['structures'])

# 2b. coverage mask evidence: OSM streets carrying the municipal programme's
# street references (PE-44, SC-15, OKM-1) - see SPEC 3.6 ------------------------
refs = Counter()
rp = os.path.join(work, 'streetrefs.json')
if os.path.exists(rp):
    for ref, lon, lat, _ in json.load(open(rp)):
        z = zones.lookup(lat, lon)
        if not z:
            continue
        e, n = E.utm_forward(lat, lon)
        p = nearest(z, e, n)
        if p:
            refs[p['id']] += 1
OFFICIAL_MIN_REFS = 3

# 3. keep lieux that hold compounds; index; nearest town as a place-card hint ---
# Same-named lieux are not told apart by a qualifier: they share their
# name's national range (tools/name-ranges.py, SPEC 3.3). 'nearTown' is only
# shown on the place card ("Keur Mbaye, near Ngoye"); it is never part of the address.
HEAD = 3  # headroom: room for three times today's compounds


out, zstats = [], {}
for z in sorted(by_zone):
    used = [p for p in by_zone[z] if counts[p['id']]]
    used.sort(key=lambda p: (fold(p['name']), p['e'], p['n']))
    names = Counter(fold(p['name']) for p in used)
    towns = [p for p in by_zone[z] if p['tier'] in 'BC']
    for i, p in enumerate(used):
        q = None
        if names[fold(p['name'])] > 1:
            others = [t for t in towns if fold(t['name']) != fold(p['name'])] or \
                     [t for t in used if fold(t['name']) != fold(p['name'])]
            if others:
                q = min(others, key=lambda t: math.hypot(t['e'] - p['e'], t['n'] - p['n']))['name']
        n = counts[p['id']]
        out.append({'zone': z, 'index': i, 'name': p['name'], 'officialName': p['name'], 'nearTown': q, 'aliases': [a for a in [p['alias']] if a], 'kind': p['kind'], 'source': p['id'],
                    'e': round(p['e']), 'n': round(p['n']), 'compounds': n, 'structures': structs[p['id']],
                    'digits': None, 'programmeStreetRefs': refs[p['id']],
                    'coverage': 'official-municipal' if refs[p['id']] >= OFFICIAL_MIN_REFS else 'nways'})
    zl = [o for o in out if o['zone'] == z]
    tot = sum(o['compounds'] for o in zl)
    zstats[z] = {
        'lieux': len(zl), 'compounds': tot,
        'compoundsByDigits': {},   # filled by tools/name-ranges.py
        'compoundsInOversizeLieux': sum(o['compounds'] for o in zl if HEAD * o["compounds"] > 81000),
        'lieuxByDigits': {},
        'oversizeLieux': [o['name'] for o in zl if HEAD * o["compounds"] > 81000],
        'largest': sorted(({'name': o['name'], 'compounds': o['compounds']} for o in zl),
                          key=lambda x: -x['compounds'])[:5],
        'orphanCompounds': orphans[z],
        'compoundsInOfficialMask': sum(o['compounds'] for o in zl if o['coverage'] != 'nways'),
        'lieuxInOfficialMask': sum(1 for o in zl if o['coverage'] != 'nways'),
    }

alln = sum(s['compounds'] for s in zstats.values())
summary = {
    'headroom': HEAD,
    'rule': 'filled by tools/name-ranges.py',
    'candidates': len(raw), 'droppedGeonamesDuplicates': dropped['geonames-duplicate'],
    'lieuxUsed': len(out), 'compounds': alln,
    'shareCompoundsByDigits': {},
    'shareCompoundsInOversizeLieux': round(sum(s['compoundsInOversizeLieux'] for s in zstats.values()) / alln, 4),
    'lieuxByDigits': {},
    'oversizeLieux': sum(len(s['oversizeLieux']) for s in zstats.values()),
    'programmeStreetRefs': sum(refs.values()),
    'shareCompoundsInOfficialMask': round(sum(s['compoundsInOfficialMask'] for s in zstats.values()) / alln, 4),
    'lieuxInOfficialMask': sum(s['lieuxInOfficialMask'] for s in zstats.values()),
    'medianCompoundsPerLieu': sorted(o['compounds'] for o in out)[len(out) // 2],
}
json.dump({'status': 'frozen at first issue (2026-10-20): index, plate name, family and blocks never change; '
                     'blocks are only added',
           'sources': 'OpenStreetMap place nodes (ODbL); GeoNames populated places (CC BY 4.0)',
           'lieux': out}, open(os.path.join(HERE, '..', 'model', 'lieux.json'), 'w'), ensure_ascii=False,
          separators=(',', ':'))
json.dump({'summary': summary, 'zones': zstats}, open(os.path.join(HERE, '..', 'model', 'lieux-stats.json'), 'w'),
          ensure_ascii=False, indent=1)
# 4. national name ranges: number length and block per lieu (SPEC 3.3)
import runpy  # noqa: E402
runpy.run_path(os.path.join(HERE, 'name-ranges.py'), run_name='__main__')
