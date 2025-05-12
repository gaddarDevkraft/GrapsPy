from fastapi import FastAPI, status
from langchain.memory import ConversationBufferMemory

# import streamlit as st
#
# st.title("Hello World")
#
# if st.checkbox("Show/Hide"):
#     st.text("Showing the widget")


# from langchain.llms import OpenAI
# from langchain.chains import ConversationChain
# from langchain.memory import ConversationBufferMemory
#
# # Initialize the LLM
# llm = OpenAI(temperature=0)  # Or ChatOpenAI for chat-based models
#
# # Add memory
# memory = ConversationBufferMemory()
#
# conversation = ConversationChain(
#     llm=llm,
#     memory=memory,
#     verbose=True
# )
#
# # Simulate a conversation
# print(conversation.predict(input="Hi, my name is Gaddar"))
# print(conversation.predict(input="What's my name?"))

from langchain.memory import ConversationBufferMemory, Conv

memory = ConversationBufferMemory()
memory.save_context({"input": "My name is Gaddar"}, {"output": "Nice to meet you!"})
print(memory.load_memory_variables({}))  # Shows stored history
print(memory)

# app = FastAPI()
#
#
# @app.get("/")
# def hello():
#     return {"data": {"status", "hello server"}}


# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host = "0.0.0.0", port = 8000)
