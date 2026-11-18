"""
ShopPulse - Power BI Dashboard Refinement & DAX Measure Injector
================================================================
Updates Olist_Ecommerce_Intelligence.pbix:
1. Injects explicit DAX measures into DataModelSchema:
   - Total Revenue, Total Orders, Total Customers, AOV, Avg Review Score, Items Sold, Positive Review Rate
   - Average Customer Spend (DIVIDE segment_revenue by customer_count = R$ 166.04)
   - Total Purchasing Customers (95,420), One-time (92,507), Repeat (2,913), Repeat Rate (3.05%)
   - Delivered Orders (96,478), On-time (89,853), Late Orders (6,533), Delivery Rate (93.13%)
   - Marketing Leads (8,000), Conversions (842), Conversion Rate (10.53%)
2. Reconstructs all 4 pages in Report/Layout with:
   - Professional titles & card callout names (no "Sum of...")
   - Proper BRL, percentage, and whole-number formatting
   - Correct sorting (chronological for monthly trends, descending for rankings)
   - Interactive Slicers on all 4 pages
   - Professional 16:9 Full HD canvas with dark navy headers and fluent styling
"""

import zipfile
import json
import uuid
import re
from pathlib import Path

PBIX_PATH = Path("E:/ShopPulse/powerbi/Olist_Ecommerce_Intelligence.pbix")
BACKUP_PATH = Path("E:/ShopPulse/powerbi/Olist_Ecommerce_Intelligence_backup.pbix")

def uid():
    return uuid.uuid4().hex[:20]

# =============================================================================
# 1. DEFINE MEASURES FOR DATAMODELSCHEMA
# =============================================================================

