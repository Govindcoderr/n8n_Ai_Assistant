# File: backend/mytools/search_node_wrapper.py

"""
Wrapper for search_node_engine to handle different function signatures gracefully.
This ensures compatibility regardless of the actual implementation.
"""

import inspect
from typing import Dict, Any, List


def safe_search_node_engine(user_prompt: str, best_practices: str, search_node_engine_func) -> Dict[str, Any]:
    """
    Safely call search_node_engine with the correct parameters.
    
    Args:
        user_prompt: The user's workflow intent
        best_practices: Best practices text
        search_node_engine_func: The actual search_node_engine function
        
    Returns:
        Dict with 'possible_nodes' key and list of nodes
    """
    
    try:
        # Get function signature
        sig = inspect.signature(search_node_engine_func)
        params = list(sig.parameters.keys())
        
        # Build kwargs based on available parameters
        kwargs = {}
        
        # Common parameter name variations
        if 'user_prompt' in params:
            kwargs['user_prompt'] = user_prompt
        elif 'prompt' in params:
            kwargs['prompt'] = user_prompt
        elif 'final_intent' in params:
            kwargs['final_intent'] = user_prompt
        elif 'intent' in params:
            kwargs['intent'] = user_prompt
        
        if 'best_practices' in params:
            kwargs['best_practices'] = best_practices
        elif 'best_practice_text' in params:
            kwargs['best_practice_text'] = best_practices
        elif 'best_practices_text' in params:
            kwargs['best_practices_text'] = best_practices
        elif 'bp_text' in params:
            kwargs['bp_text'] = best_practices
        
        # Call the function
        result = search_node_engine_func(**kwargs)
        
        # Ensure result has the expected structure
        if isinstance(result, dict) and 'possible_nodes' in result:
            return result
        elif isinstance(result, list):
            return {"possible_nodes": result}
        else:
            return {"possible_nodes": []}
            
    except Exception as e:
        print(f"Error in safe_search_node_engine: {e}")
        return {"possible_nodes": []}


def get_search_node_engine_signature():
    """
    Debug function to inspect the search_node_engine signature.
    """
    try:
        from backend.node_generator.search_node_engine import search_node_engine
        sig = inspect.signature(search_node_engine)
        
        params_info = []
        for name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
            default = param.default if param.default != inspect.Parameter.empty else "REQUIRED"
            params_info.append({
                "name": name,
                "type": str(param_type),
                "default": str(default)
            })
        
        return {
            "function": "search_node_engine",
            "parameters": params_info,
            "total_params": len(params_info)
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Could not inspect search_node_engine function"
        }