# Copyright (c) 2013, Codes Soft and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe import _
# from frappe.utils import cstr
from frappe.utils import getdate, cstr
import json	
import frappe
import ast
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
from frappe.utils import getdate, cstr, fmt_money
import json
import frappe
from datetime import *
from dateutil.relativedelta import *
import calendar
from datetime import date, timedelta
from frappe.utils import add_days, getdate, formatdate, nowdate ,  get_first_day, date_diff, add_years  , flt, cint, getdate, now


def execute(filters=None):
	if not filters:
		filters = {}

	conditions = get_conditions(filters)
	data = []
	columns = get_columns(conditions , filters)
	data  = get_data_normal(conditions = conditions )
	return columns , data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.attendance_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.attendance_date <=  '{}' ".format(filters.get("to_date"))
	if filters.get("status"):
		conditions += " and s.status =  '{}' ".format(filters.get("status"))
	if filters.get("employee"):
		conditions += " and s.employee =  '{}' ".format(filters.get("employee"))

	return conditions




def get_data_normal(conditions   = "", filters = {}):
		data =  frappe.db.sql(""" select s.employee, s.status , s.attendance_date , s.docstatus ,  
			s.early_exit ,   s.early_exit_time ,  s.late_exit ,   s.late_exit_time  , 
			s.late_entry , 
			s.late_entry_time ,  s.early_entry ,  s.early_entry_time ,
			s.late_entry_time_hours , s.early_entry_time_hours , s.timein , 
			s.first_time_in_time ,  s.timeout ,  s.attendance_day ,
			s.last_log_type , s.early_entry_time_hours , s.timein , 
			s.early_exit_time_hours ,  s.late_exit_time_hours ,  s.last_update_out_time ,
			s.working_hours , s.actual_working_hours	 
			from `tabAttendance` s
			where 1=1 {}  order by s.attendance_date desc """.format(conditions ), as_dict=1 , debug = True)
		return data

def get_columns(conditions  = "" ,  filters = {}):
	columns = [
		{
		"fieldname": "sn",
		"label": "SNO",
		"fieldtype": "Data",
		"width": 100
		},

		{
		"fieldname": "employee",
		"label": "Employee ID",
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "employee_name",
		"label": "Name",
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "status",
		"label": _("Status"),
		"fieldtype": "Data",
		"width": 100
		},
		{

		"fieldname": "attendance_date",
		"label": _("Date"),
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "docstatus",
		"label": _("DocStatus"),
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "first_time_in_time",
		"label": _("First TimeIn"),
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "timein",
		"label": _("In"),
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "timeout",
		"label": _("OUT"),
		"fieldtype": "Data",
		"width": 100
		},


		{
		"fieldname": "early_entry",
		"label": _("Early Entry"),
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "early_entry_time",
		"label": _("Time"),
		"fieldtype": "Data",
		"width": 100
		},

		{
		"fieldname": "early_entry_time_hours",
		"label": _("Early Hours"),
		"fieldtype": "Data",
		"width": 100
		},





		{
		"fieldname": "early_exit",
		"label": _("Early Exit"),
		"options" : "Data",
		"width": 100
		},
		{
		"fieldname": "early_exit_time",
		"label": _("Time"),
		"fieldtype": "Data",
		"width": 100
		},

		{
		"fieldname": "early_exit_time_hours",
		"label": _("Early Hours"),
		"fieldtype": "Data",
		"width": 100
		},


		{
		"fieldname": "late_entry",
		"label": _("Late Entry"),
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "late_entry_time",
		"label": _("Time"),
		"fieldtype": "Data",
		"width": 100
		},

		{
		"fieldname": "late_entry_time_hours",
		"label": _("Late Hours %"),
		"fieldtype": "Data",
		"width": 100
		},





		{
		"fieldname": "late_exit",
		"label": _("Late Exit"),
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "late_exit_time",
		"label": _("Time"),
		"fieldtype": "Data",
		"width": 100
		},

		{
		"fieldname": "late_exit_time_hours",
		"label": _("Late Hour"),
		"fieldtype": "Data",
		"width": 100
		},



		{
		"fieldname": "last_log_type",
		"label": _("Last Logtype"),
		"fieldtype": "Data",
		"width": 100
		},


		{
		"fieldname": "last_update_out_time",
		"label": _("Last Update Out Time"),
		"fieldtype": "Data",
		"width": 100
		},
		{
		"fieldname": "working_hours",
		"label": _("Total Working Hours"),
		"options" : "Data",
		"width": 100
		},
		{
		"fieldname": "actual_working_hours",
		"label": _("Actual Working Hours"),
		"options" : "Data",
		"width": 100
		},
	]

	return columns
