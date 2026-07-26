import time
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
    # Pridobimo vse izhodne povezave (u, v, podatki_povezave)
    # Vsaka paralelna povezava bo v seznamu nastopala kot samostojen element
    izhodne_povezave = list(graf.out_edges(trenutno_vozlisce, data=True))
    
    if not izhodne_povezave:
        print(f"Vozlišče {trenutno_vozlisce} nima izhodnih povezav. Ostajam na mestu.")
        return trenutno_vozlisce
        
    # Pridobimo časovne uteži za vsako posamezno povezavo
    casi = [podatki['weight'] for _, _, podatki in izhodne_povezave]
    
    # Pretvorimo čase v stopnje / inverzne uteži (r = 1 / t)
    inverzne_utezi = [1.0 / c for c in casi]
    
    # Izberemo naključno povezavo glede na izračunane inverzne uteži
    izbrana_povezava = random.choices(izhodne_povezave, weights=inverzne_utezi, k=1)[0]
    
    # Izbrana povezava je v obliki (trenutno_vozlisce, ciljno_vozlisce, podatki)
    naslednje_vozlisce = izbrana_povezava[1]
    
    return naslednje_vozlisce

rezultati_simulacij = []

print(f"Začenjam s simulacijo na Modelu 3 ({STEVILO_SIMULACIJ} ponovitev)...")
start_time = time.perf_counter()

for i in range(STEVILO_SIMULACIJ):
    #id_a = random.choice(vsa_vozlisca)
    #id_b = random.choice(vsa_vozlisca)
    id_a = "603011" #Jadranska
    id_b = "402031" #Klinicni center

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

end_time = time.perf_counter()
print(f"Simulacija končana! Rezultati so shranjeni v '{OUTPUT_CSV}'.")
print(f"Čas simulacije: {end_time - start_time:.2f} sekund")

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