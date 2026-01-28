
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from langchain_openai import ChatOpenAI

# ===== YOUR IMPORTS =====
from backend.evalution_chain.best_practice_evalution import evaluateBestPractices
from backend.evalution_chain.data_flow_evalution import evaluateDataFlow
from backend.evalution_chain.evalution import EvaluationInput, EvaluationResult
from backend.evalution_chain.functionality_evalution import evaluateFunctionality
from backend.evalution_chain.maintainability_evalution import evaluateMaintainability
from backend.evalution_chain.node_config_evalution import evaluate_node_configuration
from backend.evalution_chain.workflow_evaluator import evaluate_workflow
from backend.mytypes.workflow import SimpleWorkflow
from backend.llm_config import get_llm # Assuming llm is defined in llm_config.py 
from langchain_core.language_models.chat_models import BaseChatModel
from backend.evalution_chain.connection_evalution import evaluate_connections
from backend.evalution_chain.efficiency_evalution import evaluateEfficiency
from backend.evalution_chain.expression_evalution import evaluateExpressions

# FASTAPI APP
app = FastAPI(
    title="n8n Workflow Evaluator",
    description="Best Practices Evaluator API",
    version="1.0.0",
)

# REQUEST MODEL

class EvaluateRequest(BaseModel):
    userPrompt: str
    generatedWorkflow: dict
    referenceWorkflow: dict | None = None


llm = get_llm()

# ENDPOINT
@app.post("/evaluate/best-practices")
def evaluate_best_practices(request: EvaluateRequest):
    """
    Run best practices evaluator and return raw result
    """
    try:
        evaluation_input = EvaluationInput(
            userPrompt=request.userPrompt,
            generatedWorkflow=SimpleWorkflow(data=request.generatedWorkflow),
            referenceWorkflow=(
                SimpleWorkflow(data=request.referenceWorkflow)
                if request.referenceWorkflow
                else None
            ),
        )

        result =  evaluateBestPractices(
            llm=llm,
            input=evaluation_input,
        )

        # Pydantic v2 safe
        return result

    except Exception as e:
        print(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/evaluate/connections")
def evaluate_connections_api(payload: EvaluationInput):
    try:
        llm: BaseChatModel = get_llm()

        result = evaluate_connections(
            llm=llm,
            input=payload,
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during connections evaluation: {str(e)}",
        )

@app.post("/evaluate/functionality")
def evaluate_functionality_api(payload: EvaluationInput):   
    try:
        llm: BaseChatModel = get_llm()

        result = evaluateFunctionality(
            llm=llm,
            input=payload,
        )

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during functionality evaluation: {str(e)}",
        )   
    
@app.post("/evaluate/data-flow")
def evaluate_data_flow_api(payload: EvaluationInput):
    try:
        llm: BaseChatModel = get_llm()

        result = evaluateDataFlow(
            llm=llm,
            input=payload,
        )

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during data flow evaluation: {str(e)}",
        )
    
@app.post("/evaluate/efficiency")
def evaluate_efficiency_api(payload: EvaluationInput):
    try:
        llm: BaseChatModel = get_llm()

        result = evaluateEfficiency(
            llm=llm,
            input=payload,
        )

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during efficiency evaluation: {str(e)}",
        )
@app.post("/evaluate/expressions")
def evaluate_expressions_api(payload: EvaluationInput):
    try:
        llm: BaseChatModel = get_llm()

        result = evaluateExpressions(
            llm=llm,
            input=payload,
        )

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during expressions evaluation: {str(e)}",
        )

@app.post("/evaluate/maintainability")
def evaluate_maintainability_api(payload: EvaluationInput):
    try:
        llm: BaseChatModel = get_llm()

        result = evaluateMaintainability(
            llm=llm,
            input=payload,
        )

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during maintainability evaluation: {str(e)}",
        )

@app.post("/evaluate/node-configuration")
def evaluate_node_configuration_api(payload: EvaluationInput):
    try:
        llm: BaseChatModel = get_llm()

        result = evaluate_node_configuration(
            llm=llm,
            input=payload,
        )

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during node configuration evaluation: {str(e)}",
        )
    
# @app.post("/evaluate/workflow")
# def evaluate_workflow_api(payload: EvaluationInput):    
#     try:
#         llm: BaseChatModel = get_llm()

#         result = evaluate_workflow(
#             llm=llm,
#             input=payload,
#         )

#         return {
#             "success": True,
#             "data": result
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error during workflow evaluation: {str(e)}",
#         )


@app.post("/evaluate/workflow", response_model=EvaluationResult)
def evaluate_workflow_api(payload: EvaluationInput):
    try:
        llm: BaseChatModel = get_llm()

        result = evaluate_workflow(
            llm=llm,
            input=payload,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during workflow evaluation: {str(e)}",
        )
