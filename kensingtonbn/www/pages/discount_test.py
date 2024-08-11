import frappe
# from erpnext.e_commerce.shopping_cart.product_info import get_product_info_for_website

# def get_context(context):
    # strQuery = """ SELECT item_name FROM `tabHomepage Featured Product` """        
    # context.items = frappe.db.sql(strQuery , as_dict = 1) 
    # context.test = 'Old Jamaica Diet Ginger Beer Can 330ml'
    # context.product_info = get_product_info_for_website(context.test, skip_quotation_creation=True).get('product_info')
    # # context.price = []
    # context.price = [context.product_info.get('price')]   
    # print(context)
    # return context 

# @frappe.whitelist(allow_guest = True)
# def get_productinfo_html():
#     return frappe.render_template('kensingtonbn/templates/includes/home/hpagefproducts.html', {
#         "productprice": get_product_info()     
        
#     })
   

# @frappe.whitelist(allow_guest = True)
# def get_product_info():
#     strQuery = """ SELECT item_name FROM `tabHomepage Featured Product` """        
#     items = frappe.db.sql(strQuery , as_dict = 1)    
#     for item in items:           
#         product_info = get_product_info_for_website(item.item_name, skip_quotation_creation=True).get('product_info')
#         price = [product_info['price']]
    
#     return price
        
    
