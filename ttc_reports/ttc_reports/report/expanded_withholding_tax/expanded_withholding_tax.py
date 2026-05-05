import frappe
from frappe import _
from frappe.utils import flt
from itertools import groupby
from operator import itemgetter

# =========================
# ENTRY POINT
# Called by Frappe Report engine
# =========================
def execute(filters=None):
    filters = filters or {}
    
    columns = get_columns()
    data = get_data(filters)
     
    return columns, data


# =========================
# REPORT COLUMNS
# Defines layout of the report
# =========================
def get_columns():
    return [
        {"label": _("ATC"), "fieldname": "atc_code", "fieldtype": "Data", "width": 150},  # ATC Code first
        {"label": _("TIN"), "fieldname": "tax_id", "fieldtype": "Data", "width": 180},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data", "width": 410},
        {"label": _("Invoice No"), "fieldname": "invoice_no", "fieldtype": "Dynamic Link", "options": "doc_type", "width": 200},
        {"label": _("Taxable Amount"), "fieldname": "taxable_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Tax Amount"), "fieldname": "tax_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Tax Rate"), "fieldname": "tax_rate", "fieldtype": "Data", "width": 120, "align": "center"},
    ]


# =========================
# REPORT DATA BUILDER
# - Fetches ATC records
# - Groups by ATC Code
# - Builds report rows (header, details, totals)
# =========================
def get_data(filters):
    """Fetches, sorts, and structures the report data."""
    
    if not filters.get("company"):
        return []

    db_filters = {"company": filters.get("company")}

    if filters.get("from_date") and filters.get("to_date"):
        db_filters["posting_date"] = ("between", (filters.get("from_date"), filters.get("to_date")))

    records = frappe.get_all(
        "ATC Record",
        filters=db_filters,
        fields=[
            "tax_id",
            "supplier",
            "invoice_no",
            "taxable_amount",
            "tax_amount",
            "account",
            "atc_code",
            "tax_rate",
            "doc_type"
        ],
    )

    if not records:
        return []

    records.sort(key=_get_sort_key)

    data = []
    grand_total_taxable = 0
    grand_total_tax = 0

    for atc_code, group_rows in groupby(records, key=itemgetter("atc_code")):
        rows = list(group_rows)

        # Group header row → ATC Code in first column
        data.append({"atc_code": f"{atc_code}", "is_bold": 1})

        # Detail rows
        for row in rows:
            _add_detail_row(data, row)

        # Group total row
        group_taxable, group_tax = _add_total_row(data, atc_code, rows)
        grand_total_taxable += group_taxable
        grand_total_tax += group_tax

    # Grand total row at the end
    if data:
        data.append({})  # Spacer row
        data.append({
            "atc_code": "Grand Total",   # ATC Code column
            "taxable_amount": grand_total_taxable,
            "tax_amount": grand_total_tax,
            "is_bold": 1
        })

    return data


def _get_sort_key(record):
    invoice_no = record.get("invoice_no", "")
    prefix_order = 0 if invoice_no.startswith("PI") else 1 if invoice_no.startswith("JV") else 2
    return (record.get("atc_code"), prefix_order, invoice_no)


def _add_detail_row(data, row):
    taxable = flt(row.get("taxable_amount"))
    tax = flt(row.get("tax_amount")) 

    data.append({
        "indent": 1,
        # "atc_code": "none",  # ATC Code in detail rows too
        "tax_id": f'{row.get("tax_id") or ""}',
        "supplier": row.get("supplier") or "",
        "invoice_no": row.get("invoice_no") or "",
        "doc_type": row.get("doc_type") or "",
        "taxable_amount": taxable or "",
        "tax_rate": f"{row.get('tax_rate')}%",
        "tax_amount": tax
    })


def _add_total_row(data, atc_code, rows):
    total_taxable = sum(flt(r.get("taxable_amount")) for r in rows)
    total_tax = sum(flt(r.get("tax_amount")) for r in rows)

    data.append({
        "atc_code": f"Total - {atc_code}",  # ATC Code column
        "taxable_amount": total_taxable,
        "tax_amount": total_tax,
        "is_bold": 1
    })
    
    return total_taxable, total_tax
