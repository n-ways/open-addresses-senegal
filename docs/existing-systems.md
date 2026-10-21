# Senegal: existing postal and address systems

Checked 2026-10-18. Every source is listed with its URL in [SOURCES.md](../SOURCES.md).

## Summary

**Postal codes exist but are coarse (delivery-office level) and not door-level.** La Poste Sénégal's 5-digit codes name a delivery post office and its area: 163 well-formed codes cover 18.1 million people, and the whole of Touba (Mbacké département has 1.36 million residents, census 2023) shares the single code 22300.

**A partial physical address system exists in some cities.** Blue street plates with neighbourhood street codes (SC-15, PE-44, OKM-1) and metric door numbers cover parts of Dakar, Guédiawaye, Pikine, Saint-Louis, Thiès, Kaolack, Diourbel, Tambacounda and Ziguinchor. It is incomplete, many plates are missing or out of date, and there is no public register of these addresses.

**The state's door-level digital system, the Adressage Numérique National (ANN), is not yet live.** It was relaunched on 5-6 August 2026 with a target of finishing its pilot within a year. As of 2026-10-18 nothing door-level has been published: no format, no platform, no API, no data and no licence.

What this means for N-Ways, whose rule is that where the government already gives addresses, its data is used and its address is shown as written:

- **Street plates.** Where the municipal street addressing is in use or its data is obtainable, N-Ways shows that address as written ("120 Rue PE-44, Point E"), first, and puts up no plate of its own; the N-Ways address stays beside it, so that one kind of address works for every home.
- **ANN.** Once the ANN publishes, it takes over each area it covers, and every N-Ways address there becomes an alias that resolves to it.
- **La Poste.** Postcodes are delivery-office zones, not door addresses. The N-Ways door-level model therefore applies everywhere else, and every compound maps to its La Poste code.

This split is the coverage mask: [model.md](model.md) section 0.1, SPEC section 3.6. Until it takes over an area, the N-Ways model is a **companion to the ANN and a candidate input for it**, never a rival. Every compound has an `annId` slot, the registry is published in a form the ANN can take over, and the hand-over is written into [GOVERNANCE.md](../GOVERNANCE.md).

## 1. La Poste Sénégal postcodes

| | |
|---|---|
| Operator | Société Nationale La Poste (state postal operator, UPU member) |
| Format | 5 digits to the left of the delivery office name: `12500 DAKAR`, `27000 Ziguinchor`, `46024 SAINT-LOUIS` (UPU addressing sheet, 02/2015) |
| Structure | UPU: routeing area, then delivery post office, then delivery area. In La Poste's own data the first two digits follow the geography: 10-17 Dakar region, 20-27 the centre and south (20 Rufisque/Thiès, 22 Touba and Diourbel, 23-24 Kaolack/Fatick/Mbour, 25-26 Tambacounda/Kédougou, 27 Casamance), 30-36 the north (30-31 Louga, 32-35 Saint-Louis, 36 Matam). |
| Granularity | La Poste's finder data maps 4,143 locality and neighbourhood names to 166 values: 163 well-formed 5-digit codes and 3 malformed entries ("0", "159", "36"). The code 17000 alone covers 250 named places in the Pikine/Keur Massar suburbs. All of Touba is `22300`. |
| How it is used | On mail and forms, with a P.O. box (`BP 1534`) or a neighbourhood "postchance" box. Home delivery to a street address is the exception. UPU examples put the street address above the postcode line, e.g. `12 AVENUE CHEIKH ANTA DIOP / 12500 DAKAR`. |
| Lookup | <https://www.laposte.sn/code-postal-senegal/>: a finder that gives the code for a locality and the nearest post office, backed by a public JavaScript file (`postal-data.js`, which its header says is built from the base of the administrative divisions of Senegal). There is no API, the page states no licence (only "© 2026 La Poste Sénégal"), and there are no code boundaries: entries are names, not polygons. |
| In OpenStreetMap | 173 building features carry `addr:postcode` in the N-Ways Senegal extract. |

**Use in the model:** each compound record carries `laPosteCode`, resolved in this order:

1. the OSM `addr:postcode` on the building;
2. the code of the La Poste finder entry whose locality matches the compound's commune and quartier name, but **only once La Poste agrees** to that use, since its data has no licence;
3. otherwise left empty, and the app links to La Poste's finder.

The N-Ways code never contains the postcode digits. La Poste can renumber its zones, and its zones have no published boundaries. Embedding the code would make N-Ways codes change whenever La Poste's zones do.

## 2. Physical street addressing ("adressage")

