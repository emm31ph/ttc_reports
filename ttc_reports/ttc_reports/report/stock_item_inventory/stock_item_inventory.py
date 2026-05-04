# file: stock_balance_mapping.py

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Data", "width": 120},
        {"label": _("Description"), "fieldname": "item_name", "fieldtype": "Data", "width": 400},
        {"label": _("UOM"), "fieldname": "stock_uom", "fieldtype": "Data", "width": 80},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 200},
        {"label": _("Balance Count"), "fieldname": "balance_count", "fieldtype": "Float", "width": 140},
        {"label": _("Valuation Rate"), "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters):
    data = []

    # Step 1: Get warehouses for the selected company
    wh_filters = {}
    if filters and filters.get("company"):
        wh_filters["company"] = filters.get("company")

    warehouses = frappe.get_all("Warehouse", fields=["name"], filters=wh_filters)
    wh_names = [w.name for w in warehouses]

    # Step 2: Get Bin records for those warehouses
    bin_filters = {"warehouse": ["in", wh_names]} if wh_names else {}
    bins = frappe.get_all(
        "Bin",
        fields=["item_code", "actual_qty", "valuation_rate", "warehouse"],
        filters=bin_filters
    )

    # Step 3: Map Bin records to Item details, filter stock items only
    for b in bins:
        item = frappe.db.get_value("Item", b.item_code, ["item_name", "stock_uom", "is_stock_item"])
        if item and item[2]:  # Only include if is_stock_item = 1
            data.append({
                "item_code": b.item_code,
                "item_name": item[0],
                "stock_uom": item[1],
                "warehouse": b.warehouse,
                "balance_count": b.actual_qty,
                "valuation_rate": b.valuation_rate,
                "value": (b.actual_qty or 0) * (b.valuation_rate or 0)
            })

    # Step 4: Sort ascending by Description
    data = sorted(data, key=lambda x: x["item_name"] or "")
    return data
