import frappe

def get_context(context):
    # productlist = frappe.get_all('Homepage Featured Product', filters={}, fields=['item_code','item_name','image','thumbnail','group_title','section_number'], order_by="idx Desc", limit=100)
    # filtered_pos = []
    # for num in productlist:
    #     if num not in filtered_pos:
    #         filtered_pos.append(num)
    # context.productlist = filtered_pos
    pass



@frappe.whitelist(allow_guest = True)
def get_productlist_html(sn):
    return frappe.render_template('kensingtonbn/templates/includes/home/homepagefeaturedproduct.html', {
        "productlist": get_productlist(sn)
        
    })
    

def get_productlist(sn):    
    return  frappe.db.sql("""

        SELECT tabItem.name AS item, tabItem.image, tabBatch.expiry_date AS expiry_date, tabItemPrice.price_list_rate
        
        FROM tabItem 
            LEFT OUTER JOIN tabBatch ON tabBatch.item =  tabItem.name
            LEFT OUTER JOIN `tabItem Price` AS tabItemPrice ON tabItemPrice.batch_no =  tabBatch.name
            
        """
    , as_dict=True)

# def get_productlist(sn):
#     return  frappe.db.sql("select hp.item_code, hp.item_name, hp.image, hp.thumbnail, hp.group_title, hp.section_number, i.route from `tabHomepage Featured Product` as hp left join `tabItem` as i on hp.item_code=i.name where hp.section_number = " + sn + " order by hp.idx ASC limit 0, 100", as_dict=True)



