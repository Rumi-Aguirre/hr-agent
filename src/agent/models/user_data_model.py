from pydantic import BaseModel
from typing import List, Optional

class UserData(BaseModel):
    first_name: Optional[str] = None
    age: Optional[int] = None
    preferred_schedule: Optional[str] = None

    def get_missing_fields(self) -> List[str]:
        missing = []
        if not self.first_name:
            missing.append('first_name')
        if not self.age:
            missing.append('age')
        if not self.preferred_schedule:
            missing.append('preferred_schedule')
        return missing

    def is_complete(self) -> bool:
        return len(self.get_missing_fields()) == 0