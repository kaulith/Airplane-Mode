# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)

	return columns, data, None, chart, summary


def get_columns():
	return [
		{
			"fieldname": "airline",
			"label": _("Airline"),
			"fieldtype": "Link",
			"options": "Airline",
			"width": 200,
		},
		{"fieldname": "revenue", "label": _("Revenue"), "fieldtype": "Currency", "width": 150},
	]


def get_data(filters):
	airlines = frappe.get_all("Airline", fields=["name"])

	data = []
	total_revenue = 0

	for airline in airlines:
		revenue = frappe.db.sql(
			"""
            SELECT COALESCE(SUM(ticket.total_amount), 0) as revenue
            FROM `tabAirplane Ticket` as ticket
            INNER JOIN `tabAirplane Flight` as flight ON ticket.flight = flight.name
            INNER JOIN `tabAirplane` as airplane ON flight.airplane = airplane.name
            WHERE airplane.airline = %s
            AND ticket.docstatus = 1
        """,
			(airline.name,),
			as_dict=True,
		)

		airline_revenue = revenue[0].revenue if revenue else 0
		total_revenue += airline_revenue

		data.append({"airline": airline.name, "revenue": airline_revenue})

	# Sort by revenue descending
	data.sort(key=lambda x: x["revenue"], reverse=True)

	return data


def get_chart_data(data):
	if not data:
		return None

	labels = []
	values = []

	for row in data:
		labels.append(row["airline"])
		values.append(row["revenue"])

	return {
		"data": {"labels": labels, "datasets": [{"name": _("Revenue"), "values": values}]},
		"type": "donut",
		"height": 300,
		"colors": ["#FF6B9D", "#4A90E2", "#50E3C2", "#F5A623", "#BD10E0"],
	}


def get_summary(data):
	if not data:
		return []

	total_revenue = sum(row["revenue"] for row in data)

	return [
		{"value": total_revenue, "label": _("Total Revenue"), "datatype": "Currency", "indicator": "green"}
	]
