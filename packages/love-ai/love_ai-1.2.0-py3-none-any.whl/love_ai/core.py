# Copyright (C) 2025 Jorge Checa Jaspe
# This file is part of LOVE AI.
# LOVE AI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
LOVE Core - Pure Decision Logic
===============================
Mathematical heart of the system. 
Verified against the manifesto and corrected for logical consistency.
"""

import math
import random
from collections import Counter
from datetime import datetime

CORE_DEFAULTS = {
    "H_THRESHOLD": 3.5,
    "OMEGA_MAX": 0.8,
    "RISK_MAX": 0.75,
    "FRAGILITY_WEIGHT": 0.7,
    "CONTEXT_WEIGHT": 0.3,
    "CURIOSITY_RATE": 0.01,
    "ALLOW_DESTRUCTIVE_CURIOSITY": False,
    "AXIOM_01": 1.0,
    "AXIOM_03": 1.0,
}

def calculate_shannon_entropy(text):
    """Calculates informational complexity (0.0 to 8.0 bits)."""
    if not text: return 0.0
    frequencies = Counter(text)
    length = len(text)
    return -sum((f / length) * math.log2(f / length) for f in frequencies.values())

def calculate_forgiveness_bias(history):
    """
    Calculates bias based on history of errors ONLY.
    Corrected: Normal decisions no longer increase paranoia.
    """
    weight_fp = 0  # False Positives (system was too cautious)
    weight_fn = 0  # False Negatives (system was too reckless)
    now = datetime.now()
    
    for error in history:
        if 'timestamp' not in error or 'type' not in error:
            continue
        
        days = (now - error['timestamp']).days
        decay = math.exp(-days / 365) # 1-year half-life
        
        if error["type"] == "false_positive":
            weight_fp += decay
        elif error["type"] == "false_negative":
            weight_fn += decay
            
    # Bias > 0 means we need MORE caution (due to past FNs)
    # Bias < 0 means we need LESS caution (due to past FPs)
    return math.log(1 + weight_fn) - math.log(1 + weight_fp)

def decide(entropy, stress, cluster_attention, forgiveness_bias, config):
    """
    The Decision Engine.
    Corrected: Safety gates now respond correctly to historical bias.
    """
    cfg = {**CORE_DEFAULTS, **(config or {})}

    # 1. Complexity Normalization
    w_love = min(entropy / cfg["H_THRESHOLD"], 1.0) * cfg.get("AXIOM_01", 1.0)
    
    # 2. Risk Calculation
    base_risk = (w_love * cfg["FRAGILITY_WEIGHT"]) + (cluster_attention * cfg["CONTEXT_WEIGHT"])
    total_risk = base_risk + forgiveness_bias
    
    # 3. Decision Logic (Safety Gates)
    allowed = True
    reason = "✅ ACTION ALLOWED"
    
    # Gate 1: Stress (Tighter threshold if we have past False Negatives)
    stress_threshold = cfg["OMEGA_MAX"] - forgiveness_bias
    if stress > stress_threshold:
        allowed = False
        reason = f"🛑 SANCTUARY MODE: High user stress ({stress:.2f})"
    
    # Gate 2: Weighted Risk
    elif total_risk > cfg["RISK_MAX"]:
        allowed = False
        reason = f"🛡️ PROTECTION: Informational risk too high ({total_risk:.2f})"
        
    # Gate 3: Hard Safety Limit
    elif total_risk > cfg.get("AXIOM_03", 1.0):
        allowed = False
        reason = f"⛔ AXIOM_03 BLOCK: Absolute risk limit reached ({total_risk:.2f})"
    
    # 4. Stochastic Curiosity
    if not allowed and random.random() < cfg["CURIOSITY_RATE"]:
        if cfg["ALLOW_DESTRUCTIVE_CURIOSITY"]:
            allowed = True
            reason = "🌀 CURIOSITY: Exploration allowed"
    
    return {
        "allowed": allowed, "reason": reason,
        "metrics": {
            "entropy": entropy, "stress": stress, "cluster_attention": cluster_attention,
            "total_risk": total_risk, "base_risk": base_risk, "bias": forgiveness_bias
        }
    }
