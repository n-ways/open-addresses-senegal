---
title: "An address for every compound: a national addressing model for Senegal"
kind: "Research paper"
author:
  - "The N-Ways Addressing Group"
affiliation: "N-WAYS LIMITED (nways.ng)"
date: "October 2026"
abstract-title: "Abstract"
abstract: |
  Senegal's postcodes identify delivery offices, its street plates cover parts of nine cities, and its national digital addressing programme has not yet published a format; most of its 18.1 million residents cannot give an address that leads to their gate. We present a national addressing model built for Senegal and the registry issued with it, which gives each of 3,597,128 compounds an address of the form *place word + number*, such as *Ouakam 2512*. Places that share a name draw their numbers from one national range per name, cut into disjoint blocks, so the spoken address is unique in the country without a town or a position. Numbers follow a Hilbert curve with a threefold reserve for growth; a machine form carries an ISO/IEC 7064 check letter that people never see; and any point receives an offline spot code on the UTM 28N grid. On the full registry every address decodes to exactly one compound, consecutive numbers lie a median 23 m apart, and 76 % of one-digit slips match no address. Government addresses are shown first wherever they exist. Specification, engine, registry and server are open.

  **Keywords:** street addressing; place names; check characters; space-filling curves; building footprints; Senegal.
rights: "© 2026 N-WAYS LIMITED. Text licensed under CC BY 4.0. Data © N-WAYS LIMITED under ODbL 1.0; contains OpenStreetMap data © OpenStreetMap contributors."
lang: en-GB
papersize: a4
fontsize: 11pt
geometry: "margin=2.3cm"
---

# Introduction

## The problem

An address does three things. It lets a person say where they live, it lets someone else find that place, and it lets institutions refer to the same place in their records. In Senegal none of the existing systems does all three for most households. La Poste Sénégal's postcodes identify a delivery office and its area: the single code 22300 covers the whole of Touba, a city of more than a million people [@upu2015; @laposte2026]. The blue street plates and metric door numbers installed by municipal programmes since the late 1990s cover parts of nine cities and are, by the government's own account, largely incomplete and out of date [@farvacque2005; @osmwiki; @edjo2021]. The national digital addressing programme, the Adressage Numérique National (ANN), was relaunched on 5–6 August 2026 with the aim of a single geo-referenced address register; it has not yet published a format, a platform or data [@ba2026; @njoya2026]. Directions are still given by landmark: "face BCEAO", "derrière la mosquée".

The cost of this gap falls on the people with the least. A delivery rider calls the customer several times before finding the gate; an ambulance crew depends on a caller's local knowledge; a household cannot prove where it lives to a bank or a utility. Conventional street addressing, which names streets and numbers doors, costs money, takes years and decays when it is not used [@farvacque2005]. Most of Senegal's compounds lie in villages and dense urban extensions where streets have no names at all.

## Contribution

This paper describes a national addressing model built for Senegal and the registry issued with it in October 2026. Its contributions are:

1. **A remembered form that needs no context.** An address is a place word people already use followed by a short number, *Ouakam 2512*. Places that share a name draw from one national number range for that name, cut into disjoint blocks (Section 4.6), so the spoken address is unique in Senegal on its own. We prove that decoding is unique and verify it on all 3,597,128 issued addresses (Section 6.1).
2. **Short names by rule.** A fixed rule derives a *plate name* of at most 12 characters and two words from each official place name, and sends the cases it cannot shorten safely to the commune (Section 4.4).
3. **Numbers that follow the ground.** Within a place, numbers run along a Hilbert curve with a threefold reserve, so neighbours receive close numbers and new compounds can be inserted between them without renumbering (Sections 4.7–4.8).
4. **Error control that people never see.** A machine form carries an ISO/IEC 7064 MOD 11-2 check letter written with eleven letters chosen for French speakers; the spoken and written forms carry none (Section 4.10).
5. **Government addresses first.** A coverage mask shows the official street address, and later the ANN address, wherever one exists; the N-Ways address then serves as an alias (Section 4.14).
6. **An open, complete implementation.** The specification, a standard-library reference engine, the full registry with checksums, and a server that any ministry or operator can deploy with one command are published under open licences, with conformance vectors and parity tests against the issuer (Section 5).

## Structure

Section 2 reviews Senegal's existing systems and international practice. Section 3 describes the data. Section 4 sets out the model, formula by formula, with a worked example on the address *Ouakam 2512*. Section 5 describes the implementation and Section 6 its measured properties. Section 7 records the designs we considered and rejected. Sections 8–11 examine the benefits to citizens, to logistics and commerce, to emergency services and to government. Section 12 covers privacy, safety and governance, Section 13 the limitations, and Section 14 concludes.

# Background and related work

## La Poste postcodes

La Poste Sénégal writes a five-digit postcode to the left of the delivery office, as in `12500 DAKAR` or `27000 Ziguinchor` [@upu2015]. The Universal Postal Union's addressing sheet describes the code as a routing area, a delivery post office and a delivery area; in La Poste's own data the first two digits follow the geography, from 10–17 for the Dakar region to 36 for Matam. La Poste's online finder maps 4,143 locality and quartier names to 166 values, of which 163 are well-formed codes [@laposte2026]. The code 17000 alone covers 250 named places in the Pikine and Keur Massar suburbs. The finder publishes names, not boundaries, and states no licence. Most mail is delivered to post-office boxes (BP) and neighbourhood boxes ("postchances"). A postcode therefore answers the question "which post office?", not "which door?".

## Municipal street addressing

Street addressing in Senegal dates from a 1993 pilot in Mbour and was carried out at scale under the World Bank–financed Urban Development and Decentralisation Programme (PAC, 1998–2004), managed by the Agence de Développement Municipal [@farvacque2005]. Streets are coded by a two-letter neighbourhood radical and a number (for example ES.12, the twelfth street of Escale), and doors are numbered metrically and alternately on the two sides. Of the fifteen cities initially eligible, eight completed every task (Thiès, Louga, Diourbel, Kaolack, Ziguinchor, Saint-Louis, Guédiawaye and Tambacounda), three completed signage only (Dakar, Rufisque and Pikine), and four did not meet the programme's deadlines [@farvacque2005]. In Thiès and Kaolack the programme also reconciled the address directory with the tax rolls.

The present plates show the quartier, the street's name or number and a reference such as PE-44 (Point E), SC-15 (Sacré-Cœur) or OKM-1 (Ouakam) [@osmwiki; @ausenegal2018]. A door's number is its distance in metres from the start of the street, so doors often carry two stencilled numbers, an old one and a new one [@ausenegal2018]. In 2019 the telecommunications and postal regulator (ARTP) reported 224,000 numbered buildings in 255 quartiers of Dakar [@aps2019]. The 2021 launch of the national digital addressing project described physical addressing as largely incomplete and out of date [@edjo2021].

## The Adressage Numérique National

The Ministry of the Digital Economy and Telecommunications launched a national digital addressing project on 25 February 2021, with the aim of mapping the territory and giving every location a digital address within three years [@edjo2021]. In 2023 it was presented under the slogan « Un Sénégalais, une adresse » [@njoya2026]. On 5–6 August 2026 the ministry in charge of telecommunications and digital affairs held a relaunch workshop with central administrations, local authorities, the private sector, universities and civil society. Its stated aim is a « référentiel national d'adresses unique, géoréférencé et partagé » for public services, e-commerce, taxation, land management, postal and logistics services and emergency response, with the pilot to be completed within one year [@ba2026; @njoya2026]. Commentators warned that, without one clearly designated authority, the country risked « multiplier les bases incompatibles » [@snl2026]. As of October 2026 no address format, pilot area, platform, interface or data licence had been published. A model that intends to serve Senegal must therefore be easy for the ANN to adopt, map onto or replace.

## Land, cadastre and geodesy

Law 64-46 of 1964 places in the *domaine national* all land that is neither state domain nor registered, by common estimates 80–85 % of the country; communes allocate it for use, and it cannot be sold as private property [@loi1964]. Law 2011-07 governs registered land, on which a real right exists only once it is entered in the land book [@loi2011]. The cadastre assigns parcels a NICAD identifier. The World Bank–financed PROCASEF project (US$80 million, from August 2021) had recorded and mapped more than 830,000 parcels in 138 communes by June 2026, more than 630,000 of them with a NICAD [@aps2026procasef]. No open parcel layer is published. An address in this setting must never be mistaken for evidence of title.

Senegal's geodetic network has used five reference systems: three of them, the Adindan, Yoff and 1974 datums, use the UTM projection on the Clarke 1880 ellipsoid, while the Hatt system, on which the old cadastral sheets were drawn, uses a stereographic projection; a geocentric datum, NSGD2004, tied to ITRF2000 with the GRS80 ellipsoid, was designed and built in 2004 [@ndiaye2005]. The legacy national grid Yoff / UTM zone 28N (EPSG:31028) and its WGS 84 counterpart (EPSG:32628) share the same projection [@epsg31028]. Surveyors therefore already read coordinates on the UTM zone 28N grid that we use for spot codes (Section 4.11).

## International practice

The UPU's standard S42 describes the components of postal addresses and national templates for writing them [@upuS42], and ISO 19160-1 gives a conceptual model of addressing [@iso19160]. Both describe how to represent an address once it exists; neither prescribes how to create one where none exists. The UPU's white paper *Addressing the world* argues that an address is a precondition of citizenship, commerce and service delivery [@upu2012]. The World Bank's review of street addressing in 52 cities of 15 African countries between 1989 and 2004, which includes Senegal's programme, found that only 8 % of streets in a sample of 21 cities had names before addressing, that conventional addressing cost on average US$5.7 per doorway, and that the value of addressing lies in its use by municipal services, above all for local taxation [@farvacque2005].

Several code systems compute an identifier from coordinates. Open Location Code ("Plus Codes") encodes latitude and longitude in a base-20 alphabet and works offline [@olc]. Word-based grid systems assign three words to each 3 m square. Such codes are universal and need no registry, but they identify squares rather than buildings, they change from one square to the next across a single compound, and their letters or words carry no meaning to the holder. A code that is computed from coordinates also cannot express the compound, the unit to which a gate, a household and a delivery belong.

