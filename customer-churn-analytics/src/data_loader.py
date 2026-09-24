"""
data_loader.py
==============
Loads all four Dataset A CSV files from data/raw/ with enforced dtypes and
returns them as plain pandas DataFrames.  Does NOT modify the raw files.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

# ── Default raw directory (relative to project root) ─────────────────────────
DEFAULT_RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


# ── Per-file dtype specifications ─────────────────────────────────────────────
CUSTOMERS_DTYPES: dict[str, str] = {
    "CustomerID": "int64",
    "customer_type": "str",
}

PURCHASES_DTYPES: dict[str, str] = {
    "InvoiceID": "int64",
    "CustomerID": "int64",
    "product_id": "int64",
    "quantity": "int64",
    # 'date' loaded as str and parsed separately
}

INVOICE_ITEMS_DTYPES: dict[str, str] = {
    "InvoiceID": "int64",
    "product_id": "int64",
    "quantity": "int64",
    "price": "float64",
    "line_total": "float64",
}

PRODUCTS_DTYPES: dict[str, str] = {
    "product_id": "int64",
    "item": "str",
    "category": "str",
    "price": "float64",
}


def _load(path: Path, dtype: dict, label: str) -> pd.DataFrame:
    """Generic loader with logging and basic dtype coercion."""
    log.info("Loading %s from %s", label, path)
    df = pd.read_csv(path, dtype=dtype, low_memory=False)
    log.info("  → %d rows × %d columns", len(df), len(df.columns))
    return df


def load_customers(raw_dir: Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Load customers.csv."""
    return _load(raw_dir / "customers.csv", CUSTOMERS_DTYPES, "customers")


def load_purchases(raw_dir: Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Load purchases.csv and parse the 'date' column to datetime."""
    df = _load(raw_dir / "purchases.csv", PURCHASES_DTYPES, "purchases")
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    n_bad = df["date"].isna().sum()
    if n_bad:
        log.warning("  purchases.date: %d values failed to parse", n_bad)
    else:
        log.info("  purchases.date parsed OK  (range: %s – %s)",
                 df["date"].min().date(), df["date"].max().date())
    return df


def load_invoice_items(raw_dir: Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Load invoice_items.csv."""
    return _load(raw_dir / "invoice_items.csv", INVOICE_ITEMS_DTYPES, "invoice_items")


def load_products(raw_dir: Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Load products.csv."""
    return _load(raw_dir / "products.csv", PRODUCTS_DTYPES, "products")


def load_all(raw_dir: Path = DEFAULT_RAW_DIR) -> dict[str, pd.DataFrame]:
    """
    Load all four Dataset A files.

    Returns
    -------
    dict with keys: 'customers', 'purchases', 'invoice_items', 'products'
    """
    return {
        "customers":     load_customers(raw_dir),
        "purchases":     load_purchases(raw_dir),
        "invoice_items": load_invoice_items(raw_dir),
        "products":      load_products(raw_dir),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    frames = load_all()
    for name, df in frames.items():
        print(f"\n{name}: {df.shape}  columns={list(df.columns)}")
        print(df.dtypes.to_string())
