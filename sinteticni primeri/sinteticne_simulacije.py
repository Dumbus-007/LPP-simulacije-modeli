import networkx as nx
import random
import pandas as pd
import os

# --- KONFIGURACIJA ---
STEVILO_VOZLISC = 20
STEVILO_SIMULACIJ = 1000
OUTPUT_CSV = "sinteticni primeri/sinteticni_grafi_rezultati.csv"  # Pot do izhodne datoteke
# ---------------------

def pripravi_graf(G_undirected):
    """Pretvori neusmerjen graf v usmerjenega in doda časovne uteži."""
    G_directed = nx.DiGraph()
    G_directed.add_nodes_from(G_undirected.nodes(data=True))
    
    # Vsako neusmerjeno povezavo pretvorimo v dve usmerjeni s časom 1.0 min
    for u, v in G_undirected.edges():
        G_directed.add_edge(u, v, weight=1.0)
        G_directed.add_edge(v, u, weight=1.0)
    return G_directed

def naredi_korak_model3(graf, trenutno_vozlisce):
    sosedje = list(graf.successors(trenutno_vozlisce))
    if not sosedje:
        return trenutno_vozlisce
    casi = [graf[trenutno_vozlisce][sosed]['weight'] for sosed in sosedje]
    # Manjši čas -> večja utež za izbiro
    inverzne_utezi = [1.0 / (c + 0.01) for c in casi]
    return random.choices(sosedje, weights=inverzne_utezi, k=1)[0]

def zazeni_simulacijo(graf, ime_topologije):
    vsa_vozlisca = list(graf.nodes())
    maks_korakov = len(vsa_vozlisca) * 10
    srečanja = 0
    skupni_koraki = 0
    
    for _ in range(STEVILO_SIMULACIJ):
        id_a = random.choice(vsa_vozlisca)
        id_b = random.choice(vsa_vozlisca)
        koraki = 0
        
        while koraki < maks_korakov:
            koraki += 1
            id_a = naredi_korak_model3(graf, id_a)
            id_b = naredi_korak_model3(graf, id_b)
            
            if id_a == id_b:
                srečanja += 1
                skupni_koraki += koraki
                break
                
    procent = (srečanja / STEVILO_SIMULACIJ) * 100
    povprecni_koraki = (skupni_koraki / srečanja) if srečanja > 0 else maks_korakov
    return procent, povprecni_koraki

# --- GENERIRANJE TOPOLOGIJ (vse na 20 vozliščih) ---
grafi = {}

grafi["Path"] = nx.path_graph(STEVILO_VOZLISC)
grafi["Ring"] = nx.cycle_graph(STEVILO_VOZLISC)
grafi["Star"] = nx.star_graph(STEVILO_VOZLISC - 1)

grafi["Lattice"] = nx.grid_2d_graph(4, 5)
grafi["Lattice"] = nx.convert_node_labels_to_integers(grafi["Lattice"])

grafi["Lollipop"] = nx.lollipop_graph(m=10, n=10)
grafi["Tadpole"] = nx.tadpole_graph(m=10, n=10)

G_sun = nx.cycle_graph(10)
for n in list(G_sun.nodes()):
    G_sun.add_edge(n, n + 10)
grafi["Sun"] = G_sun

# --- POGANJANJE SIMULACIJ ---
rezultati = []

print("Začenjam simulacije na sintetičnih grafih...\n")
for ime, G_undir in grafi.items():
    G_dir = pripravi_graf(G_undir)
    uspeh, koraki = zazeni_simulacijo(G_dir, ime)
    rezultati.append({
        "Topologija": ime, 
        "Uspešnost srečanj (%)": round(uspeh, 2), 
        "Povprečni koraki": round(koraki, 1)
    })

# --- SHRANJEVANJE V DATOTEKO ---
df = pd.DataFrame(rezultati)

# Izpis v konzolo za hiter pregled
print(df.to_string(index=False))
print("\n" + "-"*40)

# Zapis v CSV datoteko
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"Tabela rezultatov je uspešno shranjena v datoteko: '{OUTPUT_CSV}'")