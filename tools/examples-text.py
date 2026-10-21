#!/usr/bin/env python3
"""Print the worked-examples section of the papers (en|fr) from
engine/reference/vectors.json, so the papers show exactly what the engine
computes.

  tools/examples-text.py en|fr
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
v = json.load(open(os.path.join(HERE, '..', 'engine', 'reference', 'vectors.json')))
LX = {(it['zone'], it['index']): it for it in json.load(open(os.path.join(HERE, '..', 'model', 'lieux.json')))['lieux']}
FR = (sys.argv[1] if len(sys.argv) > 1 else 'en') == 'fr'
T = {
    'spot': ('**Codes de point** (calculés hors ligne, sans registre) :' if FR else
             '**Spot codes** (computed offline, no registry needed):'),
    'cols': (['Lieu', 'Code', 'Cellule', 'Lu à voix haute'] if FR else ['Place', 'Code', 'Cell', 'Read aloud']),
    'nums': ('**Lire un numéro.**' if FR else '**Reading a number.**'),
    'samp': ('**Adresses tirées d\'empreintes réelles.** Trois carrés de 300 m de la carte N-Ways (OpenStreetMap + '
             'Google/Microsoft) sont regroupés en concessions, rattachés à leur lieu et numérotés par le moteur de '
             'référence. Les numéros viennent du seul échantillon : à la première attribution nationale, chaque lieu '
             'est numéroté en entier et les numéros différeront.' if FR else
             '**Addresses from real footprints.** Three 300 m squares of the N-Ways map (OpenStreetMap + Google/'
             'Microsoft) are grouped into compounds, given their place word and numbered by the reference engine. The '
             'numbers come from the sample alone: at the national first issue each place is numbered whole, so the '
             'numbers will differ.'),
    'amh': ('**« Ajouter ma maison ».**' if FR else '**"Add my home".**'),
}
NAMES = {'dakar-medina.csv': ('Médina, Dakar', 'Médina, Dakar'), 'touba.csv': ('Touba, near the Grande Mosquée',
         'Touba, près de la Grande Mosquée'), 'bambey-village.csv': ('a village of Bambey département',
         'un village du département de Bambey')}
print(T['spot'])
print()
print('| ' + ' | '.join(T['cols']) + ' |')
print('|---|---|---|---|')
for s in v['spot']:
    print(f"| {s['place']} | `{s['code']}` | {s['cellMetres']} m | {s['spokenFr'].replace(' | ', ' · ')} |")
print()
print(T['nums'] + ' ' + '; '.join(f"{x['written']} → « {x['spokenFr']} » / wolof « {x['spokenWo']} »" if FR else
                                  f"{x['written']} → \"{x['spokenFr']}\" / Wolof \"{x['spokenWo']}\"" for x in v['numbers']))
print()
print('**Même nom, lieux différents** (décodés sans contexte : ni zone, ni position) :' if FR else
      '**Same name, different places** (decoded with no context: no zone, no position):')
print()
print('| ' + ' | '.join(['Adresse retenue', 'Lieu trouvé', 'Bloc du lieu', 'Canonique', 'Une faute de frappe vers un autre lieu du même nom']
                        if FR else ['Remembered', 'Decodes to', 'Block of the place', 'Canonical', 'One-digit slip into another same-named place']) + ' |')
print('|---|---|---|---|---|')
for x in v['sameName']:
    sl = x['slipIntoOtherLieu']
    slip = '-' if not sl else (
        (f"`{sl['typed']}` → refusée par la lettre (sans lettre : {', '.join(sl['withoutLetter']) or 'refusée, chiffre du nom'})")
        if FR else
        (f"`{sl['typed']}` → refused by the letter (without it: {', '.join(sl['withoutLetter']) or 'refused, name numeral'})"))
    zn = x['zoneName'].split(' (')[0]
    print(f"| **{x['remembered']}** | {zn} ({x['zone']}/{x['lieu']}) | {x['block'][0]}-{x['block'][1]} | "
          f"`{x['canonical']}` | {slip} |")
print()
pv = v['plateNames']
print('**Noms de plaque** (nom officiel → nom dit et tapé ; le nom officiel tapé mène au même lieu) :' if FR else
      '**Plate names** (official name → the name said and typed; the official name typed leads to the same place):')
print()
print('| ' + ' | '.join(['Nom officiel', 'Nom de plaque', 'Règle', 'Retenue', 'Le nom officiel tapé'] if FR else
                        ['Official name', 'Plate name', 'Rule', 'Remembered', 'Official name typed']) + ' |')
print('|---|---|---|---|---|')
RULE_FR = {'cleaned': 'nettoyé', 'known': 'forme courte documentée', 'distinctive': 'mot le plus distinctif',
           'council': 'provisoire : la commune choisit', 'as-is': 'tel quel'}
RULE_EN = {'cleaned': 'cleaned', 'known': 'documented short form', 'distinctive': 'most distinctive word',
           'council': 'provisional: the commune chooses', 'as-is': 'as is'}
for x in pv['long']:
    rule = (RULE_FR if FR else RULE_EN)[x['plateRule']]
    if x.get('source'):
        rule += f" ({x['source'].split(':')[0]})"
    print(f"| {x['officialName']} | **{x['plateName']}** ({x['plateLength']}) | {rule} | **{x['remembered']}** | "
          f"{'→ ' + ', '.join(x['decodedOfficial'])} |")
print()
print('**Deux lieux dont les noms de plaque ne se confondent qu\'après raccourcissement** (une seule plage, deux blocs) :'
      if FR else '**Two places whose plate names collide only after shortening** (one range, two blocks):')
print()
print('| ' + ' | '.join(['Nom officiel', 'Nom de plaque', 'Bloc', 'Retenue', 'Lieu trouvé'] if FR else
                        ['Official name', 'Plate name', 'Block', 'Remembered', 'Decodes to']) + ' |')
print('|---|---|---|---|---|')
for pair in pv['collide']:
    for x in pair:
        print(f"| {x['officialName']} | {x['plateName']} | {x['block'][0]}-{x['block'][1]} | **{x['remembered']}** | "
              f"{', '.join(x['decoded'])} |")
print()
print(T['samp'])
print()
for f, s in v['samples'].items():
    nm = NAMES.get(f, (f, f))[1 if FR else 0]
    head = (f"*{nm}* : {s['footprints']} empreintes → {s['compounds']} concessions, dont {s['multiStructureCompounds']} "
            f"à plusieurs bâtiments." if FR else
            f"*{nm}*: {s['footprints']} footprints → {s['compounds']} compounds, {s['multiStructureCompounds']} of them "
            f"with several structures.")
    print(head)
    for zk, li in sorted({tuple(c['canonical'].split('-')[1:3]) for c in s['first']}):
        it = LX.get((zk, int(li)))
        if it and it['officialName'] != it['name']:
            print()
            print((f"Nom officiel du lieu : « {it['officialName']} » ; nom de plaque **{it['name']}**"
                   + (" (provisoire : la commune choisit)." if it['needsCouncilChoice'] else ".")) if FR else
                  (f"Official name of the place: \"{it['officialName']}\"; plate name **{it['name']}**"
                   + (" (provisional: the commune chooses)." if it['needsCouncilChoice'] else ".")))
    if any(c['coverage'] != 'nways' for c in s['first']):
        print()
        print('\\* Zone d\'adressage municipal : l\'adresse affichée est la rue et le numéro officiels ; l\'adresse N-Ways '
              'n\'est qu\'un alias provisoire.' if FR else
              '\\* Municipal addressing area: the address shown is the official street and number; the N-Ways address is '
              'only a temporary alias.')
    print()
    print('| ' + ' | '.join(['Retenue', 'Écrite (plaque)', 'Canonique', 'Couverture', 'Bâtiments', 'Usages'] if FR else
                            ['Remembered', 'Written (plate)', 'Canonical', 'Coverage', 'Structures', 'Classes']) + ' |')
    print('|---|---|---|---|---|---|')
    for c in s['first']:
        off = c['coverage'] != 'nways'
        plate = ('aucune (zone officielle)' if FR else 'none (official area)') if off else f"`{c['written']}`"
        cov = (('officielle : adresse de rue affichée' if FR else 'official: street address shown') if off
               else 'N-Ways')
        print(f"| **{c['remembered']}**{' *' if off else ''} | {plate} | `{c['canonical']}` | {cov} | {c['structures']} | "
              f"{', '.join(c['classes'][:4])}{'…' if len(c['classes']) > 4 else ''} |")
    print()
print(T['amh'])
print()
for f, a in v['addMyHome'].items():
    nm = NAMES.get(f, (f, f))[1 if FR else 0]
    g, n_ = a['gateInsideExisting'], a['newHome']
    if FR:
        print(f"- *{nm}* : portail à l'intérieur d'une concession existante → **{g['status']}** ({g.get('reason', '')}). "
              f"Portail à 40 m de la dernière concession → **{n_['status']}** : **{n_.get('remembered', '')}**, "
              f"`{n_.get('canonical', '')}`, code de point immédiat `{n_.get('spotCode', '')}`.")
    else:
        print(f"- *{nm}*: a gate inside an existing compound → **{g['status']}** ({g.get('reason', '')}). "
              f"A gate 40 m beyond the last compound → **{n_['status']}**: **{n_.get('remembered', '')}**, "
              f"`{n_.get('canonical', '')}`, immediate spot code `{n_.get('spotCode', '')}`.")
