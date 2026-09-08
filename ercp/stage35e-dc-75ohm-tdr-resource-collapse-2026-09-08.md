# ERCP Stage 35E — DC / 75 Ω TDR resource-collapse design

Date: 2026-09-08  
Status: **PROSPECTIVE DESIGN / BLOCKED_BY_RESOURCE**  
Advanced / negative-lag response: **NOT OBSERVED**

## 1. Project-level advance

Stage 35D still assumed a conventional RF-style source/bridge and a dedicated RF load switch. That is not necessary for the first high-information falsification.

A simpler orthogonal receiver can be built as a **DC-biased 75 Ω TDR-like transmission-line experiment**:

- ordinary consumer RG6 coax instead of 50 Ω laboratory RF cable;
- battery + two resistors as a near-75 Ω Thevenin source instead of a signal generator;
- the oscilloscope samples the source node directly in high-Z mode instead of requiring a directional bridge;
- a permanent 75 Ω far-end termination defines the matched state;
- a cheap MOSFET shunts the far end toward a short for the second load state;
- a D flip-flop forms the treatment label only at `t = 0` and immediately commands the MOSFET.

This is **not a new TDR theorem**. It is a project-new combination of standard reflection physics with the late-choice negative-lag falsification topology.

Standard TDR theory gives

`rho = (Z_L - Z_0) / (Z_L + Z_0)`,

so a matched load has `rho=0`, a short `rho=-1`, and an open `rho=+1`. The experiment therefore does not conceptually require 50 Ω hardware; it requires the source, cable and reference load to be calibrated to the same characteristic impedance.

## 2. Minimal circuit

```text
SOURCE END                                              FAR END
                                                   +----------------- 75 Ω ---- shield
+3 V battery                                          |
   |                                                  +---- drain 2N7000
 1.1 kΩ                                              |       source ---- shield
   |                                                  |       gate <---- Q
   +---- SOURCE NODE ================= RG6 75 Ω ======+
   |         |
  82 Ω       +---- scope CH1 high-Z
   |
 shield/GND

Far-end treatment logic:
local analog noise -> comparator/logic D -> 74HC74 D flip-flop
                                      CLK <- bit-independent t=0 edge
                                      Q   -> MOSFET gate
```

`/PRE` and `/CLR` are held inactive. A gate pulldown is used so the MOSFET has a defined state before the latch event.

The bit-independent timing edge must be observable by the acquisition system without carrying the treatment value. For a low-cost pilot, a separately calibrated timing path is acceptable. A confirmatory run should prefer optical isolation or another topology that removes a conductive ground/EMI bypass.

## 3. Source and load planning calculation

With a 3.0 V source, `Rtop=1.1 kΩ`, `Rbot=82 Ω`:

- Thevenin voltage = **0.208122 V**
- Thevenin resistance = **76.311 Ω**
- source reflection coefficient relative to 75 Ω = **0.00867**
- matched-line source node ≈ **103.16 mV**

Using `Rds(on)=5.3 Ω` as a conservative 2N7000 planning value:

- switched far-end load `75 Ω || 5.3 Ω` = **4.950 Ω**
- corresponding load reflection coefficient = **-0.8762**

So the ordinary positive-lag load transition should be large. The amplitudes below use Belden 8215's **1 MHz insertion loss only as a proxy** for round-trip step loss; they are not a substitute for measuring the actual assembled cable step response.

## 4. Timing and sensitivity table

The planning cable proxy is Belden 8215 RG-6A/U: 75 Ω, nominal delay 5.05274 ns/m and 1.3124 dB/100 m attenuation at 1 MHz. The treatment-chain planning budget is deliberately conservative at `t_sw,max = 60 ns`.

Primary window:
`[t_sw - 1.2 tau, t_sw - 0.8 tau]`.

