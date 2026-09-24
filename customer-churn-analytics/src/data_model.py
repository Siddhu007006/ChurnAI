"""
data_model.py
=============
Builds the four normalised analytical tables from the raw Dataset A files.

Design rules (from JOIN_GRAIN_INVESTIGATION.md):
  - purchases.csv  → customer/date context per invoice (no price column)
  - invoice_items.csv → authoritative line-item revenue (price-aware)
  - InvoiceID is the ONLY safe bridge between the two tables
  - NEVER join purchases ↔ invoice_items at row level
  - Revenue ALWAYS derived from invoice_items.line_total

Tables produced:
  dim_invoices        one row per InvoiceID
  fact_invoice_items  one row per legitimate line-item record
  dim_customers       one row per CustomerID
  dim_products        one row per product_id

All outputs written to data/processed/.
data/raw/ is never touched.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

RAW_DIR  = Path(__file__).resolve().parent.parent / "data" / "raw"
PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_raw(filename: str, dtype: dict | None = None) -> pd.DataFrame:
    path = RAW_DIR / filename
    df = pd.read_csv(path, dtype=dtype, low_memory=False)
    log.info("Loaded %s: %d rows × %d cols", filename, len(df), len(df.columns))
    return df


def _save(df: pd.DataFrame, filename: str) -> Path:
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    path = PROC_DIR / filename
    df.to_csv(path, index=False)
    log.info("Saved %s: %d rows × %d cols", filename, len(df), len(df.columns))
    return path


# ─────────────────────────────────────────────────────────────────────────────
# Step 0 — Load and deduplicate raw sources (read-only)
# ─────────────────────────────────────────────────────────────────────────────

def _load_deduped_sources() -> tuple[pd.DataFrame, pd.DataFrame,
                                     pd.DataFrame, pd.DataFrame]:
    """
    Load the four raw CSVs, apply exact-row deduplication, return clean copies.
    Raw files are never written to.
    """
    cust_raw  = _load_raw("customers.csv",     dtype={"CustomerID": "int64"})
    purch_raw = _load_raw("purchases.csv",     dtype={"InvoiceID": "int64",
                                                       "CustomerID": "int64",
                                                       "product_id": "int64",
                                                       "quantity": "int64"})
    ii_raw    = _load_raw("invoice_items.csv", dtype={"InvoiceID": "int64",
                                                       "product_id": "int64",
                                                       "quantity": "int64",
                                                       "price": "float64",
                                                       "line_total": "float64"})
    prod_raw  = _load_raw("products.csv",      dtype={"product_id": "int64",
                                                       "price": "float64"})

    purch_raw["date"] = pd.to_datetime(purch_raw["date"], errors="coerce")

    def dedup(df: pd.DataFrame, label: str) -> pd.DataFrame:
        before = len(df)
        out    = df.drop_duplicates().reset_index(drop=True)
        log.info("Dedup %s: %d → %d rows (removed %d)",
                 label, before, len(out), before - len(out))
        return out

    return (
        dedup(cust_raw,  "customers"),
        dedup(purch_raw, "purchases"),
        dedup(ii_raw,    "invoice_items"),
        dedup(prod_raw,  "products"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Build dim_invoices
# ─────────────────────────────────────────────────────────────────────────────

def build_dim_invoices(
    purch: pd.DataFrame,
    ii: pd.DataFrame,
    report: dict,
) -> pd.DataFrame:
    """
    One row per InvoiceID.

    Strategy (no row-level join):
      a. Verify purchases uniqueness constraints (1 customer / 1 date per invoice).
      b. Extract invoice→customer→date mapping by grouping purchases.
      c. Aggregate invoice_items to invoice level (revenue, line count).
      d. Merge the two aggregations on InvoiceID only.
    """
    # ── a. Pre-flight: verify 1 customer and 1 date per invoice ──────────────
    inv_check = (
        purch.groupby("InvoiceID")
             .agg(n_customers=("CustomerID", "nunique"),
                  n_dates=("date", "nunique"))
    )
    multi_cust  = int((inv_check["n_customers"] > 1).sum())
    multi_dates = int((inv_check["n_dates"]     > 1).sum())

    report["dim_invoices_preflight"] = {
        "invoices_with_multiple_customers": multi_cust,
        "invoices_with_multiple_dates":     multi_dates,
        "passed": multi_cust == 0 and multi_dates == 0,
    }
    if multi_cust or multi_dates:
        log.warning("Pre-flight FAILED: multi_cust=%d  multi_dates=%d",
                    multi_cust, multi_dates)
    else:
        log.info("Pre-flight OK: every invoice maps to exactly 1 customer and 1 date.")

    # ── b. Invoice → customer + date mapping (from purchases) ─────────────────
    # Since every invoice has exactly 1 CustomerID and 1 date, first() is safe.
    invoice_map = (
        purch.groupby("InvoiceID")
             .agg(CustomerID=("CustomerID", "first"),
                  date=("date", "first"))
             .reset_index()
    )

    # ── c. Invoice-level revenue from invoice_items (no join to purchases) ────
    invoice_rev = (
        ii.groupby("InvoiceID")
          .agg(invoice_revenue=("line_total", "sum"),
               line_item_count=("line_total", "count"))
          .reset_index()
    )

    # ── d. Merge on InvoiceID only ────────────────────────────────────────────
    dim_inv = invoice_map.merge(invoice_rev, on="InvoiceID", how="left")

    # Invoices in purchases but not in invoice_items (revenue = NaN → 0)
    n_missing_rev = int(dim_inv["invoice_revenue"].isna().sum())
    if n_missing_rev:
        log.warning("%d invoices in purchases have no matching invoice_items rows.",
                    n_missing_rev)
        dim_inv["invoice_revenue"]  = dim_inv["invoice_revenue"].fillna(0.0)
        dim_inv["line_item_count"]  = dim_inv["line_item_count"].fillna(0).astype(int)

    report["dim_invoices_build"] = {
        "rows":                     len(dim_inv),
        "unique_invoice_ids":       int(dim_inv["InvoiceID"].nunique()),
        "unique_customer_ids":      int(dim_inv["CustomerID"].nunique()),
        "invoices_with_no_revenue": n_missing_rev,
        "total_invoice_revenue":    round(float(dim_inv["invoice_revenue"].sum()), 2),
    }
    log.info("dim_invoices: %d rows, %d unique invoices, revenue=£%,.2f",
             len(dim_inv),
             dim_inv["InvoiceID"].nunique(),
             dim_inv["invoice_revenue"].sum())
    return dim_inv


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Build fact_invoice_items
# ─────────────────────────────────────────────────────────────────────────────

def build_fact_invoice_items(
    ii: pd.DataFrame,
    prod: pd.DataFrame,
    report: dict,
) -> pd.DataFrame:
    """
    One row per legitimate invoice line-item record.

    Source: deduplicated invoice_items.
    Adds item name and category from products via product_id.

    Multiple rows for the same (InvoiceID, product_id) are preserved when
    they differ by quantity, price, or line_total — these are legitimate
    split-line or multi-price entries.
    """
    fact = ii.copy()

    # Attach product descriptors (left join — all ii rows preserved)
    fact = fact.merge(
        prod[["product_id", "item", "category"]],
        on="product_id",
        how="left",
    )
    n_unmatched = int(fact["category"].isna().sum())
    if n_unmatched:
        log.warning("%d fact_invoice_items rows have no matching product.", n_unmatched)

    report["fact_invoice_items_build"] = {
        "rows":                   len(fact),
        "unique_invoice_ids":     int(fact["InvoiceID"].nunique()),
        "unique_product_ids":     int(fact["product_id"].nunique()),
        "zero_price_rows":        int((fact["price"] == 0).sum()),
        "unmatched_product_rows": n_unmatched,
        "total_line_total":       round(float(fact["line_total"].sum()), 2),
    }
    log.info("fact_invoice_items: %d rows, revenue=£%,.2f",
             len(fact), fact["line_total"].sum())
    return fact


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Build dim_customers
# ─────────────────────────────────────────────────────────────────────────────

def build_dim_customers(cust: pd.DataFrame, report: dict) -> pd.DataFrame:
    """One row per CustomerID from customers.csv (already clean)."""
    dim_cust = cust[["CustomerID", "customer_type"]].drop_duplicates(
        subset="CustomerID"
    ).reset_index(drop=True)

    report["dim_customers_build"] = {
        "rows":               len(dim_cust),
        "unique_customer_ids": int(dim_cust["CustomerID"].nunique()),
        "customer_type_dist": dim_cust["customer_type"].value_counts().to_dict(),
    }
    log.info("dim_customers: %d rows", len(dim_cust))
    return dim_cust


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Build dim_products
# ─────────────────────────────────────────────────────────────────────────────

def build_dim_products(prod: pd.DataFrame, report: dict) -> pd.DataFrame:
    """One row per product_id from products.csv (already clean)."""
    dim_prod = prod[["product_id", "item", "category", "price"]].drop_duplicates(
        subset="product_id"
    ).reset_index(drop=True)

    report["dim_products_build"] = {
        "rows":              len(dim_prod),
        "unique_product_ids": int(dim_prod["product_id"].nunique()),
        "categories":         int(dim_prod["category"].nunique()),
    }
    log.info("dim_products: %d rows", len(dim_prod))
    return dim_prod


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Integrity tests
# ─────────────────────────────────────────────────────────────────────────────

def run_integrity_checks(
    dim_inv: pd.DataFrame,
    fact_ii: pd.DataFrame,
    dim_cust: pd.DataFrame,
    dim_prod: pd.DataFrame,
    ii_raw_deduped: pd.DataFrame,
) -> dict[str, Any]:
    """
    Run all specified integrity checks.
    Returns a dict of check_name → {passed, detail}.
    """
    checks: dict[str, Any] = {}

    def _check(name: str, passed: bool, detail: Any) -> None:
        checks[name] = {"passed": passed, "detail": detail}
        status = "PASS" if passed else "FAIL"
        log.info("[%s] %s — %s", status, name, detail)

    # ── A. dim_invoices ───────────────────────────────────────────────────────
    _check(
        "A1_dim_invoices_InvoiceID_unique",
        dim_inv["InvoiceID"].nunique() == len(dim_inv),
        f"unique={dim_inv['InvoiceID'].nunique()}  rows={len(dim_inv)}",
    )
    _check(
        "A2_dim_invoices_CustomerID_not_null",
        int(dim_inv["CustomerID"].isna().sum()) == 0,
        f"nulls={dim_inv['CustomerID'].isna().sum()}",
    )
    _check(
        "A3_dim_invoices_date_not_null",
        int(dim_inv["date"].isna().sum()) == 0,
        f"nulls={dim_inv['date'].isna().sum()}",
    )
    _check(
        "A4_dim_invoices_one_customer_per_invoice",
        int(dim_inv.groupby("InvoiceID")["CustomerID"].nunique().max()) == 1,
        "max customers per invoice = "
        + str(dim_inv.groupby("InvoiceID")["CustomerID"].nunique().max()),
    )
    _check(
        "A5_dim_invoices_one_date_per_invoice",
        int(dim_inv.groupby("InvoiceID")["date"].nunique().max()) == 1,
        "max dates per invoice = "
        + str(dim_inv.groupby("InvoiceID")["date"].nunique().max()),
    )

    # ── B. fact_invoice_items ─────────────────────────────────────────────────
    _check(
        "B1_fact_ii_no_exact_duplicates",
        int(fact_ii[["InvoiceID","product_id","quantity","price","line_total"]]
            .duplicated().sum()) == 0,
        f"dups={fact_ii[['InvoiceID','product_id','quantity','price','line_total']].duplicated().sum()}",
    )
    _check(
        "B2_fact_ii_InvoiceID_not_null",
        int(fact_ii["InvoiceID"].isna().sum()) == 0,
        f"nulls={fact_ii['InvoiceID'].isna().sum()}",
    )
    _check(
        "B3_fact_ii_product_id_not_null",
        int(fact_ii["product_id"].isna().sum()) == 0,
        f"nulls={fact_ii['product_id'].isna().sum()}",
    )
    _check(
        "B4_fact_ii_quantity_non_negative",
        int((fact_ii["quantity"] < 0).sum()) == 0,
        f"negative_qty={( fact_ii['quantity'] < 0).sum()}",
    )
    _check(
        "B5_fact_ii_price_non_negative",
        int((fact_ii["price"] < 0).sum()) == 0,
        f"negative_price={(fact_ii['price'] < 0).sum()}",
    )
    _check(
        "B6_fact_ii_line_total_non_negative",
        int((fact_ii["line_total"] < 0).sum()) == 0,
        f"negative_line_total={(fact_ii['line_total'] < 0).sum()}",
    )

    # ── C. Referential integrity ──────────────────────────────────────────────
    inv_ids_in_fact = set(fact_ii["InvoiceID"].unique())
    inv_ids_in_dim  = set(dim_inv["InvoiceID"].unique())
    orphan_inv_in_dim  = len(inv_ids_in_dim  - inv_ids_in_fact)
    orphan_inv_in_fact = len(inv_ids_in_fact - inv_ids_in_dim)

    _check(
        "C1_all_dim_invoice_ids_in_fact_ii",
        orphan_inv_in_dim == 0,
        f"invoice_ids in dim_invoices but not in fact_ii: {orphan_inv_in_dim}",
    )
    _check(
        "C2_all_fact_ii_invoice_ids_in_dim",
        orphan_inv_in_fact == 0,
        f"invoice_ids in fact_ii but not in dim_invoices: {orphan_inv_in_fact}",
    )

    cust_ids_in_dim_inv  = set(dim_inv["CustomerID"].unique())
    cust_ids_in_dim_cust = set(dim_cust["CustomerID"].unique())
    orphan_cust = len(cust_ids_in_dim_inv - cust_ids_in_dim_cust)
    _check(
        "C3_dim_invoices_CustomerID_in_dim_customers",
        orphan_cust == 0,
        f"CustomerIDs in dim_invoices not in dim_customers: {orphan_cust}",
    )

    prod_ids_in_fact = set(fact_ii["product_id"].unique())
    prod_ids_in_dim  = set(dim_prod["product_id"].unique())
    orphan_prod = len(prod_ids_in_fact - prod_ids_in_dim)
    _check(
        "C4_fact_ii_product_id_in_dim_products",
        orphan_prod == 0,
        f"product_ids in fact_ii not in dim_products: {orphan_prod}",
    )

    # ── D. Revenue validation ─────────────────────────────────────────────────
    rev_direct   = round(float(ii_raw_deduped["line_total"].sum()), 4)
    rev_dim_inv  = round(float(dim_inv["invoice_revenue"].sum()), 4)
    rev_fact_ii  = round(float(
        fact_ii[["InvoiceID","product_id","quantity","price","line_total"]]
        .drop_duplicates()["line_total"].sum()
    ), 4)
    rev_diff     = round(rev_dim_inv - rev_direct, 4)

    _check(
        "D1_revenue_direct_vs_dim_invoices",
        abs(rev_diff) < 0.01,   # allow 1p floating-point tolerance
        f"direct=£{rev_direct:,.2f}  dim_inv=£{rev_dim_inv:,.2f}  diff=£{rev_diff:,.4f}",
    )
    _check(
        "D2_revenue_fact_ii_vs_direct",
        abs(rev_fact_ii - rev_direct) < 0.01,
        f"fact_ii=£{rev_fact_ii:,.2f}  direct=£{rev_direct:,.2f}  diff=£{rev_fact_ii-rev_direct:,.4f}",
    )

    checks["_revenue_summary"] = {
        "revenue_direct_from_ii":      rev_direct,
        "revenue_from_dim_invoices":   rev_dim_inv,
        "revenue_from_fact_ii":        rev_fact_ii,
        "difference_dim_vs_direct":    rev_diff,
        "pct_difference":              round(abs(rev_diff) / rev_direct * 100, 6)
                                       if rev_direct else 0,
    }

    # ── E. Invoice count validation ───────────────────────────────────────────
    n_inv_fact  = int(fact_ii["InvoiceID"].nunique())
    n_inv_dim   = len(dim_inv)
    inv_only_in_dim  = len(inv_ids_in_dim  - inv_ids_in_fact)
    inv_only_in_fact = len(inv_ids_in_fact - inv_ids_in_dim)

    _check(
        "E1_invoice_count_match",
        n_inv_fact == n_inv_dim,
        f"fact_ii unique InvoiceIDs={n_inv_fact}  dim_invoices rows={n_inv_dim}  "
        f"only_in_dim={inv_only_in_dim}  only_in_fact={inv_only_in_fact}",
    )

    # ── F. Customer validation ────────────────────────────────────────────────
    n_cust_dim_inv  = int(dim_inv["CustomerID"].nunique())
    n_cust_dim_cust = len(dim_cust)
    _check(
        "F1_customer_count",
        n_cust_dim_inv <= n_cust_dim_cust,
        f"unique customers in dim_invoices={n_cust_dim_inv}  "
        f"rows in dim_customers={n_cust_dim_cust}",
    )

    return checks


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline entry point
# ─────────────────────────────────────────────────────────────────────────────

def build_analytical_layer(
    save: bool = True,
) -> tuple[dict[str, pd.DataFrame], dict, dict]:
    """
    Build all four normalised analytical tables.

    Returns
    -------
    tables  : dict  keys = dim_invoices, fact_invoice_items, dim_customers, dim_products
    report  : dict  build metadata
    checks  : dict  integrity check results
    """
    report: dict = {}

    # Load deduplicated sources (raw files untouched)
    cust, purch, ii, prod = _load_deduped_sources()

    # Build tables
    dim_inv  = build_dim_invoices(purch, ii, report)
    fact_ii  = build_fact_invoice_items(ii, prod, report)
    dim_cust = build_dim_customers(cust, report)
    dim_prod = build_dim_products(prod, report)

    # Integrity checks
    checks = run_integrity_checks(dim_inv, fact_ii, dim_cust, dim_prod, ii)

    tables = {
        "dim_invoices":        dim_inv,
        "fact_invoice_items":  fact_ii,
        "dim_customers":       dim_cust,
        "dim_products":        dim_prod,
    }

    # Save
    if save:
        for name, df in tables.items():
            _save(df, f"{name}.csv")

    return tables, report, checks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    tables, report, checks = build_analytical_layer(save=True)

    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)
    for name, df in tables.items():
        print(f"  {name:25s}: {len(df):>8,} rows × {len(df.columns)} cols")

    print("\n" + "="*60)
    print("INTEGRITY CHECKS")
    print("="*60)
    all_passed = True
    for check_name, result in checks.items():
        if check_name.startswith("_"):
            continue
        status = "PASS" if result["passed"] else "FAIL"
        if not result["passed"]:
            all_passed = False
        print(f"  [{status}] {check_name:50s} {result['detail']}")

    print(f"\n  Overall: {'ALL PASSED ✅' if all_passed else 'FAILURES DETECTED ❌'}")

    rev = checks.get("_revenue_summary", {})
    print(f"\n  Revenue (direct from ii):    £{rev.get('revenue_direct_from_ii', 0):>14,.2f}")
    print(f"  Revenue (dim_invoices agg):  £{rev.get('revenue_from_dim_invoices', 0):>14,.2f}")
    print(f"  Difference:                  £{rev.get('difference_dim_vs_direct', 0):>14,.4f}")
