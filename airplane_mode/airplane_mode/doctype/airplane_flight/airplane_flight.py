# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.website.utils import cleanup_page_name
from frappe.website.website_generator import WebsiteGenerator


class AirplaneFlight(WebsiteGenerator):
	def on_submit(self):
		self.status = "Completed"

	def before_save(self):
		if not self.route:
			self.route = f"flights/{cleanup_page_name(self.name)}"
