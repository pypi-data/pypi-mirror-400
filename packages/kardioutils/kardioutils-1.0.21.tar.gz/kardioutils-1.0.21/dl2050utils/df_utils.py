import pandas as pd
import os
from __future__ import annotations
from typing import Tuple, List, Optional
import numpy as np

def list_prefixes(df: pd.DataFrame) -> list:
    """Return all distinct prefixes in the dataframe."""
    return df["prefix"].dropna().unique().tolist()


def filter_by_prefix(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Return all rows that match a given prefix exactly."""
    return df[df["prefix"] == prefix]


def filter_prefix_contains(df: pd.DataFrame, text: str) -> pd.DataFrame:
    """Return all rows where prefix contains the given text."""
    return df[df["prefix"].str.contains(text, na=False)]


def find_by_uid_suffix(df: pd.DataFrame, uid_suffix: str) -> pd.DataFrame:
    """Return all rows that match a given uid_suffix."""
    return df[df["uid_suffix"] == uid_suffix]


def find_by_uid_full(df: pd.DataFrame, uid_full: str) -> pd.DataFrame:
    """Return all rows that match a given uid_full."""
    return df[df["uid_full"] == uid_full]


def holter_only(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows where holter == True."""
    return df[df["holter"] == True]


def non_holter_only(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows where holter == False."""
    return df[df["holter"] == False]


def get_path_by_uid_suffix(df: pd.DataFrame, uid_suffix: str) -> str | None:
    """
    Return the path for a given uid_suffix.
    If there are multiple rows, returns the first one.
    If nothing is found, returns None.
    """
    rows = df[df["uid_suffix"] == uid_suffix]
    if rows.empty:
        return None
    return rows.iloc[0]["path"]


def get_paths_by_prefix(df: pd.DataFrame, prefix: str, holter_only_flag: bool | None = None) -> list:
    """
    Return a list of paths filtered by prefix and optionally holter flag.
    - holter_only_flag = True  → only holter rows
    - holter_only_flag = False → only non-holter rows
    - holter_only_flag = None  → ignore holter column
    """
    subset = df[df["prefix"] == prefix]
    if holter_only_flag is not None:
        subset = subset[subset["holter"] == holter_only_flag]
    return subset["path"].dropna().tolist()


def check_missing_files(df):
    """
    Return subset of rows whose 'path' does not point to an existing file.
    """
    mask = ~df["path"].astype(str).apply(os.path.exists)
    return df[mask]


def check_existing_files(df):
    """
    Return subset of rows whose 'path' exists.
    """
    mask = df["path"].astype(str).apply(os.path.exists)
    return df[mask]

def load_X_from_index_df(
    index_df: pd.DataFrame,
    fdb,
    *,
    uid_col: str = "uid_full",
    pre: str = "x_",
    ext: str = ".npy",
    allow_pickle: bool = False,
    stack: bool = True,
    on_missing: str = "skip",   # "skip" | "raise" | "keep_none"
) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
    """
    Loads x_ arrays for each row in index_df using fdb.load(row[uid_col], pre, ext).

    Returns:
      - X: stacked np.ndarray (N, ...) if stack=True; otherwise object array of length N
      - ids: list of ids in the same order as X
      - meta: dataframe aligned with X (rows kept), including a 'loaded' boolean column
    """
    if uid_col not in index_df.columns:
        raise KeyError(f"uid_col '{uid_col}' not found in index_df columns")

    loaded_arrays = []
    kept_ids: List[str] = []
    kept_rows = []
    missing_rows = []

    for _, row in index_df.iterrows():
        uid = row[uid_col]
        arr = fdb.load(uid, pre=pre, ext=ext, allow_pickle=allow_pickle)

        if arr is None:
            if on_missing == "raise":
                raise FileNotFoundError(f"Missing array for {uid} (pre={pre}, ext={ext})")
            if on_missing == "keep_none":
                loaded_arrays.append(None)
                kept_ids.append(uid)
                r = row.copy()
                r["loaded"] = False
                kept_rows.append(r)
            else:  # skip
                r = row.copy()
                r["loaded"] = False
                missing_rows.append(r)
            continue

        loaded_arrays.append(arr)
        kept_ids.append(uid)
        r = row.copy()
        r["loaded"] = True
        kept_rows.append(r)

    meta = pd.DataFrame(kept_rows).reset_index(drop=True)

    if not stack:
        # keep as object array (useful if shapes can differ or you used keep_none)
        X = np.array(loaded_arrays, dtype=object)
        return X, kept_ids, meta

    # stack=True: require all arrays exist and have same shape
    arrays_only = [a for a in loaded_arrays if a is not None]
    if len(arrays_only) == 0:
        return np.empty((0,), dtype=float), kept_ids, meta

    try:
        X = np.stack(arrays_only, axis=0)
    except Exception as e:
        raise ValueError(
            "Could not stack arrays (shapes likely differ). "
            "Use stack=False or handle padding/truncation."
        ) from e

   
    return X, kept_ids, meta