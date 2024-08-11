import frappe
from erpnext.stock.doctype.batch.batch  import get_batch_qty
import json
from frappe.utils.password import Auth
from passlib.context import CryptContext

from frappe import scrub
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.utils import nowdate, unique

passlibctx = CryptContext(
    schemes=[
        "pbkdf2_sha256",
        "argon2",
        "frappe_legacy",
    ],
    deprecated=[
        "frappe_legacy",
    ],
)

@frappe.whitelist(allow_guest = False)
def set_batch_ranking():
    strQuery = """
            SELECT  DISTINCT  tabWebsiteItem.item_code,	tabWebsiteItem.website_warehouse, tabWebsiteItem.ranking , tabBatch.name AS batch_no ,
                    tabBatch.ranking AS batch_ranking

            FROM `tabWebsite Item` AS tabWebsiteItem
            INNER JOIN `tabItem` ON tabWebsiteItem.item_code = tabItem.item_code
            LEFT OUTER JOIN `tabBatch` ON tabBatch.item =  tabItem.name 
            
            WHERE published = 1 AND tabBatch.disabled = 0 
                AND (tabBatch.expiry_date > CURRENT_TIMESTAMP OR tabBatch.expiry_date = '' OR tabBatch.expiry_date is null)
            ORDER BY batch_ranking DESC
             
            """
    website_items = frappe.db.sql(strQuery , as_dict = 1)    
    for item in website_items:        
        batch_doc = frappe.get_doc('Batch' , item.batch_no)
        qty = get_batch_qty(batch_no=item.batch_no, warehouse="Kensington Main Store - M", item_code=item.item_code)
        if qty == 0 or qty == []:
            batch_doc.set('ranking' , 0)            
        elif not batch_doc.ranking > 1:
            batch_doc.set('ranking' , 1)            
        batch_doc.save()
        frappe.db.commit()
    return ""

@frappe.whitelist(allow_guest = False)
def add_all_website_items():
    from erpnext.e_commerce.doctype.website_item.website_item import  make_website_item
    items = frappe.db.sql("""
        SELECT tabItem.name FROM `tabItem` AS tabItem 
            LEFT OUTER JOIN `tabWebsite Item` AS tabWebsiteItem ON tabItem.name = tabWebsiteItem.item_code
        WHERE tabWebsiteItem.name IS NULL  AND tabItem.disabled = 0
         
        limit 25

    """, as_dict = 1)

    x = 0
    errlog = ""
    for item in items:
        x += 1
        doc = frappe.get_doc("Item", item.name)
        try:
            make_website_item(doc)
            frappe.db.commit()
        except Exception as e:
            o  = e
            errlog += doc.name + " ||||| "
            print("|||||||||||| " + doc.name + " |||||||||||||||||")
    
    if not items:
        return "All Created"
    elif errlog != "":
        return "Error: " + errlog
    else:
        return "All Created"

@frappe.whitelist(allow_guest = False)
def reset_password_all_users():
    
    strQuery = """
        SELECT * FROM tabUser WHERE enabled = 1 AND user_type ='Website User';
        """
    users = frappe.db.sql(strQuery, as_dict = True)
    for element in users:
        user = frappe.get_doc('User' , element['name'])
        user.reset_password(user)


@frappe.whitelist(allow_guest = False)
def merge_containers(container1 , container2): 
    from kensingtonbn.kensingtonbn.doctype.container_reconciliation.container_reconciliation import get_items
    doc1 = frappe.get_doc('Container Reconciliation' , container1)
    doc2 = frappe.get_doc('Container Reconciliation' , container2)  
    container2_items = get_items(container2)   
    for item in container2_items:                  
        doc1.append("items",item)   
    
    doc1.save(ignore_permissions= True)
    doc2.delete(ignore_permissions= True)
    frappe.db.commit()
    return True

@frappe.whitelist(allow_guest = True)
def get_batch(doctype, txt, searchfield, start, page_len, filters): 
    item_code = filters.get("item_code")         
    out = frappe.db.sql(f""" 
    SELECT name
    FROM tabBatch
    WHERE item = '{item_code}' AND disabled = 0 AND batch_qty > 0 AND (expiry_date > CURRENT_TIMESTAMP OR expiry_date is null)
    """ , as_dict=True)  
    frappe.msgprint(item_code)     
    return out

