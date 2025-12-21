import frappe
from urllib.parse import unquote

def get_context(context):
	"""Fetch shop details and active lease info"""
	shop_name = frappe.request.args.get("shop") or frappe.form_dict.get("shop")
	
	if shop_name:
		shop_name = unquote(shop_name)
	
	context["shop"] = None
	context["lease"] = None
	
	if not shop_name:
		return context
	
	try:
		# Fetch shop document
		context["shop"] = frappe.get_doc("Shop", shop_name)
		
		if context["shop"].status == "Occupied":
			leases = frappe.get_all(
				"Shop Lease",
				filters={"shop": shop_name, "status": "Active"},
				fields=["name", "tenant", "tenant_name", "lease_start_date", "lease_end_date"],
				limit_page_length=1
			)
			if leases:
				context["lease"] = leases[0]
	
	except frappe.DoesNotExistError:
		context["shop"] = None
		context["lease"] = None
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Shop Details Error")
	
	return context
