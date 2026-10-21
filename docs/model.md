# The N-Ways addressing model for Senegal

Every choice below is argued from Senegal's own facts. The model was fixed on 18 October 2026 and the addresses were issued on 20 October 2026. The engine is specified in [engine/SPEC.md](../engine/SPEC.md), the evidence on existing systems is in [existing-systems.md](existing-systems.md), and the numbers are in `model/*.json`.

## 0. The format in one line

> **Ouakam 2512**: a place word people already use (quartier, village, cité), at most 12 characters and 2 words (section 1.5.1), then a 3- to 5-digit number like a house number. **It is unique in all of Senegal on its own**: no town after a comma, no zone, no position of the phone is needed to tell it apart (section 1.6).

| Form | Example | Where |
|---|---|---|
| Remembered | `Ouakam 2512` | said, written, typed |
| Written | `OUAKAM 2512 · DAKAR` | plates, stickers, forms |
| Canonical | `SN-DKR-0080-2512-J` | APIs, QR codes |
| Spot (no compound) | `DKR 5553 1512` | fields, market pitches, empty plots |

## 0.1 Government addresses first: the coverage mask

**Where the government already gives addresses, N-Ways uses the government's data and shows the address exactly as the government writes it.** N-Ways addresses are proposed only where nothing official exists. An official address is the one people are held to in law and administration, so a second address beside it must never compete with it.

In Senegal this applies to two systems:

- **Municipal street addressing.** Blue plates, street codes (PE-44, SC-15, OKM-1) and metric door numbers cover parts of Dakar, Guédiawaye, Pikine, Saint-Louis, Thiès, Kaolack, Diourbel, Tambacounda and Ziguinchor. Wherever that data is in use or obtainable, the place card shows "120 Rue PE-44, Point E", or the named street and number, as written. N-Ways puts up no plates there.
- **The ANN.** Once it publishes, it takes over each area it covers. Every N-Ways address there becomes an alias that resolves to the ANN address.

La Poste's 5-digit postcodes are delivery-office zones, not door addresses, so they do not count as coverage. The door-level model applies, and each compound maps to its postcode.

The mask is drawn per **lieu** (quartier or village), which is the unit both the programmes and the N-Ways address use. A lieu is `official-municipal` on any one of these:

- an official dataset (from a commune, the ARTP, ADM or the ANN);
- 3 or more OpenStreetMap streets carrying the programme's street references (there are 1,601 such streets in the OpenStreetMap extract used);
- plates confirmed by people at its doors.

A lieu covered by the ANN is `ann`. Every other lieu is `nways`.

The mask only grows. When official coverage arrives, the lieu's N-Ways addresses are retired as primary addresses and kept as aliases, and no address is ever reissued (SPEC 3.6). The measured share of compounds in the mask today is in section 10.

Inside the mask, before a door's official number is known, the app shows the N-Ways address marked *temporary, until the official address is confirmed*. A courier can still find the house, but no N-Ways plate goes up.

## 1. The first criterion: people must remember it

An address that people do not remember is not used, and an address that is hard to obtain is not held. The model therefore has two first criteria: the address must be easy to remember, and easy to get. Every other choice is subordinate to them.

### 1.1 What Senegalese people already remember

- **Place names.** People give their address by quartier and landmark: "Ouakam, près de la mosquée de la Divinité", "Médina, rue 15". In the countryside it is the village, sometimes with the nearest town ("Keur Mbaye, vers Ngoye"). Every person already knows their quartier or village. It costs nothing to learn.
- **Numbers in pairs.** Mobile numbers have nine digits (77 123 45 67), and everyone reads and remembers them in pairs in French: "soixante-dix-sept, cent vingt-trois, quarante-cinq, soixante-sept". House numbers on the blue plates are 2-4 digits ("n° 120").
- **Not letter codes.** P.O. boxes (BP 1534) and postcodes (12500) are numbers too. No everyday Senegalese identifier mixes letters and digits, except car plates (DK-1234-AB), which people read off the plate rather than recall.

### 1.2 Options evaluated

| Option | Example | What people must remember | Assessment |
|---|---|---|---|
| A. Alphanumeric grid code | `DKR 45 12 78 K` | 3 letters + 6 digits + 1 letter = 10 symbols, of which 4 are letters with French names | Hard. French letter names rhyme (bé, cé, dé, gé, pé, té, vé) and G/J are confused ("gé"/"ji"). The key "DKR" is new knowledge. Rejected as the remembered form; kept for spot codes, which are rarely remembered. |
| B. Digits only | `07 0080 4512` (zone, place, number) | 10 digits, the first six meaningless to the holder | Keypad-friendly, but 10 digits is a phone number nobody gave you, and the place is invisible. Rejected. |
| C. Plus Code | `7C2P+M4 Dakar` | 6-8 alphanumeric characters + town | Free and open, but it has letters, no building identity and no meaning for people. Kept as a cross-reference for sharing outside Senegal. |
| **D. Place word + short number** | `Ouakam 2512` | a word they already know + 3-5 digits | **Chosen.** Only the number is new: 3-5 digits is within what people hold for a house number or a phone-number chunk. It reads the same in French and Wolof, works on any phone keyboard, suits people who read little, and says roughly where the place is. |

### 1.3 Why the check letter is not in the remembered form

A check character catches typos, but the remembered form has to be as short as possible, and every character printed for people is one more to copy wrong. So the check letter (`J` in `SN-DKR-0080-2512-J`) is carried only in the canonical form, for systems: it is never printed on plates or shown to people, and **never has to be remembered**. In the remembered and written forms, errors are caught in three ways:

