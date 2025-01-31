from pydantic import BaseModel
from typing import Dict, Any, Optional

class BinaryAnalysisRequest(BaseModel):
    file_path: str
    format: Optional[str] = "auto"

class BinaryAnalysisResponse(BaseModel):
    file_path: str
    header: Dict[str, Any]
    metadata: Dict[str, Any]
    format: str