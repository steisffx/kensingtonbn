import frappe
from kensingtonbn.kensingtonbn.doctype.baiduri_payment_settings.baiduri_payment_settings import get_transaction_id

def get_context(context):
    data = frappe.form_dict
    order_id = data.order_id        
    data.redirect_to  = get_transaction_id(order_id)
    print('************************context******************') 
    print(data)    
    return context
