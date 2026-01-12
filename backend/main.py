# # # backend/main.py: govind  - Entry point for the Custom Logic AI Assistant backend API

# # # # backend/main.py: govind  - Entry point for the Custom Logic AI Assistant backend API

# # from fastapi import FastAPI
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel
# # from typing import Dict
# # import requests
# # from backend.llm_config import get_llm
# # from backend.mytools.categorize_prompt import create_categorize_prompt_tool
# # from backend.mytools.find_best_practice import create_get_best_practices_tool
# # from backend.mytypes.technique_normalizer import normalize_techniques
# # from backend.llm import process_user_prompt
# # from backend.node_generator.search_node_engine import search_node_engine
# # app = FastAPI()  # Entry point for Custom Logic AI Assistant backend

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # class AnalyzeRequest(BaseModel):
# #     prompt: str

# # @app.post("/analyze")
# # def analyze(req: AnalyzeRequest):
# #     llm = get_llm()
# #     categorize_tool = create_categorize_prompt_tool(llm)
# #     categorize_result = categorize_tool({"prompt": req.prompt})

# #     if not isinstance(categorize_result, dict):
# #         return {"success": False, "message": "Invalid categorization response", "data": None}

# #     categorization = categorize_result.get("data", {}).get("categorization", {})
# #     raw_techniques = categorization.get("techniques", [])
# #     confidence = categorization.get("confidence")

# #     normalized_techniques = normalize_techniques(raw_techniques)

# #     best_practices = ""
# #     best_practice_tool_data = create_get_best_practices_tool()
# #     best_practice_tool = best_practice_tool_data.get("tool")

# #     if best_practice_tool and normalized_techniques:
# #         bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
# #         data = bp_result.get("data")
# #         if isinstance(data, dict):
# #             best_practices = data.get("message", "")
# #         elif isinstance(data, str):
# #             best_practices = data
    
# #     node_engine_result = search_node_engine(
# #         final_intent=req.prompt,
# #         best_practice_text=best_practices,
# #         )

# #     return {
# #         "success": True,
# #         "message": "Prompt categorized successfully",
# #         "data": {
# #             "categorization": {
# #                 "techniques": [t.value for t in normalized_techniques],
# #                 "confidence": confidence
# #             },
# #             "techniqueCategories": best_practices,
# #             "node":[t.value for t in node_engine_result["possible_nodes"]],
# #         }
# #     }

# # class ChatRequest(BaseModel):
# #     session_id: str
# #     message: str

# # class ChatSession:
# #     def __init__(self):
# #         self.history = []

# # SESSIONS: Dict[str, ChatSession] = {}

# # @app.post("/chat")
# # def chat(req: ChatRequest):

# #     if req.message == "__FINALIZE__":
# #         req.message = "done"

# #     if req.session_id not in SESSIONS:
# #         SESSIONS[req.session_id] = ChatSession()

# #     session = SESSIONS[req.session_id]
# #     result = process_user_prompt(req.message, session.history)

# #     if result.get("finalized"):
# #         final_intent = result["clean_prompt"]
# #         analysis = requests.post(
# #             "http://localhost:8000/analyze",
# #             json={"prompt": final_intent}
# #         ).json()
# #         del SESSIONS[req.session_id]
# #         return {"finalized": True, "final_intent": final_intent, "analysis": analysis}

# #     if result.get("stop"):
# #         return {"finalized": False, "response": result["reply"]}

# #     return {"finalized": False, "response": result["clean_prompt"]}


# # # from backend.mytools.select_best_node import generate_nodes_from_analysis
# # # class AnalyzeRequest(BaseModel):
# # #     prompt: str

# # # @app.post("/workflow/nodes")
# # # def get_workflow_nodes(req: AnalyzeRequest):
# # #     analysis = analyze(req)
# # #     nodes = generate_nodes_from_analysis(analysis)

# # #     return {
# # #         "success": True,
# # #         "techniques": analysis["data"]["categorization"]["techniques"],
# # #         "nodes": nodes
# # #     }

# # backend/main.py - Fixed and Production Ready

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Dict, List, Optional
# import traceback
# import json
# import re
# from backend.llm_config import get_llm
# from backend.mytools.categorize_prompt_tool import create_categorize_prompt_tool
# from backend.mytools.find_best_practice_tool import create_get_best_practices_tool
# from backend.mytools.generate_from_parsed_bp import GeneratedWorkflow, GenerateWorkflowRequest
# from backend.mytypes.technique_normalizer import normalize_techniques
# from backend.llm import process_user_prompt

# app = FastAPI()  # Entry point for Custom Logic AI Assistant backend
# import requests
# import traceback
# from backend.llm_config import get_llm
# from backend.mytools.categorize_prompt import create_categorize_prompt_tool
# from backend.mytools.find_best_practice import create_get_best_practices_tool
# from backend.mytypes.technique_normalizer import normalize_techniques
# from backend.llm import process_user_prompt

# # New imports for best practice parsing and workflow generation
# from backend.mytools.parse_best_practices import parse_best_practices
# from backend.mytools.generate_from_parsed_bp import (
#     generate_workflow_from_parsed_bp,
#     workflow_to_n8n_format
# )

# app = FastAPI(title="n8n Workflow Generator API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class AnalyzeRequest(BaseModel):
#     prompt: str

# @app.post("/analyze")
# def analyze(req: AnalyzeRequest):
#     llm = get_llm()
#     categorize_tool = create_categorize_prompt_tool(llm)
#     categorize_result = categorize_tool({"prompt": req.prompt})

#     if not isinstance(categorize_result, dict):
#         return {"success": False, "message": "Invalid categorization response", "data": None}

#     categorization = categorize_result.get("data", {}).get("categorization", {})
#     raw_techniques = categorization.get("techniques", [])
#     confidence = categorization.get("confidence")

#     normalized_techniques = normalize_techniques(raw_techniques)

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

#     return {
#         "success": True,
#         "message": "Prompt categorized successfully",
#         "data": {
#             "categorization": {
#                 "techniques": [t.value for t in normalized_techniques],
#                 "confidence": confidence
#             },
#             "techniqueCategories": best_practices
#         }
#     }

# class AnalyzeRequest(BaseModel):
#     prompt: str


# class GenerateWorkflowRequest(BaseModel):
#     prompt: str
#     include_n8n_json: bool = False
#     include_parsed_details: bool = False


# def safe_get_node_engine_results(prompt: str, best_practices: str) -> List[str]:
#     """
#     Safely call search_node_engine if available, otherwise return empty list.
#     """
#     try:
#         from backend.node_generator.search_node_engine import search_node_engine
#         import inspect
        
#         # Get function signature
#         sig = inspect.signature(search_node_engine)
#         params = list(sig.parameters.keys())
        
#         # Build kwargs based on available parameters
#         kwargs = {}
        
#         # Map our parameters to the function's expected parameters
#         param_mapping = {
#             'user_prompt': prompt,
#             'prompt': prompt,
#             'final_intent': prompt,
#             'intent': prompt,
#             'best_practices': best_practices,
#             'best_practice_text': best_practices,
#             'best_practices_text': best_practices,
#             'bp_text': best_practices
#         }
        
#         for param_name in params:
#             if param_name in param_mapping:
#                 kwargs[param_name] = param_mapping[param_name]
        
#         result = search_node_engine(**kwargs)
        
#         # Extract possible_nodes from result
#         if isinstance(result, dict) and 'possible_nodes' in result:
#             nodes = result['possible_nodes']
#             if isinstance(nodes, list):
#                 return [str(n.value) if hasattr(n, 'value') else str(n) for n in nodes]
        
