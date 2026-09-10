# ERCP Gate-A Beacon R2 — final postmortem

Status: **VALID PROSPECTIVE NULL**

## Confirmatory result

The frozen prospective protocol completed all integrity gates. The pre-source NIST receiver was 262,144 bits with SHA-256 `9a675b1a1a20f861d75cb1bfa9e43c78b88aa9b7bb29f4661924432781c78fd1`. The pinned future source was drand quicknet round 32,032,013. Four relays agreed exactly, `SHA256(signature)=randomness`, and the signature passed BLS `VerifyBeacon` with drand v2.1.7.

Frozen QRM28 result:

- future 28-bit message: `91609351`
- observed score: `234`
- exact null SD: `512.0`
- standardized score: `0.45703125`
- exact one-sided randomization p: **0.325229920447**
- hard agreement: `131189/262144 = 0.500446320`
- 5-sigma threshold: `2.86651571879193e-07`
- strong candidate: **false**

Interpretation: **NO_GATE_A_PUBLIC_BEACON_PAST_ANOMALY_IN_R2**.

## Empirical/model-specific upper bound

As a diagnostic only, under the same IID BSC-like coupling model used for earlier capacity planning, a one-sided 95% Clopper-Pearson upper bound is

`p_agree < 0.502054519`

so `delta=p-0.5 < 0.002054519`. This corresponds to at most approximately **3.193 bits** over N=262,144 coordinates in that toy channel model. The earlier 99%-Eurojackpot-strength reference was `p≈0.505942124`, which lies above this bound. Thus R2 excludes that homogeneous coupling strength for this receiver/model at 95% confidence. This does not constitute a general no-retrocausality theorem.

## Research consequence

Repeating another static public-beacon source-only receiver is now low expected value. The next useful test must add a genuine later randomized physical intervention and preferably a physically continuous/local substrate, while keeping the earlier receiver externally frozen before the intervention source exists.
