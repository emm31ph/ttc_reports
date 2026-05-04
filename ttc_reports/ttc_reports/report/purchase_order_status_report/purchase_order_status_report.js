// Copyright (c) 2026, Edmund Managuit and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Order Status Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company"
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": [
                "",
                "Draft",
                "To Receive and Bill",
                "To Bill",
                "To Receive",
                "Completed",
                "Cancelled",
                "Outstanding PO"
            ],
            "default": "Outstanding PO"   // optional default
        }
    ]
};