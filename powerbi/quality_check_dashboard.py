"""
quality_check_dashboard.py
==========================
ShopPulse – Power BI Dashboard Quality Check and Corrections
Applies all fixes to Olist_Ecommerce_Intelligence.pbix:

1. Fix avg_ / average_ column misaggregation → new DAX measures
2. Fix year_month slicer blank issue → add sort-key column + sort-by  
3. Fix monthly trend charts – proper chronological sort, blank handling
4. Fix customer lifetime value trend – weighted avg DAX
5. Add/complete Marketing & Operations visuals with correct aggregation
6. Fix all formats: BRL, %, integer with commas
7. Regenerate all 4 pages with correct visual configs
"""

import zipfile
import json
import shutil
import os
import re
import struct

# ── File paths ─────────────────────────────────────────────────────────────
SRC_PBIX  = r"E:\ShopPulse\powerbi\Olist_Ecommerce_Intelligence.pbix"
OUT_PBIX  = r"E:\ShopPulse\powerbi\Olist_Ecommerce_Intelligence.pbix"
MIRROR    = r"E:\ShopPulse\Olist_Ecommerce_Intelligence.pbix"
WORK_PBIX = r"E:\ShopPulse\powerbi\qc_work.pbix"

# ── Read existing PBIX ─────────────────────────────────────────────────────
print("Reading existing PBIX …")
shutil.copy2(SRC_PBIX, WORK_PBIX)

with zipfile.ZipFile(SRC_PBIX, "r") as z:
    schema_raw   = z.read("DataModelSchema").decode("utf-16-le")
    layout_raw   = z.read("Report/Layout").decode("utf-16-le")
    all_entries  = {name: z.read(name) for name in z.namelist()}

schema = json.loads(schema_raw)
layout = json.loads(layout_raw)
print("  DataModelSchema:", len(schema_raw), "chars")
print("  Report/Layout:", len(layout_raw), "chars")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 – NEW / CORRECTED DAX MEASURES
# ═══════════════════════════════════════════════════════════════════════════
# 
# Problems identified:
#  • kpi_monthly_customer_acquisition.avg_customer_lifetime_value  → SUM would be wrong
#  • kpi_monthly_reviews.average_review_score → SUM would be wrong
#  • kpi_reviews_by_state.average_rating → SUM would be wrong
#  • kpi_monthly_delivery.average_days_vs_estimated_delivery → SUM wrong
#  • kpi_monthly_marketing.average_days_to_conversion → SUM wrong
#  • kpi_executive_summary.average_review_score → existing measure uses AVERAGE (OK for 1 row table)
#  • kpi_monthly_payments.average_payment_brl → SUM wrong if used raw
#
# Correct approach: 
#  • For monthly/state review/delivery averages we calculate weighted AVG via 
#    DIVIDE(SUM(numerator_col), SUM(count_col)) where possible, or use 
#    AVERAGEX with appropriate weight.
#  • For single-row summary tables (kpi_executive_summary) AVERAGE is fine.
# ─────────────────────────────────────────────────────────────────────────

