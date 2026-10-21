"""What each endpoint does, independent of HTTP.

Reads come straight from SQLite. Issuing follows the N-Ways issuer step for
step: the same checks in the same order, the same distances and limits, the
same lieu, the same number and the same forms (server/README.md, "The
issuing rules"; testdata/parity.json holds the issuer's own answers).
"""
import hashlib
import json
import math
import os
import re
import threading
import time

from . import core, db
from .core import E


class ApiError(Exception):
    def __init__(self, status, code, message, **extra):
        super().__init__(message)
        self.status, self.code, self.message, self.extra = status, code, message, extra


def bad(message, code='bad_request'):
    return ApiError(400, code, message)


class Config:
    def __init__(self, db_path=None, issue_keys=None, per_day=None, cors=None, access_log=True):
        env = os.environ
        self.access_log = access_log
        self.db_path = db_path or env.get('ADDRESSES_DB', 'data/addresses.sqlite')
        keys = issue_keys if issue_keys is not None else env.get('ISSUE_KEYS', '')
        self.issue_keys = [k.strip() for k in (keys.split(',') if isinstance(keys, str) else keys) if k.strip()]
        self.per_day = int(per_day if per_day is not None else env.get('ISSUE_PER_DAY', '5'))
        origins = cors if cors is not None else env.get('CORS_ORIGINS', '')
        self.cors = [o.strip() for o in (origins.split(',') if isinstance(origins, str) else origins) if o.strip()]


def key_id(key):
    return hashlib.sha256(key.encode()).hexdigest()[:16]


