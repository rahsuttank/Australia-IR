import json
import networkx as nx

def calculate_hits(web_graph_file, output_prefix="HITS/precomputed_scores/"):
    """Calculate HITS scores from a web graph JSON file."""
    # Load web graph
    with open(web_graph_file) as f:
        web_graph = json.load(f)
    
    # Build directed graph
    G = nx.DiGraph()
    for url, outlinks in web_graph.items():
        G.add_edges_from([(url, target) for target in outlinks])
    
    # Calculate HITS scores
    hubs, authorities = nx.hits(G, max_iter=1000, normalized=True)
    
    # Save results
    with open(f"{output_prefix}hubs_score_2", 'w') as f:
        json.dump(hubs, f)
    with open(f"{output_prefix}authority_score_2", 'w') as f:
        json.dump(authorities, f)

if __name__ == "__main__":
    calculate_hits("../australia_web_graph.json")