| L (m) | tau (ns) | primary center (ns) | primary end (ns) | guard to t=0 (ns) | samples/tau @48 MS/s | samples in 0.4tau | round-trip loss proxy (dB) | ordinary source step proxy (mV) | J/Jmax |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 252.6 | -192.6 | -142.1 | 142.1 | 12.1 | 4.9 | 1.3124 | -78.4 | 0.607 |
| 100 | 505.3 | -445.3 | -344.2 | 344.2 | 24.3 | 9.7 | 2.6248 | -67.4 | 0.898 |
| 150 | 757.9 | -697.9 | -546.3 | 546.3 | 36.4 | 14.6 | 3.9372 | -57.9 | 0.995 |
| 200 | 1010.5 | -950.5 | -748.4 | 748.4 | 48.5 | 19.4 | 5.2496 | -49.8 | 0.981 |

Even 50 m passes the nominal timing guard, but its primary window contains only about five 48-MS/s samples. 100 m is already much cleaner; 150–200 m gives substantially more temporal resolution while retaining a large ordinary reflection.

## 5. New length optimum

For a deliberately simple model:

- primary matched-filter window width scales as `0.4 tau ∝ L`;
- per-sample receiver noise is approximately white and length-independent;
- returned voltage is reduced by cable attenuation.

Then a sensitivity proxy is

`J(L) ∝ L * A(L)^2`.

With the Belden 1 MHz loss proxy `a = 0.013124 dB/m`,

`A(L)=10^(-a L / 10)`

for the round-trip voltage factor, so

`J(L)=L * 10^(-2 a L / 10)`.

Its analytic maximum is

`L* = 10 / (2 a ln 10) = 165.46 m`.

Under this explicit toy model:

- 50 m: 0.607 of optimum
- 100 m: 0.898
- 150 m: 0.995
- 200 m: 0.981
- 300 m: 0.804
- 400 m: 0.586

**Scientific consequence:** the former 100 m choice is not obviously sensitivity-optimal. A 150–200 m line is the better confirmatory planning region if actual measured loss/noise resembles this model.

This is **COMPUTATIONALLY VERIFIED only within the stated model**. Cheap CCS RG6 can have materially different DC resistance/loss, connectors add discontinuities, the scope noise is colored, and the switched edge has finite spectrum. Therefore the cable length must not be frozen from this calculation alone.

## 6. Resource-minimal acquisition

The Hantek 6022BE manual specifies:

- 48 MS/s real-time sampling;
- two channels;
- 20 MHz bandwidth;
- 8-bit vertical resolution;
- DC coupling;
- up to 1 M samples;
- Single trigger mode;
- acquisition of data to the left of the trigger point.

That is enough **on paper** for the 100–200 m timing geometry. Scientific adequacy is still decided only by an assembled-hardware qualification run.

A currently listed Finnish 100 m Harju RG6T-CCS spool was 55.90 € at the time of this audit. This is evidence that the cable-length barrier is inexpensive, not a recommendation to assume its electrical parameters equal the Belden planning proxy.

## 7. Hardware qualification gate — must happen before randomized data

No confirmatory randomized run is allowed until all of these pass:

1. **Raw pretrigger export:** verify the scope can repeatedly save raw CH1 samples before the timing marker.
2. **Deterministic load calibration:** force matched and shunt states and measure the source-side ordinary response.
3. **Measure `tau_cal`:** derive the actual propagation timing from the assembled line; never use nominal velocity for the scientific endpoint.
4. **Measure `t_sw`:** record the distribution from the latch clock to the actual far-end electrical load transition.
5. **Causal guard:** prove that the complete frozen negative window ends before treatment-label formation after uncertainties and jitter.
6. **Freeze template/statistic:** build the positive-lag waveform template only from calibration data, then freeze the same projection for `-tau_cal`.
7. **Measure `d_plus`:** if the ordinary positive control is weak, improve the hardware rather than collecting millions of trials.
8. **Sham:** keep latch/clock activity identical while disconnecting Q from the load.
9. **RNG predictability audit:** preregister a predictor and test whether the eventual latched bit is predictable from any state available during the primary past window.
10. **No noncausal processing:** no `filtfilt`, zero-phase filter, label-dependent denoising, post-hoc window movement, or waveform-based trial deletion.
11. **Mapping swap:** invert logical bit -> physical load mapping.
12. **Length law:** a candidate must move with approximately `-tau_cal`; the ordinary response must move with `+tau_cal`; fixed EMI should stay clock-relative.

