# Fishing Reports Project

## Overview
The Fishing Reports project is designed to scrape, process, and display fishing report data from various fishing landing websites. It provides users with up-to-date information about fishing activities, including the types of fish caught, the number of anglers, and trip details. The project also calculates daily averages of catches and generates a dynamic HTML report.

## Features
- **Data Scraping:** Automatically fetches fishing reports from predefined URLs.
- **Data Processing:** Calculates averages and sorts data based on trip types.
- **Report Generation:** Outputs sorted data and averages into an HTML format and saves daily metrics into CSV files.
- **Scheduled Runs:** Designed to run at specific intervals to ensure the latest data is always processed and available.

## Technologies Used
- **Python 3.x:** Main programming language used for scripting.
- **Pandas:** For data manipulation and analysis.
- **Beautiful Soup 4:** For parsing HTML and XML documents.
- **Requests:** For making HTTP requests to web pages.

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Libraries Installation
Run the following command to install the necessary libraries:
```bash
pip install pandas beautifulsoup4 requests
```

## Directory Structure
Ensure your project directory is set up as follows:
```arduino
Fishing_Reports/
│
├── database/
│   ├── (CSV files will be saved here)
│
├── assets/
│   ├── (background image files, etc.)
|
├── js-scripts/
│   ├── chart.js
│   ├── script.js
│
├── py-scripts/
│   ├── main.py
│   ├── fetch_data.py
│   ├── process_data.py
│   ├── generate_report.py
│
├── style/
│   ├── app.css
│
├── webpages/
│   ├── template.html
│
└── README.md
```

## Usage

### Running the Script
Navigate to the `py-scripts` directory and run:
```bash
python main.py
```

This command will execute the data fetching, processing, and report generation process based on the latest data from the configured URLs.

## Viewing Reports
After running the script, open the generated index.html in a web browser to view the formatted fishing reports and daily averages. This file is located in the root directory unless specified otherwise in your script configurations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that is short and to the point. It lets people do anything they want with your code as long as they provide attribution back to you and don’t hold you liable.