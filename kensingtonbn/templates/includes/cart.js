// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
// js inside blog page

// start Custom Update

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const shipping = urlParams.get('shipping');

// first load or return to cart after Edit address
if(window.location.pathname == '/cart' && shipping == null ){
	frappe.call({
		type: "POST",
		method: "erpnext.e_commerce.shopping_cart.cart.remove_taxes_and_charges",
		callback:function(r){			
			$('#net-total').html(r.message.grand_total);
			$('#description').html("");
			$('#base_tax_amount').html("");	
			$('input[name="pickup"]').removeAttr("checked");
		}		
	});
	
	
}
// after click home delivery
else if(window.location.pathname == '/cart' && shipping == 'home_delivery'){
	$('input[name="pickup"][value="home_delivery"]').attr("checked", "checked");
}
// after click shop_pickup or customer doesn't have address
else if(window.location.pathname == '/cart' && shipping == 'shop_pickup'){
	frappe.call({
		type: "POST",
		method: "erpnext.e_commerce.shopping_cart.cart.remove_taxes_and_charges"	
		
	});
	$('input[name="pickup"][value="shop_pickup"]').attr("checked", "checked");
}

// End Custom Update

// shopping cart
frappe.provide("erpnext.e_commerce.shopping_cart");
var shopping_cart = erpnext.e_commerce.shopping_cart;

