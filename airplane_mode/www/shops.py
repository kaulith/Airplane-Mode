import frappe


def get_context(context):
	# Get all shops and airports for the shop listing page
	shops = frappe.get_all(
		'Shop',
		fields=['name', 'shop_name', 'shop_number', 'airport', 'area', 'base_rent', 'status', 'rent_location', 'route'],
		limit_page_length=0
	)

	all_airports = frappe.get_all('Airport', fields=['name'], limit_page_length=0)
	airports = sorted([airport.name for airport in all_airports])

	context["shops"] = shops
	context["airports"] = airports
	return context
