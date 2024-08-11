
import frappe



@frappe.whitelist(allow_guest = True)
def get_recommended_items_html():
    return frappe.render_template('kensingtonbn/templates/includes/home/recommendedfororder.html', {
        "item": get_recommended_items()
    })
    
def get_recommended_items():

    return frappe.db.sql("""

         SELECT tabItem.item_code, tabItem.item_name, i.image, i.thumbnail, tabRecommended.batch_id, i.route, tabBatch.expiry_date AS expiry_date, tabItemPrice.price_list_rate AS price
         
         FROM `tabRecommended For Order Items` AS tabRecommended
             INNER JOIN `tabWebsite Item` as i on tabRecommended.item_code = i.item_code 
             INNER JOIN tabItem on tabItem.item_code = i.item_code
             LEFT OUTER JOIN tabBatch ON tabBatch.item =  tabItem.name
             LEFT OUTER JOIN `tabItem Price` AS tabItemPrice ON tabItemPrice.batch_no =  tabBatch.name

         LIMIT 3
    
         """
     , as_dict=True)




@frappe.whitelist(allow_guest = True)
def get_suggested_items_html():
    return frappe.render_template('kensingtonbn/templates/includes/home/suggesteditems.html', {
        "item": get_suggested_items()
    })
    
def get_suggested_items():

    return frappe.db.sql("""

         SELECT tabItem.item_code, tabItem.item_name, i.image, i.thumbnail, tabSuggested.batch_id, i.route, tabBatch.expiry_date AS expiry_date, tabBatch.best_value_date AS best_value_date, tabItemPrice.price_list_rate AS price
         
         FROM `tabSuggested Items Item` AS tabSuggested
             INNER JOIN `tabWebsite Item` as i on tabSuggested.item_code = i.item_code 
             INNER JOIN tabItem on tabItem.item_code = i.item_code
             LEFT OUTER JOIN tabBatch ON tabBatch.item =  tabItem.name
             LEFT OUTER JOIN `tabItem Price` AS tabItemPrice ON tabItemPrice.batch_no =  tabBatch.name


         LIMIT 3
         """
     , as_dict=True)


@frappe.whitelist(allow_guest = True)
def get_bestvalue_items_html():
    return frappe.render_template('kensingtonbn/templates/includes/home/bestvalue.html', {
        "item": get_bestvalue_items()
    })
    
def get_bestvalue_items():

    return frappe.db.sql("""

         SELECT tabItem.item_code, tabItem.item_name, i.image, i.thumbnail, tabItemBestValue.batch_id, i.route, tabBatch.expiry_date AS expiry_date, tabItemPrice.price_list_rate AS price
         
         FROM `tabItem Best Value` AS tabItemBestValue
             INNER JOIN `tabWebsite Item` as i on tabItemBestValue.item_code = i.item_code 
             INNER JOIN tabItem on tabItem.item_code = i.item_code
             LEFT OUTER JOIN tabBatch ON tabBatch.item =  tabItem.name
             LEFT OUTER JOIN `tabItem Price` AS tabItemPrice ON tabItemPrice.batch_no =  tabBatch.name


         LIMIT 3
         """
     , as_dict=True)
