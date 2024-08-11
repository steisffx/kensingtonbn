# Copyright (c) 2022, ClefinCode and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_purchase_receipt

class ContainerReconciliation(Document):
	pass

@frappe.whitelist(allow_guest = True)
def get_reconcile_result(doc_name):	
	invoice_items = get_invoice_items(doc_name)
	items_after_merge_with_pr_items = merge_items_with_pr_items(doc_name)
	combined_items_and_pr_items = combine_similar_items_after_merge(items_after_merge_with_pr_items)
	
	not_match_items = get_not_match_items_with_invoice_items(combined_items_and_pr_items , invoice_items)
	not_match_invoice_items = get_not_match_invoice_items_with_items(combined_items_and_pr_items , invoice_items)
	match_items = get_match_items_with_invoice_items(combined_items_and_pr_items , invoice_items)
	match_invoice_items = get_match_invoice_items_with_items(combined_items_and_pr_items , invoice_items)
	match_items_result , missing_qty , extra_qty   = compare_qty(match_items ,match_invoice_items )

	
	return{		
		'not_match_items' : not_match_items ,
		'not_match_invoice_items' : not_match_invoice_items ,		
		'missing_qty'  : missing_qty,
		'extra_qty' : extra_qty		
		}

def get_items(doc_name):	
	items = frappe.get_all("Container Reconciliation Item",
	fields=["item_code" ,"item_name" , "qty" , "uom" , "conversion_factor" ,  "stock_uom" , "warehouse"  , "batch_no" , "best_value_date" , 'barcode' ],
	filters = {"parent":doc_name})
	return items

def get_invoices(doc_name):	
	invoices = frappe.get_all("Container Reconciliation Invoice",fields=["purchase_invoice"],filters = {"parent":doc_name})
	return invoices		

def get_invoice_items(doc_name):
	invoices = get_invoices(doc_name)
	invoices_items_list = []	
	for invoice in invoices:			
		invoice_items = frappe.db.sql (""" 
		SELECT item_code , qty , uom , conversion_factor , batch_no
		FROM `tabPurchase Invoice` AS tabPurchaseInvoice
		INNER JOIN `tabPurchase Invoice Item` AS  tabPurchaseInvoiceItem ON tabPurchaseInvoice.name = tabPurchaseInvoiceItem.parent
		WHERE tabPurchaseInvoice.name = %s
		""" , invoice.purchase_invoice , as_dict = True)
		for item in invoice_items:
			if item['batch_no'] == '':
				item['batch_no'] = None
			match = 0
			if 	invoices_items_list:							
				for i in invoices_items_list:
					if item['item_code'] == i['item_code'] and item['batch_no'] == i['batch_no'] and item['uom'] == i['uom']:												
						i['qty'] += item['qty']
						match = 1
				if match != 1:
					invoices_items_list.append(item)					
			else:
				invoices_items_list.append(item)
	return invoices_items_list

def get_not_match_items_with_invoice_items(items , invoice_items):
	not_match_items = []	
	for item in items:
		# item['qty'] = item['qty'] * item['conversion_factor']
		Match = 0
		for item2 in invoice_items:
			# if item['item_code'] == item2['item_code'] =='Yazoo Chocolate 1L':
			# 	x=1
			if item['item_code'] == item2['item_code'] and item['batch_no'] == item2['batch_no']:				
				Match = 1
				# break			
		if Match != 1:						
			not_match_items.append(item)
	
	return not_match_items

def get_not_match_invoice_items_with_items(items , invoice_items):	
	not_match_invoice_items = []	
	for item in invoice_items:
		item['qty'] = item['qty'] * item['conversion_factor']
		Match = 0
		for item2 in items:
			if item2['item_code'] == item['item_code'] and item2['batch_no'] == item['batch_no'] :				
				Match = 1				
		if Match != 1:						
			not_match_invoice_items.append(item)				
	
	return not_match_invoice_items

def get_match_items_with_invoice_items(items , invoice_items):		
	match_items = []	
	for item in items:
		for i in invoice_items:
			if item['item_code'] == i['item_code'] and item['batch_no'] == i['batch_no'] :							
				match_items.append(item)
	
	return match_items

def get_match_invoice_items_with_items(items , invoice_items):	
	match_invoice_items = []	
	for i in invoice_items:
		for item in items:
			if i['item_code'] == item['item_code'] and i['batch_no'] == item['batch_no']:								
				match_invoice_items.append(i)
				break
	
	return match_invoice_items