1. the place word must exist in the inventory, matched with fuzzy spelling;
2. the number must have the name's length, fall in a block and be issued; measured over the registry, 76.1% of one-digit slips land on no issued address, 22.6% on another compound of the same lieu and 1.3% on a same-named lieu elsewhere (paper, section 6.4);
3. the app shows the compound's town, photo, class and street before it routes, so the person sees immediately if it is the wrong house, or the right name in the wrong town.

In the canonical form, the letter also catches every one-digit slip from one same-named place into another (section 1.6).

### 1.4 The arithmetic: how long the number must be

Each **name** has one national number range, shared by every lieu that bears it (section 1.6). Each lieu of the name needs a block of **3 ×** its compounds at first issue, rounded up to a round ten (3 digits) or hundred (4-5 digits). The number length d of the name is the smallest for which all its blocks fill at most 90% of the range, so at least 10% stays free for new lieux of that name.

| Digits | Range | One lieu alone fits | Typical name |
|---|---|---|---|
| 3 | 100-999 | ≤ 270 compounds | a village, a small quartier, a cité, or a few small villages sharing a name |
| 4 | 1000-9999 | 271-2,700 | an urban quartier, or a name shared by many villages (Hamdallaye: 21 villages) |
| 5 | 10000-99999 | 2,701-27,000 | a very large quartier (to split along sub-quartiers during curation), or a big name shared across towns (Darou Salam, Médina, Pikine) |

Why 3×: Senegal's urban population grows about 3.7% a year (ANSD), and 1.037³⁰ ≈ 2.97, so 3× is about 30 years of growth before a lieu fills. A lieu that does fill takes a further block from its name's free space, then continues as `<Lieu> Extension`, which is how Senegalese towns already name their growth.

The real distribution, computed from the N-Ways building map, is in section 10, `model/lieux-stats.json` and `model/name-families.json`.

### 1.5 How the place word is chosen

- **Layer.** Quartiers in towns, villages in the countryside, cités where a cité is what people say ("Cité Lamy"). The inventory comes from OpenStreetMap place nodes and GeoNames, filtered and de-duplicated (SPEC 3.2), and was frozen at first issue. Curation with the communes, which run the quartiers, and, with its permission, a check against La Poste's 4,143 locality names continue through aliases and plate names; neither ever changes an issued address.
- **Assignment.** A compound takes the nearest quartier or village point within 2.5 km in its zone, else the nearest town within 10 km. This is fixed when it is first numbered and never recomputed.
- **Duplicates.** Senegal repeats names: once shortened to plate names (section 1.5.1), 1,974 names are borne by 5,928 lieux. They are told apart by their **numbers**, never by context (section 1.6). The nearest town of same-named lieux in one zone ("Keur Mbaye, near Ngoye") is shown on the place card, and is never part of the address.
- **Spelling variants.** Wolof and French spellings (Ouakam/Wakam, Mbacké/Mbakke, Thiès/Thies), names with and without hyphens and accents, and long official names all resolve as aliases.
- **Renamed, split or disputed quartiers.** The address never changes; a new name is added as an alias. This matters in Senegal, where quartiers are renamed, communes are re-cut (Keur Massar became a département in 2021) and boundaries between quartiers are often disputed.

### 1.5.1 The plate name: at most 12 characters and 2 words

Names taken raw from the map ("Keur Serigne Ablaye Yakhine", "Parcelles Assainies", "S.I.C.A.P. Liberté Six") make an address too long to say or remember. So each lieu has two names:

- the **official name**: the full name from the map or the commune's list. It is printed in small type on the place card and the plate, for context, and it is still accepted when typed, but nobody has to say it;
- the **plate name**: the name in the address, **at most 12 characters** (letters, spaces, hyphens and apostrophes count one each; an accented letter is one) and **at most 2 words** (de, du, des, la, aux... do not count; a hyphen separates words: Sacré-Cœur is 2 words). A trailing sector numeral counts in the characters, not as a word: "Liberté 6", "HLM 5".

The whole remembered address stays short: "Ouakam 2512", "Liberté 6 16 021", "Saly 18 571". The longest today, outside the names the communes still choose, is "Yeumbeul Sud 20 699" (19 characters).

**How the plate name is derived** (`tools/sn_plates.py`, using the rule in `engine/reference/plate_names.py`; SPEC 3.2.1), in this order:

1. **A short form people already say, with a written source**, wins: "Saly" for Saly Portudal ("ou couramment Saly", SOURCES N1) and "Plateau" for Dakar-Plateau (N2).
2. **Cleaning.** A trailing numeral is split off and written in digits ("S.I.C.A.P. Liberté Six" → "Liberté 6", "Gorom Trois" → "Gorom 3"). Then the following are dropped: generic words (Quartier, Village de, Hameau, Lotissement, Zone, Secteur, Campement), developer scheme labels (S.I.C.A.P., Sicap), text in brackets or after a slash, and a second spelling after "ou". Acronyms lose their dots (H.L.M. → HLM). **"Cité" is not dropped from a name that fits**: "Cité Lamy" is what people say, and Cité Lamy is not Lamy. It is only the first word to go when the name is too long.
3. If the cleaned name fits, it is the plate name. Otherwise the candidates are the runs of **whole words** that fit; a word is never cut. They are ranked by how rare their words are among all of Senegal's lieu names.
4. The best candidate is taken automatically only when it is clearly ahead and none of the Senegal rules below applies. Otherwise the lieu is flagged **`needsCouncilChoice`** with up to 3 candidates. The first candidate is used provisionally so that the lieu can be numbered, and **the commune confirms it or chooses another candidate**; the lieu keeps its numbers either way.

Senegal rules that send a name to the commune rather than shorten it automatically:

