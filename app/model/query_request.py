from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask about the documents")