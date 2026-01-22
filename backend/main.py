# # backend/main.py: govind  - Entry point for the Custom Logic AI Assistant backend API 
# #its main flie being run by FastAPI to handle requests.

# import json
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Dict
# import requests

# from backend.llm_config import get_llm
# from backend.mytools.categorize_prompt_tool import create_categorize_prompt_tool
# from backend.mytools.find_best_practice_tool import create_get_best_practices_tool
# from backend.mytypes.technique_normalizer import  normalize_techniques
# from backend.llm import process_user_prompt
# from backend.mytools.node_search_tool import  create_node_search_tool
# # from data.node_registry import sample_nodes
# # from backend.mytypes.technique_normalizer import TECHNIQUE_DEFAULT_QUERY
# from backend.n8n_worflow.technique_to_connection import TECHNIQUE_TO_CONNECTION_MAP

# app = FastAPI()  # Entry point for Custom Logic AI Assistant backend

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class AnalyzeRequest(BaseModel):
#     prompt: str

# with open("data/nodes_catalog.json", "r") as f:
#     sample_nodes = json.load(f)    

# # print(type(sample_nodes))   # <class 'list'>
# # print(len(sample_nodes))    # total nodes
# # print("sample node json to list data : ",sample_nodes[0])  

# @app.post("/analyze")
# def analyze(req: AnalyzeRequest):
#     # 1. Categorize the prompt
#     llm = get_llm()
#     categorize_tool = create_categorize_prompt_tool(llm)
#     categorize_result = categorize_tool({"prompt": req.prompt})
#     print("Prompt:", req.prompt)
#     print("Categorize Result:", categorize_result)
    
#     if not isinstance(categorize_result, dict):
#         return {"success": False, "message": "Invalid categorization response", "data": None}
    
#     # Extract categorization data
#     categorization = categorize_result.get("data", {}).get("categorization", {})
#     raw_techniques = categorization.get("techniques", [])
#     confidence = categorization.get("confidence")
#     # Normalize techniques
#     print("Raw Techniques:", raw_techniques)
#     normalized_techniques = normalize_techniques(raw_techniques)
#     # Fetch best practices
#     best_practices = ""
#     best_practice_tool_data = create_get_best_practices_tool()
#     best_practice_tool = best_practice_tool_data.get("tool")

#     if best_practice_tool and normalized_techniques:
#         bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
#         data = bp_result.get("data")
#         if isinstance(data, dict):
#             best_practices = data.get("message", "")
#         elif isinstance(data, str):
#             best_practices = data
    
      
#     # 4. Node Search (NEW – does not affect old logic)
#     node_search_tool = create_node_search_tool(sample_nodes).get("tool")
    
    
#     # print(NODE_REGISTRY)
#     # print("Node Search Tool:", node_search_tool)

#     queries = []

#     for technique in normalized_techniques:
#       conn_types = TECHNIQUE_TO_CONNECTION_MAP.get(technique)
#       print("Technique:", technique.value, "-> Connection Type:", conn_types)

#       if not conn_types:
#         continue
     
#       if isinstance(conn_types, str):
#         conn_types = [conn_types]

#       for ct in conn_types:
#          queries.append({
#             "queryType": ct.name,  # ✅ Enum name
#             "connectionType": ct,   # ✅ हमेशा STRING
#             "query": None,
#         })
     
#     #  queries.append({   
#     #  "queryType": "subNodeSearch",
#     #   "connectionType": conn_type,
#     #   "query": None,
#     # })
      
#     print("Queries:", queries)


    
     
#     if not queries:
#       return {
#         "success": True,
#         "message": "Prompt analyzed successfully",
#         "data": {
#             "categorization": {
#                 "techniques": [t.value for t in normalized_techniques],
#                 "confidence": confidence,
#             },
#             # "techniqueCategories": best_practices,
#             "nodeSearch": {
#                 "results": [],
#                 "totalResults": 0,
#                 "message": "No matching nodes found for techniques",
#             },
#         },
#     }
#     print("Node Search Queries its fine now check further steps ") 

#     node_search_input = {"queries": queries}
    
#     # print("Node Search Input:", node_search_input)
#     # node_search_input = NodeSearchInput(queries=queries)
#     node_search_result = node_search_tool.invoke(node_search_input)
#     node_search_data = node_search_result.get("data", {})

