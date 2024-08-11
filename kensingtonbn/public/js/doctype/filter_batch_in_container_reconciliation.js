frappe.ui.form.on("Container Reconciliation", "refresh", function(frm) {
    frm.fields_dict['items'].grid.get_field('batch_no').get_query = function(doc, cdt, cdn) {
        let child = locals[cdt][cdn];
        // console.log(child);
                return{	
            filters:[
                ['item', '=', child.item_code]
            ]
        }
    }
    });