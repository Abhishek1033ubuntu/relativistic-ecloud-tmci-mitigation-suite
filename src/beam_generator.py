"""
6D Courant-Snyder Matched Phase-Space Bunch Generator
Author: Abhishek Singh | Copyright (c) 2026 Abhishek Singh
"""
import numpy as np

def generate_matched_6d_bunch(
    num_particles=20000,
    emit_x=2.5e-6,
    emit_y=2.5e-6,
    beta_x=180.0,
    alpha_x=0.0,
    beta_y=180.0,
    alpha_y=0.0,
    momentum=7000.0,
    mass=0.93827,
    sigma_z=0.075,
    sigma_delta=1.1e-4,
    initial_offset_x=1.0e-3
):
    gamma_rel = momentum / mass
    beta_rel = np.sqrt(1.0 - 1.0 / (gamma_rel ** 2))
    geom_emit_x = emit_x / (beta_rel * gamma_rel)
    geom_emit_y = emit_y / (beta_rel * gamma_rel)

    r_x = np.random.standard_normal((2, num_particles))
    sigma_xx = np.sqrt(geom_emit_x * beta_x)
    sigma_xpxp = np.sqrt(geom_emit_x / beta_x)
    x = sigma_xx * r_x[0] + initial_offset_x
    xp = -alpha_x * sigma_xpxp * r_x[0] + sigma_xpxp * r_x[1]

    r_y = np.random.standard_normal((2, num_particles))
    sigma_yy = np.sqrt(geom_emit_y * beta_y)
    sigma_ypyp = np.sqrt(geom_emit_y / beta_y)
    y = sigma_yy * r_y[0]
    yp = -alpha_y * sigma_ypyp * r_y[0] + sigma_ypyp * r_y[1]

    z = np.random.normal(0.0, sigma_z, num_particles)
    delta = np.random.normal(0.0, sigma_delta, num_particles)

    return np.column_stack((x, xp, y, yp, z, delta))
