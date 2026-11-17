"""
Milestone 2B: Subatomic Materials Discovery & 50 K Helium-Free BOM Screener
Author: Abhishek Singh | Copyright (c) 2026 Abhishek Singh
"""

def screen_subatomic_materials():
    candidates = [
        {"name": "Baseline LHC (Cu-Coated SS + Nb-Ti @ 1.9K)", "Tc_K": 9.2, "op_temp_K": 1.9, "B_max_T": 8.3, "gradient_gain_factor": 1.00, "sey_max": 1.35, "thermal_margin_W_m": 1.2, "rad_hardness_score": 0.75},
        {"name": "Candidate A (a-C Liner + Nb3Sn @ 4.5K)", "Tc_K": 18.3, "op_temp_K": 4.5, "B_max_T": 12.0, "gradient_gain_factor": 1.25, "sey_max": 1.08, "thermal_margin_W_m": 4.5, "rad_hardness_score": 0.85},
        {"name": "Candidate B (Ti3C2Tx MXene + MgB2 @ 25K He-Free)", "Tc_K": 39.0, "op_temp_K": 25.0, "B_max_T": 15.0, "gradient_gain_factor": 1.45, "sey_max": 1.04, "thermal_margin_W_m": 18.0, "rad_hardness_score": 0.91},
        {"name": "Champion Stack (sp2-C/Diamond Liner + Doped REBCO @ 50K He-Free)", "Tc_K": 93.0, "op_temp_K": 50.0, "B_max_T": 20.5, "gradient_gain_factor": 1.85, "sey_max": 1.01, "thermal_margin_W_m": 45.0, "rad_hardness_score": 0.97}
    ]
    for mat in candidates:
        cryo_score = min(mat["op_temp_K"] / 50.0, 1.0) * 30.0
        field_score = (mat["B_max_T"] / 20.5) * 25.0
        sey_score = max(0.0, (1.35 - mat["sey_max"]) / 0.35) * 30.0
        rad_score = mat["rad_hardness_score"] * 15.0
        mat["FoM"] = round(cryo_score + field_score + sey_score + rad_score, 2)
    return sorted(candidates, key=lambda m: m["FoM"], reverse=True)
