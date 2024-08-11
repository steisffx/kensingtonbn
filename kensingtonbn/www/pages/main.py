import frappe
from frappe.utils import flt

from erpnext.e_commerce.shopping_cart.product_info import get_product_info_for_website
from frappe.utils.background_jobs import enqueue
from erpnext.utilities.product import get_non_stock_item_status
from erpnext.stock.doctype.batch.batch import get_batch_qty

# from kensingtonbn.e_commerce.product_data_engine.query import ProductQuery
# from kensingtonbn.e_commerce.product_data_engine.query import add_display_details

def get_context(context):
    context.slides = frappe.get_all('Home Page Main Slideshow', filters={}, fields=['image_file','video_file','slideshow_file_link'], order_by="idx Desc", limit=100)
#    slides = frappe.db.sql("""
#
#       SELECT hpf.image_file, hpf.video_file, hpf.slideshow_file_link
#       FROM `tabHome Page Main Slideshow Files` as hpf  
#   
#       """
#       , as_dict=True)
#   return slides
    # productlist = frappe.get_all('Homepage Featured Product', filters={}, fields=['item_code','item_name','image','thumbnail','group_title','section_number'], order_by="idx Desc", limit=100)
    # filtered_pos = []
    # for num in productlist:
    #     if num not in filtered_pos:
    #         filtered_pos.append(num)
    # context.productlist = filtered_pos
    # print(context)
    



@frappe.whitelist(allow_guest = True)
def get_productlist_html(sn):
    productlist = get_productlist(sn)
    for i in productlist:
        if i.image:
            i.image = i.image.replace("'", "\\\'")
    return frappe.render_template('kensingtonbn/templates/includes/home/hpagefproducts.html', {        
        "productlist": productlist
    })
    

def get_productlist(sn):
    productlist = frappe.db.sql("""

         SELECT tabItem.item_code, tabItem.item_name, i.image, hp.thumbnail, s.group_title, hp.section, s.group_image, s.section_number, hp.batch_id, i.route, tabBatch.expiry_date AS expiry_date, tabBatch.best_value_date AS best_value_date
         FROM `tabHomepage Featured Product` as hp     
             INNER JOIN `tabWebsite Item` as i on hp.item_code=i.name 
             INNER JOIN tabItem on tabItem.item_code = i.item_code 
             LEFT OUTER JOIN `tabHomepage Product Section` as s on hp.section=s.name 
             LEFT OUTER JOIN tabBatch ON tabBatch.item =  tabItem.name
             
         WHERE (hp.batch_id = tabBatch.name OR hp.batch_id IS NULL)  AND s.section_number = """ + sn + """   order by hp.idx ASC limit 0, 100   
    
         """
     , as_dict=True)
    
    for  item in productlist:
        if item.batch_id:           
            productinfo = get_product_info_for_website(item.item_code, True , item.batch_id ).get('product_info').get('price')            
        else:
            productinfo = get_product_info_for_website(item.item_code, True ).get('product_info').get('price')
        if productinfo:
            item.update(productinfo)     
    return  productlist


# send email with payment link
@frappe.whitelist()
def send_email(order_name):
	customer = frappe.db.get_value('Sales Order' , order_name , 'customer')
	customer_email = frappe.db.get_value('Customer' , customer , 'email_id')
	message = '<p> Payment Request for '+ order_name + ' </p> <a href=/orders/'+ order_name + '> click here to pay </a>'	
	if customer_email:
		email_args = {
			"recipients": customer_email,
			"sender": None,
			"subject": 'Payment Request for '+ order_name ,
			"message": message ,
			"now": True
			}
		enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
		frappe.msgprint('Email Sent')
	else:
		frappe.msgprint('Customer doesn\'t have email')
 

@frappe.whitelist(allow_guest = True)
def get_slideshow_html(sn):
    return frappe.render_template('kensingtonbn/templates/includes/home/commercial'+sn+'.html', {
        "slideshow": get_slideshow(sn)
    })
    
def get_slideshow(sn):
 return  frappe.db.sql("""

         SELECT hpa.advertising_image, hpa.advertising_text, hpa.advertising_link, hpa.advertising_background_color, hpa.section_number
         FROM `tabHomepage Advertising` as hpa 
         WHERE hpa.section_number = """ + sn + """ order by hpa.idx ASC limit 0, 100   
    
         """
     , as_dict=True)




#  get discount price info

# -------------------------------------------------------------------------------


# .....
# def get_productlist(sn):
#     return  frappe.db.sql("select hp.item_code, hp.item_name, hp.image, hp.thumbnail, hp.group_title, hp.section_number, i.route from `tabHomepage Featured Product` as hp left join `tabItem` as i on hp.item_code=i.name where hp.section_number = " + sn + " order by hp.idx ASC limit 0, 100", as_dict=True)



# @frappe.whitelist(allow_guest = True)
# def get_productlist_html(sn):
#     productlist, price = get_productlist(sn)
#     return frappe.render_template('kensingtonbn/templates/includes/home/hpagefproducts.html', {
#         "productlist": productlist,
#         "price": price
#     })
    

# def get_productlist(sn):

#     from erpnext.e_commerce.shopping_cart.product_info import get_product_info_for_website

#     strQuery = """ 

#         SELECT tabItem.item_code, tabItem.item_name, i.image, hp.thumbnail, hp.group_title, hp.section_number, i.route 
#         FROM `tabHomepage Featured Product` as hp 
#             INNER JOIN `tabWebsite Item` as i on hp.item_code=i.name 
#             INNER JOIN tabItem on tabItem.item_code = i.item_code 
#         WHERE hp.section_number = """ + sn + """ order by hp.idx ASC limit 0, 100   

#         """

#     ItemNameList = frappe.db.sql(strQuery, as_dict=True)

#     pricedict = {}
#     innerindex = 1
#     if ItemNameList:
#         for ItemName in ItemNameList:
#             pricedict[innerindex] = get_product_info_for_website(ItemName.item_code)
#             innerindex += 1

#     return  ItemNameList, pricedict