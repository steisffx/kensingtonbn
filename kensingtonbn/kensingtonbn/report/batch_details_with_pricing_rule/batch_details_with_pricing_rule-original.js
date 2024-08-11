// Copyright (c) 2016, ClefinCode and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Batch Details with Pricing Rule"] ={
	"filters": prepare_filters() ,
	
	onload: function(report) {
		var checked_items = [];
		report.page.add_inner_button(__("Add Item Label"), function() {
			frappe.dom.freeze("Loading..");
			// $('input[type="checkbox"].check_item:checked').each((i, input)=> {
			// 	items.push($(input).attr('data-item'));
			// 	batches.push($(input).attr('data-batch'));
			// 	frappe.db.get_value("Item", {'name': $(input).attr('data-item')}, 'item_name',(r) => {
			// 		items_names.push(r.item_name);
			// 	})
			// })
			if (checked_items.length != 0) {
				doc = frappe.new_doc('Item Label', {'selling_price_list' : 'Standard Selling'}, doc => {
					for (let i = 0; i<checked_items.length; i++){
						let row = frappe.model.add_child(doc, "items");
						row.item_code = checked_items[i]['item_code'];
						row.batch_no = checked_items[i]['batch_no'];
						row.qty= checked_items[i]['qty'];
						row.price_list_rate = checked_items[i]['rate'];
						frappe.db.get_value("Item", {'name': checked_items[i]['item_code']}, 'item_name', (r) => {
							row.item_name = r.item_name;
						})
						
					}
					//doc.insert();
				});
			}
			else {
				frappe.throw("You didn't select any item!")
			}
			frappe.dom.unfreeze();
		});

		$(document).on('click','input.check_item[type="checkbox"]',function(e) {		
			if ($(this).is(":checked")){
				checked_items.push({
					'item_code': $(this).attr('data-item'),
					'batch_no': $(this).attr('data-batch'),
					'qty': parseInt($('.qty[data-batch = "'+$(this).attr('data-batch')+'"]').attr('value')),
					'rate': parseFloat($('div.pricing_rule[data-batch = "'+$(this).attr('data-batch')+'"]').attr('value'))
				})
			}
			else {
				for (var i=0; i< checked_items.length; i++){
					if ((checked_items[i]['item_code'] == $(this).attr('data-item')) && 
					(checked_items[i]['batch_no'] == $(this).attr('data-batch'))){
						checked_items.splice(i,1);
						break;
					}
				}
			}
		});
		waitForElm('.dt-scrollable').then((elm) => {
			$(elm).scroll(function(){
				for (var i=0; i<checked_items.length; i++){
					var item = checked_items[i]['item_code']
					var batch_no = checked_items[i]['batch_no']
					selector = $('input.check_item[data-item = "'+item+'"][data-batch = "'+batch_no+'"]')
					if (selector.length != 0) {
						if ($('input.check_item[data-item = "'+item+'"][data-batch = "'+batch_no+'"]').is(":checked") == 0) {
							$('input.check_item[data-item = "'+item+'"][data-batch = "'+batch_no+'"]').attr('checked','checked');
						}
					}
				}
			})
		});
	}
};

function new_price_rule(btn_add){
	var batch = $(btn_add).attr('data-batch');
	var item = $(btn_add).attr('data-item');
	//frappe.set_route('Form','Pricing Rule');
	doc = frappe.new_doc('Pricing Rule', {'apply_on' : 'Item Code'}, doc => {
		let row = frappe.model.add_child(doc, "items");
		row.item_code = item;
		row.batch_no = batch;
	});
    doc.insert();
}

function change_price_rule(btn_chg){
	var batch = $(btn_chg).attr('data-batch');
	var pricing_rule = $('div.pricing_rule[data-batch = "'+batch+'"]').attr('data-pricing-rule');	
	if (pricing_rule){
		frappe.set_route('Form','Pricing Rule', {'name': pricing_rule});
	}
	else{
		frappe.confirm(__("There is no pricing rule for this batch. Do you want to add a new one?"), function(){
			var item = $(btn_chg).attr('data-item');
			doc = frappe.new_doc('Pricing Rule', {'apply_on' : 'Item Code'}, doc => {
				let row = frappe.model.add_child(doc, "items");
				row.item_code = item;
				row.batch_no = batch;
			});
			doc.insert();
		})
	}
		
	//frappe.set_route('Form','Pricing Rule', {'name': pricing_rule});
}

function prepare_filters(){
	filters = [
		{
			"fieldname":"from_date",
			"label": __("From Best Value Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"to_date",
			"label": __("To Best Value Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			
		},
		{
			"fieldname":"batch",
			"label": __("Batch"),
			"fieldtype": "Link",
			"options": "Batch",
		},
		{
			"fieldname":"barcode",
			"label": __("Barcode"),
			"fieldtype": "Data",
		},
		{
			"fieldname":"disabled",
			"label": __("Show disabled Batches"),
			"fieldtype": "Check",
			"default": 0,
		},
	]
	frappe.db.get_list("Warehouse",{
		fields: ['name'],
		filters: {'is_group': 0, 'disabled': 0}
	}).then((res)=> {
		for (let i=0; i<res.length; i++){
			filters.push(
				{
					"fieldname":"warehouse " + res[i]['name'],
					"label": __(res[i]['name']),
					"fieldtype": "Check",
					"default": 1,
				},
			)
		}			
	})
	return filters	

}

function waitForElm(selector) {
    return new Promise(resolve => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }

        const observer = new MutationObserver(mutations => {
            if (document.querySelector(selector)) {
                resolve(document.querySelector(selector));
                observer.disconnect();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}

