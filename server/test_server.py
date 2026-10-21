"""Tests of the registry server: python3 -m unittest server.test_server

The fixture (server/testdata/registry) is the published registry cut to one
zone, Salémata (SLM, 5,839 addresses), with the full lieux table, so the
national name ranges and their spare space are real. testdata/parity.json
holds 62 issue cases and the answers the N-Ways issuer's own code (its
nearest-lieu rule, insertion, address forms and compound profile) gave for
them against the same state, issued one after another.
"""
import csv
import gzip
import io
import json
import os
import shutil
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request

from . import core, db
from .api import make_server
from .service import Config, Service

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, 'testdata', 'registry')
PARITY = os.path.join(HERE, 'testdata', 'parity.json')
KEY = 'test-key-1'


def quiet(*_):
    pass


def unzip(path):
    with gzip.open(path, 'rb') as f:
        return f.read()


class Base(unittest.TestCase):
    """An imported copy of the fixture per test class, served on a free port."""
    keys = [KEY]
    per_day = 1000
    cors = ['https://example.org']

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='sn-server-')
        cls.db = os.path.join(cls.tmp, 'addresses.sqlite')
        shutil.copy(cls.imported(), cls.db)
        cls.svc = Service(Config(db_path=cls.db, issue_keys=cls.keys, per_day=cls.per_day, cors=cls.cors, access_log=False))
        cls.srv = make_server(cls.svc, '127.0.0.1', 0)
        cls.base = f'http://127.0.0.1:{cls.srv.server_address[1]}'
        cls.thread = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.svc.release()
        shutil.rmtree(cls.tmp)

    _imported = None

    @staticmethod
    def imported():
        if Base._imported is None:
            d = tempfile.mkdtemp(prefix='sn-fixture-')
            p = os.path.join(d, 'fixture.sqlite')
            db.import_registry(FIXTURE, p, log=quiet)
            Base._imported = p
        return Base._imported

    def call(self, method, path, body=None, key=KEY, headers=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.base + path, data=data, method=method)
        if data is not None:
            req.add_header('Content-Type', 'application/json')
        if key:
            req.add_header('Authorization', f'Bearer {key}')
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read()), r.headers
        except urllib.error.HTTPError as e:
            with e:
                return e.code, json.loads(e.read()), e.headers

    def get(self, path, **params):
        return self.call('GET', path + ('?' + urllib.parse.urlencode(params) if params else ''))

    def error(self, res, status, code):
        st, body, _ = res
        self.assertEqual(st, status, body)
        self.assertEqual(set(body), {'error'})
        self.assertEqual(body['error']['code'], code)
        self.assertTrue(body['error']['message'])
        return body['error']


def man_anchors(out):
    with open(os.path.join(out, 'anchors', 'MANIFEST.json'), encoding='utf-8') as f:
        return json.load(f)


def fixture_rows():
    return list(csv.DictReader(io.StringIO(unzip(os.path.join(FIXTURE, 'SLM.csv.gz')).decode('utf-8'))))


