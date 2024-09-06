from pydantic import BaseModel, Field, EmailStr, validator
from typing import List
from datetime import datetime

class Item(BaseModel):
    item_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class UserData(BaseModel):
    user_id: str = Field(..., min_length=1)
    email: EmailStr
    timestamp: str
    items: List[Item]

    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Invalid timestamp format. Must be ISO 8601 format.")
        return v