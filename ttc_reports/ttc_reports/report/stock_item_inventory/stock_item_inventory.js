frappe.query_reports["Stock Item Inventory"] = {
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
            fieldname: "item_code",
            label: "Item Code",
            fieldtype: "Link",
            options: "Item",
        },
        {
            fieldname: "item_group",
            label: "Item Group",
            fieldtype: "Link",
            options: "Item Group",
        },
        {
            fieldname: "warehouse",
            label: "Warehouse",
            fieldtype: "Link",
            options: "Warehouse",
            reqd: 0,  // make warehouse required
            get_query: function() {
                return {
                    filters: {
                        "company": frappe.query_report.get_filter_value("company")
                    }
                };
            }
        }
    ],

    onload: function(report) {
        // Example: auto-set date filters if needed
        // let today = frappe.datetime.get_today();
        // frappe.query_report.set_filter_value('from_date', frappe.datetime.month_start(today));
        // frappe.query_report.set_filter_value('to_date', frappe.datetime.month_end(today));
    }
};
