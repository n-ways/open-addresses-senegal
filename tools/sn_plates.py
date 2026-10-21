#!/usr/bin/env python3
"""Plate names for Senegal: the short remembered name of every lieu (SPEC 3.2.1).

The name in the remembered address is at most 12 characters and 2 words
("Ouakam 2512", "Liberté 6 4512"), because a long address is not remembered.
The lieu keeps its full official name (from the map or the commune list),
printed in small type on cards and plates and still accepted when typed; the
PLATE name is what people say and type.

The derivation is the rule in engine/reference/plate_names.py. This file
configures it for Senegal:

  * French word lists; word frequencies are counted over all of Senegal's
    official lieu names;
  * a trailing sector numeral ("HLM 5", "Pikine 3", "Plan Jaxaay 01",
    "S.I.C.A.P. Liberté Six") is split off first, as the engine's name key
    already does, and written back in digits after the shortened name; it
    counts towards the 12 characters but not as a word;
  * KNOWN: short forms people already say, each with a source (SOURCES.md N1-N9);
  * scheme labels are dropped like generic words (S.I.C.A.P., Sicap); "Cité"
    is NOT dropped from a name that fits (Cité Lamy is said "Cité Lamy"), it
    only goes first when the name is too long; ethnic and compass qualifiers
    (Peul, Wolof, Sérère, Toucouleur, Nord, Ouest...) are weak words, so a
    name is never shortened by silently dropping them;
  * settlement heads that start a person's or a family's place name (Keur,
    Darou, Médina, Saré, Sinthiou, Gourel, Ouro, Santhie, Dara...) bind to the
    next word: "Keur Momar Sarr" is never shortened to "Momar Sarr"; and a
    shortened name that starts with one of them always goes to the commune
    (needsCouncilChoice), because any cut drops part of a person's name;
  * the avoid set: commune and département seats, regional capitals, the
    large towns of Senegal and the towns across its borders that people
    travel to; the lieu's own town (its zone's seat and the nearest town
    within 15 km) is removed from the set for that lieu.
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'engine', 'reference'))
import plate_names as P  # noqa: E402
import sn_engine as E  # noqa: E402

LANG = 'fr'

# ---- trailing sector numeral and the plate check: in the engine (SPEC 3.2.1) ----
split_numeral = E.split_numeral
plate_ok = E.plate_ok


# ---- documented short forms (sources: SOURCES.md, section "Place names") ------
# The plate value is the name without its trailing numeral (written back after it).
SRC_SALY = ('N1: fr.wikipedia.org/wiki/Saly_Portudal, "Saly Portudal (ou couramment Saly) est une station '
            'balnéaire" (accessed 2026-10-18)')
SRC_PLATEAU = ('N2: fr.wikipedia.org/wiki/Dakar-Plateau, the article names the area "le Plateau" ("Le Plateau '
               'demeure parmi les ensembles urbains...") (accessed 2026-10-18)')
KNOWN = {
    # official name in the inventory: (plate name, source)
    'Saly Portudal': ('Saly', SRC_SALY),
    'Sali Portudal': ('Saly', SRC_SALY),       # the same resort, second spelling in the map
    'Dakar-Plateau': ('Plateau', SRC_PLATEAU),
}
# Short forms people say but for which no written source was found: the
# commune decides; the first candidate is used provisionally.
COUNCIL = {
    'Parcelles Assainies': (['Parcelles', 'Assainies'], '"Parcelles" is the usual short form in speech, but no written '
                            'source was found; the commune confirms it'),
    'Fann-Point E-Amitié': (['Point E', 'Fann', 'Amitié'], 'a commune named after three quartiers: the commune '
                            'chooses'),
    'Gueule Tapée-Fass-Colobane': (['Gueule Tapée', 'Colobane', 'Fass'], 'a commune named after three quartiers: '
                                   'the commune chooses'),
    'Mermoz-Sacré-Cœur': (['Mermoz', 'Sacré-Cœur'], 'a commune named after two quartiers: the commune chooses'),
    'Joal-Fadiouth': (['Joal', 'Fadiouth'], 'the commune joins two villages (Joal on the coast, Fadiouth on its '
                      'island): the commune chooses'),
}

# ---- country word lists -------------------------------------------------------
GENERIC_EXTRA = ['s.i.c.a.p.', 'sicap', 'quarter']   # 'Quarter Angel Mouss': an English mistranslation of Quartier
GENERIC_REMOVE = {'cité', 'cite'}                     # kept in a name that fits; still a head when too long
ETHNIC = ['peul', 'peulh', 'peuhl', 'peulhs', 'peuls', 'wolof', 'ouolof', 'woloff', 'sérère', 'serere', 'sérèr',
          'serer', 'sereer', 'toucouleur', 'toucouleurs', 'bambara', 'maure', 'maures', 'diola', 'mandingue',
          'mandinka', 'socé', 'soce', 'lébou', 'lebou', 'sarakholé', 'sarakole', 'soninké', 'soninke', 'khassonké',
          'bassari', 'bédik', 'malinké', 'malinke', 'foula', 'laobé', 'laobe']
# Descriptive common nouns: a plate name is never only these, and a name is
# never shortened to them ("Cité Compagnie des Eaux" is not "Eaux").
NOUNS = ['marché', 'marche', 'hebdomadaire', 'mosquée', 'mosquee', 'gendarmerie', 'standing', 'compagnie', 'eaux',
         'central', 'centrale', 'artisanal', 'artisanale', 'artisanales', 'artisanaux', 'croisement', 'carrefour',
         'maison', 'rail', 'rails', 'pépinière', 'poste', 'police', 'école', 'usine', 'plage', 'port', 'aéroport',
         'résidence', 'résidences', 'villa', 'villas', 'route', 'piste', 'forage', 'militaire', 'cimetière',
         'station', 'pont', 'plan', 'parcelle', 'parcelles', 'cap', 'île', 'ile', 'pointe', 'fass', 'diamaguène', 'puits',
         'premier', 'première', 'deuxième', 'deuxiéme', 'troisième', 'quatrième']
WEAK_EXTRA = ETHNIC + NOUNS + ['escale', 'gare', 'extension', 'ext', 'ancien', 'nouveau', 'nouvelle', 'deux', 'i',
                               'ii', 'iii', 'iv', 'v', 'kounda', 'walo', 'ferlo', 'diéri', 'dieri', 'djiéri', 'djeri']
# Settlement heads that open a person's, a family's or a holy place's name
# (Wolof keur "house of", Arabic dar/darou, médina, djannatoul, boukhatoul;
# Pulaar saré, sinthiou, gourel, ouro "village / hamlet of").
SN_HEADS = {'keur', 'ker', 'kerr', 'kër', 'beyti', 'darou', 'daru', 'dar', 'daroul', 'médina', 'medina', 'madina', 'medinatoul',
            'médinatoul', 'djannatoul', 'boukhatoul', 'saré', 'sare', 'sinthiou', 'sintiou', 'sinntiou',
            'santhiou', 'santiou', 'sinthian', 'sintian', 'sintiân', 'sinthiang', 'santhie', 'gourel', 'ouro',
            'wouro', 'dara', 'daara', 'touba', 'taïba', 'taiba', 'missira', 'missirah', 'hamdallaye', 'hamdalaye',
            'baïti', 'baiti', 'bayti'}
for w in SN_HEADS:
    P.HEADS[LANG].add(w)
P.LINKING[LANG].add('&')       # 'Cité Barry & Ly'
# Given names and family names: a shortened name that keeps or drops one of
# them is a person's name cut in two, so it goes to the commune.
PERSON = set('''mamadou modou amadou ahmadou amath amat ousmane abdoulaye ablaye abdou abdoul aliou ali alassane
assane boubacar bocar bokar babacar babou ibra ibrahima ibou malick malik cheikh serigne sérigne samba demba moussa
massamba mor matar yoro alpha alfa oumar omar seydou sidi lamine madi mamour mandiaye birame birane biram ndiaga
daouda fodé bakary bakari pathé pathe paté amadi sadio thierno tierno elhadji hadji elimane mbaye ndiaye diop fall
fal sow ba bâ gueye guèye sy diallo dialo ndour faye sarr sar seck sek cissé cisse ciss sissé thiam dieng diouf kane
wade samb niang touré toure ndao lo lô ly dia kébé kebe niane sall sène sene diagne ndoye mbodj dramé drame camara
konaté coly sagna badji diatta diedhiou sané mané baldé balde barry sidibé kandé diakhaté ndiaw diaw dièye diaye
mballo sambou badiane gaye ngom sèye seye boye ndaw tall tal kâ ka ndiongue sidy mamadi njie jallow malamine senghor boucar boubou bernard'''.split())
HEADS_PLAIN = {P.plain(h) for h in SN_HEADS}
PERSON_PLAIN = {P.plain(h) for h in PERSON}
P.GENERIC[LANG] = [g for g in P.GENERIC[LANG] if g not in GENERIC_REMOVE]


# ---- avoid set ----------------------------------------------------------------
REGION_CAPITALS = ['Dakar', 'Thiès', 'Diourbel', 'Fatick', 'Kaolack', 'Kaffrine', 'Louga', 'Saint-Louis', 'Matam',
                   'Tambacounda', 'Kédougou', 'Kolda', 'Sédhiou', 'Ziguinchor']
# Never removed as a lieu's "own town": a quartier is not called "Dakar" or "Touba" alone.
REGION_CITIES = ['Touba', 'Mbacké', 'Rufisque', 'Pikine', 'Guédiawaye', 'Keur Massar', 'Mbour', 'Tivaouane',
                 'Richard-Toll', 'Joal', 'Saly', 'Diamniadio',
                 # across the borders: The Gambia, Mauritania, Mali, Guinea, Guinea-Bissau
                 'Banjul', 'Serrekunda', 'Nouakchott', 'Rosso', 'Nouadhibou', 'Bamako', 'Kayes', 'Conakry', 'Bissau']


def zone_seats(zones):
    out = {}
    for z in zones:
        nm = re.sub(r'\s*\(.*$', '', z['name'])
        out[z['key']] = 'Touba' if z['key'] == 'TBA' else ('Mbacké' if z['key'] == 'MBK' else nm)
    return out


def avoid_sets(items, zones):
    """-> (national avoid set, per-lieu own towns)."""
    seats = zone_seats(zones)
    towns = [it for it in items if it['kind'] in ('town', 'city')]
    base = set(REGION_CAPITALS) | set(REGION_CITIES) | set(seats.values()) | {split_numeral(t['officialName'])[0]
                                                                              for t in towns}
    big = {E.name_key(a) for a in REGION_CAPITALS + REGION_CITIES}
    own = {}
    for it in items:
        mine = {seats[it['zone']]}
        near = [t for t in towns if t['zone'] == it['zone'] and math.hypot(t['e'] - it['e'], t['n'] - it['n']) <= 15000]
        if near:
            mine.add(split_numeral(min(near, key=lambda t: math.hypot(t['e'] - it['e'], t['n'] - it['n']))['officialName'])[0])
        own[(it['zone'], it['index'])] = {E.name_key(m) for m in mine} - big
    return {E.name_key(a): a for a in base}, own


def tidy(plate):
    """'H.L.M.' -> 'HLM', 'S.A.E.D.' -> 'SAED' (an acronym is written without dots on a
    plate); 'PUITS' -> 'Puits' (capitals only for an acronym of three letters or fewer)."""
    out = []
    for w in plate.split(' '):
        if re.fullmatch(r'(?:[A-Z]\.){2,}', w):
            w = w.replace('.', '')
        elif len(w) > 3 and w.isupper() and w.isalpha():
            w = w.capitalize()
        out.append(w)
    return ' '.join(out)


def zkey(name):
    """Name key with the sector numeral kept: 'Liberté 2' is not the lieu 'Liberté'."""
    stem, num = split_numeral(name)
    return E.name_key(stem) + num


def hyphen_candidates(cl):
    """Runs of whole words of a hyphen-joined name that fit, for the commune to
    choose from (the shared rule keeps a hyphen compound whole). Never only weak,
    head or linking words."""
    spans = [(m.start(), m.end(), m.group()) for m in re.finditer(r"[^\s-]+", cl)]
    weak = {P.plain(w) for w in WEAK_EXTRA} | {P.plain(w) for w in P.WEAK[LANG]} | HEADS_PLAIN
    out = []
    for a in range(len(spans)):
        for b in range(a, len(spans)):
            ws = [w for _, _, w in spans[a:b + 1]]
            if P._is_link(ws[0], LANG) or P._is_link(ws[-1], LANG) or P.plain(ws[-1]) in P.BINDING:
                continue
            if a > 0 and P.plain(spans[a - 1][2]) in P.BINDING:
                continue     # never 'Georges' out of 'Saint-Georges'
            sub = cl[spans[a][0]:spans[b][1]]
            if P.fits(sub, LANG) and any(P.plain(w) not in weak and not P._is_link(w, LANG) for w in ws) \
                    and sum(ch.isalpha() for ch in sub) >= P.MIN_LETTERS and sub not in out:
                out.append(sub)
    out.sort(key=lambda c: (-P.plate_length(c), c))
    return out[:3]


def derive_all(items, zones):
    """Set on every item: name (plate), officialName, plateRule, needsCouncilChoice,
    plateCandidates, plateReason, plateSource. Returns the per-item results."""
    for it in items:
        it.setdefault('officialName', it['name'])
    stems = [split_numeral(it['officialName'])[0] for it in items]
    freq = P.word_freq(stems, LANG)
    avoid, own = avoid_sets(items, zones)
    zone_names = {}
    for it in items:   # official names (and their stems) of the lieux of each zone
        zone_names.setdefault(it['zone'], {}).setdefault(zkey(it['officialName']), set()).add(it['index'])
    for it, stem in zip(items, stems):
        off = it['officialName']
        _, num = split_numeral(off)
        av = [a for k, a in avoid.items() if k not in own[(it['zone'], it['index'])]]
        known = {stem: KNOWN[off]} if off in KNOWN else None
        budget = P.MAX_CHARS - (len(num) + 1 if num else 0)
        saved = P.MAX_CHARS
        P.MAX_CHARS = budget     # the numeral takes its share of the 12 characters
        try:
            r = P.derive(stem, LANG, freq, known=known, avoid=av, generic_extra=GENERIC_EXTRA,
                         weak_extra=WEAK_EXTRA, avoid_key=E.name_key)
        finally:
            P.MAX_CHARS = saved
        add = (lambda s_: f'{s_} {num}' if num else s_)
        if r['rule'] == 'as-is' and add(r['plate']) != P.nfc(off).strip():
            r['rule'] = 'cleaned'           # 'Plan Jaxaay 01' -> 'Plan Jaxaay 1', 'Liberté Six' -> 'Liberté 6'
        cl, _ = P.clean(stem, LANG, GENERIC_EXTRA, WEAK_EXTRA)
        words = [w for w in re.split(r'[\s-]+', P.plain(cl)) if w]
        heads = [w for w in words if w in HEADS_PLAIN]
        people = [w for w in words if w in PERSON_PLAIN or re.fullmatch(r'[a-z]\.', w)]   # 'M. Binta': an initial
        why = None
        if r['rule'] == 'distinctive':
            if heads:
                why = 'a "%s ..." name: any cut drops part of a person\'s or family\'s name' % heads[0].capitalize()
            elif people:
                why = 'holds a person\'s name (%s): any cut drops part of it' % people[0].capitalize()
            elif cl.count('-') >= 2 or ('-' in cl and ' ' in cl):
                why = 'a joined name of several quartiers: the commune chooses'
            elif any(P._is_link(w, LANG) for w in P._units(cl, LANG)):
                why = 'the parts of a "X de Y" name belong together'
        if r['rule'] in ('distinctive', 'cleaned') and not why:
            others = zone_names[it['zone']].get(zkey(add(r['plate'])), set()) - {it['index']}
            if others:
                why = 'equals the name of another lieu of the same zone'
        if why:
            r.update(rule='council', needsCouncilChoice=True, reason=why,
                     candidates=r['candidates'] or [r['plate']])
        if r['needsCouncilChoice'] and not P.fits(r['plate'], LANG) and re.search(r'\w-\w', cl):
            hy = hyphen_candidates(cl)     # 'Mermoz-Sacré-Cœur' -> Mermoz, Sacré-Cœur; 'Mboro-sur-Mer' -> Mboro
            if hy:
                r.update(plate=hy[0], candidates=hy)
        if r['needsCouncilChoice']:   # never offer 'K.' or 'I.' alone
            cs = [c for c in r['candidates'] if sum(ch.isalpha() for ch in c) >= P.MIN_LETTERS]
            if cs != r['candidates']:
                r['candidates'] = cs
                r['plate'] = cs[0] if cs else cl
        if off in COUNCIL:
            c_, why = COUNCIL[off]
            r.update(plate=c_[0], rule='council', needsCouncilChoice=True, candidates=c_, reason=why)
        # an all-capitals word in the map ("Route des PUITS", "Dougar AITHIA") is written in capitals only
        # when it is an acronym of three letters or fewer
        r['plate'] = tidy(r['plate'])
        r['candidates'] = [tidy(c) for c in r['candidates']]
        if r['rule'] == 'as-is' and add(r['plate']) != P.nfc(off).strip():
            r['rule'] = 'cleaned'
        if (r.get('reason') or '').startswith('every short form drops a qualifier'):
            r['reason'] = 'every short form drops a qualifier (Peul, Wolof, Sérère, Nord, Sud...)'
        cand = r['candidates'] or []
        it['name'] = add(r['plate'])
        it['plateRule'] = r['rule']
        it['needsCouncilChoice'] = bool(r['needsCouncilChoice'])
        for k in ('plateCandidates', 'plateReason', 'plateSource'):
            it.pop(k, None)
        if it['needsCouncilChoice']:
            it['plateCandidates'] = [add(c) for c in cand[:3]] or [it['name']]
            it['plateReason'] = r.get('reason', '')
        if r.get('source'):
            it['plateSource'] = r['source']
        it['plateOverLimit'] = not plate_ok(it['name'])
    return items
