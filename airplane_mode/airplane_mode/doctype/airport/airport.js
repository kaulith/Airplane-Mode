// Copyright (c) 2025, Kaushal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airport", {


	refresh(frm) {

        frm.add_custom_button("Get shop list", () =>{
            //shop list with status
            frappe.db.get_list("Shop", 
                {
                    fields: ['shop_name', 'status'],
                    filters:{'airport': frm.doc.name}
                }
            ).then( r => {
                let ls = '<ol>'
                for(const i of r){
                    ls = ls + '<li>' + i.shop_name + ":" + i.status+ '</li>'
                }
                ls = ls + '</ol>'
                frappe.msgprint(ls)
            })
        })
    }
    }
)