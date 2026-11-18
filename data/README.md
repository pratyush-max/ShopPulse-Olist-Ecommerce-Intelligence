# ShopPulse Data Directory

This directory manages datasets for the **ShopPulse: Olist E-Commerce Intelligence** platform across its lifecycle.

## Data Sources & Attribution

1. **Brazilian E-Commerce Public Dataset by Olist**
   - **Source:** [Kaggle - Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
   - **Publisher:** Olist
   - **License:** CC BY-NC-SA 4.0
   - **Contents:** 100k anonymized orders from 2016 to 2018 across Brazilian marketplaces, covering orders, order items, customers, products, payments, reviews, sellers, and geolocation.

2. **Olist Marketing Funnel Dataset**
   - **Source:** [Kaggle - Marketing Funnel by Olist](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist)
   - **Publisher:** Olist
   - **License:** CC BY-NC-SA 4.0
   - **Contents:** Marketing Qualified Leads (MQLs) and closed deals generated from landing pages between June 2017 and May 2018.

3. **Brazilian National Public Holidays (External REST API)**
   - **Source:** [Nager.Date Public Worldwide Holiday API](https://date.nager.at/)
   - **Endpoint:** `GET https://date.nager.at/api/v3/PublicHolidays/{year}/BR`
   - **Years Ingested:** 2016, 2017, 2018 (42 total holiday entries)

---

## Directory Organization

- `data/raw/`: Staging directory for raw CSV files and API JSON responses before ingestion to cloud storage (Unity Catalog Volume: `/Volumes/workspace/default/shoppulse_raw/`).
- `data/processed/`: Local scratchpad for validation outputs and test transformations.
- `data/gold_exports/`: Curated analytical marts exported from the Gold layer for Power BI reporting.

> **Note on Data Storage:**  
> Large raw CSV files (>100 MB total) are excluded from version control in accordance with `.gitignore` best practices. Run `python src/extraction/validate_raw_files.py` and `python src/extraction/api_extract_holidays.py` to validate and extract datasets locally.
