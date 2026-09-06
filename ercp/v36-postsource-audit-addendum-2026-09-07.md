# ERCP V36 post-source audit addendum — 2026-09-07

This document is a **post-source audit addendum**. It does not modify any pre-source V36 artifact, receiver, decoder, route, statistic, target, source round, actuator, success criterion, or public commitment. It cannot retroactively change the frozen V36 validity classification.

## 1. Independent cryptographic closure of the preserved drand source

Preserved V36 source:

- network: drand quicknet
- chain hash: `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971`
- round: `31916813`
- scheme: `bls-unchained-g1-rfc9380`
- quicknet public key: `83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a`
- preserved signature: `a1a0b13d0cef00331ef721970839ae379a7a7d5bb591e1914b5e63b866286a60cc3c2a4aeed6c062936eabf1f14d5509`
- preserved randomness: `d9f14c3ab77fd0290e1e499864b305556a4d5b031cc7515a2eb0514871a64158`

A new reproducible GitHub Actions audit was added in `.github/workflows/v36-bls-verify.yml`. The successful audit used Go 1.26.4 and **drand v2.1.7** itself. It instantiated `crypto.NewPedersenBLSUnchainedG1()`, decoded the preserved group public key, recomputed randomness with drand's `RandomnessFromSignature`, and called `Scheme.VerifyBeacon` on the preserved round/signature.

Successful audit:

- workflow run: `34060420877`
- workflow commit: `9ed36a0da64a2b326875773882ac7293516ba27f`
- `PUBLIC_KEY_DECODE=true`
- `SIGNATURE_TO_RANDOMNESS_SHA256=true`
- recomputed randomness: `d9f14c3ab77fd0290e1e499864b305556a4d5b031cc7515a2eb0514871a64158`
- `BLS_VERIFIED=true`
- verified round: `31916813`
- verified scheme: `bls-unchained-g1-rfc9380`
- drand implementation: `v2.1.7`

Therefore the preserved V36 future randomness source is now **cryptographically verified in a post-source independent audit**.

### Important validity boundary

This does **not** make the frozen V36 physical trial valid. The pre-source hardened evaluation contract was fail-closed and the preserved source/transcript schema did not satisfy that frozen contract (`public_key` was absent from the preserved source object and relay records used a different field shape). Those frozen validity gates may not be repaired retrospectively. V36 therefore remains:

`INVALID / INCONCLUSIVE`

as a confirmatory physical future-to-past trial.

## 2. Frozen V36 diagnostic outcome

Official 2026-09-04 Eurojackpot row rank:

`55,240,899`

Frozen primary algebra after the future mask:

- corrected payload: `241,260,050` — not the official row rank;
- corrected calibration: `137,485,741` — not zero;
- joint primary pass: `false`.

Pre-source Gate-A soft-statistic addendum, evaluated after the source:

- calibration exact randomization p: `0.2806280180811882`;
- payload exact randomization p: `0.5239644423127174`;
- two-soft-channel Bonferroni family p: `0.5612560361623764`;
- strong Gate-A candidate: `false`.

Hard robustness diagnostics:

- calibration agreement: `131143 / 262144 = 0.5002708435058594`;
- payload agreement: `131118 / 262144 = 0.5001754760742188`.

These values show no diagnostic anomaly.

## 3. Post-hoc model-specific effect upper bound

The following is **not** a replacement confirmatory test. It is a quantitative diagnostic bound under an additional explicit toy model that was not needed by the exact Gate-A randomization null.

Assume independently across the `N=262144` positions that the earlier hard receiver bit agrees with the later routed target bit with probability `p >= 1/2`. Under this IID Bernoulli/BSC-like coupling model, a one-sided 95% Clopper–Pearson upper confidence limit gives:

| channel | observed agreement | 95% upper `p` | upper `p-1/2` |
|---|---:|---:|---:|
| calibration | 0.5002708435 | 0.5018790451 | 0.0018790451 |
| payload | 0.5001754761 | 0.5017836786 | 0.0017836786 |

Using the earlier ERCP BSC parameterization

`p = 1 / (1 + exp(-2*kappa))`,

the same one-sided 95% limits are approximately:

- calibration: `kappa <= 0.00375811`;
- payload: `kappa <= 0.00356737`.

For a symmetric binary channel, `C = 1 - h2(1-p)`. Multiplying by `N=262144`, these 95% limits correspond to model-specific information ceilings of approximately:

- calibration: `N*C <= 2.671 bits`;
- payload: `N*C <= 2.406 bits`.

For comparison, the theory-independent ERCP 99%-recovery Fano requirement for the complete Eurojackpot row is `26.7077979 bits`. With `N=262144` independent BSC-like positions, merely reaching that information floor requires approximately

- `p >= 0.505942124`,
- `kappa >= 0.011884807`.

Thus, **within this explicit IID BSC-like coupling model**, the V36 payload hard-agreement data are far below the coupling scale needed for 99% full-row recovery. This is only a model-specific diagnostic statement because the V36 confirmatory physical trial itself remains invalid/inconclusive and the exact Gate-A test intentionally did not assume IID noise.

## 4. Research decision

- Frozen V36 confirmatory physical trial: **INVALID / INCONCLUSIVE**.
- Preserved future drand source authenticity: **cryptographically verified post-source**.
- Frozen primary equality diagnostics: **no anomaly**.
- Pre-source Gate-A exact randomization diagnostics: **no anomaly**.
- Simple IID BSC-like coupling large enough for the final 99% Eurojackpot objective: **not supported by V36 diagnostic data; model-specific upper bound is far below the required scale**.

The next project-level priority should not be another coding optimization. The high-value path is either:

1. a new prospective Gate-A existence/controllability replication whose source schema, external BLS verification, transcript binding and execution validity are all exercised end-to-end **before** the future source exists; or
2. the already designed negative-lag RF hardware experiment, which remains blocked by actual high-resolution physical hardware.
