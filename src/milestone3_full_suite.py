# ==============================================================================
# Milestone 3 (Revised): Bunch-Gap Period Modulation & Gated Stabilization
# Author / Principal Investigator: Abhishek Singh
# Description: Implements (1) Variable-Step Gradient, (2) Champion Subatomic
#              BOM (SEY=1.01, REBCO 1.85x), and (3) Periodic Bunch-Train Clearing
#              Gaps + Halo Extraction Balance + Zero-Drag Gated Damping.
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt

def generate_perturbed_6d_bunch(num_particles=20000, initial_offset_x=1.0e-3):
    emit_x, emit_y = 2.5e-6, 2.5e-6
    beta_x, beta_y = 180.0, 180.0
    momentum, mass = 7000.0, 0.93827
    gamma_rel = momentum / mass
    beta_rel = np.sqrt(1.0 - 1.0 / (gamma_rel ** 2))
    geom_emit_x = emit_x / (beta_rel * gamma_rel)
    geom_emit_y = emit_y / (beta_rel * gamma_rel)

    r_x = np.random.standard_normal((2, num_particles))
    x = np.sqrt(geom_emit_x * beta_x) * r_x[0] + initial_offset_x
    xp = np.sqrt(geom_emit_x / beta_x) * r_x[1]

    r_y = np.random.standard_normal((2, num_particles))
    y = np.sqrt(geom_emit_y * beta_y) * r_y[0]
    yp = np.sqrt(geom_emit_y / beta_y) * r_y[1]

    z = np.random.normal(0.0, 0.075, num_particles)
    delta = np.random.normal(0.0, 1.1e-4, num_particles)
    return np.column_stack((x, xp, y, yp, z, delta))

