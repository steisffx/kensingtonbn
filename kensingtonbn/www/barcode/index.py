import frappe
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import base64
from barcode import get_barcode_class
from barcode import EAN13
from barcode.writer import SVGWriter
@frappe.whitelist(allow_guest = True)
def get_generate_barcodes_html():
    return frappe.render_template('kensingtonbn/templates/includes/barcode/barcode.html',{
        "productlist": generate_barcodes()
    })

def generate_barcodes():
    # CODE39 = get_barcode_class('code39')
    # images = []
    # items = [6211804065713,6211804065711,6211804065712]
    # for item in items:
    #     rv = BytesIO()
    #     CODE39(str(item), writer=ImageWriter()).write(rv)
    #     img_str = base64.b64encode(rv.getvalue()).decode()
    #     print('img_str')
    #     print(img_str)
    #     images.append(img_str)
    #     rv.close()
    # return images
    items =  frappe.db.get_all(
        "Item Barcode",
        fields=["barcode"],
        filters={
        'parent': 'Lockets Cranberry & Blueberry 41g'
        },
        order_by="barcode asc",
    )
    CODE39 = get_barcode_class('code39')
    Code128 = get_barcode_class('code128')
    EAN13 = get_barcode_class('ean13')
    images = []
    for item in items:
        barcode_value = item.get('barcode')
        if barcode_value:
            rv = BytesIO()
            Code128(str(barcode_value), writer=ImageWriter()).write(rv)
            img_str = base64.b64encode(rv.getvalue()).decode()
            images.append(img_str)
            rv.close()
    return images



@frappe.whitelist(allow_guest = True)
def get_jinja_barcode_image(barcode):
    Code128 = get_barcode_class('code128')
    # images = []
    rv = BytesIO()
    Code128(str(barcode), writer=ImageWriter()).write(rv)
    img_str = base64.b64encode(rv.getvalue()).decode()
    # images.append(img_str)
    rv.close()
    return img_str