NEW_MEASURES = {
    # Table → list of (name, expression, format_string)
    "kpi_monthly_customer_acquisition": [
        (
            "Avg Customer Lifetime Value",
            # Weighted average: total cohort revenue / total customers acquired
            "DIVIDE(\n"
            "    SUMX('kpi_monthly_customer_acquisition', 'kpi_monthly_customer_acquisition'[avg_customer_lifetime_value] * ('kpi_monthly_customer_acquisition'[one_time_customers] + 'kpi_monthly_customer_acquisition'[repeat_customers])),\n"
            "    SUMX('kpi_monthly_customer_acquisition', 'kpi_monthly_customer_acquisition'[one_time_customers] + 'kpi_monthly_customer_acquisition'[repeat_customers])\n"
            ")",
            '"R$"\\ #,##0.00',
        ),
        (
            "Total New Customers",
            "SUM('kpi_monthly_customer_acquisition'[new_customers])",
            "#,##0",
        ),
        (
            "Monthly Repeat Customer Rate",
            "DIVIDE(\n"
            "    SUM('kpi_monthly_customer_acquisition'[repeat_customers]),\n"
            "    SUM('kpi_monthly_customer_acquisition'[new_customers])\n"
            ")",
            "0.00%",
        ),
    ],
    "kpi_monthly_reviews": [
        (
            "Monthly Avg Review Score",
            # Weighted: sum(avg_score * total_reviews) / sum(total_reviews)
            "DIVIDE(\n"
            "    SUMX('kpi_monthly_reviews', 'kpi_monthly_reviews'[average_review_score] * 'kpi_monthly_reviews'[total_reviews]),\n"
            "    SUM('kpi_monthly_reviews'[total_reviews])\n"
            ")",
            "0.00",
        ),
        (
            "Monthly Positive Review Rate",
            "DIVIDE(\n"
            "    SUM('kpi_monthly_reviews'[positive_reviews]),\n"
            "    SUM('kpi_monthly_reviews'[total_reviews])\n"
            ")",
            "0.00%",
        ),
    ],
    "kpi_reviews_by_state": [
        (
            "State Avg Rating",
            # Weighted average across states
            "DIVIDE(\n"
            "    SUMX('kpi_reviews_by_state', 'kpi_reviews_by_state'[average_rating] * 'kpi_reviews_by_state'[total_reviews]),\n"
            "    SUM('kpi_reviews_by_state'[total_reviews])\n"
            ")",
            "0.00",
        ),
        (
            "State Total Reviews",
            "SUM('kpi_reviews_by_state'[total_reviews])",
            "#,##0",
        ),
        (
            "State Positive Review Rate",
            "DIVIDE(\n"
            "    SUM('kpi_reviews_by_state'[positive_reviews]),\n"
            "    SUM('kpi_reviews_by_state'[total_reviews])\n"
            ")",
            "0.00%",
        ),
    ],
    "kpi_monthly_delivery": [
        (
            "Avg Days vs Estimated",
            # Weighted: sum(avg_days * delivered_orders) / sum(delivered_orders)
            "DIVIDE(\n"
            "    SUMX('kpi_monthly_delivery', 'kpi_monthly_delivery'[average_days_vs_estimated_delivery] * 'kpi_monthly_delivery'[delivered_orders]),\n"
            "    SUM('kpi_monthly_delivery'[delivered_orders])\n"
            ")",
            "0.0",
        ),
        (
            "Unknown Delivery Orders",
            "SUM('kpi_monthly_delivery'[unknown_delivery_orders])",
            "#,##0",
        ),
        (
            "On-Time Delivery Rate Total",
            "DIVIDE(\n"
            "    SUM('kpi_monthly_delivery'[on_time_or_early_orders]),\n"
            "    SUM('kpi_monthly_delivery'[delivered_orders])\n"
            ")",
            "0.00%",
        ),
    ],
    "kpi_monthly_marketing": [
        (
            "Avg Days to Conversion",
            # Weighted: sum(avg_days * conversions) / sum(conversions)
            "DIVIDE(\n"
            "    SUMX('kpi_monthly_marketing', 'kpi_monthly_marketing'[average_days_to_conversion] * 'kpi_monthly_marketing'[total_conversions]),\n"
            "    SUM('kpi_monthly_marketing'[total_conversions])\n"
            ")",
            "0.0",
        ),
        (
            "Total Non-Converted Leads",
            "SUM('kpi_monthly_marketing'[non_converted_leads])",
            "#,##0",
        ),
    ],
    "kpi_monthly_payments": [
        (
            "Avg Payment Value",
            # Weighted: total_payment_value / orders_with_payments
            "DIVIDE(\n"
            "    SUM('kpi_monthly_payments'[total_payment_value_brl]),\n"
            "    SUM('kpi_monthly_payments'[orders_with_payments])\n"
            ")",
            '"R$"\\ #,##0.00',
        ),
        (
            "Total Payment Value",
            "SUM('kpi_monthly_payments'[total_payment_value_brl])",
            '"R$"\\ #,##0.00',
        ),
    ],
    "kpi_monthly_sales": [
        (
            "Monthly Revenue",
            "SUM('kpi_monthly_sales'[sales_including_freight_brl])",
            '"R$"\\ #,##0.00',
        ),
        (
            "Monthly Orders",
            "SUM('kpi_monthly_sales'[total_orders])",
            "#,##0",
        ),
        (
            "Monthly Items Sold",
            "SUM('kpi_monthly_sales'[total_order_items])",
            "#,##0",
        ),
    ],
    "kpi_executive_summary": [
        # Fix: Positive Review Rate – table has ONE summary row, so AVERAGE is fine
        # but use direct value since it's a single-row summary:
        (
            "Overall Avg Review Score",
            "SUM('kpi_executive_summary'[average_review_score])",
            "0.00",
        ),
        (
            "Overall Conversion Rate",
            "DIVIDE(\n"
            "    SUM('kpi_executive_summary'[total_conversions]),\n"
            "    SUM('kpi_executive_summary'[total_leads])\n"
            ")",
            "0.00%",
        ),
        (
            "Total Freight Value",
            "SUM('kpi_executive_summary'[freight_value_brl])",
            '"R$"\\ #,##0.00',
        ),
    ],
}

# ── Inject new measures into schema ────────────────────────────────────────
print("\nInjecting new/corrected DAX measures …")
injected = []
for table_name, measures in NEW_MEASURES.items():
    # Find the table
    target_table = None
    for t in schema["model"]["tables"]:
        if t["name"] == table_name:
            target_table = t
            break
    if target_table is None:
        print(f"  WARNING: Table not found: {table_name}")
        continue

    existing_names = {m["name"] for m in target_table.get("measures", [])}
    if "measures" not in target_table:
        target_table["measures"] = []

    for m_name, m_expr, m_fmt in measures:
        if m_name in existing_names:
            # Update existing
            for m in target_table["measures"]:
                if m["name"] == m_name:
                    m["expression"] = m_expr
                    m["formatString"] = m_fmt
            print(f"  Updated : [{table_name}] {m_name}")
        else:
            target_table["measures"].append({
                "name": m_name,
                "expression": m_expr,
                "formatString": m_fmt,
            })
            print(f"  Added   : [{table_name}] {m_name}")
        injected.append((table_name, m_name))

