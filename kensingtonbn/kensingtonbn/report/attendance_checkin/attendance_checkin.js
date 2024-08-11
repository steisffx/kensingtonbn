// Copyright (c) 2016, ClefinCode and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Checkin"] = {

	"filters": [
	{
		"fieldname" : "employee",
		"fieldtype": "Link",
		"label": __("Employee ID"),
		"options": "Employee",
	},
	{
		"fieldname": "from_date",
		"fieldtype": "Date",
		"label": __("From Date"),
		"default" : frappe.datetime.month_start(),
	},
	{
		"fieldname": "to_date",
		"fieldtype": "Date",
		"label": __("To Date"),
		"default": frappe.datetime.month_end(),
	},
	]

};
