# Copyright (C) 2025 Jorge Checa Jaspe
# This file is part of LOVE AI.
# LOVE AI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Persistence Module
==================

Handles:
1. Decision history (for learning/forgiveness)
2. Persistent rate limiting (anti-abuse)

This module ensures that context is maintained across script executions.
"""

import os
import json
import time
from datetime import datetime

# Persistence file paths
HISTORY_PATH = "psi_history.json"
RATE_LIMIT_PATH = "rate_limit.json"

# --- History Management ---

def load_history():
    """Loads the decision history from the local JSON file."""
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, 'r') as f:
            data = json.load(f)
        for item in data:
            if 'timestamp' in item and isinstance(item['timestamp'], str):
                item['timestamp'] = datetime.fromisoformat(item['timestamp'])
        return data
    except Exception:
        return []

def save_history(history):
    """Saves the decision history to the local JSON file."""
    try:
        with open(HISTORY_PATH, 'w') as f:
            json.dump(history, f, default=str, indent=2)
    except Exception:
        pass

def register_decision(file_path, allowed, reason, error_type=None):
    """Registers a decision in the history for future bias calculation."""
    history = load_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "decision": "allowed" if allowed else "blocked",
        "reason": reason
    }
    if error_type:
        entry["type"] = error_type
    history.append(entry)
    save_history(history)

def report_false_positive(file_path):
    """Flags the last block for this file as a mistake (False Positive)."""
    history = load_history()
    for entry in reversed(history):
        if entry.get("file") == file_path and entry.get("decision") == "blocked":
            entry["type"] = "false_positive"
            save_history(history)
            return True
    return False

def report_false_negative(file_path, damage_description=""):
    """Flags the last allow for this file as a mistake (False Negative)."""
    history = load_history()
    for entry in reversed(history):
        if entry.get("file") == file_path and entry.get("decision") == "allowed":
            entry["type"] = "false_negative"
            if damage_description:
                entry["damage"] = damage_description
            save_history(history)
            return True
    return False

# --- Persistent Rate Limiting ---

def _load_rate_limits():
    if not os.path.exists(RATE_LIMIT_PATH):
        return {}
    try:
        with open(RATE_LIMIT_PATH, 'r') as f:
            data = json.load(f)
            return {user: [float(t) for t in attempts] for user, attempts in data.items()}
    except Exception:
        return {}

def _save_rate_limits(limits):
    try:
        with open(RATE_LIMIT_PATH, 'w') as f:
            json.dump(limits, f, indent=2)
    except Exception:
        pass

def verify_rate_limit(user="default", limit=10, window=60):
    """Ensures a user doesn't spam the decision engine."""
    now = time.time()
    limits = _load_rate_limits()
    
    if user not in limits:
        limits[user] = []
    
    # Cleanup expired attempts
    limits[user] = [t for t in limits[user] if now - t < window]
    
    if len(limits[user]) >= limit:
        return False, f"⚠️ RATE LIMIT: Max {limit} attempts per {window}s. Please wait."
    
    limits[user].append(now)
    _save_rate_limits(limits)
    return True, "OK"

def clear_rate_limits():
    """Wipes the rate limit data. Useful for demos."""
    if os.path.exists(RATE_LIMIT_PATH):
        os.remove(RATE_LIMIT_PATH)
