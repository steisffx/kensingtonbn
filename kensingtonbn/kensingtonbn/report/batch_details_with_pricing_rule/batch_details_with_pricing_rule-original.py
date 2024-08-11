# Copyright (c) 2013, ClefinCode and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from erpnext.utilities.product import get_price
from frappe.utils import flt
from erpnext.e_commerce.doctype.e_commerce_settings.e_commerce_settings import get_shopping_cart_settings

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
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
			"fieldname": "valuation_rate",
			"label": _("Valuation Rate"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100
		},
		{
			"fieldname": "price_list_rate",
			"label": _("Standard Selling Rate"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100
		},
		{
			"fieldname": "total_qty",
			"label": _("Balance Qty"),
			"fieldtype": "Data",
		},
	]
	for filter in filters:
		if "warehouse " in filter:
			columns.extend((
				{
				"fieldname": filter,
				"label": _(filter.replace("warehouse", "", 1)),
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
			"fieldname": "btn_add",
			"label": _("Add Pricing Rule"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "btn_change",
			"label": _("Change Pricing Rule"),
			"fieldtype": "Data",
			"width": 100
		},
		
		))
		
	add_warehouses_columns(filters)
	return columns

def get_data(filters):
	batches_data = get_batches_data(filters)
	return batches_data

def get_conditions(filters):
	conditions = []
	if filters.get("from_date"):
		conditions.append(["best_value_date" ,">=", filters.get("from_date")])
	if filters.get("to_date"):
		conditions.append(["best_value_date" ,"<=", filters.get("to_date")])
	if filters.get("item"):
		conditions.append(["item" ,"=", filters.get("item")])
	if filters.get("batch") and not filters.get("barcode"):
		conditions.append(["name" ,"=", filters.get("batch")])
	if not filters.get("disabled"):
		conditions.append(["disabled" ,"=", 0])
	return conditions

def get_batches_data(filters):
	conditions = get_conditions(filters)
	if filters.get("barcode"):
		batch = frappe.db.get_value("Item Barcode", {'barcode': filters.get("barcode")}, 'batch_no')
		conditions.append(["name" ,"=", batch])
		batches = frappe.db.get_all("Batch", filters = conditions, fields = ['name', 'item'])
	if not filters.get("barcode"):
		batches = frappe.db.get_all("Batch", filters = conditions, fields = ['name', 'item'])

	selling_price_list = frappe.db.get_single_value('Selling Settings', 'selling_price_list') or frappe.db.get_value('Price List', _('Standard Selling'))
	customer_group = get_shopping_cart_settings().default_customer_group
	company = get_shopping_cart_settings().company 
	results = []
	for batch in batches:
		res = frappe.db.sql("""
					SELECT 
					CONCAT('<input type="checkbox" class="check_item" data-batch="', batch.name,'" data-item="', batch.item,'">') as chk,
					batch.item,  batch.name, batch.best_value_date, 
					IFNULL(
						(SELECT valuation_rate FROM `tabStock Ledger Entry` WHERE batch_no = batch.name ORDER BY posting_date DESC, posting_time DESC LIMIT 1 ),
						(SELECT valuation_rate FROM `tabStock Ledger Entry` WHERE item_code = batch.item and batch_no IS NULL ORDER BY posting_date DESC, posting_time DESC LIMIT 1))
					AS valuation_rate,
					(CASE WHEN ip.price_list_rate IS NULL THEN 
						(SELECT price_list_rate FROM `tabItem Price` WHERE item_code = batch.item and batch_no IS NULL LIMIT 1)
					ELSE ip.price_list_rate END) AS price_list_rate, 
					#sum(actual_qty) AS qty,
					CONCAT('<div class="qty" data-batch="', batch.name,'" value="',cast(sum(actual_qty) as float),'">', cast(sum(actual_qty) as float), '</div>') as total_qty,
					{warehouses}
					CONCAT('<a class="btn_pr_add" data-batch="', batch.name,'" data-item="', batch.item,'" style="width:80px; text-align: center; background-color: #e7e7e7; color: black; padding: 5px 30px" onclick="new_price_rule(this)">', 'Add', '</a>') as btn_add,
					CONCAT('<a class="btn_pr_chg" data-batch="', batch.name,'" data-item="', batch.item,'" style="width:80px; text-align: center; background-color: #e7e7e7; color: black; padding: 5px 30px" onclick="change_price_rule(this)">', 'Change', '</a>') as btn_change
					FROM `tabBatch` AS batch 
					LEFT JOIN `tabStock Ledger Entry` AS sle ON batch.name = sle.batch_no
					LEFT JOIN `tabItem Price` AS ip ON ip.batch_no = batch.name
					WHERE batch.name = "{name}" AND sle.is_cancelled = 0
					GROUP BY batch.name
					ORDER BY batch.item

		""".format(warehouses = add_warehouses_columns(filters), name=batch['name']), filters, as_list=1) 
		if res:
			# res[-1][6] = res[-1][6].decode("utf-8")
			price = get_price(batch['item'],
				selling_price_list,
				customer_group,
				company,
				1,
				batch['name'], return_pr= True)

			if price:
				if price.price_list_rate == res[-1][5]:
					price = get_price(batch['item'],
					selling_price_list,
					customer_group,
					company,
					1, return_pr= True)

				if (price.pricing_rule):
					pricing_rule = price.pricing_rule.replace('[','')
					pricing_rule = pricing_rule.replace(']','')
					pricing_rule = pricing_rule.replace('"','')					
					pricing_rule = pricing_rule.lstrip()
					rate = price.formatted_price_sales_uom
					
				else: 
					pricing_rule = ""
					rate = ""
				price_div = "<div class= 'pricing_rule' data-batch='"+batch['name']+"' data-pricing-rule ='"+pricing_rule+"' value="+str(price.price_list_rate)+">"+rate+"</div>"
				res[-1].insert(len(res[-1]) - 2, price_div)
			else: 
				res[-1].insert(len(res[-1]) - 2, 0)
			results +=res
	return results
	
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
