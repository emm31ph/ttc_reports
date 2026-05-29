import frappe
from frappe.utils import get_first_day, get_last_day, nowdate


def execute(filters=None):
    filters = filters or {}

    set_default_dates(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def set_default_dates(filters):
    if not filters.get("from_date"):
        filters["from_date"] = get_first_day(nowdate())

    if not filters.get("to_date"):
        filters["to_date"] = get_last_day(nowdate())

def get_columns():
    return [
        {
            "label": "Material Request",
            "fieldname": "material_request",
            "fieldtype": "Link",
            "options": "Material Request",
        },
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Data",
            "options": "Item",
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
        },
        {
            "label": "MR Qty",
            "fieldname": "mr_qty",
            "fieldtype": "Float",
        },
        {
            "label": "MR Status",
            "fieldname": "mr_status",
            "fieldtype": "Data",
        },
        {
            "label": "MR Workflow",
            "fieldname": "mr_workflow_state",
            "fieldtype": "Data",
        },

        {
            "label": "Supplier Quotation",
            "fieldname": "supplier_quotation",
            "fieldtype": "Link",
            "options": "Supplier Quotation",
        },
        {
            "label": "SQ Qty",
            "fieldname": "sq_qty",
            "fieldtype": "Float",
        },
        {
            "label": "SQ Status",
            "fieldname": "sq_status",
            "fieldtype": "Data",
        },
        {
            "label": "SQ Workflow",
            "fieldname": "sq_workflow_state",
            "fieldtype": "Data",
        },

        {
            "label": "Purchase Order",
            "fieldname": "purchase_order",
            "fieldtype": "Link",
            "options": "Purchase Order",
        },
        {
            "label": "PO Qty",
            "fieldname": "po_qty",
            "fieldtype": "Float",
        },
        {
            "label": "PO Status",
            "fieldname": "po_status",
            "fieldtype": "Data",
        },
        {
            "label": "PO Workflow",
            "fieldname": "po_workflow_state",
            "fieldtype": "Data",
        },

        {
            "label": "Purchase Receipt",
            "fieldname": "purchase_receipt",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
        },
        {
            "label": "PR Qty",
            "fieldname": "pr_qty",
            "fieldtype": "Float",
        },
        {
            "label": "PR Status",
            "fieldname": "pr_status",
            "fieldtype": "Data",
        },
        {
            "label": "PR Workflow",
            "fieldname": "pr_workflow_state",
            "fieldtype": "Data",
        },

        {
            "label": "Purchase Invoice",
            "fieldname": "purchase_invoice",
            "fieldtype": "Link",
            "options": "Purchase Invoice",
        },
        {
            "label": "PI Qty",
            "fieldname": "pi_qty",
            "fieldtype": "Float",
        },
        {
            "label": "PI Status",
            "fieldname": "pi_status",
            "fieldtype": "Data",
        },
        {
            "label": "PI Workflow",
            "fieldname": "pi_workflow_state",
            "fieldtype": "Data",
        },
    ]


def get_data(filters):
    mr_filters = get_mr_filters(filters)

    material_requests = frappe.get_all(
        "Material Request",
        fields=["name", "status", "workflow_state"],
        filters=mr_filters,
    )

    if not material_requests:
        return []

    mr_names = [mr.name for mr in material_requests]

    mr_docs = {
        mr.name: mr for mr in material_requests
    }

    mr_items = frappe.get_all(
        "Material Request Item",
        fields=[
            "name",
            "parent",
            "item_code",
            "item_name",
            "qty",
        ],
        filters={"parent": ["in", mr_names]},
    )

    procurement_data = get_procurement_data()

    data = []

    for mr_item in mr_items:
        row = build_base_row(
            mr_item,
            mr_docs.get(mr_item.parent),
        )

        update_row_from_links(
            row,
            mr_item.name,
            procurement_data,
        )

        data.append(row)

    return data


def get_mr_filters(filters):
    mr_filters = {
        "transaction_date": [
            "between",
            [filters["from_date"], filters["to_date"]],
        ],
        "docstatus": ["!=", 2],
    }

    if filters.get("company"):
        mr_filters["company"] = filters["company"]

    if filters.get("owner"):
        mr_filters["owner"] = filters["owner"]

    if filters.get("material_request"):
        mr_filters["name"] = filters["material_request"]

    return mr_filters


def get_procurement_data():
    procurement_config = {
        "sq": {
            "doctype": "Supplier Quotation Item",
            "parent_doctype": "Supplier Quotation",
        },
        "po": {
            "doctype": "Purchase Order Item",
            "parent_doctype": "Purchase Order",
        },
        "pr": {
            "doctype": "Purchase Receipt Item",
            "parent_doctype": "Purchase Receipt",
        },
        "pi": {
            "doctype": "Purchase Invoice Item",
            "parent_doctype": "Purchase Invoice",
        },
    }

    result = {}

    for key, config in procurement_config.items():

        child_items = frappe.get_all(
            config["doctype"],
            filters={"docstatus": ["!=", 2]},
            fields=[
                "name",
                "parent",
                "material_request_item",
                "qty",
            ],
        )

        grouped = {}

        for item in child_items:
            grouped.setdefault(
                item.material_request_item,
                []
            ).append(item)

        parent_names = list({
            item.parent for item in child_items
        })

        parent_docs = {}

        if parent_names:
            parents = frappe.get_all(
                config["parent_doctype"],
                filters={"name": ["in", parent_names]},
                fields=[
                    "name",
                    "status",
                    "workflow_state",
                ],
            )

            parent_docs = {
                doc.name: doc for doc in parents
            }

        result[key] = {
            "grouped": grouped,
            "parent_docs": parent_docs,
        }

    return result


def build_base_row(mr_item, mr_doc):
    return {
        "material_request": mr_item.parent,
        "mr_item": mr_item.name,
        "item_code": mr_item.item_code,
        "item_name": mr_item.item_name,
        "mr_qty": mr_item.qty,
        "mr_status": mr_doc.status if mr_doc else None,
        "mr_workflow_state": (
            mr_doc.workflow_state if mr_doc else None
        ),
    }


def update_row_from_links(row, mr_item_name, procurement_data):

    field_mapping = {
        "sq": {
            "link_field": "supplier_quotation",
            "qty_field": "sq_qty",
            "status_field": "sq_status",
            "workflow_field": "sq_workflow_state",
        },
        "po": {
            "link_field": "purchase_order",
            "qty_field": "po_qty",
            "status_field": "po_status",
            "workflow_field": "po_workflow_state",
        },
        "pr": {
            "link_field": "purchase_receipt",
            "qty_field": "pr_qty",
            "status_field": "pr_status",
            "workflow_field": "pr_workflow_state",
        },
        "pi": {
            "link_field": "purchase_invoice",
            "qty_field": "pi_qty",
            "status_field": "pi_status",
            "workflow_field": "pi_workflow_state",
        },
    }

    for key, mapping in field_mapping.items():

        linked_docs = procurement_data[key]["grouped"].get(
            mr_item_name,
            []
        )

        for doc in linked_docs:

            parent_doc = procurement_data[key][
                "parent_docs"
            ].get(doc.parent)

            row.update({
                mapping["link_field"]: doc.parent,
                mapping["qty_field"]: doc.qty,
                mapping["status_field"]: (
                    parent_doc.status if parent_doc else None
                ),
                mapping["workflow_field"]: (
                    parent_doc.workflow_state
                    if parent_doc else None
                ),
            })