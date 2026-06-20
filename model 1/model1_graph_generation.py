import pandas as pd
import networkx as nx

# 1. Naložimo vsa postajališča (Vozlišča)
# Predpostavljamo, da je mapa 'lpp_gtfs' v istem imeniku
stops_df = pd.read_csv('lpp_gtfs/stops.txt')

# 2. Za pravilno povezovanje postajališč potrebujemo zaporedje (stop_times.txt)
# stop_times nam pove, kateri trip (vožnja) obišče katero postajo in kdaj
stop_times_df = pd.read_csv('lpp_gtfs/stop_times.txt')
trips_df = pd.read_csv('lpp_gtfs/trips.txt')

# 3. Naložimo vašo datoteko s številom voženj za posamezne linije
# Predpostavljam, da ima stolpca: 'route_id' (ali 'trip_id') in 'num_trips' (število voženj na dan)
all_lines_trips = pd.read_csv('model 1/all_lines_trips.csv')

print("Podatki uspešno naloženi. Začenjam z gradnjo grafa...")

# Ustvarimo usmerjen graf
G1 = nx.DiGraph()

# Dodamo vozlišča z dodatnimi atributi (ime, koordinati, če jih potrebujete)
for _, row in stops_df.iterrows():
    G1.add_node(
        row['stop_id'], 
        name=row['stop_name'], 
        lat=row['stop_lat'], 
        lon=row['stop_lon']
    )

# Združimo stop_times in trips, da vemo, kateri liniji (route_id) pripada kateri stop_time
# Nato dodamo še podatek o številu dnevnih voženj iz vaše datoteke
merged_stops = stop_times_df.merge(trips_df[['trip_id', 'route_id']], on='trip_id')
merged_stops = merged_stops.merge(all_lines_trips[['route_id', 'num_trips']], on='route_id')

# Sortiramo po trip_id in stop_sequence, da dobimo pravilno zaporedje vožnje autobusov
merged_stops = merged_stops.sort_values(by=['trip_id', 'stop_sequence'])

# Ustvarimo slovar, kjer bomo seštevali vožnje med pari postajališč
# Ključ bo (source_stop, target_stop), vrednost pa vsota voženj
edge_weights = {}

# Grupiramo po posameznih vožnjah (trips) in poiščemo zaporedne povezave
for trip_id, group in merged_stops.groupby('trip_id'):
    # Pridobimo seznam postajališč v vrstnem redu za ta konkretni trip
    stop_list = group['stop_id'].tolist()
    # Število dnevnih voženj, ki jih ta linija predstavlja
    daily_trips = group['num_trips'].iloc[0] 
    
    # Ustvarimo povezave med zaporednimi postajami: (stop A -> stop B)
    for i in range(len(stop_list) - 1):
        u = stop_list[i]
        v = stop_list[i+1]
        
        # Če avtobus pelje od u do v, prištejemo število dnevnih voženj te linije
        if (u, v) in edge_weights:
            edge_weights[(u, v)] += daily_trips
        else:
            edge_weights[(u, v)] = daily_trips

# Prenesemo povezave in njihove izračunane uteži v naš NetworkX graf
for (u, v), weight in edge_weights.items():
    G1.add_edge(u, v, weight=weight)

print(f"Graf je zgrajen! Število vozlišč (postaj): {G1.number_of_nodes()}, Število usmerjenih povezav: {G1.number_of_edges()}")

# Shranimo prvi model v datoteko GraphML za kasnejše simulacije
nx.write_graphml(G1, "model1_frekvenca.graphml")
print("Model 1 uspešno shranjen kot 'model1_frekvenca.graphml'.")