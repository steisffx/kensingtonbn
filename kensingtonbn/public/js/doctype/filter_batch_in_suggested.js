frappe.ui.form.on("Suggested Items", "refresh", function(frm) {
    frm.fields_dict['suggested_items_item'].grid.get_field('batch_id').get_query = function(doc, cdt, cdn) {
        let child = locals[cdt][cdn];
        // console.log(child);
                return{	
            filters:[
                ['item', '=', child.item_code]
            ]
        }
    }
    });