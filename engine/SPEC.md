# N-Ways Senegal engine: specification

Version 0.2 (2026-10-18). This SPEC is normative. `engine/reference/sn_engine.py` is its executable reference: where the two disagree, this document wins and the script has a bug. The engine is self-contained: it needs only the Python standard library and the files in `model/`. The registry server in `server/` (section 10) serves and issues addresses with it.

Words used in this SPEC:

- **Structure**: one building footprint.
- **Compound**: the addressable unit, such as a concession, villa plot, apartment block, school or market.
- **Zone**: one of the 46 frozen code zones.
- **Lieu**: the place word of an address, such as a quartier, a village or a cité.

---

## 1. What the engine does

| Function | Online? | Input → output |
|---|---|---|
| `find` | offline with `lieux.json` | remembered or written address ("Ouakam 2512", "HLM 5 17 395", "OUAKAM 2512 · DAKAR") → the one (zone, lieu, number) it names, with **no context** (3.3.6) |
| `address_forms` | offline | (lieu, number) → remembered, written, canonical and spoken forms |
| `validate` | offline (`lieux.json` for addresses) | canonical address or spot code → valid or the reason it is not |
| `name_key` / `allocate_families` | registry build | place words → national name families, number lengths and blocks (3.3) |
| `encode_spot` / `decode_spot` | offline | latitude, longitude ↔ spot code `KEY eeee nnnn C` |
| lookup (registry) | offline with the zone's index file, else online | address → compound record (gate, outline, structures, profile) |
| `group_compounds` | registry build | structures (+ enclosures) → compounds |
| `Lieux.nearest` | registry build, Add my home | point → its lieu |
| `number_lieu` | registry build | the compounds of one lieu → numbers (first issue) |
| `insert_in_lieu` / `reserve_provisional` | registry (online) | a new compound → its number (provisional) |

## 2. Zones

### 2.1 The zone list

There are 46 zones (`model/zones.json`, outlines in `model/zones.geojson`). They were frozen on 2026-10-18 and never change (GOVERNANCE.md). Each zone has:

| Field | Meaning |
|---|---|
| `key` | three capital letters, e.g. `DKR` |
| `index` | 0-45, the position in the key-sorted list; used by the check letter |
| `name`, `region` | display name; ISO 3166-2 region of the source département |
| `source` | geoBoundaries 2019 département it was cut from |
| `originE`, `originN` | south-west corner of the zone's spot frame, in WGS 84 / UTM 28N metres, floored to the kilometre |
| `frameMetres` | side of the square frame: the larger of the zone's east-west and north-south extents, rounded up to the kilometre |
| `cellMetres` | spot cell size: the smallest of 1, 2, 5, 10 m for which `frameMetres / cellMetres ≤ 10 000` |
| `digits` | 4 if `frameMetres / cellMetres ≤ 10 000`, else 5 (cells then 10 m) |

The zones are the 45 départements of geoBoundaries SEN ADM2 (2019), except Mbacké, which is split in two: **TBA** is the arrondissement of Ndame, which holds Touba and Mbacké town, and **KTF** is the rest (Kaël and Taïf). Keur Massar (a département since 2021) stays inside **PKN**: no open boundary for it exists, and zones never follow administrative changes.

| Cell | Zones | Why |
|---|---|---|
| 1 m | GDW | 8 km frame |
| 2 m | DKR, PKN | 16 km frames |
| 5 m | BMB, GNG, OUS, RUF, STL, TBA | 34-49 km frames |
| 10 m, 4+4 digits | the other 19 zones | frames 55-100 km |
| 10 m, 5+5 digits | BKL, DAG, GRY, KBM, KDG, KGH, KLD, KNL, KPT, LGA, LNG, MAT, MYF, POD, RAN, SRY, TBC, TIV | frames 101-215 km |

### 2.2 Zone lookup (point → zone)

1. Ray-cast the point (longitude, latitude) against every zone outline whose bounding box holds it. Holes count: a point in a hole is outside.
2. If one or more zones hold it, the answer is the one with the **lowest index**. This settles the rare overlaps between the 2019 outlines.
3. Otherwise (the coast, river banks, gaps in the 2019 outlines), the answer is the zone with the nearest outline vertex within 2 km, measured in UTM metres.
4. Otherwise the point is outside Senegal, and no code is given.
5. For issuing an address, moving an entrance and the registry's lookups by position, a point that steps 1-3 give a zone but which lies more than 300 m outside the national border is outside Senegal too (2.3, `Border.holds`).

The lookup decides only which zone a **new** spot code uses. Decoding never needs it, because the key is in the code.

### 2.3 The border decides

An address is only ever issued for a building whose entrance lies inside Senegal's national border, OpenStreetMap's admin_level=2 boundary (`ISO3166-1=SN`), or within 300 m of it (`sn_engine.BORDER_M`). A point further out is in a neighbouring country and is outside Senegal, whatever the zone rule of 2.2 gives: the 2019 département outlines, the 2 km reach along rivers and coasts, and outlines from other sources (GADM and the like) may spill over the border, and they never decide.

The border ships as `engine/data/border.geojson`, made by `tools/build_border.py` from the OpenStreetMap relation: its ways joined into rings and simplified by Douglas-Peucker at 50 m on the UTM 28N grid, coordinates to 1e-5 degrees (about 70 kB). The file records the largest distance between the simplified line and the true one, measured both ways (`maxDeviationM`, 50.4 m for the current file). `sn_engine.Border` applies 300 m less that deviation, rounded up (249 m), so a point it accepts is never more than 300 m outside the true border. The price is on the safe side: a point between 249 and 300 m outside may be refused, never one in a neighbouring country accepted.

## 3. The address

### 3.1 One identity, four forms

| Form | Pattern | Example | Who uses it |
|---|---|---|---|
| **Remembered** | `<Lieu> <number>` | `Ouakam 2512` | people: said, written on a parcel, typed in WhatsApp |
| **Written** | `<LIEU> <number> · <ZONE NAME>` | `OUAKAM 2512 · DAKAR` | plates, stickers, forms, receipts; no check letter, because people never need it |
| **Canonical** | `SN-<KEY>-<lieu index, 4 digits>-<number>-<check>[·<structure>[.<unit>]]` | `SN-DKR-0080-2512-J·2` | APIs, QR codes, partner databases |

The forms map one-to-one. The remembered form has **no letters to learn and no check character**. The check letter appears only in the canonical form, for systems; it is never printed on plates or shown to people.

