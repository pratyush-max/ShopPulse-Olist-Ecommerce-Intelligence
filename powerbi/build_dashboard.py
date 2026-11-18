"""
ShopPulse - Power BI Dashboard Generator
========================================
Builds the complete 4-page executive dashboard inside 'Olist_Ecommerce_Intelligence.pbix'
using the verified Gold tables imported from Databricks.

Pages created:
1. EXECUTIVE OVERVIEW (7 KPI cards, monthly sales trend, monthly payment trend, revenue breakdown)
2. SALES AND PRODUCT ANALYSIS (Top 10 categories bar chart, revenue by category table, sales by state, seller state)
3. CUSTOMER INTELLIGENCE (One-time vs repeat distribution, customer segment revenue, acquisition trend, CLV analysis)
4. MARKETING AND OPERATIONS (Delivery performance KPIs, monthly delivery trend, lead conversion rate, reviews analysis)
"""

import zipfile
import json
import uuid
import re
from pathlib import Path

SRC_ZIP = Path("E:/ShopPulse/powerbi/recovered_test.zip")
OUTPUT_PBIX = Path("E:/ShopPulse/powerbi/Olist_Ecommerce_Intelligence.pbix")

def uid():
    return uuid.uuid4().hex[:20]

def make_card_visual(table, column, display_name, x, y, width, height, is_currency=False, is_pct=False):
    guid = uid()
    query_ref = f"Sum({table}.{column})"
    
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
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "t"}},
                                "Property": column
                            }
                        },
                        "Function": 0
                    },
                    "Name": query_ref,
                    "NativeReferenceName": display_name
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
            "Select": [{"Restatement": display_name, "Name": query_ref, "Type": 1}]
        },
        "visualElements": [{"DataRoles": [{"Name": "Data", "Projection": 0, "isActive": False}]}],
        "selects": [{
            "displayName": display_name,
            "queryName": query_ref,
            "roles": {"Data": True},
            "expr": {
                "Aggregation": {
                    "Expression": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": table}},
                            "Property": column
                        }
                    },
                    "Function": 0
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

def make_chart_visual(visual_type, table, x_col, y_cols, titles, x, y, width, height, chart_title):
    guid = uid()
    
    # Projections
    cat_query_ref = f"{table}.{x_col}"
    projections = {
        "Category": [{"queryRef": cat_query_ref}],
        "Y": [{"queryRef": f"Sum({table}.{yc})"} for yc in y_cols]
    }
    
    # Prototype Query
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
    
    proto_query = {
        "Version": 2,
        "From": [{"Name": "t", "Entity": table, "Type": 0}],
        "Select": selects,
        "OrderBy": [{
            "Direction": 1,
            "Expression": {
                "Column": {
                    "Expression": {"SourceRef": {"Source": "t"}},
                    "Property": x_col
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
        ]
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

def make_textbox(text, x, y, width, height, font_size=18, is_bold=True):
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

def build_all_sections():
    sections = []

    # =========================================================================
    # PAGE 1: EXECUTIVE OVERVIEW
    # =========================================================================
    p1_vcs = []
    p1_vcs.append(make_textbox("ShopPulse — Executive Overview & Marketplace Performance", 20, 10, 1240, 45, 18, True))
    
    # 7 KPI Cards (Row 1: y=65, h=90)
    # card w=165, gap=14 -> 20, 199, 378, 557, 736, 915, 1094
    p1_vcs.append(make_card_visual("kpi_executive_summary", "sales_including_freight_brl", "Total Revenue (BRL)", 20, 65, 165, 90, is_currency=True))
    p1_vcs.append(make_card_visual("kpi_executive_summary", "total_orders", "Total Orders", 199, 65, 165, 90))
    p1_vcs.append(make_card_visual("kpi_executive_summary", "unique_customers", "Total Customers", 378, 65, 165, 90))
    p1_vcs.append(make_card_visual("kpi_executive_summary", "average_order_value_brl", "Average Order Value", 557, 65, 165, 90, is_currency=True))
    p1_vcs.append(make_card_visual("kpi_executive_summary", "average_review_score", "Avg Review Score", 736, 65, 165, 90))
    p1_vcs.append(make_card_visual("kpi_executive_summary", "total_order_items", "Total Items Sold", 915, 65, 165, 90))
    p1_vcs.append(make_card_visual("kpi_executive_summary", "positive_review_rate_pct", "Positive Review %", 1094, 65, 165, 90, is_pct=True))

    # Charts Row 2 (y=170, h=250)
    p1_vcs.append(make_chart_visual("lineChart", "kpi_monthly_sales", "year_month", ["sales_including_freight_brl"], ["Monthly Revenue (BRL)"], 20, 170, 605, 250, "Monthly Sales Trend"))
    p1_vcs.append(make_chart_visual("lineChart", "kpi_monthly_payments", "year_month", ["total_payment_value_brl"], ["Monthly Payment Value (BRL)"], 645, 170, 615, 250, "Monthly Payment Trend"))

    # Chart Row 3 (y=435, h=265)
    p1_vcs.append(make_chart_visual("clusteredColumnChart", "kpi_monthly_sales", "year_month", ["product_sales_brl", "freight_value_brl"], ["Product Sales (BRL)", "Freight Value (BRL)"], 20, 435, 1240, 265, "Revenue Overview: Product vs Freight Breakdown"))

    sections.append({
        "id": 0,
        "name": "Section_Executive_Overview",
        "displayName": "EXECUTIVE OVERVIEW",
        "filters": "[]",
        "ordinal": 0,
        "width": 1280.0,
        "height": 720.0,
        "visualContainers": p1_vcs
    })

    # =========================================================================
    # PAGE 2: SALES AND PRODUCT ANALYSIS
    # =========================================================================
    p2_vcs = []
    p2_vcs.append(make_textbox("ShopPulse — Sales, Product Category & Geographic Intelligence", 20, 10, 1240, 45, 18, True))

    # Top-Left: Top 10 categories by revenue (Bar Chart)
    p2_vcs.append(make_chart_visual("clusteredBarChart", "kpi_top_10_categories", "product_category", ["total_sales_brl"], ["Total Sales (BRL)"], 20, 65, 605, 305, "Top 10 Product Categories by Revenue"))

    # Top-Right: Sales by state (Column Chart)
    p2_vcs.append(make_chart_visual("clusteredColumnChart", "kpi_sales_by_state", "customer_state", ["total_sales_brl"], ["Total Sales (BRL)"], 645, 65, 615, 305, "Sales Revenue by Customer State"))

    # Bottom-Left: Revenue by category table
    p2_vcs.append(make_table_visual("kpi_sales_by_category", ["product_category", "total_sales_brl", "total_orders", "total_items_sold"], ["Product Category", "Revenue (BRL)", "Orders", "Items Sold"], 20, 385, 605, 315))

    # Bottom-Right: Seller-state performance
    p2_vcs.append(make_chart_visual("clusteredColumnChart", "kpi_sales_by_seller_state", "seller_state", ["total_sales_brl"], ["Seller Sales (BRL)"], 645, 385, 615, 315, "Seller Revenue by Merchant State"))

    sections.append({
        "id": 1,
        "name": "Section_Sales_Product",
        "displayName": "SALES AND PRODUCT ANALYSIS",
        "filters": "[]",
        "ordinal": 1,
        "width": 1280.0,
        "height": 720.0,
        "visualContainers": p2_vcs
    })

    # =========================================================================
    # PAGE 3: CUSTOMER INTELLIGENCE
    # =========================================================================
    p3_vcs = []
    p3_vcs.append(make_textbox("ShopPulse — Customer Segmentation & Retention Intelligence", 20, 10, 1240, 45, 18, True))

    # 3 Summary Cards (Row 1: y=65, h=85)
    p3_vcs.append(make_card_visual("kpi_customer_segments", "customer_count", "Total Purchasing Customers", 20, 65, 385, 85))
    p3_vcs.append(make_card_visual("kpi_customer_segments", "segment_revenue", "Segment Revenue (BRL)", 425, 65, 395, 85, is_currency=True))
    p3_vcs.append(make_card_visual("kpi_customer_segments", "avg_customer_spend", "Avg Customer Spend (BRL)", 840, 65, 420, 85, is_currency=True))

    # Middle Row: One-time vs Repeat Donut + Acquisition Trend (y=165, h=265)
    p3_vcs.append(make_donut_visual("kpi_customer_segments", "customer_type", "customer_count", "Customer Count", 20, 165, 450, 265, "Customer Type Distribution (One-Time vs Repeat)"))
    p3_vcs.append(make_chart_visual("lineChart", "kpi_monthly_customer_acquisition", "acquisition_month", ["new_customers", "repeat_customers"], ["New Customers", "Repeat Customers"], 490, 165, 770, 265, "Monthly Customer Acquisition Trend"))

    # Bottom Row: Customer Segment Revenue + Customer Lifetime Value (y=445, h=255)
    p3_vcs.append(make_chart_visual("clusteredColumnChart", "kpi_customer_segments", "customer_type", ["segment_revenue"], ["Revenue (BRL)"], 20, 445, 450, 255, "Customer Segment Revenue Contribution"))
    p3_vcs.append(make_chart_visual("lineChart", "kpi_monthly_customer_acquisition", "acquisition_month", ["avg_customer_lifetime_value"], ["Avg CLV (BRL)"], 490, 445, 770, 255, "Average Customer Lifetime Value (CLV) Trend"))

    sections.append({
        "id": 2,
        "name": "Section_Customer_Intelligence",
        "displayName": "CUSTOMER INTELLIGENCE",
        "filters": "[]",
        "ordinal": 2,
        "width": 1280.0,
        "height": 720.0,
        "visualContainers": p3_vcs
    })

    # =========================================================================
    # PAGE 4: MARKETING AND OPERATIONS
    # =========================================================================
    p4_vcs = []
    p4_vcs.append(make_textbox("ShopPulse — Operations, Delivery Logistics & Marketing Funnel", 20, 10, 1240, 45, 18, True))

    # 5 KPI Cards (Row 1: y=65, h=85)
    p4_vcs.append(make_card_visual("kpi_monthly_delivery", "delivered_orders", "Delivered Orders", 20, 65, 230, 85))
    p4_vcs.append(make_card_visual("kpi_monthly_delivery", "on_time_or_early_orders", "On-Time / Early Orders", 265, 65, 230, 85))
    p4_vcs.append(make_card_visual("kpi_monthly_delivery", "late_orders", "Late Orders (Carrier Delay)", 510, 65, 230, 85))
    p4_vcs.append(make_card_visual("kpi_executive_summary", "total_leads", "Total Marketing Leads", 755, 65, 235, 85))
    p4_vcs.append(make_card_visual("kpi_executive_summary", "total_conversions", "Won Deals (Conversions)", 1005, 65, 255, 85))

    # Middle Row (y=165, h=265): Delivery Trend + Marketing Leads/Conversions
    p4_vcs.append(make_chart_visual("clusteredColumnChart", "kpi_monthly_delivery", "purchase_month", ["on_time_or_early_orders", "late_orders"], ["On-Time Orders", "Late Orders"], 20, 165, 605, 265, "Monthly Delivery Performance Trend"))
    p4_vcs.append(make_chart_visual("clusteredColumnChart", "kpi_monthly_marketing", "year_month", ["total_leads", "total_conversions"], ["Marketing Leads", "Won Deals"], 645, 165, 615, 265, "Marketing Funnel: Inbound Leads vs Closed Deals"))

    # Bottom Row (y=445, h=255): Monthly Review Trend + Review Score by State
    p4_vcs.append(make_chart_visual("lineChart", "kpi_monthly_reviews", "year_month", ["average_review_score"], ["Avg Rating (1-5)"], 20, 445, 605, 255, "Monthly Customer Review Score Trend"))
    p4_vcs.append(make_chart_visual("clusteredColumnChart", "kpi_reviews_by_state", "customer_state", ["average_rating"], ["Avg Rating"], 645, 445, 615, 255, "Customer Review Satisfaction by State"))

    sections.append({
        "id": 3,
        "name": "Section_Marketing_Operations",
        "displayName": "MARKETING AND OPERATIONS",
        "filters": "[]",
        "ordinal": 3,
        "width": 1280.0,
        "height": 720.0,
        "visualContainers": p4_vcs
    })

    return sections

def generate_report():
    print(f"Reading base template from {SRC_ZIP}...")
    with zipfile.ZipFile(SRC_ZIP, "r") as zin:
        layout_raw = zin.read("Report/Layout")
        try:
            layout_text = layout_raw.decode("utf-16-le")
        except:
            layout_text = layout_raw.decode("utf-8")
        layout_json = json.loads(layout_text)
        
        # Build 4 complete sections
        sections = build_all_sections()
        layout_json["sections"] = sections
        
        # Encode modified layout to UTF-16LE without BOM
        new_layout_bytes = json.dumps(layout_json, ensure_ascii=False).encode("utf-16-le")
        
        print(f"Creating final report: {OUTPUT_PBIX}...")
        with zipfile.ZipFile(OUTPUT_PBIX, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "SecurityBindings":
                    continue
                content = zin.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    xml_text = content.decode("utf-8")
                    xml_text = re.sub(r'<Override\s+PartName="/SecurityBindings"\s+ContentType=""\s*/>', '', xml_text)
                    content = xml_text.encode("utf-8")
                elif item.filename == "Report/Layout":
                    content = new_layout_bytes
                
                zout.writestr(item.filename, content, compress_type=zipfile.ZIP_DEFLATED)
                
    print(f"[SUCCESS] Olist_Ecommerce_Intelligence.pbix successfully created at {OUTPUT_PBIX}")
    print(f"Total sections (pages): {len(sections)}")
    for i, s in enumerate(sections):
        print(f"  Page {i+1}: {s['displayName']} ({len(s['visualContainers'])} visuals)")

if __name__ == "__main__":
    generate_report()