def compare_qty(match_items , match_invoice_items ):			
	match_items_result = []
	missing_qty = []
	extra_qty = []
	# match_items = combine_items_before_compare_qty(match_items)	
	for item in match_items:		
		for item2 in match_invoice_items :			
			required_qty = item2['qty']
			receive_qty = item['qty']	
			if item['item_code'] == item2['item_code'] and item['batch_no'] == item2['batch_no'] and receive_qty == required_qty :
				match_items_result.append(item)				
			if item['item_code'] == item2['item_code']  and item['batch_no'] == item2['batch_no'] and receive_qty != required_qty :
				if receive_qty > required_qty:
					item2['qty'] = required_qty										
					item2['container_qty'] = receive_qty					
					item2['qty_extra'] = receive_qty - required_qty					
					item2['best_value_date'] = item['best_value_date']
					extra_qty.append(item2)
					
				if receive_qty < required_qty:
					item2['qty'] = required_qty						
					item2['container_qty'] = receive_qty					
					item2['qty_missing'] = required_qty - receive_qty					
					item2['best_value_date'] = item['best_value_date']
					missing_qty.append(item2)
					
	
	return match_items_result , missing_qty , extra_qty

# def combine_items_before_compare_qty(match_items):
# 	combine_list = []
# 	for item in match_items:
# 			match = 0
# 			if 	combine_list:							
# 				for i in combine_list:
# 					if item['item_code'] == i['item_code']:												
# 						i['qty'] += item['qty']
# 						match = 1
# 				if match != 1:
# 					combine_list.append(item)					
# 			else:
# 				combine_list.append(item)
# 	return combine_list	

@frappe.whitelist(allow_guest = True)
def combine_similar_items(doc_name):
	combine_similar_items = []	
	items = get_items(doc_name)
	doc = frappe.get_doc('Container Reconciliation' , doc_name)	
	for item in items:
		item['qty'] = item['qty'] * item['conversion_factor']
		item['uom'] = 'Nos'
		item['conversion_factor'] = 1
		if item['batch_no'] == '':
			item['batch_no'] = None
		# if not item['best_value_date']:
		# 	item['best_value_date'] = frappe.utils.add_months(6)
		# item['batch_no'] = ''
		match = 0
		if combine_similar_items:
			for i in combine_similar_items:								
				if item.item_code == i.item_code  and item.warehouse == i.warehouse:			
					if (item.batch_no and i.batch_no and item.batch_no == i.batch_no) or (item.best_value_date and i.best_value_date and item.best_value_date == i.best_value_date):
						i['batch_no'] = item['batch_no']
						i['best_value_date'] = item['best_value_date']
						i['qty'] += item['qty']
						match = 1
					# batch_no and best_value_date are empty
					elif item.batch_no == i.batch_no and item.best_value_date == i.best_value_date:
						i['qty'] += item['qty']
						match = 1					
			if match != 1:
				combine_similar_items.append(item)							
		else:
			combine_similar_items.append(item)
	values = {'items' : combine_similar_items}
	doc.update(values)
	doc.combine_similar_items = 1	
	doc.save(ignore_permissions=True)
	frappe.db.commit()

