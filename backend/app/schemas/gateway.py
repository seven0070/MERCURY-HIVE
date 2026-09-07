from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class GatewayRequest(BaseModel):
    system_prompt: str
    messages: List[Dict[str, str]]
    model: Optional[str] = "default"
    temperature: Optional[float] = 0.7

class GatewayResponse(BaseModel):
    content: str
    model_used: str
    usage: Dict[str, int]
