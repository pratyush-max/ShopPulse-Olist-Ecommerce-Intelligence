

"""
ShopPulse Configuration Loader
==============================
Reads environment variables from '.env' file or provides safe defaults.

Why we need this file:
- Avoids hardcoding file paths or connection parameters.
- Keeps secrets and local machine differences cleanly separated from code.
- Enforces modern Unity Catalog Volume standards rather than deprecated DBFS root.

Author: ShopPulse Big Data Team
Date: November 2026
"""

import os
from pathlib import Path

# Base project directory (ShopPulse repository root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Standard local data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GOLD_EXPORTS_DIR = DATA_DIR / "gold_exports"

# Nager.Date Public Holidays API configuration
NAGER_DATE_API_BASE_URL = os.getenv("NAGER_DATE_API_BASE_URL", "https://date.nager.at/api/v3")
HOLIDAY_COUNTRY_CODE = os.getenv("HOLIDAY_COUNTRY_CODE", "BR")
HOLIDAY_YEARS = [2016, 2017, 2018]

# Databricks Configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://community.cloud.databricks.com")

# Unity Catalog configuration (Modern Databricks Standard)
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG", "main")
DATABRICKS_SCHEMA_BRONZE = os.getenv("DATABRICKS_SCHEMA_BRONZE", "shoppulse_bronze")
DATABRICKS_SCHEMA_SILVER = os.getenv("DATABRICKS_SCHEMA_SILVER", "shoppulse_silver")
DATABRICKS_SCHEMA_GOLD = os.getenv("DATABRICKS_SCHEMA_GOLD", "shoppulse_gold")

# Unity Catalog Managed Volume for raw landing
DATABRICKS_VOLUME_RAW = os.getenv(
    "DATABRICKS_VOLUME_RAW",
    f"/Volumes/{DATABRICKS_CATALOG}/{DATABRICKS_SCHEMA_BRONZE}/raw_data"
)
