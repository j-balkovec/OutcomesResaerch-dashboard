# %%
from pathlib import Path

import numpy as np
import pandas as pd

# %%
source = pd.read_csv("rest_tableau.csv", dtype={"participant_id": "string"})
data = source.copy()
assert data["source_row_index"].is_unique
assert data["participant_id"].notna().all()

labels = {participant: f"P{i:02d}" for i, participant in enumerate(sorted(data["participant_id"].unique()), 1)}
data["participant_label"] = data["participant_id"].map(labels)

# %%
duplicate_columns = [column for column in source.columns if column != "source_row_index"]
ordered = source.sort_values("source_row_index")
later_duplicate = ordered.duplicated(subset=duplicate_columns, keep="first")
later_duplicate_rows = ordered.loc[later_duplicate, "source_row_index"]
assert source.loc[source["source_row_index"].isin(later_duplicate_rows), "source_exact_duplicate"].all()

data["include_primary_sleep_analysis"] = (
    data["has_valid_sleep_measurement"]
    & ~data["sleep_measurement_flag"].isin(["under_60_min", "over_720_min"])
    & ~data["source_row_index"].isin(later_duplicate_rows)
)
primary = data["include_primary_sleep_analysis"]

# %%
data["sleep_duration_hours"] = data["total_sleep_time_min"] / 60
primary_hours = data["sleep_duration_hours"].where(primary)
data["sleep_duration_category"] = pd.cut(
    primary_hours,
    bins=[-np.inf, 6, 7, 9, np.inf],
    labels=["Less than 6 hours", "6 to less than 7 hours", "7 to less than 9 hours", "9 hours or more"],
    right=False,
)
data["is_short_sleep"] = pd.Series(pd.NA, index=data.index, dtype="Int64")
data.loc[primary, "is_short_sleep"] = (primary_hours[primary] < 7).astype(int)
data["sleep_continuity_ratio"] = (
    data["longest_sleep_interval_min"] / data["total_sleep_time_min"]
).where(primary & data["total_sleep_time_min"].gt(0))
data["self_report_discrepancy_hours"] = (
    data["self_reported_sleep_hours"].where(data["self_reported_sleep_hours"].gt(0))
    - primary_hours
)

# %%
data["primary_sleep_duration_hours"] = primary_hours
data["caffeine_for_mean"] = data["caffeine_mg"].mask(data["caffeine_zero_uncertain"])
data["flagged_sleep_observation"] = data["sleep_measurement_flag"].isin(
    ["under_60_min", "over_720_min", "inconsistent_or_incomplete"]
)

groups = data.groupby("participant_id", sort=False)
summary = groups.agg(
    participant_mean_sleep_duration_hours=("primary_sleep_duration_hours", "mean"),
    participant_sleep_duration_std_hours=("primary_sleep_duration_hours", "std"),
    participant_short_sleep_percentage=("is_short_sleep", "mean"),
    participant_mean_sleep_continuity_ratio=("sleep_continuity_ratio", "mean"),
    participant_median_sleep_quality=("sleep_quality", "median"),
    participant_mean_caffeine_mg=("caffeine_for_mean", "mean"),
    participant_mean_self_report_discrepancy_hours=("self_report_discrepancy_hours", "mean"),
    participant_wearable_completeness_pct=("has_valid_sleep_measurement", "mean"),
    participant_sleep_quality_completeness_pct=("has_sleep_quality_response", "mean"),
    participant_recovery_completeness_pct=("has_recovery_response", "mean"),
    participant_valid_sleep_observation_count=("has_valid_sleep_measurement", "sum"),
    participant_primary_sleep_observation_count=("include_primary_sleep_analysis", "sum"),
    participant_flagged_sleep_observation_count=("flagged_sleep_observation", "sum"),
)
percentage_columns = [
    "participant_short_sleep_percentage", "participant_wearable_completeness_pct",
    "participant_sleep_quality_completeness_pct", "participant_recovery_completeness_pct",
]
summary[percentage_columns] = summary[percentage_columns] * 100

data = data.drop(columns=["caffeine_for_mean", "flagged_sleep_observation"])
data = data.merge(summary, left_on="participant_id", right_index=True, how="left", validate="many_to_one", sort=False)

# %%
assert len(data) == len(source)
assert data["source_row_index"].equals(source["source_row_index"])
assert data["participant_label"].nunique() == data["participant_id"].nunique()
assert data.groupby("participant_id")["participant_label"].nunique().eq(1).all()
assert data["sleep_continuity_ratio"].dropna().between(0, 1).all()
assert data.loc[~primary, ["sleep_duration_category", "is_short_sleep", "sleep_continuity_ratio", "self_report_discrepancy_hours", "primary_sleep_duration_hours"]].isna().all().all()
assert data.loc[primary, "is_short_sleep"].notna().all()
assert data[percentage_columns].stack().between(0, 100).all()

# %%
Path("data/processed").mkdir(parents=True, exist_ok=True)
data.to_csv("data/processed/rest_dashboard.csv", index=False, encoding="utf-8")
exported = pd.read_csv("data/processed/rest_dashboard.csv", dtype={"participant_id": "string"})
assert exported.shape == data.shape
assert exported["source_row_index"].is_unique
assert exported["source_row_index"].equals(source["source_row_index"])
for column in source.columns:
    pd.testing.assert_series_equal(exported[column], source[column], check_dtype=False)

assert np.allclose(exported["sleep_duration_hours"], source["total_sleep_time_min"] / 60, equal_nan=True)
assert exported["sleep_continuity_ratio"].dropna().between(0, 1).all()
assert exported.loc[~exported["include_primary_sleep_analysis"], "is_short_sleep"].isna().all()
assert exported[percentage_columns].stack().between(0, 100).all()
assert exported.groupby("participant_id")["participant_label"].nunique().eq(1).all()
assert exported.groupby("participant_label")["participant_id"].nunique().eq(1).all()
assert exported["participant_label"].equals(exported["participant_id"].map(labels))

for participant, rows in exported.groupby("participant_id"):
    eligible = rows.loc[rows["include_primary_sleep_analysis"], "total_sleep_time_min"] / 60
    expected = eligible.mean()
    actual = rows["participant_mean_sleep_duration_hours"].iloc[0]
    assert np.isclose(actual, expected, equal_nan=True)
    assert rows["participant_mean_sleep_duration_hours"].nunique(dropna=False) == 1

print("Shape:", exported.shape)
print("Participants:", exported["participant_id"].nunique())
print("Primary observations:", exported["include_primary_sleep_analysis"].sum())
print("Excluded observations:", (~exported["include_primary_sleep_analysis"]).sum())
print("Sleep measurement flags:\n", exported["sleep_measurement_flag"].value_counts())
print("Later exact duplicates:", len(later_duplicate_rows))
print("Uncertain caffeine zeros:", exported["caffeine_zero_uncertain"].sum())
