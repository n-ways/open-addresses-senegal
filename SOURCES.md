# Sources

All sources were accessed on **2026-10-18** unless a row says otherwise. Earlier desk research (G7) was checked on 2026-10-17. "Unverified" marks claims we could not confirm with a primary source.

## Postal codes and postal addressing

| # | Source | URL | What it supports |
|---|---|---|---|
| P1 | UPU, Senegal postal addressing sheet (02/2015; PDF metadata 2020) | https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/senEn.pdf | 5-digit postcode to the left of the delivery office; routeing area / delivery office / delivery area; examples `12500 DAKAR`, `27000 Ziguinchor`, `46024 SAINT-LOUIS`; BP and "postchances" |
| P2 | La Poste Sénégal, postcode finder | https://www.laposte.sn/code-postal-senegal/ | Public finder (locality, code, nearest office); no terms or licence beyond "© 2026 La Poste Sénégal" |
| P3 | La Poste Sénégal, finder data file | https://www.laposte.sn/wp-content/plugins/posteasy/assets/js/postal-data.js | 4,143 locality entries, 166 values (163 well-formed 5-digit codes); Touba = 22300; 17000 covers 250 named places. Read only for counting; **not copied into this repo** |

## Street addressing and the national digital addressing programme

| # | Source | URL | What it supports |
|---|---|---|---|
| A1 | OpenStreetMap wiki, FR:WikiProject Sénégal/Conventions de marquage des rues | https://wiki.openstreetmap.org/wiki/Senegal_Highway_tag | Street-addressing project since 2008 in Dakar, Guédiawaye, Pikine, Saint-Louis, Thiès, Kaolack, Diourbel, Tambacounda, Ziguinchor; blue plates; `ref=PE-44` convention |
| A2 | Au Sénégal, "Noms des rues de Dakar : comment ça marche ?" | https://au-senegal.com/noms-des-rues-de-dakar-comment-ca-marche,14231.html | Street codes (SC-15, OKM-1, GD-28, DF-59; Thiès DX-1); metric house numbers; landmark directions still common |
| A3 | APS via OSIRIS, "Système d'adressage : 224 000 bâtiments numérotés à Dakar" (19 Mar 2019) | https://osiris.sn/systeme-d-adressage-224000-batiments-numerotes-a-dakar.html | ARTP / FDSUT: 224,000 buildings numbered in 255 quartiers of Dakar, other regions to follow |
| A4 | OSIRIS, "Le ministère des Télécoms lance le projet d'adressage numérique du pays" (26 Feb 2021) | https://www.osiris.sn/senegal-le-ministere-des-telecoms-lance-le-projet-d-adressage-numerique-du-pays.html | 25 Feb 2021 launch, Minister Yankhoba Diattara, 3-year plan, platform + database; physical addressing "largely incomplete and outdated" |
| A5 | WeAreTech Africa via OSIRIS, "Le projet d'adressage numérique national entre dans une nouvelle phase" (10 Aug 2026) | https://www.osiris.sn/senegal-le-projet-d-adressage-numerique-national-entre-dans-une-nouvelle-phase.html | ANN relaunch; "référentiel national d'adresses unique, géoréférencé et partagé"; 2023 « Un Sénégalais, une adresse »; pilot in 1 year |
| A6 | Social Net Link via OSIRIS, "Adressage numérique : le Sénégal relance un chantier stratégique resté inachevé" (10 Aug 2026) | https://www.osiris.sn/adressage-numerique-le-senegal-relance-un-chantier-strategique-reste-inacheve.html | 2023 presentation of the project; 5-6 Aug 2026 workshop participants; risk of "incompatible databases"; CDP to be involved; no format published |
| A7 | Senego, "Adressage numérique : le Sénégal se donne pour objectif de boucler la phase pilote en un an" (Aug 2026) | https://senego.com/adressage-numerique-le-senegal-se-donne-pour-objectif-de-boucler-la-phase-pilote-en-un-an_1990855.html | One-year pilot target before national roll-out |
| A8 | Afrique IT News, "Le Sénégal relance l'adressage numérique…" (11 Aug 2026) | https://afriqueitnews.com/tech-media/senegal-relance-adressage-numerique-pour-geolocaliser-plus-precisement-habitations-et-activites/ | Relaunch coverage; dates the project to 2021 |
| A9 | Acteurs publics, "Le Sénégal va numériser les adresses des localités du pays" | https://acteurspublics.fr/articles/le-senegal-va-numeriser-les-adresses-des-localites-du-pays/ | Physical addressing exists in Dakar and some towns but is not exhaustive; map first, then an address per location |
| A10 | WeAreTech Africa, "Le Sénégal élabore un projet d'adressage numérique national" | https://www.wearetech.africa/fr/fils/actualites/gestion-publique/le-senegal-elabore-un-projet-dadressage-numerique-national | « Un Sénégalais, une adresse » |
| A11 | Farvacque-Vitkovic, C., Godin, L., Leroux, H., Verdet, F., Chavez, R., *Street Addressing and the Management of Cities*, World Bank, 2005 (accessed 2026-10-21) | https://documents1.worldbank.org/curated/en/573071468142795481/pdf/329230Street0Addressing01not0external1.pdf | Table 3.1: 21 cities, 8% of streets named before addressing, US$5.7 per doorway; Senegal section: 1993 Mbour pilot, PAC 1998-2004 run by the ADM, street radical + number, metric numbering, 8 of 15 cities completed, Thiès and Kaolack tax registers (box 2.4) |

