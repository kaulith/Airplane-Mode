# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, nowdate


class RentPaymentSchedule(Document):
	def validate(self):
		if self.status == "Paid" and not self.actual_payment_date:
			self.actual_payment_date = nowdate()
		if self.amount_paid:
			if self.amount_paid < self.expected_amount:
				frappe.msgprint(
					"Amount paid is less than expected amount",
					indicator="orange"
				)
			elif self.amount_paid > self.expected_amount:
				frappe.msgprint(
					"Amount paid is more than expected amount (overpayment)",
					indicator="blue"
				)


	@staticmethod
	def send_rent_reminders():
		settings = frappe.get_single("Shop Settings")

		if not settings.enable_rent_reminders:
			return

		reminder_days = settings.reminder_days_before or 3
		today = getdate(nowdate())
		reminder_date = add_days(today, reminder_days)

		schedules = frappe.get_all(
			"Rent Payment Schedule",
			filters={
				"status": "Pending",
				"due_date": ["in", [today, reminder_date]]
			},
			fields=[
				"name",
				"lease_contract",
				"tenant",
				"due_date",
				"expected_amount",
				"payment_period"
			]
		)

		for schedule in schedules:
			RentPaymentSchedule.send_reminder_email(schedule)


	@staticmethod
	def send_reminder_email(schedule):
		try:
			lease = frappe.get_doc("Shop Lease", schedule.lease_contract)

			if not lease.email:
				frappe.log_error(
					f"No email found for lease {lease.name}",
					"Rent Reminder"
				)
				return

			days_until_due = (
				getdate(schedule.due_date) - getdate(nowdate())
			).days

			if days_until_due == 0:
				subject = f"Rent Payment Due Today - {schedule.payment_period}"
				intro = "due <strong>today</strong>"
			else:
				subject = (
					f"Rent Payment Due in {days_until_due} Days - "
					f"{schedule.payment_period}"
				)
				intro = f"due in <strong>{days_until_due} days</strong>"

			message = f"""
				<p>Dear {schedule.tenant},</p>
				<p>This is a reminder that your rent payment is {intro}.</p>

				<p><strong>Payment Details:</strong></p>
				<ul>
					<li>Period: {schedule.payment_period}</li>
					<li>Due Date: {frappe.format(schedule.due_date, {'fieldtype': 'Date'})}</li>
					<li>Amount: {frappe.format(schedule.expected_amount, {'fieldtype': 'Currency'})}</li>
					<li>Contract: {schedule.lease_contract}</li>
				</ul>

				<p>Please ensure timely payment to avoid any inconvenience.</p>
				<p>Best regards,<br>Airport Management</p>
			"""

			frappe.sendmail(
				recipients=[lease.email],
				subject=subject,
				message=message
			)

			frappe.logger().info(
				f"Rent reminder sent to {lease.email} "
				f"for schedule {schedule.name}"
			)

		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"Failed to send rent reminder for {schedule.name}"
			)
