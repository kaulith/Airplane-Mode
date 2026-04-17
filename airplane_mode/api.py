import frappe
from frappe import _


@frappe.whitelist()
def get_shops(airport=None, status=None):
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
def create_shop(shop_number, shop_area, shop_name=None, airport=None, shop_type=None, floor=None, terminal=None, zone=None):
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
