#!/usr/bin/env python3
"""
Configuration file for Energy Consumption Analyzer
Centralizes all configuration settings and paths
"""

import os
from pathlib import Path

# Base project directory
PROJECT_ROOT = Path("/Users/saxu/PycharmProjects/Energy_Project/energy_project_v3")

# Data directory
DATA_DIR = PROJECT_ROOT / "data"

# Backend directory
BACKEND_DIR = PROJECT_ROOT / "backend"

# Static files directory (frontend)
STATIC_DIR = PROJECT_ROOT / "static"

# API server configuration
API_HOST = "localhost"
API_PORT = 8000
API_URL = f"http://{API_HOST}:{API_PORT}"

# ML Engine configuration
ML_ENGINE_CONFIG = {
    "anomaly_contamination": 0.1,
    "random_state": 42,
    "prediction_confidence_threshold": 0.8
}

# Required Python packages
REQUIRED_PACKAGES = [
    'numpy', 'pandas', 'sklearn', 'plotly', 
    'scipy', 'statsmodels', 'flask', 'flask_cors'
]

# Data validation settings
VALID_BED_TYPES = ["2", "4", "6"]
VALID_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
