# ShopPulse: Team Member Responsibility Matrix & Defense Guide

> **Project Title:** ShopPulse – An End-to-End E-Commerce Customer Behaviour, Sales and Delivery Intelligence Platform  
> **Industry Option:** Option 2 — E-Commerce, Customer Behaviour and Sales Intelligence  
> **Team Composition:** 3 Members  
> **Mandatory Standard:** While each team member maintains dedicated presentation and technical review ownership over specific modules, all members share a comprehensive understanding of the entire end-to-end data engineering and BI pipeline.

---

## 1. Team Allocation Matrix

| Team Member | Role | Responsibility |
| :--- | :--- | :--- |
| **Pratyush Pratim Thakur** | **Team Lead – Architecture & Engineering Integration** | Core hands-on implementation, overall architecture, Databricks configuration, Medallion pipeline integration, repository management and technical decisions. |
| **Anuj** | **Data Ingestion & Quality Engineering** | Technical review and presentation of source datasets, CSV/API ingestion, Bronze and Silver layers, validation, schema enforcement and data-quality auditing. |
| **Chirag** | **Gold Analytics & Business Intelligence** | Technical review and presentation of Gold-layer modelling, fact and dimension tables, KPI calculations, Power BI, DAX and business insights. |

---

## 2. Ownership Structure: Implementation vs. Presentation & Review

To ensure academic transparency and clear accountability during project evaluation:

- **Implementation Ownership:** Led and executed hands-on by **Pratyush Pratim Thakur**, encompassing end-to-end architecture, Python extraction and validation scripts, Databricks workspace orchestration, PySpark Medallion Delta Lake pipelines (Notebook 1 and Notebook 2), Power BI semantic model engineering, DAX measure creation, and Git repository management.
- **Technical Review & Presentation Ownership:** Assigned across **Pratyush Pratim Thakur**, **Anuj**, and **Chirag** to ensure deep domain mastery, rigorous peer review, and comprehensive module explanation during the project demonstration and faculty viva defense.

---

## 3. Granular Module Breakdown & Viva Defense Areas

### Module 1: System Architecture, Platform Governance & Integration
- **Assigned Presenter & Defense Lead:** **Pratyush Pratim Thakur**
- **Core Deliverables & Workstream:**
  - System architecture design (`ARCHITECTURE.md`, `PROJECT_PLAN.md`).
  - Databricks workspace configuration, Serverless PySpark compute, and Unity Catalog Managed Volume (`/Volumes/workspace/default/shoppulse_raw/`).
  - Catalog and schema governance across `workspace.default` (Bronze), `workspace.silver` (Silver), and `workspace.gold` (Gold).
  - Serving layer configuration: Databricks SQL Warehouse connection (Thrift API, Port 443).
  - Version control orchestration: Git branching, `.gitignore`, `.env.example`, and commit verification.
- **Viva Defense Questions to Master:**
  1. *Why choose a Medallion Lakehouse architecture on Databricks over traditional relational databases or raw object storage?*  
     Delta Lake provides ACID transaction guarantees, schema enforcement, time-travel auditing via the transaction log (`_delta_log`), and unified batch/streaming compute on Apache Spark.
  2. *How do Unity Catalog Managed Volumes differ from deprecated DBFS root mounts?*  
     Managed Volumes provide governed, audited POSIX path access (`/Volumes/catalog/schema/volume/`) without exposing underlying cloud credentials or root storage paths.
  3. *How is data isolation and cross-layer lineage maintained across schemas?*  
     By strictly segmenting append-only raw data (`default`), validated business tables (`silver`), and curated dimensional marts (`gold`) within the governed `workspace` catalog.

---

