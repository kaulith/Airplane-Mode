# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	"""Define the columns for the report"""
	return [
		{
			"fieldname": "add_on_type",
			"label": "Add-On Type",
			"fieldtype": "Link",
			"options": "Airplane Ticket Add-on Type",
			"width": 300,
		},
		{"fieldname": "sold_count", "label": "Sold Count", "fieldtype": "Int", "width": 150},
	]


def get_data(filters):
	data = frappe.db.sql(
		"""
        SELECT 
            item as add_on_type,
            COUNT(*) as sold_count
        FROM 
            `tabAirplane Ticket Add-on Item`
        WHERE
            parenttype = 'Airplane Ticket'
        GROUP BY 
            item
        ORDER BY 
            sold_count DESC
    """,
		as_dict=1,
	)

	return data
