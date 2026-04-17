# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, get_last_day, getdate, today


class ShopContract(Document):
    def validate(self):
        self.validate_dates()
        self.validate_shop_availability()
        if self.tenant:
            overdue = frappe.db.exists("Shop Contract", {
                "tenant": self.tenant,
                "rent_status": "Overdue",
                "name": ["!=", self.name]
            })

            if overdue:
                frappe.throw(_("Tenant has overdue rent. Cannot create new contract."))

    def validate_dates(self):
        if self.contract_start_date and self.contract_end_date:
            if getdate(self.contract_start_date) > getdate(self.contract_end_date):
                frappe.throw(_("Start date can't be after end date"))

    def validate_shop_availability(self):
        if not self.shop:
            return

        active = frappe.db.exists("Shop Contract", {
            "shop": self.shop,
            "status": "Active",
            "name": ["!=", self.name]
        })
        if active:
            frappe.throw(_("Shop {0} is already under an active contract").format(self.shop))


    def before_submit(self):
        self.generate_payment_plan()

    def on_submit(self):
        self.lock_shop()
        frappe.db.set_value("Shop Contract", self.name, "status", "Active")

    def on_cancel(self):
        self.release_shop()
        self.cancel_future_payments()
        frappe.db.set_value("Shop Contract", self.name, "status", "Cancelled")


    # Shop State
    def lock_shop(self):
        frappe.db.set_value("Shop", self.shop, "status", "Occupied")

    def release_shop(self):
        frappe.db.set_value("Shop", self.shop, "status", "Available")

    # Payment Plan
    def generate_payment_plan(self):
        self.shop_contract_payment.clear()

        start = getdate(self.contract_start_date)
        end = getdate(self.contract_end_date)
        due_day = self.payment_due_day or start.day
        today_date = getdate(today())

        current = start
        while current <= end:
            period_start = current.replace(day=1)
            period_end = get_last_day(current)
            due_date = self.get_due_date(current, due_day)

            status = "Due" if today_date >= period_start else "Planned"

            self.append("shop_contract_payment", {
                "payment_month": period_start,
                "period_start": period_start,
                "period_end": period_end,
                "due_date": due_date,
                "amount_due": self.monthly_rent,
                "amount_paid": 0,
                "status": status
            })

            current = add_months(current, 1)

    def cancel_future_payments(self):
        for row in self.shop_contract_payment:
            if row.status in ("Planned", "Due"):
                frappe.db.set_value("Shop Contract Payment", row.name, "status", "Cancelled")


    def get_due_date(self, base_date, due_day):
        # Handle months with fewer days than due_day (e.g., Feb 30th)
        try:
            return base_date.replace(day=due_day)
        except ValueError:
            return get_last_day(base_date)
