import json

class NodeCatalog:
    def __init__(self):
        self.nodes = json.load(open("data/nodes.json"))

    def by_technique(self, technique):
        return [n for n in self.nodes if technique in n["techniques"]]

