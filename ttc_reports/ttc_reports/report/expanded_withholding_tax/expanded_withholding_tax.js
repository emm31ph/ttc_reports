// Copyright (c) 2026, Edmund Managuit and contributors
// For license information, please see license.txt

frappe.query_reports["Expanded Withholding Tax"] = {
    "filters": [
        {

            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            reqd: 1,
            options: "Company"        
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default:""
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default:"" 
        }
    ],
};
