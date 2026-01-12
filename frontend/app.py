
import streamlit as st
import uuid
import requests

CHAT_URL = "http://localhost:8000/chat"
ANALYZE_URL = "http://localhost:8000/analyze"

st.set_page_config(page_title="Custom Logic Workflow Assistant", layout="centered")

st.title("Custom Logic Workflow Assistant")

mode = st.radio("Choose mode:", ["Workflow Builder (Chat)", "Analyze Prompt"])

if mode == "Workflow Builder (Chat)":

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    col1, col2 = st.columns([4, 1])

    with col1:
        user_message = st.text_input("You:", placeholder="Describe the workflow...")

    with col2:
        done_pressed = st.button("DONE")

    send_pressed = st.button("Send")

    if send_pressed and user_message.strip():
        st.session_state.messages.append(("user", user_message))
        res = requests.post(
            CHAT_URL,
            json={"session_id": st.session_state.session_id, "message": user_message}
        ).json()

        if res.get("finalized"):
            st.success("Final Workflow Intent")
            st.write(res.get("final_intent"))
            st.subheader("Analysis")
            st.json(res.get("analysis"))
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
        else:
            st.session_state.messages.append(("assistant", res.get("response", "")))

    if done_pressed:
        res = requests.post(
            CHAT_URL,
            json={"session_id": st.session_state.session_id, "message": "__FINALIZE__"}
        ).json()

        if res.get("finalized"):
            st.success("Final Workflow Intent")
            st.write(res.get("final_intent"))
            st.subheader("Analysis")
            st.json(res.get("analysis"))
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
        else:
            st.error("Backend did not finalize")

    st.write("Conversation")

    for role, msg in st.session_state.messages:
        if role == "user":
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**Assistant:** {msg}")

else:

    prompt = st.text_area(
        "Enter your prompt",
        height=120,
        placeholder="Example: Create an automation that runs every Monday...."
    )

    analyze_btn = st.button("Analyze Prompt")

    if analyze_btn:
        if not prompt.strip():
            st.warning("Please enter a prompt")
        else:
            with st.spinner("Analyzing prompt..."):
                try:
                    response = requests.post(
                        ANALYZE_URL,
                        json={"prompt": prompt},
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.success(result.get("message", "Prompt analyzed"))
                        data = result.get("data", {})
                        categorization = data.get("categorization", {})
                        techniques = categorization.get("techniques", [])
                        confidence = categorization.get("confidence")

                        if techniques:
                            st.markdown("Techniques Identified:")
                            for t in techniques:
                                st.markdown(f"- {t}")
                        else:
                            st.info("No techniques identified")

                        if confidence is not None:
                            st.markdown(f"Confidence Score: `{confidence}`")

                        with st.expander("Raw API Response"):
                            st.json(result)
                    else:
                        st.error(f"Backend error: {response.status_code}")
                        st.text(response.text)

                except requests.exceptions.RequestException as e:
                    st.error("Unable to connect to backend")
                    st.text(str(e))
