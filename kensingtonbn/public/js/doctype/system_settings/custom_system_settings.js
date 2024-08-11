frappe.ui.form.on("System Settings", {
	refresh: function(frm) {
		frm.add_custom_button(__("Reset Website Users"), function() {
			frappe.confirm(__("Reset All Website Users Password?"), function() {
					frappe.call({
						method: "kensingtonbn.www.api.api.reset_password_all_users",
						callback: function(r) {
							frappe.msgprint('Done');
						}
					});
				});
			})
			
	},
	
	
});