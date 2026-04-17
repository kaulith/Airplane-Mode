import random

import frappe
from frappe import _
from frappe.model.document import Document


class AirplaneTicket(Document):
	def validate(self):
		self.update_flight_details()
		self.remove_duplicate_addons()
		self.calculate_total()

	def before_insert(self):
		if not self.seat:
			capital_alphabets = [chr(i) for i in range(ord("A"), ord("E") + 1)]
			self.seat = f"{random.randint(1, 100)}{random.choice(capital_alphabets)}"
		self.check_capacity()

	def before_submit(self):
		if self.status != "Boarded":
			frappe.throw(_("Cannot submit ticket unless status is 'Boarded'."))

	def update_flight_details(self):
		if not self.flight:
			return

		flight = frappe.get_doc("Airplane Flight", self.flight)

		self.source_airport_code = flight.get("source_airport_code")
		self.destination_airport_code = flight.get("destination_airport_code")
		# Only set flight_price if not already entered by user
		if not self.flight_price:
			self.flight_price = flight.get("flight_price")
		self.departure_date = flight.get("date_of_departure")
		self.departure_time = flight.get("time_of_departure")
		self.gate_number = flight.get("gate_number")
		self.duration_of_flight = flight.get("duration")

	def calculate_total(self):
		addons_total = sum([d.amount for d in self.add_ons])
		self.total_amount = float(self.flight_price or 0) + float(addons_total or 0)

	def remove_duplicate_addons(self):
		seen = set()
		unique = []
		duplicates = []
		for row in self.add_ons:
			if row.item not in seen:
				seen.add(row.item)
				unique.append(row)
			else:
				duplicates.append(row.item)
		if duplicates:
			self.set("add_ons", [])
			for row in unique:
				self.append("add_ons", row)
			frappe.msgprint(
				_("Removed duplicate add-ons: {0}").format(", ".join(duplicates)),
				indicator="orange",
				alert=True,
			)

	def check_capacity(self):
		if not self.flight:
			return

		flight = frappe.get_doc("Airplane Flight", self.flight)
		if not flight.airplane:
			return

		airplane = frappe.get_doc("Airplane", flight.airplane)
		capacity = airplane.capacity

		existing_tickets = frappe.db.count(
			"Airplane Ticket",
			{
				"flight": self.flight,
				"docstatus": ["!=", 2],
				"name": ["!=", self.name],
			},
		)

		if existing_tickets >= capacity:
			frappe.throw(
				_("Cannot create ticket. Flight {0} has reached maximum capacity of {1} seats.").format(
					self.flight, capacity
				),
				title=_("Capacity Exceeded"),
			)
