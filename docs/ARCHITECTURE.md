# System Architecture & Mathematical Formulation

**Author:** Abhishek Singh | **Copyright (c) 2026 Abhishek Singh**

## 1. Symplectic 6D Phase-Space Initialization
Macro-particles are sampled from a 4D Courant-Snyder transverse Gaussian ellipse parameterized by Twiss parameters (α, β, γ) and normalized emittance ε<sub>n</sub>, paired with longitudinal bunch length σ<sub>z</sub> and momentum spread σ<sub>δ</sub>.

## 2. Variable-Step Transverse Gradient Operator (Milestone 1)
To maintain frictionless central confinement while overcoming relativistic magnetic rigidity (β ≈ 0.999999991 c), the radial restoring acceleration scales non-linearly beyond a threshold radius r<sub>0</sub>:

`F_grad(r) = -k_nl * r * [1 + 10 * max(0, (r - r_0) / r_0)^2]`

## 3. Coupled Electron-Cloud Multipacting & Wakefield Feedback (Milestone 2)
Electron cloud density n<sub>e</sub> evolves per bunch passage according to photoemission seeding S<sub>γ</sub>, secondary electron yield δ<sub>max</sub>, and space-charge saturation n<sub>sat</sub>:

`dn_e / dt = [S_γ + 0.42 * (δ_max - 1.12) * n_e] * (1 - n_e / n_sat)`

Reducing δ<sub>max</sub> to `1.01` via the porous sp<sup>2</sup>-carbon / diamond liner forces the net amplification term negative, preventing multipacting avalanche.

## 4. Bunch-Train Period-Gap Modulation & Gated Damping (Milestone 3)
Periodic empty bucket clearing gaps allow residual photoelectrons to decay via wall absorption (`n_e(t+1) = 0.62 * n_e(t)`), while velocity-gated damping engages strictly on outward overshoot (`x * v_x > 0`) to prevent overdamped centroid drag.
