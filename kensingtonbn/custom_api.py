# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, has_gravatar, cint

from frappe.model.document import Document
import json

from frappe.utils.background_jobs import enqueue



@frappe.whitelist()
def get_payment_mode_credit_detail(invoice_id):
	data = []
	data_record = frappe.db.get_list('Sales Invoice Payment',
	filters={
		'mode_of_payment': 'Credit Card',
		'parent' : invoice_id,
		'parenttype' : 'Sales Invoice'
	},
	fields=['parent' , 'mode_of_payment', 'amount'],
	)
	if data_record:
		return data_record
	else:
		return data




@frappe.whitelist(allow_guest=True)
def update_forcely_item_values(method_name = "Moving Average", item = ""):
	frappe.db.set_value('Item', item, 'valuation_method', method_name)
	frappe.db.commit()









@frappe.whitelist(allow_guest = True)
def generate_item_update_long():
	try:
		enqueue("kensingtonbn.custom_api.item_updating", queue='long', timeout=1500)
		return "Queued"
	except Exception as e:
		print("Process terminated: {}".format(e))
		error_message = frappe.get_traceback() + "\nErrorItem: {}".format(str(e))
		frappe.log_error(error_message, "Error Item Updating")



def item_updating():
	data = frappe.db.sql(""" SELECT i.name as name  
							FROM `tabItem` as i
							WHERE 1=1 and i.valuation_method IS NULL order by valuation_method """, as_dict=1)
	if data:
		for i in data:
			if i.get("name"):
				try:
					frappe.db.set_value('Item', i.get("name"), 'valuation_method', 'Moving Average')
				except Exception as e:
					error_message = frappe.get_traceback() + "\nError updating item {}: {}".format(i['name'], str(e))
					frappe.log_error(error_message, "Error in item updating.")
		frappe.db.commit()



@frappe.whitelist(allow_guest = True)
def item_updating_list():
	data = frappe.db.sql(""" SELECT i.name as name  , i.valuation_method as valuation_method , i.docstatus as status
							FROM `tabItem` as i
							WHERE 1=1 and  i.valuation_method IS NULL order by i.valuation_method asc  """, as_dict=1)
	return data
	if data:
		for i in data:
			if i.get("name"):
				try:
					frappe.db.set_value('Item', i.get("name"), 'valuation_method', 'Moving Average')
				except Exception as e:
					error_message = frappe.get_traceback() + "\nError updating item {}: {}".format(i['name'], str(e))
					frappe.log_error(error_message, "Error in item updating.")
		frappe.db.commit()
