// Copyright (c) 2026, Edmund Managuit and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Invoice Status and Payment"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_end()
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": [
				"",
				 "Draft",
				 "Submitted",
				 "Cancelled",
				 "Paid",
				 "Unpaid",
				 "Overdue",
				 "Partly Paid",
				 "Return"
			]			      
        }
    ]
};