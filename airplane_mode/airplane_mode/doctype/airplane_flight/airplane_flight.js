// Copyright (c) 2025, Kaushal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airplane Flight", {
	refresh(frm) {
		let dep_field = frm.fields_dict.date_of_departure;
		if (dep_field.datepicker) {
			dep_field.datepicker.update("minDate", new Date());
		}

		// Set filter for crew member field: active + belongs to flight's airline
		frm.set_query('crew_member', 'flight_crew', function(doc, cdt, cdn) {
			return {
				filters: {
					'status': 'Active',
					'airline': frm.doc.airline
				}
			};
		});

		// Set filter for gate number field to show only gates from source airport
		frm.set_query('gate_number', function() {
			return {
				filters: {
					'airport': frm.doc.source_airport
				}
			};
		});
	}
});
