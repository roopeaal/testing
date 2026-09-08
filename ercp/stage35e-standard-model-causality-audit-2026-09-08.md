# ERCP Stage 35E — standard-model causality and analysis-leakage audit

Date: 2026-09-08  
Status: **THEORETICAL / COMPUTATIONALLY VERIFIED ADDENDUM**  
Advanced / negative-lag response: **NOT OBSERVED**

## 1. Why this audit matters

The Stage 35E hardware branch asks whether a load choice formed at the far end at `t_sw` can correlate with a source-side record near `t_sw - tau_cal`. Before spending effort on hardware, the ordinary transmission-line prediction must be stated in a way that cannot be confused with the mere mathematical existence of advanced Green functions.

The key result is stronger than “we expect causality”: for the ordinary transmission-line initial-boundary-value problem, the far-end boundary choice is outside the source event's domain of dependence until the left-going characteristic has had time to propagate back to the source.

## 2. Lossless telegrapher-equation theorem

For a lossless line,

`∂V/∂x = -L' ∂I/∂t`,  
`∂I/∂x = -C' ∂V/∂t`,

with

`u = 1/sqrt(L'C')`, `Z0 = sqrt(L'/C')`.

Define the Riemann invariants

`a = V + Z0 I`,  
`b = V - Z0 I`.

Direct substitution gives

`(∂t + u ∂x) a = 0`,  
`(∂t - u ∂x) b = 0`.

Thus `a` propagates toward increasing `x` and `b` toward decreasing `x`, with finite speed `u`.

Let the load be at `x=L`, the source at `x=0`, and `tau=L/u`. A load-boundary change at physical time `t_sw` can modify the left-going invariant only on characteristics emerging from `(L,t_sw)`. The earliest such characteristic reaches the source at

` t = t_sw + tau `.

Therefore, within ordinary local transmission-line dynamics:

**the source waveform for every `t < t_sw + tau` is independent of a load choice first formed at `t_sw`.**

This is a domain-of-dependence statement, not a statistical expectation.

## 3. Explicit reflection formula

Write the voltage as

`V(x,t)=F(t-x/u)+G(t+x/u)`

and current as

`I(x,t)=[F(t-x/u)-G(t+x/u)]/Z0`.

For a memoryless time-varying load with instantaneous reflection coefficient `Gamma_L(t)`, the reflected wave at the boundary is

`G_L(t)=Gamma_L(t) F_L(t)`.

Propagation back to the source gives

`G_source(t) = Gamma_L(t-tau) F(t-2tau)`.

Hence a change in `Gamma_L` at `t_sw` first changes the source at **`t_sw+tau`**. Stage 35E's hypothetical advanced center is **`t_sw-tau`**. The two centers are separated by exactly **`2 tau`**.

A mismatched source can create later re-reflections, but it cannot make the first load-dependent influence arrive earlier than this characteristic.

## 4. Advanced Maxwell solutions do not imply operational future-to-past signalling

Maxwell/wave equations are time-reversal symmetric and admit both retarded and advanced Green-function representations. That fact alone does **not** make an independently chosen future load boundary influence an already-fixed past source record.

The ordinary causal initial-value problem uses retarded propagation. An advanced solution corresponds to a different boundary-value prescription, effectively supplying final/future boundary information.

Zhao's 2023 proposal explicitly assumes absorber theory / an advanced potential before deriving the earlier source response. Therefore its `-tau` prediction is **conditional on an additional advanced/final-boundary physical law**, rather than a consequence forced by standard Maxwell initial-value dynamics.

Stage 35E interpretation is therefore:

- a normal `+tau` response validates the apparatus and ordinary transmission-line model;
- a null at `-tau` is the standard-model expectation;
- a robust `-tau` response would challenge the causal initial-boundary-value model only after leakage/artifact controls survive.

## 5. Noncausal filtering can fake the target

Suppose the true ordinary load-dependent source signal begins at `t_sw+tau`.

For a preprocessing kernel `h(t)` that is causal (`h(t)=0` for `t<0`), convolution cannot create output before the physical first arrival.

But a symmetric/zero-phase kernel has negative-time support. Stage 35E's primary window is

