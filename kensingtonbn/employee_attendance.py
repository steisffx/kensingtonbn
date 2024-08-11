# -*- coding: utf-8 -*-
# Copyright (c) 2021, Shahid and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import ast

import frappe

from frappe.utils import getdate, nowdate, get_first_day, get_last_day
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr

from datetime import datetime, date, timedelta
from datetime import *
from dateutil.relativedelta import *
import dateutil.relativedelta
from frappe.utils.background_jobs import enqueue
import json



@frappe.whitelist(allow_guest=True)
def a():
	return "Hellow"



@frappe.whitelist(allow_guest=True)
def generate_attendance_long(data= None):
	attendance = None
	data = frappe.request.data
	attendance = data
	try:
		frappe.log_error(" data -  json {} ".format(attendance))
		enqueue("kensingtonbn.employee_attendance.generate_attendance", attendance=attendance, queue='long', timeout=1500)
		error_message = frappe.get_traceback()+"\n{}\n{}".format(attendance,str(attendance))
		frappe.log_error(error_message, " Try Block Queque : ")
		return "Queued"

	except Exception as e:
		print ("Process terminate : {}".format(e))
		error_message = frappe.get_traceback()+"\n{}\n{}".format(attendance,str(e))
		frappe.log_error(error_message, "Error Exception Queque ")


@frappe.whitelist(allow_guest=True)
def generate_attendance(attendance = None):
	attendance = json.loads(attendance)
	# frappe.log_error("Response ", "Data {} ".format(attendance))

	# attendance = b'["<Attendance>: 888 : 2023-06-25 08:33:10 (1, 0)", "<Attendance>: 888 : 2023-06-25 08:40:40 (1, 0)", "<Attendance>: 888 : 2023-07-02 10:53:15 (1, 0)", "<Attendance>: 888 : 2023-07-02 10:56:50 (1, 0)", "<Attendance>: 888 : 2023-07-02 11:18:56 (1, 1)", "<Attendance>: 888 : 2023-07-02 13:52:42 (1, 1)", "<Attendance>: 999 : 2023-07-02 14:40:03 (1, 0)", "<Attendance>: 888 : 2023-07-02 14:40:58 (1, 1)", "<Attendance>: 888 : 2023-07-02 14:45:19 (1, 1)"]'
	# attendance = json.loads(attendance)

	try:
		for a in attendance:
			print("We are in attendance Testing for loop in python erp file. ")
			frappe.log_error(a, " Attendance Data")
			# biometric = a.get("b_id")
			# date = a.get("b_date")
			# time = a.get("b_time")
			# date_time = date+" "+time
			a = str(a).split()
			print("a split date")


			biometric = str(a[1])
			date = a[3]
			time = a[4]
			date_time = date+" "+ time

			log_detail = a[6]
			log_value = int(log_detail.replace(')', '').replace(',', ''))
			log_type = "IN"


			if log_value == 0:
				log_type = "IN"
				print(" I am one. ")
			else:
				print(" I am 0 ")
				log_type = "OUT"
			emp = frappe.db.get_value("Employee", {"status": "Active", "attendance_device_id": biometric}, "name")
			if emp:
				att = frappe.db.get_value("Employee Checkin", {"employee": emp, "time": date_time}, "name")
				if not att:
					try:
						new_att = frappe.new_doc("Employee Checkin")
						new_att.employee = emp
						new_att.time = date_time
						new_att.log_type = log_type
						new_att.insert(ignore_permissions=True)
					except Exception as e:
						print ("Process terminate : {}".format(e))
						error_message = frappe.get_traceback()+"\n{}\n{}".format(str(a),str(e))
						frappe.log_error(error_message, "Checkin Creation Error from Desktop App")
	except Exception as e:
		print ("Process terminate : {}".format(e))
		error_message = frappe.get_traceback()+"\n{}\n{}".format(attendance,str(e))
		frappe.log_error(error_message, "Generate Attendance Error from Desktop App")



@frappe.whitelist(allow_guest = True)
def get_attendance_from_machine(data = None):
	try:
		if frappe.request.data:		
			bbb = json.loads(frappe.request.data)
			frappe.log_error("Data comming is {} ".format(bbb))
			try:
				attendance = json.loads(data)
				for a in attendance:
					a = str(a).split()
					biometric = str(a[1])
					date = a[3]
					time = a[4]
					date_time = date+" "+time

					emp = frappe.db.get_value("Employee", {"status": "Active", "biometric_id": biometric}, "name")
					if emp:
						att = frappe.db.get_value("Attendance Checkin", {"employee": emp, "time": date_time}, "name")
						if not att:
							new_att = frappe.new_doc("Attendance Checkin")
							new_att.employee = emp
							new_att.time = date_time
							new_att.insert(ignore_permissions=True)
			except Exception as e:
				print ("Process terminate : {}".format(e))
				error_message = frappe.get_traceback()+"\n{}\n{}".format(attendance,str(e))
				frappe.log_error(error_message, "Generate Attendance Error from Desktop App")

		else:
			frappe.log_error("Data request.data False ")

	except Exception as e:
		error_message = frappe.get_traceback() + "\n  Machine Data  {}  ".format(str(e))
		frappe.log_error(error_message, "Machine Error Exception ")
























