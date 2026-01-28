from typing import Optional, List, Dict
from langchain.chat_models.base import BaseChatModel


from ..evalution_chain.evalution import EvaluationInput, EvaluationResult
from backend.evalution_chain.connection_evalution import evaluate_connections
from backend.evalution_chain.functionality_evalution import evaluateFunctionality
from backend.evalution_chain.node_config_evalution import evaluate_node_configuration
from backend.evalution_chain.best_practice_evalution import evaluateBestPractices
from backend.evalution_chain.efficiency_evalution import  evaluateEfficiency
from backend.evalution_chain.expression_evalution import  evaluateExpressions
from backend.evalution_chain.data_flow_evalution import evaluateDataFlow 
from backend.evalution_chain.maintainability_evalution import evaluateMaintainability



def calculate_weighted_score(result: EvaluationResult) -> float:
    weights = {
        "functionality": 0.25,
        "connections": 0.15,
        "expressions": 0.15,
        "nodeConfiguration": 0.15,
        "efficiency": 0.10,
        "dataFlow": 0.10,
        "maintainability": 0.05,
        "bestPractices": 0.10,
        "structuralSimilarity": 0.05,
    }

    total_weight = 0.0
    weighted_sum = 0.0

    # Core categories
    weighted_sum += result.functionality.score * weights["functionality"]
    weighted_sum += result.connections.score * weights["connections"]
    weighted_sum += result.expressions.score * weights["expressions"]
    weighted_sum += result.nodeConfiguration.score * weights["nodeConfiguration"]

    total_weight += (
        weights["functionality"]
        + weights["connections"]
        + weights["expressions"]
        + weights["nodeConfiguration"]
    )

    # New metrics
    weighted_sum += result.efficiency.score * weights["efficiency"]
    weighted_sum += result.dataFlow.score * weights["dataFlow"]
    weighted_sum += result.maintainability.score * weights["maintainability"]
    weighted_sum += result.bestPractices.score * weights["bestPractices"]

    total_weight += (
        weights["efficiency"]
        + weights["dataFlow"]
        + weights["maintainability"]
        + weights["bestPractices"]
    )

    # Structural similarity (optional)
    if result.structuralSimilarity and result.structuralSimilarity.applicable:
        weighted_sum += (
            result.structuralSimilarity.score * weights["structuralSimilarity"]
        )
        total_weight += weights["structuralSimilarity"]

    return weighted_sum / total_weight if total_weight > 0 else 0.0

def generate_evaluation_summary(result: EvaluationResult) -> str:
    strengths: List[str] = []
    weaknesses: List[str] = []

    if result.functionality.score >= 0.8:
        strengths.append("strong functional implementation")
    elif result.functionality.score < 0.5:
        weaknesses.append("functional gaps")

    if result.connections.score >= 0.8:
        strengths.append("well-connected nodes")
    elif result.connections.score < 0.5:
        weaknesses.append("connection issues")

    if result.expressions.score >= 0.8:
        strengths.append("correct expression syntax")
    elif result.expressions.score < 0.5:
        weaknesses.append("expression errors")

    if result.nodeConfiguration.score >= 0.8:
        strengths.append("well-configured nodes")
    elif result.nodeConfiguration.score < 0.5:
        weaknesses.append("node configuration issues")

    if result.dataFlow.score >= 0.8:
        strengths.append("proper data flow")
    elif result.dataFlow.score < 0.5:
        weaknesses.append("data flow problems")

    if result.efficiency.score >= 0.8:
        strengths.append("efficient design")
    elif result.efficiency.score < 0.5:
        weaknesses.append("inefficiencies")

    if result.maintainability.score >= 0.8:
        strengths.append("maintainable structure")
    elif result.maintainability.score < 0.5:
        weaknesses.append("poor maintainability")

    if result.bestPractices.score >= 0.8:
        strengths.append("follows best practices")
    elif result.bestPractices.score < 0.5:
        weaknesses.append("deviates from best practices")

    summary = ""

    if strengths:
        summary += f"The workflow demonstrates {', '.join(strengths)}."
    if weaknesses:
        summary += f" Key areas for improvement include {', '.join(weaknesses)}."

    if not summary:
        summary = "The workflow shows adequate implementation across all evaluated metrics."

    return summary.strip()

