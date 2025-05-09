import torch
import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredFileLoader
)
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from qdrant_client.http import models as qdrant_models
import threading
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create directories
os.makedirs("uploaded_docs", exist_ok=True)
os.makedirs("vector_db", exist_ok=True)

# OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Qdrant settings
qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
collection_name = os.getenv("QDRANT_COLLECTION", "rag_documents")

# Initialize global variables
vector_store = None
qa_chain = None

# Initialize Qdrant client
try:
    qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
    logger.info(f"Connected to Qdrant at {qdrant_host}:{qdrant_port}")
except Exception as e:
    logger.error(f"Failed to connect to Qdrant: {e}")
    raise

# Initialize embeddings
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)


def initialize_services():
    """Initialize the vector store and QA chain on application startup"""
    global vector_store, qa_chain

    try:
        # Check if collection exists, create it if it doesn't
        if not qdrant_client.collection_exists(collection_name):
            logger.info(f"Creating new collection: {collection_name}")
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=embeddings.embed_query("test").__len__(),
                    distance=qdrant_models.Distance.COSINE
                )
            )

        # Initialize vector store
        vector_store = Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=embeddings
        )

        # Initialize LLM
        llm = init_llm()

        # Create QA chain with custom prompt
        prompt_template = """
        You are a helpful assistant that answers questions based on the provided context.

        Context information:
        {context}

        Question: {query}

        Answer:
        """

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "query"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": PROMPT}
        )

        logger.info("Vector store and QA chain initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        logger.error(traceback.format_exc())
        raise


def init_llm():
    """Initialize the language model"""
    try:
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
        max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "512"))

        logger.info(f"Initializing ChatOpenAI with model: {model_name}")

        return ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        raise


def process_file(file_path):
    """Process a file and break it into chunks"""
    logger.info(f"Processing file: {file_path}")

    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        # Select appropriate loader based on file extension
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_extension == '.docx':
            loader = Docx2txtLoader(file_path)
        elif file_extension == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            # Fallback to generic loader for other file types
            loader = UnstructuredFileLoader(file_path)

        # Load the documents
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} document sections from {file_path}")

        # Extract document ID from filename
        doc_id = os.path.basename(file_path).split('_')[0]

        # Add metadata to documents
        for doc in documents:
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            doc.metadata['source'] = file_path
            doc.metadata['doc_id'] = doc_id

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")

        return chunks

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        logger.error(traceback.format_exc())
        raise


def update_vector_store(document_chunks):
    """Update the vector store with new document chunks"""
    global vector_store, qa_chain

    try:
        logger.info(f"Updating vector store with {len(document_chunks)} chunks")

        # Ensure collection exists
        if not qdrant_client.collection_exists(collection_name):
            logger.info(f"Creating new collection: {collection_name}")
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=embeddings.embed_query("test").__len__(),
                    distance=qdrant_models.Distance.COSINE
                )
            )

        # Add documents to vector store
        if vector_store is None:
            # Initialize vector store if it doesn't exist
            vector_store = Qdrant.from_documents(
                documents=document_chunks,
                embedding=embeddings,
                client=qdrant_client,
                collection_name=collection_name
            )
        else:
            # Add documents to existing vector store
            vector_store.add_documents(document_chunks)

        # Reinitialize QA chain with updated vector store
        llm = init_llm()

        # Create a simpler QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 5})
        )

        logger.info("Vector store and QA chain updated successfully")

    except Exception as e:
        logger.error(f"Error updating vector store: {e}")
        logger.error(traceback.format_exc())
        raise


def delete_document_from_vector_store(doc_id):
    """Delete a document from the vector store (not implemented yet)"""
    # This would require implementing a filtering mechanism with Qdrant
    # For now, this is a placeholder for future implementation
    logger.warning(f"Deletion from vector store not implemented yet. Document {doc_id} remains in the vector store.")
    return False