**The remembered form is unique in the whole country on its own.** A name is said without its town, so the address must not need one. "Ouakam 2512" names one compound in Senegal without a zone, a town after a comma or the position of the phone. Same-named places are kept apart by their numbers, never by context (3.3). The zone name on the written form is information for the reader, not part of the identity: "Médina 23 150" is the Médina of Ziguinchor with or without "· ZIGUINCHOR". A form such as "Medina 150, Ziguinchor", which needs the town to be told apart from the Médina of Dakar, is not used: without the town it would name two places.

- **Number.** It has 3, 4 or 5 digits and never starts with 0, so it reads like a house number. All numbers of one **name** have the same length, in every lieu of that name (3.3).
- **Grouping.** 3 digits are written and read whole ("120", "cent vingt"). 4 digits are written whole and read in two pairs ("4512", "quarante-cinq, douze"). 5 digits are written and read as 2 + 3 ("45 128", "quarante-cinq, cent vingt-huit").
- **Structure and unit.** Inside a compound, `·2` names its second building and `·1.3` the third flat or shop door of its main building. They are said as "Ouakam 2512, bâtiment 2, porte 3". Most addresses never need them.

### 3.2 The lieu (place word)

The lieu is a named place that people already use, and every address hangs off one. The inventory is `model/lieux.json`, with one entry per lieu:

| Field | Meaning |
|---|---|
| `zone`, `index` | the zone, and the lieu's index (0-9999) within it; frozen at first issue |
| `name` | the **plate name**: the place word as written on the plate and said in the address, at most 12 characters and 2 words (3.2.1): `Médina`, `Liberté 6`, `Saly`, `Cité Lamy` |
| `officialName` | the full official name from the map or the commune's list (`S.I.C.A.P. Liberté Six`, `Saly Portudal`); printed in small type on cards and plates, never required |
| `plateRule` | how the plate name was found: `as-is`, `cleaned`, `known` (documented short form, with `plateSource`), `distinctive`, `council` |
| `needsCouncilChoice`, `plateCandidates`, `plateReason` | set when the commune chooses the plate name: up to 3 candidates, the first used provisionally, and why |
| `aliasesDropped` | official names or spellings not kept as aliases because two plate names would claim them |
| `placeWord` | the name as said in the address: `name`, plus the qualifier when its name needed one (3.3.4; none today) |
| `nameKey`, `family` | the normalised name (3.3.1) and the 5-digit id of its name family; frozen at first issue |
| `digits` | number length, 3-5, **shared by every lieu of the name** (3.3.2); frozen at first issue |
| `blocks` | the lieu's block(s) of its name's national range, `[[lo, hi], …]` (3.3.3); frozen, only ever appended to |
| `nearTown` | when several lieux of one zone share a name: the nearest town, shown on the place card only ("Keur Mbaye, near Ngoye"). Never part of the address |
| `aliases` | other spellings and names that resolve to it: the official name, OSM alternative names, French and Wolof spellings (`Ouakam`/`Wakam`, `Mbacké`/`Mbakke`) |
| `kind` | `neighbourhood`, `suburb`, `village`, `locality`, `town`, `city`, `extension` |
| `e`, `n` | the lieu's point (UTM 28N) |

#### 3.2.1 The plate name

The place word in the address is the lieu's **plate name** (`name`), never the raw map name. A long address is not remembered ("Keur Serigne Ablaye Yakhine 2 345" is too long to say), so the plate name has a limit:

- **at most 12 characters**, counted on the NFC form: letters, spaces, hyphens and apostrophes count one each, an accented letter is one;
- **at most 2 words**: a word is a part between spaces or hyphens that is not a linking word (`de`, `du`, `des`, `d'`, `la`, `le`, `les`, `l'`, `et`, `sur`, `en`, `au`, `aux`, `à`, `&`);
- a trailing **sector numeral** (1-2 digits) is written in digits after the name ("Liberté 6", "HLM 5"); it counts in the 12 characters, not as a word. No other digit is allowed.

`plate_ok(name)` implements the check, with `split_numeral` (`'S.I.C.A.P. Liberté Six'` → `('S.I.C.A.P. Liberté', '6')`). `allocate_families` refuses a plate name over the limit unless the lieu is flagged `needsCouncilChoice`; `Lieux.add_lieu` refuses any plate name over the limit.

The plate name is derived from the official name by `tools/sn_plates.py` with the rule of `plate_names.py` (`derive`): a documented short form (`known`, with its source) wins; else the name is cleaned (numeral split off and written in digits; generic words *quartier*, *village de*, *hameau*, *lotissement*, *zone*, *secteur*, *campement*, and the scheme labels *S.I.C.A.P.*, *Sicap* dropped; brackets, text after a slash and a second spelling after *ou* dropped; acronym dots removed); if it fits it is used; else the runs of whole words that fit are ranked by rarity over all lieu names and the best is taken only when clearly ahead (score ≥ 1.5 × the next). *Cité* is not a generic word in Senegal: it stays in a name that fits ("Cité Lamy") and is the first word to go when the name is too long. A lieu goes to the commune (`needsCouncilChoice`, up to 3 `plateCandidates`) when:

1. no run of whole words fits, or no candidate is clearly ahead;
2. the shortening would drop a qualifier: ethnic (Peul, Wolof, Sérère, Toucouleur, Bambara, Diola, Lébou…), compass (Nord, Sud, Est, Ouest, Centre), land (Walo, Diéri, Ferlo), Kounda, or a descriptive noun (Marché, Gare, Plage…);
3. the name starts with or contains a settlement head that opens a person's, family's or holy place's name: Keur/Kër/Kerr, Darou/Dar, Médina/Madina, Médinatoul, Djannatoul, Boukhatoul, Saré, Sinthiou (and spellings), Sinthiang, Santhie, Gourel, Ouro/Wouro, Dara, Touba, Taïba, Missira, Hamdallaye, Baïti/Beyti;
4. the name holds a given name, a family name or an initial (Mamadou, Ousmane, Ndiaye, Diop, Fall, "M. Binta"…);
5. it is a joined name of several quartiers (two hyphens, or a hyphen and a space) or an "X de Y" name;
6. the result equals a commune or département seat, a regional capital or a large city of the region (Dakar, Touba, Rufisque, Pikine, Mbour, Banjul, Bamako, Bissau…), unless that town is the lieu's own (its zone seat or the nearest town within 15 km; the regional capitals and large cities are never "own");
7. the result equals the name (with numeral) of another lieu of the same zone;
8. it is listed in `COUNCIL` (short forms said but not documented, such as "Parcelles").

The first candidate is the provisional plate name, so the lieu can be numbered; the commune confirms it or chooses another candidate, and the lieu keeps its family and block. A flagged lieu with no fitting candidate keeps its cleaned name provisionally and is counted as over the limit.

