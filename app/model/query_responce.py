from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SourceDocument(BaseModel):
    content: str = Field(..., description="Extract from the source document")
    document_name: str = Field(..., description="Name of the source document")
    page: Optional[str] = Field(None, description="Page number if available")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="The answer to the query")
    source_documents: List[SourceDocument] = Field(default_factory=list, description="Source documents used for the answer")