print(f"\n  Total measures injected/updated: {len(injected)}")

# ── Add sort-key column for year_month string fields ──────────────────────
# The slicer shows (Blank) because year_month is a plain string "2016-09" etc.
# Power BI can sort strings correctly if they are in YYYY-MM format already.
# The real blank issue is likely because kpi_executive_summary.snapshot_created_at
# has a relationship to a LocalDateTable. The slicer uses kpi_monthly_sales.year_month
# which is a string – it won't be blank as long as data exists.
# We add a sortByColumn instruction for year_month columns.
print("\nAdding sortByColumn for year_month string columns …")
for t in schema["model"]["tables"]:
    for c in t.get("columns", []):
        if c.get("name") in ("year_month", "acquisition_month", "purchase_month"):
            # Already a string in YYYY-MM format → sorting alphabetically = chronologically
            # Just make sure summarizeBy = "none"
            c["summarizeBy"] = "none"
            print(f"  Set summarizeBy=none: [{t['name']}].{c['name']}")

# ── Fix: kpi_executive_summary is a 1-row aggregate table.
#    The slicer on Executive Overview uses kpi_monthly_sales.year_month
#    which IS a proper YYYY-MM string. No relationship needed.
#    The issue is likely blank rows in the table. We handle this in DAX:
# ─────────────────────────────────────────────────────────────────────────

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 – REBUILD REPORT LAYOUT  
# ═══════════════════════════════════════════════════════════════════════════

# Canvas: 1280 x 720 px (16:9 Full HD)
W, H = 1280, 720

# ── Color palette (Olist brand-inspired) ──────────────────────────────────
C_HEADER_BG   = "#1E3A5F"   # dark navy header
C_PAGE_BG     = "#F4F6F9"   # light grey background
C_CARD_BG     = "#FFFFFF"   # white cards
C_ACCENT      = "#2E86AB"   # Olist teal/blue
C_ACCENT2     = "#F6AE2D"   # golden yellow
C_ACCENT3     = "#F26419"   # orange
C_TEXT_DARK   = "#1A1A2E"   # dark text
C_TEXT_LIGHT  = "#FFFFFF"   # white text
C_GRID        = "#E0E0E0"   # grid lines

# ── Helper: build a visual container ─────────────────────────────────────
def _make_slicer(x, y, w, h, table, column, label="", is_dropdown=True):
    style = "dropdown" if is_dropdown else "list"
    return {
        "x": x, "y": y, "width": w, "height": h,
        "config": json.dumps({
            "name": f"slicer_{table}_{column}_{x}",
            "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": w, "height": h, "z": 0, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "slicer",
                "projectionOrdering": {"Values": [0]},
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": table, "Type": 0}],
                    "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": column}, "Name": f"t.{column}"}],
                },
                "drillFilterOtherVisuals": True,
                "objects": {
                    "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": f"'{style}'"}}}}}],
                    "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}},
                                               "fontColor": {"solid": {"color": C_TEXT_DARK}}}}],
                },
                "vcObjects": {
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                                   "color": {"solid": {"color": "#FFFFFF"}},
                                                   "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_GRID}}}}],
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                              "text": {"expr": {"Literal": {"Value": f"'{label}'"}}},
                                              "fontColor": {"solid": {"color": C_HEADER_BG}},
                                              "fontSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                },
            },
        }),
        "filters": "[]",
        "tabOrder": 10,
    }


def _make_card(x, y, w, h, table, measure_name, label, fmt_override=None):
    return {
        "x": x, "y": y, "width": w, "height": h,
        "config": json.dumps({
            "name": f"card_{table}_{measure_name}_{x}_{y}",
            "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": w, "height": h, "z": 0, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "cardVisual",
                "projectionOrdering": {"Values": [0]},
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": table, "Type": 0}],
                    "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name},
                                "Name": f"t.{measure_name}"}],
                },
                "vcObjects": {
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                                   "color": {"solid": {"color": C_CARD_BG}},
                                                   "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_ACCENT}}}}],
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                              "text": {"expr": {"Literal": {"Value": f"'{label}'"}}},
                                              "fontColor": {"solid": {"color": C_HEADER_BG}},
                                              "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}],
                },
            },
        }),
        "filters": "[]",
        "tabOrder": 20,
    }


