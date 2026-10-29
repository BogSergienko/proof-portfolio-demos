# Proof Portfolio — two tiny, runnable automation case studies

**Work you can see, run, and check.** Two *synthetic*, self-contained Python examples using only the standard library. No external API, live customer data, personal messages or internal research code.

**[Open the visual portfolio](docs/index.html)** (can also be served through GitHub Pages by selecting `/docs` on the `main` branch).

| Case | Problem | Reproducible result | Start |
|---|---|---|---|
| [CSV order clean-up](cases/orders/) | Two inconsistent exports | 138 synthetic rows → 111 validated + 27 flagged; summary generated | `python cases/orders/process_orders.py` |
| [Evidence audit](cases/evidence-audit/) | A synthetic agent invents numbers, cites stale sources and acts after STOP | 7 fixtures: 2 verified, 5 flagged | `python cases/evidence-audit/proof_check.py` |

### Quick test

Requires **Python 3.10+**. No `pip install` needed.

```bash
python -m unittest discover -s tests -v
```

The tests check exact expected outputs, re-run the source data generator, introduce a deliberate error and verify it is flagged. Running a script writes generated reports **only in its own demo directory**. Neither demo sends anything over the network.

### Who may find this useful?

- Small businesses: *Could you combine exports without silently hiding bad rows?*
- Automation teams: *Can your code produce auditable, repeatable results?*
- AI product teams: *Can claims be checked against referenced versions, and can STOP violations be detected in a recorded log?*

These are **examples of problem-solving**, not commercial integrations or proof of a deployed system. The original code is intentionally small and educational.

### Honest limits

- All input orders, prices, IDs, and agent events are **fictional**.
- The order rules are illustrative, **not accounting or tax advice**. A real importer needs customer-specific validation and acceptance tests.
- Evidence integrity in the sample uses hashes in the same data bundle; this is **not proof of independent authenticity**.
- STOP is an **offline audit of recorded actions**; it does **not enforce permissions**.
- `7/7 PASS` means seven fixed test expectations were reproduced, **not** that seven independent security properties or live LLM errors were solved.
- No revenue, performance gains, paid customers, or model reliability improvements are claimed.

### Reuse and contact

This is a demonstration portfolio. **No reuse license is granted yet**; ask the owner before redistribution or derivative commercial use. No passwords, account access, or private materials are needed to review it. If you need a similar tool, define a specific task and acceptance criteria first.

[Technical evidence and reproduction notes](EVIDENCE.md) · [Russian short description](PITCH_RU.md) · [Publication notes](PUBLICATION.md)