#         return []
        
#     except Exception as e:
#         print(f"Warning: search_node_engine not available or failed: {e}")
#         return []


# @app.post("/analyze")
# def analyze(req: AnalyzeRequest):
#     """
#     Enhanced analyze endpoint with full best practice parsing.
    
#     Returns:
#     - Categorization (techniques, confidence)
#     - Best practices text
#     - Parsed node information from best practices
#     - Workflow patterns
#     - Critical instructions
#     - Node engine results (if available)
#     """
#     try:
#         llm = get_llm()
#         categorize_tool = create_categorize_prompt_tool(llm)
#         categorize_result = categorize_tool({"prompt": req.prompt})

#         if not isinstance(categorize_result, dict):
#             return {"success": False, "message": "Invalid categorization response", "data": None}

#         categorization = categorize_result.get("data", {}).get("categorization", {})
#         raw_techniques = categorization.get("techniques", [])
#         confidence = categorization.get("confidence")

#         normalized_techniques = normalize_techniques(raw_techniques)

#         # Get best practices
#         best_practices = ""
#         best_practice_tool_data = create_get_best_practices_tool()
#         best_practice_tool = best_practice_tool_data.get("tool")

#         if best_practice_tool and normalized_techniques:
#             bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
#             data = bp_result.get("data")
#             if isinstance(data, dict):
#                 best_practices = data.get("message", "")
#             elif isinstance(data, str):
#                 best_practices = data
        
#         # Parse best practices to extract structured node information
#         parsed_bp = None
#         parsed_nodes = []
#         workflow_patterns = []
#         critical_instructions = []
        
#         if best_practices:
#             try:
#                 bp_parser = parse_best_practices(best_practices)
                
#                 parsed_nodes = [
#                     {
#                         "name": node.name,
#                         "node_id": node.node_id,
#                         "category": node.category,
#                         "purpose": node.purpose,
#                         "pitfalls": node.pitfalls,
#                         "use_cases": node.use_cases,
#                         "alternatives": node.alternatives
#                     }
#                     for node in bp_parser.nodes
#                 ]
                
#                 workflow_patterns = [
#                     {
#                         "description": pattern.description,
#                         "nodes_sequence": pattern.nodes_sequence
#                     }
#                     for pattern in bp_parser.patterns
#                 ]
                
#                 critical_instructions = bp_parser.critical_instructions
#                 parsed_bp = bp_parser.to_dict()
                
#             except Exception as e:
#                 print(f"Error parsing best practices: {e}")
        
#         # Use node engine for additional suggestions (safely)
#         node_engine_results = safe_get_node_engine_results(req.prompt, best_practices)

#         return {
#             "success": True,
#             "message": "Prompt analyzed successfully",
#             "data": {
#                 "categorization": {
#                     "techniques": [t.value for t in normalized_techniques],
#                     "confidence": confidence
#                 },
#                 # "bestPracticesText": best_practices,
#                 "parsedNodes": parsed_nodes,
#                 "workflowPatterns": workflow_patterns,
#                 "criticalInstructions": critical_instructions,
#                 "nodeEngineResults": node_engine_results,
#                 "parsedBestPractices": parsed_bp
#             }
#         }
        
#     except Exception as e:
#         print(f"Error in /analyze: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/workflow/generate")
# def generate_workflow(req: GenerateWorkflowRequest):
#     """
#     Generate complete workflow from user intent using parsed best practices.
    
#     Process:
#     1. Categorize the prompt
#     2. Get best practices documentation
#     3. Parse best practices to extract nodes
#     4. Select appropriate nodes for user intent
#     5. Generate workflow with proper connections
#     6. Return n8n-compatible JSON
#     """
    
#     try:
#         # Step 1: Categorize
#         llm = get_llm()
#         categorize_tool = create_categorize_prompt_tool(llm)
#         categorize_result = categorize_tool({"prompt": req.prompt})

#         if not isinstance(categorize_result, dict):
#             return {"success": False, "error": "Invalid categorization response"}

#         categorization = categorize_result.get("data", {}).get("categorization", {})
#         raw_techniques = categorization.get("techniques", [])
#         normalized_techniques = normalize_techniques(raw_techniques)
        
#         # Step 2: Get best practices
#         best_practices = ""
#         best_practice_tool_data = create_get_best_practices_tool()
#         best_practice_tool = best_practice_tool_data.get("tool")

#         if best_practice_tool and normalized_techniques:
#             bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
#             data = bp_result.get("data")
#             if isinstance(data, dict):
#                 best_practices = data.get("message", "")
#             elif isinstance(data, str):
#                 best_practices = data
        
#         if not best_practices:
#             return {
#                 "success": False,
#                 "error": "No best practices found for this workflow type"
#             }
        
#         # Step 3-5: Parse best practices and generate workflow
#         generated_workflow = generate_workflow_from_parsed_bp(
#             user_intent=req.prompt,
#             best_practices_text=best_practices,
#             techniques=[t.value for t in normalized_techniques]
#         )
        
#         response_data = {
#             "success": True,
#             "workflow": {
#                 "description": generated_workflow.description,
#                 "nodes": [
#                     {
#                         "id": node.id,
#                         "name": node.name,
#                         "type": node.type,
#                         "position": node.position,
#                         "parameters": node.parameters,
#                         "notes": node.notes
#                     }
#                     for node in generated_workflow.nodes
#                 ],
#                 "connections": [
#                     {
#                         "source": conn.source,
#                         "target": conn.target,
#                         "sourceOutput": conn.source_output,
#                         "targetInput": conn.target_input
#                     }
#                     for conn in generated_workflow.connections
#                 ],
#                 "metadata": generated_workflow.metadata
#             },
#             "techniques": [t.value for t in normalized_techniques]
#         }
        
#         # Include n8n-compatible JSON if requested
#         if req.include_n8n_json:
#             response_data["n8nWorkflow"] = workflow_to_n8n_format(generated_workflow)
        
#         # Include parsed details if requested
#         if req.include_parsed_details:
#             bp_parser = parse_best_practices(best_practices)
#             response_data["parsedBestPractices"] = bp_parser.to_dict()
        
#         return response_data
        
#     except Exception as e:
#         print(f"Error in /workflow/generate: {e}")
#         traceback.print_exc()
#         return {
#             "success": False,
#             "error": f"Failed to generate workflow: {str(e)}",
#             "trace": traceback.format_exc()
#         }


# @app.post("/workflow/parse-best-practices")
# def parse_best_practices_endpoint(req: AnalyzeRequest):
#     """
#     Debug endpoint to see parsed best practices for any prompt.
#     """
    
#     try:
#         llm = get_llm()
#         categorize_tool = create_categorize_prompt_tool(llm)
#         categorize_result = categorize_tool({"prompt": req.prompt})

#         if not isinstance(categorize_result, dict):
#             return {"success": False, "error": "Invalid categorization"}

#         categorization = categorize_result.get("data", {}).get("categorization", {})
#         raw_techniques = categorization.get("techniques", [])
#         normalized_techniques = normalize_techniques(raw_techniques)
        
#         # Get best practices
#         best_practices = ""
#         best_practice_tool_data = create_get_best_practices_tool()
#         best_practice_tool = best_practice_tool_data.get("tool")

#         if best_practice_tool and normalized_techniques:
#             bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
#             data = bp_result.get("data")
#             if isinstance(data, dict):
#                 best_practices = data.get("message", "")
#             elif isinstance(data, str):
#                 best_practices = data
        
#         if not best_practices:
#             return {"success": False, "error": "No best practices found"}
        
