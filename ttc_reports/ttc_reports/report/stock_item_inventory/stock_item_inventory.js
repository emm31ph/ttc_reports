frappe.query_reports["Stock Item Inventory"] = {
    "filters": [
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            reqd: 1,
            options: "Company"
        },
        
    ],

    onload: function(report) {
        // // You can also auto‑set defaults here if needed
        // let today = frappe.datetime.get_today();
        // frappe.query_report.set_filter_value('from_date', frappe.datetime.month_start(today));
        // frappe.query_report.set_filter_value('to_date', frappe.datetime.month_end(today));
    }
};
