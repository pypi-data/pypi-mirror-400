# Copyright (C) 2025 Jorge Checa Jaspe
# This file is part of LOVE AI.
# LOVE AI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Main Entry Point
================

Orchestrates the entire decision flow.
Restored to the "Original Intelligence" version with added Rate Limiting
and Governance (Axiom 02).
"""

import os
import pprint
from .core import calculate_shannon_entropy, decide as core_decide, calculate_forgiveness_bias
from .config import load_legislation, validate_config
from .persistence import register_decision, load_history, verify_rate_limit
from .adapters.fs import read_file_and_context
from .adapters.sentiment import analyze_stress

def _print_debug_info(result, filepath, prompt):
    """Utility to print metrics when DEBUG_LOVE_AI=1."""
    if os.environ.get("DEBUG_LOVE_AI", "").lower() in ["true", "1"]:
        print("\n--- [LOVE AI DEBUG] ---")
        print(f"File: '{filepath}' | Prompt: '{prompt}'")
        print("-" * 25)
        pprint.pprint(result)
        print("--- [END DEBUG] ---\n")

def decide(
    filepath,
    prompt,
    user="default",
    config_path="heart.txt",
    register=True
):
    """
    High-level API for decision making.
    Orchestrates configuration, signals, and governance rules.
    """
    # 1. Load and Validate Configuration
    config = load_legislation(config_path)
    if not validate_config(config):
        return {"allowed": False, "reason": "🚨 INVALID CONFIGURATION: Core keys missing.", "metrics": {}}

    # 2. Governance Check (AXIOM_02: Master Switch)
    if not config.get("AXIOM_02", True):
        return {"allowed": False, "reason": "⏸️  SYSTEM DISABLED (AXIOM_02=FALSE)", "metrics": {}}

    # 3. Security Check (Rate Limiting)
    rate_limit = config.get("RATE_LIMIT", 10)
    rate_ok, rate_msg = verify_rate_limit(user, limit=rate_limit)
    if not rate_ok:
        return {"allowed": False, "reason": rate_msg, "metrics": {}}
    
    # 4. Gather Physical Signals
    try:
        content, cluster_score = read_file_and_context(filepath)
    except FileNotFoundError:
        result = {"allowed": False, "reason": f"🛑 FILE NOT FOUND: '{filepath}'.", "metrics": {}}
        _print_debug_info(result, filepath, prompt)
        return result

    # 5. Gather Emotional and Historical Signals
    entropy = calculate_shannon_entropy(content)
    stress = analyze_stress(prompt, config)
    history = load_history()
    bias = calculate_forgiveness_bias(history)
    
    # 6. Core Decision
    result = core_decide(
        entropy=entropy, stress=stress, cluster_attention=cluster_score,
        forgiveness_bias=bias, config=config
    )
    
    # 7. Persistence and Logging
    if register:
        register_decision(
            file_path=filepath, allowed=result["allowed"], reason=result["reason"]
        )
    
    _print_debug_info(result, filepath, prompt)
    return result


def is_allowed(filepath, prompt="delete", user="default", config_path="heart.txt"):
    """Simplified API returning a Boolean verdict."""
    result = decide(filepath, prompt, user, config_path=config_path)
    return result["allowed"]
