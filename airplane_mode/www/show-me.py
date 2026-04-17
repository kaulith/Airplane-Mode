import re


def get_context(context):
	color = context.get("frappe", {}).get("form_dict", {}).get("color", "")

	# Only allow safe CSS color values (hex, named colors, rgb/rgba)
	if color and re.match(r"^[a-zA-Z0-9#(), .%]+$", color):
		context["color"] = color
	else:
		context["color"] = "black"
