from typing import Optional

import frappe
from frappe import _


@frappe.whitelist()
def get_shops(airport: str | None = None, status: str | None = None) -> list[dict]:
	"""GET /api/method/airplane_mode.api.get_shops

	List shops with optional filters.
	Requires authentication.
	"""
	filters = {}
	if airport:
		filters["airport"] = airport
	if status:
		filters["status"] = status

	shops = frappe.get_all(
		"Shop",
		filters=filters,
		fields=["name", "shop_number", "shop_name", "airport", "shop_type", "area", "base_rent", "status"],
	)

	return shops

@frappe.whitelist()
def get_shop_count(airport: str) -> int:
	return frappe.db.count('Shop', {'airport': airport})

@frappe.whitelist()
def set_terminal_for_airport(shop_name: str, terminal: str) -> None:
	frappe.db.set_value('Shop', shop_name, 'terminal', terminal)

@frappe.whitelist()
def create_shop(
	shop_number: str,
	shop_area: str,
	shop_name: str | None = None,
	airport: str | None = None,
	shop_type: str | None = None,
	floor: str | None = None,
	terminal: str | None = None,
	zone: str | None = None,
) -> dict:
	"""POST /api/method/airplane_mode.api.create_shop

	Create a new shop.
	Requires authentication.
	"""
	shop = frappe.new_doc("Shop")
	shop.shop_number = shop_number
	shop.shop_area = shop_area

	if shop_name:
		shop.shop_name = shop_name
	if airport:
		shop.airport = airport
	if shop_type:
		shop.shop_type = shop_type
	if floor:
		shop.floor = floor
	if terminal:
		shop.terminal = terminal
	if zone:
		shop.zone = zone

	shop.insert()

	return shop.as_dict()
