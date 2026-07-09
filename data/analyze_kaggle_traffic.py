import pandas as pd

df = pd.read_csv("data/raw/kaggle_traffic.csv")

# ---- Parse hour from Time column ----
df["hour"] = pd.to_datetime(df["Time"], format="%I:%M:%S %p").dt.hour

# ---- Map day of week to weekday/weekend ----
weekend_days = {"Saturday", "Sunday"}
df["day_type"] = df["Day of the week"].apply(lambda d: "weekend" if d in weekend_days else "weekday")

# ---- Average total vehicle count per (day_type, hour) ----
hourly = df.groupby(["day_type", "hour"])["Total"].mean().reset_index()
hourly.to_csv("data/raw/hourly_traffic_curve.csv", index=False)

print("Hourly average traffic volume by day type:")
print(hourly.to_string(index=False))

# ---- Find peak windows per day_type ----
def find_peak_windows(day_type, window_size=3, num_windows=2):
    sub = hourly[hourly["day_type"] == day_type].sort_values("hour").reset_index(drop=True)
    baseline = sub["Total"].mean()

    windows = []
    for start in range(0, 24 - window_size + 1):
        window = sub[(sub["hour"] >= start) & (sub["hour"] < start + window_size)]
        if len(window) == window_size:
            avg = window["Total"].mean()
            windows.append((start, start + window_size, avg))

    windows.sort(key=lambda w: -w[2])

    selected = []
    for w in windows:
        if all(w[0] >= s[1] or w[1] <= s[0] for s in selected):  # non-overlapping
            selected.append(w)
        if len(selected) == num_windows:
            break

    print(f"\n{day_type} baseline avg: {baseline:.1f}")
    for start, end, avg in selected:
        ratio = avg / baseline
        print(f"  Peak window {start}-{end}h: avg={avg:.1f}, ratio to baseline={ratio:.2f}")

    return selected, baseline

weekday_windows, weekday_baseline = find_peak_windows("weekday", num_windows=2)
weekend_windows, weekend_baseline = find_peak_windows("weekend", num_windows=1)