@frappe.whitelist(allow_guest = False)
def set_order_type_in_invoices():
    """ set order_type to Shopping Cart in sales invoice if invoice arrives from website"""
    sales_orders = frappe.db.sql(""" 
    SELECT DISTINCT sales_order , parent
    FROM `tabSales Invoice Item`
    WHERE sales_order is not null and sales_order <> ''
    """ , as_dict = True)    
    for order in sales_orders:
        so_doc = frappe.get_doc('Sales Order' , order.sales_order)
        si_doc = frappe.get_doc('Sales Invoice' , order.parent)
        if so_doc.order_type == 'Shopping Cart':
            si_doc.order_type = 'Shopping Cart'
            si_doc.save(ignore_permissions= True)
    frappe.db.commit()

@frappe.whitelist(allow_guest = True)
def merge_contacts():
    try:
        users = frappe.db.sql("""
        SELECT name
        FROM `tabUser`
        WHERE enabled = 1        
        """ , as_dict = True)
        for user in users:
            contacts = frappe.db.sql(f"""
            SELECT name
            FROM `tabContact`
            WHERE user = '{user.name}'
            """ , as_dict = True)
            if len(contacts) == 2 :
                # 1- get Contact docs
                contact_doc1 = frappe.get_doc('Contact' , contacts[0].name)
                contact_doc2 = frappe.get_doc('Contact' , contacts[1].name)
                # 2- append customer referenc in child table
                if contact_doc1.links:
                    contact_doc2.links = contact_doc1.links
                    contact_doc2.save(ignore_permissions= True)
                    frappe.db.sql(f"""DELETE FROM `tabContact` WHERE name = '{contact_doc1.name}' """)                
                else:
                    contact_doc1.links = contact_doc2.links
                    contact_doc1.save(ignore_permissions= True)
                    frappe.db.sql(f"""DELETE FROM `tabContact` WHERE name = '{contact_doc2.name}' """)   
                frappe.db.commit()
        return [{"status":1,"description":"Done Successfully","data":users}]
    except Exception as e:
        return [{"status":0,"description":"Not Available","data":f"{e}"}]



###Create new container reconciliation    
@frappe.whitelist()
def add_container_reconciliation(items):
    items = json.loads(items)
    itemslist = []
    
    for item in items:
        ContainerReconciliationItem = frappe.new_doc("Container Reconciliation Item")
        Detailvalues = {
            "doctype": "Container Reconciliation Item",
            "item_code": item["item_code"],
            "qty": item["qty"],
            "uom":get_default_info_for_item(item["item_code"])[0]["uom"],
            "batch_no": item["batch_no"],
            "warehouse":item['warehouse']  if 'warehouse' in item else get_default_info_for_item(item["item_code"])[0]["warehouse"],
            "conversion_factor":get_default_info_for_item(item["item_code"])[0]["uom_conversion_factor"],
            # "t_warehouse": frappe.get_all("Item Default",fields=["default_warehouse"],filters = {"parent":item["item_code"]})[0].default_warehouse,
        }
        ContainerReconciliationItem.update(Detailvalues)
        itemslist.append(ContainerReconciliationItem)    

    ContainerReconciliation = frappe.new_doc("Container Reconciliation")
    values = {
        "doctype": "Container Reconciliation",
        "naming_series": "PU-CO-.YYYY.-.####",
        "company": "MAJESTICA",
        "items": itemslist
    }

    ContainerReconciliation.update(values)
    ContainerReconciliation.insert(ignore_permissions=True)
    # ContainerReconciliation.submit()
    frappe.db.commit()

    return [{"status":"Done", "id": ContainerReconciliation.name}]

def get_items_of_barcode(barcode):
    items = frappe.db.get_all('Item Barcode', {'barcode': barcode}, 'parent')
    itemslist = []
    for item in items:
        itemslist.append(item.parent)
    return {'item_code': ("in", itemslist)}

