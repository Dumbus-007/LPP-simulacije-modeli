import pandas as pd
import folium
from folium.plugins import HeatMap

# 1. Preberemo datoteki
df_sim = pd.read_csv("model 3/random_start_sim_rez.csv")
df_nodes = pd.read_csv("model 3/nodes.csv")

# 2. Preštejemo, kolikokrat se je srečanje zgodilo v vsakem vozlišču
srecanja_counts = (
    df_sim["srecanje_id"].value_counts().reset_index()
)
srecanja_counts.columns = ["node_id", "stevilo_srecanj"]

# 3. Združimo podatke o srečanjih s koordinatami iz nodes.csv
df_merged = pd.merge(
    srecanja_counts, df_nodes, left_on="node_id", right_on="Id"
)

# 4. Izračunamo središče zemljevida na podlagi povprečnih koordinat
center_lat = df_merged["lat"].mean()
center_lon = df_merged["lon"].mean()

# Ustvarimo osnovni zemlevid
m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# 5. Pripravimo podatke v obliki seznama: [[lat, lon, utež], ...]
heat_data = [
    [row["lat"], row["lon"], row["stevilo_srecanj"]]
    for index, row in df_merged.iterrows()
]

# 6. Dodamo HeatMap sloj
HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)

# 7. Shranimo zemlevid v HTML datoteko in jo odpremo v brskalniku
m.save("vrocinski_zemljevid_srecanj.html")
print("Zemljevid je shranjen v 'vrocinski_zemljevid_srecanj.html'")
