#!/usr/bin/env python3
"""Print the statistics tables used in docs/model.md and the papers
(English and French) from model/building-stats.json, model/lieux-stats.json
and model/name-families.json.

  tools/stats-tables.py en|fr
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, '..', 'model')
b = json.load(open(os.path.join(M, 'building-stats.json')))
l = json.load(open(os.path.join(M, 'lieux-stats.json')))
nf = json.load(open(os.path.join(M, 'name-families.json')))['summary']
lang = sys.argv[1] if len(sys.argv) > 1 else 'en'
FR = lang == 'fr'
REG = {'SN-DK': 'Dakar', 'SN-TH': 'Thiès', 'SN-DB': 'Diourbel', 'SN-FK': 'Fatick', 'SN-KL': 'Kaolack',
       'SN-KA': 'Kaffrine', 'SN-LG': 'Louga', 'SN-SL': 'Saint-Louis', 'SN-MT': 'Matam', 'SN-TC': 'Tambacounda',
       'SN-KE': 'Kédougou', 'SN-KD': 'Kolda', 'SN-SE': 'Sédhiou', 'SN-ZG': 'Ziguinchor'}
G = ['residential', 'commercial', 'government', 'education', 'health', 'religious', 'hospitality', 'unknown']
GFR = {'residential': 'habitat', 'commercial': 'commerce', 'government': 'administration', 'education': 'enseignement',
       'health': 'santé', 'religious': 'culte', 'hospitality': 'hôtellerie', 'unknown': 'inconnu'}


def n(x, d=0):
    s = f'{x:,.{d}f}'
    return s.replace(',', ' ').replace('.', ',') if FR else s


def pct(x):
    return (n(100 * x, 1) + ' %') if FR else f'{100 * x:.1f}%'


regs = b['regions']
tot = sum(r['structures'] for r in regs.values())
comp = sum(r['compounds'] for r in regs.values())
print(('**Par région.** ' if FR else '**By region.** ') + (
    f"{n(tot)} empreintes regroupées en {n(comp)} concessions." if FR else
    f"{n(tot)} footprints grouped into {n(comp)} compounds."))
print()
hdr = (['Région', 'Empreintes', 'Concessions', 'Dans une concession à plusieurs bâtiments', 'Emprise médiane (m²)']
       + [GFR[g] for g in G[:-1]] + ['inconnu'] if FR else
       ['Region', 'Footprints', 'Compounds', 'In multi-structure compounds', 'Median footprint (m²)'] + G)
print('| ' + ' | '.join(hdr) + ' |')
print('|' + '---|' * len(hdr))
for code, r in sorted(regs.items(), key=lambda kv: -kv[1]['structures']):
    row = [REG.get(code, code), n(r['structures']), n(r['compounds']), pct(r['shareInMultiStructureCompounds']),
           n(r['footprintM2'].get('median', 0))] + [pct(r['groups'].get(g, 0)) for g in G]
    print('| ' + ' | '.join(row) + ' |')
print()
for z in ('DKR', 'TBA'):
    d = b['detail'].get(z)
    zs = b['zones'].get(z)
    if not d:
        continue
    name = {'DKR': 'Dakar (département)', 'TBA': 'Touba-Mbacké (Ndame)'}[z]
    print(f'**{name}.** ' + (
        f"{n(zs['structures'])} empreintes, {n(zs['compounds'])} concessions ; {pct(zs['shareInMulti'])} des empreintes "
        f"sont dans une concession à plusieurs bâtiments ; portail connu pour {pct(zs['shareCompoundsWithKnownGate'])} "
        f"des concessions ({n(zs['compoundsWithKnownGate'])}). Tissu urbain : {pct(zs['urbanShare'])}." if FR else
        f"{n(zs['structures'])} footprints, {n(zs['compounds'])} compounds; {pct(zs['shareInMulti'])} of footprints are "
        f"in multi-structure compounds; a gate is known for {pct(zs['shareCompoundsWithKnownGate'])} of compounds "
        f"({n(zs['compoundsWithKnownGate'])}). Urban fabric: {pct(zs['urbanShare'])}."))
    print()
    fp = d['footprintM2']
    print(('Emprise (m²) : ' if FR else 'Footprint (m²): ') + ', '.join(f"{k} {n(v)}" for k, v in fp.items()))
    cls = d['classes']
    tc = sum(cls.values())
    top = list(cls.items())[:8]
    print()
    print(('Usages les plus fréquents : ' if FR else 'Most common classes: ') +
          '; '.join(f"`{k}` {pct(v / tc)}" for k, v in top))
    rp = d['rPlus']
    print()
    print(('Niveaux (OpenStreetMap ; « unknown » = inconnu) : ' if FR else 'Floors (from OpenStreetMap; "unknown" where it has none): ') +
          '; '.join(f"{k} {n(v)}" for k, v in rp.items()))
    cs = d['compoundSizes']
    print()
    print(('Bâtiments par concession : ' if FR else 'Structures per compound: ') +
          '; '.join(f"{k}: {n(v)}" for k, v in cs.items()))
    print()
s = l['summary']
print(('**Noms de lieux et longueur des numéros.** ' if FR else '**Place words and number length.** ') + (
    f"{n(s['lieuxUsed'])} lieux reçoivent au moins une concession ; médiane {n(s['medianCompoundsPerLieu'])} concessions "
    f"par lieu. Part des concessions dont le numéro a 3 chiffres : {pct(s['shareCompoundsByDigits']['3'])} ; 4 chiffres : "
    f"{pct(s['shareCompoundsByDigits']['4'])} ; 5 chiffres : {pct(s['shareCompoundsByDigits']['5'])} ; lieux trop grands "
    f"(plus de 27 000, à découper) : {n(s['oversizeLieux'])} lieux, {pct(s['shareCompoundsInOversizeLieux'])} des concessions."
    if FR else
    f"{n(s['lieuxUsed'])} places receive at least one compound; median {n(s['medianCompoundsPerLieu'])} compounds per place. "
    f"Share of compounds whose number has 3 digits: {pct(s['shareCompoundsByDigits']['3'])}; 4 digits: "
    f"{pct(s['shareCompoundsByDigits']['4'])}; 5 digits: {pct(s['shareCompoundsByDigits']['5'])}; oversized places "
    f"(over 27,000, to split): {n(s['oversizeLieux'])} places, {pct(s['shareCompoundsInOversizeLieux'])} of compounds."))
print()
pn = nf['plateNames']
bs = pn['before']['shareCompoundsByDigits']
print((f"Les longueurs viennent des plages nationales par nom de plaque ; avec les noms officiels entiers, elles "
       f"étaient de {pct(bs['3'])}, {pct(bs['4'])} et {pct(bs['5'])} ; avec une plage par lieu, de 29,7 %, 45,4 % et "
       f"24,9 %. Un astérisque marque un nom de plaque provisoire, que la commune confirme.") if FR else
      (f"The lengths come from the national per-name ranges of the plate names; with the full official names they "
       f"were {pct(bs['3'])}, {pct(bs['4'])} and {pct(bs['5'])}; with one range per place, 29.7%, 45.4% and 24.9%. "
       f"An asterisk marks a provisional plate name, which the commune confirms."))
print()
hdr = ['Zone', 'Lieux', 'Concessions', '3 ch.', '4 ch.', '5 ch.', 'trop grands', 'lieux au nom partagé', 'plus grands lieux'] if FR else \
    ['Zone', 'Places', 'Compounds', '3 digits', '4 digits', '5 digits', 'oversized', 'places with a shared name', 'largest places']
print('| ' + ' | '.join(hdr) + ' |')
print('|' + '---|' * len(hdr))
for z in ('DKR', 'PKN', 'GDW', 'RUF', 'TBA', 'THS', 'STL', 'ZIG', 'BMB', 'KLD', 'TBC'):
    zs = l['zones'].get(z)
    if not zs:
        continue
    t = zs['compounds'] or 1
    big = ', '.join(f"{x['name']}{'*' if x.get('needsCouncilChoice') else ''} ({n(x['compounds'])})"
                    for x in zs['largest'][:3])
    print('| ' + ' | '.join([z, n(zs['lieux']), n(zs['compounds'])] +
                            [pct(zs['compoundsByDigits'][k] / t) for k in '345'] +
                            [pct(zs['compoundsInOversizeLieux'] / t), n(zs['lieuxSharingANameNationally']), big]) + ' |')
print()
L = nf['largestSharedRange']
print(('**Noms répétés.** ' if FR else '**Repeated names.** ') + (
    f"{n(nf['lieux'])} lieux portent {n(nf['nameKeys'])} noms une fois normalisés. {n(nf['repeatingNames'])} noms se "
    f"répètent, sur {n(nf['lieuxWithRepeatingNames'])} lieux ({n(nf['repeatingNamesAcrossZones'])} dans plusieurs zones, "
    f"{n(nf['repeatingNamesWithinOneZoneOnly'])} dans une seule) qui tiennent {pct(nf['shareCompoundsInRepeatingNames'])} "
    f"des concessions. Plages partagées : {n(nf['repeatingNamesByDigits'].get('3', 0))} à 3 chiffres, "
    f"{n(nf['repeatingNamesByDigits'].get('4', 0))} à 4, {n(nf['repeatingNamesByDigits'].get('5', 0))} à 5. "
    f"La plus grande : {L['names'][0]}, {n(L['lieux'])} lieux dans {n(L['zones'])} zones, {n(L['compounds'])} concessions, "
    f"5 chiffres, {pct(L['allocatedShare'])} de la plage attribués. Noms qui demandent un qualificatif : "
    f"{n(nf['namesNeedingQualifier'])}."
    if FR else
    f"{n(nf['lieux'])} places carry {n(nf['nameKeys'])} names once normalised. {n(nf['repeatingNames'])} names repeat, "
    f"over {n(nf['lieuxWithRepeatingNames'])} places ({n(nf['repeatingNamesAcrossZones'])} names in several zones, "
    f"{n(nf['repeatingNamesWithinOneZoneOnly'])} within one zone only) holding {pct(nf['shareCompoundsInRepeatingNames'])} "
    f"of compounds. Shared ranges: {n(nf['repeatingNamesByDigits'].get('3', 0))} of 3 digits, "
    f"{n(nf['repeatingNamesByDigits'].get('4', 0))} of 4, {n(nf['repeatingNamesByDigits'].get('5', 0))} of 5. The largest: "
    f"{L['names'][0]}, {n(L['lieux'])} places in {n(L['zones'])} zones, {n(L['compounds'])} compounds, 5 digits, "
    f"{pct(L['allocatedShare'])} of the range allocated. Names needing a qualifier: {n(nf['namesNeedingQualifier'])}."))
print()
hdr = ['Nom', 'Lieux', 'Zones', 'Concessions', 'Chiffres', 'Plage attribuée'] if FR else \
    ['Name', 'Places', 'Zones', 'Compounds', 'Digits', 'Range allocated']
print('| ' + ' | '.join(hdr) + ' |')
print('|' + '---|' * len(hdr))
seen = set()
for r in nf['topSharedByLieux'][:8] + nf['topSharedByCompounds'][:6]:
    if r['names'][0] in seen:
        continue
    seen.add(r['names'][0])
    print(f"| {' / '.join(r['names'][:3])} | {n(r['lieux'])} | {n(r['zones'])} | {n(r['compounds'])} | {r['digits']} | "
          f"{pct(r['allocatedShare'])} |")
print()
# plate names (SPEC 3.2.1)
ru = pn['byRule']
B, A = pn['before'], pn['after']
print(('**Noms de plaque.** ' if FR else '**Plate names.** ') + (
    f"Sur {n(pn['lieux'])} noms officiels, {n(pn['officialOverLimit']['any'])} dépassent la limite "
    f"({n(pn['officialOverLimit']['over12Characters'])} ont plus de 12 caractères, "
    f"{n(pn['officialOverLimit']['over2Words'])} plus de 2 mots). {n(ru.get('as-is', 0))} noms restent tels quels ; "
    f"{n(ru.get('cleaned', 0))} sont nettoyés (mot générique, sigle, numéral en chiffres), {n(ru.get('known', 0))} prennent "
    f"une forme courte documentée, {n(ru.get('distinctive', 0))} gardent leurs un ou deux mots les plus distinctifs. "
    f"{n(pn['needsCouncilChoice'])} sont soumis à la commune avec au plus 3 propositions, dont "
    f"{n(pn['stillOverLimitProvisionally'])} restent provisoirement trop longs (aucune proposition ne tient). "
    f"{n(pn['aliasesDropped'])} noms officiels ne sont pas gardés comme alias, parce que deux noms de plaque les "
    f"revendiqueraient."
    if FR else
    f"Of {n(pn['lieux'])} official names, {n(pn['officialOverLimit']['any'])} are over the limit "
    f"({n(pn['officialOverLimit']['over12Characters'])} have more than 12 characters, "
    f"{n(pn['officialOverLimit']['over2Words'])} more than 2 words). {n(ru.get('as-is', 0))} names stay as they are; "
    f"{n(ru.get('cleaned', 0))} are cleaned (generic word, acronym, numeral in digits), {n(ru.get('known', 0))} take a "
    f"documented short form, {n(ru.get('distinctive', 0))} keep their one or two most distinctive words. "
    f"{n(pn['needsCouncilChoice'])} go to the commune with up to 3 candidates; "
    f"{n(pn['stillOverLimitProvisionally'])} of them stay over the limit provisionally (no candidate fits). "
    f"{n(pn['aliasesDropped'])} official names are not kept as aliases, because two plate names would claim them."))
print()
hdr = ['', 'Noms officiels', 'Noms de plaque'] if FR else ['', 'Official names', 'Plate names']
print('| ' + ' | '.join(hdr) + ' |')
print('|---|---|---|')
rows = [(('Noms une fois normalisés' if FR else 'Names once normalised'), n(B['nameKeys']), n(A['nameKeys'])),
        (('Noms partagés (lieux)' if FR else 'Shared names (places)'),
         f"{n(B['sharedNames'])} ({n(B['lieuxInSharedNames'])})", f"{n(A['sharedNames'])} ({n(A['lieuxInSharedNames'])})"),
        (('Plus grande plage partagée' if FR else 'Largest shared range'),
         f"{B['largestSharedRange']['names'][0]}, {n(B['largestSharedRange']['lieux'])}, {n(B['largestSharedRange']['compounds'])}",
         f"{A['largestSharedRange']['names'][0]}, {n(A['largestSharedRange']['lieux'])}, {n(A['largestSharedRange']['compounds'])}"),
        (('Nom le plus partagé' if FR else 'Most shared name'),
         f"{B['mostSharedName']['names'][0]}, {n(B['mostSharedName']['lieux'])}",
         f"{A['mostSharedName']['names'][0]}, {n(A['mostSharedName']['lieux'])}"),
        (('Lieux à 3 / 4 / 5 chiffres' if FR else 'Places with 3 / 4 / 5 digits'),
         ' / '.join(n(B['lieuxByDigits'][k]) for k in '345'), ' / '.join(n(A['lieuxByDigits'][k]) for k in '345')),
        (('Concessions à 3 / 4 / 5 chiffres' if FR else 'Compounds with 3 / 4 / 5 digits'),
         ' / '.join(pct(B['shareCompoundsByDigits'][k]) for k in '345'),
         ' / '.join(pct(A['shareCompoundsByDigits'][k]) for k in '345'))]
for r in rows:
    print('| ' + ' | '.join(r) + ' |')
print()
lc, lf = pn['longestRememberedCode'], pn['longestRememberedCodeNotFlagged']
print((f"Adresse retenue la plus longue : « {lf['code']} » ({lf['length']} caractères) ; avec les noms provisoires, "
       f"« {lc['code']} » ({lc['length']}), un nom que la commune doit raccourcir.") if FR else
      (f"Longest remembered address: \"{lf['code']}\" ({lf['length']} characters); with the provisional names, "
       f"\"{lc['code']}\" ({lc['length']}), a name the commune has to shorten."))
