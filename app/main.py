import os
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.services import rag_service
from app.model.query_responce import QueryResponse
from app.model.query_request import QueryRequest
from app.model.document_reaponce import DocumentResponse

os.makedirs("uploaded_docs", exist_ok=True)

# Store document metadata
document_store = {}

app = FastAPI(title="RAG - GenAi Demo")

# Add CORS middleware - helpful if you plan to have a separate frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/upload", response_class=JSONResponse)
async def upload_document(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        document_name: Optional[str] = Form(None)
):

    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.txt', '.pdf', '.docx']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Please upload .txt, .pdf, or .docx files only."
            )

        doc_id = str(uuid.uuid4())
        if document_name is None:
            document_name = file.filename

        # Save the file
        file_path = f"uploaded_docs/{doc_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            if os.path.getsize(file_path) < 1_000_000:  # Less than 1MB
                document_chunks = rag_service.process_file(file_path)
                rag_service.update_vector_store(document_chunks)
                chunk_count = len(document_chunks)

                # Store document metadata
                document_store[doc_id] = {
                    "id": doc_id,
                    "name": document_name,
                    "filename": file.filename,
                    "path": file_path,
                    "chunk_count": chunk_count,
                    "status": "completed"
                }

                return {
                    "status": "success",
                    "message": f"Document '{document_name}' uploaded and processed successfully",
                    "document_id": doc_id,
                    "chunks_processed": chunk_count
                }
            else:
                document_store[doc_id] = {
                    "id": doc_id,
                    "name": document_name,
                    "filename": file.filename,
                    "path": file_path,
                    "status": "processing"
                }

                background_tasks.add_task(process_document_background, doc_id, file_path)

                return {
                    "status": "processing",
                    "message": f"Document '{document_name}' uploaded and is being processed",
                    "document_id": doc_id,
                }

        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Error processing document: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


def process_document_background(doc_id: str, file_path: str):
    try:
        document_chunks = rag_service.process_file(file_path)
        rag_service.update_vector_store(document_chunks)

        # Update document metadata
        document_store[doc_id].update({
            "chunk_count": len(document_chunks),
            "status": "completed"
        })
    except Exception as e:
        document_store[doc_id].update({
            "status": "failed",
            "error": str(e)
        })
        # Optionally log the error
        print(f"Error processing document {doc_id}: {str(e)}")


# @app.get("/documents", response_class=JSONResponse)
# async def list_documents():
#     return {"documents": list(document_store.values())}


# @app.get("/documents/{doc_id}", response_class=JSONResponse)
# async def get_document(doc_id: str):
#     if doc_id not in document_store:
#         raise HTTPException(status_code=404, detail="Document not found")
#
#     return document_store[doc_id]


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG"""
    if rag_service.vector_store is None:
        raise HTTPException(status_code=400, detail="No documents have been uploaded yet")

    try:
        # Check if any documents are processed successfully
        processed_docs = [doc for doc in document_store.values() if doc.get("status") == "completed"]
        if not processed_docs:
            raise HTTPException(status_code=400, detail="No documents are fully processed yet")

        # Simple query - just pass the query string directly
        result = rag_service.qa_chain({"query": request.query})

        source_docs = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                # Get document ID from metadata if available
                doc_id = doc.metadata.get("doc_id", "unknown") if hasattr(doc, "metadata") else "unknown"
                doc_name = "Unknown"

                # Try to find the document name
                for stored_doc in document_store.values():
                    if stored_doc.get("id") == doc_id:
                        doc_name = stored_doc.get("name", "Unknown")
                        break

                source_docs.append({
                    "content": doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else ""),
                    "document_name": doc_name,
                    "page": doc.metadata.get("page", "N/A") if hasattr(doc, "metadata") and hasattr(doc.metadata,
                                                                                                    "get") else "N/A"
                })

        return {
            "answer": result["result"],
            "source_documents": source_docs
        }

    except Exception as e:
        import traceback
        print(f"Query error: {str(e)}")
        print(traceback.format_exc())
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
#         # Note: This doesn't remove the document from the vector store
#         # For a complete solution, you would need to implement a way to
#         # delete the document's vectors from Qdrant
#
#         return {"status": "success", "message": f"Document {doc_id} deleted successfully"}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# @app.get("/health", response_class=JSONResponse)
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "documents_count": len(document_store),
#         "vector_store_initialized": rag_service.vector_store is not None
#     }


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    try:
        # Initialize the vector store and QA chain
        rag_service.initialize_services()
        print("RAG services initialized successfully")
    except Exception as e:
        print(f"Startup error: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)