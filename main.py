from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agent import system_flow
from tool.generate_tool import create_tool
from model.module import RequestMessage
from langchain_core.messages import AIMessage, HumanMessage
app = FastAPI()


async def call_system_flow(messages : list, meme: bool):
    tool = await create_tool()
    responed = system_flow.call_process(tool , meme).invoke({"messages" : messages})
    return responed["messages"][-1].content


@app.post("/request_chat")
async def chat_action(chatmessages: RequestMessage):
    messages = []
    for chat in chatmessages.messages:
        if chat.role == "ai":
            messages.append(AIMessage(content=chat.content))
        if chat.role == "human":
            messages.append(HumanMessage(content=chat.content))
    
    return await call_system_flow(messages, chatmessages.meme)
