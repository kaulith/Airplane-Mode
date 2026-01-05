import frappe

def get_context(context):
	# Pre-fill shop from query parameter
	shop = frappe.request.args.get('shop')
	if shop:
		context.doc = {"shop": shop}
