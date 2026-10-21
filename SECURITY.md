# Security and privacy

## Reporting a problem

Write to **hello@nways.ng**, with "Security" or "Privacy" in the subject. Write privately before you publish anything. Please include:

- what you found and where: a file, an endpoint, a deployment URL, or an address in machine form;
- how to reproduce it;
- what an attacker or a mistaken reader could do with it.

We acknowledge a report within 3 working days and say what we will do. We fix or mitigate within 30 days, sooner when people's safety or privacy is at stake, and credit the reporter if they wish.

## What counts

- **Privacy.** The registry describes places, never people: no names, phone numbers or households (docs/model.md section 9). Report anything in the registry, the documents or an API response that identifies a person. Report also a home that carries a name, or a door that a household asked to hide but that is still shown. N-WAYS LIMITED answers privacy requests within 30 days (GOVERNANCE.md).
- **The server.** Report a way to issue or change an address without a key, to exceed the daily limit, to read the database beyond the API, to crash the service with a request, or to make two deployments disagree on the same registry.
- **The registry files.** Report a file whose SHA-256 does not match its manifest, or an address that decodes to two places.

## Running a deployment safely

- Run read-only (no `ISSUE_KEYS`) unless your deployment is the designated issuer.
- Serve issuing deployments over TLS only, keep the keys out of the repository and out of logs, and give each office its own key so that one can be withdrawn.
- Back up an issuing deployment daily (server/README.md).