**Aliases.** The official name and the map's other spellings are aliases of the plate name, so typing them decodes. If an alias's name key is claimed by two different plate names, it is dropped as an alias and listed in `aliasesDropped`.

**Ranges.** Same-normalised plate names share one national range (3.3): the name key is computed on the plate name.

**Source layer.** The inventory comes from OpenStreetMap place nodes (`neighbourhood`, `suburb`, `village`, `town`, `city`) and GeoNames populated places. A GeoNames place is dropped when an OSM node lies within 300 m of it, or within 1 km with the same name. Names that are institutions or squares ("Place …", "Ministère …", "Chez …") are dropped, and text in parentheses becomes an alias. It was frozen at first issue (20 October 2026). Curation with the communes (they run the quartiers) and, if it agrees, La Poste (its 4,143 locality names) continues through aliases and the plate-name choices above: an entry can gain aliases but never changes its index, family, digits or blocks.

**Assignment (point → lieu, `Lieux.nearest`):**

1. the nearest `neighbourhood`, `suburb`, `village`, `locality` or `extension` point of the same zone within 2.5 km;
2. else the nearest `town` point within 10 km;
3. else the nearest lieu of the zone.

Ties go to the lower index. The lieu is decided when the compound is first numbered and stored with it. It is never recomputed.

**Renamed or disputed places.** When a quartier is renamed, split by the commune, or claimed by two neighbourhoods, the **address does not change**. A new name becomes an alias, and the plate can carry either name.

### 3.3 One national range per name

A name is said without its town. So every lieu that shares a name, anywhere in Senegal, draws its numbers from **one national range for that name**, cut into one block per lieu. A number falls in exactly one block, so "name + number" decodes to exactly one lieu and one compound. The block table is `model/name-families.json` (built by `tools/name-ranges.py`), and each lieu carries its family, digits and blocks in `model/lieux.json`.

#### 3.3.1 Normalisation: which names are "the same"

Two place words are the same name when their **name key** is equal (`name_key`). The folding is deliberately generous: names that people can confuse by ear or in spelling must share one range, or two places would get the same remembered address. Over-folding costs nothing but a slightly longer range. The steps, in order:

1. `ñ` → `ny`, `œ` → `oe`, `æ` → `ae`; accents and case removed (Médina = Medina, Kër = Ker, Sacré-Cœur = Sacré Coeur).
2. Hyphens, apostrophes, dots and brackets become spaces; `St`/`Ste`/`Sainte` → `saint`.
3. A trailing numeral is dropped, with `numero`/`no` before it: HLM, HLM 2 … HLM 6 are one name; Pikine and Pikine 3 are one name (3.3.6 explains the numeral).
4. Leading articles and generic words are dropped when something follows: `le`, `la`, `les`, `l'`, `de`, `du`, `d'`, `quartier`, `village`, `hameau`. *Cité* is kept: "Cité Lamy" is a different name from "Lamy".
5. Spaces are removed (Keur Massar = Keurmassar).
6. French and Wolof spellings are folded: `ou` before a vowel → `w` (Ouakam = Wakam, Taoua = Tawa); other `ou` → `u` (Darou = Daru); `eu` → `e` (Keur = Kër); `kh` → `x` (Khoudoss = Xudoss); `th` → `t` (Thiès = Ties); `ph` → `f`; `dj` and `di` before a vowel → `j` (Ndiaye = Njaay, Diamaguène = Jamaguen); `gn` → `ny`; `c` before e/i/y → `s`; `ck`, `qu`, `q`, `c` → `k` (Mbacké = Mbakke); `y` → `i`; silent `h` dropped (Hamdallaye = Amdalaye, Missirah = Missira).
7. Doubled letters are collapsed (Gounass = Gounas, Salaam = Salam), then a final silent `e` is dropped (Ndiayène = Ndiayene, Darou Rahmane = Darou Rahman).

The variants stay as they are on plates and in the inventory; only the key is shared. The selftest checks the pairs above.

#### 3.3.2 Number length per name

The lieux of one name share one length **d**. With n₁ … nₖ compounds in the k lieux of the name at first issue, each lieu needs a block of `3 × nᵢ` numbers (room for three times today's compounds, about 30 years at Senegal's 3.7% urban growth, since 1.037³⁰ ≈ 2.97), rounded up to a multiple of the **grain**: 10 for 3 digits, 100 for 4 and 5 digits, and at least one grain. d is the smallest of 3, 4, 5 for which the blocks fill **at most 90% of the range**; the other 10% at least stays free for new lieux of the same name.

| d | Range | Allocatable at first issue (90%) | Always kept free | One lieu alone fits up to |
|---|---|---|---|---|
| 3 | 100-999 (900 numbers) | 810 | 90 | 270 compounds |
| 4 | 1000-9999 (9,000) | 8,100 | 900 | 2,700 |
| 5 | 10000-99999 (90,000) | 81,000 | 9,000 | 27,000 |

A single lieu with more than 27,000 compounds is split along named sub-quartiers before first issue. The real counts for every name are in `model/name-families.json` and section 3.3.7.

#### 3.3.3 Blocks

Within a name's range the blocks are cut from the bottom, one per lieu, in the order (zone key, lieu index), each of the size computed in 3.3.2. Example, the name Médina (9 lieux, 5 digits): Dagana 10000-10399, **Dakar 10400-17699**, Foundiougne 17700-18999, … **Saint-Louis 19500-22799**, **Ziguinchor 22800-23299**; 23300-99999 is free. "Médina 12 150" is in Dakar, "Médina 23 150" in Ziguinchor, and no number is in both.

Inside its block a lieu is numbered as before (7.3): Hilbert order, numbers spread evenly over the block.

#### 3.3.4 Names that do not fit: one qualifier, decided once

If the lieux of one name cannot fit 5 digits together, the largest of them take **one established qualifier that people already say**, decided once per name with the commune and listed in `tools/name-ranges.py` (`QUALIFIERS`). The qualifier becomes part of the place word and so of the name key, giving that lieu its own range (as "Médina Baye" already is a name of its own, apart from "Médina"). It is never a zone or département name added at the end, and never an ordinal.

**With the counts of 18 October 2026, no name needs a qualifier.** The fullest 5-digit range is Darou Salam (23 lieux in 17 zones, 22,091 compounds): 75.1% of its range is allocated. The same rule covers a new lieu after first issue whose block does not fit its name's free space: it takes a qualifier, decided once with its commune. 159 names are already 75% allocated or more (most are 3-digit village names shared by two or three villages); the 20 shared by most lieux are listed in `name-families.json` (`summary.watch`).

#### 3.3.5 Stability