# ---------------------------------------------------------------- import and export
class ImportExport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='sn-io-')

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_round_trip_is_byte_identical(self):
        p = os.path.join(self.tmp, 'a.sqlite')
        self.assertEqual(db.import_registry(FIXTURE, p, log=quiet), 5839)
        out = os.path.join(self.tmp, 'out')
        man = db.export_registry(p, out, log=quiet)
        for name in ('SLM.csv', 'lieux.csv'):
            self.assertEqual(unzip(os.path.join(FIXTURE, name + '.gz')), unzip(os.path.join(out, name + '.gz')), name)
        with open(os.path.join(out, 'lieux.csv'), 'rb') as f:
            self.assertEqual(f.read(), unzip(os.path.join(FIXTURE, 'lieux.csv.gz')))
        with open(os.path.join(FIXTURE, 'MANIFEST.json'), encoding='utf-8') as f:
            want = json.load(f)
        self.assertEqual(man['sha256'], want['sha256'])
        self.assertEqual((man['addresses'], man['byZone']), (want['addresses'], want['byZone']))
        self.assertEqual(unzip(os.path.join(FIXTURE, 'anchors', 'SLM.csv.gz')), unzip(os.path.join(out, 'anchors', 'SLM.csv.gz')))
        with open(os.path.join(FIXTURE, 'anchors', 'MANIFEST.json'), encoding='utf-8') as f:
            self.assertEqual(json.load(f)['sha256'], man_anchors(out)['sha256'])
        with open(os.path.join(out, 'SLM.csv.gz'), 'rb') as f:
            head = f.read(10)
        self.assertEqual(head[3] & 0x08, 0, 'gzip -n: no file name')
        self.assertEqual(head[4:8], b'\0\0\0\0', 'gzip -n: no time')

    def test_reimport_is_safe(self):
        p = os.path.join(self.tmp, 'a.sqlite')
        db.import_registry(FIXTURE, p, log=quiet)
        db.import_registry(FIXTURE, p, log=quiet)
        con = db.connect(p)
        self.assertEqual(db.code_count(con), 5839)
        self.assertEqual(con.execute('SELECT count(*) FROM lieux').fetchone()[0], 14997)
        if db.has_rtree(con):
            self.assertEqual(con.execute('SELECT count(*) FROM codes_rtree').fetchone()[0], 5839)
        con.close()

    def _copy_fixture(self):
        d = os.path.join(self.tmp, 'reg')
        shutil.copytree(FIXTURE, d)
        return d

    def test_refuses_wrong_sha(self):
        d = self._copy_fixture()
        mp = os.path.join(d, 'MANIFEST.json')
        with open(mp, encoding='utf-8') as f:
            m = json.load(f)
        m['sha256']['SLM.csv'] = '0' * 64
        with open(mp, 'w', encoding='utf-8') as f:
            json.dump(m, f)
        p = os.path.join(self.tmp, 'a.sqlite')
        db.import_registry(FIXTURE, p, log=quiet)
        with self.assertRaisesRegex(db.RegistryError, 'SHA-256'):
            db.import_registry(d, p, log=quiet)
        self.assertEqual(db.count_codes(p), 5839, 'a refused import changes nothing')

    def test_refuses_wrong_total(self):
        d = self._copy_fixture()
        mp = os.path.join(d, 'MANIFEST.json')
        with open(mp, encoding='utf-8') as f:
            m = json.load(f)
        m['byZone']['SLM'] += 1
        m['addresses'] += 1
        with open(mp, 'w', encoding='utf-8') as f:
            json.dump(m, f)
        with self.assertRaisesRegex(db.RegistryError, 'rows|count'):
            db.import_registry(d, os.path.join(self.tmp, 'b.sqlite'), log=quiet)
        shutil.rmtree(os.path.join(d, 'anchors'))
        with self.assertRaisesRegex(db.RegistryError, 'rows'):
            db.import_registry(d, os.path.join(self.tmp, 'c.sqlite'), log=quiet)

    def test_anchors_are_checked(self):
        d = self._copy_fixture()
        src = os.path.join(d, 'anchors', 'SLM.csv.gz')
        lines = unzip(src).split(b'\n')
        lines[1], lines[2] = lines[2], lines[1]
        with gzip.open(src, 'wb') as f:
            f.write(b'\n'.join(lines))
        with self.assertRaisesRegex(db.RegistryError, 'not in step'):
            db.import_registry(d, os.path.join(self.tmp, 'd.sqlite'), log=quiet)

    def test_without_anchors_entrances_serve(self):
        d = self._copy_fixture()
        shutil.rmtree(os.path.join(d, 'anchors'))
        said = []
        p = os.path.join(self.tmp, 'e.sqlite')
        self.assertEqual(db.import_registry(d, p, log=said.append), 5839)
        self.assertTrue(any('anchors' in m for m in said))
        con = db.connect(p)
        self.assertEqual(db.meta(con, 'anchors'), 'entrance')
        con.close()

    def test_refuses_other_country(self):
        d = self._copy_fixture()
        mp = os.path.join(d, 'MANIFEST.json')
        with open(mp, encoding='utf-8') as f:
            m = json.load(f)
        m['country'] = 'XX'
        with open(mp, 'w', encoding='utf-8') as f:
            json.dump(m, f)
        with self.assertRaisesRegex(db.RegistryError, 'serves SN'):
            db.import_registry(d, os.path.join(self.tmp, 'c.sqlite'), log=quiet)

    def test_csv_quoting_matches_the_exporter(self):
        self.assertEqual(db._line(['a', 'b,c', 'say "x"', ' lead', '']), b'a,"b,c","say ""x"""," lead",\n')


