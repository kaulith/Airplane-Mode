frappe.ui.form.on("Airplane Ticket", {
    refresh(frm) {
        frm.add_custom_button(
            __("Assign Seat"),
            () => {
                const d = new frappe.ui.Dialog({
                    title: __("Assign Seat"),
                    fields: [
                        {
                            label: __("Seat Number"),
                            fieldname: "seat_number",
                            fieldtype: "Data",
                            reqd: 1,
                            description: __(
                                "Enter the seat number (e.g., 12A, 5B)"
                            ),
                        },
                    ],
                    primary_action_label: __("Assign"),
                    primary_action(values) {
                        frm.set_value("seat", values.seat_number);
                        d.hide();

                        frappe.show_alert(
                            {
                                message: __(
                                    "Seat {0} assigned successfully",
                                    [values.seat_number]
                                ),
                                indicator: "green",
                            },
                            5
                        );
                    },
                });

                if (frm.doc.seat) {
                    d.set_value("seat_number", frm.doc.seat);
                }

                d.show();
            },
            __("Actions")
        );
    },
});
