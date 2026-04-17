# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CrewMember(Document):
	def before_save(self):
		if self.last_name:
			self.full_name = f"{self.first_name} {self.last_name}"
		else:
			self.full_name = self.first_name

		self.check_duplicate_crew_member()

	def check_duplicate_crew_member(self):
		# Don't allow same name + airline combo
		if not self.first_name or not self.airline:
			return

		filters = {
			"first_name": self.first_name,
			"airline": self.airline,
			"name": ["!=", self.name]
		}

		# If last_name exists, include it in the filter
		if self.last_name:
			filters["last_name"] = self.last_name

		existing_crew = frappe.db.exists("Crew Member", filters)

		if existing_crew:
			frappe.throw(
				f"Crew member '{self.full_name}' already exists in {self.airline}. No duplicates allowed.",
				frappe.DuplicateEntryError
			)
