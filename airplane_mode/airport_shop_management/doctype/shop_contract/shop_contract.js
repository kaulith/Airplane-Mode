frappe.ui.form.on("Shop Contract Payment", {
    pay(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.status === "Paid") {
            frappe.msgprint("This month is already paid");
            return;
        }

        frappe.new_doc("Rent Payment", {
            shop_contract: frm.doc.name,
            tenant: frm.doc.tenant,
            payment_item: row.name,
            amount_paid: row.amount_due,
            payment_date: frappe.datetime.nowdate()
        });
    }
});
