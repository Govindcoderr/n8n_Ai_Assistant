# # node_search_engine.py
# from typing import List, Dict, Any, Optional, Union
# from backend.n8n_worflow.sublime_search import sublimeSearch
# # from backend.n8n_worflow.node_connection_types import NodeConnectionTypes


# NODE_SEARCH_KEYS = [
#     {"key": "displayName", "weight": 1.5},
#     {"key": "name", "weight": 1.3},
#     {"key": "codex.alias", "weight": 1.0},
#     {"key": "description", "weight": 0.7},
# ]

# SCORE_WEIGHTS = {
#     "CONNECTION_EXACT": 100,
#     "CONNECTION_IN_EXPRESSION": 50,
# }


# def get_latest_version(version: Union[int, List[int]]) -> int:
#     return max(version) if isinstance(version, list) else version


# def dedupe_nodes(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     cache: Dict[str, Dict[str, Any]] = {}

#     for node in nodes:
#         name = node["name"]
#         if name not in cache:
#             cache[name] = node
#             continue

#         if get_latest_version(node["version"]) > get_latest_version(cache[name]["version"]):
#             cache[name] = node

#     return list(cache.values())

# class NodeSearchEngine:

#     def __init__(self, node_types: List[Dict[str, Any]]):
#         self.node_types = dedupe_nodes(node_types)

#     def search_by_name(self, query: str, limit: int = 20):
#         results = sublimeSearch(query, self.node_types, NODE_SEARCH_KEYS)

#         return [
#             self._to_result(r["item"], r["score"])
#             for r in results[:limit]
#         ]

#     def search_by_connection_type(
#         self,
#         connection_type: str,
#         limit: int = 20,
#         name_filter: Optional[str] = None,
#     ):
#         matched = []

#         for node in self.node_types:
#             score = self._get_connection_score(node, connection_type)
#             if score > 0:
#                 matched.append((node, score))

#         if not name_filter:
#             return [
#                 self._to_result(node, score)
#                 for node, score in sorted(matched, key=lambda x: x[1], reverse=True)[:limit]
#             ]

#         filtered_nodes = [n for n, _ in matched]
#         name_results = sublimeSearch(name_filter, filtered_nodes, NODE_SEARCH_KEYS)

#         final = []
#         for r in name_results[:limit]:
#             base_score = dict(matched).get(r["item"], 0)
#             final.append(self._to_result(r["item"], base_score + r["score"]))

#         return final

#     def format_result(self, result: Dict[str, Any]) -> str:
#         return f"""
# <node>
#   <node_name>{result['name']}</node_name>
#   <node_version>{result['version']}</node_version>
#   <node_description>{result['description']}</node_description>
#   <node_inputs>{result['inputs']}</node_inputs>
#   <node_outputs>{result['outputs']}</node_outputs>
# </node>
# """.strip()

#     # def _get_connection_score(self, node: Dict[str, Any], connection_type: str) -> int:
#     #     outputs = node.get("outputs")

#     #     if isinstance(outputs, list) and connection_type in outputs:
#     #         return SCORE_WEIGHTS["CONNECTION_EXACT"]

#     #     if isinstance(outputs, str) and connection_type in outputs:
#     #         return SCORE_WEIGHTS["CONNECTION_IN_EXPRESSION"]

#     #     return 0
    
#     def _get_connection_score(self, node: Dict[str, Any], connection_type: str) -> int:
#       outputs = node.get("outputs") or []
#       inputs = node.get("inputs") or []

#      # Exact match in outputs (what this node produces)
#       if isinstance(outputs, list) and connection_type in outputs:
#         return SCORE_WEIGHTS["CONNECTION_EXACT"]

#       if isinstance(outputs, str) and connection_type in outputs:
#         return SCORE_WEIGHTS["CONNECTION_IN_EXPRESSION"]

#      #  Exact match in inputs (what this node accepts)
#       if isinstance(inputs, list) and connection_type in inputs:
#         return SCORE_WEIGHTS["CONNECTION_EXACT"]

