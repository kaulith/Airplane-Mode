import frappe
import json

def get_context(context):
	"""Fetch shops for dropdown and handle pre-selected shop"""
	try:
		# Fetch all shops
		shops = frappe.get_all(
			"Shop",
			fields=["name", "shop_name", "shop_number", "airport", "area", "rent", "status"],
			limit_page_length=0
		)
		
		# Convert to list of dicts if needed
		shops_list = []
		for shop in shops:
			shops_list.append({
				'name': shop.name,
				'shop_name': shop.shop_name or '',
				'shop_number': shop.shop_number or '',
				'airport': shop.airport or '',
				'area': str(shop.area) if shop.area else '0',
				'rent': str(shop.rent) if shop.rent else '0',
				'status': shop.status or 'Available'
			})
	except Exception as e:
		shops_list = []
		frappe.log_error(frappe.get_traceback(), "Shop Lead Error")
	
	# Get pre-selected shop from URL
	selected_shop = frappe.request.args.get('shop', '')
	
	# Set context variables
	context.shops = shops_list
	context.selected_shop = selected_shop
	context.shops_json = json.dumps(shops_list)
	
	return context