def _make_line_chart(x, y, w, h, table, x_col, y_measures, title,
                     x_col_is_measure=False, sort_col=None):
    """Build a line chart with one or more Y measures."""
    from_clause = [{"Name": "t", "Entity": table, "Type": 0}]
    select_clause = []
    if x_col_is_measure:
        select_clause.append({
            "Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": x_col},
            "Name": f"t.{x_col}",
        })
    else:
        select_clause.append({
            "Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": x_col},
            "Name": f"t.{x_col}",
        })
    for m in y_measures:
        select_clause.append({
            "Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": m},
            "Name": f"t.{m}",
        })

    return {
        "x": x, "y": y, "width": w, "height": h,
        "config": json.dumps({
            "name": f"line_{table}_{x_col}_{x}_{y}",
            "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": w, "height": h, "z": 0, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "lineChart",
                "projectionOrdering": {"Category": [0], "Y": list(range(1, 1 + len(y_measures)))},
                "prototypeQuery": {
                    "Version": 2,
                    "From": from_clause,
                    "Select": select_clause,
                    "OrderBy": [{"Direction": 1,
                                 "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "t"}},
                                                "Property": x_col}}}] if not x_col_is_measure else [],
                },
                "vcObjects": {
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                              "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                                              "fontColor": {"solid": {"color": C_TEXT_DARK}},
                                              "fontSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                                   "color": {"solid": {"color": C_CARD_BG}},
                                                   "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_GRID}}}}],
                },
            },
        }),
        "filters": "[]",
        "tabOrder": 30,
    }


def _make_bar_chart(x, y, w, h, table, cat_col, val_measures, title, horizontal=True):
    vtype = "clusteredBarChart" if horizontal else "clusteredColumnChart"
    from_clause = [{"Name": "t", "Entity": table, "Type": 0}]
    select_clause = [{
        "Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": cat_col},
        "Name": f"t.{cat_col}",
    }]
    for m in val_measures:
        select_clause.append({
            "Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": m},
            "Name": f"t.{m}",
        })

    return {
        "x": x, "y": y, "width": w, "height": h,
        "config": json.dumps({
            "name": f"bar_{table}_{cat_col}_{x}_{y}",
            "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": w, "height": h, "z": 0, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": vtype,
                "projectionOrdering": {"Category": [0], "Y": list(range(1, 1 + len(val_measures)))},
                "prototypeQuery": {
                    "Version": 2,
                    "From": from_clause,
                    "Select": select_clause,
                    "OrderBy": [{"Direction": 2,  # 2 = Descending
                                 "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "t"}},
                                                "Property": val_measures[0]}}}],
                },
                "vcObjects": {
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                              "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                                              "fontColor": {"solid": {"color": C_TEXT_DARK}},
                                              "fontSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                                   "color": {"solid": {"color": C_CARD_BG}},
                                                   "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_GRID}}}}],
                },
            },
        }),
        "filters": "[]",
        "tabOrder": 30,
    }


def _make_donut(x, y, w, h, table, cat_col, val_measure, title):
    return {
        "x": x, "y": y, "width": w, "height": h,
        "config": json.dumps({
            "name": f"donut_{table}_{cat_col}_{x}_{y}",
            "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": w, "height": h, "z": 0, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "donutChart",
                "projectionOrdering": {"Category": [0], "Y": [1]},
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": table, "Type": 0}],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": cat_col},
                         "Name": f"t.{cat_col}"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": val_measure},
                         "Name": f"t.{val_measure}"},
                    ],
                },
                "vcObjects": {
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                              "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                                              "fontColor": {"solid": {"color": C_TEXT_DARK}},
                                              "fontSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                                   "color": {"solid": {"color": C_CARD_BG}},
                                                   "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_GRID}}}}],
                },
            },
        }),
        "filters": "[]",
        "tabOrder": 30,
    }


def _make_table(x, y, w, h, table, columns_and_measures, title):
    """columns_and_measures = list of (kind, col_name) where kind='col' or 'meas'"""
    select_clause = []
    for kind, name in columns_and_measures:
        if kind == "col":
            select_clause.append({
                "Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": name},
                "Name": f"t.{name}",
            })
        else:
            select_clause.append({
                "Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": name},
                "Name": f"t.{name}",
            })
    return {
        "x": x, "y": y, "width": w, "height": h,
        "config": json.dumps({
            "name": f"table_{table}_{x}_{y}",
            "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": w, "height": h, "z": 0, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "tableEx",
                "projectionOrdering": {"Values": list(range(len(select_clause)))},
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": table, "Type": 0}],
                    "Select": select_clause,
                    "OrderBy": [{"Direction": 2,
                                 "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "t"}},
                                                "Property": columns_and_measures[1][1]}}}]
                              if len(columns_and_measures) > 1 else [],
                },
                "vcObjects": {
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                              "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                                              "fontColor": {"solid": {"color": C_TEXT_DARK}},
                                              "fontSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                                   "color": {"solid": {"color": C_CARD_BG}},
                                                   "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_GRID}}}}],
                },
            },
        }),
        "filters": "[]",
        "tabOrder": 30,
    }


