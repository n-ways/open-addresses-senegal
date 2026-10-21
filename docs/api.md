# The registry API

Every endpoint of the server in `server/`, with a real request and the response it gave. The responses were copied from the server running on the complete registry (3,597,138 addresses); the issuing examples come from a scratch copy of it with an issuing key. Long lists are shortened and say so. The OpenAPI description is [server/openapi.yaml](../server/openapi.yaml); deployment and configuration are in [server/README.md](../server/README.md).

`https://addresses.example.org` stands for wherever the server is deployed (`http://localhost:8080` after `docker compose up`).

## Conventions

- Every response is JSON in UTF-8, with stable field names.
- An error has the shape `{"error": {"code": "...", "message": "..."}}` and the matching HTTP status:

| HTTP | `code` | When |
|---|---|---|
| 400 | `bad_request` | a parameter is missing or out of range, or the body is not the JSON expected |
| 400 | `invalid_code` | a machine form or spot code is malformed, names an unknown zone or area, or its check letter does not match |
| 401 | `unauthorized` | no issuing key, or a key this deployment does not have |
| 403 | `read_only` | the deployment does not issue (no `ISSUE_KEYS`) |
| 404 | `not_found` | no such address, zone, area or endpoint |
| 404 | `retired` | the address was retired |
| 405 | `method_not_allowed` | the path exists, the method does not |
| 409 | `exists` | the building already has an address (the error carries it as `existing`) |
| 409 | `full` | the area's name has used its whole national range |
| 409 | `conflict` | a status change that is not allowed |
| 413 | `too_large` | a request body over 64 KB |
| 422 | `outside` | the point is outside Senegal: in no zone, or more than 300 m outside the national border (engine/SPEC.md 2.3) |
| 422 | `bad_outline` | an outline under 12 m² or over 2 ha |
| 422 | `far` | a door or an entrance move more than 80 m away |
| 429 | `limit` | the key has issued its daily number (`ISSUE_PER_DAY`) |
| 500 | `internal` | a fault in the server; the details are in its log |

- People never see the check letter: `remembered` and `written` carry none; the machine form ends with it.
- Positions are WGS 84 decimal degrees; distances are metres.

## GET /v1/health

Whether the service is up, and the registry it serves.

**Health**

```sh
curl -s 'https://addresses.example.org/v1/health'
```

`HTTP 200`

```json
{
  "status": "ok",
  "country": "SN",
  "codes": 3597128,
  "registryExported": "2026-10-21T18:48:16Z"
}
```

## GET /v1/info

Country, zones, areas, counts by status and zone, the registry export it was loaded from, licences, credit, and whether this deployment issues.

**Information**

```sh
curl -s 'https://addresses.example.org/v1/info'
```

`HTTP 200`

```json
{
  "country": "SN",
  "name": "Senegal",
  "zones": 46,
  "areas": 14997,
  "codes": {
    "total": 3597128,
    "byStatus": {
      "provisional": 3597128
    }
  },
  "byZone": {
    "BIG": 65019,
    "BKL": 41737,
    "BMB": 83034,
    "BNK": 36264,
    "BRK": 33656,
    "DAG": 89049,
    "DBL": 68418,
    "DKR": 107430,
    "FDG": 79408,
    "FTK": 101628,
    "GDW": 23425,
    "GMP": 27865,
    "GNG": 39809,
    "GOS": 30827,
    "GRY": 35962,
    "KAF": 75331,
    "KAO": 129054,
    "KBM": 94438,
    "KDG": 47506,
    "KGH": 48680,
    "KLD": 72605,
    "KNL": 66004,
    "KPT": 40224,
    "KTF": 22957,
    "LGA": 131320,
    "LNG": 96934,
    "MAT": 77460,
    "MBR": 205416,
    "MHD": 25139,
    "MYF": 54533,
    "NRP": 103624,
    "OUS": 16172,
    "PKN": 123594,
    "POD": 91267,
    "RAN": 32597,
    "RUF": 158721,
    "SED": 32322,
    "SLM": 5839,
    "SRY": 45759,
    "STL": 73706,
    "TBA": 289328,
    "TBC": 100102,
    "THS": 175645,
    "TIV": 144845,
    "VEL": 104269,
    "ZIG": 48206
  },
  "registry": {
    "exported": "2026-10-21T18:48:16Z",
    "imported": "2026-10-21T18:57:22Z",
    "addresses": 3597128
  },
  "licences": {
    "data": "ODbL 1.0 (LICENSE-DATA)",
    "code": "Apache-2.0 (LICENSE)",
    "documents": "CC BY 4.0 (LICENSE-DOCS)"
  },
  "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-senegal",
  "engine": "internal/addressing/sn (SPEC v0.2)",
  "spec": "engine/SPEC.md v0.2",
  "issuing": {
    "enabled": false,
    "perKeyPerDay": 5
  }
}
```

## GET /v1/codes/{machine}

The full card of one address: every registry column under `registry`, named as in the files, plus the spot code, the Plus Code, the area and the zone, and the spoken forms. The machine form is checked first: a wrong check letter is refused, never corrected.

**One address**

```sh
curl -s 'https://addresses.example.org/v1/codes/SN-DKR-0080-2512-J'
```

`HTTP 200`

```json
{
  "machine": "SN-DKR-0080-2512-J",
  "remembered": "Ouakam 2512",
  "written": "OUAKAM 2512 · DAKAR",
  "spokenFr": "Ouakam, vingt-cinq, douze",
  "spokenWo": "Ouakam, ñaar, juróom, benn, ñaar",
  "number": 2512,
  "check": "J",
  "status": "provisional",
  "issued": "bulk",
  "issuedAt": "2026-10-20T03:43:01Z",
  "entrance": {
    "lat": 14.7247067,
    "lng": -17.4849374,
    "kind": "centre"
  },
  "spotCode": "DKR 2719 4676",
  "plusCode": "7C64PGF8+V2P",
  "area": {
    "id": "DKR-0080",
    "plateName": "Ouakam",
    "officialName": "Ouakam",
    "kind": "suburb",
    "nearTown": null,
    "needsCommuneChoice": false
  },
  "zone": {
    "key": "DKR",
    "name": "Dakar",
    "plateName": "Dakar",
    "region": "SN-DK"
  },
  "compound": {
    "class": "res.maison",
    "use": "residential",
    "kind": "un_batiment",
    "structures": 1,
    "floorAreaM2": 32.7
  },
  "postcode": null,
  "coverage": null,
  "officialAddress": null,
  "registry": {
    "canonical": "SN-DKR-0080-2512-J",
    "remembered": "Ouakam 2512",
    "written": "OUAKAM 2512 · DAKAR",
    "lieu": "DKR-0080",
    "official_name": "Ouakam",
    "number": "2512",
    "check": "J",
    "status": "provisional",
    "issued": "bulk",
    "issued_at": "2026-10-20T03:43:01Z",
    "entrance_lat": "14.7247067",
    "entrance_lng": "-17.4849374",
    "entrance_kind": "centre",
    "spot_code": "DKR 2719 4676",
    "class": "res.maison",
    "use": "residential",
    "kind": "un_batiment",
    "structures": "1",
    "floor_area_m2": "32.7",
    "postcode": "",
    "coverage": "",
    "official_address": ""
  },
  "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
}
```

