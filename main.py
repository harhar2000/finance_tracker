import pandas as pd
import csv 
from datetime import datetime

class CSV:
    CSV_FILE = "finance_data.csv"

    @classmethod        # Gives access to class but not its respective instance
    def initialise_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["date", "amount", "category", "description"])
            df.to_csv(cls.CSV_FILE, index=False)
            