# Copyright (c) 2026, Edmund Managuit and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _
from frappe.utils import today


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
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data", "width": 230},
        {"label": _("Purchase Invoice"),"fieldname": "purchase_invoice","fieldtype": "Link","options": "Purchase Invoice","width": 180},     
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": _("Finance Book"), "fieldname": "finance_book", "fieldtype": "Data", "width": 120},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Total"), "fieldname": "total", "fieldtype": "Currency", "width": 120},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Workflow State"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 120},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 120},
        {"label": _("Is Paid"), "fieldname": "is_paid", "fieldtype": "Data", "width": 100},
        {"label": _("Is Return"), "fieldname": "is_return", "fieldtype": "Data", "width": 100},
        {"label": _("Approver"), "fieldname": "approver", "fieldtype": "Data", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Data", "width": 150},
        {"label": _("Tax Template"), "fieldname": "taxes_template", "fieldtype": "Data", "width": 180},
        {"label": _("Payment Terms"), "fieldname": "payment_terms_template", "fieldtype": "Data", "width": 180},
        {"label": _("Expense Account"), "fieldname": "expense_account", "fieldtype": "Data", "width": 180},
        {"label": _("Total Taxes"), "fieldname": "total_taxes", "fieldtype": "Currency", "width": 120},
        {"label": _("Payment Amount"), "fieldname": "payment_amount", "fieldtype": "Currency", "width": 150},
    ]
# =========================
# STATUS FILTER LOGIC
# =========================
def apply_status_filter(conditions, filters):

    status = filters.get("status")
    if not status:
        return conditions

    if status == "Draft":
        conditions += " AND pi.docstatus = 0"

    elif status == "Submitted":
        conditions += " AND pi.docstatus = 1"

    elif status == "Cancelled":
        conditions += " AND pi.docstatus = 2"

    elif status == "Paid":
        conditions += " AND pi.docstatus = 1 AND pi.outstanding_amount = 0"

    elif status == "Unpaid":
        conditions += " AND pi.docstatus = 1 AND pi.outstanding_amount > 0"

    elif status == "Partly Paid":
        conditions += " AND pi.docstatus = 1 AND pi.paid_amount > 0 AND pi.outstanding_amount > 0"

    elif status == "Overdue":
        conditions += f" AND pi.docstatus = 1 AND pi.outstanding_amount > 0 AND pi.due_date < '{today()}'"

    elif status == "Return":
        conditions += " AND pi.is_return = 1"

    return conditions


# =========================
# DATA
# =========================
def get_data(filters):
    conditions = "WHERE 1=1"

    if filters.get("company"):
        conditions += " AND pi.company = %(company)s"

    if filters.get("from_date"):
        conditions += " AND pi.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND pi.posting_date <= %(to_date)s"

    # APPLY STATUS FILTER
    conditions = apply_status_filter(conditions, filters)

    query = f"""
        SELECT
            pi.supplier,
            pi.name AS purchase_invoice,         
            pi.posting_date,
            pi.finance_book,
            pi.remarks,
            pi.cost_center,
            pi.workflow_state,
            pi.due_date,
            pi.is_paid,
            pi.is_return,
            pi.owner AS approver,
            pi.project,
            pi.taxes_and_charges AS taxes_template,
            pi.payment_terms_template,
            pi.total AS total,
            pi.outstanding_amount,
            pi.paid_amount,

            (
    		SELECT SUM(qty)
    		FROM `tabPurchase Invoice Item`
    		WHERE parent = pi.name
			) AS total_qty,
            GROUP_CONCAT(DISTINCT pii.warehouse) AS warehouse,
            GROUP_CONCAT(DISTINCT pii.expense_account) AS expense_account,

            pi.total_taxes_and_charges AS total_taxes,
			MAX(ps.payment_amount) AS payment_amount

        FROM
            `tabPurchase Invoice` pi

        LEFT JOIN
            `tabPurchase Invoice Item` pii ON pii.parent = pi.name

        LEFT JOIN
            `tabPurchase Taxes and Charges` ptc ON ptc.parent = pi.name

        LEFT JOIN
            `tabPayment Schedule` ps ON ps.parent = pi.name

        {conditions}

        GROUP BY pi.name
        ORDER BY pi.supplier, pi.posting_date
    """

    result = frappe.db.sql(query, filters, as_dict=True)

    data = []
    supplier_map = {}

    # =========================
    # GROUPING
    # =========================
    for row in result:
        supplier = row.supplier or "No Supplier"

        if supplier not in supplier_map:
            supplier_map[supplier] = {
                "total": 0,
                "payment_amount":0,
                "count": 0,
                "rows": []
            }

        supplier_map[supplier]["rows"].append(row)
        supplier_map[supplier]["total"] += row.total or 0
        supplier_map[supplier]["payment_amount"] += row.payment_amount or 0
        supplier_map[supplier]["count"] += 1

    grand_total = 0
    grand_total1 = 0
    grand_count = 0

    # =========================
    # BUILD OUTPUT
    # =========================
    for supplier, details in supplier_map.items():

        # Supplier header
        data.append({
            "supplier": supplier,
            "total_qty":None,
            "total_taxes":None,
            "total":None,
            "payment_amount":None
        })

        # Invoice rows
        for row in details["rows"]:
            data.append({
                "supplier": "   ",
                "purchase_invoice": row.purchase_invoice,
                "posting_date": row.posting_date,
                "finance_book": row.finance_book,
                "remarks": row.remarks,
                "cost_center": row.cost_center,
                "workflow_state": row.workflow_state,
                "due_date": row.due_date,
                "is_paid": "Yes" if row.is_paid else "No",
                "is_return": "Yes" if row.is_return else "No",
                "approver": row.approver,
                "project": row.project,
                "warehouse": row.warehouse,
                "total_qty": row.total_qty,
                "total": row.total,
                "taxes_template": row.taxes_template,
                "payment_terms_template": row.payment_terms_template,
                "expense_account": row.expense_account,
                "total_taxes": row.total_taxes,
                "payment_amount": row.payment_amount
            })

        # Supplier total
        data.append({
            "supplier": f"<span style='float:right; font-weight:bold;'>TOTAL (Invoice: {details['count']})</span>",
           # "supplier": f"<b>TOTAL (Invoice: {details['count']})</b>",
            "total": details["total"],  
            "payment_amount": details["payment_amount"],     
            "total_qty": None,
            "total_taxes": None
        })

        grand_total += details["total"]
        grand_total1 += details["payment_amount"]
        grand_count += details["count"]

    # Grand total
    data.append({
        "supplier": f"<b>GRAND TOTAL (Invoice: {grand_count})</b>",
        "total": grand_total,
        "payment_amount": grand_total1,
        "total_qty": None,
        "total_taxes": None
    })

    return data