---
title: "Une adresse pour chaque concession : un modèle national d'adressage pour le Sénégal"
kind: "Article de recherche"
author:
  - "The N-Ways Addressing Group"
affiliation: "N-WAYS LIMITED (nways.ng)"
date: "Octobre 2026"
abstract-title: "Résumé"
abstract: |
  Les codes postaux du Sénégal désignent des bureaux distributeurs, ses plaques de rue ne couvrent qu'une partie de neuf villes, et son programme national d'adressage numérique n'a pas encore publié de format : la plupart de ses 18,1 millions d'habitants ne peuvent pas donner une adresse qui mène jusqu'à leur portail. Nous présentons un modèle national d'adressage conçu pour le Sénégal et le registre émis avec lui, qui donne à chacune des 3 597 128 concessions une adresse de la forme *nom de lieu + numéro*, par exemple *Ouakam 2512*. Les lieux qui portent le même nom tirent leurs numéros d'une plage nationale unique par nom, découpée en blocs disjoints, si bien que l'adresse dite est unique dans le pays sans ville ni position. Les numéros suivent une courbe de Hilbert avec une réserve triple pour la croissance ; une forme machine porte une lettre de contrôle ISO/IEC 7064 que personne n'a à voir ; et tout point reçoit hors ligne un code de point sur la grille UTM 28N. Sur l'ensemble du registre, chaque adresse se décode en une seule concession, deux numéros consécutifs sont distants de 23 m en médiane, et 76 % des erreurs d'un chiffre ne correspondent à aucune adresse. Partout où l'État donne une adresse, celle-ci s'affiche en premier. Spécification, moteur, registre et serveur sont ouverts.

  **Mots-clés :** adressage ; noms de lieux ; caractères de contrôle ; courbes de remplissage ; empreintes de bâtiments ; Sénégal.
rights: "© 2026 N-WAYS LIMITED. Texte sous licence CC BY 4.0. Données © N-WAYS LIMITED sous ODbL 1.0 ; contient des données OpenStreetMap © les contributeurs d'OpenStreetMap."
lang: fr-FR
papersize: a4
fontsize: 11pt
geometry: "margin=2.3cm"
toc-title: "Table des matières"
---

# Introduction

## Le problème

Une adresse remplit trois fonctions : elle permet à une personne de dire où elle habite, à une autre de trouver ce lieu, et aux institutions de désigner le même lieu dans leurs fichiers. Au Sénégal, aucun des systèmes existants ne remplit ces trois fonctions pour la plupart des ménages. Les codes postaux de La Poste désignent un bureau distributeur et sa zone : le seul code 22300 couvre toute la ville de Touba, qui compte plus d'un million d'habitants [@upu2015; @laposte2026]. Les plaques bleues et les numéros métriques posés par les programmes municipaux depuis la fin des années 1990 couvrent une partie de neuf villes et sont, de l'aveu même des autorités, largement incomplets et obsolètes [@farvacque2005; @osmwiki; @edjo2021]. Le programme d'Adressage Numérique National (ANN), relancé les 5 et 6 août 2026 avec l'objectif d'un référentiel unique d'adresses géoréférencées, n'a encore publié ni format, ni plateforme, ni données [@ba2026; @njoya2026]. On continue d'indiquer le chemin par des repères : « face BCEAO », « derrière la mosquée ».

Ce manque pèse d'abord sur ceux qui ont le moins. Le livreur appelle plusieurs fois son client avant de trouver le portail ; l'équipage d'une ambulance dépend de la connaissance du quartier qu'a l'appelant ; un ménage ne peut pas prouver son domicile à une banque ou à un concessionnaire de service. L'adressage classique, qui nomme les rues et numérote les portes, coûte cher, prend des années et se dégrade s'il n'est pas utilisé [@farvacque2005]. La plupart des concessions du Sénégal se trouvent dans des villages et des extensions urbaines denses où les rues n'ont pas de nom.

## Contribution

Cet article décrit un modèle national d'adressage conçu pour le Sénégal et le registre émis avec lui en octobre 2026. Ses apports sont les suivants :

1. **Une forme mémorisée qui se passe de contexte.** Une adresse est un nom de lieu déjà en usage suivi d'un numéro court, *Ouakam 2512*. Les lieux qui portent le même nom tirent leurs numéros d'une plage nationale unique pour ce nom, découpée en blocs disjoints (section 4.6) : l'adresse dite est donc unique au Sénégal à elle seule. Nous démontrons l'unicité du décodage et la vérifions sur les 3 597 128 adresses émises (section 6.1).
2. **Des noms courts par règle.** Une règle fixe tire de chaque nom officiel un *nom de plaque* d'au plus 12 caractères et deux mots, et renvoie à la commune les cas qu'elle ne peut pas raccourcir sans risque (section 4.4).
3. **Des numéros qui suivent le terrain.** Dans un lieu, les numéros suivent une courbe de Hilbert avec une réserve triple : des voisins reçoivent des numéros proches, et une nouvelle concession s'insère entre eux sans renumérotation (sections 4.7 et 4.8).
4. **Un contrôle d'erreur invisible.** La forme machine porte une lettre de contrôle ISO/IEC 7064 MOD 11-2 écrite avec onze lettres choisies pour des francophones ; les formes dite et écrite n'en portent aucune (section 4.10).
5. **L'adresse de l'État d'abord.** Un masque de couverture affiche l'adresse municipale officielle, puis celle de l'ANN, partout où elle existe ; l'adresse N-Ways devient alors un alias (section 4.14).
6. **Une mise en œuvre ouverte et complète.** La spécification, un moteur de référence en bibliothèque standard, le registre complet avec ses empreintes cryptographiques, et un serveur qu'un ministère ou un opérateur déploie en une commande sont publiés sous licences ouvertes, avec des vecteurs de conformité et des tests de parité avec l'émetteur (section 5).

## Plan

La section 2 passe en revue les systèmes existants du Sénégal et la pratique internationale. La section 3 décrit les données. La section 4 expose le modèle, formule par formule, avec un exemple résolu sur l'adresse *Ouakam 2512*. La section 5 décrit la mise en œuvre et la section 6 ses propriétés mesurées. La section 7 rend compte des conceptions étudiées puis écartées. Les sections 8 à 11 examinent les bénéfices pour les citoyens, la logistique et le commerce, les services d'urgence et l'État. La section 12 traite de la vie privée, de la sécurité et de la gouvernance, la section 13 des limites, et la section 14 conclut.

# Contexte et travaux antérieurs

## Les codes postaux de La Poste

La Poste Sénégal écrit un code postal à cinq chiffres à gauche du bureau distributeur, comme dans `12500 DAKAR` ou `27000 Ziguinchor` [@upu2015]. La fiche d'adressage de l'Union postale universelle décrit le code comme une zone d'acheminement, un bureau distributeur et une zone de distribution ; dans les données de La Poste, les deux premiers chiffres suivent la géographie, de 10–17 pour la région de Dakar à 36 pour Matam. L'outil de recherche en ligne de La Poste associe 4 143 noms de localités et de quartiers à 166 valeurs, dont 163 codes bien formés [@laposte2026]. Le seul code 17000 couvre 250 lieux nommés des banlieues de Pikine et de Keur Massar. L'outil publie des noms, pas des limites, et n'indique aucune licence. Le courrier est surtout distribué en boîtes postales (BP) et en « postchances ». Le code postal répond donc à la question « quel bureau de poste ? », non à la question « quelle porte ? ».

## L'adressage municipal

L'adressage des rues au Sénégal remonte à un projet pilote à Mbour en 1993 et a été mené à grande échelle dans le cadre du Programme d'appui aux communes (PAC, 1998–2004), financé par la Banque mondiale et conduit par l'Agence de développement municipal [@farvacque2005]. Une rue est codée par un radical de deux lettres propre au quartier et un numéro (ES.12, douzième rue de l'Escale), et les portes sont numérotées selon le système métrique, pairs et impairs de part et d'autre. Sur les quinze villes éligibles au départ, huit ont achevé toutes les tâches (Thiès, Louga, Diourbel, Kaolack, Ziguinchor, Saint-Louis, Guédiawaye et Tambacounda), trois n'ont réalisé que la signalisation (Dakar, Rufisque et Pikine) et quatre n'ont pas tenu les délais du programme [@farvacque2005]. À Thiès et à Kaolack, le programme a aussi rapproché le répertoire d'adresses des rôles d'impôt.

Les plaques actuelles indiquent le quartier, le nom ou le numéro de la rue et une référence telle que PE-44 (Point E), SC-15 (Sacré-Cœur) ou OKM-1 (Ouakam) [@osmwiki; @ausenegal2018]. Le numéro d'une porte est sa distance en mètres depuis le début de la rue, si bien que les portes portent souvent deux numéros peints au pochoir, l'ancien et le nouveau [@ausenegal2018]. En 2019, l'Autorité de régulation des télécommunications et des postes (ARTP) faisait état de 224 000 bâtiments numérotés dans 255 quartiers de Dakar [@aps2019]. Au lancement du projet national d'adressage numérique, en 2021, l'adressage physique était décrit comme largement incomplet et obsolète [@edjo2021].

## L'Adressage Numérique National

Le ministère de l'Économie numérique et des Télécommunications a lancé un projet national d'adressage numérique le 25 février 2021, avec l'objectif de cartographier le territoire et de doter chaque lieu d'une adresse numérique en trois ans [@edjo2021]. En 2023, il a été présenté sous le slogan « Un Sénégalais, une adresse » [@njoya2026]. Les 5 et 6 août 2026, le ministère chargé des télécommunications et du numérique a tenu un atelier de relance avec les administrations centrales, les collectivités territoriales, le secteur privé, l'université et la société civile. L'objectif affiché est un « référentiel national d'adresses unique, géoréférencé et partagé » au service des services publics, du commerce en ligne, de la fiscalité, de la gestion foncière, de la poste et de la logistique et des urgences, la phase pilote devant s'achever en un an [@ba2026; @njoya2026]. Des observateurs ont averti que, faute d'une autorité clairement désignée, le pays risquait de « multiplier les bases incompatibles » [@snl2026]. En octobre 2026, aucun format d'adresse, aucune zone pilote, aucune plateforme, aucune interface ni aucune licence de données n'avait été publié. Un modèle qui veut servir le Sénégal doit donc pouvoir être adopté, rapproché ou remplacé sans peine par l'ANN.

## Foncier, cadastre et géodésie

La loi 64-46 de 1964 range dans le *domaine national* toutes les terres qui ne relèvent ni du domaine de l'État ni de l'immatriculation, soit selon les estimations courantes 80 à 85 % du territoire ; les communes en affectent l'usage, et elles ne peuvent être vendues comme propriété privée [@loi1964]. La loi 2011-07 régit les terres immatriculées, sur lesquelles un droit réel n'existe qu'une fois inscrit au livre foncier [@loi2011]. Le cadastre attribue aux parcelles un numéro NICAD. Le projet PROCASEF, financé par la Banque mondiale (80 millions de dollars, depuis août 2021), avait levé et cartographié plus de 830 000 parcelles dans 138 communes en juin 2026, dont plus de 630 000 dotées d'un NICAD [@aps2026procasef]. Aucune couche parcellaire ouverte n'est publiée. Dans ce contexte, une adresse ne doit jamais pouvoir être prise pour une preuve de propriété.

Le réseau géodésique sénégalais a connu cinq systèmes de référence : trois d'entre eux, les systèmes Adindan, Yoff et 1974, emploient la projection UTM sur l'ellipsoïde de Clarke 1880, tandis que le système Hatt, sur lequel ont été dressées les anciennes feuilles cadastrales, repose sur une projection stéréographique ; un système géocentrique, NSGD2004, rattaché à l'ITRF2000 avec l'ellipsoïde GRS80, a été conçu et réalisé en 2004 [@ndiaye2005]. La grille nationale historique Yoff / UTM fuseau 28N (EPSG:31028) et son équivalent WGS 84 (EPSG:32628) partagent la même projection [@epsg31028]. Les géomètres lisent donc déjà leurs coordonnées sur la grille UTM fuseau 28N que nous utilisons pour les codes de point (section 4.11).

## Pratique internationale

