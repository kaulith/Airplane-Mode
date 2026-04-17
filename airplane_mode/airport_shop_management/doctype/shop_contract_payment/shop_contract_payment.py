# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ShopContractPayment(Document):
	def validate(self):
		# Prevent editing paid rows
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc and old_doc.status == "Paid":
				# Allow only cancellation of paid rows
				if self.status != "Paid":
					frappe.throw(_("Cannot modify a paid payment row. Please cancel the related Rent Payment first."))
