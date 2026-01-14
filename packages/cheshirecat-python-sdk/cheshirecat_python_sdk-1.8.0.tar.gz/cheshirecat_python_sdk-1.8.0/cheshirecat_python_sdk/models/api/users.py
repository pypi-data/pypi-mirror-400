from typing import Dict, List, Any
from pydantic import BaseModel


class UserOutput(BaseModel):
    username: str
    permissions: Dict[str, List[str]]
    metadata: Dict[str, Any] | None = None
    id: str
    created_at: float | None = None
    updated_at: float | None = None
