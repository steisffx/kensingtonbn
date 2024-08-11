// Copyright (c) 2016, ClefinCode and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Activity Report"] = {
	"filters": [
		{
			"fieldname":"assigned_date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "80"
		},
		{
			"fieldname":"assigned_user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "User",
		},
	]
};