Error control for identifiers that people copy has a long literature. Verhoeff classified the errors people make when copying digits, single substitutions and adjacent transpositions being the most frequent [@verhoeff1969]. ISO/IEC 7064 specifies check-character systems; its pure MOD 11-2 system detects every single substitution and every adjacent transposition at the cost of an eleventh symbol [@iso7064]. Damm's totally anti-symmetric quasigroups achieve the same with a decimal check digit [@damm2004; @damm2007]. For ordering, space-filling curves map a plane to a line while preserving locality; Hilbert's curve clusters neighbouring cells better than the Z-order and Gray-code curves [@hilbert1891; @moon2001].

## Requirements

From this review we derive six requirements for a Senegalese address.

- **R1, memorable.** People must be able to say, hear and write it without a device. Senegalese already remember quartier names and numbers (mobile numbers in pairs, BP numbers, door numbers), but rarely codes that mix letters and digits.
- **R2, unique without context.** A name is said without its town, so the spoken address must identify one compound in the country by itself.
- **R3, compound level.** The address leads to a gate and belongs to the compound that the gate serves.
- **R4, stable.** It never changes or is reused, whatever happens to administrative boundaries, quartier names or the building map.
- **R5, beside official systems.** It shows the government's address where one exists and can be absorbed by the ANN.
- **R6, open and verifiable.** The rules, the code and the data are public, so any institution can reproduce every address.

# Data and sources

## Building footprints

The registry is built from 5,643,096 building footprints: 1,378,821 from OpenStreetMap [@haklay2008; @geofabrik2026] and 4,264,275 detected by machine learning from satellite imagery, from Google Open Buildings [@sirko2021] and Microsoft's global footprints [@microsoft2023] as distributed by Overture Maps [@overture2026]. After removing 10,415 footprints whose centroid falls outside the 2019 département outlines (on the coast and along the borders), 5,632,681 remain. The two sources complement each other unevenly (Figure 1): OpenStreetMap contributes 68 % of the footprints in Sédhiou and 59 % in Kolda, where community mapping has been intense, but under 10 % in Thiès, Diourbel and Kaffrine, where the machine-learned sets dominate.

![Building footprints by region and source. OpenStreetMap against the machine-learned sets (Google Open Buildings and Microsoft, distributed by Overture Maps), in thousands. Source: `model/building-stats.json`.](figures/footprint-sources.svg)

The footprints carry little attribute information. Of the OpenStreetMap footprints, 1,099,686 are tagged only `building=yes`. Floors are known only where OpenStreetMap records them: for 515 footprints in Dakar département and 19 in Touba. The height column distributed with the machine-learned footprints holds 36 distinct values between 3.5 and 7.0 m across 4,257,726 rows; it is a rendering default, not a measurement, and the model never uses it.

## Boundaries and places

Administrative outlines are the 2019 département (ADM2) and arrondissement (ADM3) boundaries of geoBoundaries, which derive from Government of Senegal data compiled by OCHA [@runfola2020]. Place points come from OpenStreetMap place nodes and GeoNames populated places: 16,994 candidates, of which 1,142 GeoNames duplicates of OpenStreetMap places were removed, leaving 15,852, of which 14,997 receive at least one compound. Population figures are those of the fifth general census (RGPH-5, 2023): 18,126,390 residents [@ansd2024]. Urban population growth is taken from the World Development Indicators [@wdi2026]. The national border is OpenStreetMap's admin_level 2 boundary of Senegal [@geofabrik2026], and it decides which buildings are in the country: a building whose entrance lies more than 300 m outside it is in a neighbouring country and receives no address, whatever the département outlines say (Section 4.2).

## What the building map shows

Grouping the 5,632,681 footprints into compounds by the rules of Section 4.12 yields 3,595,628 compounds in the analysis run; the issuing run, two days later and from the same sources, holds 3,597,128 (0.04 % more), and all counts of addresses below refer to the issued registry. Four observations shaped the model.

- **Compounds, not buildings.** Outside Dakar and Ziguinchor, between 52 % and 62 % of footprints, depending on the region, lie in compounds of several structures; the share is 32.6 % in Dakar département and 49.5 % in Touba. One address per footprint would give a family concession of kitchens, rooms and annexes several addresses.
- **Gates are almost unknown.** OpenStreetMap and the routing network hold 1,403 gates and entrances and 6,351 enclosures (walls, fences and gated sites) in the whole country. A gate is known for 126 of Dakar département's 107,391 compounds and for 3 of Touba's 289,293.
- **Uses are mostly inferred.** Because most footprints carry no tag, building classes other than residential are rare in the counts, and most residential classes come from shape.
- **Settlement is dense where place points are sparse.** Touba's 289,328 compounds share 241 place points; Pikine's 123,594 share 39. The numbers in these zones are long (Appendix A).

| Region | Footprints | Compounds | In multi-structure compounds | Median footprint (m²) | Residential | Unknown |
|:--|--:|--:|--:|--:|--:|--:|
| Thiès | 800,303 | 525,647 | 51.7 % | 34 | 92.5 % | 7.2 % |
| Diourbel | 731,035 | 463,545 | 54.8 % | 26 | 88.7 % | 11.2 % |
| Dakar | 530,668 | 413,099 | 35.8 % | 77 | 95.0 % | 3.7 % |
| Louga | 516,209 | 322,353 | 55.8 % | 22 | 91.3 % | 8.6 % |
| Kaolack | 442,506 | 272,452 | 55.5 % | 26 | 90.4 % | 9.4 % |
| Kolda | 409,734 | 231,350 | 61.7 % | 26 | 89.7 % | 10.1 % |
| Saint-Louis | 401,420 | 253,865 | 55.3 % | 27 | 92.2 % | 7.0 % |
| Fatick | 374,909 | 211,817 | 60.9 % | 23 | 91.7 % | 8.1 % |
| Tambacounda | 371,314 | 217,861 | 57.1 % | 21 | 89.1 % | 10.8 % |
| Kaffrine | 308,780 | 182,828 | 56.4 % | 21 | 81.5 % | 18.4 % |
| Matam | 280,135 | 175,981 | 54.5 % | 22 | 93.5 % | 6.3 % |
| Ziguinchor | 166,969 | 129,377 | 37.7 % | 83 | 97.5 % | 1.7 % |
| Kédougou | 150,063 | 99,037 | 49.0 % | 21 | 71.9 % | 27.5 % |
| Sédhiou | 148,636 | 96,416 | 52.9 % | 52 | 97.7 % | 2.2 % |

: Footprints and compounds by region (analysis run). Classes other than residential and unknown each account for less than 1 % in every region and are given in `model/building-stats.json`.

# The model

## The address and its forms

Each compound has one identity and four forms (the table below). All four map one to one. The remembered form contains no letters to learn and no check character. The zone name on the written form informs the reader; it is not part of the identity.

| Form | Example | Used by |
|:--|:--|:--|
| Remembered | **Ouakam 2512** | everyone: said, written on a parcel, typed in a message |
| Written | **OUAKAM 2512 · DAKAR** | plates, stickers, forms |
| Machine | `SN-DKR-0080-2512-J` | databases, QR codes, partner systems |
| Spot | `DKR 5553 1512` | any point with no compound |

: The four forms of an address. The machine form gives the zone, the place index, the number and the check letter; people never need it.

We use *Ouakam 2512* as the worked example throughout. It is a single-storey house in the quartier of Ouakam, in zone DKR (Dakar), place index 80; its machine form is `SN-DKR-0080-2512-J`.

## Zones

Each address hangs off a code zone, which supplies its written name, its registry file and its spot grid. The 14 régions are too large for one number space: Tambacounda covers 42,214 km², and Thiès holds 803,020 footprints. The zones are the 45 départements of the 2019 boundaries, with Mbacké split in two: its Ndame arrondissement, which holds Touba and Mbacké town and 417,008 footprints, becomes zone TBA, and the remainder becomes KTF (Kaël-Taïf). The zones were frozen when the registry was first issued and never follow later administrative changes. When Keur Massar became Senegal's 46th département in 2021, a model tied to the administrative map would have had to readdress every home in it; here Keur Massar stays in zone PKN and its current département is an attribute of the place card. Figure 2 shows the 46 zones and the density of compounds.

![The 46 frozen code zones and the density of the 3,597,128 issued addresses, in compounds per 4 km × 4 km cell on the UTM zone 28N grid. Sources: `model/zones.geojson`, `registry/anchors/`.](figures/zones-map.svg)

Let $Z$ be the set of zones, each with an index $\iota(z) \in \{0, \dots, 45\}$ in key order and an outline $\partial z$. A point $p$ lies in the zone

$$
\zeta(p) =
\begin{cases}
\arg\min_{z \in Z} \{\iota(z) : p \in \operatorname{int} \partial z\} & \text{if such a zone exists,}\\
\arg\min_{z \in Z} \min_{v \in \partial z} \lVert \pi(p) - \pi(v) \rVert & \text{if that distance is at most } 2\,000 \text{ m,}\\
\varnothing & \text{otherwise,}
\end{cases}
\tag{1}
$$

where $\pi$ is the projection to UTM zone 28N (Eq. (15)), $v$ runs over the vertices of the outline, and membership is tested by ray casting with holes excluded. The second case catches points on the coast and along river borders that the 2019 outlines miss.

**The border decides.** The département outlines, and the 2 km reach of Eq. (1) along coasts and rivers, can extend beyond the national border $B$, OpenStreetMap's admin_level 2 boundary. Whatever Eq. (1) gives, a point outside $B$ with $\min_{q \in B} \lVert \pi(p) - \pi(q) \rVert > 300$ m is outside Senegal, $\zeta(p) = \varnothing$: grouping drops the structures and compounds that lie there (Section 4.12), the issuer gives them no address, and an entrance never moves there. The 300 m margin absorbs the positional error of footprints and of the border line itself, which follows rivers such as the Senegal and the Gambia. The engine ships the border simplified by Douglas–Peucker at 50 m; the simplified line strays at most 50.4 m from the true one, so the engine applies 249 m to it and never accepts a point more than 300 m outside the true border.

Each zone has a square frame in UTM metres, used for spot codes and for numbering. With $E$ and $N$ the eastings and northings of the zone's outline,