## Land, cadastre, surveying, geodesy

| # | Source | URL | What it supports |
|---|---|---|---|
| L1 | Loi n° 2011-07 du 30 mars 2011 portant régime de la propriété foncière (vie-publique.sn) | https://www.vie-publique.sn/documents/6145/loi-n-2011-07-du-30-mars-2011-portant-regime-de-la-propriete-fonciere-6145 | Registration by the State only; titre foncier; real rights exist only once recorded |
| L2 | Loi n° 64-46 du 17 juin 1964 relative au domaine national (UNEP LEAP) | https://leap.unep.org/en/countries/sn/national-legislation/loi-no-64-46-relative-au-domaine-national | Domaine national |
| L3 | ILC / Land Coalition, brochure on land governance in Senegal | https://learn.landcoalition.org/documents/803/brochure_gouv_fonciere_senegal.pdf | Share of land under the domaine national (commentators' estimate 80-85%) |
| L4 | AllAfrica (APS), "Le PROCASEF plaide pour une réforme d'envergure nationale" (9 Jun 2026) | https://fr.allafrica.com/stories/202606090568.html | More than 830,000 parcels surveyed and mapped in 138 communes; proposed national programme |
| L5 | AllAfrica (APS), "Le PROCASEF envisage de sécuriser les terres de 1 393 000 ménages" (1 Apr 2025) | https://fr.allafrica.com/stories/202504010585.html | US$80 M World Bank; launched Aug 2021; NICAD; titres d'affectation |
| L6 | AllAfrica (APS), "Gestion foncière à Mlomp : 13 000 titres d'affectation délivrés" (Jun 2025) | https://fr.allafrica.com/stories/202506020723.html | Rural allocation titles in Oussouye |
| L7 | Dakaractu, "Géomètre expert : un métier agressé par des non professionnels…" (2025) | https://www.dakaractu.com/Geometre-Expert-Un-metier-agresse-par-des-non-professionnels-selon-Lamine-Fall-president-de-l-Ordre-des-Geometres-du_a260326.html | Ordre National des Géomètres-Experts du Sénégal; the Director of the Cadastre is government commissioner to it. The licensing law itself was **not found: unverified** |
| L8 | EPSG:31028, Yoff / UTM zone 28N | https://epsg.io/31028 | Legacy national grid: TM, CM -15°, k0 0.9996, FE 500 000, Clarke 1880 (IGN) |
| L9 | EPSG:8633 / EPSG:6903, Yoff to WGS 84 transformations | https://epsg.io/4310-8633 | Datum shift of several tens of metres (dX -37, dY +157, dZ +89.5 m) |
| L10 | Ndiaye, M., FIG Working Week Cairo 2005, TS01.6 (Direction des Travaux Géographiques et Cartographiques) | https://fig.net/resources/proceedings/fig_proceedings/cairo/papers/ts_01/ts01_06_ndiaye.pdf | Five legacy reference systems (Adindan, Yoff, 1974, Hatt…); NSGD2004 on ITRF2000 / GRS80. Its 2026 status is **unverified** |
| L11 | EPSG:32628, WGS 84 / UTM zone 28N | https://epsg.io/32628 | Projection used by the spot grid |

## Data protection

