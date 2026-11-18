# ShopPulse: Phase 1B API Extraction Audit Report

> **Extraction Timestamp:** 2026-11-12 20:33:56  
> **Source API:** `https://date.nager.at/api/v3/PublicHolidays/{year}/BR`  
> **Target Country:** Brazil (`BR`)  
> **Execution Status:** ✅ SUCCESS  

---

## 1. Executive Summary

| Metric | Value | Verification |
| :--- | :--- | :--- |
| Target Years Requested | `2016, 2017, 2018` | Corresponds to Olist order timeline |
| Total Records Retrieved | **42** | All national holidays captured |
| Raw JSON Files Created | **3** | Unmodified responses in `data/raw/api_responses/` |
| Consolidated CSV Created | **✅ Yes** | Saved at `data/raw/brazil_public_holidays_2016_2018.csv` |

---

## 2. Year-by-Year Extraction Details

| Year | Endpoint URL | HTTP Status | Holiday Count | Raw JSON Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2016** | `https://date.nager.at/api/v3/PublicHolidays/2016/BR` | ✅ 200 OK | 14 | `brazil_holidays_2016.json` | ✅ Success |
| **2017** | `https://date.nager.at/api/v3/PublicHolidays/2017/BR` | ✅ 200 OK | 14 | `brazil_holidays_2017.json` | ✅ Success |
| **2018** | `https://date.nager.at/api/v3/PublicHolidays/2018/BR` | ✅ 200 OK | 14 | `brazil_holidays_2018.json` | ✅ Success |

---

## 3. Sample Holiday Records Retrieved

Here is an excerpt of Brazilian national holidays retrieved for correlation with e-commerce purchase spikes:

| Date | Local Name (Portuguese) | English Name | Fixed? | Global? | Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `2016-01-01` | Confraternização Universal | New Year's Day | False | True | `Public` |
| `2016-02-08` | Carnaval | Carnival | False | True | `Bank;Optional` |
| `2016-02-09` | Carnaval | Carnival | False | True | `Bank;Optional` |
| `2016-03-25` | Sexta-feira Santa | Good Friday | False | True | `Public` |
| `2016-03-27` | Domingo de Páscoa | Easter Sunday | False | True | `Public` |
| `2016-04-21` | Dia de Tiradentes | Tiradentes | False | True | `Public` |
| `2016-05-01` | Dia do Trabalhador | Labour Day | False | True | `Public` |
| `2016-05-26` | Corpus Christi | Corpus Christi | False | True | `Public` |
| `2016-07-09` | Revolução Constitucionalista de 1932 | Constitutionalist Revolution of 1932 | False | False | `Public` |
| `2016-09-07` | Dia da Independência | Independence Day | False | True | `Public` |
| `2016-10-12` | Nossa Senhora Aparecida | Our Lady of Aparecida | False | True | `Public` |
| `2016-11-02` | Dia de Finados | All Souls' Day | False | True | `Public` |

---

## 4. Preservation of Schema & Data Integrity

- **Raw JSON Preserved:** Unmodified API responses saved directly to `data/raw/api_responses/` without alterations.
- **Unified CSV Export:** `data/raw/brazil_public_holidays_2016_2018.csv` standardizes field names (`date`, `local_name`, `english_name`, `country_code`, etc.) to snake_case for seamless PySpark reading.
- **No Fake Data:** All records were fetched live from the official Nager.Date API with verified ISO-8601 date strings (`YYYY-MM-DD`).

---

## 5. Next Steps for Lakehouse Ingestion

With the completion of Phase 1B, the raw data layer is 100% complete:
- 11 Olist CSV tables (e-commerce and marketing funnel)
- 1 Brazilian public holidays CSV table + 3 raw JSON responses
- **Total:** 12 curated raw datasets ready for cloud storage upload (Phase 1C) and Bronze Layer Delta Lake ingestion.