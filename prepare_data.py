# %%
from pathlib import Path

import numpy as np
import pandas as pd

# %%
daily = pd.read_csv("REST/daily_responses.csv", dtype={"id": "string"})
baseline = pd.read_csv("REST/initial_questionnaire.csv", sep=";", dtype={"id": "string"})

assert daily["id"].notna().all()
assert baseline["id"].dropna().is_unique
assert set(daily["id"]).issubset(set(baseline["id"].dropna()))

# %%
daily.insert(0, "source_row_index", np.arange(1, len(daily) + 1))
daily["source_exact_duplicate"] = daily.drop(columns="source_row_index").duplicated(keep=False)
daily["handgrip_kg"] = pd.to_numeric(
    daily["handgrip_kg"].str.replace(",", ".", regex=False), errors="raise"
)

daily = daily.rename(columns={
    "id": "participant_id",
    "total_sleep_time": "total_sleep_time_min",
    "longest_interval_duration": "longest_sleep_interval_min",
    "longest_interval_start": "longest_sleep_interval_start",
    "longest_interval_end": "longest_sleep_interval_end",
    "sleep period mean": "sleep_period_activity_mean",
    "sleep period standard deviation": "sleep_period_activity_std",
    "sleep period msd": "sleep_period_activity_msd",
    "screentime": "screen_time",
    "sleepquality": "sleep_quality",
    "sleepdura_sr": "self_reported_sleep_hours",
})
daily = daily.drop(columns="Comments (optional)")

# %%
baseline = baseline.rename(columns={
    "id": "participant_id",
    "Age": "age",
    "Your height in centimeters (cm)": "height_cm",
    "Your weight in kilograms (kg)": "weight_kg",
})
baseline = baseline.loc[baseline["participant_id"].notna(), [
    "participant_id", "age", "height_cm", "weight_kg",
]]

prepared = daily.merge(baseline, on="participant_id", how="left", validate="many_to_one", indicator=True, sort=False)
assert prepared["_merge"].eq("both").all()
prepared = prepared.drop(columns="_merge")
assert len(prepared) == len(daily)
assert prepared["source_row_index"].is_unique
assert prepared["source_row_index"].tolist() == daily["source_row_index"].tolist()

# %%
prepared["has_valid_sleep_measurement"] = (
    prepared["total_sleep_time_min"].notna()
    & prepared["total_sleep_time_min"].gt(0)
    & prepared["longest_sleep_interval_min"].notna()
    & prepared["longest_sleep_interval_min"].gt(0)
    & prepared["longest_sleep_interval_min"].le(prepared["total_sleep_time_min"])
    & prepared["sleep_intervals"].ge(1)
    & prepared["sleep_onset"].notna()
    & prepared["sleep_offset"].notna()
)
prepared["has_sleep_quality_response"] = prepared["sleep_quality"].notna()
prepared["has_recovery_response"] = prepared[["fatigue", "readiness", "soreness"]].notna().any(axis=1)
prepared["sleep_measurement_flag"] = np.select(
    [
        prepared["total_sleep_time_min"].isna(),
        ~prepared["has_valid_sleep_measurement"],
        prepared["total_sleep_time_min"].lt(60),
        prepared["total_sleep_time_min"].gt(720),
    ],
    ["missing", "inconsistent_or_incomplete", "under_60_min", "over_720_min"],
    default="no_rule_triggered",
)
beverages = ["energy", "cola", "coffee", "tea", "espresso"]
prepared["caffeine_zero_uncertain"] = prepared["caffeine_mg"].eq(0) & prepared[beverages].isna().all(axis=1)

# %%
assert prepared["participant_id"].nunique() == daily["participant_id"].nunique()
assert prepared["total_sleep_time_min"].equals(daily["total_sleep_time_min"])
assert prepared["longest_sleep_interval_min"].equals(daily["longest_sleep_interval_min"])
assert not (prepared["longest_sleep_interval_min"] > prepared["total_sleep_time_min"]).any()
assert prepared.loc[prepared["total_sleep_time_min"].isna(), "sleep_measurement_flag"].eq("missing").all()
assert prepared.loc[prepared["total_sleep_time_min"].lt(60), "sleep_measurement_flag"].eq("under_60_min").all()
assert prepared.loc[prepared["total_sleep_time_min"].gt(720), "sleep_measurement_flag"].eq("over_720_min").all()

# %%
Path("data/processed").mkdir(parents=True, exist_ok=True)
prepared.to_csv("data/processed/rest_tableau.csv", index=False, encoding="utf-8")
exported = pd.read_csv("data/processed/rest_tableau.csv", dtype={"participant_id": "string"})

assert exported.shape == prepared.shape
assert exported["source_row_index"].equals(prepared["source_row_index"])
assert exported["participant_id"].equals(prepared["participant_id"])
assert exported["participant_id"].nunique() == daily["participant_id"].nunique()
assert exported["source_row_index"].is_unique
assert exported["total_sleep_time_min"].equals(prepared["total_sleep_time_min"])
assert exported["longest_sleep_interval_min"].equals(prepared["longest_sleep_interval_min"])
assert exported["sleep_measurement_flag"].equals(prepared["sleep_measurement_flag"])
assert exported["has_valid_sleep_measurement"].equals(prepared["has_valid_sleep_measurement"])
assert exported["has_sleep_quality_response"].equals(prepared["has_sleep_quality_response"])
assert exported["has_recovery_response"].equals(prepared["has_recovery_response"])
assert exported["caffeine_zero_uncertain"].equals(prepared["caffeine_zero_uncertain"])
assert exported["source_exact_duplicate"].equals(prepared["source_exact_duplicate"])
for column in prepared.columns:
    if column == "participant_id":
        continue
    pd.testing.assert_series_equal(
        exported[column], prepared[column], check_dtype=False, check_names=False
    )

print("Shape:", exported.shape)
print("Participants:", exported["participant_id"].nunique())
print("Exact source duplicate rows:", exported["source_exact_duplicate"].sum())
print("\nObservations per participant:\n", exported.groupby("participant_id").size())
print("\nMissing percentages:\n", (exported.isna().mean() * 100).round(2))
print("\nNumeric ranges:\n", exported.select_dtypes(include="number").agg(["min", "max"]))
print("\nTypes:\n", exported.dtypes)
print("\nSleep flags:\n", exported["sleep_measurement_flag"].value_counts())
print("\nBaseline coverage:", exported["age"].notna().sum(), "of", len(exported))
print("Identified baseline records retained:", len(baseline))
print("Unidentified baseline records excluded:", pd.read_csv("REST/initial_questionnaire.csv", sep=";")["id"].isna().sum())
