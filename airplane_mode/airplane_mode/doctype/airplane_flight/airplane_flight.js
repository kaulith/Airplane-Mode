// Copyright (c) 2025, Kaushal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airplane Flight", {
	refresh(frm) {
		// Set filter for crew member field to show only active crew
		frm.set_query('crew_member', 'flight_crew', function(doc, cdt, cdn) {
			return {
				filters: {
					'status': 'Active'
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
