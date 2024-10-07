from pandas.api.types import CategoricalDtype

trip_type_order = [
    "1/2 Day AM", "1/2 Day PM", "1/2 Day Twilight", "3/4 Day", "Full Day",
    "Overnight", "1.5 Day", "2 Day", "2.5 Day", "3 Day", "3.5 Day", "4 Day"
]
trip_type_cat = CategoricalDtype(categories=trip_type_order, ordered=True)

TRIP_TYPE = 'Trip Type'

def calculate_averages(df):
    full_day_boats = df[df[TRIP_TYPE].astype(str).str.contains('Full Day', na=False)]
    fish_types = ['Yellowtail', 'Bluefin Tuna', 'Yellowfin Tuna', 'Dorado']
    
    averages = {}
    for fish in fish_types:
        # Filter reports that mention the specific fish type
        relevant_reports = full_day_boats[full_day_boats['Fish Count'].astype(str).str.contains(f'{fish}', na=False)]
        # Extract the fish count for each specific fish type from relevant reports
        fish_counts = relevant_reports['Fish Count'].str.extractall(rf'(\d+)\s+{fish}').astype(int)
        
        if not fish_counts.empty:
            total_fish = fish_counts[0].sum()  # Sum up all counts of this fish
            total_anglers = relevant_reports['Anglers'].sum()  # Sum of anglers only in relevant reports
            
            if total_anglers > 0:
                averages[fish] = total_fish / total_anglers  # Calculate average
            else:
                averages[fish] = 0  # Avoid division by zero
        else:
            averages[fish] = 0  # If no reports mention this fish, set average to zero
    
    return averages

def sort_dataframe(df):
    # Convert TRIP_TYPE column to ordered categorical type
    df[TRIP_TYPE] = df[TRIP_TYPE].astype(trip_type_cat)
    # Check categories after conversion
    print(df[TRIP_TYPE].cat.categories)
    # Sort DataFrame by TRIP_TYPE
    sorted_df = df.sort_values(TRIP_TYPE)
    print(sorted_df[TRIP_TYPE])  # Debugging to see the order after sorting
    return sorted_df