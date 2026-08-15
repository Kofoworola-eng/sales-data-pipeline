"""
clean_sales_data.py

Cleans raw sales order data for downstream analysis.

Handles:
    - Missing customer names
    - Missing quantity values
    - Inconsistent region name casing/abbreviations
    - Mixed date formats
    - Missing order dates
    - Calculates total order value (quantity * unit_price)

Usage:
    python clean_sales_data.py
"""

import pandas as pd
from pathlib import Path

RAW_DATA_PATH = Path("data/raw_sales_data.csv")
CLEAN_DATA_PATH = Path("data/cleaned_sales_data.csv")

# Maps messy region entries to a single standard form
REGION_MAP = {
    "lagos": "Lagos",
    "abuja": "Abuja",
    "kano": "Kano",
    "ph": "Port Harcourt",
    "port harcourt": "Port Harcourt",
}


def load_data(path: Path) -> pd.DataFrame:
    """Load the raw CSV into a DataFrame."""
    if not path.exists():
        raise FileNotFoundError(f"Could not find raw data file at {path}")
    return pd.read_csv(path)


def clean_customer_names(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing customer names and standardize capitalization."""
    df["customer_name"] = df["customer_name"].fillna("Unknown Customer")
    df["customer_name"] = df["customer_name"].str.strip().str.title()
    return df


def clean_quantity(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing quantities with 1, assuming a single-item order as the safest default."""
    df["quantity"] = df["quantity"].fillna(1).astype(int)
    return df


def clean_region(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize region names using the region map, case-insensitively."""
    df["region"] = df["region"].str.strip().str.lower().map(REGION_MAP)
    return df


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse mixed date formats into a single standard format, dropping rows with no date at all."""
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")
    before = len(df)
    df = df.dropna(subset=["order_date"]).copy()
    dropped = before - len(df)
    if dropped:
        print(f"Dropped {dropped} row(s) with missing or unparseable order dates.")
    return df


def add_total_value(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total order value as quantity * unit_price."""
    df["total_value"] = (df["quantity"] * df["unit_price"]).round(2)
    return df


def clean_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full cleaning pipeline in sequence."""
    df = clean_customer_names(df)
    df = clean_quantity(df)
    df = clean_region(df)
    df = clean_dates(df)
    df = add_total_value(df)
    return df


def main():
    print(f"Loading raw data from {RAW_DATA_PATH}...")
    df = load_data(RAW_DATA_PATH)
    print(f"Loaded {len(df)} rows.")

    print("Running cleaning pipeline...")
    cleaned_df = clean_pipeline(df)

    CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(CLEAN_DATA_PATH, index=False)
    print(f"Cleaned data saved to {CLEAN_DATA_PATH} ({len(cleaned_df)} rows).")


if __name__ == "__main__":
    main()
