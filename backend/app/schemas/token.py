from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[dict] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None
