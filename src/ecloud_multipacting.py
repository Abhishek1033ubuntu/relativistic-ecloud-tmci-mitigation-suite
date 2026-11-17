"""
Milestone 2: Electron-Cloud Multipacting Buildup & Wakefield Back-Reaction
Author: Abhishek Singh | Copyright (c) 2026 Abhishek Singh
"""
import numpy as np

def update_electron_cloud(n_e, sey_max=1.35, photo_seed=1.2e9, n_e_sat=5.0e12, in_clearing_gap=False):
    if in_clearing_gap:
        return np.clip(n_e * 0.62, 1.0e7, n_e_sat)
    net_gain = (sey_max - 1.12) * 0.42
    dn_e = (photo_seed + net_gain * n_e) * (1.0 - n_e / n_e_sat)
    return np.clip(n_e + dn_e, 1.0e7, n_e_sat)

def compute_wakefield_kick(x, y, cx, cy, n_e):
    e_charge = 1.60217663e-19
    eps_0 = 8.85418781e-12
    wake_k = (e_charge * n_e) / (2.0 * eps_0) * 1.8e-4
    Fx_wake = wake_k * (0.35 * cx - 0.15 * (x - cx))
    Fy_wake = wake_k * (0.35 * cy - 0.15 * (y - cy))
    return Fx_wake, Fy_wake
