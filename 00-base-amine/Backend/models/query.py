from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class QueryRequest(BaseModel):
    query:                  str
    top_k:                  Optional[int]  = 5
    session_id:             Optional[str]  = None
    force_route:            Optional[str]  = None
    voice_mode:             Optional[bool] = False
    conversation_id:        Optional[str]  = None
    pending_doc_ids:        Optional[List[str]] = None
    preferred_provider:     Optional[str]  = None
    attached_doc_filenames: Optional[List[str]] = None
    # ── Metadata filters for hybrid search ──────────────────
    project_name:           Optional[str]  = None
    site_id:                Optional[str]  = None
    filter_doc_type:        Optional[str]  = None
    sql_filters:            Optional[Dict] = None


class QueryResponse(BaseModel):
    answer:     str
    sources:    List[dict]
    confidence: float
    route:      Optional[str] = None
    analytics:  Optional[Any] = None
    session_id: str
    chat_title: Optional[str] = None
