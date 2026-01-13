# Copyright (C) 2025 Jorge Checa Jaspe
# This file is part of LOVE AI.
# LOVE AI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
FileSystem Adapter
==================

Handles interaction with the OS file system.
Restored to the "Original Intelligence" version for smarter context analysis.
"""

import os

def calculate_cluster_attention(filepath, directory_files):
    """
    Calculates contextual importance based on related files in the same folder.
    
    Restored original logic: Counts files with the same extension.
    A high match count indicates the file is part of a critical 'cluster'
    (like a photo album or a document project).
    """
    if not directory_files:
        return 0.0
    
    # Extract extension of the target file
    filename = os.path.basename(filepath)
    extension = filename.split('.')[-1] if '.' in filename else ""
    
    if not extension:
        return 0.1 # Base attention for files without extension
    
    # Count how many other files share the same extension
    matches = 0
    for f in directory_files:
        if f != filename and f.endswith(extension):
            matches += 1
            
    # Normalize (10+ matching files = Large cluster/Maximum attention)
    return min(matches / 10.0, 1.0)


def read_file_and_context(filepath):
    """
    Reads file content (binary-safe) and its directory context.
    
    CRITICAL: Always reads in binary mode ('rb') and decodes to latin-1
    to ensure Shannon entropy works perfectly for PDFs, ZIPs, images, etc.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        # Read in binary mode to support ALL file types
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
            
        # Map bytes 1:1 to characters using latin-1 for consistent entropy calculation
        content = content_bytes.decode('latin-1')
        
        # Get context (other files in the same directory)
        directory = os.path.dirname(os.path.abspath(filepath))
        directory_files = os.listdir(directory)
        
        cluster_score = calculate_cluster_attention(filepath, directory_files)
        
        return content, cluster_score
        
    except Exception as e:
        print(f"⚠️  FileSystem Adapter Error: {e}")
        return "", 0.0

def get_file_info(filepath):
    """
    Restored helper to get basic file metadata.
    """
    info = {"size": 0, "extension": "", "exists": False}
    if os.path.exists(filepath):
        info["exists"] = True
        info["size"] = os.path.getsize(filepath)
        info["extension"] = filepath.split('.')[-1] if '.' in filepath else ""
    return info