def identify_critical_issues(result: EvaluationResult) -> Optional[List[str]]:
    critical_issues: List[str] = []

    categories = [
        ("functionality", result.functionality),
        ("connections", result.connections),
        ("expressions", result.expressions),
        ("nodeConfiguration", result.nodeConfiguration),
        ("efficiency", result.efficiency),
        ("dataFlow", result.dataFlow),
        ("maintainability", result.maintainability),
        ("bestPractices", result.bestPractices),
    ]

    for name, data in categories:
        if not data:
            continue

        for violation in data.violations:
            if violation.type == "critical":
                critical_issues.append(f"[{name}] {violation.description}")

    return critical_issues if critical_issues else None

# Helper to convert models to dicts
def to_dict(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj


# def evaluate_workflow(llm: BaseChatModel, input: EvaluationInput) -> EvaluationResult:

#     functionality = evaluateFunctionality(llm, input)
#     connections = evaluate_connections(llm, input)
#     expressions = evaluateExpressions(llm, input)
#     node_configuration = evaluate_node_configuration(llm, input)
#     efficiency = evaluateEfficiency(llm, input)
#     data_flow = evaluateDataFlow(llm, input)
#     maintainability = evaluateMaintainability(llm, input)
#     best_practices = evaluateBestPractices(llm, input)

#     evaluation_result = EvaluationResult(
#         overallScore=0.0,
#         functionality=functionality.model_dump(),
#         connections=connections.model_dump(),
#         expressions=expressions.model_dump(),
#         nodeConfiguration=node_configuration.model_dump(),
#         efficiency=efficiency.model_dump(),
#         dataFlow=data_flow.model_dump(),
#         maintainability=maintainability.model_dump(),
#         bestPractices=best_practices,
#         structuralSimilarity={
#             "violations": [],
#             "score": 0.0,
#             "applicable": False,
#         },
#         summary="",
#         criticalIssues=None,
#     )

#     evaluation_result.overallScore = calculate_weighted_score(evaluation_result)
#     evaluation_result.summary = generate_evaluation_summary(evaluation_result)
#     evaluation_result.criticalIssues = identify_critical_issues(evaluation_result)

#     return evaluation_result

def evaluate_workflow(llm: BaseChatModel, input: EvaluationInput) -> EvaluationResult:

    functionality = evaluateFunctionality(llm, input)
    connections = evaluate_connections(llm, input)
    expressions = evaluateExpressions(llm, input)
    node_configuration = evaluate_node_configuration(llm, input)
    efficiency = evaluateEfficiency(llm, input)
    data_flow = evaluateDataFlow(llm, input)
    maintainability = evaluateMaintainability(llm, input)
    best_practices = evaluateBestPractices(llm, input)

    evaluation_result = EvaluationResult(
        overallScore=0.0,

        functionality=to_dict(functionality),
        connections=to_dict(connections),
        expressions=to_dict(expressions),
        nodeConfiguration=to_dict(node_configuration),

        efficiency=to_dict(efficiency),
        dataFlow=to_dict(data_flow),
        maintainability=to_dict(maintainability),
        bestPractices=to_dict(best_practices),

        structuralSimilarity={
            "violations": [],
            "score": 0.0,
            "applicable": False,
        },

        summary="",
        criticalIssues=None,
    )

    evaluation_result.overallScore = calculate_weighted_score(evaluation_result)
    evaluation_result.summary = generate_evaluation_summary(evaluation_result)
    evaluation_result.criticalIssues = identify_critical_issues(evaluation_result)

    return evaluation_result