The block table is **frozen at first issue**. Afterwards:

- a name's blocks are never renumbered, moved or shrunk;
- a new lieu with an existing name (curation, a new quartier) gets a new block from the top of the name's free space, of the size in 3.3.2 (`Lieux.add_lieu`);
- a lieu whose block is full gets a further block of one grain from the same free space (`Lieux.add_block`), then `<Lieu> Extension` (7.4);
- a lieu that is renamed keeps its block; the new name is an alias.

`allocate_families(…, frozen=…)` reproduces an issued table exactly and only appends; the selftest checks this.

#### 3.3.6 Decoding with no context

`find` reads the trailing digits as the number and the words before them as the name. The name key gives the family, and the family gives d, so the number is **the last d digits**; any digits before them must be the lieu's own trailing numeral (`HLM 5 17 395` and `HLM 17395` are HLM 5's compound 17395; `HLM 3 17395` is refused). The number then falls in exactly one block. A zone name given after a comma is only checked: a wrong one makes the address invalid, it never re-routes it to another lieu. An address whose number is in no block is not issued.

#### 3.3.7 The real counts (18 October 2026)

From the inventory of 14,997 lieux, by plate name (`tools/name-ranges.py`; `name-families.json`, `summary.plateNames` has the same counts on the full official names as `before`):

| | Count |
|---|---|
| Name keys | 11,043 (12,344 on the official names) |
| Names that repeat | **1,974**, over **5,928 lieux** (1,322 names in several zones, 652 within one zone only), holding 41.9% of compounds (official names: 1,404 names, 4,057 lieux, 29.2%) |
| Lieux per repeated name | 2: 1,224 names; 3: 380; 4: 137; 5-9: 187; 10-32: 46 |
| Shared ranges by length | 3 digits: 902; 4 digits: 964; 5 digits: 108 |
| Largest shared range | **Darou Salam**: 23 lieux in 17 zones, 22,091 compounds, 5 digits, 75.1% allocated |
| Most repeated | Ndiayène: 32 lieux in 18 zones, 8,754 compounds, 5 digits, 31.0% allocated |
| Other large shared ranges | Gounas (3 lieux, 21,590 compounds, 5 digits), Diadie (2, 15,672), Bayakh (5, 14,338), Vélingara (18, 13,376), Malikounda (4, 12,587) |
| Names needing a qualifier | **0** |
| Plate names | 4,208 official names over the limit; 10,763 kept, 100 cleaned, 3 documented short forms, 1,016 distinctive; 3,116 to the commune (one of them a cleaned name), 172 of them over the limit provisionally; 55 aliases dropped |

Number lengths, share of compounds: 3 digits 20.0%, 4 digits 46.6%, 5 digits 33.4% (on the official names: 22.9%, 45.9%, 31.3%; with one range per lieu instead of per name: 29.7%, 45.4%, 24.9%). The lengths rise slightly because a name's lieux add up, because each name keeps 10% of its range free, and because shorter plate names bring more lieux under one name.

### 3.4 Reading and typing

- **French.** The place word, then the number as above. A pair starting with 0 is read "zéro sept".
- **Wolof.** The place word, then the digits one by one: benn, ñaar, ñett, ñeent, juróom, juróom benn, juróom ñaar, juróom ñett, juróom ñeent, tus (0). Wolof 3/4 (ñett/ñeent) and 8/9 (juróom ñett/juróom ñeent) sound alike. That is why the app always shows the place and a photo of the building before navigating.
- **Typed input** (`find`) folds the place word to its name key (3.3.1), so case, accents, hyphens, apostrophes and French/Wolof spellings do not matter. It accepts a trailing check letter, and a trailing `, <zone name>` which is only checked (3.3.6). It never uses the user's area or position: one address, one place.

### 3.5 Spot codes

A spot code `KEY eeee nnnn` (section 5; no check letter, an older code ending in one still decodes) covers any point that has no compound: a field, a pitch in a market, a bus stop, an empty plot before "Add my home". It is computed offline; its only letters are the zone key.

### 3.6 Coverage mask: government addresses first

**Rule:** where the government already gives addresses, N-Ways uses the government's data and shows the address exactly as the government writes it, **first**. Every compound still has its N-Ways address beside it, official areas included, so one kind of address works for every home in Senegal. An official address is the one people are held to in law and administration; showing it first means N-Ways never competes with it.

Each lieu carries a `coverage` value, and together these values form the coverage mask:

| `coverage` | Meaning | What the app shows | Plates |
|---|---|---|---|
| `ann` | The ANN has published addresses for the area | the ANN address as written, first, with the N-Ways address beside it | none from N-Ways |
| `official-municipal` | The municipal street-addressing programme (blue plates, street codes such as PE-44, metric door numbers) covers the area, and its data is in use or obtainable | the street address as written (e.g. "120 Rue PE-44, Point E", or a named street with its number), first, with the N-Ways address beside it; until a door's official number is obtained, the N-Ways address | none from N-Ways |
| `nways` | No official door-level address exists | the N-Ways address (`Ouakam 2512`) | N-Ways plates and stickers |

In the registry each compound carries `coverage`: `official` when its door's street and number are known (shown first), `official-pending` in a lieu of the municipal programme whose door numbers aren't shared yet, empty otherwise.

La Poste postcodes do **not** put an area in the mask: they are delivery-office zones, not door addresses. Every compound carries its `laPosteCode` whatever its coverage.

**How the mask is drawn.**

1. **Evidence per lieu.** These count:
   - (a) an official dataset obtained from a commune, the ARTP, ADM or the ANN for the lieu;
   - (b) at least 3 OpenStreetMap streets in the lieu carrying the programme's street references (`ref=PE-44` style; 1,601 such streets nationally in the OpenStreetMap extract used);
   - (c) official plates confirmed by people at sampled doors.

   Any one of them puts the lieu in `official-municipal`. A lieu covered by an ANN publication becomes `ann`.
2. **Granularity.** The mask is drawn at the level of the lieu (quartier, village), because that is the unit the programmes numbered (for example 255 quartiers of Dakar in 2019) and the unit of the N-Ways address.
3. **Growth.** The mask only grows. When official coverage reaches a `nways` lieu, the lieu switches to the official status: the official address is shown first and the N-Ways address stays beside it, resolving to the same door, through the crosswalk built from the official data or from door confirmations. An address is never reissued.
4. **Every compound has a registry entry**, whatever its coverage. The canonical identifier (`SN-DKR-0080-2512-J`) is the join key for partners, the building profile and the crosswalk, and nobody has to see it.

## 4. Check letter

