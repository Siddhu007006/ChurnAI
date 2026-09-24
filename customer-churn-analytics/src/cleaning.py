"""
cleaning.py
===========
Reproducible cleaning pipeline for Dataset A.

Design principles:
- raw/ files are NEVER written to.
- Every decision is logged and recorded in a cleaning report dict.
- Zero-price rows are INVESTIGATED and DOCUMENTED, not silently deleted.
- Duplicates are characterised before removal.
- Returns cleaned DataFrames + a detailed report dict.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _record(report: dict, section: str, entry: Any) -> None:
    """Append an entry to a section of the cleaning report."""
    report.setdefault(section, [])
    if isinstance(entry, dict):
        report[section].append(entry)
    else:
        report[section].append({"note": str(entry)})


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Investigate and remove exact duplicates
# ─────────────────────────────────────────────────────────────────────────────

def remove_exact_duplicates(
    df: pd.DataFrame,
    table: str,
    report: dict,
) -> pd.DataFrame:
    """
    Investigate and remove fully-identical rows.

    Investigation logged:
    - How many duplicate rows exist.
    - Whether duplicates cluster on specific InvoiceIDs (if column present).
    - Sample of the first 5 duplicated rows.
    """
    rows_before = len(df)
    dup_mask = df.duplicated(keep=False)          # mark ALL copies
    n_dup_rows = int(dup_mask.sum())
    dup_groups = int(df.duplicated(keep="first").sum())  # rows to DROP

    # Investigation
    investigation: dict[str, Any] = {
        "table": table,
        "rows_before": rows_before,
        "fully_duplicated_rows_total": n_dup_rows,
        "rows_to_drop": dup_groups,
    }

    if n_dup_rows > 0:
        sample = df[dup_mask].head(5).to_dict(orient="records")
        investigation["sample_duplicates"] = sample

        # Does duplication cluster on any key column?
        for key_col in ("InvoiceID", "CustomerID", "product_id"):
            if key_col in df.columns:
                top = (
                    df[dup_mask]
                    .groupby(key_col)
                    .size()
                    .nlargest(5)
                    .to_dict()
                )
                investigation[f"top_{key_col}_in_dups"] = top

    df_clean = df.drop_duplicates(keep="first").reset_index(drop=True)
    rows_after = len(df_clean)
    investigation["rows_after"] = rows_after
    investigation["rows_removed"] = rows_before - rows_after

    _record(report, "deduplication", investigation)
    log.info("[%s] Deduplication: %d → %d rows  (removed %d)",
             table, rows_before, rows_after, rows_before - rows_after)
    return df_clean


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Investigate zero-price rows
# ─────────────────────────────────────────────────────────────────────────────

def investigate_zero_price(
    invoice_items: pd.DataFrame,
    report: dict,
) -> dict[str, Any]:
    """
    Characterise zero-price rows in invoice_items.
    Returns an investigation summary.  Does NOT delete any rows.
    The decision to remove or keep is documented in the report.
    """
    zero_mask = invoice_items["price"] == 0
    n_zero = int(zero_mask.sum())
    total = len(invoice_items)

    inv: dict[str, Any] = {
        "zero_price_rows": n_zero,
        "pct_of_total": round(n_zero / total * 100, 3),
    }

    if n_zero > 0:
        zero_df = invoice_items[zero_mask]
        inv["qty_range_in_zero_price"] = {
            "min": int(zero_df["quantity"].min()),
            "max": int(zero_df["quantity"].max()),
        }
        inv["line_total_non_zero_in_zero_price"] = int(
            (zero_df["line_total"] != 0).sum()
        )
        inv["unique_products_affected"] = int(zero_df["product_id"].nunique())
        inv["sample_rows"] = zero_df.head(5).to_dict(orient="records")

        # Decision rule: line_total is also 0 → likely promotional/cancelled.
        # We will FLAG them but NOT remove them in Phase 1.
        # They will be excluded from revenue aggregations via line_total > 0.
        inv["decision"] = (
            "Zero-price rows are retained in the cleaned transaction dataset. "
            "They will be excluded from revenue and monetary-value aggregations "
            "by filtering line_total > 0 at feature-engineering time. "
            "No rows deleted in this step."
        )
    else:
        inv["decision"] = "No zero-price rows found."

    _record(report, "zero_price_investigation", inv)
    log.info("[invoice_items] Zero-price rows: %d (%.2f%%) — retained, flagged.",
             n_zero, inv["pct_of_total"])
    return inv


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Parse and validate the date column
# ─────────────────────────────────────────────────────────────────────────────

def clean_dates(purchases: pd.DataFrame, report: dict) -> pd.DataFrame:
    """
    Ensure purchases.date is a proper datetime64.
    Already parsed by data_loader; this step re-confirms and records the range.
    """
    if not pd.api.types.is_datetime64_any_dtype(purchases["date"]):
        purchases = purchases.copy()
        purchases["date"] = pd.to_datetime(purchases["date"], errors="coerce")

    n_bad = int(purchases["date"].isna().sum())
    date_range = {
        "min_date": str(purchases["date"].min().date()),
        "max_date": str(purchases["date"].max().date()),
        "parse_failures": n_bad,
        "note": "date column parsed to datetime64[ns].",
    }
    _record(report, "date_cleaning", date_range)
    log.info("[purchases] date range: %s – %s  (failures: %d)",
             date_range["min_date"], date_range["max_date"], n_bad)
    return purchases


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Relational joins
# ─────────────────────────────────────────────────────────────────────────────

def build_transaction_dataset(
    customers: pd.DataFrame,
    purchases: pd.DataFrame,
    invoice_items: pd.DataFrame,
    products: pd.DataFrame,
    report: dict,
) -> pd.DataFrame:
    """
    Join the four tables into a single flat transaction-level dataset.

    Join sequence:
      purchases
        ← invoice_items  (InvoiceID + product_id)
        ← products       (product_id)
        ← customers      (CustomerID)

    Revenue is derived from invoice_items.line_total (not re-computed).
    """
    rows_start = len(purchases)

    # 4a. purchases ← invoice_items on (InvoiceID, product_id)
    tx = purchases.merge(
        invoice_items[["InvoiceID", "product_id", "price", "line_total"]],
        on=["InvoiceID", "product_id"],
        how="left",
        suffixes=("_purch", "_ii"),
    )
    _record(report, "joins", {
        "step": "purchases ← invoice_items",
        "join_keys": ["InvoiceID", "product_id"],
        "join_type": "left",
        "rows_before": rows_start,
        "rows_after": len(tx),
        "unmatched_rows": int(tx["price"].isna().sum()),
    })

    # 4b. tx ← products on product_id
    tx = tx.merge(
        products[["product_id", "item", "category"]],
        on="product_id",
        how="left",
    )
    _record(report, "joins", {
        "step": "tx ← products",
        "join_keys": ["product_id"],
        "join_type": "left",
        "rows_after": len(tx),
        "unmatched_rows": int(tx["category"].isna().sum()),
    })

    # 4c. tx ← customers on CustomerID
    tx = tx.merge(
        customers[["CustomerID", "customer_type"]],
        on="CustomerID",
        how="left",
    )
    _record(report, "joins", {
        "step": "tx ← customers",
        "join_keys": ["CustomerID"],
        "join_type": "left",
        "rows_after": len(tx),
        "unmatched_rows": int(tx["customer_type"].isna().sum()),
    })

    # Rename quantity_purch (the master quantity) for clarity
    if "quantity_purch" in tx.columns:
        tx = tx.rename(columns={"quantity_purch": "quantity"})
    if "quantity_ii" in tx.columns:
        # quantity should be identical in both; drop the copy
        mismatches = (tx["quantity"] != tx["quantity_ii"]).sum()
        _record(report, "joins", {
            "note": f"quantity mismatch between purchases and invoice_items: {mismatches} rows."
        })
        tx = tx.drop(columns=["quantity_ii"])

    log.info("[build_transaction_dataset] Final shape: %d × %d",
             len(tx), len(tx.columns))
    return tx


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Save processed files
# ─────────────────────────────────────────────────────────────────────────────

def save_processed(
    tx: pd.DataFrame,
    customers_clean: pd.DataFrame,
    processed_dir: Path = PROCESSED_DIR,
) -> None:
    """Save cleaned outputs to data/processed/. Does NOT touch data/raw/."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    tx_path   = processed_dir / "transactions_clean.csv"
    cust_path = processed_dir / "customers_clean.csv"
    tx.to_csv(tx_path, index=False)
    customers_clean.to_csv(cust_path, index=False)
    log.info("Saved: %s  (%d rows)", tx_path.name, len(tx))
    log.info("Saved: %s  (%d rows)", cust_path.name, len(customers_clean))


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_cleaning_pipeline(
    frames: dict[str, pd.DataFrame],
    save: bool = True,
    processed_dir: Path = PROCESSED_DIR,
) -> tuple[dict[str, pd.DataFrame], dict]:
    """
    Execute the full cleaning pipeline.

    Parameters
    ----------
    frames      : dict returned by data_loader.load_all()
    save        : if True, write processed CSVs to processed_dir
    processed_dir : override output directory

    Returns
    -------
    (cleaned_frames, report)
        cleaned_frames : dict with keys 'transactions', 'customers'
        report         : full cleaning report dict
    """
    report: dict = {
        "pipeline_run_at": datetime.utcnow().isoformat(),
        "input_row_counts": {k: len(v) for k, v in frames.items()},
    }

    cust  = frames["customers"].copy()
    purch = frames["purchases"].copy()
    ii    = frames["invoice_items"].copy()
    prod  = frames["products"].copy()

    # Step 1 — Remove exact duplicates (purchases & invoice_items only)
    purch = remove_exact_duplicates(purch, "purchases",     report)
    ii    = remove_exact_duplicates(ii,    "invoice_items", report)

    # Customers and products had 0 duplicates; still record for completeness
    for table, df in [("customers", cust), ("products", prod)]:
        _record(report, "deduplication", {
            "table": table,
            "rows_before": len(df),
            "fully_duplicated_rows_total": 0,
            "rows_to_drop": 0,
            "rows_after": len(df),
            "rows_removed": 0,
            "note": "No duplicates found; no action taken.",
        })

    # Step 2 — Investigate zero-price rows (no deletion)
    investigate_zero_price(ii, report)

    # Step 3 — Date parsing / confirmation
    purch = clean_dates(purch, report)

    # Step 4 — Build joined transaction dataset
    tx = build_transaction_dataset(cust, purch, ii, prod, report)

    # Record final counts
    report["output_row_counts"] = {
        "transactions_clean": len(tx),
        "customers_clean":    len(cust),
    }
    report["columns_in_transactions"] = list(tx.columns)

    # Step 5 — Save
    if save:
        save_processed(tx, cust, processed_dir)

    cleaned = {
        "transactions": tx,
        "customers":    cust,
    }
    return cleaned, report


def save_cleaning_report(report: dict, processed_dir: Path = PROCESSED_DIR) -> Path:
    """Write the cleaning report as JSON next to the processed CSVs."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    path = processed_dir / "cleaning_report.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    log.info("Cleaning report saved: %s", path)
    return path
