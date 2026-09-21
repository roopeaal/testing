# ERCP R4 Trial2 — pre-source primary-run adjudication

Status: **PRESOURCE / OUTCOME-BLIND**

This note is committed before target quicknet round **32397413** (2026-09-21T13:00:03Z) and assignment round **32397613** (2026-09-21T13:10:03Z). Neither future source exists at the time of this adjudication.

## Why this note exists

GitHub Actions indexing was delayed after a workflow-format correction. While a parse-safe replacement workflow was being prepared, the earlier corrected workflow also started and successfully froze a separate receiver. This unintentionally created two prospective run instances against the same future target/assignment pair.

To prevent outcome-dependent selection or hidden multiple testing, the confirmatory status is fixed now, before either future source.

## Frozen adjudication

- **SOLE CONFIRMATORY PRIMARY RUN:** GitHub Actions run **35585381162**
  - trigger SHA: `32d70cd3892682edaaa57c5d82a2279c79aff547`
  - pre-source Git receiver commit: `5e562a857714047f95431cb8fc39b8e6fd1904c0`
  - receiver SHA-256: `bf46cdc4aec6746e2811a4efe5db77139c787047272689a9fe89d4404f06b2df`
  - pre-source Actions artifact digest: `sha256:5ab952f9ebd884dfa44dbf03cb3f3199e925f0313385c6e0bbf5191df23ec833`
  - rationale: this is the explicitly parse-safe, fail-closed orchestration run launched after the workflow-indexing ambiguity was identified.

- **SUPERSEDED / DIAGNOSTIC-ONLY RUN:** GitHub Actions run **35585150007**
  - trigger SHA: `acfac26603151ba8726a2d251e677c96e8f83438`
  - pre-source Git receiver commit: `3afdf00d975cf2fd1a645da4f7cceaa6b972475f`
  - its future result, whether null or anomalous, is **not** an additional confirmatory discovery opportunity and cannot replace the primary run.

## Statistical rule

Only run 35585381162 may be evaluated against the preregistered one-sided 5-sigma threshold as the confirmatory R4 Trial2 primary test. Run 35585150007 may be inspected only as a labeled diagnostic/technical replication and cannot be used to claim discovery if the primary run is null.

This designation is irreversible after either future source exists. No best-of-two selection is permitted.
