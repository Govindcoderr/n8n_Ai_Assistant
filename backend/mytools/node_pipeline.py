from backend.mytools.dummy_best_practice import dummy_best_practice
from backend.mytools.generate_possible_nodes import generate_possible_nodes
from backend.mytools.select_best_node import select_best_node


def extract_context(best_practice_result: dict) -> dict:
    return {
        "toolName": best_practice_result["toolName"],
        "displayTitle": best_practice_result["displayTitle"],
        "documentation": best_practice_result["tool"]().__doc__
    }


def generate_best_node(final_intent: str) -> dict:
    """
    Dummy pipeline for testing:
    Intent → Dummy Best Practice → Possible Nodes → Best Node
    """

    best_practice = dummy_best_practice()
    bp_context = extract_context(best_practice)

    possible_nodes = generate_possible_nodes(
        final_intent,
        bp_context
    )

    best_node_info = select_best_node(
        final_intent,
        possible_nodes,
        bp_context
    )

    return {
        "possible_nodes": possible_nodes,
        **best_node_info
    }

if __name__ == "__main__":
    result = generate_best_node(
        "Create a workflow that automatically generates dashboard using powerbi"
    )
    print(result)
