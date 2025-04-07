from pydantic import BaseModel
from typing import List
 
class RequestMessage(BaseModel):
    requset : str
