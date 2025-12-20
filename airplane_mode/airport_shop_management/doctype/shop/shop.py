# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Shop(Document):
	def before_insert(self):
		if not self.rent:
			settings = frappe.get_single("Shop Settings")
			if settings.default_rent_amount:
				self.rent = settings.default_rent_amount