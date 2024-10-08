// Copyright (c) 2016, ClefinCode and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Ledger POS Invoice"] = {
	"filters": [
                {
                        "fieldname":"company",
                        "label": __("Company"),
                        "fieldtype": "Link",
                        "options": "Company",
                        "default": frappe.defaults.get_user_default("Company"),
                        "reqd": 1
                },
                {
                        "fieldname":"from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.get_today(), //frappe.datetime.add_months(frappe.datetime.get_today(), -1),
                        "reqd": 1
                },
                {
                        "fieldname":"to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.get_today(),
                        "reqd": 1
                },
                {
                        "fieldname":"item_code",
                        "label": __("Item"),
                        "fieldtype": "Link",
                        "options": "Item",
                        "get_query": function() {
                                return {
                                        query: "erpnext.controllers.queries.item_query"
                                }
                        }
                },
                {
                        "fieldname":"batch",
                        "label": __("Batch"),
                        "fieldtype": "Link",
                        "options": "Batch"
                }
        ]
};
