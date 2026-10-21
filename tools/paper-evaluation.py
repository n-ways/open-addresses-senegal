#!/usr/bin/env python3
"""Measure the properties reported in the paper's evaluation chapter, from the
published registry and the reference engine alone:

  - uniqueness of the canonical and remembered forms over the whole registry;
  - context-free decoding: every remembered form resolved by the engine's find()
    with no zone and no position, compared with the registry row;
  - number lengths and remembered-form lengths;
  - what a one-digit slip in a remembered number lands on;
  - detection of single substitutions and adjacent transpositions by the check
    letter, over the payloads of a sample of issued addresses;
  - the round-trip error of spot codes on random points;
  - locality: how far apart compounds with consecutive numbers are.

  python3 tools/paper-evaluation.py [--sample 100000] > docs/figures/data/evaluation.json

Standard library only. Reads registry/*.csv.gz and registry/anchors once (about two minutes)."""
import argparse, csv, glob, gzip, json, math, os, random, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'engine', 'reference'))
import sn_engine as E  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=int, default=100000, help='addresses used for the slip and check-letter tests')
    ap.add_argument('--seed', type=int, default=20261020)
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    zones, lieux = E.Zones(), E.Lieux()
    by_ref = {f"{it['zone']}-{it['index']:04d}": it for it in lieux.items}

    canon, remem = set(), set()
    dup_canon = dup_remem = 0
    issued = set()          # (family key, number)
    rows = []               # (lieu ref, number, remembered)
    lengths, digits = [], {3: 0, 4: 0, 5: 0}
    decoded_ok = decoded_none = decoded_many = decoded_wrong = 0
    for f in sorted(glob.glob(os.path.join(ROOT, 'registry', '*.csv.gz'))):
        if os.path.basename(f).startswith('lieux'):
            continue
        for r in csv.DictReader(gzip.open(f, 'rt', encoding='utf-8')):
            if r['canonical'] in canon:
                dup_canon += 1
            canon.add(r['canonical'])
            k = E.fold(r['remembered'])
            if k in remem:
                dup_remem += 1
            remem.add(k)
            lieu = by_ref[r['lieu']]
            n = int(r['number'])
            issued.add((lieu['nameKey'], n))
            digits[len(r['number'])] += 1
            lengths.append(len(r['remembered']))
            rows.append((r['lieu'], n))
            hits = E.find(r['remembered'], zones, lieux)
            if not hits:
                decoded_none += 1
            elif len(hits) > 1:
                decoded_many += 1
            elif f"{hits[0][0]}-{hits[0][1]['index']:04d}" == r['lieu'] and hits[0][2] == n:
                decoded_ok += 1
            else:
                decoded_wrong += 1
    total = len(rows)
    lengths.sort()

    # One-digit slips in the remembered number (same length, no leading zero).
    slip = {'sameLieuIssued': 0, 'otherLieuIssued': 0, 'otherLieuUnissued': 0, 'sameLieuUnissued': 0,
            'noBlock': 0}
    letter_single = letter_swap = letter_single_n = letter_swap_n = 0
    for ref, n in rnd.sample(rows, min(a.sample, total)):
        lieu = by_ref[ref]
        key, s = lieu['nameKey'], str(n)
        for i in range(len(s)):
            for c in '0123456789':
                if c == s[i] or (i == 0 and c == '0'):
                    continue
                m = int(s[:i] + c + s[i + 1:])
                owner = lieux.owner(key, m)
                if owner is None:
                    slip['noBlock'] += 1
                elif owner is lieu:
                    slip['sameLieuIssued' if (key, m) in issued else 'sameLieuUnissued'] += 1
                else:
                    slip['otherLieuIssued' if (key, m) in issued else 'otherLieuUnissued'] += 1
        # Check letter over the payload: family (5 digits) + number (5 digits).
        payload = f"{lieu['family']:05d}{n:05d}"
        good = E.mod11_2(payload)
        for i in range(10):
            for c in '0123456789':
                if c != payload[i]:
                    letter_single_n += 1
                    letter_single += E.mod11_2(payload[:i] + c + payload[i + 1:]) != good
            if i < 9 and payload[i] != payload[i + 1]:
                letter_swap_n += 1
                sw = payload[:i] + payload[i + 1] + payload[i] + payload[i + 2:]
                letter_swap += E.mod11_2(sw) != good
    slips = sum(slip.values())

    # Spot codes: random points inside each zone's frame that the zone lookup keeps.
    errs = {}
    for key, z in zones.by_key.items():
        worst, n_ok = 0.0, 0
        while n_ok < 400:
            e = z['originE'] + rnd.random() * min(z['frameMetres'], z['cellMetres'] * 10 ** z['digits'])
            nn = z['originN'] + rnd.random() * min(z['frameMetres'], z['cellMetres'] * 10 ** z['digits'])
            lat, lon = E.utm_inverse(e, nn)
            code = E.encode_spot(lat, lon, zones, key)
            la2, lo2, _ = E.decode_spot(code, zones)
            e2, n2 = E.utm_forward(la2, lo2)
            worst = max(worst, math.hypot(e2 - e, n2 - nn))
            n_ok += 1
        errs[key] = {'cell': z['cellMetres'], 'maxError': round(worst, 3),
                     'bound': round(z['cellMetres'] * math.sqrt(2) / 2, 3)}

    # Locality: distance between compounds with consecutive numbers in a place, against
    # the distance between two compounds of the same place drawn at random.
    pos = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'registry', 'anchors', '*.csv.gz'))):
        base = os.path.basename(f)
        main = csv.DictReader(gzip.open(os.path.join(ROOT, 'registry', base), 'rt', encoding='utf-8'))
        for r, an in zip(main, csv.DictReader(gzip.open(f, 'rt', encoding='utf-8'))):
            pos.setdefault(r['lieu'], []).append((int(r['number']), *E.utm_forward(float(an['anchor_lat']),
                                                                                   float(an['anchor_lng']))))
    consec, rand_ = [], []
    for pts in pos.values():
        if len(pts) < 2:
            continue
        pts.sort()
        consec += [math.hypot(v[1] - u[1], v[2] - u[2]) for u, v in zip(pts, pts[1:])]
        for _ in range(len(pts) - 1):
            u, v = rnd.sample(pts, 2)
            rand_.append(math.hypot(v[1] - u[1], v[2] - u[2]))
    consec.sort()
    rand_.sort()

    def q(v, p):
        return round(v[int(p * (len(v) - 1))], 1)

    out = {
        'addresses': total,
        'uniqueCanonical': len(canon), 'duplicateCanonical': dup_canon,
        'uniqueRemembered': len(remem), 'duplicateRemembered': dup_remem,
        'decode': {'exact': decoded_ok, 'none': decoded_none, 'several': decoded_many, 'wrong': decoded_wrong},
        'digits': digits,
        'rememberedLength': {'min': lengths[0], 'median': statistics.median(lengths),
                             'p95': lengths[int(0.95 * total)], 'p99': lengths[int(0.99 * total)],
                             'max': lengths[-1], 'atMost12': sum(1 for x in lengths if x <= 12),
                             'atMost16': sum(1 for x in lengths if x <= 16)},
        'slips': {'sampled': min(a.sample, total), 'variants': slips, **slip,
                  'shares': {k: round(v / slips, 4) for k, v in slip.items()}},
        'checkLetter': {'single': [letter_single, letter_single_n], 'adjacentSwap': [letter_swap, letter_swap_n]},
        'spot': errs,
        'locality': {'pairs': len(consec), 'consecutiveMedian': q(consec, 0.5), 'consecutiveP90': q(consec, 0.9),
                     'randomMedian': q(rand_, 0.5), 'randomP90': q(rand_, 0.9)},
        'seed': a.seed,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print()


if __name__ == '__main__':
    main()
