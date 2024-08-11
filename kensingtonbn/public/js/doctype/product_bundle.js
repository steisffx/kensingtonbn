frappe.ui.form.on("Product Bundle", {
	refresh: function(frm){
		console.log("here");
	}
});

cur_frm.set_query("batch", "items", function(doc, cdt, cdn) {
	console.log("here");
	var d = locals[cdt][cdn];
	return{
		filters: [
			['Batch', 'item', '=', d.item_code],
		]
	}
});
