# Copyright (c) 2013, ClefinCode and contributors
# For license information, please see license.txt

import frappe
from frappe import _

 
def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_employee_activity_data(filters)
	return columns, data


def get_columns():
	return [
		_("Name") + ":Data:150",
		_("Description") + ":data:150",
		_("Notes") + ":Data:150",
		_("Accept Date") + ":Date:150",
		_("Start Date") + ":Date:150",
		_("End Date") + ":Date:150",
		_("Activity Total Time") + ":Data:210"
	]


def get_conditions(filters):
	conditions = ""
	if filters.get("assigned_date"):
		conditions += "and assigned_date = %(assigned_date)s"
	if filters.get("assigned_user"):
		conditions += "and assigned_user = %(assigned_user)s"
	return conditions


def get_employee_activity_data(filters):
	conditions = get_conditions(filters)
	query = """ select parent, description, note, activity_accept_date, activity_start_date, activity_end_date, total_activity_time from `tabEmployee Activity Item` 
				where name is not null %s """

	data = frappe.db.sql(query  % conditions, filters, as_list=1)

	for idx, x in enumerate(data):
		total = 0.0
		if x[5]:
			diff = x[5] - x[4]
			days, seconds = diff.days, diff.seconds
			hours = days * 24 + seconds // 3600
			minutes = (seconds % 3600) // 60
			seconds = seconds % 60
			if days and hours and minutes:
				total = str(days) +" Days "+ str(hours)+" Hours "+ str(minutes)+" Minutes"
			elif hours and minutes:
				total = str(hours)+" Hours "+ str(minutes)+" Minutes"
			elif hours:
				total = str(hours)+" Hours"
			elif minutes:
				total = str(minutes)+" Minutes"
			else:
				total = 0.0

			x[6]=total

	return data