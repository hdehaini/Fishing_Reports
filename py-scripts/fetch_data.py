import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd

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