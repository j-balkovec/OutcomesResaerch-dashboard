## 1. Dataset Overview

| Property                        | Value                       |
| ------------------------------- | --------------------------- |
| Participants                    | 21                          |
| Daily observations              | 370                         |
| Daily variables                 | 30                          |
| Initial questionnaire records   | 22                          |
| Initial questionnaire variables | 27                          |
| Observations per participant    | 17–20                       |
| Dataset type                    | Longitudinal, observational |

The daily and initial questionnaire datasets can be linked using `id`. One initial questionnaire record has a missing ID.

**Important:** No calendar date column is available. The chronological order of observations must be verified before creating time-series charts.

## 2. Descriptive Statistics

| Variable                     | Mean   | Median | SD     | IQR    |
| ---------------------------- | ------ | ------ | ------ | ------ |
| Total sleep time (min)       | 474.53 | 495.00 | 137.44 | 115.25 |
| Longest sleep interval (min) | 327.62 | 315.00 | 150.57 | 230.50 |
| Sleep period mean            | 17.47  | 17.35  | 5.67   | 5.20   |
| Sleep period SD              | 47.66  | 46.23  | 20.16  | 18.13  |
| Sleep period MSD             | 20.65  | 20.87  | 8.43   | 9.05   |
| Handgrip strength (kg)       | 33.66  | 32.00  | 6.38   | 6.57   |
| Caffeine (mg)                | 90.28  | 65.00  | 104.83 | 160.00 |

### Participant characteristics

| Variable    | Mean   | Median | Range   |
| ----------- | ------ | ------ | ------- |
| Age (years) | 23.91  | 23.5   | 17–34   |
| Height (cm) | 168.68 | 169.5  | 157–177 |
| Weight (kg) | 66.32  | 68     | 53–75   |

## 3. Distribution Findings

**Total Sleep Time**

- Mean: 7.91 hours; median: 8.25 hours.

- Most observations cluster around 450–600 minutes.

- Left-skewed distribution, with unusually short durations.

- Minimum: 5 minutes; maximum: 773 minutes.

- Very short observations require investigation before interpretation.

**Longest Sleep Interval**

- Mean: 327.62 minutes.

- Wide distribution, indicating substantial variation in uninterrupted sleep intervals.

- Several observations are close to zero.

- Potentially useful for studying sleep continuity.

**Sleep Period Metrics**

- Sleep period mean and standard deviation show concentrated distributions with long tails.

- Extreme observations occur in several variables.

- The exact measurement definitions should be checked before using these metrics in the dashboard.

**Caffeine Consumption**

- Mean: 90.28 mg; median: 65 mg.

- Strongly right-skewed.

- Many observations report little or no caffeine.

- Maximum: 765 mg.

- Potential explanatory variable for sleep-related comparisons.

**Handgrip Strength**

- Mean: 33.66 kg.

- Concentrated around 25–35 kg, with higher observations extending toward 50 kg.

- Potential recovery indicator, but substantial missingness limits its usefulness.

**Demographics**

- Participants are relatively young, with a mean age of 23.91 years.

- Age distribution is irregular, reflecting the small sample.

- Results apply to the observed athlete group, not the general population.

## 4. Missing Data

| Variable                     | Missing |
| ---------------------------- | ------- |
| Wearable sleep measurements  | 10.27%  |
| Sleep quality                | 26.22%  |
| Fatigue                      | 24.86%  |
| Readiness                    | 24.32%  |
| Self-reported sleep duration | 24.32%  |
| Screen time                  | 43.24%  |
| Caffeine timing              | 43.78%  |
| Handgrip strength            | 61.62%  |
| Energy                       | 91.08%  |
| Caffeine (mg)                | 0%      |

**Observations:**

- Wearable sleep measurements have relatively good coverage.

- Subjective questionnaire data have higher missingness.

- Energy and handgrip strength have limited analytical usefulness.

- Caffeine values are complete, but the treatment of unreported consumption should be verified.

- Missing data must not be replaced with zeros.

## 5. Participant-Level Findings

- Participants contribute between 17 and 20 daily records.

- Average recorded sleep duration differs considerably between participants.

- Lowest participant mean: approximately 335 minutes (5.59 hours).

- Highest participant mean: approximately 538 minutes (8.97 hours).

- Some participants have substantially shorter average sleep durations than others.

**Interpretation:** Individual-level monitoring is valuable because aggregated study averages can obscure meaningful participant differences.

## 6. Proposed Calculated Metrics

| Metric                          | Calculation / Definition                           |
| ------------------------------- | -------------------------------------------------- |
| Sleep duration (hours)          | `total_sleep_time / 60`                            |
| Average sleep per participant   | Mean valid sleep duration                          |
| Short-sleep percentage          | % of valid records below 7 hours                   |
| Sleep variability               | SD of sleep duration per participant               |
| Longest sleep interval ratio    | Longest interval / total sleep time                |
| Wearable data completeness      | Valid sleep records / expected observations        |
| Survey completeness             | Valid subjective responses / expected observations |
| Self-report discrepancy         | Self-reported minus wearable sleep duration        |
| Average caffeine consumption    | Mean caffeine intake per participant               |
| Sleep quality by caffeine group | Median sleep quality across caffeine groups        |