```
payload (address) = name family id (5 digits) ++ number (5, zero-padded)                e.g. "12107" "02512"
payload (spot)    = zone index (2 digits) ++ E digits ++ N digits
p = 0; for each digit d of payload: p = ((p + d) * 2) mod 11
value = (12 - p) mod 11                                        (ISO/IEC 7064 MOD 11-2)
CHECK = "FHJKMQRTWXZ"[value]
```

| Check letter | F | H | J | K | M | Q | R | T | W | X | Z |
|---|---|---|---|---|---|---|---|---|---|---|---|
| French name | effe | ache | ji | ka | emme | ku | erre | té | double vé | ixe | zède |
| Value | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |

The eleven letters are chosen from how French names letters:

- one of each rhyming set (bé cé dé gé pé té vé: only T is kept);
- one of each e-e pair (effe/esse, emme/enne, elle/erre: F, M and R are kept);
- J but not G (gé/ji are a classic francophone confusion);
- no vowels, no Y (i grec), and no O, I or L.

MOD 11-2 is an ISO standard (also used by ORCID). With 11 prime and weights 2^k mod 11, it detects **every single wrong digit and every swap of adjacent digits**. The selftest checks this exhaustively on 3,000 random payloads.

**What the address letter binds.** The name enters as its family id, the number as itself, and the lieu through the frozen block table: within a name each number belongs to exactly one lieu, so a letter that is right for "Médina 12 150" is right for one lieu only, Médina of Dakar. The zone and lieu indices are deliberately **not** in the payload. If they were, a typo that moves the number into another same-named lieu's block would change several payload positions at once, and the letter would miss it one time in eleven. With family + number, such a typo changes one position and is **always** caught: a machine form that carries Dakar's letter with the number 22 150 (a slip from Dakar's 12 150 into Saint-Louis's block) is refused. The selftest checks this for every Médina block, and `vectors.json` → `sameName` records one such slip per example. The canonical form keeps the zone key and lieu index for databases; `validate` checks them against the block table exactly, so a canonical code pointing to another lieu is refused whatever its letter.

**Errors in the remembered form**, which has no check letter, are caught in three ways:

- the place word must match the inventory (closed list, name key);
- the number must have the name's length, fall in a block, and be **issued**. With numbers spread at about one in three, a random one-digit slip lands on an unissued number about two times in three, and many slips land in no block at all;
- the app shows the compound's town, photo, class and street before routing. A slip that lands on an issued number of another same-named lieu ("Médina 22 150" for "Médina 12 150") shows **Saint-Louis**, not Dakar, at once. Systems that hold the canonical form catch this slip by its check letter.

## 5. Spot codes

### 5.1 Projection

Spot codes use **WGS 84 / UTM zone 28N** (EPSG:32628): Transverse Mercator, central meridian 15° W, scale 0.9996, false easting 500,000 m. The forward and inverse formulas are Krüger's series to n⁴ (Karney 2011), given in `sn_engine.py` (`utm_forward`, `utm_inverse`). They are accurate to well under a millimetre inside Senegal, whose east tip is 3.65° from the central meridian.

Why UTM 28N:

- Senegal sits almost centred on 15° W, so one projection covers the whole country with little distortion.
- The legacy national grid, Yoff / UTM zone 28N (EPSG:31028, Clarke 1880), uses the same projection on another datum. Senegalese surveyors already read coordinates in UTM 28N metres. Whether today's titres fonciers must use Yoff or NSGD2004 is unverified (existing-systems.md section 4).
- A spot code can therefore be read as a coordinate: E = originE + x × cell.

### 5.2 Encode

```
key  = zone lookup (2.2)
E, N = utm_forward(lat, lon)
x    = floor((E - originE) / cell);  y = floor((N - originN) / cell)
require 0 ≤ x, y < 10^digits
code = key + " " + x (zero-padded to digits) + " " + y (zero-padded)
# no check letter is written (people type spot codes); a code written with a trailing CHECK(index, x‖y) is still verified
```

### 5.3 Decode

Validate the code (section 4). Then the cell centre is E = originE + (x + 0.5) × cell and N = originN + (y + 0.5) × cell, and (lat, lon) = utm_inverse(E, N). The error is at most cell × √2 / 2: 0.7 m in Guédiawaye, 1.4 m in Dakar, 3.5 m in Touba, 7.1 m in rural zones.

A spot code encoded with the zone key given explicitly still decodes correctly even if the point lies outside that zone's outline, as long as it is inside the frame. This is how a point on a zone edge can keep the key of the zone its compound belongs to.

## 6. Building profile (per structure)

Every structure in the registry carries the profile below. Each attribute carries its **source** and **lastConfirmed** date.

| Field | Type | How it is filled |
|---|---|---|
| `class` | taxonomy code (6.1) | inference ladder (6.2) |
| `classConfidence` | 0-1 | from the rule that fired; people's confirmations raise it to 0.95 |
| `footprintM2`, `perimeterM` | number | from the footprint polygon, computed in UTM 28N |
| `heightM`, `heightSource` | number or null | OSM `height`, else OSM `building:levels` × 3.0 m, else **null**. The height value carried with the machine-learned footprints is a rendering filler (section 6.4) and is never used |
| `floors`, `floorsSource`, `rPlus` | integer, text | OSM `building:levels`, else height ÷ 3.0 m rounded (min 1), else 1 with source `default`; shown the Senegalese way as `RDC`, `R+1`, `R+2`… |
| `floorAreaM2`, `floorAreaIsEstimate` | number, bool | footprint × floors; marked as an estimate when floors is the default |
| `name` | text | **only for businesses and public buildings**, from OSM `name`, N-Ways places, or the building's owner. Never for homes |
| `status` | `existing` / `construction` / `ruin` / `demolished` | OSM `building=construction` / `ruins`, imagery, people |
| `entrances` | list | doors: position, kind (`main`, `shop`, `service`), `streetRef` + `metricNumber` when a plate is confirmed, confirmed-since date |
| `sources` | object | one entry per attribute: `osm:<tag>`, `ml:footprint`, `places:<category>`, `people`, `partner:<name>`, `default` |
| `lastConfirmed` | date per attribute | the last time the evidence was seen or confirmed |

### 6.1 Use classes (Senegal)

