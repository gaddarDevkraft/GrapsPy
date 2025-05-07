from typing import Union
#from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException
#from openai import OpenAI
import os
# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import shutil


load_dotenv()

app = FastAPI()

#client = OpenAI(api_key=os.environ.get("DEVKRAFT_OPENAI_API_KEY"))

openai.api_key = os.environ.get("OPENAI_API_KEY")

CHROMA_PATH = "chroma"
DATA_PATH = "app/data"


def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    try:
        loader = DirectoryLoader(DATA_PATH, glob="*.md")
        documents = loader.load()
        return documents
    except FileNotFoundError as exception:
        print(f"Error loading documents: {exception}")
        return exception


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")




# @app.get("/chat")
# def get_chatbot_response(q: str):
#     try:
#         completion = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "user", "content": q
#                 }
#             ]
#         )
#         return {"response": completion.choices[0].message.content}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host = "0.0.0.0", port = 8000)

if __name__ == "__main__":
    main()