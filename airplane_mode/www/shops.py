import frappe
import json

def get_context(context):
	"""Fetch shops and all airports for the listing page"""
	shops = frappe.get_all(
		'Shop',
		fields=['name', 'shop_name', 'shop_number', 'airport', 'area', 'rent', 'status', 'location'],
		limit_page_length=500
	)
	
	try:
		all_airports = frappe.get_all('Airport', fields=['name'], limit_page_length=0)
		airports = sorted([airport.name for airport in all_airports])
	except:
		airports = sorted(list(set([shop.get('airport') for shop in shops if shop.get('airport')])))
	
	for shop in shops:
		if shop.get('rent'):
			shop['rent'] = str(shop['rent'])
	
	context["shops"] = shops
	context["airports"] = airports
	context["shops_json"] = json.dumps(shops)
	
	return context