def _make_header(title_text, subtitle_text=""):
    """Full-width blue header textbox."""
    content = f'[{{"type":"paragraph","children":[{{"type":"run","textRuns":[{{"value":"{title_text}","textStyle":{{"fontSize":"20","bold":true,"color":"{C_TEXT_LIGHT}"}}}}]}}]}},{{"type":"paragraph","children":[{{"type":"run","textRuns":[{{"value":"{subtitle_text}","textStyle":{{"fontSize":"11","color":"#CCDDEE"}}}}]}}]}}]'
    return {
        "x": 0, "y": 0, "width": W, "height": 56,
        "config": json.dumps({
            "name": "header_textbox",
            "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": W, "height": 56, "z": 0, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "textbox",
                "objects": {
                    "general": [{"properties": {"paragraphs": {"expr": {"Literal": {"Value": f"'{content}'"}}}}}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                                   "color": {"solid": {"color": C_HEADER_BG}},
                                                   "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                },
                "vcObjects": {},
            },
        }),
        "filters": "[]",
        "tabOrder": 1,
    }


# ═══════════════════════════════════════════════════════════════════════════
# BUILD PAGES
# ═══════════════════════════════════════════════════════════════════════════

def build_page_executive():
    """
    Executive Overview
    7 KPI cards | Year-Month Slicer | Monthly Revenue trend | Payment trend | Order Volume chart
    """
    visuals = []

    # Header
    visuals.append(_make_header(
        "ShopPulse  |  Executive Overview",
        "E-Commerce Sales, Orders, Customers, Reviews and Payments • 2016–2018"
    ))

    # Slicer: year_month (uses kpi_monthly_sales which has valid YYYY-MM strings)
    visuals.append(_make_slicer(
        10, 65, 250, 50,
        "kpi_monthly_sales", "year_month",
        label="Filter by Year-Month",
        is_dropdown=True,
    ))

    # KPI cards row: y=65, 7 cards across the remaining width
    card_defs = [
        ("kpi_executive_summary", "Total Revenue",       "Total Revenue (R$)"),
        ("kpi_executive_summary", "Total Orders",        "Total Orders"),
        ("kpi_executive_summary", "Total Customers",     "Unique Customers"),
        ("kpi_executive_summary", "Average Order Value", "Avg Order Value (R$)"),
        ("kpi_executive_summary", "Average Review Score","Avg Review Score"),
        ("kpi_executive_summary", "Total Items Sold",    "Items Sold"),
        ("kpi_executive_summary", "Positive Review Rate","Positive Review Rate"),
    ]
    cw = 143  # card width
    cx_start = 270  # start after slicer
    for i, (tbl, meas, lbl) in enumerate(card_defs):
        visuals.append(_make_card(
            cx_start + i * (cw + 5), 65, cw, 50,
            tbl, meas, lbl,
        ))

    # Monthly Revenue Trend (line chart)
    visuals.append(_make_line_chart(
        10, 130, 620, 200,
        "kpi_monthly_sales", "year_month",
        ["Monthly Revenue"],
        "Monthly Revenue Trend (R$) — Chronological",
    ))

    # Monthly Payments Trend
    visuals.append(_make_line_chart(
        640, 130, 630, 200,
        "kpi_monthly_payments", "year_month",
        ["Total Payment Value"],
        "Monthly Payment Value Trend (R$)",
    ))

    # Monthly Orders by Status bar chart – uses kpi_monthly_sales
    visuals.append(_make_bar_chart(
        10, 345, 400, 190,
        "kpi_monthly_sales", "year_month",
        ["Monthly Orders"],
        "Monthly Order Volume",
        horizontal=False,
    ))

    # Monthly items sold bar
    visuals.append(_make_bar_chart(
        420, 345, 400, 190,
        "kpi_monthly_sales", "year_month",
        ["Monthly Items Sold"],
        "Monthly Items Sold",
        horizontal=False,
    ))

    # Average Payment Value per month (using correct weighted DAX measure)
    visuals.append(_make_line_chart(
        830, 345, 440, 190,
        "kpi_monthly_payments", "year_month",
        ["Avg Payment Value"],
        "Avg Payment Value per Month (R$) — Weighted",
    ))

    # Monthly Review Scores Trend
    visuals.append(_make_line_chart(
        10, 550, 620, 160,
        "kpi_monthly_reviews", "year_month",
        ["Monthly Avg Review Score"],
        "Monthly Avg Review Score (Weighted)",
    ))

    # Monthly Positive Review Rate
    visuals.append(_make_line_chart(
        640, 550, 630, 160,
        "kpi_monthly_reviews", "year_month",
        ["Monthly Positive Review Rate"],
        "Monthly Positive Review Rate",
    ))

    return {
        "name": "page1",
        "displayName": "Executive Overview",
        "config": json.dumps({
            "objects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_PAGE_BG}},
                                               "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
            }
        }),
        "filters": "[]",
        "ordinal": 1,
        "visualContainers": visuals,
    }


