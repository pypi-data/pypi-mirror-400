from pydantic import BaseModel
from typing import List, Optional

# class ConnectionRequest(BaseModel):
#     query: str
#     user_id: str
#     session_id: str
#     workflow_id: str
#     datastore: Optional[List] = []
#     tools: Optional[List] = []

class ConnectionRequest(BaseModel):
    query: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    workflow_id: Optional[str] = None
    datastore: Optional[List] = None
    tools: Optional[List] = None
    d365request: Optional[dict] = None