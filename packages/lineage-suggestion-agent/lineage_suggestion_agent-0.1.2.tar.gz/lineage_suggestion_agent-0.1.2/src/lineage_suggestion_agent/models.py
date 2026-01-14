from pydantic import BaseModel, Field , ConfigDict
from typing import Dict

class LineageSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: str = Field(..., description="The suggestion text ")