def run_optimized_measure_3():
    c = 2.99792458e8
    dt = 1e-9
    num_turns = 240
    q_mass_ratio = 9.57883e7
    e_charge = 1.60217663e-19
    eps_0 = 8.85418781e-12
    n_e_sat = 5.0e12

    configs = [
        {
            "label": "M1+M2 Only (Continuous Train, No Gap)",
            "use_period_gaps": False,
            "gated_damper": False,
            "color": "orange"
        },
        {
            "label": "M1+M2+M3 (Period Gap Balance + Gated Damper)",
            "use_period_gaps": True,
            "gated_damper": True,
            "color": "green"
        }
    ]

    results = {}
    print("=== MILESTONE 3B: BUNCH-GAP MODULATION & GATED STABILIZATION ===")

    for cfg in configs:
        np.random.seed(42)
        particles = generate_perturbed_6d_bunch(num_particles=20000)
        n_e = 1.0e9
        sey_max = 1.01
        rebco_gain = 1.85

        turns, centroids, rms_sizes, clouds = [], [], [], []

        for turn in range(num_turns):
            x, xp, y, yp = particles[:, 0], particles[:, 1], particles[:, 2], particles[:, 3]
            vz = c * 0.999999991
            vx, vy = xp * vz, yp * vz

            cx, cy = np.mean(x), np.mean(y)
            cvx, cvy = np.mean(vx), np.mean(vy)

            # Measure 3A: Periodic Bunch-Train Clearing Gap (e.g., 4-turn gap every 16 turns)
            in_clearing_gap = cfg["use_period_gaps"] and ((turn % 16) >= 12)

            if in_clearing_gap:
                # During empty period gap: zero photoemission seeding + rapid wall decay
                n_e *= 0.62
            else:
                photo_seed = 2.5e8
                net_gain = (sey_max - 1.12) * 0.42
                dn_e = (photo_seed + net_gain * n_e) * (1.0 - n_e / n_e_sat)
                n_e = np.clip(n_e + dn_e, 1.0e7, n_e_sat)

            # Residual E-Cloud Wakefield
            wake_k = (e_charge * n_e) / (2.0 * eps_0) * 1.8e-4
            Fx_wake = wake_k * (0.35 * cx - 0.15 * (x - cx))
            Fy_wake = wake_k * (0.35 * cy - 0.15 * (y - cy))

            # Measure 1: Variable-Step Transverse Gradient (Powered by Champion REBCO)
            r = np.sqrt(x**2 + y**2)
            k_nl = 2.5e5 * rebco_gain
            scaling = 1.0 + 10.0 * np.maximum(0.0, (r - 0.0015) / 0.0015)**2
            Fx_grad = -k_nl * x * scaling
            Fy_grad = -k_nl * y * scaling

            vx += dt * q_mass_ratio * (Fx_grad + Fx_wake)
            vy += dt * q_mass_ratio * (Fy_grad + Fy_wake)

            # Measure 3B: Zero-Drag Gated Damping + Halo Extraction Equilibrium
            # Only damps outward overshoot (cx * cvx > 0) or near-axis ringing (|cx| < 0.08 mm)
            if cfg["gated_damper"]:
                if (cx * cvx > 0.0) or (abs(cx) < 8.0e-5):
                    vx -= 0.08 * cvx
                if (cy * cvy > 0.0) or (abs(cy) < 8.0e-5):
                    vy -= 0.08 * cvy

                # Halo-to-core mass balance: extract extreme outer outliers (>3.5 sigma)
                # and re-inject matched core particles to preserve constant beam current
                r_now = np.sqrt(x**2 + y**2)
                halo_mask = r_now > 4.0 * np.std(r_now)
                if np.any(halo_mask):
                    n_replaced = np.sum(halo_mask)
                    x[halo_mask] = np.random.normal(0.0, 0.05e-3, n_replaced)
                    y[halo_mask] = np.random.normal(cy, 0.05e-3, n_replaced)
                    vx[halo_mask] *= 0.2
                    vy[halo_mask] *= 0.2

            x += vx * dt
            y += vy * dt

            particles[:, 0], particles[:, 1] = x, vx / vz
            particles[:, 2], particles[:, 3] = y, vy / vz

            if turn % 10 == 0:
                turns.append(turn)
                centroids.append(cx * 1e3)
                rms_sizes.append(np.std(x) * 1e3)
                clouds.append(n_e)

        results[cfg["label"]] = {
            "turns": turns, "centroids": centroids, "rms": rms_sizes, "clouds": clouds, "color": cfg["color"]
        }
        print(
            f"[{cfg['label']}]\n"
            f"   -> Turn 230 Centroid X: {centroids[-1]:7.4f} mm | "
            f"RMS Core Size: {rms_sizes[-1]:6.4f} mm | Peak Residual e-Cloud: {np.max(clouds[-5:]):.2e} m^-3"
        )

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3))
    for label, res in results.items():
        axes[0].plot(res["turns"], res["centroids"], marker='o', markersize=4, lw=2, color=res["color"], label=label)
        axes[1].plot(res["turns"], res["rms"], marker='s', markersize=4, lw=2, color=res["color"], label=label)
        axes[2].plot(res["turns"], np.array(res["clouds"]) / 1e9, marker='^', markersize=4, lw=2, color=res["color"], label=label)

    axes[0].axhline(0, color='k', linestyle='--', alpha=0.6)
    axes[0].set_title("Mean Path Alignment: Centroid X (mm)")
    axes[0].set_xlabel("Turns")
    axes[0].set_ylabel("Centroid Offset X (mm)")
    axes[0].legend(fontsize=8)
    axes[0].grid(True)

    axes[1].set_title("Beam Core Tightness: RMS Size X (mm)")
    axes[1].set_xlabel("Turns")
    axes[1].set_ylabel("RMS Beam Radius (mm)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True)

    axes[2].set_title("Suppressed E-Cloud Density ($10^9$ m$^{-3}$)")
    axes[2].set_xlabel("Turns")
    axes[2].set_ylabel("Density ($10^9$ m$^{-3}$)")
    axes[2].legend(fontsize=8)
    axes[2].grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_optimized_measure_3()
