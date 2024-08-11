// Copyright (c) 2016, ClefinCode and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Total Statement Enquiry"] = {
	"filters": [
		{
			"fieldname" : "company",
			"fieldtype": "Link",
			"label": __("Company"),
			"options": "Company",
			"default": frappe.defaults.get_user_default("company"),
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
		{
			"fieldname": "customer",
			"fieldtype": "Link",
			"label": __("Customer"),
			"options": "Customer",
			get_data : function(txt){
				return frappe.db.get_link_options('Customer', txt, {
					company: frappe.query_report.get_filter_value("company")
				});
			}
		},
		// {
		// 	"fieldname": "branch",
		// 	"fieldtype": "Link",
		// 	"options": "Branch",
		// 	"label": __("Branch"),
		// 	get_data: function(txt){
		// 		return frappe.db.get_link_options("Branch", txt, {
		// 			company : frappe.query_report.get_filter_value('company')
		// 		})
		// 	}
		// },
	// 	{

	// 		"fieldname": "department",
	// 		"fieldtype": "Link",
	// 		"options": "Department",
	// 		"label": __("Department"),
	// 		get_data : function(txt){
	// 			return frappe.db.get_link_options("Department", txt, {
					
	// 			})
	// 		}
			
	// 	},
		{
			"fieldname": "territory",
			"fieldtype": "Link",
			"options": "Territory",
			"label": __("Territory")
			// get_data : function(txt){
			// 	return frappe.db.get_link_options("Territory", txt, {
			// 		'company' : frappe.query_report.get_filter_value('company')
			// 	})
			// }
		},
	// 	{
	// 		"fieldname": "warehouse",
	// 		"label": __("Warehouse"),
	// 		"fieldtype": "Link",
	// 		"width": "80",
	// 		"options": "Warehouse",
	// 		get_data : function(txt){
	// 			return frappe.db.get_link_options("Warehouse", txt, {
	// 				company: frappe.query_report.get_filter_value('company')
	// 			})
	// 		}
	// 	},
		{
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Customer Group",
			get_data : function(txt){
				return frappe.db.get_link_options("Customer Group", txt, {
					company: frappe.query_report.get_filter_value('company')
				})
			}
		},
	]
};


