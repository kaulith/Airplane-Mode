# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class Shop(WebsiteGenerator):
    def validate(self):
        super().validate()

        if self.shop_area:
            area = frappe.db.get_value("Shop Area", self.shop_area, "calculated_area")
            self.area = area

        # Auto-fill base_rent with default_rent_amount if empty
        if not self.base_rent:
            settings = frappe.get_single("Shop Settings")
            self.base_rent = settings.default_rent_amount or 0
    def get_context(self, context):
        # Add contract information if the shop is occupied
        if self.status == "Occupied":
            contracts = frappe.get_all(
                "Shop Contract",
                filters={"shop": self.name, "status": "Active"},
                fields=["name", "tenant", "contract_start_date", "contract_end_date", "monthly_rent"],
                limit_page_length=1
            )
            if contracts:
                contract = contracts[0]
                tenant_name = frappe.db.get_value("Shop Tenant", contract.tenant, "tenant_name")
                contract["tenant_name"] = tenant_name
                context["lease"] = contract

        return context
