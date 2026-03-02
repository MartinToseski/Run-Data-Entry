"""
Storage layer.

Handles CSV persistence of dataset.
"""

import os
import pandas as pd
from typing import Dict
from .schema import FINAL_SCHEMA


DATA_PATH = "data/running_dataset.csv"


def create_csv_if_missing() -> None:
    """
    Create empty CSV with header if not exists.
    """
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        df = pd.DataFrame(columns=FINAL_SCHEMA)
        df.to_csv(DATA_PATH, index=False)


def save_row(row: Dict) -> None:
    """
    Save a single aggregated row to CSV.

    Avoids duplicate date entries.
    """
    create_csv_if_missing()
    df = pd.read_csv(DATA_PATH)

    df = df[df["date"] != row["date"]]

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df = df.sort_values("date")
    df.to_csv(DATA_PATH, index=False)
