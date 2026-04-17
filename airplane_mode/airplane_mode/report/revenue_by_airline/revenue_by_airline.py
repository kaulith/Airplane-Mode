# Copyright (c) 2025, Kaushal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Coalesce


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
	Airline = DocType("Airline")
	Airplane = DocType("Airplane")
	Flight = DocType("Airplane Flight")
	Ticket = DocType("Airplane Ticket")

	revenue_field = Coalesce(Sum(Ticket.total_amount), 0)

	query = (
		frappe.qb.from_(Airline)
		.left_join(Airplane).on(Airplane.airline == Airline.name)
		.left_join(Flight).on(Flight.airplane == Airplane.name)
		.left_join(Ticket).on(
			(Ticket.flight == Flight.name) & (Ticket.docstatus == 1)
		)
		.select(
			Airline.name.as_("airline"),
			revenue_field.as_("revenue"),
		)
		.groupby(Airline.name)
		.orderby(revenue_field, order=frappe.qb.desc)
	)

	return query.run(as_dict=True)


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