# ---------------------------------------------------------------- reads
class Reads(Base):
    rows = fixture_rows()

    def test_health_and_info(self):
        st, h, _ = self.get('/v1/health')
        self.assertEqual((st, h['status'], h['country'], h['codes']), (200, 'ok', 'SN', 5839))
        self.assertEqual(h['registryExported'], '2026-10-20T15:57:33Z')
        st, i, _ = self.get('/v1/info')
        self.assertEqual((i['zones'], i['areas'], i['codes']['total']), (46, 14997, 5839))
        self.assertEqual(i['credit'], core.CREDIT)
        self.assertTrue(i['issuing']['enabled'])

    def test_card_has_every_registry_column(self):
        r = self.rows[123]
        st, c, _ = self.get('/v1/codes/' + r['canonical'])
        self.assertEqual(st, 200)
        self.assertEqual(c['registry'], r)
        self.assertEqual((c['machine'], c['remembered'], c['written'], c['spotCode']),
                         (r['canonical'], r['remembered'], r['written'], r['spot_code']))
        self.assertEqual(c['zone']['key'], 'SLM')
        self.assertEqual(c['area']['id'], r['lieu'])
        self.assertNotIn(' · ' + r['check'], c['written'], 'people never see the check letter')
        st, c2, _ = self.get('/v1/codes/' + r['canonical'].lower())
        self.assertEqual(c2['machine'], r['canonical'])

    def test_card_errors(self):
        r = self.rows[0]
        wrong = r['canonical'][:-1] + ('F' if r['canonical'][-1] != 'F' else 'H')
        self.error(self.get('/v1/codes/' + wrong), 400, 'invalid_code')
        self.error(self.get('/v1/codes/SN-XXX-0000-101-Q'), 400, 'invalid_code')
        self.error(self.get('/v1/codes/hello'), 400, 'invalid_code')
        lieu = self.svc.reg.lieu('SLM-0000')
        free = next(n for n in range(lieu['blocks'][0][0], lieu['blocks'][0][1]) if
                    not any(x['lieu'] == 'SLM-0000' and int(x['number']) == n for x in self.rows))
        m = self.svc.reg.forms(lieu, free)['canonical']
        self.error(self.get('/v1/codes/' + m), 404, 'not_found')

    def test_find_remembered_as_typed(self):
        r = self.rows[200]
        for q in (r['remembered'], r['remembered'].upper(), r['remembered'].lower(), '  ' + r['remembered'].replace(' ', '   ') + ' ',
                  core.fold(r['remembered']), r['remembered'].replace(' ', ''), r['written'], r['remembered'] + ', Salémata'):
            st, f, _ = self.get('/v1/find', q=q)
            self.assertEqual(st, 200, q)
            self.assertEqual(f['kind'], 'remembered')
            self.assertEqual([m['machine'] for m in f['matches']], [r['canonical']], q)

    def test_find_machine_spot_and_errors(self):
        r = self.rows[300]
        st, f, _ = self.get('/v1/find', q=r['canonical'])
        self.assertEqual((st, f['kind'], f['matches'][0]['machine']), (200, 'machine', r['canonical']))
        st, f, _ = self.get('/v1/find', q=r['spot_code'])
        self.assertEqual((st, f['kind']), (200, 'spot'))
        self.assertEqual(f['matches'][0]['machine'], r['canonical'])
        wrong = r['canonical'][:-1] + ('F' if r['canonical'][-1] != 'F' else 'H')
        self.error(self.get('/v1/find', q=wrong), 400, 'invalid_code')
        self.error(self.get('/v1/find'), 400, 'bad_request')
        self.error(self.get('/v1/find', q='Nowhere At All 12345'), 404, 'not_found')
        self.error(self.get('/v1/find', q='SLM 0001 0001'), 404, 'not_found')
        self.error(self.get('/v1/find', q='SLM 1 1'), 404, 'not_found')

    def test_find_number_in_range_not_issued(self):
        lieu = self.svc.reg.lieu('SLM-0000')
        used = {int(x['number']) for x in self.rows if x['lieu'] == 'SLM-0000'}
        free = next(n for n in range(lieu['blocks'][0][0], lieu['blocks'][0][1]) if n not in used)
        e = self.error(self.get('/v1/find', q=f"{lieu['placeWord']} {free}"), 404, 'not_found')
        self.assertIn('range of', e['message'])

    def test_at_found_and_none(self):
        r = self.rows[400]
        lat, lng = float(r['entrance_lat']), float(r['entrance_lng'])
        st, a, _ = self.get('/v1/at', lat=lat + 5 / 111320, lng=lng)
        self.assertEqual((st, a['status'], a['code']['machine']), (200, 'found', r['canonical']))
        self.assertAlmostEqual(a['distanceM'], 5.0, delta=0.2)
        far = None
        for dx in range(1, 50):
            la = lat + dx * 30 / 111320
            if not db.near(self.svc.con(), la, lng, 12.5, 1):
                far = la
                break
        st, a, _ = self.get('/v1/at', lat=far, lng=lng)
        self.assertEqual((st, a['status']), (200, 'none'))
        self.assertEqual(a['zone']['key'], 'SLM')
        self.assertTrue(a['area']['id'].startswith('SLM-'))
        self.error(self.get('/v1/at', lat=48.85, lng=2.35), 422, 'outside')
        self.error(self.get('/v1/at', lat='x', lng=1), 400, 'bad_request')
        self.error(self.get('/v1/at', lat=91, lng=1), 400, 'bad_request')

    def test_near(self):
        r = self.rows[500]
        lat, lng = float(r['entrance_lat']), float(r['entrance_lng'])
        st, n, _ = self.get('/v1/near', lat=lat, lng=lng, radius=200, limit=10)
        self.assertEqual(st, 200)
        self.assertEqual(n['codes'][0]['machine'], r['canonical'])
        ds = [c['distanceM'] for c in n['codes']]
        self.assertEqual(ds, sorted(ds))
        self.assertTrue(all(d <= 200 for d in ds) and len(ds) <= 10)
        self.error(self.get('/v1/near', lat=lat, lng=lng, radius=501), 400, 'bad_request')
        self.error(self.get('/v1/near', lat=lat, lng=lng, limit=101), 400, 'bad_request')

    def test_verify(self):
        r = self.rows[600]
        st, v, _ = self.get('/v1/verify', code=r['canonical'])
        self.assertEqual((st, v['valid'], v['issued'], v['status']), (200, True, True, 'provisional'))
        wrong = r['canonical'][:-1] + ('F' if r['canonical'][-1] != 'F' else 'H')
        st, v, _ = self.get('/v1/verify', code=wrong)
        self.assertEqual((v['valid'], v['issued']), (False, False))
        self.assertIn('check letter', v['reason'].lower())
        st, v, _ = self.get('/v1/verify', code=r['spot_code'])
        self.assertEqual((v['kind'], v['valid']), ('spot', True))
        self.error(self.get('/v1/verify'), 400, 'bad_request')

    def test_spot(self):
        with open(os.path.join(core.ENGINE_DIR, 'vectors.json'), encoding='utf-8') as f:
            vec = json.load(f)['spot']
        for v in vec:
            st, s, _ = self.get('/v1/spot', lat=v['lat'], lng=v['lon'])
            self.assertEqual((st, s['spotCode']), (200, v['code']))
            st, d, _ = self.get('/v1/spot/decode', code=v['code'])
            self.assertEqual([round(d['lat'], 6), round(d['lng'], 6)], v['decoded'])
        self.error(self.get('/v1/spot/decode', code='DKR 12 34'), 400, 'invalid_code')
        self.error(self.get('/v1/spot/decode', code='QQQ 1234 5678'), 400, 'invalid_code')
        self.error(self.get('/v1/spot/decode'), 400, 'bad_request')
        self.error(self.get('/v1/spot', lat=48.85, lng=2.35), 422, 'outside')

    def test_plus_code_matches_the_issuer(self):
        # SN-DKR-0080-2512-J on the N-Ways card: entrance 14.7247067, -17.4849374, Plus Code 7C64PGF8+V2P
        self.assertEqual(core.plus_code(14.7247067, -17.4849374), '7C64PGF8+V2P')
        self.assertEqual(core.plus_code(14.7383683, -17.5167533), '7C64PFQM+87X')

    def test_zones_and_areas(self):
        st, z, _ = self.get('/v1/zones')
        self.assertEqual((st, z['count']), (200, 46))
        slm = next(x for x in z['zones'] if x['key'] == 'SLM')
        self.assertEqual(slm['codes'], 5839)
        st, z, _ = self.get('/v1/zones/slm')
        self.assertEqual(sum(a['codes'] for a in z['areaList']), 5839)
        self.error(self.get('/v1/zones/QQQ'), 404, 'not_found')
        st, a, _ = self.get('/v1/areas/SLM-0046')
        self.assertEqual((st, a['plateName'], a['blocks'][0]), (200, 'Kadioré', [250, 269]))
        self.assertEqual(a['blockUse'][0]['used'], a['codes']['total'])
        self.error(self.get('/v1/areas/SLM-9999'), 404, 'not_found')
        st, f, _ = self.get('/v1/areas', name='kadiore')
        self.assertIn('SLM-0046', [x['id'] for x in f['areas']])
        st, f, _ = self.get('/v1/areas', name='Edine')
        ids = [x['id'] for x in f['areas']]
        self.assertTrue({'SLM-0023', 'SLM-0024'} <= set(ids))
        self.error(self.get('/v1/areas'), 400, 'bad_request')

    def test_paging(self):
        seen, after = [], ''
        while True:
            st, p, _ = self.get('/v1/zones/SLM/codes', after=after, limit=1000)
            self.assertEqual(st, 200)
            seen += [c['machine'] for c in p['codes']]
            if not p['next']:
                break
            after = p['next']
        self.assertEqual(seen, sorted(r['canonical'] for r in self.rows))
        self.error(self.get('/v1/zones/SLM/codes', limit=0), 400, 'bad_request')
        self.error(self.get('/v1/zones/QQQ/codes'), 404, 'not_found')

    def test_routing_errors_and_cors(self):
        self.error(self.get('/v1/nothing'), 404, 'not_found')
        self.error(self.call('DELETE', '/v1/codes/SN-SLM-0000-101-Q'), 405, 'method_not_allowed')
        st, _, h = self.call('GET', '/v1/health', headers={'Origin': 'https://example.org'})
        self.assertEqual(h['Access-Control-Allow-Origin'], 'https://example.org')
        st, _, h = self.call('GET', '/v1/health', headers={'Origin': 'https://other.example'})
        self.assertIsNone(h['Access-Control-Allow-Origin'])
        req = urllib.request.Request(self.base + '/v1/codes', method='OPTIONS', headers={'Origin': 'https://example.org'})
        with urllib.request.urlopen(req) as r:
            self.assertEqual(r.status, 204)


