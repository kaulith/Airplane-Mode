import frappe
from frappe.model.document import Document


class AirplaneFlight(Document):
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

def update_tickets_gate_number(flight_name, new_gate_number):
	try:
		tickets = frappe.get_all(
			"Airplane Ticket",
			filters={"flight": flight_name},
			fields=["name"]
		)

		updated_count = 0
		for ticket in tickets:
			ticket_doc = frappe.get_doc("Airplane Ticket", ticket.name)
			ticket_doc.gate_number = new_gate_number
			ticket_doc.save()
			updated_count += 1

		frappe.db.commit()

		frappe.logger().info(
			f"Updated gate number to {new_gate_number} "
			f"for {updated_count} tickets of flight {flight_name}"
		)

		frappe.publish_realtime(
			event='msgprint',
			message=f'Successfully updated gate number for {updated_count} tickets',
			user=frappe.session.user
		)

	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Failed to update gate numbers for flight {flight_name}"
		)
