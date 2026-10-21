#!/usr/bin/env python3
"""Cut the small real footprint samples the test vectors use
(engine/reference/samples/*.csv) out of <work>/sn-buildings.parquet.

  tools/make-samples.py <work-dir>

Samples: a block of the Médina (Dakar), a block next to the Grande Mosquée
de Touba, and the densest rural village tile of Bambey département (picked
by the query, so it is reproducible). Each is a 300 m square. Data:
OpenStreetMap (ODbL) and Google/Microsoft footprints via Overture (CC BY 4.0
/ ODbL); see SOURCES.md X1-X2.
"""
import os, subprocess, sys

work = os.path.abspath(sys.argv[1])
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine', 'reference', 'samples')
os.makedirs(out, exist_ok=True)
P = f"'{work}/sn-buildings.parquet'"
# Each footprint carries tile_count: the footprints in its 250 m UTM tile over the WHOLE map,
# so the urban-fabric rule (SPEC 7.1) sees the real density, not the sample's cut edges.
T = ("(SELECT b.*, count(*) OVER (PARTITION BY floor(ST_X(u) / 250), floor(ST_Y(u) / 250)) AS tile_count FROM "
     "(SELECT *, ST_Transform(ST_Point(lon, lat), 'EPSG:4326', 'EPSG:32628', always_xy := true) AS u FROM {P} "
     "WHERE {W}) b)")
COLS = ("bid AS id, src, tile_count, round(lon, 7) AS lon, round(lat, 7) AS lat, round(area_m2, 1) AS area_m2, "
        "round(perimeter_m, 1) AS perimeter_m, building, building_levels, height, amenity, shop, office, "
        "tourism, religion, craft, industrial, man_made, healthcare, government, poi_cat")
D = 0.00139  # half of 300 m in latitude degrees


def box(lat, lon, d=D):
    dl = d / 0.967  # cos(14.7 deg)
    return f"lat BETWEEN {lat - d} AND {lat + d} AND lon BETWEEN {lon - dl} AND {lon + dl}"


sql_main = f"""SET memory_limit='3GB'; LOAD spatial;
COPY (SELECT {COLS} FROM {T.format(P=P, W=box(14.6835, -17.4495, 0.004))} WHERE {box(14.6835, -17.4495)} ORDER BY id) TO '{out}/dakar-medina.csv' (HEADER);
COPY (SELECT {COLS} FROM {T.format(P=P, W=box(14.8650, -15.8800, 0.004))} WHERE {box(14.8650, -15.8800)} ORDER BY id) TO '{out}/touba.csv' (HEADER);
SELECT (ty + 0.5) * 0.0027, (tx + 0.5) * 0.0028 FROM (
  SELECT floor(lat / 0.0027) AS ty, floor(lon / 0.0028) AS tx, count(*) n, median(area_m2) med
  FROM {P} WHERE adm2 = 'Bambey' GROUP BY 1, 2) WHERE med < 40 ORDER BY n DESC, ty, tx LIMIT 1;
"""
r = subprocess.run(['duckdb', '-csv', '-noheader', '-c', sql_main], capture_output=True, text=True)
if r.returncode:
    sys.exit(r.stderr)
lat, lon = map(float, r.stdout.strip().splitlines()[-1].split(','))
r = subprocess.run(['duckdb', '-c', f"SET memory_limit='3GB'; LOAD spatial; COPY (SELECT {COLS} FROM {T.format(P=P, W=box(lat, lon, 0.004))} WHERE {box(lat, lon)} "
                    f"ORDER BY id) TO '{out}/bambey-village.csv' (HEADER);"], capture_output=True, text=True)
if r.returncode:
    sys.exit(r.stderr)
print(f'village tile centre {lat:.5f} {lon:.5f}')
for f in sorted(os.listdir(out)):
    print(f, sum(1 for _ in open(os.path.join(out, f))) - 1, 'footprints')
