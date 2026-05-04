frappe.query_reports["PO Status Report"] = {
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