#     print("Node Search Data:", node_search_data)
#     print("Node Search Results:", node_search_data.get("results", []))
#     # 5. Final response (old + new)
#     return {
#         "success": True,
#         "message": "Prompt analyzed successfully",
#         "data": {

#             "categorization": {
#                 "techniques": [t.value for t in normalized_techniques],
#                 "confidence": confidence,
#             },
#             # "techniqueCategories": best_practices,
#             "nodeSearch": {
#                 "results": node_search_data.get("results", []),
#                 "totalResults": node_search_data.get("totalResults", 0),
#                 "message": node_search_data.get("message", ""),
#             },
#         },
#     }

#     # return {
#     #     "success": True,
#     #     "message": "Prompt categorized successfully",
#     #     "data": {
#     #         "categorization": {
#     #             "techniques": [t.value for t in normalized_techniques],
#     #             "confidence": confidence
#     #         },
#     #         "techniqueCategories": best_practices
#     #     }
#     # }

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str

# class ChatSession:
#     def __init__(self):
#         self.history = []

# SESSIONS: Dict[str, ChatSession] = {}

# @app.post("/chat")
# def chat(req: ChatRequest):

#     if req.message == "__FINALIZE__":
#         req.message = "done"

#     if req.session_id not in SESSIONS:
#         SESSIONS[req.session_id] = ChatSession()

#     session = SESSIONS[req.session_id]
#     result = process_user_prompt(req.message, session.history)

#     if result.get("finalized"):
#         final_intent = result["clean_prompt"]
#         analysis = requests.post(
#             "http://localhost:8000/analyze",
#             json={"prompt": final_intent}
#         ).json()
#         del SESSIONS[req.session_id]
#         return {"finalized": True, "final_intent": final_intent, "analysis": analysis}

#     if result.get("stop"):
#         return {"finalized": False, "response": result["reply"]}

#     return {"finalized": False, "response": result["clean_prompt"]}




# backend/main.py - Complete Integration with All Components
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import traceback

from backend.llm_config import get_llm
from backend.mytools.categorize_prompt_tool import create_categorize_prompt_tool
from backend.mytools.find_best_practice_tool import create_get_best_practices_tool
from backend.mytypes.technique_normalizer import normalize_techniques
from backend.mytypes.categorization import WorkflowTechnique
from backend.llm import process_user_prompt

# Import all components
from backend.mytools.parse_best_practices import parse_best_practices, NodeInfo

from backend.mytools.registry_node_generator import (
    generate_workflow_nodes_from_registry,
    format_workflow_nodes_for_api,
)
from backend.mytools.generate_from_parsed_bp import llm_select_and_adapt_nodes_for_intent