## 8. Trial-count gate

Keep the earlier planning rule

`n_per_state ~= 78.91578014 / (eta * d_plus)^2`

for one-sided 5-sigma / 90% power planning only.

The initial falsification target remains `eta = 1%` of the apparatus's own measured ordinary positive-lag response. The final significance comes from the frozen randomization/permutation test, not this Gaussian planning approximation.

## 9. Recommended build sequence

**Engineering pilot:** start with one uninterrupted 100 m cable. It is cheaper and mechanically simpler, and it is enough to validate the DC source, MOSFET load, pretrigger capture, `tau_cal`, `t_sw`, raw export and ordinary `+tau` response.

**Sensitivity/confirmatory length:** after measuring the pilot's actual delay, attenuation, noise and edge shape, rerun the frozen length-selection calculation using those calibration-only quantities. If the measured system resembles the planning model, select roughly **150–200 m**, not automatically 100 m.

**Independent length-law replication:** use a materially different calibrated length after any candidate. Do not call a single negative-lag association an advanced wave.

## 10. Literature audit

Zhao's 2023 paper proposes changing a load impedance and looking for a source-side change before the load change, but the paper explicitly states that the author **did not complete the proposed experimental verifications**. Searches performed for this audit did not surface an independent completed replication; the obvious later transmission-line follow-on is again Zhao's own work.

Therefore Stage 35E is motivated as a falsification of a published proposal, **not** as replication of an established anomalous observation.

## 11. Epistemic state

- Standard reflection coefficient / retarded TDR response: **PROVEN within ordinary transmission-line theory**.
- Stage 35E arithmetic and the explicit 165.46 m toy-model optimum: **COMPUTATIONALLY VERIFIED**.
- DC/75 Ω circuit: **PROSPECTIVE DESIGN**.
- Its expected positive-lag step amplitudes: **MODEL-BASED PLANNING ONLY**.
- Advanced / future-to-past response: **NOT OBSERVED**.
- Independent replication: **NONE**.
- Branch status: **BLOCKED_BY_RESOURCE**, but the required resource has collapsed to a low-cost scope, long 75 Ω cable and simple discrete electronics.

## 12. Current project decision

The highest-value physical experiment is no longer a conventional RF bench. It is a calibrated late-choice **DC / 75 Ω transmission-line** test with raw pretrigger acquisition and hard leakage controls.

The next decisive empirical question is:

> After the future treatment label is physically formed only at `t=0`, does the earlier source record contain any reproducible load-state association centered at `t_sw - tau_cal`, while sham, predictability, mapping-swap and length-law controls remain null/consistent?

A null result would set a direct apparatus-relative upper bound on negative-lag response. A positive result would be only a **candidate anomaly** until ordinary leakage, trigger artifacts, common causes and independent replication are addressed.

## Sources inspected

- Tektronix, *TDR Impedance Measurements: A Foundation for Signal Integrity*.
- Belden 8215 RG-6A/U metric technical data.
- Hantek 6022BE user manual.
- STMicroelectronics 2N7000/2N7002 datasheet.
- onsemi MC74HC74A / 74HC74 timing data.
- Shuang-ren Zhao, *Experiment to Prove the Existence of the Advanced Wave...*, International Journal of Physics 11(2), 2023.
- Current Finnish availability checks for RG6 cable and simple switching parts (Puuilo / Partco), used only for feasibility/cost context.
