import math
import os
from collections import defaultdict
import pandas as pd
import networkx as nx

def haversine(lat1, lon1, lat2, lon2):
    """Izračuna razdaljo v metrih med dvema GPS koordinatama."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def generate_model_3():
    # 1. Naložimo Model 1
    print("Nalagam Model 1...")
    G1 = nx.read_graphml("model 1/model1_frekvenca.graphml")
    
    # Ustvarimo usmerjen MULTIGRAF za Model 3
    G3 = nx.MultiDiGraph()
    
    # Prenesemo vozlišča
    for node, data in G1.nodes(data=True):
        G3.add_node(node, **data)
    
    # Konstante (vse v sekundah ali metrih)
    SERVICE_WINDOW = 18 * 3600  # 18 ur = 64800 sekund
    WALK_THRESHOLD = 300        # 300 metrov
    WALK_SPEED = 1.4            # 1.4 m/s (pribl. 5 km/h)
    
    # 2. Izračun čakalnih dob neposredno iz uteži (frekvenc) Modela 1
    print("Računam čakalne dobe iz frekvenc Modela 1 za BUS povezave...")
    stop_outgoing_waits = defaultdict(list)
    skipped_bus_edges = 0
    
    # Obdelamo vse avtobusne povezave iz Modela 1
    for u, v, data in G1.edges(data=True):
        count = float(data.get('weight', 0.0))
        
        # Če je število voženj 0 ali manj, povezavo preskočimo
        if count <= 0:
            skipped_bus_edges += 1
            continue
            
        # Čas čakanja
        wait_penalty_sec = SERVICE_WINDOW / (2.0 * count)
        
        # Prenesemo vse obstoječe atribute in dodamo utež ter tip
        edge_attr = dict(data)
        edge_attr['weight'] = round(wait_penalty_sec, 2)
        edge_attr['type'] = "BUS"
        
        # BUS povezava v Modelu 3
        G3.add_edge(u, v, **edge_attr)
        
        # Beležimo izhodne čakalne dobe za posamezno vozlišče
        stop_outgoing_waits[u].append(wait_penalty_sec)

    # 3. Izračun povprečnega časa čakanja na vsakem vozlišču
    node_avg_wait_sec = {}
    terminal_nodes = set()
    
    for node in G3.nodes():
        waits = stop_outgoing_waits.get(node, [])
        if waits:
            node_avg_wait_sec[node] = sum(waits) / len(waits)
        else:
            # Vozlišče nima izhodnih avtobusnih linij (je končna postaja)
            terminal_nodes.add(node)
            node_avg_wait_sec[node] = 0.0  # Na končni postaji potnik ne čaka več na izhodni avtobus

    print(f"- Število končnih postaj (brez izhodnih BUS povezav): {len(terminal_nodes)}")

    # 4. Dodajanje WALK povezav (< 300m) z utežmi v SEKUNDAH
    print("Računam in dodajam peš povezave (WALK)...")
    nodes_list = list(G3.nodes(data=True))
    walk_edges_count = 0
    terminal_walk_count = 0
    
    for i in range(len(nodes_list)):
        n1, data1 = nodes_list[i]
        
        lat1 = data1.get('lat') or data1.get('stop_lat')
        lon1 = data1.get('lon') or data1.get('stop_lon')
        if lat1 is None or lon1 is None:
            continue
            
        lat1, lon1 = float(lat1), float(lon1)
        
        for j in range(i + 1, len(nodes_list)):
            n2, data2 = nodes_list[j]
            lat2 = data2.get('lat') or data2.get('stop_lat')
            lon2 = data2.get('lon') or data2.get('stop_lon')
            if lat2 is None or lon2 is None:
                continue
                
            lat2, lon2 = float(lat2), float(lon2)
            
            # Hitri grobi filter razdalje
            if abs(lat1 - lat2) < 0.003 and abs(lon1 - lon2) < 0.005:
                dist = haversine(lat1, lon1, lat2, lon2)
                
                if dist <= WALK_THRESHOLD:
                    walk_time_sec = dist / WALK_SPEED
                    
                    # Peš pot n1 -> n2
                    weight_1_to_2 = walk_time_sec + node_avg_wait_sec[n2]
                    G3.add_edge(n1, n2, weight=round(weight_1_to_2, 2), type="WALK", dist_m=round(dist, 1))
                    if n2 in terminal_nodes:
                        terminal_walk_count += 1
                    
                    # Peš pot n2 -> n1
                    weight_2_to_1 = walk_time_sec + node_avg_wait_sec[n1]
                    G3.add_edge(n2, n1, weight=round(weight_2_to_1, 2), type="WALK", dist_m=round(dist, 1))
                    if n1 in terminal_nodes:
                        terminal_walk_count += 1
                    
                    walk_edges_count += 1

    print(f"\nStatistika peš povezav:")
    print(f"- Dodano parov peš povezav: {walk_edges_count}")
    print(f"- Skupno usmerjenih WALK povezav: {walk_edges_count * 2}")
    print(f"- Kolikokrat se WALK povezava konča na končni postaji: {terminal_walk_count}")

    print(f"\nSkupna statistika grafa (Model 3):")
    print(f"- Število vozlišč: {G3.number_of_nodes()}")
    print(f"- Število vseh povezav (BUS + WALK): {G3.number_of_edges()}")

    # 5. Shranjevanje Modela 3 v GraphML
    os.makedirs("model 3", exist_ok=True)
    output_path = "model 3/model3_cakanje.graphml"
    nx.write_graphml(G3, output_path)
    print(f"\nModel 3 je uspešno generiran in shranjen v '{output_path}'.")

    # 6. IZVOZ V CSV ZA GEPHI (za multigrafe v Gephiju)
    print("Pripravljam CSV datoteke za Gephi...")
    nodes_data = []
    for node, data in G3.nodes(data=True):
        nodes_data.append({
            'Id': node,
            'Label': data.get('name', node),
            'lat': data.get('lat'),
            'lon': data.get('lon')
        })
    pd.DataFrame(nodes_data).to_csv("model 3/nodes.csv", index=False)

    edges_data = []
    for u, v, key, data in G3.edges(keys=True, data=True):
        edges_data.append({
            'Source': u,
            'Target': v,
            'Type': 'Directed',
            'Weight': data.get('weight'),
            'EdgeType': data.get('type'),
            'routes': data.get('routes', ''),
            'dist_m': data.get('dist_m', 0)
        })
    pd.DataFrame(edges_data).to_csv("model 3/edges.csv", index=False)
    print("Datoteki 'model 3/nodes.csv' in 'model 3/edges.csv' sta pripravljeni za Gephi!")

if __name__ == "__main__":
    generate_model_3()