class Official(Base):
    """An address the commune numbered is found by its official address."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        con = sqlite3.connect(cls.db)
        con.execute("UPDATE codes SET official_address = '12 Rue de la Mairie', official_key = '12 rue de la mairie', "
                    "coverage = 'official' WHERE canonical = 'SN-SLM-0000-101-Q'")
        con.commit()
        con.close()

    def test_find_official(self):
        st, f, _ = self.get('/v1/find', q='12 RUE DE LA MAIRIE')
        self.assertEqual((st, f['kind'], f['matches'][0]['machine']), (200, 'official', 'SN-SLM-0000-101-Q'))
        self.assertEqual(f['matches'][0]['officialAddress'], '12 Rue de la Mairie')


# ---------------------------------------------------------------- issuing
class ReadOnly(Base):
    keys = []

    def test_read_only_refuses_writes(self):
        self.error(self.call('POST', '/v1/codes', {'lat': 12.6, 'lng': -12.8}), 403, 'read_only')
        self.error(self.call('PATCH', '/v1/codes/SN-SLM-0000-101-Q', {'status': 'confirmed'}), 403, 'read_only')


class Parity(Base):
    """Issued one after another, every case gets exactly the issuer's answer."""

    def test_parity_with_the_issuer(self):
        with open(PARITY, encoding='utf-8') as f:
            cases = json.load(f)
        blocks_seen = 0
        for i, c in enumerate(cases):
            cs, want = c['case'], c['issuer']
            body = {'lat': cs['lat'], 'lng': cs['lng']}
            if cs.get('of'):
                body['of'] = cs['of']
            if cs.get('outline'):
                body['outline'] = cs['outline']
            st, got, _ = self.call('POST', '/v1/codes', body)
            if 'error' in want:
                self.assertEqual(got['error']['code'], want['error'], (i, cs, got))
                continue
            self.assertEqual(st, 201, (i, cs, got))
            self.assertEqual((got['area']['id'], got['number'], got['machine'], got['remembered'], got['written']),
                             (want['lieu'], want['number'], want['canonical'], want['remembered'], want['written']), (i, cs))
            reg = got['registry']
            self.assertEqual((reg['class'], reg['use'], reg['kind'], int(reg['structures']), float(reg['floor_area_m2'])),
                             (want['class'], want['use'], want['kind'], want['structures'], float(want['floorAreaM2'])), (i, cs))
            self.assertEqual((reg['status'], reg['issued']), ('provisional', 'on-demand'))
            blocks_seen += len(want.get('newBlocks') or [])
        self.assertGreaterEqual(blocks_seen, 2, 'the cases add extension blocks')
        # The new blocks are frozen: in the database, in a restarted service, and in an export.
        lieu = self.svc.reg.lieu('SLM-0046')
        self.assertEqual(lieu['blocks'], [[250, 269], [270, 279], [280, 289]])
        again = Service(Config(db_path=self.db, issue_keys=[KEY]))
        self.assertEqual(again.reg.lieu('SLM-0046')['blocks'], lieu['blocks'])
        again.release()
        out = os.path.join(self.tmp, 'export')
        man = db.export_registry(self.db, out, log=quiet)
        self.assertEqual(man['byZone']['SLM'], 5839 + 60)
        lieux = {r['lieu']: r for r in csv.DictReader(io.StringIO(unzip(os.path.join(out, 'lieux.csv.gz')).decode()))}
        self.assertEqual(lieux['SLM-0046']['blocks'], '250-269|270-279|280-289')
        rows = list(csv.DictReader(io.StringIO(unzip(os.path.join(out, 'SLM.csv.gz')).decode())))
        keys = [(int(lieux[r['lieu']]['family']), int(r['number'])) for r in rows]
        self.assertEqual(keys, sorted(keys), 'rows by name family, then number')
        # ...and that export imports again, with its own manifest, to the same state.
        p2 = os.path.join(self.tmp, 'again.sqlite')
        self.assertEqual(db.import_registry(out, p2, log=quiet), 5899)
        out2 = os.path.join(self.tmp, 'export2')
        db.export_registry(p2, out2, log=quiet)
        for name in ('SLM.csv', 'lieux.csv', 'anchors/SLM.csv'):
            self.assertEqual(unzip(os.path.join(out, name + '.gz')), unzip(os.path.join(out2, name + '.gz')))


