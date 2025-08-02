import os
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.parent.parent

# Configuration file paths
CONFIG_FILE_PATH = ROOT_DIR / "config" / "config.yaml"
PARAMS_FILE_PATH = ROOT_DIR / "params.yaml"
SCHEMA_FILE_PATH = ROOT_DIR / "schema.yaml"
