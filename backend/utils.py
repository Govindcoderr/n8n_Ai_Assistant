def display_workflow_summary(techniques, best_practices, nodes, ranked_nodes=None):
    summary = "=== Workflow Summary ===\n\n"
    for tech in techniques:
        summary += f"Technique: {tech}\n"
        summary += f"Best Practice: {best_practices.get(tech)}\n"
        summary += f"Recommended Nodes: {', '.join(nodes.get(tech, []))}\n\n"

    if ranked_nodes:
        summary += "=== Ranked Nodes Across Techniques ===\n"
        for node, score in ranked_nodes:
            summary += f"{node}: Score {score}\n"
    return summary
