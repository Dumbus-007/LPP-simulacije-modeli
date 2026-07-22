import math
import os
from collections import defaultdict
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
    
    # Ustvarimo nov usmerjen graf z istimi vozlišči in njihovimi atributi
    G3 = nx.DiGraph()
    G3.add_nodes_from(G1.nodes(data=True))
    
    # Konstante (vse v sekundah ali metrih)
    SERVICE_WINDOW = 18 * 3600  # 18 ur = 64800 sekund
    WALK_THRESHOLD = 300        # 300 metrov
    WALK_SPEED = 1.4            # 1.4 m/s (pribl. 5 km/h)
    
    # 2. Izračun čakalnih dob v SEKUNDAH neposredno iz uteži (frekvenc) Modela 1
    print("Računam čakalne dobe iz frekvenc Modela 1...")
    stop_outgoing_waits = defaultdict(list)
    
    for u, v, data in G1.edges(data=True):
        count = float(data.get('weight', 1.0))
        if count <= 0:
            count = 1.0
            
        # Čas čakanja v SEKUNDAH
        wait_penalty_sec = SERVICE_WINDOW / (2.0 * count)
        
        # BUS povezava v Modelu 3 (utež je čas čakanja v sekundah)
        G3.add_edge(u, v, weight=round(wait_penalty_sec, 2), type="BUS")
        
        # Beležimo izhodne čakalne dobe za posamezno vozlišče
        stop_outgoing_waits[u].append(wait_penalty_sec)

    # 3. Izračun povprečnega časa čakanja v SEKUNDAH na vsakem vozlišču
    node_avg_wait_sec = {}
    for node in G3.nodes():
        waits = stop_outgoing_waits.get(node, [])
        if waits:
            node_avg_wait_sec[node] = sum(waits) / len(waits)
        else:
            # Če vozlišče nima izhodnih avtobusov, damo privzeto kazen (npr. 30 minut = 1800 sekund)
            node_avg_wait_sec[node] = 1800.0

    # 4. Dodajanje WALK povezav (< 300m) z utežmi v SEKUNDAH
    print("Računam in dodajam peš povezave (WALK)...")
    nodes_list = list(G3.nodes(data=True))
    walk_edges_count = 0
    
    for i in range(len(nodes_list)):
        n1, data1 = nodes_list[i]
        
        # Pridobivanje GPS koordinat
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
                    # Čas hoje v SEKUNDAH
                    walk_time_sec = dist / WALK_SPEED
                    
                    # Peš pot n1 -> n2 (hoja + čakanje na n2)
                    weight_1_to_2 = walk_time_sec + node_avg_wait_sec[n2]
                    G3.add_edge(n1, n2, weight=round(weight_1_to_2, 2), type="WALK")
                    
                    # Peš pot n2 -> n1 (hoja + čakanje na n1)
                    weight_2_to_1 = walk_time_sec + node_avg_wait_sec[n1]
                    G3.add_edge(n2, n1, weight=round(weight_2_to_1, 2), type="WALK")
                    
                    walk_edges_count += 1

    print(f"Dodano {walk_edges_count * 2} usmerjenih peš povezav ({walk_edges_count} parov).")
    
    # 5. Shranjevanje Modela 3
    os.makedirs("model 3", exist_ok=True)
    output_path = "model 3/model3_cakanje.graphml"
    nx.write_graphml(G3, output_path)
    print(f"Model 3 je uspešno generiran in shranjen v '{output_path}'.")

if __name__ == "__main__":
    generate_model_3()