#!/usr/bin/env python3
"""Build Senegal's frozen code zones (model/zones.geojson + model/zones.json).

A code zone is the area a Senegal N-Ways code hangs off (SPEC.md section 2).
Zones are built ONCE from the 2019 départements (geoBoundaries SEN ADM2,
Government of Senegal / OCHA ROWCA, CC BY 3.0 IGO) and then frozen: later
changes to the administrative map (Keur Massar, 2021) never move a zone.
Mbacké département is split along the Ndame arrondissement line into
TBA (Touba-Mbacké) and KTF (Kaël-Taïf), because Touba alone holds more
structures than a 6-digit number space can take with room to grow.

  tools/build-zones.py <dir with adm2.geojson and adm3.geojson>

Needs the duckdb CLI (spatial extension) for the one split; the rest is
standard-library Python. Writes into ../model/.
"""
import json, math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'engine', 'reference'))
import sn_engine as E  # noqa: E402  (UTM maths)

src = os.path.abspath(sys.argv[1])
MODEL = os.path.join(HERE, '..', 'model')

# geoBoundaries name -> (key, display name, region ISO code)
ZONES = {
    'Dakar': ('DKR', 'Dakar', 'SN-DK'), 'Pikine': ('PKN', 'Pikine (incl. Keur Massar)', 'SN-DK'),
    'Guediawaye': ('GDW', 'Guédiawaye', 'SN-DK'), 'Rufisque': ('RUF', 'Rufisque', 'SN-DK'),
    'Thies': ('THS', 'Thiès', 'SN-TH'), 'Mbour': ('MBR', 'Mbour', 'SN-TH'), 'Tivaoune': ('TIV', 'Tivaouane', 'SN-TH'),
    'Diourbel': ('DBL', 'Diourbel', 'SN-DB'), 'Bambey': ('BMB', 'Bambey', 'SN-DB'),
    'Kaolack': ('KAO', 'Kaolack', 'SN-KL'), 'Nioro Du Rip': ('NRP', 'Nioro du Rip', 'SN-KL'),
    'Guinguineo': ('GNG', 'Guinguinéo', 'SN-KL'),
    'Fatick': ('FTK', 'Fatick', 'SN-FK'), 'Foundiougne': ('FDG', 'Foundiougne', 'SN-FK'), 'Gossas': ('GOS', 'Gossas', 'SN-FK'),
    'Kaffrine': ('KAF', 'Kaffrine', 'SN-KA'), 'Birkelane': ('BRK', 'Birkelane', 'SN-KA'),
    'Koungheul': ('KGH', 'Koungheul', 'SN-KA'), 'Malem Hodar': ('MHD', 'Malem Hodar', 'SN-KA'),
    'Louga': ('LGA', 'Louga', 'SN-LG'), 'Kebemer': ('KBM', 'Kébémer', 'SN-LG'), 'Linguere': ('LNG', 'Linguère', 'SN-LG'),
    'Saint Louis': ('STL', 'Saint-Louis', 'SN-SL'), 'Dagana': ('DAG', 'Dagana', 'SN-SL'), 'Podor': ('POD', 'Podor', 'SN-SL'),
    'Matam': ('MAT', 'Matam', 'SN-MT'), 'Kanel': ('KNL', 'Kanel', 'SN-MT'), 'Ranerou': ('RAN', 'Ranérou-Ferlo', 'SN-MT'),
    'Tambacounda': ('TBC', 'Tambacounda', 'SN-TC'), 'Bakel': ('BKL', 'Bakel', 'SN-TC'),
    'Goudiry': ('GRY', 'Goudiry', 'SN-TC'), 'Koumpentoum': ('KPT', 'Koumpentoum', 'SN-TC'),
    'Kedougou': ('KDG', 'Kédougou', 'SN-KE'), 'Saraya': ('SRY', 'Saraya', 'SN-KE'), 'Salemata': ('SLM', 'Salémata', 'SN-KE'),
    'Kolda': ('KLD', 'Kolda', 'SN-KD'), 'Velingara': ('VEL', 'Vélingara', 'SN-KD'),
    'Medina Yoroufoula': ('MYF', 'Médina Yoro Foulah', 'SN-KD'),
    'Sedhiou': ('SED', 'Sédhiou', 'SN-SE'), 'Bounkiling': ('BNK', 'Bounkiling', 'SN-SE'), 'Goudomp': ('GMP', 'Goudomp', 'SN-SE'),
    'Ziguinchor': ('ZIG', 'Ziguinchor', 'SN-ZG'), 'Bignona': ('BIG', 'Bignona', 'SN-ZG'), 'Oussouye': ('OUS', 'Oussouye', 'SN-ZG'),
}
SPLIT = {'TBA': ('Touba-Mbacké (arr. de Ndame)', 'SN-DB'), 'KTF': ('Kaël-Taïf (Mbacké rural)', 'SN-DB')}