#       if isinstance(inputs, str) and connection_type in inputs:
#         return SCORE_WEIGHTS["CONNECTION_IN_EXPRESSION"]

#       return 0


#     def _to_result(self, node: Dict[str, Any], score: float):
#         return {
#             "name": node["name"],
#             "displayName": node["displayName"],
#             "description": node.get("description") or "No description available",
#             "version": get_latest_version(node["version"]),
#             "inputs": node.get("inputs"),
#             "outputs": node.get("outputs"),
#             "score": score,
#         }





# # backend/mytools/engine/node_search_engine.py

# import json
# from typing import List, Dict, Any, Optional, Union
# from backend.n8n_worflow.sublime_search import sublimeSearch
# from backend.n8n_worflow.node_connection_types import NodeConnectionTypes


# NODE_SEARCH_KEYS = [
#     {"key": "displayName", "weight": 1.5},
#     {"key": "name", "weight": 1.3},
#     {"key": "codex.alias", "weight": 1.0},
#     {"key": "description", "weight": 0.7},
# ]

# SCORE_WEIGHTS = {
#     "CONNECTION_EXACT": 100,
#     "CONNECTION_IN_EXPRESSION": 50,
#     # "GENERIC_MAIN_FALLBACK": 10,   # ⭐ NEW
# }


# def get_latest_version(version: Union[int, List[int]]) -> int:
#     return max(version) if isinstance(version, list) else version


# def dedupe_nodes(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     cache: Dict[str, Dict[str, Any]] = {}

#     for node in nodes:
#         name = node["name"]
#         if name not in cache:
#             cache[name] = node
#             continue

#         if get_latest_version(node["version"]) > get_latest_version(cache[name]["version"]):
#             cache[name] = node

#     return list(cache.values()) 


# class NodeSearchEngine:
#     """
#     Pure business logic for searching nodes
#     Separated from tool infrastructure for better testability
#     """

#     def __init__(self, node_types):
#         self.nodeTypes = dedupe_nodes(node_types)

#     def searchByName(self, query: str, limit: int = 20):
#         """
#         Search nodes by name, display name, or description
#         Always return the latest version of a node
#         """

#         search_results = sublimeSearch(
#             query,
#             self.nodeTypes,
#             NODE_SEARCH_KEYS,
#         )

#         return [
#             {
#                 "name": item["name"],
#                 "displayName": item["displayName"],
#                 "description": item.get("description", "No description available"),
#                 "version": get_latest_version(item["version"]),
#                 "inputs": item.get("inputs"),
#                 "outputs": item.get("outputs"),
#                 "score": score,
#             }
#             for item, score in search_results[:limit]
#         ]

#     def searchByConnectionType(
#         self,
#         connectionType,
#         limit: int = 20,
#         nameFilter: str | None = None,
#     ):
#         """
#         Search for sub-nodes that output a specific connection type
#         Always return the latest version of a node
#         """

#         nodes_with_connection_type = []

#         for node_type in self.nodeTypes:
#             connection_score = self.getConnectionScore(node_type, connectionType)
#             if connection_score > 0:
#                 nodes_with_connection_type.append({
#                     "nodeType": node_type,
#                     "connectionScore": connection_score,
#                 })

#         # No name filter → sort by connection score
#         if not nameFilter:
#             nodes_with_connection_type.sort(
#                 key=lambda x: x["connectionScore"],
#                 reverse=True,
#             )

#             return [
#                 {
#                     "name": item["nodeType"]["name"],
#                     "displayName": item["nodeType"]["displayName"],
#                     "description": item["nodeType"].get(
#                         "description", "No description available"
#                     ),
#                     "version": get_latest_version(item["nodeType"]["version"]),
#                     "inputs": item["nodeType"].get("inputs"),
#                     "outputs": item["nodeType"].get("outputs"),
#                     "score": item["connectionScore"],
#                 }
#                 for item in nodes_with_connection_type[:limit]
#             ]

