# file: stock_balance_mapping.py

import frappe
from frappe import _

def execute(filters=None):
    # Entry point for the report
    # Returns column definitions and data based on filters
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data

def get_columns():
    # Define the report columns
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Data", "width": 120},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 350},
        {"label": _("UOM"), "fieldname": "stock_uom", "fieldtype": "Data", "width": 80},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 200},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 240},
        {"label": _("Stocks"), "fieldname": "balance_count", "fieldtype": "Float", "width": 120},
        {"label": _("To Receive"), "fieldname": "ordered_qty", "fieldtype": "Float", "width": 120},
    ]

def get_data(filters):
    data = []

    # Step 1: Get warehouses belonging to the selected company
    # If company filter is provided, restrict warehouses to that company
    wh_filters = {}
    if filters.get("company"):
        wh_filters["company"] = filters.get("company")

    warehouses = frappe.get_all("Warehouse", fields=["name"], filters=wh_filters)
    wh_names = [w.name for w in warehouses]

    # Step 2: Build Bin filters (Bin = stock balance per item per warehouse)
    bin_filters = {}
    if wh_names:
        bin_filters["warehouse"] = ["in", wh_names]

    # Override with specific warehouse if provided
    if filters.get("warehouse"):
        bin_filters["warehouse"] = filters.get("warehouse")

    # Apply Item Code filter if provided
    if filters.get("item_code"):
        bin_filters["item_code"] = filters.get("item_code")

    # Step 3: Get Bin records (actual stock + ordered qty)
    bins = frappe.get_all(
        "Bin",
        fields=["item_code", "actual_qty", "ordered_qty", "warehouse"],
        filters=bin_filters
    )

    # Step 4: Map Bin records to Item details
    # Only include stock items (is_stock_item = 1)
    for b in bins:
        item = frappe.db.get_value(
            "Item",
            b.item_code,
            ["item_name", "stock_uom", "is_stock_item", "item_group"]
        )
        if item and item[2]:  # Only include if is_stock_item = 1
            # Apply Item Group filter if provided
            if filters.get("item_group"):
                if item[3] != filters.get("item_group"):
                    continue
            else:
                # If item_group filter is empty, enforce company filter
                if filters.get("company"):
                    wh_company = frappe.db.get_value("Warehouse", b.warehouse, "company")
                    if wh_company != filters.get("company"):
                        continue

            # Append record to data
            data.append({
                "item_code": b.item_code,
                "item_name": item[0],
                "stock_uom": item[1],
                "item_group": item[3] or "",
                "warehouse": b.warehouse or "",
                "balance_count": b.actual_qty,
                "ordered_qty": b.ordered_qty
            })

    # Step 5: Sort ascending by Item Name for readability
    data = sorted(data, key=lambda x: x["item_name"] or "")
    return data
