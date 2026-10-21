#!/usr/bin/env python3
"""Tests for the Senegal reference engine: python3 -m unittest test_sn (from engine/reference).

The selftest covers the arithmetic; these tests pin the national-uniqueness
rule (SPEC 3.3): a remembered address ('Ouakam 2512') is unique in the whole
country on its own, also when many places share the name."""
import json, os, unittest

import sn_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
ZONES, LIEUX = E.Zones(), E.Lieux()
with open(os.path.join(HERE, 'vectors.json'), encoding='utf-8') as _f:
    VEC = json.load(_f)


def decode(text):
    return [f"{z}/{c['index']}" for z, c, _ in E.find(text, ZONES, LIEUX)]


class SelfTest(unittest.TestCase):
    def test_selftest(self):
        E.selftest(ZONES, LIEUX)

    def test_vectors_up_to_date(self):
        got = json.loads(json.dumps(E.vectors(ZONES, LIEUX), ensure_ascii=False))
        self.assertEqual(got, VEC)


class TheBorderDecides(unittest.TestCase):
    """SPEC 2.3: the national border decides, not the zone outlines."""

    def test_border(self):
        b = E.Border()
        self.assertLessEqual(b.limit, E.BORDER_M - 1)
        for p in [(14.6681, -17.4317), (12.5833, -16.2719), (12.556, -12.175), (16.02, -16.49), (14.667, -17.398)]:
            self.assertTrue(b.holds(*p), p)                    # Dakar, Ziguinchor, Kédougou, Saint-Louis, Gorée
        self.assertTrue(b.holds(16.5, -15.795))                # about 110 m outside the line, on the Senegal river
        across = (16.5, -15.7755)                              # about 790 m into a neighbouring country
        self.assertEqual(ZONES.lookup(*across), 'DAG')         # the zone rule alone would take it
        self.assertFalse(b.holds(*across))
        for p in [(13.4549, -16.5790), (13.31, -14.22), (11.86, -15.6), (14.45, -11.44)]:
            self.assertFalse(b.holds(*p), p)                   # points in neighbouring countries

    def test_limit_takes_off_the_simplification(self):
        b = E.Border()
        dev = E._load_json(E.BORDER)['properties']['maxDeviationM']
        self.assertEqual(b.limit, E.BORDER_M - __import__('math').ceil(dev))
        self.assertLess(os.path.getsize(E.BORDER), 1 << 20)


