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

tab1, tab2, tab3, tab4 = st.tabs([
    "Place Order",
    "View Inventory",
    "Restock",
    "Manage Orders"
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