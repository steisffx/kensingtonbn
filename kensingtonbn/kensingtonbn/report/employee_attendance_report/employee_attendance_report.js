// Copyright (c) 2016, ClefinCode and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Attendance Report"] = {
	"filters": [

		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"width": "80",
			"reqd":  1  , 
			"options": "Employee",
			"default" : "EMP/00047"
        },



		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": __("From Date"),
			"default" : frappe.datetime.month_start(),
			"reqd":  1  

		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": __("To Date"),
			"reqd":  1  , 

			"default": frappe.datetime.month_end()
		},


		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"width": "80",
			"options" : ["Present" , "Absent" , "On Leave" , "Half Day" , "Work From Home"],
			"reqd":  0
        },




    ]
};
