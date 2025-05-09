from typing import Optional
from pydantic import BaseModel, Field

class DocumentResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the document")
    name: str = Field(..., description="Display name of the document")
    filename: str = Field(..., description="Original filename")
    path: str = Field(..., description="Path to the stored document")
    status: str = Field(..., description="Processing status: 'processing', 'completed', 'failed'")
    chunk_count: Optional[int] = Field(None, description="Number of chunks the document was split into")
    error: Optional[str] = Field(None, description="Error message if processing failed")