@frappe.whitelist()
def view_container_reconciliation(**kwargs):
    # from kensingtonbn.kensingtonbn.doctype.container_reconciliation.container_reconciliation import get_items
    kwargs=frappe._dict(kwargs)
    start = kwargs.start or 0
    page_length = kwargs.page_length or 20
    barcode = kwargs.barcode
    filters = {}
    containers = []
    if barcode:
        filters = get_items_of_barcode(barcode)

        containers = frappe.db.get_all('Container Reconciliation Item', filters = filters, fields = ['parent'], distinct=1, start=start, limit_page_length=page_length)

    if not containers:
        containers = frappe.db.get_all('Container Reconciliation', start=start, limit_page_length=page_length)
    
    containerslist = []
    for container in containers:
        key = list(container.keys())[0]
        doc = frappe.get_doc('Container Reconciliation', container[str(key)])
        # containerslist.append(doc)
        containerslist.append(doc)
        
    #     items = frappe.get_all("Container Reconciliation Item",
    #             fields=["item_code" ,"item_name" , "qty" , "uom" , "conversion_factor" ,  "stock_uom" , "warehouse"  , "batch_no" , "best_value_date" , 'barcode','parent' ],
    #             filters = {"parent":container.name})
    #     for item in items:
    #         containerslist.append(item)
    # print(containerslist)
    return [{'status':1,"description":"Done successfully","data":containerslist}]
    # return containers1


##Update container reconciliation items table by adding new items
@frappe.whitelist()
def add_container_reconciliation_items(**kwargs):
# def add_container_reconciliation_items(container, newitems):
    kwargs=frappe._dict(kwargs)
    container=kwargs.container
    newitems=kwargs.newitems
    doc = frappe.get_doc('Container Reconciliation', container)
    
    # record = frappe.get_list('Container Reconciliation Item', filters = {"parent":container})
    #delete current items table
    # if(len(record)>0):
        # frappe.db.delete('Container Reconciliation Item', record[0])
        # doc.save(ignore_permissions=True)
        # frappe.db.commit()
    # doc.save(ignore_permissions=True)
    #create new item table
    doc_items=[]
    newitems = json.loads(newitems)
    for item in newitems:                
        item_doc = frappe.new_doc("Container Reconciliation Item")
        items = {
            "doctype": "Container Reconciliation Item",
            "item_code": item["item_code"],
            "qty": item["qty"],
            # "uom":get_default_info_for_item(item["item_code"])[0]["uom"],
            "uom":item["uom"] if 'uom' in item else get_default_info_for_item(item["item_code"])[0]["uom"],
            "warehouse":item['warehouse']  if 'warehouse' in item else get_default_info_for_item(item["item_code"])[0]["warehouse"],
            "batch_no": item["batch_no"],
            "best_value_date": item["best_value_date"],
            # "conversion_factor":get_default_info_for_item(item["item_code"])[0]["uom_conversion_factor"],
            "conversion_factor":item["conversion_factor"] if 'conversion_factor' in item else get_default_info_for_item(item["item_code"])[0]["uom_conversion_factor"],
        }
        item_doc.update(items)
        doc_items.append(items)
    items_list = {
        "items": doc_items
    }
    doc.update(items_list)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    

    return "Done"

###Delete container reconciliation
@frappe.whitelist()
def delete_container_reconciliation(container_reconciliation):
    container_reconciliation_doc = frappe.get_doc('Contanier Reconciliation', container_reconciliation)
    if container_reconciliation_doc.docstatus == 1:
        container_reconciliation_doc.cancel()
    container_reconciliation_doc.delete()
    frappe.db.commit()

@frappe.whitelist(allow_guest = True)
def login(email , password): 
    user = frappe.db.get("User", {"email": email}) 
    if user:
        if not user.enabled:          
            return [{"status":0,"description":"User Account is disabled","data":None}]
        result =(
            frappe.qb.from_(Auth)
            .select(Auth.name, Auth.password)
            .where(
                (Auth.doctype == "User")
                & (Auth.name == user.email)
                & (Auth.fieldname == "password")
                & (Auth.encrypted == 0)
            )
            .limit(1)
            .run(as_dict=True)
        )

        if not result or not passlibctx.verify(password, result[0].password):
            return [{"status":0,"description":"Incorrect email or password","data":None}]
            
        else:
            user = frappe.get_doc('User' , email)
            api_secret = frappe.generate_hash(length=15)
            # if api key is not set generate api key
            if not user.api_key:
                api_key = frappe.generate_hash(length=15)
                user.api_key = api_key
            user.api_secret = api_secret
            user.save(ignore_permissions=True)
            frappe.db.commit()               
            return [{'status':1,"description":"Done successfully","data":[{"api_key":user.api_key,"api_secret":api_secret}]}]
            
    else:    
        return [{"status":0,"description":"User doesn't exist","data":None}]
        
