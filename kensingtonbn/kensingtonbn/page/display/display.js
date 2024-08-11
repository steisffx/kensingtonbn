frappe.pages['display'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Display',
		single_column: true
	});

	new frappe.Display(wrapper);
}

frappe.Display = Class.extend({
	init: function(wrapper){
		var me = this;
		this.parent = wrapper;
		setTimeout(function() {
			me.setup(wrapper);
		}, 10);
	},

	setup: function(wrapper){
		frappe.realtime.on('realtime_updates', function(data) {
			frappe.msgprint(data);
		});
	}
});
