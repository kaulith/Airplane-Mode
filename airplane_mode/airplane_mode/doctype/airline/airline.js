frappe.ui.form.on('Airline', {
    refresh: function(frm) {
        if (frm.doc.website) {
            frm.add_web_link(frm.doc.website, __('Visit Website'));
        }
    },
    
    website: function(frm) {
        frm.refresh();
    }
});