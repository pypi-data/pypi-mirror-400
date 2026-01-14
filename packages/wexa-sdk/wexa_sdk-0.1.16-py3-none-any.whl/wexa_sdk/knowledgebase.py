from __future__ import annotations
from typing import Any, Dict, TypedDict, Optional, List

from .core.http import HttpClient


class KnowledgebaseUploadBody(TypedDict, total=False):
    """
    Body for knowledge base file upload request.

    Required:
      - source_type: str (e.g., "STORAGE")
      - filenames: List[str] (e.g., ["report.pdf"])
      - tags: List[str] (e.g., ["Invoices"])
    Optional:
      - projectID: str (some backends also accept in body)
      - org_id: str
    """
    source_type: str
    filenames: List[str]
    tags: List[str]
    projectID: str
    org_id: str


class KnowledgeBase:
    def __init__(self, http: HttpClient):
        self.http = http

    def upload(self, *, project_id: Optional[str] = None, container_name: Optional[str] = None, body: KnowledgebaseUploadBody = {}):
        """
        Files upload (Knowledge Base)
        POST /files/upload

        Query:
          - projectID: string (optional)
          - container_name: string (optional)

        Body (application/json; backend may accept multipart at edge):
          - source_type: string (required)
          - filenames: List[str] (required)
          - tags: List[str] (required)
          - projectID: string (optional)
          - org_id: string (optional)
        """
        params: Dict[str, Any] = {}
        if project_id is not None:
            params["projectID"] = project_id
        if container_name is not None:
            params["container_name"] = container_name
        return self.http.request("POST", "/files/upload", params=params or None, json=body)


