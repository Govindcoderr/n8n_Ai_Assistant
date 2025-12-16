# import streamlit as st
# from backend.categorizer import PromptCategorizer
# from backend.best_practices import BestPracticesRetriever
# from backend.node_search import NodeSearcher
# from backend.node_ranking import NodeRanker
# from backend.utils import display_workflow_summary
# from backend.llm_interface import LLMInterface

# # Initialize modules
# categorizer = PromptCategorizer("data/example_prompts.json")
# best_practices_retriever = BestPracticesRetriever("data/workflow_best_practices.json")
# node_searcher = NodeSearcher("data/nodes_catalog.json")
# node_ranker = NodeRanker(node_searcher.get_all_nodes())

# # Streamlit UI
# st.title("Custom Logic AI Assistant")
# user_prompt = st.text_area("Describe your workflow requirement:")

# api_key = st.text_input("Enter OpenAI API Key:", type="password")

# if st.button("Generate Workflow Guidance"):
#     if not user_prompt or not api_key:
#         st.warning("Please provide both prompt and API key")
#     else:
#         llm = LLMInterface(api_key)
#         # Step 1: Categorize
#         techniques = categorizer.categorize(user_prompt)

#         # Step 2: Retrieve best practices
#         best_practices = best_practices_retriever.get_best_practices(techniques)

#         # Step 3: Search nodes
#         nodes = node_searcher.search_nodes(techniques)

#         # Step 4: Rank nodes
#         ranked_nodes = node_ranker.rank_nodes(techniques)

#         # Step 5: Summarize and send to LLM
#         summary = display_workflow_summary(techniques, best_practices, nodes, ranked_nodes)
#         llm_prompt = f"User wants to automate a workflow.\nDetails:\n{summary}\nProvide a step-by-step actionable guide."
#         llm_response = llm.ask(llm_prompt)

#         st.subheader("Workflow Guidance")
#         st.text_area("LLM Output", value=llm_response, height=400)
