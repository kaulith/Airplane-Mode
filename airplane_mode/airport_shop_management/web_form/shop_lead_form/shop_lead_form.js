frappe.ready(function() {
	// Get shop from URL query parameter and pre-fill
	const urlParams = new URLSearchParams(window.location.search);
	const shop = urlParams.get('shop');
	
	if (shop && cur_frm) {
		cur_frm.set_value('shop', shop);
	}
})