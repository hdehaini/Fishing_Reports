TRIP_TYPE = "Trip Type"


def calculate_averages(df):
    full_day_boats = df[df[TRIP_TYPE].astype(str).str.contains("Full Day", na=False)]
    fish_types = ["Yellowtail", "Bluefin Tuna", "Yellowfin Tuna", "Dorado"]

    averages = {}
    for fish in fish_types:
        # Filter reports that mention the specific fish type
        relevant_reports = full_day_boats[
            full_day_boats["Fish Count"].astype(str).str.contains(f"{fish}", na=False)
        ]
        # Extract the fish count for each specific fish type from relevant reports
        fish_counts = (
            relevant_reports["Fish Count"]
            .str.extractall(rf"(\d+)\s+{fish}")
            .astype(int)
        )

        if not fish_counts.empty:
            total_fish = fish_counts[0].sum()  # Sum up all counts of this fish
            total_anglers = relevant_reports[
                "Anglers"
            ].sum()  # Sum of anglers only in relevant reports

            if total_anglers > 0:
                averages[fish] = total_fish / total_anglers  # Calculate average
            else:
                averages[fish] = 0  # Avoid division by zero
        else:
            averages[fish] = 0  # If no reports mention this fish, set average to zero

    return averages


def _trip_type_rank(s: str) -> float:
    """Map trip type text to a numeric duration rank in days for sorting.

    Heuristics (non-exhaustive, but covers dynamic variants):
    - 1/2 Day AM/PM/Twilight -> 0.50/0.51/0.52
    - 3/4 Day -> 0.75
    - Full Day (and variants like 'Full Day Coronado Islands') -> 1.0
    - Overnight -> 1.2 (just after Full Day, before 1.5 Day)
    - X Day (e.g., 1.5 Day, 2 Day, 2.5 Day, 3 Day, ...) -> float(X)
    - Extended X Day -> float(X) + 0.05
    - Unrecognized or missing -> 99.0 (sort to bottom)
    """
    if not isinstance(s, str):
        return 99.0
    t = s.strip().lower()

    # Half day variants
    if "1/2 day" in t or "half day" in t:
        if "am" in t:
            return 0.50
        if "pm" in t:
            return 0.51
        if "twilight" in t:
            return 0.52
        return 0.50

    # Three-quarter day
    if "3/4 day" in t:
        return 0.75

    # Full day variants
    if "full day" in t:
        return 1.0

    # Overnight
    if "overnight" in t:
        return 1.2

    # Extended trips (slight bump over the base duration)
    extended_bump = 0.05 if "extended" in t else 0.0

    # Numeric forms like 1.5 Day, 2 Day, 2.5 Day, 3 Day, etc.
    import re

    m = re.search(r"(\d+(?:\.\d+)?)\s*day", t)
    if m:
        try:
            return float(m.group(1)) + extended_bump
        except ValueError:
            pass

    # Fractional like 3/2 Day or other forms
    m2 = re.search(r"(\d+)\s*/\s*(\d+)\s*day", t)
    if m2:
        num = float(m2.group(1))
        den = float(m2.group(2))
        if den:
            return (num / den) + extended_bump

    return 99.0


def sort_dataframe(df):
    # Sort using computed trip duration rank while preserving dynamic variants.
    df = df.copy()
    df["_trip_rank"] = df[TRIP_TYPE].astype(str).apply(_trip_type_rank)
    sorted_df = df.sort_values(
        by=["_trip_rank", "Boat Name", "Source"], kind="mergesort"
    )
    return sorted_df.drop(columns=["_trip_rank"])
