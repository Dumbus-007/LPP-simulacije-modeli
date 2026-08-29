import pandas as pd
import networkx as nx

# 1. Naložimo vsa postajališča in GTFS tabele
print("Nalagam GTFS podatke in all_lines_trips.csv...")
stops_df = pd.read_csv('lpp_gtfs/stops.txt')
stop_times_df = pd.read_csv('lpp_gtfs/stop_times.txt')
trips_df = pd.read_csv('lpp_gtfs/trips.txt')
routes_df = pd.read_csv('lpp_gtfs/routes.txt')
all_lines_trips = pd.read_csv('model 1/all_lines_trips.csv')

# Ustvarimo slovarje za preslikavo stop_id -> stop_code in route_id -> route_short_name
stop_id_to_code = dict(zip(stops_df['stop_id'].astype(str), stops_df['stop_code'].astype(str)))
route_id_to_name = dict(zip(routes_df['route_id'], routes_df['route_short_name'].astype(str)))

# Ustvarimo usmerjen graf
G1 = nx.DiGraph()

# Dodamo vozlišča
for _, row in stops_df.iterrows():
    stop_code = str(row['stop_code'])
    G1.add_node(
        stop_code, 
        name=row['stop_name'], 
        lat=float(row['stop_lat']), 
        lon=float(row['stop_lon'])
    )

# Združimo stop_times z trips, da vemo kateri route_id pripada kateri vožnji
merged_stops = stop_times_df.merge(trips_df[['trip_id', 'route_id']], on='trip_id')
merged_stops['stop_id'] = merged_stops['stop_id'].astype(str)

# Slovar za shranjevanje uteži in linij na povezavah
edge_weights = {}
edge_routes = {}  # Slovar obliki: (u, v) -> set(route_short_name)

print("Obdelujem linije in dodajam uteži ter imena linij...")

# 2. Zanka gre po vsaki LINIJI (route_id) iz datoteke all_lines_trips.csv
for _, line_row in all_lines_trips.iterrows():
    route_id = line_row['route_id']
    num_trips = float(line_row['num_trips'])

    if num_trips <= 0: # nekatere linije nimajo voženj na delavnike
        continue
    
    route_short_name = route_id_to_name.get(route_id, str(route_id))
    
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
            # Preslikamo stop_id v stop_code
            u_code = stop_id_to_code.get(stop_list[i])
            v_code = stop_id_to_code.get(stop_list[i+1])
            
            if u_code and v_code:
                route_edges.add((u_code, v_code))
            
    # Vsaki unikatni povezavi te linije prištejemo njene dnevne vožnje in dodamo ime linije
    for u, v in route_edges:
        edge_weights[(u, v)] = edge_weights.get((u, v), 0) + num_trips
        
        if (u, v) not in edge_routes:
            edge_routes[(u, v)] = set()
        edge_routes[(u, v)].add(route_short_name)

# 3. Prenesemo v graf
for (u, v), weight in edge_weights.items():
    # Seznam linij pretvorimo v niz, ločen s vejicami (npr. "1, 6, 11")
    lines_str = ", ".join(sorted(edge_routes[(u, v)]))
    G1.add_edge(u, v, weight=round(weight, 2), routes=lines_str)

# Odstranjevanje izoliranih/manjših komponent
if not nx.is_weakly_connected(G1):
    largest_cc = max(nx.weakly_connected_components(G1), key=len)
    removed_nodes_count = G1.number_of_nodes() - len(largest_cc)
    
    # Obdržimo le največjo komponento
    G1 = G1.subgraph(largest_cc).copy()
    print(f"- Odstranjena manjša komponenta ({removed_nodes_count} vozlišč).")

print(f"\nGraf je zgrajen!")
print(f"- Število vozlišč: {G1.number_of_nodes()}")
print(f"- Število usmerjenih povezav: {G1.number_of_edges()}")

# Shranimo v GraphML
nx.write_graphml(G1, "model 1/model1_frekvenca.graphml")
print("\nModel 1 je uspešno shranjen kot 'model 1/model1_frekvenca.graphml'.")