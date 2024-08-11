erpnext.ProductList = class {
	/* Options:
		- items: Items
		- settings: E Commerce Settings
		- products_section: Products Wrapper
		- preference: If preference is not list view, render but hide
	*/
	constructor(options) {
		Object.assign(this, options);

		if (this.preference !== "List View") {
			this.products_section.addClass("hidden");
		}

		this.products_section.empty();
		this.make();
	}

	make() {
		let me = this;
		let html = `<br><br>`;

		this.items.forEach(item => {
			let title = item.web_item_name || item.item_name || item.item_code || "";
			title =  title.length > 200 ? title.substr(0, 200) + "..." : title;

			html += `<div class='row list-row w-100 mb-4'>`;
			html += me.get_image_html(item, title, me.settings);
			html += me.get_row_body_html(item, title, me.settings);
			html += `</div>`;
		});

		let $product_wrapper = this.products_section;
		$product_wrapper.append(html);
		me.bind_request_quotation();///custom
	}

	get_image_html(item, title, settings) {
		let image = item.website_image || item.image;
		let wishlist_enabled = !item.has_variants && settings.enable_wishlist;
		let image_html = ``;

		if (image) {
			image_html += `
				<div class="col-2 border text-center rounded list-image">
					<a class="product-link product-list-link" href="/${ item.route}${item.batch_no ?'?batch='+item.batch_no:''}">
						<img itemprop="image" class="website-image h-100 w-100" alt="${ title }"
							src="${ image }">
					</a>
					${ wishlist_enabled ? this.get_wishlist_icon(item): '' }
				</div>
			`;
		} else {
			image_html += `
				<div class="col-2 border text-center rounded list-image">
					<a class="product-link product-list-link" href="/${ item.route}${item.batch_no ?'?batch='+item.batch_no:''}"
						style="text-decoration: none">
						<div class="card-img-top no-image-list">
							${ frappe.get_abbr(title) }
						</div>
					</a>
					${ wishlist_enabled ? this.get_wishlist_icon(item): '' }
				</div>
			`;
		}

		return image_html;
	}

	get_row_body_html(item, title, settings) {
		let body_html = `<div class='col-10 text-left'>`;
		body_html += this.get_title_html(item, title, settings);
		body_html += this.get_item_details(item, settings);
		body_html += `</div>`;
		return body_html;
	}

	get_title_html(item, title, settings) {
		let title_html = `<div class="d-flex flex-column flex-lg-row" style="display: flex; margin-left: -15px;">`;
		title_html += `
			<div class="col-12 col-lg-8" style="margin-right: -15px;">
				<a class="" href="/${ item.route}${item.batch_no ?'?batch='+item.batch_no:''}"
					style="color: var(--gray-800); font-weight: 500;">
					${ title }
				</a>
			</div>
		`;
		//custom update enable or disable add to cart
		if (settings.enabled) {
			title_html += `<div class="d-flex col-12 col-lg-4 cart-action-container ${item.in_cart ? 'd-flex' : ''}" >`;
			title_html += this.get_primary_button(item, settings);
			title_html += `</div>`;
		}
		title_html += `</div>`;

		return title_html;
	}
// ${ item.item_group } | Item Code : ${ item.item_code }

	get_item_details(item, settings) {
		let details = `
			<p class="product-code">` ;
		//custom update
		//details +=`EXP:${ item.best_value_date || 'NA'} |` ;
		details +=` Item Code : ${ item.item_code }
			</p>
			<div class="mt-2" style="color: var(--gray-600) !important; font-size: 13px;">
				${ item.short_description || '' }
			</div>
			<div class="product-price">
		`;
		if ( item.batch_price ){
			 details +=
			`
			${ item.symbol + ' ' +  format_currency(item.batch_price)  } 
		`
		} else if (  item.formatted_price){
			details +=
			`
			${  item.formatted_price}
		`
		}
		else {
			details +=
			`
			${ 'NA' }
		`
		};

		if (item.formatted_mrp) {
			details += `
				<small class="striked-price">
					<s>${ item.formatted_mrp ? item.formatted_mrp.replace(/ +/g, "") : "" }</s>
				</small>
				<small class="ml-1 product-info-green">
					${ item.discount } OFF
				</small>
			`;
		}

		details += this.get_stock_availability(item, settings);
		details += `</div>`;

		return details;
	}

	get_stock_availability(item, settings) {
		if (settings.show_stock_availability && !item.has_variants) {
			if (item.on_backorder) {
				return `
					<br>
					<span class="out-of-stock mt-2" style="color: var(--primary-color)">
						${ __("Available on backorder") }
					</span>
				`;
			} else if (!item.in_stock) {
				return `
					<br>
					<span class="out-of-stock mt-2">${ __("Out of stock") }</span>
				`;
			}
		}
		return ``;
	}

	get_wishlist_icon(item) {
		let icon_class = item.wished ? "wished" : "not-wished";

		return `
			<div class="like-action-list ${ item.wished ? "like-action-wished" : ''}"
				data-item-code="${ item.item_code }">
				<svg class="icon sm">
					<use class="${ icon_class } wish-icon" href="#icon-heart"></use>
				</svg>
			</div>
		`;
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
					<div class="btn btn-sm btn-explore-variants btn mb-0 mt-0">
						${ __('Explore') }
					</div>
				</a>
			`;
		} else if (settings.enabled && (settings.allow_items_not_in_stock || item.in_stock)) {
			return `
				<div id="${ item.name }" class="btn
					btn-sm btn-primary btn-add-to-cart-list mb-0
					${ item.in_cart ? 'hidden' : '' }"
					data-item-code="${ item.item_code }" data-batch="${ item.batch_no  || 'NA' }"
					style="margin-top: 0px !important; max-height: 30px; float: right;
						padding: 0.25rem 1rem; min-width: 135px;">
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
						<div class="input-group input-group-edited  number-spinner-item  mt-1 mb-4 ${ item.in_cart ? '' : 'hidden' }" data-item-code="${ item.item_code }" data-batch="${ item.batch_no  || 'NA' }">
							<span class="input-group-prepend d-sm-inline-block">
								<button class="btn cart-btn" data-dir="dwn" style="padding:5px 10px;width:30px;">
									-
								</button>
							</span>
							<input class="form-control form-control-edited text-center qty +" value="1"  style="padding:5px"
							data-item-code="${ item.item_code }" data-batch="${ item.batch_no  || 'NA' }"
							style="max-width: 70px;" readonly>
							<span class="input-group-append d-sm-inline-block">
								<button class="btn cart-btn" data-dir="up" style="padding:5px 10px;width:30px;">
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