@frappe.whitelist()
def view_stock_reconciliations(**kwargs):
    kwargs=frappe._dict(kwargs)
    start = kwargs.start or 0
    page_length = kwargs.page_length or 20
    barcode = kwargs.barcode
    stock_recs = []
    if barcode:
        filters = get_items_of_barcode(barcode)
        stock_recs = frappe.db.get_all('Stock Reconciliation Item', filters = filters, fields = ['parent'], distinct=1, start=start, limit_page_length=page_length)

    if not stock_recs:
        stock_recs = frappe.db.get_all('Stock Reconciliation', {'docstatus': 0}, start=start, limit_page_length=page_length)
    
    stock_rec_list = []
    for stock_rec in stock_recs:
        key = list(stock_rec.keys())[0]
        doc = frappe.get_doc('Stock Reconciliation', stock_rec[str(key)])
        stock_rec_list.append(doc)
        
    return [{'status':1,"description":"Done successfully","data":stock_rec_list}]

###Create new stock reconciliation
@frappe.whitelist()
def add_stock_reconciliation(**kwargs):
    kwargs=frappe._dict(kwargs)
    items=kwargs.itemslist
    main_warehouse=kwargs.main_warehouse
    main_company=kwargs.main_company
    items = json.loads(items)
    itemslist = []
    
    for item in items:
        warehouse=item['warehouse']  if 'warehouse' in item else main_warehouse
        StockReconciliationItem = frappe.new_doc("Stock Reconciliation Item")
        Detailvalues = {
            "doctype": "Stock Reconciliation Item",
            "item_code": item["item_code"],
            "qty": item["qty"],
             "warehouse":warehouse,
            "batch_no": item["batch_no"],
            "valuation_rate": item["valuation_rate"],
            }
        StockReconciliationItem.update(Detailvalues)
        itemslist.append(StockReconciliationItem)    

    StockReconciliation = frappe.new_doc("Stock Reconciliation")
    values = {
        "doctype": "Stock Reconciliation",
        "naming_series": "SR/.#####",
        "company": main_company,
        "purpose": "Stock Reconciliation",
        "items": itemslist
    }

    StockReconciliation.update(values)
    StockReconciliation.insert(ignore_permissions=True)
    frappe.db.commit()

    return [{"status":"Done", "id": StockReconciliation.name}]

## Update stock reconciliation items table by adding new items
@frappe.whitelist()
def add_stock_reconciliation_items(**kwargs):
# def add_stock_reconciliation_items(stock_reconciliation, newitems):
    kwargs=frappe._dict(kwargs)
    stock_reconciliation=kwargs.stock_reconciliation
    newitems=kwargs.newitems
    doc = frappe.get_doc('Stock Reconciliation', stock_reconciliation)
    doc_items=[]
    newitems = json.loads(newitems)
    for item in newitems:
        if 'warehouse' not in item and not get_default_info_for_item(item["item_code"])[0]["warehouse"]:
            return [{"status":"ERR", "message": "You havan't specify warehouse for item {0} and there is no default warehouse for this item".format(item["item_code"])}]
                     
        item_doc = frappe.new_doc("Stock Reconciliation Item")
        items = {
            "doctype": "Stock Reconciliation Item",
            "item_code": item["item_code"],
            "qty": item["qty"],
            # "uom": get_default_info_for_item(item["item_code"])[0]["uom"],
            "warehouse": item['warehouse']  if 'warehouse' in item else get_default_info_for_item(item["item_code"])[0]["warehouse"],
            "batch_no": item["batch_no"],
            # "serial_no": item["serial_no"],
            # "barcode":item["barcode"],
            "valuation_rate": item["valuation_rate"],
            # "conversion_factor": get_default_info_for_item(item["item_code"])[0]["uom_conversion_factor"],
        }
        item_doc.update(items)
        doc_items.append(items)
    items_list = {
        "items": doc_items
    }
    doc.update(items_list)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    

    return "Done"

###Delete stock reconciliation
@frappe.whitelist()
def delete_stock_reconciliation(stock_reconciliation):
    stock_reconciliation_doc = frappe.get_doc('Stock Reconciliation', stock_reconciliation)
    if stock_reconciliation_doc.docstatus == 1:
        stock_reconciliation_doc.cancel()
    stock_reconciliation_doc.delete()
    frappe.db.commit()