**A machine form with a wrong check letter**

```sh
curl -s 'https://addresses.example.org/v1/codes/SN-DKR-0080-2512-F'
```

`HTTP 400`

```json
{
  "error": {
    "code": "invalid_code",
    "message": "Check letter does not match: a character is wrong or two are swapped."
  }
}
```

**A valid machine form that was never issued**

```sh
curl -s 'https://addresses.example.org/v1/codes/SN-DKR-0080-2513-F'
```

`HTTP 404`

```json
{
  "error": {
    "code": "not_found",
    "message": "SN-DKR-0080-2513-F is a valid form, but no address has been issued with it."
  }
}
```

## GET /v1/find?q=

Finds an address from what a person has: the remembered address in any case, spacing or accents, with or without the zone name; a machine form; the official address where the commune numbered the door; or a spot code where a compound stands.

**Find: a remembered address, typed loosely**

```sh
curl -s 'https://addresses.example.org/v1/find?q=ouakam2512'
```

`HTTP 200`

```json
{
  "query": "ouakam2512",
  "kind": "remembered",
  "matches": [
    {
      "machine": "SN-DKR-0080-2512-J",
      "remembered": "Ouakam 2512",
      "written": "OUAKAM 2512 · DAKAR",
      "spokenFr": "Ouakam, vingt-cinq, douze",
      "spokenWo": "Ouakam, ñaar, juróom, benn, ñaar",
      "number": 2512,
      "check": "J",
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-20T03:43:01Z",
      "entrance": {
        "lat": 14.7247067,
        "lng": -17.4849374,
        "kind": "centre"
      },
      "spotCode": "DKR 2719 4676",
      "plusCode": "7C64PGF8+V2P",
      "area": {
        "id": "DKR-0080",
        "plateName": "Ouakam",
        "officialName": "Ouakam",
        "kind": "suburb",
        "nearTown": null,
        "needsCommuneChoice": false
      },
      "zone": {
        "key": "DKR",
        "name": "Dakar",
        "plateName": "Dakar",
        "region": "SN-DK"
      },
      "compound": {
        "class": "res.maison",
        "use": "residential",
        "kind": "un_batiment",
        "structures": 1,
        "floorAreaM2": 32.7
      },
      "postcode": null,
      "coverage": null,
      "officialAddress": null,
      "registry": {
        "canonical": "SN-DKR-0080-2512-J",
        "remembered": "Ouakam 2512",
        "written": "OUAKAM 2512 · DAKAR",
        "lieu": "DKR-0080",
        "official_name": "Ouakam",
        "number": "2512",
        "check": "J",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-20T03:43:01Z",
        "entrance_lat": "14.7247067",
        "entrance_lng": "-17.4849374",
        "entrance_kind": "centre",
        "spot_code": "DKR 2719 4676",
        "class": "res.maison",
        "use": "residential",
        "kind": "un_batiment",
        "structures": "1",
        "floor_area_m2": "32.7",
        "postcode": "",
        "coverage": "",
        "official_address": ""
      },
      "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
    }
  ]
}
```

**Find: a five-digit number, grouped or not**

```sh
curl -s 'https://addresses.example.org/v1/find?q=MEDINA%20KEL%2017404'
```

`HTTP 200`

```json
{
  "query": "MEDINA KEL 17404",
  "kind": "remembered",
  "matches": [
    {
      "machine": "SN-PKN-0027-17404-X",
      "remembered": "Médina Kel 17 404",
      "written": "MÉDINA KEL 17 404 · PIKINE",
      "spokenFr": "Médina Kel, dix-sept, quatre cent quatre",
      "spokenWo": "Médina Kel, benn, juróom ñaar, ñeent, tus, ñeent",
      "number": 17404,
      "check": "X",
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-20T03:45:39Z",
      "entrance": {
        "lat": 14.7754149,
        "lng": -17.3127966,
        "kind": "centre"
      },
      "spotCode": "PKN 6520 3384",
      "plusCode": "7C64QMGP+5V8",
      "area": {
        "id": "PKN-0027",
        "plateName": "Médina Kel",
        "officialName": "Médina Kel",
        "kind": "locality",
        "nearTown": null,
        "needsCommuneChoice": false
      },
      "zone": {
        "key": "PKN",
        "name": "Pikine (incl. Keur Massar)",
        "plateName": "Pikine",
        "region": "SN-DK"
      },
      "compound": {
        "class": "com.boutique",
        "use": "commercial",
        "kind": "un_batiment",
        "structures": 1,
        "floorAreaM2": 259.6
      },
      "postcode": "10000",
      "coverage": "official",
      "officialAddress": "125 Boulevard Ainoumady",
      "registry": {
        "canonical": "SN-PKN-0027-17404-X",
        "remembered": "Médina Kel 17 404",
        "written": "MÉDINA KEL 17 404 · PIKINE",
        "lieu": "PKN-0027",
        "official_name": "Médina Kel",
        "number": "17404",
        "check": "X",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-20T03:45:39Z",
        "entrance_lat": "14.7754149",
        "entrance_lng": "-17.3127966",
        "entrance_kind": "centre",
        "spot_code": "PKN 6520 3384",
        "class": "com.boutique",
        "use": "commercial",
        "kind": "un_batiment",
        "structures": "1",
        "floor_area_m2": "259.6",
        "postcode": "10000",
        "coverage": "official",
        "official_address": "125 Boulevard Ainoumady"
      },
      "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
    }
  ]
}
```

**Find: an official address**

```sh
curl -s 'https://addresses.example.org/v1/find?q=125%20Boulevard%20Ainoumady'
```

`HTTP 200`

