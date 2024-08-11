frappe.ui.form.on("Item", "refresh", function(frm) {
frm.fields_dict['barcodes'].grid.get_field('batch_no').get_query = function(doc, cdt, cdn) {
			return{	
		filters:[
			['item', '=', frm.doc.name]
		]
	}
}
});