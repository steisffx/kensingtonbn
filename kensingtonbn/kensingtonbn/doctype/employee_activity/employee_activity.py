# Copyright (c) 2022, ClefinCode and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.share import add

class EmployeeActivity(Document):
    def after_insert(self):
        add("Employee Activity", self.name, user=self.assigned_to, read=1, write=1, submit=0)

        notification = frappe.new_doc("Notification Log")
        notification.document_type = "Employee Activity"
        notification.document_name = self.name
        notification.for_user = self.assigned_to
        notification.from_user = self.assigned_by
        notification.subject = "New Task has been assigned to you by "+self.assigned_by+" with subject "+self.subject
        notification.type = "Assignment"
        notification.save(ignore_permissions=True)