@frappe.whitelist()
def view_stock_entries(**kwargs):
    kwargs=frappe._dict(kwargs)
    start = kwargs.start or 0
    page_length = kwargs.page_length or 20
    barcode = kwargs.barcode
    stock_entries = []
    if barcode:
        filters = get_items_of_barcode(barcode)
        stock_entries = frappe.db.get_all('Stock Entry Detail', filters = filters, fields = ['parent'], distinct=1, start=start, limit_page_length=page_length)

    if not stock_entries:
        stock_entries = frappe.db.get_all('Stock Entry', {'docstatus': 0}, start=start, limit_page_length=page_length)
    
    stock_entries_list = []
    for stock_entry in stock_entries:
        key = list(stock_entry.keys())[0]
        doc = frappe.get_doc('Stock Entry', stock_entry[str(key)])
        stock_entries_list.append(doc)
        
    return [{'status':1,"description":"Done successfully","data":stock_entries_list}]

###Create new stock entry
@frappe.whitelist()
def add_stock_entry(**kwargs):
    kwargs=frappe._dict(kwargs)
    toWrehouse=kwargs.to_warehouse
    fromWarehouse=kwargs.from_warehouse
    stockEntryType=kwargs.stock_entry_type
    items=kwargs.itemslist
    items = json.loads(items)
    itemslist = []
    
    for item in items:
        if  'warehouse' not in item and not get_default_info_for_item(item["item_code"])[0]["warehouse"]:
            return [{"status":"ERR", "message": "You havan't specify warehouse for item {0} and there is no default warehouse for this item".format(item["item_code"])}]
        
        StockEntryItem = frappe.new_doc("Stock Entry Detail")
        Detailvalues = {
            "doctype": "Stock Entry Detail",
            "item_code": item["item_code"],
            "qty": item["qty"],
            "uom":get_default_info_for_item(item["item_code"])[0]['uom'],
            "batch_no": item["batch_no"],
            "serial_no": item["serial_no"],
            "barcode":item["barcode"],
            "basic_rate": item["basic_rate"],
            "conversion_factor":get_default_info_for_item(item["item_code"])[0]["uom_conversion_factor"]
            }
        StockEntryItem.update(Detailvalues)
        itemslist.append(StockEntryItem)    

    StockEntry = frappe.new_doc("Stock Entry")
    values = {
                "doctype": "Stock Entry",
                "company": "MAJESTICA",
                "stock_entry_type": stockEntryType,
                "items": itemslist,
                "to_warehouse": toWrehouse,
                "from_warehouse": fromWarehouse,
              }
    StockEntry.update(values)
    StockEntry.insert(ignore_permissions=True)
    frappe.db.commit()

    return [{"status":"Done", "id": StockEntry.name}]

## Update stock entry items table by adding new items
@frappe.whitelist()
def add_stock_entry_items(**kwargs):
    kwargs=frappe._dict(kwargs)
    toWrehouse=kwargs.to_warehouse
    fromWarehouse=kwargs.from_warehouse
    stockEntryType=kwargs.stock_entry_type
    stock_entry=kwargs.stock_entry
    newitems=kwargs.newitems
    doc = frappe.get_doc('Stock Entry', stock_entry)
    doc_items=[]
    newitems = json.loads(newitems)
    for item in newitems:   
        if  'warehouse' not in item and not get_default_info_for_item(item["item_code"])[0]["warehouse"] and not doc.to_warehouse:
            return [{"status":"ERR", "message": "You havan't specify warehouse for item {0} and there is no default warehouse for this item".format(item["item_code"])}]
                     
        item_doc = frappe.new_doc("Stock Entry Detail")
        
        items = {
            "doctype": "Stock Entry Detail",
            "item_code": item["item_code"],
            "qty": item["qty"],
            # "uom":get_default_info_for_item(item["item_code"])[0]['uom'],
            "uom":item["uom"] if 'uom' in item else get_default_info_for_item(item["item_code"])[0]['uom'],
            "batch_no": item["batch_no"],
            "serial_no": item["serial_no"],
            "barcode":item["barcode"],
            "basic_rate": item["basic_rate"],
            # "conversion_factor":get_default_info_for_item(item["item_code"])[0]["uom_conversion_factor"]
            "conversion_factor":item["conversion_factor"] if 'conversion_factor' in item else get_default_info_for_item(item["item_code"])[0]["uom_conversion_factor"]
        }
        item_doc.update(items)
        doc_items.append(items)
    items_list = {
        "items": doc_items,
        "stock_entry_type": stockEntryType,
        "to_warehouse": toWrehouse,
        "from_warehouse": fromWarehouse,
    }
    doc.update(items_list)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return "Done"