- **Names of a person's or a family's place.** Keur ("house of", Wolof), Darou/Dar, Médina, Djannatoul and Boukhatoul (Arabic), Saré, Sinthiou, Gourel, Ouro (Pulaar "village, hamlet of"), Touba, Taïba, Missira, Hamdallaye: "Keur Momar Sarr" is the village of Momar Sarr, and any cut drops part of his name. The same holds for any name holding a given name or a family name (Ousmane, Mamadou, Ndiaye, Diop, Fall...).
- **Qualifiers.** Ethnic qualifiers (Peul, Wolof, Sérère, Toucouleur, Bambara, Diola...), compass words (Nord, Sud, Est, Ouest, Centre) and land qualifiers (Walo, Diéri, Ferlo) tell two villages apart: "Nguékokh Wolof" and "Nguékokh Sérère" are never both cut to "Nguékokh" without the commune.
- **Joined names.** Communes named after several quartiers (Mermoz-Sacré-Cœur, Gueule Tapée-Fass-Colobane, Fann-Point E-Amitié) and "X de Y" names (Cap des Biches, Pointe des Almadies) are never cut automatically.
- **Well-known towns.** A shortened name never becomes the name of a commune or département seat, a regional capital or a large city of the region (Dakar, Touba, Rufisque, Banjul, Bamako...), unless that town is the lieu's own; a quartier is never called "Dakar" or "Touba" alone.
- **Another lieu of the zone.** A shortened name that equals another lieu's name in the same zone ("HLM Grand Yoff" → "Grand Yoff") goes to the commune.
- **Short forms said but not documented.** "Parcelles" for Parcelles Assainies is the usual short form in speech, but we found no written source for it; it is the first candidate and the commune confirms it. Joal-Fadiouth joins two villages; the commune chooses.

**The counts** (18 October 2026, `model/name-families.json`, `plateNames`):

| | Lieux |
|---|---|
| Official names over the limit | **4,208** of 14,997 (4,154 over 12 characters, 1,474 over 2 words) |
| Kept as they are | 10,763 |
| Cleaned (generic word, scheme label, acronym, numeral in digits) | 100 |
| Documented short form | 3 |
| Most distinctive one or two words | 1,016 |
| To the commune (`needsCouncilChoice`) | **3,116** (one of them a cleaned name, "Richard Toll", that would equal a well-known town), of which 172 stay over the limit provisionally: no candidate fits (a single word over 12 letters such as "Diabrikindiong", or only qualifiers and heads left: "Touba Mosquée") |

**Typing the official name still works.** The official name and the map's other spellings are aliases of the plate name. An alias that two different plate names would claim is dropped, so that a typed name never leads to two places: 55 official names are dropped this way, listed per lieu (`aliasesDropped`) in `model/lieux.json`.

**Same plate names share one range** (section 1.6). Shortening brings more lieux under one name: "Diawar" and "Mbenguène Diawar" now share the Diawar range, in two blocks, and "Diawar 1419" and "Diawar 4085" are two different places.

### 1.6 Same names: one national range per name

Many places in Senegal share a name. Same-named places could be told apart by context: the zone said after a comma ("Medina 150, Ziguinchor" against the Médina of Dakar), the user's area, or a qualifier in brackets ("Keur Mbaye (Ngoye)"). None of these survives everyday use: a name is said without its town, and a courier in Dakar who hears "Médina 150" goes to Dakar's Médina. **The remembered address must be unique in the whole country on its own.**

**The rule.** Every lieu whose name is the same once normalised, anywhere in Senegal, draws its numbers from **one national range for that name**. The range is cut into one block per lieu, each with room for three times its compounds, and at least 10% of the range stays free for new lieux of the name. A number falls in exactly one block, so "name + number" names one lieu and one compound:

| Remembered | Is | Block of the name's range |
|---|---|---|
| **Médina 12 149** | Médina, Dakar | 10400-17699 |
| **Médina 20 096** | Médina, Saint-Louis | 19500-22799 |
| **Médina 23 151** | Médina, Ziguinchor | 22800-23299 |
| **Pikine 12 150** | Pikine, Diourbel | 10000-20899 |
| **Pikine 22 150** | Pikine, Saint-Louis | 20900-29999 |
| **Darou Salam 26 690** | Darou Salam, Pikine | 23200-45799 |
| **Darou Salam 50 859** | Darou Salam, Touba | 46200-76599 |
| **HLM 5 17 394** | HLM 5, Dakar (HLM, HLM 1 … HLM 6 share one range) | 17100-18399 |

Médina has 9 lieux, all 5 digits; 23300-99999 is still free. "Ouakam" is borne by one lieu only, so Ouakam's block is 1000-3399 and "Ouakam 2512" is its compound; "Ouakam 4512" does not exist.

**Which names are "the same".** The normalisation folds everything people can confuse by ear or in spelling, in French and Wolof (official Wolof spelling, décret 2005-992). Over-folding only makes a range a little longer; under-folding would give two places one address. So it folds:

- case and accents (Médina = Medina, Kër = Ker, Sacré-Cœur = Sacré Coeur), hyphens, apostrophes, spaces (Keur Massar = Keurmassar), and St = Saint;
- leading articles and generic words: le, la, les, l', de, du, quartier, village, hameau (Cité is kept: Cité Lamy is not Lamy);
- a trailing numeral: HLM, HLM 2 … HLM 6 are one name, and Pikine 3 shares Pikine's range. The numeral stays in the address ("HLM 5 17 395"); it cannot be mistaken for part of the number, because the name's length is known;
- French and Wolof spellings: Ouakam = Wakam, Darou = Daru, Keur = Kër, Khoudoss = Xudoss, Thiès = Ties, Ndiaye = Njaay, Diamaguène = Jamaguen, Mbacké = Mbakke, Hamdallaye = Amdalaye, Missirah = Missira, Gounass = Gounas, Ndiayène = Ndiayene.