#         bp_parser = parse_best_practices(best_practices)
        
#         return {
#             "success": True,
#             "data": {
#                 "summary": bp_parser.format_summary(),
#                 "detailed": bp_parser.to_dict(),
#                 "techniques": [t.value for t in normalized_techniques]
#             }
#         }
        
#     except Exception as e:
#         print(f"Error in /workflow/parse-best-practices: {e}")
#         traceback.print_exc()
#         return {"success": False, "error": str(e)}


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ChatSession:
#     def __init__(self):
#         self.history = []

# SESSIONS: Dict[str, ChatSession] = {}

# @app.post("/chat")
# def chat(req: ChatRequest):
#     """Enhanced chat endpoint with full workflow generation."""

# SESSIONS: Dict[str, ChatSession] = {}


# @app.post("/chat")
# def chat(req: ChatRequest):
#     """
#     Enhanced chat endpoint with full workflow generation.
#     """
    
#     try:
#         if req.message == "__FINALIZE__":
#             req.message = "done"

#         if req.session_id not in SESSIONS:
#             SESSIONS[req.session_id] = ChatSession()

#         session = SESSIONS[req.session_id]
#         result = process_user_prompt(req.message, session.history)

#         if result.get("finalized"):
#             final_intent = result["clean_prompt"]
            
#             # Generate complete workflow
#             workflow_result = GeneratedWorkflow(
#             # Generate complete workflow using parsed best practices
#             workflow_result = generate_workflow(
#                 GenerateWorkflowRequest(
#                     prompt=final_intent,
#                     include_n8n_json=True,
#                     include_parsed_details=True
#                 )
#             )
            
#             # Get analysis
#             analysis = None
#             try:
#             # Get basic analysis (with proper error handling)
#             analysis = None
#             try:
#                 # Call analyze directly instead of making HTTP request to avoid circular dependency
#                 analysis = analyze(AnalyzeRequest(prompt=final_intent))
#             except Exception as e:
#                 print(f"Error getting analysis: {e}")
#                 analysis = {"success": False, "error": str(e)}
            
#             # Clean up session
#             if req.session_id in SESSIONS:
#                 del SESSIONS[req.session_id]
            
#             return {
#                 "finalized": True,
#                 "final_intent": final_intent,
#                 "analysis": analysis,
#                 "workflow": workflow_result.get("workflow") if workflow_result.get("success") else None,
#                 "n8nWorkflow": workflow_result.get("n8nWorkflow") if workflow_result.get("success") else None,
#                 "parsedBestPractices": workflow_result.get("parsedBestPractices") if workflow_result.get("success") else None,
#                 "error": workflow_result.get("error") if not workflow_result.get("success") else None
#             }

#         if result.get("stop"):
#             return {"finalized": False, "response": result["reply"]}

#         return {"finalized": False, "response": result["clean_prompt"]}
        
#     except Exception as e:
#         print(f"Error in /chat: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))



# backend/main.py - Complete Integration with All Components
# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "service": "n8n-workflow-generator",
#         "version": "2.0.0",
#         "features": [
#             "best-practice-parsing",
#             "node-extraction",
#             "workflow-generation",
#             "n8n-json-export",
#             "chat-interface"
#         ]
#     }


# @app.get("/debug/best-practices")
# def debug_best_practices():
#     """
#     Debug endpoint to view all available best practices.
#     """
#     try:
#         from backend.mytools.best_practices.index import documentation
        
#         available = []
#         for technique, doc_class in documentation.items():
#             doc_preview = doc_class.get_documentation()[:200] if hasattr(doc_class, 'get_documentation') else "N/A"
#             available.append({
#                 "technique": technique.value if hasattr(technique, 'value') else str(technique),
#                 "version": doc_class.version if hasattr(doc_class, 'version') else "N/A",
#                 "preview": doc_preview + "..."
#             })
        
#         return {
#             "success": True,
#             "count": len(available),
#             "best_practices": available
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e)
#         }


# @app.get("/debug/search-node-signature")
# def debug_search_node_signature():
#     """
#     Debug endpoint to check search_node_engine function signature.
#     """
#     try:
#         from backend.node_generator.search_node_engine import search_node_engine
#         import inspect
        
#         sig = inspect.signature(search_node_engine)
        
#         params_info = []
#         for name, param in sig.parameters.items():
#             param_type = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
#             default = param.default if param.default != inspect.Parameter.empty else "REQUIRED"
#             params_info.append({
#                 "name": name,
#                 "type": str(param_type),
#                 "default": str(default)
#             })
        
#         return {
#             "success": True,
#             "function": "search_node_engine",
#             "parameters": params_info,
#             "total_params": len(params_info)
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "message": "Could not inspect search_node_engine function"
#         }

# backend/main.py - Fixed and Production Ready




# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Dict, List, Optional
# import requests
# import traceback
# import json
# import re
# from backend.llm_config import get_llm
# from backend.mytools.categorize_prompt import create_categorize_prompt_tool
# from backend.mytools.find_best_practice import create_get_best_practices_tool
# from backend.mytypes.technique_normalizer import normalize_techniques
# from backend.llm import process_user_prompt
# from langchain_core.prompts import ChatPromptTemplate
# # New imports for best practice parsing and workflow generation
# from backend.mytools.parse_best_practices import parse_best_practices, NodeInfo
# from backend.mytools.node_registry import search_registry,NODE_REGISTRY
# from backend.mytools.generate_from_parsed_bp import (
#     generate_workflow_from_parsed_bp,
#     workflow_to_n8n_format,
#     select_nodes_for_intent,
#     align_nodes_after_parsing,
#     llm_select_and_adapt_nodes_for_intent,
#     generate_workflow_structure
# )

# app = FastAPI(title="n8n Workflow Generator API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# class AnalyzeRequest(BaseModel):
#     prompt: str


# class GenerateWorkflowRequest(BaseModel):
#     prompt: str
#     include_n8n_json: bool = False
#     include_parsed_details: bool = False


# def safe_get_node_engine_results(prompt: str, best_practices: str) -> List[str]:
#     """
#     Safely call search_node_engine if available, otherwise return empty list.
#     """
#     try:
#         from backend.node_generator.search_node_engine import search_node_engine
#         import inspect
        
#         # Get function signature
#         sig = inspect.signature(search_node_engine)
#         params = list(sig.parameters.keys())
        
#         # Build kwargs based on available parameters
#         kwargs = {}
        
#         # Map our parameters to the function's expected parameters
#         param_mapping = {
#             'user_prompt': prompt,
#             'prompt': prompt,
#             'final_intent': prompt,
#             'intent': prompt,
#             'best_practices': best_practices,
#             'best_practice_text': best_practices,
#             'best_practices_text': best_practices,
#             'bp_text': best_practices
#         }
        
#         for param_name in params:
#             if param_name in param_mapping:
#                 kwargs[param_name] = param_mapping[param_name]
        
#         result = search_node_engine(**kwargs)
        
#         # Extract possible_nodes from result
#         if isinstance(result, dict) and 'possible_nodes' in result:
#             nodes = result['possible_nodes']
#             if isinstance(nodes, list):
#                 return [str(n.value) if hasattr(n, 'value') else str(n) for n in nodes]
        
#         return []
        
#     except Exception as e:
#         print(f"Warning: search_node_engine not available or failed: {e}")
#         return []


# @app.post("/analyze")
# def analyze(req: AnalyzeRequest):
#     """
#     Enhanced analyze endpoint with full best practice parsing.
    