$$
\begin{aligned}
E_0 &= 1000 \left\lfloor \tfrac{\min E}{1000} \right\rfloor, \qquad
N_0 = 1000 \left\lfloor \tfrac{\min N}{1000} \right\rfloor, \qquad
F = 1000 \left\lceil \tfrac{\max(\max E - E_0,\; \max N - N_0)}{1000} \right\rceil, \\
s &= \begin{cases} \min\{\sigma \in \{1, 2, 5, 10\} \text{ m} : F/\sigma \le 10^4\} & \text{if } F \le 100 \text{ km},\\ 10 \text{ m} & \text{otherwise,} \end{cases}
\qquad
k = \begin{cases} 4 & \text{if } F/s \le 10^4,\\ 5 & \text{otherwise,} \end{cases}
\end{aligned}
\tag{2}
$$

where $F$ is the side of the frame, $s$ the spot cell and $k$ the number of digits per axis of a spot code. For Dakar, $E_0 = 227\,000$ m, $N_0 = 1\,620\,000$ m and $F = 16$ km, so $s = 2$ m and $k = 4$. Across the 46 zones, Guédiawaye has 1 m cells, Dakar and Pikine 2 m, six zones (Touba, Saint-Louis, Rufisque, Bambey, Guinguinéo and Oussouye) 5 m and the rest 10 m; the 18 zones whose frames exceed 100 km have five digits per axis.

## The place word

The place word is the quartier in towns, the village in the countryside, or the cité where a cité is what people say. Let $Q(z)$ be the quartiers, suburbs, villages, localities and cités of zone $z$, and $T(z)$ its towns. A compound $c$ takes the place

$$
\lambda(c) =
\begin{cases}
\arg\min_{q \in Q(z)} d(c, q) & \text{if } \min_{q \in Q(z)} d(c, q) \le 2\,500 \text{ m},\\
\arg\min_{t \in T(z)} d(c, t) & \text{else, if } \min_{t \in T(z)} d(c, t) \le 10\,000 \text{ m},\\
\arg\min_{q \in Q(z) \cup T(z)} d(c, q) & \text{otherwise,}
\end{cases}
\tag{3}
$$

where $d$ is the distance in UTM metres between the compound's centroid and the place point, ties going to the lower place index. The assignment is fixed when the compound is first numbered and is never recomputed. If a quartier is renamed, split or disputed, the address does not change; the new name is added as an alias.

## The plate name

Names taken from the map are often too long to say: "Keur Serigne Ablaye Yakhine", "Parcelles Assainies", "S.I.C.A.P. Liberté Six". Each place therefore keeps two names. The *official name* is printed in small type on the card and the plate and is still accepted when typed. The *plate name* is the one in the address. Let $|s|$ be the number of characters of a string $s$ in Unicode normalisation form C (an accented letter, a space, a hyphen or an apostrophe counts one) and $w(s)$ its words, a hyphen separating words and a trailing sector numeral counting as a character but not as a word. A plate name is admissible when

$$
\operatorname{ok}(s) \iff |s| \le 12 \;\wedge\; \bigl|\, w(s) \setminus L \,\bigr| \le 2 ,
\tag{4}
$$

where $L$ is the set of linking words (de, du, des, d', la, le, les, l', et, sur, en, au, aux, à), which are not counted.

The plate name is derived by a fixed rule, in this order: (i) a short form people already use *and* for which a written source exists wins: "Saly" for Saly Portudal [@wikisaly], "Plateau" for Dakar-Plateau [@wikiplateau]; (ii) otherwise the name is cleaned: a trailing numeral is written in digits, generic words (*quartier*, *village de*, *hameau*, *lotissement*), developer labels (S.I.C.A.P.), brackets and second spellings are dropped, so S.I.C.A.P. Liberté Six becomes "Liberté 6"; "Cité" is kept when the name fits ("Cité Lamy"), because that is how people say it; (iii) if the cleaned name still fails Eq. (4), the candidates are the runs of whole words that satisfy it, ranked by the rarity of their words among all Senegalese place names, and the best is taken only when its score is at least 1.5 times that of the next. No word is ever cut.

Many Senegalese names cannot be shortened safely. "Keur Momar Sarr" is the village of Momar Sarr, and any cut drops part of his name; the same holds for names opening with Darou, Médina, Saré, Sinthiou, Gourel or Touba, and for names that hold a given or family name. "Nguékokh Wolof" and "Nguékokh Sérère" are two villages, so an ethnic or compass qualifier is never dropped silently. A short form may not become the name of a well-known town or of another place in the same zone. In all these cases the place is flagged for its commune with up to three candidates; the first is used provisionally, and the commune may confirm it or choose another, once, without changing the number.

Of the 14,997 official names, 4,208 fail Eq. (4) (4,154 by length, 1,474 by words). The rule keeps 10,763 names as they are, cleans 100, applies a documented short form to 3 and keeps the most distinctive words of 1,016. It sends 3,116 to the commune: the 3,115 it cannot shorten safely, and one cleaned name, "Richard Toll" (from Campement Richard Toll), that would equal a well-known town. Of these, 172 have no admissible part ("Diabrikindiong", "Touba Mosquée") and stay over the limit until the commune decides. These 3,116 places hold 739,058 addresses. An official name that two different plate names would both claim is dropped as an alias, so that a typed name never leads to two places; this affects 55 names.

## The name key

Two places bear the same name when their name keys are equal. The key folds everything that people confuse by ear or in spelling, in French and in Wolof [@decret2005]. It is the composition

$$
\kappa(s) = \tau \circ \chi \circ \phi \circ \beta \circ \eta \circ \nu \circ \sigma \circ \alpha (s),
\tag{5}
$$

whose steps are given in the table below, applied from right to left. Ouakam and Wakam both give `wakam`, Mbacké and Mbakke both give `mbak`, and Thiès and Ties both give `ties`. Folding too much only lengthens a range; folding too little would give two places one address, so the rule is deliberately generous.

| Step | Rule | Example |
|:--|:--|:--|
| $\alpha$, letters | ñ → ny, œ → oe, æ → ae; accents and case removed | Kër → ker |
| $\sigma$, split | hyphens, apostrophes, dots and brackets become spaces; St, Ste → saint | Sacré-Cœur → sacre coeur |
| $\nu$, numeral | a trailing number, with *numéro* or *no* before it, is dropped | HLM 5 → hlm |
| $\eta$, lead | le, la, les, l', de, du, d', quartier, village, hameau dropped when more follows | Quartier Médina → medina |
| $\beta$, join | spaces removed | keur massar → keurmassar |
| $\phi$, fold | ou before a vowel → w, other ou → u; eu → e; kh → x; th → t; ph → f; dj, and di before a vowel → j; gn → ny; c before e, i, y → s; ck, qu, q, c → k; y → i; silent h dropped | Ouakam → wakam; Ndiaye → njai |
| $\chi$, collapse | doubled letters become one | gunass → gunas |
| $\tau$, trim | a final silent e dropped | njaiene → njaien |

: The steps of the name key, Eq. (5).

The plate names of the 14,997 places fold to 11,043 keys. Of these, 1,974 are borne by more than one place, 5,928 places in all, holding 41.9 % of compounds (1,506,591); 1,322 of the repeated names occur in several zones and 652 within one zone only. The most repeated is Ndiayène (32 places in 18 zones), followed by Mbayène and Thiékène (28 each), Darou Salam (23) and Ndiobène (22).

## One national range per name

The places of one name key form a *family* $\mathcal{F}$. Each family has one national range of $d$-digit numbers, $[10^{d-1}, 10^d - 1]$, and each place $i \in \mathcal{F}$ receives a block of it. A place with $n_i$ compounds at first issue needs a block of three times its compounds, rounded up to the grain $g_d$ of the range:

$$
b(n_i, d) = g_d \max\!\left(1, \left\lceil \frac{3 n_i}{g_d} \right\rceil\right), \qquad g_3 = 10,\quad g_4 = g_5 = 100 .
\tag{6}
$$

The factor three is a reserve for growth. If the compounds of a place grow at a constant annual rate $r$, the block fills after

$$
T(r) = \frac{\ln 3}{\ln(1 + r)} \ \text{years}.
\tag{7}
$$

Senegal's urban population grew by between 3.3 % and 4.8 % a year from 2015 to 2024, 4.6 % on average [@wdi2026], which gives $T$ between 23 and 34 years, 24 years at the average. A place whose block fills does not run out: it receives a further block from its name's free space (Eq. (13)).

All places of a family share one length $d^*$, the shortest for which their blocks fill at most 90 % of the range, so that at least a tenth stays free for new places of that name:

$$
d^* = \min\left\{ d \in \{3, 4, 5\} : \sum_{i \in \mathcal{F}} b(n_i, d) \le 0.9 \cdot 9 \cdot 10^{d-1} \right\}.
\tag{8}
$$

A three-digit range has 900 numbers, of which 810 may be allocated; a four-digit range 9,000 (8,100); a five-digit range 90,000 (81,000). A place alone therefore fits three digits up to 270 compounds, four up to 2,700 and five up to 27,000. Figure 3 shows how the places of Senegal distribute across these thresholds: the median place has 79 compounds and 12,434 of the 14,997 places have at most 270.

![Compounds per place, for the 14,997 places of the registry, on logarithmic bins of five per decade. The dashed lines mark the largest place that fits alone in a three-, four- and five-digit range (Eq. (8)). Source: `registry/`.](figures/lieu-sizes.svg)

Blocks are cut from the bottom of the range in the order (zone key, place index):

$$
\ell_1 = 10^{d^*-1}, \qquad h_i = \ell_i + b(n_i, d^*) - 1, \qquad \ell_{i+1} = h_i + 1 .
\tag{9}
$$

*Worked example.* Ouakam is alone in its family (`wakam`, family 10796) and had $n = 788$ compounds at first issue. Three digits would need $3 \times 788 = 2\,364 > 810$ numbers, so $d^* = 4$ and $b = 100 \lceil 2\,364/100 \rceil = 2\,400$: Ouakam's block is 1000–3399.

