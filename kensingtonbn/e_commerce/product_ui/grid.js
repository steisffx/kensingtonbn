erpnext.ProductGrid = class {
	/* Options:
		- items: Items
		- settings: E Commerce Settings
		- products_section: Products Wrapper
		- preference: If preference is not grid view, render but hide
	*/
	constructor(options) {
		Object.assign(this, options);

		if (this.preference !== "Grid View") {
			this.products_section.addClass("hidden");
		}

		this.products_section.empty();
		this.make();
	}

	make() {
		let me = this;
		let html = ``;

		this.items.forEach(item => {
			let title = item.web_item_name || item.item_name || item.item_code || "";
			title =  title.length > 90 ? title.substr(0, 90) + "..." : title;

			html += `<div class="col-sm-4 item-card"><div class="card text-left">`;
			html += me.get_image_html(item, title);
			html += me.get_card_body_html(item, title, me.settings);
			html += `</div></div>`;
		});

		let $product_wrapper = this.products_section;
		$product_wrapper.append(html);
		me.bind_request_quotation();///custom
	}

	get_image_html(item, title) {
		let image = item.website_image || item.image;

		if (image) {
			return `
				<div class="card-img-container">
					<a href="/${ item.route}${item.batch_no ?'?batch='+item.batch_no:''}" style="text-decoration: none;">
						<img class="card-img" src="${ image }" alt="${ title }">
					</a>
				</div>
			`;
		} else {
			return `
				<div class="card-img-container">
					<a href="/${ item.route}${item.batch_no ?'?batch='+item.batch_no:''}" style="text-decoration: none;">
						<div class="card-img-top no-image">
							${ frappe.get_abbr(title) }
						</div>
					</a>
				</div>
			`;
		}
	}

	get_card_body_html(item, title, settings) {
		let body_html = `
			<div class="card-body text-left card-body-flex" style="width:100%">
				<div style="margin-top: 1rem; display: flex;">
		`;
		body_html += this.get_title(item, title);

		// get floating elements
		if (!item.has_variants) {
			if (settings.enable_wishlist) {
				body_html += this.get_wishlist_icon(item);
			}
			// if (settings.enabled) {
			// 	body_html += this.get_cart_indicator(item);
			// }

		}

		body_html += `</div>`;
		// body_html += `<div class="product-category">${ item.item_group || product.best_value_date '' }</div>`;
		//body_html += `<div class="product-category">EXP:${  item.best_value_date || 'N/A' }</div>`;
		//custom update
		// if (item.formatted_price) {
		body_html += this.get_price_html(item);
		//}

		body_html += this.get_stock_availability(item, settings);
		body_html += this.get_primary_button(item, settings);
		body_html += `</div>`; // close div on line 49

		return body_html;
	}

	get_title(item, title) {
		let title_html = `
			<a href="/${ item.route}${item.batch_no ?'?batch='+item.batch_no:''}">
				<div class="product-title">
					${ title || '' }
				</div>
			</a>
		`;
		return title_html;
	}

	get_wishlist_icon(item) {
		let icon_class = item.wished ? "wished" : "not-wished";
		return `
			<div class="like-action ${ item.wished ? "like-action-wished" : ''}"
				data-item-code="${ item.item_code }">
				<svg class="icon sm">
					<use class="${ icon_class } wish-icon" href="#icon-heart"></use>
				</svg>
			</div>
		`;
	}

	get_cart_indicator(item) {
		return `
			<div class="cart-indicator ${item.in_cart ? '' : 'hidden'}" data-item-code="${ item.item_code }">
				1
			</div>
		`;
	}

	get_price_html(item){
			let price_html = `
				<div class="product-price">
			`;
			//custom update
			if ( item.batch_price ){
				price_html +=
			    `
			    ${ item.symbol + ' ' +  format_currency(item.batch_price)  } 
		  	    `
		   	} else if (  item.formatted_price){
				price_html +=
				`
				${  item.formatted_price}
				`
		    }
		    else {
				price_html +=
				`
				${ 'NA' }
		   		`
		   	};
			//end custom update
			if (item.formatted_mrp) {
				price_html += `
					<small class="striked-price">
						<s>${ item.formatted_mrp ? item.formatted_mrp.replace(/ +/g, "") : "" }</s>
					</small>
					<small class="ml-1 product-info-green">
						${ item.discount } OFF
					</small>
				`;
			}
			price_html += `</div>`;
			return price_html;
		}

	get_stock_availability(item, settings) {
		if (settings.show_stock_availability && !item.has_variants) {
			if (item.on_backorder) {
				return `
					<span class="out-of-stock mb-2 mt-1" style="color: var(--primary-color)">
						${ __("Available on backorder") }
					</span>
				`;
			} else if (!item.in_stock) {
				return `
					<span class="out-of-stock mb-2 mt-1">
						${ __("Out of stock") }
					</span>
				`;
			}
		}

		return ``;
	}
		//custom
	bind_request_quotation(){
		if (frappe.session.user ==="Guest") {
			return;
		}
		return frappe.call({
			type: "POST",
			method: "erpnext.e_commerce.shopping_cart.cart.get_cart_quotation",
			callback: function(r) {
				if(r.message) {
					var quotation_items = r.message.doc.items;
					$('input.qty').each(function(i){
						for (var index in quotation_items){
							if ((quotation_items[index].item_code == $(this).attr('data-item-code')) && (quotation_items[index].batch_no == $(this).attr('data-batch'))){
								this.value = quotation_items[index].qty;
								break;
							}
						}
					});

				}
			}
		});
	}//end
	get_primary_button(item, settings) {
		if (item.has_variants) {
			return `
				<a href="/${ item.route || '#' }">
					<div class="btn btn-sm btn-explore-variants w-100 mt-4">
						${ __('Explore') }
					</div>
				</a>
			`;
		} else if (settings.enabled && (settings.allow_items_not_in_stock || item.in_stock)) { //custom update enable or disable add to cart
			return `
				<div id="${ item.name }" class="btn
					btn-sm btn-primary btn-add-to-cart-list
					w-100 mt-2 ${ item.in_cart ? 'hidden' : '' }"
					data-item-code="${ item.item_code }" data-batch="${ item.batch_no || 'NA' }">
					<span class="mr-2">
						<svg class="icon icon-md">
							<use href="#icon-assets"></use>
						</svg>
					</span>
					${ settings.enable_checkout ? __('Add to Cart') :  __('Add to Quote') }
				</div>

				<!-- Custom -->	
				<td class="text-right" style="width: 25%;">
					<div class="d-flex">
						<div class="input-group input-group-edited number-spinner-item  mt-1 mb-4 ${ item.in_cart ? '' : 'hidden' }" data-item-code="${ item.item_code }" data-batch="${ item.batch_no  || 'NA' }">
							<span class="input-group-prepend d-sm-inline-block" >
								<button class="btn cart-btn" data-dir="dwn" style="padding:5px 10px;width:30px;" >
									-
								</button>
							</span>
							<input class="form-control form-control-edited text-center qty +" value="1"  style="padding:5px;"
							data-item-code="${ item.item_code }" data-batch="${ item.batch_no  || 'NA' }"
							style="max-width: 70px;" readonly>
							<span class="input-group-append d-sm-inline-block" >
								<button class="btn cart-btn" data-dir="up" style="padding:5px 7px; width:30px;">
									+
								</button>
							</span>
						</div>
					</div>
				</td>
				<!-- end -->
				
			`;
		} else {
			return ``;
		}
	}
};