class Issuing(Base):
    rows = fixture_rows()

    def free_point(self, i=0):
        r = self.rows[1000 + i * 37]
        lat, lng = float(r['entrance_lat']), float(r['entrance_lng'])
        for k in range(1, 400):
            la = lat + k * 9 / 111320
            if self.svc.reg.zone_at(la, lng) == 'SLM' and not db.near(self.svc.con(), la, lng, 30, 1):
                return la, lng
        raise AssertionError('no free point')

    def square(self, lat, lng, side):
        h = side / 2
        dl, dg = h / 111320, h / (111320 * 0.976)
        return [[lng - dg, lat - dl], [lng + dg, lat - dl], [lng + dg, lat + dl], [lng - dg, lat + dl], [lng - dg, lat - dl]]

    def test_auth(self):
        self.error(self.call('POST', '/v1/codes', {'lat': 12.6, 'lng': -12.8}, key=None), 401, 'unauthorized')
        self.error(self.call('POST', '/v1/codes', {'lat': 12.6, 'lng': -12.8}, key='nope'), 401, 'unauthorized')

    def test_duplicates_are_refused(self):
        r = self.rows[50]
        lat, lng = float(r['entrance_lat']), float(r['entrance_lng'])
        e = self.error(self.call('POST', '/v1/codes', {'lat': lat + 2 / 111320, 'lng': lng}), 409, 'exists')
        self.assertEqual(e['existing']['machine'], r['canonical'])
        la, lo = self.free_point(1)
        st, c, _ = self.call('POST', '/v1/codes', {'lat': la, 'lng': lo, 'outline': self.square(la, lo, 12)})
        self.assertEqual(st, 201, c)
        e = self.error(self.call('POST', '/v1/codes', {'lat': la, 'lng': lo}), 409, 'exists')
        self.assertEqual(e['existing']['machine'], c['machine'])
        # a point inside the outline, 5 m from its centre: the outline holds it
        e = self.error(self.call('POST', '/v1/codes', {'lat': la + 5 / 111320, 'lng': lo}), 409, 'exists')
        self.assertEqual(e['existing']['machine'], c['machine'])
        # an outline over most of the first one, centred 6 m away
        la2 = la + 4 / 111320
        st, _, _ = self.get('/v1/at', lat=la2 + 7 / 111320, lng=lo)
        e = self.error(self.call('POST', '/v1/codes', {'lat': la2 + 7 / 111320, 'lng': lo,
                                                        'outline': self.square(la2, lo, 12)}), 409, 'exists')
        self.assertEqual(e['existing']['machine'], c['machine'])
        st, a, _ = self.get('/v1/at', lat=la + 3 / 111320, lng=lo)
        self.assertEqual((a['status'], a['code']['machine']), ('found', c['machine']))

    def test_issue_errors(self):
        la, lo = self.free_point(2)
        e = self.error(self.call('POST', '/v1/codes', {'lat': la, 'lng': lo, 'outline': self.square(la, lo, 3)}), 422, 'bad_outline')
        self.assertIn('12 m²', e['message'])
        self.error(self.call('POST', '/v1/codes', {'lat': la, 'lng': lo, 'outline': self.square(la, lo, 150)}), 422, 'bad_outline')
        self.error(self.call('POST', '/v1/codes', {'lat': 48.85, 'lng': 2.35}), 422, 'outside')
        self.error(self.call('POST', '/v1/codes', {'lat': la, 'lng': lo, 'of': 'SN-SLM-0000-999-Q'}), 404, 'not_found')
        self.error(self.call('POST', '/v1/codes', {'lat': la, 'lng': lo, 'of': self.rows[0]['canonical']}), 422, 'far')
        self.error(self.call('POST', '/v1/codes', {'lng': lo}), 400, 'bad_request')
        self.error(self.call('POST', '/v1/codes', {'lat': la, 'lng': lo, 'outline': 'square'}), 400, 'bad_request')
        self.error(self.call('POST', '/v1/codes', [1, 2]), 400, 'bad_request')
        self.error(self.call('POST', '/v1/codes', {'lat': True, 'lng': False}), 400, 'bad_request')

    def test_status_and_entrance(self):
        r = self.rows[700]
        m = r['canonical']
        st, c, _ = self.call('PATCH', f'/v1/codes/{m}', {'status': 'confirmed'})
        self.assertEqual((st, c['status'], c['registry']['status']), (200, 'confirmed', 'confirmed'))
        lat, lng = float(r['entrance_lat']), float(r['entrance_lng'])
        self.error(self.call('PATCH', f'/v1/codes/{m}', {'entrance': {'lat': lat + 100 / 111320, 'lng': lng}}), 422, 'far')
        st, c, _ = self.call('PATCH', f'/v1/codes/{m}', {'entrance': {'lat': lat + 20 / 111320, 'lng': lng}})
        self.assertEqual((st, c['entrance']['kind']), (200, 'gate'))
        self.assertEqual(c['spotCode'], self.svc.reg.spot(lat + 20 / 111320, lng, 'SLM'))
        self.error(self.call('PATCH', f'/v1/codes/{m}', {'status': 'bogus'}), 400, 'bad_request')
        self.error(self.call('PATCH', f'/v1/codes/{m}', {'status': ['confirmed']}), 400, 'bad_request')
        self.error(self.call('PATCH', f'/v1/codes/{m}', {}), 400, 'bad_request')
        st, c, _ = self.call('PATCH', f'/v1/codes/{m}', {'status': 'retired'})
        self.assertEqual(c['status'], 'retired')
        self.error(self.call('PATCH', f'/v1/codes/{m}', {'status': 'confirmed'}), 409, 'retired')
        self.error(self.get('/v1/find', q=r['remembered']), 404, 'retired')
        st, a, _ = self.get('/v1/at', lat=lat + 20 / 111320, lng=lng)
        self.assertTrue(a['status'] == 'none' or a['code']['machine'] != m, 'a retired address is never found by position')
        st, c, _ = self.get('/v1/codes/' + m)
        self.assertEqual(c['status'], 'retired')
        # a retired number is never given again
        st, n, _ = self.call('POST', '/v1/codes', {'lat': lat + 20 / 111320, 'lng': lng, 'of': self.rows[701]['canonical']})
        self.assertNotEqual(n.get('machine'), m)


