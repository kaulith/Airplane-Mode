# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ShopArea(Document):
    def validate(self):
        if self.length is None or self.width is None:
            self.calculated_area = 0
        else:
            self.calculated_area = float(self.length) *	 float(self.width)

