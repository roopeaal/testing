#!/usr/bin/env python3
"""ERCP Stage35E DC/75-ohm TDR planning audit.

This script is intentionally a planning calculator, not evidence for an
advanced/negative-lag effect. Confirmatory quantities must be measured on
the assembled apparatus and frozen before randomized trials.
"""
import math, json

DELAY_NS_PER_M = 5.05274
ATTEN_DB_PER_100M_1MHZ = 1.3124
FS = 48e6
TSW_NS = 60.0
VBAT = 3.0
RTOP = 1100.0
RBOT = 82.0
Z0 = 75.0
RMOS = 5.3

VTH = VBAT * RBOT / (RTOP + RBOT)
RTH = RTOP * RBOT / (RTOP + RBOT)
GAMMA_S = (RTH-Z0)/(RTH+Z0)
VINC = VTH*Z0/(RTH+Z0)
ZON = 1/(1/Z0 + 1/RMOS)
GAMMA_L = (ZON-Z0)/(ZON+Z0)

def calculate(L):
    tau = DELAY_NS_PER_M*L
    rt_loss_db = ATTEN_DB_PER_100M_1MHZ*(2*L/100)
    amp = 10**(-rt_loss_db/20)
    step = VINC*GAMMA_L*amp*(1+GAMMA_S)
    return {
        "length_m": L,
        "tau_ns": tau,
        "primary_center_ns": TSW_NS-tau,
        "primary_start_ns": TSW_NS-1.2*tau,
        "primary_end_ns": TSW_NS-0.8*tau,
        "guard_ns": 0.8*tau-TSW_NS,
        "samples_per_tau": tau*1e-9*FS,
        "samples_primary_window": 0.4*tau*1e-9*FS,
        "roundtrip_loss_dB_proxy": rt_loss_db,
        "roundtrip_voltage_factor_proxy": amp,
        "expected_source_step_mV_proxy": 1000*step,
        "J": L*amp**2,
    }

a = ATTEN_DB_PER_100M_1MHZ/100
Lstar = 10/(2*a*math.log(10))
Jstar = calculate(Lstar)["J"]
rows = []
for L in (50,100,150,200,250,300,400):
    r = calculate(L)
    r["J_relative"] = r["J"]/Jstar
    rows.append(r)

print(json.dumps({
    "thevenin_V": VTH,
    "thevenin_R_ohm": RTH,
    "source_gamma": GAMMA_S,
    "incident_node_V": VINC,
    "far_on_load_ohm": ZON,
    "far_on_gamma": GAMMA_L,
    "analytic_length_optimum_m": Lstar,
    "rows": rows,
}, indent=2))
