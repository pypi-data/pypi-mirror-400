'''import pandas as pd

data = {
    "City": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "Demand": [200, 500, 300, 450, 600, 250, 700, 350]
}

df = pd.DataFrame(data)
print(df)

best = df.loc[df["Demand"].idxmax()]

print("\nBest Warehouse Location")
print(best)
'''

'''import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

routers = [
    ("Router1", "Router2"),
    ("Router2", "Router3"),
    ("Router3", "Router4"),
    ("Router4", "Router1"),
    ("Router1", "Router5"),
    ("Router5", "Router2"),
    ("Router3", "Router6"),
    ("Router6", "Router4")
]

G.add_edges_from(routers)

print("Routers:", G.nodes())
print("Connections:", G.edges())

nx.draw(G, with_labels=True, node_size=2000)
plt.show()
'''