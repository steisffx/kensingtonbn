# Copyright (c) 2022, ClefinCode and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import  getdate, nowdate


class BatchBarcodeReconciliation(Document):
	pass

@frappe.whitelist(allow_guest = True)
def update_batches(doc):
    """ Auto Update New Batches with Barcode in Items Master """

    new_batch_list =  frappe.db.sql(f""" 
    SELECT name , barcode , batch_no 
    FROM `tabBatch Barcode Reconciliation Item`
	WHERE parent = '{doc}' and batch_reconcile = 0
   """ , as_dict = True)
   
    for i in new_batch_list:        
        barcode = i.barcode.strip()              
        new_batch = i.batch_no        	        
        barcode_data = frappe.db.get_value('Item Barcode', {'barcode': barcode}, ['name' , 'batch_no'] ,as_dict=True) 
        if barcode_data:        
            current_batch = barcode_data.batch_no
            if check_batch_status(current_batch):            
                barcode_doc = frappe.get_doc('Item Barcode' , barcode_data.name )            
                barcode_doc.update({'batch_no' :new_batch}) 
                barcode_doc.save(ignore_permissions=True)
                reconcile_child_doc = frappe.get_doc('Batch Barcode Reconciliation Item' , i.name) 
                reconcile_child_doc.batch_reconcile = 1 
                reconcile_child_doc.save(ignore_permissions=True)         		
    frappe.db.commit()

def check_batch_status(batch_no):
    if not batch_no:
        return True
    else:
        batch_doc = frappe.get_doc('Batch' , batch_no )    
        if batch_doc.disabled == 1 or batch_doc.batch_qty == 0 or batch_doc.expiry_date < getdate(nowdate()):
            return True
        else:
            return False