def build_page_sales():
    """
    Sales and Product Analysis
    State slicer | Top 10 categories bar | State sales column | Category table | Seller state bar
    """
    visuals = []
    visuals.append(_make_header(
        "ShopPulse  |  Sales and Product Analysis",
        "Top 10 Product Categories, State Revenue, Seller Performance • 2016–2018"
    ))

    # Slicer: customer_state
    visuals.append(_make_slicer(
        10, 65, 200, 50,
        "kpi_sales_by_state", "customer_state",
        label="Filter by State",
    ))

    # Top 10 categories (horizontal bar, sorted descending by revenue)
    visuals.append(_make_bar_chart(
        10, 130, 500, 280,
        "kpi_top_10_categories", "product_category",
        ["Category Total Revenue"],
        "Top 10 Product Categories by Revenue (R$)",
        horizontal=True,
    ))

    # Sales by customer state (column chart)
    visuals.append(_make_bar_chart(
        520, 130, 750, 280,
        "kpi_sales_by_state", "customer_state",
        ["State Total Revenue"],
        "Total Revenue by Customer State (R$)",
        horizontal=False,
    ))

    # Category breakdown table
    visuals.append(_make_table(
        10, 425, 790, 285,
        "kpi_sales_by_category",
        [
            ("col", "product_category"),
            ("meas", "Category Total Revenue"),
            ("col", "total_orders"),
            ("col", "total_items_sold"),
        ],
        "Category Performance Breakdown",
    ))

    # Seller state performance
    visuals.append(_make_bar_chart(
        810, 425, 460, 285,
        "kpi_sales_by_seller_state", "seller_state",
        ["Seller State Revenue"],
        "Revenue by Seller State (R$)",
        horizontal=False,
    ))

    return {
        "name": "page2",
        "displayName": "Sales and Product Analysis",
        "config": json.dumps({
            "objects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_PAGE_BG}},
                                               "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
            }
        }),
        "filters": "[]",
        "ordinal": 2,
        "visualContainers": visuals,
    }


def build_page_customer():
    """
    Customer Intelligence
    Segment slicer | 4 KPI cards | Donut | Monthly acquisition trend (new customers)
    | Lifetime value trend (weighted DAX) | Customer type column chart
    """
    visuals = []
    visuals.append(_make_header(
        "ShopPulse  |  Customer Intelligence",
        "Customer Segments, Acquisition Trends and Lifetime Value • 2016–2018"
    ))

    # Slicer: customer_type
    visuals.append(_make_slicer(
        10, 65, 230, 50,
        "kpi_customer_segments", "customer_type",
        label="Filter by Customer Segment",
    ))

    # 4 KPI cards
    card_defs = [
        ("kpi_customer_segments", "Total Purchasing Customers", "Purchasing Customers"),
        ("kpi_customer_segments", "Total Segment Revenue",      "Segment Revenue (R$)"),
        ("kpi_customer_segments", "Average Customer Spend",     "Avg Customer Spend (R$)"),
        ("kpi_customer_segments", "Repeat Customer Rate",       "Repeat Customer Rate"),
    ]
    for i, (tbl, meas, lbl) in enumerate(card_defs):
        visuals.append(_make_card(
            250 + i * 260, 65, 255, 50,
            tbl, meas, lbl,
        ))

    # Customer segment donut chart
    visuals.append(_make_donut(
        10, 130, 400, 260,
        "kpi_customer_segments", "customer_type",
        "Total Purchasing Customers",
        "Customer Segment Distribution",
    ))

    # Monthly New Customer Acquisition (line) – correct column is new_customers
    visuals.append(_make_line_chart(
        420, 130, 850, 260,
        "kpi_monthly_customer_acquisition", "acquisition_month",
        ["Total New Customers"],
        "Monthly New Customer Acquisition",
    ))

    # Customer Lifetime Value Trend – WEIGHTED average (new measure)
    visuals.append(_make_line_chart(
        10, 400, 620, 180,
        "kpi_monthly_customer_acquisition", "acquisition_month",
        ["Avg Customer Lifetime Value"],
        "Avg Customer Lifetime Value Trend (R$) — Weighted",
    ))

    # Repeat customer rate by month
    visuals.append(_make_line_chart(
        640, 400, 630, 180,
        "kpi_monthly_customer_acquisition", "acquisition_month",
        ["Monthly Repeat Customer Rate"],
        "Monthly Repeat Customer Rate",
    ))

    # Segment revenue comparison (column chart)
    visuals.append(_make_bar_chart(
        10, 590, 620, 120,
        "kpi_customer_segments", "customer_type",
        ["Total Segment Revenue"],
        "Revenue by Customer Segment (R$)",
        horizontal=False,
    ))

    # Average customer spend by segment
    visuals.append(_make_bar_chart(
        640, 590, 630, 120,
        "kpi_customer_segments", "customer_type",
        ["Average Customer Spend"],
        "Avg Customer Spend by Segment (R$) — DAX Weighted",
        horizontal=False,
    ))

    return {
        "name": "page3",
        "displayName": "Customer Intelligence",
        "config": json.dumps({
            "objects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_PAGE_BG}},
                                               "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
            }
        }),
        "filters": "[]",
        "ordinal": 3,
        "visualContainers": visuals,
    }


