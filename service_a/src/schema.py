from pydantic import BaseModel, field_validator
from typing import Optional, List, Callable

class StripStringsModel(BaseModel):
    @field_validator('*', mode='before')
    def strip_all_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    
class ProvisionParameters(StripStringsModel):
    username: str
    password: str
    vlan: Optional[int] = None
    interfaces: Optional[List[int]] = None

class ProvisionRequest(StripStringsModel):
    timeoutInSeconds: int
    parameters: ProvisionParameters
    
class ProvisionResponse(BaseModel):
    code: int
    message: str