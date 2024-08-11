// Copyright (c) 2022, ClefinCode and contributors
// For license information, please see license.txt

let user = frappe.session.user;

frappe.ui.form.on('Employee Activity', {
	refresh: function(frm) {
		if(user == frm.doc.assigned_to && frm.doc.__islocal != 1 && user != frm.doc.assigned_by){
                        cur_frm.toggle_enable("assigned_by", 0);
			cur_frm.toggle_enable("subject", 0);
			cur_frm.toggle_enable("assigned_to", 0);
                }

		if(frm.doc.__islocal == 1){
			cur_frm.set_value("assigned_by", user);
		}

		$.each(cur_frm.doc.employee_activity_item, function (index, item) {
			if (item.accept == 1){
				cur_frm.fields_dict['employee_activity_item'].grid.grid_rows_by_docname[item.name].activate();
				cur_frm.fields_dict["employee_activity_item"].grid.grid_rows_by_docname[item.name].set_field_property('accept','read_only',1)
			}
			if(item.accept == 1 && item.start == 0){
				cur_frm.fields_dict['employee_activity_item'].grid.grid_rows_by_docname[item.name].activate();
				cur_frm.fields_dict["employee_activity_item"].grid.grid_rows_by_docname[item.name].set_field_property('start','read_only',0)
			}else if(item.accept == 1 && item.start == 1){
				cur_frm.fields_dict["employee_activity_item"].grid.grid_rows_by_docname[item.name].set_field_property('start','read_only',1);
				cur_frm.fields_dict['employee_activity_item'].grid.grid_rows_by_docname[item.name].activate();
			}


			if(item.start == 1 && item.end == 0){
				cur_frm.fields_dict['employee_activity_item'].grid.grid_rows_by_docname[item.name].activate();
				cur_frm.fields_dict["employee_activity_item"].grid.grid_rows_by_docname[item.name].set_field_property('end','read_only',0)
			}else if(item.start == 1 && item.end == 1){
				cur_frm.fields_dict["employee_activity_item"].grid.grid_rows_by_docname[item.name].set_field_property('end','read_only',1);
				cur_frm.fields_dict['employee_activity_item'].grid.grid_rows_by_docname[item.name].activate();
			}


			if(item.end == 1 && item.reopen == 0){
				cur_frm.fields_dict['employee_activity_item'].grid.grid_rows_by_docname[item.name].activate();
				cur_frm.fields_dict["employee_activity_item"].grid.grid_rows_by_docname[item.name].set_field_property('reopen','read_only',0)
			}
			if(item.reopen == 1 && item.end == 0){
				cur_frm.fields_dict['employee_activity_item'].grid.grid_rows_by_docname[item.name].activate();
				cur_frm.fields_dict["employee_activity_item"].grid.grid_rows_by_docname[item.name].set_field_property('end','read_only',0)
			}
		})
	},
	// validate: function(frm){
	// 	$.each(frm.doc.employee_activity_item, function (index, item) {
	// 		check_buttons(item);
	// 	})
	// },
	assigned_to: function(frm){
		$.each(cur_frm.doc.employee_activity_item, function (index, item) {
			frappe.model.set_value(item.doctype, item.name, "assigned_user", frm.doc.assigned_to);
		})
	},
	date: function(frm){
		$.each(cur_frm.doc.employee_activity_item, function (index, item) {
			frappe.model.set_value(item.doctype, item.name, "assigned_date", frm.doc.date);
		})
	}
});

frappe.ui.form.on("Employee Activity Item", {
	end: function(frm, cdt, cdn){
		let child = frappe.get_doc(cdt, cdn)
		if(child.end == 1){
			frappe.model.set_value(child.doctype, child.name, "reopen", 0);
		}
		end(child)
	},
	start: function(frm, cdt, cdn){
		let child = frappe.get_doc(cdt, cdn)
		start(child)
	},
	reopen: function(frm, cdt, cdn){
		let child = frappe.get_doc(cdt, cdn)
		child.end = 0
		reactivate(child)
	},
	before_employee_activity_item_remove: function(frm, cdt, cdn){
		let child = frappe.get_doc(cdt, cdn);
		if(child.__islocal != 1 && user != frm.doc.assigned_by){
			frappe.throw("You cannot delete this row");
		}
	},
	accept: function(frm, cdt, cdn){
		let child = frappe.get_doc(cdt, cdn)
		if(user != frm.doc.assigned_to){
			frappe.model.set_value(child.doctype, child.name, "accept", 0);
		}else{
			accept_button(child);
		}
	},
	employee_activity_item_add: function(frm, cdt, cdn){
		let child = frappe.get_doc(cdt, cdn);
		child.assigned_user = frm.doc.assigned_to;
		child.assigned_date = frm.doc.date;
		if(child.__islocal == 1 && user != frm.doc.assigned_by){
			cur_frm.get_field("employee_activity_item").grid.grid_rows[child.idx-1].remove();
			cur_frm.get_field("employee_activity_item").grid.refresh();
			frappe.throw("You cannot add row");
		}
	},

	form_render: function(frm, cdt, cdn){
		let child = frappe.get_doc(cdt, cdn);
		activity_time(child);
	}
});