app = FastAPI(title="n8n Workflow Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    prompt: str

class node_searchRequest(BaseModel):
    prompt: str
    include_n8n_json: bool = True
    include_parsed_details: bool = True

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        llm = get_llm()

        # STEP 1: Categorize Prompt
        categorize_tool = create_categorize_prompt_tool(llm)
        categorize_result = categorize_tool({"prompt": req.prompt})

        if not isinstance(categorize_result, dict):
            return {"success": False, "message": "Invalid categorization response", "data": None}

        categorization = categorize_result.get("data", {}).get("categorization", {})
        raw_techniques = categorization.get("techniques", [])
        confidence = categorization.get("confidence")
        normalized_techniques = normalize_techniques(raw_techniques)

        # STEP 2: Get Best Practices
        best_practices = ""
        bp_tool_data = create_get_best_practices_tool()
        bp_tool = bp_tool_data.get("tool")

        if bp_tool and normalized_techniques:
            bp_result = bp_tool.invoke({"techniques": normalized_techniques})
            data = bp_result.get("data")
            best_practices = data.get("message", "") if isinstance(data, dict) else data or ""

        # STEP 3: Parse Best Practices
        parsed_bp_nodes = []
        if best_practices:
            try:
                bp_parser = parse_best_practices(best_practices)
                parsed_bp_nodes = bp_parser.nodes
            except Exception as e:
                print(f"BP parsing failed: {e}")

        # STEP 4: Generate Registry Nodes
        registry_nodes = []
        try:
            reg_nodes = generate_workflow_nodes_from_registry(req.prompt)
            registry_nodes = format_workflow_nodes_for_api(reg_nodes)
        except Exception as e:
            print(f"Registry generation failed: {e}")

        # STEP 5: Merge Registry + BP nodes
        merged_nodes = registry_nodes.copy()
        registry_ids = {n["node_id"] for n in registry_nodes}

        for node in parsed_bp_nodes:
            if node.node_id not in registry_ids:
                merged_nodes.append({
                    "name": node.name,
                    "node_id": node.node_id,
                    "category": node.category,
                    "purpose": node.purpose,
                    "pitfalls": node.pitfalls,
                    "use_cases": getattr(node, "use_cases", []),
                    "alternatives": node.alternatives,
                    "input_connections": [],
                    "output_connections": [],
                })

        # STEP 6: LLM Adaptation
        if merged_nodes:
            try:
                node_infos = [
                    NodeInfo(
                        name=n["name"],
                        node_id=n["node_id"],
                        purpose=n["purpose"],
                        category=n["category"],
                        pitfalls=n.get("pitfalls", []),
                        use_cases=n.get("use_cases", []),
                        alternatives=n.get("alternatives", []),
                        input_connections=[],
                        output_connections=[]
                    )
                    for n in merged_nodes
                ]

                adapted = llm_select_and_adapt_nodes_for_intent(
                    user_intent=req.prompt,
                    parsed_nodes=node_infos
                )

                if adapted:
                    merged_nodes = adapted

            except Exception as e:
                print(f"LLM adaptation failed: {e}")

        # STEP 7: Ensure Sequential Connections
        for i, node in enumerate(merged_nodes):
            node.setdefault("input_connections", [])
            node.setdefault("output_connections", [])

            if i > 0:
                node["input_connections"] = [merged_nodes[i - 1]["name"]]
            if i < len(merged_nodes) - 1:
                node["output_connections"] = [merged_nodes[i + 1]["name"]]

        return {
            "success": True,
            "message": "Prompt analyzed successfully",
            "data": {
                "categorization": {
                    "techniques": [t.value for t in normalized_techniques],
                    "confidence": confidence
                },
                "parsedBestPractices": {
                    "nodes": merged_nodes
                }
            }
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to analyze prompt: {str(e)}",
            "data": None
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
    """Enhanced chat endpoint for clean prompt and get intent finalization."""
    try:
        if req.message == "__FINALIZE__":
            req.message = "done"

        if req.session_id not in SESSIONS:
            SESSIONS[req.session_id] = ChatSession()

        session = SESSIONS[req.session_id]
        result = process_user_prompt(req.message, session.history)

        if result.get("finalized"):
            final_intent = result["clean_prompt"]
            
            # Get analysis
            analysis = None
            try:
                analysis = analyze(AnalyzeRequest(prompt=final_intent))
            except Exception as e:
                print(f"Error getting analysis: {e}")
                analysis = {"success": False, "error": str(e)}
            
            # Clean up session
            if req.session_id in SESSIONS:
                del SESSIONS[req.session_id]
            
            return {"finalized": True, "final_intent": final_intent, "analysis": analysis}

        if result.get("stop"):
            return {"finalized": False, "response": result["reply"]}

        return {"finalized": False, "response": result["clean_prompt"]}
        
    except Exception as e:
        print(f"Error in /chat: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Optional , Any, Dict, List

# from backend.mytools.add_node_tool import create_add_node_tool
# from backend.mytools.get_node_details_tool import create_node_details_tool
# from backend.mytools.helpers.state import get_workflow_state
# from backend.mytools.get_node_details_tool import INodeTypeDescription
# from data.node_registry import sample_nodes


# app = FastAPI(title="Node Details API")


# sample_nodes = [
#     INodeTypeDescription(**node_dict)
#     for node_dict in sample_nodes
# ]


# tool_config = create_node_details_tool(sample_nodes)
# node_details_tool = tool_config["tool"]

# # Request schema

# class NodeDetailsRequest(BaseModel):
#     nodeName: str
#     nodeVersion: int
#     withParameters: Optional[bool] = False
#     withConnections: Optional[bool] = True

# # API Endpoint

# @app.post("/node-details")
# def get_node_details_api(payload: NodeDetailsRequest):
#     try:
#         result = node_details_tool.invoke(payload.dict())
#         return {
#             "success": True,
#             "data": result
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- test for add node tool api --------------------------

# # ts code for test the api for **add node tool**
# from typing import Dict, Any, List

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware

# from backend.mytools.add_node_tool import (
#     create_add_node_tool,
#     NodeTypeDescription,
# )

# # =========================================================
# # App Initialization
# # =========================================================

# app = FastAPI(
#     title="Workflow Builder API",
#     description="Deterministic workflow builder powered by LangChain tools",
#     version="1.0.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # =========================================================
# # Node Registry (normally loaded dynamically)
# # =========================================================

# NODE_TYPES: List[NodeTypeDescription] = [
#     NodeTypeDescription(
#         name="n8n-nodes-base.httpRequest",
#         display_name="HTTP Request",
#     ),
#     NodeTypeDescription(
#         name="n8n-nodes-base.set",
#         display_name="Set",
#     ),
#     NodeTypeDescription(
#         name="n8n-nodes-langchain.agent",
#         display_name="AI Agent",
#         is_sub_node=True,
#     ),
# ]

# # =========================================================
# # Tool Initialization
# # =========================================================

# add_node_tool = create_add_node_tool(NODE_TYPES)


# # =========================================================
# # Add Node Endpoint
# # =========================================================

# @app.post("/tools/add-node")
# def add_node(payload: Dict[str, Any]):
#     """
#     Executes the Add Node LangChain tool via HTTP.

#     This endpoint is intentionally thin:
#     - No business logic
#     - No validation duplication
#     - Delegates everything to the tool layer
#     """

#     try:
#         # Tool config can carry runtime flags
#         tool_config = {
#             "E2E_TESTS": False,
#         }

#         result = add_node_tool.func(payload, tool_config)

#         if not result.get("success"):
#             raise HTTPException(
#                 status_code=400,
#                 detail=result.get("error"),
#             )

#         return result

#     except HTTPException:
#         raise

#     except Exception as ex:
#         raise HTTPException(
#             status_code=500,
#             detail=str(ex),
#         )



#-----------------------test end for add node tool api --------------------------- 


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Dict, Any

# from backend.mytools.add_node_tool import create_add_node_tool
# # from backend.mytools import NODE_TYPES  # list[INodeTypeDescription]
# from backend.n8n_worflow.inode_type_description import INodeTypeDescription

# from dataclasses import dataclass
# from typing import Optional, Dict, Any



# sample_nodes: list[INodeTypeDescription] = [
#     INodeTypeDescription(
#         name="n8n-nodes-base.httpRequest",
#         displayName="HTTP Request",
#         version=1,
#         inputs=["main"],
#     ),
#     INodeTypeDescription(
#         name="n8n-nodes-base.set",
#         displayName="Set",
#         version=1,
#         inputs=["main"],
#     ),
#     INodeTypeDescription(
#         name="@n8n/n8n-nodes-langchain.agent",
#         displayName="AI Agent",
#         version=1,
#         inputs=[],
        
#     ),
# ]


# app = FastAPI(
#     title="Workflow Builder Tool Tester",
#     version="1.0.0",
# )

# # CORS (important for UI / Streamlit / Frontend testing)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize tool once (important)
# add_node_tool_wrapper = create_add_node_tool(sample_nodes)
# print("Add Node Tool Wrapper Created:")
# print(dir(add_node_tool_wrapper))
# add_node_tool = add_node_tool_wrapper.tool
# print("Add Node Tool Created:")
# print(add_node_tool)
# print(dir(add_node_tool))

# class ToolRequest(BaseModel):
#     input: Dict[str, Any]
#     config: Dict[str, Any] = {}

# class ToolResponse(BaseModel):
#     success: bool
#     data: Dict[str, Any] | None = None
#     error: Dict[str, Any] | None = None

# @app.post("/tools/add-node", response_model=ToolResponse)
# async def test_add_node(request: ToolRequest):
#     """
#     Endpoint to test add_nodes LangChain tool.
#     Delegates all logic to the tool layer.
#     Args:
#         request (ToolRequest): Input and config for the tool.
#     Returns:
#         ToolResponse: Standardized response from the tool.

#     """

#     try:
#         result = await add_node_tool.ainvoke({
#             "payload": {
#                 "input_data": request.input,
#                 "config": request.config,
#             }
#         })
#         print("Add Node Tool Result:")
#         print(result)

#         # Success response format (aligned with createSuccessResponse)
#         return ToolResponse(
#             success=True,
#             data=result,
#         )

#     except Exception as e:
#         # Fallback safety net
#         return ToolResponse(
#             success=False,
#             error={
#                 "message": str(e),
#                 "code": "FASTAPI_EXECUTION_ERROR",
#             },
#         )