$.extend(shopping_cart, {
	show_error: function(title, text) {
		$("#cart-container").html('<div class="msg-box"><h4>' +
			title + '</h4><p class="text-muted">' + text + '</p></div>');
	},

	bind_events: function() {
		shopping_cart.bind_address_picker_dialog();
		shopping_cart.bind_place_order();
		shopping_cart.bind_request_quotation();
		shopping_cart.bind_change_qty();
		shopping_cart.bind_remove_cart_item();
		shopping_cart.bind_change_notes();
		shopping_cart.bind_coupon_code();
		// custom update for shop pickup
		shopping_cart.apply_tax_rule();
		shopping_cart.remove_tax_rule();
	},

	bind_address_picker_dialog: function() {
		const d = this.get_update_address_dialog();
		this.parent.find('.btn-change-address').on('click', (e) => {
			const type = $(e.currentTarget).parents('.address-container').attr('data-address-type');
			$(d.get_field('address_picker').wrapper).html(
				this.get_address_template(type)
			);
			d.show();
		});
	},

	get_update_address_dialog() {
		let d = new frappe.ui.Dialog({
			title: "Select Address",
			fields: [{
				'fieldtype': 'HTML',
				'fieldname': 'address_picker',
			}],
			primary_action_label: __('Set Address'),
			primary_action: () => {
				const $card = d.$wrapper.find('.address-card.active');
				const address_type = $card.closest('[data-address-type]').attr('data-address-type');
				const address_name = $card.closest('[data-address-name]').attr('data-address-name');
				// start custom update
				if($('input[name="pickup"][value="shop_pickup"]').is(':checked')){
					shop_pickup = 'checked'
				}else{
					shop_pickup = 'notChecked'
				}				
				// end custom update						
				frappe.call({
					type: "POST",
					method: "erpnext.e_commerce.shopping_cart.cart.update_cart_address",
					freeze: true,
					args: {
						address_type,
						address_name,
						shop_pickup
					},
					callback: function(r) {
						d.hide();
						if (!r.exc) {
							$(".cart-tax-items").html(r.message.total);
							shopping_cart.parent.find(
								`.address-container[data-address-type="${address_type}"]`
							).html(r.message.address);
						}
						window.location.reload();
					}
				});
			}
		});

		return d;
	},

	get_address_template(type) {
		return {
			shipping: `<div class="mb-3" data-section="shipping-address">
				<div class="row no-gutters" data-fieldname="shipping_address_name">
					{% for address in shipping_addresses %}
						<div class="mr-3 mb-3 w-100" data-address-name="{{address.name}}"  data-address-type="shipping"
							{% if doc.shipping_address_name == address.name %} data-active {% endif %}>
							{% include "templates/includes/cart/address_picker_card.html" %}
						</div>
					{% endfor %}
				</div>
			</div>`,
			billing: `<div class="mb-3" data-section="billing-address">
				<div class="row no-gutters" data-fieldname="customer_address">
					{% for address in billing_addresses %}
						<div class="mr-3 mb-3 w-100" data-address-name="{{address.name}}" data-address-type="billing"
							{% if doc.shipping_address_name == address.name %} data-active {% endif %}>
							{% include "templates/includes/cart/address_picker_card.html" %}
						</div>
					{% endfor %}
				</div>
			</div>`,
		}[type];
	},

	bind_place_order: function() {
		$(".btn-place-order").on("click", function() {			
			if(frappe.get_cookie("recomended")!='true'){
				document.cookie = "recomended=true"
				suggested();
			}else if(
				$('input[name="pickup"][value="home_delivery"]').prop('checked') == false &&
				$('input[name="pickup"][value="shop_pickup"]').prop('checked') == false 
			){
				frappe.msgprint({
					message:"<style>.modal-dialog {max-width:30%;} .msgprint-dialog{margin-top: 40vh;}.modal-content{box-shadow: 0px 0px 20px 10px #c7c7c7;background-color: #f3f8fd;}.btn-modal-close{visibility: hidden;}</style><div>Please select free shop pick up or Home delivery<div>",
					title:'Message',
					primary_action:{
						'label': 'OK',
						action() {
							this.hide();
						}
					}
				});
				return;
			}else{
				shopping_cart.place_order(this);
				document.cookie = "recomended="
			}
			
		});
	},

	bind_request_quotation: function() {
		$('.btn-request-for-quotation').on('click', function() {
			shopping_cart.request_quotation(this);
		});
	},

	bind_change_qty: function() {
		// bind update button
		$(".cart-items").on("change", ".cart-qty", function() {
			var item_code = $(this).attr("data-item-code");
			var batch_no = $(this).attr("data-batch"); // custom update
			var newVal = $(this).val();
			shopping_cart.shopping_cart_update({item_code, qty: newVal ,batch_no });
		});

		$(".cart-items").on('click', '.number-spinner button', function () {
			var btn = $(this),
				input = btn.closest('.number-spinner').find('input'),
				oldValue = input.val().trim(),
				newVal = 0;

			if (btn.attr('data-dir') == 'up') {
				newVal = parseInt(oldValue) + 1;
			} else {
				if (oldValue > 1) {
					newVal = parseInt(oldValue) - 1;
				}
			}
			input.val(newVal);

			let notes = input.closest("td").siblings().find(".notes").text().trim();
			var item_code = input.attr("data-item-code");
			var batch_no = input.attr("data-batch"); //custom update
			shopping_cart.shopping_cart_update({
				item_code,
				qty: newVal,
				batch_no, //custom update
				additional_notes: notes
			});
		});
	},

	bind_change_notes: function() {
		$('.cart-items').on('change', 'textarea', function() {
			const $textarea = $(this);
			const item_code = $textarea.attr('data-item-code');
			const qty = $textarea.closest('tr').find('.cart-qty').val();
			const notes = $textarea.val();
			shopping_cart.shopping_cart_update({
				item_code,
				qty,
				additional_notes: notes
			});
		});
	},

	bind_remove_cart_item: function() {
		$(".cart-items").on("click", ".remove-cart-item", (e) => {
			const $remove_cart_item_btn = $(e.currentTarget);
			var item_code = $remove_cart_item_btn.data("item-code");
			var batch_no = $remove_cart_item_btn.data("batch"); //custom update

			shopping_cart.shopping_cart_update({
				item_code: item_code,
				qty: 0,
				batch_no:batch_no //custom update
			});
		});
	},

	render_tax_row: function($cart_taxes, doc, shipping_rules) {
		var shipping_selector;
		if(shipping_rules) {
			shipping_selector = '<select class="form-control">' + $.map(shipping_rules, function(rule) {
				return '<option value="' + rule[0] + '">' + rule[1] + '</option>' }).join("\n") +
			'</select>';
		}

		var $tax_row = $(repl('<div class="row">\
			<div class="col-md-9 col-sm-9">\
				<div class="row">\
					<div class="col-md-9 col-md-offset-3">' +
					(shipping_selector || '<p>%(description)s</p>') +
					'</div>\
				</div>\
			</div>\
			<div class="col-md-3 col-sm-3 text-right">\
				<p' + (shipping_selector ? ' style="margin-top: 5px;"' : "") + '>%(formatted_tax_amount)s</p>\
			</div>\
		</div>', doc)).appendTo($cart_taxes);

		if(shipping_selector) {
			$tax_row.find('select option').each(function(i, opt) {
				if($(opt).html() == doc.description) {
					$(opt).attr("selected", "selected");
				}
			});
			$tax_row.find('select').on("change", function() {
				shopping_cart.apply_shipping_rule($(this).val(), this);
			});
		}
	},

	apply_shipping_rule: function(rule, btn) {
		return frappe.call({
			btn: btn,
			type: "POST",
			method: "erpnext.e_commerce.shopping_cart.cart.apply_shipping_rule",
			args: { shipping_rule: rule },
			callback: function(r) {
				if(!r.exc) {
					shopping_cart.render(r.message);
				}
			}
		});
	},

	place_order: function(btn) {
		shopping_cart.freeze();

		return frappe.call({
			type: "POST",
			method: "erpnext.e_commerce.shopping_cart.cart.place_order",
			btn: btn,
			callback: function(r) {
				if(r.exc) {
					shopping_cart.unfreeze();
					var msg = "";
					if(r._server_messages) {
						msg = JSON.parse(r._server_messages || []).join("<br>");
					}

					$("#cart-error")
						.empty()
						.html(msg || frappe._("Something went wrong!"))
						.toggle(true);
				} else {
					$(btn).hide();
					window.location.href = '/orders/' + encodeURIComponent(r.message);
				}
			}
		});
	},

	request_quotation: function(btn) {
		shopping_cart.freeze();

		return frappe.call({
			type: "POST",
			method: "erpnext.e_commerce.shopping_cart.cart.request_for_quotation",
			btn: btn,
			callback: function(r) {
				if(r.exc) {
					shopping_cart.unfreeze();
					var msg = "";
					if(r._server_messages) {
						msg = JSON.parse(r._server_messages || []).join("<br>");
					}

					$("#cart-error")
						.empty()
						.html(msg || frappe._("Something went wrong!"))
						.toggle(true);
				} else {
					$(btn).hide();
					window.location.href = '/quotations/' + encodeURIComponent(r.message);
				}
			}
		});
	},

	bind_coupon_code: function() {
		$(".bt-coupon").on("click", function() {
			shopping_cart.apply_coupon_code(this);
		});
	},

	apply_coupon_code: function(btn) {
		return frappe.call({
			type: "POST",
			method: "erpnext.e_commerce.shopping_cart.cart.apply_coupon_code",
			btn: btn,
			args : {
				applied_code : $('.txtcoupon').val(),
				applied_referral_sales_partner: $('.txtreferral_sales_partner').val()
			},
			callback: function(r) {
				if (r && r.message){
					location.reload();
				}
			}
		});
	},

	apply_tax_rule:function(){
		$('input[name="pickup"][value="home_delivery"]').on('click' , function(){	
			shopping_cart.freeze();
			$('.btn-place-order').attr("disabled", "disabled");				
					frappe.call({
						method: "erpnext.e_commerce.shopping_cart.cart.restore_taxes_and_charges",
						callback: function(r) {	
							if(r.message == 0){	
								let d = new frappe.ui.Dialog({
									title: 'Message',
									fields:[{fieldtype: "HTML",options:'<style>[type=button][class=close]{display:none}</style><p>Please Set Shipping Address or Billing Address</p>'}],						
									primary_action_label: 'Ok',
									primary_action() {										
										window.location.href = "/cart";
										d.hide();
									}
								});
								d.show();
								$('input[name="pickup"]').removeAttr("checked");
								// $('.btn-place-order').removeAttr('disabled');	
								shopping_cart.unfreeze();
													
							}else{																			
								window.location.href = "/cart?shipping=home_delivery";
								// $('.btn-place-order').removeAttr('disabled');								
								$('input[name="pickup"][value="home_delivery"]').attr("checked", "checked");
								shopping_cart.unfreeze();
								}										
														
							}										
					});	
				
			});
		
	},

	remove_tax_rule:function(){
		$('input[name="pickup"][value="shop_pickup"]').on('click' , function(){	
			$('.btn-place-order').attr("disabled", "disabled");	
			shopping_cart.freeze();	
				frappe.call({
					method: "erpnext.e_commerce.shopping_cart.cart.remove_taxes_and_charges",
					callback: function() {						
							window.location.href = "/cart?shipping=shop_pickup";
							// $('.btn-place-order').removeAttr('disabled');						
							$('input[name="pickup"][value="shop_pickup"]').attr("checked", "checked");
							shopping_cart.unfreeze();				
							
						}								
				});	
		});
	}

});