#     Returns:
#     - Categorization (techniques, confidence)
#     - Best practices text
#     - Parsed node information from best practices
#     - Workflow patterns
#     - Critical instructions
#     - Node engine results (if available)
#     """
#     try:
#         llm = get_llm()
#         categorize_tool = create_categorize_prompt_tool(llm)
#         categorize_result = categorize_tool({"prompt": req.prompt})

#         if not isinstance(categorize_result, dict):
#             return {"success": False, "message": "Invalid categorization response", "data": None}

#         categorization = categorize_result.get("data", {}).get("categorization", {})
#         raw_techniques = categorization.get("techniques", [])
#         confidence = categorization.get("confidence")

#         normalized_techniques = normalize_techniques(raw_techniques)

#         # Get best practices
#         best_practices = ""
#         best_practice_tool_data = create_get_best_practices_tool()
#         best_practice_tool = best_practice_tool_data.get("tool")

#         if best_practice_tool and normalized_techniques:
#             bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
#             data = bp_result.get("data")
#             if isinstance(data, dict):
#                 best_practices = data.get("message", "")
#             elif isinstance(data, str):
#                 best_practices = data
        
#         # Parse best practices to extract structured node information
#         parsed_bp = None
#         parsed_nodes = []
#         workflow_patterns = []
#         critical_instructions = []
        
#         if best_practices:
#             try:
#                 bp_parser = parse_best_practices(best_practices)
                
#                 # Select relevant nodes based on intent, using parsed nodes as reference
#                 selected_nodes = select_nodes_for_intent(
#                     user_intent=req.prompt,
#                     available_nodes=bp_parser.nodes,
#                     patterns=bp_parser.patterns,
#                     critical_instructions=bp_parser.critical_instructions
#                 )
                
#                 # Align/order selected nodes based on workflow phases
#                 aligned_nodes = align_nodes_after_parsing(req.prompt, selected_nodes)
                
#                 # Prepare parsed_nodes (full raw list from parsing)
#                 parsed_nodes = [
#                     {
#                         "name": node.name,
#                         "node_id": node.node_id,
#                         "category": node.category,
#                         "purpose": node.purpose,
#                         "pitfalls": node.pitfalls,
#                         "use_cases": node.use_cases,
#                         "alternatives": node.alternatives
#                     }
#                     for node in bp_parser.nodes
#                 ]
                
#                 # Prepare workflow patterns
#                 workflow_patterns = [
#                     {
#                         "description": pattern.description,
#                         "nodes_sequence": pattern.nodes_sequence
#                     }
#                     for pattern in bp_parser.patterns
#                 ]
                
#                 critical_instructions = bp_parser.critical_instructions
                
#                 # For parsedBestPractices.nodes, use only the aligned nodes that form the workflow
#                 parsed_bp = bp_parser.to_dict()
#                 parsed_bp["nodes"] = [
#                     {
#                         "name": node.name,
#                         "node_id": node.node_id,
#                         "purpose": node.purpose,
#                         "category": node.category,
#                         "pitfalls": node.pitfalls,
#                         "use_cases": node.use_cases,
#                         "alternatives": node.alternatives,
#                         "is_recommended": node.is_recommended
#                     }
#                     for node in aligned_nodes  # Aligned nodes represent the workflow-specific nodes
#                 ]
                
#             except Exception as e:
#                 print(f"Error parsing best practices: {e}")
#                 traceback.print_exc()
        
#         # Get node engine results
#         node_engine_results = safe_get_node_engine_results(req.prompt, best_practices)
        
#         return {
#             "success": True,
#             "message": "Prompt analyzed successfully",
#             "data": {
#                 "categorization": {
#                     "techniques": [t.value for t in normalized_techniques],
#                     "confidence": confidence
#                 },
#                 "parsedNodes": parsed_nodes,
#                 "workflowPatterns": workflow_patterns,
#                 "criticalInstructions": critical_instructions,
#                 "nodeEngineResults": node_engine_results,
#                 "parsedBestPractices": parsed_bp
#             }
#         }
        
#     except Exception as e:
#         print(f"Error in /analyze: {e}")
#         traceback.print_exc()
#         return {
#             "success": False,
#             "message": f"Failed to analyze prompt: {str(e)}",
#             "data": None
#         }


# @app.post("/workflow/generate")
# def generate_workflow(req: GenerateWorkflowRequest):
#     """
#     Generate complete n8n workflow based on user prompt.
    
#     Process:
#     1. Use LLM to extract all relevant techniques from prompt (generalized)
#     2. Categorize prompt to get base techniques
#     3. Merge techniques
#     4. Get best practices for all techniques
#     5. Parse best practices
#     6. Select and align relevant nodes (workflow-specific)
#     7. Generate workflow structure
#     """
    
#     try:
#         llm = get_llm()
        
#         # === NEW: LLM extracts all relevant techniques from prompt (generalized for any prompt) ===
#         technique_prompt = ChatPromptTemplate.from_messages([
#             ("system", """You are an expert in n8n workflows. From the user prompt, extract ALL relevant workflow techniques.
# Possible techniques include: scraping_and_research, content_generation, youtube_integration, chatbot, anthropic_integration, openai_integration, data_transformation, notification, scheduling, database_storage, ai_agent, and any others that fit.
# Output ONLY JSON: {"techniques": ["technique1", "technique2", ...]}"""),
#             ("user", "Prompt: {prompt}")
#         ])
        
#         chain = technique_prompt | llm
#         response = chain.invoke({"prompt": req.prompt})
#         content = response.content if hasattr(response, 'content') else str(response)
        
#         try:
#             match = re.search(r'\{[\s\S]*\}', content)
#             if match:
#                 extracted = json.loads(match.group())
#                 extra_techniques = set(extracted.get("techniques", []))
#             else:
#                 extra_techniques = set()
#         except:
#             extra_techniques = set()
        
#         # Step 1: Original categorization
#         categorize_tool = create_categorize_prompt_tool(llm)
#         categorize_result = categorize_tool({"prompt": req.prompt})

#         if not isinstance(categorize_result, dict):
#             return {"success": False, "error": "Invalid categorization"}

#         categorization = categorize_result.get("data", {}).get("categorization", {})
#         raw_techniques = categorization.get("techniques", [])
#         normalized_techniques = normalize_techniques(raw_techniques)
        
#         # Merge extracted + categorized techniques
#         all_technique_names = {t.value for t in normalized_techniques} | extra_techniques
#         final_techniques = [WorkflowTechnique(value=name) for name in all_technique_names]
        
#         # Step 2: Get best practices using all techniques
#         best_practices = ""
#         best_practice_tool_data = create_get_best_practices_tool()
#         best_practice_tool = best_practice_tool_data.get("tool")

#         if best_practice_tool and final_techniques:
#             bp_result = best_practice_tool.invoke({"techniques": final_techniques})
#             data = bp_result.get("data")
#             if isinstance(data, dict):
#                 best_practices = data.get("message", "")
#             elif isinstance(data, str):
#                 best_practices = data
        
#         if not best_practices.strip():
#             return {"success": False, "error": "No best practices found"}
        
#         # Step 3-5: Generate workflow
#         generated_workflow = generate_workflow_from_parsed_bp(
#             user_intent=req.prompt,
#             best_practices_text=best_practices,
#             techniques=[t.value for t in final_techniques]
#         )
        
