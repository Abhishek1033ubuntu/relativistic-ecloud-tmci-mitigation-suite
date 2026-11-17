"""
Milestone 1: Relativistic Boris-PIC Pusher with Variable-Step Transverse Gradient
Author: Abhishek Singh | Copyright (c) 2026 Abhishek Singh
"""
import numpy as np

def adaptive_center_confinement_gradient(x, y, k_base=2.5e5, gain_multiplier=1.0, edge_threshold=0.0015):
    r = np.sqrt(x**2 + y**2)
    k_nl = k_base * gain_multiplier
    scaling = 1.0 + 10.0 * np.maximum(0.0, (r - edge_threshold) / edge_threshold) ** 2
    Fx = -k_nl * x * scaling
    Fy = -k_nl * y * scaling
    return Fx, Fy

def boris_step(x, y, vx, vy, vz, Fx_total, Fy_total, dt=1e-9, q_mass_ratio=9.57883e7):
    vx_next = vx + dt * q_mass_ratio * Fx_total
    vy_next = vy + dt * q_mass_ratio * Fy_total
    x_next = x + vx_next * dt
    y_next = y + vy_next * dt
    c = 2.99792458e8
    beta_max = np.max(np.sqrt(vx_next**2 + vy_next**2 + vz**2)) / c
    return x_next, y_next, vx_next, vy_next, beta_max
