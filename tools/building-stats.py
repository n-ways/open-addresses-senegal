#!/usr/bin/env python3
"""Pass 2 of the Senegal building profile: compounds, classes, sizes, gates.

Reads <work>/sn-buildings.parquet (tools/extract-buildings.py), the OSM
walls/fences/gates/entrances for Senegal and the N-Ways gated compounds and
gates (data/valhalla/*.geojsonseq), groups every zone's structures into
compounds with the reference engine's rules, classifies every structure,
and writes model/building-stats.json.

  tools/building-stats.py <work-dir> [<data-root>]

Heavy: streams 5.6 million rows from DuckDB (memory_limit 3GB), one zone at
a time in Python. Run it on its own: DuckDB is capped at 3 GB.
"""
import csv, io, json, math, os, subprocess, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'engine', 'reference'))
import sn_engine as E  # noqa: E402

csv.field_size_limit(1 << 30)
work = os.path.abspath(sys.argv[1])
root = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.abspath(os.path.join(HERE, '..', '..', '..'))
zones = E.Zones()
meta = json.load(open(os.path.join(HERE, '..', 'model', 'zones.json')))['zones']
by_source = {m['source']: m['key'] for m in meta if m['source'] != 'Mbacke'}


def zone_of(adm2, adm3, lat, lon):
    if adm2 == 'Mbacke':
        return 'TBA' if adm3 == 'Ndame' else 'KTF'
    if adm2 in by_source:
        return by_source[adm2]
    return zones.lookup(lat, lon)


# ---- gates, entrances and enclosures (OSM + N-Ways routing build) ----------
def seq(path):
    with open(path) as f:
        for line in f:
            line = line.lstrip('\x1e').strip()
            if line:
                yield json.loads(line)


gates = defaultdict(list)       # zone -> [(e, n, source)]
enclosures = defaultdict(list)  # zone -> [(id, kind, ring_utm)]
osm_src = os.path.join(root, 'data', 'detail', 'countries', 'senegal', 'src.geojsonseq')
with open(osm_src) as f:
    for line in f:
        if '"barrier"' not in line and '"entrance"' not in line:
            continue
        ft = json.loads(line.lstrip('\x1e'))
        p, g = ft['properties'], ft['geometry']
        if g['type'] == 'Point' and (p.get('barrier') in ('gate', 'entrance', 'sliding_gate', 'swing_gate', 'lift_gate')
                                     or p.get('entrance')):
            lon, lat = g['coordinates']
            z = zones.lookup(lat, lon)
            if z:
                gates[z].append((*E.utm_forward(lat, lon), 'osm'))
        elif p.get('barrier') in ('wall', 'fence', 'hedge'):
            coords = g['coordinates'] if g['type'] == 'LineString' else g['coordinates'][0] if g['type'] == 'Polygon' else None
            if coords and len(coords) >= 4 and coords[0] == coords[-1]:
                lon, lat = coords[0]
                z = zones.lookup(lat, lon)
                if z:
                    enclosures[z].append((f"osm:{p.get('@id')}", 'wall', [E.utm_forward(y, x) for x, y in coords]))
vg = os.path.join(root, 'data', 'valhalla', 'gates.geojsonseq')
for ft in seq(vg):
    lon, lat = ft['geometry']['coordinates']
    if -17.6 < lon < -11.3 and 12.3 < lat < 16.7:
        z = zones.lookup(lat, lon)
        if z:
            gates[z].append((*E.utm_forward(lat, lon), 'nways-gates'))
