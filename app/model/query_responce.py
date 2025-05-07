from pydantic import BaseModel
from typing import List


class QueryResponse(BaseModel):
    answer: str
    source_documents: List[str]
