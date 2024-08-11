frappe.ui.form.on("Best Value", "refresh", function(frm) {
    frm.fields_dict['best_value_items'].grid.get_field('batch_id').get_query = function(doc, cdt, cdn) {
        let child = locals[cdt][cdn];
        // console.log(child);
                return{	
            filters:[
                ['item', '=', child.item_code]
            ]
        }
    }
    });