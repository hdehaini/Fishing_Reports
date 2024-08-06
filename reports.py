import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

# URLs for fishing reports
urls = {
    'seaforth': 'https://www.sportfishingreport.com/landings/seaforth-sportfishing.php',
    'hmlanding': 'https://www.sportfishingreport.com/landings/h&m-landing.php',
    'pointloma': 'https://www.sportfishingreport.com/landings/point-loma-sportfishing.php',
    'fisherman': 'https://www.sportfishingreport.com/landings/fishermans-landing.php',
    'oceanside': 'https://www.sportfishingreport.com/landings/oceanside-sea-center.php',
    'ironclad': 'https://www.sportfishingreport.com/landings/ironclad-sportfishing.php'
}

def get_report(url, name):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
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
    
    return pd.DataFrame(reports)

def get_all_reports(urls):
    reports = []
    for name, url in urls.items():
        df = get_report(url, name)
        reports.append(df)
    return pd.concat(reports, ignore_index=True)

def calculate_averages(df):
    full_day_boats = df[df['Trip Type'].str.contains('Full Day')]
    fish_types = ['Yellowtail', 'Bluefin Tuna', 'Yellowfin Tuna', 'Dorado']
    
    averages = {}
    for fish in fish_types:
        # Extract the fish count for each specific fish type
        fish_counts = full_day_boats['Fish Count'].str.extractall(f'(\d+)\s+{fish}')
        fish_counts = fish_counts[0].astype(float)
        
        if not fish_counts.empty:
            total_fish = fish_counts.sum()
            total_anglers = full_day_boats['Anglers'].sum()
            if total_anglers > 0:
                averages[fish] = total_fish / total_anglers
            else:
                averages[fish] = 0
        else:
            averages[fish] = 0
    
    return averages


def generate_html(df, averages, template_path='index.html', output_path='output.html'):
    with open(template_path, 'r') as file:
        template = file.read()

    # Get the current date
    current_date = datetime.now().strftime("%B %d, %Y")
    title = f"Fishing Reports {current_date}"
    
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
    averages_html = '<ul>'
    for fish, avg in averages.items():
        averages_html += f'<li>Average {fish} per angler: {avg:.2f}</li>'
    averages_html += '</ul>'
    
    html_content = html_content.replace('<!-- Averages will be inserted here by the Python script -->', averages_html)
    
    with open(output_path, 'w') as file:
        file.write(html_content)

if __name__ == '__main__':
    all_reports_df = get_all_reports(urls)
    averages = calculate_averages(all_reports_df)
    generate_html(all_reports_df, averages)
