# import streamlit as st
# import requests

# BACKEND_URL = "http://localhost:8000/analyze"

# st.set_page_config(
#     page_title="Custom Logic AI Assistant",
#     layout="centered"
# )

# st.title("Custom Logic AI Assistant")
# st.write("Analyze prompts using rule-based + LLM categorization logic.")

# prompt = st.text_area(
#     "Enter your prompt",
#     height=120,
#     placeholder="Example: Create an automation that runs every Monday..."
# )

# analyze_btn = st.button("Analyze Prompt")

# if analyze_btn:
#     if not prompt.strip():
#         st.warning("Please enter a prompt.")
#     else:
#         with st.spinner("Analyzing prompt..."):
#             try:
#                 response = requests.post(
#                     BACKEND_URL,
#                     json={"prompt": prompt},
#                     timeout=30
#                 )

#                 if response.status_code == 200:
#                     result = response.json()

#                     st.subheader("Analysis Result")

#                     # Show success message
#                     st.success(result.get("message", "Prompt analyzed."))

#                     data = result.get("data", {})
#                     categorization = data.get("categorization", {})

#                     techniques = categorization.get("techniques", [])
#                     confidence = categorization.get("confidence")

#                     if techniques:
#                         st.markdown("**Techniques Identified:**")
#                         for t in techniques:
#                             st.markdown(f"- {t}")
#                     else:
#                         st.info("No techniques identified.")

#                     if confidence is not None:
#                         st.markdown(f"**Confidence Score:** `{confidence}`")
#                     else:
#                         st.info("Confidence score not available.")

#                     # Optional: show raw JSON for debugging
#                     with st.expander("Raw API Response"):
#                         st.json(result)

#                 else:
#                     st.error(f"Backend error: {response.status_code}")
#                     st.text(response.text)

#             except requests.exceptions.RequestException as e:
#                 st.error("Unable to connect to backend.")
#                 st.text(str(e))

# frontend/app.py : govind work/company_Task/n8n_chatbot_logical/frontend/app.py 
import streamlit as st
import requests
import json

BACKEND_URL = "http://localhost:8000/analyze"

st.set_page_config(
    page_title="Custom Logic AI Assistant",
    layout="centered"
)

st.title("Custom Logic AI Assistant")
st.caption("Analyze automation prompts using custom logic and LLM intelligence")

prompt = st.text_area(
    "Enter your prompt",
    height=140,
    placeholder="Example: Create an automation that runs every Monday at 8 PM and sends an email alert"
)

analyze_btn = st.button("Analyze Prompt", type="primary")

if analyze_btn:
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Analyzing prompt..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={"prompt": prompt},
                    timeout=30
                )

                if response.status_code != 200:
                    st.error("Backend error occurred.")
                    st.stop()

                try:
                    result = response.json()
                except json.JSONDecodeError:
                    st.error("Invalid response from backend.")
                    st.stop()

                if not result.get("success"):
                    st.error("Prompt analysis failed.")
                    st.stop()

                data = result.get("data", {})
                categorization = data.get("categorization", {})

                techniques = categorization.get("techniques", [])
                confidence = categorization.get("confidence")
                technique_categories = data.get("techniqueCategories", "")

                st.success(result.get("message", "Analysis completed successfully."))

                st.subheader("Identified Techniques")
                if techniques:
                    for t in techniques:
                        st.markdown(f"- **{t}**")
                else:
                    st.info("No techniques identified.")

                if confidence is not None:
                    st.subheader("Confidence Score")
                    st.progress(float(confidence))
                    st.code(confidence)

                st.subheader("Best Practices")
                if isinstance(technique_categories, str) and technique_categories.strip():
                    st.markdown(technique_categories)
                else:
                    st.info("No best practices available.")

            except requests.exceptions.RequestException:
                st.error("Unable to connect to backend service.")

















# import streamlit as st
# import uuid
# import requests

# # Backend endpoints
# CHAT_URL = "http://localhost:8000/chat"
# ANALYZE_URL = "http://localhost:8000/analyze"

# # ----------------------------------------------------------
# # PAGE SETUP
# # ----------------------------------------------------------
# st.set_page_config(page_title="Workflow Builder Assistant", layout="centered")
# st.title("🤖 Workflow Builder Assistant")

