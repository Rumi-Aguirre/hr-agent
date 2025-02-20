from typing import Optional
from pydantic import BaseModel, Field

class ExtractedInfo(BaseModel):
    first_name: Optional[str] = Field(None, description="First name of the person")
    age: Optional[int] = Field(None, description="Age of the person")
    preferred_schedule: Optional[str] = Field(None, description="Preferred schedule (mañana/tarde)")