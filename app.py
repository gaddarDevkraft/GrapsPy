import streamlit as st
from langgraph_app import create_langgraph_app

st.title("LangGraph + Streamlit Chatbot")

# Initialize the LangGraph app only once
if "app" not in st.session_state:
    st.session_state.app = create_langgraph_app()

# Chat history display
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
user_input = st.text_input("Ask me something")

if st.button("Submit") and user_input:
    result = st.session_state.app.invoke({"input": user_input})
    output = result.get("final") or result.get("response")

    st.session_state.messages.append(("You", user_input))
    st.session_state.messages.append(("Bot", output))

# Show chat history
for sender, msg in st.session_state.messages:
    st.markdown(f"**{sender}:** {msg}")
