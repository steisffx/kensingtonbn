# Copyright (c) 2013, ClefinCode and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
            {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
            {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 250},
            {"label": _("Item Name"), "fieldname": "item_name", "width": 250},
            {"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 90},
            {"label": _("Sold Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
            {"label": _("Batch No"), "fieldname": "batch_no", "fieldtype": "Link", "width": 250, "options": "Batch"},
    ]

    return columns


def get_condition(filters):
    condition = ""
    if(filters.get("company")):
        condition += " and p.company = %(company)s"

    if(filters.get("item_code")):
        condition += " and c.item_code = %(item_code)s"

    if filters.get("from_date") and filters.get("to_date"):
        condition += " and p.posting_date between '%s' and '%s'"%(filters.get("from_date"), filters.get("to_date"))

    if(filters.get("batch")):
        condition += " and c.batch_no = %(batch)s"

    return condition


def get_data(filters):
    try:
        condition = get_condition(filters)
        data = frappe.db.sql("""select p.posting_date as date, c.item_code, c.item_name, c.stock_uom, c.batch_no, c.qty from `tabPOS Invoice` p inner join `tabPOS Invoice Item` c where p.name = c.parent and p.docstatus = 1 %s """%condition, filters, as_dict=True)
        #frappe.msgprint(_("{0}").format(data))
        return data
    except Exception as e:
        frappe.msgprint(e)

