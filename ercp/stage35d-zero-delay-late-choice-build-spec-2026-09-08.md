# ERCP Stage 35D — zero-delay late-choice timing closure and build specification

Date: 2026-09-08
Status: PROSPECTIVE DESIGN / BLOCKED_BY_RESOURCE

## 1. Project-level advance

Stage 35C established that a 50–100 m RG-58 transmission-line test can move the decisive negative-vs-positive lag separation into the sub-microsecond regime where low-cost USB-scope-class acquisition is adequate. This Stage 35D addendum removes an unnecessary 100 ns digital delay from the late-choice design and closes the timing budget with currently specified off-the-shelf logic/RF-switch parts.

The new topology is:

1. the future treatment bit is **latched at t = 0** from a local far-end noise source;
2. the D-flip-flop output immediately drives the load switch;
3. the physical load transition occurs after only the calibrated latch + switch latency `t_sw`;
4. the hypothesized advanced arrival is tested at the source near `t_sw - tau_cal`;
5. the ordinary Maxwell/telegrapher response is tested near `t_sw + tau_cal`.

No deliberate post-latch delay line is required.

## 2. Timing closure

Let:

- `tau_cal` = experimentally measured one-way cable delay;
- `w = 0.2 tau_cal` = preregistered half-width of the primary window;
- `t_label = 0` = far-end D-flip-flop sampling edge;
- `t_sw` = calibrated latency from the sampling edge to the actual electrical load transition.

Primary candidate window center:

`c_minus = t_sw - tau_cal`

Primary window:

`[t_sw - 1.2 tau_cal, t_sw - 0.8 tau_cal]`

Ordinary positive-control center:

`c_plus = t_sw + tau_cal`

A sufficient causal-validity condition is:

`t_sw,max < 0.8 tau_cal`

because then the entire negative-lag primary window ends before the treatment label is formed at `t = 0`.

Using Belden 8219 planning delay 4.56059 ns/m and a conservative 14 ns worst-case logic + switch budget:

| cable | nominal tau | primary window end worst-case | guard to label formation |
|---|---:|---:|---:|
| 50 m | 228.0295 ns | -168.4236 ns | 168.4236 ns |
| 100 m | 456.0590 ns | -350.8472 ns | 350.8472 ns |

Thus even the shorter 50 m line retains >168 ns of temporal separation between the end of the discovery window and the first latched treatment bit under this conservative component budget.

## 3. Concrete far-end switching chain

### Treatment latch

Candidate: TI SN74LVC1G74 single positive-edge-triggered D flip-flop.

Relevant manufacturer specification:

- operation 1.65–5.5 V;
- up to 200 MHz clock;
- maximum propagation delay about 5.9 ns at 3.3 V.

The noise/random analog process may exist before the sample edge, but **the treatment label is defined only by the Q state captured at the t=0 edge**. Q and any downstream load-control node are enclosed locally at the far end.

### Load switch — preferred high-integrity option

Candidate: Analog Devices ADG901 absorptive RF switch.

Relevant manufacturer specification:

- DC to multi-GHz operation;
- absorptive/matched off-state architecture;
- typical on switching ~3.6 ns, maximum ~6 ns;
- typical off switching ~5.8 ns, maximum ~9.5 ns;
- CMOS/LVTTL control.

This is preferable to a generic analog multiplexer when the goal is a repeatable 50-ohm-vs-reflective load boundary. Exact load states must still be characterized with the actual assembled board.

### Low-cost alternate load switch

Candidate: SN74LVC1G3157 / 74LVC1G3157-class SPDT analog switch.

Relevant current specifications include roughly 6-ohm typical on resistance, hundreds of MHz analog bandwidth and single-digit-nanosecond enable/disable times at 3.3–5 V. If used, the matched branch resistor must be selected **after measuring actual on resistance**, not from the nominal value alone.

## 4. Acquisition architecture

Source side:

- 50-ohm source/bridge or directional sampling network;
- continuously present low-frequency test excitation, initially <=1 MHz;
- channel A: raw source-side waveform;
- channel B: bit-independent t=0 timing marker only;
- pretrigger capture mandatory;
- save raw ADC counts before any filtering.

USB-scope classes already identified as sufficient on paper:

- Hantek 6022BE: 48 MS/s, 20 MHz, 2 channels, 8-bit, up to 1 M sample buffer;
- PicoScope 2204A: 100 MS/s, 10 MHz, 2 channels.

The mandatory ordinary `+tau_cal` calibration, not the catalog sample rate, decides whether a specific unit is scientifically adequate.

## 5. Strict pre-randomization calibration sequence

Before any randomized trials:

1. assemble the far-end switch with deterministic 0/1 control;
2. measure the actual electrical transition latency distribution from the t=0 timing edge to the load boundary;
3. record `t_sw,median`, `t_sw,max_cal` and timing jitter;
4. measure `tau_cal` from the ordinary return/transition, independently for each cable;
5. freeze the ordinary `+tau_cal` waveform template;
6. freeze the scalar/matched-filter projection used at both negative and positive windows;
7. verify that `t_sw,max_cal < 0.8 tau_cal - margin`;
8. verify the ordinary positive-control effect size `d_plus` is large enough for a useful trial count;
9. only then freeze the randomized trial count and analysis manifest.

