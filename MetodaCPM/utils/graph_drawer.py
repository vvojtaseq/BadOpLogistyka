import matplotlib.pyplot as plt
import networkx as nx

def draw_aoa_graph(task_list):
    G = nx.DiGraph()

    for task in task_list:
        G.add_node(task["name"], duration=task["duration"])

    for task in task_list:
        for pred in task["predecessors"]:
            G.add_edge(pred, task["name"])

    pos = nx.spring_layout(G)
    labels = {n: f"{n}\n({G.nodes[n]['duration']})" for n in G.nodes}

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, labels=labels, node_color="lightblue", node_size=1500, font_size=10, arrows=True)
    plt.title("Graf AOA – Metoda CPM")
    plt.tight_layout()
    plt.show()
