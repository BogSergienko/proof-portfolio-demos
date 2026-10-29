# Example 2 — checks on a synthetic AI action log

A toy assistant refers to documents and attempts actions; our offline checker examines reference availability, a locally supplied checksum, version, field-value match and STOP status.

Run `python proof_check.py`. Expected demo fixtures: **7 checks**, 2 `VERIFIED`, 5 flagged/blocked. HTML overview: `PREVIEW.html`.

This is a compact demonstration of *auditable assertions*, not a real LLM evaluation, not a trusted signature scheme, not a permission enforcement system. The source can easily be altered together with its local checksum; no claim about real authenticity is justified.
