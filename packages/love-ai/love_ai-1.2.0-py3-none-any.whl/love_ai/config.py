# Copyright (C) 2025 Jorge Checa Jaspe
# This file is part of LOVE AI.

"""
Configuration Module
====================
Calibrated to AXIOM_01 = 1.1 to ensure isolated unique files are protected.
"""

import os

DEFAULT_CONFIG = {
    "H_THRESHOLD": 3.5,
    "OMEGA_MAX": 0.8,
    "RISK_MAX": 0.75,
    "FRAGILITY_WEIGHT": 0.7,
    "CONTEXT_WEIGHT": 0.3,
    "CURIOSITY_RATE": 0.01,
    "ALLOW_DESTRUCTIVE_CURIOSITY": False,
    "PROVIDER": "local",
    "GEMINI_MODEL": "gemini-1.5-flash",
    "AXIOM_01": 1.1,            # Protection boost for high-entropy objects
    "AXIOM_02": True,
    "AXIOM_03": 1.0,
    "RATE_LIMIT": 10
}

def get_default_config():
    return DEFAULT_CONFIG.copy()

def load_legislation(filepath="heart.txt"):
    config = DEFAULT_CONFIG.copy()
    if not filepath or not os.path.exists(filepath): return config
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("["): continue
                sep = ":" if ":" in line else "="
                if sep in line:
                    k, v = line.split(sep, 1)
                    k, v = k.strip(), v.strip()
                    if k in config:
                        if isinstance(config[k], bool): config[k] = v.lower() in ['true', '1', 'yes', 'on']
                        elif isinstance(config[k], (int, float)):
                            try: config[k] = float(v) if "." in v else int(v)
                            except ValueError: pass
                        else: config[k] = v
    except Exception: pass
    return config

def validate_config(config):
    return all(k in config for k in ["H_THRESHOLD", "OMEGA_MAX", "RISK_MAX"])