MEASURES_BY_TABLE = {
    "kpi_executive_summary": [
        {
            "name": "Total Revenue",
            "expression": "SUM('kpi_executive_summary'[sales_including_freight_brl])",
            "formatString": "\"R$\"\\ #,##0.00;-\"R$\"\\ #,##0.00;\"R$\"\\ 0.00"
        },
        {
            "name": "Total Orders",
            "expression": "SUM('kpi_executive_summary'[total_orders])",
            "formatString": "#,##0"
        },
        {
            "name": "Total Customers",
            "expression": "SUM('kpi_executive_summary'[unique_customers])",
            "formatString": "#,##0"
        },
        {
            "name": "Average Order Value",
            "expression": "AVERAGE('kpi_executive_summary'[average_order_value_brl])",
            "formatString": "\"R$\"\\ #,##0.00;-\"R$\"\\ #,##0.00;\"R$\"\\ 0.00"
        },
        {
            "name": "Average Review Score",
            "expression": "AVERAGE('kpi_executive_summary'[average_review_score])",
            "formatString": "0.00"
        },
        {
            "name": "Total Items Sold",
            "expression": "SUM('kpi_executive_summary'[total_order_items])",
            "formatString": "#,##0"
        },
        {
            "name": "Positive Review Rate",
            "expression": "DIVIDE(AVERAGE('kpi_executive_summary'[positive_review_rate_pct]), 100)",
            "formatString": "0.00%"
        },
        {
            "name": "Total Leads",
            "expression": "SUM('kpi_executive_summary'[total_leads])",
            "formatString": "#,##0"
        },
        {
            "name": "Total Conversions",
            "expression": "SUM('kpi_executive_summary'[total_conversions])",
            "formatString": "#,##0"
        },
        {
            "name": "Lead Conversion Rate",
            "expression": "DIVIDE(SUM('kpi_executive_summary'[total_conversions]), SUM('kpi_executive_summary'[total_leads]))",
            "formatString": "0.00%"
        }
    ],
    "kpi_customer_segments": [
        {
            "name": "Total Purchasing Customers",
            "expression": "SUM('kpi_customer_segments'[customer_count])",
            "formatString": "#,##0"
        },
        {
            "name": "Total Segment Revenue",
            "expression": "SUM('kpi_customer_segments'[segment_revenue])",
            "formatString": "\"R$\"\\ #,##0.00;-\"R$\"\\ #,##0.00;\"R$\"\\ 0.00"
        },
        {
            "name": "Average Customer Spend",
            "expression": "DIVIDE(SUM('kpi_customer_segments'[segment_revenue]), SUM('kpi_customer_segments'[customer_count]))",
            "formatString": "\"R$\"\\ #,##0.00;-\"R$\"\\ #,##0.00;\"R$\"\\ 0.00"
        },
        {
            "name": "One-Time Customers",
            "expression": "CALCULATE(SUM('kpi_customer_segments'[customer_count]), 'kpi_customer_segments'[customer_type] = \"one_time_customer\")",
            "formatString": "#,##0"
        },
        {
            "name": "Repeat Customers",
            "expression": "CALCULATE(SUM('kpi_customer_segments'[customer_count]), 'kpi_customer_segments'[customer_type] = \"repeat_customer\")",
            "formatString": "#,##0"
        },
        {
            "name": "Repeat Customer Rate",
            "expression": "DIVIDE(CALCULATE(SUM('kpi_customer_segments'[customer_count]), 'kpi_customer_segments'[customer_type] = \"repeat_customer\"), SUM('kpi_customer_segments'[customer_count]))",
            "formatString": "0.00%"
        }
    ],
    "kpi_monthly_delivery": [
        {
            "name": "Delivered Orders",
            "expression": "SUM('kpi_monthly_delivery'[delivered_orders])",
            "formatString": "#,##0"
        },
        {
            "name": "On-Time or Early Orders",
            "expression": "SUM('kpi_monthly_delivery'[on_time_or_early_orders])",
            "formatString": "#,##0"
        },
        {
            "name": "Late Orders",
            "expression": "SUM('kpi_monthly_delivery'[late_orders])",
            "formatString": "#,##0"
        },
        {
            "name": "On-Time Delivery Rate",
            "expression": "DIVIDE(SUM('kpi_monthly_delivery'[on_time_or_early_orders]), SUM('kpi_monthly_delivery'[delivered_orders]))",
            "formatString": "0.00%"
        }
    ],
    "kpi_monthly_marketing": [
        {
            "name": "Marketing Inbound Leads",
            "expression": "SUM('kpi_monthly_marketing'[total_leads])",
            "formatString": "#,##0"
        },
        {
            "name": "Marketing Won Deals",
            "expression": "SUM('kpi_monthly_marketing'[total_conversions])",
            "formatString": "#,##0"
        },
        {
            "name": "Monthly Conversion Rate",
            "expression": "DIVIDE(SUM('kpi_monthly_marketing'[total_conversions]), SUM('kpi_monthly_marketing'[total_leads]))",
            "formatString": "0.00%"
        }
    ],
    "kpi_sales_by_category": [
        {
            "name": "Category Total Revenue",
            "expression": "SUM('kpi_sales_by_category'[total_sales_brl])",
            "formatString": "\"R$\"\\ #,##0.00;-\"R$\"\\ #,##0.00;\"R$\"\\ 0.00"
        }
    ],
    "kpi_sales_by_state": [
        {
            "name": "State Total Revenue",
            "expression": "SUM('kpi_sales_by_state'[total_sales_brl])",
            "formatString": "\"R$\"\\ #,##0.00;-\"R$\"\\ #,##0.00;\"R$\"\\ 0.00"
        }
    ],
    "kpi_sales_by_seller_state": [
        {
            "name": "Seller State Revenue",
            "expression": "SUM('kpi_sales_by_seller_state'[total_sales_brl])",
            "formatString": "\"R$\"\\ #,##0.00;-\"R$\"\\ #,##0.00;\"R$\"\\ 0.00"
        }
    ]
}

def update_datamodel_schema(schema_json):
    """Adds explicit DAX measures to the tables in DataModelSchema."""
    model = schema_json.get("model", {})
    tables = model.get("tables", [])
    
    for t in tables:
        tname = t.get("name")
        if tname in MEASURES_BY_TABLE:
            existing_measures = t.get("measures", [])
            existing_names = {m["name"] for m in existing_measures}
            for m_def in MEASURES_BY_TABLE[tname]:
                if m_def["name"] not in existing_names:
                    m_obj = {
                        "name": m_def["name"],
                        "expression": m_def["expression"],
                        "formatString": m_def["formatString"],
                        "lineageTag": f"lt-{uid()}"
                    }
                    existing_measures.append(m_obj)
            t["measures"] = existing_measures
            print(f"Updated table '{tname}': {len(t['measures'])} measures present.")
    return schema_json

