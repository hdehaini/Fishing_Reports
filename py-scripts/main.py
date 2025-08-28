from datetime import datetime, timedelta
from fetch_data import get_all_reports
from process_data import sort_dataframe, calculate_averages
from generate_report import (
    save_to_csv,
    append_averages_to_csv,
    generate_html,
    append_reports_history,
)

if __name__ == "__main__":
    # URLs for fishing reports
    urls = {
        "seaforth": "https://www.sportfishingreport.com/landings/seaforth-sportfishing.php",
        "hmlanding": "https://www.sportfishingreport.com/landings/h&m-landing.php",
        "pointloma": "https://www.sportfishingreport.com/landings/point-loma-sportfishing.php",
        "fisherman": "https://www.sportfishingreport.com/landings/fishermans-landing.php",
        "oceanside": "https://www.sportfishingreport.com/landings/oceanside-sea-center.php",
        "ironclad": "https://www.sportfishingreport.com/landings/ironclad-sportfishing.php",
    }
    current_date = datetime.now().date()
    previous_date = current_date - timedelta(days=1)

    all_reports_df, dates = get_all_reports(urls, current_date)
    if all_reports_df.empty:
        all_reports_df, _ = get_all_reports(urls, previous_date)
        title_date = previous_date.strftime("%B %d, %Y")
    else:
        title_date = current_date.strftime("%B %d, %Y")

    if not all_reports_df.empty:
        sorted_df = sort_dataframe(all_reports_df)
        save_to_csv(sorted_df, "database/sorted_fishing_reports.csv")
        averages = calculate_averages(sorted_df)
        append_averages_to_csv(averages, "./database/daily_averages.csv")
        generate_html(sorted_df, averages, title_date, "template.html", "index.html")
        # Append daily full table to history file
        report_date = datetime.strptime(title_date, "%B %d, %Y").date()
        append_reports_history(sorted_df, report_date, "database/reports_history.csv")
        print(f"Generated report for {title_date}")
    else:
        print("No reports available.")
