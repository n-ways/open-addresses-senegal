# Contributing

N-Ways Addressing for Senegal welcomes corrections and improvements from anyone: residents, communes, La Poste, the ANN programme, researchers and developers.

## What you can propose

- **A correction to a place name.** Examples: a misspelt plate name, a missing alias, the plate name a commune has chosen for a flagged lieu (`needsCouncilChoice`). Open an issue with the lieu id (for example `DKR-0080`, from `/v1/areas?name=` or `registry/lieux.csv`), the name, and a source: the commune's decision, a published list or a sign. A plate name or an alias changes no issued number.
- **A correction to an address.** Examples: the wrong entrance, two homes under one address, or a building that is gone. In the N-Ways app, the people at the door confirm or correct it, and agreement settles it (GOVERNANCE.md, "Disputes and corrections"). You can also open an issue with the machine form (`SN-DKR-0080-2512-J`) and what is wrong. Do not put anyone's name or phone number in an issue.
- **A change to the code, the server, the tools or the documents.** Send a pull request against `main`. Keep the engine to the standard library. Run the tests below and say in the pull request what you ran.
- **A change to the model.** Examples: a new rule for plate names, or a change to the specification. Open an issue first. GOVERNANCE.md lists what can never change: zones, issued numbers, blocks, the spot grid and the check-letter method. Anything that would alter an issued address belongs in a new, separate system.

## Tests to run

```sh
(cd engine/reference && python3 sn_engine.py selftest && python3 -m unittest test_sn)
python3 -m unittest server.test_server
```

If you change the engine's output, refresh the vectors with `python3 sn_engine.py vectors --write` and explain every changed vector in the pull request.

## The issuer rule

Pull requests never issue addresses. Addresses are issued by one issuer only: N-WAYS LIMITED, or the deployment the State designates. A second issuer working from the same registry would give the same number to two compounds. New addresses reach this repository only through the issuer's export into `registry/`, with its manifests. A pull request that edits `registry/` by hand is declined.

## Licences

By contributing you agree that your contribution is licensed as the part of the repository it changes: Apache 2.0 for code, ODbL 1.0 for data, CC BY 4.0 for documents (LICENSING.md).

## Contact

hello@nways.ng. To report a security or privacy problem, see SECURITY.md.