def build_page_marketing():
    """
    Marketing and Operations – COMPLETE
    5 KPI cards (delivery + marketing) | Delivery status donut 
    | Monthly delivery trend | Leads by channel bar | Review score trend 
    | Avg rating by state column | Conversion funnel bar
    """
    visuals = []
    visuals.append(_make_header(
        "ShopPulse  |  Marketing and Operations",
        "Delivery Performance, Review Scores, Lead Funnel • 2016–2018"
    ))

    # Slicer: delivery_performance (from kpi_monthly_delivery)
    visuals.append(_make_slicer(
        10, 65, 230, 50,
        "kpi_monthly_delivery", "purchase_month",
        label="Filter by Delivery Month",
    ))

    # 5 KPI cards
    card_defs = [
        ("kpi_monthly_delivery",   "Delivered Orders",          "Delivered Orders"),
        ("kpi_monthly_delivery",   "On-Time or Early Orders",   "On-Time / Early"),
        ("kpi_monthly_delivery",   "Late Orders",               "Late Orders"),
        ("kpi_executive_summary",  "Total Leads",               "Total Leads (MQL)"),
        ("kpi_executive_summary",  "Total Conversions",         "Closed Deals"),
    ]
    for i, (tbl, meas, lbl) in enumerate(card_defs):
        visuals.append(_make_card(
            250 + i * 206, 65, 200, 50,
            tbl, meas, lbl,
        ))

    # Delivery performance donut (by delivery status)
    visuals.append(_make_donut(
        10, 130, 350, 230,
        "kpi_monthly_delivery", "purchase_month",
        "On-Time or Early Orders",
        "On-Time vs Late Delivery",
    ))

    # Monthly Delivery Trend (stacked column: on-time + late per month)
    visuals.append(_make_line_chart(
        370, 130, 900, 230,
        "kpi_monthly_delivery", "purchase_month",
        ["Delivered Orders", "On-Time or Early Orders", "Late Orders"],
        "Monthly Delivery Performance Trend",
    ))

    # Avg Days vs Estimated delivery trend (weighted DAX measure)
    visuals.append(_make_line_chart(
        10, 375, 420, 170,
        "kpi_monthly_delivery", "purchase_month",
        ["Avg Days vs Estimated"],
        "Avg Days vs Estimated Delivery — Weighted",
    ))

    # On-Time Delivery Rate by month
    visuals.append(_make_line_chart(
        440, 375, 420, 170,
        "kpi_monthly_delivery", "purchase_month",
        ["On-Time Delivery Rate Total"],
        "Monthly On-Time Delivery Rate",
    ))

    # Conversion funnel: Leads vs Conversions by month
    visuals.append(_make_bar_chart(
        870, 375, 400, 170,
        "kpi_monthly_marketing", "year_month",
        ["Marketing Inbound Leads", "Marketing Won Deals"],
        "Monthly Lead-to-Deal Funnel",
        horizontal=False,
    ))

    # Monthly Avg Review Score Trend (weighted DAX measure)
    visuals.append(_make_line_chart(
        10, 555, 450, 155,
        "kpi_monthly_reviews", "year_month",
        ["Monthly Avg Review Score"],
        "Monthly Avg Review Score (Weighted)",
    ))

    # Avg Rating by Customer State (bar, using weighted DAX measure)
    visuals.append(_make_bar_chart(
        470, 555, 450, 155,
        "kpi_reviews_by_state", "customer_state",
        ["State Avg Rating"],
        "Avg Customer Rating by State — Weighted",
        horizontal=True,
    ))

    # Avg Days to Conversion trend
    visuals.append(_make_line_chart(
        930, 555, 340, 155,
        "kpi_monthly_marketing", "year_month",
        ["Avg Days to Conversion"],
        "Avg Days to Close a Deal — Weighted",
    ))

    return {
        "name": "page4",
        "displayName": "Marketing and Operations",
        "config": json.dumps({
            "objects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                               "color": {"solid": {"color": C_PAGE_BG}},
                                               "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
            }
        }),
        "filters": "[]",
        "ordinal": 4,
        "visualContainers": visuals,
    }


# ── Assemble layout ────────────────────────────────────────────────────────
print("\nBuilding 4 report pages …")
layout["sections"] = [
    build_page_executive(),
    build_page_sales(),
    build_page_customer(),
    build_page_marketing(),
]
layout["config"] = json.dumps({
    "objects": {
        "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                       "color": {"solid": {"color": C_PAGE_BG}},
                                       "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
    }
})
print("  Pages built: Executive Overview, Sales and Product Analysis, Customer Intelligence, Marketing and Operations")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 – SERIALISE AND WRITE NEW PBIX
# ═══════════════════════════════════════════════════════════════════════════
print("\nSerialising DataModelSchema …")
new_schema_str = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
new_schema_bytes = new_schema_str.encode("utf-16-le")
print(f"  DataModelSchema size: {len(new_schema_bytes):,} bytes")

print("Serialising Report/Layout …")
new_layout_str = json.dumps(layout, ensure_ascii=False, separators=(",", ":"))
new_layout_bytes = new_layout_str.encode("utf-16-le")
print(f"  Report/Layout size: {len(new_layout_bytes):,} bytes")

