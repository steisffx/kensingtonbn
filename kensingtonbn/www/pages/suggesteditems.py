import frappe
from frappe.utils import flt
from erpnext.e_commerce.shopping_cart.product_info import get_product_info_for_website
from frappe.utils.background_jobs import enqueue
from erpnext.utilities.product import get_non_stock_item_status
from erpnext.stock.doctype.batch.batch import get_batch_qty

# from kensingtonbn.e_commerce.product_data_engine.query import ProductQuery
# from kensingtonbn.e_commerce.product_data_engine.query import add_display_details

@frappe.whitelist(allow_guest = True)
def get_items_html():
    return frappe.render_template('kensingtonbn/templates/includes/home/suggesteditems.html', {
        "suggesteditems": get_items()
    })
    
def get_items():

    suggesteditems = frappe.db.sql("""

         SELECT tabItem.item_code, tabItem.item_name, i.image, i.thumbnail, tabSuggested.batch_id, i.route, tabBatch.expiry_date AS expiry_date, tabBatch.best_value_date AS best_value_date
         
         FROM `tabSuggested Items Item` AS tabSuggested
             INNER JOIN `tabWebsite Item` as i on tabSuggested.item_code = i.item_code 
             INNER JOIN tabItem on tabItem.item_code = i.item_code
             LEFT OUTER JOIN tabBatch ON tabBatch.item =  tabItem.name
        WHERE (tabSuggested.batch_id = tabBatch.name OR tabSuggested.batch_id IS NULL)  order by tabSuggested.idx ASC limit 0, 100


    
         """
     , as_dict=True)  

    for  item in suggesteditems: 
        if item.batch_id:            
            productinfo = get_product_info_for_website(item.item_code, True , item.batch_id ).get('product_info').get('price')            
        else:
            productinfo = get_product_info_for_website(item.item_code, True ).get('product_info').get('price')
        if productinfo:
            item.update(productinfo)     
    return  suggesteditems