sql = f"""
LOAD spatial;
CREATE TABLE a2 AS SELECT shapeName n, geom FROM ST_Read('{src}/adm2.geojson');
CREATE TABLE a3 AS SELECT shapeName n, geom FROM ST_Read('{src}/adm3.geojson');
COPY (
  SELECT n, ST_AsGeoJSON(geom) g FROM a2 WHERE n <> 'Mbacke'
  UNION ALL SELECT 'TBA', ST_AsGeoJSON(ST_Intersection(m.geom, d.geom)) FROM a2 m, a3 d WHERE m.n='Mbacke' AND d.n='Ndame'
  UNION ALL SELECT 'KTF', ST_AsGeoJSON(ST_Difference(m.geom, d.geom)) FROM a2 m, a3 d WHERE m.n='Mbacke' AND d.n='Ndame'
) TO '/dev/stdout' (FORMAT csv, HEADER false, QUOTE '"');
"""
r = subprocess.run(['duckdb', '-c', "SET memory_limit='1GB';" + sql], capture_output=True, text=True)
if r.returncode:
    sys.exit(r.stderr)
import csv, io  # noqa: E402
csv.field_size_limit(1 << 30)
rows = list(csv.reader(io.StringIO(r.stdout)))

feats, meta = [], []
for name, g in rows:
    geom = json.loads(g)
    if name in SPLIT:
        key, (disp, reg) = name, SPLIT[name]
        src_name = 'Mbacke'
    else:
        key, disp, reg = ZONES[name]
        src_name = name
    # Round to 6 decimals (~0.1 m): the zone outline is frozen as published.
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 6), round(c[1], 6)]
    geom = {'type': geom['type'], 'coordinates': rnd(geom['coordinates'])}
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    es, ns = [], []
    for poly in polys:
        for lon, lat in poly[0]:
            e, n = E.utm_forward(lat, lon)
            es.append(e); ns.append(n)
    oe, on = math.floor(min(es) / 1000) * 1000, math.floor(min(ns) / 1000) * 1000
    size = max(math.ceil(max(es) / 1000) * 1000 - oe, math.ceil(max(ns) / 1000) * 1000 - on)
    cell = next((c for c in (1, 2, 5, 10) if size / c <= 10000), 10)
    digits = 4 if size / cell <= 10000 else 5
    meta.append({'key': key, 'name': disp, 'region': reg, 'source': src_name,
                 'originE': oe, 'originN': on, 'frameMetres': size, 'cellMetres': cell, 'digits': digits})
    feats.append({'type': 'Feature', 'properties': {'key': key}, 'geometry': geom})

meta.sort(key=lambda m: m['key'])
for i, m in enumerate(meta):
    m['index'] = i
order = {m['key']: m['index'] for m in meta}
feats.sort(key=lambda f: order[f['properties']['key']])
os.makedirs(MODEL, exist_ok=True)
json.dump({'crs': 'EPSG:32628 (WGS 84 / UTM zone 28N)', 'frozen': '2026-10-18',
           'source': 'geoBoundaries SEN ADM2/ADM3 (2019), Government of Senegal / OCHA ROWCA, CC BY 3.0 IGO',
           'zones': meta}, open(os.path.join(MODEL, 'zones.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({'type': 'FeatureCollection', 'features': feats},
          open(os.path.join(MODEL, 'zones.geojson'), 'w'), separators=(',', ':'))
for m in meta:
    print(m['index'], m['key'], m['name'], m['frameMetres'], m['cellMetres'], m['digits'])
