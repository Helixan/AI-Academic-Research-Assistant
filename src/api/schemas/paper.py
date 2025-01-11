from pydantic import BaseModel, ConfigDict
from typing import Optional

class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    content: Optional[str] = None

class PaperCreate(PaperBase):
    pass

class Paper(PaperBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
