import math
import networkx as nx

# Vaša funkcija za izračun razdalje
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
vsa_vozlisca = list(G1.nodes(data=True))

# 2. Poiščemo vse dopustne pare za združevanje
vsi_mozni_pari = []

print("Analiziram pare postajališč (iščem nesosednja in bližnja)...")
for i in range(len(vsa_vozlisca)):
    id1, attrs1 = vsa_vozlisca[i]
    lat1, lon1 = float(attrs1['lat']), float(attrs1['lon'])
    
    for j in range(i + 1, len(vsa_vozlisca)):
        id2, attrs2 = vsa_vozlisca[j]
        
        # POGOJ 1: Vozlišči ne smeta biti sosednji v G1 (v nobeni smeri)
        if G1.has_edge(id1, id2) or G1.has_edge(id2, id1):
            continue
            
        lat2, lon2 = float(attrs2['lat']), float(attrs2['lon'])
        razdalja = haversine(lat1, lon1, lat2, lon2)
        
        # POGOJ 2: Razdalja mora biti manjša od 300 metrov
        if razdalja < 300:
            vsi_mozni_pari.append((razdalja, id1, id2))

# Sortiramo pare po razdalji naraščajoče (najbližji imajo prednost)
vsi_mozni_pari.sort(key=lambda x: x[0])

# 3. Izbiranje parov brez kaskadnega združevanja
uporabljene_postaje = set()
končne_skupine = []

print("Izvajam kontrolirano združevanje (največ 2 postaji skupaj)...")
for razdalja, id1, id2 in vsi_mozni_pari:
    # Če nobena od dveh postaj še ni bila združena, tvorita novo mega-vozlišče
    if id1 not in uporabljene_postaje and id2 not in uporabljene_postaje:
        končne_skupine.append([id1, id2])
        uporabljene_postaje.add(id1)
        uporabljene_postaje.add(id2)

# Vse preostale postaje, ki niso našle nesosednjega para znotraj 300m, ostanejo same
for id_postaje, _ in vsa_vozlisca:
    if id_postaje not in uporabljene_postaje:
        končne_skupine.append([id_postaje])

# 4. Izgradnja novega usmerjenega grafa G2
G2 = nx.DiGraph()
preslikava_idjev = {}

print("Gradim končni graf G2...")
for index, skupina in enumerate(končne_skupine):
    mega_id = f"mega_{index}"
    
    Zbrana_imena = []
    vsi_lat = []
    vsi_lon = []
    
    for star_id in skupina:
        preslikava_idjev[star_id] = mega_id
        Zbrana_imena.append(G1.nodes[star_id]['name'])
        vsi_lat.append(float(G1.nodes[star_id]['lat']))
        vsi_lon.append(float(G1.nodes[star_id]['lon']))
        
    # Združevanje imen (npr. Ajdovščina/Pošta)
    unikatna_imena = sorted(list(set(Zbrana_imena)))
    novo_ime = "/".join(unikatna_imena)
    
    povprecen_lat = sum(vsi_lat) / len(vsi_lat)
    povprecen_lon = sum(vsi_lon) / len(vsi_lon)
    
    G2.add_node(mega_id, name=novo_ime, lat=povprecen_lat, lon=povprecen_lon)

# 5. Preslikava povezav in seštevanje uteži
for u, v, data in G1.edges(data=True):
    novi_u = preslikava_idjev[u]
    novi_v = preslikava_idjev[v]
    utez = data['weight']
    
    if novi_u != novi_v:
        if G2.has_edge(novi_u, novi_v):
            G2[novi_u][novi_v]['weight'] += utez
        else:
            G2.add_edge(novi_u, novi_v, weight=utez)

# Izpis končne statistike
st_zdruzenih = sum(1 for s in končne_skupine if len(s) == 2)
print("\n--- STATISTIKA STROGEGA ZDRUŽEVANJA ---")
print(f"Skupno število novih vozlišč v G2: {G2.number_of_nodes()}")
print(f"Število uspešno združenih parov (velikosti 2): {st_zdruzenih}")
print(f"Število povezav v G2: {G2.number_of_edges()}")

# 6. Shranjevanje modela 2
nx.write_graphml(G2, "model 2/model2_zdruzene_postaje.graphml")
print("\nModel 2 uspešno posodobljen in shranjen.")