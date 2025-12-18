#!/usr/bin/env python3
"""
Calculate d_evo and eta values for Table I using material properties
Reads laser parameters from experiments.yaml
"""

import yaml

with open("materials.yaml") as f:
    materials = yaml.safe_load(f)

with open("experiments.yaml") as f:
    experiments = yaml.safe_load(f)

# Map experiment tags to Table I labels
table_systems = {
    "Bykov et al.": "Northup",
    "Nikkhou et al.": "Millen",
    "Passive Q-switched": "Standa_Al",
    "Pulsed diode": "uFlash_Ti",
}

# Extract laser parameters from experiments.yaml
laser_systems = {}
for label, tag in table_systems.items():
    exp = experiments[tag]
    laser_systems[label] = {
        "w": float(exp["waist"]) * 1e6,  # Convert m to μm
        "tau": float(exp["pulse_duration"]) * 1e9,  # Convert s to ns
        "lambda": float(exp["wavelength"]) * 1e9,  # Convert m to nm
    }

print("Table I parameter calculations using material-specific sound velocities")
print("=" * 80)

for system_name, params in laser_systems.items():
    w = params["w"]  # μm
    tau = params["tau"]  # ns

    print(f"\n{system_name}: w={w} μm, τ={tau} ns")
    print(f"{'Material':<6} {'v [m/s]':<10} {'d_evo [μm]':<12} {'η':<8}")
    print("-" * 45)

    for mat_name, mat_props in materials.items():
        v = mat_props["speed_of_sound"]  # m/s
        v_um_ns = v / 1000  # Convert to μm/ns

        # Calculate d_evo = w^2/(v*tau) and eta = w/(v*tau)
        eta = w / (v_um_ns * tau)
        d_evo = w * eta 

        print(f"{mat_name:<6} {v:<10.0f} {d_evo:<12.0f} {eta:<8.2f}")

print("\n" + "=" * 80)
