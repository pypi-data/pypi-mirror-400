# Copyright (C) 2025 Jorge Checa Jaspe
# This file is part of LOVE AI.
# LOVE AI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
LOVE AI - Learnable Object Valuation Engine
============================================

Ethical governance system for computational decisions.

Basic Usage:
    from love_ai import is_allowed
    
    if is_allowed("file.pdf", "delete", user="john"):
        # Action allowed
        os.remove("file.pdf")
    else:
        print("File protected")

Author: Jorge Checa Jaspe
License: AGPLv3
Version: 1.2.0
"""

__version__ = "1.2.0"
__author__ = "Jorge Checa Jaspe"
__license__ = "AGPLv3"

# Main Imports
from .__main__ import decide, is_allowed
from .core import calculate_shannon_entropy, calculate_forgiveness_bias
from .config import load_legislation, get_default_config
from .adapters.fs import read_file_and_context, calculate_cluster_attention
from .adapters.sentiment import analyze_stress

# Aliases (Optional backward compatibility if needed, but we are refactoring)
# protect = is_allowed 

__all__ = [
    "is_allowed",
    "decide",
    "calculate_shannon_entropy",
    "calculate_forgiveness_bias",
    "load_legislation",
    "get_default_config",
    "read_file_and_context",
    "calculate_cluster_attention",
    "analyze_stress",
]
