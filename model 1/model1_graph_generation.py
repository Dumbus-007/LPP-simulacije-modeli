import pandas as pd
import networkx as nx

# 1. Naložimo vsa postajališča in GTFS tabele
print("Nalagam GTFS podatke in all_lines_trips.csv...")
stops_df = pd.read_csv('lpp_gtfs/stops.txt')
stop_times_df = pd.read_csv('lpp_gtfs/stop_times.txt')
trips_df = pd.read_csv('lpp_gtfs/trips.txt')
all_lines_trips = pd.read_csv('model 1/all_lines_trips.csv')

# Ustvarimo usmerjen graf
G1 = nx.DiGraph()

# Dodamo vozlišča
for _, row in stops_df.iterrows():
    G1.add_node(
        str(row['stop_id']), 
        name=row['stop_name'], 
        lat=float(row['stop_lat']), 
        lon=float(row['stop_lon'])
    )

# Združimo stop_times z trips, da vemo kateri route_id pripada kateri vožnji
merged_stops = stop_times_df.merge(trips_df[['trip_id', 'route_id']], on='trip_id')
merged_stops['stop_id'] = merged_stops['stop_id'].astype(str)

edge_weights = {}

print("Obdelujem linije in dodajam uteži po Pristopu B...")

# 2. Zanka gre po vsaki LINIJI (route_id) iz datoteke all_lines_trips.csv
for _, line_row in all_lines_trips.iterrows():
    route_id = line_row['route_id']
    num_trips = float(line_row['num_trips'])
    
    # Pridobimo vse postanke za to konkretno linijo
    route_stops = merged_stops[merged_stops['route_id'] == route_id]
    if route_stops.empty:
        continue

    # Poiščemo vse unikatne zaporedne povezave (u -> v), ki se pojavijo na tej liniji
    route_edges = set()
    for trip_id, group in route_stops.groupby('trip_id'):
        group_sorted = group.sort_values(by='stop_sequence')
        stop_list = group_sorted['stop_id'].tolist()
        
        for i in range(len(stop_list) - 1):
            u = stop_list[i]
            v = stop_list[i+1]
            route_edges.add((u, v))
            
    # Vsaki unikatni povezavi te linije prištejemo njene dnevne vožnje
    for u, v in route_edges:
        edge_weights[(u, v)] = edge_weights.get((u, v), 0) + num_trips

# 3. Prenesemo v graf
for (u, v), weight in edge_weights.items():
    G1.add_edge(u, v, weight=round(weight, 2))

print(f"\nGraf je zgrajen!")
print(f"- Število vozlišč: {G1.number_of_nodes()}")
print(f"- Število usmerjenih povezav: {G1.number_of_edges()}")

# Preverjanje največje uteži
max_edge = max(edge_weights.items(), key=lambda x: x[1])
print(f"- Največja frekvenca na povezavi: {max_edge[1]} voženj na dan (med postajama {max_edge[0]}).")

# Shranimo v GraphML
nx.write_graphml(G1, "model 1/model1_frekvenca.graphml")
print("\nModel 1 je uspešno shranjen kot 'model 1/model1_frekvenca.graphml'.")