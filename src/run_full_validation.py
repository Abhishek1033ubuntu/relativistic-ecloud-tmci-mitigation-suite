"""
Master Validation Orchestrator: Milestones 1, 2, and 3 Comparative Suite
Author: Abhishek Singh | Copyright (c) 2026 Abhishek Singh
"""
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from src.beam_generator import generate_matched_6d_bunch
from src.boris_gradient_solver import adaptive_center_confinement_gradient, boris_step
from src.ecloud_multipacting import update_electron_cloud, compute_wakefield_kick
from src.materials_bom_screener import screen_subatomic_materials
from src.bunch_gap_damper import apply_gated_damping_and_halo_balance

def run_all(output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    ranked_materials = screen_subatomic_materials()
    champion = ranked_materials[0]
    c = 2.99792458e8
    dt = 1e-9
    num_turns = 240

    configs = [
        {"key": "baseline", "label": "Baseline (SEY=1.35, 1.9K)", "sey": 1.35, "gain": 1.00, "seed": 1.2e9, "gaps": False, "damper": False, "color": "tab:blue"},
        {"key": "m1_m2", "label": "M1+M2 Only (Champion BOM, No Gap)", "sey": champion["sey_max"], "gain": champion["gradient_gain_factor"], "seed": 2.5e8, "gaps": False, "damper": False, "color": "orange"},
        {"key": "m1_m2_m3", "label": "M1+M2+M3 (Period Gap + Gated Damper)", "sey": champion["sey_max"], "gain": champion["gradient_gain_factor"], "seed": 2.5e8, "gaps": True, "damper": True, "color": "green"},
    ]

    summary = {"champion_material": champion, "benchmarks": {}}
    trajectories = {}

    for cfg in configs:
        np.random.seed(42)
        particles = generate_matched_6d_bunch(num_particles=20000)
        n_e = 1.0e9
        turns, centroids, rms_list, clouds = [], [], [], []
        beta_peak = 0.0

        for turn in range(num_turns):
            x, xp, y, yp = particles[:, 0], particles[:, 1], particles[:, 2], particles[:, 3]
            vz = c * 0.999999991
            vx, vy = xp * vz, yp * vz
            cx, cy = np.mean(x), np.mean(y)
            cvx, cvy = np.mean(vx), np.mean(vy)

            in_gap = cfg["gaps"] and ((turn % 16) >= 12)
            n_e = update_electron_cloud(n_e, sey_max=cfg["sey"], photo_seed=cfg["seed"], in_clearing_gap=in_gap)
            Fx_wake, Fy_wake = compute_wakefield_kick(x, y, cx, cy, n_e)
            Fx_grad, Fy_grad = adaptive_center_confinement_gradient(x, y, gain_multiplier=cfg["gain"])

            x, y, vx, vy, b_max = boris_step(x, y, vx, vy, vz, Fx_grad + Fx_wake, Fy_grad + Fy_wake, dt=dt)
            beta_peak = max(beta_peak, b_max)

            if cfg["damper"]:
                x, y, vx, vy = apply_gated_damping_and_halo_balance(x, y, vx, vy, cx, cy, cvx, cvy)

            particles[:, 0], particles[:, 1] = x, vx / vz
            particles[:, 2], particles[:, 3] = y, vy / vz

            if turn % 10 == 0:
                turns.append(turn)
                centroids.append(float(cx * 1e3))
                rms_list.append(float(np.std(x) * 1e3))
                clouds.append(float(n_e))

        trajectories[cfg["key"]] = {"cfg": cfg, "turns": turns, "centroids": centroids, "rms": rms_list, "clouds": clouds}
        summary["benchmarks"][cfg["key"]] = {
            "label": cfg["label"],
            "final_centroid_mm": round(centroids[-1], 4),
            "final_rms_mm": round(rms_list[-1], 4),
            "peak_residual_ecloud_m3": float(f"{np.max(clouds[-5:]):.2e}"),
            "peak_relativistic_beta": round(float(beta_peak), 9)
        }

    # Plot 1: Milestone 1 Confinement
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    t_m1 = trajectories["m1_m2"]["turns"]
    ax1.plot(t_m1, trajectories["m1_m2"]["centroids"], "r-o", markersize=4, lw=2, label="Centroid Offset X (mm)")
    ax1.axhline(0, color="k", linestyle="--", alpha=0.5)
    ax1.set_title("Milestone 1: Variable-Step Gradient Confinement")
    ax1.set_xlabel("Turns")
    ax1.set_ylabel("Mean Centroid X (mm)")
    ax1.grid(True)
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig(f"{output_dir}/milestone1_gradient_confinement.png", dpi=150)
    plt.close(fig1)

    # Plot 2: Milestone 2 BOM E-Cloud Suppression
    fig2, axes2 = plt.subplots(1, 2, figsize=(11, 4.2))
    for k in ["baseline", "m1_m2"]:
        tr = trajectories[k]
        axes2[0].plot(tr["turns"], tr["centroids"], marker="o", markersize=4, lw=2, color=tr["cfg"]["color"], label=tr["cfg"]["label"])
        axes2[1].plot(tr["turns"], np.array(tr["clouds"]) / 1e12, marker="^", markersize=4, lw=2, color=tr["cfg"]["color"], label=tr["cfg"]["label"])
    axes2[0].set_title("Centroid Recovery: Baseline vs Champion BOM")
    axes2[0].set_xlabel("Turns")
    axes2[0].set_ylabel("Centroid X (mm)")
    axes2[0].grid(True)
    axes2[0].legend(fontsize=8)
    axes2[1].set_title("E-Cloud Multipacting Extinction (10^12 m^-3)")
    axes2[1].set_xlabel("Turns")
    axes2[1].set_ylabel("Cloud Density (10^12 m^-3)")
    axes2[1].grid(True)
    axes2[1].legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(f"{output_dir}/milestone2_bom_ecloud_suppression.png", dpi=150)
    plt.close(fig2)

    # Plot 3: Milestone 3 Period Gap + Gated Stabilization
    fig3, axes3 = plt.subplots(1, 3, figsize=(15, 4.3))
    for k in ["m1_m2", "m1_m2_m3"]:
        tr = trajectories[k]
        axes3[0].plot(tr["turns"], tr["centroids"], marker="o", markersize=4, lw=2, color=tr["cfg"]["color"], label=tr["cfg"]["label"])
        axes3[1].plot(tr["turns"], tr["rms"], marker="s", markersize=4, lw=2, color=tr["cfg"]["color"], label=tr["cfg"]["label"])
        axes3[2].plot(tr["turns"], np.array(tr["clouds"]) / 1e9, marker="^", markersize=4, lw=2, color=tr["cfg"]["color"], label=tr["cfg"]["label"])
    axes3[0].axhline(0, color="k", linestyle="--", alpha=0.6)
    axes3[0].set_title("Mean Path Alignment: Centroid X (mm)")
    axes3[0].set_xlabel("Turns")
    axes3[0].set_ylabel("Centroid Offset X (mm)")
    axes3[0].legend(fontsize=8)
    axes3[0].grid(True)
    axes3[1].set_title("Beam Core Tightness: RMS Size X (mm)")
    axes3[1].set_xlabel("Turns")
    axes3[1].set_ylabel("RMS Beam Radius (mm)")
    axes3[1].legend(fontsize=8)
    axes3[1].grid(True)
    axes3[2].set_title("Suppressed E-Cloud Density (10^9 m^-3)")
    axes3[2].set_xlabel("Turns")
    axes3[2].set_ylabel("Density (10^9 m^-3)")
    axes3[2].legend(fontsize=8)
    axes3[2].grid(True)
    fig3.tight_layout()
    fig3.savefig(f"{output_dir}/milestone3_gap_gated_stabilization.png", dpi=150)
    plt.close(fig3)

    with open(f"{output_dir}/validation_telemetry_summary.json", "w", encoding="utf-8") as jf:
        json.dump(summary, jf, indent=2)
    print("Validation complete. Artifacts saved to:", output_dir)

if __name__ == "__main__":
    run_all()
