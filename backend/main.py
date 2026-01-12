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

