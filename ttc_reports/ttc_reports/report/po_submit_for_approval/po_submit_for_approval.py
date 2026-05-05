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
        {"label": _("Workflow State"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 150},
        {"label": _("Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 120},
        {"label": _("Creator"), "fieldname": "creator", "fieldtype": "Data", "width": 150},
        {"label": _("PO Number"), "fieldname": "po_number", "fieldtype": "Link", "options": "Purchase Order", "width": 150},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data", "width": 200},
        {"label": _("Item/s Name"), "fieldname": "items", "fieldtype": "Small Text", "width": 250},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Total"), "fieldname": "total", "fieldtype": "Currency", "width": 140},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
        {"label": _("Target Warehouse"), "fieldname": "target_warehouse", "fieldtype": "Data", "width": 180},
        {"label": _("Finance Book"), "fieldname": "finance_book", "fieldtype": "Data", "width": 120},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": _("Tax Category"), "fieldname": "tax_category", "fieldtype": "Data", "width": 120},
        {"label": _("Payment Terms"), "fieldname": "payment_terms_template", "fieldtype": "Link", "options": "Payment Terms Template", "width": 180},
    ]

# =========================
# DATA
# =========================
def get_data(filters):
    if not filters.get("company"):
        return []

    # Base filters for Purchase Orders
    po_filters = {
        "company": filters.get("company"),
        "workflow_state": "Submit for Approval"
    }

    if filters.get("from_date") and filters.get("to_date"):
        po_filters["transaction_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
        if filters.get("from_date") > filters.get("to_date"):
            frappe.throw(_("From Date cannot be greater than To Date"))


    # Get Purchase Orders
    purchase_orders = frappe.db.get_all(
        "Purchase Order",
        fields=[
            "name as po_number",
            "supplier",
            "transaction_date",
            "status",
            "workflow_state",
            "finance_book",
            "remarks",
            "owner",
            "cost_center",
            "project",
            "tax_category",
            "payment_terms_template",
            "total"
        ],
        filters=po_filters,
        order_by="transaction_date desc"
    )

    if not purchase_orders:
        return []

    # Collect PO numbers
    po_numbers = [po.po_number for po in purchase_orders]

    # Get Items for those POs
    po_items = frappe.db.get_all(
        "Purchase Order Item",
        fields=["parent as po_number", "item_name", "qty", "warehouse"],
        filters={"parent": ["in", po_numbers]}
    )

    # Organize items by PO
    items_map = {}
    for item in po_items:
        po_number = item.po_number
        if po_number not in items_map:
            items_map[po_number] = {"items": [], "total_qty": 0, "warehouses": set()}
        items_map[po_number]["items"].append(item.item_name)
        items_map[po_number]["total_qty"] += item.qty
        
        items_map[po_number]["warehouses"].add(item.warehouse or "")

    # Merge items into PO data
    data = []
    for po in purchase_orders:
        creator = frappe.db.get_value("User", po.owner, "full_name") or po.owner
        item_info = items_map.get(po.po_number, {"items": [], "total_qty": 0, "warehouses": set()})

        data.append({
            "po_number": po.po_number,
            "supplier": po.supplier,
            "transaction_date": po.transaction_date,
            "status": po.status,
            "workflow_state": po.workflow_state,
            "items": ", ".join(item_info["items"]),
            "total_qty": item_info["total_qty"],
            "target_warehouse": ", ".join(item_info["warehouses"]),
            "finance_book": po.finance_book,
            "remarks": po.remarks,
            "creator": creator,
            "cost_center": po.cost_center,
            "project": po.project,
            "tax_category": po.tax_category,
            "payment_terms_template": po.payment_terms_template,
            "total": po.total
        })

    return data
