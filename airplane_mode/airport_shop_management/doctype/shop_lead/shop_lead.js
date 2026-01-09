// Copyright (c) 2026, Kaushal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shop Lead", {
	refresh(frm) {
		// Show "Convert to Tenant" button if not already converted
		if (frm.doc.status !== "Converted" && !frm.doc.tenant && !frm.is_new()) {
			frm.add_custom_button(__("Convert to Tenant"), function() {
				frappe.call({
					method: "airplane_mode.airport_shop_management.doctype.shop_lead.shop_lead.convert_to_tenant",
					args: {
						lead_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frm.reload_doc();
							// Open the new tenant
							frappe.set_route("Form", "Shop Tenant", r.message);
						}
					}
				});
			});
		}
		
		// If already converted, show link to tenant
		if (frm.doc.tenant) {
			frm.add_custom_button(__("View Tenant"), function() {
				frappe.set_route("Form", "Shop Tenant", frm.doc.tenant);
			});
		}
	},
});
