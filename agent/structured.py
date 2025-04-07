from pydantic import BaseModel, Field
from typing import List

class LogoChoice(BaseModel):
    data : str = Field(description="")