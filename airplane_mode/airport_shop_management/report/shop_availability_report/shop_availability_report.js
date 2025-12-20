// Copyright (c) 2025, Kaushal and contributors
// For license information, please see license.txt

frappe.query_reports["Shop Availability Report"] = {
	"filters": [
		{
			"fieldname": "airport",
			"label": __("Airport"),
			"fieldtype": "Link",
			"options": "Airplane"
		}
	]
};