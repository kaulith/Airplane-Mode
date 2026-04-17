from datetime import timedelta

import frappe
from frappe.utils import getdate, today


def update_shop_status_on_contract_expiry():
	# Free up shops when contracts expire
	now = getdate(today())

	expired_contracts = frappe.get_all(
		"Shop Contract",
		filters={"status": "Active", "contract_end_date": ["<", now]},
		fields=["name", "shop"],
	)

	for contract in expired_contracts:
		frappe.db.set_value("Shop", contract.shop, "status", "Available")
		frappe.db.set_value("Shop Contract", contract.name, "status", "Expired")


def send_rent_reminders():
	settings = frappe.get_single("Shop Settings")

	if not settings.enable_rent_reminder:
		return

	# Figure out which payments are coming up
	days_before = settings.reminder_days_before or 3
	target = getdate(today()) + timedelta(days=days_before)

	#instead of ["!=", "Paid"] using "in" as prior one can scan "cancelled" & "Overdue" rows
	items = frappe.get_all(
		"Shop Contract Payment",
		filters={"due_date": target, "status": ["in", ["Planned", "Due"]]},
		fields=["parent", "due_date"],
	)

	# Send email to each tenant whose rent is due(before_due_day)
	for item in items:
		contract = frappe.get_doc("Shop Contract", item.parent)
		tenant = frappe.get_doc("Shop Tenant", contract.tenant)

		frappe.sendmail(
			recipients=tenant.email,
			subject="Rent Due Reminder",
			message=f"Your rent for shop {contract.shop_number_snapshot} is due on {item.due_date}",
		)


def update_rent_status():
	# Update payment row status based on dates (only non-terminal statuses)
	rows = frappe.get_all(
		"Shop Contract Payment",
		filters={"status": ["in", ["Planned", "Due"]]},
		fields=["name", "due_date", "payment_month", "status"],
	)

	now = getdate(today())
	for r in rows:
		if now > getdate(r.due_date):
			new_status = "Overdue"
		elif now >= getdate(r.payment_month):
			new_status = "Due"
		else:
			new_status = "Planned"

		if new_status != r.status:
			frappe.db.set_value("Shop Contract Payment", r.name, "status", new_status)

	# Update rent_status only for active contracts (not expired/cancelled/completed)
	contracts = frappe.get_all(
		"Shop Contract",
		filters={"status": "Active"},
		fields=["name"],
	)

	for c in contracts:
		children = frappe.get_all(
			"Shop Contract Payment",
			filters={"parent": c.name},
			fields=["status", "due_date"],
			order_by="due_date asc",
		)

		if not children:
			contract_status = "Active"
		else:
			past_and_current = [p for p in children if getdate(p.due_date) <= now]

			if all(p.status == "Paid" for p in children):
				contract_status = "Completed"
			elif any(p.status == "Overdue" for p in past_and_current):
				contract_status = "Overdue"
			elif any(p.status == "Due" for p in past_and_current):
				contract_status = "Due"
			else:
				contract_status = "Active"

		frappe.db.set_value("Shop Contract", c.name, "rent_status", contract_status)
