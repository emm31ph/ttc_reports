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
        {"label": _("PO Number"), "fieldname": "po_number", "fieldtype": "Link", "options": "Purchase Order", "width": 200},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data", "width": 200},
        {"label": _("Workflow State"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 120},
        {"label": _("Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 120},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 100},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},     
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 120},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Data", "width": 150},
	]
# =========================
# DATA
# =========================
def get_data(filters):
    if not filters.get("company"):
        return []

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    po_filters = {"company": filters.get("company"), "workflow_state": "Approved"}
    if from_date and to_date:
        po_filters["transaction_date"] = ["between", [from_date, to_date]]

    purchase_orders = frappe.get_all(
        "Purchase Order",
        filters=po_filters,
        fields=[
            "name as po_number",
            "supplier",
            "transaction_date",
            "workflow_state",
            "finance_book",
            "remarks",
            "cost_center",
            "project",
            "tax_category",
            "payment_terms_template"
        ],
        order_by="transaction_date"
    )

    data = []

    for po in purchase_orders:
        # Header row per PO
        data.append({
            "po_number": po.po_number,
            "supplier": po.supplier,
            "workflow_state": po.workflow_state,
            "transaction_date": po.transaction_date,
            "remarks": po.remarks,
            "qty": None,
            "rate": None,
			"amount": None,
		    "remarks": None,
            "cost_center": None,
            "finance_book": None,
            "cost_center": None,
            "project": None,
            "tax_category": None,
            "payment_terms_template": None
        })

        # Item rows under this PO
        items = frappe.get_all(
            "Purchase Order Item",
            filters={"parent": po.po_number},
            fields=["item_code", "item_name", "qty", "uom", "rate", "amount", "warehouse"]
        )

        for item in items:
            data.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty,
                "uom": item.uom,
                "rate": item.rate,
                "amount": item.amount,
                "warehouse": item.warehouse
            })

    return data
