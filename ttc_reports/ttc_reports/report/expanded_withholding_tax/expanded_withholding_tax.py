import frappe
from frappe import _
from frappe.utils import flt
from collections import defaultdict


# =========================
# ENTRY POINT
# Called by Frappe Report engine
# =========================
def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


# =========================
# REPORT COLUMNS
# Defines layout of the report
# =========================
def get_columns():
    return [
        {"label": _("Tax"), "fieldname": "tax_id", "fieldtype": "Data", "width": 200},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data", "width": 300},
        {"label": _("Invoice No"), "fieldname": "invoice_no", "fieldtype": "Data", "width": 200},
        {"label": _("Taxable Amount"), "fieldname": "taxable_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Tax Rate"), "fieldname": "tax_rate", "fieldtype": "Data", "width": 120},
        {"label": _("Tax Amount"), "fieldname": "tax_amount", "fieldtype": "Currency", "width": 150},
    ]


# =========================
# REPORT DATA BUILDER
# - Fetches ATC records
# - Groups by ATC Code
# - Computes tax rate dynamically
# - Builds report rows (header, details, total)
# =========================
def get_data(filters):
    
    # Return empty if no company selected
    if not filters.get("company"):
        return []

    # =========================
    # BASE FILTERS
    # =========================
    atc_filters = {"company": filters.get("company")}

    # Optional date filtering
    if filters.get("from_date") and filters.get("to_date"):
        atc_filters["posting_date"] = [
            "between",
            [filters.get("from_date"), filters.get("to_date")]
        ]

    # =========================
    # FETCH DATA FROM DB
    # =========================
    records = frappe.get_all(
        "ATC Record",
        filters=atc_filters,
        fields=[
            "tax_id",
            "supplier",
            "invoice_no",
            "taxable_amount",
            "tax_amount",
            "account",
            "atc_code"
        ],
        order_by="atc_code, supplier, invoice_no"
    )

    # =========================
    # GROUP BY ATC CODE
    # =========================
    grouped = defaultdict(list)

    for r in records:
        grouped[r.get("atc_code")].append(r)

    data = []

    # =========================
    # BUILD REPORT OUTPUT
    # =========================
    for atc_code, rows in grouped.items():

        # HEADER ROW (group title)
        data.append({
            "invoice_no": f"<b>ATC Code: {atc_code}</b>",
            "taxable_amount": None,
            "tax_rate": None,
            "tax_amount": None
        })

        total_taxable = 0
        total_tax = 0

        # DETAIL ROWS
        for r in rows:
            taxable = flt(r.get("taxable_amount"))
            tax = flt(r.get("tax_amount"))

            # Compute tax rate (whole number percentage)
            tax_rate = int(round((tax / taxable) * 100)) if taxable else 0

            total_taxable += taxable
            total_tax += tax

            data.append({
                "tax_id": r.get("tax_id"),
                "supplier": r.get("supplier"),
                "invoice_no": r.get("invoice_no"),
                "taxable_amount": taxable,
                "tax_rate": f"{tax_rate}%",  # display format (no decimals)
                "tax_amount": tax
            })

        # TOTAL ROW (per ATC group)
        data.append({
            "invoice_no": f"<b>Total - {atc_code}</b>",
            "taxable_amount": total_taxable,
            "tax_amount": total_tax
        })

    return data