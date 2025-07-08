from pydantic import BaseModel

class AuthLog(BaseModel):
    user_id: str
    timestamp: str
    ip_address: str
    action: str
    location: str
    device: str
