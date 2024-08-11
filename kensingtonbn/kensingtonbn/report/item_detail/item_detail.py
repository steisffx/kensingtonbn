# Copyright (c) 2022, ClefinCode and contributors
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
            {
                "label": _("Item"),
                "fieldname": "item",
                "fieldtype": "Link",
                "options": "Item",
                "width": 150
            },
            {
                "label": _("Re-Order Level"),
                "fieldname": "reorder",
                "fieldtype": "Data",
                "width": 180
            },
            {
                "label": _("Top-UP QTY"),
                "fieldname": "topup",
                "fieldtype": "Data",
                "width": 150
            },
            {
                "label": _("Current Batch"),
                "fieldname": "batch",
                "fieldtype": "Link",
                "options": "Batch",
                "width": 180
            },
            {
                "label": _("Store"),
                "fieldname": "store",
                "fieldtype": "Data",
                "width": 100
            },
            {
                "label": _("Warehouse"),
                "fieldname": "warehouse",
                "fieldtype": "Data",
                "width": 100
            },
            {
                "label": _("Total QTY(All Batches)"),
                "fieldname": "total",
                "fieldtype": "Data",
                "width": 200
            },
            {
                "label": _("Transfer batch"),
                "fieldname": "batch_1",
                "fieldtype": "Link",
                "options": "Batch",
                "width": 150
            },
            {
                "label": _("Transfer QTY"),
                "fieldname": "total_1",
                "fieldtype": "Data",
                "width": 150
            },
            {
                "label": _("Sales(Last 3)"),
                "fieldname": "sales",
                "fieldtype": "Data",
                "width": 150
            },
            {
                "label": _("Reserved QTY from POS"),
                "fieldname": "sales",
                "fieldtype": "Data",
                "width": 150
            }
    ]
    return columns


def get_data(filters):
    try:
        result = []
        if filters.get("item"):
            items = [filter.get("item")]
        else:
            batch_item = frappe.db.sql("""select DISTINCT item from `tabBatch` where disabled = 0 """, as_dict=1)
            items = [i.item for i in batch_item]

        for i in items:
            qty = frappe.db.sql("""select name, item, batch_qty from `tabBatch` where item = %s and batch_qty != 0 and disabled = 0 order by expiry_date asc""", i, as_dict=1)
            re_order_level, top_up_qty = frappe.db.get_value("Item", i, ["re_order_level", "top_up_qty"])
            if(len(qty) > 0):
                qt, total, qt_bt = 0, 0, 0
                next_batch = qty[1].name if len(qty) > 1 else ''
                pos_qty, sales_qty = 0, 0
                if(qty[0].batch_qty <= re_order_level):
                    qt_bt = qty[0].batch_qty
                    qtys = frappe.db.sql("""select actual_qty from `tabBin` where item_code = %s """, i, as_dict=1)
                    for s in qtys:
                        qt += s.actual_qty

                    for q in qty:
                        total += q.batch_qty

                    pos_qtys = frappe.db.sql("""select DISTINCT parent, qty from `tabPOS Invoice Item` where item_code = %s and docstatus = 1 limit 3 """,i, as_dict=1)
                    for p in pos_qtys:
                        pos_qty += p.qty

                    sales_qtys = frappe.db.sql("""select DISTINCT parent, qty from `tabSales Invoice Item` where item_code = %s and docstatus = 1 limit 3 """,i, as_dict=1)
                    for s in sales_qtys:
                        sales_qty += s.qty

                result.append([i, re_order_level, top_up_qty, qty[0].name, qty[0].batch_qty, qt, total, next_batch, top_up_qty-qt_bt, sales_qty, pos_qty])

        return result
    except Exception as e:
        frappe.msgprint(e)