###Delete stock entry
@frappe.whitelist()
def delete_stock_entry(stock_entry):
    stock_entry_doc = frappe.get_doc('Stock Entry', stock_entry)
    if stock_entry_doc.docstatus == 1:
        stock_entry_doc.cancel()
    stock_entry_doc.delete()
    frappe.db.commit()

## Get Items of a doctype (stock reconciliation, stock entry, container reconciliation)
@frappe.whitelist()
def get_items(doctype, doc_name): 
    doc = frappe.get_doc(doctype, doc_name)
    if doctype == "Stock Entry":
        child_doctype = "Stock Entry Detail"
    else:
        child_doctype = doctype + " Item"
    items_list = []
    for item in doc.items:
        item_doc = frappe.get_doc(child_doctype, {'parent': doc_name})
        items_list.append(item_doc)
    return [{"description":"Done successfully","data":items_list}]
            


# @frappe.whitelist()
# def view_uom_warehouse_batch_list(doc,item_code):
#     # containers = frappe.db.get_all('Container Reconciliation')
#     batch = frappe.db.get_list('')
#     frappe.db.get_list('Batch',
#     filters={
#         'status': 'Open'
#     },
#     fields=['subject', 'date'],
#     order_by='date desc',
#     start=10,
#     page_length=20,
#     as_list=True
# )

#     containerslist = []
#     for container in containers:
#         doc = frappe.get_doc('Container Reconciliation', container.name)
#         containerslist.append(doc)

#     # print(containerslist)
#     return [{'status':1,"description":"Done successfully","data":containerslist}]
#     # return containers1

@frappe.whitelist()
def get_uoms_list():
    return frappe.db.get_all("UOM", {"enabled": 1})

@frappe.whitelist()
def get_companies_list():
    return frappe.db.get_all("Company", {})


@frappe.whitelist()
def get_batchs_list(**kwargs):
    kwargs=frappe._dict(kwargs)
    item_code = kwargs.item_code
    if item_code: 
        return frappe.db.get_all("Batch" , {"disabled": 0, "item": item_code})
    return frappe.db.get_all("Batch" , {"disabled": 0})

@frappe.whitelist()
def get_warehouses_list():
    return frappe.db.get_all("Warehouse", {"disabled": 0})


@frappe.whitelist()
def get_items_MainWarehouse(key, barcode, limit_start = None, limit = None):

    strQuery = """ 
    SELECT DISTINCT tabItem.item_code, tabItem.item_name, tabBin.actual_qty , tabItem.image
    
    FROM tabItem 
        LEFT OUTER JOIN
        (SELECT tabBin.item_code, SUM(actual_qty) AS actual_qty
                FROM tabBin 
                WHERE warehouse IN ( SELECT tabItemDefault.default_warehouse 
                                    FROM `tabItem` AS tabItem INNER JOIN `tabItem Default` AS tabItemDefault ON  tabItemDefault.parent = tabItem.item_code
                                    WHERE tabItem.item_code = tabBin.item_code)
        GROUP BY tabBin.item_code) AS tabBin on tabBin.item_code = tabItem.item_code
    """
    if barcode:
        # strQuery += """ 
        #     INNER JOIN `tabItem Barcode` as tabItemBarcode on tabItemBarcode.parent = tabItem.name 
        #     WHERE tabItemBarcode.barcode = '""" + barcode + """'
        #     """
        # strQuery += " WHERE  tabItem.item_code = '" + barcode + "' and tabItem.has_variants = 0"
        strQuery += """ 
            INNER JOIN `tabItem Barcode` as tabItemBarcode on tabItemBarcode.parent = tabItem.name 
            WHERE tabItemBarcode.barcode = '""" + barcode + """' and tabItem.has_variants = 0
            """
    elif key:
        strQuery += """ LEFT OUTER JOIN `tabItem Barcode` as tabItemBarcode on tabItemBarcode.parent = tabItem.name WHERE tabItemBarcode.barcode = '""" + key + """' and tabItem.has_variants = 0 """
        strQuery += " OR ( tabItem.item_code like '%" + key + "%' OR tabItem.item_name like '%" + key + "%' OR tabItem.description like '%" + key + "%' ) and tabItem.has_variants = 0"
    else: strQuery += " WHERE  tabItem.has_variants = 0"

    if limit and not limit_start:
        strQuery += " LIMIT " + limit + " "
    elif limit and limit_start:
        strQuery += " LIMIT " + limit_start + "," + limit + " "

    return frappe.db.sql(strQuery, as_dict = True)


