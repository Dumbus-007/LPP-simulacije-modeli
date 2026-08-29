import networkx as nx
import random
import pandas as pd

# --- KONFIGURACIJA ---
STEVILO_VOZLISC = 6
SIMULACIJ_NA_PAR = 100  # 6x6 = 36 parov -> skupaj 3600 simulacij na graf
OUTPUT_CSV = "sinteticni primeri/sinteticni_grafi_rezultati.csv"
# ---------------------

# 1. enostaven korak
def naredi_enostaven_korak(graf, trenutno_vozlisce):
    sosedje = list(graf.successors(trenutno_vozlisce))
    if not sosedje:
        return trenutno_vozlisce
    return random.choice(sosedje)  # Enakomerna verjetnost za vse sosede

# 2. Simulacijska zanka
def zaženi_simulacijo(ime_topologije, graf):
    vsa_vozlisca = list(graf.nodes())
    maks_korakov = len(vsa_vozlisca) * 5
    simulacije_rezultati = []
    
    # Izvedemo simulacije za vsak par začetnih vozlišč
    for start_a in vsa_vozlisca:
        for start_b in vsa_vozlisca:
            for _ in range(SIMULACIJ_NA_PAR):
                id_a = start_a
                id_b = start_b
                koraki = 0
                koncno_vozlisce = None
                
                
                while koraki < maks_korakov:
                    koraki += 1
                    id_a = naredi_enostaven_korak(graf, id_a)
                    id_b = naredi_enostaven_korak(graf, id_b)
                    
                    if id_a == id_b:
                        koncno_vozlisce = id_a
                        break
                
                simulacije_rezultati.append({
                    "Topologija": ime_topologije,
                    "Zacetno_A": start_a,
                    "Zacetno_B": start_b,
                    "Koncno": koncno_vozlisce,
                    "Koraki": koraki
                })
                
    return simulacije_rezultati

# 3. generiranje usmerjenih grafov (.to_directed())
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
vsi_rezultati = []

print("Začenjam posodobljene simulacije (merjenje ponovnega srečanja)...\n")
for ime, G_dir in grafi.items():
    rezultati_grafa = zaženi_simulacijo(ime, G_dir)
    vsi_rezultati.extend(rezultati_grafa)

# Zapis v CSV
df = pd.DataFrame(vsi_rezultati)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"Rezultati so shranjeni v '{OUTPUT_CSV}'.")