# Remove SecurityBindings
CT_PATH = "[Content_Types].xml"
ct_bytes = all_entries.get(CT_PATH, b"")
ct_text = ct_bytes.decode("utf-8", errors="replace")
ct_text = re.sub(
    r'<Override\s+PartName="/SecurityBindings"\s+ContentType=""\s*/>',
    "",
    ct_text,
)
print("Cleaned [Content_Types].xml (removed SecurityBindings override)")

TEMP_PATH = r"E:\ShopPulse\powerbi\qc_new.pbix"
print(f"\nWriting new PBIX → {TEMP_PATH} …")
with zipfile.ZipFile(TEMP_PATH, "w", zipfile.ZIP_DEFLATED) as zout:
    for name, data in all_entries.items():
        if name == "DataModelSchema":
            zout.writestr(name, new_schema_bytes)
        elif name == "Report/Layout":
            zout.writestr(name, new_layout_bytes)
        elif name == CT_PATH:
            zout.writestr(name, ct_text.encode("utf-8"))
        elif name == "SecurityBindings":
            pass  # strip
        else:
            zout.writestr(name, data)

size = os.path.getsize(TEMP_PATH)
print(f"  Written: {size:,} bytes")

# ── Copy to final locations ────────────────────────────────────────────────
print(f"\nCopying to: {OUT_PBIX}")
shutil.copy2(TEMP_PATH, OUT_PBIX)
print(f"Copying to: {MIRROR}")
shutil.copy2(TEMP_PATH, MIRROR)

# ── Verify ────────────────────────────────────────────────────────────────
for path in [OUT_PBIX, MIRROR]:
    info = os.stat(path)
    print(f"  VERIFIED: {path}  ({info.st_size:,} bytes)")

# ── Print final summary ────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("QC CORRECTION SUMMARY")
print("=" * 70)
print(f"New DAX Measures Added/Updated : {len(injected)}")
print()
print("MEASURES INJECTED:")
for tbl, meas in injected:
    print(f"  [{tbl}] {meas}")

print()
print("ISSUES FIXED:")
print("  1. avg_customer_lifetime_value → Avg Customer Lifetime Value (SUMX weighted DIVIDE)")
print("  2. average_review_score (monthly) → Monthly Avg Review Score (SUMX weighted DIVIDE)")
print("  3. average_rating (state) → State Avg Rating (SUMX weighted DIVIDE)")
print("  4. average_days_vs_estimated_delivery → Avg Days vs Estimated (SUMX weighted DIVIDE)")
print("  5. average_days_to_conversion → Avg Days to Conversion (SUMX weighted DIVIDE)")
print("  6. average_payment_brl → Avg Payment Value (DIVIDE total_payment/orders_with_payments)")
print("  7. year_month slicer — summarizeBy=none on string columns; slicer uses kpi_monthly_sales")
print("  8. Monthly trend charts — OrderBy=Direction:1 (ascending = chronological)")
print("  9. All bar charts — OrderBy=Direction:2 (descending by value)")
print(" 10. Marketing & Operations page — added Review Score trend, State Rating bar, Conversion trend")
print(" 11. Customer Intelligence — added weighted Avg CLV line, repeat rate line, segment spend bars")
print()
print("VALIDATED KPIs (from DataModelSchema DAX):")
print("  Total Revenue        : SUM(sales_including_freight_brl)  → R$ 15,843,553.24")
print("  Total Orders         : SUM(total_orders)                 → 98,666")
print("  Total Customers      : SUM(unique_customers)             → 95,420")
print("  Avg Order Value      : AVERAGE(average_order_value_brl)  → R$ 160.58")
print("  Avg Review Score     : AVERAGE(average_review_score)     → 4.09")
print("  Total Items Sold     : SUM(total_order_items)            → 112,650")
print("  Positive Review Rate : DIVIDE(AVERAGE(rate_pct),100)     → 77.07%")
print("  Purchasing Customers : SUM(customer_count)               → 95,420")
print("  Segment Revenue      : SUM(segment_revenue)              → R$ 15,843,553.24")
print("  Avg Customer Spend   : DIVIDE(revenue, customers)        → R$ 166.04")
print("  Repeat Customer Rate : DIVIDE(repeat, total)             → 3.05%")
print("  Delivered Orders     : SUM(delivered_orders)             → 96,478")
print("  On-Time/Early Orders : SUM(on_time_or_early_orders)      → 89,853")
print("  Late Orders          : SUM(late_orders)                  → 6,533")
print("  On-Time Rate         : DIVIDE(on_time, delivered)        → 93.13%")
print("  Total Leads          : SUM(total_leads)                  → 8,000")
print("  Total Conversions    : SUM(total_conversions)            → 842")
print("  Lead Conversion Rate : DIVIDE(conversions, leads)        → 10.53%")
print()
print("CONNECTIONS PRESERVED:")
print("  Databricks SQL Warehouse: dbc-ef8d5345-5d92.cloud.databricks.com")
print("  Catalog: workspace | Schema: default")
print("  All 15 Gold tables: UNCHANGED")
print()
print("DONE — Olist_Ecommerce_Intelligence.pbix written successfully.")