- **Street plates and codes.** Senegal's municipal addressing puts a blue plate at each intersection showing the quartier, the street's name or number ("Rue 12"), and a street reference made of the quartier's initials and a number: `PE-44` (Point E), `SC-15` (Sacré-Cœur), `OKM-1` (Ouakam), `GD-28` (Grand Dakar), `DF-59` (Dalifort). Thiès uses the same pattern (`DX-1`, `CR-02`). The OpenStreetMap Senegal convention puts this reference in `ref=*` on the street (OSM wiki "FR:WikiProject Sénégal/Conventions de marquage des rues").
- **Metric house numbers.** A door's number is its distance in metres from the start of the street, so doors often show two stencilled numbers, an old one and a new one (Au Sénégal, "Noms des rues de Dakar : comment ça marche ?").
- **Coverage.** The OSM wiki says the project has run since 2008 and reached Dakar, Guédiawaye, Pikine, Saint-Louis, Thiès, Kaolack, Diourbel, Tambacounda and Ziguinchor. In March 2019 the telecom and postal regulator ARTP said a geolocated addressing system had numbered 224,000 buildings across 255 quartiers of Dakar, with the other 13 regions to follow (APS via OSIRIS, 19 Mar 2019). The World Bank's *Street Addressing and the Management of Cities* (Farvacque-Vitkovic et al., 2005) describes the programme's origin: a 1993 pilot in Mbour, then the Urban Development and Decentralisation Programme (PAC, 1998-2004) run by the Agence de Développement Municipal. Streets are coded by a two-letter neighbourhood radical and a number ("ES.12", the twelfth street of Escale), and doors are numbered metrically, even and odd on opposite sides. Of the fifteen cities first eligible, eight completed every task (Thiès, Louga, Diourbel, Kaolack, Ziguinchor, Saint-Louis, Guédiawaye, Tambacounda), three completed signage only (Dakar, Rufisque, Pikine) and four did not meet the deadlines; Thiès and Kaolack also reconciled the address directory with the tax rolls.
- **State in 2026.** The Ministry of Local Government itself calls the physical addressing "incomplete, not exhaustive and not digital" (2021-2023 statements, via OSIRIS and Acteurs publics). Landmark directions ("face BCEAO siège") remain the everyday norm.
- **Use in the model.** This is a government address system, so its areas are in the coverage mask (`official-municipal`). There the address shown is the street address as written, for example "120 Rue PE-44", taken from the programme's data where N-Ways can obtain it, or from plates confirmed by people. N-Ways puts up no plates of its own there. Every door record carries `streetRef` and `metricNumber`.

## 3. Adressage Numérique National (ANN)

