# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, get_last_day, getdate


class ShopLease(Document):
	def validate(self):
		self.validate_shops()

	def on_submit(self):
		self.create_contracts_on_submit()

	def validate_shops(self):
		seen = set()

		for row in self.leased_shop:
			if row.shop in seen:
				frappe.throw(_("Shop {0} is duplicated in lease").format(row.shop))

			seen.add(row.shop)

			# Check if already leased
			active = frappe.db.exists(
				"Shop Contract",
				{
					"shop": row.shop,
					"status": "Active"
				}
			)

			if active:
				frappe.throw(_("Shop {0} is already leased").format(row.shop))

	def create_contracts_on_submit(self):
		create_contracts(self.name)


@frappe.whitelist()
def create_contracts(lease):
	lease_doc = frappe.get_doc("Shop Lease", lease)

	if lease_doc.docstatus != 1:
		frappe.throw(_("Lease must be submitted before creating contracts"))

	if not lease_doc.leased_shop:
		frappe.throw(_("No shops selected in this lease"))

	for row in lease_doc.leased_shop:
		# Avoid duplicates
		exists = frappe.db.exists(
			"Shop Contract",
			{
				"shop_lease": lease_doc.name,
				"shop": row.shop,
				"status": ["!=", "Cancelled"]
			}
		)
		if exists:
			continue

		shop = frappe.get_doc("Shop", row.shop)

		contract = frappe.new_doc("Shop Contract")
		contract.shop_lease = lease_doc.name
		contract.shop = shop.name
		contract.tenant = lease_doc.tenant
		contract.contract_start_date = lease_doc.start_date
		contract.contract_end_date = lease_doc.end_date
		contract.payment_due_day = lease_doc.payment_due_day
		contract.status = "Draft"

		# Snapshot
		contract.shop_number_snapshot = shop.shop_number
		contract.shop_name_snapshot = shop.shop_name
		contract.airport_snapshot = shop.airport
		contract.shop_area_snapshot = shop.area
		contract.rent_location_snapshot = shop.rent_location
		contract.shop_type_snapshot = shop.shop_type

		# Rent
		contract.monthly_rent = shop.base_rent

		contract.insert()
