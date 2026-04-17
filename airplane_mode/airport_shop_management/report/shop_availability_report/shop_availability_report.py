# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "airport",
			"label": "Airport",
			"fieldtype": "Link",
			"options": "Airport",
			"width": 200
		},
		{
			"fieldname": "total_shops",
			"label": "Total Shops",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "occupied",
			"label": "Occupied",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "available",
			"label": "Available",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "under_maintenance",
			"label": "Under Maintenance",
			"fieldtype": "Int",
			"width": 150
		},
		{
			"fieldname": "occupancy_rate",
			"label": "Occupancy Rate (%)",
			"fieldtype": "Percent",
			"width": 150
		}
	]

def get_data(filters):
	conditions = ""
	values = {}
	if filters and filters.get("airport"):
		conditions = "WHERE a.name = %(airport)s"
		values["airport"] = filters["airport"]

	data = frappe.db.sql("""
		SELECT
			a.name as airport,
			COUNT(s.name) as total_shops,
			SUM(CASE WHEN s.status = 'Occupied' THEN 1 ELSE 0 END) as occupied,
			SUM(CASE WHEN s.status = 'Available' THEN 1 ELSE 0 END) as available,
			SUM(CASE WHEN s.status = 'Under Maintenance' THEN 1 ELSE 0 END) as under_maintenance
		FROM `tabAirport` a
		LEFT JOIN `tabShop` s ON a.name = s.airport
		{conditions}
		GROUP BY a.name
		ORDER BY a.name
	""".format(conditions=conditions), values=values, as_dict=1)

	for row in data:
		row.occupancy_rate = (row.occupied / row.total_shops * 100) if row.total_shops > 0 else 0

	return data