@frappe.whitelist(allow_guest = True)
def make_purchase_receipts_from_invoice_container(doc_name):
	from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_purchase_receipt
	items = get_items(doc_name)
	invoices = get_invoices(doc_name)
	reconcile_doc = frappe.get_doc('Container Reconciliation' , doc_name)
	
	
	for invoice in invoices:		
		invoice_items = frappe.db.sql (""" 
		SELECT item_code , item_name , qty , uom , warehouse , stock_uom , batch_no , best_value_date , conversion_factor ,
		tabPurchaseInvoiceItem.name as tabPurchaseInvoiceItemName,
		tabPurchaseInvoiceItem.price_list_rate, tabPurchaseInvoiceItem.base_price_list_rate, tabPurchaseInvoiceItem.margin_type, tabPurchaseInvoiceItem.margin_rate_or_amount, tabPurchaseInvoiceItem.rate_with_margin, tabPurchaseInvoiceItem.discount_percentage, tabPurchaseInvoiceItem.discount_amount, tabPurchaseInvoiceItem.base_rate_with_margin, tabPurchaseInvoiceItem.rate, tabPurchaseInvoiceItem.amount, tabPurchaseInvoiceItem.base_rate, tabPurchaseInvoiceItem.base_amount, tabPurchaseInvoiceItem.pricing_rules, tabPurchaseInvoiceItem.stock_uom_rate, tabPurchaseInvoiceItem.net_rate, tabPurchaseInvoiceItem.net_amount, tabPurchaseInvoiceItem.base_net_rate, tabPurchaseInvoiceItem.base_net_amount, tabPurchaseInvoiceItem.valuation_rate
		FROM `tabPurchase Invoice` AS tabPurchaseInvoice
		INNER JOIN `tabPurchase Invoice Item` AS  tabPurchaseInvoiceItem ON tabPurchaseInvoice.name = tabPurchaseInvoiceItem.parent
		WHERE tabPurchaseInvoice.name = %s
		""" , invoice.purchase_invoice , as_dict = True)
		pr_items_list = []
		for invoice_item in invoice_items:	

			for item in items:
				if invoice_item['item_code'] == item['item_code'] and item['qty'] != 99999999 and invoice_item.qty != 99999999 and int(item['qty'] / invoice_item.conversion_factor)	> 0:# and invoice_item['batch_no'] == item['batch_no']
					invoice_item_total = (invoice_item['qty'] * invoice_item['conversion_factor'])
					pr_item = item.copy()
					pr_item.purchase_invoice = invoice.purchase_invoice
					pr_item.purchase_invoice_item = invoice_item.tabPurchaseInvoiceItemName
					pr_item.uom = invoice_item.uom
					pr_item.price_list_rate = invoice_item.price_list_rate
					pr_item.base_price_list_rate = invoice_item.base_price_list_rate
					pr_item.margin_type = invoice_item.margin_type
					pr_item.margin_rate_or_amount = invoice_item.margin_rate_or_amount
					pr_item.rate_with_margin = invoice_item.rate_with_margin
					pr_item.discount_percentage = invoice_item.discount_percentage
					pr_item.discount_amount = invoice_item.discount_amount
					pr_item.base_rate_with_margin = invoice_item.base_rate_with_margin
					pr_item.rate = invoice_item.rate
					pr_item.amount = invoice_item.amount
					pr_item.base_rate = invoice_item.base_rate
					pr_item.base_amount = invoice_item.base_amount
					pr_item.pricing_rules = invoice_item.pricing_rules
					pr_item.stock_uom_rate = invoice_item.stock_uom_rate
					pr_item.net_rate = invoice_item.net_rate
					pr_item.net_amount = invoice_item.net_amount
					pr_item.base_net_rate = invoice_item.base_net_rate
					pr_item.base_net_amount = invoice_item.base_net_amount
					pr_item.valuation_rate = invoice_item.valuation_rate
					pr_item.conversion_factor = invoice_item.conversion_factor
					pr_item.batch_no = check_batch_exist(pr_item , invoice_item)

					##temp update to recreate purchase recipt with already created batches before #not we need to disable the auto remove f batches in this file:  # self.delete_auto_created_batches()
					#erpnext/erpnext/stock/doctype/purchase_receipt/purchase_receipt.py:237
					
					# create_new_batch, batch_number_series = frappe.db.get_value('Item', pr_item.item_code,
					# 		['create_new_batch', 'batch_number_series'])
					# if create_new_batch and batch_number_series and pr_item.best_value_date:
					# 	best_value_date_str = str(pr_item.best_value_date)
					# 	from datetime import datetime
					# 	best_value_date = datetime.strptime(best_value_date_str, '%Y-%m-%d')
					# 	best_value_day = str(best_value_date.day)
					# 	best_value_month = str(best_value_date.month)
					# 	best_value_year = str(best_value_date.year)[2:]
					# 	if len(best_value_day) == 1:
					# 		best_value_day = '0' + best_value_day
					# 	if len(best_value_month) == 1:
					# 		best_value_month = '0' + best_value_month

					# 	pr_item.batch_no = batch_number_series.replace('#','').replace('.','') + '-' + best_value_day + best_value_month + best_value_year

					# 	if pr_item.batch_no in ['MT1--190223','TI21--120723','WZ25--241022','MFL13--010822','GC9--180422','B15--110522','ALP2--090222','MFL16--010722','PG8--010423','DRP4--010922','SD--011022','BK6--011022','JC5--200822','MC47--230722','GUL1--010822','NAN4--251122','C33--010522','OO10--280222','CRU20--011022','FO19--010622','NAN20--010922','BL3--040722','MY231--010222','FO20--040622','FO21--010522','MC41--010522','SWIZ25--311022','SWIZ25--311022','NAN14--010622','FO34--010722','NAN5--011022','N39--300622','AW9--01082','N42--310522','FAB--010822','N8--010822','TT--010822','ASTO62-010822','PM2--010822','PM2--010822','PRS--010822','VIA1--010822','FRS--010822','LUM--010822','SC8--010822','SC8--010822','AW4--010822','FAB2--010822','BOB2--010822','N17--310522','ASTO57-010822','N18--310522','AW3--010822']:
					# 		pr_item.batch_no = ""

					if invoice_item_total == item['qty']:
						pr_item.qty = item['qty'] / invoice_item.conversion_factor
						pr_items_list.append(pr_item)	
						item['qty'] = 99999999
						invoice_item['qty'] = 99999999
						# Delete item in items
					elif invoice_item_total > item['qty']:
						pr_item.qty = int(item['qty'] / invoice_item.conversion_factor)		
						pr_items_list.append(pr_item)

						invoice_item['qty'] = invoice_item['qty'] - pr_item.qty	

						if 	item['qty'] % invoice_item.conversion_factor != 0:
							item['qty'] = item['qty'] % invoice_item.conversion_factor
						else:
							item['qty'] = 99999999
						# Delete item in items
					elif invoice_item_total < item['qty']:
						pr_item.qty = int(invoice_item_total / invoice_item.conversion_factor)														
						pr_items_list.append(pr_item)
						# update qty of item in items	
						invoice_item['qty'] = 99999999
						item['qty'] =  item['qty'] - invoice_item_total

		if (pr_items_list):
			pr_doc = make_purchase_receipt(invoice.purchase_invoice)
			pr_items = {'items' : pr_items_list, 'per_billed' : 100, 'container_reconciliation' : doc_name}
			pr_doc.update(pr_items)	
			pr_doc.save()		
	
	reconcile_item_list = []

	for item in items:
		if item['qty'] != 99999999:
			reconcile_item_doc = frappe.new_doc('Container Reconciliation Item')
			values = {
				'item_code' : item['item_code'],
				'item_name' : item['item_name'],
				'qty' : item['qty'],
				'uom' : item['uom'],
				'stock_uom' : item['stock_uom'],
				'conversion_factor' : item['conversion_factor'],
				'batch_no' : item['batch_no'],
				'best_value_date' : item['best_value_date'],
				'warehouse' : item['warehouse']
			}
			reconcile_item_doc.update(values)
			reconcile_item_list.append(reconcile_item_doc)	

	reconcile_items = {'items' : reconcile_item_list}
	reconcile_doc.update(reconcile_items)	
	reconcile_doc.save(ignore_permissions= True)		
	frappe.db.commit()

