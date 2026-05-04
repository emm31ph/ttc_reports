import frappe
from frappe import _
from collections import defaultdict

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
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 150},
        {"label": _("Workflow State"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 120},
        {"label": _("Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 120},
        {"label": _("PO Number"), "fieldname": "po_number", "fieldtype": "Link", "options": "Purchase Order", "width": 200},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data", "width": 300},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Gross Total"), "fieldname": "gross_total", "fieldtype": "Currency", "width": 140},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
        {"label": _("Target Warehouse"), "fieldname": "target_warehouse", "fieldtype": "Data", "width": 180},
        {"label": _("Finance Book"), "fieldname": "finance_book", "fieldtype": "Data", "width": 120},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": _("Tax Category"), "fieldname": "tax_category", "fieldtype": "Data", "width": 120},
        {"label": _("Payment Terms"), "fieldname": "payment_terms_template", "fieldtype": "Link", "options": "Payment Terms Template", "width": 180}
    ]

# =========================
# DATA
# =========================
def get_data(filters):
    if not filters.get("company"):
        return []

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    # =========================
    # BASE FILTERS
    # =========================
    po_filters = {"company": filters.get("company")}

    if from_date and to_date:
        po_filters["transaction_date"] = ["between", [from_date, to_date]]

    # =========================
    # FETCH PURCHASE ORDERS
    # =========================
    purchase_orders = frappe.get_all(
        "Purchase Order",
        filters=po_filters,
        fields=[
            "name as po_number",
            "supplier",
            "transaction_date",
            "status",
            "workflow_state",
            "finance_book",
            "remarks",
            "cost_center",
            "project",
            "tax_category",
            "payment_terms_template",
            "net_total"
        ],
        order_by="status, transaction_date"
    )

    # =========================
    # EXCLUDED COMBINATIONS
    # =========================
    excluded_conditions = {
        ("Cancelled", "Cancel"),
        ("Completed", "Approved"),
        ("Draft", "Draft"),
    }

    # Apply exclusion
    purchase_orders = [
        po for po in purchase_orders
        if (po.status, po.workflow_state) not in excluded_conditions
    ]

#     purchase_orders = frappe.db.sql("""
#     SELECT *
#     FROM `tabPurchase Order`
#     WHERE company = %(company)s

#     AND NOT (
#         (status = 'Cancelled' AND workflow_state = 'Cancel')
#         OR (status = 'Completed' AND workflow_state = 'Approved')
#         OR (status = 'Draft' AND workflow_state = 'Draft')
#     )
# """, filters, as_dict=1)
    
    po_names = [po.po_number for po in purchase_orders]
    # =========================
    # GET TAXES (ADD ONLY)
    # =========================
    taxes = frappe.db.get_all(
        "Purchase Taxes and Charges",
        filters={
            "parent": ["in", po_names],
            "base_tax_amount": [">", 0],
            "add_deduct_tax": "Add"
        },
        fields=["parent", "base_tax_amount"]
    )

    # =========================
    # MAP TAXES
    # =========================
    tax_map = defaultdict(float)
    for t in taxes:
        tax_map[t.parent] += (t.base_tax_amount or 0)

    # =========================
    # BUILD DATA
    # =========================
    data = []
    grand_total = 0

    for po in purchase_orders:
        items = frappe.get_all(
            "Purchase Order Item",
            filters={"parent": po.po_number},
            fields=["qty", "warehouse"]
        )

        total_qty = sum(item.qty for item in items)
        warehouses = ", ".join(sorted(set(item.warehouse for item in items if item.warehouse)))

        total_tax = tax_map.get(po.po_number, 0)
        gross_total = (po.net_total or 0) + total_tax

        data.append({
            "po_number": po.po_number,
            "supplier": po.supplier,
            "transaction_date": po.transaction_date,
            "status": po.status,
            "workflow_state": po.workflow_state,
            "finance_book": po.finance_book,
            "remarks": po.remarks,
            "cost_center": po.cost_center,
            "project": po.project,
            "tax_category": po.tax_category,
            "payment_terms_template": po.payment_terms_template,
            "gross_total": gross_total,
            "total_qty": total_qty,
            "target_warehouse": warehouses
        })

        grand_total += gross_total

    # =========================
    # GRAND TOTAL ROW
    # =========================
    data.append({
        "supplier": f"<span style='float:right; font-weight:bold;'>GRAND TOTAL (Total PO: {len(purchase_orders)})</span>",
        "gross_total": grand_total
    })

    return data
