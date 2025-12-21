# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShopLead(Document):
	def validate(self):
		if not self.email:
			frappe.throw("Email is required")
		if not self.phone:
			frappe.throw("Phone is required")

	def on_insert(self):
		# Send confirmation email to the lead
		self.send_confirmation_email()

	def send_confirmation_email(self):
		try:
			message = f"""
				<p>Dear {self.lead_name},</p>
				<p>Thank you for your interest in leasing Shop {self.shop_name} at {self.airport or 'our airport'}!</p>

				<p>We have received your lead submission and our team will contact you shortly to discuss:</p>
				<ul>
					<li>Shop specifications and availability</li>
					<li>Lease terms and pricing</li>
					<li>Documentation requirements</li>
					<li>Next steps in the leasing process</li>
				</ul>

				<p><strong>Your Submission Details:</strong></p>
				<ul>
					<li>Shop: {self.shop_name}</li>
					<li>Company/Organization: {self.company_name or 'N/A'}</li>
					<li>Phone: {self.phone}</li>
					<li>Reference: {self.name}</li>
				</ul>

				<p>If you have any questions in the meantime, feel free to reply to this email.</p>
				<p>Best regards,<br>Airport Shop Management Team</p>
			"""

			frappe.sendmail(
				recipients=[self.email],
				subject=f"Shop Lead Confirmation - {self.shop_name}",
				message=message
			)

			frappe.logger().info(
				f"Shop lead confirmation email sent to {self.email} "
				f"for lead {self.name}"
			)
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"Failed to send confirmation email for shop lead {self.name}"
			)
