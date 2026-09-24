"""
validation.py
=============
Schema and referential-integrity validation for Dataset A.
All functions return a dict with at least:
    { 'passed': bool, 'details': str | dict }
They raise no exceptions — callers decide how to handle failures.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

# ── Expected schemas ──────────────────────────────────────────────────────────
EXPECTED_SCHEMAS: dict[str, dict[str, type]] = {
    "customers": {
        "CustomerID": "int64",
        "customer_type": "object",
    },
    "purchases": {
        "InvoiceID": "int64",
        "date": "datetime64[ns]",
        "CustomerID": "int64",
        "product_id": "int64",
        "quantity": "int64",
    },
    "invoice_items": {
        "InvoiceID": "int64",
        "product_id": "int64",
        "quantity": "int64",
        "price": "float64",
        "line_total": "float64",
    },
    "products": {
        "product_id": "int64",
        "item": "object",
        "category": "object",
        "price": "float64",
    },
}


# ── 1. Schema validation ──────────────────────────────────────────────────────
def validate_schema(df: pd.DataFrame, table: str) -> dict[str, Any]:
    """Check that all expected columns are present with the right dtypes."""
    expected = EXPECTED_SCHEMAS.get(table, {})
    missing_cols: list[str] = []
    wrong_dtype: dict[str, str] = {}

    for col, exp_dtype in expected.items():
        if col not in df.columns:
            missing_cols.append(col)
        else:
            actual = str(df[col].dtype)
            if not actual.startswith(exp_dtype.rstrip("0123456789[]ns")):
                wrong_dtype[col] = f"expected≈{exp_dtype}, got {actual}"

    passed = (not missing_cols) and (not wrong_dtype)
    result = {
        "table": table,
        "passed": passed,
        "missing_columns": missing_cols,
        "wrong_dtypes": wrong_dtype,
    }
    if passed:
        log.info("Schema OK: %s", table)
    else:
        log.warning("Schema FAIL: %s  missing=%s  dtype_mismatch=%s",
                    table, missing_cols, wrong_dtype)
    return result


# ── 2. Null checks ────────────────────────────────────────────────────────────
def validate_nulls(df: pd.DataFrame, table: str) -> dict[str, Any]:
    """Return a per-column null count for every column in the dataframe."""
    null_counts = df.isna().sum()
    total_nulls = int(null_counts.sum())
    result = {
        "table": table,
        "passed": total_nulls == 0,
        "total_nulls": total_nulls,
        "by_column": null_counts[null_counts > 0].to_dict(),
    }
    if result["passed"]:
        log.info("Null check OK: %s", table)
    else:
        log.warning("Null check FAIL: %s  %s", table, result["by_column"])
    return result


# ── 3. Duplicate-row checks ───────────────────────────────────────────────────
def validate_duplicates(df: pd.DataFrame, table: str,
                         subset: list[str] | None = None) -> dict[str, Any]:
    """
    Count fully-duplicated rows (all columns) and, optionally,
    key-subset duplicates.
    """
    full_dups = int(df.duplicated().sum())
    key_dups: int | None = None
    if subset:
        key_dups = int(df.duplicated(subset=subset).sum())

    result = {
        "table": table,
        "passed": full_dups == 0,
        "full_duplicate_rows": full_dups,
        "key_subset": subset,
        "key_duplicate_rows": key_dups,
    }
    if result["passed"]:
        log.info("Duplicate check OK: %s (0 full duplicates)", table)
    else:
        log.warning("Duplicate check FAIL: %s  full_dups=%d  key_dups=%s",
                    table, full_dups, key_dups)
    return result


# ── 4. Foreign-key validation ─────────────────────────────────────────────────
def validate_foreign_key(
    child_df: pd.DataFrame,
    child_col: str,
    parent_df: pd.DataFrame,
    parent_col: str,
    child_label: str,
    parent_label: str,
) -> dict[str, Any]:
    """
    Check that every value in child_df[child_col] exists in
    parent_df[parent_col].
    """
    parent_keys = set(parent_df[parent_col].dropna().unique())
    orphan_mask = ~child_df[child_col].isin(parent_keys)
    n_orphans = int(orphan_mask.sum())
    orphan_vals = child_df.loc[orphan_mask, child_col].unique().tolist()[:20]

    result = {
        "relationship": f"{child_label}.{child_col} → {parent_label}.{parent_col}",
        "passed": n_orphans == 0,
        "orphan_rows": n_orphans,
        "sample_orphan_values": orphan_vals,
    }
    if result["passed"]:
        log.info("FK OK: %s", result["relationship"])
    else:
        log.warning("FK FAIL: %s  orphan_rows=%d  samples=%s",
                    result["relationship"], n_orphans, orphan_vals[:5])
    return result


# ── 5. Value-range checks ─────────────────────────────────────────────────────
def validate_non_negative(df: pd.DataFrame, table: str,
                            cols: list[str]) -> dict[str, Any]:
    """Assert that numeric columns contain no negative values."""
    violations: dict[str, int] = {}
    for col in cols:
        if col in df.columns:
            n_neg = int((df[col] < 0).sum())
            if n_neg:
                violations[col] = n_neg

    result = {
        "table": table,
        "passed": len(violations) == 0,
        "negative_value_counts": violations,
    }
    if result["passed"]:
        log.info("Non-negative check OK: %s %s", table, cols)
    else:
        log.warning("Non-negative FAIL: %s  %s", table, violations)
    return result


def validate_zero_price(df: pd.DataFrame, table: str,
                         price_col: str = "price") -> dict[str, Any]:
    """Identify zero-price rows — documented as an investigation step, not deleted."""
    if price_col not in df.columns:
        return {"table": table, "passed": True, "zero_price_rows": 0,
                "note": f"Column {price_col!r} not found — skipped."}
    n_zero = int((df[price_col] == 0).sum())
    result = {
        "table": table,
        "passed": n_zero == 0,
        "zero_price_rows": n_zero,
        "pct_of_total": round(n_zero / len(df) * 100, 3) if len(df) else 0,
        "note": (
            "Zero-price rows detected. Investigate before deciding to remove."
            if n_zero else "No zero-price rows."
        ),
    }
    if n_zero:
        log.warning("Zero-price rows in %s.%s: %d (%.2f%%)",
                    table, price_col, n_zero, result["pct_of_total"])
    else:
        log.info("Zero-price check OK: %s.%s", table, price_col)
    return result


# ── 6. Invoice row-count consistency ─────────────────────────────────────────
def validate_invoice_consistency(
    purchases: pd.DataFrame,
    invoice_items: pd.DataFrame,
) -> dict[str, Any]:
    """
    Check that each InvoiceID appears the same number of times in both
    purchases and invoice_items (before deduplication).
    """
    pu = purchases.groupby("InvoiceID").size().rename("purchases_rows")
    ii = invoice_items.groupby("InvoiceID").size().rename("invoice_items_rows")
    merged = pu.to_frame().join(ii, how="outer")
    mismatch = merged[merged["purchases_rows"] != merged["invoice_items_rows"]]

    result = {
        "passed": len(mismatch) == 0,
        "mismatched_invoices": len(mismatch),
        "sample_mismatches": mismatch.head(5).to_dict() if len(mismatch) else {},
    }
    if result["passed"]:
        log.info("Invoice consistency OK: row counts match across both files.")
    else:
        log.warning("Invoice consistency FAIL: %d invoices have mismatched row counts.",
                    len(mismatch))
    return result


# ── 7. Run all validations at once ────────────────────────────────────────────
def run_all_validations(frames: dict[str, pd.DataFrame]) -> dict[str, list[dict]]:
    """
    Run every validation check against the loaded DataFrames.

    Parameters
    ----------
    frames : dict returned by data_loader.load_all()

    Returns
    -------
    dict mapping table name → list of result dicts
    """
    cust = frames["customers"]
    purch = frames["purchases"]
    ii = frames["invoice_items"]
    prod = frames["products"]

    results: dict[str, list[dict]] = {}

    # Schema
    results["schema"] = [
        validate_schema(cust,  "customers"),
        validate_schema(purch, "purchases"),
        validate_schema(ii,    "invoice_items"),
        validate_schema(prod,  "products"),
    ]

    # Nulls
    results["nulls"] = [
        validate_nulls(cust,  "customers"),
        validate_nulls(purch, "purchases"),
        validate_nulls(ii,    "invoice_items"),
        validate_nulls(prod,  "products"),
    ]

    # Duplicates
    results["duplicates"] = [
        validate_duplicates(cust,  "customers"),
        validate_duplicates(purch, "purchases",
                            subset=["InvoiceID", "CustomerID", "product_id",
                                    "date", "quantity"]),
        validate_duplicates(ii, "invoice_items",
                            subset=["InvoiceID", "product_id",
                                    "quantity", "price", "line_total"]),
        validate_duplicates(prod, "products"),
    ]

    # Foreign keys
    results["foreign_keys"] = [
        validate_foreign_key(purch, "CustomerID", cust,  "CustomerID",
                             "purchases", "customers"),
        validate_foreign_key(purch, "InvoiceID",  ii,   "InvoiceID",
                             "purchases", "invoice_items"),
        validate_foreign_key(purch, "product_id", prod, "product_id",
                             "purchases", "products"),
        validate_foreign_key(ii,   "product_id",  prod, "product_id",
                             "invoice_items", "products"),
    ]

    # Non-negative numerics
    results["non_negative"] = [
        validate_non_negative(ii,   "invoice_items",
                              ["quantity", "price", "line_total"]),
        validate_non_negative(purch, "purchases", ["quantity"]),
        validate_non_negative(prod,  "products",  ["price"]),
    ]

    # Zero-price investigation
    results["zero_price"] = [
        validate_zero_price(ii,   "invoice_items", "price"),
        validate_zero_price(prod, "products",       "price"),
    ]

    # Invoice cross-file consistency
    results["invoice_consistency"] = [
        validate_invoice_consistency(purch, ii),
    ]

    return results
