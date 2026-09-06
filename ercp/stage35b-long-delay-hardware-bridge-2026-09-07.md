# ERCP Stage 35B — Long-delay hardware bridge

## Project-level result

Stage 35's 2.5 m cable is not the cheapest falsification geometry. Its nominal one-way delay at velocity factor 0.66 is only ~12.64 ns, so an engineering design that wants ~10 samples across one one-way delay points toward ~0.8 GS/s acquisition.

The same sign-of-lag test can be made much easier to instrument by increasing propagation length while keeping the late randomized load intervention and frozen source-side pre-window logic unchanged.

A **100 m 50-ohm RG58 line** has nominal propagation speed `u = 0.66 c`, giving

- one-way delay `tau ~= 505.4 ns`;
- claimed advanced signature center `-tau ~= -505.4 ns`;
- ordinary Maxwell reflection center `+tau ~= +505.4 ns`;
- advanced-vs-retarded prediction separation `2 tau ~= 1.0108 us`.

Ten samples per one-way delay then require only ~19.8 MS/s. A practical target of **>=100 MS/s, >=50 MHz analog bandwidth** gives substantial timing margin and is far less demanding than the original 2.5 m geometry. This bandwidth target is an engineering starting point, not a substitute for calibration.

## Cable-loss check

A representative RG58 C/U datasheet gives velocity factor 0.66 and attenuation about 4.7 dB/100 m at 10 MHz. A 100 m load reflection traverses 200 m, so cable loss is about 9.4 dB round-trip. For an ideal `|Gamma|=1` load change this corresponds to a returned voltage ratio of about 0.339 before splitter/connector/instrument losses. This is still large enough for an ordinary positive-lag calibration to be straightforward.

The experiment should begin with a bandwidth-limited signal at <=10 MHz rather than maximizing edge bandwidth. The primary question is the **sign and scaling of lag**, not GHz bandwidth.

## Do not use nominal velocity factor for the scientific endpoint

Before randomized trials, measure the actual line delay `tau_cal` by conventional TDR/reflection calibration. Freeze it. All prospective windows are then defined from `tau_cal`:

- primary advanced window centered at `-tau_cal`;
- positive-control Maxwell window centered at `+tau_cal`.

This removes cable-manufacturer velocity-factor uncertainty from the causal claim.

## Recommended two-length falsification design

Use **50 m and 100 m** physical lines (or independently calibrated equivalent lengths) in separate preregistered runs.

Nominally:

| Length | one-way `tau` | advanced/retarded separation | 10 MHz round-trip cable loss |
|---:|---:|---:|---:|
| 50 m | ~252.7 ns | ~505.4 ns | ~4.7 dB |
| 100 m | ~505.4 ns | ~1.0108 us | ~9.4 dB |

A genuine claimed advanced response must move with **negative** calibrated propagation delay as length changes. A standard reflection moves with **positive** delay. Fixed electronics pickup, clock feedthrough and many trigger artifacts will not obey the `-L/u` law.

This length-scaling test is substantially stronger than merely finding a pre-switch waveform difference at one cable length.

## Late-choice architecture

At the far end, the load controller must create the treatment bit only **after the source-side primary pre-window is already over**. The bit then selects one of two well-characterized load states at `t=0`.

A practical architecture is:

1. source side continuously records the source-power/reflection proxy;
2. far-end logic samples a local physical random source after the pre-window;
3. the sampled bit is latched;
4. a fixed later edge applies the selected load at `t=0`;
5. generation timestamp, switch timestamp and bit label are returned/logged only after the relevant earlier samples exist;
6. raw source traces are never discarded based on the later bit or trial quality, except by objective preregistered hardware-validity gates.

The far-end random choice is the treatment. A deterministic pre-known alternating load sequence is a weaker control because synchronous pickup can become treatment-correlated before the switch.

## Measurement topology

Use a source-side resistive bridge or directional-coupler/TDR-style node to record a scalar waveform sensitive to load reflection. The ordinary `+tau` response is a mandatory positive control: if the apparatus cannot robustly recover the known causal load response, it cannot make a meaningful negative-lag claim.

The trial should preserve:

- full raw pre/post waveform;
- independently recorded future bit;
- bit-generation timestamp;
- load-switch timestamp;
- cable-delay calibration;
- load-state calibration;
- all trials, including null/failed treatment states unless a preregistered hardware-validity gate fails.

## Primary endpoint

For each trial, compute a frozen scalar from the source-side window centered at `-tau_cal` and compare its unconditioned distribution between the two later randomized load states.

Do not condition on later detector outcomes or select favorable waveform regions after labels are known.

The positive-control statistic uses the corresponding window around `+tau_cal` and must detect the ordinary causal response with the expected sign.

## Controls that matter most

1. **Sham:** generate the same late random bit but disconnect it from the load; pre-window effect must disappear.
2. **Positive lag:** `+tau_cal` must show the normal load reflection.
3. **Length law:** repeat at 50 m and 100 m; candidate advanced center must scale as `-L/u`.
4. **Load-state swap:** invert the electrical mapping of bit 0/1; signal must follow physical load, not digital label.
5. **Blind analysis:** freeze the waveform statistic before treatment labels are exposed to analysis.
6. **Independent acquisition:** replicate with another assembled source/load/acquisition chain if any negative-lag candidate appears.

## Statistical scale

Retain Stage 35's rough 5-sigma / 90%-power planning as the initial benchmark:

- standardized effect `d=0.1`: about 7,892 trials per load state;
- `d=0.05`: about 31,568 trials per state by `1/d^2` scaling;
- `d=0.01`: about 789,158 trials per state.

The actual analysis should use the measured noise/autocorrelation structure and a preregistered permutation/randomization test where possible rather than relying on Gaussian IID assumptions.

## What this does and does not achieve

**Achieved:** the high-end nanosecond acquisition barrier is not fundamental. A 100 m line increases the decisive advanced-vs-retarded timing separation by a factor of 40 relative to 2.5 m while retaining a usable ordinary reflection at <=10 MHz.

**Not achieved:** no advanced response has been observed. The experiment still needs real coax, a late randomized load switch, and acquisition hardware. It therefore remains **BLOCKED_BY_RESOURCE**, but the missing resource is now a much more ordinary RF/TDR bench rather than necessarily a GHz-class setup.

## Evidence state

- transmission-line causal sign prediction: **PROVEN within the retarded telegrapher/Maxwell model**;
- delay/loss scaling calculation: **COMPUTATIONALLY VERIFIED**;
- long-delay hardware design: **PROSPECTIVE DESIGN**;
- advanced-wave effect: **NOT OBSERVED**.
