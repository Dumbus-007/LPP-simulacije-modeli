import csv
import os
from collections import defaultdict, Counter
from datetime import datetime

def count_all_lines():
    gtfs_dir = "lpp_gtfs"
    output_csv = "model 1/all_lines_trips.csv"
    
    # 1. Load routes
    routes = {}
    routes_file = os.path.join(gtfs_dir, "routes.txt")
    with open(routes_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            routes[row["route_id"]] = {
                "route_id": row["route_id"],
                "route_short_name": row["route_short_name"],
                "route_long_name": row.get("route_long_name", ""),
                "route_desc": row.get("route_desc", "")
            }
            
    # 2. Load weekday service_ids
    weekday_services = {}
    calendar_dates_file = os.path.join(gtfs_dir, "calendar_dates.txt")
    with open(calendar_dates_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row["date"]
            dt = datetime.strptime(date_str, "%Y%m%d")
            # 0=Monday, 4=Friday
            if dt.weekday() < 5:
                weekday_services[date_str] = row["service_id"]
                
    valid_service_ids = set(weekday_services.values())
    
    # 3. Count trips per route per service
    # trip_counts[route_id][service_id] = number of trips
    trip_counts = defaultdict(lambda: defaultdict(int))
    trips_file = os.path.join(gtfs_dir, "trips.txt")
    
    with open(trips_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r_id = row["route_id"]
            s_id = row["service_id"]
            if s_id in valid_service_ids:
                trip_counts[r_id][s_id] += 1
                
    # 4. Calculate the general weekday trips (mode) and write CSV
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["route_id", "route_short_name", "route_long_name", "route_desc", "num_trips"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r_id, route_info in routes.items():
            # Collect the number of trips this route makes on each weekday
            counts_list = []
            for s_id in valid_service_ids:
                counts_list.append(trip_counts[r_id].get(s_id, 0))
                
            mode_count = 0
            if counts_list:
                # The most common trip count across all weekdays is our "general" count
                mode_count = Counter(counts_list).most_common(1)[0][0]
                
            writer.writerow({
                "route_id": route_info["route_id"],
                "route_short_name": route_info["route_short_name"],
                "route_long_name": route_info["route_long_name"],
                "route_desc": route_info["route_desc"],
                "num_trips": mode_count
            })
            
    print(f"Successfully processed {len(routes)} bus lines.")
    print(f"Data saved to: {output_csv}")

if __name__ == "__main__":
    count_all_lines()