#         response_data = {
#             "success": True,
#             "workflow": {
#                 "description": generated_workflow.description,
#                 "nodes": [
#                     {
#                         "id": node.id,
#                         "name": node.name,
#                         "type": node.type,
#                         "position": node.position,
#                         "parameters": node.parameters,
#                         "notes": node.notes
#                     }
#                     for node in generated_workflow.nodes
#                 ],
#                 "connections": [
#                     {
#                         "source": conn.source,
#                         "target": conn.target,
#                         "sourceOutput": conn.source_output,
#                         "targetInput": conn.target_input
#                     }
#                     for conn in generated_workflow.connections
#                 ],
#                 "metadata": generated_workflow.metadata
#             },
#             "techniques": [t.value for t in final_techniques]  # Updated to final
#         }
        
#         # Include n8n JSON
#         if req.include_n8n_json:
#             response_data["n8nWorkflow"] = workflow_to_n8n_format(generated_workflow)
        
#         # Include parsed details with adapted nodes
#         # Include parsed details if requested - use workflow-selected nodes directly
#         if req.include_parsed_details:
#             # We no longer filter against parsed_bp — use the nodes from the workflow
#             selected_node_ids = set(generated_workflow.metadata.get("source_nodes", []))

#             # Build nodes from the workflow's selected nodes (already adapted)
#             workflow_nodes = []
#             node_map = {n.id: n for n in generated_workflow.nodes}  # from actual workflow

#             for node_id in selected_node_ids:
#                 # Find in actual workflow nodes for full details
#                 workflow_node = next((n for n in generated_workflow.nodes if n.type == node_id), None)
#                 if workflow_node:
#                     workflow_nodes.append({
#                         "name": workflow_node.name,
#                         "node_id": workflow_node.type,
#                         "purpose": workflow_node.notes or "Workflow step",
#                         "category": "action" if "action" in workflow_node.type else "trigger" if "trigger" in workflow_node.type else "ai" if "langchain" in workflow_node.type else "transform",
#                         "pitfalls": [],
#                         "use_cases": [],
#                         "alternatives": [],
#                         "is_recommended": True
#                     })
#                 else:
#                     # Fallback: basic entry
#                     registry_node = next((n for n in NODE_REGISTRY if n.node_id == node_id), None)
#                     if registry_node:
#                         workflow_nodes.append({
#                             "name": registry_node.name,
#                             "node_id": registry_node.node_id,
#                             "purpose": registry_node.purpose,
#                             "category": registry_node.category,
#                             "pitfalls": registry_node.pitfalls,
#                             "use_cases": [],
#                             "alternatives": registry_node.alternatives,
#                             "is_recommended": True
#                         })

#             response_data["parsedBestPractices"] = {
#                 "nodes": workflow_nodes,
#                 "patterns": [],
#                 "critical_instructions": [],
#                 "general_guidelines": ["Custom workflow generated using node registry for accuracy"]
#             }
#             return response_data
        
#     except Exception as e:
#         print(f"Error in /workflow/generate: {e}")
#         traceback.print_exc()
#         return {
#             "success": False,
#             "error": f"Failed to generate workflow: {str(e)}",
#             "trace": traceback.format_exc()
#         }

# @app.post("/workflow/parse-best-practices")
# def parse_best_practices_endpoint(req: AnalyzeRequest):
#     """
#     Debug endpoint to see parsed best practices for any prompt.
#     """
    
#     try:
#         llm = get_llm()
#         categorize_tool = create_categorize_prompt_tool(llm)
#         categorize_result = categorize_tool({"prompt": req.prompt})

#         if not isinstance(categorize_result, dict):
#             return {"success": False, "error": "Invalid categorization"}

#         categorization = categorize_result.get("data", {}).get("categorization", {})
#         raw_techniques = categorization.get("techniques", [])
#         normalized_techniques = normalize_techniques(raw_techniques)
        
#         # Get best practices
#         best_practices = ""
#         best_practice_tool_data = create_get_best_practices_tool()
#         best_practice_tool = best_practice_tool_data.get("tool")

#         if best_practice_tool and normalized_techniques:
#             bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
#             data = bp_result.get("data")
#             if isinstance(data, dict):
#                 best_practices = data.get("message", "")
#             elif isinstance(data, str):
#                 best_practices = data
        
#         if not best_practices:
#             return {"success": False, "error": "No best practices found"}
        
#         bp_parser = parse_best_practices(best_practices)
        
#         return {
#             "success": True,
#             "data": {
#                 "summary": bp_parser.format_summary(),
#                 "detailed": bp_parser.to_dict(),
#                 "techniques": [t.value for t in normalized_techniques]
#             }
#         }
        
#     except Exception as e:
#         print(f"Error in /workflow/parse-best-practices: {e}")
#         traceback.print_exc()
#         return {"success": False, "error": str(e)}


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ChatSession:
#     def __init__(self):
#         self.history = []


# SESSIONS: Dict[str, ChatSession] = {}


# @app.post("/chat")
# def chat(req: ChatRequest):
#     """
#     Enhanced chat endpoint with full workflow generation.
#     """
    
#     try:
#         if req.message == "__FINALIZE__":
#             req.message = "done"

#         if req.session_id not in SESSIONS:
#             SESSIONS[req.session_id] = ChatSession()

#         session = SESSIONS[req.session_id]
#         result = process_user_prompt(req.message, session.history)

#         if result.get("finalized"):
#             final_intent = result["clean_prompt"]
            
#             # Generate complete workflow using parsed best practices
#             workflow_result = generate_workflow(
#                 GenerateWorkflowRequest(
#                     prompt=final_intent,
#                     include_n8n_json=True,
#                     include_parsed_details=True
#                 )
#             )
            
#             # Get basic analysis (with proper error handling)
#             analysis = None
#             try:
#                 # Call analyze directly instead of making HTTP request to avoid circular dependency
#                 analysis = analyze(AnalyzeRequest(prompt=final_intent))
#             except Exception as e:
#                 print(f"Error getting analysis: {e}")
#                 analysis = {"success": False, "error": str(e)}
            
#             # Clean up session
#             if req.session_id in SESSIONS:
#                 del SESSIONS[req.session_id]
            
#             return {
#                 "finalized": True,
#                 "final_intent": final_intent,
#                 "analysis": analysis,
#                 "workflow": workflow_result.get("workflow") if workflow_result.get("success") else None,
#                 "n8nWorkflow": workflow_result.get("n8nWorkflow") if workflow_result.get("success") else None,
#                 "parsedBestPractices": workflow_result.get("parsedBestPractices") if workflow_result.get("success") else None,
#                 "error": workflow_result.get("error") if not workflow_result.get("success") else None
#             }

#         if result.get("stop"):
#             return {"finalized": False, "response": result["reply"]}

#         return {"finalized": False, "response": result["clean_prompt"]}
        
#     except Exception as e:
#         print(f"Error in /chat: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "service": "n8n-workflow-generator",
#         "version": "2.0.0",
#         "features": [
#             "best-practice-parsing",
#             "node-extraction",
#             "workflow-generation",
#             "n8n-json-export",
#             "chat-interface"
#         ]
#     }


# @app.get("/debug/best-practices")
# def debug_best_practices():
#     """
#     Debug endpoint to view all available best practices.
#     """
#     try:
#         from backend.mytools.best_practices.index import documentation
        
#         available = []
#         for technique, doc_class in documentation.items():
#             doc_preview = doc_class.get_documentation()[:200] if hasattr(doc_class, 'get_documentation') else "N/A"
#             available.append({
#                 "technique": technique.value if hasattr(technique, 'value') else str(technique),
#                 "version": doc_class.version if hasattr(doc_class, 'version') else "N/A",
#                 "preview": doc_preview + "..."
#             })
        
#         return {
#             "success": True,
#             "count": len(available),
#             "best_practices": available
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e)
#         }