frappe.ready(function() {
	// $(".cart-icon").hide();
	$(".shopping-cart-icon").hide(); ///custom
	shopping_cart.parent = $(".cart-container");
	shopping_cart.bind_events();
	

});

function show_terms() {
	var html = $(".cart-terms").html();
	frappe.msgprint(html);
}  
function continue_as_place_order(){
	if(
		$('input[name="pickup"][value="home_delivery"]').prop('checked') == false &&
		$('input[name="pickup"][value="shop_pickup"]').prop('checked') == false 
	){
		frappe.msgprint({
			message:"<style>.modal-dialog {max-width:30%;} .msgprint-dialog{margin-top: 40vh;}.modal-content{box-shadow: 0px 0px 20px 10px #c7c7c7;background-color: #f3f8fd;}.btn-modal-close{visibility: hidden;}</style><div>Please select free shop pick up or Home delivery<div>",
			title:'Message',
			primary_action:{
				'label': 'OK',
				action() {
					this.hide();
				}
			}
		});
		return;
	}else{
		shopping_cart.place_order(this);
		document.cookie = "recomended="
	}
}
function suggested(){	
	let me = this;	
	let html = `</head><style>.modal-dialog {max-width:1000px;}</style>`	
	html += `<div id="products-grid-area" class="row products-list mt-minus-1 ">`;	
    frappe.call({
        method: 'erpnext.e_commerce.shopping_cart.cart.show_suggested',
        callback: function(r) {            
			itemList = r.message;			
			for(item in itemList){	
				settings = 	itemList['settings'];						
				for(let i = 0 ; i<itemList[item].length ; i++){
					product_info = itemList[item][i].product_info															
					let title = itemList[item][i].item_name || itemList[item][i].item_code || "";
					title =  title.length > 90 ? title.substr(0, 90) + "..." : title;
					html += `<div class="col-sm-4 item-card-group-section my-2"><div class="card text-left">`;
					html += me.get_image_html(itemList[item][i], title);
					html += me.get_card_body_html(itemList[item][i], title, settings);
					html += `</div></div>`;
				}
			}
			html +=`</div>`;					
			$('.modal-body').html(html);
			$('#recomendedItems').modal({
				backdrop: 'static',
				keyboard: false
			  });
			$('#recomendedItems #continue').on('click' ,function(){				
				continue_as_place_order();
			});	
			
			
		}
			
        
    });
}