| Code | Class | Notes |
|---|---|---|
| `res.concession` | concession familiale | a structure in a multi-structure family compound |
| `res.maison` | maison basse / villa | a single house, RDC or R+1 |
| `res.immeuble` | immeuble d'habitation | R+2 and up, flats |
| `res.case` | case | round or small hut, rural |
| `res.annexe` | annexe | kitchen, toilets, store, boys' quarters, gatehouse inside a compound |
| `com.boutique` | boutique / commerce | |
| `com.marche` | marché / cantines | market hall or rows of stalls |
| `com.bureau` | bureaux, banque | |
| `com.entrepot` | entrepôt / magasin | |
| `com.station` | station-service | |
| `com.atelier` | atelier, garage, vulcanisateur | |
| `hot.hotel` | hôtel / campement / auberge | Saly, the Petite Côte, Cap Skirring |
| `hot.restaurant` | restaurant, dibiterie, café | |
| `gov.admin` | administration | ministries in Plateau and Diamniadio, gouvernance, préfecture, mairie, police, gendarmerie, poste |
| `edu.ecole` / `edu.daara` / `edu.universite` | school / Qur'anic school / university | daaras are recorded only from tags or people (6.2) |
| `san.hopital` / `san.centre` / `san.pharmacie` | hospital / centre, poste or case de santé / pharmacy | |
| `rel.mosquee` / `rel.eglise` / `rel.mausolee` | mosque / church / mausoleum | Touba's Grande Mosquée and mausolées |
| `ind.usine` | industrial | |
| `tra.gare` | gare routière, gare, port, aéroport | |
| `pec.quai` | quai de pêche, fumoir | fishing landing buildings (Soumbédioune, Kayar, Joal, Mbour) |
| `agr.magasin` / `agr.grenier` / `agr.ferme` | seed and groundnut stores (seccos) / granary / farm building | |
| `mix.immeuble` | mixed-use | R+2 or higher with a shop or service at street level |
| `chantier` | under construction | |
| `ruine` | ruin | |
| `inconnu` | unknown | |

### 6.2 Inference ladder (first rule that fires wins)

| # | Evidence | Class | Confidence |
|---|---|---|---|
| 1 | OSM `building=construction` / `ruins` | `chantier` / `ruine` | 0.9 |
| 2 | OSM `amenity=place_of_worship` (+ `religion`) | `rel.mosquee` / `rel.eglise` | 0.9 |
| 3 | other OSM `amenity` (townhall, police, school, hospital, marketplace, bank, fuel…) | per table in `sn_engine.OSM_AMENITY` | 0.9 |
| 4 | OSM `shop=*` | `com.boutique`, or `mix.immeuble` if floors ≥ 3 | 0.85 |
| 5 | OSM `office=government` / `government=*` / other `office` | `gov.admin` / `com.bureau` | 0.9 / 0.85 |
| 6 | OSM `tourism=hotel|guest_house|…`, `healthcare=*`, `industrial=*` | `hot.hotel`, `san.centre`, `ind.usine` / `pec.quai` | 0.8-0.9 |
| 7 | OSM `building=<specific value>` (house, apartments, school, mosque, warehouse, hut…) | per `sn_engine.OSM_BUILDING` | 0.85 |
| 8 | an N-Ways place inside the footprint (most common category) | per `sn_engine.PLACES`; shops on floors ≥ 3 → `mix.immeuble` | 0.7 / 0.6 |
| 9 | satellite (section 7.1, R1) | `res.annexe` | 0.4 |
| 10 | floors ≥ 3 and footprint ≥ 60 m² | `res.immeuble` | 0.45 |
| 11 | footprint < 25 m² in rural fabric | `res.case` | 0.5 |
| 12 | footprint ≥ 1,500 m², floors ≤ 2 | `com.entrepot` | 0.3 |
| 13 | member of a multi-structure compound | `res.concession` | 0.45 |
| 14 | 25-600 m² | `res.maison` | 0.45 |
| 15 | otherwise | `inconnu` | 0.2 |

People's evidence overrides every rule. Any of the following sets the class and a confidence of 0.95, settled by agreement as in section 7.5:

- the building owner's claim;
- two independent confirmations;
- a courier's delivery to a business door.

A **daara** is never inferred from shape, because many are family homes. It comes only from tags, N-Ways places or people.

### 6.3 Compound profile

| Field | Meaning |
|---|---|
| `use` | `residential-one-household` / `residential-multi-household` / `mixed` / `commercial` / `public` / `religious` / `industrial` / `unknown` |
| `useConfidence` | 0-1. Residential compounds default to `unknown households` (`residential-multi-household` is never inferred: Senegalese concessions often house several ménages, and only people can say so) |
| `plotAreaM2` | outline area if known (enclosure, Add my home, cadastral parcel), else null |
| `structures` | count, and the list of structure profiles in index order |
| `floorAreaM2` | sum over structures (estimate flag if any structure's floors are default) |
| `gates` | list: position, kind (`gate`, `entry`, `estate-gate`), source, confirmed-since |
| `estate` | the cité/estate this compound sits in (name + estate gate), if any |
| `laPosteCode`, `streetRefs`, `annId`, `nicad`, `lotissementPlot` | cross-references (section 10) |
| `groupingRule`, `groupingConfidence` | how the compound was formed (7.1) |
| `status` | `provisional` / `confirmed` / `retired` |

### 6.4 Heights of the machine-learned footprints

The Google and Microsoft footprints (via Overture Maps) carry no measured height in Senegal. The copy used to build the registry fills the missing value with `3.5 + 3.5 × (hash(id) % 1000) / 1000` metres for map rendering: all 4,264,275 footprints lie between 3.5 and 7.0 m, with 36 distinct values. The engine therefore **never** reads that value, unless a dataset flags a height as measured (`h_measured`).

## 7. Compounds and the registry

### 7.1 Grouping structures into compounds (`group_compounds`)

All distances are in UTM metres. The **gap** between two structures is the distance between their centroids minus the radii of their equivalent circles, r = √(area / π). This is a deliberate, reproducible approximation: true polygon distances would make the grouping depend on the geometry library used.

A structure is in **urban fabric** when its 250 m tile (UTM-aligned) holds at least 100 structures, i.e. 1,600 per km². The count is over **all** structures of the zone, so a sample or a partial download must carry each structure's whole-map tile count (`tile_count` in the samples).

The rules are applied in this order:

| Rule | Condition | Effect | Confidence |
|---|---|---|---|
| **R0 enclosure** | the structure's centroid is inside an enclosure: an OSM closed `barrier=wall/fence/hedge` way, a gated compound or site of the N-Ways map, a confirmed "Add my home" outline, or a cadastral parcel once available | all structures inside the smallest enclosing outline form one compound. An **estate** (kind `estate`, a cité with one gate) does not merge its houses: it becomes the `estate` of the compounds inside it | 0.9 |
| **R1 satellite** | footprint < 30 m² and gap ≤ 4 m (urban) or ≤ 8 m (rural) to a structure ≥ 30 m² | joins the nearest such structure's compound (kitchen, toilets, gatehouse, boys' quarters) | 0.6 |
| **R2 rural concession** | rural fabric; both footprints < 120 m²; gap ≤ 6 m | single-linkage clusters of cases and small houses, at most 30 structures | 0.5 |
| **R3 people** | "these buildings are one home" / "this is a separate home", from the building's owner plus one confirmation, or two independent confirmations | merge or split | 0.95 |
| (none) | | the structure is its own compound | 0.7 |