# # Choice between chat mode and analyze mode
# mode = st.radio("Choose mode:", ["Workflow Builder (Chat)"])


# # ==========================================================
# # MODE 1 — MULTI-TURN WORKFLOW BUILDER (CHAT)
# # ==========================================================
# if mode == "Workflow Builder (Chat)":

#     # New session ID if first time
#     if "session_id" not in st.session_state:
#         st.session_state.session_id = str(uuid.uuid4())

#     # Conversation history
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     user_message = st.text_input("You:", placeholder="Describe the workflow you want to build...")

#     send = st.button("Send")

#     if send and user_message.strip():

#         # Add user message to UI
#         st.session_state.messages.append(("user", user_message))

#         # Send message to backend
#         res = requests.post(
#             CHAT_URL,
#             json={
#                 "session_id": st.session_state.session_id,
#                 "message": user_message
#             }
#         ).json()

#         # --------------------------------------------------
#         # FINALIZATION CASE
#         # --------------------------------------------------
#         if res.get("finalized"):

#             final_intent = res["final_intent"]
#             analysis = res["analysis"]

#             # Display results
#             st.success("🎉 Final Workflow Intent")
#             st.write(final_intent)

#             st.subheader("🔍 Analysis of Final Intent")
#             st.json(analysis)

#             # Reset session
#             st.session_state.session_id = str(uuid.uuid4())
#             st.session_state.messages = []

#         else:
#             # Continue the refinement chat
#             reply = res["response"]
#             st.session_state.messages.append(("assistant", reply))

#     # --------------------------------------------------
#     # DISPLAY CHAT HISTORY
#     # --------------------------------------------------
#     st.write("---")
#     st.subheader("Conversation")

#     for role, msg in st.session_state.messages:
#         if role == "user":
#             st.markdown(f"**👤 You:** {msg}")
#         else:
#             st.markdown(f"**🤖 Assistant:** {msg}")


# # # ==========================================================
# # # MODE 2 — SIMPLE PROMPT ANALYZER
# # # ==========================================================
# # elif mode == "Analyze Prompt":

# #     prompt = st.text_area("Enter text to analyze")

# #     if st.button("Analyze"):
# #         if prompt.strip():
# #             response = requests.post(ANALYZE_URL, json={"prompt": prompt}).json()
# #             st.json(response)



































# # frontend/app.py

# import streamlit as st
# import uuid
# import requests

# CHAT_URL = "http://localhost:8000/chat"
# ANALYZE_URL = "http://localhost:8000/analyze"

# st.set_page_config(page_title="Workflow Builder Assistant", layout="centered")
# st.title("🤖 Workflow Builder Assistant")

# mode = st.radio("Choose mode:", ["Workflow Builder (Chat)"])


# # ==========================================================
# # WORKFLOW BUILDER (CHAT MODE)
# # ==========================================================
# if mode == "Workflow Builder (Chat)":

#     if "session_id" not in st.session_state:
#         st.session_state.session_id = str(uuid.uuid4())

#     if "messages" not in st.session_state:
#         st.session_state.messages = []


#     # UI Layout for input + DONE button
#     col1, col2 = st.columns([4, 1])

#     with col1:
#         user_message = st.text_input("You:", placeholder="Describe the workflow...")

#     with col2:
#         done_pressed = st.button("DONE")


#     send_pressed = st.button("Send")


#     # ------------------------------------------------------
#     # SEND MESSAGE
#     # ------------------------------------------------------
#     if send_pressed and user_message.strip():

#         st.session_state.messages.append(("user", user_message))

#         res = requests.post(
#             CHAT_URL,
#             json={
#                 "session_id": st.session_state.session_id,
#                 "message": user_message
#             }
#         ).json()

#         if res.get("finalized"):
#             final_intent = res["final_intent"]
#             analysis = res["analysis"]

#             st.success("🎉 Final Workflow Intent")
#             st.write(final_intent)

#             st.subheader("🔍 Analysis of Final Intent")
#             st.json(analysis)

#             st.session_state.session_id = str(uuid.uuid4())
#             st.session_state.messages = []

#         else:
#             reply = res["response"]
#             st.session_state.messages.append(("assistant", reply))


