# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, get_datetime , cstr,formatdate, get_datetime, getdate, nowdate , today

import datetime
from datetime import time
import pandas as pd

@frappe.whitelist(allow_guest=True)
def attendance_schedular_background_job():
	employee_list = frappe.db.sql("""
			select e.name as employee ,  e.status as em_status , s.status as shift_status , 
				s.day_name as day_name , s.day_no as shift_day_no , 
				WEEKDAY(CURDATE()) as day_number
				from `tabEmployee` e
				inner join `tabEmployee Shift Timing` s
				on e.name = s.parent
				where  1=1 and e.date_of_joining <= '{}' and e.status = 'Active'
		""".format(today() , as_dict = 1))
	for e in employee_list:

		employee = e[0]
		shift_status = e[2]
		day_name = e[3]
		shift_day_no = e[4]
		day_number = e[5]

		frappe.log_error("attendance_schedular_background_job", " {} {} {} {} {}  ".format(employee,shift_status,day_name,shift_day_no,day_number))
		if frappe.db.get_value('Attendance', {'attendance_date': today(),'employee': employee}):
			frappe.log_error(" user_attendance ", " user_attendance Found.   {}  ")
			user_attendance = frappe.db.get_value('Attendance', {
			'attendance_date': today(),
			'employee': employee,
			'last_log_type' : 'OUT'
			},
			['name' ,  'employee' , 'last_log_type', 'last_update_out_time' , 'timeout' , 'timein'],
			as_dict=1)
			if user_attendance:
				frappe.log_error(" user_attendance ", " user_attendance 1  {}  ".format(user_attendance.last_log_type))
				if user_attendance.get("last_log_type") == 'OUT' and user_attendance.get("timeout") and user_attendance.get("timein"):
					print("Please submitted the records. ")
					attendance_submitted(user_attendance.name)
					frappe.log_error(" user_attendance ", " uPlease submitted the records  ")

				else:
					frappe.log_error(" user_attendance ", " User attendance has not today Attendance   ")
					print("So we are not submitting attendance. ")
					send_email_forget_checkout(user_attendance.employee)
	
			else:
				frappe.log_error(" user_attendance ", " User attendance Not found. 2    ")
				create_attendance_record_absent(employee , day_name , day_number)
		else:
			frappe.log_error(" user_attendance ", " User attendance Not found.   ")
			if check_today_holiday():
				print("Yes holiday found. ")
				print("Please marked attendance as General Holiday")
				frappe.log_error(" user_attendance ", " Please marked attendance as General Holida   ")
				create_attendance_record_holiday(employee , day_name , day_number )
			else:
				print("Sorry holidays not found. ")
				frappe.log_error(" user_attendance ", " Sorry holidays not found   ")

				if check_leave_allocation(employee):
					print("Leave found. please marked as Leave. ")
					frappe.log_error(" user_attendance ", " Leave found. please marked as Leav  ")
					create_attendance_record_user_leave(employee , day_name , day_number)
				else:
					print("check_leave_allocation Not Found. ")
					frappe.log_error(" user_attendance ", " heck_leave_allocation Not Found  ")
					create_attendance_record_absent(employee , day_name , day_number)


def check_today_holiday():
	result = False
	if frappe.db.get_value('Holiday', {'holiday_date': today()}):
		print("today is holiday please marked attendance as holiday")
		result = True
	return result

def check_leave_allocation(employee):
	print("check_leave_allocation")
	result = False
	if frappe.db.get_value('Leave Allocation', 
		{'employee': employee,
		'from_date': ['>=',today()], 
		'to_date': ['<=',today()],
		'docstatus': ['=','1'],		
		}):
		print("today is holiday please marked attendance as holiday")
		result = True
	return result

def attendance_submitted(doc_name):
	print("attendance_submitted")
	doc_attendance = frappe.get_doc('Attendance', doc_name )
	doc_attendance.docstatus =  1
	try:
		doc_attendance.save(
		ignore_permissions=True, # ignore write permissions during insert
		ignore_version=True # do not create a version record
		)
	except Exception as e:
		print ("Process terminate : {}".format(e))
		error_message = frappe.get_traceback()+"\n{}".format(str(e))
		frappe.log_error(error_message, "Error in  attendance_submitted Schedular .  ")

def send_email_forget_checkout(employee):
	print("sending email but in queque should. ")

def create_attendance_record_holiday(employee , attendance_day , attendance_day_no):

	doc_attendance = frappe.new_doc('Attendance')
	doc_attendance.employee = employee
	doc_attendance.status = 'General Holiday'
	doc_attendance.attendance_date = today()
	doc_attendance.early_exit =  0
	doc_attendance.early_exit_time = "00:00:00"
	doc_attendance.late_exit =  0
	doc_attendance.late_exit_time = "00:00:00"
	doc_attendance.late_entry =   1
	doc_attendance.late_entry_time = "00:00:00"
	doc_attendance.early_entry =  0
	doc_attendance.early_entry_time =  "00:00:00"
	doc_attendance.late_entry_time_hours = 0.0
	doc_attendance.early_entry_time_hours = 0.0
	doc_attendance.timein  = "00:00:00"
	doc_attendance.attendance_day  = attendance_day
	doc_attendance.attendance_day_no  = attendance_day_no
	doc_attendance.last_log_type  = ""
	doc_attendance.docstatus  = 1
	try:
		doc_attendance.save(
		ignore_permissions=True, # ignore write permissions during insert
		ignore_links=True, # ignore Link validation in the document
		ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
		ignore_mandatory=True # insert even if mandatory fields are not set
		)
	except Exception as e:
		print ("Process terminate : {}".format(e))
		error_message = frappe.get_traceback()+"\n{}\n{}".format(str(e))
		frappe.log_error(error_message, "create_attendance_record_holiday  ")

