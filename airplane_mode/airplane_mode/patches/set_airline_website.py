import frappe

def execute():
    """Populate website field for existing Airline records"""
    airlines = {
        "Emirates": "https://www.emirates.com",
        "Qatar Airways": "https://www.qatarairways.com",
        "Lufthansa": "https://www.lufthansa.com",
        "Singapore Airlines": "https://www.singaporeair.com",
    }

    for airline_name, website in airlines.items():
        frappe.db.set_value("Airline", airline_name, "website", website, update_modified=False)

    frappe.db.commit()