#     # ------------------------------------------------------
#     # DONE BUTTON FINALIZATION
#     # ------------------------------------------------------
#     if done_pressed:

#         res = requests.post(
#             CHAT_URL,
#             json={
#                 "session_id": st.session_state.session_id,
#                 "message": "__FINALIZE__"
#             }
#         ).json()

#         if res.get("finalized"):

#             final_intent = res["final_intent"]
#             analysis = res["analysis"]

#             st.success("🎉 Final Workflow Intent")
#             st.write(final_intent)

#             st.subheader("🔍 Analysis of Final Intent")
#             st.json(analysis)

#             st.session_state.session_id = str(uuid.uuid4())
#             st.session_state.messages = []

#         else:
#             try:
#                 response = requests.post(CHAT_URL, json={
#                     "session_id": st.session_state.session_id,
#                     "message": "__FINALIZE__"
#                 })
#                 if response.status_code != 200:
#                     st.error(f"Backend error: {response.status_code}")
#                     st.text(response.text)

#             except requests.exceptions.RequestException as e:
#                 st.error("Unable to connect to backend.")
#                 st.text(str(e))



























# import streamlit as st
# import requests

# BACKEND_URL = "http://localhost:8000/analyze"

# st.set_page_config(
#     page_title="Custom Logic AI Assistant",
#     layout="centered"
# )

# st.title("Custom Logic AI Assistant")
# st.write("Analyze prompts using rule-based + LLM categorization logic.")

# prompt = st.text_area(
#     "Enter your prompt",
#     height=120,
#     placeholder="Example: Create an automation that runs every Monday..."
# )

# analyze_btn = st.button("Analyze Prompt")

# if analyze_btn:
#     if not prompt.strip():
#         st.warning("Please enter a prompt.")
#     else:
#         with st.spinner("Analyzing prompt..."):
#             try:
#                 response = requests.post(
#                     BACKEND_URL,
#                     json={"prompt": prompt},
#                     timeout=30
#                 )

#                 if response.status_code == 200:
#                     result = response.json()

#                     st.subheader("Analysis Result")

#                     # Show success message
#                     st.success(result.get("message", "Prompt analyzed."))

#                     data = result.get("data", {})
#                     categorization = data.get("categorization", {})

#                     techniques = categorization.get("techniques", [])
#                     confidence = categorization.get("confidence")

#                     if techniques:
#                         st.markdown("**Techniques Identified:**")
#                         for t in techniques:
#                             st.markdown(f"- {t}")
#                     else:
#                         st.info("No techniques identified.")

#                     if confidence is not None:
#                         st.markdown(f"**Confidence Score:** `{confidence}`")
#                     else:
#                         st.info("Confidence score not available.")

#                     # Optional: show raw JSON for debugging
#                     with st.expander("Raw API Response"):
#                         st.json(result)

#                 else:
#                     st.error(f"Backend error: {response.status_code}")
#                     st.text(response.text)

#             except requests.exceptions.RequestException as e:
#                 st.error("Unable to connect to backend.")
#                 st.text(str(e))


























# #frontend(app.py)
# import streamlit as st
# import requests
 
# BACKEND_URL = "http://localhost:8000/analyze"
 
# st.set_page_config(
#     page_title="Custom Logic AI Assistant",
#     layout="centered"
# )
 
# st.title("Custom Logic AI Assistant")
# st.write("Analyze prompts using rule-based + LLM categorization logic.")
 
# prompt = st.text_area(
#     "Enter your prompt",
#     height=120,
#     placeholder="Example: Create an automation that runs every Monday..."
# )
 
# analyze_btn = st.button("Analyze Prompt")
 
# if analyze_btn:
#     if not prompt.strip():
#         st.warning("Please enter a prompt.")
#     else:
#         with st.spinner("Analyzing prompt..."):
#             try:
#                 response = requests.post(
#                     BACKEND_URL,
#                     json={"prompt": prompt},
#                     timeout=30
#                 )
 
#                 if response.status_code == 200:
#                     result = response.json()
 
#                     st.subheader("Analysis Result")
 
#                     # Show success message
#                     st.success(result.get("message", "Prompt analyzed."))
 
#                     data = result.get("data", {})
#                     categorization = data.get("categorization", {})
 
#                     techniques = categorization.get("techniques", [])
#                     confidence = categorization.get("confidence")
 
