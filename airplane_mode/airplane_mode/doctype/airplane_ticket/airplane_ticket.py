import frappe
import random
from frappe.model.document import Document

class AirplaneTicket(Document):

    def validate(self):
        self.remove_duplicate_addons()
        self.calculate_total()

    def before_insert(self):
        capital_alphabets = [chr(i) for i in range(ord('A'), ord('E') + 1)]
        self.seat = f"{random.randint(1, 100)}{random.choice(capital_alphabets)}"

    def before_submit(self):
        if self.status != "Boarded":
            frappe.throw("Cannot submit ticket unless status is 'Boarded'.")

    def calculate_total(self):
        addons_total = sum([d.amount for d in self.add_ons])
        self.total_amount = (self.flight_price or 0) + addons_total

    def remove_duplicate_addons(self):
        seen = set()
        unique = []

        for row in self.add_ons:
            if row.item not in seen:
                seen.add(row.item)
                unique.append(row)

        self.set("add_ons", [])
        for row in unique:
            self.append("add_ons", row)