# =============================================================================
# 2. VISUAL BUILDERS WITH EXPLICIT MEASURE SUPPORT
# =============================================================================

def make_measure_card(table, measure_name, display_title, x, y, width, height):
    """Builds a KPI card bound to an explicit DAX measure."""
    guid = uid()
    query_ref = f"{table}.{measure_name}"
    
    config = {
        "name": guid,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "width": width, "height": height, "z": 0, "tabOrder": 0}
        }],
        "singleVisual": {
            "visualType": "cardVisual",
            "projections": {
                "Data": [{"queryRef": query_ref}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "t", "Entity": table, "Type": 0}],
                "Select": [{
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "t"}},
                        "Property": measure_name
                    },
                    "Name": query_ref,
                    "NativeReferenceName": display_title
                }]
            },
            "drillFilterOtherVisuals": True,
            "hasDefaultSort": True
        }
    }
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": config["singleVisual"]["prototypeQuery"],
                "Binding": {"Primary": {"Groupings": [{"Projections": [0]}]}, "Version": 1},
                "ExecutionMetricsKind": 1
            }
        }]
    }
    
    transforms = {
        "projectionOrdering": {"Data": [0]},
        "queryMetadata": {
            "Select": [{"Restatement": display_title, "Name": query_ref, "Type": 1}]
        },
        "visualElements": [{"DataRoles": [{"Name": "Data", "Projection": 0, "isActive": False}]}],
        "selects": [{
            "displayName": display_title,
            "queryName": query_ref,
            "roles": {"Data": True},
            "expr": {
                "Measure": {
                    "Expression": {"SourceRef": {"Entity": table}},
                    "Property": measure_name
                }
            }
        }]
    }

    return {
        "x": x,
        "y": y,
        "z": 0,
        "width": width,
        "height": height,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps(query),
        "dataTransforms": json.dumps(transforms)
    }

def make_chart_visual(visual_type, table, x_col, y_cols, titles, x, y, width, height, chart_title, sort_desc=False, sort_col=None):
    """Builds a Chart visual with explicit sort direction."""
    guid = uid()
    cat_query_ref = f"{table}.{x_col}"
    projections = {
        "Category": [{"queryRef": cat_query_ref}],
        "Y": [{"queryRef": f"Sum({table}.{yc})"} for yc in y_cols]
    }
    
    selects = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "t"}},
            "Property": x_col
        },
        "Name": cat_query_ref,
        "NativeReferenceName": x_col
    }]
    
    for yc, title in zip(y_cols, titles):
        selects.append({
            "Aggregation": {
                "Expression": {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "t"}},
                        "Property": yc
                    }
                },
                "Function": 0
            },
            "Name": f"Sum({table}.{yc})",
            "NativeReferenceName": title
        })
    
    # Sort expression: either category or first value column
    if sort_col:
        order_expr = {
            "Aggregation": {
                "Expression": {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "t"}},
                        "Property": sort_col
                    }
                },
                "Function": 0
            }
        }
    else:
        order_expr = {
            "Column": {
                "Expression": {"SourceRef": {"Source": "t"}},
                "Property": x_col
            }
        }
    
    direction = 2 if sort_desc else 1 # 1 = Ascending, 2 = Descending
    
    proto_query = {
        "Version": 2,
        "From": [{"Name": "t", "Entity": table, "Type": 0}],
        "Select": selects,
        "OrderBy": [{
            "Direction": direction,
            "Expression": order_expr
        }]
    }
    
    config = {
        "name": guid,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "width": width, "height": height, "z": 0, "tabOrder": 0}
        }],
        "singleVisual": {
            "visualType": visual_type,
            "projections": projections,
            "prototypeQuery": proto_query,
            "drillFilterOtherVisuals": True,
            "hasDefaultSort": True
        }
    }
    
    groupings = [{"Projections": [0]}]
    proj_order = {"Category": [0], "Y": list(range(1, 1 + len(y_cols)))}
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": proto_query,
                "Binding": {
                    "Primary": {"Groupings": groupings},
                    "Version": 1
                },
                "ExecutionMetricsKind": 1
            }
        }]
    }
    
    transforms = {
        "projectionOrdering": proj_order,
        "queryMetadata": {
            "Select": [{"Restatement": x_col, "Name": cat_query_ref, "Type": 2048}] +
                      [{"Restatement": t, "Name": f"Sum({table}.{yc})", "Type": 1} for yc, t in zip(y_cols, titles)]
        },
        "visualElements": [
            {"DataRoles": [{"Name": "Category", "Projection": 0, "isActive": False}]}
        ] + [
            {"DataRoles": [{"Name": "Y", "Projection": i + 1, "isActive": False}]} for i in range(len(y_cols))
        ]
    }
    
    return {
        "x": x,
        "y": y,
        "z": 0,
        "width": width,
        "height": height,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps(query),
        "dataTransforms": json.dumps(transforms)
    }