function get_image_html(item, title) {
	let image = item.website_image || item.image;

	if (image) {
		return `
			<div class="card-img-container">
				<a href="/${ item.route}${item.batch_id ?'?batch='+item.batch_id:''}" style="text-decoration: none;">
					<img class="card-img" src="${ image }" alt="${ title }" >
				</a>
			</div>
		`;
	} else {
		return `
			<div class="card-img-container">
				<a href="/${ item.route}${item.batch_id ?'?batch='+item.batch_id:''}" style="text-decoration: none;">
					<div class="card-img-top no-image">
						${ frappe.get_abbr(title) }
					</div>
				</a>
			</div>
		`;
	}
}
function get_card_body_html(item, title, settings) {
	let body_html = `
		<div class="card-body  card-body-flex" style="width:100%">
			<div style="margin-top: 1rem; text-align:center!important;">
	`;
	body_html += this.get_title(item, title);
	body_html += `</div>`;
	body_html += this.get_price_html(item);
	body_html += this.get_stock_availability(item, settings);
	body_html += this.get_primary_button(item, settings);
	body_html += `</div>`;

	return body_html;
	}

function get_title(item, title) {
	let title_html = `
		<a href="/${ item.route}${item.batch_id ?'?batch='+item.batch_id:''}" style="text-decoration:none;color:black;">
			<div class="product-title" >
				${ title || '' }
			</div>
		</a>
	`;
	return title_html;
}
function get_price_html(item) {
	// let price_html = `<div class="product-price" style="text-align:center;">`;
    // price_html +=`<b>${item.formatted_price}</b>`;
	// price_html += `</div>`;
	// return price_html;

	let price_html = `<div class="product-price" style="text-align:center;">`
			if(product_info.price){
				if(product_info.price.formatted_price){
					price_html +=
					`
					${  product_info.price.formatted_price}
				`
				}else {
					price_html +=
					`
					${  'NA' }
				`
				}
				if(product_info.price.formatted_mrp){
					price_html += `
					<small class="striked-price">
						<s>${ product_info.price.formatted_mrp ? product_info.price.formatted_mrp.replace(/ +/g, "") : "" }</s>
					</small>`
				}
				if(product_info.price.formatted_discount_percent){
					price_html +=
					`<small class="ml-1 product-info-green">					
					${ product_info.price.formatted_discount_percent } OFF
					</small>`;
				}if(product_info.price.formatted_discount_rate){
					price_html +=
					`<small class="ml-1 product-info-green">					
					${ product_info.price.formatted_discount_rate } OFF
					</small>`;
				}
					
				}
			
		
		price_html += `</div>`;
		return price_html;
	}

	function get_stock_availability(item, settings){
		if (settings.show_stock_availability) {
			if (!item.product_info.in_stock) {
				return `
					<div style="text-align:center"><span class="out-of-stock mb-2 mt-1">
						${ __("Out of stock") }
					</span></div>
				`;
			}
		}

		return ``;
	}



