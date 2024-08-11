// Copyright (c) 2022, ClefinCode and contributors
// For license information, please see license.txt

frappe.ui.form.on('Batch Barcode Reconciliation', {
	refresh: function(frm) {
		if (!frm.is_new()) {
		frm.add_custom_button(__('Batch Reconcile'), function(){ 
			frappe.db.get_doc('Batch Barcode Reconciliation', frm.doc.name)
			.then(r => {     
				frappe.call({  
					method: "kensingtonbn.kensingtonbn.doctype.batch_barcode_reconciliation.batch_barcode_reconciliation.update_batches",
					args: {
						doc: frm.doc.name ,						
					},
					callback: function(r) {						
						frappe.msgprint('Reconciliation Done');
						frm.reload_doc();
					}
                                                                                        
				});     
			
			});
		}).addClass("btn-primary").removeClass("btn-default");
	}
	}
});

