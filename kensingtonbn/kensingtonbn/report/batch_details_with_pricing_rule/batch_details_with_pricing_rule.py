# Copyright (c) 2013, ClefinCode and contributors
# For license information, please see license.txt
import json
import re
from datetime import datetime

import frappe
from frappe import _
from frappe.utils import nowdate, flt
from erpnext.utilities.product import get_price
from erpnext.setup.utils import get_exchange_rate
from erpnext.stock.get_item_details import get_conversion_factor
from erpnext.e_commerce.doctype.e_commerce_settings.e_commerce_settings import get_shopping_cart_settings

def execute(filters=None):
	columns, data = [], []
	data, count = get_data(filters)
	columns = get_columns(filters, count)
	return columns, data

def get_columns(filters, count):
	columns = [
		{
			"fieldname": "chk",
			"label": _(" "),
			"fieldtype": "Data",
		},
		{
			"fieldname": "item",
			"label": _("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 125
		},
		{
			"fieldname": "name",
			"label": _("Batch"),
			"fieldtype": "Link",
			"options": "Batch",
			"width": 125
		},
		{
			"fieldname": "best_value_date",
			"label": _("Best Value Date"),
			"fieldtype": "Date",
			"width": 125
		},
		{
			"fieldname": "total_qty",
			"label": _("Balance Qty"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "buying_rate",
			"label": _("Buying Price"),
			"fieldtype": "Currency",
			"options": "Company:company:default_currency",
			"width": 100
		},
		# {
		# 	"fieldname": "valuation_rate",
		# 	"label": _("Valuation Rate"),
		# 	"fieldtype": "Currency",
		# 	"options": "currency",
		# 	"width": 100
		# },
		{
			"fieldname": "price_list_rate",
			"label": _("Standard Selling Rate"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100
		},

	]
	for filter in filters:
		if "warehouse " in filter:
			warehouse, word_to_check = filter, "Kensington"
			if re.search(rf"\b{word_to_check}\b", warehouse, re.IGNORECASE):
				warehouse = re.sub(rf"\b{word_to_check}\b", "", warehouse, flags=re.IGNORECASE)
				warehouse = " ".join(warehouse.split())
			
			columns.extend((
				{
				"fieldname": filter,
				"label": _(warehouse.replace("warehouse", "", 1)),
				"fieldtype": "Data",
				"width": 125
				},
			))
	columns.extend(
		(
		{
			"fieldname": "rate",
			"label": _("Rate"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "last_modified",
			"label": _("Last Update"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "btn_add",
			"label": _("Add Pricing Rule"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "btn_change",
			"label": _("Change Pricing Rule"),
			"fieldtype": "Data",
			"width": 120
		},
		# {
		# 	"fieldname": "recommended_price",
		# 	"label": _("Recommended Price"),
		# 	"fieldtype": "Data",
		# 	"width": 100
		# },
		{
			"fieldname": "confirmed_price",
			"label": _("Confirmed Price"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "count",
			"label": _("Count"),
			"fieldtype": "Data",
			"hidden": 1,
			"default": count
		}
		
		))
		
	add_warehouses_columns(filters)
	return columns

def get_data(filters):
	batches_data = get_batches_data(filters)
	return batches_data

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and batch.best_value_date >= '" + filters.get("from_date") + "' "
	if filters.get("to_date"):
		conditions += " and batch.best_value_date <= '" + filters.get("to_date") + "' "
	if filters.get("item"):
		conditions += " and batch.item = '" + filters.get("item") + "' "
	if filters.get("batch") and not filters.get("barcode"):
		conditions += " and batch.name = '" + filters.get("batch") +"' "
	if not filters.get("disabled"):
		conditions += " and batch.disabled = 0 "
	return conditions

def get_batches_data(filters):
	conditions = get_conditions(filters)
	if filters.get("barcode"):
		batch = frappe.db.get_value("Item Barcode", {'barcode': filters.get("barcode")}, 'batch_no')
		conditions += " and batch.name = " + batch
	
	selling_price_list = frappe.db.get_single_value('Selling Settings', 'selling_price_list') or frappe.db.get_value('Price List', _('Standard Selling'))

	strQuery = """
		select CONCAT('<input type="checkbox" class="check_item" data-batch="', batch.name,'" data-item="', batch.item,'">') as chk,
		batch.item,  batch.name, batch.best_value_date,
		IFNULL(
			(SELECT price_list_rate FROM `tabItem Price` WHERE item_code = batch.item and batch_no = batch.name and selling = 1 and price_list = '{price_list}' LIMIT 1),
			(SELECT price_list_rate FROM `tabItem Price` WHERE item_code = batch.item and (batch_no IS NULL or batch_no = '') and selling = 1 and price_list = '{price_list}' LIMIT 1)) 
		AS price_list_rate, 
		IFNULL(
			(SELECT currency FROM `tabItem Price` WHERE item_code = batch.item and batch_no = batch.name and selling = 1 and price_list = '{price_list}' LIMIT 1),
			(SELECT currency FROM `tabItem Price` WHERE item_code = batch.item and (batch_no IS NULL or batch_no = '') and selling = 1 and price_list = '{price_list}' LIMIT 1)) 
		AS selling_currency, 
		CONCAT('<div class="qty" data-batch="', batch.name,'" value="',cast(sum(actual_qty) as float),'">', cast(sum(actual_qty) as float), '</div>') as total_qty,
		{warehouses}
		CONCAT('<a class="btn_pr_add" data-batch="', batch.name,'" data-item="', batch.item,'" style="width:80px; text-align: center; background-color: #e7e7e7; color: black; padding: 5px 30px" onclick="new_price_rule(this)">', 'Add', '</a>') as btn_add,
		CONCAT('<a class="btn_pr_chg" data-batch="', batch.name,'" data-item="', batch.item,'" style="width:80px; text-align: center; background-color: #e7e7e7; color: black; padding: 5px 30px" onclick="change_price_rule(this)">', 'Change', '</a>') as btn_change,
		CONCAT('<input type="number" value="', ROUND(item.confimed_price, 2), '" class="confirmed_price" data-batch="', batch.name,'" data-item="', batch.item,'" style="width:80px; text-align: center; background-color: black; color: white;">') as confirmed_price,
		IFNULL(
			(SELECT rate_of_stock_uom from `tabPurchase Invoice Item` WHERE item_code = batch.item AND batch_no = batch.name and docstatus = 1 ORDER BY creation DESC LIMIT 1),
			(SELECT rate_of_stock_uom from `tabPurchase Invoice Item` WHERE item_code = batch.item AND (batch_no = '' or batch_no IS NULL) and docstatus = 1 ORDER BY creation DESC LIMIT 1)
		) as buying_rate,
		IFNULL(
			(SELECT base_rate from `tabPurchase Invoice Item` WHERE item_code = batch.item AND batch_no = batch.name and docstatus = 1 ORDER BY creation DESC LIMIT 1),
			(SELECT base_rate from `tabPurchase Invoice Item` WHERE item_code = batch.item AND (batch_no = '' or batch_no IS NULL) and docstatus = 1 ORDER BY creation DESC LIMIT 1)
		) as base_rate,
		IFNULL(
			(SELECT conversion_factor from `tabPurchase Invoice Item` WHERE item_code = batch.item AND batch_no = batch.name and docstatus = 1 ORDER BY creation DESC LIMIT 1),
			(SELECT conversion_factor from `tabPurchase Invoice Item` WHERE item_code = batch.item AND (batch_no = '' or batch_no IS NULL) and docstatus = 1 ORDER BY creation DESC LIMIT 1)
		) as conversion_factor
		
		FROM `tabBatch` AS batch 
		LEFT JOIN `tabStock Ledger Entry` AS sle ON batch.name = sle.batch_no
		INNER JOIN `tabItem` AS item ON item.name=batch.item
		WHERE sle.is_cancelled = 0 AND actual_qty!=0
		{conditions}
		GROUP BY batch.name
	""".format(conditions=conditions, 
			warehouses = add_warehouses_columns(filters),
			price_list = selling_price_list)
	
	if filters.get("balance_qty"):
		strQuery += " HAVING sum(actual_qty) > 0 "
	else:
		strQuery += " HAVING sum(actual_qty) >= 0 "
	
	tosort = True
	if filters.get("sort_by") and filters.get("sorting"):
		sort_by = ""
		if filters.get("sort_by") == "Item Code": sort_by = "batch.item"
		elif filters.get("sort_by") == "Batch": sort_by = "batch.name"
		elif filters.get("sort_by") == "Best Value Date": sort_by = "batch.best_value_date"
		else: tosort = False
		if tosort:
			strQuery += f" order by {sort_by} {filters.get('sorting')}"

	start = filters.get("start") - 1
	number_of_rows = filters.get("number_of_rows")

	if filters.get("sort_by", "") != "Last Update":
		strQuery += " LIMIT {0} OFFSET {1} ".format(number_of_rows, start)

	batches = frappe.db.sql(strQuery, as_dict=1)
	shopping_cart_settings = get_shopping_cart_settings()
	customer_group = shopping_cart_settings.default_customer_group
	company = shopping_cart_settings.company 
	company_currency = frappe.db.get_value("Company", company, "default_currency")
	results, exchange_rates = [], {}
	for batch in batches:
		if batch.get('conversion_rate') and batch.get('base_rate', 0) > 0 and batch.get('buying_rate', 0) == 0:
			batch['buying_rate'] = batch.get('base_rate') / batch.get('conversion_factor', 1)
		
		# Setting Prices in Company Currency

		if batch.get('price_list_rate') and batch.get('selling_currency'):
			if not exchange_rates.get(batch['selling_currency']):
				exchange_rate = get_exchange_rate(batch['selling_currency'], company_currency)
				exchange_rates[batch['selling_currency']] = exchange_rate
			else:
				exchange_rate = exchange_rates[batch['selling_currency']]

			batch['price_list_rate'] = batch['price_list_rate'] * exchange_rate

		price = get_price(batch['item'],
			selling_price_list,
			customer_group,
			company,
			1,
			batch['name'], return_pr= True)

		if price:
			# last update : comment these lines to show the rate value based on batch
			# if price.price_list_rate == res[-1][5]:
			# 	price = get_price(batch['item'],
			# 	selling_price_list,
			# 	customer_group,
			# 	company,
			# 	1, return_pr= True)

			if (price.pricing_rule):
				pricing_rule = price.pricing_rule.replace('[','')
				pricing_rule = pricing_rule.replace(']','')
				pricing_rule = pricing_rule.replace('"','')	
				pricing_rule = pricing_rule.strip()
				rate = price.formatted_price_sales_uom
				last_modified = frappe.db.get_value("Pricing Rule", pricing_rule, "modified")
			
			else: 
				pricing_rule = ""
				rate = ""
				last_modified = ""

			price_div = "<div class= 'pricing_rule' data-batch='"+batch['name']+"' data-pricing-rule ='"+pricing_rule+"' value="+str(price.price_list_rate)+">"+rate+"</div>"
			batch["rate"] = price_div
			batch["last_modified"] = str(last_modified)
			
		else: 
			batch["rate"] = 0
			batch["last_modified"] = str(last_modified)

		results.append(batch)
	
	if filters.get("sort_by", "") == "Last Update" and filters.get("sorting"):
		if filters.get("sorting") == "Desc":
			results = sorted(results, key=lambda x: x['last_modified'], reverse=True)
		else:
			results = sorted(results, key=lambda x: x['last_modified'])

		results = results[start: start + int(number_of_rows)]
	return results, len(results)
	
def add_warehouses_columns(filters):
	warehouses = []
	for filter in filters:
		if "warehouse " in filter:
			warehouses.append(filter.replace("warehouse", "", 1))

	warehouses = frappe.db.get_list("Warehouse", filters = {'name': ['in', warehouses], 'disabled': 0} ,fields=['name'], as_list=True)
	strWarehouse = ""
	i = 0
	for wr in warehouses:
		strWarehouse += "SUM(CASE WHEN sle.warehouse = '"+wr[0]+"' THEN actual_qty END) 'warehouse "+wr[0]+"' , "
		i +=1
	return strWarehouse



@frappe.whitelist(allow_guest=True)
def set_pricing():
	batches = frappe.db.get_all("Batch", filters = {'disabled': 0}, fields = ['name', 'item'])

	return batches

@frappe.whitelist()
def add_pricing_rule(item_code, batch, rate):
	rate = flt(rate)
	shopping_cart_settings = get_shopping_cart_settings()

	if rate == 0 or frappe.db.exists("Pricing Rule", {
		"item_code": item_code,
		"batch_no": batch,
		"price_or_product_discount": "Price",
		"company": shopping_cart_settings.company,
		"valid_upto": (">=", nowdate()),
		"currency": frappe.db.get_value("Company", shopping_cart_settings.company, "default_currency"),
		"margin_rate_or_amount": rate,
		"rate_or_discount": "Rate"
	}):
		return

	import random

	doc = frappe.new_doc("Pricing Rule")
	items = {
			"item_code": item_code,
			"batch_no": batch
	}
	doc.update({
		"title": item_code + "_" + str(random.randint(1, 1000)),
		"item_code": item_code,
		"batch_no": batch,
		"price_or_product_discount": "Price",
		"company": shopping_cart_settings.company,
		"valid_from": nowdate(),
		"selling": 1,
		"currency": frappe.db.get_value("Company", shopping_cart_settings.company, "default_currency"),
		"rate": rate,
		"rate_or_discount": "Rate"
	})
	doc.append("items", items)
	doc.insert(ignore_permissions = True)
	return doc.name

@frappe.whitelist()
def update_pricing_rule(rule_name, rate):
	if not frappe.db.exists("Pricing Rule", rule_name):
		return

	doc = frappe.get_doc("Pricing Rule", rule_name)

	doc.update({
		"rate": rate
	})
	doc.save(ignore_permissions = True)
	return doc.name

@frappe.whitelist()
def create_item_label():
	items = frappe.form_dict.get('items', '')
	if items:
		try:
			items = json.loads(items)

		except json.JSONDecodeError:
			frappe.throw("Invalid JSON format received")
	batches = frappe.db.get_all("Batch",{
		"disabled": 0,
		"date_in_report": nowdate(),
	}, "name")

	newitems = []
	if batches:
		for batch in batches:
			bdoc = frappe.get_doc("Batch", batch.name)
			newitems.append({
				"item_code": bdoc.item,
				"item_name": bdoc.item_name,
				"batch_no": bdoc.batch_id,
				"qty": bdoc.qty_in_report,
				"price_list_rate": bdoc.price_in_report
			})

	if newitems and items:
		for item in items:
			found = False
			for newitem in newitems:
				if item["item_code"] == newitem["item_code"]:
					found = True
			if not found:
				newitems.append(item)

	if newitems:
		doc = frappe.new_doc("Item Label")
		doc.update({
			"items": newitems
		})

		return doc
	
@frappe.whitelist()
def set_values(item_code, batch_no, price, qty):
	frappe.db.set_value("Item", item_code, "confimed_price", price)

	doc = frappe.get_doc("Batch", {"batch_id": batch_no}) 
	doc.update({
		"date_in_report": nowdate(),
		"price_in_report": price,
		"qty_in_report": qty
	})
	doc.save(ignore_permissions = True)
	frappe.db.commit()