### Module 2: Data Sourcing, Ingestion & Data Quality Engineering
- **Assigned Presenter & Defense Lead:** **Anuj**
- **Core Deliverables & Workstream:**
  - Source data understanding: 9 Olist e-commerce tables, 2 marketing funnel tables, and the Nager.Date Brazilian public holidays REST API (42 records across 2016–2018).
  - Pre-flight schema validation and relational audits (`src/extraction/validate_raw_files.py`, `src/extraction/secondary_audit.py`).
  - **Notebook 1 Walkthrough:** `notebooks/01_Raw_Bronze_Silver_Pipeline.ipynb` (193 cells, 1.24 MB):
    - Raw volume access and verification in `/Volumes/workspace/default/shoppulse_raw/`.
    - 12 Bronze append-only Delta tables with `_ingested_at` and `_source_file` audit columns.
    - 11 Silver cleansed, typed, deduplicated, and enriched Delta tables in `workspace.silver`.
    - Execution of Silver layer data-quality audit (11 tables verified, 11 passed, 0 failed).
- **Key Technical Findings to Explain:**
  1. *Multi-line CSV parsing in customer reviews:* Explaining how `.option("multiLine", "true").option("quote", '"').option("escape", '"')` prevented record splitting on embedded newlines, preserving all 99,224 review rows.
  2. *Delivery timestamp anomaly reconciliation:* Accounting for why 2,965 orders have null delivery timestamps out of 99,441 total orders (96,478 delivered orders, +8 delivered orders missing carrier delivery logs, -6 canceled orders with recorded delivery timestamps).
  3. *Marketing funnel overlap:* Explaining the verified set intersection where exactly 380 of the 842 closed deals match active sellers with transaction records in the marketplace snapshot, while 462 closed deals represent merchants outside the transactional window.
- **Viva Defense Questions to Master:**
  1. *What is the difference between Bronze and Silver tables in Delta Lake?*  
     Bronze tables retain 100% source fidelity as append-only raw copies with ingestion metadata. Silver tables enforce strict data types, deduplication on primary keys, relational lookups (English category translations), and quality constraints.
  2. *How does the REST API extraction handle network retries, timeouts, and JSON parsing?*  
     Using structured HTTP GET requests with timeout guards, error handling, local caching in `data/raw/api_responses/`, and structured CSV consolidation.
  3. *Why do we avoid synthetic joins when analyzing the marketing funnel?*  
     Authentic data engineering preserves genuine operational attribution: marketing conversion is evaluated on the 842 closed deals, while sales impact is attributed strictly to the 380 active selling merchants.

---

### Module 3: Gold Dimensional Modeling, Business KPIs & Power BI Analytics
- **Assigned Presenter & Defense Lead:** **Chirag**
- **Core Deliverables & Workstream:**
  - **Notebook 2 Walkthrough:** `notebooks/gold/02_Gold_Layer_Analytics.ipynb` (114 cells, 10.42 MB):
    - 5 Gold dimensional tables: `dim_date`, `dim_products`, `dim_sellers`, `dim_customers`, `dim_geolocation`.
    - 5 Gold fact tables: `fact_sales`, `fact_payments`, `fact_reviews`, `fact_marketing_conversion`, `fact_orders`.
    - 14 Gold analytical KPI marts and 1 audit table (25 total Gold tables in `workspace.gold`).
  - **Power BI Dashboard Walkthrough:** `powerbi/ShopPulse_Dashboard.pbix` (476 KB, 4 reporting pages):
    - Page 1: Executive Overview & Marketplace Performance
    - Page 2: Sales, Product Category & Geographic Intelligence
    - Page 3: Customer Intelligence & Retention Dynamics
    - Page 4: Marketing Funnel & Operational Delivery Performance
  - Semantic modeling, DAX measures, and Databricks SQL Warehouse Thrift connection optimization (`maxParallelism=1`, `ConcurrentEvaluationCount=1`).
- **Key Business Metrics to Explain & Defend:**
  1. *Order & Item Reconciliation:* 99,441 total registered orders; 98,666 orders represented in `fact_sales` across 112,650 line items; exactly 775 registered orders do not have corresponding order-item records in the transaction dataset.
  2. *Financial Figures:* Net product GMV of R$ 13,591,643.70 + freight charges of R$ 2,251,909.54 = Total marketplace revenue of R$ 15,843,553.24.
  3. *Average Order Value (AOV):* R$ 160.58 = R$ 15,843,553.24 / 98,666 orders with items (verified in `workspace.gold.kpi_executive_summary`).
  4. *Customer Retention:* 95,420 unique purchasers (`customer_unique_id`), with 2,913 repeat buyers yielding a 3.05% repeat customer rate.
  5. *Logistics & Delivery:* 96,478 delivered orders; 89,853 on-time/early; 6,533 late; 92 unknown delivery dates. On-time delivery rate = 89,853 / 96,478 = 93.13%.
