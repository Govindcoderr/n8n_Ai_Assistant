def score(node):
    s = 0
    if node["native"]: s += 40
    if node["api"]: s += 30
    if node["stable"]: s += 20
    if node["simple"]: s += 10
    return s

def select_best(nodes):
    ranked = sorted(nodes, key=score, reverse=True)
    return ranked[:1]  # ONLY BEST NODE