The steps are in SPEC 3.3.1 and the engine's `name_key`.

**Names too big for 5 digits** would take one established qualifier that people already say, decided once per name with the commune and listed, the way "Médina Baye" is already a name apart from "Médina". **None is needed today.** The fullest range is Darou Salam's: 23 lieux in 17 zones, 22,082 compounds, 75.0% of its 5-digit range allocated.

**The check letter binds name, number and lieu.** The letter is computed over the name's family number and the house number; the lieu follows from the block. A one-digit slip from "Médina 12 149" (Dakar) to "Médina 22 149" (Saint-Louis's block) changes one digit of what the letter covers, so in a machine form it is always refused. In the remembered form, which has no letter, the app shows "Saint-Louis" before it routes.

**Stable for ever.** The blocks are frozen at first issue. A new lieu with an existing name gets a new block from the name's free space; a lieu whose block fills gets a further block from it; a name's blocks are never renumbered.

**The real counts** (18 October 2026, 14,997 lieux, by plate name, `model/name-families.json`):

| | |
|---|---|
| Names once normalised | 11,043 (12,344 with the full official names) |
| Names that repeat | **1,974**, borne by **5,928 lieux**: 1,322 names in several zones, 652 within one zone only (with the official names: 1,404 names, 4,057 lieux) |
| Compounds in lieux with a repeated name | 41.9% |
| Lieux per repeated name | 2: 1,224 names; 3: 380; 4: 137; 5-9: 187; 10-32: 46 |
| Most repeated | Ndiayène (32 lieux), Mbayène and Thiékène (28 each), Darou Salam (23), Ndiobène (22), Hamdallaye and Thiarène (21 each) |
| Largest shared range | **Darou Salam**, 23 lieux in 17 zones, 22,082 compounds, **5 digits**; then Gounas (3 lieux, 21,611), Diadie (2, 15,680), Bayakh (5, 14,412), Vélingara (18, 13,383) |
| Shared ranges by length | 3 digits: 900; 4 digits: 966; 5 digits: 108 |
| Names needing a qualifier | **0** |
| Number length, share of compounds | 3 digits 20.0%, 4 digits 46.6%, 5 digits 33.4% (with the full official names: 22.8%, 45.9%, 31.3%; with one range per lieu instead of per name: 29.7%, 45.4%, 24.9%) |

The numbers are a little longer than with one range per lieu, because the lieux of a name add up and each name keeps 10% free, and shorter plate names bring more lieux together under one name. That is the price of an address that is short and needs no town after it.

### 1.7 Getting your address: zero effort

| How | Steps |
|---|---|
| App, home already saved | **0 taps.** "Votre adresse : Ouakam 2512" is on the home screen. |
| App, standing at the gate | **1 tap** ("C'est chez moi" / "This is my home"), then the address is shown. |
| Share it | **1 tap** (Partager). It goes by WhatsApp or SMS as a link: "Ouakam 2512 · nways.ng/a/SN-DKR-0080-2512-J". The recipient needs no app to open the map. |
| New house not on the map | "Add my home": 4 steps (gate, outline, describe, confirm), about 2 minutes. The provisional address is shown at once. |
| No smartphone | The plate or QR sticker on the gate, put up at the claim or by a courier partner. Anyone with the app can read it to them. |
| Courier or partner | The partner looks the address up through the N-Ways API, with the customer's consent (privacy, section 9). |

An SMS lookup service is only a possible later option.

## 2. Hierarchy: why départements, frozen

| Level | Count | Role in the model | Why |
|---|---|---|---|
| Région | 14 | none in the code | Too big for one number space: Tambacounda is 42,214 km², and Thiès holds 803,020 footprints. Dakar region is dense: 534,090 footprints in 620 km². |
| **Département → code zone** | 45 in 2019 + Keur Massar (2021) → **46 zones** | the zone of every address (key + name), the spot grid, the registry file | People already say the département-level town when away ("à Mbour", "à Kolda"). |
| Arrondissement | 121 | only to split Mbacké | Ndame arrondissement holds 417,008 footprints: Touba and Mbacké town. |
| Commune, quartier, village | thousands | **the place word** | What people say every day. |

**The national border decides.** A zone outline (and the 2 km reach of the zone rule along coasts and rivers) may spill over the border; it never carries an address into a neighbouring country. A building whose entrance lies more than 300 m outside OpenStreetMap's admin_level=2 border of Senegal gets no address, and the issuer refuses one there (SPEC 2.3, `engine/data/border.geojson`).

The zones are **frozen** on 2026-10-18 and never follow administrative changes. Keur Massar's 2021 creation as the 46th département proves why: had the zones followed the map, every address in it would have had to change. Keur Massar stays inside zone **PKN** (no open boundary for it exists), and the place card shows the current département as an attribute.

**Touba gets its own zone (TBA).** Mbacké is Senegal's most populous département (1,359,758 residents, census 2023). Touba, the holy city of the Mouride brotherhood, is one of Africa's fastest-growing and densest cities, and La Poste covers all of it with the single code 22300. Splitting the Ndame arrondissement off as TBA keeps Touba's registry, its spot cells (5 m) and its plates its own.

## 3. Settlement patterns and what they change

