from . import __version__ as app_version

app_name = "kensingtonbn"
app_title = "Kensingtonbn"
app_publisher = "ClefinCode"
app_description = "Kensingtonbn Website"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@clefincode.com"
app_license = "MIT"
# app_logo_url = "/assets/kensingtonbn/images/logo.png"

# Includes in <head>
# ------------------
website_context = {
	"favicon": 	"/assets/kensingtonbn/images/favicon.jpeg",
	"splash_image": "/assets/kensingtonbn/images/splash_image.jpeg"
}
# include js, css files in header of desk.html
# app_include_css = "/assets/kensingtonbn/css/kensingtonbn.css"
# app_include_js = "/assets/kensingtonbn/js/kensingtonbn.js"
app_include_css = [
	'https://fonts.googleapis.com/css2?family=Libre+Barcode+39&family=Poppins&display=swap',
	'/assets/kensingtonbn/css/overrides.css'
]
# include js, css files in header of web template
# web_include_css = "/assets/kensingtonbn/css/kensingtonbn.css"
# web_include_js = "/assets/kensingtonbn/js/kensingtonbn.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "kensingtonbn/public/scss/website"

# include js, css files in header of web form
webform_include_js = {"Address": "public/js/webform/address.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Homepage" : "public/js/doctype/filter_batch_in_homepage.js",
	"Item" : "public/js/doctype/filter_batch_in_item.js",
	"Best Value" : "public/js/doctype/filter_batch_in_best_value.js",
	"Item Label" : "public/js/doctype/filter_batch_in_item_label.js",
	"Suggested Items" : "public/js/doctype/filter_batch_in_suggested.js",
	"Recommended For Order" : "public/js/doctype/filter_batch_in_recommended.js",
	"Container Reconciliation" : "public/js/doctype/filter_batch_in_container_reconciliation.js",
	"System Settings" : "public/js/doctype/system_settings/custom_system_settings.js",
    "Purchase Invoice":"public/js/doctype/Purchase_Invoice_Item.js",
    "Purchase Order":"public/js/doctype/Purchase_Order_Item.js",
	#"Product Bundle": "public/js/doctype/product_bundle.js"
	}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }
jenv = {
	"methods": [
		"get_jinja_data:kensingtonbn.kensingtonbn.doctype.item_label.item_label.get_jinja_data",
        "get_jinja_barcode_image:kensingtonbn.www.barcode.index.get_jinja_barcode_image",
        
	]
}
# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "kensingtonbn.install.before_install"
# after_install = "kensingtonbn.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "kensingtonbn.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
	"Item": {
		"on_update": [
			"kensingtonbn.www.pages.qr.create_qr_code"
		],
		"on_trash": [
			"kensingtonbn.www.pages.qr.delete_qr_code_file"
		]
	},
}
# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly_long": [
		"kensingtonbn.www.api.api.set_batch_ranking"
	],
# 	"all": [
# 		"kensingtonbn.tasks.all"
# 	],
# 	"daily": [
# 		"kensingtonbn.tasks.daily"
# 	],
# 	"hourly": [
# 		"kensingtonbn.tasks.hourly"
# 	],
# 	"weekly": [
# 		"kensingtonbn.tasks.weekly"
# 	]
# 	"monthly": [
# 		"kensingtonbn.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "kensingtonbn.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "kensingtonbn.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "kensingtonbn.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"kensingtonbn.auth.validate"
# ]

