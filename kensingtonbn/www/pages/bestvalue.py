import frappe

def get_context(context):
    # context.bvalue = frappe.get_single('Best Value').best_value_items

    pass


@frappe.whitelist(allow_guest = True)
def get_items_html():
    return frappe.render_template('kensingtonbn/templates/includes/home/bestvalue.html', {
        "item": get_items()
    })
    
def get_items():

    return frappe.db.sql("""

         SELECT tabItem.item_code, tabItem.item_name, i.image, i.thumbnail, tabItemBestValue.batch_id, i.route, tabBatch.expiry_date AS expiry_date, tabItemPrice.price_list_rate AS price
         
         FROM `tabItem Best Value` AS tabItemBestValue
             INNER JOIN `tabWebsite Item` as i on tabItemBestValue.item_code = i.item_code 
             INNER JOIN tabItem on tabItem.item_code = i.item_code
             LEFT OUTER JOIN tabBatch ON tabBatch.item =  tabItem.name
             LEFT OUTER JOIN `tabItem Price` AS tabItemPrice ON tabItemPrice.batch_no =  tabBatch.name


    
         """
     , as_dict=True)
