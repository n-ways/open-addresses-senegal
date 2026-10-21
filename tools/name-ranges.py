#!/usr/bin/env python3
"""National name ranges for Senegal (SPEC 3.3): make every remembered address
('Ouakam 2512') unique in the whole country on its own.

First, every lieu gets its PLATE name (tools/sn_plates.py, SPEC 3.2.1): at most
12 characters and 2 words, the name people say and type; the full official
name is kept (officialName) and accepted as an alias unless two plate names
would claim it. The ranges below are cut by plate name.

Every lieu whose place word folds to the same name key (engine `name_key`:
case, accents, hyphens, apostrophes, leading articles, trailing numerals and
French/Wolof spelling variants folded) joins one name family. The family gets
one national number range (3, 4 or 5 digits) and each of its lieux one block
of it, sized for three times the lieu's compounds, with at least 10 % of the
range left free for new same-named lieux. The block table is frozen at first
issue: a rebuild keeps every existing block and only adds new ones.

  tools/name-ranges.py            reads model/lieux.json (from tools/build-lieux.py),
                                  writes model/lieux.json (family, digits, blocks),
                                  model/name-families.json and model/lieux-stats.json

Light: works on the inventory only (15,000 lieux, a few seconds), no footprints.
"""
import json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, '..', 'model')
sys.path.insert(0, os.path.join(HERE, '..', 'engine', 'reference'))
import sn_engine as E  # noqa: E402
sys.path.insert(0, HERE)
import sn_plates  # noqa: E402

# Names whose lieux together do not fit 5 digits get ONE established qualifier,
# decided once per name and listed here: {(zone, lieu index): qualifier}.
# With the counts of 18 October 2026 no name overflows (largest: Darou Salam).
QUALIFIERS = {}
# Names whose range is already 75 % allocated: a NEW same-named lieu that does
# not fit the remaining spare space takes a qualifier (SPEC 3.3.4), decided once
# with its commune and added to QUALIFIERS above.
WATCH_SHARE = 0.75

lp = os.path.join(MODEL, 'lieux.json')
doc = json.load(open(lp))
items = doc['lieux']
for it in items:  # a per-zone qualifier is only a hint on the place card, never part of the address
    if 'qualifier' in it:
        it['nearTown'] = it.pop('qualifier')

zones_list = json.load(open(os.path.join(MODEL, 'zones.json')))['zones']
for it in items:
    it.setdefault('officialName', it['name'])


def range_stats(rows):
    """Collisions and number lengths for a list of lieux with 'name' set (one range per name key)."""
    tmp = [{'zone': it['zone'], 'index': it['index'], 'name': it['name'], 'compounds': it['compounds'],
            'needsCouncilChoice': True} for it in rows]
    E.allocate_families(tmp)
    byk = {}
    for it in tmp:
        byk.setdefault(it['nameKey'], []).append(it)
    shared = {k: v for k, v in byk.items() if len(v) > 1}
    tot = sum(it['compounds'] for it in tmp)
    big = max(shared.values(), key=lambda v: (sum(it['compounds'] for it in v), len(v)))
    most = max(shared.values(), key=lambda v: (len(v), sum(it['compounds'] for it in v)))
    return {'nameKeys': len(byk), 'sharedNames': len(shared), 'lieuxInSharedNames': sum(len(v) for v in shared.values()),
            'largestSharedRange': {'names': sorted({it['name'] for it in big}), 'lieux': len(big),
                                   'compounds': sum(it['compounds'] for it in big), 'digits': big[0]['digits']},
            'mostSharedName': {'names': sorted({it['name'] for it in most})[:6], 'lieux': len(most),
                               'compounds': sum(it['compounds'] for it in most), 'digits': most[0]['digits']},
            'lieuxByDigits': {str(d): sum(1 for it in tmp if it['digits'] == d) for d in (3, 4, 5)},
            'namesByDigits': {str(d): sum(1 for v in byk.values() if v[0]['digits'] == d) for d in (3, 4, 5)},
            'shareCompoundsByDigits': {str(d): round(sum(it['compounds'] for it in tmp if it['digits'] == d) / tot, 4)
                                       for d in (3, 4, 5)}}


before = range_stats([dict(it, name=it['officialName']) for it in items])
over_chars = sum(1 for it in items if E._P.plate_length(it['officialName']) > E._P.MAX_CHARS)
over_words = sum(1 for it in items if E._P.word_count(E.split_numeral(it['officialName'])[0], 'fr') > E._P.MAX_WORDS)
over_any = sum(1 for it in items if not E.plate_ok(it['officialName']))
sn_plates.derive_all(items, zones_list)

# aliases: the official name and the map's other spellings, unless two plate names would claim one
for it in items:
    pool = [it['officialName']] + it.get('aliases', []) + [a for a, _ in it.pop('aliasesDropped', [])]
    seen, al = set(), []
    for a in pool:
        if a != it['name'] and a not in seen:
            seen.add(a)
            al.append(a)
    it['aliases'] = al
