import networkx as nx
import random
import pandas as pd
import numpy as np

# --- KONFIGURACIJA SIMULACIJE ---
GRAF_PATH = "model 3/model3_cakanje.graphml"
OUTPUT_CSV = "model 3/fixed_start_sim_rez.csv"
STEVILO_SIMULACIJ = 5000  # Število ponovitev poskusa
# --------------------------------

print("Nalagam Model 3...")
G3 = nx.read_graphml(GRAF_PATH)
vsa_vozlisca = list(G3.nodes())

MAKSIMALNO_KORAKOV = len(vsa_vozlisca) * 5

def naredi_utezen_korak_model3(graf, trenutno_vozlisce):
    sosedje = list(graf.successors(trenutno_vozlisce))
    
    if not sosedje:
        return trenutno_vozlisce
        
    # Pridobimo časovne uteži za vse možne naslednje korake
    casi = [graf[trenutno_vozlisce][sosed]['weight'] for sosed in sosedje]
    
    # Pretvrimo čase v inverzne vrednosti (manjši čas -> večja utež)
    # Dodamo majhno vrednost (npr. 0.01), da preprečimo deljenje z nič, če bi bil čas naključno 0.
    inverzne_utezi = [1.0 / (c + 0.01) for c in casi]
    
    # Naključna izbira naslednje postaje glede na INVERZNE uteži
    naslednje_vozlisce = random.choices(sosedje, weights=inverzne_utezi, k=1)[0]
    return naslednje_vozlisce

rezultati_simulacij = []

print(f"Začenjam s simulacijo na Modelu 3 ({STEVILO_SIMULACIJ} ponovitev)...")

for i in range(STEVILO_SIMULACIJ):
    #id_a = random.choice(vsa_vozlisca)
    #id_b = random.choice(vsa_vozlisca)
    id_a = "889e3719-7d29-4888-b690-5a1531d2930e" #Jadranska
    id_b = "3429cda2-6047-453c-bf54-952dfa6674c0" #Klinicni center

    zacetna_a = id_a
    zacetna_b = id_b
    
    koraki = 0
    srecanje_id = "N/A"
    srecanje_ime = "N/A"

    while koraki < MAKSIMALNO_KORAKOV:
        koraki += 1
        
        id_a = naredi_utezen_korak_model3(G3, id_a)
        id_b = naredi_utezen_korak_model3(G3, id_b)
        
        if id_a == id_b:
            srecanje_id = id_a
            srecanje_ime = G3.nodes[id_a].get('name', 'Neznano')
            break

    rezultati_simulacij.append({
        "zacetek_A": zacetna_a,
        "zacetek_B": zacetna_b,
        "srecanje_id": srecanje_id,
        "srecanje_ime": srecanje_ime,
        "stevilo_korakov": koraki if srecanje_id != "N/A" else MAKSIMALNO_KORAKOV
    })

# Zapis rezultatov
df_rezultati = pd.DataFrame(rezultati_simulacij)
df_rezultati.to_csv(OUTPUT_CSV, index=False)

print(f"Simulacija končana! Rezultati so shranjeni v '{OUTPUT_CSV}'.")

# --- STATISTIKA ---
uspesna_srecanja = df_rezultati[df_rezultati["srecanje_id"] != "N/A"]
procent_uspeha = (len(uspesna_srecanja) / STEVILO_SIMULACIJ) * 100

print(f"--- REZULTATI SIMULACIJE (MODEL 3) ---")
print(f"Uspešnost srečanj: {procent_uspeha:.2f}%")

if not uspesna_srecanja.empty:
    print(f"Povprečno število korakov do srečanja: {uspesna_srecanja['stevilo_korakov'].mean():.1f}")
    
    top_postaje = uspesna_srecanja["srecanje_ime"].value_counts().head(5)
    print("\n#### TOP 5 POSTAJALIŠČ SREČANJA")
    for postaja, st_srecanj in top_postaje.items():
        print(f" - {postaja}: {st_srecanj}x")