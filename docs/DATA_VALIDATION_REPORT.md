# ShopPulse: Raw Dataset Validation Report

> **Report Generation Timestamp:** 2026-11-12 14:45:25  
> **Audit Target Directory:** `E:\ShopPulse\data\raw`  
> **Phase:** Phase 1A — Pre-Ingestion Data Quality & Schema Audit  

---

## 1. Executive Summary & Gate Checklist

**Overall Gate Status:** ✅ PASS

| Validation Check | Expected | Actual Result | Status |
| :--- | :--- | :--- | :--- |
| Total CSV Files in `data/raw` | 11 CSVs | 11 CSVs | ✅ PASS |
| Olist E-Commerce Core Tables | 9 Tables | 9 Present | ✅ PASS |
| Olist Marketing Funnel Tables | 2 Tables | 2 Present | ✅ PASS |
| Empty Files (0 Bytes) | 0 Empty | 0 Empty | ✅ PASS |
| Header & Encoding Readability | 100% Readable | 100% Readable UTF-8 | ✅ PASS |
| Orders Primary Key (`order_id`) | Zero Duplicates | 0 Duplicates | ✅ PASS |
| Marketing to Marketplace Link | `seller_id` Join Validated | 380 Matches Found | ✅ PASS |

---

## 2. Granular Table-by-Table Inventory

| Table Filename | Size | Row Count | Column Count | Total Null Cells | Readability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `olist_orders_dataset.csv` | 16.84 MB | 99,441 | 8 | 4,908 | ✅ Valid CSV |
| `olist_order_items_dataset.csv` | 14.72 MB | 112,650 | 7 | 0 | ✅ Valid CSV |
| `olist_customers_dataset.csv` | 8.62 MB | 99,441 | 5 | 0 | ✅ Valid CSV |
| `olist_products_dataset.csv` | 2.27 MB | 32,951 | 9 | 2,448 | ✅ Valid CSV |
| `olist_sellers_dataset.csv` | 170.61 KB | 3,095 | 4 | 0 | ✅ Valid CSV |
| `olist_order_payments_dataset.csv` | 5.51 MB | 103,886 | 5 | 0 | ✅ Valid CSV |
| `olist_order_reviews_dataset.csv` | 13.78 MB | 99,224 | 7 | 145,903 | ✅ Valid CSV |
| `olist_geolocation_dataset.csv` | 58.44 MB | 1,000,163 | 5 | 0 | ✅ Valid CSV |
| `product_category_name_translation.csv` | 2.55 KB | 71 | 2 | 0 | ✅ Valid CSV |
| `olist_marketing_qualified_leads_dataset.csv` | 687.34 KB | 8,000 | 4 | 60 | ✅ Valid CSV |
| `olist_closed_deals_dataset.csv` | 167.34 KB | 842 | 14 | 3,300 | ✅ Valid CSV |

---

## 3. Critical Key Column & Schema Integrity

### 3.1 Orders Table (`olist_orders_dataset.csv`)
- **Total Order Rows:** 99,441
- **Distinct `order_id` values:** 99,441 *(Primary Key is 100% unique; zero duplicates)*
- **Distinct `customer_id` tokens:** 99,441
- **Date Range of Purchases:** `2016-09-04 21:15:19` to `2018-10-17 17:30:18`
- **Null Purchase Timestamps:** 0 *(100% valid timestamps)*
- **Orders In Transit / Canceled (Null Delivery Dates):** 2,965
- **Order Status Breakdown:**
  - `delivered`: 96,478 orders
  - `shipped`: 1,107 orders
  - `canceled`: 625 orders
  - `unavailable`: 609 orders
  - `invoiced`: 314 orders
  - `processing`: 301 orders
  - `created`: 5 orders
  - `approved`: 2 orders

### 3.2 Customers Table (`olist_customers_dataset.csv`)
- **Total Customer Rows:** 99,441
- **Unique Order-Level Tokens (`customer_id`):** 99,441
- **Unique Human Buyers (`customer_unique_id`):** 96,096
- **Repeat Customer Purchases Identified:** 3,345 transactions

### 3.3 Order Items Table (`olist_order_items_dataset.csv`)
- **Total Purchased Line Items:** 112,650
- **Unique Orders Represented:** 98,666
- **Unique Products Sold (`product_id`):** 32,951
- **Active Fulfilling Merchants (`seller_id`):** 3,095
- **Total Product Price Sum:** R$ 13,591,643.70
- **Total Freight Value Sum:** R$ 2,251,909.54

### 3.4 Sellers Table (`olist_sellers_dataset.csv`)
- **Total Registered Sellers:** 3,095
- **Distinct `seller_id` values:** 3,095 *(Primary Key is 100% unique)*

---

## 4. Marketing Funnel to Main Marketplace Cross-Join Audit

- **Total Marketing Qualified Leads (MQLs):** 8,000
- **Total Closed Deals Won:** 842
- **Overall Lead-to-Customer Conversion Rate:** **10.53%**
- **Unique `seller_id` values in Closed Deals:** 842
- **Closed Deal Sellers Matching Main Seller Directory (`olist_sellers_dataset`):** **380**
- **Closed Deal Sellers Actively Generating Orders (`olist_order_items_dataset`):** **380**

> **Key Academic Finding:**  
> Out of 842 closed deals in the marketing funnel, 380 closed-deal seller IDs match registered sellers in the main marketplace dataset. 
> This reflects real-world marketplace dynamics: only a subset of marketing leads closed in 2017–2018 were onboarded into this specific e-commerce store cohort. 
> **Zero synthetic data was generated.** This relationship is authentic and verified.

---

## 5. Next Steps for Phase 1B

All 11 raw CSV files have passed schema, row count, null, and relationship audits.
We are ready to execute **Phase 1B: REST API Public Holiday Ingestion (`src/extraction/api_extract_holidays.py`)**.
