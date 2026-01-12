# backend/main.py: govind  - Entry point for the Custom Logic AI Assistant backend API 
#its main flie being run by FastAPI to handle requests.

import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import requests

from backend.llm_config import get_llm
from backend.mytools.categorize_prompt_tool import create_categorize_prompt_tool
from backend.mytools.find_best_practice_tool import create_get_best_practices_tool
from backend.mytypes.technique_normalizer import  normalize_techniques
from backend.llm import process_user_prompt
from backend.mytools.node_search_tool import  create_node_search_tool
# from data.node_registry import sample_nodes
# from backend.mytypes.technique_normalizer import TECHNIQUE_DEFAULT_QUERY
from backend.n8n_worflow.technique_to_connection import TECHNIQUE_TO_CONNECTION_MAP

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

with open("data/nodes_catalog.json", "r") as f:
    sample_nodes = json.load(f)    

# print(type(sample_nodes))   # <class 'list'>
# print(len(sample_nodes))    # total nodes
# print("sample node json to list data : ",sample_nodes[0])  

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # 1. Categorize the prompt
    llm = get_llm()
    categorize_tool = create_categorize_prompt_tool(llm)
    categorize_result = categorize_tool({"prompt": req.prompt})
    print("Prompt:", req.prompt)
    print("Categorize Result:", categorize_result)
    
    if not isinstance(categorize_result, dict):
        return {"success": False, "message": "Invalid categorization response", "data": None}
    
    # Extract categorization data
    categorization = categorize_result.get("data", {}).get("categorization", {})
    raw_techniques = categorization.get("techniques", [])
    confidence = categorization.get("confidence")
    # Normalize techniques
    print("Raw Techniques:", raw_techniques)
    normalized_techniques = normalize_techniques(raw_techniques)
    # Fetch best practices
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
    
      
    # 4. Node Search (NEW – does not affect old logic)
    node_search_tool = create_node_search_tool(sample_nodes).get("tool")
    
    
    # print(NODE_REGISTRY)
    # print("Node Search Tool:", node_search_tool)

    queries = []

    for technique in normalized_techniques:
      conn_types = TECHNIQUE_TO_CONNECTION_MAP.get(technique)
      print("Technique:", technique.value, "-> Connection Type:", conn_types)

      if not conn_types:
        continue
     
      if isinstance(conn_types, str):
        conn_types = [conn_types]

      for ct in conn_types:
         queries.append({
            "queryType": "subNodeSearch",
            "connectionType": ct,   # ✅ हमेशा STRING
            "query": None,
        })
     
    #  queries.append({   
    #  "queryType": "subNodeSearch",
    #   "connectionType": conn_type,
    #   "query": None,
    # })
      
    print("Queries:", queries)


    
     
    if not queries:
      return {
        "success": True,
        "message": "Prompt analyzed successfully",
        "data": {
            "categorization": {
                "techniques": [t.value for t in normalized_techniques],
                "confidence": confidence,
            },
            # "techniqueCategories": best_practices,
            "nodeSearch": {
                "results": [],
                "totalResults": 0,
                "message": "No matching nodes found for techniques",
            },
        },
    }
    print("Node Search Queries its fine now check further steps ") 

    node_search_input = {"queries": queries}
    
    # print("Node Search Input:", node_search_input)
    # node_search_input = NodeSearchInput(queries=queries)
    node_search_result = node_search_tool.invoke(node_search_input)
    node_search_data = node_search_result.get("data", {})

    print("Node Search Data:", node_search_data)
    print("Node Search Results:", node_search_data.get("results", []))
    # 5. Final response (old + new)
    return {
        "success": True,
        "message": "Prompt analyzed successfully",
        "data": {

            "categorization": {
                "techniques": [t.value for t in normalized_techniques],
                "confidence": confidence,
            },
            # "techniqueCategories": best_practices,
            "nodeSearch": {
                "results": node_search_data.get("results", []),
                "totalResults": node_search_data.get("totalResults", 0),
                "message": node_search_data.get("message", ""),
            },
        },
    }

    # return {
    #     "success": True,
    #     "message": "Prompt categorized successfully",
    #     "data": {
    #         "categorization": {
    #             "techniques": [t.value for t in normalized_techniques],
    #             "confidence": confidence
    #         },
    #         "techniqueCategories": best_practices
    #     }
    # }

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

