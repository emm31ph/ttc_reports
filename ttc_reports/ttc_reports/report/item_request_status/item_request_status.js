// Copyright (c) 2026, Edmund Managuit and contributors
// For license information, please see license.txt

frappe.query_reports["Item Request Status"] = {
	"filters": [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
			reqd: 1,
            options: "Company",
			default: frappe.defaults.get_user_default("Company"),
        },
        {
            fieldname: "owner",
            label: __("Owner"),
            fieldtype: "Link",
            options: "User",
			default: frappe.session.user
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_end()
        },
        {
            fieldname: "material_request",
            label: __("Material Request"),
            fieldtype: "Link",
            options: "Material Request"
        }
    ]
};