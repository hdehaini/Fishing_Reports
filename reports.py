import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta

# URLs for fishing reports
urls = {
    'seaforth': 'https://www.sportfishingreport.com/landings/seaforth-sportfishing.php',
    'hmlanding': 'https://www.sportfishingreport.com/landings/h&m-landing.php',
    'pointloma': 'https://www.sportfishingreport.com/landings/point-loma-sportfishing.php',
    'fisherman': 'https://www.sportfishingreport.com/landings/fishermans-landing.php',
    'oceanside': 'https://www.sportfishingreport.com/landings/oceanside-sea-center.php',
    'ironclad': 'https://www.sportfishingreport.com/landings/ironclad-sportfishing.php'
}

def remove_ordinal_suffix(date_str):
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

def get_report(url, name, target_date):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the date on the page
    date_element = soup.find('td', class_='scale-title')
    if date_element:
        date_text = date_element.text.strip()
        print(f"Scraped date text for {name}: '{date_text}'")  # Debug print
        try:
            # Extract the date portion from the text
            date_match = re.search(r'(\w+ \d{1,2}(?:th|st|nd|rd)?, \d{4})', date_text)
            if date_match:
                cleaned_date = remove_ordinal_suffix(date_match.group(1))
                print(f"Cleaned date for {name}: '{cleaned_date}'")  # Debug print
                report_date = datetime.strptime(cleaned_date, '%B %d, %Y').date()
            else:
                print(f"Date format error for {name}: {date_text}")  # Debug print
                return pd.DataFrame(), None
        except ValueError as e:
            print(f"Error parsing date for {name}: {e}")  # Debug print
            return pd.DataFrame(), None  # Return an empty DataFrame if the date format is unexpected
        
        if report_date != target_date:
            return pd.DataFrame(), report_date  # Return an empty DataFrame with the found date if the date does not match the target date
    else:
        print(f"No date found for {name}")  # Debug print
        return pd.DataFrame(), None  # Return an empty DataFrame if no date is found
    
    # Find the table with the reports
    table = soup.find('table', class_='scale-table')
    
    reports = []
    if table:
        for row in table.find_all('tr')[2:-2]: # Skip the first two rows (headers) and last 2 rows (footer)
            cols = row.find_all('td')
            if len(cols) == 4:  # Ensure it's a data row
                boat_name = cols[0].text.strip()
                trip_type = cols[1].text.strip()
                anglers_text = cols[2].text.strip()
                anglers = int(re.search(r'\d+', anglers_text).group())  # Extract numeric value
                fish_counts = cols[3].text.strip()
                reports.append({
                    'Source': name,
                    'Boat Name': boat_name,
                    'Trip Type': trip_type,
                    'Anglers': anglers,
                    'Fish Count': fish_counts
                })
    
    return pd.DataFrame(reports), report_date

def get_all_reports(urls, target_date):
    reports = []
    dates = []
    for name, url in urls.items():
        df, report_date = get_report(url, name, target_date)
        if not df.empty:
            reports.append(df)
        if report_date:
            dates.append(report_date)
    if reports:
        return pd.concat(reports, ignore_index=True), dates
    else:
        return pd.DataFrame(), dates  # Return an empty DataFrame if no reports are found

def calculate_averages(df):
    full_day_boats = df[df['Trip Type'].str.contains('Full Day')]
    fish_types = ['Yellowtail', 'Bluefin Tuna', 'Yellowfin Tuna', 'Dorado']
    
    averages = {}
    for fish in fish_types:
        # Extract the fish count for each specific fish type
        fish_counts = full_day_boats['Fish Count'].str.extractall(f'(\d+)\s+{fish}')
        if not fish_counts.empty:
            fish_counts = fish_counts[0].astype(float)
            total_fish = fish_counts.sum()
            total_anglers = full_day_boats['Anglers'].sum()
            if total_anglers > 0:
                averages[fish] = total_fish / total_anglers
            else:
                averages[fish] = 0
        else:
            averages[fish] = 0
    
    return averages

def generate_html(df, averages, title_date, template_path='template.html', output_path='index.html'):
    with open(template_path, 'r') as file:
        template = file.read()

    title = f"Fishing Reports {title_date}"
    
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

    # Insert table rows and title into the template
    html_content = template.replace('<!-- Data will be inserted here by the Python script -->', table_rows)
    html_content = html_content.replace('<!--TITLE-->', title)
    
    # Insert averages into the template
    averages_html = '<div class="averages-list">'
    for fish, avg in averages.items():
        averages_html += f'<div class="average-item"><span>Average {fish} per angler:</span><span class="average-value">{avg:.2f}</span></div>'
    averages_html += '</div>'
    
    html_content = html_content.replace('<!-- Averages will be inserted here by the Python script -->', averages_html)
    
    with open(output_path, 'w') as file:
        file.write(html_content)

if __name__ == '__main__':
    current_date = datetime.now().date()
    previous_date = current_date - timedelta(days=1)

    all_reports_df, dates = get_all_reports(urls, current_date)
    
    if all_reports_df.empty:
        # No current day reports, get previous day's reports
        all_reports_df, _ = get_all_reports(urls, previous_date)
        title_date = previous_date.strftime("%B %d, %Y")
    else:
        title_date = current_date.strftime("%B %d, %Y")

    if not all_reports_df.empty:
        averages = calculate_averages(all_reports_df)
        generate_html(all_reports_df, averages, title_date)
        print(f"Generated report for {title_date}")
    else:
        print("No reports available.")
