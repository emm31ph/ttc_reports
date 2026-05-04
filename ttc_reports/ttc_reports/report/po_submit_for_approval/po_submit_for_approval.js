frappe.query_reports["PO Submit for Approval"] = {
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

    onload: function(report) {
        // // You can also auto‑set defaults here if needed
        // let today = frappe.datetime.get_today();
        // frappe.query_report.set_filter_value('from_date', frappe.datetime.month_start(today));
        // frappe.query_report.set_filter_value('to_date', frappe.datetime.month_end(today));
    }
};
