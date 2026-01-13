import pandas as pd

def _analyze_series(series, drop_threshold=0.25):
    data = series.dropna().tolist()

    if len(data) < 2:
        return "not enough data"

    start, end = data[0], data[-1]
    peak, trough = max(data), min(data)

    events = []

    if end > start:
        events.append("ended higher than it started")
    elif end < start:
        events.append("ended lower than it started")
    else:
        events.append("ended at the same value it started")

    if peak != start and peak != end:
        events.insert(0, f"rose to a peak of {peak}")

    sharp_drops = []
    for i in range(1, len(data)):
        change = (data[i] - data[i - 1]) / max(abs(data[i - 1]), 1)
        if change <= -drop_threshold:
            sharp_drops.append(data[i])

    if sharp_drops:
        events.append(f"dropped sharply to {min(sharp_drops)}")

    sentence = "Data " + ", ".join(events[:-1])
    if len(events) > 1:
        sentence += ", and " + events[-1]
    else:
        sentence += events[0]

    return sentence.capitalize() + "."


def explain(data):
    # Accept file path
    if isinstance(data, str):
        if data.endswith(".xlsx"):
            data = pd.read_excel(data)
        elif data.endswith(".csv"):
            data = pd.read_csv(data)
        else:
            raise ValueError("Unsupported file format")

    insights = []

    for col in data.columns:
        if pd.api.types.is_numeric_dtype(data[col]):
            insight = _analyze_series(data[col])
            insights.append(f"{col}: {insight}")
        else:
            insights.append(
                f"{col}: {data[col].nunique()} unique values"
            )

    return "\n".join(insights)