def create_attendance_record_user_off_day(employee , attendance_day , attendance_day_no):
	doc_attendance = frappe.new_doc('Attendance')
	doc_attendance.employee = employee
	doc_attendance.status = 'Off'
	doc_attendance.attendance_date = today()
	doc_attendance.early_exit =  0
	doc_attendance.early_exit_time = "00:00:00"
	doc_attendance.late_exit =  0
	doc_attendance.late_exit_time = "00:00:00"
	doc_attendance.late_entry =   1
	doc_attendance.late_entry_time = "00:00:00"
	doc_attendance.early_entry =  0
	doc_attendance.early_entry_time =  "00:00:00"
	doc_attendance.late_entry_time_hours = 0.0
	doc_attendance.early_entry_time_hours = 0.0
	doc_attendance.timein  = "00:00:00"
	doc_attendance.attendance_day  = attendance_day
	doc_attendance.attendance_day_no  = attendance_day_no
	doc_attendance.last_log_type  = ""
	doc_attendance.docstatus  = 1
	try:
		frappe.log_error(error_message, "create_attendance_record_user_off_day Insert  ")

		doc_attendance.insert(
		ignore_permissions=True, # ignore write permissions during insert
		ignore_links=True, # ignore Link validation in the document
		ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
		ignore_mandatory=True # insert even if mandatory fields are not set
		)

		doc_attendance.save(
		ignore_permissions=True, # ignore write permissions during insert
		ignore_links=True, # ignore Link validation in the document
		ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
		ignore_mandatory=True # insert even if mandatory fields are not set
		)
		frappe.log_error(error_message, "create_attendance_record_user_off_day Save  ")

	except Exception as e:
		print ("Process terminate : {}".format(e))
		error_message = frappe.get_traceback()+"\n{}".format(str(e))
		frappe.log_error(error_message, "create_attendance_record_user_off_day  ")

def create_attendance_record_user_leave(employee , attendance_day , attendance_day_no):
	doc_attendance = frappe.new_doc('Attendance')
	doc_attendance.employee = employee
	doc_attendance.status = 'On Leave'
	doc_attendance.attendance_date = today()
	doc_attendance.early_exit =  0
	doc_attendance.early_exit_time = "00:00:00"
	doc_attendance.late_exit =  0
	doc_attendance.late_exit_time = "00:00:00"
	doc_attendance.late_entry =   1
	doc_attendance.late_entry_time = "00:00:00"
	doc_attendance.early_entry =  0
	doc_attendance.early_entry_time =  "00:00:00"
	doc_attendance.late_entry_time_hours = 0.0
	doc_attendance.early_entry_time_hours = 0.0
	doc_attendance.timein  = "00:00:00"
	doc_attendance.attendance_day  = attendance_day
	doc_attendance.attendance_day_no  = attendance_day_no
	doc_attendance.last_log_type  = ""
	doc_attendance.docstatus  = 1
	try:
		doc_attendance.save(
		ignore_permissions=True, # ignore write permissions during insert
		ignore_links=True, # ignore Link validation in the document
		ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
		ignore_mandatory=True # insert even if mandatory fields are not set
		)
	except Exception as e:
		print ("Process terminate : {}".format(e))
		error_message = frappe.get_traceback()+"\n{}".format(str(e))
		frappe.log_error(error_message, "create_attendance_record_user_leave  ")




def create_attendance_record_absent(employee , attendance_day , attendance_day_no):

	doc_attendance = frappe.new_doc('Attendance')
	doc_attendance.employee = employee
	doc_attendance.status = 'Absent'
	doc_attendance.attendance_date = today()
	doc_attendance.early_exit =  0
	doc_attendance.early_exit_time = "00:00:00"
	doc_attendance.late_exit =  0
	doc_attendance.late_exit_time = "00:00:00"
	doc_attendance.late_entry =   1
	doc_attendance.late_entry_time = "00:00:00"
	doc_attendance.early_entry =  0
	doc_attendance.early_entry_time =  "00:00:00"
	doc_attendance.late_entry_time_hours = 0.0
	doc_attendance.early_entry_time_hours = 0.0
	doc_attendance.timein  = "00:00:00"
	doc_attendance.attendance_day  = attendance_day
	doc_attendance.attendance_day_no  = attendance_day_no
	doc_attendance.last_log_type  = ""
	doc_attendance.docstatus  = 1
	try:
		doc_attendance.insert(
		ignore_permissions=True, # ignore write permissions during insert
		ignore_links=True, # ignore Link validation in the document
		ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
		ignore_mandatory=True , # insert even if mandatory fields are not set
		)
	except Exception as e:
		print ("Process terminate : {}".format(e))
		error_message = frappe.get_traceback()+"\n{}".format(str(e))
		frappe.log_error(error_message, "create_attendance_record_absent  ")

