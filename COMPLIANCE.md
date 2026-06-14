# COMPLIANCE.md — how Sentinel maps to existing AI / data law

> ⚠️ **Indicative engineering mapping — not legal advice or a conformity assessment.**
> Coverage describes what Sentinel *provides*, not whether *you* are compliant. Verify
> against the current legal texts. `sentinel compliance` is the machine-readable source
> of truth; this file mirrors it.
>
> Legend: **full** = Sentinel provides the control · **partial** = Sentinel provides
> evidence/infrastructure, you do the rest · **none** = out of scope (listed honestly).

## Coverage at a glance

| Framework | Jurisdiction | full | partial | none |
|---|---|:--:|:--:|:--:|
| EU AI Act (2024/1689) | EU | 1 | 4 | 2 |
| GDPR (2016/679) | EU/EEA | 0 | 4 | 1 |
| NIST AI RMF 1.0 | US (voluntary) | 0 | 3 | 1 |
| ISO/IEC 42001:2023 | International | 0 | 3 | 1 |
| Colorado AI Act (SB 24-205) | US — Colorado | 0 | 3 | 1 |
| SEC 17a-4 / FINRA 4511 | US — securities | 0 | 3 | 0 |

Sentinel is an **evidence + control-plane** layer: it makes the *logging, oversight,
and audit* obligations satisfiable. It does **not** do risk classification, conformity
assessment, DPIAs, user-facing disclosure, or your organisational processes.

## EU AI Act (Regulation 2024/1689)

| Article | Requirement (paraphrased) | Coverage | How |
|---|---|---|---|
| Art. 12 | Automatic event logs over the system lifetime | **full** | Append-only hash-chained audit; `export --format art12` |
| Art. 14 | Human oversight / stop button | partial | Kill switch + approvals; you design the oversight process |
| Art. 19 / 26(6) | Retain logs (deployers ≥ 6 months) | partial | Durable + tamper-evident; you set retention/backup |
| Art. 26 | Deployer monitoring, logs, oversight | partial | Action feed + audit + kill/approvals |
| Art. 72 | Post-market monitoring | partial | Audit + detector flags are the raw data |
| Art. 50 | Transparency to users / content marking | none | Sentinel governs actions, not disclosure |
| Art. 9 / Annex IV | Risk-management system & technical docs | none | Organisational process |

## GDPR (2016/679)

| Article | Requirement | Coverage | How |
|---|---|---|---|
| Art. 5(1)(c) | Data minimisation | partial | Secret/PII redaction before logging; PII detector |
| Art. 22 | Human intervention in automated decisions | partial | Approvals + kill provide the checkpoint |
| Art. 30 | Records of processing | partial | Per-action audit trail |
| Art. 32 | Security of processing | partial | Token-gated plane + tamper-evident logs |
| Art. 17 | Right to erasure | none | Audit is append-only — keep PII out (redaction); erase in source systems |

## NIST AI RMF 1.0 (+ GenAI profile)

| Function | Coverage | How |
|---|---|---|
| GOVERN | partial | Default-deny policy + immutable audit |
| MAP | none | Analytical/process activity |
| MEASURE | partial | Detector flags + action feed = continuous monitoring |
| MANAGE | partial | Kill switch + forensic audit for response/recovery |

## ISO/IEC 42001:2023

| Control theme | Coverage | How |
|---|---|---|
| Operational controls & monitoring | partial | Runtime enforcement + live monitoring + audit |
| Event logging & records | partial | Tamper-evident audit; auditor export |
| Incident management | partial | Detector + kill + audit |
| Management-system processes (Cl. 4-10) | none | Organisational AIMS |

## Colorado AI Act (SB 24-205, eff. 2026-06-30)

| Obligation | Coverage | How |
|---|---|---|
| Risk-management program | partial | Policy + audit are core evidence |
| Recordkeeping | partial | Per-action audit trail |
| AG notice of algorithmic discrimination (≤90 days) | partial | Detector + audit help detect/evidence; notice is yours |
| Consumer notice / right to contest | none | User-facing process |

## SEC Rule 17a-4 / FINRA Rule 4511 (broker-dealer recordkeeping — for trading agents)

| Obligation | Coverage | How |
|---|---|---|
| Non-rewriteable records / audit-trail alternative | partial | Hash-chained tamper-evident audit; true WORM needs object-lock storage (roadmap) |
| Retention periods | partial | Durable store; configure long-term archival |
| Supervision of automated trading | partial | Action feed + kill + approvals |

## Generate live, evidence-backed reports

```bash
sentinel compliance --all                       # coverage summary (all frameworks)
sentinel compliance --framework eu_ai_act       # full mapping + your audit evidence
sentinel export --format art12                   # EU AI Act Art. 12 record-keeping report
```
Set `SENTINEL_SYSTEM_NAME` and `SENTINEL_PROVIDER` to stamp reports with your system identity.
