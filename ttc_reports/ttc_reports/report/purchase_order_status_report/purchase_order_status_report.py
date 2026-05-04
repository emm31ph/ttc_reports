# Copyright (c) 2026, Edmund Managuit and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

# =========================
# COLUMNS
# =========================
def get_columns():
    return [
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data", "width": 300},
        {"label": _("PO Number"), "fieldname": "po_number", "fieldtype": "Link", "options": "Purchase Order", "width": 200},
        {"label": _("Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 150},
        {"label": _("Workflow State"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 120},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},    
        {"label": _("Total"), "fieldname": "total", "fieldtype": "Currency", "width": 120},

        {"label": _("Finance Book"), "fieldname": "finance_book", "fieldtype": "Data", "width": 120},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
        {"label": _("Approver"), "fieldname": "approver", "fieldtype": "Data", "width": 150},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},

        {"label": _("Tax Category"), "fieldname": "tax_category", "fieldtype": "Data", "width": 120},
        {"label": _("Payment Terms"), "fieldname": "payment_terms_template", "fieldtype": "Link", "options": "Payment Terms Template", "width": 180},
        {"label": _("Target Warehouse"), "fieldname": "target_warehouse", "fieldtype": "Data", "width": 180}
        
    ]

# =========================
# DATA
# =========================
def get_data(filters):
    conditions = "WHERE 1=1"

    if filters.get("company"):
        conditions += " AND po.company = %(company)s"

    if filters.get("from_date"):
        conditions += " AND po.transaction_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND po.transaction_date <= %(to_date)s"

    if filters.get("status"):
        if filters.get("status") == "Outstanding PO":
            conditions += """
                AND po.status IN (
                    'To Receive and Bill',
                    'To Bill',
                    'To Receive'
                )
            """
        else:
            conditions += " AND po.status = %(status)s"

    query = f"""
        SELECT
            po.name,
            po.supplier,
            po.transaction_date,
            po.status,
            po.workflow_state,
            po.finance_book,
            po.remarks,
            po.owner AS approver,
            po.cost_center,
            po.project,
            po.tax_category,
            po.payment_terms_template,

            po.total AS total,

            (
                SELECT SUM(qty)
                FROM `tabPurchase Order Item`
                WHERE parent = po.name
            ) AS total_qty,

            GROUP_CONCAT(DISTINCT poi.warehouse) AS target_warehouse

        FROM
            `tabPurchase Order` po

        LEFT JOIN
            `tabPurchase Order Item` poi ON poi.parent = po.name

        {conditions}

        GROUP BY po.name
        ORDER BY po.status, po.transaction_date
    """

    result = frappe.db.sql(query, filters, as_dict=True)

    data = []
    supplier_map = {}

    # =========================
    # GROUP DATA
    # =========================
    for row in result:
        supplier = row.supplier or "No Supplier"

        if supplier not in supplier_map:
            supplier_map[supplier] = {
                "total": 0,
                "count": 0,
                "rows": []
            }

        supplier_map[supplier]["rows"].append({
            "name": row.name,
            "transaction_date": row.transaction_date,
            "status": row.status,
            "workflow_state": row.workflow_state,
            "finance_book": row.finance_book,
            "remarks": row.remarks,
            "approver": row.approver,
            "cost_center": row.cost_center,
            "project": row.project,
            "total_qty": row.total_qty,
            "tax_category": row.tax_category,
            "payment_terms_template": row.payment_terms_template,
            "target_warehouse": row.target_warehouse,
            "total": row.total
        })

        supplier_map[supplier]["total"] += row.total or 0
        supplier_map[supplier]["count"] += 1

    grand_total = 0
    grand_count = 0

    # =========================
    # BUILD OUTPUT
    # =========================
    for supplier, details in supplier_map.items():

        # Supplier Header
        data.append({
            "supplier": supplier,
            "total_qty": None,
            "total": None
        })

        # PO Rows
        for po in details["rows"]:
            data.append({
                "supplier": "   ",
                "po_number": po["name"],
                "transaction_date": po["transaction_date"],
                "status": po["status"],
                "workflow_state": po["workflow_state"],
                "finance_book": po["finance_book"],
                "remarks": po["remarks"],
                "approver": po["approver"],
                "cost_center": po["cost_center"],
                "project": po["project"],
                "tax_category": po["tax_category"],
                "payment_terms_template": po["payment_terms_template"],
                "target_warehouse": po["target_warehouse"],
                "total_qty": po["total_qty"],
                "total": po["total"]
            })

        # Supplier TOTAL
        data.append({
            "supplier": f"<span style='float:right; font-weight:bold;'>TOTAL (PO: {details['count']})</span>",
            "total": details["total"],
            "total_qty": None
        })

        grand_total += details["total"]
        grand_count += details["count"]

    # =========================
    # GRAND TOTAL
    # =========================
    data.append({
        "supplier": f"<span style='float:right; font-weight:bold;'>GRAND TOTAL (Total PO: {grand_count})</span>",
        "total": grand_total,
        "total_qty": None
    })

    return data