@frappe.whitelist()
def get_default_info_for_item(item_code):
    from erpnext.stock.doctype.item.item import get_item_details
    from erpnext.stock.get_item_details import get_conversion_factor
    # doc = frappe.get_doc('Item', item_code)
    
    item_data = get_item_details(item_code,'MAJESTICA')
    
    conversion_factor = get_conversion_factor(item_code, item_data.stock_uom).get("conversion_factor")
    
    return [{"warehouse":item_data.default_warehouse ,"uom":item_data.stock_uom ,"uom_conversion_factor":conversion_factor}]

@frappe.whitelist()
def get_valuation_rate_for_item(**kwargs):
    kwargs=frappe._dict(kwargs)
    item_code = kwargs.item_code
    warehouse = kwargs.warehouse
    batch_no = kwargs.batch_no
    from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import get_stock_balance_for
    from frappe.utils import now_datetime
    now = now_datetime()
    posting_date = now.strftime('%Y-%m-%d')
    posting_time = now.strftime('%H:%M:%S.%f')
    item_data = get_stock_balance_for(item_code, warehouse, posting_date=posting_date, posting_time=posting_time, batch_no = batch_no)
    rate = item_data['rate']
    return [{"valuation_rate":rate,"qty":item_data['qty']}]

# APIs for Item Label
# get all Item Label list
@frappe.whitelist()
def view_item_label(**kwargs):
    kwargs=frappe._dict(kwargs)
    start = kwargs.start or 0
    page_length = kwargs.page_length or 20
    barcode = kwargs.barcode
    itemLabels = []
    if barcode:
        filters = get_items_of_barcode(barcode)
        itemLabels = frappe.db.get_all('Item Label Item', filters = filters, fields = ['parent'], distinct=1, start=start, limit_page_length=page_length)

    if not itemLabels:
        itemLabels = frappe.db.get_all('Item Label', start=start, limit_page_length=page_length)
    
    itemLabelslist = []
    for itemLabel in itemLabels:
        key = list(itemLabel.keys())[0]
        doc = frappe.get_doc('Item Label', itemLabel[str(key)])
        itemLabelslist.append(doc)
    return [{'status':1,"description":"Done successfully","data":itemLabelslist}]


##Update item label items table with new items
@frappe.whitelist()
def add_item_label_items(**kwargs):
    kwargs=frappe._dict(kwargs)
    item_label=kwargs.item_label
    newitems=kwargs.newitems
    doc = frappe.get_doc('Item Label', item_label)
    doc_items=[]
    newitems = json.loads(newitems)
    for item in newitems:                
        item_doc = frappe.new_doc("Item Label Item")
        items = {
            "doctype": "Item Label Item",
            "item_code": item["item_code"],
            "qty": item["qty"],
            "price_list_rate":item["price_list_rate"],
            "batch_no": item["batch_no"],
            "barcode":item["barcode"],
        }
        item_doc.update(items)
        doc_items.append(items)
    items_list = {
        "items": doc_items
    }
    doc.update(items_list)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return "Done"
    