# @app.get("/debug/search-node-signature")
# def debug_search_node_signature():
#     """
#     Debug endpoint to check search_node_engine function signature.
#     """
#     try:
#         from backend.node_generator.search_node_engine import search_node_engine
#         import inspect
        
#         sig = inspect.signature(search_node_engine)
        
#         params_info = []
#         for name, param in sig.parameters.items():
#             param_type = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
#             default = param.default if param.default != inspect.Parameter.empty else "REQUIRED"
#             params_info.append({
#                 "name": name,
#                 "type": str(param_type),
#                 "default": str(default)
#             })
        
#         return {
#             "success": True,
#             "function": "search_node_engine",
#             "parameters": params_info,
#             "total_params": len(params_info)
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "message": "Could not inspect search_node_engine function"
#         }

# backend/main.py - Fixed and Production Ready

# backend/main.py - Complete Integration with All Components

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import traceback
import json
import re
from backend.llm_config import get_llm
from backend.mytools.categorize_prompt_tool import create_categorize_prompt_tool
from backend.mytools.find_best_practice_tool import create_get_best_practices_tool
from backend.mytypes.technique_normalizer import normalize_techniques
from backend.mytypes.categorization import WorkflowTechnique
from backend.llm import process_user_prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
# Import all components
from backend.mytools.parse_best_practices import parse_best_practices, NodeInfo
from backend.mytools.node_registry import NODE_REGISTRY, search_registry
from backend.mytools.registry_node_generator import (
    generate_workflow_nodes_from_registry,
    format_workflow_nodes_for_api,
    analyze_workflow_requirements
)
from backend.mytools.generate_from_parsed_bp import (
    workflow_to_n8n_format,
    generate_workflow_structure,
    llm_select_and_adapt_nodes_for_intent,
    align_nodes_after_parsing,
    create_fallback_workflow,
    generate_workflow_from_parsed_bp
)
from backend.mytools.search_node_wrapper import safe_search_node_engine

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

class GenerateWorkflowRequest(BaseModel):
    prompt: str
    include_n8n_json: bool = True
    include_parsed_details: bool = True

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """
    Comprehensive analysis of user prompt to extract techniques,
    """
    try:
        llm = get_llm()
        
        # === STEP 1: Categorize Prompt ===
        categorize_tool = create_categorize_prompt_tool(llm)
        categorize_result = categorize_tool({"prompt": req.prompt})

        if not isinstance(categorize_result, dict):
            return {"success": False, "message": "Invalid categorization response", "data": None}

        categorization = categorize_result.get("data", {}).get("categorization", {})
        raw_techniques = categorization.get("techniques", [])
        confidence = categorization.get("confidence")
        normalized_techniques = normalize_techniques(raw_techniques)

        # === STEP 2: Get Best Practices ===
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
        
        # === STEP 3: Parse Best Practices (if available) ===
        parsed_bp_nodes = []
        workflow_patterns = []
        critical_instructions = []
        
        if best_practices:
            try:
                bp_parser = parse_best_practices(best_practices)
                parsed_bp_nodes = bp_parser.nodes
                
                workflow_patterns = [
                    {
                        "description": pattern.description,
                        "nodes_sequence": pattern.nodes_sequence
                    }
                    for pattern in bp_parser.patterns
                ]
                critical_instructions = bp_parser.critical_instructions
            except Exception as e:
                print(f"Warning: Best practices parsing failed: {e}")
        
        # === STEP 4: Generate Workflow Nodes from Registry ===
        registry_nodes = []
        try:
            registry_workflow_nodes = generate_workflow_nodes_from_registry(req.prompt)
            registry_nodes = format_workflow_nodes_for_api(registry_workflow_nodes)
        except Exception as e:
            print(f"Warning: Registry generation failed: {e}")
        
        # === STEP 5: Merge Nodes (Registry + Best Practices) ===
        # Convert parsed_bp_nodes to dict format
        bp_nodes_dict = [
            {
                "name": node.name,
                "node_id": node.node_id,
                "category": node.category,
                "purpose": node.purpose,
                "pitfalls": node.pitfalls,
                "use_cases": node.use_cases if hasattr(node, 'use_cases') else [],
                "alternatives": node.alternatives,
                "is_recommended": True,
                "input_connections": node.input_connections if hasattr(node, 'input_connections') else [],
                "output_connections": node.output_connections if hasattr(node, 'output_connections') else []
            }
            for node in parsed_bp_nodes
        ]
        
        # Merge: prioritize registry nodes, add unique BP nodes
        merged_nodes = registry_nodes.copy()
        registry_ids = {n["node_id"] for n in registry_nodes}
        
        for bp_node in bp_nodes_dict:
            if bp_node["node_id"] not in registry_ids:
                merged_nodes.append(bp_node)
        
        # === STEP 6: Use LLM to Select and Adapt Best Nodes ===
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
                        input_connections=n.get("input_connections", []),
                        output_connections=n.get("output_connections", [])
                    )
                    for n in merged_nodes
                ]
                
                adapted_nodes = llm_select_and_adapt_nodes_for_intent(
                    user_intent=req.prompt,
                    parsed_nodes=node_infos
                )
                
                # Use adapted nodes if LLM succeeded
                if adapted_nodes:
                    merged_nodes = adapted_nodes
                    
                    # REBUILD sequential connections after LLM adaptation
                    for i, node in enumerate(merged_nodes):
                        # Clear existing connections
                        node["input_connections"] = []
                        node["output_connections"] = []
                        
                        # Add input from previous node
                        if i > 0:
                            node["input_connections"].append(merged_nodes[i-1]["name"])
                        
                        # Add output to next node
                        if i < len(merged_nodes) - 1:
                            node["output_connections"].append(merged_nodes[i+1]["name"])
                    
            except Exception as e:
                print(f"LLM adaptation failed (using merged nodes): {e}")
        
        # === STEP 7: Get Legacy Node Engine Results (optional) ===
        node_engine_results = []
        try:
            from backend.node_generator.search_node_engine import search_node_engine
            engine_result = safe_search_node_engine(
                user_prompt=req.prompt,
                best_practices=best_practices,
                search_node_engine_func=search_node_engine
            )
            possible_nodes = engine_result.get("possible_nodes", [])
            node_engine_results = [str(n.value) if hasattr(n, 'value') else str(n) for n in possible_nodes]
        except Exception as e:
            print(f"Node engine not available: {e}")
        
        # === STEP 8: Build parsedBestPractices ===
        # Ensure all nodes have sequential connections
        for i, node in enumerate(merged_nodes):
            # Ensure connection fields exist
            if "input_connections" not in node:
                node["input_connections"] = []
            if "output_connections" not in node:
                node["output_connections"] = []
            
            # Build connections if empty
            if not node["input_connections"] and i > 0:
                node["input_connections"] = [merged_nodes[i-1]["name"]]
            
            if not node["output_connections"] and i < len(merged_nodes) - 1:
                node["output_connections"] = [merged_nodes[i+1]["name"]]
        
        parsed_bp = {
            "nodes": merged_nodes,
            # "patterns": workflow_patterns,
            # "critical_instructions": critical_instructions,
            # "general_guidelines": [
            #     "Nodes selected using registry-based analysis + best practices",
            #     "Workflow adapted specifically for your use case",
            #     f"Total {len(merged_nodes)} nodes identified as relevant"
            # ]
        }
        
        return {
            "success": True,
            "message": "Prompt analyzed successfully",
            "data": {
                "categorization": {
                    "techniques": [t.value for t in normalized_techniques],
                    "confidence": confidence
                },
                # "workflowPatterns": workflow_patterns,
                # "criticalInstructions": critical_instructions,
                # "nodeEngineResults": node_engine_results,
                "parsedBestPractices": parsed_bp
            }
        }
        
    except Exception as e:
        print(f"Error in /analyze: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to analyze prompt: {str(e)}",
            "data": None
        }


