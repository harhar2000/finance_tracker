import pandas as pd
import csv 
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description
import matplotlib.pyplot as plt

class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = "date", "amount", "category", "description"
    FORMAT = "%d-%m-%Y"

    @classmethod        # Gives access to class but not its respective instance
    def initialise_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
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
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)                              # Read df
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)  # convert date column to datetime objects
        start_date = datetime.strptime(start_date, CSV.FORMAT)      # convert start and end date to datetime objects
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)       # use mask to filter rows in df
        filtered_df = df.loc[mask]

        if filtered_df.empty: 
            print("No transactions found in given date range.")
        else:
            print(f"\nTransactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}")

            print(filtered_df.to_string(index=False, formatters={"date": lambda x:x.strftime(CSV.FORMAT)}))

            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()
            print("\nSummary:")
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expense: ${total_expense:.2f}")
            print(f"Net Savings: ${(total_income - total_expense):.2f}")

        return filtered_df


def add():
    CSV.initialise_csv()
    date = get_date("Enter date of transaction (dd-mm-yyyy) or enter for today's date: ", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)

def plot_transactions(df):
    df.set_index("date", inplace=True)
    all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')

    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum()                              # Filters "category" == "income" rows, resample data daily and totals value
        .reindex(all_dates, fill_value=0)    # reindexes to match og DF index, fill missing values w/ 0
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
    plt.xticks(rotation=45)  # Rotate x-axis labels
    plt.gcf().autofmt_xdate()  # Automatic date formatting
    plt.show()

def main():
    while True:
        print("\n1. Add new transaction")
        print("2. View transactions and summary within date range")
        print("3. Exit")
        choice = input("Enter (1-3): ")

        if choice == "1":
            add()
        elif choice == "2":
            start_date = get_date("Enter start date (dd-mm-yyyy): ")
            end_date = get_date("Enter end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date, end_date)
            if input("Do you want to see plot (y/n): ").lower() == "y":
                plot_transactions(df)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Enter 1, 2 or 3. ")

if __name__ == "__main__":
    main()