class Service:
    def __init__(self, config):
        self.cfg = config
        if not os.path.exists(config.db_path) or db.count_codes(config.db_path) == 0:
            raise SystemExit(f'{config.db_path} holds no addresses: run `python3 -m server import` first')
        self._local = threading.local()
        self.lock = threading.Lock()
        con = self.con()
        db.create(con)  # indexes added since the database was built
        self.reg = core.Register(db.load_lieux(con))
        self.exported = db.meta(con, 'exported', '')
        self.engine = db.meta(con, 'engine', '')
        self._refresh_counts()

    def con(self):
        c = getattr(self._local, 'con', None)
        if c is None:
            c = self._local.con = db.connect(self.cfg.db_path)
        return c

    def release(self):
        """Close this thread's connection (each request runs in its own thread)."""
        c = getattr(self._local, 'con', None)
        if c is not None:
            c.close()
            self._local.con = None

    def _refresh_counts(self):
        self.counts = db.zone_counts(self.con())
        self.total = sum(sum(v.values()) for v in self.counts.values())

    def _bump(self, zone, old, new):
        c = self.counts.setdefault(zone, {})
        if old:
            c[old] -= 1
            if not c[old]:
                del c[old]
        c[new] = c.get(new, 0) + 1
        self.total = sum(sum(v.values()) for v in self.counts.values())

    # ------------------------------------------------------------ cards
    def card(self, r, distance=None):
        lieu = self.reg.lieu(r['lieu'])
        z = self.reg.zone(r['zone'])
        f = self.reg.forms(lieu, r['num'])
        row = {c: r[c] for c in core.CODE_COLUMNS}
        out = {
            'machine': r['canonical'], 'remembered': r['remembered'], 'written': r['written'],
            'spokenFr': f['spokenFr'], 'spokenWo': f['spokenWo'], 'number': r['num'], 'check': r['check'],
            'status': r['status'], 'issued': r['issued'], 'issuedAt': r['issued_at'],
            'entrance': {'lat': r['lat'], 'lng': r['lng'], 'kind': r['entrance_kind']},
            'spotCode': r['spot_code'], 'plusCode': core.plus_code(r['lat'], r['lng']),
            'area': {'id': r['lieu'], 'plateName': lieu['placeWord'], 'officialName': r['official_name'],
                     'kind': lieu['kind'], 'nearTown': lieu['nearTown'], 'needsCommuneChoice': lieu['needsCouncilChoice']},
            'zone': {'key': z['key'], 'name': z['name'], 'plateName': z['name'].split(' (')[0], 'region': z['region']},
            'compound': {'class': r['class'] or None, 'use': r['use'], 'kind': r['kind'],
                         'structures': int(r['structures']), 'floorAreaM2': float(r['floor_area_m2'])},
            'postcode': r['postcode'] or None, 'coverage': r['coverage'] or None, 'officialAddress': r['official_address'] or None,
            'registry': row, 'credit': core.CREDIT, 'creditUrl': core.CREDIT_URL,
        }
        if distance is not None:
            out = {'distanceM': round(distance, 1), **out}
        return out

    @staticmethod
    def brief(r, distance=None):
        out = {'machine': r['canonical'], 'remembered': r['remembered'], 'status': r['status'],
               'entrance': {'lat': r['lat'], 'lng': r['lng'], 'kind': r['entrance_kind']}, 'spotCode': r['spot_code']}
        if distance is not None:
            out = {'distanceM': round(distance, 1), **out}
        return out

    # ------------------------------------------------------------ parsing
    @staticmethod
    def point(lat, lng):
        try:
            if isinstance(lat, bool) or isinstance(lng, bool):
                raise TypeError
            la, lo = float(lat), float(lng)
        except (TypeError, ValueError):
            raise bad('lat and lng are decimal degrees, for example lat=14.7247&lng=-17.4849')
        if not (math.isfinite(la) and math.isfinite(lo) and -90 <= la <= 90 and -180 <= lo <= 180):
            raise bad('lat must be between -90 and 90 and lng between -180 and 180')
        return la, lo

    def machine(self, text):
        """A machine form checked against the block table: (base form, lieu, number), or an error."""
        t = (text or '').strip().upper()
        m = E.CANON_RE.match(t)
        if not m:
            raise ApiError(400, 'invalid_code', f'{text!r} is not a Senegal machine form such as SN-DKR-0080-2512-J')
        base = f'SN-{m.group(1)}-{m.group(2)}-{m.group(3)}-{m.group(4)}'
        ok, why = E.validate(base, self.reg.zones, self.reg.lieux)
        if not ok:
            raise ApiError(400, 'invalid_code', why[:1].upper() + why[1:] + '.')
        return base, self.reg.lieux.get(m.group(1), int(m.group(2))), int(m.group(3))

    # ------------------------------------------------------------ reads
    def health(self):
        return {'status': 'ok', 'country': core.COUNTRY, 'codes': self.total, 'registryExported': self.exported}

    def info(self):
        by_status = {}
        for v in self.counts.values():
            for s, n in v.items():
                by_status[s] = by_status.get(s, 0) + n
        con = self.con()
        return {'country': core.COUNTRY, 'name': core.COUNTRY_NAME, 'zones': len(self.reg.zones.by_key),
                'areas': len(self.reg.lieux.items), 'codes': {'total': self.total, 'byStatus': by_status},
                'byZone': {k: sum(v.values()) for k, v in sorted(self.counts.items())},
                'registry': {'exported': self.exported, 'imported': db.meta(con, 'imported', ''),
                             'addresses': int(db.meta(con, 'registryAddresses', '0'))},
                'licences': core.LICENCES, 'credit': core.CREDIT, 'creditUrl': core.CREDIT_URL,
                'engine': self.engine, 'spec': core.SPEC,
                'issuing': {'enabled': bool(self.cfg.issue_keys), 'perKeyPerDay': self.cfg.per_day}}

    def get_code(self, machine):
        base, _, _ = self.machine(machine)
        r = db.by_machine(self.con(), base)
        if r is None:
            raise ApiError(404, 'not_found', f'{base} is a valid form, but no address has been issued with it.')
        return self.card(r)

    def find(self, q):
        q = (q or '').strip()
        if not q:
            raise bad('q is required: a remembered address (Ouakam 2512), a machine form, an official address or a spot code')
        if len(q) > 200:
            raise bad('q is at most 200 characters')
        con = self.con()
        if E.CANON_RE.match(q.upper()):
            card = self.get_code(q)
            return {'query': q, 'kind': 'machine', 'matches': [card]}
        if E.SPOT_RE.match(q):
            try:
                lat, lng, cell = E.decode_spot(q, self.reg.zones)
            except ValueError as e:
                raise ApiError(400, 'invalid_code', str(e)[:1].upper() + str(e)[1:] + '.')
            try:
                at = self.at(lat, lng)
            except ApiError:
                at = {'status': 'outside'}
            if at['status'] != 'found':
                raise ApiError(404, 'not_found', f'No address is at {q.upper()} yet: it is a spot, not an address.')
            return {'query': q, 'kind': 'spot', 'matches': [at['code']]}
        found = E.find(core.loosen(q), self.reg.zones, self.reg.lieux)
        if found:
            out, retired = [], []
            for _, lieu, num in found:
                r = db.by_number(con, lieu['family'], num)
                if r is None:
                    continue
                (retired if r['status'] == 'retired' else out).append(r)
            if out:
                return {'query': q, 'kind': 'remembered', 'matches': [self.card(r) for r in out]}
            if retired:
                raise ApiError(404, 'retired', f"{retired[0]['remembered']} was retired: there is no compound there any more.")
            _, lieu, num = found[0]
            f = self.reg.forms(lieu, num)
            z = self.reg.zone(lieu['zone'])
            raise ApiError(404, 'not_found', f"No compound has {f['remembered']} yet (the number is in the range of "
                                             f"{lieu['placeWord']}, {z['name'].split(' (')[0]}).")
        rows = db.by_official(con, core.fold(q))
        if rows:
            return {'query': q, 'kind': 'official', 'matches': [self.card(r) for r in rows]}
        raise ApiError(404, 'not_found', f'No address in Senegal reads {q!r}. Check the place name and the number, '
                                         'or look the building up by position (/v1/at).')

    def located(self, lat, lng, radius):
        """The code of the compound at a point: an outline issued here that
        holds it, else the nearest live entrance within `radius` metres."""
        con = self.con()
        inside = db.containing(con, lat, lng)
        if inside:
            return sorted(inside, key=lambda r: r['canonical'])[0], 0.0
        hits = db.near(con, lat, lng, radius, 1)
        return (hits[0][1], hits[0][0]) if hits else (None, None)

    def at(self, lat, lng):
        zk = self.reg.zone_at(lat, lng)
        if zk is None:
            raise ApiError(422, 'outside', 'That point is outside Senegal.')
        z = self.reg.zone(zk)
        zone = {'key': zk, 'name': z['name'], 'plateName': z['name'].split(' (')[0]}
        r, d = self.located(lat, lng, core.FOUND_M)
        if r is not None:
            return {'status': 'found', 'distanceM': round(d, 1), 'zone': zone, 'code': self.card(r)}
        e, n = E.utm_forward(lat, lng)
        lieu = self.reg.lieux.nearest(zk, e, n)
        area = None if lieu is None else {'id': core.ref(lieu), 'plateName': lieu['placeWord'], 'officialName': lieu['officialName'],
                                          'kind': lieu['kind']}
        return {'status': 'none', 'zone': zone, 'area': area, 'spotCode': self.reg.spot(lat, lng, zk)}

    def near(self, lat, lng, radius, limit):
        try:
            radius = float(radius) if radius not in (None, '') else 100.0
            limit = int(limit) if limit not in (None, '') else 20
        except ValueError:
            raise bad('radius is metres (at most 500) and limit a whole number (at most 100)')
        if not (0 < radius <= 500):
            raise bad('radius is in metres, more than 0 and at most 500')
        if not (1 <= limit <= 100):
            raise bad('limit is between 1 and 100')
        hits = db.near(self.con(), lat, lng, radius, limit)
        return {'lat': lat, 'lng': lng, 'radiusM': radius, 'count': len(hits), 'codes': [self.brief(r, d) for d, r in hits]}

    def verify(self, code):
        code = (code or '').strip()
        if not code:
            raise bad('code is required')
        if E.SPOT_RE.match(code):
            ok, why = E.validate(code, self.reg.zones)
            return {'code': code, 'kind': 'spot', 'valid': ok, 'reason': None if ok else why, 'issued': None}
        try:
            base, _, _ = self.machine(code)
        except ApiError as e:
            return {'code': code, 'kind': 'machine', 'valid': False, 'reason': e.message, 'issued': False}
        r = db.by_machine(self.con(), base)
        return {'code': code, 'kind': 'machine', 'valid': True, 'reason': None, 'machine': base, 'issued': r is not None,
                'status': r['status'] if r else None}

    def spot(self, lat, lng):
        zk = self.reg.zone_at(lat, lng)
        if zk is None:
            raise ApiError(422, 'outside', 'That point is outside Senegal.')
        code = self.reg.spot(lat, lng, zk)
        z = self.reg.zone(zk)
        return {'spotCode': code, 'zone': zk, 'cellMetres': z['cellMetres'], 'spokenFr': E.spoken_spot(code),
                'spokenWo': E.spoken_spot(code, 'wo'), 'plusCode': core.plus_code(lat, lng)}

    def spot_decode(self, code):
        code = (code or '').strip()
        if not code:
            raise bad('code is required, for example DKR 5553 1512')
        try:
            lat, lng, cell = E.decode_spot(code, self.reg.zones)
        except ValueError as e:
            raise ApiError(400, 'invalid_code', str(e)[:1].upper() + str(e)[1:] + '.')
        m = E.SPOT_RE.match(code)
        z = self.reg.zone(m.group(1).upper())
        canon = f"{z['key']} {m.group(2)} {m.group(3)}"
        return {'spotCode': canon, 'zone': z['key'], 'lat': round(lat, 7), 'lng': round(lng, 7), 'cellMetres': cell}

    def _bbox(self, key):
        bs = [b for k, b, _ in self.reg.zones.shapes if k == key]
        return [round(min(b[0] for b in bs), 4), round(min(b[1] for b in bs), 4),
                round(max(b[2] for b in bs), 4), round(max(b[3] for b in bs), 4)]

    def _zone_entry(self, z):
        c = self.counts.get(z['key'], {})
        return {**self.reg.zone_info(z), 'areas': len(self.reg.lieux.by_zone.get(z['key'], {})),
                'codes': sum(c.values()), 'byStatus': c, 'bbox': self._bbox(z['key'])}

    def zones(self):
        zs = sorted(self.reg.zones.by_key.values(), key=lambda z: z['index'])
        return {'count': len(zs), 'zones': [self._zone_entry(z) for z in zs]}

    def zone(self, key):
        z = self.reg.zone((key or '').upper())
        if z is None:
            raise ApiError(404, 'not_found', f'There is no zone {key!r}. GET /v1/zones lists the 46 zones.')
        counts = db.lieu_counts(self.con(), z['key'])
        areas = []
        for idx, lieu in sorted(self.reg.lieux.by_zone.get(z['key'], {}).items()):
            c = counts.get(core.ref(lieu), {})
            areas.append({'id': core.ref(lieu), 'plateName': lieu['placeWord'], 'officialName': lieu['officialName'],
                          'kind': lieu['kind'], 'digits': lieu['digits'], 'blocks': lieu['blocks'], 'codes': sum(c.values())})
        return {**self._zone_entry(z), 'areaList': areas}

    def _area_entry(self, lieu, detail=False):
        out = self.reg.lieu_info(lieu)
        rows = self.con().execute('SELECT num, status FROM codes WHERE lieu = ?', (core.ref(lieu),)).fetchall()
        by_status = {}
        for r in rows:
            by_status[r['status']] = by_status.get(r['status'], 0) + 1
        out['codes'] = {'total': len(rows), 'byStatus': by_status}
        if detail:
            out['blockUse'] = [{'block': list(b), 'size': b[1] - b[0] + 1,
                                'used': sum(1 for r in rows if b[0] <= r['num'] <= b[1])} for b in lieu['blocks']]
        return out

    def area(self, area_id):
        lieu = self.reg.lieu((area_id or '').upper())
        if lieu is None:
            raise ApiError(404, 'not_found', f'There is no area {area_id!r}. Area ids look like DKR-0080.')
        return self._area_entry(lieu, detail=True)

    def areas(self, name):
        name = (name or '').strip()
        if not name:
            raise bad('name is required: a plate name, an official name or an alias, such as Ouakam')
        hits = self.reg.find_areas(name)
        return {'name': name, 'count': len(hits), 'areas': [self._area_entry(x) for x in hits[:50]]}

    def zone_codes(self, key, after, limit):
        z = self.reg.zone((key or '').upper())
        if z is None:
            raise ApiError(404, 'not_found', f'There is no zone {key!r}.')
        try:
            limit = int(limit) if limit not in (None, '') else 100
        except ValueError:
            raise bad('limit is a whole number between 1 and 1000')
        if not (1 <= limit <= 1000):
            raise bad('limit is between 1 and 1000')
        rows = db.page(self.con(), z['key'], (after or '').upper(), limit)
        return {'zone': z['key'], 'after': after or None, 'count': len(rows), 'codes': [self.brief(r) for r in rows],
                'next': rows[-1]['canonical'] if len(rows) == limit else None}

    # ------------------------------------------------------------ writes
    def authorise(self, header):
        if not self.cfg.issue_keys:
            raise ApiError(403, 'read_only', 'This deployment is read-only: it serves the published registry and does not '
                                             'issue. Only the deployment designated as Senegal\'s issuer issues addresses.')
        m = re.match(r'^Bearer\s+(\S+)$', header or '')
        if not m:
            raise ApiError(401, 'unauthorized', 'Send the issuing key as "Authorization: Bearer <key>".')
        key = m.group(1)
        if not any(hashlib.sha256(key.encode()).digest() == hashlib.sha256(k.encode()).digest() for k in self.cfg.issue_keys):
            raise ApiError(401, 'unauthorized', 'That key is not one of this deployment\'s issuing keys.')
        return key_id(key)

    def issue(self, body, kid):
        """POST /v1/codes. The order of the checks is the issuer's."""
        if not isinstance(body, dict):
            raise bad('the body is a JSON object: {"lat": .., "lng": .., "outline": [[lng, lat], ...], "of": "SN-..."}')
        lat, lng = self.point(body.get('lat'), body.get('lng'))
        outline, of = body.get('outline'), body.get('of') or ''
        if outline is not None:
            if not (isinstance(outline, list) and all(isinstance(p, list) and len(p) == 2 and
                                                      all(isinstance(x, (int, float)) for x in p) for p in outline)):
                raise bad('outline is a list of [lng, lat] points')
        if not isinstance(of, str):
            raise bad('of is the machine form of the compound this is another door of')
        con = self.con()
        n = db.issued_by(con, kid, time.time() - 86400)
        if n >= self.cfg.per_day:
            raise ApiError(429, 'limit', f'This key has issued {n} addresses in the last 24 hours, its limit. Try again later.')
        with self.lock:
            zk = self.reg.zone_at(lat, lng)
            if zk is None:
                raise ApiError(422, 'outside', 'That spot is outside Senegal, so it cannot have an N-Ways Senegal address.')
            ring, area, per = None, 0.0, 0.0
            if not of:
                r, _ = self.located(lat, lng, core.EXISTS_M)
                if r is not None:
                    raise ApiError(409, 'exists', f"This building already has its address: {r['remembered']}.", existing=self.card(r))
                if outline and len(outline) >= 3:
                    ring = [list(map(float, p)) for p in outline]
                    if ring[0] == ring[-1]:
                        ring = ring[:-1]
                    area, per = core.ring_area_m2(ring), core.ring_perimeter_m(ring)
                    if len(ring) < 3 or area < core.MIN_AREA_M2 or area > core.MAX_AREA_M2:
                        raise ApiError(422, 'bad_outline', f'That outline is {area:.0f} m², but a compound\'s is between 12 m² and 2 ha.')
                    for o in db.outlines_near(con, ring):
                        other = json.loads(o['outline'])
                        if core.overlap_m2(ring, other) > 0.5 * min(area, core.ring_area_m2(other)):
                            raise ApiError(409, 'exists', f"This building already has its address: {o['remembered']}.",
                                           existing=self.card(o))
            e, n_ = E.utm_forward(lat, lng)
            if of:
                o = db.by_machine(con, of.strip().upper())
                if o is None:
                    raise ApiError(404, 'not_found', f'There is no address {of} to add a door to.')
                if core.dist_m(o['lat'], o['lng'], lat, lng) > core.DOOR_M:
                    raise ApiError(422, 'far', f"That door is more than 80 m from {o['remembered']}.")
                lieu = self.reg.lieu(o['lieu'])
            else:
                lieu = self.reg.lieux.nearest(zk, e, n_)
            if lieu is None:
                raise ApiError(422, 'outside', 'There is no place name for this spot yet.')
            work = dict(lieu, blocks=[list(b) for b in lieu['blocks']])
            z = self.reg.zone(lieu['zone'])
            issued = []
            for c in db.lieu_numbers(con, core.ref(lieu)):
                ce, cn = E.utm_forward(c['lat'], c['lng'])
                issued.append({'e': ce, 'n': cn, 'number': c['number']})
            nb = len(work['blocks'])
            num = E.insert_in_lieu(z, work, issued, e, n_, self.reg.lieux)
            if num is None:
                raise ApiError(409, 'full', f"{lieu['placeWord']} has used every number of its name. Its commune names the "
                                            'extension before more compounds there get an address.')
            new_blocks = work['blocks'][nb:]
            f = self.reg.forms(work, num)
            prof = core.new_compound_profile(area, per, bool(of))
            row = [f['canonical'], f['remembered'], f['written'], core.ref(lieu), lieu['officialName'], str(num),
                   E.address_check(lieu['family'], num), 'provisional', 'on-demand',
                   time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), f'{lat:.7f}', f'{lng:.7f}',
                   'door' if of else 'centre', self.reg.spot(lat, lng, lieu['zone']), prof['class'], prof['use'], prof['kind'],
                   str(prof['structures']), f"{prof['floorAreaM2']:.1f}", '', '', '']
            con.execute('BEGIN IMMEDIATE')
            try:
                cur = con.execute(
                    f'INSERT INTO codes ({db.CODE_SELECT}, zone, family, num, lat, lng, anchor_lat, anchor_lng, anchor, remembered_key, '
                    f'official_key, source, outline, cell) VALUES ({",".join("?" * (len(core.CODE_COLUMNS) + 13))})',
                    row + [lieu['zone'], lieu['family'], num, float(row[10]), float(row[11]), lat, lng, f'{lat!r},{lng!r}',
                           core.fold(row[1]), None,
                           'local', json.dumps(ring) if ring else None, db.cell_of(float(row[10]), float(row[11]))])
                if db.has_rtree(con):
                    con.execute('INSERT INTO codes_rtree VALUES (?, ?, ?, ?, ?)',
                                (cur.lastrowid, float(row[10]), float(row[10]), float(row[11]), float(row[11])))
                if new_blocks:
                    con.execute('UPDATE lieux SET blocks = ? WHERE ref = ?', (core.blocks_text(work), core.ref(lieu)))
                con.execute('INSERT INTO issue_log (key_id, at, machine) VALUES (?, ?, ?)', (kid, time.time(), row[0]))
                con.execute('COMMIT')
            except BaseException:
                con.execute('ROLLBACK')
                raise
            if new_blocks:
                lieu['blocks'] = work['blocks']
            self._bump(lieu['zone'], None, 'provisional')
            return self.card(db.by_machine(con, row[0]))

    TRANSITIONS = {('provisional', 'confirmed'), ('provisional', 'retired'), ('confirmed', 'retired'),
                   ('confirmed', 'provisional')}

    def patch(self, machine, body):
        """PATCH /v1/codes/{machine}: a status change, or the entrance moved to the real gate."""
        base, _, _ = self.machine(machine)
        if not isinstance(body, dict) or not ({'status', 'entrance'} & set(body)):
            raise bad('send {"status": "confirmed" | "retired" | "provisional"} or {"entrance": {"lat": .., "lng": ..}}')
        if body.get('status') is not None and body['status'] not in ('provisional', 'confirmed', 'retired'):
            raise bad('status is "provisional", "confirmed" or "retired"')
        con = self.con()
        with self.lock:
            r = db.by_machine(con, base)
            if r is None:
                raise ApiError(404, 'not_found', f'No address has been issued as {base}.')
            if r['status'] == 'retired':
                raise ApiError(409, 'retired', f'{base} is retired. A retired address is never used again.')
            sets = {}
            status = body.get('status')
            if status is not None and status != r['status']:
                if (r['status'], status) not in self.TRANSITIONS:
                    raise ApiError(409, 'conflict', f"{base} cannot go from {r['status']} to {status!r}.")
                sets['status'] = status
            ent = body.get('entrance')
            if ent is not None:
                if not isinstance(ent, dict):
                    raise bad('entrance is {"lat": .., "lng": ..}')
                la, lo = self.point(ent.get('lat'), ent.get('lng'))
                d = core.dist_m(r['lat'], r['lng'], la, lo)
                if d > core.MOVE_M:
                    raise ApiError(422, 'far', f'The entrance moves at most 80 m; that point is {d:.0f} m away.')
                if self.reg.zone_at(la, lo) is None:
                    raise ApiError(422, 'outside', 'That point is outside Senegal: an entrance never moves across the national border.')
                sets.update({'entrance_lat': f'{la:.7f}', 'entrance_lng': f'{lo:.7f}', 'entrance_kind': 'gate',
                             'spot_code': self.reg.spot(la, lo, r['zone'])})
            if not sets:
                return self.card(r)
            con.execute('BEGIN IMMEDIATE')
            try:
                cols = ', '.join(f'{db.q(k)} = ?' for k in sets)
                vals = list(sets.values())
                if 'entrance_lat' in sets:
                    la, lo = float(sets['entrance_lat']), float(sets['entrance_lng'])
                    cols += ', lat = ?, lng = ?, cell = ?'
                    vals += [la, lo, db.cell_of(la, lo)]
                    if db.has_rtree(con):
                        con.execute('UPDATE codes_rtree SET min_lat = ?, max_lat = ?, min_lng = ?, max_lng = ? WHERE id = ?',
                                    (la, la, lo, lo, r['id']))
                con.execute(f'UPDATE codes SET {cols} WHERE id = ?', vals + [r['id']])
                con.execute('COMMIT')
            except BaseException:
                con.execute('ROLLBACK')
                raise
            if 'status' in sets:
                self._bump(r['zone'], r['status'], sets['status'])
            return self.card(db.by_machine(con, base))
