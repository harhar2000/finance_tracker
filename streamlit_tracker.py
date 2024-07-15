import pandas as pd
import csv
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import streamlit as st

from data_entry import get_amount, get_category, get_date, get_description

class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialise_csv(cls):
        try:
            df = pd.read_csv(cls.CSV_FILE)
            if len(df.columns) != len(cls.COLUMNS):
                raise ValueError("CSV file has incorrect format")
        except (FileNotFoundError, pd.errors.ParserError, ValueError):
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)
    
    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description
        }
        df = pd.read_csv(cls.CSV_FILE)
        new_entry_df = pd.DataFrame([new_entry])
        df = pd.concat([df, new_entry_df], ignore_index=True)
        df["date"] = pd.to_datetime(df["date"], format=cls.FORMAT)
        df = df.sort_values(by="date")
        df["date"] = df["date"].dt.strftime(cls.FORMAT)
        df.to_csv(cls.CSV_FILE, index=False)
        st.success("Entry added and data sorted by date")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=cls.FORMAT)
        start_date = datetime.strptime(start_date, cls.FORMAT)
        end_date = datetime.strptime(end_date, cls.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            st.warning("No transactions found in the given date range.")
        else:
            st.write(f"\nTransactions from {start_date.strftime(cls.FORMAT)} to {end_date.strftime(cls.FORMAT)}")
            st.dataframe(filtered_df)
            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()
            st.write("\nSummary:")
            st.write(f"Total Income: £{total_income:.2f}")
            st.write(f"Total Expense: £{total_expense:.2f}")
            st.write(f"Net Savings: £{(total_income - total_expense):.2f}")

        return filtered_df

def plot_transactions(df):
    df.set_index("date", inplace=True)
    all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')

    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum()
        .reindex(all_dates, fill_value=0)
    )
    expense_df = (
        df[df["category"] == "Expense"]
        .resample("D")
        .sum()
        .reindex(all_dates, fill_value=0)
    )

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses over Time")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.gcf().autofmt_xdate()
    st.pyplot(plt)

def main():
    st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")
    st.markdown("## 💰 Finance Tracker")
    st.markdown("###   by [harhar2000](https://github.com/harhar2000)")
    st.sidebar.title("Options")

    option = st.sidebar.selectbox("Select an option", ("Add new transaction", "View transactions and summary"))

    CSV.initialise_csv()

    if option == "Add new transaction":
        st.header("Add a new transaction")
        date = st.text_input("Enter date of transaction (dd-mm-yyyy) or leave empty for today's date:", value=datetime.today().strftime(CSV.FORMAT))
        if date:
            date = date
        amount = st.number_input("Enter the amount:", min_value=0.0, format="%.2f")
        category = st.selectbox("Select category:", ["Income", "Expense"])
        description = st.text_input("Enter description (optional):")
        if st.button("Add Transaction"):
            CSV.add_entry(date, amount, category, description)

    elif option == "View transactions and summary":
        st.header("View transactions and summary within date range")
        start_date = st.text_input("Enter start date (dd-mm-yyyy):")
        end_date = st.text_input("Enter end date (dd-mm-yyyy):")
        if st.button("Get Transactions"):
            df = CSV.get_transactions(start_date, end_date)
            if not df.empty:
                plot_transactions(df)

if __name__ == "__main__":
    main()