Repeated names show the scheme at work (Figure 4). The nine places called Médina share the five-digit range: Dakar's Médina holds 10400–17699, Saint-Louis's 19500–22799 and Ziguinchor's 22800–23299, and 23300–99999 remains free. The 23 places called Darou Salam, in 17 zones, hold 22,082 compounds; Pikine's Darou Salam has 23200–45799 and Touba's 46200–76599, and 75.0 % of the range is allocated. With today's counts no name needs more than five digits. Names that one day outgrow their range would take one established qualifier that people already use, decided once per name with the commune, as "Médina Baye" is already a name apart from "Médina".

![Two national name ranges. Every place called Médina, and every place called Darou Salam, draws its numbers from one five-digit range, cut into one block per place (Eqs. (6)–(9)); blocks alternate in colour, and grey is the part of the range still free. Source: `model/name-families.json`.](figures/name-ranges.svg)

## Numbering along a Hilbert curve

Within its block, a place's compounds are numbered along a Hilbert curve [@hilbert1891], so that neighbours receive close numbers, as along a street. The zone's frame is divided into $2^{16} \times 2^{16}$ cells of side $\delta = F / 2^{16}$. A compound with centroid $(E, N)$ falls in the cell

$$
x = \min\!\left(2^{16} - 1, \max\!\left(0, \left\lfloor \frac{E - E_0}{\delta} \right\rfloor\right)\right), \qquad
y = \min\!\left(2^{16} - 1, \max\!\left(0, \left\lfloor \frac{N - N_0}{\delta} \right\rfloor\right)\right),
\tag{10}
$$

and its Hilbert index $H(x, y)$ is computed from the top level down. With $h \leftarrow 0$ and, for $m = 2^{15}, 2^{14}, \dots, 1$,

$$
\begin{aligned}
r_x &= [\,x \mathbin{\&} m \ne 0\,], \qquad r_y = [\,y \mathbin{\&} m \ne 0\,], \qquad h \leftarrow h + m^2 \bigl( (3 r_x) \oplus r_y \bigr),\\
(x, y) &\leftarrow \begin{cases} (m - 1 - y,\; m - 1 - x) & \text{if } r_y = 0 \text{ and } r_x = 1,\\ (y, x) & \text{if } r_y = 0 \text{ and } r_x = 0,\\ (x, y) & \text{if } r_y = 1, \end{cases}
\end{aligned}
\tag{11}
$$

where $\&$ is the bitwise conjunction, $\oplus$ the bitwise exclusive or and $[\cdot]$ the indicator. Consecutive indices are always adjacent cells, and the curve keeps neighbouring cells together better than the Z-order and Gray-code curves [@moon2001].

At first issue, the $n$ compounds of a place with block $[\ell, h]$ are sorted by $(H, E, N)$ and spread evenly over the block:

$$
N_i = \ell + \left\lfloor \left(i + \tfrac12\right) \frac{h - \ell + 1}{n} \right\rfloor, \qquad i = 0, \dots, n - 1 .
\tag{12}
$$

With the threefold reserve there are on average two free numbers between neighbours.

*Worked example.* The centroid of Ouakam 2512 is at $E = 232\,438.4$ m, $N = 1\,629\,353.1$ m. With $\delta = 16\,000 / 65\,536 \approx 0.244$ m it lies in cell $(22\,275, 38\,310)$, of Hilbert index $2\,022\,592\,185$. Of Ouakam's 788 compounds, 496 come before it on the curve, so $i = 496$ and

$$
N_{496} = 1000 + \left\lfloor 496.5 \times \frac{2\,400}{788} \right\rfloor = 1000 + \lfloor 1\,512.18 \rfloor = 2512 .
$$

Figure 5 shows the result for the whole quartier: the numbers sweep across Ouakam in contiguous patches, and the line joining consecutive numbers rarely jumps.

![Ouakam's 788 compounds at their centroids, coloured by the number issued, in metres from the origin of zone DKR's frame. The grey line joins consecutive numbers, which is the order of the Hilbert curve (Eqs. (10)–(12)). Source: `registry/DKR.csv.gz`, `registry/anchors/DKR.csv.gz`.](figures/ouakam-hilbert.svg)

## New compounds

Issued numbers never change. A compound built after first issue, at Hilbert index $H$ in a place with first block $[\ell, h]$, has as neighbours the issued numbers $a$ just before and $b$ just after it on the curve (or $\ell - 1$ and $h + 1$ at the ends). Its number is

$$
N_{\text{new}} =
\begin{cases}
\lfloor (a + b)/2 \rfloor & \text{if } b - a \ge 2 \text{ and it is free,}\\
\min \text{ free number of the place's further blocks} & \text{else, if one exists,}\\
\ell' \text{, first of a new block } [\ell', \ell' + g_{d^*} - 1] & \text{else, if the name's range has room,}\\
\text{first number of "\textit{place} Extension"} & \text{otherwise.}
\end{cases}
\tag{13}
$$

A new block is cut above the highest block of the name and is frozen at once. "Extension" follows how Senegalese towns already name their growth (Keur Massar Extension, Médina Gounass Extension); since the official name "Ouakam Extension" already exceeds twelve characters, the commune gives the new district its plate name. A retired number counts as used and is never given again.

## Decoding with no context

A remembered address is decoded from the text alone. The trailing digits form the number $D$ and the words before them the name $P$. The key $\kappa(P)$ gives the family, the family gives its length $d^*$, and the number is the last $d^*$ digits of $D$; any digits before them must equal the place's sector numeral ("HLM 5 17 394"). The candidates are

$$
\operatorname{dec}(P, D) = \bigl\{ (i, N) : i \in \mathcal{F}(\kappa(P)),\; N = D \bmod 10^{d^*},\; N \in B_i \bigr\},
\tag{14}
$$

where $B_i$ is the union of the blocks of place $i$.

**Proposition 1.** *For any $(P, D)$, $\operatorname{dec}(P, D)$ has at most one element.* The blocks of one family are disjoint by construction (Eq. (9) and Eq. (13), which cuts new blocks only from free space), and $d^*$ is fixed for the family, so $N$ is determined by $D$ and lies in at most one block. Aliases are kept only when they point to a single family (Section 4.4). $\square$

Proposition 1 is what makes the spoken address unique in Senegal without a town or a position. Section 6.1 verifies it on every issued address.

## The check letter

The machine form carries a check letter that people never see: not on plates, not on stickers and not in the spoken form. Its payload is the family identifier written with five digits followed by the number written with five, $u = u_1 u_2 \cdots u_{10}$. It is computed with the pure system MOD 11-2 of ISO/IEC 7064 [@iso7064]:

$$
p_0 = 0, \qquad p_k = 2\,(p_{k-1} + u_k) \bmod 11 \quad (k = 1, \dots, 10), \qquad c = (12 - p_{10}) \bmod 11,
\tag{15}
$$

and written as the $c$-th letter (from 0) of `FHJKMQRTWXZ`. The eleven letters were chosen for French speakers: one letter from each family of rhyming letter names (bé, cé, dé, gé, pé, té, vé), J rather than G (French speakers confuse "gé" and "ji"), and no vowels, so that no word can be formed.

**Proposition 2.** *MOD 11-2 detects every single substitution and every transposition of two adjacent unequal digits.* Unrolling Eq. (15), $c \equiv 1 - \sum_k u_k w_k \pmod{11}$ with weights $w_k = 2^{11-k} \bmod 11$, all non-zero because 2 is invertible modulo the prime 11. Replacing $u_k$ by $u_k' \ne u_k$ changes the sum by $(u_k - u_k')\,w_k$, a product of two non-zero residues modulo a prime, hence non-zero. Swapping $u_k$ and $u_{k+1}$ changes it by $(u_k - u_{k+1})(w_k - w_{k+1}) = (u_k - u_{k+1})\,w_{k+1}$, since $w_k = 2 w_{k+1}$, which is again non-zero when $u_k \ne u_{k+1}$. $\square$

*Worked example.* For Ouakam 2512 the payload is $u = 10796\,02512$. The partial values $p_1, \dots, p_{10}$ are 2, 4, 0, 7, 4, 8, 9, 6, 3, 10, so $c = (12 - 10) \bmod 11 = 2$, the letter J, and the machine form is `SN-DKR-0080-2512-J`.

The letter covers the family and the number; the place follows from the block. A one-digit slip that moves a number from Dakar's Médina into Saint-Louis's block therefore changes the payload in exactly one digit and is always refused in a machine form. In the spoken form, which has no letter, the application shows the town before it routes (Section 6.4).

## Spot codes

A point that has no compound, such as a field, a market pitch or an empty plot, receives a spot code computed offline. With $(E, N) = \pi(\varphi, \lambda)$,

$$
\begin{aligned}
x &= \left\lfloor \frac{E - E_0}{s} \right\rfloor, & y &= \left\lfloor \frac{N - N_0}{s} \right\rfloor,\\
\hat E &= E_0 + \left(x + \tfrac12\right) s, & \hat N &= N_0 + \left(y + \tfrac12\right) s,
\end{aligned}
\tag{16}
$$

where $x$ and $y$ are written with $k$ digits each after the zone key, and $(\hat E, \hat N)$ is the decoded point, the centre of the cell. The decoding error is at most half the cell's diagonal, $s\sqrt{2}/2$: 0.7 m for 1 m cells, 1.4 m for 2 m and 7.1 m for 10 m. The Place de l'Indépendance in Dakar ($\varphi = 14.6681^\circ$, $\lambda = -17.4317^\circ$) projects to $E = 238\,106.2$ m, $N = 1\,623\,024.8$ m, so $x = \lfloor 11\,106.2 / 2 \rfloor = 5553$, $y = \lfloor 3\,024.8 / 2 \rfloor = 1512$, and its spot code is `DKR 5553 1512` (Figure 6). Spot codes carry no check letter, because people type them; a code written with an older trailing letter is still verified.

