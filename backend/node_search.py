import json

class NodeSearcher:
    def __init__(self, nodes_catalog_file):
        with open(nodes_catalog_file, "r") as f:
            self.nodes_catalog = json.load(f)

    def search_nodes(self, techniques):
        nodes_result = {}
        for tech in techniques:
            nodes = next((item["nodes"] for item in self.nodes_catalog if item["technique"] == tech), [])
            nodes_result[tech] = nodes
        return nodes_result

    def get_all_nodes(self):
        return self.nodes_catalog
