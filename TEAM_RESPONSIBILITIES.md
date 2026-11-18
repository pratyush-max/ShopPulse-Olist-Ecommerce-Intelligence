# ShopPulse: Team Member Responsibility Matrix & Viva Defense Guide

> **Project Title:** ShopPulse – An End-to-End E-Commerce Customer Behaviour, Sales and Delivery Intelligence Platform  
> **Team Composition:** 4 Members (Modularly adjustable to 3)  
> **Mandatory Criterion:** While each member leads a specific module, all members must possess a comprehensive understanding of the complete end-to-end data pipeline.

---

## 1. Team Allocation Matrix

| Role ID | Role Title | Core Responsibilities | Assigned Member |
| :--- | :--- | :--- | :--- |
| **LEAD-01** | **Project Architect & Integration Lead** | Architecture design, Databricks cluster management, Git repository orchestration, overall quality assurance, pipeline coordination | `[Student Name 1 - Team Leader]` |
| **DATA-02** | **Data Ingestion & Storage Engineer** | REST API extraction script (`src/extraction`), dataset collection, schema validation, Databricks Unity Catalog Volume / DBFS raw upload | `[Student Name 2]` |
| **SPARK-03** | **Big Data & PySpark ETL Engineer** | Databricks PySpark development, Medallion Architecture implementation (Bronze, Silver, Gold Delta tables), business logic & KPI calculations | `[Student Name 3]` |
| **BI-04** | **BI Developer & Documentation Specialist** | Power BI dashboard development, DAX measures, data validation tests, academic project report, and presentation slide deck | `[Student Name 4]` |

*(Note: If working as a 3-member team, responsibilities for **BI-04** are divided between **LEAD-01** and **SPARK-03**).*

---

## 2. Granular Task Breakdown by Role

### Role 1: Project Architect & Integration Lead (`[Student Name 1]`)
- **Primary Deliverables:**
  - `README.md`, `ARCHITECTURE.md`, `PROJECT_PLAN.md`.
  - Setting up Git repository, branching rules, `.gitignore`, and `.env.example`.
  - Creating and configuring Databricks workspace (compute clusters, runtime selection, Unity Catalog / DBFS).
  - Monitoring end-to-end milestone completion from 12 Nov to 20 Nov.
- **Viva Defense Topics to Master:**
  - Why choose Databricks and Delta Lake over traditional PostgreSQL or Hadoop HDFS?
  - What are ACID transactions in Delta Lake, and how does the `_delta_log` work?
  - How does Unity Catalog provide governance and lineage across the lakehouse?

### Role 2: Data Ingestion & Storage Engineer (`[Student Name 2]`)
- **Primary Deliverables:**
  - `src/extraction/api_extract_holidays.py` (fetching Brazilian public holidays via Nager.Date API).
  - Downloading and verifying the 9 Olist e-commerce tables and 2 marketing funnel tables.
  - Pre-ingestion validation scripts (`src/extraction/validate_raw_files.py`).
  - Loading raw files into Databricks cloud/object storage (Unity Catalog Volume or DBFS).
- **Viva Defense Topics to Master:**
  - How does the API extraction script handle network retries, timeouts, and JSON parsing?
  - What is the difference between structured CSV data and semi-structured API JSON?
  - Why do we store immutable raw files in object storage before processing them in Spark?

### Role 3: Big Data & PySpark ETL Engineer (`[Student Name 3]`)
- **Primary Deliverables:**
  - Databricks Notebook 01: `01_bronze_ingestion.py` (Raw $\rightarrow$ Bronze Delta).
  - Databricks Notebook 02: `02_silver_transformation.py` (Bronze $\rightarrow$ Silver Delta with cleaning).
  - Databricks Notebook 03: `03_gold_business_aggregates.py` (Silver $\rightarrow$ Gold business marts).
  - Implementing data deduplication, timestamp casting, and verified joins.
- **Viva Defense Topics to Master:**
  - What is lazy evaluation in Apache Spark (Transformations vs Actions)?
  - How do you resolve skewed joins and optimise queries when joining 100k+ rows in PySpark?
  - How are the business KPIs calculated (e.g., AOV, Delivery Delay %, Seller Lead Conversion Rate)?

### Role 4: BI Developer & Documentation Specialist (`[Student Name 4]`)
- **Primary Deliverables:**
  - Interactive Microsoft Power BI dashboard (5 executive reporting pages).
  - Data modeling in Power BI (Star Schema with 1:Many relationships).
  - DAX measures documented in `powerbi/dax_measures.md`.
  - Academic project report (`docs/project_report.md`) and slide deck (`docs/presentation_outline.md`).
  - Automated validation tests in `tests/test_data_integrity.py`.
- **Viva Defense Topics to Master:**
  - How does Power BI connect to Databricks (DirectQuery vs Import Mode)?
  - What is the difference between a calculated column and a DAX measure in Power BI?
  - How does your dashboard help an e-commerce executive make operational and logistics decisions?

---

## 3. Team Collaboration & Daily Check-in Protocol

To prevent last-minute delays:
1. **Daily 10-Minute Standup:** Every morning at 10:00 AM, each member answers:
   - What did you accomplish yesterday?
   - What is your deliverable for today?
   - Is anything blocking your progress?
2. **Git Workflow:**
   - No direct commits of unverified code to `main`.
   - Feature branches (e.g., `feature/api-extraction`, `feature/silver-cleaning`).
   - Integration lead reviews and merges into `main` after running tests.
3. **Shared Knowledge Session (Day 8):**
   - The team conducts a mock viva session where members ask each other cross-functional questions to guarantee zero weak links.

