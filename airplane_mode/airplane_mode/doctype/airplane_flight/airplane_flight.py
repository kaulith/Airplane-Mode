# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator


class AirplaneFlight(Document):
	def on_submit(self):
		self.status = "Completed"