def get_pr_for_container(doc_name):
	purchase_receipts = frappe.get_all('Purchase Receipt' , {'container_reconciliation' : doc_name, 'docstatus' : ['<' , 2]} , 'name')
	return purchase_receipts

def merge_items_with_pr_items(doc_name):
	items = get_items(doc_name)
	invoices = get_invoices(doc_name)
	purchase_receipts = get_pr_for_container(doc_name)	
	# get purchase receipts  items based on invoices in container
	for invoice in invoices:		
		for pr in purchase_receipts:			
			pr_items = frappe.get_all("Purchase Receipt Item",fields=["item_code" , "qty" , "uom" , "best_value_date" , "conversion_factor" ,"warehouse" , "batch_no"],filters = {"parent":pr.name  , "purchase_invoice":invoice.purchase_invoice})		
			if pr_items	:
				for i in pr_items:					
					i['qty'] = 	i['qty'] * i['conversion_factor']
					i['uom'] = 'Nos'
					i['conversion_factor'] = 1							
					items.append(i)	
	
	return items

def combine_similar_items_after_merge(items_after_merge):			
	combine_similar_items_after_merge = []
	for item in items_after_merge:
		# item['qty'] = item['qty'] * item['conversion_factor']
		# item['uom'] = 'Nos'
		# item['conversion_factor'] = 1
		match = 0
		if 	combine_similar_items_after_merge:							
			for i in combine_similar_items_after_merge:
				if item['item_code'] == i['item_code']  and item['best_value_date'] == i['best_value_date'] and item['warehouse'] == i['warehouse']:												
					i['qty'] += item['qty']
					match = 1
			if match != 1:
				combine_similar_items_after_merge.append(item)					
		else:
			combine_similar_items_after_merge.append(item)
	
	return combine_similar_items_after_merge


def check_batch_exist(pr_item , invoice_item):		
	if not pr_item['batch_no']:
		create_new_batch, batch_number_series = frappe.db.get_value('Item', invoice_item['item_code'],
			['create_new_batch', 'batch_number_series'])

		if create_new_batch:
			if batch_number_series:
				best_value_date_str = str(pr_item['best_value_date'])
				if best_value_date_str:
					from datetime import datetime
					best_value_date = datetime.strptime(best_value_date_str, '%Y-%m-%d')
					best_value_day = str(best_value_date.day)
					best_value_month = str(best_value_date.month)
					best_value_year = str(best_value_date.year)[2:]
					if len(best_value_day) == 1:
						best_value_day = '0' + best_value_day
					if len(best_value_month) == 1:
						best_value_month = '0' + best_value_month
					if batch_number_series[len(batch_number_series) - 1 ] == '-':
						condition = ''
					else:
						condition = '-'
					batch_id = batch_number_series.replace('#','').replace('.','') + condition +  best_value_day + '-' + best_value_month + '-' + best_value_year					
					batch_list = frappe.get_all('Batch' , 'name')
					match = 0
					for batch in batch_list:
						if batch_id == batch.name:							
							match = 1
							return batch_id
					if match == 0:						
						return None
	else:		
		return pr_item['batch_no']
	

