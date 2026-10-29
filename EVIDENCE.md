# Reproduction & evidence boundaries

Test command: `python -m unittest discover -s tests -v` (Python 3.10+; standard library only). The GitHub Actions workflow repeats the tests on Ubuntu and Windows with Python 3.11 and 3.13 after publication.

## What is actually measured

- **Order demo:** expected CSV/JSON output hashes; row conservation 138 = 111 + 27; deterministic input regeneration; test that an introduced invalid amount is flagged.
- **Evidence demo:** seven expected classifications, plus new negative controls for tampered values, missing evidence and STOP attempts.

Neither demo measures production speed, business earnings, real LLM correctness, source authenticity, nor actual policy enforcement. Synthetic examples are insufficient to claim that deploying this code makes a system secure. CI results, if triggered on GitHub, independently reproduce script execution in a fresh runner but do not validate business assumptions.

The source package was locally verified before publication. `SHA256SUMS.txt` records file hashes. Do not edit a source file without regenerating hashes and rerunning tests.