| # | Source | URL | What it supports |
|---|---|---|---|
| D1 | Commission de protection des données personnelles (CDP) | https://www.cdp.sn/ | Loi 2008-12, Décret 2008-721; declarations; geolocation under "déclaration normale" (N-Ways research 2026-10-17) |
| D2 | OSIRIS, "Mise à niveau du projet de loi sur la protection des données personnelles" (2024) | https://www.osiris.sn/mise-a-niveau-du-projet-de-loi-sur-la-protection-des-donnees-personnelles-une.html | 2019 replacement bill; favourable Supreme Court opinion 2022; adoption pending; CDP workshop Oct 2024 |
| D3 | OSIRIS, "Le Sénégal va réviser la loi sur la protection des données personnelles" | https://osiris.sn/le-senegal-va-reviser-la-loi-sur-la-protection-des-donnees-personnelles.html | Planned APDP replacing the CDP; geolocation, biometrics and artificial intelligence in scope |
| D4 | DLA Piper, Data Protection Laws of the World: Senegal (updated 19 Mar 2026) | https://www.dlapiperdataprotection.com/?t=law&c=SN | No replacement law in force as of March 2026 |

## Administration, population, language

| # | Source | URL | What it supports |
|---|---|---|---|
| G1 | geoBoundaries gbOpen SEN ADM2 and ADM3 (2019; Government of Senegal / OCHA ROWCA; CC BY 3.0 IGO) | https://www.geoboundaries.org/api/current/gbOpen/SEN/ADM2/ | 45 départements and 121 arrondissements: the outlines of the frozen zones |
| G2 | Senego, "Officiel : Keur Massar érigé en département" (2021) | https://senego.com/officiel-keur-massar-erige-en-departement_1277754.html | Keur Massar becomes the 46th département (decree 2021-687, 28 May 2021) |
| G3 | Décret 2021-689 (ressort territorial et chefs-lieux), vie-publique.sn | https://www.vie-publique.sn/documents/8063/decret-2021-689-ressort-territorial-chef-lieu-regions-departements-arrondissements | Administrative map after Keur Massar |
| G4 | ANSD, main results of RGPH-5 (2023) | https://www.ansd.sn/actualite/les-principaux-resultats-du-5e-recensement-general-de-la-population-et-de-lhabitat-du | 18,126,390 residents; 54.7% urban |
| G5 | Dakaractu, "Départements les plus peuplés du Sénégal : Mbacké en tête avec 1 359 757 habitants…" | https://www.dakaractu.com/Departements-les-plus-peuples-du-Senegal-Mbacke-en-tete-avec-1-359-757-d-habitants-devant-Dakar-Mbour-et-Thies_a239855.html | Mbacké is the most populous département (ANSD atlas: 1,359,758); Dakar 1,278,471; Guédiawaye density 58,688/km² |
| G6 | Journal officiel n° 6280 du 27 mai 2006 (Décret n° 2005-992 du 21 octobre 2005, orthographe du wolof) | https://www.vie-publique.sn/documents/14178/JO-6280-du-27-mai-2006 | Official Wolof orthography (Latin alphabet, 27 letters incl. ë, ñ, ŋ, x, q) |
| G7 | N-WAYS LIMITED desk research on Senegal's regions, data protection and postcodes (checked 2026-10-17; unpublished working notes) | | 14 regions and governors; data protection summary; postcode research, superseded by P1-P3 where they overlap |

## Place names: short forms people already say (plate names, SPEC 3.2.1)

Every short form used as a plate name without the commune's choice needs a written source. These are the only ones the model asserts; each is in `tools/sn_plates.py` (`KNOWN`).

| # | Source | URL | What it supports |
|---|---|---|---|
| N1 | Wikipédia (fr), "Saly Portudal" (accessed 2026-10-18) | https://fr.wikipedia.org/wiki/Saly_Portudal | "Saly Portudal (ou couramment Saly) est une station balnéaire…": plate name **Saly** for Saly Portudal (and the map's spelling Sali Portudal) |
| N2 | Wikipédia (fr), "Dakar-Plateau" (accessed 2026-10-18) | https://fr.wikipedia.org/wiki/Dakar-Plateau | The article names the area "le Plateau" ("Le Plateau demeure parmi les ensembles urbains les plus marqués par l'influence européenne en Afrique"): plate name **Plateau** for Dakar-Plateau |

