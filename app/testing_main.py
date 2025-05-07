import os
import shutil
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader

load_dotenv()


class VectorDBHandler:
    def __init__(self, persist_directory: str = "chroma"):
        self.persist_directory = persist_directory
        self.embedding = OpenAIEmbeddings()
        self.db = None

    def create_or_load_db(self):
        """Create or load existing Chroma DB."""
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding
        )
        print("Vector DB loaded or created.")
        return self.db

    def insert_documents(self, docs: list[Document]):
        """Insert new documents into DB."""
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)  # Optional: clear old DB
        self.db = Chroma.from_documents(
            docs,
            embedding=self.embedding,
            persist_directory=self.persist_directory
        )
        self.db.persist()
        print(f"{len(docs)} documents inserted and persisted.")

    def fetch_similar(self, query: str, k: int = 3):
        """Retrieve top-k similar documents for a query."""
        if not self.db:
            self.create_or_load_db()
        results = self.db.similarity_search(query, k=k)
        return results

    def delete_db(self):
        """Delete the entire vector DB from disk."""
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            print("Vector DB deleted.")


DATA_PATH = "/"


def load_and_split():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    return splitter.split_documents(docs)


if __name__ == "__main__":
    vector_db = VectorDBHandler()
    chunks = load_and_split()

    # CREATE / INSERT
    vector_db.insert_documents(chunks)

    # READ / FETCH
    results = vector_db.fetch_similar("down the rabbit hole", k=2)
    for res in results:
        print(res.page_content[:100])  # Print first 100 chars



    # DELETE (optional)
    # vector_db.delete_db()