La norme S42 de l'UPU décrit les éléments des adresses postales et des modèles nationaux pour les écrire [@upuS42], et la norme ISO 19160-1 donne un modèle conceptuel de l'adressage [@iso19160]. L'une et l'autre décrivent la manière de représenter une adresse qui existe ; aucune ne dit comment en créer une là où il n'y en a pas. Le livre blanc de l'UPU *Addressing the world* soutient que l'adresse est une condition de la citoyenneté, du commerce et de l'accès aux services [@upu2012]. L'étude de la Banque mondiale sur l'adressage de 52 villes de 15 pays africains entre 1989 et 2004, qui inclut le programme sénégalais, constate que, dans un échantillon de 21 villes, seules 8 % des rues avaient un nom avant l'adressage, que l'adressage classique coûtait en moyenne 5,7 dollars par porte, et que sa valeur tient à son usage par les services municipaux, au premier rang desquels la fiscalité locale [@farvacque2005].

Plusieurs systèmes calculent un identifiant à partir des coordonnées. L'Open Location Code (« Plus Codes ») code la latitude et la longitude dans un alphabet de base 20 et fonctionne hors ligne [@olc]. Des systèmes à mots attribuent trois mots à chaque carré de 3 m. Ces codes sont universels et se passent de registre, mais ils désignent des carrés et non des bâtiments, ils changent d'un carré à l'autre au sein d'une même concession, et leurs lettres ou leurs mots n'ont aucun sens pour celui qui les porte. Un code calculé à partir des coordonnées ne peut pas non plus exprimer la concession, l'unité à laquelle appartiennent un portail, un ménage et une livraison.

Le contrôle d'erreur des identifiants recopiés par des personnes a une longue histoire. Verhoeff a classé les erreurs commises en recopiant des chiffres, la substitution d'un chiffre et l'inversion de deux chiffres voisins étant les plus fréquentes [@verhoeff1969]. La norme ISO/IEC 7064 spécifie des systèmes de caractères de contrôle ; son système pur MOD 11-2 détecte toute substitution simple et toute inversion de deux voisins, au prix d'un onzième symbole [@iso7064]. Les quasi-groupes totalement antisymétriques de Damm obtiennent le même résultat avec un chiffre décimal [@damm2004; @damm2007]. Pour l'ordre, les courbes de remplissage projettent le plan sur une droite en préservant la proximité ; la courbe de Hilbert regroupe les cellules voisines mieux que les courbes en Z et de Gray [@hilbert1891; @moon2001].

## Exigences

Nous tirons de cette revue six exigences pour une adresse sénégalaise.

- **E1, mémorisable.** On doit pouvoir la dire, l'entendre et l'écrire sans appareil. Les Sénégalais retiennent déjà des noms de quartiers et des nombres (numéros de téléphone par paires, numéros de BP, numéros de porte), mais rarement des codes mêlant lettres et chiffres.
- **E2, unique sans contexte.** Un nom se dit sans sa ville : l'adresse dite doit désigner à elle seule une concession du pays.
- **E3, à l'échelle de la concession.** L'adresse mène à un portail et appartient à la concession que ce portail dessert.
- **E4, stable.** Elle ne change jamais et n'est jamais réattribuée, quoi qu'il advienne des limites administratives, des noms de quartiers ou de la carte du bâti.
- **E5, à côté des systèmes officiels.** Elle affiche l'adresse de l'État là où elle existe et peut être absorbée par l'ANN.
- **E6, ouverte et vérifiable.** Les règles, le code et les données sont publics, de sorte que toute institution peut reproduire chaque adresse.

# Données et sources

## Empreintes de bâtiments

Le registre est construit à partir de 5 643 096 empreintes de bâtiments : 1 378 821 issues d'OpenStreetMap [@haklay2008; @geofabrik2026] et 4 264 275 détectées par apprentissage automatique sur images satellitaires, provenant de Google Open Buildings [@sirko2021] et des empreintes mondiales de Microsoft [@microsoft2023], diffusées par Overture Maps [@overture2026]. Après retrait de 10 415 empreintes dont le centroïde tombe hors des contours départementaux de 2019 (sur le littoral et le long des frontières), il en reste 5 632 681. Les deux sources se complètent de façon inégale (figure 1) : OpenStreetMap fournit 68 % des empreintes à Sédhiou et 59 % à Kolda, où la cartographie communautaire a été intense, mais moins de 10 % à Thiès, à Diourbel et à Kaffrine, où dominent les jeux issus de l'apprentissage automatique.

