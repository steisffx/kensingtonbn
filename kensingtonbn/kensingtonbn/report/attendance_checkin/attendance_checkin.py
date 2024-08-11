# Copyright (c) 2013, ClefinCode and contributors
# For license information, please see license.txt

# import frappe

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

	columns, data = [], []
	columns = get_columns()


	conditions = get_conditions(filters)
	data = get_data(filters, conditions)
	return columns, data



def get_columns():
	columns = [
		{
			"fieldname": "employee_id",
			"label":  _("Em ID"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 100,
		},
		{
			"fieldname": "employee_name",
			"label":  _("Em Name"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "attendance_date",
			"label":  _("Attendance Date"),
			"fieldtype": "Data",
			"width": 100,
		},


		{
			"fieldname": "time",
			"label":  _("Time"),
			"fieldtype": "Data",
			"width": 100,
		},

		{
			"fieldname": "log_type",
			"label":  _("Log Type"),
			"fieldtype": "Data",
			"width": 100,
		},

	

	]

	return columns


def get_conditions(filters):
	conditions = ""

	if filters.get("employee"):
		conditions += " and c.employee = '{}' ".format(filters.get("employee"))

	if filters.get("from_date"):
		conditions += " and DATE(c.time)  >= '{}' ".format(filters.get("from_date"))

	if filters.get("to_date"):
		conditions += " and DATE(c.time)  <= '{}' ".format(filters.get("to_date"))



	return conditions






def get_data(filters, conditions):
	data = frappe.db.sql("""
		select  c.employee as employee_id, c.employee_name as employee_name , c.log_type as log_type ,
		DATE(c.time) as attendance_date	, 	   
		TIME(c.time)  as time
		from `tabEmployee Checkin` c where 1=1  {conditions}
		""".format(conditions=conditions), as_dict=1 , debug=True)
	return data




