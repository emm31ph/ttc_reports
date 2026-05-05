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
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Workflow State"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 120},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": _("Purchase Invoice"), "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 180},
        {"label": _("Return Against"), "fieldname": "return_against", "fieldtype": "Data", "width": 100},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data", "width": 230},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 120},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 150},       
        {"label": _("Outstanding Amount"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 170},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Data", "width": 150},
        {"label": _("Finance Book"), "fieldname": "finance_book", "fieldtype": "Data", "width": 120},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": _("Tax Template"), "fieldname": "taxes_template", "fieldtype": "Data", "width": 180},
        {"label": _("Payment Terms"), "fieldname": "payment_terms_template", "fieldtype": "Data", "width": 180},
        {"label": _("Expense Account"), "fieldname": "expense_account", "fieldtype": "Data", "width": 180},
        {"label": _("Payment Amount"), "fieldname": "payment_amount", "fieldtype": "Currency", "width": 150},
    ]

# =========================
# DATA
# =========================
def get_data(filters):
    if not filters.get("company"):
        return []

    # =========================
    # DATE FILTER
    # =========================
    pi_filters = {"company": filters.get("company")}

    if filters.get("workflow_state"):
        pi_filters["workflow_state"] = filters.get("workflow_state")

    if filters.get("from_date") and filters.get("to_date"):
        if filters.get("from_date") > filters.get("to_date"):
            frappe.throw(_("From Date cannot be greater than To Date"))

        pi_filters["posting_date"] = [
            "between",
            [filters.get("from_date"), filters.get("to_date")]
        ]

    # =========================
    # FETCH INVOICES
    # =========================
    invoices = frappe.get_all(
        "Purchase Invoice",
        filters=pi_filters,
        fields=[
            "name as purchase_invoice",
            "supplier",
            "posting_date",
            "status",
            "workflow_state",
            "finance_book",
            "remarks",
            "cost_center",
            "due_date",
            "is_paid",
            "is_return", 
            "owner",
            "approver",
            "project",
            "return_against",
            "taxes_and_charges as taxes_template",
            "payment_terms_template",
            "net_total",
            "grand_total",
            "outstanding_amount"
        ],
        order_by="status, posting_date"
    )

    if not invoices:
        return []

    # =========================
    # EXCLUDE RULES
    # =========================
    filtered_invoices = []
    for inv in invoices:
        if (
            (inv.status == "Cancelled" and inv.workflow_state == "Cancel") or
            (inv.status == "Draft" and inv.workflow_state == "Reject") or
            (inv.status == "Draft" and inv.workflow_state == "Draft")
        ):
            continue

        filtered_invoices.append(inv)

    invoice_names = [inv.purchase_invoice for inv in filtered_invoices]

    # =======================
    # ITEMS
    # =======================

    items = frappe.db.get_all(
        "Purchase Invoice Item",
        fields=["parent as purchase_invoice", "qty", "warehouse", "expense_account"],
        filters={"parent": ["in", invoice_names]}
    )

    item_map = {}
    for it in items:
        inv = it.purchase_invoice
        if inv not in item_map:
            item_map[inv] = {"total_qty": 0, "warehouses": set(), "expense_accounts": set()}

        item_map[inv]["total_qty"] += it.qty or 0
        if it.warehouse:
            item_map[inv]["warehouses"].add(it.warehouse)
        if it.expense_account:
            item_map[inv]["expense_accounts"].add(it.expense_account)

    # =========================
    # PAYMENTS
    # =========================
    payments = frappe.db.get_all(
        "Payment Schedule",
        fields=["parent as purchase_invoice", "payment_amount"],
        filters={"parent": ["in", invoice_names]}
    )

    payment_map = defaultdict(float)
    for p in payments:
        payment_map[p.purchase_invoice] += p.payment_amount or 0

    # =========================
    # TAXES (POSITIVE ONLY) - 
    # =========================
    taxes = frappe.db.get_all(
        "Purchase Taxes and Charges",
        fields=["parent", "base_tax_amount"],
        filters={
            "parent": ["in", invoice_names],           
            "base_tax_amount": [">", 0],
            "add_deduct_tax": "Add"
        }
    )

    tax_map = defaultdict(float)
    for t in taxes:
        tax_map[t.parent] += t.base_tax_amount or 0

    # =========================
    # BUILD RESULT
    # =========================
    data = []
    grand_total = 0

    for inv in filtered_invoices:

        creator = frappe.db.get_value("User", inv.owner, "full_name") or inv.owner

        item = item_map.get(inv.purchase_invoice, {})
        payment_amount = payment_map.get(inv.purchase_invoice, 0)
        
        
        # total_tax = tax_map.get(inv.purchase_invoice, 0)
        #gross_total = (inv.net_total or 0) + total_tax
       
        row = {
            "supplier": inv.supplier,
            "purchase_invoice": inv.purchase_invoice,
            "posting_date": inv.posting_date,
            "status": inv.status,
            "workflow_state": inv.workflow_state,
            "finance_book": inv.finance_book,
            "remarks": inv.remarks,
            "cost_center": inv.cost_center,
            "due_date": inv.due_date,
            "is_paid": "Yes" if inv.is_paid else "No",
            "is_return": "Yes" if inv.is_return else "No",
            "creator": creator,
            "approver": inv.approver or "",
            "project": inv.project,
            "taxes_template": inv.taxes_template,
            "payment_terms_template": inv.payment_terms_template,
            "total_qty": item.get("total_qty", 0),
            "warehouse": ", ".join(item.get("warehouses", [])),
            "expense_account": ", ".join(item.get("expense_accounts", [])),
            "net_total": inv.net_total,
            "grand_total": inv.grand_total,
            "payment_amount": payment_amount,
            "return_against": inv.return_against,
            "outstanding_amount": inv.outstanding_amount,            
        }

        data.append(row)
        grand_total += inv.grand_total

    return data