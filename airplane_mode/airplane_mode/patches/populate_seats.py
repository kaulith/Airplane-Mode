import frappe
import random

def execute():
    tickets = frappe.db.get_all("Airplane Ticket", pluck="name")

    letters = [chr(i) for i in range(ord('A'), ord('E') + 1)]

    for ticket_name in tickets:
        ticket = frappe.get_doc("Airplane Ticket", ticket_name)

        if ticket.seat:
            continue

        seat = f"{random.randint(1, 100)}{random.choice(letters)}"
        ticket.db_set("seat", seat)

    frappe.db.commit()