vc = os.path.join(root, 'data', 'valhalla', 'compounds.geojsonseq')
n_sites = Counter()
for ft in seq(vc):
    g = ft['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    lon, lat = polys[0][0][0]
    if not (-17.6 < lon < -11.3 and 12.3 < lat < 16.7):
        continue
    z = zones.lookup(lat, lon)
    if not z:
        continue
    for poly in polys:
        enclosures[z].append((ft['properties'].get('id'), ft['properties'].get('kind'),
                              [E.utm_forward(y, x) for x, y in poly[0]]))
    n_sites[ft['properties'].get('kind')] += 1

# ---- stream the buildings, zone by zone ------------------------------------
cols = ['bid', 'src', 'lon', 'lat', 'area_m2', 'perimeter_m', 'h', 'building', 'building_levels', 'height',
        'amenity', 'shop', 'office', 'tourism', 'religion', 'craft', 'industrial', 'man_made', 'healthcare',
        'government', 'adm2', 'adm3', 'poi_cat']
sql = (f"SET memory_limit='3GB'; SET threads=4; COPY (SELECT {', '.join(cols)} FROM '{work}/sn-buildings.parquet' "
       f"ORDER BY CASE WHEN adm2 = 'Mbacke' AND adm3 = 'Ndame' THEN 'TBA' ELSE adm2 END NULLS LAST) TO '/dev/stdout' (FORMAT csv, HEADER true);")
proc = subprocess.Popen(['duckdb', '-c', sql], stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
reader = csv.DictReader(proc.stdout)

REGION = {m['key']: m['region'] for m in meta}
AREA_BINS = [10, 25, 50, 100, 200, 400, 1000, 5000]
reg_stats = defaultdict(lambda: {'structures': 0, 'bySource': Counter(), 'groups': Counter(), 'areas': [],
                                 'floors': Counter(), 'heightKnown': 0, 'floorArea': 0.0, 'confidence': Counter(),
                                 'compounds': 0, 'inMulti': 0})
zone_stats = {}
detail = {}
osm_values = Counter()
ml_h = Counter()
CW = csv.writer(open(os.path.join(work, 'compounds.csv'), 'w', newline=''))
CW.writerow(['zone', 'e', 'n', 'structures', 'gate', 'rule', 'extent'])
DETAIL_ZONES = ('DKR', 'PKN', 'GDW', 'RUF', 'TBA', 'ZIG', 'KLD', 'BMB')


def qs(v):
    v.sort()
    if not v:
        return {}
    pick = lambda q: round(v[min(len(v) - 1, int(q * len(v)))], 1)  # noqa: E731
    return {'p10': pick(.10), 'p25': pick(.25), 'median': pick(.5), 'p75': pick(.75), 'p90': pick(.9), 'p99': pick(.99)}


def hist(v):
    out = Counter()
    for a in v:
        for b in AREA_BINS:
            if a < b:
                out[f'<{b}'] += 1
                break
        else:
            out[f'>={AREA_BINS[-1]}'] += 1
    return out


def flush(zkey, rows):
    if not rows:
        return
    structs = []
    for i, r in enumerate(rows):
        e, n = E.utm_forward(float(r['lat']), float(r['lon']))
        structs.append({'id': i, 'e': e, 'n': n, 'area': float(r['area_m2'] or 1)})
    comps = E.group_compounds(structs, enclosures.get(zkey, ()))
    by_id = {s['id']: s for s in structs}
    multi = {sid for c in comps if len(c['members']) > 1 for sid in c['members']}
    zg = gates.get(zkey, [])
    ggrid = defaultdict(list)
    for ge, gn, gs in zg:
        ggrid[(int(ge // 50), int(gn // 50))].append((ge, gn))
    with_gate = 0
    for c in comps:
        xs = [by_id[i]['e'] for i in c['members']]
        ys = [by_id[i]['n'] for i in c['members']]
        rmax = max(E.radius(by_id[i]['area']) for i in c['members']) + 5
        x0, x1, y0, y1 = min(xs) - rmax, max(xs) + rmax, min(ys) - rmax, max(ys) + rmax
        hit = any(x0 <= ge <= x1 and y0 <= gn <= y1
                  for gx in range(int(x0 // 50), int(x1 // 50) + 1) for gy in range(int(y0 // 50), int(y1 // 50) + 1)
                  for ge, gn in ggrid.get((gx, gy), ()))
        with_gate += hit
        CW.writerow([zkey, round(c['e'], 1), round(c['n'], 1), len(c['members']), int(hit), c['rule'], c['extentM']])
    rules = Counter(c['rule'] for c in comps)
    sizes = Counter(min(len(c['members']), 10) for c in comps)
    reg = reg_stats[REGION[zkey]]
    zclass = Counter()
    zareas, zfloors, zrplus = [], Counter(), Counter()
    for i, r in enumerate(rows):
        s = by_id[i]
        sz = E.size_profile(s['area'], float(r['perimeter_m'] or 0), E.num(r['h']), r['height'], r['building_levels'])
        tags = {k: r[k] for k in ('building', 'amenity', 'shop', 'office', 'tourism', 'religion', 'craft',
                                  'industrial', 'man_made', 'healthcare', 'government') if r[k]}
        cls, conf, ev = E.classify(tags, s['area'], sz['floors'], r['poi_cat'] or None, rural=not s['urban'],
                                   in_multi=i in multi, satellite=s.get('satellite', False))
        grp = E.GROUPS[cls.split('.')[0]]
        if r['src'] == 'osm':
            osm_values[r['building'] or ''] += 1
        elif r['h']:
            ml_h[round(float(r['h']), 1)] += 1
        reg['structures'] += 1
        reg['bySource'][r['src']] += 1
        reg['groups'][grp] += 1
        reg['areas'].append(s['area'])
        reg['floors']['unknown' if sz['floorsSource'] == 'default' else min(sz['floors'], 6)] += 1
        reg['heightKnown'] += sz['heightM'] is not None
        reg['floorArea'] += sz['floorAreaM2']
        reg['confidence']['high' if conf >= 0.8 else 'medium' if conf >= 0.6 else 'low'] += 1
        if zkey in DETAIL_ZONES:
            zclass[cls] += 1
            zareas.append(s['area'])
            known = sz['floorsSource'] != 'default'
            zfloors[min(sz['floors'], 6) if known else 'unknown'] += 1
            zrplus[('R+5 et plus' if sz['floors'] >= 6 else sz['rPlus']) if known else 'unknown'] += 1
    reg['compounds'] += len(comps)
    reg['inMulti'] += len(multi)
    n = len(rows)
    zone_stats[zkey] = {
        'structures': n, 'compounds': len(comps), 'structuresInMultiStructureCompounds': len(multi),
        'shareInMulti': round(len(multi) / n, 3), 'compoundsWithKnownGate': with_gate,
        'shareCompoundsWithKnownGate': round(with_gate / len(comps), 4), 'groupingRules': dict(rules),
        'urbanShare': round(sum(s['urban'] for s in structs) / n, 3),
    }
    if zkey in DETAIL_ZONES:
        detail[zkey] = {'classes': dict(zclass.most_common()), 'footprintM2': qs(zareas), 'areaHistogram': dict(hist(zareas)),
                        'floors': {str(k): v for k, v in zfloors.items()}, 'rPlus': dict(zrplus.most_common()),
                        'compoundSizes': {('10+' if k == 10 else str(k)): v for k, v in sorted(sizes.items())}}
    print(zkey, n, len(comps), round(len(multi) / n, 3), with_gate, flush=True)


cur, buf = None, []
skipped = 0  # footprints whose centre is outside the 2019 département outlines (coast, borders)
for r in reader:
    if not r['adm2']:
        skipped += 1
        continue
    z = zone_of(r['adm2'], r['adm3'], float(r['lat']), float(r['lon']))
    if z != cur:
        if cur:
            flush(cur, buf)
        cur, buf = z, []
    buf.append(r)
if cur:
    flush(cur, buf)
proc.wait()

out = {'computed': '2026-10-18', 'note': 'N-Ways reference statistics; classes and compounds are inferred '
       '(SPEC.md sections 5-6), not surveyed. Structures = building footprints (OpenStreetMap + Google/Microsoft).',
       'skippedOutsideZones': skipped,
       'gates': {k: len(v) for k, v in sorted(gates.items())}, 'enclosures': {k: len(v) for k, v in sorted(enclosures.items())},
       'nwaysSitesInSenegal': dict(n_sites), 'osmBuildingValues': dict(osm_values.most_common(30)),
       'mlHeightFiller': {'rows': sum(ml_h.values()), 'distinct': len(ml_h), 'min': min(ml_h, default=None), 'max': max(ml_h, default=None)}, 'regions': {}, 'zones': dict(sorted(zone_stats.items())), 'detail': detail}
for reg, s in sorted(reg_stats.items()):
    n = s['structures']
    out['regions'][reg] = {
        'structures': n, 'bySource': dict(s['bySource']), 'compounds': s['compounds'],
        'shareInMultiStructureCompounds': round(s['inMulti'] / n, 3),
        'groups': {k: round(v / n, 4) for k, v in s['groups'].most_common()},
        'footprintM2': qs(s['areas']), 'areaHistogram': dict(hist(s['areas'])),
        'floors': {('6+' if k == 6 else str(k)): v for k, v in s['floors'].items()},
        'heightKnownShare': round(s['heightKnown'] / n, 3), 'floorAreaKm2': round(s['floorArea'] / 1e6, 2),
        'confidence': dict(s['confidence']),
    }
json.dump(out, open(os.path.join(HERE, '..', 'model', 'building-stats.json'), 'w'), ensure_ascii=False, indent=1)
print('written model/building-stats.json')