claims = {}
for it in items:
    pk = E.name_key(it['name'])
    claims.setdefault(pk, set()).add(pk)
    for a in it['aliases']:
        claims.setdefault(E.name_key(a), set()).add(pk)
dropped_aliases = []
for it in items:
    keep, drop = [], []
    for a in it['aliases']:
        if len(claims[E.name_key(a)]) > 1:
            drop.append([a, 'claimed by two plate names: typing it would not name one place'])
        else:
            keep.append(a)
    it['aliases'] = keep
    if drop:
        it['aliasesDropped'] = drop
        dropped_aliases += [{'lieu': f"{it['zone']}/{it['index']}", 'plate': it['name'], 'alias': a} for a, _ in drop]

fp = os.path.join(MODEL, 'name-families.json')
frozen = None
if os.path.exists(fp):
    old = json.load(open(fp))
    if old.get('issued'):
        frozen = {f['key']: {'id': f['id'], 'digits': f['digits'], 'blocks': f['blocks']} for f in old['families']}
fams = E.allocate_families(items, frozen=frozen, qualifiers=QUALIFIERS)

zones = {z['key']: z for z in json.load(open(os.path.join(MODEL, 'zones.json')))['zones']}
by_key = {}
for it in items:
    by_key.setdefault(it['nameKey'], []).append(it)

total = sum(it['compounds'] for it in items)
rep = {k: v for k, v in by_key.items() if len(v) > 1}
fam_out = [{'id': f['id'], 'key': k, 'digits': f['digits'], 'blocks': f['blocks']}
           for k, f in sorted(fams.items(), key=lambda kv: kv[1]['id'])]


def fam_row(k):
    v = by_key[k]
    f = fams[k]
    used = sum(b[1] - b[0] + 1 for bl in f['blocks'].values() for b in bl)
    return {'key': k, 'names': sorted({it['placeWord'] for it in v}), 'lieux': len(v),
            'zones': len({it['zone'] for it in v}), 'compounds': sum(it['compounds'] for it in v),
            'digits': f['digits'], 'allocated': used, 'rangeSize': 9 * 10 ** (f['digits'] - 1),
            'allocatedShare': round(used / (9 * 10 ** (f['digits'] - 1)), 3),
            'blocks': [{'zone': it['zone'], 'zoneName': zones[it['zone']]['name'], 'lieu': it['index'],
                        'name': it['placeWord'], 'compounds': it['compounds'], 'block': it['blocks'][0]}
                       for it in sorted(v, key=lambda it: (it['zone'], it['index']))]}


largest = sorted(rep, key=lambda k: (-sum(it['compounds'] for it in by_key[k]), k))
most_areas = sorted(rep, key=lambda k: (-len(by_key[k]), k))
watch = []
for k in rep:
    r = fam_row(k)
    if r['allocatedShare'] >= WATCH_SHARE:
        watch.append({'name': r['names'][0], 'lieux': r['lieux'], 'digits': r['digits'],
                      'allocatedShare': r['allocatedShare'], 'spareNumbers': r['rangeSize'] - r['allocated']})


def share(sel):
    return {str(d): round(sum(it['compounds'] for it in items if sel(it) and it['digits'] == d) / total, 4)
            for d in (3, 4, 5)}


summary = {
    'date': '2026-10-18',
    'rule': 'one national range per name key; one block per lieu = 3 x compounds rounded up to tens (3 digits) '
            'or hundreds (4-5 digits); digits = smallest d in {3,4,5} with blocks <= 90 % of the range',
    'lieux': len(items), 'nameKeys': len(by_key),
    'repeatingNames': len(rep),
    'lieuxWithRepeatingNames': sum(len(v) for v in rep.values()),
    'repeatingNamesAcrossZones': sum(1 for v in rep.values() if len({it['zone'] for it in v}) > 1),
    'repeatingNamesWithinOneZoneOnly': sum(1 for v in rep.values() if len({it['zone'] for it in v}) == 1),
    'compoundsInRepeatingNames': sum(it['compounds'] for v in rep.values() for it in v),
    'shareCompoundsInRepeatingNames': round(sum(it['compounds'] for v in rep.values() for it in v) / total, 4),
    'repeatingNamesByLieux': dict(sorted(Counter(len(v) for v in rep.values()).items())),
    'repeatingNamesByDigits': dict(sorted(Counter(fams[k]['digits'] for k in rep).items())),
    'lieuxByDigits': {str(d): sum(1 for it in items if it['digits'] == d) for d in (3, 4, 5)},
    'shareCompoundsByDigits': share(lambda it: True),
    'shareCompoundsByDigitsPerLieuRangesBefore': {'3': 0.297, '4': 0.4541, '5': 0.2489},
    'namesNeedingQualifier': len(QUALIFIERS),
    'qualifiers': [{'lieu': f'{z}/{i}', 'qualifier': q} for (z, i), q in sorted(QUALIFIERS.items())],
    'watchCount': len(watch),
    'watch': sorted(watch, key=lambda w: (-w['lieux'], -w['allocatedShare'], w['name']))[:20],
    'largestSharedRange': fam_row(largest[0]) if largest else None,
    'mostRepeatedName': fam_row(most_areas[0]) if most_areas else None,
    'topSharedByCompounds': [{k2: fam_row(k)[k2] for k2 in ('names', 'lieux', 'zones', 'compounds', 'digits', 'allocatedShare')}
                             for k in largest[:12]],
    'topSharedByLieux': [{k2: fam_row(k)[k2] for k2 in ('names', 'lieux', 'zones', 'compounds', 'digits', 'allocatedShare')}
                         for k in most_areas[:12]],
}
def longest(rows):
    best = None
    for it in rows:
        hi = max(b[1] for b in it['blocks'])
        code = f"{it['name']} {E.group_number(hi) if hi >= 10000 else hi}"
        if best is None or (len(code), code) > (len(best['code']), best['code']):
            best = {'code': code, 'length': len(code), 'lieu': f"{it['zone']}/{it['index']}",
                    'officialName': it['officialName']}
    return best


