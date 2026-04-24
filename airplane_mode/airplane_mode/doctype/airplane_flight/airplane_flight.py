import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator


class AirplaneFlight(WebsiteGenerator):
	def validate(self):
		super().validate()

		# Source and destination must be different
		if self.source_airport and self.destination_airport:
			if self.source_airport == self.destination_airport:
				frappe.throw(
					_("Source and Destination airports can't be the same"),
					frappe.ValidationError
				)

		# Gate must belong to the source airport
		if self.gate_number and self.source_airport:
			gate_doc = frappe.get_doc("Gate Number", self.gate_number)
			if gate_doc.airport != self.source_airport:
				frappe.throw(
					_("Gate '{0}' doesn't belong to {1}").format(self.gate_number, self.source_airport),
					frappe.ValidationError
				)

	def on_update(self):
		if self.has_value_changed('gate_number'):  #fire this only when gate actually changed, not on every save
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
def get_active_crew_members(
	doctype: str,
	txt: str,
	searchterm: str,
	page_len: int,
	filters: dict,
) -> list:
	# Only show active crew members in the selection
	return frappe.get_all(
		"Crew Member",
		filters={"status": "Active"},
		fields=["name", "first_name", "last_name", "designation"],
		as_list=True,
		limit_page_length=page_len
	)

def update_tickets_gate_number(flight_name: str, new_gate_number: str) -> None:
	try:
		tickets = frappe.get_all(
			"Airplane Ticket",
			filters={"flight": flight_name},
			fields=["name"]
		)

		updated_count = 0
		for ticket in tickets:
			frappe.db.set_value("Airplane Ticket", ticket.name, "gate_number", new_gate_number)
			updated_count += 1

		ticket_word = "ticket" if updated_count == 1 else "tickets"
		frappe.publish_realtime(
			event='msgprint',
			message=f'Successfully updated gate number for {updated_count} {ticket_word}',
			user=frappe.session.user
		)

	except Exception:
		frappe.log_error(
			title="Failed to update gate numbers for flight",
			message=frappe.get_traceback(),
		)
