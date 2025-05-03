import networkx as nx

def calculate_cpm(task_list):
    G = nx.DiGraph()

    for task in task_list:
        G.add_node(task["name"], duration=task["duration"])

    for task in task_list:
        for pred in task["predecessors"]:
            G.add_edge(pred, task["name"])

    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("Graf nie jest acykliczny – sprawdź powiązania.")

    top_order = list(nx.topological_sort(G))
    es = {node: 0 for node in top_order}  # najwcześniejszy start

    for node in top_order:
        preds = list(G.predecessors(node))
        if preds:
            es[node] = max([es[p] + G.nodes[p]["duration"] for p in preds])

    max_time = max([es[n] + G.nodes[n]["duration"] for n in top_order])

    result = "Wyniki CPM:\n"
    for node in top_order:
        ef = es[node] + G.nodes[node]["duration"]
        result += f"Czynność {node}: ES={es[node]}, EF={ef}\n"

    result += f"\nCzas zakończenia projektu: {max_time}"

    return result
