import networkx as nx
import random
import pandas as pd

# --- KONFIGURACIJA SIMULACIJE ---
GRAF_PATH = "model 2/model2_zdruzene_postaje.graphml"
OUTPUT_CSV = "model 2/simulacija_srecanja_rezultati.csv"
STEVILO_SIMULACIJ = 1000  # Kolikokrat želimo ponoviti celoten poskus
MAKSIMALNO_KORAKOV = 5000  # Zgornja meja korakov, da ne ostanemo v neskončni zanki
# --------------------------------

# 1. Naložimo vnaprej pripravljen graf
print("Nalagam graf...")
G1 = nx.read_graphml(GRAF_PATH)
vsa_vozlisca = list(G1.nodes())

# Funkcija za en korak naključnega sprehoda glede na uteži
def naredi_utezen_korak(graf, trenutno_vozlisce):
    sosedje = list(graf.successors(trenutno_vozlisce))
    
    # Če vozlišče nima izhodnih povezav (slepa ulica), sprehajalec ostane na mestu
    if not sosedje:
        return trenutno_vozlisce
        
    # Pridobimo uteži za vse možne naslednje korake
    utezi = [graf[trenutno_vozlisce][sosed]['weight'] for sosed in sosedje]
    
    # Naključna izbira naslednje postaje glede na uteži
    naslednje_vozlisce = random.choices(sosedje, weights=utezi, k=1)[0]
    return naslednje_vozlisce

# Seznam za shranjevanje rezultatov vsake simulacije
rezultati_simulacij = []

print(f"Začenjam s simulacijo ({STEVILO_SIMULACIJ} ponovitev)...")

for i in range(STEVILO_SIMULACIJ):
    # Naključno izberemo začetni postaji za oba sprehajalca
    id_a = random.choice(vsa_vozlisca)
    id_b = random.choice(vsa_vozlisca)
    
    # Shranimo začetni poziciji za končno poročilo
    zacetna_a = id_a
    zacetna_b = id_b
    
    koraki = 0
    srecanje_id = "N/A"  # Privzeto, če se ne srečata
    srecanje_ime = "N/A"

    # Tek s časom (koraki)
    while koraki < MAKSIMALNO_KORAKOV:
        koraki += 1
        
        # Oba sprehajalca naredita korak hkrati
        id_a = naredi_utezen_korak(G1, id_a)
        id_b = naredi_utezen_korak(G1, id_b)
        
        # Preverimo, ali sta se srečala na isti postaji
        if id_a == id_b:
            srecanje_id = id_a
            srecanje_ime = G1.nodes[id_a].get('name', 'Neznano')
            break

    # Zabeležimo rezultat posamezne simulacije
    rezultati_simulacij.append({
        "zacetek_A": zacetna_a,
        "zacetek_B": zacetna_b,
        "srecanje_id": srecanje_id,
        "srecanje_ime": srecanje_ime,
        "stevilo_korakov": koraki if srecanje_id != "N/A" else MAKSIMALNO_KORAKOV
    })

# 3. Zapis rezultatov v CSV datoteko
df_rezultati = pd.DataFrame(rezultati_simulacij)
df_rezultati.to_csv(OUTPUT_CSV, index=False)

print(f"Simulacija končana! Rezultati so shranjeni v datoteki '{OUTPUT_CSV}'.")

# --- NAPREDNA STATISTIKA V KONZOLI ---
uspesna_srecanja = df_rezultati[df_rezultati["srecanje_id"] != "N/A"]
procent_uspeha = (len(uspesna_srecanja) / STEVILO_SIMULACIJ) * 100

print(f"--- REZULTATI SIMULACIJE ---")
print(f"Uspešnost srečanj: {procent_uspeha:.2f}%")

if not uspesna_srecanja.empty:
    print(f"Povprečno število korakov do srečanja: {uspesna_srecanja['stevilo_korakov'].mean():.1f}")
    
    # Izračun najbolj priljubljenih točk srečanja
    top_postaje = uspesna_srecanja["srecanje_ime"].value_counts().head(5)
    print("\n[TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA]")
    for postaja, st_srecanj in top_postaje.items():
        print(f" - {postaja}: {st_srecanj}x")