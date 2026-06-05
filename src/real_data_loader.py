"""Load and aggregate real event-level e-commerce behavior logs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


USER_ID_CANDIDATES = ["user_id", "client_id", "visitorid", "visitor_id", "customer_id"]
ITEM_ID_CANDIDATES = ["item_id", "product_id", "sku", "itemid", "stockcode"]
TIMESTAMP_CANDIDATES = ["timestamp", "event_time", "time", "datetime", "date"]
EVENT_TYPE_CANDIDATES = ["event_type", "event", "event_name", "action", "interaction_type"]
PRICE_CANDIDATES = ["price", "unit_price", "unitprice", "product_price"]
SESSION_ID_CANDIDATES = ["session_id", "user_session", "session"]

DATASET_PRESETS = {
    "generic": {},
    "synerise": {
        "user_col": "client_id",
        "item_col": "sku",
        "timestamp_col": "timestamp",
        "event_col": "event_type",
        "price_col": "price",
    },
    "retailrocket": {
        "user_col": "visitorid",
        "item_col": "itemid",
        "timestamp_col": "timestamp",
        "event_col": "event",
        "price_col": None,
        "session_col": None,
    },
}

SYNERISE_EVENT_FILES = {
    "product_buy": "product_buy.parquet",
    "add_to_cart": "add_to_cart.parquet",
    "remove_from_cart": "remove_from_cart.parquet",
    "page_visit": "page_visit.parquet",
    "search_query": "search_query.parquet",
}

SYNERISE_PRODUCT_EVENT_TYPES = {"product_buy", "add_to_cart", "remove_from_cart"}

EVENT_ALIASES = {
    "view": "view",
    "views": "view",
    "page_visit": "view",
    "pageview": "view",
    "page_view": "view",
    "search": "search",
    "search_query": "search",
    "addtocart": "cart",
    "add_to_cart": "cart",
    "cart": "cart",
    "remove_from_cart": "remove_from_cart",
    "removefromcart": "remove_from_cart",
    "product_buy": "purchase",
    "buy": "purchase",
    "purchase": "purchase",
    "transaction": "purchase",
}


def _find_column(columns: Iterable[str], candidates: list[str]) -> str | None:
    normalized = {column.lower().strip(): column for column in columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def _normalize_event_type(value: object) -> str:
    text = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    return EVENT_ALIASES.get(text, text)


def _read_csv_sample(
    path: Path,
    sample_n_rows: int | None,
    chunksize: int | None,
) -> pd.DataFrame:
    if chunksize is None:
        return pd.read_csv(path, nrows=sample_n_rows)

    frames = []
    remaining = sample_n_rows
    for chunk in pd.read_csv(path, chunksize=chunksize):
        if remaining is None:
            frames.append(chunk)
            continue
        if remaining <= 0:
            break
        frames.append(chunk.head(remaining))
        remaining -= len(frames[-1])
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def read_event_log(
    input_path: str | Path,
    sample_n_rows: int | None = None,
    chunksize: int | None = None,
) -> pd.DataFrame:
    """Read a CSV or parquet event log, optionally using a small sample."""

    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Raw event file not found: {path}\n"
            "Download a real event-level dataset and place it under data/raw/, "
            "or run with --input-file data/fixtures/mini_event_log.csv for a format smoke test."
        )

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _read_csv_sample(path, sample_n_rows=sample_n_rows, chunksize=chunksize)
    if suffix in {".parquet", ".pq"}:
        try:
            data = pd.read_parquet(path)
        except ImportError as exc:
            raise ImportError(
                "Reading parquet files requires an optional parquet engine such as pyarrow or fastparquet. "
                "Install one with `pip install pyarrow`, or convert the event log to CSV."
            ) from exc
        return data.head(sample_n_rows) if sample_n_rows is not None else data

    raise ValueError(f"Unsupported file type: {suffix}. Use CSV or parquet.")


def _read_parquet(path: Path, sample_n_rows: int | None = None) -> pd.DataFrame:
    try:
        data = pd.read_parquet(path)
    except ImportError as exc:
        raise ImportError(
            "Reading Synerise parquet files requires an optional parquet engine such as pyarrow or fastparquet. "
            "Install one with `pip install pyarrow`, or convert the event files to CSV."
        ) from exc
    return data.head(sample_n_rows) if sample_n_rows is not None else data


def _find_synerise_data_root(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(
            f"Synerise data directory not found: {path}\n"
            "Download the RecSys Challenge 2025 / Synerise dataset and place the official parquet files under data/raw/synerise/."
        )
    if path.is_file():
        return path.parent
    return path


def read_synerise_event_directory(
    input_path: str | Path,
    sample_n_rows: int | None = None,
    include_product_properties: bool = True,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Read the official Synerise multi-parquet event directory."""

    root = _find_synerise_data_root(Path(input_path))
    frames = []
    available_files = []
    missing_files = []

    per_file_sample = None
    if sample_n_rows is not None:
        per_file_sample = max(1, sample_n_rows // len(SYNERISE_EVENT_FILES))

    for event_type, file_name in SYNERISE_EVENT_FILES.items():
        path = root / file_name
        if not path.exists():
            missing_files.append(file_name)
            continue
        event_data = _read_parquet(path, sample_n_rows=per_file_sample)
        event_data["event_type"] = event_type
        frames.append(event_data)
        available_files.append(file_name)

    if not frames:
        raise FileNotFoundError(
            "No Synerise event parquet files were found. Expected files include: "
            f"{', '.join(SYNERISE_EVENT_FILES.values())}. Place them under data/raw/synerise/."
        )

    events = pd.concat(frames, ignore_index=True)
    properties_path = root / "product_properties.parquet"
    has_product_properties = properties_path.exists()

    if include_product_properties and has_product_properties:
        properties = _read_parquet(properties_path)
        product_mask = events["event_type"].isin(SYNERISE_PRODUCT_EVENT_TYPES)
        product_events = events.loc[product_mask].merge(properties, on="sku", how="left")
        non_product_events = events.loc[~product_mask].copy()
        events = pd.concat([product_events, non_product_events], ignore_index=True, sort=False)

    metadata = {
        "synerise_root": str(root),
        "available_files": available_files,
        "missing_files": missing_files,
        "has_product_properties": has_product_properties,
        "sampling_note": (
            "For the Synerise multi-file loader, sample_n_rows is split approximately evenly "
            "across event files. This is useful for workflow validation, but it should not be "
            "interpreted as the natural traffic distribution of the full dataset."
        )
        if sample_n_rows is not None
        else "No row sampling was requested.",
    }
    return events, metadata


def _resolve_column(
    data: pd.DataFrame,
    override: str | None,
    candidates: list[str],
) -> str | None:
    if override:
        if override not in data.columns:
            raise ValueError(f"Configured column `{override}` was not found in the input file.")
        return override
    return _find_column(data.columns, candidates)


def normalize_event_log(
    data: pd.DataFrame,
    dataset_type: str = "generic",
    user_col: str | None = None,
    item_col: str | None = None,
    timestamp_col: str | None = None,
    event_col: str | None = None,
    price_col: str | None = None,
    session_col: str | None = None,
) -> tuple[pd.DataFrame, dict[str, str | None]]:
    """Normalize common real dataset schemas to user/item/time/event columns."""

    if dataset_type not in DATASET_PRESETS:
        raise ValueError(f"Unknown dataset_type `{dataset_type}`. Use one of: {sorted(DATASET_PRESETS)}")

    preset = DATASET_PRESETS[dataset_type]
    user_col = _resolve_column(data, user_col or preset.get("user_col"), USER_ID_CANDIDATES)
    item_col = _resolve_column(data, item_col or preset.get("item_col"), ITEM_ID_CANDIDATES)
    timestamp_col = _resolve_column(data, timestamp_col or preset.get("timestamp_col"), TIMESTAMP_CANDIDATES)
    event_col = _resolve_column(data, event_col or preset.get("event_col"), EVENT_TYPE_CANDIDATES)
    price_col = _resolve_column(data, price_col or preset.get("price_col"), PRICE_CANDIDATES)
    session_col = _resolve_column(data, session_col or preset.get("session_col"), SESSION_ID_CANDIDATES)

    required = {"user_id": user_col, "event_type": event_col}
    missing = [name for name, column in required.items() if column is None]
    if missing:
        raise ValueError(f"Missing required event-log columns after schema detection: {missing}")

    normalized = pd.DataFrame()
    normalized["user_id"] = data[user_col].astype(str)
    normalized["event_type"] = data[event_col].map(_normalize_event_type)
    normalized["item_id"] = data[item_col].astype(str) if item_col else pd.NA

    if timestamp_col:
        raw_timestamp = data[timestamp_col]
        if pd.api.types.is_numeric_dtype(raw_timestamp):
            median_value = raw_timestamp.dropna().median()
            unit = "ms" if median_value and median_value > 10_000_000_000 else "s"
            normalized["timestamp"] = pd.to_datetime(raw_timestamp, unit=unit, errors="coerce")
        else:
            normalized["timestamp"] = pd.to_datetime(raw_timestamp, errors="coerce")
    else:
        normalized["timestamp"] = pd.NaT

    normalized["price"] = pd.to_numeric(data[price_col], errors="coerce") if price_col else np.nan
    normalized["session_id"] = data[session_col].astype(str) if session_col else pd.NA

    source_columns = {
        "dataset_type": dataset_type,
        "user_id": user_col,
        "item_id": item_col,
        "timestamp": timestamp_col,
        "event_type": event_col,
        "price": price_col,
        "session_id": session_col,
    }
    return normalized, source_columns


def normalize_synerise_event_log(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str | None]]:
    """Normalize official Synerise event files after concatenation."""

    required = {"client_id", "timestamp", "event_type"}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Synerise event data is missing required columns: {missing}")

    normalized = pd.DataFrame()
    normalized["user_id"] = data["client_id"].astype(str)
    normalized["event_type"] = data["event_type"].map(_normalize_event_type)

    if "sku" in data.columns:
        normalized["item_id"] = data["sku"].astype("string")
    elif "url" in data.columns:
        normalized["item_id"] = data["url"].astype("string")
    else:
        normalized["item_id"] = pd.NA

    normalized["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    normalized["price"] = pd.to_numeric(data["price"], errors="coerce") if "price" in data.columns else np.nan
    normalized["category"] = pd.to_numeric(data["category"], errors="coerce") if "category" in data.columns else np.nan
    normalized["session_id"] = pd.NA

    source_columns = {
        "dataset_type": "synerise",
        "user_id": "client_id",
        "item_id": "sku/url",
        "timestamp": "timestamp",
        "event_type": "source parquet file name",
        "price": "product_properties.price",
        "category": "product_properties.category",
        "session_id": None,
    }
    return normalized, source_columns


def filter_by_time(
    events: pd.DataFrame,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """Filter events by timestamp when timestamp values are available."""

    if "timestamp" not in events.columns or events["timestamp"].isna().all():
        return events.copy()

    filtered = events.copy()
    if start_date:
        filtered = filtered[filtered["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["timestamp"] <= pd.to_datetime(end_date)]
    return filtered


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace(0, np.nan)
    return (numerator / denominator).replace([np.inf, -np.inf], np.nan).fillna(0)


def aggregate_user_features(events: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Aggregate normalized event logs into user-level behavior features."""

    if events.empty:
        raise ValueError("No events available after loading and filtering.")

    grouped = events.groupby("user_id", dropna=False)
    features = pd.DataFrame(index=grouped.size().index)
    features["event_count"] = grouped.size()
    features["view_count"] = grouped["event_type"].apply(lambda value: (value == "view").sum())
    features["cart_count"] = grouped["event_type"].apply(lambda value: (value == "cart").sum())
    features["remove_from_cart_count"] = grouped["event_type"].apply(lambda value: (value == "remove_from_cart").sum())
    features["purchase_count"] = grouped["event_type"].apply(lambda value: (value == "purchase").sum())
    features["search_count"] = grouped["event_type"].apply(lambda value: (value == "search").sum())
    features["unique_items"] = grouped["item_id"].nunique(dropna=True)

    if "category" in events.columns and events["category"].notna().any():
        features["unique_categories"] = grouped["category"].nunique(dropna=True)
    else:
        features["unique_categories"] = np.nan

    if events["session_id"].notna().any():
        features["session_count"] = grouped["session_id"].nunique(dropna=True)
    else:
        features["session_count"] = np.nan

    if events["timestamp"].notna().any():
        active_days = grouped["timestamp"].apply(lambda value: value.dt.date.nunique())
        last_purchase = (
            events[events["event_type"] == "purchase"]
            .groupby("user_id")["timestamp"]
            .max()
        )
        max_timestamp = events["timestamp"].max()
        features["active_days"] = active_days
        features["days_since_last_purchase"] = (max_timestamp - last_purchase).dt.days.reindex(features.index)
    else:
        features["active_days"] = np.nan
        features["days_since_last_purchase"] = np.nan

    purchase_events = events[events["event_type"] == "purchase"].copy()
    if events["price"].notna().any() and not purchase_events.empty:
        price_signal = purchase_events.groupby("user_id")["price"].sum()
        features["price_signal_total"] = price_signal.reindex(features.index).fillna(0)
        features["average_purchase_price_signal"] = safe_divide(features["price_signal_total"], features["purchase_count"])
    else:
        features["price_signal_total"] = np.nan
        features["average_purchase_price_signal"] = np.nan
    features["conversion_rate"] = safe_divide(features["purchase_count"], features["view_count"])
    features["cart_to_purchase_rate"] = safe_divide(features["purchase_count"], features["cart_count"])
    features["purchase_per_active_day"] = safe_divide(features["purchase_count"], features["active_days"])
    features["actions_per_active_day"] = safe_divide(features["event_count"], features["active_days"])
    features["item_diversity_ratio"] = safe_divide(features["unique_items"], features["event_count"])

    event_diversity = grouped["event_type"].nunique(dropna=True)
    features["action_diversity"] = event_diversity
    count_columns = ["view_count", "cart_count", "remove_from_cart_count", "purchase_count", "search_count"]
    features["zero_purchase_indicator"] = (features["purchase_count"] == 0).astype(int)
    features["low_activity_indicator"] = (features["event_count"] <= features["event_count"].quantile(0.25)).astype(int)
    features["behavior_sparsity"] = (features[count_columns] == 0).sum(axis=1) / len(count_columns)

    metadata = {
        "event_count": int(len(events)),
        "user_count": int(len(features)),
        "event_types": sorted(events["event_type"].dropna().unique().tolist()),
        "has_timestamp": bool(events["timestamp"].notna().any()),
        "has_price": bool(events["price"].notna().any()),
        "price_note": "Price may be anonymized or bucketed depending on the public dataset; interpret it as a price signal unless the dataset documentation says otherwise.",
        "has_session_id": bool(events["session_id"].notna().any()),
        "has_category": bool("category" in events.columns and events["category"].notna().any()),
        "unavailable_fields": [
            "coupon_usage",
            "discount_ratio",
            "return_count",
            "session_id",
            "confirmed_fraud_label",
        ],
    }
    return features.reset_index(), metadata


def load_real_user_features(
    input_path: str | Path,
    dataset_type: str = "generic",
    sample_n_rows: int | None = None,
    chunksize: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    user_col: str | None = None,
    item_col: str | None = None,
    timestamp_col: str | None = None,
    event_col: str | None = None,
    price_col: str | None = None,
    session_col: str | None = None,
    output_path: str | Path | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load event logs and save aggregated user-level features if requested."""

    extra_metadata = {}
    input_path_obj = Path(input_path)
    if dataset_type == "synerise" and (input_path_obj.is_dir() or input_path_obj.suffix == ""):
        raw_events, extra_metadata = read_synerise_event_directory(input_path, sample_n_rows=sample_n_rows)
        normalized, source_columns = normalize_synerise_event_log(raw_events)
    else:
        raw_events = read_event_log(input_path, sample_n_rows=sample_n_rows, chunksize=chunksize)
        normalized, source_columns = normalize_event_log(
            raw_events,
            dataset_type=dataset_type,
            user_col=user_col,
            item_col=item_col,
            timestamp_col=timestamp_col,
            event_col=event_col,
            price_col=price_col,
            session_col=session_col,
        )
    filtered = filter_by_time(normalized, start_date=start_date, end_date=end_date)
    features, metadata = aggregate_user_features(filtered)
    metadata.update(extra_metadata)
    metadata["source_columns"] = source_columns
    metadata["input_path"] = str(input_path)
    metadata["sample_n_rows"] = sample_n_rows
    metadata["start_date"] = start_date
    metadata["end_date"] = end_date

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        features.to_csv(output_path, index=False)

    return features, metadata