#         # Apply name filter using sublime search
#         node_types_only = [item["nodeType"] for item in nodes_with_connection_type]
#         name_filtered_results = sublimeSearch(
#             nameFilter,
#             node_types_only,
#             NODE_SEARCH_KEYS,
#         )

#         final_results = []

#         for item, name_score in name_filtered_results[:limit]:
#             connection_result = next(
#                 (
#                     r for r in nodes_with_connection_type
#                     if r["nodeType"]["name"] == item["name"]
#                 ),
#                 None,
#             )
#             connection_score = connection_result["connectionScore"] if connection_result else 0

#             final_results.append({
#                 "name": item["name"],
#                 "displayName": item["displayName"],
#                 "description": item.get("description", "No description available"),
#                 "version": get_latest_version(item["version"]),
#                 "inputs": item.get("inputs"),
#                 "outputs": item.get("outputs"),
#                 "score": connection_score + name_score,
#             })

#         return final_results

#     def formatResult(self, result):
#         """
#         Format search results for tool output
#         Returns XML-formatted string
#         """

#         inputs = (
#             json.dumps(result["inputs"])
#             if isinstance(result.get("inputs"), (dict, list))
#             else result.get("inputs")
#         )
#         outputs = (
#             json.dumps(result["outputs"])
#             if isinstance(result.get("outputs"), (dict, list))
#             else result.get("outputs")
#         )

#         return f"""
#         <node>
#             <node_name>{result["name"]}</node_name>
#             <node_version>{result["version"]}</node_version>
#             <node_description>{result["description"]}</node_description>
#             <node_inputs>{inputs}</node_inputs>
#             <node_outputs>{outputs}</node_outputs>
#         </node>
#         """

#     def getConnectionScore(self, nodeType, connectionType) -> int:
#         """
#         Check if a node has a specific connection type in outputs
#         """

#         outputs = nodeType.get("outputs")

#         if isinstance(outputs, list):
#             if connectionType in outputs:
#                 return SCORE_WEIGHTS["CONNECTION_EXACT"]

#         elif isinstance(outputs, str):
#             if connectionType in outputs:
#                 return SCORE_WEIGHTS["CONNECTION_IN_EXPRESSION"]

#         return 0

#     @staticmethod
#     def isAiConnectionType(connectionType: str) -> bool:
#         return connectionType.startswith("ai_")

#     @staticmethod
#     def getAiConnectionTypes():
#         return [
#             t for t in NodeConnectionTypes.values()
#             if NodeSearchEngine.isAiConnectionType(t)
#         ]



# class NodeSearchEngine:


#     def __init__(self, node_types: List[Dict[str, Any]]):
#         self.node_types = dedupe_nodes(node_types)

#     # -------------------------
#     # 1️⃣ Search by name
#     # -------------------------
#     def search_by_name(self, query: str, limit: int = 20):
#         if not query:
#             return []

#         results = sublimeSearch(query, self.node_types, NODE_SEARCH_KEYS)

#         return [
#             self._to_result(r["item"], r["score"])
#             for r in results[:limit]
#         ]

#     # -------------------------
#     # 2️⃣ Search by connection type (IMPORTANT)
#     # -------------------------
#     def search_by_connection_type(
#         self,
#         connection_type: str,
#         limit: int = 20,
#         name_filter: Optional[str] = None,
#     ):
#         matched: List[tuple] = []

#         for node in self.node_types:
#             score = self._get_connection_score(node, connection_type)
#             if score > 0:
#                 matched.append((node, score))

#         if not matched:
#             return []

#         # 🔹 अगर नाम filter नहीं दिया
#         if not name_filter:
#             return [
#                 self._to_result(node, score)
#                 for node, score in sorted(matched, key=lambda x: x[1], reverse=True)[:limit]
#             ]

#         # 🔹 नाम filter + connection type दोनों
#         filtered_nodes = [node for node, _ in matched]
#         name_results = sublimeSearch(name_filter, filtered_nodes, NODE_SEARCH_KEYS)