def make_donut_visual(table, cat_col, val_col, val_title, x, y, width, height, chart_title):
    """Builds a Donut Chart."""
    guid = uid()
    cat_query_ref = f"{table}.{cat_col}"
    val_query_ref = f"Sum({table}.{val_col})"
    
    proto_query = {
        "Version": 2,
        "From": [{"Name": "t", "Entity": table, "Type": 0}],
        "Select": [
            {
                "Column": {
                    "Expression": {"SourceRef": {"Source": "t"}},
                    "Property": cat_col
                },
                "Name": cat_query_ref,
                "NativeReferenceName": cat_col
            },
            {
                "Aggregation": {
                    "Expression": {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "t"}},
                            "Property": val_col
                        }
                    },
                    "Function": 0
                },
                "Name": val_query_ref,
                "NativeReferenceName": val_title
            }
        ],
        "OrderBy": [{
            "Direction": 2,
            "Expression": {
                "Aggregation": {
                    "Expression": {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "t"}},
                            "Property": val_col
                        }
                    },
                    "Function": 0
                }
            }
        }]
    }
    
    config = {
        "name": guid,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "width": width, "height": height, "z": 0, "tabOrder": 0}
        }],
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {
                "Category": [{"queryRef": cat_query_ref}],
                "Y": [{"queryRef": val_query_ref}]
            },
            "prototypeQuery": proto_query,
            "drillFilterOtherVisuals": True,
            "hasDefaultSort": True
        }
    }
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": proto_query,
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": [0]}]},
                    "Version": 1
                },
                "ExecutionMetricsKind": 1
            }
        }]
    }
    
    transforms = {
        "projectionOrdering": {"Category": [0], "Y": [1]},
        "queryMetadata": {
            "Select": [
                {"Restatement": cat_col, "Name": cat_query_ref, "Type": 2048},
                {"Restatement": val_title, "Name": val_query_ref, "Type": 1}
            ]
        },
        "visualElements": [
            {"DataRoles": [{"Name": "Category", "Projection": 0, "isActive": False}]},
            {"DataRoles": [{"Name": "Y", "Projection": 1, "isActive": False}]}
        ]
    }
    
    return {
        "x": x,
        "y": y,
        "z": 0,
        "width": width,
        "height": height,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps(query),
        "dataTransforms": json.dumps(transforms)
    }

def make_table_visual(table, cols, titles, x, y, width, height):
    """Builds a formatted Table visual."""
    guid = uid()
    selects = []
    projections = []
    
    for c, t in zip(cols, titles):
        qref = f"{table}.{c}"
        projections.append({"queryRef": qref})
        selects.append({
            "Column": {
                "Expression": {"SourceRef": {"Source": "t"}},
                "Property": c
            },
            "Name": qref,
            "NativeReferenceName": t
        })
    
    proto_query = {
        "Version": 2,
        "From": [{"Name": "t", "Entity": table, "Type": 0}],
        "Select": selects
    }
    
    config = {
        "name": guid,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "width": width, "height": height, "z": 0, "tabOrder": 0}
        }],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {"Values": projections},
            "prototypeQuery": proto_query,
            "drillFilterOtherVisuals": True,
            "hasDefaultSort": True
        }
    }
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": proto_query,
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": list(range(len(cols)))}]},
                    "Version": 1
                },
                "ExecutionMetricsKind": 1
            }
        }]
    }
    
    transforms = {
        "projectionOrdering": {"Values": list(range(len(cols)))},
        "queryMetadata": {
            "Select": [{"Restatement": t, "Name": f"{table}.{c}", "Type": 2048} for c, t in zip(cols, titles)]
        },
        "visualElements": [
            {"DataRoles": [{"Name": "Values", "Projection": i, "isActive": False}]} for i in range(len(cols))
        ]
    }
    
    return {
        "x": x,
        "y": y,
        "z": 0,
        "width": width,
        "height": height,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps(query),
        "dataTransforms": json.dumps(transforms)
    }

