"""The HTTP layer: routes under /v1, JSON in and out, CORS, errors.

Every response is JSON. An error is {"error": {"code": "...", "message": "..."}}
with the matching HTTP status (and, for `exists`, the card of the address
the building already has).
"""
import json
import re
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit

from .service import ApiError, Service, bad

MAX_BODY = 64 * 1024

ROUTES = [
    ('GET', r'/v1/health', 'health'),
    ('GET', r'/v1/info', 'info'),
    ('GET', r'/v1/find', 'find'),
    ('GET', r'/v1/at', 'at'),
    ('GET', r'/v1/near', 'near'),
    ('GET', r'/v1/verify', 'verify'),
    ('GET', r'/v1/spot', 'spot'),
    ('GET', r'/v1/spot/decode', 'spot_decode'),
    ('GET', r'/v1/zones', 'zones'),
    ('GET', r'/v1/zones/(?P<key>[^/]+)', 'zone'),
    ('GET', r'/v1/zones/(?P<key>[^/]+)/codes', 'zone_codes'),
    ('GET', r'/v1/areas', 'areas'),
    ('GET', r'/v1/areas/(?P<id>[^/]+)', 'area'),
    ('GET', r'/v1/codes/(?P<machine>[^/]+)', 'get_code'),
    ('POST', r'/v1/codes', 'issue'),
    ('PATCH', r'/v1/codes/(?P<machine>[^/]+)', 'patch'),
]
COMPILED = [(m, re.compile('^' + p + '/?$'), h) for m, p, h in ROUTES]


class Handler(BaseHTTPRequestHandler):
    server_version = 'n-ways-addresses-sn'
    sys_version = ''
    protocol_version = 'HTTP/1.1'
    svc: Service = None

    # -------------------------------------------------------- plumbing
    def log_message(self, fmt, *args):
        pass

    def _cors(self):
        origin = self.headers.get('Origin')
        allowed = self.svc.cfg.cors
        if origin and allowed and ('*' in allowed or origin in allowed):
            self.send_header('Access-Control-Allow-Origin', '*' if '*' in allowed else origin)
            self.send_header('Vary', 'Origin')

    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store' if self.command != 'GET' else 'public, max-age=60')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self._cors()
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)
        self._status = status

    def _error(self, status, code, message, **extra):
        self._send(status, {'error': {'code': code, 'message': message, **extra}})

    def _read(self):
        try:
            n = int(self.headers.get('Content-Length') or 0)
        except ValueError:
            n = 0
        if n > MAX_BODY:
            self.close_connection = True
            self._raw = None
            return
        self._raw = self.rfile.read(n) if n > 0 else b''

    def _body(self):
        if self._raw is None:
            raise ApiError(413, 'too_large', 'The body is at most 64 KB.')
        try:
            return json.loads(self._raw or b'null')
        except ValueError:
            raise bad('The body is not valid JSON.')

    def _dispatch(self, method):
        t0 = time.time()
        self._status = 0
        self._read()
        try:
            u = urlsplit(self.path)
            path = unquote(u.path)
            qs = {k: v[-1] for k, v in parse_qs(u.query, keep_blank_values=True).items()}
            allowed = []
            for m, rx, name in COMPILED:
                hit = rx.match(path)
                if hit:
                    if m == method or (m == 'GET' and method == 'HEAD'):
                        status, payload = getattr(self, 'h_' + name)(qs, **hit.groupdict())
                        self._send(status, payload)
                        return
                    allowed.append(m)
            if allowed:
                raise ApiError(405, 'method_not_allowed', f'{method} is not allowed here; use {", ".join(sorted(set(allowed)))}.')
            raise ApiError(404, 'not_found', f'There is no endpoint {path}. GET /v1/info describes this service; '
                                             'the full list is in openapi.yaml.')
        except ApiError as e:
            self._error(e.status, e.code, e.message, **e.extra)
        except Exception:
            traceback.print_exc(file=sys.stderr)
            self._error(500, 'internal', 'Something went wrong on the server. The error is in its log.')
        finally:
            self.svc.release()
            if self.svc.cfg.access_log:
                sys.stderr.write(f'{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} {method} {self.path.split("?")[0]} '
                                 f'{self._status} {1000 * (time.time() - t0):.0f}ms\n')

    def do_GET(self):
        self._dispatch('GET')

    def do_HEAD(self):
        self._dispatch('HEAD')

    def do_POST(self):
        self._dispatch('POST')

    def do_PATCH(self):
        self._dispatch('PATCH')

    def do_PUT(self):
        self._dispatch('PUT')

    def do_DELETE(self):
        self._dispatch('DELETE')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.send_header('Content-Length', '0')
        self.end_headers()

    # -------------------------------------------------------- endpoints
    def _point(self, qs):
        return self.svc.point(qs.get('lat'), qs.get('lng'))

    def h_health(self, qs):
        return 200, self.svc.health()

    def h_info(self, qs):
        return 200, self.svc.info()

    def h_find(self, qs):
        return 200, self.svc.find(qs.get('q'))

    def h_at(self, qs):
        return 200, self.svc.at(*self._point(qs))

    def h_near(self, qs):
        return 200, self.svc.near(*self._point(qs), qs.get('radius'), qs.get('limit'))

    def h_verify(self, qs):
        return 200, self.svc.verify(qs.get('code'))

    def h_spot(self, qs):
        return 200, self.svc.spot(*self._point(qs))

    def h_spot_decode(self, qs):
        return 200, self.svc.spot_decode(qs.get('code'))

    def h_zones(self, qs):
        return 200, self.svc.zones()

    def h_zone(self, qs, key):
        return 200, self.svc.zone(key)

    def h_zone_codes(self, qs, key):
        return 200, self.svc.zone_codes(key, qs.get('after'), qs.get('limit'))

    def h_areas(self, qs):
        return 200, self.svc.areas(qs.get('name'))

    def h_area(self, qs, id):
        return 200, self.svc.area(id)

    def h_get_code(self, qs, machine):
        return 200, self.svc.get_code(machine)

    def h_issue(self, qs):
        kid = self.svc.authorise(self.headers.get('Authorization'))
        return 201, self.svc.issue(self._body(), kid)

    def h_patch(self, qs, machine):
        self.svc.authorise(self.headers.get('Authorization'))
        return 200, self.svc.patch(machine, self._body())


def make_server(svc, host='0.0.0.0', port=8080):
    handler = type('BoundHandler', (Handler,), {'svc': svc})
    srv = ThreadingHTTPServer((host, port), handler)
    srv.daemon_threads = True
    return srv
