# Copyright (c) 2026, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ShopLead(Document):
	pass

@frappe.whitelist()
def convert_to_tenant(lead_name):
	"""Convert a Shop Lead to a Shop Tenant"""
	lead = frappe.get_doc("Shop Lead", lead_name)

	# Check if already converted
	if lead.get("tenant"):
		frappe.throw(_("This lead has already been converted to Tenant: {0}").format(lead.tenant))

	if lead.status == "Converted":
		frappe.throw(_("This lead has already been converted"))

	# Validate required fields
	if not lead.company_name:
		frappe.throw(_("Company Name is required to convert to tenant"))

	# Create new tenant
	from frappe.utils import strip_html_tags

	tenant = frappe.get_doc({
		"doctype": "Shop Tenant",
		"tenant_name": lead.company_name,
		"contact_person": lead.full_name,
		"email": lead.email,
		"phone": lead.phone,
		"company_name": lead.company_name,
		"address": strip_html_tags(lead.address) if lead.address else ""
	})
	tenant.insert()

	# Update lead
	lead.tenant = tenant.name
	lead.status = "Converted"
	lead.save()

	frappe.msgprint(f"Lead converted to Tenant: {tenant.name}")

	return tenant.name