#         final_results = []
#         for r in name_results[:limit]:
#             base_score = dict(matched).get(r["item"], 0)
#             final_results.append(
#                 self._to_result(r["item"], base_score + r["score"])
#             )

#         return final_results

#     # -------------------------
#     # 3️⃣ Connection scoring logic (FIXED)
#     # -------------------------
#     def _get_connection_score(self, node: Dict[str, Any], connection_type: str) -> int:
#         outputs = node.get("outputs") or []
#         inputs = node.get("inputs") or []

#         # Normalize to list
#         if isinstance(outputs, str):
#             outputs = [outputs]
#         if isinstance(inputs, str):
#             inputs = [inputs]

#         # ✅ Exact output match
#         if connection_type in outputs:
#             return SCORE_WEIGHTS["CONNECTION_EXACT"]

#         # ✅ Exact input match
#         if connection_type in inputs:
#             return SCORE_WEIGHTS["CONNECTION_EXACT"]

#         # ⭐ SPECIAL CASE: "main" is very generic in n8n
#         if connection_type == "main" and (outputs or inputs):
#             return SCORE_WEIGHTS["GENERIC_MAIN_FALLBACK"]

#         return 0

#     # -------------------------
#     # 4️⃣ Result formatter
#     # -------------------------
#     def _to_result(self, node: Dict[str, Any], score: float):
#         return {
#             "name": node["name"],
#             "displayName": node["displayName"],
#             "description": node.get("description") or "No description available",
#             "version": get_latest_version(node["version"]),
#             "inputs": node.get("inputs"),
#             "outputs": node.get("outputs"),
#             "score": score,
#         }

#     def format_result(self, result: Dict[str, Any]) -> str:
#         return f"""
# <node>
#   <node_name>{result['name']}</node_name>
#   <node_version>{result['version']}</node_version>
#   <node_description>{result['description']}</node_description>
#   <node_inputs>{result['inputs']}</node_inputs>
#   <node_outputs>{result['outputs']}</node_outputs>
# </node>
# """.strip()





from typing import List, Dict, Any, Optional


class NodeSearchEngine:
    def __init__(self, nodes: List[Dict[str, Any]]):
        
        self.nodes = [n for n in nodes if n.get("type") == "node"]

    # 1 Search by connection type
    def search_by_connection_type(
        self,
        connection_type: str,
        limit: int = 10,
        name_filter: Optional[str] = None,
    ):
        results = []

        for node in self.nodes:
            props = node.get("properties", {})
            outputs = props.get("outputs", []) or []

            if connection_type == "main" and "main" in outputs:
                score = 50
            elif connection_type.startswith("ai_") and connection_type in outputs:
                score = 100
            else:
                continue

            if name_filter:
                text = (
                    props.get("displayName", "").lower()
                    + " "
                    + props.get("description", "").lower()
                    + " "
                    + props.get("name", "").lower()
                )
                if name_filter.lower() not in text:
                    continue

            results.append(self._to_result(node, score))

        return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]

    # -------------------------
    # 2️⃣ Search by name / intent
    # -------------------------
    def search_by_name(self, query: str, limit: int = 10):
        query = query.lower()
        results = []

        for node in self.nodes:
            props = node.get("properties", {})
            text = (
                props.get("displayName", "").lower()
                + " "
                + props.get("description", "").lower()
                + " "
                + props.get("name", "").lower()
            )

            if query in text:
                results.append(self._to_result(node, 80))

        return results[:limit]

    # -------------------------
    # 3️⃣ Normalize result
    # -------------------------
    def _to_result(self, node: Dict[str, Any], score: int):
        props = node.get("properties", {})

        return {
            "key": node.get("key"),
            "name": props.get("name"),
            "displayName": props.get("displayName"),
            "description": props.get("description"),
            "outputs": props.get("outputs"),
            "categories": props.get("codex", {}).get("categories", []),
            "score": score,
        }
