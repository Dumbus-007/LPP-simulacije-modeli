import math
import networkx as nx

# funkcija za izračun razdalje
def haversine(lat1, lon1, lat2, lon2):
    """Calculates the distance in meters between two GPS coordinates."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 1. Naložimo prvi model
print("Nalagam prvi model...")
G1 = nx.read_graphml("model 1/model1_frekvenca.graphml")

# 2. Ustvarimo pomožni neusmerjen graf za iskanje bližnjih postaj
pomozni_graf = nx.Graph()
vsa_vozlisca = list(G1.nodes(data=True))

# Dodamo vsa vozlišča v pomožni graf
for node_id, _ in vsa_vozlisca:
    pomozni_graf.add_node(node_id)

print("Iščem postajališča, ki so skupaj bližje kot 300 metrov...")
# Primerjamo vsak par postaj med seboj
for i in range(len(vsa_vozlisca)):
    id1, attrs1 = vsa_vozlisca[i]
    # Opozorilo: GraphML včasih shrani številke kot nize, zato jih pretvorimo v float
    lat1, lon1 = float(attrs1['lat']), float(attrs1['lon'])
    
    for j in range(i + 1, len(vsa_vozlisca)):
        id2, attrs2 = vsa_vozlisca[j]
        lat2, lon2 = float(attrs2['lat']), float(attrs2['lon'])
        
        # Če je razdalja manjša od 300 metrov, ju povežemo v pomožnem grafu
        if haversine(lat1, lon1, lat2, lon2) < 300:
            pomozni_graf.add_edge(id1, id2)

# Poiščemo skupine (sklepišča) postaj, ki spadajo skupaj
skupine_postaj = list(nx.connected_components(pomozni_graf))

# 3. Izgradnja novega grafa G2 z mega-vozlišči
G2 = nx.DiGraph()
preslikava_idjev = {} # Slovar, ki nam bo povedal: stari_id -> novi_mega_id

print("Ustvarjam združena mega-vozlišča...")
for index, skupina in enumerate(skupine_postaj):
    mega_id = f"mega_{index}"
    
    Zbrana_imena = []
    vsi_lat = []
    vsi_lon = []
    
    for star_id in skupina:
        preslikava_idjev[star_id] = mega_id
        Zbrana_imena.append(G1.nodes[star_id]['name'])
        vsi_lat.append(float(G1.nodes[star_id]['lat']))
        vsi_lon.append(float(G1.nodes[star_id]['lon']))
    
    # Odstranimo duplikate imen, jih uredimo in združimo s poševnico
    unikates_imena = sorted(list(set(Zbrana_imena)))
    novo_ime = "/".join(unikates_imena)
    
    # Za lokacijo mega-vozlišča vzamemo povprečje vseh udeleženih koordinat
    povprecen_lat = sum(vsi_lat) / len(vsi_lat)
    povprecen_lon = sum(vsi_lon) / len(vsi_lon)
    
    # Dodamo novo vozlišče v Graf 2
    G2.add_node(mega_id, name=novo_ime, lat=povprecen_lat, lon=povprecen_lon)

# 4. Preslikava in združevanje povezav ter uteži
print("Združujem povezave in seštevam uteži...")
for u, v, data in G1.edges(data=True):
    novi_u = preslikava_idjev[u]
    novi_v = preslikava_idjev[v]
    utez = data['weight']
    
    # Če povezava ne vodi znotraj istega mega-vozlišča (s tem se izognemo zankam na isti postaji)
    if novi_u != novi_v:
        if G2.has_edge(novi_u, novi_v):
            G2[novi_u][novi_v]['weight'] += utez
        else:
            G2.add_edge(novi_u, novi_v, weight=utez)

# Poročilo o uspešnosti združevanja
print("\n--- STATISTIKA MODELA 2 ---")
print(f"Prvotno število vozlišč (G1): {G1.number_of_nodes()}")
print(f"Novo število mega-vozlišč (G2): {G2.number_of_nodes()}")
print(f"Prvotno število povezav (G1): {G1.number_of_edges()}")
print(f"Novo število povezav (G2): {G2.number_of_edges()}")

# 5. Shranjevanje modela 2
nx.write_graphml(G2, "model 2/model2_zdruzene_postaje.graphml")
print("\nModel 2 uspešno shranjen kot 'model2_zdruzene_postaje.graphml'.")