// Copyright (c) 2022, ClefinCode and contributors
// For license information, please see license.txt

frappe.ui.form.on('Container Reconciliation', {
    onload (frm) {        
	   // this delete first row of items
	   if (frm.is_new()) {
            frm.doc.items=[];
            refresh_field("items");     
        }        
    },
	refresh: function(frm) {                                   
        if (!frm.is_new()) {
            frm.add_custom_button(__('Merge Containers '), function(){ 
                var d = new frappe.ui.Dialog({
                    title: __('Merge Containers'),
                    
                    fields: [{
                        "label": "ID of the Container you want to merge this container with: ",
                        "fieldname": "contanier",
                        "fieldtype": "Link",
                        "options": "Container Reconciliation",
                        "get_query": function () {
                            return {
                                filters: [
                                    ["Container Reconciliation", "name", "!=", frm.doc.name]
                                ]
                            };
                        }
                    }],
                    primary_action: function() {
                        var data = d.get_values();
                        frappe.confirm(__(`Are you sure that you want to merge this container with ${data.contanier} contanier?`), function() {
                                frappe.call({
                                method: "kensingtonbn.www.api.api.merge_containers",
                                args: {
                                    container1: frm.doc.name ,
                                    container2: data.contanier
                                },
                                callback: function(r) {
                                    if(r.message){
                                        frappe.msgprint(`Done! ${frm.doc.name} and ${data.contanier} containers are merged.`)
                                        d.hide();
                                        frm.reload_doc();
                                    }
                                    else{
                                        frappe.throw(`Failed to merge ${frm.doc.name} with ${data.contanier}!`) 
                                    }
                                }
                            });
                        })
                    }
                })
                d.show();
            }).addClass("btn-primary").removeClass("btn-default");

            frm.add_custom_button(__('Reconcile '), function(){  
                if(frm.doc.combine_similar_items == 0 || frm.is_dirty()){
                    frappe.msgprint('You must save and combine items before reconcile')
                }else{
                    frm.set_df_property('section_break_1', 'hidden', 0)                
                frappe.db.get_doc('Container Reconciliation', frm.doc.name)
                .then(r => {                          
                    var html = "";                        
                    var extra_html = "" ;
                    var $frm = frm ;             
                    frappe.call({                                                        
                        method: "kensingtonbn.kensingtonbn.doctype.container_reconciliation.container_reconciliation.get_reconcile_result",
                        args: {
                            doc_name : frm.doc.name
                        },
                        callback: function(r) {  
                            let not_match_items  = r.message.not_match_items;
                            let not_match_invoice_items = r.message.not_match_invoice_items;                    
                            let extra_qty = r.message.extra_qty;
                            let missing_qty = r.message.missing_qty ; 
                                                    
                            
                            if (not_match_invoice_items.length != 0 || missing_qty != 0 ){
                                    html += "<h4>Missing in container</h4>" ;
                                    html+="<table class='table table-bordered'>"
                                    html +="<tr><th>Item</th><th>Batch</th><th>Required Quantity</th><th>Received Quantity</th><th>Missing Quantity</th></tr>"
                                for (let item in not_match_invoice_items){
                                    html += `<tr> <td>${not_match_invoice_items[item].item_code} </td><td>${get_batch(not_match_invoice_items[item])}</td><td> ${not_match_invoice_items[item].qty} Nos</td><td>0</td><td>${not_match_invoice_items[item].qty} Nos</td></tr> `
                                }
                            }
                            if(missing_qty.length != 0){
                                for(let item in missing_qty){                                    
                                    html += `<tr> <td> ${missing_qty[item].item_code} </td><td>${get_batch(missing_qty[item])}</td><td> ${missing_qty[item].qty} Nos </td><td> ${missing_qty[item].container_qty} Nos </td><td>${missing_qty[item].qty_missing} Nos</td></tr>`
                                }
                            }
                            html +="</table>";
                            if(not_match_items.length != 0 || extra_qty != 0){
                                html += "<h4 >Extra in container</h4>" ;
                                html+="<table class='table table-bordered'>"
                                    html +="<tr><th>Item</th><th>Batch</th><th>Required Quantity</th><th>Received Quantity</th><th>Extra Quantity</th></tr>"
                                for (let item in not_match_items){    
                                    html += `<tr><td> ${not_match_items[item].item_code} </td><td>${get_batch(not_match_items[item])}</td><td>0</td><td> ${not_match_items[item].qty} Nos</td><td>${not_match_items[item].qty} Nos</td></tr>`                                
                                }
                            }
                           
                            if(extra_qty.length != 0){
                                for(let item in extra_qty){                                    
                                    html += `<tr><td> ${extra_qty[item].item_code} </td><td> ${get_batch(extra_qty[item])} </td><td> ${extra_qty[item].qty} Nos </td><td> ${extra_qty[item].container_qty} Nos </td><td>${extra_qty[item].qty_extra} Nos</td></tr>`
                                }
                            }
                            html +="</table>";                            
                            $frm.set_df_property('reconcile_result', 'options' , html) 

                            
                            }   
                                                       
                        });               
                    
                })
                }         
                
                
            }).addClass("btn-primary").removeClass("btn-default");

                // if(frm.doc.combine_similar_items == 1){
                    frm.add_custom_button(__('Create Purchse Reciepts'), function(){ 
                        if(frm.doc.combine_similar_items == 0 || frm.is_dirty()){
                            frappe.msgprint('You must save and combine items before create purchase receipts');
                        }else{
                            frappe.call({                                                        
                                method: "kensingtonbn.kensingtonbn.doctype.container_reconciliation.container_reconciliation.make_purchase_receipts_from_invoice_container",
                                args: {
                                    doc_name : frm.doc.name
                                },
                                callback: function(r) {           
                                    frm.reload_doc();
                                    }   
                                                               
                                });
                            }                                              
                                           
                            
             }).addClass("btn-primary").removeClass("btn-default"); 
            // }     
                   
            frm.add_custom_button(__('Combine Similar Items'), function(){ 
                if(frm.is_dirty()){
                    frappe.msgprint('You must save document before combine items');
                }else{
                    frappe.call({                                                        
                        method: "kensingtonbn.kensingtonbn.doctype.container_reconciliation.container_reconciliation.combine_similar_items",
                        args: {
                            doc_name : frm.doc.name
                        },
                        callback: function(r) {                                                               
                            frm.reload_doc();                                                                               
                            
                        }   
                                                        
                        });
                }                          
                                        
                               
                }).addClass("btn-primary").removeClass("btn-default"); 

        function get_batch(list){
            if(list.batch_no){
                return list.batch_no
            }else if (list.best_value_date){
                return  list.best_value_date + " <b style='color:red'>(New)</b>"
            }else{
                return "No Batch"
            }
        }
         

        }
        frm.fields_dict['purchase_invoices'].grid.get_field('purchase_invoice').get_query = function(doc, cdt, cdn) {
             return{	
                filters:[
                    ['docstatus', '=', 1]
                ]
            }
        }       
        

	},
   
	scan_barcode: function(frm) {	
          
		let transaction_controller= new erpnext.TransactionController({frm});
        transaction_controller.scan_barcode();
        frm.set_value('combine_similar_items' , 0)
	}
    
	
});    


// child table
frappe.ui.form.on('Container Reconciliation Item', {
	refresh(frm) {
	},
	item_code: function(frm, cdt, cdn){
			let transaction_controller= new erpnext.TransactionController({frm});
            transaction_controller.item_code(frm.doc, cdt, cdn);
            frm.set_value('combine_similar_items' , 0)
	},
    uom: function(frm, cdt, cdn){
        let transaction_controller= new erpnext.TransactionController({frm});
        transaction_controller.uom(frm.doc, cdt, cdn);        
},  

});