def make_slicer_visual(table, column, display_title, x, y, width, height):
    """Builds an interactive Slicer visual."""
    guid = uid()
    query_ref = f"{table}.{column}"
    
    config = {
        "name": guid,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "width": width, "height": height, "z": 0, "tabOrder": 0}
        }],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "t", "Entity": table, "Type": 0}],
                "Select": [{
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "t"}},
                        "Property": column
                    },
                    "Name": query_ref,
                    "NativeReferenceName": display_title
                }],
                "OrderBy": [{
                    "Direction": 1,
                    "Expression": {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "t"}},
                            "Property": column
                        }
                    }
                }]
            },
            "drillFilterOtherVisuals": True,
            "hasDefaultSort": True
        }
    }
    
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": config["singleVisual"]["prototypeQuery"],
                "Binding": {"Primary": {"Groupings": [{"Projections": [0]}]}, "Version": 1},
                "ExecutionMetricsKind": 1
            }
        }]
    }
    
    transforms = {
        "projectionOrdering": {"Values": [0]},
        "queryMetadata": {
            "Select": [{"Restatement": display_title, "Name": query_ref, "Type": 2048}]
        },
        "visualElements": [{"DataRoles": [{"Name": "Values", "Projection": 0, "isActive": False}]}]
    }
    
    return {
        "x": x,
        "y": y,
        "z": 0,
        "width": width,
        "height": height,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps(query),
        "dataTransforms": json.dumps(transforms)
    }

def make_textbox(text, x, y, width, height, font_size=18, is_bold=True):
    """Builds a header banner textbox."""
    guid = uid()
    config = {
        "name": guid,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "width": width, "height": height, "z": 0, "tabOrder": 0}
        }],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": text,
                                "textStyle": {
                                    "fontFamily": "Segoe UI",
                                    "fontSize": f"{font_size}pt",
                                    "fontWeight": "bold" if is_bold else "normal",
                                    "color": "#113A63"
                                }
                            }]
                        }]
                    }
                }]
            }
        }
    }
    return {
        "x": x,
        "y": y,
        "z": 0,
        "width": width,
        "height": height,
        "config": json.dumps(config),
        "filters": "[]"
    }

# =============================================================================
# 3. BUILD ALL 4 PAGES WITH PERFECT KPI MEASURES AND SLICERS
# =============================================================================

