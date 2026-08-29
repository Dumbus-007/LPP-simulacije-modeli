import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation
import random

def animiraj_sprehod(G, start_a=None, start_b=None, interval=1000, invert_weights=False):
    """
    Animira dva naključna sprehoda po grafu G.
    
    Parameters:
    - G: networkx.DiGraph ali networkx.Graph
    - start_a, start_b: Začetni vozlišči (če je None, izbere naključno)
    - interval: Čas med koraki v ms (npr. 1000 ms = 1 sekunda)
    - invert_weights: 
        * True  -> za Model 3 (utež je ČAS: manjša utež = večja verjetnost)
        * False -> za Model 1 ali sintetične grafe (utež je FREKVENCA oz. enakovredna)
    """
    vsa_vozlisca = list(G.nodes())
    if len(vsa_vozlisca) == 0:
        print("Graf je prazen.")
        return

    # 1. Priprava verjetnosti prehodov
    transition_probabilities = {}
    for node in vsa_vozlisca:
        successors = list(G.successors(node)) if G.is_directed() else list(G.neighbors(node))
        
        # Če je slepa ulica, sprehajalec ostane na mestu
        if not successors:
            transition_probabilities[node] = ([node], [1.0])
            continue
            
        weights = [G[node][s].get('weight', 1.0) for s in successors]
        
        if invert_weights:
            # Model 3: Časne uteži (manjši čas -> večja verjetnost)
            effective_weights = [1.0 / (w + 0.01) for w in weights]
        else:
            # Model 1 ali sintetični grafi (večja/enaka utež -> večja verjetnost)
            effective_weights = [float(w) for w in weights]
            
        total_weight = sum(effective_weights)
        
        # Normalizacija v prave verjetnosti (seštevek v vrstici = 1.0)
        probabilities = [ew / total_weight for ew in effective_weights]
        transition_probabilities[node] = (successors, probabilities)

    def next_node(current):
        target_nodes, probs = transition_probabilities[current]
        return np.random.choice(target_nodes, p=probs)

    # 2. Nastavitev začetnih pozicij
    waA = start_a if start_a is not None else random.choice(vsa_vozlisca)
    waB = start_b if start_b is not None else random.choice(vsa_vozlisca)
    
    global walker1, walker2, met, step_counter, pos_draw, is_directed, anim
    walker1 = waA
    walker2 = waB
    met = (walker1 == walker2)
    step_counter = 0
    
    pos_draw = nx.spring_layout(G, seed=42)
    is_directed = G.is_directed()

    fig, ax = plt.subplots(figsize=(9, 7))

    def update(frame):
        global walker1, walker2, met, step_counter
        ax.clear()
        
        if not met:
            walker1 = next_node(walker1)
            walker2 = next_node(walker2)
            step_counter += 1
            
            if walker1 == walker2:
                met = True
        
        # Barvanje vozlišč
        colors = []
        for node in G.nodes():
            if met and node == walker1:
                colors.append("purple")  # Srečanje
            elif node == walker1:
                colors.append("green")   # Sprehajalec A
            elif node == walker2:
                colors.append("red")     # Sprehajalec B
            else:
                colors.append("lightblue")
        
        nx.draw(G, pos_draw, with_labels=True, node_color=colors,
                node_size=800, ax=ax, font_size=9, 
                arrows=is_directed)
        
        if met:
            ax.set_title(f"Srečanje na vozlišču '{walker1}' po {step_counter} korakih!", fontsize=12, fontweight='bold')
        else:
            ax.set_title(f"Korak {step_counter} | A: '{walker1}' | B: '{walker2}'", fontsize=12)

    anim = FuncAnimation(fig, update, interval=interval)
    plt.show()

# ================================================
# ============ PRIMER UPORABE ===================
# ================================================

# animacija sprehodov v sintetičnem grafu (liziki) na 6 vozliščih z začetkoma v vozlišču 0 in 5

G_l = nx.lollipop_graph(m=4, n=2).to_directed()
animiraj_sprehod(G_l, start_a=0, start_b=5, interval=500, invert_weights=False)