class SameNameNationally(unittest.TestCase):
    def test_vectors_decode_without_context(self):
        self.assertGreaterEqual(len(VEC['sameName']), 10)
        for v in VEC['sameName']:
            self.assertEqual(decode(v['typed']), [f"{v['zone']}/{v['lieu']}"], v['typed'])

    def test_two_medinas_are_two_places(self):
        dakar, zig = decode('Médina 12 150'), decode('Medina 23150')
        self.assertEqual(dakar, ['DKR/71'])
        self.assertEqual(zig, ['ZIG/155'])
        # the old context form is no longer needed, and a wrong zone is refused rather than re-routed
        self.assertEqual(decode('Medina 23 150, Ziguinchor'), ['ZIG/155'])
        self.assertEqual(decode('Medina 23 150, Dakar'), [])

    def test_one_family_per_name(self):
        f = LIEUX.families[E.name_key('Médina')]
        self.assertGreater(len({it['zone'] for it in f['lieux']}), 5)
        self.assertEqual(len({it['digits'] for it in f['lieux']}), 1)
        nums = set()
        for it in f['lieux']:
            for lo, hi in it['blocks']:
                r = set(range(lo, hi + 1))
                self.assertFalse(r & nums)
                nums |= r

    def test_spelling_variants_share_the_range(self):
        self.assertEqual(decode('Wakam 2512'), decode('Ouakam 2512'))
        self.assertEqual(decode('Darou-Salam 50 860'), ['TBA/54'])
        self.assertEqual(decode('Daru Salaam 26690'), ['PKN/10'])

    def test_unissued_number_is_refused(self):
        self.assertEqual(decode('Ouakam 4512'), [])   # outside Ouakam's block 1000-3399

    def test_trailing_numeral(self):
        self.assertEqual(decode('HLM 5 17 395'), ['DKR/54'])
        self.assertEqual(decode('HLM 17395'), ['DKR/54'])     # the numeral may be left out
        self.assertEqual(decode('HLM 3 17395'), [])           # but a wrong numeral is refused
        self.assertEqual(decode('H.L.M. Un 11 000'), ['DKR/44'])   # official 'H.L.M. Un' = plate 'HLM 1'

    def test_check_letter_catches_slip_into_other_same_named_lieu(self):
        for v in VEC['sameName']:
            sl = v['slipIntoOtherLieu']
            if sl:
                self.assertEqual(decode(sl['typed']), [], sl)

    def test_canonical_binds_lieu(self):
        v = VEC['sameName'][0]
        self.assertEqual(E.validate(v['canonical'], ZONES, LIEUX), (True, 'address'))
        other = VEC['sameName'][1]   # same name, other lieu: its number is not in this lieu's block
        forged = v['canonical'].replace(f"-{v['zone']}-{v['lieu']:04d}-", f"-{other['zone']}-{other['lieu']:04d}-")
        self.assertFalse(E.validate(forged, ZONES, LIEUX)[0])

    def test_new_same_named_lieu_takes_spare_block(self):
        lx = E.Lieux()
        f = lx.families[E.name_key('Médina')]
        before = {(it['zone'], it['index']): [list(b) for b in it['blocks']] for it in f['lieux']}
        top = lx.spare_top(E.name_key('Médina'))
        new = lx.add_lieu({'zone': 'KLD', 'index': 9999, 'name': 'Médina', 'kind': 'village', 'compounds': 120,
                           'e': 0, 'n': 0, 'aliases': []})
        self.assertEqual(new['family'], f['id'])
        self.assertEqual(new['blocks'][0][0], top + 1)
        for it in f['lieux'][:-1]:
            self.assertEqual(it['blocks'], before[(it['zone'], it['index'])])   # never renumbered


class PlateNames(unittest.TestCase):
    """SPEC 3.2.1: the name in the address is a short plate name (<= 12
    characters, <= 2 words); the official name is kept and still decodes."""

    def test_every_plate_keeps_the_limit_or_is_flagged(self):
        for it in LIEUX.items:
            self.assertTrue(E.plate_ok(it['placeWord']) or it.get('needsCouncilChoice'), it['placeWord'])

    def test_engine_refuses_a_long_plate(self):
        lx = E.Lieux()
        with self.assertRaises(ValueError):
            lx.add_lieu({'zone': 'DKR', 'index': 9999, 'name': 'Parcelles Assainies', 'kind': 'suburb',
                         'compounds': 10, 'e': 0, 'n': 0, 'aliases': []})
        with self.assertRaises(ValueError):
            E.allocate_families([{'zone': 'DKR', 'index': 1, 'name': 'Keur Mbaye Fal', 'compounds': 5}])

    def test_long_official_name_to_plate(self):
        for v in VEC['plateNames']['long']:
            self.assertLessEqual(v['plateLength'], 12)
            self.assertEqual(decode(v['remembered']), [v['lieu']], v['remembered'])
            num = v['remembered'][len(v['plateName']):].replace(' ', '')
            self.assertEqual(decode(f"{v['officialName']} {num}"), [v['lieu']], v['officialName'])
        liberte = VEC['plateNames']['long'][0]
        self.assertEqual((liberte['officialName'], liberte['plateName']), ('S.I.C.A.P. Liberté Six', 'Liberté 6'))

    def test_collision_after_shortening_decodes_to_two_places(self):
        for a, b in VEC['plateNames']['collide']:
            self.assertEqual(E.name_key(a['plateName']), E.name_key(b['plateName']))
            self.assertNotEqual(E.name_key(a['officialName']), E.name_key(b['officialName']))
            self.assertEqual(a['family'], b['family'])
            self.assertEqual(decode(a['remembered']), [a['lieu']])
            self.assertEqual(decode(b['remembered']), [b['lieu']])


if __name__ == '__main__':
    unittest.main()