###Create new item label
@frappe.whitelist()
def add_item_label(items):
    items = json.loads(items)
    itemslist = []
    for item in items:
        itemLabelItem = frappe.new_doc("Item Label Item")
        Detailvalues = {
            "doctype": "Item Label Item",
            "item_code": item["item_code"],
            "qty": item["qty"],
            "price_list_rate":item["price_list_rate"],
            "batch_no": item["batch_no"],
            "barcode":item["barcode"],
        }
        itemLabelItem.update(Detailvalues)
        itemslist.append(itemLabelItem)    

    itemLabel = frappe.new_doc("Item Label")
    values = {
        "doctype": "Item Label",
        "naming_series": "Label.#####",
        "company": "MAJESTICA",
        "Currency": "BND",
        "items": itemslist
    }
    itemLabel.update(values)
    itemLabel.insert(ignore_permissions=True)
    frappe.db.commit()

    return [{"status":"Done", "id": itemLabel.name}]

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    conditions = []
    print("/////////////////////////////////////////////////")
    print("/////////////////////////////////////////////////")
    print("/////////////////////////////////////////////////")
    print("/////////////////////////////////////////////////")
    if isinstance(filters, str):
        filters = json.loads(filters)

    #Get searchfields from meta and use in Item Link field query
    meta = frappe.get_meta("Item", cached=True)
    searchfields = meta.get_search_fields()

    # these are handled separately
    ignored_search_fields = ("item_name", "description")
    for ignored_field in ignored_search_fields:
        if ignored_field in searchfields:
            searchfields.remove(ignored_field)

    columns = ''
    extra_searchfields = [field for field in searchfields
        if not field in ["name", "item_group", "description", "item_name"]]

    if extra_searchfields:
        columns = ", " + ", ".join(extra_searchfields)

    searchfields = searchfields + [field for field in[searchfield or "name", "item_code", "item_group", "item_name"]
        if not field in searchfields]
    searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])

    if filters and isinstance(filters, dict):
        if filters.get('customer') or filters.get('supplier'):
            party = filters.get('customer') or filters.get('supplier')
            item_rules_list = frappe.get_all('Party Specific Item',
                filters = {'party': party}, fields = ['restrict_based_on', 'based_on_value'])

            filters_dict = {}
            for rule in item_rules_list:
                if rule['restrict_based_on'] == 'Item':
                    rule['restrict_based_on'] = 'name'
                filters_dict[rule.restrict_based_on] = []

            for rule in item_rules_list:
                filters_dict[rule.restrict_based_on].append(rule.based_on_value)

            for filter in filters_dict:
                filters[scrub(filter)] = ['in', filters_dict[filter]]

            if filters.get('customer'):
                del filters['customer']
            else:
                del filters['supplier']


    description_cond = ''
    sku_values_cond = ' or tabItem.sku_sos like%(_txt)s or tabItem.sku_1 like%(_txt)s or tabItem.sku_2 like%(_txt)s or tabItem.hs_code like%(_txt)s'
    if frappe.db.count('Item', cache=True) < 50000:
        # scan description only if items are less than 50000
        description_cond = 'or tabItem.description LIKE %(txt)s'
    return frappe.db.sql("""select
            tabItem.name, tabItem.item_name, tabItem.item_group,
        if(length(tabItem.description) > 40, \
            concat(substr(tabItem.description, 1, 40), "..."), description) as description
        {columns}
        from tabItem
        where tabItem.docstatus < 2
            and tabItem.disabled=0
            and tabItem.has_variants=0
            and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
            and ({scond} or tabItem.item_code IN (select parent from `tabItem Barcode` where barcode LIKE %(txt)s)
                {description_cond} {sku_values_cond})
            {fcond} {mcond}
        order by
            if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
            if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
            idx desc,
            name, item_name
        limit %(start)s, %(page_len)s """.format(
            columns=columns,
            scond=searchfields,
            fcond=get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
            mcond=get_match_cond(doctype).replace('%', '%%'),
            description_cond = description_cond,
            sku_values_cond = sku_values_cond
            ),
            {
                "today": nowdate(),
                "txt": "%%%s%%" % txt,
                "_txt": txt.replace("%", ""),
                "start": start,
                "page_len": page_len
            }, as_dict=as_dict)

@frappe.whitelist()
def sku_item_code(test):
    item = frappe.db.sql(f"""
        SELECT item_code
        FROM `tabItem`
        WHERE sku_sos='{test}'
        or sku_1='{test}'
        or sku_2='{test}'
        or hs_code='{test}'
        """, as_dict = True)
    return item

def create_customer(user):
    customer = frappe.new_doc("Customer")

    customer.update({
        "customer_name": user.full_name,
        "territory": "Brunei Darussalam",
        "customer_group": "Bronz",
        "whatsapp_no": user.phone,
        "customer_primary_contact": frappe.db.get_value("Contact", {"user": user.name}, "name")
    })
    customer.insert(ignore_permissions = True)
    frappe.db.commit()
