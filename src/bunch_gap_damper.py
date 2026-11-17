"""
Milestone 3: Bunch-Train Period-Gap Modulation & Zero-Drag Gated Damping
Author: Abhishek Singh | Copyright (c) 2026 Abhishek Singh
"""
import numpy as np

def apply_gated_damping_and_halo_balance(x, y, vx, vy, cx, cy, cvx, cvy):
    if (cx * cvx > 0.0) or (abs(cx) < 8.0e-5):
        vx = vx - 0.08 * cvx
    if (cy * cvy > 0.0) or (abs(cy) < 8.0e-5):
        vy = vy - 0.08 * cvy

    r_now = np.sqrt(x**2 + y**2)
    halo_mask = r_now > 4.0 * np.std(r_now)
    if np.any(halo_mask):
        n_rep = np.sum(halo_mask)
        x[halo_mask] = np.random.normal(0.0, 0.05e-3, n_rep)
        y[halo_mask] = np.random.normal(0.0, 0.05e-3, n_rep)
    return x, y, vx, vy
