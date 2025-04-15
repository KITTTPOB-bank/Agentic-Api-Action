from pydantic import BaseModel, Field
from typing import List, TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

 
class MessageStatus(BaseModel):
    message: str = Field(description="ข้อความ")
    status: Literal["end", "process"] = Field(description="ถ้ากำลังค้นหาข้อมูลเป็น `process` ถ้าวิเคราะห์และได้ผลลัพธ์ให้กับผู้ใช้แล้วเป็น `end`")

class MessagesFlow(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    status: str 