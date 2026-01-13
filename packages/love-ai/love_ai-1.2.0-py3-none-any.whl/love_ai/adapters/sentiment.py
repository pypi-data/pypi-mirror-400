# Copyright (C) 2025 Jorge Checa Jaspe
# This file is part of LOVE AI.
# LOVE AI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Sentiment Adapter
=================
Determines user stress (Omega). 
Updated to be more sensitive for realistic scenarios.
"""

import os, re

try:
    import google.generativeai as genai
except ImportError:
    genai = None

def _analyze_stress_local(prompt):
    """
    Local heuristic for stress analysis.
    Designed to be sensitive to urgency markers.
    """
    if not prompt: return 0.1
    
    score = 0.2 # Baseline
    
    # Heuristic 1: EXCESSIVE CAPS (Yelling)
    letters = [c for c in prompt if c.isalpha()]
    if len(letters) > 3:
        caps_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if caps_ratio > 0.6: score += 0.4
        
    # Heuristic 2: Exclamation Marks (Urgency)
    exclamations = prompt.count("!")
    if exclamations >= 3: score += 0.4
    elif exclamations >= 1: score += 0.2
    
    # Heuristic 3: Urgent keywords
    urgent_keywords = ["now", "asap", "force", "immediately", "urgent", "delete", "everything"]
    prompt_lower = prompt.lower()
    for word in urgent_keywords:
        if word in prompt_lower:
            score += 0.2
            
    return min(score, 1.0)

def analyze_stress(prompt, config):
    """Orchestrator for stress analysis."""
    provider = config.get("PROVIDER", "local").lower()
    
    if provider == "gemini" and genai and os.environ.get("GOOGLE_API_KEY"):
        try:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            model = genai.GenerativeModel(config.get("GEMINI_MODEL", "gemini-1.5-flash"))
            response = model.generate_content(f"Analyze stress (0.0 to 1.0, only number): '{prompt}'")
            match = re.search(r"(\d\.\d+)", response.text)
            if match: return float(match.group(1))
        except Exception:
            pass # Fall back
            
    return _analyze_stress_local(prompt)