function get_primary_button(item , settings) {
	if (settings.enabled && (settings.allow_items_not_in_stock || item.in_stock)) {
		return `
			<button
				data-item-code="${ item.item_code }" data-batch="${ item.batch_id || 'NA' }"
				onclick ="addToCart(event)"
				class="btn btn-primary btn-add-to-cart m-3 w-100">
				<span class="mr-2">
					<svg class="icon icon-md">
						<use href="#icon-assets"></use>
					</svg>
				</span>
				${ settings.enable_checkout ? __('Add to Cart') :  __('Add to Quote') }
			</button>
			<!-- Custom -->	
			<td class="text-right" style="width: 25%;">
				<div class="d-flex">
					<div class="input-group input-group-edited number-spinner-re  mt-1 mb-4 ${ item.in_cart ? '' : 'hidden' }" 
					data-item-code="${ item.item_code }" data-batch="${ item.batch_id  || 'NA' }">
						<span class="input-group-prepend d-sm-inline-block" >
							<button class="btn cart-btn w-100" style="padding:5px 10px;min-width:30px;" data-dir="dwn" onclick = "bind_recomended_spiner_action(event)" >
								-
							</button>
						</span>
						<input class="form-control form-control-edited text-center qty +" value="1"  style="padding:5px 10px;"
						data-item-code="${ item.item_code }" data-batch="${ item.batch_id  || 'NA' }"
						style="max-width: 70px;" readonly>
						<span class="input-group-append d-sm-inline-block" >
							<button class="btn cart-btn w-100" style="padding:5px 10px;min-width:30px;" data-dir="up" onclick = "bind_recomended_spiner_action(event)">
								+
							</button>
						</span>
					</div>
				</div>
			</td>
			<!-- end -->
						
		`;
	}else{
		return ``;
	}
}
function addToCart(event){	
	const $btn = $(event.currentTarget);	
	const item_code = $btn.data('item-code');
	const batch_no = $btn.data('batch');	
	shopping_cart.shopping_cart_update({
		item_code,
		qty: 1,
		batch_no,		
	});
	// $btn.removeAttr('onclick');	
	// $btn.removeAttr('class');
	// $btn.attr('class' , 'btn btn-secondary  m-3 w-100 disabled');
	// $btn.html('Added')
	// custom update
	$btn.addClass('hidden');
	$btn.closest('.cart-action-container').addClass('d-flex');
	$btn.parent().find('.number-spinner-re').removeClass('hidden');

}
////custom
function bind_recomended_spiner_action(event){
	var btn = $(event.currentTarget),
	input = btn.closest('.number-spinner-re').find('input'),
	oldValue = input.val().trim(),
	newVal = 0;	
	if (btn.attr('data-dir') == 'up') {
		newVal = parseInt(oldValue) + 1;
	} else {
		
		if (oldValue > 1) {
			newVal = parseInt(oldValue) - 1;
		}
	}
	input.val(newVal);
	let notes = input.closest("td").siblings().find(".notes").text().trim();
	var item_code = input.attr("data-item-code");
	var batch_no = input.attr('data-batch');

	erpnext.e_commerce.shopping_cart.shopping_cart_update({
		item_code,
		qty: newVal,
		batch_no 
	});
	if (newVal == 0) {
		input.val(1);
		input.prop('disabled', false);
		if(window.location.pathname == '/cart'){
			$('.input-group[data-batch = "'+batch_no+'"]').addClass('hidden');
			$('.btn-add-to-cart[data-batch = "'+batch_no+'"]').removeClass('hidden');	
			$('.btn-add-to-cart[data-batch = "'+batch_no+'"]').prop('disabled', false);
		}				
	}
}

//end			





	
	


