# Copyright (c) 2021, ClefinCode and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
class ItemLabel(Document):
	pass
from erpnext.utilities.product import get_price
from erpnext.e_commerce.doctype.e_commerce_settings.e_commerce_settings import get_shopping_cart_settings

@frappe.whitelist()
def get_jinja_data(item_code, batch_no, doc):
	cart_settings = get_shopping_cart_settings()
	selling_price_list = frappe.db.get_value("Item Label", doc.parent, "selling_price_list") or frappe.db.get_single_value('Selling Settings', 'selling_price_list') or frappe.db.get_value('Price List', _('Standard Selling'))
	company = frappe.db.get_value("Item Label", doc.parent, "company") or cart_settings.company

	if batch_no:
		price = get_price(
				item_code,
				selling_price_list,
				cart_settings.default_customer_group,
				company,
				1,
				batch_no
			).formatted_price_sales_uom
		if (doc.get_formatted('price_list_rate') != price):
			return price

	if item_code:
		price = get_price(
				item_code,
				selling_price_list,
				cart_settings.default_customer_group,
				cart_settings.company,
				1
			).formatted_price_sales_uom
		if (doc.get_formatted('price_list_rate') != price):
			return price
	else:
		return