```json
{
  "query": "125 Boulevard Ainoumady",
  "kind": "official",
  "matches": [
    {
      "machine": "SN-PKN-0027-17404-X",
      "remembered": "Médina Kel 17 404",
      "written": "MÉDINA KEL 17 404 · PIKINE",
      "spokenFr": "Médina Kel, dix-sept, quatre cent quatre",
      "spokenWo": "Médina Kel, benn, juróom ñaar, ñeent, tus, ñeent",
      "number": 17404,
      "check": "X",
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-20T03:45:39Z",
      "entrance": {
        "lat": 14.7754149,
        "lng": -17.3127966,
        "kind": "centre"
      },
      "spotCode": "PKN 6520 3384",
      "plusCode": "7C64QMGP+5V8",
      "area": {
        "id": "PKN-0027",
        "plateName": "Médina Kel",
        "officialName": "Médina Kel",
        "kind": "locality",
        "nearTown": null,
        "needsCommuneChoice": false
      },
      "zone": {
        "key": "PKN",
        "name": "Pikine (incl. Keur Massar)",
        "plateName": "Pikine",
        "region": "SN-DK"
      },
      "compound": {
        "class": "com.boutique",
        "use": "commercial",
        "kind": "un_batiment",
        "structures": 1,
        "floorAreaM2": 259.6
      },
      "postcode": "10000",
      "coverage": "official",
      "officialAddress": "125 Boulevard Ainoumady",
      "registry": {
        "canonical": "SN-PKN-0027-17404-X",
        "remembered": "Médina Kel 17 404",
        "written": "MÉDINA KEL 17 404 · PIKINE",
        "lieu": "PKN-0027",
        "official_name": "Médina Kel",
        "number": "17404",
        "check": "X",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-20T03:45:39Z",
        "entrance_lat": "14.7754149",
        "entrance_lng": "-17.3127966",
        "entrance_kind": "centre",
        "spot_code": "PKN 6520 3384",
        "class": "com.boutique",
        "use": "commercial",
        "kind": "un_batiment",
        "structures": "1",
        "floor_area_m2": "259.6",
        "postcode": "10000",
        "coverage": "official",
        "official_address": "125 Boulevard Ainoumady"
      },
      "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
    }
  ]
}
```

**Find: a machine form**

```sh
curl -s 'https://addresses.example.org/v1/find?q=sn-dkr-0080-2512-j'
```

`HTTP 200`

```json
{
  "query": "sn-dkr-0080-2512-j",
  "kind": "machine",
  "matches": [
    {
      "machine": "SN-DKR-0080-2512-J",
      "remembered": "Ouakam 2512",
      "written": "OUAKAM 2512 · DAKAR",
      "spokenFr": "Ouakam, vingt-cinq, douze",
      "spokenWo": "Ouakam, ñaar, juróom, benn, ñaar",
      "number": 2512,
      "check": "J",
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-20T03:43:01Z",
      "entrance": {
        "lat": 14.7247067,
        "lng": -17.4849374,
        "kind": "centre"
      },
      "spotCode": "DKR 2719 4676",
      "plusCode": "7C64PGF8+V2P",
      "area": {
        "id": "DKR-0080",
        "plateName": "Ouakam",
        "officialName": "Ouakam",
        "kind": "suburb",
        "nearTown": null,
        "needsCommuneChoice": false
      },
      "zone": {
        "key": "DKR",
        "name": "Dakar",
        "plateName": "Dakar",
        "region": "SN-DK"
      },
      "compound": {
        "class": "res.maison",
        "use": "residential",
        "kind": "un_batiment",
        "structures": 1,
        "floorAreaM2": 32.7
      },
      "postcode": null,
      "coverage": null,
      "officialAddress": null,
      "registry": {
        "canonical": "SN-DKR-0080-2512-J",
        "remembered": "Ouakam 2512",
        "written": "OUAKAM 2512 · DAKAR",
        "lieu": "DKR-0080",
        "official_name": "Ouakam",
        "number": "2512",
        "check": "J",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-20T03:43:01Z",
        "entrance_lat": "14.7247067",
        "entrance_lng": "-17.4849374",
        "entrance_kind": "centre",
        "spot_code": "DKR 2719 4676",
        "class": "res.maison",
        "use": "residential",
        "kind": "un_batiment",
        "structures": "1",
        "floor_area_m2": "32.7",
        "postcode": "",
        "coverage": "",
        "official_address": ""
      },
      "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
    }
  ]
}
```

**Find: a wrong check letter is refused, not corrected**

```sh
curl -s 'https://addresses.example.org/v1/find?q=SN-DKR-0080-2512-F'
```

`HTTP 400`

```json
{
  "error": {
    "code": "invalid_code",
    "message": "Check letter does not match: a character is wrong or two are swapped."
  }
}
```

**Find: a number in a range with no compound yet**

```sh
curl -s 'https://addresses.example.org/v1/find?q=M%C3%A9dina%2012%20150'
```

`HTTP 404`

```json
{
  "error": {
    "code": "not_found",
    "message": "No compound has Medina 12 150 yet (the number is in the range of Medina, Dakar)."
  }
}
```

**Find: a spot code where no compound stands**

```sh
curl -s 'https://addresses.example.org/v1/find?q=DKR%205553%201512'
```

`HTTP 404`

```json
{
  "error": {
    "code": "not_found",
    "message": "No address is at DKR 5553 1512 yet: it is a spot, not an address."
  }
}
```

**Find: nothing to search for**

```sh
curl -s 'https://addresses.example.org/v1/find'
```

`HTTP 400`

```json
{
  "error": {
    "code": "bad_request",
    "message": "q is required: a remembered address (Ouakam 2512), a machine form, an official address or a spot code"
  }
}
```

## GET /v1/at?lat=&lng=

