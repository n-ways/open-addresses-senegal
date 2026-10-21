# registry/

The issued registry of Senegal's N-Ways addresses (engine/SPEC.md section 7). Every compound in Senegal received its address on 20 October 2026, in one run, with the place list and every name's blocks frozen: 3,597,128 addresses in the 46 zones. No address lies more than 300 m outside the national border (engine/SPEC.md 2.3; `python3 tools/build_border.py check`). An address is provisional until people confirm it. The registry publishes every issued address. Nothing is held back.

The N-Ways issuer is Senegal's single issuer. It numbers the compounds that `tools/issue_registry.py` lists, keeps every address already issued and only adds new ones, so a rerun never renumbers. Every file here, the anchors included, is written by its export in one step (`go run ./cmd/homecodes export -country SN -out <open-addresses-sn>/registry`), in the format that `python3 -m server export` also writes:

- `lieux.csv` (and `lieux.csv.gz`): the frozen place list. Columns: lieu, zone, index, plate name, official name, kind, name key, name family, digits, blocks (lo-hi), whether the commune still chooses the plate name, aliases, nearest town, coverage, position (UTM 28N).
- `<KEY>.csv.gz`: one gzip file per zone (DKR, TBA, ...), one row per address, by name family then number. Columns: canonical address, remembered and written forms, lieu, number, check letter, status, how and when issued, entrance (gate or centre) with its spot code, class, use and kind of the compound, structures, floor area, La Poste postcode where mapped, coverage (`official`, `official-pending` or empty) and the official address where the commune numbered the door. Nothing about the people in a home.
- `anchors/<KEY>.csv.gz`: for every address, row for row with `<KEY>.csv.gz`, the compound's centroid (`anchor_lat`, `anchor_lng`) at full precision. The issuer orders an area's compounds by this point when it numbers a new one (SPEC 7.3-7.4). With it, an independent deployment of `server/` issues exactly the numbers the N-Ways issuer would. `anchors/MANIFEST.json` gives its counts and SHA-256.
- `MANIFEST.json`: counts, the SHA-256 of every file before compression, the export date, the engine version, the credit and the licence.

Files are UTF-8, comma-separated, with LF line ends; a field is quoted only when it holds a comma, a quote or a line break. The `.gz` files are gzip at level 9 without a name or a time stamp, so the same data always gives the same bytes. Each SHA-256 is that of the uncompressed file: two gzip implementations need not choose the same encoding of the same contents, so an export by `python3 -m server export` matches these files once uncompressed.

Read a zone with `gzip -dc registry/DKR.csv.gz | head`, or in Python with `csv.DictReader(gzip.open('registry/DKR.csv.gz', 'rt'))`. Load the whole registry into a ready-made API with `python3 -m server import` (see [server/README.md](../server/README.md)). The import checks every file against the manifests.

Credit: "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)".
