import json
from pathlib import Path
import streamlit as st

json_file = Path("inventory.json")

if json_file.exists():
    with open(json_file, "r") as f:
        inventory = json.load(f)
else:
    inventory = []

with open(json_file, "w") as f:
    json.dump(inventory, f, indent=4)

#1: Place Order (Create)

if "orders" not in st.session_state:
    st.session_state.orders = []

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Place Order",
    "View Inventory",
    "Restock",
    "Manage Orders",
    "absen      ce"
])

with tab1:
    st.header("Place Order")
    item_names = [item["name"] for item in inventory]
    selected_item = st.selectbox("Select Item", item_names)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    customer = st.text_input("Customer Name")
    if st.button("Submit Order"):
        for item in inventory:
            if item["name"] == selected_item:
                if item["stock"] >= quantity:
                    item["stock"] -= quantity
                    total = item["price"] * quantity
                    order = {
                        "order_id": len(st.session_state.orders) + 1,
                        "customer": customer,
                        "item": selected_item,
                        "total": total,
                        "status": "Placed"
                    }
                    st.session_state.orders.append(order)
                    with open(json_file, "w") as f:
                        json.dump(inventory, f, indent=4)
                    st.success("Order Placed Successfully!")
                    with st.expander("View Receipt"):
                        st.write("Order ID:", order["order_id"])
                        st.write("Customer:", order["customer"])
                        st.write("Item:", order["item"])
                        st.write("Total:", order["total"])
                        st.write("Status:", order["status"])
                else:
                    st.error("Out of Stock")


#2: View and Search Inventory (Read)

with tab2:
    st.header("View & Search Inventory")

    search = st.text_input("Search for an item")

    filtered_inventory = inventory

    if search:
        filtered_inventory = [
            item for item in inventory
            if search.lower() in item ["name"].lower()
        ]

        total_stock = sum(item["stock"] for item in inventory)

        st.metric("Total Items in Stock", total_stock)

    for item in filtered_inventory:
        if item["stock"] < 10:
            st.warning(item)
        else:
            st.write(item)

#3. Restock (Update)

with tab3:
    st.header("Restock Items")

    item_names = [item["name"] for item in inventory]

    selected_item = st.selectbox("Select Item to Restock", item_names)

    amount = st.number_input("Amount to Add", min_value=1)

    if st.button("Update Stock"):
        for item in inventory:
            if item["name"] == selected_item:
                item["stock"] += amount
        with open(json_file, "w") as f:
            json.dump(inventory, f, indent=4)
        st.success("Stock Updated Successfully!")

#4. Manage Orders (Delete/Cancel)

with tab4:
    st.header("Manage Orders")
    if len(st.session_state.orders) == 0:
        st.write("No orders available.")
    else:
        st.write(st.session_state.orders)
        order_ids = [order["order_id"] for order in st.session_state.orders]
        selected_order = st.selectbox("Select Order ID to Cancel", order_ids)
        if st.button("Cancel Order"):
            for order in st.session_state.orders:
                if order["order_id"] == selected_order:
                    for item in inventory:
                        if item["name"] == order["item"]:
                            item["stock"] += order.get("stock", 0)
                    order["status"] = "Cancelled"
                    with open(json_file, "w") as f:
                        json.dump(inventory, f, indent=4)
                    st.success("Order Cancelled and Stock Refunded")

with tab5:
    import streamlit as st
    import json
    import os
    from datetime import datetime

    # --- 1. DATA PERSISTENCE LAYER ---
    DB_FILE = "absences.json"

    def load_data():
        if not os.path.exists(DB_FILE):
            return []
        with open(DB_FILE, "r") as f:
            return json.load(f)

    def save_data(data):
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # --- 2. INITIALIZE SESSION STATE ---
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # --- 3. SIDEBAR NAVIGATION ---
    st.sidebar.title("Navigation")
    if st.sidebar.button("📊 Dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()

    if st.sidebar.button("📝 Submit Request"):
        st.session_state.current_page = "Request"
        st.rerun()



    # PAGE 1: DASHBOARD
    if st.session_state.current_page == "Dashboard":
        st.title("Excused Absence Dashboard")
        
        data = load_data()
        
        if not data:
            st.info("No absence requests found.")
        else:
            st.subheader("Existing Requests")
            
            event = st.dataframe(
                data,
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                selected_request = data[selected_index]
                
                st.divider()
                st.subheader(f"Details for Request #{selected_index}")
                
                
                col1, col2 = st.columns(2)
                col1.metric("Status", selected_request["status"])
                col2.metric("Date", selected_request["absence_date"])
                
                st.write(f"**Student:** {selected_request['student_email']}")
                st.write(f"**Type:** {selected_request['type']}")
                st.info(f"**Reason:** {selected_request['reason']}")

    # PAGE 2: REQUEST FORM
    elif st.session_state.current_page == "Request":
        st.title("Submit Excused Absence")
        
        
        st.info("Note: This form is currently under active development.")

        with st.form("absence_form", clear_on_submit=True):
            email = st.text_input("Student Email", key="input_email")
            absence_date = st.date_input("Select Absence Date", key="input_date")
            excuse_type = st.selectbox(
                "Excuse Type", 
                ["Medical", "University Competitions", "Other"],
                key="input_type"
            )
            reason = st.text_area("Student Explanation / Reason", key="input_reason")
            
            submit_btn = st.form_submit_button("Submit Request")

            if submit_btn:
                if email and reason:
                    
                    new_request = {
                        "status": "Pending",
                        "course_id": "011101",
                        "student_email": email,
                        "absence_date": absence_date.strftime("%Y-%m-%d"),
                        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": excuse_type,
                        "reason": reason,
                        "instructor_note": ""
                    }
                    
                    
                    current_records = load_data()
                    current_records.append(new_request)
                    save_data(current_records)
                    
                    st.success("Request submitted successfully!")
                    
                else:
                    st.error("Please fill in all required fields.")