| Date | Event | Source |
|---|---|---|
| 25 Feb 2021 | The Ministry of the Digital Economy and Telecommunications (Minister Yankhoba Diattara), with the Ministry of Local Government and Land Planning, launches a national digital addressing project: map the country and give every location a digital address, over 3 years, with a platform, a database and geolocation, to supplement the "largely incomplete and outdated" physical addressing. | OSIRIS, 26 Feb 2021 |
| 2021 | A Dakar pilot is announced. | OSIRIS archive |
| 2023 | The project is presented under the slogan « Un Sénégalais, une adresse », with a legal framework announced. | WeAreTech Africa; OSIRIS 10 Aug 2026 |
| 5-6 Aug 2026 | The Ministry in charge of telecommunications and digital affairs (named "Ministère des Télécommunications et du Numérique" in the press; the government's 2024 title is Ministère de la Communication, des Télécommunications et du Numérique) holds a two-day relaunch workshop with the Presidency, the Primature, local authorities, the private sector, universities and the CDP. The aim is a "référentiel national d'adresses unique, géoréférencé et partagé", for public services, e-commerce, taxation, land management, post and logistics, and emergencies. The pilot is to finish within one year, before a phased national roll-out. It sits under the New Deal technologique, the digital strand of the Vision Sénégal 2050. | Senego 5 Aug 2026; OSIRIS 10 Aug 2026; Afrique IT News 11 Aug 2026 |

What has **not** been published as of 2026-10-18: the address format, the pilot areas, the platform, an API, open data or licence terms, and the governing body. OSIRIS warns that without one clearly designated authority, Senegal risks "multiplying incompatible databases". That warning is the main design constraint for N-Ways: our registry must be easy to merge into whatever the ANN adopts.

**Use in the model:**

- every compound has an `annId` field (empty until the ANN issues identifiers);
- the registry is published as open, documented data;
- the zones are frozen and published;
- the codes are computed by a published algorithm.

This lets the ANN adopt the registry, map onto it, or ignore it without loss. If the ANN publishes a door-level format, N-Ways shows the ANN address first ([GOVERNANCE.md](../GOVERNANCE.md) section "If the state's system goes live").

## 4. Cadastre, land and surveying (relevant to "Add my home")

- **Land tenure.** Law 64-46 (1964) on the domaine national covers all land that is neither state domain nor registered, about 80-85% of the country by commentators' estimates. Communes allocate it for use ("affectation"), and it cannot be sold as private property. Law 2011-07 (30 Mar 2011) governs registered land: only the State may request registration, and a real right exists only once it is in the land book (titre foncier).
- **Cadastre.** The cadastre is held by the Direction du Cadastre under the Direction générale des Impôts et des Domaines (DGID, Ministry of Finance). Parcels get a NICAD (numéro d'identification cadastral). PROCASEF, the World Bank-financed cadastre and land-tenure project (US$80 million, from Aug 2021), had surveyed and mapped more than 830,000 parcels in 138 communes by June 2026 and issued titres d'affectation, e.g. about 13,000 in Mlomp, Oussouye. A 2026-2028 phase hands the data to the communes, ahead of a planned Programme national de sécurisation foncière. We found no public open parcel layer.
- **Lotissements.** Urban plots are laid out in official subdivision plans (plans de lotissement) with plot numbers. A plot number plus the lotissement name is the most precise address many owners have.
- **Surveyors.** The Ordre National des Géomètres-Experts du Sénégal organises the profession, and the Director of the Cadastre sits with it as government commissioner (Dakaractu, 2025). The law that licenses géomètres-experts was not found online (unverified).
- **Datum and projection.** Senegal's legacy systems are the Adindan, Yoff (Yoff / UTM zone 28N, EPSG:31028) and 1974 datums, all on UTM with the Clarke 1880 ellipsoid, and the stereographic Hatt system of the old cadastral sheets. The Direction des Travaux Géographiques et Cartographiques described a new datum, NSGD2004 (ITRF2000, GRS80), in 2005. Rural plot plans must give vertex coordinates (X, Y) in "the national geographic system" (2000 arrêté on the rural domain). Which datum titres fonciers must use today is unverified. The Yoff to WGS 84 shift is several tens of metres (EPSG:8633: dX -37, dY +157, dZ +89.5 m), so an imported survey plan **must** state its datum.
- **Use in the model.** Option (c) of "Add my home" imports survey-plan beacons in Yoff/UTM 28N, NSGD2004/UTM 28N or WGS 84/UTM 28N, and records the NICAD or lotissement plot number when the owner has one. An N-Ways code is an address, never a land title.

## 5. Data protection

- **Law.** Loi n° 2008-12 du 25 janvier 2008 sur la protection des données à caractère personnel, with its implementing Décret n° 2008-721 du 30 juin 2008.
- **Authority.** The Commission de protection des données personnelles (CDP), <https://www.cdp.sn/>. Processing must be declared before it starts, and geolocation falls under the "déclaration normale". Transfers outside Senegal need prior authorisation.
- **Reform.** A bill replacing the 2008 law, and creating an Autorité de protection des données à caractère personnel, has been in preparation since 2019. It received a favourable Supreme Court opinion in 2022, and the CDP held an update workshop in October 2024. We found **no adoption** in 2025-2026. This absence was not confirmed on the National Assembly site, so it is unverified. The CDP was invited to the ANN relaunch workshop (Aug 2026).

## 6. Other systems checked

- **Open Location Code (Plus Codes).** Open (Apache-2.0) and works offline. N-Ways already shares Plus Codes. The Senegal spot code converts to and from latitude and longitude, so it converts to and from Plus Codes too.
- **Census geography.** ANSD (RGPH-5, 2023) gives 18,126,390 residents, 54.7% urban. Guédiawaye is the densest département (58,688 per km²) and Mbacké the most populous (1,359,758). Census enumeration areas are not published as an address system.
- **Short place names in use.** People shorten some long names in speech: "Saly" for Saly Portudal (written in fr.wikipedia, SOURCES N1), "le Plateau" for Dakar-Plateau (N2), "Liberté 6" for Sicap Liberté 6, "Parcelles" for Parcelles Assainies. Only the first two have a written source we could find; the model uses them as plate names, and sends the others to the commune (SPEC 3.2.1). "Liberté 6" is not a short form claimed from usage: it is S.I.C.A.P. Liberté Six with the developer label dropped and the numeral in digits.
- **Proprietary grid codes.** None is endorsed by the Senegalese state as far as we found.
