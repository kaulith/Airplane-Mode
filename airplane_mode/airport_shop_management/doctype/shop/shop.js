// Copyright (c) 2025, Kaushal and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shop', {
	refresh: function(frm) {
		// Filter shop_type link to show only enabled types(set_query JS API)
		frm.set_query('shop_type', function() {
			return {
				filters: {
					'enabled': 1
				}
			};
		});
	}
});