The address of the compound at a point. The point is at a compound when an outline issued by this deployment holds it, or when a live entrance is within 12 m (the issuer's distance). Otherwise the answer is `none`, with the zone, the area a new address there would be numbered in, and the spot code. A point in no zone, or more than 300 m outside the national border whatever the zones say (engine/SPEC.md 2.3), is outside Senegal (`422 outside`).

**At a point: a compound**

```sh
curl -s 'https://addresses.example.org/v1/at?lat=14.7247067&lng=-17.4849374'
```

`HTTP 200`

```json
{
  "status": "found",
  "distanceM": 0.0,
  "zone": {
    "key": "DKR",
    "name": "Dakar",
    "plateName": "Dakar"
  },
  "code": {
    "machine": "SN-DKR-0080-2512-J",
    "remembered": "Ouakam 2512",
    "written": "OUAKAM 2512 · DAKAR",
    "spokenFr": "Ouakam, vingt-cinq, douze",
    "spokenWo": "Ouakam, ñaar, juróom, benn, ñaar",
    "number": 2512,
    "check": "J",
    "status": "provisional",
    "issued": "bulk",
    "issuedAt": "2026-10-20T03:43:01Z",
    "entrance": {
      "lat": 14.7247067,
      "lng": -17.4849374,
      "kind": "centre"
    },
    "spotCode": "DKR 2719 4676",
    "plusCode": "7C64PGF8+V2P",
    "area": {
      "id": "DKR-0080",
      "plateName": "Ouakam",
      "officialName": "Ouakam",
      "kind": "suburb",
      "nearTown": null,
      "needsCommuneChoice": false
    },
    "zone": {
      "key": "DKR",
      "name": "Dakar",
      "plateName": "Dakar",
      "region": "SN-DK"
    },
    "compound": {
      "class": "res.maison",
      "use": "residential",
      "kind": "un_batiment",
      "structures": 1,
      "floorAreaM2": 32.7
    },
    "postcode": null,
    "coverage": null,
    "officialAddress": null,
    "registry": {
      "canonical": "SN-DKR-0080-2512-J",
      "remembered": "Ouakam 2512",
      "written": "OUAKAM 2512 · DAKAR",
      "lieu": "DKR-0080",
      "official_name": "Ouakam",
      "number": "2512",
      "check": "J",
      "status": "provisional",
      "issued": "bulk",
      "issued_at": "2026-10-20T03:43:01Z",
      "entrance_lat": "14.7247067",
      "entrance_lng": "-17.4849374",
      "entrance_kind": "centre",
      "spot_code": "DKR 2719 4676",
      "class": "res.maison",
      "use": "residential",
      "kind": "un_batiment",
      "structures": "1",
      "floor_area_m2": "32.7",
      "postcode": "",
      "coverage": "",
      "official_address": ""
    },
    "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
    "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
  }
}
```

**At a point: no compound within 12 m**

```sh
curl -s 'https://addresses.example.org/v1/at?lat=14.6681&lng=-17.4317'
```

`HTTP 200`

```json
{
  "status": "none",
  "zone": {
    "key": "DKR",
    "name": "Dakar",
    "plateName": "Dakar"
  },
  "area": {
    "id": "DKR-0025",
    "plateName": "Plateau",
    "officialName": "Dakar-Plateau",
    "kind": "suburb"
  },
  "spotCode": "DKR 5553 1512"
}
```

**At a point outside Senegal**

```sh
curl -s 'https://addresses.example.org/v1/at?lat=13.4549&lng=-16.5790'
```

`HTTP 422`

```json
{
  "error": {
    "code": "outside",
    "message": "That point is outside Senegal."
  }
}
```

**At a point the zone rule reaches, across the national border**

The point is on the far bank of the Senegal river, about 800 m outside the border: within 2 km of Dagana's outline, so the zone rule alone would give it a zone, but the border decides.

```sh
curl -s 'https://addresses.example.org/v1/at?lat=16.5&lng=-15.7755'
```

`HTTP 422`

```json
{
  "error": {
    "code": "outside",
    "message": "That point is outside Senegal."
  }
}
```

## GET /v1/near?lat=&lng=&radius=&limit=

Live addresses whose entrance is within `radius` metres (default 100, at most 500), nearest first, at most `limit` (default 20, at most 100).

**Near a point**

```sh
curl -s 'https://addresses.example.org/v1/near?lat=14.7247067&lng=-17.4849374&radius=30&limit=3'
```

`HTTP 200`

```json
{
  "lat": 14.7247067,
  "lng": -17.4849374,
  "radiusM": 30.0,
  "count": 3,
  "codes": [
    {
      "distanceM": 0.0,
      "machine": "SN-DKR-0080-2512-J",
      "remembered": "Ouakam 2512",
      "status": "provisional",
      "entrance": {
        "lat": 14.7247067,
        "lng": -17.4849374,
        "kind": "centre"
      },
      "spotCode": "DKR 2719 4676"
    },
    {
      "distanceM": 6.9,
      "machine": "SN-DKR-0080-2472-W",
      "remembered": "Ouakam 2472",
      "status": "provisional",
      "entrance": {
        "lat": 14.7247569,
        "lng": -17.484975,
        "kind": "centre"
      },
      "spotCode": "DKR 2717 4679"
    },
    {
      "distanceM": 7.9,
      "machine": "SN-DKR-0080-2509-K",
      "remembered": "Ouakam 2509",
      "status": "provisional",
      "entrance": {
        "lat": 14.7247175,
        "lng": -17.484865,
        "kind": "centre"
      },
      "spotCode": "DKR 2723 4677"
    }
  ]
}
```

**Near: radius over 500 m**

```sh
curl -s 'https://addresses.example.org/v1/near?lat=14.7247067&lng=-17.4849374&radius=800'
```

`HTTP 400`

```json
{
  "error": {
    "code": "bad_request",
    "message": "radius is in metres, more than 0 and at most 500"
  }
}
```

## GET /v1/verify?code=

Checks a machine form (shape, zone, area, number in the area's blocks, check letter) and says whether it has been issued. A spot code is checked for its shape and zone.

**Verify a machine form**

```sh
curl -s 'https://addresses.example.org/v1/verify?code=SN-DKR-0080-2512-J'
```

`HTTP 200`

```json
{
  "code": "SN-DKR-0080-2512-J",
  "kind": "machine",
  "valid": true,
  "reason": null,
  "machine": "SN-DKR-0080-2512-J",
  "issued": true,
  "status": "provisional"
}
```

**Verify: two digits swapped**

```sh
curl -s 'https://addresses.example.org/v1/verify?code=SN-DKR-0080-2152-J'
```

`HTTP 200`

```json
{
  "code": "SN-DKR-0080-2152-J",
  "kind": "machine",
  "valid": false,
  "reason": "Check letter does not match: a character is wrong or two are swapped.",
  "issued": false
}
```

## GET /v1/spot?lat=&lng=

The spot code of any point in Senegal, computed offline from the zone grid.

**Spot code of a point**

```sh
curl -s 'https://addresses.example.org/v1/spot?lat=14.6681&lng=-17.4317'
```

`HTTP 200`

```json
{
  "spotCode": "DKR 5553 1512",
  "zone": "DKR",
  "cellMetres": 2,
  "spokenFr": "D K R | cinquante-cinq, cinquante-trois | quinze, douze",
  "spokenWo": "D K R | juróom, juróom, juróom, ñett | benn, juróom, benn, ñaar",
  "plusCode": "7C64MH99+68V"
}
```

## GET /v1/spot/decode?code=

The centre of a spot code's cell.

**Decode a spot code**

```sh
curl -s 'https://addresses.example.org/v1/spot/decode?code=DKR%205553%201512'
```

`HTTP 200`

```json
{
  "spotCode": "DKR 5553 1512",
  "zone": "DKR",
  "lat": 14.6681018,
  "lng": -17.4316927,
  "cellMetres": 2
}
```

**Decode: wrong number of digits**

```sh
curl -s 'https://addresses.example.org/v1/spot/decode?code=DKR%20555%201512'
```

`HTTP 400`

```json
{
  "error": {
    "code": "invalid_code",
    "message": "Not an N-Ways Senegal code."
  }
}
```

## GET /v1/zones

The 46 code zones with their grid, counts and bounding boxes.

**Zones**

```sh
curl -s 'https://addresses.example.org/v1/zones'
```

`HTTP 200`

```json
{
  "count": 46,
  "zones": [
    {
      "key": "BIG",
      "index": 0,
      "name": "Bignona",
      "plateName": "Bignona",
      "region": "SN-ZG",
      "digits": 4,
      "cellMetres": 10,
      "origin": {
        "e": 306000,
        "n": 1388000
      },
      "frameMetres": 98000,
      "areas": 595,
      "codes": 65019,
      "byStatus": {
        "provisional": 65019
      },
      "bbox": [
        -16.7871,
        12.5542,
        -15.894,
        13.1704
      ]
    },
    {
      "key": "BKL",
      "index": 1,
      "name": "Bakel",
      "plateName": "Bakel",
      "region": "SN-TC",
      "digits": 5,
      "cellMetres": 10,
      "origin": {
        "e": 748000,
        "n": 1473000
      },
      "frameMetres": 199000,
      "areas": 219,
      "codes": 41737,
      "byStatus": {
        "provisional": 41737
      },
      "bbox": [
        -12.6877,
        13.3111,
        -11.8642,
        15.1112
      ]
    }
  ]
}
```

Shortened here: `zones` has 46 entries, the first 2 are shown.

## GET /v1/zones/{key}

One zone and the list of its areas (lieux) with their blocks and counts.

**One zone, with its areas**

```sh
curl -s 'https://addresses.example.org/v1/zones/TBA'
```

`HTTP 200`

```json
{
  "key": "TBA",
  "index": 40,
  "name": "Touba-Mbacké (arr. de Ndame)",
  "plateName": "Touba-Mbacké",
  "region": "SN-DB",
  "digits": 4,
  "cellMetres": 5,
  "origin": {
    "e": 379000,
    "n": 1627000
  },
  "frameMetres": 49000,
  "areas": 241,
  "codes": 289328,
  "byStatus": {
    "provisional": 289328
  },
  "bbox": [
    -16.1161,
    14.718,
    -15.6734,
    14.9977
  ],
  "areaList": [
    {
      "id": "TBA-0000",
      "plateName": "Afé Gouye",
      "officialName": "Afé Gouye",
      "kind": "locality",
      "digits": 4,
      "blocks": [
        [
          1000,
          2999
        ]
      ],
      "codes": 657
    },
    {
      "id": "TBA-0001",
      "plateName": "Alie",
      "officialName": "Alie",
      "kind": "suburb",
      "digits": 5,
      "blocks": [
        [
          10000,
          23999
        ]
      ],
      "codes": 4643
    }
  ]
}
```

Shortened here: `areaList` has 241 entries, the first 2 are shown.

**An unknown zone**

```sh
curl -s 'https://addresses.example.org/v1/zones/XYZ'
```

`HTTP 404`

```json
{
  "error": {
    "code": "not_found",
    "message": "There is no zone 'XYZ'. GET /v1/zones lists the 46 zones."
  }
}
```

## GET /v1/zones/{key}/codes?after=&limit=

Every address of a zone in machine-form order, a page at a time (default 100, at most 1,000). Pass the `next` of a page as `after` to get the following one; `next` is null on the last page.

**Addresses of a zone, page by page**

```sh
curl -s 'https://addresses.example.org/v1/zones/DKR/codes?limit=3'
```

`HTTP 200`

```json
{
  "zone": "DKR",
  "after": null,
  "count": 3,
  "codes": [
    {
      "machine": "SN-DKR-0000-1001-M",
      "remembered": "Almadies 1001",
      "status": "provisional",
      "entrance": {
        "lat": 14.7383683,
        "lng": -17.5167533,
        "kind": "centre"
      },
      "spotCode": "DKR 1013 5451"
    },
    {
      "machine": "SN-DKR-0000-1004-X",
      "remembered": "Almadies 1004",
      "status": "provisional",
      "entrance": {
        "lat": 14.7384155,
        "lng": -17.5165486,
        "kind": "centre"
      },
      "spotCode": "DKR 1024 5454"
    },
    {
      "machine": "SN-DKR-0000-1007-K",
      "remembered": "Almadies 1007",
      "status": "provisional",
      "entrance": {
        "lat": 14.7385692,
        "lng": -17.5166776,
        "kind": "centre"
      },
      "spotCode": "DKR 1018 5462"
    }
  ],
  "next": "SN-DKR-0000-1007-K"
}
```

**The next page**

```sh
curl -s 'https://addresses.example.org/v1/zones/DKR/codes?limit=3&after=SN-DKR-0000-1007-R'
```

`HTTP 200`

```json
{
  "zone": "DKR",
  "after": "SN-DKR-0000-1007-R",
  "count": 3,
  "codes": [
    {
      "machine": "SN-DKR-0000-1010-J",
      "remembered": "Almadies 1010",
      "status": "provisional",
      "entrance": {
        "lat": 14.738798,
        "lng": -17.5168995,
        "kind": "centre"
      },
      "spotCode": "DKR 1006 5475"
    },
    {
      "machine": "SN-DKR-0000-1013-T",
      "remembered": "Almadies 1013",
      "status": "provisional",
      "entrance": {
        "lat": 14.7387805,
        "lng": -17.5167382,
        "kind": "centre"
      },
      "spotCode": "DKR 1014 5474"
    },
    {
      "machine": "SN-DKR-0000-1016-H",
      "remembered": "Almadies 1016",
      "status": "provisional",
      "entrance": {
        "lat": 14.7390099,
        "lng": -17.5166789,
        "kind": "centre"
      },
      "spotCode": "DKR 1018 5487"
    }
  ],
  "next": "SN-DKR-0000-1016-H"
}
```

## GET /v1/areas/{id}

One area: plate and official names, aliases, name family and the other areas that share its national range, its blocks and how much of each is used.

**One area**

```sh
curl -s 'https://addresses.example.org/v1/areas/DKR-0080'
```

`HTTP 200`

```json
{
  "id": "DKR-0080",
  "zone": "DKR",
  "index": 80,
  "plateName": "Ouakam",
  "officialName": "Ouakam",
  "kind": "suburb",
  "aliases": [],
  "nearTown": null,
  "coverage": "nways",
  "needsCommuneChoice": false,
  "nameKey": "wakam",
  "family": 10796,
  "digits": 4,
  "blocks": [
    [
      1000,
      3399
    ]
  ],
  "sameName": [],
  "position": {
    "lat": 14.7247404,
    "lng": -17.4850623,
    "e": 232425.0,
    "n": 1629357.0
  },
  "codes": {
    "total": 788,
    "byStatus": {
      "provisional": 788
    }
  },
  "blockUse": [
    {
      "block": [
        1000,
        3399
      ],
      "size": 2400,
      "used": 788
    }
  ]
}
```

## GET /v1/areas?name=

Areas whose plate name, official name or alias has the same name key as `name` (so spelling variants match), and those whose name starts with it. At most 50.

**Areas by name**

```sh
curl -s 'https://addresses.example.org/v1/areas?name=Darou%20Salam'
```

`HTTP 200`

```json
{
  "name": "Darou Salam",
  "count": 40,
  "areas": [
    {
      "id": "BKL-0034",
      "zone": "BKL",
      "index": 34,
      "plateName": "Darou Salam",
      "officialName": "Darou Salam",
      "kind": "village",
      "aliases": [],
      "nearTown": null,
      "coverage": "nways",
      "needsCommuneChoice": false,
      "nameKey": "darusalam",
      "family": 1684,
      "digits": 5,
      "blocks": [
        [
          10000,
          10099
        ]
      ],
      "sameName": [
        "DBL-0023",
        "DBL-0024",
        "GOS-0049",
        "KAF-0042",
        "KAF-0043",
        "KAF-0044",
        "KBM-0079",
        "KGH-0028",
        "KGH-0029",
        "KNL-0038",
        "KPT-0035",
        "MBR-0032",
        "MHD-0024",
        "MHD-0025",
        "NRP-0041",
        "NRP-0042",
        "PKN-0010",
        "RAN-0022",
        "TBA-0054",
        "TBC-0056",
        "TIV-0089",
        "VEL-0041"
      ],
      "position": {
        "lat": 14.4013825,
        "lng": -12.2114724,
        "e": 800710.0,
        "n": 1593939.0
      },
      "codes": {
        "total": 17,
        "byStatus": {
          "provisional": 17
        }
      }
    },
    {
      "id": "DBL-0023",
      "zone": "DBL",
      "index": 23,
      "plateName": "Darou Salam",
      "officialName": "Darou Salam",
      "kind": "village",
      "aliases": [
        "Darou Salam (Ndiourene)"
      ],
      "nearTown": "Ndindy",
      "coverage": "nways",
      "needsCommuneChoice": false,
      "nameKey": "darusalam",
      "family": 1684,
      "digits": 5,
      "blocks": [
        [
          10100,
          10199
        ]
      ],
      "sameName": [
        "BKL-0034",
        "DBL-0024",
        "GOS-0049",
        "KAF-0042",
        "KAF-0043",
        "KAF-0044",
        "KBM-0079",
        "KGH-0028",
        "KGH-0029",
        "KNL-0038",
        "KPT-0035",
        "MBR-0032",
        "MHD-0024",
        "MHD-0025",
        "NRP-0041",
        "NRP-0042",
        "PKN-0010",
        "RAN-0022",
        "TBA-0054",
        "TBC-0056",
        "TIV-0089",
        "VEL-0041"
      ],
      "position": {
        "lat": 14.788929,
        "lng": -16.2773276,
        "e": 362534.0,
        "n": 1635372.0
      },
      "codes": {
        "total": 16,
        "byStatus": {
          "provisional": 16
        }
      }
    }
  ]
}
```

Shortened here: `areas` has 40 entries, the first 2 are shown.

## POST /v1/codes

Issues an address for a compound that has none (`lat`, `lng`, optional `outline` as `[lng, lat]` points), or for another door of a compound (`of`). Needs an issuing key, and only the deployment designated as Senegal's issuer has keys (see server/README.md). The checks, distances, limits, the choice of area and the number are those of the N-Ways issuer. A new address is `provisional` and `on-demand`. The point must lie inside the national border or within 300 m of it, whatever the zone outlines say (engine/SPEC.md 2.3).

**Issue an address for a new compound**

```sh
curl -s -X POST -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"lat": 14.6681, "lng": -17.4317, "outline": [[-17.43179, 14.66804], [-17.43161, 14.66804], [-17.43161, 14.66817], [-17.43179, 14.66817]]}' 'https://addresses.example.org/v1/codes'
```

`HTTP 201`

```json
{
  "machine": "SN-DKR-0025-1005-H",
  "remembered": "Plateau 1005",
  "written": "PLATEAU 1005 · DAKAR",
  "spokenFr": "Plateau, dix, zéro cinq",
  "spokenWo": "Plateau, benn, tus, tus, juróom",
  "number": 1005,
  "check": "H",
  "status": "provisional",
  "issued": "on-demand",
  "issuedAt": "2026-10-21T19:01:28Z",
  "entrance": {
    "lat": 14.6681,
    "lng": -17.4317,
    "kind": "centre"
  },
  "spotCode": "DKR 5553 1512",
  "plusCode": "7C64MH99+68V",
  "area": {
    "id": "DKR-0025",
    "plateName": "Plateau",
    "officialName": "Dakar-Plateau",
    "kind": "suburb",
    "nearTown": null,
    "needsCommuneChoice": false
  },
  "zone": {
    "key": "DKR",
    "name": "Dakar",
    "plateName": "Dakar",
    "region": "SN-DK"
  },
  "compound": {
    "class": "res.maison",
    "use": "residential",
    "kind": "un_batiment",
    "structures": 1,
    "floorAreaM2": 279.1
  },
  "postcode": null,
  "coverage": null,
  "officialAddress": null,
  "registry": {
    "canonical": "SN-DKR-0025-1005-H",
    "remembered": "Plateau 1005",
    "written": "PLATEAU 1005 · DAKAR",
    "lieu": "DKR-0025",
    "official_name": "Dakar-Plateau",
    "number": "1005",
    "check": "H",
    "status": "provisional",
    "issued": "on-demand",
    "issued_at": "2026-10-21T19:01:28Z",
    "entrance_lat": "14.6681000",
    "entrance_lng": "-17.4317000",
    "entrance_kind": "centre",
    "spot_code": "DKR 5553 1512",
    "class": "res.maison",
    "use": "residential",
    "kind": "un_batiment",
    "structures": "1",
    "floor_area_m2": "279.1",
    "postcode": "",
    "coverage": "",
    "official_address": ""
  },
  "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
}
```

**Another door of a compound**

```sh
curl -s -X POST -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"lat": 14.72475, "lng": -17.48484, "of": "SN-DKR-0080-2512-J"}' 'https://addresses.example.org/v1/codes'
```

`HTTP 201`

```json
{
  "machine": "SN-DKR-0080-2510-R",
  "remembered": "Ouakam 2510",
  "written": "OUAKAM 2510 · DAKAR",
  "spokenFr": "Ouakam, vingt-cinq, dix",
  "spokenWo": "Ouakam, ñaar, juróom, benn, tus",
  "number": 2510,
  "check": "R",
  "status": "provisional",
  "issued": "on-demand",
  "issuedAt": "2026-10-21T19:01:28Z",
  "entrance": {
    "lat": 14.72475,
    "lng": -17.48484,
    "kind": "door"
  },
  "spotCode": "DKR 2724 4678",
  "plusCode": "7C64PGF8+W33",
  "area": {
    "id": "DKR-0080",
    "plateName": "Ouakam",
    "officialName": "Ouakam",
    "kind": "suburb",
    "nearTown": null,
    "needsCommuneChoice": false
  },
  "zone": {
    "key": "DKR",
    "name": "Dakar",
    "plateName": "Dakar",
    "region": "SN-DK"
  },
  "compound": {
    "class": null,
    "use": "unknown",
    "kind": "porte",
    "structures": 0,
    "floorAreaM2": 0.0
  },
  "postcode": null,
  "coverage": null,
  "officialAddress": null,
  "registry": {
    "canonical": "SN-DKR-0080-2510-R",
    "remembered": "Ouakam 2510",
    "written": "OUAKAM 2510 · DAKAR",
    "lieu": "DKR-0080",
    "official_name": "Ouakam",
    "number": "2510",
    "check": "R",
    "status": "provisional",
    "issued": "on-demand",
    "issued_at": "2026-10-21T19:01:28Z",
    "entrance_lat": "14.7247500",
    "entrance_lng": "-17.4848400",
    "entrance_kind": "door",
    "spot_code": "DKR 2724 4678",
    "class": "",
    "use": "unknown",
    "kind": "porte",
    "structures": "0",
    "floor_area_m2": "0.0",
    "postcode": "",
    "coverage": "",
    "official_address": ""
  },
  "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
}
```

**The same building again**

```sh
curl -s -X POST -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"lat": 14.66811, "lng": -17.43171}' 'https://addresses.example.org/v1/codes'
```

`HTTP 409`

```json
{
  "error": {
    "code": "exists",
    "message": "This building already has its address: Plateau 1005.",
    "existing": {
      "machine": "SN-DKR-0025-1005-H",
      "remembered": "Plateau 1005",
      "written": "PLATEAU 1005 · DAKAR",
      "spokenFr": "Plateau, dix, zéro cinq",
      "spokenWo": "Plateau, benn, tus, tus, juróom",
      "number": 1005,
      "check": "H",
      "status": "provisional",
      "issued": "on-demand",
      "issuedAt": "2026-10-21T19:01:28Z",
      "entrance": {
        "lat": 14.6681,
        "lng": -17.4317,
        "kind": "centre"
      },
      "spotCode": "DKR 5553 1512",
      "plusCode": "7C64MH99+68V",
      "area": {
        "id": "DKR-0025",
        "plateName": "Plateau",
        "officialName": "Dakar-Plateau",
        "kind": "suburb",
        "nearTown": null,
        "needsCommuneChoice": false
      },
      "zone": {
        "key": "DKR",
        "name": "Dakar",
        "plateName": "Dakar",
        "region": "SN-DK"
      },
      "compound": {
        "class": "res.maison",
        "use": "residential",
        "kind": "un_batiment",
        "structures": 1,
        "floorAreaM2": 279.1
      },
      "postcode": null,
      "coverage": null,
      "officialAddress": null,
      "registry": {
        "canonical": "SN-DKR-0025-1005-H",
        "remembered": "Plateau 1005",
        "written": "PLATEAU 1005 · DAKAR",
        "lieu": "DKR-0025",
        "official_name": "Dakar-Plateau",
        "number": "1005",
        "check": "H",
        "status": "provisional",
        "issued": "on-demand",
        "issued_at": "2026-10-21T19:01:28Z",
        "entrance_lat": "14.6681000",
        "entrance_lng": "-17.4317000",
        "entrance_kind": "centre",
        "spot_code": "DKR 5553 1512",
        "class": "res.maison",
        "use": "residential",
        "kind": "un_batiment",
        "structures": "1",
        "floor_area_m2": "279.1",
        "postcode": "",
        "coverage": "",
        "official_address": ""
      },
      "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
    }
  }
}
```

**An outline too small for a compound**

```sh
curl -s -X POST -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"lat": 14.669, "lng": -17.433, "outline": [[-17.43301, 14.66899], [-17.43299, 14.66899], [-17.43299, 14.66901], [-17.43301, 14.66901]]}' 'https://addresses.example.org/v1/codes'
```

`HTTP 422`

```json
{
  "error": {
    "code": "bad_outline",
    "message": "That outline is 5 m², but a compound's is between 12 m² and 2 ha."
  }
}
```

**A point across the national border**

```sh
curl -s -X POST -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"lat": 16.5, "lng": -15.7755}' 'https://addresses.example.org/v1/codes'
```

`HTTP 422`

```json
{
  "error": {
    "code": "outside",
    "message": "That spot is outside Senegal, so it cannot have an N-Ways Senegal address."
  }
}
```

**A door more than 80 m away**

```sh
curl -s -X POST -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"lat": 14.73, "lng": -17.4849, "of": "SN-DKR-0080-2512-J"}' 'https://addresses.example.org/v1/codes'
```

`HTTP 422`

```json
{
  "error": {
    "code": "far",
    "message": "That door is more than 80 m from Ouakam 2512."
  }
}
```

**No key**

```sh
curl -s -X POST -H 'Content-Type: application/json' -d '{"lat": 14.6681, "lng": -17.4317}' 'https://addresses.example.org/v1/codes'
```

`HTTP 401`

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Send the issuing key as \"Authorization: Bearer <key>\"."
  }
}
```

**Issuing on a read-only deployment**

```sh
curl -s -X POST -H 'Authorization: Bearer any-key' -H 'Content-Type: application/json' -d '{"lat": 14.6681, "lng": -17.4317}' 'https://addresses.example.org/v1/codes'
```

`HTTP 403`

```json
{
  "error": {
    "code": "read_only",
    "message": "This deployment is read-only: it serves the published registry and does not issue. Only the deployment designated as Senegal's issuer issues addresses."
  }
}
```

## PATCH /v1/codes/{machine}

Changes the status (`provisional` to `confirmed`, either to `retired`, or `confirmed` back to `provisional` while a dispute is open) or moves the entrance to the real gate, at most 80 m and never more than 300 m outside the national border (`422 outside`). A retired address is never used again and cannot be changed.

**Confirm an address**

```sh
curl -s -X PATCH -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"status": "confirmed"}' 'https://addresses.example.org/v1/codes/SN-DKR-0080-2512-J'
```

`HTTP 200`

```json
{
  "machine": "SN-DKR-0080-2512-J",
  "remembered": "Ouakam 2512",
  "written": "OUAKAM 2512 · DAKAR",
  "spokenFr": "Ouakam, vingt-cinq, douze",
  "spokenWo": "Ouakam, ñaar, juróom, benn, ñaar",
  "number": 2512,
  "check": "J",
  "status": "confirmed",
  "issued": "bulk",
  "issuedAt": "2026-10-20T03:43:01Z",
  "entrance": {
    "lat": 14.7247067,
    "lng": -17.4849374,
    "kind": "centre"
  },
  "spotCode": "DKR 2719 4676",
  "plusCode": "7C64PGF8+V2P",
  "area": {
    "id": "DKR-0080",
    "plateName": "Ouakam",
    "officialName": "Ouakam",
    "kind": "suburb",
    "nearTown": null,
    "needsCommuneChoice": false
  },
  "zone": {
    "key": "DKR",
    "name": "Dakar",
    "plateName": "Dakar",
    "region": "SN-DK"
  },
  "compound": {
    "class": "res.maison",
    "use": "residential",
    "kind": "un_batiment",
    "structures": 1,
    "floorAreaM2": 32.7
  },
  "postcode": null,
  "coverage": null,
  "officialAddress": null,
  "registry": {
    "canonical": "SN-DKR-0080-2512-J",
    "remembered": "Ouakam 2512",
    "written": "OUAKAM 2512 · DAKAR",
    "lieu": "DKR-0080",
    "official_name": "Ouakam",
    "number": "2512",
    "check": "J",
    "status": "confirmed",
    "issued": "bulk",
    "issued_at": "2026-10-20T03:43:01Z",
    "entrance_lat": "14.7247067",
    "entrance_lng": "-17.4849374",
    "entrance_kind": "centre",
    "spot_code": "DKR 2719 4676",
    "class": "res.maison",
    "use": "residential",
    "kind": "un_batiment",
    "structures": "1",
    "floor_area_m2": "32.7",
    "postcode": "",
    "coverage": "",
    "official_address": ""
  },
  "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
}
```

**Move the entrance to the real gate**

```sh
curl -s -X PATCH -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"entrance": {"lat": 14.72462, "lng": -17.485}}' 'https://addresses.example.org/v1/codes/SN-DKR-0080-2512-J'
```

`HTTP 200`

```json
{
  "machine": "SN-DKR-0080-2512-J",
  "remembered": "Ouakam 2512",
  "written": "OUAKAM 2512 · DAKAR",
  "spokenFr": "Ouakam, vingt-cinq, douze",
  "spokenWo": "Ouakam, ñaar, juróom, benn, ñaar",
  "number": 2512,
  "check": "J",
  "status": "confirmed",
  "issued": "bulk",
  "issuedAt": "2026-10-20T03:43:01Z",
  "entrance": {
    "lat": 14.72462,
    "lng": -17.485,
    "kind": "gate"
  },
  "spotCode": "DKR 2715 4671",
  "plusCode": "7C64PGF8+R2R",
  "area": {
    "id": "DKR-0080",
    "plateName": "Ouakam",
    "officialName": "Ouakam",
    "kind": "suburb",
    "nearTown": null,
    "needsCommuneChoice": false
  },
  "zone": {
    "key": "DKR",
    "name": "Dakar",
    "plateName": "Dakar",
    "region": "SN-DK"
  },
  "compound": {
    "class": "res.maison",
    "use": "residential",
    "kind": "un_batiment",
    "structures": 1,
    "floorAreaM2": 32.7
  },
  "postcode": null,
  "coverage": null,
  "officialAddress": null,
  "registry": {
    "canonical": "SN-DKR-0080-2512-J",
    "remembered": "Ouakam 2512",
    "written": "OUAKAM 2512 · DAKAR",
    "lieu": "DKR-0080",
    "official_name": "Ouakam",
    "number": "2512",
    "check": "J",
    "status": "confirmed",
    "issued": "bulk",
    "issued_at": "2026-10-20T03:43:01Z",
    "entrance_lat": "14.7246200",
    "entrance_lng": "-17.4850000",
    "entrance_kind": "gate",
    "spot_code": "DKR 2715 4671",
    "class": "res.maison",
    "use": "residential",
    "kind": "un_batiment",
    "structures": "1",
    "floor_area_m2": "32.7",
    "postcode": "",
    "coverage": "",
    "official_address": ""
  },
  "credit": "N-Ways Addressing for Senegal, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-senegal"
}
```

**A move of more than 80 m**

```sh
curl -s -X PATCH -H 'Authorization: Bearer demo-key-1' -H 'Content-Type: application/json' -d '{"entrance": {"lat": 14.73, "lng": -17.4849}}' 'https://addresses.example.org/v1/codes/SN-DKR-0080-2512-J'
```

`HTTP 422`

```json
{
  "error": {
    "code": "far",
    "message": "The entrance moves at most 80 m; that point is 599 m away."
  }
}
```

## Unknown paths

**An unknown endpoint**

```sh
curl -s 'https://addresses.example.org/v1/streets'
```

`HTTP 404`

```json
{
  "error": {
    "code": "not_found",
    "message": "There is no endpoint /v1/streets. GET /v1/info describes this service; the full list is in openapi.yaml."
  }
}
```