The longest-interval ratio is only a descriptive proxy for sleep continuity, not a validated clinical sleep-efficiency measure.

## 7. Proposed Dashboard

**Target audience:** Sleep researchers and sports scientists.

**Primary objective:** Monitor participant-level sleep patterns, recovery indicators, and data completeness throughout the study.

### Three main visualizations

1. **Line chart:** Sleep duration across study days, with participant filtering.

2. **Scatter plot:** Caffeine consumption versus sleep duration or subjective sleep quality.

3. **Heatmap:** Participants × study days, colored by sleep duration, with missing measurements clearly indicated.

### KPI Indicators

- Mean sleep duration

- Median sleep quality

- Short-sleep percentage

- Wearable completeness

### Filters

- Participant

- Study day

- Match day

- Weekday

---

### Identifiers & Demographics

- `source_row_index` | Source Row Index: Original CSV row number. Values: Integers.
- `participant_id` | Participant ID: Unique participant identifier. Values: UUID strings.
- `age` | Age: Participant age. Values: 17–34 years.
- `height_cm` | Height (cm): Participant height. Values: 157–177 cm.
- `weight_kg` | Weight (kg): Participant weight. Values: 53–75 kg.

### Sleep Measurements

- `sleep_onset` | Sleep Onset: Time sleep began. Values: HH:MM:SS.
- `sleep_offset` | Sleep Offset: Time sleep ended. Values: HH:MM:SS.
- `total_sleep_time_min` | Total Sleep Time (min): Total recorded sleep. Values: 5–773 min, or null.
- `sleep_intervals` | Sleep Intervals: Number of detected sleep intervals. Values: 1–13, or null.
- `longest_sleep_interval_start` | Longest Interval Start: Start time of longest sleep interval. Values: HH:MM:SS.
- `longest_sleep_interval_end` | Longest Interval End: End time of longest sleep interval. Values: HH:MM:SS.
- `longest_sleep_interval_min` | Longest Sleep Interval (min): Duration of longest interval. Values: 5–773 min, or null.
- `sleep_period_activity_mean` | Mean Sleep Activity: Mean sensor activity during sleep. Values: 3.49–43.83.
- `sleep_period_activity_std` | Sleep Activity SD: Standard deviation of sleep activity. Values: 0.18–129.36.
- `sleep_period_activity_msd` | Sleep Activity MSD: Mean successive difference metric. Values: 0.18–43.38.
- `sleep_quality` | Subjective Sleep Quality: Self-reported sleep quality. Values: Ordinal numeric scale, exact bounds not established.
- `self_reported_sleep_hours` | Self-Reported Sleep Duration (h): Participant-estimated sleep duration. Values: Numeric hours, or null.

### Lifestyle & Caffeine

- `screen_time` | Screen Time: Reported screen exposure. Values: Short, Medium, Long, or null.
- `energy` | Energy Level: Self-reported energy. Values: Ordinal numeric score, or null.
- `cola` | Cola Consumption: Reported cola servings. Values: Numeric count, or null.
- `coffee` | Coffee Consumption: Reported coffee servings. Values: 1, 2, 3, 4 or more, or null.
- `tea` | Tea Consumption: Reported tea servings. Values: Numeric count, or null.
- `espresso` | Espresso Consumption: Reported espresso servings. Values: Numeric count, or null.
- `caffeine_time` | Caffeine Timing: Reported time of caffeine consumption. Values: Morning, Afternoon, Evening, or null.
- `caffeine_mg` | Caffeine Intake (mg): Estimated caffeine consumption. Values: 0–765 mg.
- `caffeine_zero_uncertain` | Uncertain Caffeine Zero: Flags ambiguous zero-consumption records. Values: True, False.

### Recovery & Activity

- `handgrip_kg` | Handgrip Strength (kg): Measured grip strength. Values: 24.2–50.5 kg, or null.
- `fatigue` | Fatigue Level: Self-reported fatigue. Values: Ordinal numeric score, or null.
- `soreness` | Muscle Soreness: Self-reported soreness. Values: Ordinal numeric score, or null.
- `soreness_location_1` | Primary Soreness Location: First reported soreness location. Values: Coded categories, exact definitions unverified.
- `soreness_location_2` | Secondary Soreness Location: Second reported soreness location. Values: Coded categories, exact definitions unverified.
- `readiness` | Readiness Level: Self-reported readiness to perform. Values: Ordinal numeric score, or null.
- `matchday` | Matchday Status: Match-related timing. Values: `MD`, `MD-2`, etc., or null.
- `weekday` | Weekday: Day associated with the observation. Values: Monday–Sunday.

---

_Jakob Balkovec_
