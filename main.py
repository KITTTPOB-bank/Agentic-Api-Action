from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agent import system_flow
from tool.generate_tool import create_tool
from model.module import RequestMessage
from langchain_core.messages import AIMessage, HumanMessage
app = FastAPI()
from fastapi.concurrency import run_in_threadpool

 
async def call_system_flow(messages: list, meme: bool):
    tool = await create_tool()
    workflow = system_flow.call_process(tool, meme)
    
    result = await run_in_threadpool(workflow.invoke, {"messages": messages})
    
    return result["messages"][-1].content

@app.post("/request_chat")
async def chat_action(chatmessages: RequestMessage):
    messages = []
    for chat in chatmessages.messages:
        if chat.role == "ai":
            messages.append(AIMessage(content=chat.content))
        if chat.role == "human":
            messages.append(HumanMessage(content=chat.content))
    
    return await call_system_flow(messages, chatmessages.meme)