@app.post("/workflow/generate")
def generate_workflow(req: GenerateWorkflowRequest):
    """
    ENHANCED workflow generation using ALL components.
    
    Flow:
    1. Analyze intent with LLM to extract ALL relevant techniques
    2. Categorize to get base techniques
    3. Merge techniques
    4. Get best practices
    5. Parse best practices
    6. Generate registry-based nodes
    7. Merge nodes from both sources
    8. Use LLM to select best nodes for intent
    9. Order nodes using align_nodes_after_parsing
    10. Generate workflow structure
    11. Return n8n JSON
    """
    
    try:
        llm = get_llm()
        
        # === STEP 1: LLM extracts ALL relevant techniques ===     
        technique_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in n8n workflows. From the user prompt, extract ALL relevant workflow techniques.\n\n"
                       "Possible techniques include:\n"
                       "- scraping_and_research (web scraping, data extraction)\n"
                       "- content_generation (AI-generated content, writing)\n"
                       "- youtube_integration (YouTube API, video management)\n"
                       "- chatbot (conversational interfaces, Q&A bots)\n"
                       "- anthropic_integration (Claude AI)\n"
                       "- openai_integration (GPT, ChatGPT)\n"
                       "- gemini_integration (Google Gemini)\n"
                       "- data_transformation (data processing, ETL)\n"
                       "- notification (email, Slack, messaging)\n"
                       "- scheduling (cron, periodic tasks)\n"
                       "- database_storage (SQL, NoSQL databases)\n"
                       "- spreadsheet_integration (Google Sheets, Excel)\n"
                       "- ai_agent (autonomous agents, tool usage)\n"
                       "- api_integration (REST APIs, webhooks)\n"
                       "- business_intelligence (PowerBI, Tableau, analytics)\n"
                       "- document_processing (PDF, OCR, file handling)\n\n"
                       "Return your answer as valid JSON with only one key 'techniques' and a list of technique names as values.\n"
                       "Example format:\n"
                       "{{\n"
                       "  \"techniques\": [\"notification\", \"scheduling\"]\n"
                       "}}"),
            ("user", "Prompt: {prompt}\n\nExtract ALL relevant techniques as JSON:")
        ])
        
        chain = technique_prompt | llm
        response = chain.invoke({"prompt": req.prompt})
        content = response.content if hasattr(response, 'content') else str(response)
        
        extra_techniques = set()
        try:
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                extracted = json.loads(match.group())
                extra_techniques = set(extracted.get("techniques", []))
        except Exception as e:
            print(f"LLM technique extraction failed: {e}")
        
        # === STEP 2: Original categorization ===
        categorize_tool = create_categorize_prompt_tool(llm)
        categorize_result = categorize_tool({"prompt": req.prompt})

        if not isinstance(categorize_result, dict):
            return {"success": False, "error": "Invalid categorization"}

        categorization = categorize_result.get("data", {}).get("categorization", {})
        raw_techniques = categorization.get("techniques", [])
        normalized_techniques = normalize_techniques(raw_techniques)
        
        # === STEP 3: Merge ALL techniques ===
        all_technique_names = {t.value for t in normalized_techniques} | extra_techniques
        final_techniques = [WorkflowTechnique(value=name) for name in all_technique_names]
        
        print(f"Final techniques: {[t.value for t in final_techniques]}")
        
        # === STEP 4: Get best practices using ALL techniques ===
        best_practices = ""
        best_practice_tool_data = create_get_best_practices_tool()
        best_practice_tool = best_practice_tool_data.get("tool")

        if best_practice_tool and final_techniques:
            bp_result = best_practice_tool.invoke({"techniques": final_techniques})
            data = bp_result.get("data")
            if isinstance(data, dict):
                best_practices = data.get("message", "")
            elif isinstance(data, str):
                best_practices = data
        
        # === STEP 5: Parse best practices ===
        bp_parser = None
        parsed_bp_nodes = []
        critical_instructions = []
        
        if best_practices:
            try:
                bp_parser = parse_best_practices(best_practices)
                parsed_bp_nodes = bp_parser.nodes
                critical_instructions = bp_parser.critical_instructions
                print(f"Parsed {len(parsed_bp_nodes)} nodes from best practices")
            except Exception as e:
                print(f"Best practices parsing failed: {e}")
        
        # === STEP 6: Generate registry nodes ===
        registry_nodes_raw = []
        try:
            registry_nodes_raw = generate_workflow_nodes_from_registry(req.prompt)
            print(f"Registry generated {len(registry_nodes_raw)} nodes")
        except Exception as e:
            print(f"Registry generation failed: {e}")
        
        # === STEP 7: Merge nodes from BOTH sources ===
        all_available_nodes = []
        seen_ids = set()
        
        # Add registry nodes first (they're more specific to intent)
        for node in registry_nodes_raw:
            if node["node_id"] not in seen_ids:
                all_available_nodes.append(NodeInfo(
                    name=node["name"],
                    node_id=node["node_id"],
                    purpose=node["purpose"],
                    category=node["category"],
                    pitfalls=node.get("pitfalls", []),
                    use_cases=node.get("use_cases", []),
                    alternatives=node.get("alternatives", []),
                    input_connections=node.get("input_connections", []),
                    output_connections=node.get("output_connections", [])
                ))
                seen_ids.add(node["node_id"])
        
        # Add parsed best practice nodes (for additional options)
        for node in parsed_bp_nodes:
            if node.node_id not in seen_ids:
                all_available_nodes.append(node)
                seen_ids.add(node.node_id)
        
        # Add ALL registry nodes as fallback options
        for reg_node in NODE_REGISTRY:
            if reg_node.node_id not in seen_ids:
                all_available_nodes.append(NodeInfo(
                    name=reg_node.name,
                    node_id=reg_node.node_id,
                    purpose=reg_node.purpose,
                    category=reg_node.category,
                    pitfalls=reg_node.pitfalls,
                    use_cases=[],
                    alternatives=reg_node.alternatives,
                    input_connections=reg_node.input_connections,
                    output_connections=reg_node.output_connections
                ))
                seen_ids.add(reg_node.node_id)
        
        print(f"Total available nodes: {len(all_available_nodes)}")
        
        # === STEP 8: LLM selects BEST nodes for intent ===
        selected_nodes = []
        try:
            adapted = llm_select_and_adapt_nodes_for_intent(
                user_intent=req.prompt,
                parsed_nodes=all_available_nodes
            )
            
            # Convert to NodeInfo
            selected_nodes = [
                NodeInfo(
                    name=n["name"],
                    node_id=n["node_id"],
                    purpose=n["purpose"],
                    category=n["category"],
                    pitfalls=n.get("pitfalls", []),
                    use_cases=n.get("use_cases", []),
                    alternatives=n.get("alternatives", []),
                    input_connections=n.get("input_connections", []),
                    output_connections=n.get("output_connections", [])
                )
                for n in adapted
            ]
            print(f"LLM selected {len(selected_nodes)} nodes")
        except Exception as e:
            print(f"LLM selection failed, using heuristic: {e}")
            # Fallback: use registry nodes
            selected_nodes = all_available_nodes[:8]
        
        # === STEP 9: Order nodes properly ===
        ordered_nodes = align_nodes_after_parsing(req.prompt, selected_nodes)
        print(f"Ordered {len(ordered_nodes)} nodes for workflow")
        # Find transform node (usually Set) and action nodes
        transform_node = None
        action_nodes = []

        for node in ordered_nodes:
            if node.category == "transform":
                transform_node = node
            elif node.category in ("action", "ai", "communication"):
                action_nodes.append(node)

        # Build connections
        input_connections = []
        output_connections = []

        for i, node in enumerate(ordered_nodes):
            inputs = []
            outputs = []

            # Trigger → Transform
            if node == transform_node and i > 0:
                inputs.append(ordered_nodes[i-1].name)

            # Transform → All actions (parallel)
            if node == transform_node and action_nodes:
                outputs = [n.name for n in action_nodes]

            # Actions have input from transform
            if node in action_nodes and transform_node:
                inputs.append(transform_node.name)

            # Fallback sequential if no transform detected
            if not inputs and i > 0:
                inputs.append(ordered_nodes[i-1].name)
            if not outputs and i < len(ordered_nodes) - 1:
                outputs.append(ordered_nodes[i+1].name)

            input_connections.append(inputs)
            output_connections.append(outputs)
        
        # === STEP 10: Generate workflow structure with connections ===
        patterns = bp_parser.patterns if bp_parser else []
        guidelines = bp_parser.general_guidelines if bp_parser else []
        
        generated_workflow = generate_workflow_structure(
            user_intent=req.prompt,
            selected_nodes=ordered_nodes,
            patterns=patterns,
            guidelines=guidelines
        )

        # === STEP 11: Build response ===
        response_data = {
            "success": True,
            "workflow": {
                "description": generated_workflow.description,
                "nodes": [],  # Will be filled below
                "connections": [
                    {
                        "source": conn.source,
                        "target": conn.target,
                        "sourceOutput": conn.source_output,
                        "targetInput": conn.target_input
                    }
                    for conn in generated_workflow.connections
                ],
                "metadata": generated_workflow.metadata
            },
            "techniques": [t.value for t in final_techniques]
        }

        # === ENHANCED: Add per-node input/output connections ===
        # Build maps for inputs and outputs with actual node names
        node_inputs = {node.id: [] for node in generated_workflow.nodes}
        node_outputs = {node.id: [] for node in generated_workflow.nodes}
        
        # Create lookup: node ID -> node name
        id_to_name = {node.id: node.name for node in generated_workflow.nodes}

        for conn in generated_workflow.connections:
            source = conn.source
            target = conn.target
            source_output = conn.source_output or "main"
            target_input = conn.target_input or "main"

            # Add to source node's outputs (with target node NAME)
            if source in node_outputs:
                node_outputs[source].append({
                    "target_node": id_to_name.get(target, target),  # Use name instead of ID
                    "output_name": source_output
                })

            # Add to target node's inputs (with source node NAME)
            if target in node_inputs:
                node_inputs[target].append({
                    "source_node": id_to_name.get(source, source),  # Use name instead of ID
                    "input_name": target_input
                })

        # Attach to each node
        enhanced_nodes = []
        for node in generated_workflow.nodes:
            node_dict = {
                "id": node.id,
                "name": node.name,
                "type": node.type,
                "position": node.position,
                "parameters": node.parameters,
                "notes": node.notes,
                "inputs": node_inputs.get(node.id, []),
                "outputs": node_outputs.get(node.id, [])
            }
            enhanced_nodes.append(node_dict)

        response_data["workflow"]["nodes"] = enhanced_nodes
        
        if req.include_n8n_json:
            response_data["n8nWorkflow"] = workflow_to_n8n_format(generated_workflow)
        
        if req.include_parsed_details:
            # Build connection mapping for ordered nodes
            ordered_node_inputs = []
            ordered_node_outputs = []
            
            for i, node in enumerate(ordered_nodes):
                # Input: previous node
                inputs = []
                if i > 0:
                    inputs.append(ordered_nodes[i-1].name)
                ordered_node_inputs.append(inputs)
                
                # Output: next node
                outputs = []
                if i < len(ordered_nodes) - 1:
                    outputs.append(ordered_nodes[i+1].name)
                ordered_node_outputs.append(outputs)
            
            response_data["parsedBestPractices"] = {
                "nodes": [
                    {
                        "name": node.name,
                        "node_id": node.node_id,
                        "purpose": node.purpose,
                        "category": node.category,
                        "pitfalls": node.pitfalls,
                        "use_cases": node.use_cases if hasattr(node, 'use_cases') else [],
                        "alternatives": node.alternatives,
                        "is_recommended": True,
                        "input_connections": ordered_node_inputs[i],    
                        "output_connections": ordered_node_outputs[i]   
                    }
                    for i, node in enumerate(ordered_nodes)
                ],
                "patterns": [
                    {
                        "description": p.description,
                        "nodes_sequence": p.nodes_sequence
                    }
                    for p in patterns
                ],
                "critical_instructions": critical_instructions if bp_parser else [],
                "general_guidelines": guidelines
            }
        
        return response_data
        
    except Exception as e:
        print(f"Error in /workflow/generate: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Failed to generate workflow: {str(e)}",
            "trace": traceback.format_exc()
        }


