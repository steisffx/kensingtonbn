# Copyright (c) 2013, ClefinCode and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_pos_sales_payment_data(filters)
	return columns, data


def get_columns():
	return [
		_("Name") + ":Link/POS Invoice:125",
		_("Date") + ":Date:80",
		_("POS Profile") + ":Data:80",
		_("Cash") + ":Currency/currency:120",
		_("Credit Card") + ":Currency/currency:120",
		#_("Paid Total") + ":Currency/currency:120",
		_("Grand Total") + ":Currency/currency:120",
		_("Discount Amount") + ":Currency/currency:120",
		_("Total Quantity") + ":Data:120",
		_("Status") + ":Data:120"
	]

def get_pos_sales_payment_data(filters):
	sales_invoice_data = get_pos_invoice_data(filters)
	data = [
		[
			row['name'],
			row['posting_date'],
			row['pos_profile'],
			row['Cash'],
			row['Credit_Card'],
			#row['paid_amount'],
			row['grand_total'],
			row['discount_amount'],
			row['total_qty'],
			row['status']
		] for row in sales_invoice_data]

	return data



def get_conditions(filters):
	conditions = []
	if filters.get("from_date"):
		conditions.append(["posting_date", ">=", filters.get("from_date")])
	if filters.get("to_date"):
		conditions.append(["posting_date", "<=", filters.get("to_date")])
	if filters.get("company"):
		conditions.append(["company", "=", filters.get("company")])
	if filters.get("customer"):
		conditions.append(["customer", "=", filters.get("customer")])
	if filters.get("cashier"):
		conditions.append(["pos_profile", "=", filters.get("cashier")])
	return conditions


def get_pos_invoice_data(filters):
	conditions = get_conditions(filters)
	conditions.append(["docstatus", "=", "1"])
	conditions.append(["status", "!=", "Draft"])
	conditions.append(["status", "!=", "Cancelled"])
	pos_invoices = frappe.db.get_all("POS Invoice", filters = conditions, fields = ['name', 'paid_amount', 'grand_total'])
	result = []
	for pos_invoice in pos_invoices:
		subselect = """IFNULL(res.Cash, 0) as Cash, """
		if pos_invoice['paid_amount'] > pos_invoice['grand_total']:
			subselect = """IFNULL(IF(res.Cash > res.grand_total, res.grand_total - IFNULL(res.Credit_Card, 0) ,res.Cash), 0) as Cash,"""
		if pos_invoice['paid_amount'] < pos_invoice['grand_total']:
			subselect = """IFNULL(IF(res.Cash > 0, res.Cash + (res.grand_total - res.paid_amount), res.Cash), 0) as Cash,"""
		res = frappe.db.sql('''SELECT res.name, res.posting_date, res.pos_profile,  
									{subselect}
									res.grand_total,
									res.discount_amount,  res.total_qty, res.status
									FROM 
									(SELECT pos.name as name, pos.posting_date as posting_date, pos.pos_profile as pos_profile, 
									 MAX(CASE WHEN pos_pay.mode_of_payment = "Cash" THEN amount END) "Cash" ,
									 MAX(CASE WHEN pos_pay.mode_of_payment = "Credit Card" THEN amount END) "Credit_Card" ,
									 pos.paid_amount as paid_amount, 
									 pos.grand_total as grand_total,
									 pos.discount_amount as discount_amount,  pos.total_qty as total_qty, pos.status as status
									 FROM `tabPOS Invoice` AS pos
									 INNER JOIN `tabSales Invoice Payment` AS pos_pay ON pos.name= pos_pay.parent
									 WHERE 
									 pos.name = '{name}'
									 AND pos.status !='Draft' AND pos.status != 'Cancelled'
									 AND pos.docstatus =1 
									 GROUP BY pos.name) as res
							'''.format(subselect = subselect, name=pos_invoice['name']), filters, as_dict=1
							)
		res[0]['Credit_Card'] = res[0]['grand_total'] - res[0]['Cash']
		#res[0]['paid_amount'] = res[0]['Cash'] + res[0]['Credit_Card']

		result += res
	return result