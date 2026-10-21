# Governance: N-Ways Addressing for Senegal

## Status

**Issued on 20 October 2026; open (LICENSING.md).** These addresses are "N-Ways addresses". They are not national addresses, not postcodes, and not land titles. Nobody may call them official until a Senegalese public authority adopts them.

## Maintainers

| Role | Who | Responsibility |
|---|---|---|
| Maintainer | N-WAYS LIMITED | Approves changes to the zones, the code format, the engine and the registry rules. Publishes releases. Answers privacy requests. |
| Registry operator | N-WAYS LIMITED | Issues addresses. It is the single issuer, so no two homes share an address. Applies the people-confirmed corrections described in `docs/model.md`, and publishes the registry in `registry/`. |
| Reviewers wanted | La Poste Sénégal; the Adressage Numérique National programme (Ministry in charge of digital affairs); the Direction du Cadastre (DGID); municipalities (the communes that run street addressing); the CDP for privacy | They are invited to review, and their review is welcome at any time. |

## What can change, and how

| Thing | Can it change? | Rule |
|---|---|---|
| A **zone** (its key, its index, its outline) | **Never.** | Zones are frozen on 2026-10-18. New administrative units, such as Keur Massar (2021), are shown as attributes and never move a zone. A place that runs out of numbers continues as "<lieu> Extension" (SPEC section 7.4); the zone outline never changes. |
| A new zone | Only to cover land no zone covers (for example land reclaimed from the sea). | It gets the next index and a new key. Existing addresses are untouched. |
| An issued **address** (place word + number) | **Never** reused, never moved. | A merge keeps both addresses, with one as an alias. A split keeps the address on the part with the gate. A demolished compound's address is retired, never reissued. |
| A **lieu** (place word) | Its index, name, name family, number length and block are frozen at first issue. | New spellings and new names are added as aliases. A renamed, split or disputed quartier never changes an address. A lieu whose block fills gets a further block from its name's free space, then continues as "<lieu> Extension". |
| A **name's national range** (SPEC 3.3) | Its blocks are never renumbered, moved or shrunk. | A new lieu with an existing name gets a new block from the name's free space. A name that runs out of space gives the new lieu one established qualifier, decided once with its commune and published. The name normalisation never changes for issued addresses. |
| **Structure indices** inside a compound | Append only. | A new structure gets the next index. A demolished one keeps its index, marked retired. |
| The **spot grid** (origins, cell sizes, digits) | **Never.** | It is part of the zone definition. |
| The **check letter** method | **Never.** | ISO/IEC 7064 MOD 11-2 with the letters `FHJKMQRTWXZ`. |
| **Building profiles** (class, size, name, status) | Any time. | Updated by evidence (SPEC section 6). Each attribute carries its source and its last-confirmed date. |
| This document, the SPEC, the papers | Yes. | By pull request with a maintainer's approval. The SPEC version number goes up on any change to the algorithms. |

Format changes that would alter any issued address are not allowed. Anything that needs one becomes a new, separate system with a new name.

## Government addresses first

Where a government address system exists, even partially, N-Ways uses the government's data and shows its address exactly as written. An official address is the one people are held to in law and administration, so a second address must never compete with it. In Senegal that means the municipal street addressing today and the ANN once it publishes. N-Ways addresses are proposed only where nothing official exists. The coverage mask (SPEC 3.6) records, for each place, which applies. It only grows, and when it reaches a place, that place's N-Ways addresses become aliases of the official ones.

## One issuer, many copies

Addresses are issued by one issuer only: N-WAYS LIMITED today, or the body the State designates. A new address takes the next free number in its area's block. Two issuers working from the same registry would each see the same number as free and give it to two compounds, and nothing could later say which is right.

Anyone may run a copy of the registry with the ready-made server (`server/`): a ministry, La Poste, a commune, an emergency service, a university or a company. A copy is read-only. It serves the published registry and updates from each new export. A deployment issues addresses only when the State or N-WAYS LIMITED has designated it as Senegal's issuer, and the previous issuer then stops. The handover starts from the latest published registry, including `registry/anchors/`, so the new issuer gives exactly the numbers the old one would have.

## If the state's system goes live (ANN)

1. When the ANN publishes a door-level address format, N-Ways shows the **ANN address first**, everywhere: app, plates, API. The N-Ways address stays as a cross-reference (`annId` on each compound) for as long as people still use it.
2. N-Ways offers the ANN the registry, the zones, the engine and the history of people's confirmations under its open licences (LICENSING.md: Apache 2.0 code, ODbL data, CC BY 4.0 documents), free of charge.
3. N-Ways never presents its addresses as an alternative to the ANN, and never asks a public body to choose between them.

## Hand-over to a national body

The repository is built so that it can be transferred whole. Its zones, registry, engine and rules depend on nothing outside this repository. A hand-over would work like this:

1. A Senegalese public body (the ANN programme, La Poste, or a body they designate) asks for it in writing.
2. N-Ways transfers the repository and the issuing rights, and names a contact for the transition.
3. The new body becomes maintainer and registry operator. N-Ways continues as a user, a contributor and the operator of the app.
4. Issued addresses stay valid after the transfer, unless the new body decides to retire them in favour of its own, with a published crosswalk.

## Disputes and corrections

- **A wrong grouping**, such as "these two houses are separate homes" or "these buildings are one home", is settled by people's agreement, the same way N-Ways settles map corrections: two independent confirmations, or the building's owner plus one other person. It is not queued for staff review.
- **A dispute between neighbours over a plot outline** (from "Add my home") freezes that compound at provisional status. N-Ways never decides land disputes, because an address is not a land title. The provisional address stays on the gate, but the outline is not published until the dispute clears.
- **Privacy requests** (making a door private, removing a business name, renaming a place word) are answered by the maintainer within 30 days and take effect immediately in the app.