| Setting | Facts | Consequence in the model |
|---|---|---|
| **Dakar peninsula** (DKR, PKN, GDW, RUF) | 534,090 footprints; Guédiawaye has 58,688 people per km²; walls and terraces; blue street plates in parts | Fine spot cells (1-2 m). Wall-to-wall houses are never merged by shape alone (R1/R2 do not apply to main buildings in urban fabric). Street plates are shown next to the address. Cités (SICAP, HLM, Cité Keur Gorgui) are both lieux and estates (one gate). |
| **Touba** (TBA) | 417,008 footprints in one arrondissement; large family concessions, sometimes several houses in one walled plot; the Grande Mosquée and mausolées | Own zone. Concession grouping (enclosures where mapped, satellites, people). Religious buildings classed `rel.*` from OSM and places. |
| **Groundnut basin and the centre** (Kaolack, Fatick, Kaffrine, Diourbel, Bambey) | Villages of round cases and small houses in concessions; ML footprints dominate (OSM only 6-15%) | Rule R2 (rural concession) groups cases; numbers have 3 digits in most villages. |
| **River valley** (Saint-Louis, Dagana, Podor, Matam, Kanel) | Linear villages along the Senegal river; Saint-Louis island city | Large zones get 10 m spot cells with 5+5 digits. Saint-Louis has its own 5 m zone. |
| **East** (Tambacounda, Bakel, Kédougou, Saraya) | Huge, sparsely settled zones (frames up to 215 km); mining camps in Kédougou | 10 m spot cells with 5+5 digits; few compounds per village (3 digits). |
| **Casamance** (Ziguinchor, Bignona, Oussouye, Sédhiou, Kolda) | Cut off from the north by The Gambia; Jola, Mandinka and Pulaar villages; dense OSM mapping in parts | Zones independent of the north. Village lieux. The place word is the village name in its local spelling. |
| **Petite Côte** (Mbour, Saly, Joal) | Hotels, holiday villas, fishing quays | `hot.hotel`, `pec.quai` classes; villas in cités with one gate. |

## 4. The existing systems and how the address relates to them

| System | What it is | How N-Ways relates |
|---|---|---|
| **ANN (Adressage Numérique National)** | The state's national digital address register, relaunched 5-6 Aug 2026; pilot within a year; no format published | **Takes over** every area it covers (coverage `ann`): the ANN address is shown as written and the N-Ways address becomes an alias. Until then N-Ways is a companion and candidate input: `annId` on every compound, and the registry is offered for adoption (GOVERNANCE.md). |
| **La Poste postcodes** | 163 five-digit delivery-office codes | `laPosteCode` on every compound, shown on the place card ("12300 Ouakam"); never inside the address (codes can be renumbered and have no boundaries) |
| **Street plates** | Street codes (PE-44) + metric door numbers | **Used as the address** wherever in use or obtainable (coverage `official-municipal`): shown as written; `streetRef` + `metricNumber` on every door; no N-Ways plates |
| **Cadastre** | NICAD parcels (PROCASEF: 830,000+ parcels in 138 communes) and lotissement plots | `nicad`, `lotissementPlot`; survey-plan import in Add my home |

## 5. Languages and how the address is said

- **French** (official). The place word, then the number the way Senegalese say house numbers and phone numbers:
  - 3 digits: "cent vingt";
  - 4 digits in pairs: "quarante-cinq, douze";
  - 5 digits as 2 + 3: "quarante-cinq, cent vingt-huit".
- **Wolof** (lingua franca, spoken by most Senegalese). The place word (most are Wolof already: Keur, Ndiaye, Darou…), then digits one by one: benn, ñaar, ñett, ñeent, juróom, juróom benn… Wolof 3 and 4 (ñett/ñeent) and 8 and 9 (juróom ñett/juróom ñeent) sound alike, so the app reads the number back and shows the house. Many Wolof speakers say numbers in French anyway, especially phone numbers.
- **Pulaar, Serer, Jola, Mandinka, Soninké.** The place word is the same, and the digits are said in French or Wolof, as they are for phone numbers.
- **Letters**, which appear only in the zone key of spot codes and in the machine form's check letter, use eleven letters whose French names do not rhyme with each other (F H J K M Q R T W X Z; SPEC 4). The official Wolof alphabet (décret 2005-992) names letters the French way in practice.

## 6. Spot codes (any point)

Some places have no compound: a field, a pitch in Sandaga market, a bus stop, an empty plot. These get a spot code computed offline on **WGS 84 / UTM 28N**, the projection Senegalese surveyors already use (Yoff / UTM 28N, EPSG:31028, is the legacy national grid). The format is the zone key, then the easting and northing digits, e.g. `DKR 5553 1512`. No check letter is written, because people type spot codes; a code written with an older trailing letter is still verified.

The cell size follows the zone frame:

| Cell | Zones |
|---|---|
| 1 m | Guédiawaye |
| 2 m | Dakar, Pikine |
| 5 m | Touba, Saint-Louis, Rufisque, Bambey, Guinguinéo, Oussouye |
| 10 m | the rest (5+5 digits in the 18 widest rural zones) |

Spot codes are the one form with letters, and people rarely need to remember them: they are for sharing a point once.

## 7. Compounds: the addressable unit

Most Senegalese live in **concessions**, walled or fenced family plots with several buildings: a main house, rooms around a courtyard, a kitchen, toilets, sometimes shops built into the street wall. Villas sit in walled plots with a gate and a gatehouse. One gate serves the whole plot. So the address belongs to the **compound**, its buildings are sub-units, and navigation ends at the **gate**.

| Case | Model |
|---|---|
| A villa with a gatehouse and boys' quarters | One compound; structures 1 (villa), 2 (gatehouse), 3 (annexe) |
| A family concession with many ménages | One compound, `residential-multi-household` only when people say so (never inferred) |
| An apartment block R+4 | One compound, one structure, units (flats) `·1.1`, `·1.2`… |
| Shops in the street wall of a concession | Structures of the compound, each with its own shop door (unit) |
| A cité with one gate (SICAP, cités privées) | The cité is an **estate**: estate gate → compound gate; each house keeps its own address |
| Rural concession of cases | One compound grouped by rule R2 (cases < 120 m², within 6 m) |

