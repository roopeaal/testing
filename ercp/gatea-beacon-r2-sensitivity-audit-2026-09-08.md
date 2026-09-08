# ERCP Gate-A Beacon R2 — sensitivity audit

Date: 2026-09-08  
Status: **COMPUTATIONALLY VERIFIED DIAGNOSTIC / DOES NOT MODIFY R2**

R2's confirmatory endpoint remains the frozen exact QRM28 randomization test. This addendum asks only whether its sample size is in the right order of magnitude for the coupling strength that would matter to the final Eurojackpot goal under the same explicit IID BSC-like toy model used in earlier diagnostics.

## Exact discrete discovery threshold

R2 has `M=2^28=268,435,456` possible 28-bit future messages and uses

`p_exact = tail_count_ge / 2^28`.

The frozen one-sided five-sigma threshold is `2.86651571879193e-07`.

Therefore a strong candidate requires

`tail_count_ge <= 76`

out of `268,435,456` messages.

The minimum corresponding exact percentile is approximately `99.99997169%`.

## IID BSC-like sensitivity approximation

If each of the `N=2^18=262,144` receiver bits independently agrees with the future target codeword with

`p = 1/2 + delta`,

then the target hard-correlation score has approximately

`E[Z] = 2 delta sqrt(N)`.

So:

- expected 5-sigma mean requires `delta ~= 0.004882812`, i.e. `p ~= 0.504882812`;
- one-sided 5-sigma with 90% approximate power requires `delta ~= 0.006134328`, i.e. `p ~= 0.506134328`.

Earlier final-goal information accounting gave a 99% full-Eurojackpot-row reference of approximately

`p ~= 0.505942124`

under this same toy BSC model. At R2's N this implies mean

`Z ~= 6.0847`

and approximate 5-sigma power of **86.10%**.

Hence R2 is not arbitrarily underpowered relative to the *final-goal-strength* coupling scale in this explicit model: its 5-sigma/90%-power threshold (`p≈0.506134`) is close to the earlier 99%-row reference (`p≈0.505942`).

This does **not** mean R2 can recover a Eurojackpot row, and it does not turn a null into a general no-go theorem. It means the prospective public-beacon screen is operating at a scientifically relevant effect-size scale rather than merely searching for infinitesimal correlations.

## Important limitation

The actual confirmatory R2 p-value is **not Gaussian** and does not assume IID receiver bits. It is computed exactly over the entire frozen QRM28 message family conditional on the realized earlier NIST receiver.

These BSC/Gaussian calculations are therefore diagnostic power planning only and cannot replace the frozen exact randomization result.

## Artifact hashes

- report SHA256: `81b9307fe86d5cb1f2bf6ca9d09129040775bcc22222f9afda8b9718e6d9bd53`
- machine-readable JSON SHA256: `c0b34b8bcbffe74142b7f45547509ed02515195535bfdf1cd261b20ed79def95`
