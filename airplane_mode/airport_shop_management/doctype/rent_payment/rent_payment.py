# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class RentPayment(Document):
	def validate(self):
		contract = frappe.get_doc("Shop Contract", self.shop_contract)

		if contract.status in ["Cancelled", "Expired"]:
			frappe.throw("This contract is not active")

		if contract.rent_status == "Completed":
			frappe.throw("This contract has no outstanding rent")

		if self.payment_item:
			existing = frappe.db.exists(
				"Rent Payment",
				{
					"payment_item": self.payment_item,
					"docstatus": ["in", [0, 1]],
					"name": ["!=", self.name],
				},
			)
			if existing:
				frappe.throw(f"A payment already exists for this period: {existing}")

	def on_submit(self):
		self.apply_payment()

	def on_cancel(self):
		self.rollback_payment()

	def apply_payment(self):
		item = frappe.get_doc("Shop Contract Payment", self.payment_item)

		if item.status == "Paid":
			frappe.throw("This month is already paid")

		if item.status == "Cancelled":
			frappe.throw("This payment period is cancelled")

		item.amount_paid = self.amount_paid
		item.payment_date = self.payment_date
		item.status = "Paid"
		item.rent_payment = self.name
		item.save()

	def rollback_payment(self):
		item = frappe.get_doc("Shop Contract Payment", self.payment_item)

		item.amount_paid = 0
		item.payment_date = None
		item.status = "Due"
		item.rent_payment = None
		item.save()