function check_buttons(item){
	if(item.accept == 1){
		if(!item.activity_accept_date){
			accept_button(item);
		}
	}
	if(item.accept == 1 && item.start == 1){
		start(item);
	}

	if(item.accept == 1 && item.start == 1 && item.end == 1 && item.reopen == 0){
		end(item);
	}
	if(item.accept == 1 && item.start == 1 && item.end == 1 && item.reopen == 1){
		reactivate(item);
	}
}

/*----------accept---------*/
function accept_button(item){
	if(user == cur_frm.doc.assigned_to){
		frappe.model.set_value(item.doctype, item.name, 'accept', 1)
		frappe.model.set_value(item.doctype, item.name, 'activity_accept_date', frappe.datetime.now_datetime())
	}
}

/*------start-----*/
function start(item){
	if(user == cur_frm.doc.assigned_to){
		frappe.model.set_value(item.doctype, item.name, 'start', 1)
		frappe.model.set_value(item.doctype, item.name, 'activity_start_date', frappe.datetime.now_datetime())
	}
}

/*----end----*/
function end(item){
	if(user == cur_frm.doc.assigned_to){
		frappe.model.set_value(item.doctype, item.name, 'end', 1)
		frappe.model.set_value(item.doctype, item.name, 'reopen', 0)
		frappe.model.set_value(item.doctype, item.name, 'activity_end_date', frappe.datetime.now_datetime())
	}
}

/*----reactivate-----*/
function reactivate(item){
	if(user == cur_frm.doc.assigned_to){
		frappe.model.set_value(item.doctype, item.name, 'end', 0)
		frappe.model.set_value(item.doctype, item.name, 'reopen', 1)
		frappe.model.set_value(item.doctype, item.name, 'activity_end_date', frappe.datetime.now_datetime())
	}
	cur_frm.get_field("employee_activity_item").grid.refresh();
}


/*-------------------*/
function time_taken(frm){
	let items = cur_frm.doc.employee_activity_item || [];
	for(let item in items){
		activity_time(items[item]);
	}
}


function activity_time(child){
	let time = "";
	if(child.activity_start_date && !child.activity_end_date){
		var today = new Date(child.activity_start_date);
		var Christmas = new Date(frappe.datetime.now_datetime());
		var diffMs = (Christmas - today); // milliseconds between now & Christmas
		var diffDays = Math.floor(diffMs / 86400000); // days
		var diffHrs = Math.floor((diffMs % 86400000) / 3600000); // hours
		var diffMins = Math.round(((diffMs % 86400000) % 3600000) / 60000); // minutes
		time = diffDays + " days, " + diffHrs + " hours, " + diffMins + " minutes";
	}else if(child.activity_start_date && child.activity_end_date){
		var today = new Date(child.activity_start_date);
                var Christmas = new Date(child.activity_end_date);
                var diffMs = (Christmas - today); // milliseconds between now & Christmas
                var diffDays = Math.floor(diffMs / 86400000); // days
                var diffHrs = Math.floor((diffMs % 86400000) / 3600000); // hours
                var diffMins = Math.round(((diffMs % 86400000) % 3600000) / 60000); // minutes
                time = diffDays + " days, " + diffHrs + " hours, " + diffMins + " minutes";
	}else if(!child.activity_start_date && !child.activity_end_date){
		time = "Not yet Started"
	}

	let html = `
                <div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="subject" title="Activity Total Time">
                        <div class="form-group">
                                <div class="clearfix">
                                        <label class="control-label" style="padding-right: 0px;">Activity Total Time</label>
                                </div>
                                <div class="control-input-wrapper">
                                        <div class="control-input">
                                                <input type="text" autocomplete="off" class="input-with-feedback form-control bold" maxlength="140" data-fieldtype="Data" data-fieldname="subject" placeholder="" data-doctype="Employee Activity" disabled value="${time}">
                                        </div>
                                        <div class="control-value like-disabled-input bold" style="display: none;">Test</div>
                                        <p class="help-box small text-muted"></p>
                                </div>
                        </div>
                </div>`;
	$(cur_frm.fields_dict[child.parentfield].grid.grid_rows_by_docname[child.name].grid_form.fields_dict['time_taken'].wrapper).html(html);
}


function check_activity_item(frm){
	$.each(frm.doc.employee_activity_item, function (index, item) {
		check_buttons(item);
	})
}
