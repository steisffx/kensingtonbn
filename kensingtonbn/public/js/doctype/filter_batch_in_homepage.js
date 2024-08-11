frappe.ui.form.on("Homepage", "refresh", function(frm) {
    frm.fields_dict['products'].grid.get_field('batch_id').get_query = function(doc, cdt, cdn) {
        let child = locals[cdt][cdn];
            return{	
                filters:[
                    ['item_name', '=', child.item_name]
                ]
        }
    }
});