def build_refined_sections():
    sections = []

    # -------------------------------------------------------------------------
    # PAGE 1: EXECUTIVE OVERVIEW
    # -------------------------------------------------------------------------
    p1 = []
    p1.append(make_textbox("ShopPulse — Executive Overview & Marketplace Performance", 20, 10, 1055, 45, 18, True))
    p1.append(make_slicer_visual("kpi_monthly_sales", "year_month", "Filter Month", 1090, 10, 170, 48))

    # 7 KPI Cards using Explicit DAX Measures
    # Width=165 each, gap=14 -> 20, 199, 378, 557, 736, 915, 1094
    p1.append(make_measure_card("kpi_executive_summary", "Total Revenue", "Total Revenue", 20, 65, 165, 90))
    p1.append(make_measure_card("kpi_executive_summary", "Total Orders", "Total Orders", 199, 65, 165, 90))
    p1.append(make_measure_card("kpi_executive_summary", "Total Customers", "Total Customers", 378, 65, 165, 90))
    p1.append(make_measure_card("kpi_executive_summary", "Average Order Value", "Average Order Value", 557, 65, 165, 90))
    p1.append(make_measure_card("kpi_executive_summary", "Average Review Score", "Avg Review Score", 736, 65, 165, 90))
    p1.append(make_measure_card("kpi_executive_summary", "Total Items Sold", "Total Items Sold", 915, 65, 165, 90))
    p1.append(make_measure_card("kpi_executive_summary", "Positive Review Rate", "Positive Review Rate", 1094, 65, 165, 90))

    # Charts Row 2 (y=168, h=255)
    # Sorted Ascending by year_month
    p1.append(make_chart_visual("lineChart", "kpi_monthly_sales", "year_month", ["sales_including_freight_brl"], ["Monthly Revenue (BRL)"], 20, 168, 605, 255, "Monthly Sales Trend", sort_desc=False))
    p1.append(make_chart_visual("lineChart", "kpi_monthly_payments", "year_month", ["total_payment_value_brl"], ["Monthly Payment Value (BRL)"], 645, 168, 615, 255, "Monthly Payment Trend", sort_desc=False))

    # Chart Row 3 (y=435, h=270)
    p1.append(make_chart_visual("clusteredColumnChart", "kpi_monthly_sales", "year_month", ["product_sales_brl", "freight_value_brl"], ["Product Sales (BRL)", "Freight Value (BRL)"], 20, 435, 1240, 270, "Revenue Overview: Product Sales vs Freight Breakdown", sort_desc=False))

    sections.append({
        "id": 0,
        "name": "Section_Executive_Overview",
        "displayName": "Executive Overview",
        "filters": "[]",
        "ordinal": 0,
        "width": 1280.0,
        "height": 720.0,
        "visualContainers": p1
    })

    # -------------------------------------------------------------------------
    # PAGE 2: SALES AND PRODUCT ANALYSIS
    # -------------------------------------------------------------------------
    p2 = []
    p2.append(make_textbox("ShopPulse — Sales, Product Category & Geographic Intelligence", 20, 10, 1055, 45, 18, True))
    p2.append(make_slicer_visual("kpi_sales_by_state", "customer_state", "Filter State", 1090, 10, 170, 48))

    # Top-Left: Top 10 Product Categories by Revenue (Sorted DESCENDING by revenue!)
    p2.append(make_chart_visual("clusteredBarChart", "kpi_top_10_categories", "product_category", ["total_sales_brl"], ["Total Sales (BRL)"], 20, 65, 605, 305, "Top 10 Product Categories by Revenue", sort_desc=True, sort_col="total_sales_brl"))

    # Top-Right: Sales Revenue by Customer State (Sorted DESCENDING by revenue!)
    p2.append(make_chart_visual("clusteredColumnChart", "kpi_sales_by_state", "customer_state", ["total_sales_brl"], ["Total Sales (BRL)"], 645, 65, 615, 305, "Sales Revenue by Customer State", sort_desc=True, sort_col="total_sales_brl"))

    # Bottom-Left: Category Performance Details (Table Visual)
    p2.append(make_table_visual("kpi_sales_by_category", ["product_category", "total_sales_brl", "total_orders", "total_items_sold"], ["Product Category", "Revenue (BRL)", "Orders", "Items Sold"], 20, 385, 605, 320))

    # Bottom-Right: Seller Revenue by Merchant State (Sorted DESCENDING by revenue!)
    p2.append(make_chart_visual("clusteredColumnChart", "kpi_sales_by_seller_state", "seller_state", ["total_sales_brl"], ["Seller Sales (BRL)"], 645, 385, 615, 320, "Seller Revenue by Merchant State", sort_desc=True, sort_col="total_sales_brl"))

    sections.append({
        "id": 1,
        "name": "Section_Sales_Product",
        "displayName": "Sales and Product Analysis",
        "filters": "[]",
        "ordinal": 1,
        "width": 1280.0,
        "height": 720.0,
        "visualContainers": p2
    })

    # -------------------------------------------------------------------------
    # PAGE 3: CUSTOMER INTELLIGENCE
    # -------------------------------------------------------------------------
    p3 = []
    p3.append(make_textbox("ShopPulse — Customer Segmentation & Retention Intelligence", 20, 10, 960, 45, 18, True))
    p3.append(make_slicer_visual("kpi_customer_segments", "customer_type", "Filter Customer Segment", 1000, 10, 260, 48))

    # 4 Summary Cards across top (y=65, h=90)
    # Total Purchasing Customers: 95,420
    # Total Segment Revenue: R$ 15,843,553.24
    # Average Customer Spend: R$ 166.04 (Calculated by DAX DIVIDE, NOT sum of averages!)
    # Repeat Customer Rate: 3.05%
    p3.append(make_measure_card("kpi_customer_segments", "Total Purchasing Customers", "Total Purchasing Customers", 20, 65, 290, 90))
    p3.append(make_measure_card("kpi_customer_segments", "Total Segment Revenue", "Total Segment Revenue", 325, 65, 300, 90))
    p3.append(make_measure_card("kpi_customer_segments", "Average Customer Spend", "Average Customer Spend", 640, 65, 320, 90))
    p3.append(make_measure_card("kpi_customer_segments", "Repeat Customer Rate", "Repeat Customer Rate", 975, 65, 285, 90))

    # Middle Row: One-time vs Repeat Donut + Monthly Acquisition Trend (y=168, h=255)
    p3.append(make_donut_visual("kpi_customer_segments", "customer_type", "customer_count", "Customers", 20, 168, 450, 255, "Customer Distribution: One-Time (92,507) vs Repeat (2,913)"))
    p3.append(make_chart_visual("lineChart", "kpi_monthly_customer_acquisition", "acquisition_month", ["new_customers", "repeat_customers"], ["New Customers", "Repeat Customers"], 490, 168, 770, 255, "Monthly Customer Acquisition Trend", sort_desc=False))

    # Bottom Row: Customer Segment Revenue + Customer Lifetime Value (y=435, h=270)
    p3.append(make_chart_visual("clusteredColumnChart", "kpi_customer_segments", "customer_type", ["segment_revenue"], ["Revenue (BRL)"], 20, 435, 450, 270, "Revenue Contribution by Customer Segment", sort_desc=True, sort_col="segment_revenue"))
    p3.append(make_chart_visual("lineChart", "kpi_monthly_customer_acquisition", "acquisition_month", ["avg_customer_lifetime_value"], ["Average CLV (BRL)"], 490, 435, 770, 270, "Average Customer Lifetime Value (CLV) Trend", sort_desc=False))

    sections.append({
        "id": 2,
        "name": "Section_Customer_Intelligence",
        "displayName": "Customer Intelligence",
        "filters": "[]",
        "ordinal": 2,
        "width": 1280.0,
        "height": 720.0,
        "visualContainers": p3
    })

    # -------------------------------------------------------------------------
    # PAGE 4: MARKETING AND OPERATIONS
    # -------------------------------------------------------------------------
    p4 = []
    p4.append(make_textbox("ShopPulse — Operations, Delivery Logistics & Marketing Funnel", 20, 10, 960, 45, 18, True))
    p4.append(make_slicer_visual("fact_orders", "delivery_performance", "Filter Delivery Status", 1000, 10, 260, 48))

    # 5 KPI Cards (y=65, h=90):
    # Delivered Orders: 96,478
    # On-Time or Early Orders: 89,853
    # Late Orders: 6,533
    # Marketing Inbound Leads: 8,000
    # Marketing Won Deals: 842 (10.53% Lead Conversion Rate)
    p4.append(make_measure_card("kpi_monthly_delivery", "Delivered Orders", "Delivered Orders", 20, 65, 230, 90))
    p4.append(make_measure_card("kpi_monthly_delivery", "On-Time or Early Orders", "On-Time / Early Orders", 265, 65, 230, 90))
    p4.append(make_measure_card("kpi_monthly_delivery", "Late Orders", "Late Orders (Delay)", 510, 65, 230, 90))
    p4.append(make_measure_card("kpi_executive_summary", "Total Leads", "Total Marketing Leads", 755, 65, 235, 90))
    p4.append(make_measure_card("kpi_executive_summary", "Total Conversions", "Won Deals (10.53%)", 1005, 65, 255, 90))

    # Middle Row: Delivery Trend + Marketing Funnel (y=168, h=255)
    p4.append(make_chart_visual("clusteredColumnChart", "kpi_monthly_delivery", "purchase_month", ["on_time_or_early_orders", "late_orders"], ["On-Time Orders", "Late Orders"], 20, 168, 605, 255, "Monthly Delivery Performance Trend (On-Time vs Late)", sort_desc=False))
    p4.append(make_chart_visual("clusteredColumnChart", "kpi_monthly_marketing", "year_month", ["total_leads", "total_conversions"], ["Inbound Leads", "Closed Deals"], 645, 168, 615, 255, "Marketing Funnel: Inbound Leads vs Closed Deals", sort_desc=False))

    # Bottom Row: Review Score Trend + Reviews by State (y=435, h=270)
    p4.append(make_chart_visual("lineChart", "kpi_monthly_reviews", "year_month", ["average_review_score"], ["Average Review Score (1-5)"], 20, 435, 605, 270, "Monthly Customer Review Score Trend", sort_desc=False))
    p4.append(make_chart_visual("clusteredColumnChart", "kpi_reviews_by_state", "customer_state", ["average_rating"], ["Average Rating (1-5)"], 645, 435, 615, 270, "Customer Review Satisfaction by State", sort_desc=True, sort_col="average_rating"))

    sections.append({
        "id": 3,
        "name": "Section_Marketing_Operations",
        "displayName": "Marketing and Operations",
        "filters": "[]",
        "ordinal": 3,
        "width": 1280.0,
        "height": 720.0,
        "visualContainers": p4
    })

    return sections

