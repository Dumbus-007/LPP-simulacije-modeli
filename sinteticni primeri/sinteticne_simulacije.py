import networkx as nx
import random
import pandas as pd

# --- KONFIGURACIJA ---
STEVILO_VOZLISC = 6
STEVILO_SIMULACIJ = 1000
OUTPUT_CSV = "sinteticni primeri/sinteticni_grafi_rezultati.csv"
# ---------------------

# 1. Popolnoma enostaven korak (brez uteži, brez računanja verjetnosti)
def naredi_enostaven_korak(graf, trenutno_vozlisce):
    sosedje = list(graf.successors(trenutno_vozlisce))
    if not sosedje:
        return trenutno_vozlisce
    return random.choice(sosedje) # Enakomerna verjetnost za vse sosede

# 2. Simulacijska zanka
def zaženi_simulacijo(graf):
    vsa_vozlisca = list(graf.nodes())
    maks_korakov = len(vsa_vozlisca) * 5
    srečanja = 0
    skupni_koraki = 0
    
    for _ in range(STEVILO_SIMULACIJ):
        id_a = random.choice(vsa_vozlisca)
        id_b = random.choice(vsa_vozlisca)
        koraki = 0
        
        while koraki < maks_korakov:
            koraki += 1
            id_a = naredi_enostaven_korak(graf, id_a)
            id_b = naredi_enostaven_korak(graf, id_b)
            
            if id_a == id_b:
                srečanja += 1
                skupni_koraki += koraki
                break
                
    procent = (srečanja / STEVILO_SIMULACIJ) * 100
    povprecni_koraki = (skupni_koraki / srečanja) if srečanja > 0 else maks_korakov
    return procent, povprecni_koraki

# 3. DIRECTNO GENERIRANJE USMERJENIH GRAFOV (.to_directed())
grafi = {
    "Path": nx.path_graph(STEVILO_VOZLISC).to_directed(),
    "Ring": nx.cycle_graph(STEVILO_VOZLISC).to_directed(),
    "Star": nx.star_graph(STEVILO_VOZLISC - 1).to_directed(),
    "Lattice": nx.convert_node_labels_to_integers(nx.grid_2d_graph(3, 2)).to_directed(),
    "Lollipop": nx.lollipop_graph(m=4, n=2).to_directed(),
    "Tadpole": nx.tadpole_graph(m=4, n=2).to_directed(),
}

# Za Sun graf (Cikel 3 + 3 zunanjih krakov)
G_sun = nx.cycle_graph(3)
for n in range(3):
    G_sun.add_edge(n, n + 3)
grafi["Sun"] = G_sun.to_directed()

# 4. Poganjanje in shranjevanje
rezultati = []

print("Začenjam poenostavljene simulacije...\n")
for ime, G_dir in grafi.items():
    uspeh, koraki = zaženi_simulacijo(G_dir)
    rezultati.append({
        "Topologija": ime, 
        "Uspešnost srečanj (%)": round(uspeh, 2), 
        "Povprečni koraki": round(koraki, 1)
    })

# Prikaz in zapis v CSV
df = pd.DataFrame(rezultati)
print(df.to_string(index=False))

df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"\nRezultati so shranjeni v '{OUTPUT_CSV}'.")