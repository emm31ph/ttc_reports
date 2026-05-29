// Copyright (c) 2026, Edmund Managuit and contributors
// For license information, please see license.txt


frappe.query_reports["PO Items Report"] = {
    "filters": [
        {

            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            reqd: 1,
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        }
    ],

    onload: function(report) {
    //     // Auto‑populate ng filter kapag nag‑load ang report
    //     frappe.db.get_list('User Permission', {
    //         filters: {
    //             user: frappe.session.user,
    //             allow: 'Company'
    //         },
    //         fields: ['for_value']
    //     }).then(records => {
    //         let companies = records.map(r => r.for_value);
    //         if (companies.length) {
    //             frappe.query_report.set_filter_value('company', companies);
    //         }
    //     });
     }
};