![Empreintes de bâtiments par région et par source : OpenStreetMap face aux jeux issus de l'apprentissage automatique (Google Open Buildings et Microsoft, diffusés par Overture Maps), en milliers. Source : `model/building-stats.json`.](figures/footprint-sources.fr.svg)

Les empreintes portent peu d'attributs. Parmi celles d'OpenStreetMap, 1 099 686 ne sont étiquetées que `building=yes`. Le nombre de niveaux n'est connu que là où OpenStreetMap l'indique : pour 515 empreintes du département de Dakar et 19 à Touba. La colonne de hauteur diffusée avec les empreintes issues de l'apprentissage automatique ne prend que 36 valeurs distinctes, entre 3,5 et 7,0 m, sur 4 257 726 lignes : c'est une valeur d'affichage par défaut, non une mesure, et le modèle ne l'utilise jamais.

## Limites et lieux

Les contours administratifs sont ceux des départements (ADM2) et arrondissements (ADM3) de 2019 publiés par geoBoundaries, issus de données du Gouvernement du Sénégal compilées par OCHA [@runfola2020]. Les points de lieux proviennent des nœuds de lieux d'OpenStreetMap et des lieux habités de GeoNames : 16 994 candidats, dont 1 142 doublons GeoNames de lieux OpenStreetMap ont été retirés, soit 15 852, dont 14 997 reçoivent au moins une concession. Les chiffres de population sont ceux du cinquième recensement général (RGPH-5, 2023) : 18 126 390 résidents [@ansd2024]. La croissance de la population urbaine est tirée des Indicateurs du développement dans le monde [@wdi2026]. La frontière nationale est la limite admin_level 2 du Sénégal dans OpenStreetMap [@geofabrik2026], et c'est elle qui décide des bâtiments situés dans le pays : un bâtiment dont l'entrée se trouve à plus de 300 m au-delà est dans un pays voisin et ne reçoit pas d'adresse, quoi que disent les contours départementaux (section 4.2).

## Ce que montre la carte du bâti

Le regroupement des 5 632 681 empreintes en concessions selon les règles de la section 4.12 donne 3 595 628 concessions dans le calcul d'analyse ; le calcul d'émission, deux jours plus tard et à partir des mêmes sources, en compte 3 597 128 (0,04 % de plus), et tous les comptes d'adresses qui suivent portent sur le registre émis. Quatre constats ont orienté le modèle.

- **Des concessions, non des bâtiments.** Hors de Dakar et de Ziguinchor, 52 à 62 % des empreintes, selon la région, appartiennent à des concessions de plusieurs bâtiments ; la part est de 32,6 % dans le département de Dakar et de 49,5 % à Touba. Une adresse par empreinte donnerait plusieurs adresses à une concession familiale faite de cuisines, de chambres et d'annexes.
- **Les portails sont presque inconnus.** OpenStreetMap et le réseau de navigation contiennent 1 403 portails et entrées et 6 351 clôtures (murs, grillages et sites clos) pour tout le pays. Un portail est connu pour 126 des 107 391 concessions du département de Dakar et pour 3 des 289 293 de Touba.
- **Les usages sont surtout déduits.** La plupart des empreintes n'ayant aucune étiquette, les classes autres que l'habitat sont rares dans les comptes, et la plupart des classes d'habitat sont déduites de la forme.
- **Le bâti est dense là où les points de lieux sont rares.** Les 289 328 concessions de Touba se répartissent entre 241 points de lieux, les 123 594 de Pikine entre 39. Les numéros y sont longs (annexe A).

| Région | Empreintes | Concessions | Dans des concessions à plusieurs bâtiments | Empreinte médiane (m²) | Habitat | Inconnu |
|:--|--:|--:|--:|--:|--:|--:|
| Thiès | 800 303 | 525 647 | 51,7 % | 34 | 92,5 % | 7,2 % |
| Diourbel | 731 035 | 463 545 | 54,8 % | 26 | 88,7 % | 11,2 % |
| Dakar | 530 668 | 413 099 | 35,8 % | 77 | 95,0 % | 3,7 % |
| Louga | 516 209 | 322 353 | 55,8 % | 22 | 91,3 % | 8,6 % |
| Kaolack | 442 506 | 272 452 | 55,5 % | 26 | 90,4 % | 9,4 % |
| Kolda | 409 734 | 231 350 | 61,7 % | 26 | 89,7 % | 10,1 % |
| Saint-Louis | 401 420 | 253 865 | 55,3 % | 27 | 92,2 % | 7,0 % |
| Fatick | 374 909 | 211 817 | 60,9 % | 23 | 91,7 % | 8,1 % |
| Tambacounda | 371 314 | 217 861 | 57,1 % | 21 | 89,1 % | 10,8 % |
| Kaffrine | 308 780 | 182 828 | 56,4 % | 21 | 81,5 % | 18,4 % |
| Matam | 280 135 | 175 981 | 54,5 % | 22 | 93,5 % | 6,3 % |
| Ziguinchor | 166 969 | 129 377 | 37,7 % | 83 | 97,5 % | 1,7 % |
| Kédougou | 150 063 | 99 037 | 49,0 % | 21 | 71,9 % | 27,5 % |
| Sédhiou | 148 636 | 96 416 | 52,9 % | 52 | 97,7 % | 2,2 % |

: Empreintes et concessions par région (calcul d'analyse). Les classes autres que l'habitat et l'inconnu représentent chacune moins de 1 % dans chaque région ; elles figurent dans `model/building-stats.json`.

# Le modèle

## L'adresse et ses formes

Chaque concession a une identité et quatre formes (tableau ci-dessous), qui se correspondent une à une. La forme mémorisée ne contient aucune lettre à apprendre ni aucun caractère de contrôle. Le nom de zone de la forme écrite renseigne le lecteur ; il ne fait pas partie de l'identité.

| Forme | Exemple | Utilisée par |
|:--|:--|:--|
| Mémorisée | **Ouakam 2512** | tout le monde : dite, écrite sur un colis, tapée dans un message |
| Écrite | **OUAKAM 2512 · DAKAR** | plaques, autocollants, formulaires |
| Machine | `SN-DKR-0080-2512-J` | bases de données, codes QR, systèmes des partenaires |
| Point | `DKR 5553 1512` | tout point sans concession |

: Les quatre formes d'une adresse. La forme machine donne la zone, l'indice du lieu, le numéro et la lettre de contrôle ; personne n'a besoin de la retenir.

Nous prenons *Ouakam 2512* comme exemple tout au long de l'article. C'est une maison de plain-pied du quartier de Ouakam, dans la zone DKR (Dakar), lieu d'indice 80 ; sa forme machine est `SN-DKR-0080-2512-J`.

## Les zones

Chaque adresse se rattache à une zone de code, qui fournit son nom écrit, son fichier de registre et sa grille de points. Les 14 régions sont trop vastes pour un seul espace de numéros : Tambacounda couvre 42 214 km² et Thiès compte 803 020 empreintes. Les zones sont les 45 départements des limites de 2019, Mbacké étant scindé en deux : son arrondissement de Ndame, qui regroupe Touba et la ville de Mbacké et 417 008 empreintes, devient la zone TBA, et le reste devient KTF (Kaël-Taïf). Les zones ont été figées à la première émission du registre et ne suivent jamais les découpages ultérieurs. Lorsque Keur Massar est devenu le 46^e^ département du Sénégal en 2021, un modèle lié à la carte administrative aurait dû réadresser chaque logement ; ici, Keur Massar reste dans la zone PKN et son département actuel est un attribut de la fiche du lieu. La figure 2 montre les 46 zones et la densité des concessions.

![Les 46 zones de code figées et la densité des 3 597 128 adresses émises, en concessions par maille de 4 km × 4 km sur la grille UTM fuseau 28N. Sources : `model/zones.geojson`, `registry/anchors/`.](figures/zones-map.fr.svg)

Soit $Z$ l'ensemble des zones, chacune munie d'un indice $\iota(z) \in \{0, \dots, 45\}$ dans l'ordre des clés et d'un contour $\partial z$. Un point $p$ appartient à la zone

$$
\zeta(p) =
\begin{cases}
\arg\min_{z \in Z} \{\iota(z) : p \in \operatorname{int} \partial z\} & \text{s'il existe une telle zone,}\\
\arg\min_{z \in Z} \min_{v \in \partial z} \lVert \pi(p) - \pi(v) \rVert & \text{si cette distance est d'au plus } 2\,000 \text{ m,}\\
\varnothing & \text{sinon,}
\end{cases}
\tag{1}
$$

où $\pi$ est la projection en UTM fuseau 28N (éq. (17)), $v$ parcourt les sommets du contour, et l'appartenance est testée par lancer de rayon, trous exclus. Le deuxième cas rattrape les points du littoral et des frontières fluviales que les contours de 2019 laissent de côté.

**La frontière décide.** Les contours départementaux, et la portée de 2 km de l'éq. (1) le long des côtes et des fleuves, peuvent déborder la frontière nationale $B$, la limite admin_level 2 d'OpenStreetMap. Quoi que donne l'éq. (1), un point situé hors de $B$ avec $\min_{q \in B} \lVert \pi(p) - \pi(q) \rVert > 300$ m est hors du Sénégal, $\zeta(p) = \varnothing$ : le regroupement écarte les bâtiments et les concessions qui s'y trouvent (section 4.12), l'émetteur ne leur donne pas d'adresse, et une entrée n'y est jamais déplacée. La marge de 300 m absorbe l'erreur de position des empreintes et du tracé de la frontière lui-même, qui suit des fleuves comme le Sénégal et la Gambie. Le moteur embarque la frontière simplifiée par Douglas–Peucker à 50 m ; la ligne simplifiée s'écarte d'au plus 50,4 m de la vraie, si bien que le moteur lui applique 249 m et n'accepte jamais un point situé à plus de 300 m au-delà de la vraie frontière.

Chaque zone possède un cadre carré en mètres UTM, qui sert aux codes de point et à la numérotation. Avec $E$ et $N$ les abscisses et ordonnées du contour de la zone,

$$
\begin{aligned}
E_0 &= 1000 \left\lfloor \tfrac{\min E}{1000} \right\rfloor, \qquad
N_0 = 1000 \left\lfloor \tfrac{\min N}{1000} \right\rfloor, \qquad
F = 1000 \left\lceil \tfrac{\max(\max E - E_0,\; \max N - N_0)}{1000} \right\rceil, \\
s &= \begin{cases} \min\{\sigma \in \{1, 2, 5, 10\} \text{ m} : F/\sigma \le 10^4\} & \text{si } F \le 100 \text{ km},\\ 10 \text{ m} & \text{sinon,} \end{cases}
\qquad
k = \begin{cases} 4 & \text{si } F/s \le 10^4,\\ 5 & \text{sinon,} \end{cases}
\end{aligned}
\tag{2}
$$

où $F$ est le côté du cadre, $s$ la maille des codes de point et $k$ le nombre de chiffres par axe d'un code de point. Pour Dakar, $E_0 = 227\,000$ m, $N_0 = 1\,620\,000$ m et $F = 16$ km, d'où $s = 2$ m et $k = 4$. Sur les 46 zones, Guédiawaye a une maille de 1 m, Dakar et Pikine de 2 m, six zones (Touba, Saint-Louis, Rufisque, Bambey, Guinguinéo et Oussouye) de 5 m et les autres de 10 m ; les 18 zones dont le cadre dépasse 100 km ont cinq chiffres par axe.

## Le nom de lieu

Le nom de lieu est le quartier en ville, le village à la campagne, ou la cité là où c'est la cité que l'on nomme. Soit $Q(z)$ l'ensemble des quartiers, faubourgs, villages, localités et cités de la zone $z$, et $T(z)$ ses villes. Une concession $c$ reçoit le lieu

$$
\lambda(c) =
\begin{cases}
\arg\min_{q \in Q(z)} d(c, q) & \text{si } \min_{q \in Q(z)} d(c, q) \le 2\,500 \text{ m},\\
\arg\min_{t \in T(z)} d(c, t) & \text{sinon, si } \min_{t \in T(z)} d(c, t) \le 10\,000 \text{ m},\\
\arg\min_{q \in Q(z) \cup T(z)} d(c, q) & \text{sinon,}
\end{cases}
\tag{3}
$$

où $d$ est la distance en mètres UTM entre le centroïde de la concession et le point du lieu, les égalités allant à l'indice le plus bas. Le rattachement est fixé à la première numérotation de la concession et n'est jamais recalculé. Si un quartier est renommé, scindé ou disputé, l'adresse ne change pas : le nouveau nom s'ajoute comme alias.

## Le nom de plaque

Les noms tirés de la carte sont souvent trop longs à dire : « Keur Serigne Ablaye Yakhine », « Parcelles Assainies », « S.I.C.A.P. Liberté Six ». Chaque lieu garde donc deux noms. Le *nom officiel* est imprimé en petits caractères sur la fiche et sur la plaque, et reste accepté à la saisie. Le *nom de plaque* est celui de l'adresse. Soit $|s|$ le nombre de caractères d'une chaîne $s$ en forme normalisée C d'Unicode (une lettre accentuée, une espace, un trait d'union ou une apostrophe comptent pour un) et $w(s)$ ses mots, le trait d'union séparant deux mots et un numéro de secteur final comptant comme caractère mais non comme mot. Un nom de plaque est admissible lorsque

$$
\operatorname{ok}(s) \iff |s| \le 12 \;\wedge\; \bigl|\, w(s) \setminus L \,\bigr| \le 2 ,
\tag{4}
$$

où $L$ est l'ensemble des mots de liaison (de, du, des, d', la, le, les, l', et, sur, en, au, aux, à), qui ne comptent pas.

Le nom de plaque est tiré du nom officiel par une règle fixe, dans cet ordre : (i) une forme courte déjà en usage *et* attestée par écrit l'emporte : « Saly » pour Saly Portudal [@wikisaly], « Plateau » pour Dakar-Plateau [@wikiplateau] ; (ii) sinon le nom est nettoyé : un numéral final s'écrit en chiffres, les mots génériques (*quartier*, *village de*, *hameau*, *lotissement*), les sigles de promoteurs (S.I.C.A.P.), les parenthèses et les secondes graphies tombent, si bien que S.I.C.A.P. Liberté Six devient « Liberté 6 » ; « Cité » est conservé quand le nom tient (« Cité Lamy »), parce que c'est ainsi qu'on le dit ; (iii) si le nom nettoyé ne satisfait toujours pas l'éq. (4), les candidats sont les suites de mots entiers qui la satisfont, classées selon la rareté de leurs mots parmi tous les noms de lieux du Sénégal, et la meilleure n'est retenue que si son score vaut au moins 1,5 fois celui de la suivante. Aucun mot n'est jamais coupé.

Bien des noms sénégalais ne peuvent pas être raccourcis sans risque. « Keur Momar Sarr » est le village de Momar Sarr, et toute coupe retire une partie de son nom ; il en va de même des noms qui commencent par Darou, Médina, Saré, Sinthiou, Gourel ou Touba, et des noms qui contiennent un prénom ou un nom de famille. « Nguékokh Wolof » et « Nguékokh Sérère » sont deux villages : un qualificatif ethnique ou d'orientation n'est donc jamais supprimé sans le dire. Une forme courte ne peut pas devenir le nom d'une ville connue ni celui d'un autre lieu de la même zone. Dans tous ces cas, le lieu est signalé à sa commune avec jusqu'à trois candidats ; le premier sert à titre provisoire, et la commune peut le confirmer ou en choisir un autre, une seule fois, sans changer le numéro.

Sur les 14 997 noms officiels, 4 208 ne satisfont pas l'éq. (4) (4 154 par la longueur, 1 474 par le nombre de mots). La règle garde 10 763 noms tels quels, en nettoie 100, applique une forme courte attestée à 3 et garde les mots les plus distinctifs de 1 016. Elle en renvoie 3 116 à la commune : les 3 115 qu'elle ne peut raccourcir sans risque, et un nom nettoyé, « Richard Toll » (pour Campement Richard Toll), qui reprendrait le nom d'une ville connue. Parmi eux, 172 n'ont aucune partie admissible (« Diabrikindiong », « Touba Mosquée ») et restent au-dessus de la limite jusqu'à la décision de la commune. Ces 3 116 lieux portent 739 058 adresses. Un nom officiel que deux noms de plaque différents revendiqueraient est retiré des alias, afin qu'un nom tapé ne mène jamais à deux lieux ; c'est le cas de 55 noms.

## La clé de nom

Deux lieux portent le même nom quand leurs clés de nom sont égales. La clé efface tout ce que l'on confond à l'oreille ou à l'écrit, en français comme en wolof [@decret2005]. C'est la composée

$$
\kappa(s) = \tau \circ \chi \circ \phi \circ \beta \circ \eta \circ \nu \circ \sigma \circ \alpha (s),
\tag{5}
$$

dont les étapes figurent dans le tableau ci-dessous, appliquées de droite à gauche. Ouakam et Wakam donnent tous deux `wakam`, Mbacké et Mbakke `mbak`, Thiès et Ties `ties`. Trop replier ne fait qu'allonger une plage ; trop peu replier donnerait une même adresse à deux lieux : la règle est donc volontairement généreuse.

| Étape | Règle | Exemple |
|:--|:--|:--|
| $\alpha$, lettres | ñ → ny, œ → oe, æ → ae ; accents et casse effacés | Kër → ker |
| $\sigma$, découpage | traits d'union, apostrophes, points et parenthèses deviennent des espaces ; St, Ste → saint | Sacré-Cœur → sacre coeur |
| $\nu$, numéral | un nombre final, précédé ou non de *numéro* ou *no*, est retiré | HLM 5 → hlm |
| $\eta$, tête | le, la, les, l', de, du, d', quartier, village, hameau retirés quand un mot suit | Quartier Médina → medina |
| $\beta$, jonction | espaces supprimées | keur massar → keurmassar |
| $\phi$, repli | ou devant voyelle → w, autre ou → u ; eu → e ; kh → x ; th → t ; ph → f ; dj, et di devant voyelle → j ; gn → ny ; c devant e, i, y → s ; ck, qu, q, c → k ; y → i ; h muet retiré | Ouakam → wakam ; Ndiaye → njai |
| $\chi$, réduction | lettres doublées réduites à une | gunass → gunas |
| $\tau$, fin | e muet final retiré | njaiene → njaien |

: Les étapes de la clé de nom, éq. (5).

Les noms de plaque des 14 997 lieux se replient en 11 043 clés. Parmi elles, 1 974 sont portées par plusieurs lieux, 5 928 lieux au total, qui regroupent 41,9 % des concessions (1 506 591) ; 1 322 de ces noms répétés se retrouvent dans plusieurs zones et 652 dans une seule. Le plus répété est Ndiayène (32 lieux dans 18 zones), suivi de Mbayène et Thiékène (28 chacun), Darou Salam (23) et Ndiobène (22).

## Une plage nationale par nom

Les lieux d'une même clé forment une *famille* $\mathcal{F}$. Chaque famille dispose d'une plage nationale de numéros à $d$ chiffres, $[10^{d-1}, 10^d - 1]$, et chaque lieu $i \in \mathcal{F}$ en reçoit un bloc. Un lieu de $n_i$ concessions à la première émission reçoit un bloc de trois fois ses concessions, arrondi au grain $g_d$ de la plage :

$$
b(n_i, d) = g_d \max\!\left(1, \left\lceil \frac{3 n_i}{g_d} \right\rceil\right), \qquad g_3 = 10,\quad g_4 = g_5 = 100 .
\tag{6}
$$

Le facteur trois est une réserve pour la croissance. Si les concessions d'un lieu croissent à un taux annuel constant $r$, le bloc se remplit au bout de

$$
T(r) = \frac{\ln 3}{\ln(1 + r)} \ \text{ans}.
\tag{7}
$$

La population urbaine du Sénégal a crû de 3,3 % à 4,8 % par an entre 2015 et 2024, soit 4,6 % en moyenne [@wdi2026], ce qui donne $T$ entre 23 et 34 ans, et 24 ans au taux moyen. Un lieu dont le bloc se remplit ne manque pas de numéros : il reçoit un bloc supplémentaire dans l'espace libre de son nom (éq. (13)).

Tous les lieux d'une famille partagent une même longueur $d^*$, la plus courte pour laquelle leurs blocs occupent au plus 90 % de la plage, afin qu'au moins un dixième reste libre pour de nouveaux lieux du même nom :

$$
d^* = \min\left\{ d \in \{3, 4, 5\} : \sum_{i \in \mathcal{F}} b(n_i, d) \le 0{,}9 \cdot 9 \cdot 10^{d-1} \right\}.
\tag{8}
$$

Une plage à trois chiffres compte 900 numéros, dont 810 attribuables ; à quatre chiffres, 9 000 (8 100) ; à cinq chiffres, 90 000 (81 000). Un lieu seul tient donc en trois chiffres jusqu'à 270 concessions, en quatre jusqu'à 2 700 et en cinq jusqu'à 27 000. La figure 3 montre la répartition des lieux du Sénégal par rapport à ces seuils : le lieu médian compte 79 concessions, et 12 434 des 14 997 lieux en comptent au plus 270.

![Concessions par lieu, pour les 14 997 lieux du registre, en classes logarithmiques de cinq par décade. Les tirets marquent le plus grand lieu qui tient seul dans une plage de trois, quatre et cinq chiffres (éq. (8)). Source : `registry/`.](figures/lieu-sizes.fr.svg)

Les blocs sont découpés depuis le bas de la plage dans l'ordre (clé de zone, indice du lieu) :

$$
\ell_1 = 10^{d^*-1}, \qquad h_i = \ell_i + b(n_i, d^*) - 1, \qquad \ell_{i+1} = h_i + 1 .
\tag{9}
$$

*Exemple résolu.* Ouakam est seul dans sa famille (`wakam`, famille 10796) et comptait $n = 788$ concessions à la première émission. Trois chiffres demanderaient $3 \times 788 = 2\,364 > 810$ numéros, donc $d^* = 4$ et $b = 100 \lceil 2\,364/100 \rceil = 2\,400$ : le bloc de Ouakam est 1000–3399.

Les noms répétés montrent le mécanisme (figure 4). Les neuf lieux nommés Médina partagent la plage à cinq chiffres : la Médina de Dakar occupe 10400–17699, celle de Saint-Louis 19500–22799 et celle de Ziguinchor 22800–23299, et 23300–99999 reste libre. Les 23 lieux nommés Darou Salam, répartis dans 17 zones, regroupent 22 082 concessions ; le Darou Salam de Pikine occupe 23200–45799 et celui de Touba 46200–76599, et 75,0 % de la plage est attribuée. Avec les effectifs actuels, aucun nom n'a besoin de plus de cinq chiffres. Un nom qui dépasserait un jour sa plage prendrait un qualificatif établi, déjà en usage, décidé une fois pour toutes avec la commune, comme « Médina Baye » est déjà un nom distinct de « Médina ».

![Deux plages nationales de noms. Chaque lieu nommé Médina, et chaque lieu nommé Darou Salam, tire ses numéros d'une même plage à cinq chiffres, découpée en un bloc par lieu (éq. (6) à (9)) ; les blocs alternent de couleur, et le gris est la partie de la plage encore libre. Source : `model/name-families.json`.](figures/name-ranges.fr.svg)

## Numérotation le long d'une courbe de Hilbert

Dans son bloc, les concessions d'un lieu sont numérotées le long d'une courbe de Hilbert [@hilbert1891], de sorte que des voisins reçoivent des numéros proches, comme le long d'une rue. Le cadre de la zone est divisé en $2^{16} \times 2^{16}$ cellules de côté $\delta = F / 2^{16}$. Une concession de centroïde $(E, N)$ tombe dans la cellule

$$
x = \min\!\left(2^{16} - 1, \max\!\left(0, \left\lfloor \frac{E - E_0}{\delta} \right\rfloor\right)\right), \qquad
y = \min\!\left(2^{16} - 1, \max\!\left(0, \left\lfloor \frac{N - N_0}{\delta} \right\rfloor\right)\right),
\tag{10}
$$

et son indice de Hilbert $H(x, y)$ se calcule du niveau le plus haut au plus bas. Avec $h \leftarrow 0$ et, pour $m = 2^{15}, 2^{14}, \dots, 1$,

$$
\begin{aligned}
r_x &= [\,x \mathbin{\&} m \ne 0\,], \qquad r_y = [\,y \mathbin{\&} m \ne 0\,], \qquad h \leftarrow h + m^2 \bigl( (3 r_x) \oplus r_y \bigr),\\
(x, y) &\leftarrow \begin{cases} (m - 1 - y,\; m - 1 - x) & \text{si } r_y = 0 \text{ et } r_x = 1,\\ (y, x) & \text{si } r_y = 0 \text{ et } r_x = 0,\\ (x, y) & \text{si } r_y = 1, \end{cases}
\end{aligned}
\tag{11}
$$

où $\&$ est la conjonction bit à bit, $\oplus$ le ou exclusif bit à bit et $[\cdot]$ l'indicatrice. Deux indices consécutifs désignent toujours des cellules adjacentes, et la courbe regroupe les cellules voisines mieux que les courbes en Z et de Gray [@moon2001].

À la première émission, les $n$ concessions d'un lieu de bloc $[\ell, h]$ sont triées selon $(H, E, N)$ et réparties régulièrement sur le bloc :

$$
N_i = \ell + \left\lfloor \left(i + \tfrac12\right) \frac{h - \ell + 1}{n} \right\rfloor, \qquad i = 0, \dots, n - 1 .
\tag{12}
$$

Avec la réserve triple, il reste en moyenne deux numéros libres entre deux voisins.

*Exemple résolu.* Le centroïde de Ouakam 2512 se trouve en $E = 232\,438{,}4$ m, $N = 1\,629\,353{,}1$ m. Avec $\delta = 16\,000 / 65\,536 \approx 0{,}244$ m, il tombe dans la cellule $(22\,275, 38\,310)$, d'indice de Hilbert $2\,022\,592\,185$. Sur les 788 concessions de Ouakam, 496 la précèdent sur la courbe, donc $i = 496$ et

$$
N_{496} = 1000 + \left\lfloor 496{,}5 \times \frac{2\,400}{788} \right\rfloor = 1000 + \lfloor 1\,512{,}18 \rfloor = 2512 .
$$

La figure 5 montre le résultat pour tout le quartier : les numéros balaient Ouakam par plages contiguës, et la ligne qui relie les numéros consécutifs ne saute que rarement.

![Les 788 concessions de Ouakam à leurs centroïdes, colorées selon le numéro émis, en mètres depuis l'origine du cadre de la zone DKR. La ligne grise relie les numéros consécutifs, c'est-à-dire l'ordre de la courbe de Hilbert (éq. (10) à (12)). Sources : `registry/DKR.csv.gz`, `registry/anchors/DKR.csv.gz`.](figures/ouakam-hilbert.fr.svg)

## Les nouvelles concessions

Un numéro émis ne change jamais. Une concession bâtie après la première émission, d'indice de Hilbert $H$ dans un lieu de premier bloc $[\ell, h]$, a pour voisins les numéros émis $a$ juste avant elle et $b$ juste après sur la courbe (ou $\ell - 1$ et $h + 1$ aux extrémités). Son numéro est

$$
N_{\text{nouv}} =
\begin{cases}
\lfloor (a + b)/2 \rfloor & \text{si } b - a \ge 2 \text{ et s'il est libre,}\\
\text{plus petit numéro libre des blocs suivants du lieu} & \text{sinon, s'il en existe,}\\
\ell' \text{, début d'un nouveau bloc } [\ell', \ell' + g_{d^*} - 1] & \text{sinon, si la plage du nom a de la place,}\\
\text{premier numéro de « \textit{lieu} Extension »} & \text{sinon.}
\end{cases}
\tag{13}
$$

Un nouveau bloc est découpé au-dessus du plus haut bloc du nom et figé aussitôt. « Extension » reprend la façon dont les villes sénégalaises nomment déjà leur croissance (Keur Massar Extension, Médina Gounass Extension) ; le nom officiel « Ouakam Extension » dépassant déjà douze caractères, c'est la commune qui donne au nouveau quartier son nom de plaque. Un numéro retiré compte comme utilisé et n'est jamais réattribué.

## Décodage sans contexte

Une adresse mémorisée se décode à partir du seul texte. Les chiffres finals forment le nombre $D$ et les mots qui les précèdent le nom $P$. La clé $\kappa(P)$ donne la famille, la famille sa longueur $d^*$, et le numéro est formé des $d^*$ derniers chiffres de $D$ ; les chiffres éventuels qui les précèdent doivent être égaux au numéro de secteur du lieu (« HLM 5 17 394 »). Les candidats sont

$$
\operatorname{dec}(P, D) = \bigl\{ (i, N) : i \in \mathcal{F}(\kappa(P)),\; N = D \bmod 10^{d^*},\; N \in B_i \bigr\},
\tag{14}
$$

où $B_i$ est la réunion des blocs du lieu $i$.

**Proposition 1.** *Pour tout $(P, D)$, $\operatorname{dec}(P, D)$ a au plus un élément.* Les blocs d'une famille sont disjoints par construction (éq. (9), et éq. (13), qui ne découpe de nouveaux blocs que dans l'espace libre), et $d^*$ est fixé pour la famille ; $N$ est donc déterminé par $D$ et appartient à au plus un bloc. Les alias ne sont gardés que lorsqu'ils désignent une seule famille (section 4.4). $\square$

La proposition 1 est ce qui rend l'adresse dite unique au Sénégal sans ville ni position. La section 6.1 la vérifie sur chaque adresse émise.

## La lettre de contrôle

La forme machine porte une lettre de contrôle que personne n'a à voir : ni sur les plaques, ni sur les autocollants, ni dans la forme dite. Sa charge utile est l'identifiant de famille écrit sur cinq chiffres suivi du numéro écrit sur cinq, $u = u_1 u_2 \cdots u_{10}$. Elle se calcule avec le système pur MOD 11-2 de l'ISO/IEC 7064 [@iso7064] :

$$
p_0 = 0, \qquad p_k = 2\,(p_{k-1} + u_k) \bmod 11 \quad (k = 1, \dots, 10), \qquad c = (12 - p_{10}) \bmod 11,
\tag{15}
$$

et s'écrit comme la $c$-ième lettre (à partir de 0) de `FHJKMQRTWXZ`. Les onze lettres ont été choisies pour des oreilles francophones : une lettre par famille de noms de lettres qui riment (bé, cé, dé, gé, pé, té, vé), J plutôt que G (« gé » et « ji » se confondent), et aucune voyelle, pour qu'aucun mot ne puisse se former.

**Proposition 2.** *MOD 11-2 détecte toute substitution simple et toute inversion de deux chiffres voisins différents.* En développant l'éq. (15), $c \equiv 1 - \sum_k u_k w_k \pmod{11}$ avec les poids $w_k = 2^{11-k} \bmod 11$, tous non nuls puisque 2 est inversible modulo le nombre premier 11. Remplacer $u_k$ par $u_k' \ne u_k$ modifie la somme de $(u_k - u_k')\,w_k$, produit de deux résidus non nuls modulo un nombre premier, donc non nul. Échanger $u_k$ et $u_{k+1}$ la modifie de $(u_k - u_{k+1})(w_k - w_{k+1}) = (u_k - u_{k+1})\,w_{k+1}$, puisque $w_k = 2 w_{k+1}$, qui est encore non nul dès que $u_k \ne u_{k+1}$. $\square$

*Exemple résolu.* Pour Ouakam 2512, la charge utile est $u = 10796\,02512$. Les valeurs partielles $p_1, \dots, p_{10}$ sont 2, 4, 0, 7, 4, 8, 9, 6, 3, 10, d'où $c = (12 - 10) \bmod 11 = 2$, la lettre J, et la forme machine `SN-DKR-0080-2512-J`.

La lettre couvre la famille et le numéro ; le lieu se déduit du bloc. Une erreur d'un chiffre qui fait passer un numéro de la Médina de Dakar dans le bloc de Saint-Louis modifie donc exactement un chiffre de la charge utile et est toujours refusée dans une forme machine. Dans la forme dite, qui n'a pas de lettre, l'application affiche la ville avant de guider (section 6.4).

## Les codes de point

Un point sans concession, comme un champ, une place de marché ou une parcelle vide, reçoit un code de point calculé hors ligne. Avec $(E, N) = \pi(\varphi, \lambda)$,

$$
\begin{aligned}
x &= \left\lfloor \frac{E - E_0}{s} \right\rfloor, & y &= \left\lfloor \frac{N - N_0}{s} \right\rfloor,\\
\hat E &= E_0 + \left(x + \tfrac12\right) s, & \hat N &= N_0 + \left(y + \tfrac12\right) s,
\end{aligned}
\tag{16}
$$

où $x$ et $y$ s'écrivent chacun sur $k$ chiffres après la clé de zone, et $(\hat E, \hat N)$ est le point décodé, centre de la maille. L'erreur de décodage vaut au plus la demi-diagonale de la maille, $s\sqrt{2}/2$ : 0,7 m pour une maille de 1 m, 1,4 m pour 2 m et 7,1 m pour 10 m. La place de l'Indépendance à Dakar ($\varphi = 14{,}6681^\circ$, $\lambda = -17{,}4317^\circ$) se projette en $E = 238\,106{,}2$ m, $N = 1\,623\,024{,}8$ m, d'où $x = \lfloor 11\,106{,}2 / 2 \rfloor = 5553$, $y = \lfloor 3\,024{,}8 / 2 \rfloor = 1512$ et le code de point `DKR 5553 1512` (figure 6). Les codes de point ne portent pas de lettre de contrôle, parce que ce sont des personnes qui les tapent ; un code écrit avec une lettre finale, à l'ancienne, reste vérifié.

![La grille de points de la zone DKR : un cadre de 16 km d'origine $(E_0, N_0) = (227\,000, 1\,620\,000)$ m en UTM fuseau 28N, découpé en mailles de 2 m, si bien que chaque axe va de 0000 à 7999 (éq. (2) et (16)). Le contour est celui de la zone ; les deux points sont des exemples résolus de l'article. Sources : `model/zones.json`, `model/zones.geojson`.](figures/dakar-spot.fr.svg)

La projection est la projection de Mercator transverse de WGS 84 sur le fuseau UTM 28N, calculée avec les séries de Krüger à l'ordre quatre en le troisième aplatissement [@karney2011]. Avec $a$ et $f$ le demi-grand axe et l'aplatissement de WGS 84, $k_0 = 0{,}9996$, $\lambda_0 = -15^\circ$ et $\alpha_j$ les coefficients des séries,

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

avec $n \approx 0{,}001\,679\,2$ et $A \approx 6\,367\,449{,}146$ m. Sur le Sénégal, presque centré sur le méridien central du fuseau, la série est exacte à bien moins d'un millimètre près [@karney2011].

## Les concessions

La plupart des Sénégalais vivent en *concession* : une parcelle familiale close de murs, avec plusieurs bâtiments, un portail et souvent plusieurs ménages. Les villas ont une loge de gardien et une annexe ; les immeubles abritent de nombreux appartements derrière une porte ; les boutiques sont construites dans le mur sur rue des concessions. L'adresse appartient donc à la concession, ses bâtiments sont des sous-unités numérotées (« Ouakam 2512, bâtiment 2 »), les appartements et les portes de boutique sont des unités, et le guidage s'arrête au portail.

Les empreintes sont regroupées en concessions avant la numérotation. Pour deux bâtiments $a$ et $b$ de centroïdes $c_a, c_b$ et de surfaces $A_a, A_b$, l'*écart* est la distance entre centroïdes diminuée des rayons des cercles de même surface, et un bâtiment est *urbain* lorsque sa tuile de 250 m compte au moins 100 bâtiments (1 600 au km²) :

$$
\operatorname{écart}(a, b) = \lVert c_a - c_b \rVert - \sqrt{\frac{A_a}{\pi}} - \sqrt{\frac{A_b}{\pi}}, \qquad
\operatorname{urbain}(a) \iff \bigl|\operatorname{tuile}_{250}(a)\bigr| \ge 100 .
\tag{18}
$$

Les règles s'appliquent dans l'ordre. R0 (*clôture*) : tous les bâtiments situés dans un mur, un grillage ou un site clos cartographié, un contour tracé par le propriétaire ou, plus tard, une parcelle cadastrale forment une concession. R1 (*satellite*) : un bâtiment de moins de 30 m² dont l'écart à un bâtiment d'au moins 30 m² est d'au plus 4 m (en ville) ou 8 m (à la campagne) le rejoint ; ce sont les cuisines, les toilettes et les loges. R2 (*concession rurale*) : en milieu rural, les bâtiments de moins de 120 m² distants d'au plus 6 m forment des groupes par simple lien d'au plus 30 bâtiments. R3 (*habitants*) : les confirmations des habitants fusionnent ou séparent des concessions. Deux bâtiments principaux en tissu urbain ne sont jamais fusionnés sur la seule foi de leur forme : à la Médina ou à Pikine, des maisons mitoyennes sont des concessions distinctes. Une cité à un seul portail (SICAP, HLM, cités privées) est un *ensemble* : chaque maison garde sa propre adresse derrière le portail de la cité. Un regroupement ultérieur ne change jamais une adresse émise. Avant toute règle, les bâtiments dont le centre et les concessions dont l'entrée se trouvent à plus de 300 m au-delà de la frontière nationale sont écartés (section 4.2).

## Les profils de bâtiment

Chaque bâtiment du registre porte un profil : une classe d'usage selon une nomenclature sénégalaise (concession, maison basse, immeuble R+*n*, case et annexe pour l'habitat ; boutique, marché, bureaux, entrepôt, atelier et station pour le commerce ; administration, école, daara, université, hôpital, poste de santé et pharmacie pour les services publics ; mosquée, église et mausolée pour le culte ; quais de pêche, seccos et greniers, entre autres), une confiance associée à la classe, l'empreinte et le périmètre, les niveaux lorsqu'ils sont connus (notés RDC, R+1, R+2, comme à Dakar), la surface de plancher, ainsi que la source et la date de chaque attribut. Les classes sont déduites dans un ordre fixe : les étiquettes OpenStreetMap d'abord (confiance 0,85 à 0,9), puis les lieux cartographiés situés dans l'empreinte (0,6 à 0,7), puis la forme (0,2 à 0,5) ; les confirmations des habitants (0,95) priment sur toutes. Un daara n'est jamais déduit de la forme, car beaucoup de daaras sont des maisons familiales.

## L'adresse de l'État d'abord : le masque de couverture

Là où l'État donne déjà une adresse, N-Ways n'en crée pas de concurrente. La règle s'applique lieu par lieu, sous la forme d'un *masque de couverture* à trois niveaux. Un lieu est *municipal-officiel* lorsque le programme municipal d'adressage le couvre, sur l'une de ces trois preuves : un jeu de données officiel d'une commune, de l'ARTP ou de l'Agence de développement municipal ; au moins trois rues cartographiées portant des références du programme (1 601 rues de ce type sont cartographiées dans le pays) ; ou des plaques confirmées par les habitants à leurs portes. L'adresse affichée y est alors la rue et le numéro tels que la commune les écrit, par exemple « 120 Rue PE-44, Point E », et aucune plaque N-Ways n'est posée ; tant que le numéro officiel d'une porte n'est pas connu, l'adresse N-Ways s'affiche avec la mention « provisoire ». Un lieu est *ANN* dès que l'ANN publie des adresses pour lui, et l'adresse ANN s'affiche alors telle qu'elle est écrite. Tous les autres lieux sont *N-Ways*. Les codes postaux ne comptent pas comme couverture, puisque ce sont des zones de bureaux distributeurs, mais chaque concession porte son code postal lorsqu'il est connu.

Le masque ne fait que croître. Quand une couverture officielle atteint un lieu, ses adresses N-Ways cessent d'être principales mais restent valides comme alias renvoyant à l'adresse officielle, et aucun numéro n'est réattribué. Dans le registre émis, 112 lieux sont municipaux-officiels ; ils regroupent 128 950 concessions (3,6 % du pays et 44,0 % du département de Dakar), et le numéro de porte officiel est déjà connu pour 87 d'entre elles.

## Dire l'adresse

En français, le numéro se dit comme les numéros de maison et de téléphone : trois chiffres d'un bloc (« Affiniam, trois cent vingt »), quatre chiffres en deux paires (« Ouakam, vingt-cinq, douze ») et cinq chiffres en deux puis trois (« Médina, douze, cent quarante-neuf » pour 12 149). En wolof, les chiffres se disent un à un (« Ouakam, ñaar, juróom, benn, ñaar »). En wolof, 3 et 4 (*ñett*, *ñeent*) et 8 et 9 (*juróom ñett*, *juróom ñeent*) se ressemblent ; l'application relit donc toujours l'adresse et montre le bâtiment avant de guider. Les locuteurs du pulaar, du sérère, du diola, du mandingue et du soninké emploient le même nom de lieu et disent les chiffres en français ou en wolof, comme pour un numéro de téléphone.

# Mise en œuvre

## Le moteur de référence

Le moteur de référence (`engine/reference/sn_engine.py`, avec `plate_names.py`) est écrit en Python 3.9 avec la seule bibliothèque standard et n'a besoin que des fichiers de `model/`. Il met en œuvre toutes les formules de la section 4 : recherche de zone et cadres (éq. (1) et (2)), rattachement au lieu et noms de plaque (éq. (3) et (4)), clé de nom (éq. (5)), plages nationales (éq. (6) à (9)), numérotation de Hilbert et insertion (éq. (10) à (13)), décodage sans contexte (éq. (14)), lettre de contrôle (éq. (15)), codes de point et projection (éq. (16) et (17)) et regroupement des concessions (éq. (18)). Son autotest vérifie la projection, toutes les substitutions simples et inversions voisines de la lettre de contrôle sur des charges tirées au hasard, l'aller-retour des codes de point, la numérotation, douze décodages de noms homonymes et les vecteurs de test publiés. La description normative est la spécification `engine/SPEC.md`.

## Le registre

Le registre (`registry/`) publie chaque adresse émise, sans rien retenir : un fichier gzip par zone, une ligne par adresse, triées par famille de nom puis par numéro. Chaque ligne donne les formes machine, mémorisée et écrite ; le lieu, le numéro et la lettre de contrôle ; le statut (toute adresse est *provisoire* jusqu'à confirmation par les habitants) et la manière et la date d'émission ; l'entrée et son code de point ; la classe, l'usage, le type, le nombre de bâtiments et la surface de plancher de la concession ; le code postal là où il est cartographié ; et le niveau de couverture, avec l'adresse officielle là où la commune a numéroté la porte. Aucune ligne ne décrit les personnes qui habitent un logement. `lieux.csv` donne la liste figée des lieux avec leurs noms de plaque et officiels, leur clé, leur famille, leur longueur et leurs blocs. `anchors/` donne le centroïde de chaque concession en pleine précision, ligne à ligne avec les fichiers de zone : c'est le point selon lequel l'éq. (10) ordonne, et grâce à lui un déploiement indépendant numérote les nouvelles concessions exactement comme l'émetteur. Un manifeste donne les effectifs et l'empreinte SHA-256 de chaque fichier avant compression.

## Le serveur et son interface

`server/` est un service HTTP prêt à l'emploi, en Python avec la seule bibliothèque standard, qu'un ministère, un bureau de poste ou un développeur déploie avec `docker compose up`. Au premier démarrage, il importe le registre dans SQLite en vérifiant chaque fichier contre le manifeste et refuse toute discordance ; il sert ensuite une interface JSON sous `/v1` : état et informations, fiche complète d'une adresse, recherche par n'importe quelle forme (mémorisée, écrite, machine ou point, quels que soient les espaces, la casse ou les accents), concession située en un point et concessions voisines, vérification d'une forme machine, codage et décodage des codes de point, zones et lieux, et liste paginée des adresses d'une zone. Son export réécrit le registre au format publié, octet pour octet. Sur le seul déploiement que l'État ou N-WAYS LIMITED désigne comme émetteur, `POST /v1/codes` émet de nouvelles adresses selon les règles des sections 4.2 et 4.8 et `PATCH` les confirme, les retire ou les déplace. Tous les autres déploiements sont en lecture seule, car deux émetteurs travaillant sur le même registre verraient chacun le même numéro libre et le donneraient à deux concessions. L'interface est décrite dans `server/openapi.yaml` et, avec de vraies requêtes et réponses, dans `docs/api.md`.

## Conformité

Trois familles de tests rattachent les composants publiés à l'émetteur. Les vecteurs du moteur (`engine/reference/vectors.json`) fixent des codes de point, des lettres de contrôle, des nombres dits, des décodages de noms homonymes, des noms de plaque et des échantillons réels d'empreintes. Les 62 cas de parité du serveur (`server/testdata/parity.json`) consignent, pour de nouvelles concessions, des portes supplémentaires, des contours de toutes les classes de taille et des blocs d'extension, le lieu, le numéro, les formes et le profil produits par la propre mise en œuvre de l'émetteur sur un registre d'essai ; le serveur les reproduit tous. Sur le registre complet, un import suivi d'un export reproduit chaque fichier publié octet pour octet, et 59 adresses comparées champ par champ avec l'interface en service de l'émetteur n'ont montré aucune différence sur 1 416 champs.

## Obtenir et partager son adresse

Rien n'est demandé au ménage. Chaque concession déjà présente sur la carte a reçu son adresse lors de l'émission du registre, et l'application N-Ways l'affiche d'un geste (« Mon code »), en français ou en wolof : la concession où l'on se trouve, ou celle que l'on touche sur la carte. Le partage se fait d'un geste et envoie un message contenant l'adresse et un lien qui ouvre la carte sans l'application. Une maison absente de la carte s'ajoute en quatre étapes d'environ deux minutes (« Ajouter ma maison ») : la position du portail est moyennée sur dix secondes et photographiée depuis la rue ; le contour est tracé sur l'image, parcouru le long du mur avec la caméra du téléphone, ou importé d'un plan de bornage dont le système géodésique (Yoff, NSGD2004 ou WGS 84) doit être indiqué, avec son NICAD ou son numéro de lot de lotissement s'il y en a un ; le ménage indique le nombre de bâtiments et de niveaux et l'usage ; et le numéro libre entre les voisins est émis aussitôt, à titre provisoire. Un contour qui chevauche une concession existante est refusé, et le parcours rappelle, en français et en wolof, qu'une adresse n'est pas un titre foncier. Une adresse devient *confirmée* lorsque des habitants indépendants s'accordent à la dire juste, par le même consensus automatique qui corrige la carte ; personne ne relit les adresses à la main. Une plaque ou un autocollant QR sur le portail sert ceux qui n'ont pas de téléphone intelligent.

# Évaluation

Toutes les mesures de cette section sont calculées à partir du registre publié et du moteur de référence par `tools/paper-evaluation.py` ; les résultats figurent dans `docs/figures/data/evaluation.json`.

## Unicité et décodage

Les 3 597 128 formes machine sont toutes distinctes, de même que les 3 597 128 formes mémorisées une fois la casse et les accents repliés. Chaque forme mémorisée a été décodée par le moteur sans zone ni position (éq. (14)) : 3 597 128 se sont décodées exactement en la concession de la ligne du registre, aucune en une autre concession, aucune en plusieurs et aucune en rien. La proposition 1 se vérifie donc sur tout le registre.

## Longueurs

Parmi les numéros émis, 717 894 (20,0 %) ont trois chiffres, 1 676 892 (46,6 %) quatre et 1 202 342 (33,4 %) cinq. L'adresse mémorisée compte 13 caractères en médiane, espace compris ; 95 % des adresses ont au plus 18 caractères et 99 % au plus 20. La plus longue hors noms provisoires est « Yeumbeul Sud 20 699 » (19 caractères) ; avec les noms provisoires, c'est « Ancien Marché Hebdomadaire 22 199 » (33), un nom que sa commune doit raccourcir. Les numéros sont longs là où les points de lieux sont rares : à Touba, 83,9 % des concessions et, à Pikine, 87,0 % ont cinq chiffres (annexe A). Un travail sur les sous-quartiers avec les communes ramènerait beaucoup d'entre eux à quatre chiffres.

## Proximité

Sur l'ensemble des lieux, deux concessions de numéros consécutifs sont distantes de 23,4 m en médiane (80,8 m au 90^e^ centile), contre 561,4 m (1 912 m au 90^e^ centile) pour deux concessions du même lieu tirées au hasard. Les numéros suivent donc le terrain : le livreur qui trouve « Ouakam 2512 » trouvera « Ouakam 2515 » quelques portes plus loin.

## Erreurs

Nous avons appliqué toutes les substitutions d'un chiffre aux numéros de 100 000 adresses tirées au hasard, en conservant la longueur et un premier chiffre non nul, soit 3 621 599 numéros erronés. Leurs issues figurent ci-dessous.

| Issue d'une erreur d'un chiffre dans le numéro mémorisé | Part |
|:--|--:|
| Aucune adresse émise (hors de tout bloc, ou numéro libre d'un bloc) | 76,1 % |
| Une autre concession émise du même lieu | 22,6 % |
| Une concession émise d'un autre lieu du même nom | 1,3 % |

: Où mène une erreur d'un chiffre, sur 3 621 599 erreurs portant sur 100 000 adresses.

Les trois quarts des erreurs sont refusées parce que l'adresse n'existe pas. La plupart des autres mènent à une autre concession du même lieu ; l'application montre alors une photo, une classe et une rue que la personne ne reconnaît pas. Seules 1,3 % mènent dans une autre ville, et la ville s'affiche alors avant le guidage. Dans une forme machine, toutes ces erreurs sont refusées : sur le même échantillon, la lettre de contrôle a détecté les 9 000 000 de substitutions simples et les 800 830 inversions de chiffres voisins différents, comme l'exige la proposition 2.

Le chiffre de 22,6 % est le pendant empirique d'une estimation simple. Si un bloc contient $n$ numéros émis parmi $b$, un numéro du bloc tiré uniformément est émis avec la probabilité

$$
P(\text{atteinte}) \approx \frac{n}{b} \approx \frac{1}{3},
\tag{19}
$$

d'après l'éq. (6). La part mesurée est plus faible parce que les erreurs sur les premiers chiffres sortent du bloc.

## Codes de point

Pour 400 points tirés au hasard dans chacun des 46 cadres de zone (18 400 points), la distance entre un point et le centre décodé de sa maille n'a jamais dépassé la borne $s\sqrt 2 / 2$ de l'éq. (16) ; le plus grand rapport de l'erreur à la borne a été de 0,997.

## Couverture

Chaque concession de la carte du bâti située dans la frontière nationale a reçu une adresse : la couverture est complète par construction. Aucune entrée émise ne se trouve à plus de 300 m au-delà de la frontière : mesurées sur le tracé complet de la frontière, deux se trouvent au-delà, toutes deux de moins d'un mètre. Deux réserves s'imposent. D'abord, le bâti cartographié est lui-même incomplet, surtout pour les constructions récentes ; « Ajouter ma maison » et la règle d'insertion de l'éq. (13) existent pour cette raison. Ensuite, les entrées sont connues pour peu de concessions : 142 adresses mènent à un portail cartographié et les autres au centre de la concession jusqu'à ce qu'un portail soit confirmé.

## Mêmes noms, lieux différents

Le tableau ci-dessous montre le décodage d'adresses réellement émises portant un nom répété, le lieu étant indiqué par sa zone et son indice. Chacune se décode à partir du seul texte. La dernière colonne donne une erreur d'un chiffre qui tombe dans le bloc d'un autre lieu du même nom : dans une forme machine, la lettre de contrôle la refuse, et dans la forme dite, l'application montre l'autre ville. Pour HLM, le numéro de secteur la refuse aussi.

| Mémorisée | Lieu | Bloc | Forme machine | Erreur vers |
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

: Mêmes noms, lieux différents : adresses réellement émises, décodées sans contexte.

Les deux dernières lignes montrent une paire que seul le raccourcissement a réunie : « Mbenguène Diawar », à Kébémer, a pour nom de plaque « Diawar », comme le village de Diawar à Dagana, et les deux partagent désormais une plage en deux blocs.

# Conceptions étudiées et écartées

Le modèle est l'aboutissement de plusieurs variantes, chacune mesurée sur la même carte du bâti avant d'être retenue ou écartée.

| Variante | Exemple | Appréciation |
|:--|:--|:--|
| Code de grille alphanumérique | `DKR 45 12 78 K` | dix symboles, dont quatre lettres ; en français, les noms de lettres riment (bé, cé, dé, gé, pé, té, vé) et G et J se confondent ; gardé seulement pour les codes de point, rarement mémorisés |
| Code national tout en chiffres | `07 0080 4512` | dix chiffres qui ne disent rien à leur porteur ; une erreur mène à un vrai logement n'importe où dans le pays |
| Open Location Code | `7C2P+M4 Dakar` | des lettres et un signe plus ; change tous les quelques mètres dans une même concession ; non lié à un portail ; gardé comme renvoi |
| Lieu et numéro, la zone distinguant les homonymes | `Médina 150, Ziguinchor` | une adresse qui a besoin de sa ville n'est pas unique, puisque la ville ne se dit pas ; écartée |
| Une plage de numéros par lieu | `Médina 150` dans chaque Médina | deux logements de même adresse dite ; écartée |
| Noms officiels complets | `Keur Serigne Ablaye Yakhine 2 345` | trop longs à dire ou à écrire sur un colis |
| Nom de plaque et une plage nationale par nom | **`Ouakam 2512`** | **retenue** |

: Les formes étudiées.

La figure 7 donne le coût en chiffres des trois numérotations. Une plage par lieu donne les numéros les plus courts (29,7 % des concessions à trois chiffres), mais ses adresses ne sont uniques qu'avec la zone. Une plage par nom avec les noms officiels complets allonge légèrement les numéros (22,8 % à trois chiffres) et rend les adresses uniques. Le passage aux noms de plaque réunit davantage de lieux sous un même nom et allonge encore un peu les numéros (20,0 % à trois chiffres), mais l'adresse devient assez courte pour être dite. Nous avons jugé ce chiffre de plus un prix raisonnable : un chiffre se retient plus facilement qu'une ville après une virgule que personne ne prononce, et c'est lui qui fait que « Médina 12 149 » désigne Dakar où qu'on le dise.

![Part des concessions selon le nombre de chiffres du numéro, pour les trois numérotations, mesurée sur les mêmes concessions. La numérotation retenue est la dernière ligne. Source : `model/name-families.json`.](figures/number-lengths.fr.svg)

Pour le caractère de contrôle, nous avons comparé MOD 11-2 de l'ISO/IEC 7064, qui exige un onzième symbole, au chiffre de contrôle décimal de Damm, qui détecte les mêmes erreurs avec dix [@damm2007]. Une lettre convient mieux au Sénégal : un chiffre de contrôle accolé à un nombre se lit facilement comme en faisant partie, alors qu'une lettre tirée d'un ensemble fixe de onze se distingue à l'œil, et MOD 11-2 est une norme internationale largement employée. Nous avons choisi les lettres pour des oreilles francophones, comme le décrit la section 4.10. Pour l'ordre dans un lieu, nous avons préféré la courbe de Hilbert à une numérotation ligne par ligne ou en Z (ordre de Morton) en raison de sa meilleure proximité [@moon2001], ce que la section 6.3 confirme sur le registre.

# Bénéfices pour les citoyens

Pour une famille de Pikine, de Touba ou d'un village de Kolda, une adresse change quatre choses ordinaires.

**Être trouvé.** Aujourd'hui, un visiteur, un taxi ou un livreur est guidé au téléphone, de repère en repère. Avec une adresse, la personne dit une courte phrase, « Ouakam, vingt-cinq, douze », et l'application mène au portail.

**Justifier de son domicile.** Banques, agents de mobile money, écoles, employeurs et administrations demandent une adresse vérifiable. Avant le registre, presque aucun ménage ne pouvait en donner une :

| | Concessions | Part |
|:--|--:|--:|
| Avec un numéro de porte officiel connu | 87 | 0,002 % |
| Dans les quartiers du programme municipal d'adressage | 128 950 | 3,6 % |
| Avec une adresse qui se dit et se vérifie | 3 597 128 | 100 % |

: Les concessions selon le type d'adresse dont elles disposent.

**Recevoir biens et services.** Les familles de la diaspora, les boutiques en ligne et les compagnies d'eau et d'électricité peuvent envoyer à une adresse plutôt qu'à une description, et un ménage peut demander un branchement, un relevé de compteur ou une réparation au bon portail.

**Simplicité.** L'adresse est gratuite, ne demande aucun document et ne contient aucune donnée personnelle (section 12). Ce n'est pas un titre foncier, et l'application le dit.

Le bénéfice est le plus grand pour ceux qui ont le moins aujourd'hui : les 96 % de concessions situées hors des quartiers adressés, les familles des extensions denses de Touba et de Pikine, les villages du *domaine national* où personne ne détient de parcelle immatriculée, et les habitants qui lisent peu, pour qui un quartier connu et un numéro sont plus simples que des lettres. Nous ne disposons pas encore d'une mesure du temps que les ménages passent à indiquer leur chemin, et la section 13 expose comment le mesurer.

# Logistique et commerce

Au Sénégal, la livraison passe par le téléphone. Le livreur atteint le quartier, appelle le client, se fait guider, rappelle souvent et renonce parfois. Ce qu'une adresse apporte à une entreprise de logistique, c'est une clé stable pour la concession de chaque client, un guidage jusqu'au portail préparé avant le départ, une saisie vérifiée au moment de la commande plutôt que sur la route (dans les formes machine, la lettre de contrôle détecte tout chiffre erroné), le code postal pour le tri du courrier, et un accès ouvert : un transporteur, une boutique, une banque ou une fintech peut résoudre les adresses dans ses propres systèmes, hors ligne, sans rien payer à personne.

*Estimation.* Nous modélisons l'économie pour 1 000 tentatives de livraison par

$$
S = 1\,000 \times f_0 \times \theta \times c ,
\tag{20}
$$

où $f_0$ est la part des premières tentatives qui échouent aujourd'hui, $\theta$ la fraction de ces échecs qu'une adresse précise élimine, et $c$ le coût d'une tentative. Aucune étude publiée ne mesure ces grandeurs au Sénégal ; nous les tirons donc d'estimations de praticiens pour Dakar et en donnons les fourchettes. Les taux d'échec à la première tentative avancés sont de 8 à 12 % au centre de Dakar et de 12 à 15 % en périphérie [@bah2026b], et de 22 à 30 % pour les livraisons vers des lieux sans adresse formelle [@bah2026a]. Parmi les échecs de livraison contre paiement à Dakar, une adresse incomplète est invoquée dans 22 % des cas et un client injoignable dans 28 % [@bah2026c]. Une course en moto coûte de 1 000 à 1 500 FCFA au centre et de 1 500 à 2 500 FCFA en périphérie [@bah2026b]. Nous retenons $f_0 \in [0{,}08\,;\,0{,}30]$, $\theta \in [0{,}22\,;\,0{,}50]$ (de la seule part imputée à l'adresse jusqu'à la moitié des échecs, puisqu'une adresse abrège aussi les appels qu'occasionne un client injoignable) et $c \in [1\,000\,;\,2\,500]$ FCFA.

| $f_0$ | $\theta$ | $c$ (FCFA) | $S$ pour 1 000 tentatives (FCFA) |
|--:|--:|--:|--:|
| 0,08 | 0,22 | 1 000 | 17 600 |
| 0,15 | 0,30 | 1 750 | 78 750 |
| 0,30 | 0,50 | 2 500 | 375 000 |

: Économie pour 1 000 tentatives de livraison, éq. (20) : hypothèses basse, centrale et haute.

L'hypothèse centrale correspond à environ 79 FCFA par tentative, soit 4,5 % de son coût. La fourchette couvre plus d'un ordre de grandeur, ce qui est en soi le principal enseignement : l'économie dépend de la fréquence des échecs dus au manque de localisation, que la section 13 propose de mesurer avec des transporteurs partenaires. Ces estimations proviennent de sources commerciales sans méthode publiée et doivent être lues comme indicatives.

Deux situations sénégalaises illustrent l'usage. Touba accueille un très grand nombre de pèlerins pour le Grand Magal ; hôtes, commerçants et transporteurs peuvent donner une adresse à des concessions qui n'ont pas de nom de rue. Les marchés, grossistes et gares routières de Dakar, Thiès et Kaolack peuvent envoyer des marchandises à la bonne concession d'un village plutôt qu'à la ville la plus proche. Les hôtels et locations de la Petite Côte, de Saint-Louis et de Casamance peuvent donner à leurs hôtes une adresse pour le chauffeur.

# Services d'urgence

Une ambulance, les sapeurs-pompiers ou la police affrontent le problème du livreur avec un enjeu plus grave. Une étude qualitative des services médicaux d'urgence de Kigali a montré que la localisation du patient dépendait d'outils inadaptés, de la connaissance du terrain des appelants et des équipages, et d'appels répétés entre appelant, régulateur et ambulance, ce qui allongeait les délais d'intervention [@hunt2024]. Nous ne connaissons aucune mesure publiée pour le Sénégal, ce qui est en soi une raison d'en entreprendre une.

Avec une adresse, l'appelant dit une phrase : « Médina, douze, cent quarante-neuf ». Le régulateur la saisit et le registre renvoie une concession, sa ville et son portail : il n'y a pas de liste de Médinas, car le numéro à lui seul indique qu'il s'agit de celle de Dakar (proposition 1). Le régulateur relit l'adresse, et une erreur qui mène à un autre lieu du même nom affiche « Saint-Louis » au lieu de « Dakar », ce que l'appelant corrige aussitôt. L'équipage se rend au portail, dont les coordonnées sont données sur la grille UTM fuseau 28N qu'utilisent les géomètres sénégalais et de nombreux SIG. Le moteur et le registre fonctionnent sans réseau : un système de régulation peut résoudre les adresses même quand la ligne est coupée.

*Estimation.* Larsen et ses collègues ont modélisé la survie après un arrêt cardiaque extrahospitalier par

$$
S_{\text{ACEH}} = 67 - 2{,}3\,t_{\text{RCP}} - 1{,}1\,t_{\text{défib}} - 2{,}1\,t_{\text{RCS}} \quad \text{(pour cent, temps en minutes)},
\tag{21}
$$

où les trois temps sont les délais entre l'effondrement et la réanimation cardio-pulmonaire, la défibrillation et la réanimation spécialisée [@larsen1993]. Lorsqu'un même équipage apporte les trois, un retard $\Delta t$ pour trouver le portail retarde les trois délais et coûte $(2{,}3 + 1{,}1 + 2{,}1)\,\Delta t = 5{,}5\,\Delta t$ points de survie : environ 5,5 points pour une minute, 11 pour deux et 27,5 pour cinq. Le modèle a été ajusté dans le comté de King (État de Washington) ; il donne un ordre de grandeur pour le Sénégal, non une prévision, et, modèle linéaire, il ne vaut que tant que la survie prédite reste positive. Son sens, en revanche, ne fait pas de doute : là où trouver le portail prend des minutes, une adresse qui supprime la recherche compte autant qu'un véhicule plus rapide.

# Coordination et planification de l'État

Une adresse est une clé partagée. Quand ministères, communes, concessionnaires de services et institut statistique désignent une concession par la même adresse, leurs fichiers peuvent être rapprochés sans comparer des noms et des descriptions.

**Une référence pour tous les services.** L'expérience sénégalaise en montre l'intérêt. L'étude de la Banque mondiale relève qu'un répertoire d'adresses fournit en général une liste des activités économiques plus complète que celle des services fiscaux et révèle qui manque aux rôles ; le programme sénégalais a mis ce rapprochement à l'essai à Thiès et à Kaolack [@farvacque2005]. La fiche d'une concession porte le code postal, l'adresse municipale officielle là où elle existe et, dès qu'il existera, l'identifiant ANN : chaque service garde ses propres fichiers et s'accorde pourtant sur la concession.

**Ce qu'aurait coûté une numérotation des portes.** Au coût moyen de l'adressage classique dans les villes africaines relevé par la Banque mondiale [@farvacque2005],

$$
C = N \times c_{\text{porte}} = 3\,597\,128 \times 5{,}7\ \text{USD} \approx 20{,}5 \text{ millions USD (prix de 2005)},
\tag{22}
$$

où $N$ est le nombre de concessions et $c_{\text{porte}}$ le coût par porte adressée. Au coût par porte le plus élevé de la même étude, 7,6 USD, le montant atteindrait 27,3 millions USD. La comparaison donne l'ordre de grandeur de l'adressage classique, non une économie : plaques et noms de rues gardent leur valeur, et là où une commune numérote ses rues, ses numéros s'affichent en premier et les adresses N-Ways deviennent des alias (section 4.14).

**Planifier avec des effectifs réels.** Le registre dénombre les concessions par zone, par lieu et par classe de bâtiment, et chaque effectif peut être recalculé à partir des fichiers ouverts. Le département de Dakar compte 107 430 adresses et Touba-Mbacké (Ndame) 289 328, davantage que la plupart des régions.

**Accès aux services.** Les distances à vol d'oiseau entre un échantillon de 20 000 concessions et l'équipement le plus proche cartographié dans la carte de base N-Ways figurent ci-dessous. La couche des équipements ne fait pas partie du dépôt publié, et ces chiffres décrivent la carte, non le terrain : écoles, daaras et postes non cartographiés allongent les distances apparentes. Un ministère peut substituer sa propre liste d'équipements et recalculer le tableau en quelques minutes à partir du registre.

| Équipement | À moins de 2 km | À moins de 5 km | Distance médiane |
|:--|--:|--:|--:|
| Structure de santé (hôpital, centre, poste de santé) | 53,1 % | 74,5 % | 1,74 km |
| École | 43,3 % | 59,4 % | 3,10 km |
| Police ou gendarmerie | 22,4 % | 35,0 % | 12,57 km |
| Pharmacie | 32,7 % | 44,0 % | 7,30 km |

: Distance des concessions à l'équipement cartographié le plus proche (échantillon de 20 000 concessions).

**Recensements et enquêtes.** Le recensement de 2023 a dénombré 18,1 millions de résidents [@ansd2024]. Les 3,6 millions de concessions du registre, chacune dotée d'un code stable, offrent aux équipes d'enquête une base où tirer un échantillon et où revenir ; une enquête qui consigne l'adresse de chaque entretien peut être cartographiée et rapprochée des services sans conserver de nom.

**Foncier.** Une adresse n'est pas un titre. Le registre peut néanmoins porter le NICAD d'une parcelle, afin que le cadastre, le PROCASEF et les communes retrouvent la concession et le portail d'une parcelle immatriculée.

**Croissance.** Les nouvelles concessions reçoivent une adresse dès leur apparition (éq. (13)). Le registre montre ainsi où le Sénégal grandit, mois après mois : les extensions de Touba, de Keur Massar et de Diamniadio sont là où il faudra demain des routes, de l'eau, des écoles et des postes de santé.

# Vie privée, sécurité et gouvernance

**Des lieux, jamais des personnes.** Les adresses décrivent des lieux. Les concessions d'habitation ne portent aucune donnée sur leurs occupants : ni nom, ni numéro de téléphone, ni composition du ménage. Le nombre de ménages n'est conservé que sous la forme « un, plusieurs ou non précisé » et n'est jamais affiché. Sont publics les positions, les contours, les classes, les tailles, les statuts, la position des portails, le nom des entreprises et des bâtiments publics, et les plaques de rue. Les photos prises dans « Ajouter ma maison » ne servent qu'à la vérification et ne sont pas publiées, et un ménage peut demander qu'une porte soit masquée. Un partenaire ne voit l'adresse d'un client qu'avec le consentement de celui-ci.

**Le droit.** La loi sénégalaise 2008-12 et son décret d'application 2008-721 s'appliquent : la Commission de protection des données personnelles (CDP) doit recevoir une déclaration avant le début du traitement, la géolocalisation relève de la déclaration normale, et les transferts de données hors du Sénégal sont soumis à son autorisation [@loi2008]. L'Acte additionnel de la CEDEAO relatif à la protection des données à caractère personnel fixe le cadre régional [@ecowas2010]. Un projet de loi remplaçant celle de 2008 et créant une nouvelle autorité est en préparation depuis 2019 ; nous n'avons trouvé aucune trace de son adoption en octobre 2026. La CDP a pris part à l'atelier de relance de l'ANN.

**Ouverture et sécurité.** Le registre est publié en entier, sans rien retenir, et il ne contient aucune information sur les personnes qui habitent un logement.

**Gouvernance.** N-WAYS LIMITED maintient le modèle et en est, pour l'heure, l'unique émetteur, afin qu'aucun numéro ne soit donné deux fois. Les zones, les adresses émises, les blocs de la plage de chaque nom, la grille des points et la méthode de contrôle ne changent jamais ; les profils de bâtiment évoluent avec les preuves ; les noms de plaque en attente du choix d'une commune peuvent changer une fois. Le dépôt est conçu pour être remis en entier, avec son registre, son moteur et ses règles, à l'ANN ou à un organisme qu'elle désigne. Si l'ANN entre en service, son adresse s'affiche en premier et l'adresse N-Ways devient un renvoi. Les désaccords sur les regroupements se règlent par l'accord des habitants ; les litiges fonciers ne se règlent jamais par une adresse. Les règles de modification et de remise figurent dans `GOVERNANCE.md`.

# Limites et travaux futurs

**L'inventaire des lieux provient de cartes ouvertes.** Les points de lieux d'OpenStreetMap et de GeoNames sont inégaux : denses dans une partie de Dakar et de Ziguinchor, rares dans les quartiers de Touba et dans bien des villages. Certains lieux sont donc trop grands, ce qui allonge leurs numéros, et certains noms sont mal orthographiés. Le travail avec les communes ajoute des alias et corrige des noms de plaque, sans jamais changer un numéro émis.

**De nombreux noms de plaque sont provisoires.** 3 116 lieux, environ un cinquième, attendent le choix de leur commune ; ce sont surtout des villages portant le nom d'une personne et des noms à qualificatif ethnique ou d'orientation ; 739 058 adresses portent un tel nom. Seules trois formes courtes sont attestées par écrit ; « Parcelles » pour Parcelles Assainies, courant à l'oral, attend la commune.

**Le repli des noms relève du jugement.** La normalisation de l'éq. (5) est volontairement généreuse, mais une graphie qu'elle ne replie pas, comme une translittération rare ou un nom écrit selon l'orthographe du pulaar ou du diola, ouvre une plage à part. Ces graphies s'ajoutent comme alias ; des blocs ne sont jamais fusionnés.

**Les concessions sont déduites.** Peu de murs sont cartographiés ; la plupart des regroupements reposent donc sur les règles de forme de l'éq. (18) et seront faux pour certaines parcelles jusqu'à correction par les habitants. Le registre publié contient les entrées et les centroïdes, non les empreintes ; un déploiement indépendant applique donc les contrôles de doublons sur la seule base des distances aux entrées.

**Les attributs sont minces.** Les hauteurs sont presque partout inconnues, et hors des villes les classes sont des hypothèses peu sûres tant que les habitants ou les partenaires ne les ont pas confirmées.

**Les limites.** Les zones reprennent les contours départementaux de 2019 et ne distinguent pas Keur Massar ; elles sont figées à dessein.

**Les systèmes extérieurs.** La liste des localités de La Poste ne sera utilisée qu'avec l'accord de La Poste, puisqu'elle ne porte aucune licence. Les renvois devront peut-être s'adapter quand l'ANN publiera son format. Nous n'avons pu vérifier ni le système géodésique imposé aujourd'hui aux titres, ni la loi qui encadre la profession de géomètre-expert, ni l'état du projet de loi de 2019 sur les données personnelles.

**Ce que nous mesurerons.** Les estimations des sections 9 et 10 reposent sur peu de données locales. Nous proposons les mesures suivantes, à convenir avec des partenaires :

| Mesure | Méthode | Objectif |
|:--|:--|:--|
| Mémorisation de sa propre adresse après un mois | habitants interrogés sans l'application | au moins 80 % exactes |
| Réussite de la première tentative de livraison | transporteurs partenaires, avec et sans adresse | au moins 20 points de plus avec |
| Temps entre l'arrivée dans le quartier et le portail | horodatage de l'application du livreur | divisé par deux |
| Portails et portes confirmés | habitants et livreurs | 10 000 |
| Temps de localisation des appels d'urgence | avec un service d'ambulance ou de pompiers volontaire | mesuré, puis divisé par deux |

: Mesures proposées pour la première année.

# Conclusion

Une adresse nationale n'a pas besoin que les rues soient nommées ni les portes levées pour exister. En associant un nom de lieu déjà en usage à un numéro court tiré d'une plage nationale unique par nom, chaque concession du Sénégal peut porter une adresse assez courte pour être dite, unique sans contexte, ordonnée sur le terrain, stable et ouverte. Le registre émis selon ce modèle compte 3 597 128 adresses ; chacune se décode en une seule concession à partir de sa seule forme dite, ses numéros suivent le terrain, et une lettre de contrôle que personne n'a à voir protège la forme machine. Le modèle affiche l'adresse de l'État en premier partout où elle existe et est conçu pour être absorbé par l'Adressage Numérique National. Ses principales limites, l'inventaire inégal des lieux, les noms de plaque provisoires et les concessions déduites, se corrigent chacune sans renumérotation, par les communes, par les habitants et par l'ANN.

# Disponibilité des données et du code {-}

La spécification, le moteur de référence, le registre, les fichiers du modèle, le serveur et le présent article sont publiés à l'adresse <https://github.com/n-ways/open-addresses-senegal> [@nways2026]. Le code est sous licence Apache 2.0, les données sous Open Database License 1.0 et les documents sous CC BY 4.0. Mention de crédit : « N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng) ». Chaque figure et chaque mesure de la section 6 se reproduit avec `tools/paper-figures.py` et `tools/paper-evaluation.py` ; les PDF se construisent avec `sh docs/paper/build.sh`.

# Remerciements {-}

Le registre repose sur le travail des contributeurs d'OpenStreetMap qui ont cartographié les bâtiments et les lieux du Sénégal, notamment à Sédhiou, à Kolda et à Matam, où ils ont tracé la plupart des empreintes ; sur les empreintes de bâtiments publiées par Google et Microsoft et diffusées par la fondation Overture Maps ; sur les limites de geoBoundaries et du Gouvernement du Sénégal ; et sur GeoNames. Nous remercions La Poste Sénégal, l'ANSD et les cellules municipales d'adressage, dont les travaux publiés ont rendu cette étude possible.

# Références {-}

::: {#refs}
:::

# Annexe A. Les 46 zones de code {-}

| # | Clé | Zone | Région | Cadre (km) | Maille (m) | Point | Lieux | Adresses | 3 (%) | 4 (%) | 5 (%) |
|--:|:--|:--|:--|--:|--:|:-:|--:|--:|--:|--:|--:|
| 0 | BIG | Bignona | Ziguinchor | 98 | 10 | 4+4 | 595 | 65 019 | 41,9 | 42,4 | 15,8 |
| 1 | BKL | Bakel | Tambacounda | 199 | 10 | 5+5 | 219 | 41 737 | 23,8 | 59,4 | 16,8 |
| 2 | BMB | Bambey | Diourbel | 49 | 5 | 4+4 | 489 | 83 034 | 28,3 | 58,9 | 12,8 |
| 3 | BNK | Bounkiling | Sédhiou | 84 | 10 | 4+4 | 253 | 36 264 | 39,6 | 42,7 | 17,7 |
| 4 | BRK | Birkelane | Kaffrine | 59 | 10 | 4+4 | 202 | 33 656 | 33,6 | 62,6 | 3,8 |
| 5 | DAG | Dagana | Saint-Louis | 123 | 10 | 5+5 | 235 | 89 049 | 12,4 | 60,7 | 26,9 |
| 6 | DBL | Diourbel | Diourbel | 55 | 10 | 4+4 | 425 | 68 418 | 32,4 | 24,4 | 43,3 |
| 7 | DKR | Dakar | Dakar | 16 | 2 | 4+4 | 112 | 107 430 | 1,2 | 62,7 | 36,1 |
| 8 | FDG | Foundiougne | Fatick | 73 | 10 | 4+4 | 416 | 79 408 | 25,8 | 59,3 | 14,9 |
| 9 | FTK | Fatick | Fatick | 86 | 10 | 4+4 | 461 | 101 628 | 27,5 | 55,8 | 16,7 |
| 10 | GDW | Guédiawaye | Dakar | 8 | 1 | 4+4 | 11 | 23 425 | 0,8 | 25,2 | 73,6 |
| 11 | GMP | Goudomp | Sédhiou | 93 | 10 | 4+4 | 225 | 27 865 | 40,8 | 57,0 | 2,2 |
| 12 | GNG | Guinguinéo | Kaolack | 49 | 5 | 4+4 | 221 | 39 809 | 28,2 | 44,9 | 26,9 |
| 13 | GOS | Gossas | Fatick | 83 | 10 | 4+4 | 291 | 30 827 | 43,7 | 42,8 | 13,5 |
| 14 | GRY | Goudiry | Tambacounda | 164 | 10 | 5+5 | 424 | 35 962 | 43,3 | 55,4 | 1,6 |
| 15 | KAF | Kaffrine | Kaffrine | 94 | 10 | 4+4 | 294 | 75 331 | 15,5 | 52,0 | 32,4 |
| 16 | KAO | Kaolack | Kaolack | 77 | 10 | 4+4 | 468 | 129 054 | 19,2 | 42,6 | 38,3 |
| 17 | KBM | Kébémer | Louga | 109 | 10 | 5+5 | 639 | 94 438 | 35,7 | 45,8 | 18,5 |
| 18 | KDG | Kédougou | Kédougou | 167 | 10 | 5+5 | 176 | 47 506 | 17,9 | 16,5 | 65,8 |
| 19 | KGH | Koungheul | Kaffrine | 104 | 10 | 5+5 | 309 | 48 680 | 29,0 | 51,3 | 19,7 |
| 20 | KLD | Kolda | Kolda | 116 | 10 | 5+5 | 515 | 72 605 | 34,5 | 25,3 | 40,3 |
| 21 | KNL | Kanel | Matam | 134 | 10 | 5+5 | 189 | 66 004 | 16,9 | 73,4 | 9,7 |
| 22 | KPT | Koumpentoum | Tambacounda | 128 | 10 | 5+5 | 269 | 40 224 | 29,0 | 58,2 | 12,9 |
| 23 | KTF | Kaël-Taïf | Diourbel | 72 | 10 | 4+4 | 237 | 22 957 | 41,5 | 53,5 | 5,2 |
| 24 | LGA | Louga | Louga | 109 | 10 | 5+5 | 716 | 131 320 | 27,0 | 46,5 | 26,6 |
| 25 | LNG | Linguère | Louga | 155 | 10 | 5+5 | 560 | 96 934 | 34,5 | 49,7 | 15,9 |
| 26 | MAT | Matam | Matam | 118 | 10 | 5+5 | 208 | 77 460 | 13,4 | 70,1 | 16,6 |
| 27 | MBR | Mbour | Thiès | 72 | 10 | 4+4 | 438 | 205 416 | 11,6 | 35,0 | 53,4 |
| 28 | MHD | Malem Hodar | Kaffrine | 81 | 10 | 4+4 | 157 | 25 139 | 28,5 | 67,0 | 4,5 |
| 29 | MYF | Médina Yoro Foulah | Kolda | 115 | 10 | 5+5 | 463 | 54 533 | 35,0 | 57,7 | 7,3 |
| 30 | NRP | Nioro du Rip | Kaolack | 92 | 10 | 4+4 | 524 | 103 624 | 25,8 | 60,1 | 14,1 |
| 31 | OUS | Oussouye | Ziguinchor | 39 | 5 | 4+4 | 70 | 16 172 | 21,0 | 70,0 | 9,0 |
| 32 | PKN | Pikine–Keur Massar | Dakar | 16 | 2 | 4+4 | 39 | 123 594 | 0,0 | 13,0 | 87,0 |
| 33 | POD | Podor | Saint-Louis | 186 | 10 | 5+5 | 364 | 91 267 | 21,3 | 74,6 | 4,2 |
| 34 | RAN | Ranérou-Ferlo | Matam | 155 | 10 | 5+5 | 131 | 32 597 | 22,4 | 73,4 | 4,3 |
| 35 | RUF | Rufisque | Dakar | 34 | 5 | 4+4 | 119 | 158 721 | 1,6 | 43,0 | 55,5 |
| 36 | SED | Sédhiou | Sédhiou | 100 | 10 | 4+4 | 211 | 32 322 | 35,7 | 42,7 | 21,6 |
| 37 | SLM | Salémata | Kédougou | 81 | 10 | 4+4 | 97 | 5 839 | 72,3 | 27,8 | 0,0 |
| 38 | SRY | Saraya | Kédougou | 126 | 10 | 5+5 | 152 | 45 759 | 13,8 | 48,0 | 38,2 |
| 39 | STL | Saint-Louis | Saint-Louis | 47 | 5 | 4+4 | 194 | 73 706 | 11,0 | 66,8 | 22,3 |
| 40 | TBA | Touba-Mbacké (Ndame) | Diourbel | 49 | 5 | 4+4 | 241 | 289 328 | 3,0 | 13,1 | 83,9 |
| 41 | TBC | Tambacounda | Tambacounda | 215 | 10 | 5+5 | 674 | 100 102 | 26,4 | 30,4 | 43,2 |
| 42 | THS | Thiès | Thiès | 63 | 10 | 4+4 | 485 | 175 645 | 13,3 | 62,9 | 23,9 |
| 43 | TIV | Tivaouane | Thiès | 101 | 10 | 5+5 | 822 | 144 845 | 25,8 | 57,2 | 17,0 |
| 44 | VEL | Vélingara | Kolda | 99 | 10 | 4+4 | 460 | 104 269 | 24,9 | 35,4 | 39,7 |
| 45 | ZIG | Ziguinchor | Ziguinchor | 72 | 10 | 4+4 | 197 | 48 206 | 12,5 | 69,4 | 18,1 |

: Les 46 zones de code : indice, clé, côté du cadre, maille et nombre de chiffres par axe des codes de point (éq. (2)), lieux, adresses émises, et part des concessions dont le numéro a 3, 4 ou 5 chiffres. Sources : `model/zones.json`, `model/lieux-stats.json`, `registry/MANIFEST.json`.
