import os
from datetime import datetime
import pandas as pd

def ensure_directory_exists(filename):
    """ Ensure the directory exists. If not, create it. """
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_to_csv(df, filename):
    ensure_directory_exists(filename)  # Ensure the directory exists
    df.to_csv(filename, index=False)
    print(f"Saved sorted data to {filename}")

def append_averages_to_csv(averages, filename):
    now = datetime.now()
    today = now.date()
    current_time = now.time()
    start_time = datetime.strptime('19:00', '%H:%M').time()
    end_time = datetime.strptime('23:59', '%H:%M').time()

    if start_time <= current_time <= end_time:
        # Check if the CSV file exists and has entries
        try:
            df = pd.read_csv(filename)
            if not df.empty:
                last_entry_date = pd.to_datetime(df['Date'].iloc[-1]).date()
                # Check if the last entry is today's date
                if last_entry_date == today:
                    print(f"Daily average already recorded for {today}. No action taken.")
                    return
        except FileNotFoundError:
            # File doesn't exist yet, so we'll create it with the new entry
            df = pd.DataFrame()
            
        data = {'Date': today}
        data.update(averages)
        df = pd.DataFrame([data])
        with open(filename, 'a') as f:
            df.to_csv(f, header=f.tell()==0, index=False)
        print("Averages recorded.")
    else:
        print(f"Current time {current_time} is outside the recording window ({start_time} - {end_time}). No action taken.")

def generate_html(df, averages, title_date, template_path, output_path):
    # Assuming the script is run from within the py-scripts directory, adjust accordingly if not
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_template_path = os.path.join(project_root, template_path)
    
    try:
        with open(full_template_path, 'r') as file:
            template = file.read()
    except FileNotFoundError:
        print(f"Error: The template file was not found at {full_template_path}")
        return

    # Replace the title placeholder with the actual title
    title = f"Fishing Reports {title_date}"
    html_content = template.replace('<!--TITLE-->', title)
    
    # Convert DataFrame to HTML table rows
    table_rows = ''
    for _, row in df.iterrows():
        table_rows += '<tr>'
        table_rows += f'<td>{row["Source"]}</td>'
        table_rows += f'<td>{row["Boat Name"]}</td>'
        table_rows += f'<td>{row["Trip Type"]}</td>'
        table_rows += f'<td>{row["Anglers"]}</td>'
        table_rows += f'<td>{row["Fish Count"]}</td>'
        table_rows += '</tr>'

    # Insert table rows into the template
    html_content = html_content.replace('<!-- Data will be inserted here by the Python script -->', table_rows)
    
    # Insert averages into the template
    averages_html = '<div class="averages-list">'
    for fish, avg in averages.items():
        averages_html += f'<div class="average-item"><span>Average <u>{fish}</u> per angler:</span><span class="average-value">{avg:.2f}</span></div>'
    averages_html += '<p>Averages reflect counts from full day boats that caught  specific fish types only</p></div>'
    
    html_content = html_content.replace('<!-- Averages will be inserted here by the Python script -->', averages_html)
    
    # Insert the date into the template
    html_content = html_content.replace('<!--DATE-->', title_date)
    
    with open(output_path, 'w') as file:
        file.write(html_content)
