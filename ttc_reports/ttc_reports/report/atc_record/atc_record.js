frappe.query_reports["ATC Record"] = {
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
