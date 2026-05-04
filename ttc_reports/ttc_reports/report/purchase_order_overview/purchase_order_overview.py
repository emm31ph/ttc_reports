# Copyright (c) 2026, Edmund Managuit and contributors
# For license information, please see license.txt

# file: purchase_order_summary.py
# location: frappe-bench/apps/your_app/your_app/report/purchase_order_summary/

# file: purchase_order_summary.py

# file: purchase_order_overview.py
# path: your_app/your_app/report/purchase_order_overview/

import frappe

def execute(filters=None):
    company = filters.get("company") if filters else None

    columns = [
        {"label": "Metric", "fieldname": "metric", "fieldtype": "Data", "width": 250},
        {"label": "Value", "fieldname": "value", "fieldtype": "Data", "width": 200},
    ]

    company_condition = f" AND company = '{company}'" if company else ""

    # Total Outstanding POs
    total_outstanding_pos = frappe.db.sql(f"""
        SELECT COUNT(*)
        FROM `tabPurchase Order`
        WHERE docstatus = 1
        AND status IN ('To Receive','To Bill','To Receive and Bill')
        {company_condition}
    """)[0][0]
    
    # Total Value of Outstanding POs
    result1 = frappe.db.sql(f"""
        SELECT SUM(grand_total) AS total
        FROM `tabPurchase Order`
        WHERE docstatus = 1
        AND status IN ('To Receive','To Bill','To Receive and Bill','To Deliver and Bill','Open')
        {company_condition}
    """, as_dict=True)

    total_value_outstanding_pos = result1[0].total or 0

    # Completed Purchase Orders (all time)
    total_completed_pos = frappe.db.sql(f"""
        SELECT COUNT(*)
        FROM `tabPurchase Order`
        WHERE docstatus = 1
        AND status = 'Completed'
        {company_condition}
    """)[0][0]

    result2 = frappe.db.sql(f"""
        SELECT SUM(grand_total) AS total
        FROM `tabPurchase Order`
        WHERE docstatus = 1
        AND status = 'Completed'
        {company_condition}
    """, as_dict=True)

    total_value_completed_pos = result2[0].total or 0


    data = [
        {"metric": "Total Outstanding Purchase Orders", "value": total_outstanding_pos},
        {"metric": "Total Value of Outstanding POs", "value": f"₱{total_value_outstanding_pos:,.2f}"},
        {"metric": "Total Completed Purchase Orders (All Time)", "value": total_completed_pos},
        {"metric": "Total Value of Completed POs (All Time)", "value": f"₱{total_value_completed_pos:,.2f}"}
    ]

    return columns, data