Grouping rules (SPEC 7.1):

- **R0 enclosures**: OSM walls and fences, N-Ways gated sites, Add-my-home outlines, cadastral parcels;
- **R1 satellites**: small buildings next to a main one;
- **R2 rural concessions**;
- **R3 people's confirmations.**

**Two main buildings in urban fabric are never merged by shape alone.** In the Médina or Pikine, houses touching wall to wall are separate concessions, and only an enclosure or people can say otherwise. Regrouping never changes an issued address.

## 8. Building profile

Every structure carries a profile, so the registry describes the building and not just its position: whether it is residential, commercial or public, and how big it is. Emergency services, planners and couriers need that as much as the position.

- **Use class**, with a Senegal taxonomy:
  - residential: concession, maison basse, immeuble R+n, case, annexe;
  - commercial: boutique, marché/cantines, bureaux, entrepôt, station, atelier;
  - hospitality: hôtel/campement, restaurant/dibiterie;
  - public: administration, école, daara, université, hôpital, centre/poste/case de santé, pharmacie;
  - religious: mosquée, église, mausolée;
  - industrial, transport, fishing quay, agricultural (magasin/secco, grenier);
  - mixed, chantier, ruine, inconnu.

  Each class comes with a **confidence** from the rule that set it (SPEC 6.2): OSM tags 0.85-0.9, N-Ways places inside the footprint 0.6-0.7, shape 0.2-0.5, people 0.95. A daara is never guessed from shape.
- **Size**: footprint and perimeter (from the polygon, in UTM metres); height and floors only from OSM `height` or `building:levels`. Floors are shown as RDC, R+1, R+2, the way Dakar describes buildings. Floor area is footprint × floors, marked as an estimate when the floors are unknown. **The height value carried with the machine-learned footprints is not a measurement** (SPEC 6.4) and is never used.
- **Sources and last-confirmed date per attribute**: `osm:<tag>`, `ml:footprint`, `places:<category>`, `people`, `partner:<name>`.
- **Entrances, name and status.** Names are kept only for businesses and public buildings. Status is existing, chantier, ruine or demolished. Unfinished buildings are common in Senegal: houses are built floor by floor over years, so `chantier` is a normal, long-lasting status.

**Correcting.** Couriers delivering to a door, visitors arriving, owners claiming their building and partners' data all confirm or correct attributes. Agreement settles a change (the building's owner + 1, or 2 independent people), with no staff queue.

## 9. Privacy and data protection

