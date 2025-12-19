import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/analyze"

st.set_page_config(
    page_title="Custom Logic AI Assistant",
    layout="centered"
)

st.title("Custom Logic AI Assistant")
st.write("Analyze prompts using rule-based + LLM categorization logic.")

prompt = st.text_area(
    "Enter your prompt",
    height=120,
    placeholder="Example: Create an automation that runs every Monday..."
)

analyze_btn = st.button("Analyze Prompt")

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

                if response.status_code == 200:
                    result = response.json()

                    st.subheader("Analysis Result")

                    # Show success message
                    st.success(result.get("message", "Prompt analyzed."))

                    data = result.get("data", {})
                    categorization = data.get("categorization", {})

                    techniques = categorization.get("techniques", [])
                    confidence = categorization.get("confidence")

                    if techniques:
                        st.markdown("**Techniques Identified:**")
                        for t in techniques:
                            st.markdown(f"- {t}")
                    else:
                        st.info("No techniques identified.")

                    if confidence is not None:
                        st.markdown(f"**Confidence Score:** `{confidence}`")
                    else:
                        st.info("Confidence score not available.")

                    # Optional: show raw JSON for debugging
                    with st.expander("Raw API Response"):
                        st.json(result)

                else:
                    st.error(f"Backend error: {response.status_code}")
                    st.text(response.text)

            except requests.exceptions.RequestException as e:
                st.error("Unable to connect to backend.")
                st.text(str(e))




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

#                     # ---- EXISTING LOGIC (UNCHANGED) ----
#                     st.success(result.get("message", "Prompt analyzed."))

#                     data = result.get("data", {})
#                     categorization = data.get("categorization", {})

#                     techniques = categorization.get("techniques", [])
#                     confidence = categorization.get("confidence")

#                     if techniques:
#                         st.markdown("### Techniques Identified")
#                         for t in techniques:
#                             st.markdown(f"- `{t}`")
#                     else:
#                         st.info("No techniques identified.")

#                     if confidence is not None:
#                         st.markdown(f"**Confidence Score:** `{confidence}`")
#                     else:
#                         st.info("Confidence score not available.")

#                     # ---- NEW STEP: BEST PRACTICES ----
#                     best_practices = data.get("bestPractices", {})

#                     if best_practices:
#                         st.markdown("---")
#                         st.subheader("Recommended Best Practices")

#                         preview = best_practices.get("preview")

#                         if preview:
#                             # Clean preview rendering
#                             cleaned_preview = (
#                                 preview
#                                 .replace("<best_practices>", "")
#                                 .replace("</best_practices>", "")
#                                 .strip()
#                             )

#                             st.markdown(cleaned_preview, unsafe_allow_html=False)

#                         else:
#                             st.info("No best practices available for the identified techniques.")

#                         # Expandable full response
#                         with st.expander("View full best practices response"):
#                             st.json(best_practices)

#                     # ---- DEBUG / RAW RESPONSE ----
#                     with st.expander("Raw API Response"):
#                         st.json(result)

#                 else:
#                     st.error(f"Backend error: {response.status_code}")
#                     st.text(response.text)

#             except requests.exceptions.RequestException as e:
#                 st.error("Unable to connect to backend.")
#                 st.text(str(e))