Looked for and **not found** (so these go to the commune, `COUNCIL` in `tools/sn_plates.py`): a written source for "Parcelles" as the short form of Parcelles Assainies (checked fr.wikipedia "Les Parcelles Assainies", en.wikipedia "Parcelles Assainies", vie-publique.sn, Le Soleil, Senego, Seneweb: all use the full name); "Joal" alone for Joal-Fadiouth (fr.wikipedia describes Joal and Fadiouth as two villages of one commune).

## Data used to build the registry

| # | Data | Licence | Use |
|---|---|---|---|
| X1 | OpenStreetMap buildings for Senegal (extract of October 2026, 1,378,821 footprints) | ODbL 1.0, © OpenStreetMap contributors | Footprints, tags (building, levels, amenity, shop…) |
| X2 | Google Open Buildings and Microsoft building footprints via Overture Maps (4,264,275 footprints in Senegal) | CC BY 4.0 / ODbL | Footprints. The height value carried with them is a **rendering filler, not a height** (see X5) |
| X3 | N-Ways places database (23,415 points of interest in the Senegal box) | Mixed (OSM ODbL, Overture CDLA/ODbL, Foursquare OS Places Apache-2.0, healthsites) | Classes from places inside a footprint; no place record is redistributed |
| X4 | N-Ways gates and gated compounds of the routing network | Derived from OSM, ODbL | Gates and enclosures |
| X5 | The footprint copy used (X2) | | Where Overture has no height it carries 3.5 + 3.5 × (hash(id) % 1000)/1000 m for map rendering: every Senegal footprint is 3.5-7.0 m, with 36 distinct values, so the value is never used |
| X6 | Open Location Code | Apache-2.0 | https://github.com/google/open-location-code |
| X7 | OpenStreetMap admin_level=2 boundary of Senegal (relation 192775, extract of October 2026) | ODbL 1.0, © OpenStreetMap contributors | The national border (`engine/data/border.geojson`, `tools/build_border.py`): no address more than 300 m outside it |

## Literature and impact sources cited in the paper

The paper's full bibliography, with every entry checked against the publisher's or the issuing body's page (accessed 2026-10-21), is [docs/paper/references.bib](docs/paper/references.bib). The sources used for the impact estimates are:

| # | Source | URL | What it supports |
|---|---|---|---|
| I1 | M. Bah, "Livraison last-mile à Dakar : coûts et délais réels (2026)", Kolonell, 20 Aug 2026 | https://kolonell.com/fr/blog/livraison-last-mile-cout-delai-dakar-2026 | Intra-Dakar motorbike run 1,000-1,500 FCFA (centre), 1,500-2,500 FCFA (periphery); failure rates 8-12% and 12-15% (practitioner estimate) |
| I2 | M. Bah, "Livraison sans adresse formelle : points relais et géolocalisation e-commerce à Dakar 2026", Kolonell, 10 Aug 2026 | https://kolonell.com/fr/blog/livraison-sans-adresse-points-relais-geolocalisation-dakar-2026 | First-attempt failure 22-30% without a formal address; 8-12% with a GPS pin and a spoken landmark (practitioner estimate) |
| I3 | M. Bah, "Réduire le taux d'échec de livraison en cash à Dakar en 2026", Kolonell, 25 Aug 2026 | https://kolonell.com/fr/blog/reduire-taux-echec-livraison-cash-dakar-2026 | Of failed cash-on-delivery attempts, 22% cite an incomplete address, 28% an unreachable customer |
| I4 | M. P. Larsen et al., "Predicting survival from out-of-hospital cardiac arrest: a graphic model", *Annals of Emergency Medicine* 22(11), 1993 | https://doi.org/10.1016/S0196-0644(05)81302-2 | Survival 67% less 2.3, 1.1 and 2.1 points per minute to CPR, defibrillation and advanced care |
| I5 | M. Hunt et al., "Challenges locating the scene of emergency: a qualitative study of the EMS system in Rwanda", *Prehospital Emergency Care* 28(3), 2024 | https://doi.org/10.1080/10903127.2023.2225195 | Locating patients depends on local knowledge and repeated calls, lengthening response intervals |
| I6 | World Bank, World Development Indicators, SP.URB.GROW (Senegal) | https://data.worldbank.org/indicator/SP.URB.GROW?locations=SN | Urban population growth 3.3-4.8% a year in 2015-2024 (mean 4.6%): the headroom of Eq. (7) |
