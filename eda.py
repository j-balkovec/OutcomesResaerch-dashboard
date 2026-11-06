# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %%
daily = pd.read_csv(
    "/Users/jbalkovec/Desktop/MSc/OutcomesResearch/REST/daily_responses.csv"
)
questionnaire = pd.read_csv(
    "/Users/jbalkovec/Desktop/MSc/OutcomesResearch/REST/initial_questionnaire.csv",
    sep=";",
)

daily["handgrip_kg"] = pd.to_numeric(
    daily["handgrip_kg"].str.replace(",", ".", regex=False), errors="coerce"
)

print("Daily responses:", daily.shape)
print(daily.head())
print("\nInitial questionnaire:", questionnaire.shape)
print(questionnaire.head())

# %%
datasets = {"Daily responses": daily, "Initial questionnaire": questionnaire}

for name, data in datasets.items():
    print(f"\n{name} columns and types:\n{data.dtypes}")
    print("Unique participants:", data["id"].nunique())
    print("Observations per participant:")
    print(data.groupby("id", dropna=False).size())
    print("No calendar date column available.")

# %%
for name, data in datasets.items():
    missing = pd.DataFrame(
        {
            "Count": data.isna().sum(),
            "Percent": data.isna().mean() * 100,
        }
    )
    print(f"\n{name} missing values:")
    print(missing.round(2))

# %%
continuous = {
    "Daily responses": [
        "total_sleep_time",
        "longest_interval_duration",
        "sleep period mean",
        "sleep period standard deviation",
        "sleep period msd",
        "handgrip_kg",
        "caffeine_mg",
    ],
    "Initial questionnaire": [
        "Age",
        "Your height in centimeters (cm)",
        "Your weight in kilograms (kg)",
    ],
}

for name, columns in continuous.items():
    summary = datasets[name][columns].describe().T
    summary = summary.rename(columns={"25%": "Q1", "50%": "median", "75%": "Q3"})
    summary["IQR"] = summary["Q3"] - summary["Q1"]
    summary["range"] = summary["max"] - summary["min"]
    print(f"\n{name} numerical statistics:")
    print(summary.round(2))

# %%
for name, columns in continuous.items():
    for column in columns:
        values = datasets[name][column].dropna()
        if values.empty:
            continue

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(values, bins="auto", edgecolor="black")
        ax.axvline(np.mean(values), color="red", linestyle="--", label="Mean")
        ax.axvline(np.median(values), color="green", linestyle=":", label="Median")
        ax.set(title=f"{name}: {column}", xlabel=column, ylabel="Frequency")
        ax.legend()
        plt.tight_layout()
        plt.show()

# %%
ordinal = {
    "screentime": ["Short", "Medium", "Long"],
    "caffeine_time": ["Morning", "Afternoon", "Evening"],
    "weekday": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ],
    "coffee": ["1", "2", "3", "4 or more"],
}

ordered_numbers = [
    "sleep_intervals",
    "energy",
    "cola",
    "tea",
    "espresso",
    "sleepquality",
    "fatigue",
    "soreness",
    "readiness",
    "sleepdura_sr",
]

for column in ordered_numbers:
    ordinal[column] = sorted(daily[column].dropna().unique())

# %%
daily_categories = list(ordinal) + [
    "matchday",
    "soreness_location_1",
    "soreness_location_2",
]

for column in questionnaire.columns:
    if column.startswith("Athlete Sleep Behaviour Questionnaire"):
        ordinal[column] = ["Never", "Rarely", "Sometimes", "Frequently", "Always"]

questionnaire_categories = [
    column
    for column in questionnaire.columns
    if column not in continuous["Initial questionnaire"] + ["id", "Comments (optional)"]
]

categories = {
    "Daily responses": daily_categories,
    "Initial questionnaire": questionnaire_categories,
}

# %%
for name, columns in categories.items():
    for column in columns:
        counts = datasets[name][column].value_counts()
        if column in ordinal:
            counts = counts.reindex(ordinal[column], fill_value=0)
        else:
            counts = counts.sort_index()

        print(f"\n{name}: {column}\n{counts}")
        print("Missing:", datasets[name][column].isna().sum())

        fig, ax = plt.subplots(figsize=(10, 4))
        bars = ax.bar(counts.index.astype(str), counts.values)
        ax.bar_label(bars)
        ax.set(title=f"{name}: {column}", xlabel=column, ylabel="Frequency")
        ax.tick_params(axis="x", rotation=45)
        plt.tight_layout()
        plt.show()
# %%
print("Daily observations per participant:")
print(daily.groupby("id").size())

averages = daily.groupby("id")["total_sleep_time"].mean().dropna().sort_values()
print("\nAverage total sleep time per participant:")
print(averages)

# %%
if not averages.empty:
    averages.plot.barh(
        figsize=(10, 7), title="Average total sleep time per participant"
    )
    plt.xlabel("Average total sleep time (original units)")
    plt.ylabel("Participant ID")
    plt.tight_layout()
    plt.show()
