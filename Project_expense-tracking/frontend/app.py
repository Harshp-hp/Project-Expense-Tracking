import pandas as pd
import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

st.title("Expense Management System")

tab1, tab2, tab3 = st.tabs(["Add/Update", "Analytics by Category","Monthly Analytics"])

with tab1:
    selected_date =st.date_input("Enter Date", datetime(2024,8,1), label_visibility="collapsed")
    response = requests.get(f"{API_URL}/expenses/{selected_date}")
    if response.status_code == 200:
        existing_expenses = response.json()
        #st.write(existing_expenses)
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    categories = ['Rent','Food','Shopping','Entertainment','Other']

    with st.form(key="expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text("Amount")
        with col2:
            st.text("Category")
        with col3:
            st.text("Notes")
        expenses =[]
        for i in range(5):
            if i < len(existing_expenses):
                amount = existing_expenses[i]['amount']
                category = existing_expenses[i]['category']
                notes = existing_expenses[i]['notes']
            else:
                amount = 0.0
                category = "Shopping"
                notes = ""

            col1, col2, col3 = st.columns(3)
            with col1:
                amount_input = st.number_input(
                    "Amount", min_value=0.0, step=1.0,
                    value=float(amount),
                    key=f"amount_{i}", label_visibility="collapsed")

            with col2:
                category_input = st.selectbox("Category",
                             options=categories,
                             index=categories.index(category), key=f"category_{i}", label_visibility="collapsed")
            with col3:
                notes_input = st.text_input("", value=notes ,key=f"notes_{i}", label_visibility="collapsed")

            expenses.append({
                'amount': amount_input,
                'category': category_input,
                'notes': notes_input
            })
        submit_button = st.form_submit_button()
        if submit_button:
            filtered_expenses = [expense for expense in expenses if expense['amount']>0]

            response = requests.post(f"{API_URL}/expenses/{selected_date}", json=filtered_expenses)
            if response.status_code == 200:
                st.success("Expenses updated successfully")
            else:
                st.error("Failed to update expenses.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime(2024,8,1))
    with col2:
        end_date = st.date_input("End Date", datetime(2024,8,6))
    if st.button("Get Analytics"):
        payload= {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
        }

        response = requests.post(f"{API_URL}/analytics/", json=payload)
        if response.status_code == 200:
            data_json= response.json()
            data = {
                "Category": list(data_json.keys()),
                "Total": [data_json[category]["total"] for category in data_json],
                "Percentage": [data_json[category]["percentage"] for category in data_json]
            }
            df = pd.DataFrame(data)
            df_sorted = df.sort_values(by="Percentage", ascending=False)

            st.title("Expense Breakdown By Category")

            st.bar_chart(data = df_sorted.set_index('Category')['Percentage'], use_container_width=True)
            df_sorted["Total"] = df_sorted["Total"].map("{:.2f}".format)
            df_sorted["Percentage"] = df_sorted["Percentage"].map("{:.2f}".format)
            st.dataframe(df_sorted)
        else:
            st.error(f"API Error {response.status_code}: {response.text}")

with tab3:
    if st.button("Get Monthly Analytics"):
        response = requests.post(f"{API_URL}/analytics_month/")
        if response.status_code == 200:
            data_json = response.json()

            data = {
                "Month": list(data_json.keys()),
                "Total": [data_json[month]["total"] for month in data_json]
            }
            df = pd.DataFrame(data)
            df_sorted = df.sort_values(by="Total", ascending=False)

            st.title("Expense Breakdown By Monthly")

            st.bar_chart(data = df_sorted.set_index('Month')['Total'],  use_container_width=True)
            df_sorted["Total"] = df_sorted["Total"].map("{:.2f}".format)

            st.dataframe(df_sorted)
        else:
            st.error(f"API Error {response.status_code}: {response.text}")