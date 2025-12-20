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
			"options": "Airplane",
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
	data = frappe.db.sql("""
		SELECT 
			airport,
			COUNT(*) as total_shops,
			SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) as occupied,
			SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) as available,
			SUM(CASE WHEN status = 'Under Maintenance' THEN 1 ELSE 0 END) as under_maintenance
		FROM `tabShop`
		WHERE airport IS NOT NULL
		GROUP BY airport
		ORDER BY airport
	""", as_dict=1)

	for row in data:
		if row.total_shops > 0:
			row.occupancy_rate = (row.occupied / row.total_shops) * 100
		else:
			row.occupancy_rate = 0

	return data