import frappe
from frappe.website.website_generator import WebsiteGenerator


class AirplaneFlight(WebsiteGenerator):
	def validate(self):
		super().validate()

		# Source and destination must be different
		if self.source_airport and self.destination_airport:
			if self.source_airport == self.destination_airport:
				frappe.throw(
					"Source and Destination airports can't be the same",
					frappe.ValidationError
				)

		# Gate must belong to the source airport
		if self.gate_number and self.source_airport:
			gate_doc = frappe.get_doc("Gate Number", self.gate_number)
			if gate_doc.airport != self.source_airport:
				frappe.throw(
					f"Gate '{self.gate_number}' doesn't belong to {self.source_airport}",
					frappe.ValidationError
				)

	def on_update(self):
		if self.has_value_changed('gate_number'):
			self.update_gate_in_tickets_background()

	def update_gate_in_tickets_background(self):
		frappe.enqueue(
			method='airplane_mode.airplane_mode.doctype.airplane_flight.airplane_flight.update_tickets_gate_number',
			queue='default',
			timeout=300,
			flight_name=self.name,
			new_gate_number=self.gate_number
		)
		frappe.msgprint(
			f"Gate number update queued for all tickets of flight {self.name}",
			indicator="blue",
			alert=True
		)

@frappe.whitelist()
def get_active_crew_members(doctype, txt, searchterm, page_len, filters):
	# Only show active crew members in the selection
	return frappe.get_all(
		"Crew Member",
		filters={"status": "Active"},
		fields=["name", "first_name", "last_name", "designation"],
		as_list=True,
		limit_page_length=page_len
	)

def update_tickets_gate_number(flight_name, new_gate_number):
	try:
		tickets = frappe.get_all(
			"Airplane Ticket",
			filters={"flight": flight_name},
			fields=["name"]
		)

		updated_count = 0
		for ticket in tickets:
			ticket_doc = frappe.get_cached_doc("Airplane Ticket", ticket.name)
			ticket_doc.gate_number = new_gate_number
			ticket_doc.save()
			updated_count += 1

		frappe.logger().info(
			f"Updated gate number to {new_gate_number} "
			f"for {updated_count} tickets of flight {flight_name}"
		)

		ticket_word = "ticket" if updated_count == 1 else "tickets"
		frappe.publish_realtime(
			event='msgprint',
			message=f'Successfully updated gate number for {updated_count} {ticket_word}',
			user=frappe.session.user
		)

	except Exception:
		frappe.log_error(
			"Failed to update gate numbers for flight",
			frappe.get_traceback(),
		)
