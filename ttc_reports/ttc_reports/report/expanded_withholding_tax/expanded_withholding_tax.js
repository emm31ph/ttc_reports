// Copyright (c) 2026, Edmund Managuit and contributors
// For license information, please see license.txt

frappe.query_reports["Expanded Withholding Tax"] = {
	formatter: function (value, row, column, data, default_formatter) {

		// If it's a currency field and the raw value is 0, return an empty string
		if (column.fieldtype === "Currency" && value === undefined) {
			return "";
		}
        console.log(data);
        
        value = default_formatter(value, row, column, data);
        if (data && data.is_bold) {
            value = `<b style="font-weight:600">${value}</b>`;
        }

		// Otherwise, use the default formatter
		return value
	},
	filters: [
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
		},
	],
};