`[t_sw-1.2tau, t_sw-0.8tau]`.

Therefore:

- negative filter support of **`1.8 tau`** is enough for the ordinary `+tau` response to leak into the latest edge of the advanced window;
- support of **`2 tau`** reaches the nominal advanced center.

For a simple symmetric Gaussian smoothing of a unit step, the false value at the advanced center is

`Phi(-2 tau / sigma)`.

A Gaussian width of only

`sigma ≈ 0.86 tau`

already creates a **1% apparent advanced fraction** at `-tau`, which is the same order as the Stage 35E initial falsification target.

Planning examples using 5.05274 ns/m:

| L | tau | 1.8 tau | 2 tau | Gaussian sigma giving 1% false center response |
|---:|---:|---:|---:|---:|
| 50 m | 252.6 ns | 454.7 ns | 505.3 ns | 217.2 ns |
| 100 m | 505.3 ns | 909.5 ns | 1.011 us | 434.4 ns |
| 150 m | 757.9 ns | 1.364 us | 1.516 us | 651.6 ns |
| 165.46 m | 836.0 ns | 1.505 us | 1.672 us | 718.7 ns |
| 200 m | 1.011 us | 1.819 us | 2.021 us | 868.8 ns |

So the existing ban on `filtfilt`, zero-phase filters and label-dependent denoising is mathematically necessary to prevent an ordinary post-switch signal from being smeared into the exact discovery region.

## 6. Trigger-shift artifact

If the trigger/alignment marker has a treatment-dependent timing shift `delta t`, then for a baseline waveform `V(t)` the aligned difference contains approximately

`delta V(t) ≈ - delta t * dV/dt`.

The artifact can appear anywhere the baseline has slope or ringing, including an earlier analysis window. This makes the bit-independent timing marker, fixed alignment procedure and `t≈0` sentinel mandatory.

Length-law testing remains decisive: fixed trigger/EMI artifacts remain approximately clock-relative, ordinary load response moves as `+tau_cal`, while the hypothesized advanced candidate must move as `-tau_cal`.

## 7. Confirmatory fail-closed rules

1. raw pretrigger ADC samples are authoritative;
2. primary analysis uses raw data or only explicitly causal preprocessing with frozen finite impulse support;
3. no symmetric/zero-phase/filtfilt operation anywhere in the discovery path;
4. same calibration-derived template and preprocessing at `-tau` and `+tau`;
5. trigger marker must be bit-independent;
6. direct pickup around `t=0` is diagnostic only;
7. length-law behavior distinguishes propagation from fixed-time pickup;
8. any candidate must survive sham and load-mapping reversal.

## 8. Epistemic state

- finite-speed retarded load→source domain of dependence: **PROVEN within the standard lossless telegrapher model**;
- same qualitative front-causality for ordinary passive causal line models: **standard causal systems consequence**;
- `1.8 tau` / `2 tau` analysis-leakage thresholds and Gaussian 1% examples: **COMPUTATIONALLY VERIFIED**;
- Zhao `-tau` prediction from ordinary Maxwell initial-value dynamics: **NOT DERIVED**; it is **CONDITIONAL** on an advanced/final-boundary assumption;
- physical advanced response: **NOT OBSERVED**.

This does not falsify all conceivable absorber/final-boundary physics. It shows that a Stage 35E negative-lag candidate cannot be explained merely by saying that Maxwell's equations also possess advanced mathematical solutions.

## Preserved artifact hashes

- report SHA256: `7e90a8cd430401d46fb9169f6e82abb3c2751107f9839336e2a2212438375950`
- calculation script SHA256: `67b479e76abbdc41ce7a973391e7156dcaae33dc5de1b0cc134e1ec79d67e818`
- machine-readable output SHA256: `86ef3d4da4a2a173892453bfc7411d9792fc2ecae1fd48f9fca07e76d28221b9`

## References inspected

- Standard telegrapher-equation / TDR sources (Tektronix and university notes).
- Maxwell retarded/advanced Green-function notes (MIT OCW / UT Austin).
- Shuang-ren Zhao, 2023, proposed advanced-wave transmission-line experiment.