@app.post("/workflow/parse-best-practices")
def parse_best_practices_endpoint(req: AnalyzeRequest):
    """Debug endpoint to see parsed best practices for any prompt."""
    try:
        llm = get_llm()
        categorize_tool = create_categorize_prompt_tool(llm)
        categorize_result = categorize_tool({"prompt": req.prompt})

        if not isinstance(categorize_result, dict):
            return {"success": False, "error": "Invalid categorization"}

        categorization = categorize_result.get("data", {}).get("categorization", {})
        raw_techniques = categorization.get("techniques", [])
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
        
        if not best_practices:
            return {"success": False, "error": "No best practices found"}
        
        bp_parser = parse_best_practices(best_practices)
        
        return {
            "success": True,
            "data": {
                "summary": bp_parser.format_summary(),
                "detailed": bp_parser.to_dict(),
                "techniques": [t.value for t in normalized_techniques]
            }
        }
        
    except Exception as e:
        print(f"Error in /workflow/parse-best-practices: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatSession:
    def __init__(self):
        self.history = []

SESSIONS: Dict[str, ChatSession] = {}

@app.post("/chat")
def chat(req: ChatRequest):
    """Enhanced chat endpoint with full workflow generation."""
    try:
        if req.message == "__FINALIZE__":
            req.message = "done"

        if req.session_id not in SESSIONS:
            SESSIONS[req.session_id] = ChatSession()

        session = SESSIONS[req.session_id]
        result = process_user_prompt(req.message, session.history)

        if result.get("finalized"):
            final_intent = result["clean_prompt"]
            
            # Generate complete workflow
            workflow_result = generate_workflow(
                GenerateWorkflowRequest(
                    prompt=final_intent,
                    include_n8n_json=True,
                    include_parsed_details=True
                )
            )
            
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
            
            return {
                "finalized": True,
                "final_intent": final_intent,
                "analysis": analysis,
                "workflow": workflow_result.get("workflow") if workflow_result.get("success") else None,
                "n8nWorkflow": workflow_result.get("n8nWorkflow") if workflow_result.get("success") else None,
                "parsedBestPractices": workflow_result.get("parsedBestPractices") if workflow_result.get("success") else None,
                "error": workflow_result.get("error") if not workflow_result.get("success") else None
            }

        if result.get("stop"):
            return {"finalized": False, "response": result["reply"]}

        return {"finalized": False, "response": result["clean_prompt"]}
        
    except Exception as e:
        print(f"Error in /chat: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