class TheBorderDecides(Base):
    """engine/SPEC.md 2.3: a point the zone rule gives to Dagana (within 2 km of
    its outline) but which lies across the Senegal river, more than 300 m
    outside the national border, in a neighbouring country, is refused; inside
    the border, and within the limit of it, an address is issued."""
    across, near, inside = (16.5, -15.7755), (16.5, -15.795), (16.5, -15.82)

    def test_issue_and_lookup(self):
        reg = self.svc.reg
        self.assertEqual(reg.zones.lookup(*self.across), 'DAG')
        self.assertFalse(reg.border.holds(*self.across))
        self.assertIsNone(reg.zone_at(*self.across))
        e = self.error(self.call('POST', '/v1/codes', {'lat': self.across[0], 'lng': self.across[1]}), 422, 'outside')
        self.assertIn('outside Senegal', e['message'])
        self.error(self.get('/v1/at', lat=self.across[0], lng=self.across[1]), 422, 'outside')
        self.error(self.get('/v1/spot', lat=self.across[0], lng=self.across[1]), 422, 'outside')
        self.assertGreater(reg.border.outside_m(*self.near), 0)       # about 110 m outside the line
        for lat, lng in (self.inside, self.near):
            st, c, _ = self.call('POST', '/v1/codes', {'lat': lat, 'lng': lng})
            self.assertEqual(st, 201, c)
            self.assertTrue(c['machine'].startswith('SN-DAG-'), c['machine'])

    def test_entrance_never_moves_across(self):
        lat, lng = 16.5, -15.7925                                     # about 230 m outside the line: accepted
        st, c, _ = self.call('POST', '/v1/codes', {'lat': lat, 'lng': lng})
        self.assertEqual(st, 201, c)
        out = (lat, -15.792)                                          # 53 m further, about 255 m outside: refused
        self.assertFalse(self.svc.reg.border.holds(*out))
        self.error(self.call('PATCH', f"/v1/codes/{c['machine']}", {'entrance': {'lat': out[0], 'lng': out[1]}}), 422, 'outside')
        st, c2, _ = self.call('PATCH', f"/v1/codes/{c['machine']}", {'entrance': {'lat': lat, 'lng': -15.793}})
        self.assertEqual(st, 200, c2)
        self.assertEqual(c2['entrance']['kind'], 'gate')


class DailyLimit(Base):
    per_day = 2

    def test_limit_per_key(self):
        rows = fixture_rows()
        done = 0
        for r in rows[3000:3010]:
            st, body, _ = self.call('POST', '/v1/codes', {'lat': float(r['entrance_lat']) + 10 / 111320,
                                                          'lng': float(r['entrance_lng']), 'of': r['canonical']})
            if st == 201:
                done += 1
            if done == 2:
                break
        self.assertEqual(done, 2)
        self.error(self.call('POST', '/v1/codes', {'lat': 12.6, 'lng': -12.8}), 429, 'limit')


if __name__ == '__main__':
    unittest.main()