# =============================================================================
# 4. MAIN PACKAGING ROUTINE
# =============================================================================

def execute_refinement():
    print(f"Reading current report package from {PBIX_PATH}...")
    
    with zipfile.ZipFile(PBIX_PATH, "r") as zin:
        # 1. Update DataModelSchema with explicit DAX measures
        schema_raw = zin.read("DataModelSchema")
        schema_json = json.loads(schema_raw.decode("utf-16-le"))
        updated_schema = update_datamodel_schema(schema_json)
        updated_schema_bytes = json.dumps(updated_schema, ensure_ascii=False).encode("utf-16-le")
        
        # 2. Update Report/Layout with new sections & visuals
        layout_raw = zin.read("Report/Layout")
        layout_json = json.loads(layout_raw.decode("utf-16-le"))
        sections = build_refined_sections()
        layout_json["sections"] = sections
        updated_layout_bytes = json.dumps(layout_json, ensure_ascii=False).encode("utf-16-le")
        
        # 3. Write to temporary new pbix file
        temp_pbix = Path("E:/ShopPulse/powerbi/Olist_Ecommerce_Intelligence_new.pbix")
        print(f"Writing updated package to {temp_pbix}...")
        
        with zipfile.ZipFile(temp_pbix, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "SecurityBindings":
                    continue
                content = zin.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    xml_text = content.decode("utf-8")
                    xml_text = re.sub(r'<Override\s+PartName="/SecurityBindings"\s+ContentType=""\s*/>', '', xml_text)
                    content = xml_text.encode("utf-8")
                elif item.filename == "DataModelSchema":
                    content = updated_schema_bytes
                elif item.filename == "Report/Layout":
                    content = updated_layout_bytes
                
                zout.writestr(item.filename, content, compress_type=zipfile.ZIP_DEFLATED)

    # 4. Replace original pbix and root pbix
    print("Replacing original pbix file with refined report...")
    if PBIX_PATH.exists():
        temp_pbix.replace(PBIX_PATH)
    
    # Also copy to project root
    root_copy = Path("E:/ShopPulse/Olist_Ecommerce_Intelligence.pbix")
    with open(PBIX_PATH, "rb") as fsrc, open(root_copy, "wb") as fdst:
        fdst.write(fsrc.read())

    print(f"[SUCCESS] Refined report saved to:\n  - {PBIX_PATH}\n  - {root_copy}")
    print(f"Total sections: {len(sections)}")
    for i, s in enumerate(sections):
        print(f"  Page {i+1}: '{s['displayName']}' with {len(s['visualContainers'])} visuals")

if __name__ == "__main__":
    execute_refinement()

