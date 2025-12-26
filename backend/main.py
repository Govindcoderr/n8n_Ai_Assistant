# # backend/main.py: govind  - Entry point for the Custom Logic AI Assistant backend API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import requests
from backend.node_generator.generator import generate_nodes
from backend.llm_config import get_llm
from backend.mytools.categorize_prompt import create_categorize_prompt_tool
from backend.mytools.find_best_practice import create_get_best_practices_tool
from backend.mytypes.technique_normalizer import normalize_techniques
from backend.llm import process_user_prompt

app = FastAPI()  # Entry point for Custom Logic AI Assistant backend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    prompt: str

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    llm = get_llm()
    categorize_tool = create_categorize_prompt_tool(llm)
    categorize_result = categorize_tool({"prompt": req.prompt})

    if not isinstance(categorize_result, dict):
        return {"success": False, "message": "Invalid categorization response", "data": None}

    categorization = categorize_result.get("data", {}).get("categorization", {})
    raw_techniques = categorization.get("techniques", [])
    confidence = categorization.get("confidence")

    normalized_techniques = normalize_techniques(raw_techniques)

    best_practices = ""
    best_practice_tool_data = create_get_best_practices_tool()
    best_practice_tool = best_practice_tool_data.get("tool")

    if best_practice_tool and normalized_techniques:
        bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
        data = bp_result.get("data")
        if isinstance(data, dict):
            best_practices = data.get("message", "")
        elif isinstance(data, str):
            best_practices = data

    return {
        "success": True,
        "message": "Prompt categorized successfully",
        "data": {
            "categorization": {
                "techniques": [t.value for t in normalized_techniques],
                "confidence": confidence
            },
            "techniqueCategories": best_practices
        }
    }

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatSession:
    def __init__(self):
        self.history = []

SESSIONS: Dict[str, ChatSession] = {}

@app.post("/chat")
def chat(req: ChatRequest):

    if req.message == "__FINALIZE__":
        req.message = "done"

    if req.session_id not in SESSIONS:
        SESSIONS[req.session_id] = ChatSession()

    session = SESSIONS[req.session_id]
    result = process_user_prompt(req.message, session.history)

    if result.get("finalized"):
        final_intent = result["clean_prompt"]
        analysis = requests.post(
            "http://localhost:8000/analyze",
            json={"prompt": final_intent}
        ).json()
        del SESSIONS[req.session_id]
        return {"finalized": True, "final_intent": final_intent, "analysis": analysis}

    if result.get("stop"):
        return {"finalized": False, "response": result["reply"]}

    return {"finalized": False, "response": result["clean_prompt"]}


# from backend.mytools.select_best_node import generate_nodes_from_analysis
# class AnalyzeRequest(BaseModel):
#     prompt: str

# @app.post("/workflow/nodes")
# def get_workflow_nodes(req: AnalyzeRequest):
#     analysis = analyze(req)
#     nodes = generate_nodes_from_analysis(analysis)

#     return {
#         "success": True,
#         "techniques": analysis["data"]["categorization"]["techniques"],
#         "nodes": nodes
#     }

