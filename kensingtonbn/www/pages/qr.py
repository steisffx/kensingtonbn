import io
import os
import frappe
from frappe import _
import pyqrcode

def create_qr_code(doc, error='H'):
    """Create QR Code after inserting Item
    """

        # if QR Code field not present, do nothing
    if not hasattr(doc, 'qr_code'):
        return

    # Don't create QR Code if it already exists
    qr_code = doc.get("qr_code")
    if qr_code and frappe.db.exists({"doctype": "File", "file_url": qr_code}):
        return

    # meta = frappe.get_meta('Item')
    # for field in meta.get_image_fields():
    #     if field.fieldname == 'qr_code':
    child = frappe.get_all("Item Barcode", filters = dict(parent=doc.name), fields = 'barcode' )

    thisItem = frappe.get_doc(doc, doc.name)
    thisItem.as_dict()
    # child = frappe.db.get_value(doc, doc.name , 'item_code')
    # print(thisItem)
    print(child[1].barcode)  
    qr_image = io.BytesIO()
    # url = pyqrcode.create('http://uca.edu')
    # url = pyqrcode.create(doc.item_code)
    url = pyqrcode.create(child[0].barcode)
    # if number we delete  , scale=8
    # url.png(qr_image, scale=8)
    url.png(qr_image)
    # print("test")
    # print(url.terminal(quiet_zone=1))
    name = frappe.generate_hash(doc.name, 5)
    filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "is_private": 0,
        "content": qr_image.getvalue(),
        "attached_to_doctype": doc.get("doctype"),
        "attached_to_name": doc.get("name"),
        "attached_to_field": "qr_code"
    })
    _file.save()
    doc.db_set('qr_code', _file.file_url)
    doc.notify_update()

def delete_qr_code_file(doc, method):
	"""Delete QR Code on deleted Item"""

	if hasattr(doc, 'qr_code'):
		if doc.get('qr_code'):
			file_doc = frappe.get_list('File', {
				'file_url': doc.get('qr_code')
			})
			if len(file_doc):
				frappe.delete_doc('File', file_doc[0].name)