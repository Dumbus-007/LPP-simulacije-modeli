import networkx as nx

# 1. Naložimo prvi model
print("Nalagam prvi model...")
G1 = nx.read_graphml("model 1/model1_frekvenca.graphml")

# Ustvarimo kopijo grafa, ki jo bomo spreminjali
# (Direktno spreminjanje grafa med iteracijo čez vozlišča lahko povzroči napake)
G_reduced = G1.copy()

# Zanka se izvaja, dokler v grafu še najdemo vozlišča za odstranitev
while True:
    nodes_to_remove = []
    
    for node in G_reduced.nodes():
        # Preverimo vhodno stopnjo (in-degree)
        in_degree = G_reduced.in_degree(node)
        out_degree = G_reduced.out_degree(node)
        
        # Vozlišče odstranimo le, če ima vhodno stopnjo natanko 1
        # Izpustimo začetna vozlišča (in_degree == 0) in ponikalnice brez izhoda (out_degree == 0),
        # če želimo ohraniti končne točke.
        if in_degree == 1 and out_degree > 0:
            nodes_to_remove.append(node)
            
    # Če ni več vozlišč, ki ustrezajo pogoju, prekinemo zanko
    if not nodes_to_remove:
        break
        
    # Izvedemo glajenje za najdena vozlišča
    for node in nodes_to_remove:
        # Ker je in_degree == 1, obstaja natanko en predhodnik (parent)
        parent = list(G_reduced.predecessors(node))[0]
        
        # Vsi nasledniki (children) tega vozlišča
        children = list(G_reduced.successors(node))
        
        # Ustvarimo nove direktne povezave od predhodnika do vseh naslednikov
        for child in children:
            # Pridobimo utež prve povezave (Parent -> Node)
            w1 = G_reduced[parent][node].get('weight', 1)
            
            # Pridobimo utež druge povezave (Node -> Child)
            w2 = G_reduced[node][child].get('weight', 1)
            
            # Izračunamo novo utež kot MINIMUM (ozko grlo)
            nova_utez = min(w1, w2)
            
            # Ustvarimo novo povezavo z novo utežjo
            G_reduced.add_edge(parent, child, weight=nova_utez)
            
        # Sedaj lahko varno izbrišemo vmesno vozlišče
        G_reduced.remove_node(node)

print(# Končni izpis stanja
    f"Zmanjševanje uspešno. Število vozlišč se je spremenilo iz {len(G1)} na {len(G_reduced)}."
)

# 2. Shranimo nov, zreduciran graf
nx.write_graphml(G_reduced, "model 1.5/model1.5_zreduciran.graphml")
print("Nov graf je shranjen kot 'model1.5_zreduciran.graphml'.")