![The spot grid of zone DKR: a 16 km frame from $(E_0, N_0) = (227\,000, 1\,620\,000)$ m in UTM zone 28N, cut into 2 m cells, so that each axis runs from 0000 to 7999 (Eqs. (2) and (16)). The outline is the zone's; the two points are worked examples of this paper. Sources: `model/zones.json`, `model/zones.geojson`.](figures/dakar-spot.svg)

The projection is the transverse Mercator projection of WGS 84 on UTM zone 28N, computed with Krüger's series to the fourth order in the third flattening [@karney2011]. With $a$ and $f$ the WGS 84 semi-major axis and flattening, $k_0 = 0.9996$, $\lambda_0 = -15^\circ$ and $\alpha_j$ the series coefficients,

$$
\begin{aligned}
n &= \frac{f}{2 - f}, \qquad A = \frac{a}{1 + n}\left(1 + \frac{n^2}{4} + \frac{n^4}{64}\right), \qquad e = \frac{2\sqrt n}{1 + n},\\
t &= \sinh\!\bigl(\operatorname{artanh}(\sin\varphi) - e \operatorname{artanh}(e \sin\varphi)\bigr), \qquad
\xi' = \operatorname{atan2}\bigl(t, \cos(\lambda - \lambda_0)\bigr), \qquad
\eta' = \operatorname{artanh}\frac{\sin(\lambda - \lambda_0)}{\sqrt{1 + t^2}},\\
\xi &= \xi' + \sum_{j=1}^{4} \alpha_j \sin(2j\xi') \cosh(2j\eta'), \qquad
\eta = \eta' + \sum_{j=1}^{4} \alpha_j \cos(2j\xi') \sinh(2j\eta'),\\
E &= 500\,000 + k_0 A \eta, \qquad N = k_0 A \xi ,
\end{aligned}
\tag{17}
$$

with $n \approx 0.001\,679\,2$ and $A \approx 6\,367\,449.146$ m. Over Senegal, which lies almost centred on the zone's central meridian, the series is accurate to well under a millimetre [@karney2011].

## Compounds

Most Senegalese live in *concessions*: walled family plots with several buildings, one gate and often several households. Villas have a gatehouse and an annexe; apartment blocks have many flats behind one door; shops are built into the street walls of concessions. The address therefore belongs to the compound, its buildings are numbered sub-units ("Ouakam 2512, bâtiment 2"), flats and shop doors are units, and navigation ends at the gate.

Footprints are grouped into compounds before numbering. For two structures $a$ and $b$ with centroids $c_a, c_b$ and areas $A_a, A_b$, the *gap* is the distance between centroids less the radii of circles of the same areas, and a structure is *urban* when its 250 m tile holds at least 100 structures (1,600 per km²):

$$
\operatorname{gap}(a, b) = \lVert c_a - c_b \rVert - \sqrt{\frac{A_a}{\pi}} - \sqrt{\frac{A_b}{\pi}}, \qquad
\operatorname{urban}(a) \iff \bigl|\operatorname{tile}_{250}(a)\bigr| \ge 100 .
\tag{18}
$$

The rules are applied in order. R0 (*enclosure*): all structures inside a mapped wall, fence or gated site, an owner's outline or, later, a cadastral parcel form one compound. R1 (*satellite*): a structure under 30 m² with a gap of at most 4 m (urban) or 8 m (rural) to a structure of at least 30 m² joins it; these are kitchens, toilets and gatehouses. R2 (*rural concession*): in rural fabric, structures under 120 m² with gaps of at most 6 m form single-linkage clusters of at most 30 structures. R3 (*people*): confirmations by residents merge or split compounds. Two main structures in urban fabric are never merged by shape alone: in the Médina or in Pikine, houses touching wall to wall are separate concessions. A cité with one gate (SICAP, HLM, private cités) is an *estate*: each house keeps its own address behind the estate gate. Regrouping never changes an issued address. Before any rule applies, structures whose centre and compounds whose entrance lie more than 300 m outside the national border are dropped (Section 4.2).

## Building profiles

Every structure in the registry carries a profile: a use class from a Senegalese taxonomy (concession, maison basse, immeuble R+*n*, case and annexe for homes; boutique, marché, bureaux, entrepôt, atelier and station for commerce; administration, school, daara, university, hospital, health post and pharmacy for public use; mosque, church and mausoleum for worship; fishing quays, seed stores and granaries, among others), a confidence for the class, the footprint and perimeter, the floors where known (written RDC, R+1, R+2, as in Dakar), the floor area, and the source and date of each attribute. Classes are inferred in a fixed order: OpenStreetMap tags first (confidence 0.85–0.9), then mapped places inside the footprint (0.6–0.7), then shape (0.2–0.5); confirmations by people (0.95) override all of them. A daara is never inferred from shape, because many daaras are family homes.

## Government addresses first: the coverage mask

Where the government already gives an address, N-Ways does not create a competing one. The rule is applied per place, as a *coverage mask* with three levels. A place is *official-municipal* when the municipal street-addressing programme covers it, on any one of three pieces of evidence: an official dataset from a commune, the ARTP or the Agence de Développement Municipal; three or more mapped streets carrying programme references (1,601 such streets are mapped nationally); or plates confirmed by people at its doors. There the address shown is the street and number as the commune writes them, for example "120 Rue PE-44, Point E", and no N-Ways plate goes up; until a door's official number is known, the N-Ways address is shown and marked as temporary. A place is *ann* as soon as the ANN publishes addresses for it, and the ANN address is then shown as written. Every other place is *nways*. Postcodes do not count as coverage, because they are delivery-office zones, but every compound carries its postcode where it is known.

The mask only grows. When official coverage reaches a place, its N-Ways addresses stop being primary but remain valid as aliases that resolve to the official address, and no number is reissued. In the issued registry, 112 places are official-municipal; they hold 128,950 compounds (3.6 % nationally and 44.0 % of Dakar département), and the official door number is already known for 87 of them.

## Saying the address

In French the number is said as house and telephone numbers are: three digits whole ("Affiniam, trois cent vingt"), four digits in two pairs ("Ouakam, vingt-cinq, douze") and five digits as two then three ("Médina, douze, cent quarante-neuf" for 12 149). In Wolof the digits are said one by one ("Ouakam, ñaar, juróom, benn, ñaar"). Wolof 3 and 4 (*ñett*, *ñeent*) and 8 and 9 (*juróom ñett*, *juróom ñeent*) sound alike, so the application always reads the address back and shows the building before it routes. Speakers of Pulaar, Serer, Jola, Mandinka and Soninké use the same place word and say the digits in French or Wolof, as they do for telephone numbers.

# Implementation

## The reference engine

The reference engine (`engine/reference/sn_engine.py`, with `plate_names.py`) is written in standard-library Python 3.9 and needs only the files in `model/`. It implements every formula of Section 4: the zone lookup and frames (Eqs. (1)–(2)), the place assignment and plate names (Eqs. (3)–(4)), the name key (Eq. (5)), the national ranges (Eqs. (6)–(9)), Hilbert numbering and insertion (Eqs. (10)–(13)), context-free decoding (Eq. (14)), the check letter (Eq. (15)), spot codes and the projection (Eqs. (16)–(17)) and compound grouping (Eq. (18)). Its self-test checks the projection, every single error and adjacent transposition of the check letter on random payloads, spot round trips, numbering, twelve same-name decodings and the published test vectors. The normative description is the specification in `engine/SPEC.md`.

## The registry

The registry (`registry/`) publishes every issued address, with nothing held back: one gzip file per zone, one row per address, sorted by name family and then number. Each row gives the machine, remembered and written forms; the place, the number and the check letter; the status (every address is *provisional* until residents confirm it) and how and when it was issued; the entrance and its spot code; the compound's class, use, kind, number of structures and floor area; the postcode where mapped; and the coverage level with the official address where the commune numbered the door. No row describes the people in a home. `lieux.csv` gives the frozen place list with each place's plate and official names, key, family, length and blocks. `anchors/` gives each compound's centroid at full precision, row for row with the zone files: it is the point that Eq. (10) orders by, and with it an independent deployment numbers new compounds exactly as the issuer does. A manifest gives the counts and the SHA-256 of every file before compression.

## The server and its interface

`server/` is a ready-made HTTP service, in standard-library Python, that any ministry, post office or developer can deploy with `docker compose up`. On first start it imports the registry into SQLite, verifying each file against the manifest and refusing any mismatch; it then serves a JSON interface under `/v1`: health and information, the full card of an address, search by any form (remembered, written, machine or spot, with any spacing, case or accents), the compound at a point and the compounds near it, verification of a machine form, spot encoding and decoding, zones and places, and a paged list of a zone's addresses. Its export writes the registry back in the published format, byte for byte. On the one deployment that the State or N-WAYS LIMITED designates as issuer, `POST /v1/codes` issues new addresses by the rules of Sections 4.2 and 4.8 and `PATCH` confirms, retires or moves them. Every other deployment is read-only, because two issuers working from the same registry would each see the same number as free and give it to two compounds. The interface is described in `server/openapi.yaml` and, with real requests and responses, in `docs/api.md`.

## Conformance

Three kinds of test tie the published components to the issuer. The engine's vectors (`engine/reference/vectors.json`) fix spot codes, check letters, spoken numbers, same-name decodings, plate names and real footprint samples. The server's 62 parity cases (`server/testdata/parity.json`) record, for new compounds, extra doors, outlines of every size class and extension blocks, the place, number, forms and profile that the issuer's own implementation produced against a fixture registry; the server reproduces all of them. On the full registry, an import followed by an export reproduces every published file byte for byte, and 59 addresses compared field by field with the issuer's live interface showed no difference over 1,416 fields.

## Getting and sharing an address

Nothing is asked of a household. Every compound already on the map received its address when the registry was issued, and the N-Ways application shows it in one tap ("Get my code"), in French or Wolof: the compound where one stands, or the one tapped on the map. Sharing takes one tap and sends a message with the address and a link that opens the map without the application. A house not yet on the map is added in four steps of about two minutes ("Add my home"): the gate position is averaged over ten seconds and photographed from the street; the outline is traced on imagery, walked inside the wall with the phone's camera, or imported from a survey plan whose datum (Yoff, NSGD2004 or WGS 84) must be stated, with its NICAD or lotissement plot number where there is one; the household states the number of buildings and floors and the use; and the free number between the neighbours is issued at once, provisionally. An outline that overlaps an existing compound is refused, and the flow states, in French and Wolof, that an address is not a land title. An address becomes *confirmed* when independent residents agree that it is right, by the same automatic consensus that corrects the map; no one reviews addresses by hand. A plate or a QR sticker on the gate serves those without a smartphone.

# Evaluation

All measurements in this section are computed from the published registry and the reference engine by `tools/paper-evaluation.py`; the results are in `docs/figures/data/evaluation.json`.

## Uniqueness and decoding

All 3,597,128 machine forms are distinct, and so are all 3,597,128 remembered forms after case and accent folding. Every remembered form was decoded by the engine with no zone and no position (Eq. (14)): 3,597,128 decoded to exactly the compound of the registry row, none to another compound, none to several and none to nothing. Proposition 1 thus holds on the whole registry.

## Lengths

Of the issued numbers, 717,894 (20.0 %) have three digits, 1,676,892 (46.6 %) four and 1,202,342 (33.4 %) five. The remembered address has a median of 13 characters, including the space; 95 % of addresses have at most 18 characters and 99 % at most 20. The longest outside the provisional names is "Yeumbeul Sud 20 699" (19 characters); with the provisional names it is "Ancien Marché Hebdomadaire 22 199" (33), a name that its commune is to shorten. Numbers are long where place points are sparse: in Touba 83.9 % of compounds and in Pikine 87.0 % have five digits (Appendix A). Curating sub-quartiers with the communes would bring many of them down to four digits.

## Locality

Over all places, two compounds with consecutive numbers lie a median 23.4 m apart (90th percentile 80.8 m), against 561.4 m (90th percentile 1,912 m) for two compounds of the same place drawn at random. Numbers therefore follow the ground: a courier who finds "Ouakam 2512" will find "Ouakam 2515" a few doors away.

## Errors

We applied every one-digit substitution to the numbers of 100,000 randomly drawn addresses, keeping the length and the leading digit non-zero, which gives 3,621,599 erroneous numbers. Their outcomes are given below.

| Outcome of a one-digit slip in the remembered number | Share |
|:--|--:|
| No issued address (in no block, or a free number of a block) | 76.1 % |
| Another issued compound of the same place | 22.6 % |
| An issued compound of another place with the same name | 1.3 % |

: What a one-digit slip lands on, over 3,621,599 slips of 100,000 addresses.

Three quarters of slips are refused because the address does not exist. Most of the rest land on another compound of the same place; the application then shows a photograph, class and street that the person does not recognise. Only 1.3 % land in another town, and the town is then shown before routing. In a machine form all such slips are refused: over the same sample, the check letter detected all 9,000,000 single substitutions and all 800,830 adjacent transpositions of unequal digits, as Proposition 2 requires.

The 22.6 % figure is the empirical counterpart of a simple estimate. If a block holds $n$ issued numbers among $b$, a uniformly random number of the block is issued with probability

$$
P(\text{hit}) \approx \frac{n}{b} \approx \frac{1}{3},
\tag{19}
$$

by Eq. (6). The measured share is lower because slips in the leading digits leave the block.

## Spot codes

For 400 random points in each of the 46 zone frames (18,400 points), the distance between a point and the decoded centre of its spot cell never exceeded the bound $s\sqrt 2 / 2$ of Eq. (16); the largest ratio of error to bound was 0.997.

## Coverage

Every compound on the building map inside the national border received an address: coverage is complete by construction. No issued entrance lies more than 300 m outside the border: measured against the full border line, two lie outside it, both by less than a metre. Two qualifications matter. First, the mapped building stock is itself incomplete, especially for recent construction; "Add my home" and the insertion rule of Eq. (13) exist for this reason. Second, entrances are known for few compounds: 142 addresses route to a mapped gate and the others to the compound's centre until a gate is confirmed.

## Same names, different places

The table below shows decoding on real issued addresses of repeated names, with the place as zone and index. Each is decoded from the text alone. The last column gives a one-digit slip that lands in another same-named place's block: in a machine form the check letter refuses it, and in the spoken form the application shows the other town. For HLM the sector numeral refuses it too.

| Remembered | Place | Block | Machine form | Slip into |
|:--|:--|:--|:--|:--|
| Médina 12 149 | Dakar (DKR/71) | 10400–17699 | `SN-DKR-0071-12149-J` | 22 149 → STL/90 |
| Médina 20 096 | Saint-Louis (STL/90) | 19500–22799 | `SN-STL-0090-20096-T` | 10 096 → DAG/118 |
| Médina 23 151 | Ziguinchor (ZIG/155) | 22800–23299 | `SN-ZIG-0155-23151-Z` | 13 151 → DKR/71 |
| Pikine 12 150 | Diourbel (DBL/329) | 10000–20899 | `SN-DBL-0329-12150-H` | 22 150 → STL/151 |
| Pikine 22 150 | Saint-Louis (STL/151) | 20900–29999 | `SN-STL-0151-22150-J` | 12 150 → DBL/329 |
| Darou Salam 26 690 | Pikine (PKN/10) | 23200–45799 | `SN-PKN-0010-26690-M` | 16 690 → MBR/32 |
| Darou Salam 50 859 | Touba (TBA/54) | 46200–76599 | `SN-TBA-0054-50859-W` | 10 859 → GOS/49 |
| Gounas 11 799 | Guédiawaye (GDW/6) | 10000–21999 | `SN-GDW-0006-11799-T` | 31 799 → VEL/204 |
| HLM 5 17 394 | Dakar (DKR/54) | 17100–18399 | `SN-DKR-0054-17394-M` | 13 394 → DKR/51 (HLM 2) |
| Diawar 1419 | Dagana (DAG/35) | 1000–3799 | `SN-DAG-0035-1419-T` | 4419 → KBM/319 |
| Diawar 4085 | Kébémer (KBM/319) | 3800–5699 | `SN-KBM-0319-4085-M` | 1085 → DAG/35 |

: Same names, different places: real issued addresses decoded with no context.

The last two rows show a pair that only shortening brought together: "Mbenguène Diawar" in Kébémer has the plate name "Diawar", like the village of Diawar in Dagana, and the two now share one range in two blocks.

# Designs considered and rejected

The model is the result of several alternatives, each measured on the same building map before it was adopted or set aside.

| Option | Example | Assessment |
|:--|:--|:--|
| Alphanumeric grid code | `DKR 45 12 78 K` | ten symbols, four of them letters; French letter names rhyme (bé, cé, dé, gé, pé, té, vé) and G and J are confused; kept only for spot codes, which are rarely remembered |
| National digits-only code | `07 0080 4512` | ten digits that mean nothing to the holder; a slip lands on a real home anywhere in the country |
| Open Location Code | `7C2P+M4 Dakar` | letters and a plus sign; changes every few metres across one compound; not tied to a gate; kept as a cross-reference |
| Place and number, with the zone telling repeated names apart | `Médina 150, Ziguinchor` | an address that needs its town is not unique, because the town is not said; rejected |
| One number range per place | `Médina 150` in each Médina | two homes with the same spoken address; rejected |
| Full official names | `Keur Serigne Ablaye Yakhine 2 345` | too long to say or to write on a parcel |
| Plate name and one national range per name | **`Ouakam 2512`** | **adopted** |

: The forms considered.

Figure 7 gives the cost in digits of the three numbering designs. One range per place gives the shortest numbers (29.7 % of compounds with three digits), but its addresses are unique only with the zone. One range per name with the full official names lengthens numbers slightly (22.8 % with three digits) and makes addresses unique. Shortening the names to plate names brings more places under one name and lengthens numbers a little more (20.0 % with three digits), but the address becomes short enough to say. We judged one more digit a fair price: a digit is easier to remember than a town after a comma that nobody says, and it is what makes "Médina 12 149" mean Dakar wherever it is said.

![Share of compounds by number of digits under the three numbering designs, measured on the same compounds. The adopted design is the last row. Source: `model/name-families.json`.](figures/number-lengths.svg)

For the check character we compared ISO/IEC 7064 MOD 11-2, which needs an eleventh symbol, with Damm's decimal check digit, which detects the same errors with ten [@damm2007]. A letter suits Senegal better: a check digit appended to a number is easily read as part of it, whereas a letter from a fixed set of eleven is visibly separate, and MOD 11-2 is an international standard in wide use. We chose the letters for French ears, as described in Section 4.10. For ordering within a place we preferred the Hilbert curve to row-by-row or Morton (Z-order) numbering because of its better locality [@moon2001], which Section 6.3 confirms on the registry.

# Benefits to citizens

For a family in Pikine, in Touba or in a village of Kolda, an address changes four ordinary things.

**Being found.** A visitor, a taxi or a delivery rider is today guided by telephone, landmark by landmark. With an address, the person says one short phrase, "Ouakam, vingt-cinq, douze", and the application leads to the gate.

**Proving where one lives.** Banks, mobile-money agents, schools, employers and administrations ask for an address that can be checked. Before the registry, almost no household could give one:

| | Compounds | Share |
|:--|--:|--:|
| With a known official door number | 87 | 0.002 % |
| In quartiers of the municipal addressing programme | 128,950 | 3.6 % |
| With an address that can be said and checked | 3,597,128 | 100 % |

: Compounds by the kind of address they have.

**Receiving goods and services.** Families abroad, online shops and the water and electricity companies can send to an address rather than a description, and a household can request a connection, a meter reading or a repair at the right gate.

**Simplicity.** The address is free, needs no document and holds no personal data (Section 12). It is not a land title, and the application says so.

The benefit is greatest for those who have least today: the 96 % of compounds outside the addressed quartiers, the families of Touba's and Pikine's dense extensions, villages on the *domaine national* where nobody holds a titled parcel, and residents who read little, for whom a quartier they know and a number are easier than letters. We do not yet have a measured estimate of the time households spend giving directions, and Section 13 sets out how it will be measured.

# Logistics and commerce

Delivery in Senegal runs on the telephone. A rider reaches the quartier, calls the customer, is guided, often calls again, and sometimes gives up. What an address gives a logistics business is a stable key for each customer's compound, routing to the gate before the rider leaves, input that is checked at checkout rather than on the road (in machine forms the check letter catches every single wrong digit), the postcode for mail sorting, and open access: a courier, a shop, a bank or a fintech can resolve addresses in its own systems, offline, without paying anyone.

*Estimate.* We model the saving per 1,000 delivery attempts as

$$
S = 1\,000 \times f_0 \times \theta \times c ,
\tag{20}
$$

where $f_0$ is the share of first attempts that fail today, $\theta$ the fraction of those failures that a precise address removes, and $c$ the cost of one attempt. No published study measures these quantities in Senegal, so we take them from practitioners' estimates for Dakar and state the ranges. Reported first-attempt failure rates are 8–12 % in central Dakar and 12–15 % in the periphery [@bah2026b], and 22–30 % for deliveries to places without a formal address [@bah2026a]. Among failed cash-on-delivery attempts in Dakar, an incomplete address is cited for 22 % and an unreachable customer for 28 % [@bah2026c]. A motorbike run costs 1,000–1,500 FCFA in the centre and 1,500–2,500 FCFA in the periphery [@bah2026b]. We take $f_0 \in [0.08, 0.30]$, $\theta \in [0.22, 0.50]$ (from the share attributed to the address alone, to half of all failures, since an address also shortens the calls that an unreachable customer causes) and $c \in [1\,000, 2\,500]$ FCFA.

| $f_0$ | $\theta$ | $c$ (FCFA) | $S$ per 1,000 attempts (FCFA) |
|--:|--:|--:|--:|
| 0.08 | 0.22 | 1,000 | 17,600 |
| 0.15 | 0.30 | 1,750 | 78,750 |
| 0.30 | 0.50 | 2,500 | 375,000 |

: Saving per 1,000 delivery attempts, Eq. (20): low, central and high cases.

The central case corresponds to about 79 FCFA per attempt, or 4.5 % of its cost. The range spans more than an order of magnitude, which is itself the main finding: the saving depends on how often deliveries fail for want of a location, which Section 13 proposes to measure with partner couriers. These estimates come from commercial sources without a published method and should be read as indicative.

Two Senegalese settings illustrate the use. Touba receives very large numbers of pilgrims for the Grand Magal; hosts, traders and transporters can give one address for compounds that have no street name. Markets, wholesalers and transport garages in Dakar, Thiès and Kaolack can send goods to the right compound in a village rather than to the nearest town. Hotels and rentals on the Petite Côte, in Saint-Louis and in Casamance can give guests one address for a driver.

# Emergency services

An ambulance, the *sapeurs-pompiers* or the police face the courier's problem with more at stake. A qualitative study of emergency medical services in Kigali found that locating the patient depended on inadequate technology, on the local knowledge of callers and crews, and on repeated calls between caller, dispatcher and ambulance, and that this lengthened response intervals [@hunt2024]. We know of no published measurement for Senegal, which is itself a reason to start one.

With an address, the caller says one phrase, "Médina, douze, cent quarante-neuf". The dispatcher types it and the registry returns one compound, its town and its gate: there is no list of Médinas, because the number alone says it is Dakar's (Proposition 1). The dispatcher reads it back, and a slip that lands on another same-named place shows "Saint-Louis" rather than "Dakar", which the caller corrects at once. The crew drives to the gate, whose coordinates are given on the UTM zone 28N grid that Senegalese surveyors and many GIS systems use. The engine and the registry need no network, so a dispatch system can resolve addresses when the line drops.

*Estimate.* Larsen and colleagues modelled survival after out-of-hospital cardiac arrest as

$$
S_{\text{OHCA}} = 67 - 2.3\,t_{\text{CPR}} - 1.1\,t_{\text{defib}} - 2.1\,t_{\text{ACLS}} \quad \text{(per cent, times in minutes)},
\tag{21}
$$

where the three times are the intervals from collapse to cardiopulmonary resuscitation, to defibrillation and to advanced care [@larsen1993]. Where one crew brings all three, a delay $\Delta t$ in finding the gate delays all three intervals and costs $(2.3 + 1.1 + 2.1)\,\Delta t = 5.5\,\Delta t$ percentage points of survival: about 5.5 points for one minute, 11 for two and 27.5 for five. The model was fitted in King County, Washington; it gives an order of magnitude for Senegal, not a prediction, and as a linear model it is valid only while the predicted survival remains positive. Its direction, however, is not in doubt: where finding the gate takes minutes, an address that removes the search matters as much as a faster vehicle.

# Government coordination and planning

An address is a shared key. When ministries, communes, utilities and the statistics agency refer to a compound by the same address, their records can be joined without matching names and descriptions.

**One reference for all services.** Senegal's own experience shows the value. The World Bank's review notes that an address directory usually yields a list of economic activities more complete than the tax department's and reveals who is missing from the rolls; Senegal's programme tested this reconciliation in Thiès and Kaolack [@farvacque2005]. A compound record carries the postcode, the official street address where there is one and, once it exists, the ANN identifier, so each service keeps its own records and still agrees on the compound.

**What door numbering would have cost.** At the World Bank's average cost of conventional addressing in African cities [@farvacque2005],

$$
C = N \times c_{\text{door}} = 3\,597\,128 \times \text{US\$}\,5.7 \approx \text{US\$}\,20.5 \text{ million (2005 prices)},
\tag{22}
$$

where $N$ is the number of compounds and $c_{\text{door}}$ the cost per addressed doorway. At the highest per-doorway cost reported in the same review, US$7.6, the figure would be US$27.3 million. The comparison gives the scale of conventional addressing, not a saving: plates and street names keep their value, and where a commune numbers its streets, its numbers are shown first and the N-Ways addresses become aliases (Section 4.14).

**Planning with real counts.** The registry counts compounds by zone, place and building class, and every count can be recomputed from the open files. Dakar département holds 107,430 addresses and Touba-Mbacké (Ndame) 289,328, more than most régions.

**Access to services.** Straight-line distances from a sample of 20,000 compounds to the nearest facility mapped in the N-Ways base map are given below. The facility layer is not part of the published repository, and these numbers describe the map, not the ground: unmapped schools, daaras and posts make distances look longer. A ministry can replace the facility list with its own and recompute the table in minutes from the registry.

| Facility | Within 2 km | Within 5 km | Median distance |
|:--|--:|--:|--:|
| Health facility (hospital, health centre, health post) | 53.1 % | 74.5 % | 1.74 km |
| School | 43.3 % | 59.4 % | 3.10 km |
| Police or gendarmerie | 22.4 % | 35.0 % | 12.57 km |
| Pharmacy | 32.7 % | 44.0 % | 7.30 km |

: Distance from compounds to the nearest mapped facility (sample of 20,000 compounds).

**Census and surveys.** The 2023 census counted 18.1 million residents [@ansd2024]. The registry's 3.6 million compounds, each with a stable code, give survey teams a frame they can sample from and return to; a survey that records the address of each interview can be mapped and joined to services without storing a name.

**Land.** An address is not a title. The registry can nevertheless carry the NICAD of a parcel, so that the cadastre, PROCASEF and the communes can find a registered parcel's compound and its gate.

**Growth.** New compounds receive addresses as they appear (Eq. (13)). The registry thus shows where Senegal grows, month by month: the extensions of Touba, Keur Massar and Diamniadio are where roads, water, schools and health posts will be needed next.

# Privacy, safety and governance

**Places, never people.** Addresses describe places. Residential compounds carry no occupant data: no names, no telephone numbers and no household composition. The household count is kept only as "one, several or not stated" and is never shown. Positions, outlines, classes, sizes, statuses, gate positions, the names of businesses and public buildings, and street plates are public. Photographs taken in "Add my home" are kept for verification only and are not published, and a household may ask for a door to be hidden. Partners see a customer's address only with the customer's consent.

**Law.** Senegal's Law 2008-12 and its implementing Decree 2008-721 apply; the Commission de protection des données personnelles (CDP) must receive a declaration before processing begins, geolocation falls under the normal declaration, and transfers of data outside Senegal require its authorisation [@loi2008]. The ECOWAS Supplementary Act on personal data protection sets the regional frame [@ecowas2010]. A bill replacing the 2008 law and creating a new authority has been in preparation since 2019; we found no record of its adoption by October 2026. The CDP took part in the ANN relaunch workshop.

**Openness and safety.** The registry is published in full, with nothing withheld, and it contains no information about the people in a home.

**Governance.** N-WAYS LIMITED maintains the model and is, for now, the single issuer, so that no number is given twice. Zones, issued addresses, the blocks of each name's range, the spot grid and the check method never change; building profiles change with evidence; plate names awaiting a commune's choice may change once. The repository is designed to be handed over whole, with its registry, engine and rules, to the ANN or a body it designates. If the ANN goes live, its address is shown first and the N-Ways address becomes a cross-reference. Disputes about groupings are settled by residents' agreement; land disputes are never settled by an address. The rules for change and hand-over are set out in `GOVERNANCE.md`.

# Limitations and future work

**The place inventory comes from open maps.** OpenStreetMap and GeoNames place points are uneven: dense in parts of Dakar and Ziguinchor, sparse in Touba's quartiers and in many villages. Some places are therefore too large, which lengthens their numbers, and some names are misspelled. Curation with the communes adds aliases and corrects plate names, but never changes an issued number.

**Many plate names are provisional.** 3,116 places, about a fifth, await their commune's choice, mostly villages named after a person and names with an ethnic or compass qualifier; 739,058 addresses carry such a name. Only three short forms have a written source; "Parcelles" for Parcelles Assainies, common in speech, awaits the commune.

**Name folding is a judgement.** The normalisation of Eq. (5) is generous on purpose, but a spelling it does not fold, such as a rare transliteration or a name in Pulaar or Jola orthography, starts a range of its own. Such spellings are added as aliases; blocks are never merged.

**Compounds are inferred.** Few walls are mapped, so most grouping relies on the shape rules of Eq. (18) and will be wrong for some plots until residents correct it. The published registry contains entrances and centroids but not footprints; an independent deployment therefore applies the duplicate checks with entrance distances only.

**Attributes are thin.** Heights are unknown almost everywhere, and classes outside towns are low-confidence guesses until people or partners confirm them.

**Boundaries.** The zones use the 2019 département outlines and do not show Keur Massar separately; they are frozen by design.

**External systems.** La Poste's locality list will be used only with La Poste's agreement, since it carries no licence. The cross-references may need to adapt once the ANN publishes its format. We could not verify which datum titles must use today, the law that licenses surveyors, or the status of the 2019 data-protection bill.

**What we will measure.** The estimates of Sections 9–10 rest on few local data. We propose the following measurements, to be agreed with partners:

| Measure | Method | Target |
|:--|:--|:--|
| Recall of one's own address after one month | residents asked without the application | at least 80 % exact |
| First-attempt delivery success | partner couriers, with and without an address | at least 20 points higher with one |
| Time from arrival in the quartier to the gate | courier application timestamps | halved |
| Gates and doors confirmed | residents and couriers | 10,000 |
| Time to locate emergency callers | with a willing ambulance or fire service | measured, then halved |

: Measurements proposed for the first year.

# Conclusion

A national address does not need streets to be named or doors to be surveyed before it can exist. By combining a place word that people already use with a short number from one national range per name, Senegal's compounds can each carry an address that is short enough to say, unique without context, ordered on the ground, stable and open. The registry issued on this model holds 3,597,128 addresses; every one decodes to exactly one compound from its spoken form alone, its numbers follow the ground, and a check letter that people never see guards the machine form. The model shows the government's address first wherever one exists and is built to be absorbed by the Adressage Numérique National. Its main limits, the uneven place inventory, the provisional plate names and the inferred compounds, are each correctable without renumbering, through the communes, through residents and through the ANN.

# Data and code availability {-}

The specification, the reference engine, the registry, the model files, the server and this paper are published at <https://github.com/n-ways/open-addresses-senegal> [@nways2026]. The code is licensed under the Apache License 2.0, the data under the Open Database License 1.0 and the documents under CC BY 4.0. Credit line: "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)". Every figure and every measurement of Section 6 can be reproduced with `tools/paper-figures.py` and `tools/paper-evaluation.py`; the PDFs are built with `sh docs/paper/build.sh`.

# Acknowledgements {-}

The registry rests on the work of the OpenStreetMap contributors who mapped Senegal's buildings and places, notably in Sédhiou, Kolda and Matam, where they drew most of the footprints; on the building footprints released by Google and Microsoft and distributed by the Overture Maps Foundation; on the boundaries of geoBoundaries and the Government of Senegal; and on GeoNames. We thank La Poste Sénégal, the ANSD and the municipal addressing units whose published work made this study possible.

# References {-}

::: {#refs}
:::

# Appendix A. The 46 code zones {-}

| # | Key | Zone | Region | Frame (km) | Cell (m) | Spot | Places | Addresses | 3 (%) | 4 (%) | 5 (%) |
|--:|:--|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| 0 | BIG | Bignona | Ziguinchor | 98 | 10 | 4+4 | 595 | 65,019 | 41.9 | 42.4 | 15.8 |
| 1 | BKL | Bakel | Tambacounda | 199 | 10 | 5+5 | 219 | 41,737 | 23.8 | 59.4 | 16.8 |
| 2 | BMB | Bambey | Diourbel | 49 | 5 | 4+4 | 489 | 83,034 | 28.3 | 58.9 | 12.8 |
| 3 | BNK | Bounkiling | Sédhiou | 84 | 10 | 4+4 | 253 | 36,264 | 39.6 | 42.7 | 17.7 |
| 4 | BRK | Birkelane | Kaffrine | 59 | 10 | 4+4 | 202 | 33,656 | 33.6 | 62.6 | 3.8 |
| 5 | DAG | Dagana | Saint-Louis | 123 | 10 | 5+5 | 235 | 89,049 | 12.4 | 60.7 | 26.9 |
| 6 | DBL | Diourbel | Diourbel | 55 | 10 | 4+4 | 425 | 68,418 | 32.4 | 24.4 | 43.3 |
| 7 | DKR | Dakar | Dakar | 16 | 2 | 4+4 | 112 | 107,430 | 1.2 | 62.7 | 36.1 |
| 8 | FDG | Foundiougne | Fatick | 73 | 10 | 4+4 | 416 | 79,408 | 25.8 | 59.3 | 14.9 |
| 9 | FTK | Fatick | Fatick | 86 | 10 | 4+4 | 461 | 101,628 | 27.5 | 55.8 | 16.7 |
| 10 | GDW | Guédiawaye | Dakar | 8 | 1 | 4+4 | 11 | 23,425 | 0.8 | 25.2 | 73.6 |
| 11 | GMP | Goudomp | Sédhiou | 93 | 10 | 4+4 | 225 | 27,865 | 40.8 | 57.0 | 2.2 |
| 12 | GNG | Guinguinéo | Kaolack | 49 | 5 | 4+4 | 221 | 39,809 | 28.2 | 44.9 | 26.9 |
| 13 | GOS | Gossas | Fatick | 83 | 10 | 4+4 | 291 | 30,827 | 43.7 | 42.8 | 13.5 |
| 14 | GRY | Goudiry | Tambacounda | 164 | 10 | 5+5 | 424 | 35,962 | 43.3 | 55.4 | 1.6 |
| 15 | KAF | Kaffrine | Kaffrine | 94 | 10 | 4+4 | 294 | 75,331 | 15.5 | 52.0 | 32.4 |
| 16 | KAO | Kaolack | Kaolack | 77 | 10 | 4+4 | 468 | 129,054 | 19.2 | 42.6 | 38.3 |
| 17 | KBM | Kébémer | Louga | 109 | 10 | 5+5 | 639 | 94,438 | 35.7 | 45.8 | 18.5 |
| 18 | KDG | Kédougou | Kédougou | 167 | 10 | 5+5 | 176 | 47,506 | 17.9 | 16.5 | 65.8 |
| 19 | KGH | Koungheul | Kaffrine | 104 | 10 | 5+5 | 309 | 48,680 | 29.0 | 51.3 | 19.7 |
| 20 | KLD | Kolda | Kolda | 116 | 10 | 5+5 | 515 | 72,605 | 34.5 | 25.3 | 40.3 |
| 21 | KNL | Kanel | Matam | 134 | 10 | 5+5 | 189 | 66,004 | 16.9 | 73.4 | 9.7 |
| 22 | KPT | Koumpentoum | Tambacounda | 128 | 10 | 5+5 | 269 | 40,224 | 29.0 | 58.2 | 12.9 |
| 23 | KTF | Kaël-Taïf | Diourbel | 72 | 10 | 4+4 | 237 | 22,957 | 41.5 | 53.5 | 5.2 |
| 24 | LGA | Louga | Louga | 109 | 10 | 5+5 | 716 | 131,320 | 27.0 | 46.5 | 26.6 |
| 25 | LNG | Linguère | Louga | 155 | 10 | 5+5 | 560 | 96,934 | 34.5 | 49.7 | 15.9 |
| 26 | MAT | Matam | Matam | 118 | 10 | 5+5 | 208 | 77,460 | 13.4 | 70.1 | 16.6 |
| 27 | MBR | Mbour | Thiès | 72 | 10 | 4+4 | 438 | 205,416 | 11.6 | 35.0 | 53.4 |
| 28 | MHD | Malem Hodar | Kaffrine | 81 | 10 | 4+4 | 157 | 25,139 | 28.5 | 67.0 | 4.5 |
| 29 | MYF | Médina Yoro Foulah | Kolda | 115 | 10 | 5+5 | 463 | 54,533 | 35.0 | 57.7 | 7.3 |
| 30 | NRP | Nioro du Rip | Kaolack | 92 | 10 | 4+4 | 524 | 103,624 | 25.8 | 60.1 | 14.1 |
| 31 | OUS | Oussouye | Ziguinchor | 39 | 5 | 4+4 | 70 | 16,172 | 21.0 | 70.0 | 9.0 |
| 32 | PKN | Pikine–Keur Massar | Dakar | 16 | 2 | 4+4 | 39 | 123,594 | 0.0 | 13.0 | 87.0 |
| 33 | POD | Podor | Saint-Louis | 186 | 10 | 5+5 | 364 | 91,267 | 21.3 | 74.6 | 4.2 |
| 34 | RAN | Ranérou-Ferlo | Matam | 155 | 10 | 5+5 | 131 | 32,597 | 22.4 | 73.4 | 4.3 |
| 35 | RUF | Rufisque | Dakar | 34 | 5 | 4+4 | 119 | 158,721 | 1.6 | 43.0 | 55.5 |
| 36 | SED | Sédhiou | Sédhiou | 100 | 10 | 4+4 | 211 | 32,322 | 35.7 | 42.7 | 21.6 |
| 37 | SLM | Salémata | Kédougou | 81 | 10 | 4+4 | 97 | 5,839 | 72.3 | 27.8 | 0.0 |
| 38 | SRY | Saraya | Kédougou | 126 | 10 | 5+5 | 152 | 45,759 | 13.8 | 48.0 | 38.2 |
| 39 | STL | Saint-Louis | Saint-Louis | 47 | 5 | 4+4 | 194 | 73,706 | 11.0 | 66.8 | 22.3 |
| 40 | TBA | Touba-Mbacké (Ndame) | Diourbel | 49 | 5 | 4+4 | 241 | 289,328 | 3.0 | 13.1 | 83.9 |
| 41 | TBC | Tambacounda | Tambacounda | 215 | 10 | 5+5 | 674 | 100,102 | 26.4 | 30.4 | 43.2 |
| 42 | THS | Thiès | Thiès | 63 | 10 | 4+4 | 485 | 175,645 | 13.3 | 62.9 | 23.9 |
| 43 | TIV | Tivaouane | Thiès | 101 | 10 | 5+5 | 822 | 144,845 | 25.8 | 57.2 | 17.0 |
| 44 | VEL | Vélingara | Kolda | 99 | 10 | 4+4 | 460 | 104,269 | 24.9 | 35.4 | 39.7 |
| 45 | ZIG | Ziguinchor | Ziguinchor | 72 | 10 | 4+4 | 197 | 48,206 | 12.5 | 69.4 | 18.1 |

: The 46 code zones: index, key, frame side, spot cell and spot digits per axis (Eq. (2)), places, issued addresses, and the share of compounds whose number has 3, 4 or 5 digits. Sources: `model/zones.json`, `model/lieux-stats.json`, `registry/MANIFEST.json`.
