import os
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from app.services import rag_service
from app.model.query_responce import QueryResponse
from app.model.query_request import QueryRequest
from app.services.rag_service import embeddings

document_store = {}

app = FastAPI(title="RAG Document QA System")


@app.post("/upload", response_class=JSONResponse)
async def upload_document(file: UploadFile = File(...), document_name: Optional[str] = Form(None)):
    try:
        doc_id = str(uuid.uuid4())
        if document_name is None:
            document_name = file.filename

        file_path = f"uploaded_docs/{doc_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the document
        try:
            document_chunks = rag_service.process_file(file_path)

            # Store document metadata
            document_store[doc_id] = {
                "id": doc_id,
                "name": document_name,
                "filename": file.filename,
                "path": file_path,
                "chunk_count": len(document_chunks)
            }

            # Update vector store
            rag_service.update_vector_store(document_chunks)

            return {
                "status": "success",
                "message": f"Document '{document_name}' uploaded and processed successfully",
                "document_id": doc_id,
                "chunks_processed": len(document_chunks)
            }

        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Error processing document: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# @app.get("/documents", response_class=JSONResponse)
# async def list_documents():
#     return {"documents": list(document_store.values())}


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    if rag_service.vector_store is None:
        print("Vector store is not initialized yet")
        raise HTTPException(status_code=400, detail="No documents have been uploaded yet")

    try:
        result = rag_service.qa_chain({"query": request.query})

        source_docs = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                source_docs.append(doc.page_content[:200] + "...")  # First 200 chars of each source

        return {
            "answer": result["result"],
            "source_documents": source_docs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


# @app.delete("/documents/{doc_id}", response_class=JSONResponse)
# async def delete_document(doc_id: str):
#     if doc_id not in document_store:
#         raise HTTPException(status_code=404, detail="Document not found")
#
#     try:
#         file_path = document_store[doc_id]["path"]
#         if os.path.exists(file_path):
#             os.remove(file_path)
#
#         del document_store[doc_id]
#
#
#         return {"status": "success", "message": f"Document {doc_id} deleted successfully"}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup if vector DB exists."""
    if os.path.exists("vector_db/faiss_index"):

        vector_store = FAISS.load_local("vector_db/faiss_index", embeddings)

        # Initialize QA chain
        llm = rag_service.init_llm()
        rag_service.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3})
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