#                     if techniques:
#                         st.markdown("**Techniques Identified:**")
#                         for t in techniques:
#                             st.markdown(f"- {t}")
#                     else:
#                         st.info("No techniques identified.")
 
#                     if confidence is not None:
#                         st.markdown(f"**Confidence Score:** `{confidence}`")
#                     else:
#                         st.info("Confidence score not available.")
 
#                     # Optional: show raw JSON for debugging
#                     with st.expander("Raw API Response"):
#                         st.json(result)
 
#                 else:
#                     st.error(f"Backend error: {response.status_code}")
#                     st.text(response.text)
 
#             except requests.exceptions.RequestException as e:
#                 st.error("Unable to connect to backend.")
#                 st.text(str(e))
 










# # frontend(app.py)
# import streamlit as st
# import requests
 
# BACKEND_URL = "http://localhost:8000/analyze"
 
# st.set_page_config(
#     page_title="Custom Logic AI Assistant",
#     layout="centered"
# )
 
# st.title("Custom Logic AI Assistant")
# st.write("Analyze prompts using rule-based + LLM categorization logic.")
 
# prompt = st.text_area(
#     "Enter your prompt",
#     height=120,
#     placeholder="Example: Create an automation that runs every Monday..."
# )
 
# analyze_btn = st.button("Analyze Prompt")
 
# if analyze_btn:
#     if not prompt.strip():
#         st.warning("Please enter a prompt.")
#     else:
#         with st.spinner("Analyzing prompt..."):
#             try:
#                 response = requests.post(
#                     BACKEND_URL,
#                     json={"prompt": prompt},
#                     timeout=30
#                 )
 
#                 if response.status_code == 200:
#                     result = response.json()
 
#                     st.subheader("Analysis Result")
 
#                     # Show success message
#                     st.success(result.get("message", "Prompt analyzed."))
 
#                     data = result.get("data", {})
#                     categorization = data.get("categorization", {})
 
#                     techniques = categorization.get("techniques", [])
#                     confidence = categorization.get("confidence")
 
#                     if techniques:
#                         st.markdown("**Techniques Identified:**")
#                         for t in techniques:
#                             st.markdown(f"- {t}")
#                     else:
#                         st.info("No techniques identified.")
 
#                     if confidence is not None:
#                         st.markdown(f"**Confidence Score:** `{confidence}`")
#                     else:
#                         st.info("Confidence score not available.")
 
#                     # Optional: show raw JSON for debugging
#                     with st.expander("Raw API Response"):
#                         st.json(result)
 
#                 else:
#                     st.error(f"Backend error: {response.status_code}")
#                     st.text(response.text)
 
#             except requests.exceptions.RequestException as e:
#                 st.error("Unable to connect to backend.")
#                 st.text(str(e))
 
 
# import streamlit as st
# import uuid
# import requests
 
# # Backend endpoints
# CHAT_URL = "http://localhost:8000/chat"
# ANALYZE_URL = "http://localhost:8000/analyze"
 
# # ----------------------------------------------------------
# # PAGE SETUP
# # ----------------------------------------------------------
# st.set_page_config(page_title="Workflow Builder Assistant", layout="centered")
# st.title("🤖 Workflow Builder Assistant")
 
# # Choice between chat mode and analyze mode
# mode = st.radio("Choose mode:", ["Workflow Builder (Chat)"])
 
 
# # ==========================================================
# # MODE 1 — MULTI-TURN WORKFLOW BUILDER (CHAT)
# # ==========================================================
# if mode == "Workflow Builder (Chat)":
 
#     # New session ID if first time
#     if "session_id" not in st.session_state:
#         st.session_state.session_id = str(uuid.uuid4())
 
#     # Conversation history
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
 
#     user_message = st.text_input("You:", placeholder="Describe the workflow you want to build...")
 
#     send = st.button("Send")
 
#     if send and user_message.strip():
 
#         # Add user message to UI
#         st.session_state.messages.append(("user", user_message))
 
#         # Send message to backend
#         res = requests.post(
#             CHAT_URL,
#             json={
#                 "session_id": st.session_state.session_id,
#                 "message": user_message
#             }
#         ).json()
 