Two **main** structures (≥ 30 m²) in urban fabric are **never** merged by shape alone. In Dakar's Médina, in Pikine and in Touba, houses touching wall to wall are separate concessions. Only an enclosure or people can join them.

### 7.2 Gates

The gate is the compound's primary entrance, and navigation ends there, not at a footprint centroid. Gate sources, in order of trust:

1. a confirmed N-Ways door or gate;
2. an "Add my home" gate;
3. an OSM `barrier=gate|entrance|…` or `entrance=*` node on or within 5 m of the compound's extent;
4. a gate in the N-Ways routing network.

A compound without a known gate routes to the point of its outline nearest the road, flagged "gate unknown".

### 7.3 Registry build order (first issue of a zone)

1. Collect the zone's structures. They are assigned by `adm2`/`adm3`, or by zone lookup of the centroid. A structure whose centre, or a compound whose entrance, lies more than 300 m outside the national border is dropped before any lieu or number is given (2.3).
2. **Group into compounds (7.1) before numbering.**
3. For each compound, compute the area-weighted centroid of its structures and its extent (the largest distance from that centroid to a structure's circle).
4. Assign each compound its **lieu** (3.2). Group the lieux into name families and cut each lieu's block from its name's national range (3.3); this fixes the number length of every lieu of the name.
5. Within each lieu, order its compounds by the **Hilbert index** of their centroid on a 2¹⁶ × 2¹⁶ grid over the zone frame (`hilbert_key`). Ties are broken by E, then N.
6. Spread the numbers over the lieu's block: with n compounds and block [lo, hi], compound i (0-based) gets `lo + floor((i + 0.5) × (hi − lo + 1) / n)`. With the headroom of 3, there are on average two free numbers between neighbours.
7. Within a compound, index the structures: 1 = the largest, then by distance from it (ties by structure id).
8. Publish `registry/<KEY>.csv.gz`, one address per row (`registry/README.md`): the canonical, remembered and written forms, lieu and number, status (`provisional` until people confirm it), the entrance and its spot code, the compound's class, use, kind, structures and floor area, the La Poste postcode where mapped, and the official address where the commune numbered the door. `registry/anchors/<KEY>.csv.gz` gives each compound's centroid, the point step 5 orders by, row for row.

Neighbours get close numbers ("Ouakam 2512" is next to "Ouakam 2515"), the way house numbers run along a street.

### 7.4 After the first issue: new compounds (`insert_in_lieu`)

Existing numbers never change. A new compound's gate must lie in a zone and inside the national border or within 300 m of it (2.3); an entrance never moves beyond that limit either. For a new compound with its gate at (E, N):

1. Find its lieu (3.2) and its Hilbert neighbours among the lieu's issued compounds in its first block: `a` = the number before, `b` = the number after (or the ends of the block).
2. If `b − a ≥ 2` and `mid = (a + b) // 2` is free, issue `mid`.
3. Otherwise the lieu is full **at that spot**. Issue the lowest free number of the lieu's further blocks; if it has none free, give the lieu one more block of one grain from its name's free space (3.3.5) and issue its first number.
4. When the name's range has no free space left, the lieu continues as `<Lieu> Extension`: a new lieu with the next index in the zone. The issuer refuses the address until the commune has named the extension, then adds it as a lieu (`Lieux.add_extension`); the reference `reserve_provisional` shows the extension it would add. Its name is new, so it gets a national range of its own (a new family, same number length). This matches how Senegalese towns already name their growth (Keur Massar Extension, Médina Gounass Extension). The plate name rule applies: "<Lieu> Extension" is over 12 characters for almost every name ("Ouakam Extension" has 16), so the official name is "<Lieu> Extension" and the new lieu is flagged `needsCouncilChoice`: the commune gives it a plate name, often the one people already use for the new district, before plates go up (3.2.1).

### 7.5 Stability

| Event | Rule |
|---|---|
| Compound demolished | Its address is **retired**, never reissued. |
| Two compounds merged (people, R3) | Both addresses stay valid; the newer one becomes an alias of the older. |
| A compound split | The part with the gate keeps the address; the other part gets a new number (7.4). |
| A new structure inside | It gets the next structure index. |
| A structure demolished | It keeps its index, marked retired. |
| Regrouping after better data (walls mapped, cadastre) | **Issued addresses never change**; the new grouping is applied only through the merge and split rules above. |
| A quartier renamed, split, or its boundary disputed | The address never changes; the new name is added as an alias (3.2). The lieu keeps its block. |
| A new lieu with an existing name | It gets a new block from the name's free space (3.3.5); no other lieu's block or number changes. |
| A lieu's block used up | A further block from the name's free space, then `<Lieu> Extension` (7.4). |
| Zone outlines improved | Never: zones are frozen (2.1). |

## 8. "Add my home" (new compounds created by their owners)

The flow text the app shows: *« Cette adresse n'est pas un titre foncier. Elle ne prouve ni la propriété ni le droit d'occuper la parcelle. »* ("This address is not a land title. It proves neither ownership nor the right to occupy the plot.")

| Step | What happens | Checks |
|---|---|---|
| 1. Gate | The person stands at the gate. GPS is averaged for 10 s (at least 5 fixes with reported accuracy ≤ 15 m), and one photo is taken of the gate from the street. | Accuracy recorded; photo kept |
| 2. Outline | One of: **(a)** tap the corners on satellite imagery; **(b)** walk the boundary inside the wall with the camera (ARKit/ARCore world tracking gives the shape to centimetres, anchored by GPS averaged along the walk and snapped to imagery and nearby footprints; phone GPS alone is 3-10 m and too rough); **(c)** import the plot's survey plan: beacon coordinates typed or photographed from the plan, with the datum chosen from Yoff / UTM 28N (EPSG:31028), NSGD2004 / UTM 28N or WGS 84 / UTM 28N (EPSG:32628), plus the NICAD or the lotissement plot number if the owner has one | Closed loop; the gate lies on the outline (≤ 3 m); area 20-20,000 m²; the GPS and AR tracks agree within 5 m; an imported plan within 30 m of the GPS gate (a larger offset suggests the wrong datum, since Yoff and WGS 84 differ by tens of metres) |
| 3. Describe | Households (one / several / not said), structures, floors (RDC, R+1…), use | |
| 4. Provisional address | The registry runs `reserve_provisional`. If the gate falls inside an existing compound's extent, or the outline overlaps an existing compound or plot, the request is **flagged, not issued**. Otherwise the gate gets its lieu (3.2) and the free number midway between its Hilbert neighbours in that lieu's block (7.4), else a number from the lieu's further block, else the next number of `<Lieu> Extension`, with status `provisional`. The address can go on the gate immediately. **In an official addressing area (3.6)** the status is `provisional-alias`: no N-Ways plate is made, and the app tells the owner to ask the commune for the official number. The N-Ways address is only an alias until that number is known. | Single issuer, so no two homes share an address |
| 5. Confirmed | The status becomes `confirmed` after any of: a delivery or arrival at the gate by someone else; 30 days without a dispute from a neighbour; new imagery or footprints showing the structures | A dispute freezes the compound at `provisional` (GOVERNANCE.md) |

**Offline.** With no network, the phone shows the gate's **spot code** at once (section 5), and the person can write it down. The address is issued on the next connection. Only the registry issues addresses.

**Kept:** the outline, the averaged gate position, the gate photo. **Not kept:** video, the AR session, interior images, people's names.

**Test vectors.** `vectors.json` → `addMyHome` records two requests per sample, both computed against that sample's own registry:

- a gate 0.7 m from a compound's centroid, which is **flagged** (inside an existing compound);
- a gate 40 m beyond the sample's easternmost compound, which receives a **provisional** address: its lieu, its number (the midpoint between its Hilbert neighbours), all four forms, and the gate's spot code.

## 9. Cross-references to other systems

| Field | System | Rule |
|---|---|---|
| `laPosteCode` | La Poste Sénégal 5-digit postcode | Taken from OSM `addr:postcode`, else from La Poste's locality list **only with La Poste's permission**, else empty (the app links to the La Poste finder). Shown on the place card next to the address, never part of it |
| `streetRefs` | Municipal street plates (`PE-44`) and metric numbers | Per door, once confirmed; shown as "PE-44 n° 120" |
| `annId` | Adressage Numérique National | Filled when the ANN issues identifiers. The ANN address is then shown first (GOVERNANCE.md) |
| `nicad` | Cadastral parcel identifier (DGID) | When the owner gives it or the cadastre publishes it |
| `lotissementPlot` | Lotissement name + plot number | From the owner or a survey plan |
| Plus Code | Open Location Code | Computed from the gate or spot position, for sharing outside Senegal |

## 10. Offline behaviour and shipped files

| File | Size | Needed for |
|---|---|---|
| `model/zones.json` | 10 kB | every function |
| `model/zones.geojson` | about 1 MB | zone lookup for spot codes and Add my home |
| `engine/data/border.geojson` | about 70 kB | the national border (2.3): issuing, entrance moves and lookups by position |
| `model/lieux.json` | about 6.5 MB (14,997 lieux, with their plate and official names, families and blocks) | `find`, `address_forms`, `validate`, lieu assignment |
| `model/name-families.json` | about 1 MB | the frozen block table (registry build only; the app needs `lieux.json` alone) |
| `registry/<KEY>.csv.gz` | about 30 bytes per address compressed | the full registry of one zone |
| `registry/anchors/<KEY>.csv.gz` | about 18 bytes per address compressed | each compound's centroid, for issuing new numbers exactly as the issuer does |
| app subset `<KEY>.idx` (built for the app, not published here) | about 12 bytes per compound (lieu, number, E, N as integers): Dakar's zone fits in about 1 MB | "Votre adresse" and "where is Ouakam 2512?" offline |

Spot codes, validation and the spoken forms need only the zone files. Resolving an address to a gate offline needs the zone's index file, which the app downloads for the zones a person uses (home, work, delivery area).

**The registry server.** `server/` loads `registry/` into SQLite and serves the lookups (`/v1/codes`, `/v1/find`, `/v1/at`, `/v1/near`, `/v1/verify`, spot codes, zones and lieux) over HTTP. On the deployment designated as Senegal's issuer it also issues addresses (`POST /v1/codes`) by sections 3.2, 7.4 and 8, with the issuer's distances (a compound is found within 12 m of its entrance; a new compound within 3 m of one is the same building) and the national border of 2.3 (a point more than 300 m outside it is refused with `422 outside`). See `server/README.md` and `docs/api.md`.

## 11. Test vectors

The vectors are produced by `python3 sn_engine.py vectors --write` and stored in `engine/reference/vectors.json`. `selftest` recomputes them and fails on any difference; `python3 -m unittest test_sn` runs the selftest and the tests of the national-uniqueness rule. They cover:

- `spot`: nine places, each with its code, decoded centre, error and French and Wolof readings;
- `addressCheck`: check letters for four (name family, number) pairs, with the payload;
- `sameName`: twelve lieux that share a name with another lieu (three Médinas in Dakar, Ziguinchor and Saint-Louis; Pikine in Diourbel and Saint-Louis and Pikine 3; Darou Salam in Pikine and Touba; Gounas (official name Médina Gounas) in Guédiawaye and Vélingara; HLM 2 and HLM 5), each with its block, an address in it, what `find` returns with no context (exactly that lieu), and a one-digit slip into another same-named lieu's block, refused once the check letter is given;
- `plateNames`: (a) `long`: four long official names and their plate names (S.I.C.A.P. Liberté Six → Liberté 6, Saly Portudal → Saly, Mbenguène Diawar → Diawar, Parcelles Assainies → Parcelles, provisional), each with an address and what `find` returns for the plate name and for the official name typed (the same lieu); (b) `collide`: two pairs whose plate names are the same only after shortening (Diawar / Mbenguène Diawar, Gabou / Massara Gabou): one family, two blocks, and each address decodes to its own lieu;
- `numbers`: written and spoken forms of 3-, 4- and 5-digit numbers;
- `samples`: the three real 300 m samples (`samples/dakar-medina.csv`, `samples/touba.csv`, `samples/bambey-village.csv`, OSM + Google/Microsoft footprints) grouped, assigned to lieux and numbered, with their first five addresses in all forms. The numbers come from the sample alone: the national first issue numbers each whole lieu at once, so its numbers will differ;
- `addMyHome`: see section 8.

## 12. Versioning

A change to any algorithm, constant, zone field, frozen lieu field, the name normalisation (3.3.1) or an issued block bumps the major version and is not allowed for issued addresses (GOVERNANCE.md). Adding blocks (3.3.5) is not a change. Profile rules (6.2) may change in minor versions: they change classes, never addresses.