- **Viva Defense Questions to Master:**
  1. *How does the Star Schema in Power BI optimize query performance over Databricks SQL?*  
     Star schemas minimize join depths by connecting high-cardinality fact tables (`fact_sales`, `fact_orders`) directly to dimension tables (`dim_date`, `dim_customers`, `dim_products`) via 1:Many single-direction relationships.
  2. *How do DAX measures prevent incorrect aggregations on pre-averaged columns?*  
     DAX measures dynamically recalculate weighted ratios (such as `DIVIDE(SUM(sales_including_freight_brl), DISTINCTCOUNT(order_id))`) rather than averaging already-aggregated monthly rows.
  3. *How was the Power BI Mashup engine memory exhaustion issue resolved?*  
     By configuring serialized evaluation (`maxParallelism = 1` and `ConcurrentEvaluationCount = 1`) to prevent concurrent Thrift connector connection flooding.

---

## 4. Balanced Three-Member Presentation Sequence

For the formal project demonstration and faculty evaluation, the presentation is structured into four sequential segments:

```
[Phase 1: Architecture & Governance] ──> [Phase 2: Ingestion & Quality] ──> [Phase 3: Gold Modeling & BI] ──> [Phase 4: Joint Viva Panel]
     Pratyush (~5-7 mins)                     Anuj (~7-8 mins)                       Chirag (~7-8 mins)                All Members (~10 mins)
```

| Phase | Presentation Segment | Lead Speaker | Allocated Time | Core Slide & Demonstration Topics |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **Introduction, Problem Statement & Architecture** | **Pratyush Pratim Thakur** | 5–7 mins | E-commerce operational challenges, Medallion Architecture design, Databricks Unity Catalog storage, Git workflow, and technology stack. |
| **2** | **Data Sourcing, Ingestion & Quality Engineering** | **Anuj** | 7–8 mins | Dataset inventory, Nager.Date REST API extraction, raw volume upload, Notebook 1 walk-through, multi-line review parsing, and Silver quality audit pass. |
| **3** | **Gold Modeling, Business KPIs & Power BI Live Demo** | **Chirag** | 7–8 mins | Notebook 2 walk-through, 25 Gold tables, star schema design, financial reconciliation (R$ 15.84M revenue, R$ 160.58 AOV), and live 4-page Power BI dashboard demonstration. |
| **4** | **Technical Viva Defense & Panel Q&A** | **All Team Members** | ~10 mins | Interactive cross-functional evaluation where each member defends their assigned module and demonstrates mastery of the full pipeline. |

---

## 5. Shared Preparation & Cross-Functional Competency

To ensure a seamless, high-scoring viva defense with no single point of failure:

1. **End-to-End Pipeline Literacy:** Every team member must be capable of explaining how a raw data record flows from `data/raw/` through the Unity Catalog Volume, into Bronze Delta, through Silver cleansing, into Gold dimensions/facts, and finally onto a Power BI visual card.
2. **Metric Fluency:** All three members must know the core verified figures by heart:
   - Total Orders: **99,441**
   - Orders with Items: **98,666**
   - Order Items: **112,650**
   - Total Revenue: **R$ 15,843,553.24**
   - Average Order Value: **R$ 160.58**
   - Unique Customers: **95,420**
   - Repeat Customer Rate: **3.05%**
   - On-Time Delivery Rate: **93.13%** (89,853 on-time / 96,478 delivered)
   - Closed Deals Won: **842** (10.53% conversion rate)
   - Matched Active Sellers: **380**
3. **Internal Mock Viva:** Prior to final submission on 20 November 2026, the team conducts a simulated defense session where members cross-examine each other using the defense questions in Section 3.
