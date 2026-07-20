import math
import os
import csv
from datetime import datetime
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

def time_to_seconds(time_str):
    """Pretvori niz HH:MM:SS v sekunde."""
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def generate_model_3():
    # 1. Naložimo osnovo - Model 1
    print("Nalagam Model 1...")
    G1 = nx.read_graphml("model 1/model1_frekvenca.graphml")
    
    # Ustvarimo nov prazno usmerjen graf z istimi vozlišči
    G3 = nx.DiGraph()
    G3.add_nodes_from(G1.nodes(data=True))
    
    # Poti do GTFS podatkov
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gtfs_dir = os.path.join(script_dir, "..", "lpp_gtfs")
    
    SERVICE_WINDOW = 18 * 3600  # 18 ur v sekundah
    WALK_THRESHOLD = 300        # metri
    WALK_SPEED = 1.4            # m/s
    
    # 2. GTFS obdelava za izračun frekvenc (enako kot v tvoji datoteki)
    print("Obdelujem GTFS podatke...")
    weekday_services = set()
    with open(os.path.join(gtfs_dir, "calendar_dates.txt"), "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = datetime.strptime(row["date"], "%Y%m%d")
            if dt.weekday() < 5:
                weekday_services.add(row["service_id"])

    valid_weekday_trips = set()
    with open(os.path.join(gtfs_dir, "trips.txt"), "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["service_id"] in weekday_services:
                valid_weekday_trips.add(row["trip_id"])

    # Preštejemo vožnje med postajališči
    edge_counts = defaultdict(int)
    current_trip = None
    prev_stop = None
    
    with open(os.path.join(gtfs_dir, "stop_times.txt"), "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trip_id = row["trip_id"]
            if trip_id not in valid_weekday_trips:
                continue
            stop_id = row["stop_id"]
            
            if trip_id == current_trip:
                edge_counts[(prev_stop, stop_id)] += 1
            
            current_trip = trip_id
            prev_stop = stop_id

    # 3. Izračun povprečnega časa čakanja za vsako povezavo (v minutah)
    # Shranjujemo si tudi čakalne dobe za vsako izhodno postajališče, da bomo kasneje izračunali WALK uteži
    wait_penalties = {}  # (src, tgt) -> wait_in_minutes
    stop_outgoing_waits = defaultdict(list)  # stop_id -> lista čakalnih dob v minutah
    
    print("Računam čakalne dobe za avtobusne povezave...")
    for (src, tgt), count in edge_counts.items():
        # Izračun v sekundah in pretvorba v minute
        wait_penalty_min = (SERVICE_WINDOW / (2 * count)) / 60.0
        wait_penalties[(src, tgt)] = wait_penalty_min
        stop_outgoing_waits[src].append(wait_penalty_min)
        
    # Izračunamo povprečno čakanje na posameznem vozlišču "v katerokoli smer od tam"
    node_avg_wait = {}
    for node in G3.nodes():
        waits = stop_outgoing_waits.get(node, [])
        if waits:
            node_avg_wait[node] = sum(waits) / len(waits)
        else:
            # Če postajališče nima izhodnih avtobusov (npr. končna postaja), 
            # nastavimo privzeto kazen (npr. maksimalno čakanje, npr. 30 min ali 0, odvisno od logike)
            node_avg_wait[node] = 30.0 

    # 4. Dodajanje BUS povezav v Model 3 (samo tiste, ki so obstajale v Modelu 1)
    print("Dodajam BUS povezave v Model 3...")
    for u, v in G1.edges():
        # Če imamo podatek iz GTFS, vzamemo izračunan čas čakanja, sicer damo privzeto vrednost
        teza = wait_penalties.get((u, v), 15.0) 
        G3.add_edge(u, v, weight=round(teza, 2), type="BUS")

    # 5. Dodajanje WALK povezav (< 300m)
    print("Računam in dodajam peš povezave (WALK)...")
    nodes_list = list(G3.nodes(data=True))
    walk_edges_count = 0
    
    for i in range(len(nodes_list)):
        n1, data1 = nodes_list[i]
        # Preverimo, če ima vozlišče shranjene GPS koordinate (predpostavljam atribute 'lat' in 'lon')
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
            
            # Hitro grobo preverjanje razdalje
            if abs(lat1 - lat2) < 0.003 and abs(lon1 - lon2) < 0.005:
                dist = haversine(lat1, lon1, lat2, lon2)
                
                if dist <= WALK_THRESHOLD:
                    # Čas hoje v minutah
                    walk_time_min = (dist / WALK_SPEED) / 60.0
                    
                    # Peš povezava od n1 do n2 (vključuje čakanje na n2)
                    weight_1_to_2 = walk_time_min + node_avg_wait[n2]
                    G3.add_edge(n1, n2, weight=round(weight_1_to_2, 2), type="WALK")
                    
                    # Peš povezava od n2 do n1 (vključuje čakanje na n1)
                    weight_2_to_1 = walk_time_min + node_avg_wait[n1]
                    G3.add_edge(n2, n1, weight=round(weight_2_to_1, 2), type="WALK")
                    
                    walk_edges_count += 1

    print(f"Dodano {walk_edges_count} peš povezav.")
    
    # 6. Shranjevanje Modela 3
    os.makedirs("model 3", exist_ok=True)
    output_path = "model 3/model3_cakanje.graphml"
    nx.write_graphml(G3, output_path)
    print(f"Model 3 je uspešno shranjen v '{output_path}'.")

if __name__ == "__main__":
    generate_model_3()