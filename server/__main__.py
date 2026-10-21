"""python3 -m server import | serve | start | export

  import  --registry registry --db data/addresses.sqlite   load the published registry (checked against MANIFEST.json)
  serve   --db data/addresses.sqlite --port 8080           serve the API
  start                                                    import if the database is empty, then serve (the container's command)
  export  --db data/addresses.sqlite --out DIR             write the registry back in the published format

Configuration by environment: ADDRESSES_DB, PORT, HOST, REGISTRY_DIR,
ISSUE_KEYS (comma-separated bearer keys; none = read-only), ISSUE_PER_DAY,
CORS_ORIGINS (comma-separated origins, or *).
"""
import argparse
import os
import signal
import sys

from . import core, db


def _serve(db_path, host, port):
    from .api import make_server
    from .service import Config, Service
    cfg = Config(db_path=db_path)
    svc = Service(cfg)
    srv = make_server(svc, host, port)
    mode = f'issuing with {len(cfg.issue_keys)} key(s), {cfg.per_day} a day each' if cfg.issue_keys else 'read-only'
    print(f'serving {svc.total:,} Senegal addresses on http://{host}:{port}/v1 ({mode})', file=sys.stderr, flush=True)
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


def main(argv=None):
    env = os.environ
    p = argparse.ArgumentParser(prog='python3 -m server', description='N-Ways Addressing for Senegal: registry server')
    sub = p.add_subparsers(dest='cmd', required=True)
    default_db = env.get('ADDRESSES_DB', 'data/addresses.sqlite')
    default_reg = env.get('REGISTRY_DIR', os.path.join(core.ROOT, 'registry'))
    i = sub.add_parser('import', help='load registry/*.csv.gz into SQLite')
    i.add_argument('--registry', default=default_reg)
    i.add_argument('--db', default=default_db)
    for name in ('serve', 'start'):
        s = sub.add_parser(name, help='serve the API' if name == 'serve' else 'import when empty, then serve')
        s.add_argument('--db', default=default_db)
        s.add_argument('--host', default=env.get('HOST', '0.0.0.0'))
        s.add_argument('--port', type=int, default=int(env.get('PORT', '8080')))
        if name == 'start':
            s.add_argument('--registry', default=default_reg)
    x = sub.add_parser('export', help='write the registry in the published format')
    x.add_argument('--db', default=default_db)
    x.add_argument('--out', required=True)
    a = p.parse_args(argv)
    try:
        if a.cmd == 'import':
            db.import_registry(a.registry, a.db)
        elif a.cmd == 'export':
            db.export_registry(a.db, a.out)
        elif a.cmd == 'start':
            if not os.path.exists(a.db) or db.count_codes(a.db) == 0:
                print(f'{a.db} is empty: importing {a.registry}', file=sys.stderr, flush=True)
                db.import_registry(a.registry, a.db, log=lambda m: print(m, file=sys.stderr, flush=True))
            _serve(a.db, a.host, a.port)
        else:
            _serve(a.db, a.host, a.port)
    except db.RegistryError as e:
        print(f'refused: {e}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
