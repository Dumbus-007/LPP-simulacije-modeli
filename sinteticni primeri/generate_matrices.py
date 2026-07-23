import networkx as nx
import numpy as np
import pandas as pd

STEVILO_VOZLISC = 6
n = STEVILO_VOZLISC

# 1. Definicija 7 usmerjenih grafov (n = 6)
grafi = {
    "Path": nx.path_graph(n).to_directed(),
    "Ring": nx.cycle_graph(n).to_directed(),
    "Star": nx.star_graph(n - 1).to_directed(),
    "Lattice": nx.convert_node_labels_to_integers(nx.grid_2d_graph(3, 2)).to_directed(),
    "Lollipop": nx.lollipop_graph(m=4, n=2).to_directed(),
    "Tadpole": nx.tadpole_graph(m=4, n=2).to_directed(),
}

# Sun graf
G_sun = nx.cycle_graph(3)
for i in range(3):
    G_sun.add_edge(i, i + 3)
grafi["Sun"] = G_sun.to_directed()

# 2. Priprava stohastičnih prehodnih matrik P
def vrni_prehodno_matriko(G):
    A = nx.to_numpy_array(G, dtype=float)
    vsote = A.sum(axis=1, keepdims=True)
    vsote[vsote == 0] = 1.0
    return A / vsote

# 3. Priprava matrike E po navodilih iz izreka
# vec(I_n) v Pythonu pripravimo s sploščenjem enotske matrike I_n po stolpcih (order='F')
I_n = np.eye(n)
vec_I_n = I_n.flatten(order='F') 
diag_E = 1.0 - vec_I_n
E = np.diag(diag_E)

I_n2 = np.eye(n**2)
ones_vec = np.ones((n**2, 1))

matrike_M = {}

# 4. Izračun matrike M za vsak graf
print("=== TEORETIČNE MATRIKE PRIČAKOVANIH ČASOV SREČANJA (M) ===\n")

for ime, G_dir in grafi.items():
    P = vrni_prehodno_matriko(G_dir)
    
    # Skupna prehodna matrika P_p ⊗ P_e (ker sta enaki: P ⊗ P)
    P_kron = np.kron(P, P)
    
    # Sub-stohastična matrika (P ⊗ P) * E
    P_sub = P_kron @ E
    
    # Reševanje sistema: (I_n2 - (P ⊗ P)E) * vec(M) = 1_n2
    try:
        vec_M = np.linalg.solve(I_n2 - P_sub, ones_vec)
        
        # Preoblikovanje vec(M) nazaj v matriko M velikosti (n x n)
        # Zaradi standarda vektorizacije po stolpcih preoblikujemo z order='F'
        M = vec_M.reshape((n, n), order='F')
        matrike_M[ime] = M
        
        print(f"Topologija: {ime}")
        df_M = pd.DataFrame(M, index=range(n), columns=range(n))
        print(df_M.round(2))
        print("\n" + "="*55 + "\n")
        
    except np.linalg.LinAlgError:
        print(f"Topologija: {ime} - Matrika (I - PE) ni obrnljiva (srečanje ni zagotovljeno za vse pare!).\n")