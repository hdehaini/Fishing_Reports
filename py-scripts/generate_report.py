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
    # Ensure the directory exists
    ensure_directory_exists(filename)

    # Get current date and time
    now = datetime.now()
    today = now.date()
    current_time = now.time()

    # Define the time window
    start_time = datetime.strptime('19:50', '%H:%M').time()
    end_time = datetime.strptime('20:15', '%H:%M').time()

    # Check if current time is within the time window
    if start_time <= current_time <= end_time:
        # Create a DataFrame from the averages dictionary with today's date
        data = {'Date': today}
        data.update(averages)
        df = pd.DataFrame([data])
        # Append to CSV, creating the file if it does not exist
        with open(filename, 'a') as f:
            df.to_csv(f, header=f.tell()==0, index=False)
        print("Averages recorded.")
    else:
        print("Current time is outside the recording window. No action taken.")

def generate_html(df, averages, title_date, template_path, output_path):
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Get the parent directory of the script file
    full_template_path = os.path.join(base_dir, template_path)
    full_output_path = os.path.join(base_dir, output_path)
    
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
    averages_html += '<p>Averages reflect counts from boats catching specific fish types only</p></div>'
    
    html_content = html_content.replace('<!-- Averages will be inserted here by the Python script -->', averages_html)
    
    # Insert the date into the template
    html_content = html_content.replace('<!--DATE-->', title_date)
    
    with open(output_path, 'w') as file:
        file.write(html_content)