Recommended validity margin: require at least 5 scope samples between the end of the primary window and `t=0` after accounting for calibration uncertainty and trigger jitter.

At 48 MS/s this is ~104.2 ns. The nominal 50 m design has ~168 ns guard and therefore passes on planning values; 100 m is substantially stronger.

## 6. Randomized trial topology

Each trial:

1. keep the physical load in the common pre-trial state;
2. acquire the source waveform with pretrigger memory;
3. at t=0, latch the local random/noise state into the D flip-flop;
4. Q immediately commands the load state;
5. preserve the raw waveform and latched bit;
6. reject the trial only for a preregistered hardware-validity fault, never based on waveform value.

Primary hypothesis:

`future load state -> source waveform association centered at t_sw - tau_cal`.

Positive control:

`load state -> source waveform separation centered at t_sw + tau_cal`.

## 7. Required controls

### Sham

Latch the same late bit with identical clock and electronics, but electrically disconnect bit -> load. A negative-lag signal that survives sham is not attributable to the transmission-line load boundary.

### Sentinel around t=0

Measure direct EMI/clock pickup around the latch/switch event. This window is diagnostic only and never a discovery window.

### Load-state mapping swap

Invert bit -> physical-load mapping. A physical effect must follow actual load state, not the logical bit polarity.

### Length law

Repeat with 50 m and 100 m independently calibrated cable. A candidate advanced center must move approximately as `-tau_cal`; the ordinary response must move as `+tau_cal`; fixed EMI pickup should remain near fixed clock-relative time.

### RNG predictability audit

Freeze a predictor before randomized data collection and test whether the future latched bit is statistically predictable from source-side or far-end analog measurements available during the negative-lag primary window. If yes, the future-choice interpretation is invalid until that predictability path is removed.

## 8. Primary analysis rule

Use one frozen scalar score per trial:

`S_minus = <x_minus, template>`

where `x_minus` is the raw/predefined linearly preprocessed waveform segment in the negative-lag window. Use the same template construction and sign convention for the positive control.

Confirmatory significance must come from the preregistered treatment-label randomization/permutation distribution, not a Gaussian approximation.

No:

- filtfilt / zero-phase filtering;
- label-dependent denoising;
- post-hoc window movement;
- post-hoc polarity selection;
- changing cable delay after looking at negative-lag results;
- trial deletion based on primary score.

## 9. Go/no-go before collecting a large dataset

Proceed to a full randomized block only if all hold:

- timing-validity guard passes;
- raw pretrigger export works reliably;
- ordinary +tau calibration is clearly visible in individual or averaged traces;
- sham produces no corresponding load-state effect;
- `d_plus` is large enough that the preregistered target sensitivity is computationally and experimentally practical.

Use the previously derived planning relation:

`n_per_state ~= 78.91578014 / (eta * d_plus)^2`

for one-sided 5-sigma / 90% power planning only.

Initial falsification target remains `eta_min = 1%` of the apparatus's own ordinary positive-lag response.

## 10. Epistemic status

- R1 source-only CPU timing trial: **VALID PROSPECTIVE NULL**.
- Standard retarded cable response: **PROVEN within the standard transmission-line model**.
- Stage 35D timing inequalities: **COMPUTATIONALLY VERIFIED**.
- Off-the-shelf logic/switch timing feasibility: **SUPPORTED BY CURRENT MANUFACTURER SPECIFICATIONS**.
- Advanced/negative-lag response: **NOT OBSERVED**.
- Stage 35D experiment: **BLOCKED_BY_RESOURCE** until physical hardware is assembled.

## 11. Scientific decision

The main project bottleneck is no longer coding, future randomness provenance, CPU timing analysis or GHz-class acquisition. It is now a concrete physical question:

> Does a late, locally formed far-end load choice produce any reproducible source-side association in the objectively earlier `t_sw - tau_cal` window once ordinary leakage controls are enforced?

The next genuinely decisive action is hardware assembly and calibration, not another software-only Eurojackpot/CPU-timing version.

## Manufacturer evidence used for this design

- Hantek 6022BE official product page/user manual: 48 MS/s, 20 MHz, 2 channels, 8-bit, up to 1 M sample buffer.
- Pico Technology PicoScope 2200A Series datasheet: 2204A 100 MS/s, 10 MHz, 2 channels.
- Texas Instruments SN74LVC1G74 product page/datasheet: 1.65–5.5 V, 200 MHz class, maximum tpd about 5.9 ns at 3.3 V.
- Analog Devices ADG901/902 datasheet: absorptive/reflective RF switching, DC-to-GHz, nanosecond switching.
- TI/Nexperia SN74LVC1G3157/74LVC1G3157 datasheets: SPDT analog switching with low on resistance and nanosecond-class switching.