rules = Counter(it['plateRule'] for it in items)
flagged = [it for it in items if it['needsCouncilChoice']]
summary['plateNames'] = {
    'rule': 'plate name <= 12 characters and <= 2 words (tools/sn_plates.py, SPEC 3.2.1); same plate name key = one range',
    'lieux': len(items),
    'officialOverLimit': {'any': over_any, 'over12Characters': over_chars, 'over2Words': over_words},
    'byRule': dict(sorted(rules.items())),
    'needsCouncilChoice': len(flagged),
    'stillOverLimitProvisionally': sum(1 for it in items if not E.plate_ok(it['name'])),
    'aliasesDropped': len(dropped_aliases),
    'aliasesDroppedList': dropped_aliases[:50],
    'before': before,
    'after': range_stats(items),
    'longestRememberedCode': longest(items),
    'longestRememberedCodeNotFlagged': longest([it for it in items if not it['needsCouncilChoice']]),
}
json.dump(doc, open(lp, 'w'), ensure_ascii=False, separators=(',', ':'))
# Once issued, the block table stays frozen in every later rebuild.
json.dump({'status': ('frozen at first issue, 2026-10-20: blocks are only ever added, never moved' if frozen else
                      'not issued: blocks are cut afresh on every rebuild until first issue'),
           'issued': bool(frozen), 'summary': summary,
           'families': fam_out},
          open(fp, 'w'), ensure_ascii=False, separators=(',', ':'))

# lieux-stats.json: the number lengths now come from the name families
sp = os.path.join(MODEL, 'lieux-stats.json')
st = json.load(open(sp))
s = st['summary']
s['rule'] = summary['rule']
s['shareCompoundsByDigits'] = summary['shareCompoundsByDigits']
s['lieuxByDigits'] = summary['lieuxByDigits']
s['repeatingNames'] = summary['repeatingNames']
s['lieuxWithRepeatingNames'] = summary['lieuxWithRepeatingNames']
for z, zs in st['zones'].items():
    zl = [it for it in items if it['zone'] == z]
    zs['compoundsByDigits'] = {str(d): sum(it['compounds'] for it in zl if it['digits'] == d) for d in (3, 4, 5)}
    zs['lieuxByDigits'] = {str(d): sum(1 for it in zl if it['digits'] == d) for d in (3, 4, 5)}
    zs.pop('duplicateNamesQualified', None)
    zs['lieuxSharingANameNationally'] = sum(1 for it in zl if len(by_key[it['nameKey']]) > 1)
    zs['largest'] = [{'name': it['name'], 'officialName': it['officialName'], 'compounds': it['compounds'],
                      'needsCouncilChoice': it['needsCouncilChoice']}
                     for it in sorted(zl, key=lambda it: -it['compounds'])[:5]]
    zs['oversizeLieux'] = [it['name'] for it in zl if 3 * it['compounds'] > 81000]
json.dump(st, open(sp, 'w'), ensure_ascii=False, indent=1)

print(json.dumps({k: v for k, v in summary.items() if k not in ('largestSharedRange', 'mostRepeatedName', 'plateNames')},
                 ensure_ascii=False, indent=1))
print('plateNames', json.dumps({k: v for k, v in summary['plateNames'].items() if k != 'aliasesDroppedList'},
                               ensure_ascii=False, indent=1))
for lab in ('largestSharedRange', 'mostRepeatedName'):
    r = summary[lab]
    print(lab, json.dumps({k: v for k, v in r.items() if k != 'blocks'}, ensure_ascii=False))
    for b in r['blocks']:
        print('   ', b['zone'], b['lieu'], b['name'], b['compounds'], b['block'])
for z in ('DKR', 'PKN', 'GDW', 'RUF', 'TBA', 'THS', 'STL', 'ZIG', 'BMB', 'KLD', 'TBC'):
    zs = st['zones'][z]
    n = zs['compounds']
    print(z, zs['lieux'], n, {d: round(100 * x / n, 1) for d, x in zs['compoundsByDigits'].items()},
          zs['lieuxSharingANameNationally'])
