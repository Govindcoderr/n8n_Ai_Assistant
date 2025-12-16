from backend.node_selector import select_best

def build_workflow(techniques, catalog):
    steps = []
    for t in techniques:
        nodes = catalog.by_technique(t)
        best = select_best(nodes)
        if best:
            steps.append(best[0])
    return steps
