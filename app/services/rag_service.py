import torch
import os
from transformers import AutoTokenizer, AutoModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader
)

os.makedirs("uploaded_docs", exist_ok=True)
os.makedirs("vector_db", exist_ok=True)

# Initialize models and components
model_name = "sentence-transformers/all-MiniLM-L6-v2"  # For embeddings
llm_model_name = "google/flan-t5-small"  # For text generation

vector_store = None
qa_chain = None

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
)


# Function to initialize the LLM
def init_llm():
    from transformers import AutoModelForSeq2SeqLM, pipeline

    tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(llm_model_name)

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=512,
        device=0 if torch.cuda.is_available() else -1
    )

    llm = HuggingFacePipeline(pipeline=pipe)
    return llm


def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_extension == '.docx':
        loader = Docx2txtLoader(file_path)
    elif file_extension == '.txt':
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_documents(documents)
    return chunks


def update_vector_store(document_chunks):
    global vector_store, qa_chain

    if vector_store is None:
        vector_store = FAISS.from_documents(document_chunks, embeddings)
        vector_store.save_local("vector_db/faiss_index")
    else:
        vector_store.add_documents(document_chunks)
        vector_store.save_local("vector_db/faiss_index")

    # Initialize or update QA chain
    if qa_chain is None:
        llm = init_llm()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3})
        )
