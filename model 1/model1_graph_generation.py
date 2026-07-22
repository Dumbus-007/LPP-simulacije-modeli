import pandas as pd
import networkx as nx
from datetime import datetime

# 1. Naložimo vsa postajališča (Vozlišča)
stops_df = pd.read_csv('lpp_gtfs/stops.txt')
stop_times_df = pd.read_csv('lpp_gtfs/stop_times.txt')
trips_df = pd.read_csv('lpp_gtfs/trips.txt')
calendar_dates_df = pd.read_csv('lpp_gtfs/calendar_dates.txt')

print("Podatki uspešno naloženi. Filtriram delovne dni...")

# 2. Najdemo le tiste service_id, ki veljajo za delovne dni (pon-pet)
weekday_services = set()
for _, row in calendar_dates_df.iterrows():
    dt = datetime.strptime(str(row["date"]), "%Y%m%d")
    if dt.weekday() < 5:  # 0=Ponedeljek, 4=Petek
        weekday_services.add(row["service_id"])

# Najdemo vse veljavne delovne vožnje (trips)
valid_weekday_trips = set(trips_df[trips_df['service_id'].isin(weekday_services)]['trip_id'])

# 3. Ustvarimo usmerjen graf
G1 = nx.DiGraph()

for _, row in stops_df.iterrows():
    G1.add_node(
        str(row['stop_id']), 
        name=row['stop_name'], 
        lat=float(row['stop_lat']), 
        lon=float(row['stop_lon'])
    )

# 4. Filtriramo stop_times le za veljavne delovne vožnje in uredi zaporedje
valid_stop_times = stop_times_df[stop_times_df['trip_id'].isin(valid_weekday_trips)].copy()
valid_stop_times = valid_stop_times.sort_values(by=['trip_id', 'stop_sequence'])

edge_weights = {}

# 5. Preštejemo dejanske vožnje: vsak trip_id predstavlja TOČNO 1 vožnjo (+1)
for trip_id, group in valid_stop_times.groupby('trip_id'):
    stop_list = group['stop_id'].astype(str).tolist()
    
    for i in range(len(stop_list) - 1):
        u = stop_list[i]
        v = stop_list[i+1]
        
        # Vsaka vožnja doda točno 1
        edge_weights[(u, v)] = edge_weights.get((u, v), 0) + 1

# 6. Prenesemo v graf
for (u, v), weight in edge_weights.items():
    G1.add_edge(u, v, weight=weight)

print(f"Graf je zgrajen! Število vozlišč: {G1.number_of_nodes()}, Število usmerjenih povezav: {G1.number_of_edges()}")

# Preverjanje največje uteži
max_edge = max(edge_weights.items(), key=lambda x: x[1])
print(f"Največja frekvenca na povezavi: {max_edge[1]} voženj na dan (povezava {max_edge[0]}).")

nx.write_graphml(G1, "model 1/model1_frekvenca.graphml")
print("Model 1 uspešno shranjen kot 'model1_frekvenca.graphml'.")