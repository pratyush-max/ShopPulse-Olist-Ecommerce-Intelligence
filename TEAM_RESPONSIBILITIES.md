# ShopPulse: Team Member Responsibility Matrix & Defense Guide

> **Project Title:** ShopPulse – An End-to-End E-Commerce Customer Behaviour, Sales and Delivery Intelligence Platform  
> **Team Composition:** 3 Members  
> **Mandatory Criterion:** While individual members focus on specific project modules, all members maintain a comprehensive understanding of the entire end-to-end data pipeline.

---

## 1. Team Allocation Matrix

| Team Member | Role Title | Module Ownership / Core Responsibilities |
| :--- | :--- | :--- |
| **Pratyush** | **Team Lead** | *[Placeholder — To be finalized by team: Overall Architecture, Project Lead, Lakehouse Orchestration, Repository Management]* |
| **Anuj** | **Team Member** | *[Placeholder — To be finalized by team: Data Engineering, Pipeline Implementation, Ingestion & Quality Auditing]* |
| **Chirag** | **Team Member** | *[Placeholder — To be finalized by team: Business Intelligence, Dashboard Analytics, DAX Modeling, Documentation]* |

---

## 2. Granular Task Breakdown by Module

### Module A: Project Architecture & Lakehouse Governance
- **Primary Deliverables:**
  - Repository architecture, Git workflow, `.gitignore`, and `.env.example`.
  - Databricks workspace configuration, Unity Catalog Volumes (`/Volumes/workspace/default/shoppulse_raw/`), and schema management (`workspace.default`, `workspace.silver`, `workspace.gold`).
  - System architecture documentation (`ARCHITECTURE.md`, `PROJECT_PLAN.md`).
- **Defense Topics:**
  - Why choose Databricks and Delta Lake over traditional RDBMS or raw cloud storage?
  - How ACID transactions and the Delta transaction log (`_delta_log`) maintain data consistency.
  - How Unity Catalog manages governance, volumes, and cross-layer lineage.

### Module B: Data Extraction, Ingestion & Medallion Engineering
- **Primary Deliverables:**
  - REST API extraction of Brazilian statutory holidays (`src/extraction/api_extract_holidays.py`).
  - Pre-flight schema validation and relational audits (`src/extraction/validate_raw_files.py`, `src/extraction/secondary_audit.py`).
  - Databricks Notebook 1: `notebooks/01_Raw_Bronze_Silver_Pipeline.ipynb` (Raw verification, 12 Bronze Delta tables, 11 Silver cleansed/enriched tables).
  - Databricks Notebook 2: `notebooks/gold/02_Gold_Layer_Analytics.ipynb` (Star-schema Gold dimensional models, fact tables, customer RFM marts, and business KPI aggregates).
- **Defense Topics:**
  - How the REST API extraction script handles network retries, timeouts, and JSON parsing.
  - PySpark transformations: type casting, multi-line CSV handling, deduplication, and window functions.
  - Medallion Architecture progression (Bronze append-only $\rightarrow$ Silver validated $\rightarrow$ Gold curated marts).

### Module C: Business Intelligence & Analytical Serving
- **Primary Deliverables:**
  - Production Microsoft Power BI dashboard (`powerbi/ShopPulse_Dashboard.pbix` and `powerbi/Olist_Ecommerce_Intelligence.pbix`).
  - 4 Executive reporting pages:
    1. Executive Overview & Marketplace Performance
    2. Sales, Product Category & Geographic Intelligence
    3. Customer Intelligence & Retention Dynamics
    4. Marketing Funnel & Operational Delivery Performance
  - Star schema data model connected directly to Databricks SQL Warehouse (Port 443).
  - Validated DAX measures aligned with Lakehouse KPI aggregates.
- **Defense Topics:**
  - How Power BI connects to Databricks SQL Warehouse (DirectQuery / Import mode).
  - Star schema design: 1:Many relationships, role-playing date dimensions, and bidirectional filtering control.
  - Reconciliation between Gold layer SQL metrics and Power BI visual aggregations (e.g., AOV of R$ 160.58).

---

## 3. Team Collaboration Protocol

1. **Sprint Coordination:** Daily coordination during active milestones to track blockers, pipeline outputs, and visual design alignments.
2. **Git Workflow:**
   - Feature-specific updates with explicit file staging.
   - Synchronized commits with descriptive messages.
3. **Cross-Functional Knowledge Transfer:**
   - Joint verification of the 25 Gold tables and 4-page Power BI dashboard to ensure all members are prepared for defense and presentation.
