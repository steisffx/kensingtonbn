# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr
import numpy as np
import pandas as pd
import datetime
import json


def execute(filters=None):
	if not filters:
		filters = {}



	columns, data = get_columns(), []
	conditions = get_conditions(filters)
	data = get_data(filters, conditions)

	




	return columns, data


def get_data(filters, conditions):

	data = frappe.db.sql(""" 
			SELECT  sum(so.total) as  sales , 
		    so.territory as territory,  so.customer as customer, so.customer_name as customer_name,
			so.customer_group as customer_group	, so.territory as territory , so.set_warehouse as warehouse
		    from `tabSales Order` as so		      
			where so.docstatus=1 {} 
		""".format(conditions), as_dict=True, debug=True)

	# data = frappe.db.sql(""" 
	# 		SELECT  sum(so.total) as  sales , 
	# 	    so.territory as territory,  so.customer as customer, so.customer_name as customer_name,
	# 		so.customer_group as customer_group	, so.territory as territory , so.set_warehouse as warehouse	,
	# 		SUM(pe.paid_amount) as payment_received   
	# 	    from `tabSales Order` as so
	# 	    LEFT JOIN
	# 	    `tabPayment Entry` AS pe ON pe.reference_name = so.name
		      
	# 		where so.docstatus=1 {} 
	# 	""".format(conditions), as_dict=True, debug=True)


	return data


def get_columns():
	columns = [
		{
			"fieldname": "sales",
			"label":  _("Total Sales"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "payment_received",
			"label":  _("Payment Received"),
			"fieldtype": "Data",
			"width": 150,
		},

		{
			"fieldname": "customer",
			"label":  _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},


		{
			"fieldname": "customer_name",
			"label":  _("Customer"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "customer_group",
			"label":  _("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"width": 150,
		},
	
	

		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 100,
		},


		# {
		# 	"fieldname": "branch",
		# 	"label": _("Branch"),
		# 	"fieldtype": "Link",
		# 	"options": "Branch",
		# 	"width": 100,
		# },
		# {
		# 	"fieldname": "department",
		# 	"label": _("Department"),
		# 	"fieldtype": "Link",
		# 	"options": "Department",
		# 	"width": 100,
		# },
		{
			"fieldname": "territory",
			"label": _("Territory"),
			"fieldtype": "Link",
			"options": "Territory",
			"width": 100,
		},

	]

	return columns
def get_conditions(filters):
	conditions = ""
	if filters.company:
		conditions += " and so.company = '{}' ".format(filters.company)

	if filters.from_date:
		conditions += " and so.transaction_date BETWEEN '{}' AND '{}'".format(filters.from_date, filters.to_date)

	if filters.customer:
		conditions += " and so.customer  = '{}' ".format(filters.customer)
	
	if filters.customer_group:
		conditions += " and so.customer_group = '{}' ".format(filter.customer_group)

	if filters.territory:
		conditions += " and so.territory = '{}' ".format(filter.territory)


	# if filters.department:
	# 	conditions += " and si.department  = '{}' ".format(filters.department)
	
	# if filters.branch:
	# 	conditions += " and si.branch = '{}'  ".format(filters.sales_person)
	

	return conditions