- **Codes describe places, never people.** Residential compounds carry no occupant data: no names, no phone numbers, no household composition. Household count is stored only as one / several / not said, is never shown, and exists only for the multi-household class.
- **Public:** positions, outlines, classes, sizes, statuses, gate positions, business and public-building names, street plates.
- **Private:** Add-my-home photos (kept for verification, not published), and any door a household asks to hide (the compound's address stays; the door is hidden).
- **Partners** (couriers, banks) see a customer's address only with the customer's consent, through the API.
- **Law.** Loi n° 2008-12 and Décret n° 2008-721. The CDP must receive a declaration before processing starts: geolocation falls under the "déclaration normale", and transfers outside Senegal need authorisation. The 2019 replacement bill (APDP) has not been adopted as far as we found. The CDP is also part of the ANN workshop, which is a natural place to present this model.

## 10. Numbers from the N-Ways building map

Computed on 18 October 2026 from the N-Ways building map: 1,378,821 OpenStreetMap footprints and 4,264,275 Google/Microsoft footprints. 10,415 footprints whose centre falls outside the 2019 département outlines (coast, borders) are left out. The scripts are in `tools/`, and the full tables are in `model/building-stats.json` and `model/lieux-stats.json`.

Headlines:

- **5.63 million footprints form 3.60 million compounds.** Outside Dakar and Ziguinchor, more than half of all footprints sit in multi-structure compounds (52-62% by region). The share is 32.6% in Dakar département and 49.5% in Touba. Senegal's built form calls for one address per compound.
- **Gates are almost unknown.** OpenStreetMap and the N-Ways routing build hold 1,403 gates and entrances and 6,351 enclosures (walls, fences, gated sites) across Senegal. A gate is known for 126 of Dakar département's 107,391 compounds (0.1%), and for 3 of Touba's 289,293. Gates will come from people: claims, couriers' arrivals and Add my home.
- **Uses are mostly inferred.** 1,099,686 OpenStreetMap footprints are tagged only `building=yes`. Classes other than residential are therefore rare in the counts below, and most residential classes come from shape (confidence 0.45-0.5). These figures describe what the map knows today, not what Senegal's buildings are.
- **Heights are unknown almost everywhere.** Floors are known only where OpenStreetMap has them: 515 footprints in Dakar département and 19 in Touba. The ML height column is a filler (4,257,726 rows, 36 distinct values between 3.5 and 7.0 m) and is not used.
- **Number lengths.** 14,997 places receive compounds, with a median of 79 compounds per place. With one national range per plate name (section 1.6), 20.0% of compounds get a 3-digit number, 46.6% a 4-digit one and 33.4% a 5-digit one (with the full official names: 22.8%, 45.9%, 31.3%; with one range per place: 29.7%, 45.4%, 24.9%). The 5-digit share is high where place points are sparse: five in six compounds in Touba and Pikine. Curating sub-quartiers with the communes would bring many of those numbers down to 4 digits. No place exceeds 27,000 compounds.
- **Plate names.** 4,208 of the 14,997 official names are over 12 characters or 2 words. 1,119 are shortened by rule, and 3,116 go to the communes with candidates, 172 of them still over the limit provisionally (section 1.5.1).
- **Repeated names.** 1,974 plate names repeat, over 5,928 places holding 41.9% of compounds. The largest shared range is Darou Salam's (23 places in 17 zones, 22,082 compounds, 5 digits, 75.0% allocated). No name needs a qualifier.
- **The coverage mask today.** 1,601 OpenStreetMap streets carry the municipal programme's street references. They put 112 places in the official-municipal mask, holding 3.6% of compounds nationally and 44.0% in Dakar département. In those places the official street address is shown, not an N-Ways address. The mask will grow as the communes' and the ARTP's data is obtained.

**By region.** 5,632,681 footprints grouped into 3,595,628 compounds.

| Region | Footprints | Compounds | In multi-structure compounds | Median footprint (m²) | residential | commercial | government | education | health | religious | hospitality | unknown |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Thiès | 800,303 | 525,647 | 51.7% | 34 | 92.5% | 0.1% | 0.0% | 0.0% | 0.0% | 0.1% | 0.0% | 7.2% |
| Diourbel | 731,035 | 463,545 | 54.8% | 26 | 88.7% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 11.2% |
| Dakar | 530,668 | 413,099 | 35.8% | 77 | 95.0% | 0.7% | 0.0% | 0.1% | 0.1% | 0.1% | 0.1% | 3.7% |
| Louga | 516,209 | 322,353 | 55.8% | 22 | 91.3% | 0.0% | 0.0% | 0.0% | 0.0% | 0.1% | 0.0% | 8.6% |
| Kaolack | 442,506 | 272,452 | 55.5% | 26 | 90.4% | 0.1% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 9.4% |
| Kolda | 409,734 | 231,350 | 61.7% | 26 | 89.7% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 10.1% |
| Saint-Louis | 401,420 | 253,865 | 55.3% | 27 | 92.2% | 0.2% | 0.0% | 0.1% | 0.1% | 0.1% | 0.0% | 7.0% |
| Fatick | 374,909 | 211,817 | 60.9% | 23 | 91.7% | 0.1% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 8.1% |
| Tambacounda | 371,314 | 217,861 | 57.1% | 21 | 89.1% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 10.8% |
| Kaffrine | 308,780 | 182,828 | 56.4% | 21 | 81.5% | 0.1% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 18.4% |
| Matam | 280,135 | 175,981 | 54.5% | 22 | 93.5% | 0.0% | 0.0% | 0.0% | 0.1% | 0.0% | 0.0% | 6.3% |
| Ziguinchor | 166,969 | 129,377 | 37.7% | 83 | 97.5% | 0.1% | 0.0% | 0.1% | 0.0% | 0.1% | 0.1% | 1.7% |
| Kédougou | 150,063 | 99,037 | 49.0% | 21 | 71.9% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 27.5% |
| Sédhiou | 148,636 | 96,416 | 52.9% | 52 | 97.7% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 2.2% |

**Dakar (département).** 135,785 footprints, 107,391 compounds; 32.6% of footprints are in multi-structure compounds; a gate is known for 0.1% of compounds (126). Urban fabric: 75.5%.

Footprint (m²): p10 20, p25 38, median 94, p75 168, p90 278, p99 936

Most common classes: `res.maison` 60.1%; `res.concession` 17.4%; `res.annexe` 13.2%; `inconnu` 3.6%; `res.case` 2.0%; `com.boutique` 0.9%; `com.bureau` 0.6%; `edu.ecole` 0.4%

Floors (from OpenStreetMap; "unknown" where it has none): unknown 135,270; R+1 149; R+5 et plus 138; RDC 97; R+2 65; R+3 42; R+4 24

Structures per compound: 1: 91,549; 2: 11,972; 3: 2,320; 4: 680; 5: 290; 6: 145; 7: 97; 8: 66; 9: 47; 10+: 225

**Touba-Mbacké (Ndame).** 417,008 footprints, 289,293 compounds; 49.5% of footprints are in multi-structure compounds; a gate is known for 0.0% of compounds (3). Urban fabric: 70.5%.

Footprint (m²): p10 14, p25 18, median 32, p75 76, p90 158, p99 369

Most common classes: `res.maison` 33.7%; `res.annexe` 23.9%; `res.concession` 21.6%; `inconnu` 12.2%; `res.case` 8.5%; `rel.mosquee` 0.0%; `com.boutique` 0.0%; `com.entrepot` 0.0%

Floors (from OpenStreetMap; "unknown" where it has none): unknown 416,989; RDC 14; R+2 3; R+1 2

Structures per compound: 1: 210,547; 2: 54,713; 3: 15,174; 4: 4,464; 5: 1,752; 6: 938; 7: 527; 8: 341; 9: 244; 10+: 593

**Place words and number length.** 14,997 places receive at least one compound; median 79 compounds per place. Share of compounds whose number has 3 digits: 20.0%; 4 digits: 46.6%; 5 digits: 33.4%; oversized places (over 27,000, to split): 0 places, 0.0% of compounds.

The lengths come from the national per-name ranges of the plate names; with the full official names they were 22.8%, 45.9% and 31.3%; with one range per place, 29.7%, 45.4% and 24.9%. An asterisk marks a provisional plate name, which the commune confirms.

| Zone | Places | Compounds | 3 digits | 4 digits | 5 digits | oversized | places with a shared name | largest places |
|---|---|---|---|---|---|---|---|---|
| DKR | 112 | 107,391 | 1.2% | 62.7% | 36.1% | 0.0% | 52 | Parcelles* (9,137), Ngaparou (3,502), Keur Damel (3,484) |
| PKN | 39 | 123,528 | 0.0% | 13.0% | 86.9% | 0.0% | 17 | Ndiorane (9,765), Darou Salam (7,528), Mbaye Fal* (6,091) |
| GDW | 11 | 23,541 | 0.8% | 25.6% | 73.6% | 0.0% | 1 | Angel Mouss (4,009), Gounas* (3,966), Barry & Ly* (3,516) |
| RUF | 119 | 158,639 | 1.6% | 43.0% | 55.4% | 0.0% | 47 | Tivaouane* (7,579), Cité Tawfekh (5,626), Ndiougouye (5,228) |
| TBA | 241 | 289,293 | 3.0% | 13.1% | 83.9% | 0.0% | 108 | Féto (10,861), Darou Salam (10,102), Darou Miname (10,068) |
| THS | 485 | 175,559 | 13.5% | 62.7% | 23.8% | 0.0% | 193 | Medina Fall (5,148), Cité Lamy (4,258), Silmane (3,819) |
| STL | 194 | 73,622 | 11.0% | 66.7% | 22.3% | 0.0% | 63 | Pikine 3 (5,354), Pikine (2,997), Diaminar (2,330) |
| ZIG | 197 | 48,197 | 12.5% | 69.4% | 18.1% | 0.0% | 82 | Néma (2,083), Kénia (1,754), Boucotte Sud (1,729) |
| BMB | 489 | 82,990 | 28.0% | 59.2% | 12.8% | 0.0% | 228 | Nanlar (2,491), Diourane (2,463), Ngogom (2,421) |
| KLD | 515 | 72,580 | 34.5% | 25.2% | 40.3% | 0.0% | 174 | Gaïdé (9,492), Faraba (8,649), Ousmane* (5,349) |
| TBC | 674 | 100,066 | 26.4% | 30.4% | 43.1% | 0.0% | 260 | Diadie* (15,671), Djidje* (11,855), Tambacounda (7,094) |

**Repeated names.** 14,997 places carry 11,043 names once normalised. 1,974 names repeat, over 5,928 places (1,322 names in several zones, 652 within one zone only) holding 41.9% of compounds. Shared ranges: 900 of 3 digits, 966 of 4, 108 of 5. The largest: Darou Salam, 23 places in 17 zones, 22,082 compounds, 5 digits, 75.0% of the range allocated. Names needing a qualifier: 0.

| Name | Places | Zones | Compounds | Digits | Range allocated |
|---|---|---|---|---|---|
| Ndiayene / Ndiayenne / Ndiayène | 32 | 18 | 8,777 | 5 | 31.1% |
| Mbayene / Mbayenne / Mbayène | 28 | 12 | 5,565 | 5 | 20.0% |
| Thieckene / Thieckène / Thiekene | 28 | 14 | 4,194 | 5 | 15.8% |
| Darou Salam / Darou-Salam | 23 | 17 | 22,082 | 5 | 75.0% |
| Ndiobene / Ndiobène | 22 | 11 | 5,096 | 5 | 18.1% |
| Amdalahi / Hamdalaye / Hamdalaye 1 | 21 | 15 | 2,263 | 4 | 88.9% |
| Thiarene / Thiarréne / Thiarène | 21 | 15 | 5,766 | 5 | 20.7% |
| Diokoul / Diokul | 19 | 12 | 5,113 | 5 | 18.0% |
| Gounas / Gounass | 3 | 2 | 21,611 | 5 | 72.2% |
| Diadie / Diadj | 2 | 2 | 15,680 | 5 | 52.4% |
| Bayakh | 5 | 4 | 14,412 | 5 | 48.2% |
| Velingara / Vélingara | 18 | 13 | 13,383 | 5 | 45.6% |
| Malicounda / Malikounda | 4 | 1 | 12,609 | 5 | 42.2% |

**Plate names.** Of 14,997 official names, 4,208 are over the limit (4,154 have more than 12 characters, 1,474 more than 2 words). 10,763 names stay as they are; 100 are cleaned (generic word, acronym, numeral in digits), 3 take a documented short form, 1,016 keep their one or two most distinctive words. 3,116 go to the commune with up to 3 candidates (one of them the cleaned "Richard Toll", which would equal a well-known town); 172 of them stay over the limit provisionally (no candidate fits). 55 official names are not kept as aliases, because two plate names would claim them.

|  | Official names | Plate names |
|---|---|---|
| Names once normalised | 12,344 | 11,043 |
| Shared names (places) | 1,404 (4,057) | 1,974 (5,928) |
| Largest shared range | Darou Salam, 23, 22,082 | Darou Salam, 23, 22,082 |
| Most shared name | Darou Salam, 23 | Ndiayene, 32 |
| Places with 3 / 4 / 5 digits | 10,620 / 3,782 / 595 | 9,585 / 4,571 / 841 |
| Compounds with 3 / 4 / 5 digits | 22.8% / 45.9% / 31.3% | 20.0% / 46.6% / 33.4% |

Longest remembered address: "Yeumbeul Sud 20 699" (19 characters); with the provisional names, "Ancien Marché Hebdomadaire 22 199" (33), a name the commune has to shorten.

## 11. Who governs it

N-Ways maintains the model and issues addresses for now. The intended long-term home is the ANN programme (Ministry in charge of digital affairs) or a body it designates, working with La Poste, the communes (which own quartier names and street plates) and the Direction du Cadastre. Rules for change, hand-over and disputes are in [GOVERNANCE.md](../GOVERNANCE.md).