#         # --------------------------------------------------
#         # FINALIZATION CASE
#         # --------------------------------------------------
#         if res.get("finalized"):
 
#             final_intent = res["final_intent"]
#             analysis = res["analysis"]
 
#             # Display results
#             st.success("🎉 Final Workflow Intent")
#             st.write(final_intent)
 
#             st.subheader("🔍 Analysis of Final Intent")
#             st.json(analysis)
 
#             # Reset session
#             st.session_state.session_id = str(uuid.uuid4())
#             st.session_state.messages = []
 
#         else:
#             # Continue the refinement chat
#             reply = res["response"]
#             st.session_state.messages.append(("assistant", reply))
 
#     # --------------------------------------------------
#     # DISPLAY CHAT HISTORY
#     # --------------------------------------------------
#     st.write("---")
#     st.subheader("Conversation")
 
#     for role, msg in st.session_state.messages:
#         if role == "user":
#             st.markdown(f"**👤 You:** {msg}")
#         else:
#             st.markdown(f"**🤖 Assistant:** {msg}")
 


# # ==========================================================
# # MODE 2 — SIMPLE PROMPT ANALYZER
# # ==========================================================
# elif mode == "Analyze Prompt":
 
#     prompt = st.text_area("Enter text to analyze")
 
#     if st.button("Analyze"):
#         if prompt.strip():
#             response = requests.post(ANALYZE_URL, json={"prompt": prompt}).json()
#             st.json(response)
 
 









# # frontend/app.py
 
# import streamlit as st
# import uuid
# import requests
 
# CHAT_URL = "http://localhost:8000/chat"
# ANALYZE_URL = "http://localhost:8000/analyze"
 
# st.set_page_config(page_title="Workflow Builder Assistant", layout="centered")
# st.title(" Workflow Builder Assistant")
 
# mode = st.radio("Choose mode:", ["Workflow Builder (Chat)"])
 

# # WORKFLOW BUILDER (CHAT MODE)

# if mode == "Workflow Builder (Chat)":
 
#     if "session_id" not in st.session_state:
#         st.session_state.session_id = str(uuid.uuid4())
 
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
 
 
#     # UI Layout for input + DONE button
#     col1, col2 = st.columns([4, 1])
 
#     with col1:
#         user_message = st.text_input("You:", placeholder="Describe the workflow...")
 
#     with col2:
#         done_pressed = st.button("DONE")
 
 
#     send_pressed = st.button("Send")
 
 
  
#     # SEND MESSAGE
  
#     if send_pressed and user_message.strip():
 
#         st.session_state.messages.append(("user", user_message))
 
#         res = requests.post(
#             CHAT_URL,
#             json={
#                 "session_id": st.session_state.session_id,
#                 "message": user_message
#             }
#         ).json()
 
#         if res.get("finalized"):
#             final_intent = res["final_intent"]
#             analysis = res["analysis"]
 
#             st.success("🎉 Final Workflow Intent")
#             st.write(final_intent)
 
#             st.subheader("🔍 Analysis of Final Intent")
#             st.json(analysis)
 
#             st.session_state.session_id = str(uuid.uuid4())
#             st.session_state.messages = []
 
#         else:
#             reply = res["response"]
#             st.session_state.messages.append(("assistant", reply))
 
 

#     # DONE BUTTON FINALIZATION

#     if done_pressed:
 
#         res = requests.post(
#             CHAT_URL,
#             json={
#                 "session_id": st.session_state.session_id,
#                 "message": "__FINALIZE__"
#             }
#         ).json()
 
#         if res.get("finalized"):
 
#             final_intent = res["final_intent"]
#             analysis = res["analysis"]
 
#             st.success(" Final Workflow Intent")
#             st.write(final_intent)
 
#             st.subheader("🔍 Analysis of Final Intent")
#             st.json(analysis)
 
#             st.session_state.session_id = str(uuid.uuid4())
#             st.session_state.messages = []
 
#         else:
#             st.error(" Backend did not finalize. Try again.")
 
 

#     # DISPLAY CONVERSATION
  
#     st.write("---")
#     st.subheader("Conversation")
 
#     for role, msg in st.session_state.messages:
#         if role == "user":
#             st.markdown(f"** You:** {msg}")
#         else:
#             st.markdown(f"** Assistant:** {msg}")
 
 

