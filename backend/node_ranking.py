from collections import defaultdict

class NodeRanker:
    def __init__(self, nodes_catalog):
        self.nodes_catalog = nodes_catalog

    def rank_nodes(self, techniques):
        node_scores = defaultdict(int)
        for tech in techniques:
            for item in self.nodes_catalog:
                if item["technique"] == tech:
                    for node in item["nodes"]:
                        node_scores[node] += 10
        ranked_nodes = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked_nodes
