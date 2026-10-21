#!/usr/bin/env python3
"""Pass 1 of the Senegal building profile: one row per building.

Reads (read-only) the N-Ways building sources for Senegal:
  data/detail/countries/senegal/buildings-src.geojsonseq   OpenStreetMap (ODbL)
  data/detail/ml/SN.parquet                                Google / Microsoft footprints with height h (via Overture)
and writes <work>/sn-buildings.parquet with, per building:
  src, osm_id, lon, lat (centroid), area_m2, perimeter_m (in UTM zone 28N),
  h (ML height, m), osm tags used by the profile (building, building:levels,
  height, amenity, shop, office, tourism, religion, craft, industrial, name),
  adm2 (département, geoBoundaries 2019), adm3 (arrondissement),
  poi_cat / poi_n (N-Ways places inside the footprint, most frequent category).

  tools/extract-buildings.py <work-dir> [<data-root>]

<work-dir> must hold adm2.geojson, adm3.geojson (geoBoundaries SEN ADM2/ADM3,
CC BY 3.0 IGO) and places.csv (id,name,category,source,lon,lat exported from
the N-Ways places table for the Senegal box). DuckDB runs with a 3 GB memory
cap; run one heavy job at a time.
"""
import os, subprocess, sys

work = os.path.abspath(sys.argv[1])
root = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..'))
osm = os.path.join(root, 'data', 'detail', 'countries', 'senegal', 'buildings-src.geojsonseq')
ml = os.path.join(root, 'data', 'detail', 'ml', 'SN.parquet')
out = os.path.join(work, 'sn-buildings.parquet')

UTM = "'EPSG:4326', 'EPSG:32628', always_xy := true"
TAGS = ['building', 'building:levels', 'height', 'amenity', 'shop', 'office', 'tourism',
        'religion', 'craft', 'industrial', 'name', 'man_made', 'healthcare', 'government']
tagcols = ',\n  '.join(
    f"json_extract_string(j, '$.properties.\"{t}\"') AS \"{t.replace(':', '_')}\"" for t in TAGS)
nulltags = ', '.join(f'NULL::VARCHAR AS "{t.replace(":", "_")}"' for t in TAGS)

sql = f"""
SET memory_limit='3GB'; SET threads=4; SET preserve_insertion_order=false;
SET temp_directory='{work}/duck-tmp';
LOAD spatial;
CREATE TABLE a2 AS SELECT shapeName AS adm2, geom FROM ST_Read('{work}/adm2.geojson');
CREATE TABLE a3 AS SELECT shapeName AS adm3, geom FROM ST_Read('{work}/adm3.geojson');
CREATE TABLE raw AS
SELECT 'osm' AS src, CAST(json_extract(j, '$.properties."@id"') AS BIGINT) AS osm_id,
  ST_GeomFromGeoJSON(json_extract(j, '$.geometry')) AS g, NULL::DOUBLE AS h,
  {tagcols}
FROM (SELECT ltrim(line, chr(30)) AS j FROM read_csv('{osm}', columns={{'line': 'VARCHAR'}}, header=false,
      delim=chr(1), quote='', escape='', max_line_size=16000000) WHERE length(line) > 2)
UNION ALL
SELECT 'ml', NULL, geometry::GEOMETRY, h, {nulltags} FROM '{ml}';
CREATE TABLE b AS
SELECT row_number() OVER () AS bid, *, ST_Centroid(g) AS c,
  ST_Area(ST_Transform(g, {UTM})) AS area_m2, ST_Perimeter(ST_Transform(g, {UTM})) AS perimeter_m
FROM raw;
DROP TABLE raw;
CREATE TABLE p AS SELECT category, ST_Point(lon, lat) AS pt FROM read_csv('{work}/places.csv', header=true);
CREATE TABLE bp AS
SELECT b.bid, mode(p.category) AS poi_cat, count(*) AS poi_n
FROM p JOIN b ON ST_Contains(b.g, p.pt) GROUP BY b.bid;
CREATE TABLE b2 AS SELECT b.bid, a2.adm2 FROM b JOIN a2 ON ST_Contains(a2.geom, b.c);
CREATE TABLE b3 AS SELECT b.bid, a3.adm3 FROM b JOIN a3 ON ST_Contains(a3.geom, b.c);
COPY (
  SELECT b.bid, src, osm_id, ST_X(c) AS lon, ST_Y(c) AS lat, area_m2, perimeter_m, h,
    {', '.join('"' + t.replace(':', '_') + '"' for t in TAGS)},
    b2.adm2, b3.adm3, bp.poi_cat, coalesce(bp.poi_n, 0) AS poi_n
  FROM b LEFT JOIN b2 USING (bid) LEFT JOIN b3 USING (bid) LEFT JOIN bp USING (bid)
) TO '{out}' (FORMAT parquet);
SELECT src, count(*), count(adm2) FROM '{out}' GROUP BY src;
"""
os.makedirs(os.path.join(work, 'duck-tmp'), exist_ok=True)
r = subprocess.run(['duckdb', '-csv'], input=sql, capture_output=True, text=True)
sys.stdout.write(r.stdout)
if r.returncode != 0:
    sys.exit(r.stderr[-3000:])
