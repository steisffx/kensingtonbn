import frappe
from frappe import _
from erpnext.stock.report.stock_projected_qty.stock_projected_qty import *
from erpnext.accounts.doctype.pos_invoice.pos_invoice import *
import frappe

@frappe.whitelist()
def get_proojected_qty(item_code, company, warehouse=None):
    try:
        if not warehouse:
            warehouse = "Kensington Main Store - M"
        qty = get_pos_reserved_qty(item_code, warehouse , batch_no=None)
        return qty
    except Exception as e:
        return 0



@frappe.whitelist()
def update_customer_screen(frm, user):
    try:
        frappe.msgprint(_("sahil is here"))
        frm = json.loads(frm)
        frappe.publish_realtime('realtime_updates', message=frm, user=user)
        return "Kensington"
    except Exception as e:
        frappe.msgprint(e)
