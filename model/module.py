from pydantic import BaseModel, Field
from typing import List
 

class Message(BaseModel):
    role: str  = Field(default="human")
    content: str  = Field(default="ทองคำ กับ หุ้นแอปเปิ้ลอันไหนน่าซื้อกว่ากัน")

class RequestMessage(BaseModel):
    messages: List[Message] 
    meme: bool = Field(default=False)
