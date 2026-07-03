import os
from datetime import datetime
import pandas as pd
import pytz

# Project root: one level up from this file's directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_directory_exists(filename):
    """Ensure the directory exists. If not, create it."""
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_to_csv(df, filename):
    # Resolve to project root if relative path provided
    full_path = (
        filename if os.path.isabs(filename) else os.path.join(PROJECT_ROOT, filename)
    )
    ensure_directory_exists(full_path)
    df.to_csv(full_path, index=False)
    print(f"Saved sorted data to {full_path}")


def append_averages_to_csv(averages, filename):
    # Set your local timezone
    local_tz = pytz.timezone("America/Los_Angeles")

    now = datetime.now(local_tz)
    today = now.date()
    full_path = (
        filename if os.path.isabs(filename) else os.path.join(PROJECT_ROOT, filename)
    )

    try:
        existing = pd.read_csv(full_path)
    except FileNotFoundError:
        existing = pd.DataFrame()

    data = {"Date": today.isoformat()}
    data.update(averages)
    new_row = pd.DataFrame([data])

    if not existing.empty and "Date" in existing.columns:
        existing["Date"] = existing["Date"].astype(str)
        existing = existing[existing["Date"] != today.isoformat()]

    combined = pd.concat([existing, new_row], ignore_index=True)
    ensure_directory_exists(full_path)
    combined.to_csv(full_path, index=False)
    print(f"Averages recorded for {today}.")


def generate_html(df, averages, title_date, template_path, output_path):
    # Resolve template and output paths relative to project root
    full_template_path = (
        template_path
        if os.path.isabs(template_path)
        else os.path.join(PROJECT_ROOT, template_path)
    )

    try:
        with open(full_template_path, "r") as file:
            template = file.read()
    except FileNotFoundError:
        print(f"Error: The template file was not found at {full_template_path}")
        return

    # Replace the title placeholder with the actual title
    title = f"Fishing Reports {title_date}"
    html_content = template.replace("<!--TITLE-->", title)

    # Convert DataFrame to HTML table rows
    table_rows = ""
    for _, row in df.iterrows():
        table_rows += "<tr>"
        table_rows += f'<td>{row["Source"]}</td>'
        table_rows += f'<td>{row["Boat Name"]}</td>'
        table_rows += f'<td>{row["Trip Type"]}</td>'
        table_rows += f'<td>{row["Anglers"]}</td>'
        table_rows += f'<td>{row["Fish Count"]}</td>'
        table_rows += "</tr>"

    # Insert table rows into the template
    html_content = html_content.replace(
        "<!-- Data will be inserted here by the Python script -->", table_rows
    )

    # Insert averages into the template
    averages_html = '<div class="averages-list">'
    for fish, avg in averages.items():
        averages_html += f'<div class="average-item"><span>Average <u>{fish}</u> per angler:</span><span class="average-value">{avg:.2f}</span></div>'
    averages_html += "<p>Averages reflect counts from full day boats that caught  specific fish types only</p></div>"

    html_content = html_content.replace(
        "<!-- Averages will be inserted here by the Python script -->", averages_html
    )

    # Insert the date into the template
    html_content = html_content.replace("<!--DATE-->", title_date)

    full_output_path = (
        output_path
        if os.path.isabs(output_path)
        else os.path.join(PROJECT_ROOT, output_path)
    )
    ensure_directory_exists(full_output_path)
    with open(full_output_path, "w") as file:
        file.write(html_content)
    print(f"Generated HTML report at {full_output_path}")


def append_reports_history(df: pd.DataFrame, report_date, filename: str):
    """Append the day's full report rows to a history CSV as normalized records.

    - report_date: datetime.date object representing the report day
    - filename: relative or absolute path to CSV (columns: Date, Source, Boat Name, Trip Type, Anglers, Fish Count)
    """
    full_path = (
        filename if os.path.isabs(filename) else os.path.join(PROJECT_ROOT, filename)
    )
    ensure_directory_exists(full_path)

    # Normalize data
    out_df = df.copy()
    out_df.insert(0, "Date", pd.to_datetime(report_date).date().isoformat())

    # Keep only expected columns (if present)
    expected_cols = [
        "Date",
        "Source",
        "Boat Name",
        "Trip Type",
        "Anglers",
        "Fish Count",
    ]
    out_df = out_df[[c for c in expected_cols if c in out_df.columns]]

    # If file exists, drop any existing rows for this date to avoid duplication
    try:
        existing = pd.read_csv(full_path)
        existing = existing[existing["Date"] != report_date.isoformat()]
        combined = pd.concat([existing, out_df], ignore_index=True)
        combined.to_csv(full_path, index=False)
    except FileNotFoundError:
        out_df.to_csv(full_path, index=False)
    print(f"Appended {len(out_df)} rows to {full_path}")
