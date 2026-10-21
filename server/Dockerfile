# N-Ways Addressing for Senegal: the registry server.
# Build from the repository root (docker-compose.yml does this):
#   docker build -f server/Dockerfile -t n-ways-addresses-sn .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ADDRESSES_DB=/data/addresses.sqlite \
    REGISTRY_DIR=/app/registry \
    MODEL_DIR=/app/model \
    HOST=0.0.0.0 \
    PORT=8080

RUN useradd --system --uid 10001 --home-dir /app --shell /usr/sbin/nologin addresses \
    && mkdir -p /data && chown addresses:addresses /data

WORKDIR /app
COPY engine/reference/sn_engine.py engine/reference/plate_names.py engine/reference/
COPY engine/data/border.geojson engine/data/
COPY model/zones.json model/zones.geojson model/lieux.json model/
COPY registry/ registry/
COPY server/__init__.py server/__main__.py server/api.py server/core.py server/db.py server/service.py server/openapi.yaml server/

USER addresses
VOLUME ["/data"]
EXPOSE 8080

# The first start imports the registry (a few minutes for the whole country) before it serves.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15m --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/v1/health' % os.environ.get('PORT', '8080'), timeout=4)"]

CMD ["python", "-m", "server", "start"]
