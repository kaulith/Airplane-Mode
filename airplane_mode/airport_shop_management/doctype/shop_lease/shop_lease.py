# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, get_last_day, getdate


class ShopLease(Document):
	def validate(self):
		self.calculate_total_base_rent()
		if not self.monthly_rent and self.total_base_rent:
			self.monthly_rent = self.total_base_rent

		if self.docstatus == 0:  
			self.validate_shop_availability()

	def validate_shop_availability(self):
		for item in self.shop:
			if item.shop:
				shop_doc = frappe.get_doc("Shop", item.shop)

				if shop_doc.status == "Occupied":
					existing_contracts = frappe.get_all(
						"Shop Lease",
						filters={
							"docstatus": 1,  # Submitted
							"status": "Active",
							"name": ["!=", self.name]
						}
					)

					for contract in existing_contracts:
						contract_doc = frappe.get_doc("Shop Lease", contract.name)
						for contract_shop in contract_doc.shop:
							if contract_shop.shop == item.shop:
								frappe.throw(
									f"Shop {item.shop} is already occupied by contract {contract.name}. "
									"Please select a different shop or cancel the existing contract first.",
									title="Shop Not Available"
								)

	def calculate_total_base_rent(self):
		total = 0
		for item in self.shop:
			if item.base_rent:
				total += item.base_rent
		self.total_base_rent = total

	def on_submit(self):
		self.status = "Active"
		self.update_shop_status("Occupied")
		self.generate_payment_schedule()

	def on_cancel(self):
		self.status = "Cancelled"
		self.update_shop_status("Available")
		self.cancel_payment_schedule()

	def update_shop_status(self, status):
		for item in self.shop:
			shop_doc = frappe.get_doc("Shop", item.shop)
			shop_doc.status = status
			shop_doc.save()

	def generate_payment_schedule(self):
		if not self.start_date or not self.end_date:
			frappe.throw("Contract start date and end date are required")

		if not self.monthly_rent:
			frappe.throw("Monthly rent amount is required")

		frappe.db.delete("Rent Payment Schedule", {"lease_contract": self.name})

		start_date = getdate(self.start_date)
		end_date = getdate(self.end_date)

		due_day = self.payment_due_day if self.payment_due_day else start_date.day

		first_due_date = add_months(start_date, 1)

		try:
			first_due_date = first_due_date.replace(day=min(due_day, get_last_day(first_due_date).day))
		except ValueError:
			first_due_date = first_due_date.replace(day=get_last_day(first_due_date).day)

		current_due_date = first_due_date
		schedule_count = 0

		while current_due_date <= end_date:
			payment_schedule = frappe.get_doc({
				"doctype": "Rent Payment Schedule",
				"lease_contract": self.name,
				"tenant": self.tenant_name,
				"payment_period": current_due_date.strftime("%B %Y"),
				"due_date": current_due_date,
				"expected_amount": self.monthly_rent,
				"status": "Pending",
			})
			payment_schedule.insert()
			schedule_count += 1

			current_due_date = add_months(current_due_date, 1)
			try:
				current_due_date = current_due_date.replace(day=min(due_day, get_last_day(current_due_date).day))
			except ValueError:
				current_due_date = current_due_date.replace(day=get_last_day(current_due_date).day)

		frappe.msgprint(f"{schedule_count} payment schedule(s) generated successfully")

	def cancel_payment_schedule(self):
		schedules = frappe.get_all(
			"Rent Payment Schedule", 
			filters={"lease_contract": self.name, "status": "Pending"}
		)

		for schedule in schedules:
			doc = frappe.get_doc("Rent Payment Schedule", schedule.name)
			doc.status = "Cancelled"
			doc.save()

		frappe.msgprint(f"{len(schedules)} pending payment schedules cancelled")