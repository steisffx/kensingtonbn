// Copyright (c) 2016, ClefinCode and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Batch Details with Pricing Rule"] ={
	"filters": prepare_filters() ,
	
	onload: function(report) {
		var checked_items = [];
		var recomended_prices  = [];
		var confirmed_prices  = [];
		// setPricing()
		report.page.add_inner_button(__("Add Item Label"), function() {
			const itemsString = JSON.stringify(checked_items);

			fetch('/api/method/kensingtonbn.kensingtonbn.report.batch_details_with_pricing_rule.batch_details_with_pricing_rule.create_item_label', {
				method: 'POST',
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': frappe.csrf_token
				},
				body: JSON.stringify({ "items": itemsString })
			}).then(res => res.json()) // Parse the response to JSON
			.then(r => {
				if (r && r.message){
					var doc = frappe.model.sync(r.message);
					frappe.set_route("Form", doc[0].doctype, doc[0].name);
				}
			})
			.catch(error => console.error('Error:', error));
		
		});
		var style = document.createElement('style');
		
		style.type = 'text/css';
		style.innerHTML = `
			.confirmed_price {
			-moz-appearance: textfield;
			}
			.confirmed_price::-webkit-inner-spin-button,
			.confirmed_price::-webkit-outer-spin-button {
			-webkit-appearance: none;
			margin: 0;
			}
			.round {
				text-decoration: none;
				display: inline-block;
				padding: 8px 16px;
				border-radius: 50%;
				cursor: pointer;
			}
			.previous {
				background-color: #f1f1f1;
				color: black;
			}
			  
			.next {
				background-color: #f1f1f1;
				color: black;
			}
			  
		`;
		document.getElementsByTagName('head')[0].appendChild(style);

		$(document).on('click','input.check_item[type="checkbox"]',function(e) {		
			if ($(this).is(":checked")){
				checked_items.push({
					'item_code': $(this).attr('data-item'),
					'batch_no': $(this).attr('data-batch'),
					'qty': parseInt($('.qty[data-batch = "'+$(this).attr('data-batch')+'"]').attr('value')),
					'price_list_rate': parseFloat($('div.pricing_rule[data-batch = "'+$(this).attr('data-batch')+'"]').attr('value'))
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
		$(document).delegate('.recommended_price', 'change',  function(e) {	
			var batch = $(this).attr('data-batch');
			var item = $(this).attr('data-item');
			var recommended_price = $('.recommended_price[data-batch = "'+$(this).attr('data-batch')+'"]').val()
			
			if(this.recommended_price_timer){
				clearTimeout(this.recommended_price_timer);
				this.recommended_price_timer= null;
			}

			if(recomended_prices.length > 0){
				for(let i=0;i<recomended_prices.length;i++) {
					if(recomended_prices[i]!= undefined){
						if(recomended_prices[i].item_code === $(this).attr('data-item') && recomended_prices[i].batch_no === $(this).attr('data-batch')){
							delete recomended_prices[i]											
							break
						}
					}										
				}
				recomended_prices.push({
					'item_code': $(this).attr('data-item'),
					'batch_no': $(this).attr('data-batch'),
					'value': recommended_price,
					
				})
			}else{
				recomended_prices.push({
					'item_code': $(this).attr('data-item'),
					'batch_no': $(this).attr('data-batch'),
					'value': recommended_price,
					
				})
			}

			this.recommended_price_timer = setTimeout(() => {											
			frappe.db.set_value('Item', item, 'recommended_price', recommended_price)			
			}, 2000);
					
		
		});
		$(document).delegate('.confirmed_price','click', function(e) {
			$('.dt-row').find('.dt-cell').each(function() {
				this.style.removeProperty("background-color");
			});	

			let parentDiv = $(this).closest('.dt-row');
			
			$(parentDiv).css("background-color", "#B8860B")
			parentDiv.find('.dt-cell').each(function() {
				this.style.setProperty("background-color", "#B8860B", "important");
			});
			$(document).one('click', function(event) {
				// Remove background color if clicked outside
				if (!$(event.target).closest('.dt-row').length) {
					parentDiv.find('.dt-cell').each(function() {
						this.style.removeProperty("background-color");
					});
				}
			});
		
			// Prevent propagation to avoid immediate removal of background color
			e.stopPropagation();
		});		
		
		$(document).delegate('.confirmed_price','change', function(e) {	
			var batch = $(this).attr('data-batch');
			var item = $(this).attr('data-item');
			var confirmed_price = $('.confirmed_price[data-batch = "'+$(this).attr('data-batch')+'"]').val()
			
			if(this.confirmed_price_timer){
				clearTimeout(this.confirmed_price_timer);
				this.confirmed_price_timer = null;
			}

			if(confirmed_prices.length > 0){
				for(let i=0;i<confirmed_prices.length;i++) {
					if(confirmed_prices[i]!= undefined){
						if(confirmed_prices[i].item_code === $(this).attr('data-item') && confirmed_prices[i].batch_no === $(this).attr('data-batch')){
							delete confirmed_prices[i]											
							break
						}
					}										
				}
				confirmed_prices.push({
					'item_code': $(this).attr('data-item'),
					'batch_no': $(this).attr('data-batch'),
					'value': confirmed_price,
					
				})
			}else{
				confirmed_prices.push({
					'item_code': $(this).attr('data-item'),
					'batch_no': $(this).attr('data-batch'),
					'value': confirmed_price,
					
				})
			}
			
			let qty = parseInt($('.qty[data-batch = "'+batch+'"]').attr('value'))
			set_values(item, batch, confirmed_price, qty);
			change_price_rule(this);		
		});
		
		$(document).on('change', '.page-number', function(e) {
			let page = $('.page-number input').val();
			let number_of_rows = frappe.query_report.get_filter_value("number_of_rows")
			frappe.query_report.set_filter_value("start", (number_of_rows * page) - number_of_rows + 1);
			frappe.query_report.refresh();
		})
		$(document).on('click', '.previous', function(e) {
			let page = $('.page-number input').val() || 1;
			if (page > 1){
				let new_number = parseInt(page) - 1
				$('.page-number input').val(new_number).trigger("change");
			}

		})
		$(document).on('click', '.next', function(e) {
			let page = $('.page-number input').val() || 1;
			let new_number = parseInt(page) + 1
			$('.page-number input').val(new_number).trigger("change");
			

		})
		$(document).on('change', 'input[data-fieldname=from_date]', function(e){
			$('.page-number input').val(1)
			frappe.query_report.set_filter_value("start", 1);
			
		})
		$(document).on('change', 'input[data-fieldname=to_date]', function(e){
			$('.page-number input').val(1)
		})
		waitForElm('.dt-scrollable').then((elm) => {
			$(".layout-main-section").append(`
			<div style="text-align: center; margin: 15px;">
				<div class="previous round">&#8249;</div>
				<div class="page-number round"><input type='text' placeholder='1'></div>
				<div class="next round">&#8250;</div>
			</div>
			`)
			$('.page-number').val(1);
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
				for (var i=0; i<recomended_prices.length; i++){
					if(recomended_prices[i] != undefined){
						var item = recomended_prices[i]['item_code']
						var batch_no = recomended_prices[i]['batch_no']
						var value = recomended_prices[i]['value']
	
						selector = $('.recommended_price[data-item = "'+item+'"][data-batch = "'+batch_no+'"]')
						if (selector.length != 0) {						
							$('.recommended_price[data-item = "'+item+'"][data-batch = "'+batch_no+'"]').attr('value',value);
						}
					}					
				}
				for (var i=0; i<confirmed_prices.length; i++){
					if(confirmed_prices[i] != undefined){
						var item = confirmed_prices[i]['item_code']
						var batch_no = confirmed_prices[i]['batch_no']
						var value = confirmed_prices[i]['value']
	
						selector = $('.confirmed_price[data-item = "'+item+'"][data-batch = "'+batch_no+'"]')
						if (selector.length != 0) {						
							$('.confirmed_price[data-item = "'+item+'"][data-batch = "'+batch_no+'"]').attr('value',value);
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
	let parentDiv = $(btn_add).closest('.dt-row');
	let priceElement = parentDiv.find('.confirmed_price');
	
	if (priceElement){
		let confirmed_price = priceElement.val()
		if (parseFloat(confirmed_price) == 0){
			frappe.throw("You have to Enter a Price Greater Than Zero!!")
			return
		}
		frappe.call({
			method: "kensingtonbn.kensingtonbn.report.batch_details_with_pricing_rule.batch_details_with_pricing_rule.add_pricing_rule",
			args: {
				"item_code": item,
				"batch": batch,
				"rate": confirmed_price
			},
			freeze: true,
			freeze_message: "Creating a New Pricing Rule...",
			callback: function(r){
				if (r.message){
					const d = new frappe.ui.Dialog({
						'title': 'Updated',
						'fields': [
							{'fieldname': 'ht', 'fieldtype': 'HTML'}
						],
						primary_action_label: 'OK',
						primary_action(values) {
							d.hide();
						}
					});
					
					d.fields_dict.ht.$wrapper.html("A New Pricing Rule is Created. You can Access it from <a href='/app/pricing-rule/"+r.message +"'>here</a>");
					
					$(d.$wrapper).on('keydown', function(e) {
						if (e.which === 13) {
							d.hide();
						}
					});

					d.show();
					}
			}
		})
	}
}

function change_price_rule(btn_chg){
	var batch = $(btn_chg).attr('data-batch');
	var pricing_rule = $('div.pricing_rule[data-batch = "'+batch+'"]').attr('data-pricing-rule');	
	let parentDiv = $(btn_chg).closest('.dt-row');
	let priceElement = parentDiv.find('.confirmed_price');
	if (pricing_rule && priceElement){
		let confirmed_price = priceElement.val()
		if (parseFloat(confirmed_price) == 0){
			frappe.throw("You have to Enter a Price Greater Than Zero!!")
			return
		}
		frappe.call({
			method: "kensingtonbn.kensingtonbn.report.batch_details_with_pricing_rule.batch_details_with_pricing_rule.update_pricing_rule",
			args: {
				"rule_name": pricing_rule,
				"rate": confirmed_price
			},
			freeze: true,
			freeze_message: "Updating an Exist Pricing Rule...",
			callback: function(r){
				if (r.message){
					const d = new frappe.ui.Dialog({
						'title': 'Updated',
						'fields': [
							{'fieldname': 'ht', 'fieldtype': 'HTML'}
						],
						primary_action_label: 'OK',
						primary_action(values) {
							d.hide();
						}
					});
					
					d.fields_dict.ht.$wrapper.html("The Pricing Rule <b><a href='/app/pricing-rule/"+pricing_rule +"'>" + pricing_rule+"</a></b> is updated");
					
					$(d.$wrapper).on('keydown', function(e) {
						if (e.which === 13) {
							d.hide();
						}
					});

					d.show();
					
					
				}
			}
		})
	}
	else if (priceElement){
		new_price_rule(btn_chg)
	}
		
	//frappe.set_route('Form','Pricing Rule', {'name': pricing_rule});
}

function set_values(item, batch, confirmed_price, qty){
	if (parseFloat(confirmed_price) == 0){
		frappe.throw("You have to Enter a Price Greater Than Zero!!")
	}
	frappe.call({
		method: "kensingtonbn.kensingtonbn.report.batch_details_with_pricing_rule.batch_details_with_pricing_rule.set_values",
		args: {
			"item_code": item,
			"batch_no": batch,
			"price": confirmed_price,
			"qty": qty
		}
	})
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
		{
			"fieldname":"start",
			"label": __("Start"),
			"fieldtype": "Data",
			"default": 1,
			"hidden": 1
		},
		{
			"fieldname":"number_of_rows",
			"label": __("Number of Rows"),
			"fieldtype": "Data",
			"default": 12,
		},
		{
			"fieldname":"sort_by",
			"label": __("Sort By"),
			"fieldtype": "Select",
			"options": ['Item Code', 'Batch', 'Best Value Date', 'Last Update'],
			"default": 'Item Code'
		},
		{
			"fieldname":"sorting",
			"label": __("Asc / Des"),
			"fieldtype": "Select",
			"options": ["Asc", "Desc"],
			"default": "Asc",
		},
		{
			"fieldname":"balance_qty",
			"label": __("Balance Qty"),
			"fieldtype": "Check",
			"default": 0,
		},
	]
	frappe.db.get_list("Warehouse",{
		fields: ['name'],
		filters: {'is_group': 0, 'disabled': 0}
	}).then((res)=> {
		for (let i=0; i<res.length; i++){
			let wordToCheck = 'Kensington'
			let regex = new RegExp('\\b' + wordToCheck + '\\b', 'i');
			let cleanedString = res[i]['name']
			if (regex.test(res[i]['name'])) {
				cleanedString = res[i]['name'].replace(new RegExp('\\b' + wordToCheck + '\\b', 'gi'), "");
				cleanedString = cleanedString.replace(/\s+/g, ' ').trim();
			} 
			filters.push(
				{
					"fieldname":"warehouse " + res[i]['name'],
					"label": __(cleanedString),
					"fieldtype": "Check",
					"default": 0,
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

